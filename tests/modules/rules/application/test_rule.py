"""Use case: the rules a key of a profile expands to, written as checks a profile could write; a key that expands to
none in that profile comes back unset when the engine expands it and the profile sets it nowhere, else with why."""
import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import ExplainRule, KeyUnset, NoRuleShown, RuleShown

NAMED = profile(names={"services": ("*Service",), "controller": ("*Controller",)})
TEXT = """checks:
  names-services:
    read: class
    in: {part: services}
    keep: [public]
    may_only: {name: ["*Service"]}
    message: "{name} does not match {targets}, as every class of {where} must ({key})"
    fix: "rename {name} to match {targets}, or move it to the part whose kind of class it is"
"""


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"named": NAMED}, ExplainRule("parts.services.names", "named"),
                 RuleShown("parts.services.names", "named", TEXT, 1), id="a key of one part is its rule, as a check"),
    pytest.param({"named": NAMED}, ExplainRule("parts.path", "named"),
                 NoRuleShown("parts.path", "named", "it expands to no rule of the engine here: the profile does not "
                                                    "set it, or it is checked by a check of its own"),
                 id="a key of no rule of the engine comes back with why"),
    pytest.param({"named": NAMED}, ExplainRule("parts.types_only", "named"), KeyUnset("parts.types_only", "named"),
                 id="a key the engine expands that the profile sets on no part comes back unset"),
    pytest.param({"named": NAMED}, ExplainRule("parts.services.holds", "named"),
                 KeyUnset("parts.services.holds", "named"), id="so does such a key of one part"),
])
def test_rule(given, when, then):
    assert controller(FakeSourceTree(None, {}), FakeProfiles(given)).explain_rule(when) == then


def test_a_key_written_for_any_part_is_the_rules_of_every_part_that_sets_it_each_under_an_id_of_its_own():
    found = controller(FakeSourceTree(None, {}), FakeProfiles({"named": NAMED})).explain_rule(
        ExplainRule("parts.names", "named"))
    assert found.count == 2 and "  names-services:" in found.text and "  names-controller:" in found.text
