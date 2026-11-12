import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

STATUSES = [("todo", "Queued"), ("doing", "Printing"), ("done", "Ready")]
PRIORITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
ACCENTS = [("teal", "Teal"), ("violet", "Violet"), ("forest", "Forest"), ("clay", "Clay")]


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40, default="My workspace")
    accent = models.CharField(max_length=12, choices=ACCENTS, default="teal")
    queue_state = models.JSONField(default=list)
    workflow_state = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="tickets")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1500, blank=True)
    category = models.CharField(max_length=40, default="General")
    status = models.CharField(max_length=8, choices=STATUSES, default="todo")
    priority = models.CharField(max_length=8, choices=PRIORITIES, default="medium")
    due_date = models.DateField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_requests")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_requests")
    requester_email = models.EmailField(blank=True)
    customer_name = models.CharField(max_length=80, blank=True)
    contact_number = models.CharField(max_length=40, blank=True)
    copies = models.PositiveIntegerField(null=True, blank=True)
    paper_size = models.CharField(max_length=20, blank=True)
    status_note = models.TextField(max_length=500, blank=True)
    version = models.PositiveIntegerField(default=1)
    queued_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["workspace", "archived", "status"], name="ticket_workspace_status")]
        constraints = [
            models.CheckConstraint(condition=models.Q(status__in=[x[0] for x in STATUSES]), name="valid_ticket_status"),
            models.CheckConstraint(condition=models.Q(priority__in=[x[0] for x in PRIORITIES]), name="valid_ticket_priority"),
        ]

    @property
    def reference(self):
        return f"PP-{self.pk:04d}"

    @property
    def overdue(self):
        return bool(self.due_date and self.due_date < timezone.localdate() and self.status != "done" and not self.archived)

    def __str__(self):
        return self.title


class Event(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="events")
    kind = models.CharField(max_length=30)
    summary = models.CharField(max_length=240)
    details = models.JSONField(default=dict)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="desk_events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.summary


ROLES = [("owner", "Owner"), ("manager", "Manager"), ("agent", "Agent"), ("viewer", "Viewer")]


class Membership(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="desk_memberships")
    role = models.CharField(max_length=8, choices=ROLES, default="agent")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="unique_workspace_member"),
            models.CheckConstraint(condition=models.Q(role__in=[r[0] for r in ROLES]), name="valid_member_role"),
        ]

    @property
    def can_edit(self):
        return self.role in {"owner", "manager", "agent"}

    @property
    def can_manage(self):
        return self.role in {"owner", "manager"}

    def __str__(self):
        return f"{self.user} · {self.workspace} ({self.role})"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    body = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=8, choices=ROLES[1:], default="agent")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    @property
    def pending(self):
        return not self.revoked and self.accepted_at is None and self.expires_at > timezone.now()


class LoginThrottle(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    failures = models.PositiveIntegerField(default=0)
    window_start = models.DateTimeField(default=timezone.now)
