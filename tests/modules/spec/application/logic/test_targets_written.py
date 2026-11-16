"""How a profile writes what may be imported, on hand-made parts: a bare part, @any, a path below it, a pattern where
one is allowed, `everything`, and each target refused with why."""
import pytest

from xarch.kernel.placement import EVERYTHING, Target
from xarch.modules.spec.application.logic.targets_written import may_import
from xarch.modules.spec.domain.values import Part

API = Part("api", ("src", "*", "api"), "handlers")
SERVICE = Part("service", ("src", "*", "service"), "logic")
SHARED = Part("shared", ("shared",), "shared code")
PARTS = {part.name: part for part in (API, SERVICE, SHARED)}


def written(value, owner=API, patterns=False):
    problems: list[str] = []
    return may_import(value, owner, PARTS, set(PARTS), "parts.api.may_import", problems, patterns), problems


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
    assert written(["shared:*Id"], patterns=True) == ((Target("shared", "none", (), "*Id"),), [])
    assert written(["shared:*Id"])[1] == ["parts.api.may_import: 'shared:*Id' has a name pattern: only a part's "
                                          "`may_import` narrows what may be imported by name"]


@pytest.mark.parametrize("value, problem", [
    pytest.param(["nope"], "'nope' names no part 'nope'", id="a part not declared"),
    pytest.param(["shared@any"], "'shared@any' does not lie in the repeating folder: drop '@any'",
                 id="a scope on a part outside the repeating folder"),
    pytest.param(["api"], "'api' is implied: a part may always import itself, its own instance of the repeating "
                          "folder; remove it (api@any, another instance's too, stays allowed)", id="itself"),
    pytest.param(["everything"], "'everything' stands alone: write `may_import: everything`, not in a list",
                 id="everything in a list"),
])
def test_a_target_that_cannot_be_read_is_refused_saying_why(value, problem):
    assert written(value) == ((), [f"parts.api.may_import: {problem}"])
