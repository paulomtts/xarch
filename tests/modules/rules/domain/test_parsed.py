"""The rules the values of a parsed file keep about themselves: which statements are real, that a value built by
hand is public, and an import withholds no name, unless it says otherwise, and what a row of a table says."""
from dataclasses import fields

import pytest

from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row, Table
from xarch.modules.rules.domain.parsed import Test as DeclaredTest
from xarch.profile_values.capabilities import FACTS


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3


def test_a_value_built_with_a_name_alone_is_public_and_an_import_withholds_nothing():
    assert (Class(1, "_A").public, Function(1, "_f").public, Constant(1, "_X").public) == (True, True, True)
    assert Import(1, ("m",), ("_x",)).withheld == frozenset()
    assert (Class(1, "A", public=False).public, Import(1, ("m",), ("x",), withheld=frozenset({"x"})).withheld) == (
        False, frozenset({"x"}))


def test_a_row_says_its_line_whether_it_is_written_as_a_row_its_id_and_its_cells():
    assert [f.name for f in fields(Row)] == ["line", "written", "id", "cells"]


def test_a_row_is_no_longer_built_with_param():
    with pytest.raises(TypeError):
        Row(1, param=True, id=None, cells=())


def test_a_table_says_its_line_its_columns_its_rows_its_form_and_the_line_that_runs_them():
    assert [f.name for f in fields(Table)] == ["line", "columns", "rows", "form", "runs"]


def test_a_table_built_without_its_form_and_the_line_that_runs_it_is_refused():
    with pytest.raises(TypeError):
        Table(1, ("a",), None)


PYTHON_WORDS = ("decorat", "param", "keyword", "pytest", "tuple literal", "list literal")


TABLE_FACTS = {
    "function.tables.decorator": "the tables of cases a mark on a test function's definition holds",
    "function.tables.call": "the tables of cases a call that makes or wraps a test function holds",
    "function.tables.loop": "the tables of cases a test function's body runs through in a loop",
}
"""The facts of the tables of cases, one per form a table is written in, and what each is."""


@pytest.mark.parametrize("text", [
    pytest.param(Row.__doc__, id="the docstring of a row"),
    pytest.param(Table.__doc__, id="the docstring of a table"),
    pytest.param(DeclaredTest.__doc__, id="the docstring of a test"),
    *(pytest.param(FACTS[fact], id=f"the text of the fact {fact}") for fact in TABLE_FACTS),
])
def test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python(text):
    assert [word for word in PYTHON_WORDS if word in text.lower()] == []


def test_the_fact_of_tables_is_one_fact_per_form_each_saying_where_the_table_is_held():
    assert "function.tables" not in FACTS
    assert {fact: FACTS.get(fact) for fact in TABLE_FACTS} == TABLE_FACTS


def test_a_test_is_its_line_its_name_the_index_of_its_form_whether_it_is_titled_and_its_body():
    body = Function(3, "test_a")
    test = DeclaredTest(3, "test_a", 0, False, body)
    assert (test.line, test.name, test.form, test.titled, test.body) == (3, "test_a", 0, False, body)
