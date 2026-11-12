# Local setup and troubleshooting

1. Install Python 3.12/3.13 and add it to PATH; 3.10–3.14 is supported.
2. Extract the full ZIP into a NEW folder. Do not launch from inside an archive.
3. Windows: double-click SETUP.bat once, then START.bat. macOS/Linux: `sh setup.sh`, then `sh start.sh`.
4. Open http://127.0.0.1:8000/, create an account and choose a print-shop name.
5. Keep the terminal open while using the app; Ctrl+C stops it.

SETUP.bat downloads Django into this project's `.venv`, runs migrations and
checks configuration (needs internet, run once). START.bat only starts the
server and tells you to run SETUP.bat if setup has not been done. No Node.js or PowerShell activation is needed.

## Commands

Use `.venv\Scripts\python.exe` on Windows; `.venv/bin/python` on macOS/Linux.
Append `manage.py check_application` to check the working application. Append
`scripts/run.py queue`, `linked`, `activity` or `all` for student goals.
Native `manage.py check_queue`, `check_linked_list`, `check_activity` also work.
In the untouched starter, `manage.py test` discovers the unfinished goals and
fails until they are implemented. This completed repository passes all 84.

With uv, the equivalent commands are:

```bash
uv sync
uv run python manage.py migrate
uv run python scripts/run.py tests
uv run python scripts/run.py queue
uv run python scripts/run.py linked
uv run python scripts/run.py all
uv run python scripts/run.py serve --port 8001
```

## Common problems

| Symptom | Action |
| --- | --- |
| Python not found | Reinstall Python with PATH enabled, or use `py -3.12 scripts\bootstrap.py` |
| ModuleNotFoundError: django | Run setup and use the project's `.venv` Python |
| Port 8000 busy | Stop the older terminal/server or run `START.bat --port 8001` |
| Environment moved with an old folder | Rename/remove only `.venv` and rerun setup; keep `database/data/` |
| Installer cannot download | Restore internet access and rerun setup; downloads are needed only initially |
| Login required | Create your own account or sign in; there are no default credentials |
| Wrong-password lockout | Wait ten minutes after five failures; this is per username/IP |
| Forgot password in local development | Request reset; the link is printed in the server terminal by Django's console email backend |
| Invitation belongs to another email | Sign in/register using the invited address, then revisit the original link |
| Expired/revoked invitation | Ask the owner to create a new link; invitations last seven days |
| Viewer cannot edit | Ask the owner to change your role in Team members |
| Save says someone updated the print job | Reload before reapplying your edit; the stale form was intentionally rejected |
| Queue changed since page opened | Review the refreshed next request and start it again |
| Queue/node goal failures | Expected in the untouched starter: implement the assigned classes, not the test files |
| Syntax/import errors after editing | Read the traceback and fix the Python module; these are not expected goal failures |
| Student traversal freezes | Fix the terminating `next = None` link; portable checkers stop after 120 seconds |
| Old anonymous-edition database fails | Use a fresh extraction; account-model conversion needs an explicit migration plan |

## Phone and team use

Use START_LAN.bat and the printed IPv4 link on devices on the same trusted Wi-Fi.
Allow Python through the local firewall only for your intended classroom network.
A phone's localhost is the phone, not the teacher's computer. Both devices use
the teacher computer's printed IPv4 address and selected port.

Students register their own accounts/workspaces. Shared workspace access comes
from an invitation, not a shared browser cookie. Tabs and devices signed into
the same account see that account's memberships. Use the workspace switcher to
move between authorized teams. Refresh after another teammate makes changes.

## Local data and administration

Back up `database/data/` with the server stopped. It contains SQLite and the local
development key. Do not include it in student submissions or published source.
Create a separate staff account with `manage.py createsuperuser` when needed;
normal registered users do not become staff. This local server uses HTTP for
classroom development. Public HTTPS hosting uses `docs/DEPLOYMENT.md`.
