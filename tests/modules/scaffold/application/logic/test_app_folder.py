"""Where the app folder and the folder holding it are, for a folder named and for `.` and `..`."""
from pathlib import Path

import pytest

from xarch.modules.scaffold.application.logic.app_folder import app_name, holder


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
