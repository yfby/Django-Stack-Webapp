# Phase 4 — final checks and evidence

Date: 2026-11-12
Environment: Python 3.12.16, Django 5.2.18, managed with `uv`

## Automated suites

Run sequentially from the project root so the local development key is not
created by two processes at once.

| Command | Result | Evidence |
| --- | --- | --- |
| `uv run python scripts/run.py tests` | 57 passed | `phase4_run_tests.txt` |
| `uv run python scripts/run.py queue` | 10 passed | `phase4_check_queue.txt` |
| `uv run python scripts/run.py linked` | 17 passed | `phase4_check_linked_list.txt` |
| `uv run python scripts/run.py all` | 84 passed | `phase4_check_activity.txt` |

The `all` result combines the 57 application tests with the 27 queue and
linked-list goal tests. The untouched `challenge/` and `tests/` suites show no
changes in the final integrity check.

## Website flows

`phase4_web_flow.txt` records the end-to-end checks against the real Django
views, forms and SQLite data:

- PrintPilot branding and six seeded print jobs with customer, contact, copies
  and paper fields.
- `Queued` / `Printing` / `Ready` labels while status keys remain
  `todo` / `doing` / `done`.
- Job creation through the real form with 250 copies on A6 paper.
- Status note save, clear, viewer rejection and over-length rejection.
- Reports shop-floor summary, total copies and paper sizes.
- CSV export columns for the new print-job fields.
- Print queue join and serve changing the real job status.
- Production flow exposing the real linked-node chain and state API values.
- Stylesheet breakpoints and printer favicon.

## Integrity

`phase4_integrity.txt` records:

- `manage.py check`: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- No diff in `challenge/` or `tests/`.
- No tracked `.env`, `.venv`, `__pycache__`, SQLite database or development
  key.
- Local runtime files (`database/data/flowdesk.sqlite3` and the generated
  development key) are ignored by git.

## Responsive evidence

Earlier Phase 3 captures remain current because the stylesheet and templates
were unchanged in Phase 4:

- `responsive_phase3.txt` — 14 CSS and viewport checks passed.
- `dashboard_375.png`, `board_375.png`, `queue_375.png`, `workflow_375.png`,
  `reports_375.png` — Firefox headless renders at 375 x 900.
