"""What a profile may write as a name of the checked language: a name as its data file says one is, an outside name
read by its package pattern and its member, and a method called on anything, on the bundled language, on a hand-made
one whose names may hold a dash, and on a test-only one whose member is not a dot."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import BRACE, PYTHON
from xarch.kernel.logic.names import is_name
from xarch.modules.spec.application.logic.profile_checks import never_names, outside_names

DASHED = replace(PYTHON, names="[a-z][a-z-]*")
NOT_OUTSIDE = "is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()"


def forbidding(item: str) -> tuple[tuple[tuple[str, ...], ...] | None, list[str]]:
    """What a `never` list of the one item comes to: the names it bans, and every problem."""
    problems: list[str] = []
    read = never_names([item], "at", problems, PYTHON)
    return (None if read is None else tuple(steps for steps in read if steps is not None)), problems


def test_each_item_of_a_never_list_keeps_its_place_and_a_refused_one_holds_none():
    problems: list[str] = []
    assert never_names(["socket", "pkg..x", "socket", ".absolute()"], "at", problems, PYTHON) == (
        ("socket",), None, None, ("", "absolute()"))
    assert problems == [f"at: 'pkg..x' {NOT_OUTSIDE}", "at: 'socket' is listed twice"]


@pytest.mark.parametrize("text, language, name", [
    pytest.param("sqlmodel", PYTHON, True, id="a name of the language"),
    pytest.param("2fast", PYTHON, False, id="the language says a name does not start with a digit"),
    pytest.param("web-kit", PYTHON, False, id="nor holds a dash"),
    pytest.param("web-kit", DASHED, True, id="another language may say it does"),
    pytest.param("anything at all", replace(PYTHON, names=""), True, id="a language that says nothing allows any text"),
    pytest.param("", replace(PYTHON, names=""), False, id="but nothing"),
])
def test_a_name_is_what_the_language_says_one_is(text, language, name):
    assert is_name(text, language.names) is name


@pytest.mark.parametrize("text, found", [
    pytest.param("socket", ((("socket",),), []), id="a package alone"),
    pytest.param("datetime.datetime.now", ((("datetime", "datetime", "now"),), []), id="a package and names after it"),
    pytest.param("pytest..param", ((), [f"at: 'pytest..param' {NOT_OUTSIDE}"]), id="an empty step"),
    pytest.param("pkg.2x", ((), [f"at: 'pkg.2x' {NOT_OUTSIDE}"]), id="a step that is no name"),
])
def test_an_outside_name_is_a_package_then_names_of_the_language_after_its_member(text, found):
    assert forbidding(text) == found


def test_one_step_is_not_enough_where_two_are_wanted():
    problems: list[str] = []
    assert (outside_names(["socket"], "at", problems, PYTHON), problems) == (
        (), ["at: 'socket' is not an outside name such as <package>.<name>"])


def test_an_outside_name_of_another_language_is_read_by_its_member():
    problems: list[str] = []
    assert (outside_names(["node:test#skip"], "testing.skips", problems, BRACE), problems) == (
        (("node:test", "skip"),), [])


@pytest.mark.parametrize("item, found", [
    pytest.param(".absolute()", (((("", "absolute()"),), [])), id="a method called on anything"),
    pytest.param(".absolute", ((), ["at: '.absolute' is neither an outside name nor a method: write .absolute() for a "
                                     "method called on anything"]), id="without its parentheses it is none"),
    pytest.param("path.absolute()", ((), [f"at: 'path.absolute()' {NOT_OUTSIDE}"]), id="nor on a name"),
    pytest.param(".a.b()", ((), [f"at: '.a.b()' {NOT_OUTSIDE}"]), id="nor of two steps"),
])
def test_a_method_of_a_forbidden_list_is_named_by_what_lies_between_the_dot_and_the_parentheses(item, found):
    assert forbidding(item) == found
