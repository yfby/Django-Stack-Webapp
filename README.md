# Flowdesk — Django service desk + data-structure lab

A working team service desk built with **Django 5.2.18, Django Templates,
HTML/CSS/JavaScript, and the Django ORM**. SQLite runs locally; the supplied
production configuration uses PostgreSQL, Gunicorn, and WhiteNoise.

The product includes real accounts, workspace membership, role permissions,
request assignments, conversation notes, queue operations, a workflow editor,
activity history, reports, exports, and responsive navigation. It is also a
classroom activity: **two intentionally unfinished Python implementations
control two actual features**. The rest of the application works before students
solve them. The separate instructor archive contains the completed algorithms.


## Dark design edition

The interface now follows the navy panels, purple/cyan charts, bordered cards,
sidebar selection marker, dark tables and Kanban styling of the supplied
**Free Dark Admin Dashboards / Dashdark X** reference. Account screens, forms,
queue, workflow, reports, activity, archive and phone layouts share the theme.
Inter is bundled locally with its license, so no font CDN is required.

This edition uses the same account/database schema as the previous Flowdesk
fullstack ZIP. Existing users can follow `UPDATE_DESIGN.txt` to replace source
files while retaining their database and environment. If port 8000 is already
busy, run `START.bat --port 8001` and open http://127.0.0.1:8001/.

See `docs/DESIGN_REFERENCE.md` for the visual source, design tokens and scope.

## Run it

Extract the complete ZIP into a **new folder**. Install Python 3.12 or 3.13
(Python 3.10–3.14 is supported), then on Windows:

1. Double-click **SETUP.bat** (once). It creates `.venv`, installs Django and runs migrations.
2. Double-click **START.bat**. It starts the server and opens
   http://127.0.0.1:8000/.

 **Create your account** on the sign-in screen. Choose a team
name and optionally include the six sample requests. Your account owns that
workspace. There are no shipped accounts or shared default passwords.

Keep the terminal open; Ctrl+C stops the local server. First setup needs
internet to download dependencies. No Node.js, API key, cloud account, separate
frontend server, or local database server is needed. No environment activation
or PowerShell policy change is required.

macOS / Linux:

```bash
sh setup.sh
sh start.sh
```

Manual Windows setup/start is also available:

```powershell
py -3.12 scripts\bootstrap.py
.\.venv\Scripts\python.exe scripts\run.py serve
```

### Using uv (fast alternative)

If you use [uv](https://docs.astral.sh/uv/), you do not need `SETUP.bat`:

```powershell
uv sync
uv run python manage.py migrate
uv run python scripts/run.py serve --port 8001
```

Useful uv commands:

```powershell
uv run python scripts/run.py tests
uv run python scripts/run.py queue
uv run python scripts/run.py linked
uv run python scripts/run.py all
```

`pyproject.toml` pins Django 5.2.18 and supports Python 3.12+. `uv sync`
creates the same `.venv` that `SETUP.bat` and `START.bat` expect, so the batch
launchers keep working after a uv sync.

## What you can actually do

- **Overview:** live counts, seven-day request volume, due work, recent events,
  and current team workload. Metrics are calculated from your database.
- **Requests:** create/edit, assign agents, add requester email and due dates,
  combine search/status/priority/assignee filters, sort, paginate, or use a board.
- **Request details:** team notes, status changes, properties and action history.
  Stale edit protection prevents an older form overwriting a newer update.
- **Service queue:** enqueue, withdraw, inspect the actual selection, and start
  the next request. Starting assigns it to the signed-in agent. Stale browser
  submissions cannot accidentally start a second request.
- **Workflow:** insert, append, prepend, remove, read and search process steps;
  view saved return values and inspect the actual data structure.
- **Reports:** live category and priority counts, completion rate, unassigned
  work, and CSV export with spreadsheet-formula neutralization.
- **Team:** owner-created, email-bound invitation links, seven-day expiry,
  acceptance, revocation and member removal. No invitation email is sent
  automatically; the owner copies and shares the private link.
- **Accounts:** registration, sign-in/out, password change/reset and profile.
  Passwords are hashed by Django; failed sign-in attempts are throttled.
- **Workspaces:** create and switch between teams; membership is rechecked on
  every request. One account can work on several teams.
- **Archive:** restore individual requests with their details and notes intact.
- **Administration:** a configured Django admin with search/filter support.

| Role | Requests, queue, notes, workflow | Workspace settings | Team membership |
| --- | --- | --- | --- |
| Owner | Edit | Edit | Manage |
| Manager | Edit | Edit | Read |
| Agent | Edit | No access | Read |
| Viewer | Read/export | No access | Read |

Normal accounts cannot access Django admin. To create a separate administrator:
`manage.py createsuperuser` using `.venv` Python. Visit `/admin/` afterwards.

## Navigate the source

| Folder | Responsibility | Main files |
| --- | --- | --- |
| `frontend/` | Django HTML, product interface, responsive styles, small browser interactions | `templates/`, `static/app.css`, `static/app.js` |
| `backend/accounts/` | Django auth, account model, registration, profile, invitations and teams | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `backend/workspace/` | HTTP routes, forms, permissions, business operations and atomic writes | `views.py`, `forms.py`, `services.py`, `permissions.py` |
| `backend/dsa/` | The two student-editable algorithm modules | `queue.py`, `singly_linked_list.py` |
| `database/` | Product ORM models, migrations, admin and generated local data | `models.py`, `migrations/`, `data/` |
| `config/` | Django settings, production settings, URL routing, WSGI and ASGI | `settings.py`, `production.py`, `urls.py` |
| `tests/` | Application, identity, permission and integration checks | `test_application.py`, `test_product.py`, `test_contracts.py` |
| `challenge/` | Student goal checks | `test_queue.py`, `test_linked_list.py` |
| `docs/` | Teaching instructions, architecture, setup, deployment and validation | `STUDENT_ACTIVITY.md`, `ARCHITECTURE.md`, `DEPLOYMENT.md` |
| `scripts/` | Local setup, launchers and production entry point | `bootstrap.py`, `run.py`, `production_start.py` |

This is one server-rendered Django application. Forms reach Django views;
services call Python classes, persist through the ORM, and render Django
Templates. JavaScript enhances interactions; it does not impersonate the backend.

## Preserve the activity

| Activity | Student file | Working baseline | Required modification |
| --- | --- | --- | --- |
| A — Queues | `backend/dsa/queue.py` | Selects the newest waiting arrival | Efficient FIFO: earliest waiting arrival leaves first |
| B — Singly linked lists | `backend/dsa/singly_linked_list.py` | Functional methods backed by a Python list | Real `Node`, `head`, `tail`, `next` and cached `_size` |

For A, create A/B/C as To do requests; join A/B/C in order. The starter selects C.
For B, open Workflow and expand **Data structure inspector**. The starter reports
flat storage. Implement the algorithms, then repeat the same web actions.
The actual ticket selected and actual node references must change.

Full contracts, edge cases, demonstrations and rubric: `docs/STUDENT_ACTIVITY.md`.

## Checks

On Windows: `RUN_TESTS.bat`, `CHECK_QUEUE.bat`, `CHECK_LINKED_LIST.bat`,
`CHECK_ACTIVITY.bat`, and `RUN_ALL_CHECKS.bat`.

Native Django equivalents (prefix with `.venv` Python):

```text
manage.py check_application
manage.py check_queue
manage.py check_linked_list
manage.py check_activity
manage.py test tests challenge --noinput
```

| Suite | Untouched student starter | Completed instructor implementation |
| --- | --- | --- |
| Application — 57 checks | 57 pass | 57 pass |
| Queue goal — 10 checks | 3 pass, 7 intentional failures | 10 pass |
| Linked-list goal — 17 checks | 10 pass, 7 intentional failures | 17 pass |
| Combined — 84 checks | 14 intentional goal failures | 84 pass |

`manage.py test` discovers the unfinished goals too. Use `check_application`
when verifying the installation. Do not edit goal tests to hide failures.

## Sharing a local classroom server

`START_LAN.bat` prints a link for devices on the same Wi-Fi. Each student creates
their own account/workspace. Invited teammates share a workspace across devices;
logging in to the same account also restores the same memberships and data.
This development server is for a trusted local classroom network. HTTPS internet
hosting uses the separate deployment setup below.

## Production files and limits

`Dockerfile`, `compose.yaml`, `.env.example`, `requirements-production.txt`, and
`config/production.py` provide a PostgreSQL/Gunicorn/WhiteNoise deployment path.
Use `docs/DEPLOYMENT.md` for HTTPS, environment configuration, migrations,
maintenance and backups. Do not deploy the intentionally incorrect student
algorithms as a live customer queue; apply the instructor implementations first.

Application tests, production security checks and static collection were run.
Docker/PostgreSQL infrastructure and external SMTP were unavailable in the
build environment, so a live production deployment is **not** claimed. This is
an implemented service-desk project, not a claim of independent security audit,
load certification, or a complete commercial customer-support platform.

The classroom scope caps the waiting line at 100 requests and the workflow at
40 steps. Ticket lists and archive/history paginate. There is no billing,
external requester portal, attachment hosting, email ingestion or real-time
push; team members refresh after another person changes data.

## Your data

Local SQLite and the generated development key live in `database/data/`.
Back up that directory and keep it private. Runtime data, keys and environments
are excluded from the ZIP. This dark design update uses the same account schema as the previous fullstack
ZIP; follow UPDATE_DESIGN.txt to retain that database. The older anonymous lab
uses a different identity design and needs an explicit data migration.
