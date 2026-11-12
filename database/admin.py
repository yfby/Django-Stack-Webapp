from django.contrib import admin
from .models import Comment, Event, Invitation, Membership, Ticket, Workspace


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "workspace", "status", "priority", "assignee", "archived", "updated_at")
    list_filter = ("status", "priority", "archived")
    search_fields = ("title", "description", "workspace__name")
    autocomplete_fields = ("assignee", "created_by")
    list_select_related = ("workspace", "assignee")


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "created_at")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role", "joined_at")
    list_filter = ("role",)
    autocomplete_fields = ("user", "workspace")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("summary", "workspace", "actor", "kind", "created_at")
    list_filter = ("kind",)
    readonly_fields = ("workspace", "actor", "kind", "summary", "details", "created_at")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "created_at")
    search_fields = ("body",)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "workspace", "role", "expires_at", "accepted_at", "revoked")
    readonly_fields = ("id", "created_at")

admin.site.site_header = "PrintPilot administration"
admin.site.site_title = "PrintPilot"
admin.site.index_title = "System administration"
