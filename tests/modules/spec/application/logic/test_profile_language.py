"""The language of a profile: the one it names among the languages xarch ships, the first by name when it names none,
and what its data file says wherever a profile's values depend on it."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.language import CheckedLanguage

PASCAL = replace(Language(), name="pascal", checked=CheckedLanguage("Pascal", (".pas",), ("unit.pas",), package=r"\w+", member="."),
                 namespace="system", standard_names=frozenset({"strutils"}), builtin_names=frozenset({"writeln"}))
BOTH = {"pascal": PASCAL, "python": PYTHON}


def test_the_language_a_profile_names_is_read_from_the_languages_xarch_ships():
    assert parsed(layered(language="pascal"), languages=BOTH).language == PASCAL
    assert parsed(layered(language="python"), languages=BOTH).language == PYTHON


def test_a_profile_that_names_no_language_has_the_first_by_name():
    assert parsed(layered(), languages=BOTH).language == PASCAL
    assert parsed(layered(), languages={"python": PYTHON}).language == PYTHON


def test_a_language_xarch_does_not_ship_is_refused_naming_those_it_does():
    assert problems(layered(language="ruby"), languages=BOTH) == [
        "layered.yaml: language: 'ruby' is not a language xarch reads: use pascal, python"]
    assert problems(layered(language=["python"])) == [
        "layered.yaml: language: ['python'] is not a language xarch reads: use python"]


def test_the_extension_of_the_language_is_what_a_test_file_pattern_ends_in():
    testing = {"files": ["check_*.pas"], "functions": "check_*"}
    assert parsed(layered(testing=testing), languages=BOTH, presets={}).framework.files == ("check_*.pas",)
    assert problems(covered(testing={"files": ["check_*.py"], "functions": "check_*"}), languages=BOTH) == [
        "layered.yaml: testing.files: 'check_*.py' is not a file name pattern: a name ending in .pas, with `*` for any "
        "text"]


def test_the_standard_library_and_the_builtins_are_those_of_the_language():
    assert problems(layered(parts={**layered()["parts"], "shared": {"path": "shared", "role": "r",
                                                                       "imports": {"libraries": ["strutils"]}}}),
                    languages=BOTH) == [
        "layered.yaml: parts.shared.imports.libraries: 'strutils' is in the standard library, which every part may import "
        "unless `reserved` names it"]
    assert problems(layered(never={"pure": ["writeln"]}, parts={
        **layered()["parts"], "shared": {"path": "shared", "role": "r", "uses": {"never": "pure"}}}), languages=BOTH) == [
        "layered.yaml: never.pure: 'writeln' is a Pascal builtin, which a bare name does not ban: write system.writeln"]


@pytest.mark.parametrize("language, name", [(PASCAL, "unit.pas"), (PYTHON, "__init__.py")])
def test_a_path_is_placed_by_the_marks_of_the_language(language, name):
    architecture = replace(parsed(layered(), languages=BOTH), language=language)
    assert architecture.place_of(("shared", name)).part == "shared"
    assert architecture.place_of(("shared", f"x{language.checked.extension}")).sub == ("x",)
