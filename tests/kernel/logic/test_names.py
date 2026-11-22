"""Whether a text is a name a language allows, and a private one, by the pattern and the private mark it gives."""
import pytest

from xarch.kernel.logic.names import is_name, is_private_name, outside_name, outside_steps, outside_text

PATTERN = r"(?!\d)\w+"


@pytest.mark.parametrize("text, name, private", [
    pytest.param("docs", True, False, id="a name the pattern allows"),
    pytest.param("_cache", True, True, id="one that starts as a private one does is a private name"),
    pytest.param("2docs", False, False, id="what the pattern refuses is no name"),
])
def test_a_name_is_told_by_the_pattern_and_the_private_mark(text, name, private):
    assert (is_name(text, PATTERN), is_private_name(text, "_")) == (name, private)


def test_a_language_that_gives_no_pattern_allows_any_text_but_nothing():
    assert (is_name("a b", ""), is_name("", "")) == (True, False)


@pytest.mark.parametrize("text, private, found", [
    pytest.param("_cache", "_", True, id="a name that starts with the private mark is private"),
    pytest.param("cache", "_", False, id="one that does not is not"),
    pytest.param("_cache", "", False, id="no name is private in a language that marks none"),
])
def test_a_name_is_private_when_it_starts_with_the_mark_the_language_gives(text, private, found):
    assert is_private_name(text, private) == found


BRACE_NAME = r"[A-Za-z_$][A-Za-z0-9_$]*"
BRACE_PACKAGE = r"(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*|node:[a-z_/]+"
PERCENT = r"%?[A-Za-z][A-Za-z0-9]*"


@pytest.mark.parametrize("text, steps", [
    pytest.param("datetime.datetime.now", ("datetime", "datetime", "now"), id="a package and two names after it"),
    pytest.param("socket", ("socket",), id="a package alone"),
    pytest.param("builtins.open", ("builtins", "open"), id="a package and one name"),
    pytest.param("a..b", None, id="an empty step"),
    pytest.param("datetime.", None, id="a member with nothing after it"),
    pytest.param(".x", None, id="nothing before the member"),
    pytest.param("lodash-es", None, id="a package the pattern refuses"),
    pytest.param("@scope/pkg", None, id="a scoped package the pattern refuses"),
    pytest.param("", None, id="no text"),
])
def test_an_outside_name_is_read_by_the_patterns_of_a_language_joined_by_a_dot(text, steps):
    assert outside_name(text, PATTERN, PATTERN, ".") == steps


@pytest.mark.parametrize("text, steps", [
    pytest.param("node:fs#readFileSync", ("node:fs", "readFileSync"), id="a runtime module and a name in it"),
    pytest.param("globalThis#fetch", ("globalThis", "fetch"), id="the namespace, which the package pattern refuses"),
    pytest.param("lodash.debounce", ("lodash.debounce",), id="a dot is part of a package where the member is not one"),
    pytest.param("lodash.debounce#debounce", ("lodash.debounce", "debounce"), id="a dotted package and a name in it"),
    pytest.param("@scope/pkg", ("@scope/pkg",), id="a scoped package alone"),
    pytest.param("Foo#bar", None, id="a head that is neither a package nor the namespace"),
    pytest.param("node:fs#", None, id="a member with nothing after it"),
    pytest.param("#x", None, id="nothing before the member"),
])
def test_an_outside_name_is_read_by_the_member_of_a_language_that_joins_with_a_hash(text, steps):
    assert outside_name(text, BRACE_NAME, BRACE_PACKAGE, "#", "globalThis") == steps


@pytest.mark.parametrize("text, steps", [
    pytest.param("%Library.RegisteredObject", ("%Library", "RegisteredObject"), id="a percent package and a name"),
    pytest.param("%SerialObject", ("%SerialObject",), id="a percent package alone"),
    pytest.param("9x", None, id="a package that starts with a digit"),
])
def test_an_outside_name_is_read_by_the_patterns_of_a_language_whose_names_start_with_a_percent(text, steps):
    assert outside_name(text, PERCENT, PERCENT, ".", "%SYSTEM") == steps


def test_under_a_language_that_gives_no_member_an_outside_name_is_its_whole_text():
    assert (outside_name("datetime.datetime.now", "", "", ""), outside_name("", "", "", "")) == (
        ("datetime.datetime.now",), None)


@pytest.mark.parametrize("text, member, steps", [
    pytest.param("node:fs#readFileSync", "#", ("node:fs", "readFileSync"), id="split at the member"),
    pytest.param("a.b.c", ".", ("a", "b", "c"), id="split at a dot member, then at each dot"),
    pytest.param(".now()", ".", ("", "now()"), id="a method called on anything"),
    pytest.param("a.b.c", "", ("a.b.c",), id="no member: one step"),
    pytest.param("a.b", "#", ("a.b",), id="no member in the text: one step"),
])
def test_the_steps_of_an_outside_name_are_split_with_no_check(text, member, steps):
    assert outside_steps(text, member) == steps


@pytest.mark.parametrize("steps, member, text", [
    pytest.param(("", "absolute()"), ".", ".absolute()", id="a method, under a dot member"),
    pytest.param(("", "absolute()"), "#", ".absolute()", id="a method, under another member"),
    pytest.param(("node:fs", "readFileSync"), "#", "node:fs#readFileSync", id="a package and a name, with the member"),
    pytest.param(("datetime", "datetime", "now"), ".", "datetime.datetime.now", id="the names after it joined by dots"),
    pytest.param(("socket",), ".", "socket", id="a package alone"),
    pytest.param((), ".", "", id="nothing"),
    pytest.param(("a", "b", "c"), "", "ab.c", id="no member: nothing between the package and its names"),
])
def test_an_outside_name_is_printed_back_with_the_member_of_the_language(steps, member, text):
    assert outside_text(steps, member) == text
