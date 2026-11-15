"""The language of the app, through the spec module's controller: the profile names it, or the first by name is the
language, and checks read from the profile what its data file says; the standard library and the builtins come from the
runtime."""
from pathlib import Path

import pytest

from tests.fakes.runtime import FakeRuntime
from tests.modules.spec.application.builders import spec_controller
from xarch.kernel.logic.language import LanguageView
from xarch.modules.spec.contract import CheckProfile, ProfileChecked

PASCAL = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
          "dynamic": ["sys.load"], "namespace": "system", "standard": "interpreter"}
PYTHON = {"title": "Python", "extension": ".py", "package_file": "__init__.py", "interface": ["typing.Protocol"],
          "namespace": "builtins", "cache": "__pycache__", "standard": "interpreter"}
APP = Path("/p/app")
BASE = {"xarch": 2, "name": "base", "parts": {"core": {"path": "core", "role": "the rules"}}}
RUNTIME = FakeRuntime(frozenset({"strutils"}), frozenset({"writeln"}), frozenset({"begin"}))


def view(profile: dict, languages: dict) -> LanguageView:
    spec, _ = spec_controller({"base": profile}, languages=languages, runtime=RUNTIME)
    return spec.profile("base").language


def test_a_profile_without_a_language_has_the_first_language_by_name_as_the_checks_read_it():
    assert view(BASE, {"python": PYTHON, "pascal": PASCAL}) == LanguageView(
        "Pascal", ".pas", "unit.pas", (("sys", "Contract"),), (("sys", "load"),))


def test_a_profile_names_its_language_and_the_skeleton_says_the_file_that_stands_for_a_folder():
    spec, _ = spec_controller({"base": BASE | {"language": "python"}}, languages={"python": PYTHON, "pascal": PASCAL}, runtime=RUNTIME)
    assert spec.profile("base").language == LanguageView("Python", ".py", "__init__.py", (("typing", "Protocol"),), ())
    assert spec.skeleton("base").package_file == "__init__.py"


def test_the_standard_library_and_the_builtins_a_profile_is_checked_against_come_from_the_runtime():
    named = BASE | {"language": "pascal", "parts": {"core": {"path": "core", "role": "r", "libraries": ["strutils"]}}}
    spec, _ = spec_controller({"base": named}, languages={"pascal": PASCAL}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert isinstance(checked, ProfileChecked)
    assert [problem.text for problem in checked.problems] == [
        "base: parts.core.libraries: 'strutils' is in the standard library, which every part may import unless `reserved` names it"]


@pytest.mark.parametrize("languages", [{}, {"python": PYTHON}])
def test_xarch_with_no_language_to_choose_from_or_one_reads_the_profile_all_the_same(languages):
    assert isinstance(view(BASE, languages), LanguageView)


def test_the_skeleton_names_the_language_and_the_words_the_runtime_reserves():
    spec, _ = spec_controller({"base": BASE}, languages={"pascal": PASCAL}, runtime=RUNTIME)
    skeleton = spec.skeleton("base")
    assert (skeleton.language, skeleton.package_file, skeleton.reserved) == ("Pascal", "unit.pas", frozenset({"begin"}))
