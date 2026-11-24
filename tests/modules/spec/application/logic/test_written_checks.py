"""The checks a profile writes itself, as the format writes them: a check comes back as the record the rules module
reads (lists as tuples, filters as conditions, targets as kinds and their values as written, scopes with their
defaults), and a check that breaks the format, or names an id, a part or a tier the profile does not have, is said at
its address and left out; what a target's values name is the rules module's to read."""
import pytest

from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import layered, parsed
from xarch.modules.spec.application.logic.written_checks import checks
from xarch.profile_values.checks import (
    ANY,
    APP,
    TESTS,
    Condition,
    Quantified,
    Saying,
    Scope,
    WrittenCheck,
    WrittenTarget,
)

ARCHITECTURE = parsed(layered())
EXAMPLES = {"flagged": {"src/billing/api/x.py": "print(1)\n"}, "clean": {"src/billing/api/y.py": "pass\n"}}
SMALL = {"read": "call", "may_not": {"path": ["builtins.print"]}, "message": "{where} prints", "fix": "log it",
         "examples": EXAMPLES}


def read(value) -> tuple[dict, list[str]]:
    problems: list[str] = []
    found = checks(value, set(ARCHITECTURE.parts), ARCHITECTURE.tiers, PYTHON, problems, words=("module",))
    return found, problems


def test_a_check_comes_back_with_each_slot_as_the_rules_read_it_and_the_defaults_filled_in():
    found, problems = read({"no-print": SMALL})
    assert problems == []
    assert found == {"no-print": WrittenCheck(
        ("call",), Scope(APP, ANY, "", ()), Quantified("may_not", (WrittenTarget("path", ("builtins.print",)),)),
        (Saying("{where} prints", "log it"),), (), (), "fail", (("src/billing/api/x.py", "print(1)\n"),),
        (("src/billing/api/y.py", "pass\n"),))}


def test_a_reach_to_targets_keeps_its_targets_as_written_and_its_filters_as_conditions():
    body = {**SMALL, "read": ["import", "import-into-app"], "in": {"part": "store", "where": ["not package-file",
                                                                                              {"not below": "x/y"}]},
            "keep": [{"named": "*Repo"}], "must_reach": {"targets": [{"place": ["parts.shared"]}, "outside"],
                                                          "through": "import-into-app", "through_only": ["target-in-own-part"]},
            "cases": [{"when": ["relative"], "message": "m", "fix": "f", "once_per": ["line"]}]}
    del body["may_not"]
    found, problems = read({"reach": body})
    assert problems == []
    check = found["reach"]
    assert (check.within, check.keep, check.sayings[0]) == (
        Scope(APP, "store", "", (Condition("package-file", negated=True), Condition("below", "x/y", True))),
        (Condition("named", "*Repo"),), Saying("m", "f", (Condition("relative"),), ("line",)))
    assert check.quantified == Quantified("must_reach", (WrittenTarget("place", ("parts.shared",)), WrittenTarget("outside")),
                                          ("import-into-app",), (Condition("target-in-own-part"),))


def test_a_reach_from_roots_reads_its_roots_as_a_scope():
    body = {**SMALL, "read": "class", "must_be_reached": {"from": {"files": "tests"}, "through": "names-mentioned",
                                                          "then_through": "class", "by_another_file": True}}
    del body["may_not"]
    found, problems = read({"used": body})
    assert problems == [] and found["used"].quantified == Quantified(
        "must_be_reached", (), ("names-mentioned",), (), Scope(TESTS), ("class",), True)


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
    pytest.param({"x": {**SMALL, "in": {"part": "parts.api"}}},
                 ["checks.x.in.part: 'parts.api': names a part outside imports: write api"], id="a part by a reference"),
    pytest.param({"x": {**SMALL, "in": {"part": "orders.api"}}},
                 ["checks.x.in.part: no part named 'orders.api': write one of api, service, shared, store, or structure"],
                 id="a prefix that is no word keeps the reader's text"),
    pytest.param({"x": {**{k: v for k, v in SMALL.items() if k != "may_not"}, "read": "class",
                        "must_be_reached": {"from": {"part": "module.api"}, "through": "names-mentioned"}}},
                 ["checks.x.must_be_reached.from.part: 'module.api': names a part outside imports: write api"],
                 id="a part reached from, by a reference"),
    pytest.param({"x": {**SMALL, "keep": [{"named": "a", "x": "b"}, 3]}},
                 ["checks.x.keep: {'named': 'a', 'x': 'b'} is not a filter: write a name, `not <name>`, or "
                  "{<name>: <value>}", "checks.x.keep: 3 is not a filter: write a name, `not <name>`, or "
                  "{<name>: <value>}"], id="filters written as no filter"),
    pytest.param({"x": {**SMALL, "may_not": [{"path": 3}, 4]}},
                 ["checks.x.may_not: {'path': 3}: write the values of a target as a list of text",
                  "checks.x.may_not: 4 is not a target: write a kind, or {<kind>: [<value>, ...]}"],
                 id="values that are no text, and a target that is no kind"),
    pytest.param({"x": {**SMALL, "examples": {"flagged": {"../x.py": "a"}, "clean": {}}}},
                 ["checks.x.examples.flagged: '../x.py' is not a path of a source file below the app (or tests/...), "
                  "ending in .py",
                  "checks.x.examples.clean: must be a map of at least one file, {<path>: <code>}: the code the check "
                  "must find nothing in"], id="examples with no file of each side"),
])
def test_a_check_that_breaks_the_format_is_said_at_its_address_and_left_out(value, problems):
    found, said = read(value)
    assert (found, said) == ({}, problems)


def test_a_check_of_its_own_may_not_take_the_id_never_use_and_may_take_forbidden_which_xarch_no_longer_has():
    taken, free = read({"never-use": SMALL}), read({"forbidden": SMALL})
    assert taken == ({}, ["checks.never-use: never-use is the id of a check xarch has: give your check an id of its "
                          "own, such as my-never-use"])
    assert (list(free[0]), free[1]) == (["forbidden"], [])


def test_a_hint_for_a_check_of_its_own_named_forbidden_is_the_hint_of_that_check():
    architecture = parsed(layered(checks={"forbidden": SMALL}, hints={"forbidden": "see the docs"}))
    assert (list(architecture.checks), architecture.hints) == (["forbidden"], {"forbidden": "see the docs"})


def test_a_check_of_its_own_may_not_take_the_id_may_import_and_may_take_rules_which_xarch_no_longer_has():
    taken, free = read({"may-import": SMALL}), read({"rules": SMALL})
    assert taken == ({}, ["checks.may-import: may-import is the id of a check xarch has: give your check an id of its "
                          "own, such as my-may-import"])
    assert (list(free[0]), free[1]) == (["rules"], [])


def test_a_hint_for_a_check_of_its_own_named_rules_is_the_hint_of_that_check():
    architecture = parsed(layered(checks={"rules": SMALL}, hints={"rules": "see the docs"}))
    assert (list(architecture.checks), architecture.hints) == (["rules"], {"rules": "see the docs"})


def test_an_example_of_any_ending_of_the_language_is_read_and_a_refusal_prints_the_first():
    problems: list[str] = []
    braced = {"x": {**SMALL, "examples": {"flagged": {"src/billing/api/x.tsx": "a\n"},
                                          "clean": {"src/billing/api/y.js": "b\n"}}}}
    assert checks(braced, set(ARCHITECTURE.parts), ARCHITECTURE.tiers, BRACE, problems, words=("module",)) == {}
    assert problems == ["checks.x.examples.clean: 'src/billing/api/y.js' is not a path of a source file below the app "
                        "(or tests/...), ending in .ts"]
