"""Whether a text is a name a language allows, and a private one, by the pattern and the private mark it gives."""
import pytest

from xarch.kernel.logic.names import is_name, is_private_name

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
