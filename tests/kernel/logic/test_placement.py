"""Where a path sits among path patterns, and which places a rule's target reaches."""
import pytest

from xarch.kernel.logic.placement import module_steps, place_of, reaches, repeat_of, root_of, stands_for_folder, stem, with_itself
from xarch.kernel.placement import EVERYTHING, Marks, Place
from xarch.profile_values.placement import Repeat, Target

MARKS = Marks((".src",), ("pkg.src",))

PATTERNS = {
    "kernel": ("kernel",),
    "domain": ("modules", "*", "domain"),
    "controller": ("modules", "*", "application", "controller.src"),
    "services": ("modules", "*", "application", "services"),
    "migrations": ("bootstrap", "migrations"),
    "bootstrap": ("bootstrap",),
}


@pytest.mark.parametrize("path, place", [
    (("kernel", "errors.src"), Place("kernel", None, ("errors",))),
    (("kernel", "pkg.src"), Place("kernel")),
    (("modules", "docs", "domain", "values.src"), Place("domain", "docs", ("values",))),
    (("modules", "docs", "domain", "values"), Place("domain", "docs", ("values",))),
    (("modules", "docs", "application", "controller.src"), Place("controller", "docs")),
    (("modules", "docs", "application", "services", "x.src"), Place("services", "docs", ("x",))),
    (("bootstrap", "migrations", "m.src"), Place("migrations", None, ("m",))),
    (("bootstrap", "app.src"), Place("bootstrap", None, ("app",))),
    (("modules", "docs", "application", "helpers.src"), Place(None)),
    (("modules", "docs"), Place(None)),
    ((), Place(None)),
])
def test_a_path_sits_in_the_deepest_pattern_it_lies_in(path, place):
    assert place_of(PATTERNS, path, MARKS) == place


def test_a_star_does_not_match_a_literal_star():
    assert place_of(PATTERNS, ("modules", "*", "domain", "x.src"), MARKS) == Place(None)


@pytest.mark.parametrize("target, src, dst, answer", [
    (Target(EVERYTHING), Place("bootstrap"), Place(None), True),
    (Target("kernel"), Place("domain", "a"), Place("kernel", None, ("x",)), True),
    (Target("kernel"), Place("domain", "a"), Place("platform"), False),
    (Target("domain", "own"), Place("domain", "a"), Place("domain", "a"), True),
    (Target("domain", "own"), Place("domain", "a"), Place("domain", "b"), False),
    (Target("domain", "own"), Place("cli"), Place("domain", "a"), False),
    (Target("contract", "any"), Place("adapters", "a"), Place("contract", "b"), True),
    (Target("contract", "any"), Place("adapters", "a"), Place(None), False),
    (Target("domain", "own", ("values",)), Place("contract", "a"), Place("domain", "a", ("values",)), True),
    (Target("domain", "own", ("values",)), Place("contract", "a"), Place("domain", "a", ("values", "ids")), True),
    (Target("domain", "own", ("values",)), Place("contract", "a"), Place("domain", "a", ("doc",)), False),
    (Target("domain", "own", ("values",)), Place("contract", "a"), Place("domain", "a"), False),
    (Target("kernel"), Place("platform"), Place(None), False),
])
def test_a_target_reaches_its_part_in_its_scope_below_its_path(target, src, dst, answer):
    assert reaches(target, src, dst) is answer


REPEATS = (Repeat("module", ("modules",)), Repeat("plugin", ("plugins",)))


@pytest.mark.parametrize("pattern, root", [
    (("modules", "*", "domain"), ("modules",)),
    (("plugins", "*"), ("plugins",)),
    (("*", "domain"), ()),
    (("kernel",), None),
])
def test_the_root_of_a_pattern_is_the_folder_its_repeating_step_sits_in(pattern, root):
    assert root_of(pattern) == root


@pytest.mark.parametrize("pattern, found", [
    (("modules", "*", "domain"), REPEATS[0]),
    (("plugins", "*", "hooks"), REPEATS[1]),
    (("kernel",), None),
    (("other", "*", "x"), None),
])
def test_a_pattern_belongs_to_the_repeating_folder_that_sits_at_its_root(pattern, found):
    assert repeat_of(REPEATS, pattern) == found


def test_each_repeating_folder_captures_its_own_instances():
    patterns = {"domain": ("modules", "*", "domain"), "hooks": ("plugins", "*", "hooks"), "kernel": ("kernel",)}
    assert place_of(patterns, ("modules", "a", "domain", "x.src"), MARKS) == Place("domain", "a", ("x",))
    assert place_of(patterns, ("plugins", "a", "hooks", "x.src"), MARKS) == Place("hooks", "a", ("x",))
    assert place_of(patterns, ("plugins", "a", "domain", "x.src"), MARKS) == Place(None)


def test_a_part_may_always_import_itself_in_its_own_repeating_folder_whichever_it_is():
    assert with_itself("hooks", ("plugins", "*", "hooks"), []) == (Target("hooks", "own"),)


def test_a_path_is_read_with_the_marks_it_is_given_and_with_none_as_written():
    patterns = {"domain": ("domain",), "main": ("main.src",)}
    assert place_of(patterns, ("domain", "index.mod"), Marks((".mod",), ("index.mod",))) == Place("domain")
    assert place_of(patterns, ("domain", "x.src"), Marks()) == Place("domain", None, ("x.src",))
    assert place_of(patterns, ("main.src",), Marks()) == Place("main")


SRC = Marks((".src",), ("pkg.src",))


@pytest.mark.parametrize("path, steps, folder", [
    pytest.param(("docs", "rule.src"), ("docs", "rule"), False, id="a file is named without its ending"),
    pytest.param(("docs", "pkg.src"), ("docs",), True, id="the file that stands for its folder is the folder"),
    pytest.param(("docs", "pkg"), ("docs",), True, id="written without its ending too"),
    pytest.param(("docs",), ("docs",), False, id="a folder is its own steps"),
    pytest.param((), (), False, id="the root is no file"),
])
def test_a_path_as_the_language_names_it_and_whether_it_stands_for_its_folder(path, steps, folder):
    assert (module_steps(path, SRC), stands_for_folder(path, SRC)) == (steps, folder)


BRACE = Marks((".ts", ".tsx", ".mts"), ("index.ts", "index.tsx"))
"""The marks of the TypeScript-like test-only language: three endings, two package files."""
PERCENT = Marks((".cls", ".mac"))
"""The marks of the ObjectScript-like test-only language: two endings and no package file."""


@pytest.mark.parametrize("name, expected", [
    pytest.param("b.tsx", "b", id="the second ending"),
    pytest.param("b.ts", "b", id="the first ending"),
    pytest.param("b.mts", "b", id="the third ending"),
    pytest.param("b.js", None, id="an ending the language does not have"),
    pytest.param("b", None, id="no ending"),
])
def test_a_name_loses_the_ending_it_carries_and_has_no_stem_when_it_carries_none(name, expected):
    assert stem(name, BRACE) == expected


def test_the_longest_ending_a_name_carries_is_the_one_it_loses():
    assert stem("x.d.ts", Marks((".ts", ".d.ts"))) == "x"
    assert stem("x.d.ts", Marks((".d.ts", ".ts"))) == "x"


@pytest.mark.parametrize("path, place", [
    pytest.param(("a", "b.tsx"), Place("a", None, ("b",)), id="a module of any ending"),
    pytest.param(("a", "index.ts"), Place("a"), id="the first package file stands for its folder"),
    pytest.param(("a", "index.tsx"), Place("a"), id="the second one too"),
    pytest.param(("a", "index.mts"), Place("a", None, ("index",)), id="a module named index of an ending no package file has"),
])
def test_under_several_endings_a_path_is_placed_by_the_ending_it_carries(path, place):
    assert place_of({"a": ("a",)}, path, BRACE) == place


@pytest.mark.parametrize("path, folder", [
    pytest.param(("a", "index.ts"), True, id="a package file"),
    pytest.param(("a", "index"), True, id="a package file written without its ending"),
    pytest.param(("a", "index.mts"), False, id="no listed package file"),
    pytest.param(("a", "main.ts"), False, id="a module"),
])
def test_a_path_stands_for_its_folder_when_it_is_one_of_the_package_files(path, folder):
    assert stands_for_folder(path, BRACE) is folder


def test_with_no_package_file_no_path_stands_for_its_folder():
    assert (module_steps(("a", "Package.cls"), PERCENT), stands_for_folder(("a", "Package.cls"), PERCENT)) == (
        ("a", "Package"), False)
    assert stands_for_folder(("a", "Package"), PERCENT) is False
    assert module_steps(("a", "Run.mac"), PERCENT) == ("a", "Run")


def test_a_step_that_carries_no_ending_is_kept_as_written():
    assert module_steps(("a", "notes.txt"), BRACE) == ("a", "notes.txt")


def test_python_s_package_file_stands_for_its_folder_with_its_ending_or_without_it():
    python = Marks((".py",), ("__init__.py",))
    assert [stands_for_folder(path, python) for path in (("a", "__init__.py"), ("a", "__init__"), ("a", "__init__.pyx"))] == [
        True, True, False]
    assert module_steps(("a", "__init__.py"), python) == ("a",)
