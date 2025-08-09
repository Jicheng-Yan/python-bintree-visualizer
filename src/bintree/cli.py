from __future__ import annotations
import argparse
import json
from .bst import BinarySearchTree
from .visualizer import VisualDebugger
from .grammar_tree import GrammarSpec, build_sentence_tree, example_spec, build_sentence_tree_subject_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Binary Search Tree CLI with visual debugger")
    parser.add_argument("action", choices=["demo", "run", "grammar"], help="demo: sample; run: execute ops; grammar: visualize sentence")
    parser.add_argument("--input", dest="input_file", help="JSON file containing operations", default=None)
    parser.add_argument("--out", dest="out", help="Output directory for visualizer", default="visual")
    parser.add_argument("--subject-root", action="store_true", help="Use subject as root and noun phrases as leaves")
    args = parser.parse_args()

    tree = BinarySearchTree[int]()
    vis = VisualDebugger(out_dir=args.out)

    def rec(op: str, key: int, note: str | None = None):
        vis.record(op, key, tree, note)

    if args.action == "demo":
        for k in [8,3,10,1,6,14,4,7,13]:
            tree.insert(k)
            rec("insert", k)
        rec("inorder", -1, note=str(tree.inorder()))
        tree.delete(3); rec("delete", 3)
        tree.replace(6, 5); rec("replace", 5, note="replace 6->5")
        tree.search(7); rec("search", 7)
    elif args.action == "grammar":
        # Load spec from JSON if provided; otherwise use example
        spec_data = None
        if args.input_file:
            with open(args.input_file, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
        if spec_data is None:
            spec = example_spec()
        else:
            spec = GrammarSpec(**spec_data)
        gt = build_sentence_tree_subject_root(spec) if args.subject_root else build_sentence_tree(spec)
        vis.record("grammar", 0, gt, note="vertical-grammar")
    else:
        if not args.input_file:
            raise SystemExit("--input is required for run mode")
        with open(args.input_file, "r", encoding="utf-8") as f:
            ops = json.load(f)
        for op in ops:
            name = op.get("op")
            key = op.get("key")
            note = op.get("note")
            if name == "insert": tree.insert(key)
            elif name == "delete": tree.delete(key)
            elif name == "replace": tree.replace(op["old"], op["new"]) ; key = op["new"]
            elif name == "search": tree.search(key)
            else: raise ValueError(f"Unknown op: {name}")
            rec(name, key, note)

    path = vis.export()
    print(f"Exported visual debugger to: {path}")

if __name__ == "__main__":
    main()
