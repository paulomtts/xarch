"""The checks a profile writes itself, as the format writes them: a check comes back with each slot as the rules module
reads it (lists as tuples, filters as their text, targets as kinds and values, places as targets, scopes with their
defaults), and a check that breaks the format, or names an id, a part, a tier or a place the profile does not have,
is said at its address and left out."""
import pytest

from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles_v2 import layered, parsed
from xarch.modules.spec.application.logic.written_checks import checks
from xarch.profile_values.placement import Target

ARCHITECTURE = parsed(layered())
EXAMPLES = {"flagged": {"src/billing/api/x.py": "print(1)\n"}, "clean": {"src/billing/api/y.py": "pass\n"}}
SMALL = {"read": "call", "may_not": {"path": ["builtins.print"]}, "message": "{where} prints", "fix": "log it",
         "examples": EXAMPLES}


def read(value) -> tuple[dict, list[str]]:
    problems: list[str] = []
    found = checks(value, ARCHITECTURE.parts, set(ARCHITECTURE.parts), ARCHITECTURE.tiers, PYTHON, problems)
    return found, problems


def test_a_check_comes_back_with_each_slot_as_the_rules_read_it_and_the_defaults_filled_in():
    found, problems = read({"no-print": SMALL})
    assert problems == []
    assert found == {"no-print": {
        "read": ("call",), "in": {"files": "app", "part": "*", "tier": "", "where": ()}, "keep": (), "except": (),
        "mode": "fail", "message": "{where} prints", "fix": "log it", "once_per": (), "cases": (),
        "examples": {"flagged": (("src/billing/api/x.py", "print(1)\n"),), "clean": (("src/billing/api/y.py", "pass\n"),)},
        "may_not": ({"kind": "path", "values": ("builtins.print",)},)}}


def test_a_reach_to_targets_reads_its_places_from_the_part_its_scope_names():
    body = {**SMALL, "read": ["import", "import-into-app"], "in": {"part": "store", "where": ["not package-file",
                                                                                              {"not below": "x/y"}]},
            "keep": [{"named": "*Repo"}], "must_reach": {"targets": [{"place": ["shared"]}, "outside"],
                                                          "through": "import-into-app", "through_only": ["target-in-own-part"]},
            "cases": [{"when": ["relative"], "message": "m", "fix": "f", "once_per": ["line"]}]}
    del body["may_not"]
    found, problems = read({"reach": body})
    assert problems == []
    check = found["reach"]
    assert (check["in"], check["keep"], check["cases"]) == (
        {"files": "app", "part": "store", "tier": "", "where": ("not package-file", "not below x/y")}, ("named *Repo",),
        ({"when": ("relative",), "message": "m", "fix": "f", "once_per": ("line",)},))
    assert check["must_reach"] == {"through": ("import-into-app",), "through_only": ("target-in-own-part",),
                                   "targets": ({"kind": "place", "values": (Target("shared"),)},
                                               {"kind": "outside", "values": ()})}


def test_a_reach_from_roots_reads_its_roots_as_a_scope():
    body = {**SMALL, "read": "class", "must_be_reached": {"from": {"files": "tests"}, "through": "names-mentioned",
                                                          "then_through": "class", "by_another_file": True}}
    del body["may_not"]
    found, problems = read({"used": body})
    assert problems == [] and found["used"]["must_be_reached"] == {
        "through": ("names-mentioned",), "through_only": (), "from": {"files": "tests", "part": "*", "tier": "", "where": ()},
        "then_through": ("class",), "by_another_file": True}


@pytest.mark.parametrize("value, problems", [
    pytest.param([], ["checks: must be a map from an id of your own to a check, such as {store-names: {read: class, "
                      'may_only: {name: ["*Store"]}, message: ..., fix: ..., examples: ...}}'], id="not a map"),
    pytest.param({"No_Print": SMALL}, ["checks: 'No_Print' is not an id: write lowercase words joined by `-`, such as "
                                       "store-names"], id="an id not written as one"),
    pytest.param({"names": SMALL}, ["checks.names: names is the id of a check xarch has: give your check an id of its "
                                    "own, such as my-names"], id="the id of a check xarch has"),
    pytest.param({"x": "call"}, ["checks.x: must be a map of slots: read, in, keep, may_not, may_only, must_reach, "
                                 "must_be_reached, except, mode, message, fix, once_per, cases, examples"],
                 id="a check that is no map"),
    pytest.param({"x": {**SMALL, "colour": "red"}}, ["checks.x: unknown key `colour`: use read, in, keep, may_not, "
                                                     "may_only, must_reach, must_be_reached, except, mode, message, fix, "
                                                     "once_per, cases, examples"], id="a slot of no check"),
    pytest.param({"x": {"may_not": "exist"}}, ["checks.x: missing `read`", "checks.x: missing `message`",
                                               "checks.x: missing `fix`", "checks.x: missing `examples`"],
                 id="the slots every check needs"),
    pytest.param({"x": {k: v for k, v in SMALL.items() if k != "may_not"}},
                 ["checks.x: names no quantifier: write one of may_not, may_only, must_reach, must_be_reached"],
                 id="no quantifier"),
    pytest.param({"x": {**SMALL, "may_only": "exist"}},
                 ["checks.x: names may_not and may_only: write one of may_not, may_only, must_reach, must_be_reached"],
                 id="two quantifiers"),
    pytest.param({"x": {**SMALL, "in": {"part": "web", "tier": "unit"}}},
                 ["checks.x.in.part: no part named 'web': write one of api, service, shared, store, or structure",
                  "checks.x.in.tier: no tier named 'unit': the profile has no tiers"], id="a part and a tier not declared"),
    pytest.param({"x": {**SMALL, "keep": [{"named": "a", "x": "b"}, 3]}},
                 ["checks.x.keep: {'named': 'a', 'x': 'b'} is not a filter: write a name, `not <name>`, or "
                  "{<name>: <value>}", "checks.x.keep: 3 is not a filter: write a name, `not <name>`, or "
                  "{<name>: <value>}"], id="filters written as no filter"),
    pytest.param({"x": {**SMALL, "may_not": [{"place": ["nowhere"]}, {"path": 3}]}},
                 ["checks.x.may_not.place: 'nowhere' names no part 'nowhere'",
                  "checks.x.may_not: {'path': 3}: write the values of a target as a list of text"],
                 id="a place of no part and values that are no text"),
    pytest.param({"x": {**SMALL, "examples": {"flagged": {"../x.py": "a"}, "clean": {}}}},
                 ["checks.x.examples.flagged: '../x.py' is not a path of a source file below the app (or tests/...), "
                  "ending in .py",
                  "checks.x.examples.clean: must be a map of at least one file, {<path>: <code>}: the code the check "
                  "must find nothing in"], id="examples with no file of each side"),
])
def test_a_check_that_breaks_the_format_is_said_at_its_address_and_left_out(value, problems):
    found, said = read(value)
    assert (found, said) == ({}, problems)
