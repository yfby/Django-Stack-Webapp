# PrintPilot — print-shop queue and workflow lab

PrintPilot is a small print-shop desk built with **Django 5.2.18, Django
Templates, HTML/CSS/JavaScript, and the Django ORM**. A shop can register jobs,
record the customer and print details, move work through production, serve the
waiting line in arrival order, and review a shop-floor summary.

The project is a remix of the supplied **Flowdesk** data-structure lab. The
printing-shop concept was approved by the instructor. Authentication, role
permissions and workspace isolation are unchanged; the two required
data-structure activities remain connected to real pages:

- **Activity A — FIFO print queue:** `backend/dsa/queue.py`
- **Activity B — real singly linked workflow:** `backend/dsa/singly_linked_list.py`

SQLite runs locally. The supplied production configuration uses PostgreSQL,
Gunicorn and WhiteNoise.

## The print-shop idea

A small print or copy shop receives files by email, chat or at the counter.
Staff need one place to answer:

- Which job is next, in the order it arrived?
- Who is the customer, and how can the shop contact them?
- How many copies, on what paper size, and what is happening right now?
- Which production step is the job on: receive, print, cut or pickup?
- What did the shop finish this week, and how much paper is in play?

PrintPilot keeps the job ticket, the waiting line and the production flow in one
Django application. The interface is intentionally playful — paper colours,
ink outlines, sticker-like labels and offset shadows — while the buttons,
permissions and data remain those of a working team app.

### What the remix adds

| Area | What changed |
| --- | --- |
| Brand | PrintPilot naming, print-shop navigation, printer favicon and a bright paper-and-ink theme |
| Job ticket | Customer name, contact number, copies and paper size on create/edit and detail pages |
| Live status note | A separate short note per job, saved through its own form and shown as a "live note" card |
| Reports | Shop-floor summary with status counts, total copies queued, paper sizes in play and priority work |
| Export | CSV columns for customer, contact number, copies, paper size and status note |
| Queue | Print-queue language, job chips and a FIFO inspector, backed by the real `ServiceQueue` |
| Workflow | `Receive file -> Print -> Cut -> Pickup` steps, backed by the real linked-node inspector |
| Phone layout | Off-canvas navigation, card lists instead of wide tables, stacked queue/workflow/board layouts |

The six sample jobs created for a new workspace are print jobs, not generic
support requests. Status keys stay `todo`, `doing` and `done`; the visible
labels are **Queued**, **Printing** and **Ready**.

## Screenshots

All five captures are Firefox headless renders at **375 × 900 CSS pixels** and
live in `evidence/after/`:

| Page | File | What it shows |
| --- | --- | --- |
| Dashboard | `dashboard_375.png` | Brand, print-job counts, due work, recent shop activity and workload |
| Board | `board_375.png` | Queued / Printing / Ready columns at phone width |
| Print queue | `queue_375.png` | Next-up job, waiting line and queue actions |
| Production flow | `workflow_375.png` | Receive file -> Print -> Cut -> Pickup steps and node inspector |
| Reports | `reports_375.png` | Shop-floor summary, copies and paper sizes |

`evidence/after/responsive_phase3.txt` records the viewport and CSS checks.

## Run it

Extract the complete ZIP into a **new folder**. Install Python 3.12 or 3.13
(Python 3.10–3.14 is supported), then on Windows:

1. Double-click **SETUP.bat** (once). It creates `.venv`, installs Django and runs migrations.
2. Double-click **START.bat**. It starts the server and opens
   http://127.0.0.1:8000/.

**Create your account** on the sign-in screen. Choose a print-shop name and
optionally include the six sample print jobs. Your account owns that workspace.
There are no shipped accounts or shared default passwords.

Keep the terminal open; Ctrl+C stops the local server. First setup needs
internet to download dependencies. No Node.js, API key, cloud account, separate
frontend server, or local database server is needed.

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

```bash
uv sync
uv run python manage.py migrate
uv run python scripts/run.py serve --port 8001
```

Useful uv commands:

```bash
uv run python scripts/run.py tests
uv run python scripts/run.py queue
uv run python scripts/run.py linked
uv run python scripts/run.py all
```

`pyproject.toml` pins Django 5.2.18 and supports Python 3.12+. `uv sync`
creates the same `.venv` that `SETUP.bat` and `START.bat` expect, so the batch
launchers keep working after a uv sync.

## Daily flow

1. **Create a job** under Print jobs. Add the title, description, customer,
   contact number, copies, paper size, priority and due date.
2. **Join the print queue** when the file is ready. The queue records arrival
   order; it does not re-sort by priority.
3. **Start the next job.** The earliest waiting job leaves the queue, is assigned
   to the signed-in agent, and becomes **Printing**.
4. **Update the live status note.** Use it for proof approval, stock changes or
   a hand-off message.
5. **Move the production flow.** The workflow uses the text steps
   `Receive file -> Print -> Cut -> Pickup`; existing index-based operations
   still work because steps are stored by position.
6. **Finish and review.** A done job is **Ready** in the board and reports.

Archiving a job or moving it out of `todo` cancels its waiting position.
Restoring an archived job does not automatically rejoin the queue.

## Roles

| Role | Jobs, queue, notes, workflow | Workspace settings | Team membership |
| --- | --- | --- | --- |
| Owner | Edit | Edit | Manage |
| Manager | Edit | Edit | Read |
| Agent | Edit | No access | Read |
| Viewer | Read/export | No access | Read |

Normal accounts cannot access Django admin. To create a separate administrator:
`manage.py createsuperuser` using `.venv` Python. Visit `/admin/` afterwards.

## Data-structure activities

### Activity A — FIFO print queue

`ServiceQueue` uses `collections.deque`. `enqueue()` appends at the rear;
`dequeue()` and `peek()` operate at the front. Every end operation is O(1), and
`to_list()` returns a new arrival-order list for saving.

The real path is:

```text
Join queue form
  -> backend/workspace/views.py
  -> services.enqueue_ticket()
  -> ServiceQueue(workspace.queue_state).enqueue(ticket.id)
  -> workspace.queue_state = queue.to_list()
  -> SQLite

Start next job
  -> services.serve_next()
  -> ServiceQueue(workspace.queue_state).dequeue()
  -> ticket.status = "doing"
  -> SQLite
```

The page reconstructs the queue on every request, so a refresh does not lose
arrival order. Starting an empty queue shows a friendly message rather than a
crash.

### Activity B — real singly linked production flow

`SinglyLinkedList` stores `Node` objects with `data` and `next`. It keeps
`head`, `tail` and a cached `_size`; the final node's `next` is always `None`.
Insertion and removal preserve the identity of surviving nodes, and
`to_list()` traverses the real chain instead of reading a hidden backing list.

The Workflow page records each operation through `operate_workflow()`, saves a
snapshot of the values, and renders an inspector that follows actual
`head -> next -> ... -> None` references. The inspector is a teaching aid; the
goal checks also test representation, mutation identity, duplicates, missing
values, invalid indices and the sole-node case.

Full contracts and required demonstrations: `docs/STUDENT_ACTIVITY.md`.
The written before/after explanation is in `EXPLANATION.md`.

## Navigate the source

| Folder | Responsibility | Main files |
| --- | --- | --- |
| `frontend/` | Django HTML, product interface, responsive styles, small browser interactions | `templates/`, `static/app.css`, `static/app.js` |
| `backend/accounts/` | Django auth, registration, profile, invitations and teams | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `backend/workspace/` | HTTP routes, forms, permissions, business operations and atomic writes | `views.py`, `forms.py`, `services.py`, `permissions.py` |
| `backend/dsa/` | The two assessed algorithm modules | `queue.py`, `singly_linked_list.py` |
| `database/` | Product ORM models, migrations, admin and generated local data | `models.py`, `migrations/`, `data/` |
| `config/` | Django settings, production settings, URL routing, WSGI and ASGI | `settings.py`, `production.py`, `urls.py` |
| `tests/` | Application, identity, permission and integration checks | `test_application.py`, `test_product.py`, `test_contracts.py` |
| `challenge/` | Separate goal checks for the two activities | `test_queue.py`, `test_linked_list.py` |
| `docs/` | Teaching instructions, architecture, setup, deployment and evidence | `STUDENT_ACTIVITY.md`, `ARCHITECTURE.md` |
| `scripts/` | Local setup, launchers and production entry point | `bootstrap.py`, `run.py`, `production_start.py` |

This is one server-rendered Django application. Forms reach Django views;
services call the Python classes, persist through the ORM, and render Django
Templates. JavaScript enhances interactions; it does not impersonate the backend.

## Checks and evidence

On Windows: `RUN_TESTS.bat`, `CHECK_QUEUE.bat`, `CHECK_LINKED_LIST.bat`,
`CHECK_ACTIVITY.bat`, and `RUN_ALL_CHECKS.bat`.

Native Django equivalents:

```text
manage.py check_application
manage.py check_queue
manage.py check_linked_list
manage.py check_activity
manage.py test tests challenge --noinput
```

Final results in this repository:

| Suite | Result | Evidence |
| --- | ---: | --- |
| Application — 57 checks | 57 pass | `evidence/after/phase4_run_tests.txt` |
| Queue goal — 10 checks | 10 pass | `evidence/after/phase4_check_queue.txt` |
| Linked-list goal — 17 checks | 17 pass | `evidence/after/phase4_check_linked_list.txt` |
| Combined — 84 checks | 84 pass | `evidence/after/phase4_check_activity.txt` |

The end-to-end website flow is recorded in
`evidence/after/phase4_web_flow.txt`, integrity checks in
`evidence/after/phase4_integrity.txt`, and a short index in
`evidence/after/phase4_summary.md`.

The untouched starter intentionally fails 7 queue goal checks and 7
linked-list goal checks. The saved baseline output is in `evidence/before/`.
Do not edit the goal tests to hide failures.

## Production files and limits

`Dockerfile`, `compose.yaml`, `.env.example`, `requirements-production.txt`, and
`config/production.py` provide a PostgreSQL/Gunicorn/WhiteNoise deployment path.
Use `docs/DEPLOYMENT.md` for HTTPS, environment configuration, migrations,
maintenance and backups.

This classroom build is not a claim of a live production deployment, load
certification, accessibility certification, or an independent security audit.
Docker/PostgreSQL infrastructure and external SMTP were unavailable in the
build environment. The classroom scope caps the waiting line at 100 jobs and the
workflow at 40 steps. There is no billing, external customer portal, attachment
hosting, email ingestion or real-time push; teammates refresh after another
person changes data.

## Your data

Local SQLite and the generated development key live in `database/data/`.
Back up that directory and keep it private. Runtime data, keys, caches and
virtual environments are excluded from git. The internal data-directory
variable, database filename and launcher marker keep their original `flowdesk`
names so existing local data and scripts continue to work; the visible product
name is PrintPilot.
