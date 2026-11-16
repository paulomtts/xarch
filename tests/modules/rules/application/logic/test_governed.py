"""Which source files of the app the checks read: none below an excluded folder, and of the rest those a part or a
folder of the layout governs; the others are listed as ungoverned."""
import pytest

from tests.modules.rules.builders import PYTHON
from xarch.kernel.placement import Target
from xarch.modules.rules.application.logic.governed import excluded, governed, ungoverned
from xarch.modules.rules.domain.values import Profile
from xarch.profile_values.excluded import Excluded

PROFILE = Profile(parts={"domain": ("modules", "*", "domain")}, rules={"domain": (Target("domain", "own"),)},
                  folders=((), ("modules",), ("modules", "*")), closed_tree=True, language=PYTHON)


def paths(*written: str) -> list[tuple[str, ...]]:
    return [tuple(p.split("/")) for p in written]

def test_the_ungoverned_files_are_listed_whether_the_guard_is_on_or_not():
    off = Profile(PROFILE.parts, PROFILE.rules, PROFILE.folders, language=PYTHON)
    written = paths("main.py", "modules/docs/domain/doc.py", "modules/docs/__init__.py", "scripts/run.py")
    assert ungoverned(written, off, "app") == ungoverned(written, PROFILE, "app") == ["app/main.py", "app/scripts/run.py"]


@pytest.mark.parametrize("path, is_excluded", [
    pytest.param("examples/x.py", True, id="a file below an excluded folder"),
    pytest.param("examples/deep/y.py", True, id="at any depth"),
    pytest.param("examples_x/y.py", False, id="a folder that only starts with the excluded name"),
    pytest.param("modules/docs/domain/doc.py", False, id="a file of a part"),
])
def test_excluded(path, is_excluded):
    profile = Profile(**{**PROFILE.__dict__, "excluded": (Excluded(("examples",), "shipped as data"),)})
    assert excluded(profile, tuple(path.split("/"))) is is_excluded


@pytest.mark.parametrize("path, is_governed", [
    pytest.param("modules/docs/domain/doc.py", True, id="a file of a part"),
    pytest.param("modules/__init__.py", True, id="a package file of the layout"),
    pytest.param("stray/run.py", False, id="a file in no part and no folder of the layout"),
])
def test_governed(path, is_governed):
    assert governed(PROFILE, tuple(path.split("/"))) is is_governed
