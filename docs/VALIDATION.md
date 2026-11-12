# Validation — PrintPilot

## Scope

This file records what was actually checked for the PrintPilot remix. It does
not claim a live public deployment, formal accessibility certification, load
testing or an independent security audit.

The instructor-approved concept is a print-shop desk built on the supplied
Flowdesk starter. Authentication, workspace isolation, role permissions and the
two assessed data-structure integrations remain in place.

## Application and goal checks

| Suite | Untouched starter | This repository |
| --- | ---: | ---: |
| Django application — 57 checks | 57 pass | 57 pass |
| Queue goal — 10 checks | 3 pass, 7 intentional failures | 10 pass |
| Linked-list goal — 17 checks | 10 pass, 7 intentional failures | 17 pass |
| Combined — 84 checks | 70 pass, 14 intentional failures | 84 pass |

Commands:

```text
uv run python scripts/run.py tests
uv run python scripts/run.py queue
uv run python scripts/run.py linked
uv run python scripts/run.py all
```

Saved output is in `evidence/after/phase4_run_tests.txt`,
`phase4_check_queue.txt`, `phase4_check_linked_list.txt` and
`phase4_check_activity.txt`. The untouched baseline output is in
`evidence/before/`.

The student files are no longer the unfinished starter: both assessed activities
are implemented. The separate goal suites still test the public contracts rather
than the implementation shape alone.

## Browser and feature verification

The live-flow script (`evidence/after/phase4_web_flow.txt`) uses Django's test
client against real URLs, views, forms, templates and SQLite data. It confirms:

- PrintPilot branding and six sample print jobs with customer, contact, copies
  and paper fields.
- `Queued` / `Printing` / `Ready` labels while stored keys remain
  `todo` / `doing` / `done`.
- Job creation with customer, contact, 250 copies and A6 paper through the real
  form.
- Status note save, clear, viewer rejection and over-length rejection.
- Reports shop-floor summary, total copies and paper sizes.
- CSV export columns for the new fields.
- Queue join and serve, with the served job becoming **Printing**.
- Production flow showing real node cards and `/api/state/` exposing the new
  fields.
- Stylesheet breakpoints and printer favicon.

### Responsive layout

`evidence/after/responsive_phase3.txt` records 14 passing viewport and CSS
checks. Firefox headless rendered five authenticated pages at 375 x 900:
dashboard, board, queue, workflow and reports. The PNG files are in
`evidence/after/`. The stylesheet defines breakpoints at 1250px, 1040px, 800px,
620px and 420px, with a minimum supported page width of 320px.

These are layout captures, not a substitute for the interactive demonstration
screenshots listed in `docs/SCREENSHOT_CHECKLIST.md`.

## Integrity

`evidence/after/phase4_integrity.txt` records:

- `manage.py check`: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- No diff in `challenge/` or `tests/` during the final phase.
- No tracked `.env`, `.venv`, `__pycache__`, SQLite database or generated
  development key.
- `database/data/` and `.venv/` are ignored by git.

The visible product name is PrintPilot. Internal compatibility names
(`FLOWDESK_DATA_DIR`, `database/data/flowdesk.sqlite3`, the launcher requirement
marker and the sign-in throttle salt) were intentionally retained so existing
local data and scripts continue to work.

## Limits

- Docker/PostgreSQL infrastructure and external SMTP were not available in the
  build environment, so a live production deployment is not claimed.
- The local dev-key file is generated at runtime and excluded from git.
- The classroom waiting line is capped at 100 jobs and the workflow at 40 steps.
- No attachment hosting, external customer portal, email ingestion, billing or
  real-time push is included.
- The interactive before/after demonstration captures remain a submission task;
  see `docs/SCREENSHOT_CHECKLIST.md`.
