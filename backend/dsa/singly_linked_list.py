"""CHALLENGE B: a real singly linked list.

This module is used by the Workflow page. Values live in Node objects connected
by one ``next`` reference each. ``head`` is the first node, ``tail`` is the last
node, and the final node's ``next`` is None.

Do not keep a Python list/dictionary/deque as the backing store. A temporary
result list inside to_list() is allowed. Indices are zero-based integers;
negative indices are invalid. Search/remove uses the first matching value.
"""


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


def require_integer(index):
    """Shared input contract; bool is not a usable position."""
    if not isinstance(index, int) or isinstance(index, bool):
        raise TypeError("Index must be an integer.")


class SinglyLinkedList:
    def __init__(self, items=None):
        self.head = None
        self.tail = None
        self._size = 0
        if items is not None:
            for value in items:
                self.append(value)

    def _node_at(self, index):
        """Walk from head to a valid zero-based position. O(n)."""
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def prepend(self, value):
        """Insert a new node as the head in O(1)."""
        node = Node(value)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1

    def append(self, value):
        """Insert a new node after tail in O(1)."""
        node = Node(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def insert_at(self, index, value):
        """Insert at 0 <= index <= size. Raise IndexError otherwise."""
        require_integer(index)
        if not 0 <= index <= self._size:
            raise IndexError(index)
        if index == 0:
            self.prepend(value)
            return
        if index == self._size:
            self.append(value)
            return
        previous = self._node_at(index - 1)
        node = Node(value)
        node.next = previous.next
        previous.next = node
        self._size += 1

    def remove_at(self, index):
        """Remove and return the value at 0 <= index < size."""
        require_integer(index)
        if not 0 <= index < self._size:
            raise IndexError(index)
        if index == 0:
            node = self.head
            self.head = node.next
            if self.head is None:
                self.tail = None
        else:
            previous = self._node_at(index - 1)
            node = previous.next
            previous.next = node.next
            if node is self.tail:
                self.tail = previous
        node.next = None
        self._size -= 1
        return node.data

    def remove(self, value):
        """Remove the first match and return True; return False if missing."""
        previous = None
        node = self.head
        while node is not None:
            if node.data == value:
                if previous is None:
                    self.head = node.next
                    if self.head is None:
                        self.tail = None
                else:
                    previous.next = node.next
                    if node is self.tail:
                        self.tail = previous
                node.next = None
                self._size -= 1
                return True
            previous, node = node, node.next
        return False

    def get(self, index):
        """Read the value at a valid index without changing links. O(n)."""
        require_integer(index)
        if not 0 <= index < self._size:
            raise IndexError(index)
        return self._node_at(index).data

    def index_of(self, value):
        """Return the first matching index, or -1 if missing."""
        node = self.head
        index = 0
        while node is not None:
            if node.data == value:
                return index
            node = node.next
            index += 1
        return -1

    def size(self):
        """Return the cached node count in O(1)."""
        return self._size

    def is_empty(self):
        return self._size == 0

    def to_list(self):
        """Return a fresh display/storage snapshot, head to tail."""
        result = []
        node = self.head
        while node is not None:
            result.append(node.data)
            node = node.next
        return result
