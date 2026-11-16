"""A filter as it is written, `[not ]<name>[ <value>]`, read into a condition: its name, its value and whether it is
negated."""
import pytest

from xarch.kernel.logic.conditions import condition
from xarch.profile_values.checks import Condition


@pytest.mark.parametrize("text, read", [
    pytest.param("public", Condition("public"), id="a name"),
    pytest.param("not relative", Condition("relative", negated=True), id="a negated name"),
    pytest.param("below units/docs", Condition("below", "units/docs"), id="a name and its value"),
    pytest.param("not below fakes", Condition("below", "fakes", True), id="a negated name and its value"),
])
def test_a_condition_is_written_as_its_name_negated_or_not_and_its_value(text, read):
    assert condition(text) == read
