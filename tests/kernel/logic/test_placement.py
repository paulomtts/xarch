"""Where a path sits among path patterns, and which places a rule's target reaches."""
import pytest

from xarch.kernel.logic.placement import module_steps, place_of, reaches, repeat_of, root_of, stands_for_folder, with_itself
from xarch.kernel.placement import EVERYTHING, Marks, Place, Repeat, Target

MARKS = Marks(".src", "pkg.src")

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
    assert place_of(patterns, ("domain", "index.mod"), Marks(".mod", "index.mod")) == Place("domain")
    assert place_of(patterns, ("domain", "x.src"), Marks()) == Place("domain", None, ("x.src",))
    assert place_of(patterns, ("main.src",), Marks()) == Place("main")


SRC = Marks(".src", "pkg.src")


@pytest.mark.parametrize("path, steps, folder", [
    pytest.param(("docs", "rule.src"), ("docs", "rule"), False, id="a file is named without its ending"),
    pytest.param(("docs", "pkg.src"), ("docs",), True, id="the file that stands for its folder is the folder"),
    pytest.param(("docs", "pkg"), ("docs",), True, id="written without its ending too"),
    pytest.param(("docs",), ("docs",), False, id="a folder is its own steps"),
    pytest.param((), (), False, id="the root is no file"),
])
def test_a_path_as_the_language_names_it_and_whether_it_stands_for_its_folder(path, steps, folder):
    assert (module_steps(path, SRC), stands_for_folder(path, SRC)) == (steps, folder)
