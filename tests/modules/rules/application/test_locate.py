"""Use case: say what a path is and what code there may do, on an in-memory source tree: no filesystem."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from xarch.kernel.logic.placement import Target
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.rules.application.services.locate import Locator
from xarch.modules.rules.contract import Locate, Located, Outside
from xarch.modules.rules.domain.values import Exclusion, Nearest, PartInfo, Profile, Reach, TierInfo, Where
from xarch.modules.rules.domain.values import TestTier as Tier

APP, TESTS = Path("/src/app"), Path("/src/tests")
PROFILE = Profile(
    parts={"kernel": ("kernel",), "domain": ("modules", "*", "domain")},
    rules={"kernel": (Target("kernel"),), "domain": (Target("domain", "own"), Target("kernel"))},
    folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain")),
    tiers=(Tier("unit", (Target("kernel"), Target("domain", "own")), None, (), False, "a rule", "nothing", "Does it?"),),
    libraries={"kernel": (), "domain": ()}, each_root=("modules",),
    info={"kernel": PartInfo("primitives", "Is it a primitive?", "kernel/"),
          "domain": PartInfo("invariants", "Is it an invariant?", "domain/")},
    singular="module")
KERNEL = Where("part", "app/kernel/ids.py", True, "kernel", "primitives", "Is it a primitive?", "kernel/",
               singular="module", may_import=(Reach("kernel", "none", "kernel/", "app/kernel/"),),
               may_import_text="`kernel/`", libraries=(), tier=TierInfo("unit", "a rule", "nothing", "Does it?"),
               test_folder="tests/kernel/")
STRAY = Where("ungoverned", "app/stray/run.py", False, nearest=(
    Nearest("kernel", "kernel/", "app/kernel/"), Nearest("domain", "domain/", "app/modules/<module>/domain/")))
README = Where("ungoverned", "README.md", True, note="it lies outside the app folder and the tests folder")


def locate(files, command, profile=PROFILE):
    tree = FakeSourceTree(APP, files, {TESTS: {}}, texts={Path("/src/README.md"): "x"})
    profiles = FakeProfiles({"p": profile})
    return RulesController(ImportCheck(tree, profiles), Locator(tree, profiles)).locate(command)


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
    pytest.param("app/examples/run.py", Where("ungoverned", "app/examples/run.py", False, note="excluded from the "
                 "checks by the profile: shipped as data"), id="a file in an excluded folder says it is excluded"),
    pytest.param("app/examples", Where("ungoverned", "app/examples", False, note="excluded from the checks by the "
                 "profile: shipped as data"), id="the excluded folder itself says it is excluded"),
    pytest.param("app/examples2/run.py", Where("ungoverned", "app/examples2/run.py", False,
                 nearest=(Nearest("kernel", "kernel/", "app/kernel/"), Nearest("domain", "domain/",
                                                                              "app/modules/<module>/domain/")),
                 closed_tree=True),
                 id="a folder that only starts with the excluded name is not excluded"),
])
def test_a_path_in_an_excluded_folder_is_ungoverned_and_says_why(path, then):
    excluding = replace(PROFILE, closed_tree=True, excluded=(Exclusion(("examples",), "shipped as data"),))
    found = locate({}, Locate(Path(path), Path("/src"), APP, "p", TESTS), excluding)
    assert found == Located(then)
