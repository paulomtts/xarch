"""A tier as the checks read it: each part it tests a target in the tested file's own instance when the part lies in a
repeating folder, outside every instance when it does not."""
from tests.modules.spec.profiles import covered, parsed
from xarch.modules.spec.application.logic.checked_tier import checked_tier
from xarch.profile_values.placement import Target
from xarch.profile_values.tiers import CheckedTier


def test_a_part_of_a_repeating_folder_is_tested_in_its_own_instance():
    architecture = parsed(covered())
    assert checked_tier(architecture, architecture.tiers[0]) == CheckedTier(
        "unit", (Target("service", "own"),), proves="a rule", litmus="Does it decide?\nIf yes, it is a unit test.")


def test_a_part_outside_every_repeating_folder_is_tested_outside_the_instances():
    document = covered()
    document["parts"]["shared"] = {"path": "shared", "role": "shared code", "tests": "unit"}
    architecture = parsed(document)
    assert checked_tier(architecture, architecture.tiers[0]).subject == (Target("service", "own"), Target("shared"))


def test_what_its_tests_may_also_import_is_handed_on_as_written():
    document = covered()
    document["tiers"]["unit"]["may_also_import"] = ["service", "shared"]
    architecture = parsed(document)
    assert checked_tier(architecture, architecture.tiers[0]).may_also_import == (Target("service", "own"),
                                                                                 Target("shared"))
