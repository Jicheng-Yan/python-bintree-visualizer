# bintree

Binary Search Tree (BST) with search, replace, delete and a simple HTML visual debugger.

## Features
- Generic BST: insert, search, replace, delete
- Traversals: inorder, preorder, postorder
- Visual debugger: records snapshots to `visual/trace.json` and emits `visual/index.html`
- CLI for demos and scripted runs
- Pytest unit tests

## Install
```fish
# From repo root
python -m venv .venv
source .venv/bin/activate.fish
pip install -e .[dev]
```

## Quick demo
```fish
btree demo --out visual
# Then open visual/index.html in your browser
```

## Run from a JSON script
Create `ops.json` like:
```json
[
  {"op":"insert", "key":8},
  {"op":"insert", "key":3},
  {"op":"insert", "key":10},
  {"op":"delete", "key":3},
  {"op":"replace", "old":10, "new":9},
  {"op":"search", "key":9}
]
```
Then:
```fish
btree run --input ops.json --out visual
```

## Library usage
```python
from bintree import BinarySearchTree, VisualDebugger

t = BinarySearchTree[int]()
vis = VisualDebugger("visual")
for k in [5,2,7,1,3]:
    t.insert(k)
    vis.record("insert", k, t)
vis.export()
```

## Testing
```fish
pytest -q
```
