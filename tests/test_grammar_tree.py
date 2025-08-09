from bintree import GrammarSpec, build_sentence_tree, example_spec


def test_build_sentence_tree_example():
    spec = example_spec()
    t = build_sentence_tree(spec)
    # Ensure root exists and inorder includes key tags from both sides
    inorder = t.inorder()
    has_subject = any(k.startswith("S:[the-student") for k in inorder)
    has_time = any(k.startswith("P://do|present|singular|third/") for k in inorder)
    has_verb = any(k.startswith("V:study") for k in inorder)
    has_obj = any(k.startswith("PP:<mathematics>") for k in inorder)
    assert has_subject and has_time and has_verb and has_obj
