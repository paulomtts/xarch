"""An outside name read by the name and package patterns of a language, its member and its namespace."""
import pytest

from xarch.modules.spec.application.logic.outside_name import outside_name

PATTERN = r"(?!\d)\w+"

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
