from bintree import example_spec, build_sentence_tree_subject_root

def test_subject_root_tree_shape():
    spec = example_spec()
    t = build_sentence_tree_subject_root(spec)
    root = t.root
    assert root and root.key.startswith("S:[")
    # Left subtree contains only SP nodes or is None
    def is_sp_leaf(n):
        return n and n.key.startswith("SP:(") and n.left is None and n.right is None
    def check_sp_group(n):
        if n is None: return True
        if n.key == "SP:*":
            return check_sp_group(n.left) and check_sp_group(n.right)
        return is_sp_leaf(n)
    assert check_sp_group(root.left)
    # Right subtree root is verb and its right is PP group
    verb = root.right
    assert verb and verb.key.startswith("V:")
    pp_group = verb.right
    def is_pp_leaf(n):
        return n and n.key.startswith("PP:<") and n.left is None and n.right is None
    def check_pp_group(n):
        if n is None: return True
        if n.key == "PP:*":
            return check_pp_group(n.left) and check_pp_group(n.right)
        return is_pp_leaf(n)
    assert check_pp_group(pp_group)
