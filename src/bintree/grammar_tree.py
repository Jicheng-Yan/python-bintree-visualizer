from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Any, Dict
from .bst import BinarySearchTree, Node

"""
Grammar-to-Binary-Tree mapping (Vertical Grammar)

We represent a sentence as a binary tree with a fixed left/right convention:
- Left subtree := Subject side (pre-subject phrases then Subject name)
- Right subtree := Predicate side (Time/State verb node then post-predicate phrases)

Node.key carries a compact tagged token, like:
- S:[] subject name token (e.g., S:[the-student|who|def|sg])
- SP:(...) subject decorator/phrase (preposition/gerund/infinitive)
- P:// predicate time (type/tense/number/person)
- P:|| predicate state (still/active/passive/normal + parts)
- V:verb the main verb/lemma (e.g., V:study)
- PP:<...> post-predicate phrases

This module builds such a tree from a structured grammar spec, and
emits snapshots using the existing VisualDebugger.
"""

@dataclass
class GrammarSpec:
    sentence_type: str  # statement | negative | yesno | wh
    subject: Dict[str, Any]  # { name: str, what: str, type: str, number: str, person?: str }
    subject_phrases: List[str]  # pre-subject phrases (decorators or preposition strings)
    time: Dict[str, Any]  # { type: be|do|have, tense: present|past|future|..., number?:, person?: }
    state: Dict[str, Any]  # { type: still|active|passive|normal|..., parts?: [...] }
    verb: str             # main verb lemma (e.g., study, walk)
    predicate_phrases: List[str]  # post-predicate phrases (objects, adverbials)
    negation: bool = False
    wh: Optional[str] = None  # if wh-question, which word (what/who/where/...)


def tag_subject(subj: Dict[str, Any]) -> str:
    parts = [
        subj.get("name", ""),
        subj.get("what", ""),
        subj.get("type", ""),
        subj.get("number", ""),
        subj.get("person", ""),
    ]
    return "S:[" + "+".join(filter(None, parts)) + "]"


def tag_time(time: Dict[str, Any]) -> str:
    t = time.get("type", "")
    tense = time.get("tense", "")
    num = time.get("number", "")
    person = time.get("person", "")
    return f"P://{t}|{tense}|{num}|{person}/"


def tag_state(state: Dict[str, Any]) -> str:
    t = state.get("type", "")
    parts = state.get("parts", [])
    return "P:||" + t + ("("+"+".join(parts)+")" if parts else "") + "||"


def make_subject_subtree(spec: GrammarSpec) -> Node[str]:
    # Legacy builder: left-leaning chain of subject phrases then subject
    cur = Node(tag_subject(spec.subject))
    for phrase in reversed(spec.subject_phrases):
        cur = Node(f"SP:({phrase})", left=cur)
    return cur


def make_predicate_subtree(spec: GrammarSpec) -> Node[str]:
    # Legacy builder: Verb root, left Time/State, right chained phrases
    verb = Node(f"V:{'do_not_'+spec.verb if spec.negation else spec.verb}")
    time_node = Node(tag_time(spec.time))
    state_node = Node(tag_state(spec.state))
    time_node.left = state_node
    verb.left = time_node
    # chain predicate phrases to the right
    cur = verb
    for phrase in spec.predicate_phrases:
        cur.right = Node(f"PP:<{phrase}>")
        cur = cur.right
    return verb


def build_sentence_tree(spec: GrammarSpec) -> BinarySearchTree[str]:
    """
    Build a BST-shaped presentation tree by inserting subject-subtree node keys
    to the left side and predicate-subtree node keys to the right side using a
    custom comparator that keeps [S:] always less than others, and [V:/P:/SP:/PP:]
    sorted by a simple stable order.
    """
    order = {"S:": -2, "SP:": -1, "V:": 0, "P:": 1, "PP:": 2}

    def cmp(a: str, b: str) -> int:
        def head(s: str) -> str:
            if s.startswith("S:"): return "S:"
            if s.startswith("SP:"): return "SP:"
            if s.startswith("V:"): return "V:"
            if s.startswith("P:"): return "P:"
            if s.startswith("PP:"): return "PP:"
            return "ZZ:"
        ha, hb = head(a), head(b)
        ra, rb = order.get(ha, 99), order.get(hb, 99)
        if ra != rb:
            return (ra > rb) - (ra < rb)
        # stable fallback
        return (a > b) - (a < b)

    tree: BinarySearchTree[str] = BinarySearchTree(cmp=cmp)

    # Flatten both subtrees to a list and insert in order so BST layout groups sides
    def dfs_collect(n: Optional[Node[str]], out: List[str]):
        if not n: return
        out.append(n.key)
        dfs_collect(n.left, out)
        dfs_collect(n.right, out)

    left_sub = make_subject_subtree(spec)
    right_sub = make_predicate_subtree(spec)

    keys: List[str] = []
    dfs_collect(left_sub, keys)
    dfs_collect(right_sub, keys)

    tree.bulk_insert(keys)
    return tree


# --- Subject-rooted builder with noun phrases as leaves ---

def _build_balanced_group(label: str, leaves: List[Node[str]]) -> Optional[Node[str]]:
    """Create a balanced binary tree where all provided nodes are leaves under an internal label node.
    If no leaves, return None. If one leaf, return a single internal node with that leaf as left.
    """
    if not leaves:
        return None
    def build(nodes: List[Node[str]]) -> Node[str]:
        if len(nodes) == 1:
            return nodes[0]
        mid = len(nodes) // 2
        return Node(label, left=build(nodes[:mid]), right=build(nodes[mid:]))
    # Ensure the top is an internal label node and leaves are the provided nodes
    if len(leaves) == 1:
        return Node(label, left=leaves[0])
    return build(leaves)


def build_sentence_tree_subject_root(spec: GrammarSpec) -> BinarySearchTree[str]:
    """
    Build a binary tree where:
    - The Subject node is the root.
    - All noun phrases (subject decorators and predicate object/PPs) are leaves under grouping nodes.
    - Verb/time/state are internal nodes on the predicate side.

    Layout:
      root = S:[...]
        left  = SP:* grouping node -> leaves: subject_phrases (SP:(...))
        right = V:verb
                  left  = P://... with left child P:||...||
                  right = PP:* grouping node -> leaves: predicate_phrases (PP:<...>)
    """
    # Root is subject
    root = Node(tag_subject(spec.subject))

    # Left: subject phrase leaves
    sp_leaves = [Node(f"SP:({p})") for p in spec.subject_phrases]
    root.left = _build_balanced_group("SP:*", sp_leaves)

    # Right: predicate internal tree
    verb = Node(f"V:{'do_not_'+spec.verb if spec.negation else spec.verb}")
    time_node = Node(tag_time(spec.time))
    state_node = Node(tag_state(spec.state))
    time_node.left = state_node
    verb.left = time_node

    pp_leaves = [Node(f"PP:<{p}>") for p in spec.predicate_phrases]
    verb.right = _build_balanced_group("PP:*", pp_leaves)

    root.right = verb

    # Pack into a BinarySearchTree container for VisualDebugger compatibility
    bt: BinarySearchTree[str] = BinarySearchTree()
    bt.root = root
    return bt


def example_spec() -> GrammarSpec:
    # Example: The student in the blue suits studies mathematics at school.
    return GrammarSpec(
        sentence_type="statement",
        subject={
            "name": "the-student",
            "what": "who",
            "type": "definite",
            "number": "singular",
            "person": "third",
        },
        subject_phrases=["in-the-blue-suits"],
        time={"type": "do", "tense": "present", "number": "singular", "person": "third"},
        state={"type": "normal", "parts": ["head"]},
        verb="study",
        predicate_phrases=["mathematics", "at-school"],
    )
