"""Real request path: Django view -> student class -> saved SQLite snapshot.

Serialization is persistence, not the data structure. Each request reconstructs
the student's class, calls its operation, then commits the resulting snapshot.
"""
from collections.abc import Collection
from django.db import transaction
from django.shortcuts import get_object_or_404
from backend.dsa.queue import ServiceQueue
from backend.dsa.singly_linked_list import Node, SinglyLinkedList
from database.models import Event, Ticket, Workspace, Membership, Comment
from django.utils import timezone

MAX_QUEUE = 100
MAX_STEPS = 40


class ActivityError(ValueError):
    """A useful message for an invalid application operation."""


class StructureContractError(ActivityError):
    """A student method broke the public persistence contract."""


def log(workspace, kind, summary, actor=None, **details):
    Event.objects.create(workspace=workspace, kind=kind, summary=summary[:240], details=details, actor=actor)


@transaction.atomic
def create_workspace(owner=None, name="My workspace", seed=True):
    workspace = Workspace.objects.create(name=name, workflow_state=["Receive file", "Print", "Cut", "Pickup"])
    if owner:
        Membership.objects.create(workspace=workspace, user=owner, role="owner")
    if not seed:
        log(workspace, "welcome", "Workspace created.", actor=owner)
        return workspace
    examples = [
        ("Print 120 event flyers", "A5 flyers on glossy stock. Trim, stack, and wrap in tens.", "Flyers", "todo", "medium",
         "Riverside Café", "555-0142", 120, "A5"),
        ("Bound thesis copies", "Three A4 copies with clear covers and black spiral binding.", "Binding", "todo", "high",
         "Mara Ellison", "555-0178", 3, "A4"),
        ("Vinyl banner for Saturday market", "Weatherproof banner with eyelets in each corner.", "Signage", "todo", "low",
         "Greenfield Market", "555-0119", 1, "2 m × 1 m"),
        ("Business cards for design team", "Matte cards, double-sided, with a soft-touch finish.", "Business cards", "doing", "medium",
         "Northline Studio", "555-0164", 500, "85 × 55 mm"),
        ("Laminate classroom certificates", "A4 certificates laminated with a 3 mm rounded corner trim.", "Finishing", "done", "low",
         "Hilltop Primary", "555-0135", 24, "A4"),
        ("Menu reprints for the lunch rush", "Two-sided A4 menus on 250 gsm recycled paper.", "Menus", "todo", "medium",
         "Riverside Café", "555-0142", 40, "A4"),
    ]
    Ticket.objects.bulk_create([
        Ticket(workspace=workspace, title=t, description=d, category=c, status=s, priority=p, created_by=owner,
               assignee=owner if s == "doing" else None, resolved_at=timezone.now() if s == "done" else None,
               customer_name=customer, contact_number=contact, copies=copies, paper_size=paper)
        for t, d, c, s, p, customer, contact, copies, paper in examples
    ])
    log(workspace, "welcome", "Print shop created with six example print jobs.", actor=owner)
    return workspace


def owned_ticket(workspace, ticket_id, archived=False):
    return get_object_or_404(Ticket, pk=ticket_id, workspace=workspace, archived=archived)


def _snapshot(structure, limit):
    values = structure.to_list()
    if not isinstance(values, list) or len(values) > limit:
        raise StructureContractError("to_list() must return a new list within the documented size limit.")
    if structure.size() != len(values) or structure.is_empty() != (len(values) == 0):
        raise StructureContractError("size() and is_empty() must agree with to_list().")
    return values


def load_queue(workspace):
    values = workspace.queue_state
    if not isinstance(values, list) or any(type(x) is not int or x < 1 for x in values) or len(values) != len(set(values)):
        raise StructureContractError("The saved queue must contain distinct item IDs in arrival order.")
    return ServiceQueue(values)


def load_workflow(workspace):
    values = workspace.workflow_state
    if not isinstance(values, list) or any(not isinstance(x, str) or not x or len(x) > 80 for x in values):
        raise StructureContractError("The saved workflow must contain nonempty text values.")
    return SinglyLinkedList(values)


def _save_queue(workspace, queue):
    values = _snapshot(queue, MAX_QUEUE)
    if any(type(x) is not int or x < 1 for x in values) or len(values) != len(set(values)):
        raise StructureContractError("The queue snapshot must contain distinct item IDs.")
    valid = Ticket.objects.filter(workspace=workspace, archived=False, status="todo", id__in=values).count()
    if valid != len(values):
        raise StructureContractError("Every waiting ID must belong to an active queued print job in this workspace.")
    workspace.queue_state = values
    workspace.save(update_fields=["queue_state"])


@transaction.atomic
def enqueue_ticket(workspace_id, ticket_id, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id)
    if ticket.status != "todo":
        raise ActivityError("Only queued print jobs can join the waiting line.")
    queue = load_queue(workspace)
    if ticket.id in queue.to_list():
        raise ActivityError("This print job is already waiting.")
    if queue.size() >= MAX_QUEUE:
        raise ActivityError("The print queue has reached its 100-job classroom limit.")
    queue.enqueue(ticket.id)  # STUDENT CLASS: enqueue affects the actual website.
    _save_queue(workspace, queue)
    ticket.queued_at = timezone.now()
    ticket.version += 1
    ticket.save(update_fields=["queued_at", "version", "updated_at"])
    log(workspace, "enqueued", f'Joined the print queue: {ticket.title}', item_id=ticket.id, actor=actor)
    return ticket


@transaction.atomic
def serve_next(workspace_id, actor=None, expected_id=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    queue = load_queue(workspace)
    if queue.is_empty():
        raise ActivityError("The service queue is empty. Add a queued print job first.")
    if expected_id is not None and queue.peek() != expected_id:
        raise ActivityError("The queue changed since you opened this page. Review the next request and try again.")
    before = list(queue.to_list())
    selected = queue.dequeue()  # STUDENT CLASS: determines which database row changes.
    after = queue.to_list()
    if type(selected) is not int or selected not in before or after != [x for x in before if x != selected]:
        raise StructureContractError("dequeue() must return one waiting ID and preserve the order of the remaining IDs.")
    ticket = owned_ticket(workspace, selected)
    ticket.status = "doing"
    ticket.started_at = timezone.now()
    ticket.assignee = actor or ticket.assignee
    ticket.version += 1
    ticket.save(update_fields=["status", "started_at", "assignee", "version", "updated_at"])
    _save_queue(workspace, queue)
    log(workspace, "served", f'Started printing: {ticket.title}', item_id=ticket.id, actor=actor)
    return ticket


def _withdraw(workspace, ticket_id):
    """Application cancellation preserves the other waiting items' order."""
    queue = load_queue(workspace)
    workspace.queue_state = [x for x in queue.to_list() if x != ticket_id]
    workspace.save(update_fields=["queue_state"])


@transaction.atomic
def save_ticket(workspace_id, cleaned_data, ticket_id=None, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id) if ticket_id is not None else Ticket(workspace=workspace)
    if ticket_id and cleaned_data.get("version") != ticket.version:
        raise ActivityError("Someone updated this print job while you were editing. Reload the page and apply your changes again.")
    if not ticket_id:
        ticket.created_by = actor
    assignee = cleaned_data.get("assignee")
    if assignee and not Membership.objects.filter(workspace=workspace, user=assignee, role__in=["owner", "manager", "agent"]).exists():
        raise ActivityError("Choose an agent who belongs to this workspace.")
    ticket.assignee = assignee
    ticket.requester_email = cleaned_data.get("requester_email", "")
    ticket.version += 1 if ticket_id else 0
    if ticket.status != cleaned_data["status"]:
        ticket.resolved_at = timezone.now() if cleaned_data["status"] == "done" else None
    for key in ("title", "description", "category", "status", "priority", "due_date",
                "customer_name", "contact_number", "copies", "paper_size"):
        setattr(ticket, key, cleaned_data[key])
    ticket.full_clean()
    ticket.save()
    if ticket.status != "todo":
        _withdraw(workspace, ticket.id)
    log(workspace, "edited" if ticket_id else "created", f'{"Updated" if ticket_id else "Created"}: {ticket.title}', item_id=ticket.id, actor=actor)
    return ticket


@transaction.atomic
def move_ticket(workspace_id, ticket_id, status, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id)
    ticket.status = status
    ticket.resolved_at = timezone.now() if status == "done" else None
    ticket.started_at = ticket.started_at or (timezone.now() if status == "doing" else None)
    ticket.version += 1
    ticket.full_clean()
    ticket.save(update_fields=["status", "resolved_at", "started_at", "version", "updated_at"])
    if status != "todo":
        _withdraw(workspace, ticket.id)
    log(workspace, "moved", f'{ticket.title}: {ticket.get_status_display()}', item_id=ticket.id, actor=actor)
    return ticket


@transaction.atomic
def set_archived(workspace_id, ticket_id, archived, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id, archived=not archived)
    ticket.archived = archived
    ticket.version += 1
    ticket.save(update_fields=["archived", "version", "updated_at"])
    if archived:
        _withdraw(workspace, ticket.id)
    log(workspace, "archived" if archived else "restored", f'{"Archived" if archived else "Restored"}: {ticket.title}', item_id=ticket.id, actor=actor)
    return ticket


@transaction.atomic
def operate_workflow(workspace_id, operation, value="", index=None, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    linked = load_workflow(workspace)
    before = list(linked.to_list())
    if operation in {"append", "prepend", "insert_at"} and linked.size() >= MAX_STEPS:
        raise ActivityError("This classroom workflow supports up to 40 steps.")
    # These are real student methods, not replacements implemented in the view.
    if operation in {"append", "prepend", "remove", "index_of"}:
        result = getattr(linked, operation)(value)
    elif operation == "insert_at":
        result = linked.insert_at(index, value)
    elif operation in {"remove_at", "get"}:
        result = getattr(linked, operation)(index)
    else:
        raise ActivityError("Unknown workflow operation.")
    after = _snapshot(linked, MAX_STEPS)
    if any(not isinstance(x, str) or not x or len(x) > 80 for x in after):
        raise StructureContractError("Workflow nodes must preserve their text values.")
    if operation in {"get", "index_of"} and after != before:
        raise StructureContractError("Read operations must leave the workflow unchanged.")
    workspace.workflow_state = after
    workspace.save(update_fields=["workflow_state"])
    args = f'{index}, {value!r}' if operation == "insert_at" else (str(index) if operation in {"get", "remove_at"} else repr(value))
    summary = f'{operation}({args})'
    log(workspace, "workflow", summary, before=before, after=after, result=result, actor=actor)
    return summary, result


def inspect_nodes(linked):
    """Show actual next references. Do not draw fake links for flat storage."""
    backing = any(isinstance(x, Collection) and not isinstance(x, (str, bytes, Node)) for x in vars(linked).values())
    node = getattr(linked, "head", None)
    nodes, seen = [], set()
    error = ""
    while node is not None:
        if not isinstance(node, Node):
            error = "A link refers to an object that is not a Node."
            break
        if id(node) in seen:
            error = "A cycle appeared. The last next must be None."
            break
        if len(nodes) >= MAX_STEPS:
            error = "The chain exceeds the classroom workflow limit."
            break
        seen.add(id(node))
        nodes.append(node)
        node = node.next
    size = linked.size()
    valid = not backing and not error and len(nodes) == size and (
        (not nodes and getattr(linked, "tail", None) is None) or
        (bool(nodes) and getattr(linked, "tail", None) is nodes[-1] and nodes[-1].next is None)
    )
    return {
        "mode": "nodes" if valid else "flat" if backing else "incomplete",
        "label": "Actual node chain" if valid else "Flat-storage baseline" if backing else "Incomplete node links",
        "error": error,
        "head": "N0" if nodes else "None",
        "tail": f'N{len(nodes)-1}' if nodes else "None",
        "rows": [{"key": f'N{i}', "data": n.data, "next": f'N{i+1}' if n.next is not None and i+1 < len(nodes) else "None" if n.next is None else "invalid"} for i, n in enumerate(nodes)],
    }


def queue_context(workspace):
    queue = load_queue(workspace)
    ids = _snapshot(queue, MAX_QUEUE)
    by_id = {x.id: x for x in Ticket.objects.filter(workspace=workspace, archived=False, id__in=ids)}
    if any(x not in by_id for x in ids):
        raise StructureContractError("A waiting item no longer belongs to this workspace.")
    selected_id = None if queue.is_empty() else queue.peek()
    if selected_id is not None and selected_id not in by_id:
        raise StructureContractError("peek() must return a waiting ID.")
    return {"waiting": [by_id[x] for x in ids], "waiting_ids": ids,
            "selected": by_id.get(selected_id), "selected_id": selected_id,
            "fifo_front": by_id.get(ids[0]) if ids else None,
            "queue_size": queue.size(), "queue_empty": queue.is_empty()}


@transaction.atomic
def add_comment(workspace_id, ticket_id, body, actor):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id)
    comment = Comment(ticket=ticket, author=actor, body=body)
    comment.full_clean()
    comment.save()
    log(workspace, "comment", f"Added a note to {ticket.reference}: {ticket.title}", actor=actor, item_id=ticket.id)
    return comment


@transaction.atomic
def withdraw_ticket(workspace_id, ticket_id, actor=None):
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id)
    if ticket.id not in workspace.queue_state:
        raise ActivityError("This print job is not waiting in the queue.")
    _withdraw(workspace, ticket.id)
    ticket.queued_at = None
    ticket.version += 1
    ticket.save(update_fields=["queued_at", "version", "updated_at"])
    log(workspace, "withdrawn", f"Removed from the print queue: {ticket.title}", actor=actor, item_id=ticket.id)
    return ticket


@transaction.atomic
def update_status_note(workspace_id, ticket_id, note, actor=None):
    """Save a short shop-floor note without touching the job's workflow status."""
    workspace = Workspace.objects.select_for_update().get(pk=workspace_id)
    ticket = owned_ticket(workspace, ticket_id)
    ticket.status_note = note.strip()
    ticket.version += 1
    ticket.full_clean()
    ticket.save(update_fields=["status_note", "version", "updated_at"])
    summary = f'Status note updated for {ticket.reference}: {ticket.title}'
    log(workspace, "status_note", summary, actor=actor, item_id=ticket.id)
    return ticket
