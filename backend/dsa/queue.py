"""CHALLENGE A: a FIFO service queue.

The Service queue page calls this class. Waiting requests leave in arrival order:
the earliest waiting request is the front, and new arrivals join the rear.

Keep the class and method names. to_list() must return a NEW list in arrival
order, earliest to latest, because Django saves it and reloads it next request.
collections.deque gives O(1) append at the rear and O(1) popleft at the front.
"""

from collections import deque


class ServiceQueue:
    def __init__(self, items=None):
        # Copy the saved arrival-order snapshot into a deque. The input list is
        # never mutated, and later changes to it cannot affect this queue.
        self._items = deque(items) if items is not None else deque()

    def enqueue(self, value):
        """Add a request at the rear in O(1)."""
        self._items.append(value)

    def dequeue(self):
        """Remove and return the earliest waiting request in O(1)."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")
        return self._items.popleft()

    def peek(self):
        """Read the front request without removal; agrees with dequeue()."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def to_list(self):
        """Return a fresh arrival-order snapshot for SQLite persistence."""
        return list(self._items)
