# Architecture: real Django, separated by responsibility

## Entry points

`manage.py`, `config/wsgi.py` and `config/asgi.py` are standard Django entry points.
`config/settings.py` registers Django auth/sessions/admin/staticfiles plus three
project apps: `backend.accounts`, `backend.workspace`, and `database`.
The configured template/static directories point at `frontend/`.

| Concern | Implementation |
| --- | --- |
| HTML/frontend | Native Django Templates, `{% url %}`, `{% static %}`, CSRF form tokens, local CSS/JS |
| HTTP/backend | Django views, URLconfs, ModelForms, explicit permissions, messages, redirects, JSON responses |
| Identity | Custom AbstractUser, Django password hashing/session auth/validators, reset tokens, DB login throttle |
| Authorization | Workspace membership on every request; owner/manager/agent/viewer guards on the server |
| Business logic | `backend/workspace/services.py`; real algorithm calls, validation, transactions and events |
| Database | Django ORM models and included migrations; SQLite locally, PostgreSQL in production |
| Deployment | WSGI/Gunicorn, WhiteNoise manifest assets, Docker, explicit secrets/hosts, HTTPS settings |

JavaScript hides irrelevant workflow arguments, controls the phone menu,
dismisses notices, confirms archive/member removal, and copies invitation links.
Ordinary server forms perform all writes. The browser never writes directly to
SQLite and no in-memory global array substitutes for durable data.

## Model relationships

- `accounts.User`: Django AbstractUser; names, unique username, case-insensitive
  unique nonblank email, hashed password, standard admin permissions.
- `database.Workspace`: UUID, name/accent, queue/workflow JSON snapshots.
- `Membership`: User ↔ Workspace; one role per user/workspace pair.
- `Ticket`: belongs to Workspace; assignee/creator reference User; version,
  status, priority, due date, requester email, customer name, contact number,
  copies, paper size, status note and lifecycle timestamps.
- `Comment`: belongs to Ticket; author and timestamp; preserved on archive/restore.
- `Event`: belongs to Workspace; actor, kind, summary, JSON details and timestamp.
- `Invitation`: belongs to Workspace; UUID link, email-bound role, expiry,
  acceptance timestamp and revocation state.
- `LoginThrottle`: hashed username/IP key, failure count and ten-minute window.
- Standard Django session/admin/permission tables also exist.

Product models/migrations live under `database/`. The custom account model and
its first migration live in `backend/accounts/`, as required by Django's
swappable-user migration dependency. This is explicitly set by AUTH_USER_MODEL.

## Authentication and tenant boundaries

Anonymous requests to workspace routes redirect to Django sign-in. Registration
creates a real User and an owned Workspace atomically. The session stores the
selected workspace ID, but that ID alone grants no access: middleware resolves
an actual Membership for the authenticated User every time. A removed member's
existing session loses access on the next request. Switching requires membership.

Object routes query both object ID and current workspace. Assignee choices are
restricted to editing members of that workspace. Forms, detail notes, exports,
JSON inspection, queue actions and archive routes enforce the same boundary.
Staff administration is separate and never granted to ordinary accounts.

Invitations permit manager/agent/viewer roles, not owner injection. A signed-in
account must match the invited email; an expired, revoked or consumed link
cannot create a membership. Links are manually shared; SMTP is used only for
password reset when configured. Invitees may register using their invited email.

## Real queue path

1. POST `/queue/join/<id>/` requires editing permission.
2. `enqueue_ticket()` locks/reloads Workspace within an atomic transaction.
3. It reconstructs `ServiceQueue(workspace.queue_state)` and calls `enqueue()`.
4. The ORM saves `to_list()` in arrival order and records the actor/event.
5. GET `/queue/` reconstructs the class and calls `peek()`.
6. POST `/queue/serve/` calls `dequeue()`; the returned ID chooses the real Ticket.
7. Ticket status, assignment, queue snapshot and event commit together.

The browser's submitted expected-next value detects a stale visible selection,
including a repeated submission. It never overrides the class's selected ID.
The JSON/read API is at `/api/state/` and requires membership.

A waiting item must be an active To do Ticket in the current workspace. An item
cannot join twice. Status change/archive/explicit withdrawal remove its waiting
position while preserving other arrival order. Restoring does not auto-enqueue.

## Real singly linked-list path

POST `/workflow/` validates the operation/arguments and editing permission.
`operate_workflow()` locks Workspace, builds `SinglyLinkedList(saved_values)`,
calls the selected student method, verifies its public contract, and saves the
new snapshot and result event atomically. Read operations must not change values.

The inspector follows actual Node objects from head through next. It reports
flat storage honestly in the starter. N0/N1 are current traversal labels, not
persisted memory addresses. Rebuilding nodes on a subsequent HTTP request is
expected; rebuilding surviving nodes within an individual insertion/removal is
not the assignment target.

JSON snapshots are an O(n) persistence boundary. They do not replace the real
in-memory student data structure. End operations may be O(1), while the whole
request still performs reconstruction, serialization, database work and rendering.

## Concurrent updates

SQLite uses IMMEDIATE transactions to serialize writers; PostgreSQL uses real
`select_for_update()` row locks. Services acquire Workspace before reading or
mutating its snapshots. Failed student contracts roll back queue/ticket/event
writes together. Ticket edit forms carry an optimistic version; a stale form
gets a useful validation error rather than overwriting a newer update.

The local test suite verifies stale submissions, stale edits and rollback. It
does not claim a PostgreSQL concurrency/load test; deployment validation must
include the target database and infrastructure.

## Routes

| URL | Purpose |
| --- | --- |
| `/` | Live overview dashboard |
| `/requests/` | Paginated search, combined filters, sorting, list/board |
| `/requests/export/` | Workspace-filtered CSV; formula-like cells neutralized |
| `/items/new/`, `/items/<id>/edit/` | Django ModelForm create/edit |
| `/items/<id>/` | Details, conversation and per-request history |
| `/items/<id>/move/`, `/archive/`, `/restore/` | POST status/archive/restore actions under item routes |
| `/queue/`, `/queue/join/<id>/`, `/queue/withdraw/<id>/`, `/queue/serve/` | Queue page/actions |
| `/workflow/` | Saved process and student methods/inspector |
| `/reports/`, `/activity/`, `/archive/` | Metrics, event history, archived records |
| `/accounts/` | Login/register/logout, password/profile, teams, workspaces, invitations |
| `/settings/`, `/guide/`, `/api/state/` | Preferences, lab guide, authorized state inspection |
| `/health/` | Basic application + database readiness, no sensitive configuration |
| `/admin/` | Separate Django staff administration |

GET actions do not mutate tickets or consume invitations. Writes require POST
and Django CSRF protection. See the URLconfs for exact named route paths.

## Schema changes

Edit a model, update the ModelForm/view/template as necessary, run
`manage.py makemigrations` and `manage.py migrate`, and commit the new migration.
Do not edit already-applied initial migrations or distribute runtime databases.
Use a new extraction folder for this account-based edition; the older anonymous
edition's database requires a deliberate data migration rather than a file copy.
