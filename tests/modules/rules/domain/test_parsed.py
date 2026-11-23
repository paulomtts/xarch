"""The rules the values of a parsed file keep about themselves: which statements are real, and that a value built by
hand is public, and an import withholds no name, unless it says otherwise."""
from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, Constant, Function


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3


def test_a_value_built_with_a_name_alone_is_public_and_an_import_withholds_nothing():
    assert (Class(1, "_A").public, Function(1, "_f").public, Constant(1, "_X").public) == (True, True, True)
    assert Import(1, ("m",), ("_x",)).withheld == frozenset()
    assert (Class(1, "A", public=False).public, Import(1, ("m",), ("x",), withheld=frozenset({"x"})).withheld) == (
        False, frozenset({"x"}))
