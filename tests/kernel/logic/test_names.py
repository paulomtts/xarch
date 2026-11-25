"""Whether a text is a name a language allows, and a private one, by the pattern and the private mark it gives."""
import pytest

from xarch.kernel.logic.names import is_name, is_private_name, outside_steps, outside_text

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
