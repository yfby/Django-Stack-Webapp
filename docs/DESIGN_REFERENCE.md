# PrintPilot design reference

## Direction

PrintPilot uses a playful print-shop language rather than the dark admin
dashboard of the earlier Flowdesk edition. The visual story is paper on a
workbench: cream sheets, dark ink outlines, offset print shadows, sticker-like
labels and bright spot colours. The interface is still a dense working desk, so
the theme changes presentation rather than the routes, permissions or data.

The earlier edition adapted the public previews of the **Free Dark Admin
Dashboards / Dashdark X** community kit. That reference informed the compact
KPI/chart layout and the persistent sidebar, but the current colours, shapes,
typography scale and print-shop components are a new remix. The original Figma
file and its exact geometry were not available for verification; no reference
screenshot or brand asset is redistributed as product UI.

## Design tokens

| Token | Value / treatment |
| --- | --- |
| Page background | Cream `#fff8ea` with a faint ink dot grid |
| Paper card | `#fffdf7` |
| Ink / border | `#241b3d` |
| Soft ink | `#453a63` |
| Muted text | `#6f6688` |
| Pink accent | `#ff4f87` |
| Teal accent | `#17c3ad` |
| Blue accent | `#4b7bff` |
| Yellow accent | `#ffc838` |
| Purple accent | `#8b5cf6` |
| Success / warning / danger | `#2fbf71` / `#ff8a3d` / `#e94b5f` |
| Radius | 18px cards, pill buttons, sticker labels |
| Shadow | Offset ink shadows (`4px 4px 0`, `7px 7px 0`) |
| Type | Local Inter variable font with system fallback |

## Components

- **Sidebar:** dark ink panel, yellow active item, queue badge and workspace
  switcher.
- **Top bar:** breadcrumb, shop sticker, search and account menu.
- **Dashboard:** four colour-coded KPI cards, a real SVG activity chart, status
  bars and a completion gauge.
- **Jobs:** bordered table on desktop; stacked cards below 620px.
- **Board:** three columns with paper cards, status dots and inline move form.
- **Queue:** a highlighted next-up panel, a waiting line with front/rear labels
  and job chips for copies and paper size.
- **Workflow:** four step cards and a horizontal node inspector showing real
  `head`, `next` and `tail` references.
- **Reports:** shop-floor summary tiles for status, total copies and paper sizes.
- **Detail:** job-ticket properties and a live status-note card.
- **Auth:** split story panel with a demo queue illustration and a paper card
  form.
- **Errors:** oversized paper card with the PrintPilot mark.

## Responsive behaviour

| Width | Behaviour |
| --- | --- |
| 1600px+ | Wider content padding and larger chart panels |
| 1250px | Narrower sidebar, tighter dashboard grid |
| 1040px | Two-column stats, single-column queue, stacked form sidebar |
| 800px | Off-canvas navigation with a menu button |
| 620px | Table becomes mobile cards, board/queue/workflow/details stack, search hides |
| 420px | One-column stats, full-width actions, tighter queue rows |

The page declares a minimum width of 320px. The supported narrow target used in
the evidence is 375 x 900.

## Source locations

- `frontend/static/app.css`: tokens, components, print-shop artwork and breakpoints.
- `frontend/static/favicon.svg`: printer illustration in the ink palette.
- `frontend/static/fonts/`: locally bundled Inter and its license.
- `frontend/templates/base.html`: shell, navigation, search and account menu.
- `frontend/templates/dashboard.html`: real charts and summary panels.
- `frontend/templates/queue.html`: print queue and FIFO inspector.
- `frontend/templates/workflow.html`: production steps and node inspector.
- `frontend/templates/reports.html`: shop-floor summary.
- `frontend/templates/detail.html`: job-ticket fields and status note.
- `backend/workspace/presentation.py`: view-only chart coordinates from real data.
- `backend/workspace/views.py`: workspace-scoped queries and summary values.

Existing Django forms, ORM models, permissions, CSRF protection, persistence and
student algorithm integration remain in place. The new job fields use migration
`0003_ticket_contact_number_ticket_copies_and_more.py`.

Inter source: https://github.com/rsms/inter
Font license: `frontend/static/fonts/LICENSE.txt` (SIL Open Font License).
