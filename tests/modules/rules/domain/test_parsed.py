"""The rules the values of a parsed file keep about themselves: which statements are real, that a value built by
hand is public, and an import withholds no name, unless it says otherwise, and what a row of a table says."""
from dataclasses import fields

import pytest

from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row, Table
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


@pytest.mark.parametrize("text", [
    pytest.param(Row.__doc__, id="the docstring of a row"),
    pytest.param(Table.__doc__, id="the docstring of a table"),
    pytest.param(FACTS["function.tables"], id="the text of the fact of tables"),
])
def test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python(text):
    assert [word for word in PYTHON_WORDS if word in text.lower()] == []


def test_the_fact_of_tables_reads_the_tables_of_cases_of_a_test_function():
    assert FACTS["function.tables"] == "the tables of cases of a test function"
