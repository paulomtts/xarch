"""Where a path sits among path patterns, and which places a rule's target reaches."""
import pytest

from xarch.kernel.logic.placement import EVERYTHING, Place, Target, matches, place_of, reaches

PATTERNS = {
    "kernel": ("kernel",),
    "domain": ("modules", "*", "domain"),
    "controller": ("modules", "*", "application", "controller.py"),
    "services": ("modules", "*", "application", "services"),
    "migrations": ("bootstrap", "migrations"),
    "bootstrap": ("bootstrap",),
}


@pytest.mark.parametrize("path, place", [
    (("kernel", "errors.py"), Place("kernel", None, ("errors",))),
    (("kernel", "__init__.py"), Place("kernel")),
    (("modules", "docs", "domain", "values.py"), Place("domain", "docs", ("values",))),
    (("modules", "docs", "domain", "values"), Place("domain", "docs", ("values",))),
    (("modules", "docs", "application", "controller.py"), Place("controller", "docs")),
    (("modules", "docs", "application", "services", "x.py"), Place("services", "docs", ("x",))),
    (("bootstrap", "migrations", "m.py"), Place("migrations", None, ("m",))),
    (("bootstrap", "app.py"), Place("bootstrap", None, ("app",))),
    (("modules", "docs", "application", "helpers.py"), Place(None)),
    (("modules", "docs"), Place(None)),
    ((), Place(None)),
])
def test_a_path_sits_in_the_deepest_pattern_it_lies_in(path, place):
    assert place_of(PATTERNS, path) == place


def test_a_star_does_not_match_a_literal_star():
    assert place_of(PATTERNS, ("modules", "*", "domain", "x.py")) == Place(None)


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


@pytest.mark.parametrize("path, answer", [
    (("modules", "docs", "application"), True),
    (("modules", "docs", "application", "__init__.py"), True),
    (("modules", "docs"), False),
    (("modules", "*", "application"), False),
    (("modules", "docs", "application", "x.py"), False),
])
def test_a_path_matches_a_pattern_only_exactly(path, answer):
    assert matches(("modules", "*", "application"), path) is answer
