"""A hand-made layout tree walked: its entries, whether a path is in it, and whether as a file."""
import pytest

from xarch.modules.spec.application.logic.layout_walk import folders, is_file, lies_in, walk
from xarch.modules.spec.domain.published import Entry

TREE = {"src": {"*": {"core": {}, "main.py": None}}, "README.md": None}


def test_the_entries_are_walked_parents_first_each_a_folder_or_a_file_and_a_leaf_when_it_holds_nothing():
    assert list(walk(TREE)) == [Entry(("src",), True, False), Entry(("src", "*"), True, False),
                                Entry(("src", "*", "core"), True, True), Entry(("src", "*", "main.py"), False, True),
                                Entry(("README.md",), False, True)]


@pytest.mark.parametrize("path, there, file", [
    pytest.param(("src", "*", "main.py"), True, True, id="a file of the tree"),
    pytest.param(("src", "*", "core"), True, False, id="a folder of the tree is no file"),
    pytest.param((), True, False, id="the root is the tree itself"),
    pytest.param(("src", "*", "main.py", "x"), False, False, id="nothing lies below a file"),
    pytest.param(("docs",), False, False, id="a path the tree does not hold"),
])
def test_a_path_lies_in_the_tree_as_a_folder_or_a_file(path, there, file):
    assert (lies_in(TREE, path), is_file(TREE, path)) == (there, file)


def test_the_folders_of_a_layout_are_the_app_folder_then_each_folder_of_the_walk():
    assert folders({"kernel": {}, "modules": {"*": {"domain": {}, "controller.py": None}}}) == (
        (), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain"))
