"""What a profile may write as a name of the checked language: a name as its data file says one is, names joined by
dots, and a method called on anything, on the bundled language and on a hand-made one whose names may hold a dash."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.application.logic.profile_checks import dotted_names, is_name, never_names

DASHED = replace(PYTHON, names="[a-z][a-z-]*")
NOT_DOTTED = "is not a dotted name such as datetime.datetime.now, nor an import name such as socket, nor a method such as " \
             ".absolute()"


def forbidding(item: str) -> tuple[tuple[tuple[str, ...], ...] | None, list[str]]:
    """What a `never` list of the one item comes to: the names it bans, and every problem."""
    problems: list[str] = []
    return never_names([item], "at", problems, PYTHON), problems


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


@pytest.mark.parametrize("text, found", [
    pytest.param("socket", ((("socket",),), []), id="one name"),
    pytest.param("datetime.datetime.now", ((("datetime", "datetime", "now"),), []), id="names joined by dots"),
    pytest.param("pytest..param", ((), [f"at: 'pytest..param' {NOT_DOTTED}"]), id="an empty step"),
    pytest.param("pkg.2x", ((), [f"at: 'pkg.2x' {NOT_DOTTED}"]), id="a step that is no name"),
])
def test_a_dotted_name_is_names_of_the_language_joined_by_dots(text, found):
    assert forbidding(text) == found


def test_one_name_is_not_enough_where_two_are_wanted():
    problems: list[str] = []
    assert (dotted_names(["socket"], "at", problems, PYTHON), problems) == (
        (), ["at: 'socket' is not a dotted name such as pkg.sub.name"])


@pytest.mark.parametrize("item, found", [
    pytest.param(".absolute()", (((("", "absolute()"),), [])), id="a method called on anything"),
    pytest.param(".absolute", ((), ["at: '.absolute' is neither a dotted name nor a method: write .absolute() for a "
                                     "method called on anything"]), id="without its parentheses it is none"),
    pytest.param("path.absolute()", ((), [f"at: 'path.absolute()' {NOT_DOTTED}"]), id="nor on a name"),
    pytest.param(".a.b()", ((), [f"at: '.a.b()' {NOT_DOTTED}"]), id="nor of two steps"),
])
def test_a_method_of_a_forbidden_list_is_named_by_what_lies_between_the_dot_and_the_parentheses(item, found):
    assert forbidding(item) == found
