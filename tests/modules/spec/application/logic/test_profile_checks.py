"""What a profile may write as a name of the checked language: a name as its data file says one is, names joined by
dots, and a method called on anything, on the bundled language and on a hand-made one whose names may hold a dash."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.application.logic.profile_checks import is_dotted, is_name, method_name

DASHED = replace(PYTHON, names="[a-z][a-z-]*")


@pytest.mark.parametrize("text, language, name", [
    pytest.param("sqlmodel", PYTHON, True, id="a name of the language"),
    pytest.param("2fast", PYTHON, False, id="the language says a name does not start with a digit"),
    pytest.param("web-kit", PYTHON, False, id="nor holds a dash"),
    pytest.param("web-kit", DASHED, True, id="another language may say it does"),
    pytest.param("anything at all", replace(PYTHON, names=""), True, id="a language that says nothing allows any text"),
    pytest.param("", replace(PYTHON, names=""), False, id="but nothing"),
])
def test_a_name_is_what_the_language_says_one_is(text, language, name):
    assert is_name(text, language) is name


@pytest.mark.parametrize("text, least, dotted", [
    pytest.param("socket", 1, True, id="one name"),
    pytest.param("datetime.datetime.now", 1, True, id="names joined by dots"),
    pytest.param("socket", 2, False, id="one name is not enough when two are wanted"),
    pytest.param("pytest..param", 1, False, id="an empty step"),
    pytest.param("pkg.2x", 1, False, id="a step that is no name"),
])
def test_a_dotted_name_is_names_of_the_language_joined_by_dots(text, least, dotted):
    assert is_dotted(text, PYTHON, least) is dotted


@pytest.mark.parametrize("item, name", [
    pytest.param(".absolute()", "absolute", id="a method called on anything"),
    pytest.param(".absolute", None, id="without its parentheses it is none"),
    pytest.param("path.absolute()", None, id="nor on a name"),
    pytest.param(".a.b()", None, id="nor of two steps"),
])
def test_a_method_of_a_forbidden_list_is_named_by_what_lies_between_the_dot_and_the_parentheses(item, name):
    assert method_name(item, PYTHON) == name
