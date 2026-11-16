"""The rules the values of a parsed file keep about themselves: which statements are real."""
from xarch.modules.rules.domain.values import Function


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3
