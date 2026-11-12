# Explanation — PrintPilot remix, queue and linked list

## Concept and users

PrintPilot is a print-shop desk for a small print or copy shop. The people who
use it are counter staff, print operators and a shop owner. They receive files
by email, chat or in person and need to know which job is next, what the
customer ordered, how far the job has progressed and what the shop has finished.

The original Flowdesk starter was a general service desk. The remix keeps its
accounts, workspace isolation and role permissions but changes the product
language, fields, sample data, workflow steps, reports and visual design to
match a print shop. The concept was approved by the instructor.

The visible steps are **Queued**, **Printing** and **Ready**. The stored keys
remain `todo`, `doing` and `done` so the existing database, tests and
permission rules keep working.

## Before and after

| Area | Before | After |
| --- | --- | --- |
| Product | Generic service desk | PrintPilot print-shop desk |
| Job fields | Title, description, category, priority, due date | Adds customer name, contact number, copies and paper size |
| Per-job detail | Description and comments | Adds a separate live status note and a job-ticket panel |
| Status words | To do / In progress / Done | Queued / Printing / Ready (same keys) |
| Reports | Category, priority and completion counts | Adds total copies queued and paper sizes in play |
| Export | Core job columns | Adds customer, contact, copies, paper and status note |
| Workflow copy | Generic process steps | `Receive file -> Print -> Cut -> Pickup` |
| Queue | Newest arrival was served by the starter | Earliest arrival is served in O(1) |
| Workflow storage | Flat Python list in the starter | Real `Node` objects with `head`, `tail` and `next` |
| Visual design | Dark admin dashboard | Cream paper, ink outlines, colourful stickers and offset shadows, usable at 375px |

## Activity A — FIFO print queue

### Representation

`ServiceQueue` wraps a `collections.deque`. A deque supports O(1) insertion at
the rear and O(1) removal from the front. The constructor copies the incoming
snapshot, so saving or reusing the caller's list cannot mutate a queue that is
already in memory.

```python
def enqueue(self, value):
    self._items.append(value)

def dequeue(self):
    if self.is_empty():
        raise IndexError("The service queue is empty.")
    return self._items.popleft()

def peek(self):
    if self.is_empty():
        raise IndexError("The service queue is empty.")
    return self._items[0]
```

### Costs

| Operation | Cost | Why |
| --- | --- | --- |
| `enqueue` | O(1) | Append at the deque's right end |
| `dequeue` | O(1) | Remove from the deque's left end |
| `peek` | O(1) | Read the left end without removal |
| `is_empty`, `size` | O(1) | Deque length |
| `to_list` | O(n) | Copies every waiting value into a new list |

A plain Python list with `pop(0)` would return the correct value but shift every
remaining reference, making removal O(n). Passing the behavioural tests alone
would not meet the efficiency target; the representation matters.

### Web behaviour

The queue page reconstructs the class from `workspace.queue_state` on every
request. Arrival order therefore survives a refresh. When the queue is empty,
`dequeue()` raises `IndexError`, the view catches the application error and
shows a friendly message instead of crashing.

The required demonstration is recorded in `evidence/after/web_flow_phase1.txt`:
A, B and C join in order; A stays next after a refresh; serving A leaves B and
C; joining D produces B, C, D; serving everything leaves an empty queue; an
empty serve request is handled safely. `evidence/after/phase4_check_queue.txt`
shows the 10 queue goal checks passing.

## Activity B — real singly linked production flow

### Representation

Every value lives in a supplied `Node` with `data` and `next`. The list keeps
three pieces of metadata:

- `head` — first node, or `None` when empty.
- `tail` — final node, or `None` when empty.
- `_size` — cached node count, updated after every mutation.

The final node's `next` is always `None`. Insertion and removal change links
around the affected node; surviving nodes keep their identity. The class does
not keep a persistent list, tuple, dictionary, set or deque as a backing store.

### Costs

| Operation | Cost | Why |
| --- | --- | --- |
| `prepend` | O(1) | Create a node and point it at the old head |
| `append` | O(1) | Link the old tail to a new node |
| `insert_at(0)` / `insert_at(size)` | O(1) | Delegates to prepend or append |
| `remove_at(0)` | O(1) | Move `head` to the next node |
| `get`, `index_of`, `remove(value)` | O(n) worst case | Walk from head to find the position or value |
| Middle `insert_at` / `remove_at` | O(n) | Find the predecessor |
| Removing the final node | O(n) | A singly linked list must find its predecessor |
| `size`, `is_empty` | O(1) | Cached `_size` |
| `to_list` | O(n) | Traverse head to tail |

`require_integer()` rejects strings, fractional values and booleans for every
indexed method. Negative and out-of-range integers raise `IndexError`.

### Why `to_list()` is not flat backing storage

The Django model needs a JSON-safe snapshot to save. `to_list()` builds a new
Python list by walking `head -> next -> ... -> None`. That temporary list is
serialization output, not the data structure. The next request loads the saved
values into a new chain of real nodes. The inspector reads `head`, `tail` and
`next` directly; it deliberately refuses to draw links for a hidden collection.

### Web behaviour

The required demonstration is recorded in `evidence/after/web_flow_phase2.txt`.
It covers append 10, 20, 30; prepend 5; insert 15 at index 2; remove index 3
returning 20; append 40; `index_of(30) = 3`; `get(2) = 15`; the inspector
showing head, tail and a final `next` of `None`; a missing value; duplicate
handling; an invalid index; deleting the only node; and identity preservation
with the cached size. `evidence/after/phase4_check_linked_list.txt` shows all
17 linked-list goal checks passing.

## Integration trace

Take the **Join queue** button as the browser form to trace.

1. The browser sends `POST /queue/join/<ticket_id>/` with the CSRF token.
2. `backend/workspace/urls.py` maps that URL to `views.queue_join`.
3. The `workspace_access(edit=True)` decorator rechecks that the signed-in user
   belongs to the active workspace and may edit it. A viewer is rejected.
4. `queue_join` calls `services.enqueue_ticket(workspace_id, ticket_id, actor)`.
5. Inside the transaction, `Workspace.objects.select_for_update()` locks the
   workspace row. `owned_ticket()` verifies that the ticket belongs to that
   workspace and is not archived.
6. `load_queue()` validates the saved JSON list and constructs
   `ServiceQueue(workspace.queue_state)`.
7. `queue.enqueue(ticket.id)` adds the ID at the rear of the deque.
8. `_save_queue()` calls `queue.to_list()`, validates that the IDs are distinct
   active `todo` jobs, assigns the new list to `workspace.queue_state` and saves
   the `JSONField`.
9. The ticket's `queued_at` and version are updated, and an `Event` row records
   the action. The transaction commits to SQLite.
10. The view redirects to `/queue/` (POST/redirect/GET). On that GET,
    `queue_page` reconstructs `ServiceQueue` from the saved list and calls
    `peek()` and `to_list()` to render the next job and the waiting line.
11. A browser refresh repeats step 10, so the visible order is rebuilt from the
    database rather than from browser memory.

The Workflow form follows the same shape:
`POST /workflow/ -> views.workflow -> services.operate_workflow ->
load_workflow -> SinglyLinkedList method -> _snapshot -> JSONField -> redirect`.
The production-flow page then reads the saved snapshot and traverses the new
node chain for the inspector.

## One failure and its fix

The untouched starter's queue removed from the end of its Python list, so it
served the newest waiting job. I reproduced this in the real page with three
jobs A, B and C: the next-up panel selected C even though A had arrived first.
I inspected `dequeue()` and `peek()` and found that they read the list's last
element. I replaced the backing store with `collections.deque`, made
`dequeue()` use `popleft()`, made `peek()` read index 0, and kept `to_list()`
in arrival order. I verified the change with the queue goal suite (10 passes),
the saved-state reload tests, and the live flow that serves A, joins D and
leaves B, C, D.

## Verification

| Check | Result | Evidence |
| --- | ---: | --- |
| Application tests | 57 pass | `evidence/after/phase4_run_tests.txt` |
| Queue goal | 10 pass | `evidence/after/phase4_check_queue.txt` |
| Linked-list goal | 17 pass | `evidence/after/phase4_check_linked_list.txt` |
| Combined | 84 pass | `evidence/after/phase4_check_activity.txt` |
| Live web flow | all checks pass | `evidence/after/phase4_web_flow.txt` |
| Integrity and migrations | clean | `evidence/after/phase4_integrity.txt` |

The untouched baseline failures are preserved in `evidence/before/` for
comparison.
