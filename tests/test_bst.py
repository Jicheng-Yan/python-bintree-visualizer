from bintree import BinarySearchTree

def test_insert_and_inorder():
    t = BinarySearchTree[int]()
    for k in [8,3,10,1,6,14,4,7,13]:
        t.insert(k)
    assert t.inorder() == [1,3,4,6,7,8,10,13,14]


def test_search_and_replace():
    t = BinarySearchTree[int]()
    t.bulk_insert([5,2,7,1,3,6,8])
    assert t.search(3) is not None
    assert t.replace(3,4) is True
    assert t.search(3) is None
    assert t.search(4) is not None
    assert t.inorder() == [1,2,4,5,6,7,8]


def test_delete_cases():
    t = BinarySearchTree[int]()
    t.bulk_insert([5,3,7,2,4,6,8])
    assert t.delete(2) is True
    assert t.inorder() == [3,4,5,6,7,8]
    assert t.delete(7) is True
    assert t.inorder() == [3,4,5,6,8]
    assert t.delete(5) is True
    assert t.inorder() in ([3,4,6,8], [3,4,6,8])


def test_height_to_dict():
    t = BinarySearchTree[int]()
    assert t.height() == -1
    t.bulk_insert([2,1,3])
    assert t.height() == 1
    d = t.to_dict()
    assert d and d['key'] == 2 and d['left']['key'] == 1 and d['right']['key'] == 3
