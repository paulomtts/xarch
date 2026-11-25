"""How a profile writes what may be imported, on hand-made parts: the references parts.<part> and <word>.<part>, a path
below the part, a pattern where one is allowed, `everything`, and each target refused with why, an old form (a bare
part, @any, @own) with the reference to write."""
import pytest

from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.targets_written import allowed_targets
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target

API = Part("api", ("src", "*", "api"), "handlers")
SERVICE = Part("service", ("src", "*", "service"), "logic")
SHARED = Part("shared", ("shared",), "shared code")
PARTS = {part.name: part for part in (API, SERVICE, SHARED)}
REPEATS = (Repeat("module", ("src",)),)
NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                   ":<pattern>")


def written(value, owner=API, patterns=False):
    problems: list[str] = []
    return (allowed_targets(value, owner, PARTS, set(PARTS), "parts.api.imports.may", problems, patterns,
                            repeats=REPEATS), problems)


@pytest.mark.parametrize("value, targets", [
    pytest.param(["module.service"], (Target("service", "own"),),
                 id="a part of its own repeating folder by its word is its own instance"),
    pytest.param(["parts.service"], (Target("service", "any"),), id="any instance"),
    pytest.param(["parts.shared/text"], (Target("shared", "none", ("text",)),), id="a path below a part"),
    pytest.param("everything", (Target(EVERYTHING),), id="everything, written alone"),
    pytest.param(None, (), id="nothing written is nothing more"),
])
def test_a_target_is_read_as_written(value, targets):
    assert written(value) == (targets, [])


def test_a_name_pattern_is_read_only_where_it_is_allowed():
    assert written(["parts.shared:*Id"], patterns=True) == ((Target("shared", "none", (), "*Id"),), [])
    assert written(["parts.shared:*Id"])[1] == ["parts.api.imports.may: 'parts.shared:*Id' has a name pattern, which this key does "
                                          "not take: drop ':*Id'"]


@pytest.mark.parametrize("value, problem", [
    pytest.param(["nope"], "'nope' names no part 'nope'", id="a part not declared"),
    pytest.param(["shared@any"], "'shared@any': @any was removed in 0.3.0: write parts.shared",
                 id="a scope on a part outside the repeating folder"),
    pytest.param(["module.api"], "'module.api' is implied: a part may always import itself, its own instance of the "
                                 "repeating folder; remove it (parts.api, another instance's too, stays allowed)",
                 id="itself"),
    pytest.param(["everything"], "'everything' stands alone: write `everything` in place of the list",
                 id="everything in a list"),
])
def test_a_target_that_cannot_be_read_is_refused_saying_why(value, problem):
    assert written(value) == ((), [f"parts.api.imports.may: {problem}"])


def test_a_tier_folder_s_may_import_refuses_a_marked_entry_as_any_entry_that_is_no_target():
    problems: list[str] = []
    assert allowed_targets([{"parts.shared": "types_only"}], None, PARTS, {"shared"}, "tiers.guard.imports.may", problems,
                           repeats=REPEATS) == ()
    assert problems == ["tiers.guard.imports.may: {'parts.shared': 'types_only'} " + NOT_A_REFERENCE]


def test_each_old_form_of_a_list_is_its_own_problem_and_the_references_beside_them_are_read():
    assert written(["service", "parts.shared", "service@any", "shared/text"]) == ((Target("shared"),), [
        "parts.api.imports.may: 'service': a bare part name was removed in 0.3.0: write module.service (this "
        "module's) or parts.service (any module's)",
        "parts.api.imports.may: 'service@any': @any was removed in 0.3.0: write parts.service",
        "parts.api.imports.may: 'shared/text': a bare part name was removed in 0.3.0: write parts.shared/text"])


def test_references_are_read_with_the_profile_s_words_in_the_order_written():
    assert written(["parts.shared", "module.service", "parts.service/rules"]) == (
        (Target("shared"), Target("service", "own"), Target("service", "any", ("rules",))), [])


NO_MODULE = "no part the tier tests lies in a <module> folder, so its tests mirror no module"


@pytest.mark.parametrize("tested, targets, problems", [
    pytest.param((SERVICE.path,), (Target("service", "own", ("rules",)),), [], id="a tested part in the word's folder"),
    pytest.param((SHARED.path,), (), [f"tiers.unit.imports.also: 'module.service/rules': {NO_MODULE}: write "
                                      "parts.service/rules"], id="the tested parts outside it"),
])
def test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors(tested, targets, problems):
    said: list[str] = []
    assert allowed_targets(["module.service/rules"], None, PARTS, set(PARTS), "tiers.unit.imports.also", said,
                           mirrored=tested, repeats=REPEATS) == targets
    assert said == problems


def test_several_words_in_one_list_are_each_judged_by_the_same_tested_parts():
    said: list[str] = []
    assert allowed_targets(["module.service", "module.api/routes"], None, PARTS, set(PARTS),
                           "tiers.unit.imports.also", said, mirrored=(SERVICE.path,), repeats=REPEATS) == (
        Target("service", "own"), Target("api", "own", ("routes",)))
    assert said == []
    assert allowed_targets(["module.service", "module.api"], None, PARTS, set(PARTS), "tiers.unit.imports.also",
                           said, mirrored=(SHARED.path,), repeats=REPEATS) == ()
    assert said == [f"tiers.unit.imports.also: 'module.service': {NO_MODULE}: write parts.service",
                    f"tiers.unit.imports.also: 'module.api': {NO_MODULE}: write parts.api"]


@pytest.mark.parametrize("value, targets, problem", [
    pytest.param("everything", (), "tiers.guard.imports.also: must be a list of targets such as [parts.core, "
                                   "unit.store/schema]: `everything` is not taken, name each target the tests may also "
                                   "import", id="everything alone"),
    pytest.param(["parts.shared", "everything"], (Target("shared"),),
                 "tiers.guard.imports.also: `everything` is not taken, name each target the tests may also import",
                 id="everything in the list"),
])
def test_a_tier_that_tests_no_part_still_refuses_everything_in_what_its_tests_also_import(value, targets, problem):
    said: list[str] = []
    assert allowed_targets(value, None, PARTS, set(PARTS), "tiers.guard.imports.also", said, mirrored=(),
                           repeats=REPEATS) == targets
    assert said == [problem]
