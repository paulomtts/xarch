"""Unit tests for the import check on an in-memory source tree: no filesystem, no ast."""
from pathlib import Path

from xarch.bootstrap.wiring import build_spec
from xarch.modules.rules.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.rules.contract import CheckImports, ImportsChecked, NotADirectory
from xarch.modules.rules.domain.values import Import
from tests.fakes.filesystem import FakeSourceTree

ROOT = Path("/src/pkg")


def run(files, package="app", root=ROOT, profile="cli"):
    controller = RulesController(ImportCheck(FakeSourceTree(ROOT, files), SpecSkeleton(build_spec())))
    return controller.check(CheckImports(root, package, profile))


def test_a_missing_root_is_reported_as_such():
    assert run({}, root=Path("/nowhere")) == NotADirectory(Path("/nowhere"))


def test_a_forbidden_absolute_import_is_reported():
    result = run({"kernel/x.py": [Import(3, ("app", "platform", "sql"))]})
    assert isinstance(result, ImportsChecked)
    assert [str(v) for v in result.violations] == ["pkg/kernel/x.py:3: kernel/ may not import platform/ (app.platform.sql)"]


def test_the_root_package_name_is_a_parameter():
    files = {"kernel/x.py": [Import(1, ("xarch", "platform"), names=("sql",))]}
    assert run(files, package="app").violations == ()
    assert [str(v) for v in run(files, package="xarch").violations] == [
        "pkg/kernel/x.py:1: kernel/ may not import platform/ (xarch.platform)"]


def test_relative_imports_are_resolved_against_the_file_package():
    files = {"modules/a/domain/x.py": [Import(2, ("application", "services"), level=2, names=("svc",))]}
    assert [str(v) for v in run(files).violations] == [
        "pkg/modules/a/domain/x.py:2: domain/ of module 'a' may not import services/ of module 'a' "
        "(app.modules.a.application.services)"]


def test_a_file_outside_the_layout_is_not_checked():
    assert run({"stray.py": [Import(1, ("app", "modules", "a", "adapters"))]}).violations == ()


def test_the_profile_decides_the_entry_point():
    files = {"web/routes/x.py": [Import(4, ("app", "platform"), names=("sql",))]}
    assert run(files, profile="cli").violations == ()
    assert [str(v) for v in run(files, profile="web").violations] == [
        "pkg/web/routes/x.py:4: web/ may not import platform/ (app.platform)"]
