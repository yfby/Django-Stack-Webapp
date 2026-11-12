from django.urls import path
from . import views

app_name = "workspace"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("requests/", views.board, name="board"),
    path("requests/export/", views.export_requests, name="export"),
    path("reports/", views.reports, name="reports"),
    path("items/<int:ticket_id>/", views.detail, name="detail"),
    path("queue/withdraw/<int:ticket_id>/", views.queue_withdraw, name="queue_withdraw"),
    path("items/new/", views.ticket_form, name="new"),
    path("items/<int:ticket_id>/edit/", views.ticket_form, name="edit"),
    path("items/<int:ticket_id>/move/", views.move, name="move"),
    path("items/<int:ticket_id>/status-note/", views.status_note, name="status_note"),
    path("items/<int:ticket_id>/archive/", views.archive_item, name="archive_item"),
    path("items/<int:ticket_id>/restore/", views.restore_item, name="restore_item"),
    path("archive/", views.archive, name="archive"),
    path("queue/", views.queue_page, name="queue"),
    path("queue/join/<int:ticket_id>/", views.queue_join, name="queue_join"),
    path("queue/serve/", views.queue_serve, name="queue_serve"),
    path("workflow/", views.workflow, name="workflow"),
    path("activity/", views.activity, name="activity"),
    path("settings/", views.preferences, name="settings"),
    path("guide/", views.guide, name="guide"),
    path("api/state/", views.state_api, name="state_api"),
    path("health/", views.health, name="health"),
]
