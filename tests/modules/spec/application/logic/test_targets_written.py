"""How a profile writes what may be imported, on hand-made parts: a bare part, @any, a path below it, a pattern where
one is allowed, `everything`, the references parts.<part> and <word>.<part>, and each target refused with why."""
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


def written(value, owner=API, patterns=False):
    problems: list[str] = []
    return (allowed_targets(value, owner, PARTS, set(PARTS), "parts.api.imports.may", problems, patterns,
                            repeats=REPEATS), problems)


@pytest.mark.parametrize("value, targets", [
    pytest.param(["service"], (Target("service", "own"),), id="a part of its own repeating folder is its own instance"),
    pytest.param(["service@any"], (Target("service", "any"),), id="any instance"),
    pytest.param(["shared/text"], (Target("shared", "none", ("text",)),), id="a path below a part"),
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
    pytest.param(["shared@any"], "'shared@any' does not lie in the repeating folder: drop '@any'",
                 id="a scope on a part outside the repeating folder"),
    pytest.param(["api"], "'api' is implied: a part may always import itself, its own instance of the repeating "
                          "folder; remove it (api@any, another instance's too, stays allowed)", id="itself"),
    pytest.param(["everything"], "'everything' stands alone: write `everything` in place of the list",
                 id="everything in a list"),
])
def test_a_target_that_cannot_be_read_is_refused_saying_why(value, problem):
    assert written(value) == ((), [f"parts.api.imports.may: {problem}"])


def test_a_tier_folder_s_may_import_refuses_a_marked_entry_as_any_entry_that_is_no_target():
    problems: list[str] = []
    assert allowed_targets([{"parts.shared": "types_only"}], None, PARTS, {"shared"}, "tiers.guard.imports.may", problems,
                           repeats=REPEATS) == ()
    assert problems == ["tiers.guard.imports.may: {'parts.shared': 'types_only'} is not a target: use <part>, <part>@any, "
                        "optionally followed by /<path>"]


def test_references_are_read_with_the_profile_s_words_in_the_order_written():
    assert written(["parts.shared", "module.service", "parts.service/rules"]) == (
        (Target("shared"), Target("service", "own"), Target("service", "any", ("rules",))), [])


def test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors():
    problems: list[str] = []
    assert allowed_targets(["module.service/rules"], None, PARTS, set(PARTS), "tiers.unit.imports.also", problems,
                           mirrored=True, repeats=REPEATS) == (Target("service", "own", ("rules",)),)
    assert problems == []
