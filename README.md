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

## Sequence diagram

The following Mermaid diagram shows end-to-end call flows across CLI actions (demo, run, grammar), the grammar builder, visual debugger export, and the browser viewer.

```mermaid
sequenceDiagram
  actor User
  participant CLI as btree (CLI)
  participant Main as bintree.cli:main()
  participant BST as BinarySearchTree
  participant Grammar as grammar_tree (builder)
  participant Vis as VisualDebugger
  participant FS as FileSystem
  participant Browser
  participant Viewer as HTML Viewer (JS)

  User->>CLI: btree <action> [--input ...] [--out dir] [--legacy]
  CLI->>Main: parse args and dispatch

  alt action == "demo"
    Main->>BST: insert(k) xN
    Main->>Vis: record("insert", k, tree)
    Main->>BST: delete(3), replace(6,5), search(7)
    Main->>Vis: record("delete"/"replace"/"search", key, tree)
  else action == "run"
    Main->>FS: read ops.json
    loop for each op
      Main->>BST: insert/delete/replace/search
      Main->>Vis: record(op, key, tree)
    end
  else action == "grammar"
    opt --input spec.json provided
      Main->>FS: read spec.json
    end
    Main->>Grammar: build (subject-root by default)
    Grammar->>BST: produce tree (subject root; SP leaves up; PP leaves down)
    Main->>Vis: record("grammar", 0, tree)
  end

  Main->>Vis: export()
  Vis->>FS: write out_dir/trace.json
  Vis->>FS: write out_dir/index.html
  Main-->>User: Exported visual debugger path

  User->>Browser: open out_dir/index.html
  Browser->>Viewer: load HTML+JS
  Viewer->>FS: fetch("trace.json")
  FS-->>Viewer: JSON snapshots

  Viewer->>Viewer: build sidebar, render selected snapshot
  Viewer->>Viewer: left-to-right layout (SP up, time/state up; PP down)
  Viewer->>Viewer: draw links + colored nodes

  opt navigate snapshots
    User->>Viewer: Prev/Next or sidebar click
    Viewer->>Viewer: render(other snapshot)
  end
```
