"""The scenario-coverage guard on hand-made source files: a use case's union in contract/ is covered by the rows of
the table in its own instance's test file, and a variant credited only by name to a test with no assert is weak."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import PROFILE, in_tests, profile, source
from xarch.modules.rules.application.logic.scenarios import snake_name, violations, weak
from xarch.modules.rules.domain.values import Function, Row, Table, Union, Weak

COLUMNS = ("given", "when", "then")
RESULTS = source("modules/docs/contract/results.py", unions=(Union(4, "PublishResult", ("Published", "Missing")),))


def row(then: str | None, line: int = 10, id: str | None = "an outcome", param: bool = True) -> Row:
    return Row(line, param, id, (None, "PublishDocument", then))


def table(*rows: Row, columns=COLUMNS, line: int = 9) -> Table:
    return Table(line, columns, rows)


TABLE = table(row("Published"), row("Missing", 11))


def publish_tests(*functions: Function, path: str = "modules/docs/application/test_publish.py"):
    return in_tests(path, functions=functions)


def problems(*tests, app=(RESULTS,), checked=PROFILE) -> list[str]:
    return [str(v) for v in violations(list(app), list(tests), checked)]


def test_snake_name():
    assert [snake_name(n) for n in ["Publish", "PublishDocument", "HTTPCheck", "MarkRead2"]] == [
        "publish", "publish_document", "http_check", "mark_read2"]


FILE = "tests/modules/docs/application/test_publish.py"


@pytest.mark.parametrize("functions, expected", [
    pytest.param([Function(8, "test_publish", (TABLE,))], [], id="a table with a row per variant covers the union"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),)),
                  Function(20, "test_a_missing_document", mentions=frozenset({"Missing"}), asserts=True)], [],
                 id="a variant named by a standalone test is covered"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),))],
                 [f"{FILE}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
                  "(scenario-coverage)"],
                 id="a variant with no row and no standalone test is reported at the table"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),), mentions=frozenset({"Missing"}))],
                 [f"{FILE}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
                  "(scenario-coverage)"],
                 id="a variant named in the body of the table test is no standalone test"),
    pytest.param([Function(8, "check_publish", (TABLE,))],
                 [f"{FILE}:1: no table test whose parameters are given, when, then (scenario-coverage)"],
                 id="a function the test pattern does not match holds no table test"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11),
                                                     columns=("given", "when", "outcome")),))],
                 [f"{FILE}:1: no table test whose parameters are given, when, then (scenario-coverage)"],
                 id="a table without the three columns is not the use case's table"),
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None),))],
                 [f"{FILE}:9: the rows of the table cannot be read (scenario-coverage)"],
                 id="rows that cannot be read are reported, and no variant is then missing"),
    pytest.param([Function(8, "test_publish", (table(row("Published", param=False, id=None), row("Missing", 11)),))],
                 [f"{FILE}:10: row is not a pytest.param(...) (scenario-coverage)"],
                 id="a bare tuple is reported, and still covers the variant it names"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id=None), row("Missing", 11)),))],
                 [f"{FILE}:10: row has no id (scenario-coverage)"],
                 id="a row without an id is reported"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row("Gone", 12)),))],
                 [f"{FILE}:12: row 'an outcome' has Gone in its then column, which is not a variant of PublishResult "
                  "(scenario-coverage)"],
                 id="a row whose result is not a variant is reported"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row(None, 12)),))],
                 [f"{FILE}:12: row 'an outcome' names no variant in its then column (scenario-coverage)"],
                 id="a row whose result has no name is reported"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11),
                                                     Row(12, False, None, ())),))],
                 [f"{FILE}:12: row is not a pytest.param(...) (scenario-coverage)"],
                 id="a row that is neither a call nor a tuple is reported once, with no result to check"),
    pytest.param([Function(8, "test_publish", (table(Row(10, True, "an outcome", (None, "PublishDocument")),
                                                     row("Missing", 11)),))],
                 [f"{FILE}:10: row 'an outcome' names no variant in its then column (scenario-coverage)",
                  f"{FILE}:9: PublishResult variant Published has no row in the table and no standalone test naming "
                  "it (scenario-coverage)"],
                 id="a row with too few values names no variant"),
    pytest.param([Function(8, "test_publish", (TABLE,), branches=((14, "if"), (15, "for")))],
                 [f"{FILE}:14: test_publish has an `if` in its body (scenario-coverage)",
                  f"{FILE}:15: test_publish has a `for` in its body (scenario-coverage)"],
                 id="a branch in the body of a table test is reported where it is"),
])
def test_scenario_coverage(functions, expected):
    assert problems(publish_tests(*functions)) == expected


@pytest.mark.parametrize("tests, expected", [
    pytest.param([], ["app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among "
                      "the integration tests of docs (scenario-coverage)"],
                 id="a union with no test file is reported at the union"),
    pytest.param([publish_tests(Function(8, "test_publish", (TABLE,)), path="modules/other/application/test_publish.py")],
                 ["app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among "
                  "the integration tests of docs (scenario-coverage)"],
                 id="a test file of the same name in another instance does not cover the union"),
    pytest.param([publish_tests(Function(8, "test_publish", (TABLE,)), path="modules/docs/domain/test_publish.py")],
                 ["app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among "
                  "the integration tests of docs (scenario-coverage)"],
                 id="a test file of the same name in another tier does not cover the union"),
    pytest.param([publish_tests(Function(8, "test_publish", (TABLE,)),
                            path="modules/docs/application/services/test_publish.py")], [],
                 id="a test file anywhere among the integration tests of the instance covers the union"),
])
def test_the_test_file_of_a_use_case_is_its_own_instances(tests, expected):
    assert problems(*tests) == expected


@pytest.mark.parametrize("unions", [
    pytest.param((Union(4, "Result", ("Published", "Missing")),), id="a union named exactly the suffix"),
    pytest.param((Union(4, "PublishOutcome", ("Published", "Missing")),), id="a union not named with the suffix"),
])
def test_a_union_that_names_no_use_case_is_not_checked(unions):
    assert problems(app=(source("modules/docs/contract/results.py", unions=unions),)) == []


@pytest.mark.parametrize("path", [
    pytest.param("modules/docs/domain/results.py", id="a union outside the results part"),
    pytest.param("kernel/results.py", id="a union in no instance"),
    pytest.param("scripts/results.py", id="a union in an ungoverned file"),
])
def test_a_union_outside_an_instances_results_part_is_not_checked(path):
    assert problems(app=(source(path, unions=RESULTS.unions),)) == []


def test_without_the_guard_or_a_test_framework_nothing_is_checked():
    assert (problems(checked=profile(scenarios=None)), problems(checked=profile(framework=None))) == ([], [])


def test_the_test_file_follows_the_guards_file_pattern():
    checked = profile(scenarios=replace(PROFILE.scenarios, file="{name}_test.py"))
    covered = publish_tests(Function(8, "test_publish", (TABLE,)), path="modules/docs/application/publish_test.py")
    assert problems(covered, checked=checked) == []


@pytest.mark.parametrize("functions, expected", [
    pytest.param([Function(8, "test_publish", (table(row("Published")),)),
                  Function(20, "test_missing", mentions=frozenset({"Missing"}))],
                 [Weak("scenario-coverage", FILE, 20, "PublishResult variant Missing is credited to test_missing by "
                                                      "name only: no assert in their bodies")],
                 id="a variant credited only to a standalone test with no assert is weak"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),)),
                  Function(20, "test_missing", mentions=frozenset({"Missing"})),
                  Function(30, "test_missing_again", mentions=frozenset({"Missing"}), asserts=True)], [],
                 id="one standalone test with an assert is enough"),
    pytest.param([Function(8, "test_publish", (TABLE,)), Function(20, "test_missing", mentions=frozenset({"Missing"}))],
                 [], id="a variant a row covers is not weak"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),))], [],
                 id="a variant credited to nothing is a violation, not weak"),
])
def test_weak(functions, expected):
    assert weak([RESULTS], [publish_tests(*functions)], PROFILE) == expected


def test_a_weak_credit_counts_only_the_use_cases_own_instance():
    other = publish_tests(Function(8, "test_publish", (table(row("Published")),)),
                      Function(20, "test_missing", mentions=frozenset({"Missing"})),
                      path="modules/other/application/test_publish.py")
    assert weak([RESULTS], [other], PROFILE) == []


PUBLISH_FIX = 'write pytest.param(..., id="<a sentence stating the outcome>")'
ARRANGE_FIX = "arrange from given, act with when, assert == then, and give the odd case its own test"


@pytest.mark.parametrize("functions, fixes", [
    pytest.param([Function(8, "check_publish", (TABLE,))], ["add a table test whose parameters are given, when, then"],
                 id="no table test"),
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None),))],
                 ["write them as a list, or as the name of a list assigned at the top of the file"],
                 id="rows that cannot be read"),
    pytest.param([Function(8, "test_publish", (table(row("Published", param=False, id=None), row("Missing", 11)),))],
                 [PUBLISH_FIX], id="a bare tuple"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id=None), row("Missing", 11)),))],
                 [PUBLISH_FIX], id="a row without an id"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row(None, 12)),))],
                 ["use one of Published, Missing"], id="a row whose result has no name"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row("Gone", 12)),))],
                 ["use one of Published, Missing"], id="a row whose result is not a variant"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),))],
                 ["add a row whose then is Missing, or a standalone test naming it"], id="a variant with no row"),
    pytest.param([Function(8, "test_publish", (TABLE,), branches=((14, "if"), (15, "for")))],
                 [ARRANGE_FIX, ARRANGE_FIX], id="a branch in a table test"),
])
def test_a_violation_of_a_test_file_says_what_to_do(functions, fixes):
    assert [v.fix for v in violations([RESULTS], [publish_tests(*functions)], PROFILE)] == fixes


def test_a_union_with_no_test_file_says_where_to_write_it():
    assert [v.fix for v in violations([RESULTS], [], PROFILE)] == [
        "write test_publish.py among the integration tests of docs"]
