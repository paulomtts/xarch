"""What a skeleton turns into on disk, and where the app folder and the folder holding it are."""
from pathlib import Path

import pytest

from xarch.modules.scaffold.application.logic.plan import app_name, holder, plan


def test_plan_writes_a_package_file_for_the_root_and_every_folder_and_every_file_parents_first():
    entries = [(("kernel",), True), (("kernel", "logic"), True), (("main.src",), False)]
    assert plan(entries, "index.src") == [("index.src",), ("kernel", "index.src"), ("kernel", "logic", "index.src"),
                                          ("main.src",)]


@pytest.mark.parametrize("root, resolved, name", [
    pytest.param(Path("shop"), Path("/src/shop"), "shop", id="a named folder is its own name"),
    pytest.param(Path("."), Path("/src/shop"), "shop", id="the current folder is named by where it resolves"),
    pytest.param(Path("a/.."), Path("/src"), "src", id="a folder ending in .. is named by where it resolves"),
])
def test_app_name(root, resolved, name):
    assert app_name(root, resolved) == name


@pytest.mark.parametrize("root, absolute, held_in", [
    pytest.param(Path("src/shop"), Path("/w/src/shop"), Path("src"), id="a named folder is held by its parent"),
    pytest.param(Path("."), Path("/w"), Path("/"), id="the current folder is held by the folder above it"),
])
def test_holder(root, absolute, held_in):
    assert holder(root, absolute) == held_in
