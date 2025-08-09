from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, Callable, Iterable, List, Tuple

T = TypeVar("T")

@dataclass
class Node(Generic[T]):
    key: T
    left: Optional["Node[T]"] = None
    right: Optional["Node[T]"] = None

    def __repr__(self) -> str:
        return f"Node({self.key!r})"

class BinarySearchTree(Generic[T]):
    """
    A classic unbalanced Binary Search Tree with:
    - insert
    - search
    - replace (update a node's key, preserving BST invariant)
    - delete
    - inorder/preorder/postorder traversals

    The tree accepts a custom key comparator; by default uses Python's < and ==.
    """

    def __init__(self, *, cmp: Optional[Callable[[T, T], int]] = None) -> None:
        self.root: Optional[Node[T]] = None
        self._cmp = cmp or self._default_cmp

    # ---------- Basics ----------
    @staticmethod
    def _default_cmp(a: T, b: T) -> int:
        return (a > b) - (a < b)

    def _compare(self, a: T, b: T) -> int:
        return self._cmp(a, b)

    # ---------- Insert ----------
    def insert(self, key: T) -> None:
        if self.root is None:
            self.root = Node(key)
            return
        cur = self.root
        while True:
            c = self._compare(key, cur.key)
            if c == 0:
                # overwrite by default
                cur.key = key
                return
            elif c < 0:
                if cur.left is None:
                    cur.left = Node(key)
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = Node(key)
                    return
                cur = cur.right

    def bulk_insert(self, keys: Iterable[T]) -> None:
        for k in keys:
            self.insert(k)

    # ---------- Search ----------
    def search(self, key: T) -> Optional[Node[T]]:
        cur = self.root
        while cur:
            c = self._compare(key, cur.key)
            if c == 0:
                return cur
            cur = cur.left if c < 0 else cur.right
        return None

    # ---------- Replace ----------
    def replace(self, old_key: T, new_key: T) -> bool:
        """
        Replace node with old_key by new_key while keeping BST invariant.
        This is implemented as delete(old_key) then insert(new_key) when keys differ.
        If equal, it's a no-op.
        Returns True if old_key existed.
        """
        if self._compare(old_key, new_key) == 0:
            node = self.search(old_key)
            if node is None:
                return False
            node.key = new_key
            return True
        deleted = self.delete(old_key)
        if deleted:
            self.insert(new_key)
        return deleted

    # ---------- Delete ----------
    def delete(self, key: T) -> bool:
        """Delete a node by key. Returns True if a node was deleted."""
        self.root, deleted = self._delete_rec(self.root, key)
        return deleted

    def _delete_rec(self, node: Optional[Node[T]], key: T) -> Tuple[Optional[Node[T]], bool]:
        if node is None:
            return None, False
        c = self._compare(key, node.key)
        if c < 0:
            node.left, deleted = self._delete_rec(node.left, key)
            return node, deleted
        elif c > 0:
            node.right, deleted = self._delete_rec(node.right, key)
            return node, deleted
        else:
            # Found node
            if node.left is None and node.right is None:
                return None, True
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # Two children: replace with inorder successor
            succ_parent = node
            succ = node.right
            while succ.left is not None:
                succ_parent = succ
                succ = succ.left
            node.key = succ.key
            # Delete successor
            if succ_parent is node:
                succ_parent.right, _ = self._delete_rec(succ_parent.right, succ.key)
            else:
                succ_parent.left, _ = self._delete_rec(succ_parent.left, succ.key)
            return node, True

    # ---------- Traversals ----------
    def inorder(self) -> List[T]:
        res: List[T] = []
        def dfs(n: Optional[Node[T]]):
            if not n: return
            dfs(n.left)
            res.append(n.key)
            dfs(n.right)
        dfs(self.root)
        return res

    def preorder(self) -> List[T]:
        res: List[T] = []
        def dfs(n: Optional[Node[T]]):
            if not n: return
            res.append(n.key)
            dfs(n.left)
            dfs(n.right)
        dfs(self.root)
        return res

    def postorder(self) -> List[T]:
        res: List[T] = []
        def dfs(n: Optional[Node[T]]):
            if not n: return
            dfs(n.left)
            dfs(n.right)
            res.append(n.key)
        dfs(self.root)
        return res

    # ---------- Utilities ----------
    def height(self) -> int:
        def h(n: Optional[Node[T]]) -> int:
            if n is None: return -1
            return 1 + max(h(n.left), h(n.right))
        return h(self.root)

    def to_dict(self) -> Optional[dict]:
        def conv(n: Optional[Node[T]]):
            if n is None: return None
            return {"key": n.key, "left": conv(n.left), "right": conv(n.right)}
        return conv(self.root)
