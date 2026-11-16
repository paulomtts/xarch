"""Whether a text is a name a language allows, and a public one, by the pattern and the private mark it gives."""
import pytest

from xarch.kernel.logic.names import is_name, is_public_name

PATTERN = r"(?!\d)\w+"


@pytest.mark.parametrize("text, name, public", [
    pytest.param("docs", True, True, id="a name the pattern allows is public"),
    pytest.param("_cache", True, False, id="one that starts as a private one does is no public name"),
    pytest.param("2docs", False, False, id="what the pattern refuses is no name"),
])
def test_a_name_is_told_by_the_pattern_and_the_private_mark(text, name, public):
    assert (is_name(text, PATTERN), is_public_name(text, PATTERN, "_")) == (name, public)


def test_a_language_that_gives_no_pattern_allows_any_text_but_nothing():
    assert (is_name("a b", ""), is_name("", "")) == (True, False)
