"""The language as a check reads it: which names are special, by the pattern its data file gives. Whether a name is
public is no question of the language's: its reader says it, as the fact public."""
import itertools
from importlib import resources

import pytest
import yaml

from xarch.kernel.placement import Marks
from xarch.profile_values.language import NOTHING, CheckedLanguage

PYTHON_SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                .read_text(encoding="utf-8"))["special"]
TOKENS = CheckedLanguage(private="_", special=PYTHON_SPECIAL)
PERCENT = CheckedLanguage(special=r"%\w+")


@pytest.mark.parametrize("name, special", [
    pytest.param("load", False, id="a plain name is not special"),
    pytest.param("_load", False, id="a name that starts as a private one does is not special"),
    pytest.param("__init__", True, id="a special name is special"),
    pytest.param("__load", False, id="one that only starts as a special name does is not special"),
    pytest.param("load__", False, id="one that only ends as a special name does is not special"),
    pytest.param("__", True, id="the affix alone is special"),
    pytest.param("___", True, id="three underscores are special"),
    pytest.param("_x", False, id="one underscore makes no special name"),
])
def test_a_name_is_told_special_by_the_pattern_of_the_language(name, special):
    assert TOKENS.is_special(name) is special


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


def test_a_language_that_gives_no_tokens_has_no_special_name_and_never_says_whether_a_name_is_public():
    assert CheckedLanguage().is_special("__init__") is False
    assert not hasattr(CheckedLanguage(), "is_public")


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


def test_a_message_prints_the_first_ending_and_the_first_package_file_and_nothing_when_there_is_none():
    several = CheckedLanguage(extensions=(".ts", ".tsx"), package_files=("index.ts", "index.tsx"))
    assert (several.extension, several.package_file) == (".ts", "index.ts")
    assert (CheckedLanguage().extension, CheckedLanguage().package_file) == ("", "")


def test_the_marks_of_a_language_are_its_endings_and_its_package_files_in_full():
    several = CheckedLanguage(extensions=(".ts", ".tsx"), package_files=("index.ts", "index.tsx"))
    assert several.marks == Marks((".ts", ".tsx"), ("index.ts", "index.tsx"))
