"""Use case: the baseline of an app, written from a whole check and held against the next, on an in-memory source
tree, structure and record: no filesystem, no ast."""
from pathlib import Path

import pytest

from tests.fakes.baselines import FakeBaselines
from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.fakes.structure import FakeStructure
from tests.modules.rules.application.helpers import controller
from xarch.kernel.source import Import
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import (
    BaselineStanding,
    BaselineWritten,
    CheckApp,
    CheckRefused,
    ChecksCannotRun,
    FindingView,
    NotADirectory,
    Recorded,
    RuleCeiling,
    WriteBaseline,
)
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.placement import Target

ROOT = Path("/src/pkg")
PROFILE = Profile({"kernel": ("kernel",), "platform": ("platform",)},
                  {"kernel": (), "platform": (Target("kernel"),)}, ((), ("kernel",), ("platform",)),
                  imports_libraries={"kernel": (), "platform": ()})
BAD = {"kernel/x.py": [Import(1, ("pkg", "platform", "io"))], "platform/io.py": []}
GOOD = {"kernel/x.py": [], "platform/io.py": [Import(1, ("pkg", "kernel", "x"))]}
MISSING = Violation("pkg", 0, "missing kernel/logic/", "structure", "create pkg/kernel/logic/")
REFUSED = ("checks.mine.mode: is 'fial': write fail or list",)
UNUSABLE = "gone: cannot read the file: no such file"

RECORD = ROOT.parent / ".xarch" / "baseline.json"
IMPORT = Recorded("may-import", "pkg/kernel/x.py", "kernel/ may not import platform/ (pkg.platform.io)", 1)
STRUCTURE = Recorded("structure", "pkg", "missing kernel/logic/", 1)


def rules(files: dict, baselines: FakeBaselines, structure=(MISSING,)):
    profiles = FakeProfiles({"cli": PROFILE}, refused={"broken": REFUSED}, unusable={"gone": UNUSABLE})
    return controller(FakeSourceTree(ROOT, files), profiles, FakeStructure(list(structure)), baselines)


WRITTEN = ".xarch/baseline.json"
GONE = Recorded("may-import", "pkg/gone.py", "m", 3)


@pytest.mark.parametrize("given, when, then", [
    pytest.param({}, WriteBaseline(ROOT, "cli", ROOT.parent), BaselineWritten(WRITTEN, 2, None, False),
                 id="with no record every violation is recorded"),
    pytest.param({RECORD: (IMPORT, STRUCTURE, GONE)}, WriteBaseline(ROOT, "cli", ROOT.parent),
                 BaselineWritten(WRITTEN, 2, 5, False), id="a record is lowered to what is found, a finding gone dropped"),
    pytest.param({RECORD: (IMPORT,)}, WriteBaseline(ROOT, "cli", ROOT.parent), BaselineWritten(WRITTEN, 1, 1, False),
                 id="a record is never raised, so a new violation stays one"),
    pytest.param({RECORD: (IMPORT,)}, WriteBaseline(ROOT, "cli", ROOT.parent, reset=True),
                 BaselineWritten(WRITTEN, 2, 1, True), id="reset writes every violation found now"),
    pytest.param({}, WriteBaseline(Path("/elsewhere"), "cli", ROOT.parent), NotADirectory(Path("/elsewhere")),
                 id="an app folder that is no folder is refused"),
    pytest.param({}, WriteBaseline(ROOT, "broken", ROOT.parent), ChecksCannotRun(REFUSED),
                 id="a profile whose own checks cannot run is refused with every problem"),
    pytest.param({}, WriteBaseline(ROOT, "gone", ROOT.parent), CheckRefused(UNUSABLE),
                 id="a profile spec refuses is refused with spec's reason"),
])
def test_write_baseline(given, when, then):
    assert rules(BAD, FakeBaselines(given)).write_baseline(when) == then


@pytest.mark.parametrize("record, reset, kept", [
    pytest.param({}, False, (IMPORT, STRUCTURE), id="every violation, with no record"),
    pytest.param({RECORD: (IMPORT, STRUCTURE, GONE)}, False, (IMPORT, STRUCTURE), id="a finding gone dropped"),
    pytest.param({RECORD: (IMPORT,)}, False, (IMPORT,), id="never raised"),
    pytest.param({RECORD: (IMPORT,)}, True, (IMPORT, STRUCTURE), id="raised by reset"),
])
def test_what_the_record_holds_once_written(record, reset, kept):
    baselines = FakeBaselines(record)
    rules(BAD, baselines).write_baseline(WriteBaseline(ROOT, "cli", ROOT.parent, reset=reset))
    assert baselines.records[RECORD] == kept


def test_a_record_that_cannot_be_read_is_refused_with_its_reason():
    baselines = FakeBaselines(unreadable={RECORD: "the baseline cannot be read"})
    assert rules(BAD, baselines).write_baseline(WriteBaseline(ROOT, "cli", ROOT.parent)) == CheckRefused(
        "the baseline cannot be read")


def test_a_check_holds_back_what_the_record_holds_and_says_how_it_stands():
    checked = rules(BAD, FakeBaselines({RECORD: (IMPORT, STRUCTURE)})).check_app(CheckApp(ROOT, "cli", ROOT.parent))
    assert (checked.violations, checked.ok) == ((), True)
    assert checked.enforcement.baseline == BaselineStanding(
        ".xarch/baseline.json", (RuleCeiling("may-import", 1, 1), RuleCeiling("structure", 1, 1)), 2, 0)


def test_a_record_above_the_code_passes_and_fails_strict():
    baselines = FakeBaselines({RECORD: (IMPORT, STRUCTURE)})
    plain = rules(GOOD, baselines, ()).check_app(CheckApp(ROOT, "cli", ROOT.parent))
    strict = rules(GOOD, baselines, ()).check_app(CheckApp(ROOT, "cli", ROOT.parent, strict=True))
    assert (plain.ok, plain.enforcement.baseline.below, strict.ok) == (True, 2, False)
    assert strict.enforcement.strict == (FindingView("baseline", "2 finding(s) below baseline (.xarch/baseline.json): "
                                                                 "run `xarch baseline write` to lower it"),)
