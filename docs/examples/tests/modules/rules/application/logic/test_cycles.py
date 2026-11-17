"""Cycles among modules: a module whose adapter wraps another's controller depends on it, and a ring of them is one
cycle, named from its module first by name."""
import pytest
from app.modules.rules.application.logic.cycles import cycles


@pytest.mark.parametrize("wraps, found", [
    pytest.param({"review": frozenset({"rules"}), "rules": frozenset({"spec"})}, (),
                 id="modules that wrap each other in one direction are no cycle"),
    pytest.param({"a": frozenset({"b"}), "b": frozenset({"a"})}, (("a", "b"),),
                 id="two modules that wrap each other are one cycle"),
    pytest.param({"c": frozenset({"a"}), "b": frozenset({"c"}), "a": frozenset({"b"})}, (("a", "b", "c"),),
                 id="a ring of three is one cycle, named from its module first by name"),
])
def test_cycles(wraps, found) -> None:
    assert cycles(wraps) == found
