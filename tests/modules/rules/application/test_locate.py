"""Use case: say what a path is and what code there may do, on an in-memory source tree: no filesystem."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from xarch.kernel.logic.placement import Excluded, Repeat, Target
from xarch.kernel.logic.testing import TierView as Tier
from xarch.modules.rules.contract import (
    CoveringTest,
    InPart,
    Locate,
    Located,
    NearestView,
    Outside,
    PartShown,
    ReachView,
    TierInfoView,
    Ungoverned,
)
from xarch.modules.rules.domain.values import PartInfo, Profile

APP, TESTS = Path("/src/app"), Path("/src/tests")
PROFILE = Profile(
    parts={"kernel": ("kernel",), "domain": ("modules", "*", "domain")},
    rules={"kernel": (), "domain": (Target("kernel"),)},
    folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain")),
    tiers=(Tier("unit", (Target("kernel"), Target("domain", "own")), None, (), False, "a rule", "nothing", "Does it?"),),
    libraries={"kernel": (), "domain": ()}, repeats=(Repeat("module", ("modules",)),),
    info={"kernel": PartInfo("primitives", "Is it a primitive?", "kernel/"),
          "domain": PartInfo("invariants", "Is it an invariant?", "domain/")})
KERNEL = InPart("app/kernel/ids.py", True, PartShown("kernel", "kernel/", "", "module", "primitives", "Is it a primitive?"),
              (ReachView("kernel", "none", "kernel/", "app/kernel/"),), "`kernel/`", (), (),
              CoveringTest(TierInfoView("unit", "a rule", "nothing", "Does it?"), "tests/kernel/", "", "tests/kernel/"))
STRAY = Ungoverned("app/stray/run.py", False, (
    NearestView("kernel", "kernel/", "app/kernel/"), NearestView("domain", "domain/", "app/modules/<module>/domain/")),
    False, "")
README = Ungoverned("README.md", True, (), None, "it lies outside the app folder and the tests folder")


def locate(files, command, profile=PROFILE):
    tree = FakeSourceTree(APP, files, {TESTS: {}}, texts={Path("/src/README.md"): "x"})
    profiles = FakeProfiles({"p": profile})
    return controller(tree, profiles).locate(command)


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"kernel/ids.py": []}, Locate(Path("app/kernel/ids.py"), Path("/src"), APP, "p", TESTS),
                 Located(KERNEL), id="a file in a part is described"),
    pytest.param({}, Locate(Path("stray/run.py"), Path("/src"), APP, "p", TESTS), Located(STRAY),
                 id="a path in no part names the parts near it"),
    pytest.param({}, Locate(Path("README.md"), Path("/src"), APP, "p", TESTS), Located(README),
                 id="a file of the project outside the app is ungoverned"),
    pytest.param({}, Locate(Path("/elsewhere/x.py"), Path("/src"), APP, "p", TESTS),
                 Outside("/elsewhere/x.py lies outside the project: it is not below /src"),
                 id="a path outside the project is refused"),
])
def test_locate(given, when, then):
    assert locate(given, when) == then


@pytest.mark.parametrize("path, then", [
    pytest.param("app/examples/run.py", Ungoverned("app/examples/run.py", False, (), None, "excluded from the "
                 "checks by the profile: shipped as data"), id="a file in an excluded folder says it is excluded"),
    pytest.param("app/examples", Ungoverned("app/examples", False, (), None, "excluded from the checks by the "
                 "profile: shipped as data"), id="the excluded folder itself says it is excluded"),
    pytest.param("app/examples2/run.py", Ungoverned("app/examples2/run.py", False,
                 (NearestView("kernel", "kernel/", "app/kernel/"), NearestView("domain", "domain/",
                                                                     "app/modules/<module>/domain/")), True, ""),
                 id="a folder that only starts with the excluded name is not excluded"),
])
def test_a_path_in_an_excluded_folder_is_ungoverned_and_says_why(path, then):
    excluding = replace(PROFILE, closed_tree=True, excluded=(Excluded(("examples",), "shipped as data"),))
    found = locate({}, Locate(Path(path), Path("/src"), APP, "p", TESTS), excluding)
    assert found == Located(then)
