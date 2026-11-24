"""The scenario-coverage guard on hand-made source files: a use case's union in contract/ is covered by the rows of
the table in its own instance's test file, and a variant credited only by name to a test with no assert is weak."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import BRACE, PROFILE, PYTEST_FORM, PYTHON, STUB, declaring, in_tests, profile, source
from tests.modules.rules.builders import tests_of as found_by_form
from xarch.modules.rules.application.logic.scenarios import plain, violations, weak
from xarch.modules.rules.domain.parsed import Function, Row, Table, Union
from xarch.modules.rules.domain.parsed import Test as DeclaredTest
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.language import Writing
from xarch.profile_values.testing import Framework, Place, RowId, TableForm
from xarch.profile_values.testing import TestForm as DeclaredForm

COLUMNS = ("given", "when", "then")
RESULTS = source("modules/docs/contract/results.py", unions=(Union(4, "PublishResult", ("Published", "Missing")),))


def row(then: str | None, line: int = 10, id: str | None = "an outcome", written: bool = True) -> Row:
    return Row(line, written, id, (None, "PublishDocument", then))


def table(*rows: Row, columns=COLUMNS, line: int = 9) -> Table:
    return Table(line, columns, rows, 0, 0)


TABLE = table(row("Published"), row("Missing", 11))


def publish_tests(*functions: Function, path: str = "modules/docs/application/test_publish.py"):
    return declaring(path, *functions)


def problems(*tests, app=(RESULTS,), checked=PROFILE) -> list[str]:
    return [str(v) for v in violations(list(app), list(tests), checked)]


@pytest.mark.parametrize("use_case, written, file", [
    pytest.param("Publish", "test_{name:snake}.py", "test_publish.py", id="one word"),
    pytest.param("PublishDocument", "test_{name:snake}.py", "test_publish_document.py", id="two words"),
    pytest.param("HTTPCheck", "test_{name:snake}.py", "test_http_check.py", id="a run of capitals is one word"),
    pytest.param("MarkRead2", "test_{name:snake}.py", "test_mark_read2.py", id="a digit stays with its word"),
    pytest.param("HTTPCheck", "{name:kebab}.test.py", "http-check.test.py", id="kebab joins the words with a hyphen"),
    pytest.param("HTTPCheck", "{name:camel}.test.py", "httpCheck.test.py", id="camel capitalises each word but the first"),
    pytest.param("HTTPCheck", "{name:pascal}.test.py", "HttpCheck.test.py", id="pascal capitalises every word"),
])
def test_the_test_file_of_a_use_case_is_its_name_in_its_case(use_case, written, file):
    results = source("modules/docs/contract/results.py", unions=(Union(4, f"{use_case}Result", ("Done", "Failed")),))
    checked = profile(scenarios=replace(PROFILE.scenarios, file=written))
    assert problems(app=(results,), checked=checked) == [f"app/modules/docs/contract/results.py:4: {use_case}Result has "
                                                         f"no test file {file} among the integration tests of docs "
                                                         "(scenario-coverage)"]


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
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None, 0, 0),))],
                 [f"{FILE}:9: the rows of the table cannot be read (scenario-coverage)"],
                 id="rows that cannot be read are reported, and no variant is then missing"),
    pytest.param([Function(8, "test_publish", (table(row("Published", written=False, id=None), row("Missing", 11)),))],
                 [f"{FILE}:10: row is not a pytest.param(...) (scenario-coverage)"],
                 id="a bare tuple is reported, and still covers the variant it names"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id=None), row("Missing", 11)),))],
                 [f"{FILE}:10: row has no id (scenario-coverage)"],
                 id="a row without an id is reported"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id="  "), row("Missing", 11)),))],
                 [f"{FILE}:10: row has no id (scenario-coverage)"],
                 id="a row whose id is blanks alone is reported as having none"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id=""), row("Missing", 11)),))],
                 [f"{FILE}:10: row has no id (scenario-coverage)"],
                 id="a row whose id is empty is reported as having none"),
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
    pytest.param([Function(8, "test_publish", (TABLE,), blocks=((14, "if"), (15, "for")))],
                 [f"{FILE}:14: test_publish has an `if` in its body (scenario-coverage)",
                  f"{FILE}:15: test_publish has a `for` in its body (scenario-coverage)"],
                 id="a branch in the body of a table test is reported where it is"),
    pytest.param([Function(8, "test_publish", (TABLE,), blocks=((15, "for"),), expressions=((14, "if"), (16, "if")))],
                 [f"{FILE}:14: test_publish has an `if` expression in its body (scenario-coverage)",
                  f"{FILE}:15: test_publish has a `for` in its body (scenario-coverage)",
                  f"{FILE}:16: test_publish has an `if` expression in its body (scenario-coverage)"],
                 id="an expression that chooses between values is a branch too, reported in line order"),
    pytest.param([Function(8, "test_publish", (TABLE,), expressions=((14, "case"),))], [],
                 id="an expression whose keyword the language does not list is none"),
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
    pytest.param((Union(4, "PublishResult", ("Published",)),), id="an alias of one name is no union"),
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
    checked = profile(scenarios=replace(PROFILE.scenarios, file="{name:snake}_test.py"))
    covered = publish_tests(Function(8, "test_publish", (TABLE,)), path="modules/docs/application/publish_test.py")
    assert problems(covered, checked=checked) == []


def test_a_file_whose_functions_match_the_pattern_but_that_holds_no_test_has_no_table_test():
    unread = in_tests("modules/docs/application/test_publish.py", functions=(Function(8, "test_publish", (TABLE,)),))
    assert problems(unread) == [f"{FILE}:1: no table test whose parameters are given, when, then (scenario-coverage)"]


def test_the_test_only_framework_declares_a_function_form_and_a_call_form_and_binds_expect():
    assert ([form.function for form in STUB.declared], STUB.declared[1].call[:2], STUB.globals) == (
        ["test*", ""], (("vitest", "it"), ("vitest", "test")), (("expect",),))


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
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None, 0, 0),))],
                 ["write them as a list, or as the name of a list assigned at the top of the file"],
                 id="rows that cannot be read"),
    pytest.param([Function(8, "test_publish", (table(row("Published", written=False, id=None), row("Missing", 11)),))],
                 [PUBLISH_FIX], id="a bare tuple"),
    pytest.param([Function(8, "test_publish", (table(row("Published", id=None), row("Missing", 11)),))],
                 [PUBLISH_FIX], id="a row without an id"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row(None, 12)),))],
                 ["use one of Published, Missing"], id="a row whose result has no name"),
    pytest.param([Function(8, "test_publish", (table(row("Published"), row("Missing", 11), row("Gone", 12)),))],
                 ["use one of Published, Missing"], id="a row whose result is not a variant"),
    pytest.param([Function(8, "test_publish", (table(row("Published")),))],
                 ["add a row whose then is Missing, or a standalone test naming it"], id="a variant with no row"),
    pytest.param([Function(8, "test_publish", (TABLE,), blocks=((14, "if"), (15, "for")))],
                 [ARRANGE_FIX, ARRANGE_FIX], id="a branch in a table test"),
])
def test_a_violation_of_a_test_file_says_what_to_do(functions, fixes):
    assert [v.fix for v in violations([RESULTS], [publish_tests(*functions)], PROFILE)] == fixes


def test_a_union_with_no_test_file_says_where_to_write_it():
    assert [v.fix for v in violations([RESULTS], [], PROFILE)] == [
        "write test_publish.py among the integration tests of docs"]


UNIT_TEST = "modules/docs/domain/test_doc.py"
PLAIN = replace(PROFILE, tiers=tuple(replace(t, plain_tables=t.name in ("unit", "integration")) for t in PROFILE.tiers))
BRANCHED = Function(8, "test_doc", (table(row("x"), columns=("a", "b")),), blocks=((12, "for"),),
                    expressions=((11, "if"),))


def test_a_table_test_of_a_tier_whose_tables_are_plain_holds_no_branch_and_one_of_another_tier_may():
    tests = [declaring(UNIT_TEST, BRANCHED, Function(20, "test_other", blocks=((21, "if"),))),
             declaring("modules/web/test_page.py", BRANCHED)]
    assert [str(v) for v in plain(tests, PLAIN)] == [
        "tests/modules/docs/domain/test_doc.py:11: test_doc has an `if` expression in its body, and a table test of "
        "the unit tier holds no branch (tiers.unit.plain_tables; scenario-coverage)",
        "tests/modules/docs/domain/test_doc.py:12: test_doc has a `for` in its body, and a table test of the unit tier "
        "holds no branch (tiers.unit.plain_tables; scenario-coverage)"]
    assert plain(tests, PROFILE) == []


def test_a_branch_of_a_use_case_s_table_already_said_is_not_said_again():
    tests = [publish_tests(Function(8, "test_publish", (TABLE,), blocks=((14, "if"),)))]
    said = violations([RESULTS], tests, PLAIN)
    assert [str(v) for v in said] == [f"{FILE}:14: test_publish has an `if` in its body (scenario-coverage)"]
    assert plain(tests, PLAIN, said) == []


NAMED = TableForm(Place(0), Place(1), ("x", "case"), RowId(keyword="name"), decorator=("x", "cases"))
"""A form ahead of pytest's in the framework's list: its row x.case, its id the keyword name."""
LITERAL = TableForm("fields", Place(0), (), RowId(field="name"), decorator=("x", "cases"))
"""A form of literal rows whose id is the field name."""
FIRST = TableForm(Place(0), Place(1), ("x", "case"), RowId(position=0), decorator=("x", "cases"))
"""A form of x.case rows whose id is their first value."""
BRACKETS = Writing(call="{callee}(...)", keyword="{callee}[{keyword}: {text}]", field='{..., {field}: "{text}"}')
"""A language's templates other than Python's, the field one holding braces of its own."""


@pytest.mark.parametrize("form, writing, problem, fix", [
    pytest.param(PYTEST_FORM, PYTHON.writing, "row is not a pytest.param(...)",
                 'write pytest.param(..., id="<a sentence stating the outcome>")',
                 id="pytest's form in Python's words reads as before"),
    pytest.param(PYTEST_FORM, BRACKETS, "row is not a pytest.param(...)",
                 "write pytest.param[id: <a sentence stating the outcome>]", id="the keyword template of the language"),
    pytest.param(LITERAL, BRACKETS, "row is not a literal", 'write {..., name: "<a sentence stating the outcome>"}',
                 id="a literal row whose id is a field"),
    pytest.param(FIRST, PYTHON.writing, "row is not a x.case(...)",
                 "write the row's id, a sentence stating the outcome, as its value at position 0",
                 id="an id by position needs no template"),
])
def test_a_row_is_worded_as_the_form_at_its_index_writes_one_in_the_words_of_the_language(form, writing, problem, fix):
    checked = profile(framework=replace(PROFILE.framework, tables=(NAMED, form)),
                      language=replace(PYTHON, writing=writing))
    bare = replace(table(row("Published", written=False, id=None), row("Missing", 11)), form=1)
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", (bare,)))], checked)
    assert [(str(v), v.fix) for v in found] == [(f"{FILE}:10: {problem} (scenario-coverage)", fix)]


RUN = replace(TABLE, runs=15)
"""TABLE, its rows run by the statement on line 15 of its test's body."""


@pytest.mark.parametrize("tables, blocks, expected", [
    pytest.param((RUN,), ((14, "if"), (15, "for"), (16, "for")), [14, 16],
                 id="the loop that runs the rows is no branch, and every other block still is"),
    pytest.param((TABLE,), ((14, "if"), (15, "for"), (16, "for")), [14, 15, 16],
                 id="a table no statement runs drops nothing"),
    pytest.param((RUN,), ((15, "while"),), [15], id="only a loop at the line that runs the rows is dropped"),
])
def test_the_statement_that_runs_a_table_s_rows_is_no_branch_of_its_test(tables, blocks, expected):
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", tables, blocks=blocks))], PROFILE)
    assert [v.line for v in found] == expected


def test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_statement_that_runs_its_rows():
    ran = replace(BRANCHED, tables=(replace(BRANCHED.tables[0], runs=12),))
    assert [str(v) for v in plain([declaring(UNIT_TEST, ran)], PLAIN)] == [
        "tests/modules/docs/domain/test_doc.py:11: test_doc has an `if` expression in its body, and a table test of "
        "the unit tier holds no branch (tiers.unit.plain_tables; scenario-coverage)"]


LOOP = TableForm("bound", None, (), RowId(position=0), loop=True)
"""A form whose rows a loop of the test's body runs, each a literal whose id is its first value."""


def test_a_table_a_loop_runs_is_checked_as_any_table_by_its_form_s_slots():
    checked = profile(framework=replace(PROFILE.framework, tables=(PYTEST_FORM, LOOP)))
    looped = Table(9, COLUMNS, (row("Published", written=False, id=None),), form=1, runs=9)
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", (looped,), blocks=((9, "for"),)))], checked)
    assert [(str(v), v.fix) for v in found] == [
        (f"{FILE}:10: row is not a literal (scenario-coverage)",
         "write the row's id, a sentence stating the outcome, as its value at position 0"),
        (f"{FILE}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
         "(scenario-coverage)", "add a row whose then is Missing, or a standalone test naming it")]


NO_FORM = profile(framework=Framework(("test_*.py",), (DeclaredForm(function="test_*"),)),
                  scenarios=replace(PROFILE.scenarios, columns=()))
PUBLISHED = Function(8, "test_published", mentions=frozenset({"Published"}), asserts=True)
MISSING = Function(12, "test_missing", mentions=frozenset({"Missing"}), asserts=True)


def unnamed(variant: str, file: str = FILE) -> tuple[str, str]:
    return (f"{file}:1: PublishResult variant {variant} is named by no test (scenario-coverage)",
            f"write a test naming {variant}")


def no_form(*tests) -> list[tuple[str, str]]:
    return [(str(v), v.fix) for v in violations([RESULTS], list(tests), NO_FORM)]


@pytest.mark.parametrize("functions, expected", [
    pytest.param([PUBLISHED, MISSING], [], id="every variant named by a test of the file is covered"),
    pytest.param([Function(8, "test_both", mentions=frozenset({"Published", "Missing"}), asserts=True)], [],
                 id="one test may name every variant"),
    pytest.param([PUBLISHED], [unnamed("Missing")], id="a variant named by no test is reported at the top of the file"),
    pytest.param([], [unnamed("Published"), unnamed("Missing")],
                 id="each variant named by no test is reported, in the union's order"),
    pytest.param([PUBLISHED, replace(MISSING, name="check_missing")], [unnamed("Missing")],
                 id="a function the test pattern does not match names nothing"),
    pytest.param([PUBLISHED, replace(MISSING, owner="PublishTests")], [],
                 id="a method of a class is a test like a function"),
    pytest.param([Function(8, "test_publish", (table(row("Gone", written=False, id=None)),),
                           mentions=frozenset({"Published", "Missing"}), blocks=((14, "if"), (15, "for")),
                           expressions=((16, "if"),))], [],
                 id="a test holding a table is held to naming alone: no row, id or branch is checked"),
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None, 0, 0),), mentions=frozenset({"Published"}))],
                 [unnamed("Missing")], id="a table whose rows cannot be read is not reported, only the naming"),
    pytest.param([Function(8, "test_publish", (TABLE,), mentions=frozenset({"Published"}))], [unnamed("Missing")],
                 id="the rows of a table name no variant: only a test's body does"),
])
def test_scenario_coverage_under_a_framework_with_no_table_form(functions, expected):
    assert no_form(publish_tests(*functions)) == expected


def test_a_use_case_with_no_test_file_is_reported_with_no_form_as_with_one():
    assert no_form() == [("app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py "
                          "among the integration tests of docs (scenario-coverage)",
                          "write test_publish.py among the integration tests of docs")]


def test_each_test_file_of_a_use_case_names_every_variant_on_its_own():
    nested = "modules/docs/application/services/test_publish.py"
    assert no_form(publish_tests(PUBLISHED, MISSING), publish_tests(PUBLISHED, path=nested)) == [
        unnamed("Missing", "tests/modules/docs/application/services/test_publish.py")]


@pytest.mark.parametrize("functions, expected", [
    pytest.param([PUBLISHED, replace(MISSING, asserts=False)],
                 [Weak("scenario-coverage", FILE, 12, "PublishResult variant Missing is credited to test_missing by "
                                                      "name only: no assert in their bodies")],
                 id="a variant named only by a test with no assert is weak"),
    pytest.param([PUBLISHED, replace(MISSING, asserts=False),
                  Function(20, "test_missing_again", mentions=frozenset({"Missing"}), asserts=True)], [],
                 id="one test that asserts is enough"),
    pytest.param([PUBLISHED], [], id="a variant named by no test is a violation, not weak"),
    pytest.param([Function(8, "test_publish", (TABLE,), mentions=frozenset({"Published", "Missing"}))],
                 [Weak("scenario-coverage", FILE, 8, "PublishResult variant Published is credited to test_publish by "
                                                     "name only: no assert in their bodies"),
                  Weak("scenario-coverage", FILE, 8, "PublishResult variant Missing is credited to test_publish by "
                                                     "name only: no assert in their bodies")],
                 id="a test holding a table is a test like any other, its rows covering nothing"),
])
def test_weak_under_a_framework_with_no_table_form(functions, expected):
    assert weak([RESULTS], [publish_tests(*functions)], NO_FORM) == expected


STUB_PROFILE = profile(language=BRACE, framework=STUB, scenarios=replace(PROFILE.scenarios, file="{name:kebab}.test.ts"))
"""The profile of a test-only framework that writes a loop form (index 0) and a call form (index 1), under a language
that is not Python: nothing here is worded by pytest or Python."""
TS = "tests/modules/docs/application/publish.test.ts"
BRACE_PLAIN = replace(STUB_PROFILE, tiers=tuple(replace(t, plain_tables=t.name in ("unit", "integration"))
                                                for t in STUB_PROFILE.tiers))
CALL_FIX = 'write {..., name: "<a sentence stating the outcome>"}'
LOOP_FIX = "write the row's id, a sentence stating the outcome, as its value at position 0"
VARIANT_FIX = "add a row whose then is Missing, or a standalone test naming it"


def written(*rows: Row, form: int = 1, line: int = 9, runs: int = 0) -> Table:
    return Table(line, COLUMNS, rows, form, runs)


def brace_tests(*functions: Function, path: str = "modules/docs/application/publish.test.ts", tests=None):
    return declaring(path, *functions, framework=STUB, language=BRACE, tests=tests)


def stubbed(*tests, checked=STUB_PROFILE) -> list[tuple[str, str]]:
    return [(str(v), v.fix) for v in violations([RESULTS], list(tests), checked)]


def missing_row(file: str = TS) -> tuple[str, str]:
    return (f"{file}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
            "(scenario-coverage)", VARIANT_FIX)


BOTH = (row("Published"), row("Missing", 11))


@pytest.mark.parametrize("function, expected", [
    pytest.param(Function(8, "testPublish", (written(*BOTH),)), [], id="a row per variant, written, each with an id"),
    pytest.param(Function(8, "testPublish", (written(row("Published", written=False, id=None), row("Missing", 11)),)),
                 [(f"{TS}:10: row is not a literal (scenario-coverage)", CALL_FIX)],
                 id="a row not written is worded by the language's field template"),
    pytest.param(Function(8, "testPublish", (written(row("Published", id=None), row("Missing", 11)),)),
                 [(f"{TS}:10: row has no id (scenario-coverage)", CALL_FIX)], id="a row with no id"),
    pytest.param(Function(8, "testPublish", (written(row("Published", id="  "), row("Missing", 11)),)),
                 [(f"{TS}:10: row has no id (scenario-coverage)", CALL_FIX)], id="an id of blanks alone is no id"),
    pytest.param(Function(8, "testPublish", (written(row("Published")),)), [missing_row()],
                 id="a variant with no row"),
    pytest.param(Function(8, "testPublish", (written(*BOTH, row("Gone", 12)),)),
                 [(f"{TS}:12: row 'an outcome' has Gone in its then column, which is not a variant of PublishResult "
                   "(scenario-coverage)",
                   "use one of Published, Missing")], id="a row whose result is not a variant"),
    pytest.param(Function(8, "testPublish", (Table(9, COLUMNS, None, 1, 0),)),
                 [(f"{TS}:9: the rows of the table cannot be read (scenario-coverage)",
                   "write them as a list, or as the name of a list assigned at the top of the file")],
                 id="rows that cannot be read"),
    pytest.param(Function(8, "testPublish", (written(*BOTH),), blocks=((14, "if"),)),
                 [(f"{TS}:14: testPublish has an `if` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="an if is a branch"),
    pytest.param(Function(8, "testPublish", (written(*BOTH),), blocks=((14, "switch"),)),
                 [(f"{TS}:14: testPublish has a `switch` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="a switch is a branch, Brace listing it"),
    pytest.param(Function(8, "testPublish", (written(*BOTH),), blocks=((14, "match"),)), [],
                 id="a match is no branch, Brace not listing it"),
])
def test_scenario_coverage_under_the_call_form_in_the_words_of_the_language(function, expected):
    assert stubbed(brace_tests(function)) == expected


@pytest.mark.parametrize("table_, blocks, expected", [
    pytest.param(written(*BOTH, form=0, runs=9), ((9, "for"), (12, "if")),
                 [(f"{TS}:12: testPublish has an `if` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="the loop that runs the rows is no branch, another block is"),
    pytest.param(written(row("Published", written=False, id=None), row("Missing", 11), form=0, runs=9), ((9, "for"),),
                 [(f"{TS}:10: row is not a literal (scenario-coverage)", LOOP_FIX)],
                 id="a row of a loop is worded by its form, its id a position"),
])
def test_scenario_coverage_under_the_loop_form(table_, blocks, expected):
    assert stubbed(brace_tests(Function(8, "testPublish", (table_,), blocks=blocks))) == expected


def test_a_file_holding_a_call_form_table_and_a_loop_form_table_covers_the_union_of_both():
    published = Function(8, "testPublished", (written(row("Published")),))
    missing = Function(20, "testMissing", (written(row("Missing", 22), form=0, line=21, runs=21),), blocks=((21, "for"),))
    assert stubbed(brace_tests(published, missing)) == []


def test_a_variant_credited_by_name_only_is_weak_under_the_call_form_in_the_framework_s_file():
    functions = (Function(8, "testPublish", (written(row("Published")),)),
                 Function(20, "testMissing", mentions=frozenset({"Missing"})))
    assert weak([RESULTS], [brace_tests(*functions)], STUB_PROFILE) == [
        Weak("scenario-coverage", TS, 20, "PublishResult variant Missing is credited to testMissing by name only: "
                                          "no assert in their bodies")]
    assert violations([RESULTS], [brace_tests(*functions)], STUB_PROFILE) == []


def test_a_variant_a_row_covers_is_not_weak_for_a_standalone_test_that_names_it_without_asserting():
    functions = (Function(8, "testPublish", (written(*BOTH),)), Function(20, "testMissing", mentions=frozenset({"Missing"})))
    assert weak([RESULTS], [brace_tests(*functions)], STUB_PROFILE) == []


def test_a_test_file_of_another_tier_does_not_cover_the_use_case_and_the_file_is_named_as_the_pattern_writes_it():
    elsewhere = brace_tests(Function(8, "testPublish", (written(*BOTH),)), path="modules/docs/domain/publish.test.ts")
    assert stubbed(elsewhere) == [
        ("app/modules/docs/contract/results.py:4: PublishResult has no test file publish.test.ts among the integration "
         "tests of docs (scenario-coverage)", "write publish.test.ts among the integration tests of docs")]


DOC_TS = "tests/modules/docs/domain/doc.test.ts"
UNIT_BRANCHES = ((12, "for"), (14, "if"))


def doc_tests(form: int, runs: int = 0, path: str = "modules/docs/domain/doc.test.ts"):
    held = Table(9, ("a", "b"), (row("x"),), form, runs)
    return brace_tests(Function(8, "testDoc", (held,), blocks=UNIT_BRANCHES), path=path)


def said(*tests, checked=BRACE_PLAIN) -> list[str]:
    return [str(v) for v in plain(list(tests), checked)]


def branch(line: int, word: str) -> str:
    return (f"{DOC_TS}:{line}: testDoc has {word} in its body, and a table test of the unit tier holds no branch "
            "(tiers.unit.plain_tables; scenario-coverage)")


def test_a_table_test_of_a_plain_tier_holds_no_branch_under_the_call_form():
    assert said(doc_tests(1)) == [branch(12, "a `for`"), branch(14, "an `if`")]


def test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_loop_that_runs_the_rows_under_the_loop_form():
    assert said(doc_tests(0, runs=12)) == [branch(14, "an `if`")]


def test_a_table_test_of_a_tier_that_is_not_plain_may_branch_under_the_call_form():
    assert said(doc_tests(1), checked=STUB_PROFILE) == []


def titled(line: int, title: str, body: Function) -> DeclaredTest:
    """A test the call form of the test-only framework declares (index 1), named by its title."""
    return DeclaredTest(line, title, 1, True, body)


def test_a_test_a_call_declares_covers_the_union_by_the_rows_of_its_body_s_table():
    assert stubbed(brace_tests(tests=(titled(8, "places an order", Function(8, "", (written(*BOTH),))),))) == []


def test_a_row_of_a_titled_test_s_table_is_worded_in_the_language_s_words():
    bare = written(row("Published", written=False, id=None), row("Missing", 11))
    assert stubbed(brace_tests(tests=(titled(8, "places an order", Function(8, "", (bare,))),))) == [
        (f"{TS}:10: row is not a literal (scenario-coverage)", CALL_FIX)]


def test_a_branch_of_a_titled_test_is_said_by_its_title_in_double_quotes():
    branched = titled(8, "places an order", Function(8, "", (written(*BOTH),), blocks=((14, "if"),)))
    assert stubbed(brace_tests(tests=(branched,))) == [
        (f'{TS}:14: "places an order" has an `if` in its body (scenario-coverage)', ARRANGE_FIX)]


def test_a_titled_table_test_of_a_plain_tier_is_said_by_its_title_in_double_quotes():
    held = titled(8, "places an order", Function(8, "", (Table(9, ("a", "b"), (row("x"),), 1, 0),), blocks=((14, "if"),)))
    assert said(brace_tests(tests=(held,), path="modules/docs/domain/doc.test.ts")) == [
        f'{DOC_TS}:14: "places an order" has an `if` in its body, and a table test of the unit tier holds no branch '
        "(tiers.unit.plain_tables; scenario-coverage)"]


@pytest.mark.parametrize("name, form, titled_, function, printed", [
    pytest.param("rejects when out of stock", 1, True, "", '"rejects when out of stock"', id="a title in double quotes"),
    pytest.param("testMissing", 0, False, "testMissing", "testMissing", id="a function's name bare"),
    pytest.param("", 1, True, "", '""', id="a title that is no plain literal still counts"),
])
def test_weak_names_a_titled_test_in_double_quotes_and_a_function_bare(name, form, titled_, function, printed):
    table_test = Function(8, "testPublish", (written(row("Published")),))
    standalone = DeclaredTest(20, name, form, titled_, Function(20, function, mentions=frozenset({"Missing"})))
    found = brace_tests(table_test, tests=(*found_by_form((table_test,), STUB), standalone))
    assert weak([RESULTS], [found], STUB_PROFILE) == [
        Weak("scenario-coverage", TS, 20, f"PublishResult variant Missing is credited to {printed} by name only: no "
                                          "assert in their bodies")]


def test_weak_joins_the_names_of_every_test_it_credits_each_named_as_it_is_declared():
    table_test = Function(8, "testPublish", (written(row("Published")),))
    first = titled(20, "rejects when out of stock", Function(20, "", mentions=frozenset({"Missing"})))
    second = DeclaredTest(30, "testMissing", 0, False, Function(30, "testMissing", mentions=frozenset({"Missing"})))
    found = brace_tests(table_test, tests=(*found_by_form((table_test,), STUB), first, second))
    assert weak([RESULTS], [found], STUB_PROFILE) == [
        Weak("scenario-coverage", TS, 20, 'PublishResult variant Missing is credited to "rejects when out of stock", '
                                          "testMissing by name only: no assert in their bodies")]


def test_a_test_a_call_declares_is_among_the_tests_alone_and_still_credits_a_variant():
    table_test = Function(8, "testPublish", (written(row("Published")),))
    missing = titled(20, "rejects when missing", Function(20, "", mentions=frozenset({"Missing"}), asserts=True))
    found = brace_tests(table_test, tests=(*found_by_form((table_test,), STUB), missing))
    assert [function.name for function in found.functions] == ["testPublish"]
    assert (stubbed(found), weak([RESULTS], [found], STUB_PROFILE)) == ([], [])
