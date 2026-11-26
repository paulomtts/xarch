"""The top-level `hints` key: a profile's own advice for a rule id, shown after the built-in fix."""
import pytest

from tests.modules.spec.profiles import layered, parsed, problems
from xarch.kernel.violations import RULES


def test_a_profile_without_hints_has_none():
    assert parsed(layered()).hints == {}


def test_a_hint_loads_by_the_rule_id_in_the_order_of_the_file():
    hints = {"stand-ins": "fakes live in tests/fakes", "may-import": "see docs/project/architecture.md"}
    assert parsed(layered(hints=hints)).hints == hints


@pytest.mark.parametrize("rule", sorted(RULES))
def test_every_rule_id_may_carry_a_hint(rule):
    assert parsed(layered(hints={rule: "x"})).hints == {rule: "x"}


KNOWN = ("built-by, closed-tree, counterpart, cycles, dead-code, holds, immutable, libraries, may-import, must-import, names, "
         "never-use, no-callbacks, no-comments, no-duplicates, no-twins, package-only, pass-through, private-imports, "
         "scenario-coverage, shared, stand-ins, structure, syntax, test-tree, tiers, types-only")


@pytest.mark.parametrize("hints, problem", [
    pytest.param([], "hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}",
                 id="a list instead of a mapping"),
    pytest.param("rules", "hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}",
                 id="a string instead of a mapping"),
    pytest.param({"rulez": "x"}, f"hints.rulez: unknown rule id 'rulez': use {KNOWN}", id="an unknown rule id"),
    pytest.param({3: "x"}, f"hints.3: unknown rule id 3: use {KNOWN}", id="a rule id that is no text"),
    pytest.param({"may-import": ""}, "hints.may-import: must be one line of text", id="an empty hint"),
    pytest.param({"may-import": "two\nlines"}, "hints.may-import: must be one line of text", id="a hint of two lines"),
    pytest.param({"may-import": None}, "hints.may-import: must be one line of text", id="a hint that is no text"),
])
def test_a_bad_hints_entry_is_rejected(hints, problem):
    assert problems(layered(hints=hints)) == [f"layered.yaml: {problem}"]


def test_every_bad_hint_is_reported_at_once():
    assert problems(layered(hints={"nope": "x", "may-import": "", "cycles": "fine"})) == [
        f"layered.yaml: hints.nope: unknown rule id 'nope': use {KNOWN}",
        "layered.yaml: hints.may-import: must be one line of text"]


def test_a_hint_for_the_rule_id_rules_is_told_it_is_renamed_may_import():
    assert problems(layered(hints={"rules": "see the docs"})) == [
        f"layered.yaml: hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import; use {KNOWN}"]


def test_the_text_written_under_hints_rules_is_in_no_problem():
    found = problems(layered(hints={"rules": "secret text"}))
    assert (len(found), "secret text" in "\n".join(found)) == (1, False)
