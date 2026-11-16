"""Use case: the whole check of an app, its source then its structure, with the profile's hints and whether it passes,
on an in-memory source tree and structure."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.fakes.structure import FakeStructure
from tests.modules.rules.application.helpers import controller
from xarch.kernel.placement import Target
from xarch.kernel.source import Import
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import (
    AppChecked,
    CheckApp,
    ChecksCannotRun,
    EnforcementView,
    FindingView,
    NotADirectory,
)
from xarch.modules.rules.domain.values import Profile

ROOT = Path("/src/pkg")
PROFILE = Profile({"kernel": ("kernel",), "platform": ("platform",)},
                  {"kernel": (), "platform": (Target("kernel"),)}, ((), ("kernel",), ("platform",)),
                  libraries={"kernel": (), "platform": ()}, hints={"rules": "ask first"})
BAD = {"kernel/x.py": [Import(1, ("pkg", "platform", "io"))], "platform/io.py": []}
GOOD = {"kernel/x.py": [], "platform/io.py": [Import(1, ("pkg", "kernel", "x"))]}
IMPORT = Violation("pkg/kernel/x.py", 1, "kernel/ may not import platform/ (pkg.platform.io)", "rules",
                   "import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to a part that may "
                   "import platform/")
MISSING = Violation("pkg", 0, "missing kernel/logic/", "structure", "create pkg/kernel/logic/")


REFUSED = ("checks.mine.mode: is 'fial': write fail or list",)


def check(files: dict, when: CheckApp, structure: list[Violation] | None = None, profile: Profile = PROFILE):
    profiles = FakeProfiles({"cli": profile}, refused={"broken": REFUSED})
    return controller(FakeSourceTree(ROOT, files), profiles, FakeStructure(structure)).check_app(when)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "cli", ROOT.parent),
                 AppChecked((), EnforcementView(), {"rules": "ask first"}, True),
                 id="an app with nothing wrong passes, with the profile's hints"),
    pytest.param(dict(files=BAD, structure=[MISSING]), CheckApp(ROOT, "cli", ROOT.parent),
                 AppChecked((IMPORT, MISSING), EnforcementView(), {"rules": "ask first"}, False),
                 id="the source's violations come first, then the structure's, and the check fails"),
    pytest.param(dict(files={**GOOD, "stray.py": []}), CheckApp(ROOT, "cli", ROOT.parent, strict=True),
                 AppChecked((), EnforcementView(ungoverned=("pkg/stray.py",), ungoverned_folders=("pkg/stray.py",),
                                            strict=(FindingView("ungoverned", "pkg/stray.py"),)),
                            {"rules": "ask first"}, False),
                 id="under strict a finding of the enforcement fails the check too"),
    pytest.param(dict(files=GOOD), CheckApp(Path("/elsewhere"), "cli", ROOT.parent), NotADirectory(Path("/elsewhere")),
                 id="an app folder that is no folder is refused"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "broken", ROOT.parent), ChecksCannotRun(REFUSED),
                 id="a profile whose own checks cannot run is refused with every problem"),
])
def test_check_app(given, when, then):
    assert check(given.get("files", {}), when, given.get("structure"), given.get("profile", PROFILE)) == then


def test_without_strict_a_finding_of_the_enforcement_does_not_fail_the_check():
    result = check({**GOOD, "stray.py": []}, CheckApp(ROOT, "cli", ROOT.parent))
    assert isinstance(result, AppChecked) and result.ok
