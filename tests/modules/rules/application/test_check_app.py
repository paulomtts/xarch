"""Use case: the whole check of an app, its source and its structure, with the profile's hints and whether it passes,
on an in-memory source tree and structure: no filesystem, no ast."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.fakes.structure import FakeStructure
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON
from xarch.kernel.source import Import
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import (
    AppChecked,
    ApproximateView,
    CheckApp,
    CheckRefused,
    ChecksCannotRun,
    Drift,
    EnforcementView,
    ExcludedView,
    FindingView,
    KnownName,
    Loosened,
    NotADirectory,
    OwnCheckView,
    Partial,
    Weak,
)
from xarch.modules.rules.domain.outcomes import InitFile, Standing
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Framework
from xarch.profile_values.testing import TestForm as DeclaredForm

ROOT = Path("/src/pkg")
PROFILE = Profile({"kernel": ("kernel",), "platform": ("platform",)},
                  {"kernel": (), "platform": (Target("kernel"),)}, ((), ("kernel",), ("platform",)),
                  imports_libraries={"kernel": (), "platform": ()}, hints={"may-import": "ask first"})
BAD = {"kernel/x.py": [Import(1, ("pkg", "platform", "io"))], "platform/io.py": []}
GOOD = {"kernel/x.py": [], "platform/io.py": [Import(1, ("pkg", "kernel", "x"))]}
IMPORT = Violation("pkg/kernel/x.py", 1, "kernel/ may not import platform/ (pkg.platform.io)", "may-import",
                   "import only kernel/ in kernel/ (parts.kernel.imports.may), or move this code to a part that may "
                   "import platform/")
MISSING = Violation("pkg", 0, "missing kernel/logic/", "structure", "create pkg/kernel/logic/")


REFUSED = ("checks.mine.mode: is 'fial': write fail or list",)
UNUSABLE = "gone: cannot read the file: no such file"
STRICT_AGAINST = ("--against shows a comparison and --strict fails on one: run `check --strict` without --against, "
                  "and it judges the profile against its baseline")


def check(files: dict, when: CheckApp, structure: list[Violation] | None = None, profile: Profile = PROFILE):
    profiles = FakeProfiles({"cli": profile}, refused={"broken": REFUSED}, unusable={"gone": UNUSABLE})
    return controller(FakeSourceTree(ROOT, files), profiles, FakeStructure(structure)).check_app(when)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "cli", ROOT.parent),
                 AppChecked((), EnforcementView(), {"may-import": "ask first"}, True),
                 id="an app with nothing wrong passes, with the profile's hints"),
    pytest.param(dict(files=BAD, structure=[MISSING]), CheckApp(ROOT, "cli", ROOT.parent),
                 AppChecked((MISSING, IMPORT), EnforcementView(), {"may-import": "ask first"}, False),
                 id="the source's and the structure's violations come in order of file, line and rule, and the check "
                    "fails"),
    pytest.param(dict(files={**GOOD, "stray.py": []}), CheckApp(ROOT, "cli", ROOT.parent, strict=True),
                 AppChecked((), EnforcementView(ungoverned=("pkg/stray.py",), ungoverned_folders=("pkg/stray.py",),
                                            strict=(FindingView("ungoverned", "pkg/stray.py"),)),
                            {"may-import": "ask first"}, False),
                 id="under strict a finding of the enforcement fails the check too"),
    pytest.param(dict(files=BAD, structure=[MISSING]),
                 CheckApp(ROOT, "cli", ROOT.parent, paths=(Path("pkg/kernel/x.py"),)),
                 AppChecked((IMPORT,), EnforcementView(), {"may-import": "ask first"}, False,
                            Partial(("pkg/kernel/x.py",), 1)),
                 id="a check of some paths shows their violations alone, counts the others, and fails on those shown"),
    pytest.param(dict(files=BAD, structure=[MISSING]),
                 CheckApp(ROOT, "cli", ROOT, paths=(Path("platform"),)),
                 AppChecked((), EnforcementView(), {"may-import": "ask first"}, True, Partial(("platform",), 2)),
                 id="a path is read from the working folder, and one with no violation passes though others have"),
    pytest.param(dict(files={**GOOD, "stray.py": []}),
                 CheckApp(ROOT, "cli", ROOT.parent, strict=True, paths=(Path("pkg/kernel/x.py"),)),
                 AppChecked((), EnforcementView(ungoverned=("pkg/stray.py",), ungoverned_folders=("pkg/stray.py",),
                                                strict=(FindingView("ungoverned", "pkg/stray.py"),)),
                            {"may-import": "ask first"}, False, Partial(("pkg/kernel/x.py",), 0)),
                 id="under strict a check of some paths still fails on the enforcement of the whole app"),
    pytest.param(dict(files=GOOD), CheckApp(Path("/elsewhere"), "cli", ROOT.parent), NotADirectory(Path("/elsewhere")),
                 id="an app folder that is no folder is refused"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "broken", ROOT.parent), ChecksCannotRun(REFUSED),
                 id="a profile whose own checks cannot run is refused with every problem"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "gone", ROOT.parent), CheckRefused(UNUSABLE),
                 id="a profile spec refuses is refused with spec's reason"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "cli", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused"),
    pytest.param(dict(files=GOOD), CheckApp(Path("/elsewhere"), "cli", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused before the app folder is looked at"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "gone", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused before the profile is read"),
])
def test_check_app(given, when, then):
    assert check(given.get("files", {}), when, given.get("structure"), given.get("profile", PROFILE)) == then


def test_without_strict_a_finding_of_the_enforcement_does_not_fail_the_check():
    result = check({**GOOD, "stray.py": []}, CheckApp(ROOT, "cli", ROOT.parent))
    assert isinstance(result, AppChecked) and result.ok


def test_against_without_strict_checks_as_without_it():
    files = {**BAD, "stray.py": []}
    assert check(files, CheckApp(ROOT, "cli", ROOT.parent, against="web"), [MISSING]) == check(
        files, CheckApp(ROOT, "cli", ROOT.parent), [MISSING])


def paired(strict: bool) -> AppChecked | CheckRefused:
    profiles = FakeProfiles({"cli": PROFILE})
    structure = FakeStructure(counterparts=(("sql-has-contract", 0), ("fakes-name-a-module", 2)))
    return controller(FakeSourceTree(ROOT, GOOD), profiles, structure).check_app(CheckApp(ROOT, "cli", ROOT.parent,
                                                                                        strict=strict))


VACUOUS = ("counterparts.sql-has-contract matches nothing in the project, so it passes for want of anything to check: "
           "widen its for, or drop it")


def test_each_counterpart_is_listed_with_what_it_read_and_one_that_read_nothing_fails_strict():
    assert paired(True) == AppChecked((), EnforcementView(strict=(FindingView("vacuous", VACUOUS),), counterparts=(
        OwnCheckView("sql-has-contract", 0, VACUOUS),
        OwnCheckView("fakes-name-a-module", 2, "counterparts.fakes-name-a-module read 2 sources"))),
        {"may-import": "ask first"}, False)
    assert paired(False).ok


def entered(entry: str) -> Profile:
    """A small profile entered through entry: a kernel, a platform, and a domain and services in every module."""
    parts = {"kernel": ("kernel",), "platform": ("platform",), "domain": ("modules", "*", "domain"),
             "services": ("modules", "*", "application", "services"), entry: (entry,)}
    rules = {"kernel": (Target("kernel"),), "platform": (Target("platform"), Target("kernel")),
             "domain": (Target("domain", "own"), Target("kernel")),
             "services": (Target("services", "own"), Target("domain", "own"), Target("kernel")),
             entry: (Target(entry), Target("kernel"))}
    folders = ((), ("kernel",), ("platform",), ("modules",), ("modules", "*"), ("modules", "*", "domain"),
               ("modules", "*", "application"), ("modules", "*", "application", "services"), (entry,))
    return Profile(parts, rules, folders, imports_libraries={name: () for name in parts}, repeats=(Repeat("module", ("modules",)),))


ENTERED = FakeProfiles({"cli": entered("cli"), "web": entered("web")})


def checked(files, profiles: FakeProfiles = ENTERED, profile: str = "cli", root: Path = ROOT,
            tree: FakeSourceTree | None = None) -> AppChecked:
    """The check of the app below root, with files, under profile."""
    result = controller(tree or FakeSourceTree(root, files), profiles).check_app(CheckApp(root, profile, root.parent))
    assert isinstance(result, AppChecked)
    return result


def test_the_app_is_imported_as_the_package_its_folder_names():
    files = {"kernel/x.py": [Import(1, ("xarch", "platform"), names=("sql",))]}
    assert [str(v) for v in checked(files, root=Path("/src/app")).violations] == [
        "app/kernel/x.py:1: kernel/ may not import the outside package xarch (parts.kernel.imports.libraries)"]
    assert [str(v) for v in checked(files, root=Path("/src/xarch")).violations] == [
        "xarch/kernel/x.py:1: kernel/ may not import platform/ (xarch.platform)"]


def test_relative_imports_are_resolved_against_the_file_package():
    files = {"modules/a/domain/x.py": [Import(2, ("application", "services"), names=("svc",), relative=True, up=1)]}
    assert [str(v) for v in checked(files).violations] == [
        "pkg/modules/a/domain/x.py:2: domain/ of modules/a may not import services/ of modules/a "
        "(pkg.modules.a.application.services)"]


def test_a_file_outside_the_layout_is_not_checked():
    assert checked({"stray.py": [Import(1, ("pkg", "modules", "a", "adapters"))]}).violations == ()


def test_the_profile_decides_the_entry_point():
    files = {"web/routes/x.py": [Import(4, ("pkg", "platform"), names=("sql",))]}
    assert checked(files, profile="cli").violations == ()
    assert [str(v) for v in checked(files, profile="web").violations] == [
        "pkg/web/routes/x.py:4: web/ may not import platform/ (pkg.platform)"]


def test_a_closed_tree_reports_a_file_in_no_part_and_no_folder_of_the_layout():
    closed = FakeProfiles({"cli": replace(entered("cli"), closed_tree=True)})
    assert [str(v) for v in checked({"stray.py": [], "kernel/x.py": []}, closed).violations] == [
        "pkg/stray.py: lies in no part and no folder of the layout (closed-tree)"]


def test_the_enforcement_holds_the_ungoverned_files_the_init_files_and_what_strict_fails_on():
    guards = Standing(("closed-tree",), ("closed-tree",), ())
    files = (InitFile(("tests", "test_rules.py"), "check()\n", True), InitFile(("AGENTS.md",), "be good\n"))
    profiles = FakeProfiles({"cli": entered("cli")}, {"cli": guards}, {"cli": files})
    tree = FakeSourceTree(ROOT, {"stray.py": [], "kernel/x.py": []}, texts={Path("/src/tests/test_rules.py"): "x\n"})
    assert checked({}, profiles, tree=tree).enforcement == EnforcementView(
        ("pkg/stray.py",), ("pkg/stray.py",),
        (Drift(("tests", "test_rules.py"), "changed"), Drift(("AGENTS.md",), "missing")),
        strict=(FindingView("ungoverned", "pkg/stray.py"), FindingView("init_files", "tests/test_rules.py is changed"),
                FindingView("init_files", "AGENTS.md is missing")))


def test_a_part_the_profile_redefines_without_its_litmus_is_what_strict_fails_on():
    said = "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)"
    looser = (Loosened("untested", "api", "", "api is newly marked untested (parts.api.untested)"),
              Loosened("litmus", "cli", "", said))
    profiles = FakeProfiles({"cli": entered("cli")}, {"cli": Standing((), (), (), looser)})
    assert checked({"kernel/x.py": []}, profiles).enforcement.strict == (FindingView("litmus", said),)


def test_the_enforcement_names_the_language_of_the_profile():
    profiles = FakeProfiles({"cli": replace(entered("cli"), language=PYTHON)})
    assert checked({"kernel/x.py": []}, profiles).enforcement.language == "Python"
    assert checked({"kernel/x.py": []}).enforcement.language == ""


def test_an_excluded_folder_is_never_read_nor_listed_as_ungoverned_and_is_named_in_the_enforcement():
    excluding = FakeProfiles({"cli": replace(entered("cli"), closed_tree=True, excluded=(
        Excluded(("examples",), "shipped as data"), Excluded(("kernel", "legacy"), "copied code")))})
    bad = [Import(1, ("pkg", "platform"), names=("sql",))]
    result = checked({"examples/x.py": bad, "examples/deep/y.py": [], "kernel/legacy/z.py": bad, "kernel/x.py": bad,
                      "stray.py": []}, excluding)
    assert [str(v) for v in result.violations] == [
        "pkg/kernel/x.py:1: kernel/ may not import platform/ (pkg.platform)",
        "pkg/stray.py: lies in no part and no folder of the layout (closed-tree)"]
    assert result.enforcement.ungoverned == ("pkg/stray.py",)
    assert result.enforcement.excluded == (ExcludedView("pkg/examples", "shipped as data"),
                                           ExcludedView("pkg/kernel/legacy", "copied code"))


def test_an_excluded_folder_is_not_a_finding_strict_fails_on():
    excluding = FakeProfiles({"cli": replace(entered("cli"), excluded=(Excluded(("examples",), "shipped as data"),))})
    assert checked({"examples/x.py": [], "kernel/x.py": []}, excluding).enforcement.strict == ()


def test_a_key_whose_check_reads_a_fact_partly_is_listed_as_approximate_and_fails_strict():
    partly = Shortfall("parts.services.names", "class", "a class defined in a branch is not read")
    profiles = FakeProfiles({"cli": replace(entered("cli"), approximate=(partly,))})
    result = checked({"kernel/x.py": []}, profiles)
    said = "parts.services.names reads class only partly: a class defined in a branch is not read"
    assert result.enforcement.approximate == (
        ApproximateView("parts.services.names", "class", "a class defined in a branch is not read", said),)
    assert result.enforcement.strict == (FindingView("approximate", said),)


def test_a_part_that_reads_no_top_level_functions_for_want_of_the_fact_is_listed_as_approximate_by_its_sentence():
    said = "holds reads no top-level functions: the language Toy does not supply function.top_level"
    unread = Shortfall("parts.domain.holds", "function.top_level", said, True)
    profiles = FakeProfiles({"cli": replace(entered("cli"), approximate=(unread,))})
    result = checked({"kernel/x.py": []}, profiles)
    assert result.enforcement.approximate == (ApproximateView("parts.domain.holds", "function.top_level", said, said),)
    assert result.enforcement.strict == (FindingView("approximate", said),)


def test_a_public_name_the_profile_accepts_as_only_the_tests_is_named_in_the_enforcement_and_an_entry_that_no_longer_holds_is_weak():
    rules = SourceFile("pkg/kernel/rules.py", ("kernel", "rules.py"), (), classes=(Class(3, "Rule"),),
                       functions=(Function(9, "decide"),))
    accepting = replace(entered("cli"), dead_code=True, tests_only=True,
                        tests_only_known=("kernel/rules.py:Rule", "kernel/rules.py:gone"))
    test = SourceFile("tests/kernel/test_rules.py", ("kernel", "test_rules.py"), (),
                      functions=(Function(3, "test_rule", named=frozenset({"Rule"})),))
    tests = Path("/src/tests")
    tree = FakeSourceTree(ROOT, {"kernel/rules.py": rules}, more={tests: {"kernel/test_rules.py": test}})
    result = controller(tree, FakeProfiles({"cli": accepting})).check_app(CheckApp(ROOT, "cli", ROOT.parent, tests))
    assert isinstance(result, AppChecked)
    decide = Weak("dead-code", "pkg/kernel/rules.py", 9, "decide is public, but no other file of the app names it: only "
                                                       "the tests, or nothing, use it (guards.dead-code.tests_only)",
                  "delete decide and what tests it alone, or make it private when its own file uses it, or use it where "
                  "the app needs it")
    gone = Weak("dead-code", "pkg/kernel/rules.py", 0, "kernel/rules.py defines no public class or top-level function "
                                                     "gone, which guards.dead-code.known lists (guards.dead-code.known)",
                "drop kernel/rules.py:gone from guards.dead-code.known, or name the file and the name as they are now")
    assert result.enforcement == EnforcementView(
        weak=(decide, gone), strict=(FindingView("weak", f"pkg/kernel/rules.py:9: {decide.message}"),
                                     FindingView("weak", f"pkg/kernel/rules.py: {gone.message}")),
        known=(KnownName("pkg/kernel/rules.py", 3, "Rule"),))


def test_the_tests_are_read_with_the_framework_s_forms_and_globals_and_the_app_with_none():
    forms = (DeclaredForm(function="test_*"),)
    framed = replace(entered("cli"), framework=Framework(("test_*.py",), forms, globals=(("it",),)))
    tests = Path("/src/tests")
    tree = FakeSourceTree(ROOT, {"kernel/x.py": []}, more={tests: {"kernel/test_x.py": []}})
    controller(tree, FakeProfiles({"cli": framed})).check_app(CheckApp(ROOT, "cli", ROOT.parent, tests))
    assert (tree.forms, tree.bound) == ([(), forms], [(), (("it",),)])
