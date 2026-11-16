"""The name of a new instance: a lowercase identifier that is no reserved word and is not private, and the first of
these rules a name breaks."""
import pytest

from tests.modules.scaffold.builders import PYTHON_NAMES, PYTHON_PRIVATE
from xarch.modules.scaffold.application.logic.names import broken_rule
from xarch.modules.scaffold.domain.values import LOWERCASE, NOT_A_NAME, PRIVATE, RESERVED, Language

PYTHON = Language("Python", "__init__.py", frozenset({"class"}), PYTHON_NAMES, PYTHON_PRIVATE)
"""Python as its data file says it, with one reserved word."""


@pytest.mark.parametrize("name, broken", [
    pytest.param("documents", None, id="a lowercase word is valid"),
    pytest.param("doc_store2", None, id="an underscore and a digit inside are valid"),
    pytest.param("Documents", LOWERCASE, id="an uppercase letter is refused"),
    pytest.param("my-module", NOT_A_NAME, id="a dash is refused"),
    pytest.param("1abc", NOT_A_NAME, id="a leading digit is refused"),
    pytest.param("", NOT_A_NAME, id="an empty name is refused"),
    pytest.param("class", RESERVED, id="a reserved word is refused"),
    pytest.param("def", None, id="what the language does not reserve is not"),
    pytest.param("_x", PRIVATE, id="a private name is refused"),
    pytest.param("a b", NOT_A_NAME, id="a space is refused"),
    pytest.param("dõcs", LOWERCASE, id="a letter that is not ascii is refused"),
    pytest.param("a.b", NOT_A_NAME, id="a dot is refused"),
])
def test_the_first_rule_a_name_breaks(name, broken):
    assert broken_rule(name, PYTHON) == broken
