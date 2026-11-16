"""Where a file found at a path given to be read sits, and the files a folder stands for."""
from pathlib import Path

import pytest

from tests.modules.rules.builders import PYTHON
from xarch.modules.rules.application.logic.sources import below, sited, walked
from xarch.modules.rules.domain.values import Profile, Resolved, Sited
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat

PROFILE = Profile(parts={"kernel": ("kernel",), "domain": ("modules", "*", "domain")}, rules={"kernel": (), "domain": ()},
                  folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain")),
                  repeats=(Repeat("module", ("modules",)),), excluded=(Excluded(("examples",), "data"),), language=PYTHON)


def found(within: str, path: str) -> Resolved:
    return Resolved(within, tuple(path.split("/")), Path("/src") / within / path, True, f"{within}/{path}")


@pytest.mark.parametrize("where, then", [
    pytest.param(found("app", "modules/docs/domain/values.py"), Sited("domain", "docs", False, True),
                 id="a file of the app in a part, with its instance"),
    pytest.param(found("app", "kernel/ids.py"), Sited("kernel", "", False, True),
                 id="a file of a part outside every repeating folder has no instance"),
    pytest.param(found("app", "stray/run.py"), Sited("", "", False, True), id="a file of the app in no part"),
    pytest.param(found("app", "examples/demo.py"), Sited("", "", True, True),
                 id="a file below an excluded folder lies in no part"),
    pytest.param(found("app", "kernel/notes.txt"), Sited("kernel", "", False, False),
                 id="a file of another ending is no source file"),
    pytest.param(found("tests", "kernel/ids.py"), Sited("", "", False, True), id="a test lies in no part of the app"),
])
def test_where_a_file_sits(where, then):
    assert sited(PROFILE, where) == then


def test_a_file_below_a_folder_is_settled_as_the_folder_is():
    assert below(found("app", "kernel"), ("ids.py",)) == found("app", "kernel/ids.py")


def test_a_file_below_the_app_folder_itself_is_shown_below_it():
    app = Resolved("app", (), Path("/src/app"), True, "app")
    assert below(app, ("kernel", "ids.py")) == found("app", "kernel/ids.py")


def test_a_folder_stands_for_its_files_but_those_below_an_excluded_folder():
    app = Resolved("app", (), Path("/src/app"), True, "app")
    assert walked(PROFILE, app, [("examples", "demo.py"), ("kernel", "ids.py")]) == [found("app", "kernel/ids.py")]
