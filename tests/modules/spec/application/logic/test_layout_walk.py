"""A hand-made layout tree walked: its entries, whether a path is in it, and whether as a file."""
import pytest

from xarch.modules.spec.application.logic.layout_walk import is_file, lies_in, walk

TREE = {"src": {"*": {"core": {}, "main.py": None}}, "README.md": None}


def test_the_entries_are_walked_parents_first_each_a_folder_or_a_file_and_a_leaf_when_it_holds_nothing():
    assert list(walk(TREE)) == [(("src",), True, False), (("src", "*"), True, False), (("src", "*", "core"), True, True),
                                (("src", "*", "main.py"), False, True), (("README.md",), False, True)]


@pytest.mark.parametrize("path, there, file", [
    pytest.param(("src", "*", "main.py"), True, True, id="a file of the tree"),
    pytest.param(("src", "*", "core"), True, False, id="a folder of the tree is no file"),
    pytest.param((), True, False, id="the root is the tree itself"),
    pytest.param(("src", "*", "main.py", "x"), False, False, id="nothing lies below a file"),
    pytest.param(("docs",), False, False, id="a path the tree does not hold"),
])
def test_a_path_lies_in_the_tree_as_a_folder_or_a_file(path, there, file):
    assert (lies_in(TREE, path), is_file(TREE, path)) == (there, file)
