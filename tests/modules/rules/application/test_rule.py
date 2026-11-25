"""Use case: the rules a key of a profile expands to, written as checks a profile could write; a key that expands to
none in that profile comes back unset when the engine expands it and the profile sets it nowhere, else with why."""
import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import ExplainRule, KeyFacts, KeyUnset, NoRuleShown, RuleShown
from xarch.modules.rules.domain.errors import ProfileUnusable

NAMED = profile(holds_names={"services": {"classes": ("*Service",)}, "controller": {"classes": ("*Controller",)}})
TEXT = "names-services: reads class\n"


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"named": NAMED}, ExplainRule("parts.services.holds.classes.names", "named"),
                 RuleShown("parts.services.holds.classes.names", "named", TEXT, 1, ("class", "public")),
                 id="a key of one part is its rule, as a check, with the facts it reads"),
    pytest.param({"named": NAMED}, ExplainRule("parts.path", "named"),
                 NoRuleShown("parts.path", "named", "it expands to no rule of the engine here: the profile does not "
                                                    "set it, or it is checked by a check of its own"),
                 id="a key of no rule of the engine comes back with why"),
    pytest.param({"named": NAMED}, ExplainRule("parts.imports.may.types_only", "named"),
                 KeyUnset("parts.imports.may.types_only", "named",
                          KeyFacts("parts:\n  a: {imports: {may: [{b: types_only}]}}\n", "types_only", "part")),
                 id="a key the engine expands that the profile sets on no part comes back unset, as the format says it"),
    pytest.param({"named": NAMED}, ExplainRule("parts.services.holds", "named"),
                 KeyUnset("parts.services.holds", "named"), id="so does such a key of one part"),
    pytest.param({"named": NAMED}, ExplainRule("parts.holds.classes.immutable", "named"),
                 NoRuleShown("parts.holds.classes.immutable", "named", "python: cannot read the data file"),
                 id="such a key whose format cannot be explained comes back with why"),
])
def test_rule(given, when, then):
    profiles = FakeProfiles(given, keys={"parts.imports.may.types_only": KeyFacts("parts:\n  a: {imports: {may: [{b: types_only}]}}\n",
                                                                  "types_only", "part"),
                                         "parts.holds.classes.immutable": ProfileUnusable(
                                             "python: cannot read the data file")})
    assert controller(FakeSourceTree(None, {}), profiles).explain_rule(when) == then


def test_a_key_written_for_any_part_is_the_rules_of_every_part_that_sets_it_each_under_an_id_of_its_own():
    found = controller(FakeSourceTree(None, {}), FakeProfiles({"named": NAMED})).explain_rule(
        ExplainRule("parts.holds.classes.names", "named"))
    assert found.count == 2 and "names-services: reads class" in found.text and "names-controller: reads class" in found.text
