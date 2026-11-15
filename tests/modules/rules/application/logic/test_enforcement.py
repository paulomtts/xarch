"""The enforcement findings on hand-built values: the skipped tests, the dynamic imports, the init files that drifted,
and which findings --strict fails on."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import PYTHON
from xarch.kernel.logic.language import LanguageView
from xarch.kernel.logic.origin import Loosened, Origin
from xarch.kernel.logic.placement import Excluded
from xarch.kernel.logic.testing import Framework
from xarch.kernel.violations import At, Weak
from xarch.modules.rules.application.logic.enforcement import (
    detail,
    drift,
    dynamic,
    excluded_folder,
    folders,
    skipped,
    strict_findings,
)
from xarch.modules.rules.domain.values import Drift, Enforcement, Finding, InitFile, Profile, SourceFile, Use

SKIPS = (("pytest", "mark", "skip"), ("pytest", "mark", "xfail"), ("pytest", "skip"))
PROFILE = Profile(parts={}, rules={}, framework=Framework(("test_*.py",), "test_*", SKIPS), language=PYTHON)


def file(name: str, *uses: Use) -> SourceFile:
    return SourceFile(name, tuple(name.split("/")[1:]), (), uses=uses)


def test_a_skip_is_every_use_of_a_name_the_profile_lists_or_one_below_it():
    tests = [file("tests/test_a.py", Use(3, ("pytest", "mark", "skip"), 1), Use(4, ("pytest", "mark", "skipif"), 1),
                  Use(5, ("pytest", "skip"), 1), Use(6, ("pytest", "mark", "xfail", "with_args"), 1),
                  Use(7, ("pytest", "mark", "parametrize"), 1))]
    assert skipped(tests, PROFILE) == [At("tests/test_a.py", 3), At("tests/test_a.py", 5), At("tests/test_a.py", 6)]


def test_without_skips_in_the_profile_no_skip_is_counted():
    tests = [file("tests/test_a.py", Use(3, ("pytest", "mark", "skip"), 1))]
    assert skipped(tests, Profile(parts={}, rules={})) == []


def test_a_dynamic_import_is_a_use_of_importlib_s_import_module_or_of_import():
    files = [file("app/kernel/dyn.py", Use(2, ("importlib", "import_module"), 1), Use(3, ("builtins", "__import__"), 0),
                  Use(4, ("importlib", "resources", "files"), 1)),
             file("tests/test_x.py", Use(9, ("importlib", "__import__"), 2))]
    assert dynamic(files, PROFILE) == [At("app/kernel/dyn.py", 2), At("app/kernel/dyn.py", 3), At("tests/test_x.py", 9)]


@pytest.mark.parametrize("found, expected", [
    pytest.param(None, [Drift(("tests", "test_rules.py"), "missing")], id="a missing file is reported"),
    pytest.param("check()\n", [], id="a file as init writes it is fine"),
    pytest.param("check(--loose)\n", [Drift(("tests", "test_rules.py"), "changed")], id="a pinned file that differs is changed"),
])
def test_a_pinned_init_file(found, expected):
    assert drift([InitFile(("tests", "test_rules.py"), "check()\n", True)], [found]) == expected


def test_a_file_that_is_not_pinned_is_reported_only_when_missing():
    files = [InitFile(("AGENTS.md",), "be good\n"), InitFile(("ruff.toml",), "x\n")]
    assert drift(files, ["be bad\n", None]) == [Drift(("ruff.toml",), "missing")]


def test_strict_fails_on_every_finding_but_the_guards_its_baseline_also_leaves_off_and_how_the_profile_differs():
    enforcement = Enforcement(
        Origin("mine.yaml", False, "web", ("no-comments", "closed-tree"), ("closed-tree",),
               (Loosened("rules", "domain", "platform"),)),
        ungoverned=("app/scripts/x.py",), init_files=(CHANGED,), skipped=(SKIP,), dynamic=(DYNAMIC,), weak=(WEAK,))
    assert strict_findings(enforcement) == (
        Finding("guards_off", "no-comments"), Finding("ungoverned", "app/scripts/x.py"), Finding("init_files", CHANGED),
        Finding("skipped", SKIP), Finding("dynamic", DYNAMIC), Finding("weak", WEAK))


CHANGED = Drift(("tests", "test_rules.py"), "changed")
SKIP = At("tests/test_a.py", 3)
DYNAMIC = At("app/kernel/dyn.py", 2)
WEAK = Weak("stand-ins", "tests/fakes/repo.py", 1, "FakeRepo does not define get, which Repo declares")


@pytest.mark.parametrize("item, said", [
    pytest.param("no-comments", "no-comments", id="a guard or a file is its name"),
    pytest.param(CHANGED, "tests/test_rules.py is changed", id="an init file is its path and its state"),
    pytest.param(SKIP, "tests/test_a.py:3", id="a place is its file and line"),
    pytest.param(WEAK, "tests/fakes/repo.py:1: FakeRepo does not define get, which Repo declares",
                 id="a weak check is its place and its message"),
    pytest.param(Weak("dead-code", "app/x.py", 0, "a file no test reaches"), "app/x.py: a file no test reaches",
                 id="a weak check of a whole file shows no line"),
])
def test_the_detail_of_a_finding(item, said):
    assert detail(item) == said


def test_a_bundled_profile_with_nothing_found_passes_strict():
    assert strict_findings(Enforcement(Origin("web", True, None, ("closed-tree",), ("closed-tree",)))) == ()


def test_a_framework_that_lists_no_skips_counts_none():
    tests = [file("tests/test_a.py", Use(3, ("pytest", "mark", "skip"), 1))]
    assert skipped(tests, Profile(parts={}, rules={}, framework=Framework(("test_*.py",), "test_*"))) == []


def test_a_dynamic_import_is_what_the_language_of_the_profile_lists():
    files = [file("app/a.py", Use(2, ("sys", "load"), 1), Use(3, ("importlib", "import_module"), 1))]
    other = replace(PROFILE, language=LanguageView(dynamic=(("sys", "load"),)))
    assert dynamic(files, other) == [At("app/a.py", 2)]
    assert dynamic(files, replace(PROFILE, language=LanguageView())) == []


def test_a_name_beside_a_dynamic_import_is_no_dynamic_import():
    files = [file("app/kernel/a.py", Use(2, ("importlib", "reload"), 1), Use(3, ("builtins", "__build_class__"), 0),
                  Use(4, ("importlib",), 1))]
    assert dynamic(files, PROFILE) == []


def test_a_pinned_file_as_init_writes_it_and_a_changed_one_are_told_apart_in_order():
    files = [InitFile(("a",), "x\n", True), InitFile(("b",), "y\n", True), InitFile(("c",), "z\n")]
    assert drift(files, ["x\n", "Y\n", None]) == [Drift(("b",), "changed"), Drift(("c",), "missing")]


def test_with_no_bundled_profile_to_compare_with_every_guard_left_off_fails_strict():
    enforcement = Enforcement(Origin("mine.yaml", False, None, ("no-comments", "closed-tree"), ()))
    assert strict_findings(enforcement) == (Finding("guards_off", "no-comments"), Finding("guards_off", "closed-tree"))


def test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_never_a_strict_finding():
    differing = Origin("mine.yaml", False, "web", (), (), (Loosened("rules", "domain", "platform"),
                                                           Loosened("libraries", "", ""), Loosened("pinned", "", "x")))
    assert strict_findings(Enforcement(differing)) == ()


def test_the_excluded_folders_are_shown_below_the_app_folder():
    assert [excluded_folder("pkg", e) for e in (Excluded(("examples",), "shipped as data"), Excluded(("a", "b"), "copied"))
            ] == ["pkg/examples", "pkg/a/b"]


@pytest.mark.parametrize("files, tops", [
    pytest.param(["app/main.py", "app/kernel/x.py", "app/kernel/y/z.py", "app/scripts/a.py"],
                 ["app/main.py", "app/kernel/", "app/scripts/"],
                 id="a file at the app's root is itself, any other its top folder, each once in order"),
])
def test_folders(files, tops):
    assert folders(files) == tops
