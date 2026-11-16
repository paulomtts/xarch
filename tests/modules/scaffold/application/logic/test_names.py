"""The name of a new instance: a lowercase identifier that is no reserved word and is not private."""
import pytest

from tests.modules.scaffold.builders import PYTHON_NAMES, PYTHON_PRIVATE
from xarch.modules.scaffold.application.logic.names import valid_name
from xarch.modules.scaffold.domain.values import Language

PYTHON = Language("Python", "__init__.py", frozenset({"class"}), PYTHON_NAMES, PYTHON_PRIVATE)
"""Python as its data file says it, with one reserved word."""


@pytest.mark.parametrize("name, valid", [
    pytest.param("documents", True, id="a lowercase word is valid"),
    pytest.param("doc_store2", True, id="an underscore and a digit inside are valid"),
    pytest.param("Documents", False, id="an uppercase letter is refused"),
    pytest.param("my-module", False, id="a dash is refused"),
    pytest.param("1abc", False, id="a leading digit is refused"),
    pytest.param("", False, id="an empty name is refused"),
    pytest.param("class", False, id="a reserved word is refused"),
    pytest.param("def", True, id="what the language does not reserve is not"),
    pytest.param("_x", False, id="a private name is refused"),
    pytest.param("a b", False, id="a space is refused"),
    pytest.param("dõcs", False, id="a letter that is not ascii is refused"),
    pytest.param("a.b", False, id="a dot is refused"),
])
def test_valid_name(name, valid):
    assert valid_name(name, PYTHON) == valid
