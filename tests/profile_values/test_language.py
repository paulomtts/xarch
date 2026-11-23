"""The language as a check reads it: which names are public or special, by the tokens its data file gives."""
import itertools
from importlib import resources

import pytest
import yaml

from xarch.profile_values.language import NOTHING, CheckedLanguage

PYTHON_SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                .read_text(encoding="utf-8"))["special"]
TOKENS = CheckedLanguage(private="_", special=PYTHON_SPECIAL)
PERCENT = CheckedLanguage(special=r"%\w+")


@pytest.mark.parametrize("name, public, special", [
    pytest.param("load", True, False, id="a plain name is public"),
    pytest.param("_load", False, False, id="a name that starts as a private one does is not public"),
    pytest.param("__init__", False, True, id="a special name is special, and starts as a private one does"),
    pytest.param("__load", False, False, id="one that only starts as a special name does is not special"),
    pytest.param("load__", True, False, id="one that only ends as a special name does is not special"),
    pytest.param("__", False, True, id="the affix alone is special"),
    pytest.param("___", False, True, id="three underscores are special"),
    pytest.param("_x", False, False, id="one underscore makes no special name"),
])
def test_a_name_is_told_by_the_tokens_of_the_language(name, public, special):
    assert (TOKENS.is_public(name), TOKENS.is_special(name)) == (public, special)


def test_python_s_pattern_tells_every_short_name_as_its_affix_did():
    names = ["".join(chars) for size in range(1, 7) for chars in itertools.product("_a1", repeat=size)
             if chars[0] != "1"]
    assert [name for name in names if TOKENS.is_special(name) != (name.startswith("__") and name.endswith("__"))] == []


@pytest.mark.parametrize("name, special", [
    pytest.param("%OnNew", True, id="a name the pattern matches in full"),
    pytest.param("OnNew", False, id="a name it does not match"),
    pytest.param("x%OnNew", False, id="a name it matches only in part"),
])
def test_a_special_name_is_one_the_language_s_pattern_matches_in_full(name, special):
    assert PERCENT.is_special(name) is special


def test_a_language_that_gives_no_tokens_has_every_name_public():
    assert (CheckedLanguage().is_public("_load"), CheckedLanguage().is_special("__init__")) == (True, False)


def test_a_language_that_says_nothing_has_no_package_pattern_and_no_member():
    assert (CheckedLanguage().package, CheckedLanguage().member) == ("", "")


@pytest.mark.parametrize("language, returns, nothing", [
    pytest.param(CheckedLanguage(nothing=("None",)), "None", True, id="an annotation nothing lists"),
    pytest.param(CheckedLanguage(nothing=("void", "Promise<void>")), "Promise<void>", True, id="any one it lists"),
    pytest.param(CheckedLanguage(nothing=("void",)), "Promise<Order>", False, id="another annotation gives a value"),
    pytest.param(CheckedLanguage(nothing=("None",)), None, False, id="no annotation, and unannotated not said"),
    pytest.param(CheckedLanguage(unannotated=NOTHING), None, True, id="no annotation, and unannotated says nothing"),
    pytest.param(CheckedLanguage(unannotated=NOTHING), "Order", False, id="an annotation still gives a value"),
    pytest.param(CheckedLanguage(), "None", False, id="a language that lists nothing has no annotation of no value"),
])
def test_a_method_gives_no_value_by_the_annotations_the_language_lists_or_its_word_on_none(language, returns, nothing):
    assert language.gives_nothing(returns) is nothing
