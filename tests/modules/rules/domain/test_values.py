"""The rules the values of a parsed file keep about themselves: which statements are real, which alias is a union, and
which id says something."""
import pytest

from xarch.modules.rules.domain.values import Function, Row, Union


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3


@pytest.mark.parametrize("members, union", [
    pytest.param(("A",), False, id="an alias of one name is no union"),
    pytest.param(("A", "B"), True, id="two names joined are a union"),
])
def test_an_alias_is_a_union_when_it_joins_two_names_or_more(members, union):
    assert Union(1, "R", members).is_union is union


@pytest.mark.parametrize("written, given", [
    pytest.param("a sentence", "a sentence", id="a literal that says something is the id"),
    pytest.param("", None, id="an empty literal is no id"),
    pytest.param("  ", None, id="a literal of blanks is no id"),
    pytest.param(None, None, id="no literal is no id"),
])
def test_a_row_s_id_is_given_when_it_says_something(written, given):
    assert Row(1, True, written, ()).given_id == given
