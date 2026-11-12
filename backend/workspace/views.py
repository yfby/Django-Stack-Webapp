from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from database.models import Event, STATUSES, Workspace
from .forms import MoveForm, PreferencesForm, TicketForm, WorkflowForm, CommentForm, StatusNoteForm
from .permissions import workspace_access
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, F, Sum
from datetime import timedelta
from . import services


def filtered_tickets(request):
    items = request.workspace.tickets.filter(archived=False).select_related("assignee", "created_by")
    query = request.GET.get("q", "").strip()[:100]
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(customer_name__icontains=query))
    status = request.GET.get("status", "")
    if status in dict(STATUSES):
        items = items.filter(status=status)
    priority = request.GET.get("priority", "")
    if priority in {"low", "medium", "high"}:
        items = items.filter(priority=priority)
    assignee = request.GET.get("assignee", "")
    if assignee == "me":
        items = items.filter(assignee=request.user)
    elif assignee == "unassigned":
        items = items.filter(assignee__isnull=True)
    elif assignee.isdigit() and len(assignee) <= 19:
        items = items.filter(assignee_id=assignee)
    if request.GET.get("overdue") == "1":
        items = items.filter(due_date__lt=timezone.localdate()).exclude(status="done")
    sort = request.GET.get("sort", "updated")
    order = {"updated": "-updated_at", "created": "-created_at", "oldest": "created_at"}
    return items.order_by(F("due_date").asc(nulls_last=True), "id") if sort == "due" else items.order_by(order.get(sort, "-updated_at"), "id")

@workspace_access()
@require_GET
def board(request):
    query = request.GET.get("q", "").strip()[:100]
    view = "board" if request.GET.get("view") == "board" else "list"
    items = Paginator(filtered_tickets(request), 25).get_page(request.GET.get("page"))
    groups = [{"key": k, "label": label, "items": [x for x in items if x.status == k]} for k, label in STATUSES]
    params = request.GET.copy(); params.pop("page", None)
    return render(request, "board.html", {"page": "board", "items": items, "groups": groups,
        "query": query, "selected_status": request.GET.get("status", ""), "view": view,
        "queued_ids": request.workspace.queue_state, "filter_query": params.urlencode(),
        "agents": request.workspace.memberships.select_related("user").exclude(role="viewer")})


@workspace_access(edit=True)
@require_http_methods(["GET", "POST"])
def ticket_form(request, ticket_id=None):
    ticket = services.owned_ticket(request.workspace, ticket_id) if ticket_id is not None else None
    initial = {"category": "General", "status": "todo", "priority": "medium"}
    if request.GET.get("status") in dict(STATUSES):
        initial["status"] = request.GET["status"]
    form = TicketForm(request.POST if request.method == "POST" else None, instance=ticket, initial=initial, workspace=request.workspace)
    if request.method == "POST" and form.is_valid():
        try:
            services.save_ticket(request.workspace.id, form.cleaned_data, ticket_id, actor=request.user)
        except services.ActivityError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Print job updated." if ticket else "Print job created.")
            return redirect("workspace:board")
    return render(request, "ticket_form.html", {"page": "board", "form": form, "editing": ticket is not None}, status=422 if request.method == "POST" else 200)


@workspace_access(edit=True)
@require_POST
def move(request, ticket_id):
    form = MoveForm(request.POST)
    if not form.is_valid():
        return render(request, "error.html", {"code": 400, "message": "Choose a valid status."}, status=400)
    try:
        services.move_ticket(request.workspace.id, ticket_id, form.cleaned_data["status"], actor=request.user)
    except services.ActivityError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Job status updated.")
    return redirect("workspace:board")


@workspace_access(edit=True)
@require_POST
def archive_item(request, ticket_id):
    try:
        services.set_archived(request.workspace.id, ticket_id, True, actor=request.user)
    except services.ActivityError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Print job archived. You can restore it from Archive.")
    return redirect("workspace:board")


@workspace_access(edit=True)
@require_POST
def restore_item(request, ticket_id):
    services.set_archived(request.workspace.id, ticket_id, False, actor=request.user)
    messages.success(request, "Print job restored with its original details. It has not rejoined the print queue.")
    return redirect("workspace:archive")


@workspace_access()
@require_GET
def archive(request):
    return render(request, "archive.html", {"page": "archive", "items": Paginator(request.workspace.tickets.filter(archived=True), 25).get_page(request.GET.get("page"))})


@workspace_access()
@require_GET
def queue_page(request):
    try:
        context = services.queue_context(request.workspace)
    except services.ActivityError as exc:
        return render(request, "error.html", {"code": 422, "message": str(exc)}, status=422)
    context.update({"page": "queue", "available": request.workspace.tickets.filter(
        archived=False, status="todo").exclude(id__in=context["waiting_ids"]), "queue_limit": services.MAX_QUEUE})
    return render(request, "queue.html", context)


@workspace_access(edit=True)
@require_POST
def queue_join(request, ticket_id):
    try:
        ticket = services.enqueue_ticket(request.workspace.id, ticket_id, actor=request.user)
    except services.ActivityError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f'Added to the print queue: {ticket.title}')
    return redirect("workspace:queue")


@workspace_access(edit=True)
@require_POST
def queue_serve(request):
    try:
        expected = request.POST.get("expected_next", "")
        if expected and (not expected.isdigit() or len(expected) > 20):
            raise services.ActivityError("Reload the service queue before starting the next request.")
        ticket = services.serve_next(request.workspace.id, actor=request.user, expected_id=int(expected) if expected else None)
    except (services.ActivityError, IndexError) as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f'Now printing: {ticket.title}')
    return redirect("workspace:queue")


@workspace_access()
@require_http_methods(["GET", "POST"])
def workflow(request):
    if request.method == "POST" and not request.membership.can_edit:
        raise PermissionDenied
    form = WorkflowForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            call, result = services.operate_workflow(request.workspace.id, **form.cleaned_data, actor=request.user)
        except (services.ActivityError, IndexError, TypeError) as exc:
            form.add_error(None, f'Operation could not complete: {exc}')
        else:
            result_text = "No return value" if result is None else repr(result)
            messages.success(request, f'{call} returned {result_text}.')
            return redirect("workspace:workflow")
    # Refresh after invalid operations so a failed mutation cannot leak into the page.
    workspace = Workspace.objects.get(pk=request.workspace.id)
    linked = services.load_workflow(workspace)
    values = services._snapshot(linked, services.MAX_STEPS)
    report = services.inspect_nodes(linked)
    return render(request, "workflow.html", {"page": "workflow", "form": form,
        "values": values, "list_size": linked.size(), "list_empty": linked.is_empty(),
        "report": report, "workflow_events": workspace.events.filter(kind="workflow")[:5]},
        status=422 if request.method == "POST" else 200)


@workspace_access()
@require_GET
def activity(request):
    from django.core.paginator import Paginator
    events = Paginator(request.workspace.events.select_related("actor"), 25).get_page(request.GET.get("page"))
    return render(request, "activity.html", {"page": "activity", "events": events})


@workspace_access(manage=True)
@require_http_methods(["GET", "POST"])
def preferences(request):
    form = PreferencesForm(request.POST if request.method == "POST" else None, instance=request.workspace)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Update only preferences so concurrent queue/workflow changes survive.
            Workspace.objects.select_for_update().get(pk=request.workspace.id)
            Workspace.objects.filter(pk=request.workspace.id).update(**form.cleaned_data)
            services.log(request.workspace, "preferences", "Workspace preferences updated.", actor=request.user)
        messages.success(request, "Preferences saved.")
        return redirect("workspace:settings")
    return render(request, "settings.html", {"page": "settings", "form": form}, status=422 if request.method == "POST" else 200)


@workspace_access()
@require_GET
def guide(request):
    return render(request, "guide.html", {"page": "guide"})


@workspace_access()
@require_GET
def state_api(request):
    try:
        queue = services.queue_context(request.workspace)
        linked = services.load_workflow(request.workspace)
        values = services._snapshot(linked, services.MAX_STEPS)
        report = services.inspect_nodes(linked)
    except services.ActivityError as exc:
        return JsonResponse({"error": str(exc)}, status=422)
    return JsonResponse({
        "workspace": {"id": str(request.workspace.id), "name": request.workspace.name},
        "queue": {"arrival_order": queue["waiting_ids"], "selected_next": queue["selected_id"], "size": queue["queue_size"]},
        "workflow": {"values": values, "size": linked.size(), "is_empty": linked.is_empty(), "representation": report},
        "items": list(request.workspace.tickets.filter(archived=False).values("id", "title", "status", "priority", "category", "due_date",
                                                                               "customer_name", "copies", "paper_size")),
    })


@require_GET
def health(request):
    from django.db import connection, DatabaseError
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"app": "printpilot", "framework": "Django", "status": "ok", "version": "3.1.0"})


def error_400(request, exception=None):
    return render(request, "error.html", {"code": 400, "message": "This request could not be processed."}, status=400)


def error_403(request, exception=None):
    return render(request, "error.html", {"code": 403, "message": "You do not have permission for this action. If your session expired, sign in and try again."}, status=403)


def csrf_failure(request, reason=""):
    return error_403(request)


def error_404(request, exception=None):
    return render(request, "error.html", {"code": 404, "message": "This item or page is not available in your workspace."}, status=404)


def error_500(request):
    return render(request, "error.html", {"code": 500, "message": "The operation could not finish. Check the server terminal."}, status=500)


@workspace_access()
@require_GET
def dashboard(request):
    all_items = request.workspace.tickets.filter(archived=False)
    today = timezone.localdate()
    start = today - timedelta(days=6)
    from .presentation import activity_chart
    created = list(all_items.filter(created_at__date__gte=start, created_at__date__lte=today).values_list("created_at", flat=True))
    resolved = list(all_items.filter(status="done", resolved_at__date__gte=start, resolved_at__date__lte=today).values_list("resolved_at", flat=True))
    chart = activity_chart(created, resolved, start)
    status_counts = {status: all_items.filter(status=status).count() for status, _ in STATUSES}
    total = sum(status_counts.values())
    status_peak = max([*status_counts.values(), 1])
    status_bars = [{"key": status, "label": label, "count": status_counts[status],
                    "height": round(status_counts[status] / status_peak * 100)} for status, label in STATUSES]
    workload = request.workspace.memberships.exclude(role="viewer").select_related("user")
    agents = [{"user": m.user, "count": all_items.filter(assignee=m.user).exclude(status="done").count()} for m in workload[:8]]
    return render(request, "dashboard.html", {"page": "dashboard", "chart": chart, "status_bars": status_bars,
        "completion_rate": round(status_counts["done"] / max(total, 1) * 100),
        "total_week": len(created), "agents": agents, "overdue_count": all_items.filter(due_date__lt=today).exclude(status="done").count(),
        "attention": all_items.exclude(status="done").select_related("assignee").order_by(F("due_date").asc(nulls_last=True), "-created_at")[:6],
        "recent_events": request.workspace.events.select_related("actor")[:5]})


@workspace_access()
@require_http_methods(["GET", "POST"])
def detail(request, ticket_id):
    ticket = services.owned_ticket(request.workspace, ticket_id)
    form = CommentForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        if not request.membership.can_edit:
            raise PermissionDenied
        if form.is_valid():
            services.add_comment(request.workspace.id, ticket.id, form.cleaned_data["body"], request.user)
            messages.success(request, "Team note added.")
            return redirect("workspace:detail", ticket_id=ticket.id)
    events = request.workspace.events.filter(details__item_id=ticket.id).select_related("actor")[:20]
    status_note_form = StatusNoteForm(initial={"status_note": ticket.status_note})
    return render(request, "detail.html", {"page": "board", "item": ticket, "form": form,
        "status_note_form": status_note_form, "comments": ticket.comments.select_related("author"),
        "ticket_events": events, "in_queue": ticket.id in request.workspace.queue_state},
        status=422 if request.method == "POST" else 200)


@workspace_access(edit=True)
@require_POST
def status_note(request, ticket_id):
    form = StatusNoteForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Keep the job status note under 500 characters.")
    else:
        try:
            services.update_status_note(request.workspace.id, ticket_id, form.cleaned_data["status_note"], actor=request.user)
        except services.ActivityError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Job status note saved.")
    return redirect("workspace:detail", ticket_id=ticket_id)


@workspace_access(edit=True)
@require_POST
def queue_withdraw(request, ticket_id):
    try:
        services.withdraw_ticket(request.workspace.id, ticket_id, actor=request.user)
    except services.ActivityError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Print job removed from the queue.")
    return redirect("workspace:queue")


@workspace_access()
@require_GET
def reports(request):
    items = request.workspace.tickets.filter(archived=False)
    total = items.count()
    categories = list(items.values("category").annotate(total=Count("id")).order_by("-total", "category")[:10])
    for row in categories:
        row["percentage"] = round(row["total"] / max(total, 1) * 100)
    priorities = [{"label": label, "key": key, "count": items.filter(priority=key).count()} for key,label in [("high","High"),("medium","Medium"),("low","Low")]]
    resolved = items.filter(status="done").count()
    status_summary = [{"key": key, "label": label, "count": items.filter(status=key).count()} for key, label in STATUSES]
    copies_total = items.aggregate(total=Sum("copies"))["total"] or 0
    paper_sizes = list(items.exclude(paper_size="").values("paper_size").annotate(total=Count("id")).order_by("-total", "paper_size")[:5])
    return render(request, "reports.html", {"page": "reports", "categories": categories, "priorities": priorities,
        "report_total": total, "resolution_rate": round(resolved/max(total,1)*100), "resolved_total": resolved,
        "unassigned": items.filter(assignee__isnull=True).exclude(status="done").count(),
        "status_summary": status_summary, "copies_total": copies_total, "paper_sizes": paper_sizes})


@workspace_access()
@require_GET
def export_requests(request):
    import csv
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="printpilot-requests.csv"'
    writer = csv.writer(response)
    writer.writerow(["Reference","Job","Category","Status","Priority","Assignee","Due date","Requester email",
                     "Customer","Contact number","Copies","Paper size","Status note"])
    def cell(value):
        text = str(value or "")
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else text
    for item in filtered_tickets(request).iterator(chunk_size=500):
        writer.writerow([cell(x) for x in [item.reference,item.title,item.category,item.get_status_display(),item.get_priority_display(),item.assignee.get_username() if item.assignee else "",item.due_date,item.requester_email,item.customer_name,item.contact_number,item.copies,item.paper_size,item.status_note]])
    return response
