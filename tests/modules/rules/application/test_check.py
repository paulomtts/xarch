"""Use case: check the imports of an app, on an in-memory source tree: no filesystem, no ast."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from xarch.kernel.logic.placement import Repeat, Target
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.rules.application.services.locate import Locator
from xarch.modules.rules.contract import CheckImports, ImportsChecked, NotADirectory
from xarch.modules.rules.domain.values import (
    Drift,
    Enforcement,
    Excluded,
    Exclusion,
    Finding,
    Import,
    InitFile,
    Origin,
    Profile,
)

ROOT = Path("/src/pkg")


def profile(entry: str) -> Profile:
    """A small profile entered through entry: a kernel, a platform, and a domain and services in every module."""
    parts = {"kernel": ("kernel",), "platform": ("platform",), "domain": ("modules", "*", "domain"),
             "services": ("modules", "*", "application", "services"), entry: (entry,)}
    rules = {"kernel": (Target("kernel"),), "platform": (Target("platform"), Target("kernel")),
             "domain": (Target("domain", "own"), Target("kernel")),
             "services": (Target("services", "own"), Target("domain", "own"), Target("kernel")),
             entry: (Target(entry), Target("kernel"))}
    folders = ((), ("kernel",), ("platform",), ("modules",), ("modules", "*"), ("modules", "*", "domain"),
               ("modules", "*", "application"), ("modules", "*", "application", "services"), (entry,))
    return Profile(parts, rules, folders, libraries={name: () for name in parts}, repeats=(Repeat("module", ("modules",)),))


PROFILES = FakeProfiles({"cli": profile("cli"), "web": profile("web")})


def controller_of(tree, profiles) -> RulesController:
    return RulesController(ImportCheck(tree, profiles), Locator(tree, profiles))


def run(files, package="app", root=ROOT, profile="cli"):
    controller = controller_of(FakeSourceTree(ROOT, files), PROFILES)
    return controller.check(CheckImports(root, package, profile))


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"kernel/x.py": [Import(3, ("app", "platform", "sql"))]}, CheckImports(ROOT, "app", "cli"),
                 ImportsChecked((Violation("pkg/kernel/x.py", 3, "kernel/ may not import platform/ (app.platform.sql)",
                                           "rules", "import only kernel/ in kernel/ (parts.kernel.may_import), or move this code "
                                                    "to a part that may import platform/"),)),
                 id="a forbidden absolute import is reported"),
    pytest.param({"kernel/x.py": [Import(3, ("app", "kernel", "y"))]}, CheckImports(ROOT, "app", "cli"),
                 ImportsChecked(()), id="an allowed import is no violation"),
    pytest.param({}, CheckImports(Path("/nowhere"), "app", "cli"), NotADirectory(Path("/nowhere")),
                 id="a missing root is reported as such"),
])
def test_check(given, when, then):
    assert controller_of(FakeSourceTree(ROOT, given), PROFILES).check(when) == then


def test_the_root_package_name_is_a_parameter():
    files = {"kernel/x.py": [Import(1, ("xarch", "platform"), names=("sql",))]}
    assert [str(v) for v in run(files, package="app").violations] == [
        "pkg/kernel/x.py:1: kernel/ may not import the outside package xarch (parts.kernel.libraries)"]
    assert [str(v) for v in run(files, package="xarch").violations] == [
        "pkg/kernel/x.py:1: kernel/ may not import platform/ (xarch.platform)"]


def test_relative_imports_are_resolved_against_the_file_package():
    files = {"modules/a/domain/x.py": [Import(2, ("application", "services"), level=2, names=("svc",))]}
    assert [str(v) for v in run(files).violations] == [
        "pkg/modules/a/domain/x.py:2: domain/ of modules/a may not import services/ of modules/a "
        "(app.modules.a.application.services)"]


def test_a_file_outside_the_layout_is_not_checked():
    assert run({"stray.py": [Import(1, ("app", "modules", "a", "adapters"))]}).violations == ()


def test_the_profile_decides_the_entry_point():
    files = {"web/routes/x.py": [Import(4, ("app", "platform"), names=("sql",))]}
    assert run(files, profile="cli").violations == ()
    assert [str(v) for v in run(files, profile="web").violations] == [
        "pkg/web/routes/x.py:4: web/ may not import platform/ (app.platform)"]


def test_a_closed_tree_reports_a_file_in_no_part_and_no_folder_of_the_layout():
    closed = FakeProfiles({"cli": replace(profile("cli"), closed_tree=True)})
    controller = controller_of(FakeSourceTree(ROOT, {"stray.py": [], "kernel/x.py": []}), closed)
    assert [str(v) for v in controller.check(CheckImports(ROOT, "app", "cli")).violations] == [
        "pkg/stray.py: lies in no part and no folder of the layout (closed-tree)"]


def test_the_enforcement_holds_the_origin_the_ungoverned_files_the_init_files_and_what_strict_fails_on():
    origin = Origin("cli", True, None, ("closed-tree",), ("closed-tree",))
    files = (InitFile(("tests", "test_rules.py"), "check()\n", True), InitFile(("AGENTS.md",), "be good\n"))
    profiles = FakeProfiles({"cli": profile("cli")}, {"cli": origin}, {"cli": files})
    tree = FakeSourceTree(ROOT, {"stray.py": [], "kernel/x.py": []}, texts={Path("/src/tests/test_rules.py"): "x\n"})
    result = controller_of(tree, profiles).check(CheckImports(ROOT, "app", "cli"))
    assert result.enforcement == Enforcement(
        origin, ("pkg/stray.py",), (Drift("tests/test_rules.py", "changed"), Drift("AGENTS.md", "missing")),
        strict=(Finding("ungoverned", "pkg/stray.py"), Finding("init_files", "tests/test_rules.py is changed"),
                Finding("init_files", "AGENTS.md is missing")))


def test_an_excluded_folder_is_never_read_nor_listed_as_ungoverned_and_is_named_in_the_enforcement():
    excluding = FakeProfiles({"cli": replace(profile("cli"), closed_tree=True, excluded=(
        Exclusion(("examples",), "shipped as data"), Exclusion(("kernel", "legacy"), "copied code")))})
    bad = [Import(1, ("app", "platform"), names=("sql",))]
    tree = FakeSourceTree(ROOT, {"examples/x.py": bad, "examples/deep/y.py": [], "kernel/legacy/z.py": bad,
                                 "kernel/x.py": bad, "stray.py": []})
    result = controller_of(tree, excluding).check(CheckImports(ROOT, "app", "cli"))
    assert [str(v) for v in result.violations] == [
        "pkg/kernel/x.py:1: kernel/ may not import platform/ (app.platform)",
        "pkg/stray.py: lies in no part and no folder of the layout (closed-tree)"]
    assert result.enforcement.ungoverned == ("pkg/stray.py",)
    assert result.enforcement.excluded == (Excluded("pkg/examples", "shipped as data"),
                                           Excluded("pkg/kernel/legacy", "copied code"))


def test_an_excluded_folder_is_not_a_finding_strict_fails_on():
    excluding = FakeProfiles({"cli": replace(profile("cli"), excluded=(Exclusion(("examples",), "shipped as data"),))})
    result = controller_of(FakeSourceTree(ROOT, {"examples/x.py": [], "kernel/x.py": []}), excluding).check(
        CheckImports(ROOT, "app", "cli"))
    assert result.enforcement.strict == ()
