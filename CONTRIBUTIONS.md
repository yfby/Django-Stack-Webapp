# Contributions — PrintPilot

> **Team action required:** replace any remaining bracketed placeholders below
> with the real names and roles. Delete rows that do not apply. A solo submission
> can keep one row and list all areas. Every member must be able to explain one
> meaningful contribution, not just name a file.

## Contribution table

| Member | Role | Specific files / changes | Demonstration evidence |
| --- | --- | --- | --- |
| Ybanez | Team lead / integration | Coordinated phases, kept `challenge/` and `tests/` unchanged, reviewed the integration between views, services and the DSA classes | `evidence/after/phase4_integrity.txt`; `evidence/after/phase4_web_flow.txt` |
| Bernales | Backend / DSA | Implemented `ServiceQueue` with `collections.deque`; verified FIFO, empty cases and saved-state reload | `backend/dsa/queue.py`; `evidence/after/phase4_check_queue.txt`; `evidence/after/web_flow_phase1.txt` |
| Edralin | Backend / DSA | Implemented `SinglyLinkedList` with real `Node` links, `head`, `tail`, cached `_size`, edge cases and identity-preserving mutations | `backend/dsa/singly_linked_list.py`; `evidence/after/phase4_check_linked_list.txt`; `evidence/after/web_flow_phase2.txt` |
| Go | Frontend / UI | Rebuilt the print-shop theme, navigation copy, responsive layouts and printer favicon; checked 375px screens | `frontend/templates/`, `frontend/static/app.css`, `frontend/static/favicon.svg`; `evidence/after/*_375.png`; `evidence/after/responsive_phase3.txt` |
| Banaag | Database / features | Added customer, contact, copies, paper-size and status-note fields with migration; wired forms, detail page, CSV and reports | `database/models.py`, `database/migrations/0003_*.py`, `backend/workspace/{forms,services,views}.py`; `evidence/after/phase4_web_flow.txt` |
| [Member 6] | QA / documentation | Ran all suites, collected before/after evidence, checked migrations and ignored files, wrote README and explanation | `README.md`, `EXPLANATION.md`, `CONTRIBUTIONS.md`, `docs/SCREENSHOT_CHECKLIST.md`, `evidence/` |

## Evidence by area

| Area | Main files | Verification |
| --- | --- | --- |
| FIFO queue | `backend/dsa/queue.py` | 10 queue goal checks; live A/B/C -> serve A -> join D flow |
| Linked list | `backend/dsa/singly_linked_list.py` | 17 linked-list goal checks; node inspector shows head/tail/final `None` |
| Print-job fields | `database/models.py`, `backend/workspace/forms.py`, migration `0003` | Job created with customer, contact, 250 copies and A6 paper |
| Status note | `backend/workspace/views.py`, `backend/workspace/forms.py`, `frontend/templates/detail.html` | Save, clear, viewer rejection and over-length rejection |
| Reports and CSV | `backend/workspace/views.py`, `frontend/templates/reports.html` | Shop-floor summary, copies, paper sizes and new CSV columns |
| Theme and phone layout | `frontend/static/app.css`, `frontend/templates/` | 14 responsive checks; five 375 x 900 captures |
| Setup and tooling | `pyproject.toml`, `.python-version`, `uv.lock`, batch launchers | `uv sync`, tests and launchers still work |
| Final QA | Evidence folder | 57 + 10 + 17 + 84 checks; migration drift clean; no tracked secrets or local data |

## What each role can explain

Use these prompts to prepare a short spoken explanation. Do not read the table
aloud; demonstrate the part you actually did.

- **Team lead / integration:** how the browser form reaches a Django view, then
  a service, then the student class, and how the result is saved and reloaded.
- **Queue:** why `popleft()` is O(1), why `pop(0)` is not, and what happens when
  the queue is empty.
- **Linked list:** where `head`, `tail` and `_size` change for prepend, append,
  middle removal and deletion of the only node, and why `to_list()` is not a
  hidden backing list.
- **Frontend:** why the table becomes cards on a phone, how the sidebar becomes
  off-canvas and why the page still works at 375px.
- **Database / features:** why the new fields are optional, what the migration
  changes, and how the status note is saved without changing the job status.
- **QA / documentation:** one failure found, how it was investigated, the fix
  and the exact command or page used to verify it.

