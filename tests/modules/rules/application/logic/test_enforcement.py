"""The enforcement findings on hand-built values: the skipped tests, the dynamic imports, the init files that drifted,
and which findings --strict fails on."""
from dataclasses import replace

import pytest

from tests.modules.rules import builders
from tests.modules.rules.builders import PYTHON
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.enforcement import (
    detail,
    drift,
    dynamic,
    excluded_folder,
    folders,
    reading,
    skipped,
    strict_findings,
    unplaced,
    unresolved,
    weak_of,
)
from xarch.modules.rules.domain.outcomes import Enforcement, Finding, InitFile
from xarch.modules.rules.domain.parsed import SourceFile, Use
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import At, Drift, Loosened, Unresolved, Weak
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.testing import Framework
from xarch.profile_values.testing import TestForm as DeclaredForm

SKIPS = (("pytest", "mark", "skip"), ("pytest", "mark", "xfail"), ("pytest", "skip"))
PROFILE = Profile(parts={}, rules={}, framework=Framework(("test_*.py",), (DeclaredForm(function="test_*"),), SKIPS), language=PYTHON)


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
        ("no-comments", "closed-tree"), ("closed-tree",),
        ungoverned=("app/scripts/x.py",), init_files=(CHANGED,), skipped=(SKIP,), dynamic=(DYNAMIC,),
        unresolved=(UNRESOLVED_ITEM,), weak=(WEAK,))
    assert strict_findings(enforcement) == (
        Finding("guards_off", "no-comments"), Finding("ungoverned", "app/scripts/x.py"), Finding("init_files", CHANGED),
        Finding("skipped", SKIP), Finding("dynamic", DYNAMIC), Finding("unresolved", UNRESOLVED_ITEM),
        Finding("weak", WEAK))


CHANGED = Drift(("tests", "test_rules.py"), "changed")
SKIP = At("tests/test_a.py", 3)
DYNAMIC = At("app/kernel/dyn.py", 2)
UNRESOLVED_ITEM = Unresolved("app/x.py", 3, ".ordr")
WEAK = Weak("stand-ins", "tests/fakes/repo.py", 1, "FakeRepo does not define get, which Repo declares")


@pytest.mark.parametrize("item, said", [
    pytest.param("no-comments", "no-comments", id="a guard or a file is its name"),
    pytest.param(CHANGED, "tests/test_rules.py is changed", id="an init file is its path and its state"),
    pytest.param(SKIP, "tests/test_a.py:3", id="a place is its file and line"),
    pytest.param(UNRESOLVED_ITEM, 'app/x.py:3: import ".ordr" names no file of the app',
                 id="an import the reader could not follow is its place, its module as written and why"),
    pytest.param(WEAK, "tests/fakes/repo.py:1: FakeRepo does not define get, which Repo declares",
                 id="a weak check is its place and its message"),
    pytest.param(Weak("dead-code", "app/x.py", 0, "a file no test reaches"), "app/x.py: a file no test reaches",
                 id="a weak check of a whole file shows no line"),
])
def test_the_detail_of_a_finding(item, said):
    assert detail(item) == said


def test_a_bundled_profile_with_nothing_found_passes_strict():
    assert strict_findings(Enforcement(("closed-tree",), ("closed-tree",))) == ()


def test_a_framework_that_lists_no_skips_counts_none():
    tests = [file("tests/test_a.py", Use(3, ("pytest", "mark", "skip"), 1))]
    assert skipped(tests, Profile(parts={}, rules={}, framework=Framework(("test_*.py",), (DeclaredForm(function="test_*"),)))) == []


def test_a_dynamic_import_is_what_the_language_of_the_profile_lists():
    files = [file("app/a.py", Use(2, ("sys", "load"), 1), Use(3, ("importlib", "import_module"), 1))]
    other = replace(PROFILE, language=CheckedLanguage(dynamic=(("sys", "load"),)))
    assert dynamic(files, other) == [At("app/a.py", 2)]
    assert dynamic(files, replace(PROFILE, language=CheckedLanguage())) == []


def test_a_read_by_a_computed_name_of_what_an_import_binds_is_listed_as_dynamic():
    """`getattr(t, "time")` after `import time as t` may reach a name `uses.never` forbids, which no check can follow;
    a getattr of anything an import does not bind (a parameter, an object) is not listed."""
    files = [file("app/kernel/a.py", Use(2, ("builtins", "getattr"), 0, subject=("time",)),
                  Use(3, ("builtins", "getattr"), 0), Use(4, ("builtins", "setattr"), 0, subject=("time",)))]
    assert dynamic(files, PROFILE) == [At("app/kernel/a.py", 2)]
    other = replace(PROFILE, language=CheckedLanguage(dynamic_attributes=(("sys", "peek"),)))
    assert dynamic([file("app/b.py", Use(5, ("sys", "peek"), 1, subject=("os",)))], other) == [At("app/b.py", 5)]


def test_a_name_beside_a_dynamic_import_is_no_dynamic_import():
    files = [file("app/kernel/a.py", Use(2, ("importlib", "reload"), 1), Use(3, ("builtins", "__build_class__"), 0),
                  Use(4, ("importlib",), 1))]
    assert dynamic(files, PROFILE) == []


def test_a_pinned_file_as_init_writes_it_and_a_changed_one_are_told_apart_in_order():
    files = [InitFile(("a",), "x\n", True), InitFile(("b",), "y\n", True), InitFile(("c",), "z\n")]
    assert drift(files, ["x\n", "Y\n", None]) == [Drift(("b",), "changed"), Drift(("c",), "missing")]


def test_with_no_bundled_profile_to_compare_with_every_guard_left_off_fails_strict():
    enforcement = Enforcement(("no-comments", "closed-tree"), ())
    assert strict_findings(enforcement) == (Finding("guards_off", "no-comments"), Finding("guards_off", "closed-tree"))


def test_how_a_custom_profile_differs_from_the_profile_it_is_compared_with_is_never_a_strict_finding():
    """The enforcement holds only the guards a profile leaves off: how it is looser is spec's, and shown beside it."""
    assert strict_findings(Enforcement((), ())) == ()


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


def test_a_key_whose_check_reads_a_fact_partly_is_a_strict_finding_said_with_the_readers_note():
    partly = Shortfall("parts.services.names", "class", "a class defined in a branch is not read")
    assert strict_findings(Enforcement(approximate=(partly,))) == (Finding("approximate", partly),)
    assert detail(partly) == "parts.services.names reads class only partly: a class defined in a branch is not read"


UNREAD = "holds reads no top-level functions: the language Toy does not supply function.top_level"


def test_a_key_whose_check_reads_less_for_want_of_a_fact_is_a_strict_finding_said_by_its_note_alone():
    unread = Shortfall("parts.domain.holds", "function.top_level", UNREAD, True)
    assert strict_findings(Enforcement(approximate=(unread,))) == (Finding("approximate", unread),)
    assert detail(unread) == UNREAD


def test_a_check_of_the_profile_s_own_that_read_nothing_fails_strict_and_one_that_read_something_does_not():
    said = ("checks.no-todo reads nothing in the project, so it passes for want of anything to check: widen what it "
            "reads, or drop it")
    state = Enforcement(checks=(("no-todo", 0), ("store-names", 3)))
    assert strict_findings(state) == (Finding("vacuous", said),)
    assert reading("store-names", 3) == "checks.store-names read 3 facts"
    assert reading("one", 1) == "checks.one read 1 fact"
    assert reading("no-todo", 0) == said


def test_a_part_redefined_without_the_litmus_its_base_gives_it_fails_strict_as_said():
    said = "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)"
    assert strict_findings(Enforcement(unplaced=(said,))) == (Finding("litmus", said),)


def test_the_weak_findings_listed_are_those_found_then_the_untested_ones_when_there_are_tests():
    found, untested = Weak("holds", "a.py", 1, "m", "f"), Weak("dead-code", "b.py", 2, "m", "f")
    violation = Violation("c.py", 3, "m", "may-import", "f")
    assert weak_of([found, violation], [untested], True) == [found, untested]
    assert weak_of([found], [untested], False) == [found]


def test_an_import_the_reader_could_not_follow_is_listed_by_its_file_line_and_module_as_written():
    files = [builders.source("domain/services.py", builders.imp(1, "app.kernel", "ids"),
                             builders.imp(2, "", "order", up=0),
                             builders.aliased(3, "@app/domain/order", "app.domain.order", "Order"),
                             builders.unresolved(4, ".ordr", "Order", "Line"))]
    assert unresolved(files) == [Unresolved("app/domain/services.py", 4, ".ordr")]


def test_the_unresolved_imports_keep_the_order_of_the_files_and_within_a_file_go_by_line():
    files = [builders.source("kernel/a.py", builders.unresolved(9, ".late", "x"), builders.unresolved(3, ".early", "y")),
             builders.in_tests("kernel/test_a.py", builders.unresolved(2, "..gone", "z"))]
    assert unresolved(files) == [Unresolved("app/kernel/a.py", 3, ".early"), Unresolved("app/kernel/a.py", 9, ".late"),
                                 Unresolved("tests/kernel/test_a.py", 2, "..gone")]


def test_with_no_import_the_reader_could_not_follow_nothing_is_listed():
    assert unresolved([]) == []
    assert unresolved([builders.source("kernel/a.py", builders.imp(1, "app.kernel", "ids")),
                       builders.source("kernel/b.py")]) == []


def test_an_aliased_import_resolved_to_the_root_is_not_listed_and_one_the_reader_could_not_follow_fails_strict():
    aliased = builders.source("modules/docs/domain/values.py",
                              builders.aliased(3, "@app/platform/sql", "app.platform", "sql"))
    lost = builders.source("domain/services.py", builders.unresolved(4, "@app/domain/ordr", "Order"))
    assert unresolved([aliased]) == []
    found = tuple(unresolved([aliased, lost]))
    assert found == (Unresolved("app/domain/services.py", 4, "@app/domain/ordr"),)
    assert strict_findings(Enforcement(unresolved=found)) == (Finding("unresolved", found[0]),)
    assert detail(found[0]) == 'app/domain/services.py:4: import "@app/domain/ordr" names no file of the app'


def test_strict_fails_on_a_guard_the_anchor_does_not_excuse_and_on_a_litmus_the_anchor_demands():
    said = "core has no litmus, though cli, which --strict rests on, gives the part it pairs with one (parts.core.litmus)"
    demanded = unplaced((Loosened("untested", "api"), Loosened("litmus", "core", "cli", said)))
    assert demanded == (said,)
    assert strict_findings(Enforcement(("no-comments", "dead-code"), ("dead-code",), unplaced=demanded)) == (
        Finding("guards_off", "no-comments"), Finding("litmus", said))
