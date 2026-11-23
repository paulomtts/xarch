"""The language of the app, through the spec module's controller: the profile names it, or the first by name is the
language, and checks read from the profile what its data file says; the standard library and the builtins come from the
runtime."""
from pathlib import Path

import pytest

from tests.fakes.runtime import FakeRuntime
from tests.modules.spec.application.builders import spec_controller
from tests.modules.spec.languages import PYTHON as BUNDLED
from xarch.modules.spec.contract import CheckProfile, ProfileChecked
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark

JOINS = {"name": r"\w+", "package": r"\w+", "member": "."}
PASCAL = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": [{"base": "sys.Contract"}],
          "dynamic": ["sys.load"], "namespace": "system", "standard": "interpreter"} | JOINS
PYTHON = {"title": "Python", "extension": ".py", "package_file": "__init__.py", "interface": [{"base": "typing.Protocol"}],
          "namespace": "builtins", "cache": "__pycache__", "standard": "interpreter"} | JOINS
APP = Path("/p/app")
BASE = {"name": "base", "parts": {"core": {"path": "core", "role": "the rules"}}}
RUNTIME = FakeRuntime(frozenset({"strutils"}), frozenset({"writeln"}), frozenset({"begin"}))


def view(profile: dict, languages: dict) -> CheckedLanguage:
    spec, _ = spec_controller({"base": profile}, languages=languages, runtime=RUNTIME)
    return spec.profile("base").language


def test_a_profile_without_a_language_has_the_first_language_by_name_as_the_checks_read_it():
    assert view(BASE, {"python": PYTHON, "pascal": PASCAL}) == CheckedLanguage(
        "Pascal", ".pas", "unit.pas", (InterfaceMark(("sys", "Contract")),), (("sys", "load"),), names=r"\w+", package=r"\w+",
        member=".")


def test_a_profile_names_its_language_and_the_skeleton_says_the_file_that_stands_for_a_folder():
    spec, _ = spec_controller({"base": BASE | {"language": "python"}}, languages={"python": PYTHON, "pascal": PASCAL}, runtime=RUNTIME)
    assert spec.profile("base").language == CheckedLanguage(
        "Python", ".py", "__init__.py", (InterfaceMark(("typing", "Protocol")),), (), names=r"\w+", package=r"\w+",
        member=".")
    assert spec.skeleton("base").package_file == "__init__.py"


def test_the_standard_library_and_the_builtins_a_profile_is_checked_against_come_from_the_runtime():
    named = BASE | {"language": "pascal", "parts": {"core": {"path": "core", "role": "r", "libraries": ["strutils"]}}}
    spec, _ = spec_controller({"base": named}, languages={"pascal": PASCAL}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert isinstance(checked, ProfileChecked)
    assert [problem.text for problem in checked.problems] == [
        "base: parts.core.libraries: 'strutils' is in the standard library, which every part may import unless `reserved` names it"]


@pytest.mark.parametrize("languages, language", [
    pytest.param({}, CheckedLanguage(), id="with no language to choose from, the language is said by nothing"),
    pytest.param({"python": PYTHON}, CheckedLanguage("Python", ".py", "__init__.py", (InterfaceMark(("typing", "Protocol")),),
                                                     names=r"\w+", package=r"\w+", member="."),
                 id="with one, it is that one"),
])
def test_xarch_with_no_language_to_choose_from_or_one_reads_the_profile_all_the_same(languages, language):
    assert view(BASE, languages) == language


def test_the_skeleton_names_the_language_and_the_words_the_runtime_reserves():
    spec, _ = spec_controller({"base": BASE}, languages={"pascal": PASCAL}, runtime=RUNTIME)
    skeleton = spec.skeleton("base")
    assert (skeleton.title, skeleton.package_file, skeleton.reserved) == ("Pascal", "unit.pas", frozenset({"begin"}))


TOY = PASCAL | {"supplies": {"file": "exact", "import": "exact", "import.relative": "exact",
                             "class": {"partial": "a class defined in a branch is not read"}}}


def test_a_key_whose_check_the_reader_of_its_language_cannot_feed_is_refused_and_one_it_feeds_partly_is_approximate():
    named = BASE | {"language": "toy", "parts": {"core": {"path": "core", "role": "r", "names": "*Rule",
                                                          "no_callbacks": True}}}
    spec, _ = spec_controller({"base": named}, languages={"toy": TOY}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert [problem.text for problem in checked.problems] == [
        "base: parts.core.no_callbacks: its check reads callback (each call of a function's own parameter, whether it "
        "is the receiver and whether it is annotated as a callable), which the language toy does not supply: drop "
        "parts.core.no_callbacks, or check the app with a language whose reader supplies callback"]
    spec, _ = spec_controller({"base": named | {"parts": {"core": {"path": "core", "role": "r", "names": "*Rule"}}}},
                              languages={"toy": TOY}, runtime=RUNTIME)
    assert spec.profile("base").approximate == (
        Shortfall("parts.core.names", "class", "a class defined in a branch is not read"),)


def test_the_bundled_language_gives_its_package_pattern_and_its_member_and_reads_its_lists_as_before():
    checked = BUNDLED.checked
    assert (checked.package, checked.member, checked.interface, checked.dynamic, checked.immutable, BUNDLED.namespace) == (
        r"(?!\d)\w+", ".", (InterfaceMark(("typing", "Protocol")), InterfaceMark(("typing_extensions", "Protocol"))),
        (("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
        (RecordMark(("typing", "NamedTuple")), RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
        "builtins")
