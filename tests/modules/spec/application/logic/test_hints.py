"""The top-level `hints` key: a profile's own advice for a rule id, shown after the built-in fix."""
import pytest

from tests.modules.spec.profiles_v2 import layered, parsed, problems
from xarch.kernel.violations import RULES


def test_a_profile_without_hints_has_none():
    assert parsed(layered()).hints == {}


def test_a_hint_loads_by_the_rule_id_in_the_order_of_the_file():
    hints = {"stand-ins": "fakes live in tests/fakes", "rules": "see docs/project/architecture.md"}
    assert parsed(layered(hints=hints)).hints == hints


@pytest.mark.parametrize("rule", sorted(RULES))
def test_every_rule_id_may_carry_a_hint(rule):
    assert parsed(layered(hints={rule: "x"})).hints == {rule: "x"}


KNOWN = ("built-by, closed-tree, cycles, dead-code, forbidden, holds, libraries, must-import, names, no-callbacks, "
         "no-comments, no-duplicates, no-twins, package-only, pass-through, private-imports, rules, "
         "scenario-coverage, stand-ins, structure, syntax, test-tree, tiers, types-only")


@pytest.mark.parametrize("hints, problem", [
    pytest.param([], "hints: must be a mapping of rule ids to one line of text, such as {rules: see the docs}",
                 id="a list instead of a mapping"),
    pytest.param("rules", "hints: must be a mapping of rule ids to one line of text, such as {rules: see the docs}",
                 id="a string instead of a mapping"),
    pytest.param({"rulez": "x"}, f"hints.rulez: unknown rule id 'rulez': use {KNOWN}", id="an unknown rule id"),
    pytest.param({3: "x"}, f"hints.3: unknown rule id 3: use {KNOWN}", id="a rule id that is no text"),
    pytest.param({"rules": ""}, "hints.rules: must be one line of text", id="an empty hint"),
    pytest.param({"rules": "two\nlines"}, "hints.rules: must be one line of text", id="a hint of two lines"),
    pytest.param({"rules": None}, "hints.rules: must be one line of text", id="a hint that is no text"),
])
def test_a_bad_hints_entry_is_rejected(hints, problem):
    assert problems(layered(hints=hints)) == [f"layered.yaml: {problem}"]


def test_every_bad_hint_is_reported_at_once():
    assert problems(layered(hints={"nope": "x", "rules": "", "cycles": "fine"})) == [
        f"layered.yaml: hints.nope: unknown rule id 'nope': use {KNOWN}",
        "layered.yaml: hints.rules: must be one line of text"]
