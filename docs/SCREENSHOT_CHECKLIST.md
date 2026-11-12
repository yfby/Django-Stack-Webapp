# Screenshot checklist

Use this list before submitting. A checker output proves the data structures
behave correctly; screenshots or a short recording prove the **real pages** use
them and that the print-shop remix works on a phone-sized screen.

Do not include real customer details, passwords, invitation links or private
workspace data in submitted images. Use the six sample print jobs or disposable
test data.

## Already captured

| Capture | File | Status |
| --- | --- | --- |
| Dashboard at 375 x 900 | `evidence/after/dashboard_375.png` | Done |
| Board at 375 x 900 | `evidence/after/board_375.png` | Done |
| Print queue at 375 x 900 | `evidence/after/queue_375.png` | Done |
| Production flow at 375 x 900 | `evidence/after/workflow_375.png` | Done |
| Reports at 375 x 900 | `evidence/after/reports_375.png` | Done |
| Responsive CSS/viewport checks | `evidence/after/responsive_phase3.txt` | Done |
| Queue goal output | `evidence/after/phase4_check_queue.txt` | Done |
| Linked-list goal output | `evidence/after/phase4_check_linked_list.txt` | Done |
| Combined goal output | `evidence/after/phase4_check_activity.txt` | Done |
| Application suite output | `evidence/after/phase4_run_tests.txt` | Done |
| Live web-flow transcript | `evidence/after/phase4_web_flow.txt` | Done |

## Still needed — Activity A demonstration

Take these in order in one browser session. Refresh between each numbered step
so the saved state is visible.

- [ ] **Baseline failure:** before the fix (or using the untouched starter),
      create A, B and C as Queued jobs, join A, B, C, and capture the queue page
      showing the starter selecting the newest job instead of A. The saved text
      version is `evidence/before/check_queue_before.txt`; a page image is still
      useful for the submission.
- [ ] **After fix:** join A, B, C and capture the queue page with **NEXT UP: A**
      and the waiting order A, B, C.
- [ ] **Repeated peek:** reload twice and capture that the next job and order did
      not change.
- [ ] **Serve A:** click **Start next job** and capture the remaining order B, C
      plus A now marked **Printing**.
- [ ] **Join D:** add D and capture the order B, C, D with B next.
- [ ] **Empty case:** serve the rest, then submit an empty serve request and
      capture the friendly empty-queue message.
- [ ] **Checker:** capture or attach `CHECK_QUEUE.bat` output showing 10 passes.

## Still needed — Activity B demonstration

Start with an empty workflow (remove the initial example steps) and refresh
between operations.

- [ ] Append `10`, `20`, `30`; capture the values and the inspector.
- [ ] Prepend `5`; capture `[5, 10, 20, 30]`.
- [ ] Insert `15` at index `2`; capture `[5, 10, 15, 20, 30]`.
- [ ] Remove index `3`; capture the returned `20` and `[5, 10, 15, 30]`.
- [ ] Append `40`; capture `[5, 10, 15, 30, 40]`.
- [ ] Search/index `30` (returns `3`) and get/index `2` (returns `15`).
- [ ] Expand the inspector and capture **head N0**, **tail N4** and the final
      `next: None` with the actual node cards.
- [ ] Show a missing value (no change), a duplicate value, an invalid index and
      deletion of the only node.
- [ ] **Checker:** capture or attach `CHECK_LINKED_LIST.bat` output showing 17
      passes.

The text versions of these steps are in
`evidence/after/web_flow_phase1.txt` and `evidence/after/web_flow_phase2.txt`.
The Phase 3 sample uses `250 copies`, so the queue chip reads `250 copies`.

## Still needed — PrintPilot remix

- [ ] **New job form:** capture customer name, contact number, copies and paper
      size fields together.
- [ ] **Job detail:** capture the job-ticket panel and a saved live status note.
- [ ] **Status note permissions:** optional capture of the viewer notice or the
      validation message for an over-length note.
- [ ] **Reports:** capture the shop-floor summary showing status counts, total
      copies queued and paper sizes.
- [ ] **CSV export:** open the downloaded file and capture the customer, contact,
      copies, paper-size and status-note columns.
- [ ] **Brand:** capture the PrintPilot name, playful styling and printer
      favicon in the browser tab.

## Phone check

The five existing 375 x 900 captures cover the main pages. If your submission
requires a live phone capture, repeat these in a real browser at 375px:

- [ ] Open the off-canvas menu and navigate to another page.
- [ ] Confirm there is no sideways page scroll on the dashboard, board, queue,
      workflow, detail and reports pages.
- [ ] Confirm long job titles wrap instead of overflowing.
- [ ] Confirm the board columns stack and the queue/workflow panels stack.
- [ ] Confirm form labels and error messages remain readable.

## Suggested capture method

1. Start the app with `uv run python scripts/run.py serve --port 8001`.
2. Use a disposable account and workspace with sample data.
3. Use a browser window at 1440px for desktop shots and 375px for phone shots.
4. Crop to the relevant panel, but keep the page heading and job reference
   visible so each image is identifiable.
5. Store images under `evidence/after/` with descriptive names, for example
   `queue_after_join_abc.png` and `workflow_nodes_after_remove.png`.
6. Keep the raw checker output alongside the images.

## Re-run the text evidence

```bash
uv run python scripts/run.py tests
uv run python scripts/run.py queue
uv run python scripts/run.py linked
uv run python scripts/run.py all
```

Run them one at a time; the local development key is created on first use and
two simultaneous processes can race.
