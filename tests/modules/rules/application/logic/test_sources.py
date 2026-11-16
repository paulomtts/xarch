"""Where a file found at a path given to be read sits, and the files a folder stands for."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.modules.rules.builders import PYTHON
from xarch.modules.rules.application.logic.sources import below, sited, walked
from xarch.modules.rules.domain.published import EXCLUDED, IN_NO_PART, IN_PART, IN_PROJECT, IN_TESTS, NOT_SOURCE, NOT_THERE
from xarch.modules.rules.domain.values import Profile, Resolved, Sited
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat

PROFILE = Profile(parts={"kernel": ("kernel",), "domain": ("modules", "*", "domain")}, rules={"kernel": (), "domain": ()},
                  folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain")),
                  repeats=(Repeat("module", ("modules",)),), excluded=(Excluded(("examples",), "data"),), language=PYTHON)


def found(within: str, path: str) -> Resolved:
    return Resolved(within, tuple(path.split("/")), Path("/src") / within / path, True, f"{within}/{path}")


@pytest.mark.parametrize("where, then", [
    pytest.param(found("app", "modules/docs/domain/values.py"), Sited(IN_PART, "domain"), id="a file of the app in a part"),
    pytest.param(replace(found("app", "kernel/ids.py"), exists=False), Sited(NOT_THERE, ""),
                 id="a file that is not there, first"),
    pytest.param(found("app", "kernel/notes.txt"), Sited(NOT_SOURCE, ""), id="a file of another ending is no source file"),
    pytest.param(found("tests", "kernel/ids.py"), Sited(IN_TESTS, ""), id="a file below the tests root"),
    pytest.param(found("project", "scripts/run.py"), Sited(IN_PROJECT, ""),
                 id="a file of the project outside the app and the tests"),
    pytest.param(found("app", "examples/demo.py"), Sited(EXCLUDED, ""), id="a file below an excluded folder"),
    pytest.param(found("app", "stray/run.py"), Sited(IN_NO_PART, ""), id="a file of the app in no part"),
    pytest.param(found("app", "modules/docs/__init__.py"), Sited(IN_NO_PART, ""),
                 id="a package file of the structure lies in no part"),
])
def test_where_a_file_lies(where, then):
    assert sited(PROFILE, where) == then


def test_a_file_below_a_folder_is_settled_as_the_folder_is():
    assert below(found("app", "kernel"), ("ids.py",)) == found("app", "kernel/ids.py")


def test_a_file_below_the_app_folder_itself_is_shown_below_it():
    app = Resolved("app", (), Path("/src/app"), True, "app")
    assert below(app, ("kernel", "ids.py")) == found("app", "kernel/ids.py")


def test_a_folder_stands_for_its_files_but_those_below_an_excluded_folder():
    app = Resolved("app", (), Path("/src/app"), True, "app")
    assert walked(PROFILE, app, [("examples", "demo.py"), ("kernel", "ids.py")]) == [found("app", "kernel/ids.py")]
