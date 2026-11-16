"""The language as a check reads it: which names are public or special, by the tokens its data file gives."""
import pytest

from xarch.profile_values.language import CheckedLanguage

TOKENS = CheckedLanguage(private="_", special="__")


@pytest.mark.parametrize("name, public, special", [
    pytest.param("load", True, False, id="a plain name is public"),
    pytest.param("_load", False, False, id="a name that starts as a private one does is not public"),
    pytest.param("__init__", False, True, id="a special name is special, and starts as a private one does"),
    pytest.param("__load", False, False, id="one that only starts as a special name does is not special"),
])
def test_a_name_is_told_by_the_tokens_of_the_language(name, public, special):
    assert (TOKENS.is_public(name), TOKENS.is_special(name)) == (public, special)


def test_a_language_that_gives_no_tokens_has_every_name_public():
    assert (CheckedLanguage().is_public("_load"), CheckedLanguage().is_special("__init__")) == (True, False)
