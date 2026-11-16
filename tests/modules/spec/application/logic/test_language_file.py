"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import pytest

from xarch.kernel.capabilities import EXACT, Supply
from xarch.modules.spec.application.logic.language_file import PARTIAL, language_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.language import CheckedLanguage

DOCUMENT = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
            "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system", "cache": ".objs",
            "standard": "interpreter"}


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", ".pas", "unit.pas", (("sys", "Contract"),),
                                  (("sys", "load"), ("sys", "Contract", "load"))),
        "system", "interpreter", ".objs")


def test_the_marks_of_a_language_are_its_extension_and_its_package_file():
    assert language_of("pascal", DOCUMENT).checked.marks.extension == ".pas"
    assert language_of("pascal", DOCUMENT).checked.marks.package_file == "unit.pas"


def test_every_problem_of_a_document_is_listed_naming_the_preset():
    broken = {"title": "", "extension": "pas", "package_file": 3, "interface": "x", "dynamic": ["", "a b"], "cache": "a/b", "extra": 1}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        "unknown key 'extra': use branching, cache, call, comment, directives, dynamic, encoding, extension, "
        "importing, interface, name, namespace, nothing, package_file, private, shebang, special, standard, supplies, "
        "title",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        "extension: must be a dot and a name, such as .pas",
        "package_file: must be a file name ending in the extension",
        "interface: must be a list of dotted names, such as [pkg.Name]",
        "dynamic: '' is not a dotted name such as pkg.name", "dynamic: 'a b' is not a dotted name such as pkg.name",
        "cache: must be a folder name"]


def test_a_document_that_is_no_mapping_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", ["x"])
    assert caught.value.problems == (
        "presets/language/odd.yaml: must be a mapping of keys, such as title, extension and package_file",)


def test_the_tokens_of_the_code_are_read_when_the_document_gives_them():
    tokens = {"name": "[a-z]+", "private": "_", "special": "__", "call": "__call__", "nothing": "None",
              "comment": "//", "directives": ["lint: off"], "shebang": "#!", "encoding": "utf-8",
              "branching": ["if", "case"]}
    language = language_of("pascal", DOCUMENT | tokens)
    checked = language.checked
    assert (language.names, checked.private, checked.special, checked.call, checked.nothing, checked.comment,
            checked.directives, checked.shebang, checked.encoding, checked.branching) == (
        "[a-z]+", "_", "__", "__call__", "None", "//", ("lint: off",), "#!", "utf-8", ("if", "case"))


@pytest.mark.parametrize("given, problem", [
    pytest.param({"name": "[a-"}, "name: must be a regular expression", id="a name that is no regular expression"),
    pytest.param({"directives": "noqa"}, "directives: must be a list of non-empty strings", id="directives not a list"),
    pytest.param({"branching": ["if", ""]}, "branching: must be a list of non-empty strings", id="an empty keyword"),
    pytest.param({"comment": ""}, "comment: must be a non-empty string", id="an empty comment marker"),
    pytest.param({"importing": "import {dotted}"}, "importing: must be a line holding {dotted} and {name}",
                 id="an import that names no name"),
    pytest.param({"importing": "from {dotted}\nimport {name}"}, "importing: must be a line holding {dotted} and {name}",
                 id="an import of two lines"),
])
def test_a_token_that_is_not_what_its_key_takes_is_a_problem(given, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | given)
    assert [p.removeprefix("presets/language/odd.yaml: ").split(":")[0] for p in caught.value.problems] == [
        problem.split(":")[0]]
    assert caught.value.problems[0].removeprefix("presets/language/odd.yaml: ").startswith(problem)


def test_how_a_file_imports_a_name_is_read_when_the_document_gives_it():
    assert language_of("pascal", DOCUMENT | {"importing": "uses {dotted}.{name};"}).checked.importing == "uses {dotted}.{name};"
    assert language_of("pascal", DOCUMENT).checked.importing == ""


def test_the_facts_its_reader_supplies_are_read_each_with_its_grade():
    language = language_of("pascal", DOCUMENT | {"supplies": {"import": "exact",
                                                              "class": {"partial": "nested classes are not read"}}})
    assert language.checked.supplies == (Supply("import", EXACT), Supply("class", PARTIAL, "nested classes are not read"))


def test_a_document_that_says_nothing_of_its_reader_supplies_no_grade():
    assert language_of("pascal", DOCUMENT).checked.supplies is None


@pytest.mark.parametrize("supplies, problem", [
    pytest.param({"imports": "exact"}, "supplies: 'imports' is not a fact a check reads", id="an unknown fact"),
    pytest.param({"import": "good"}, "supplies.import: must be exact, or {partial: <what it misses>}",
                 id="a grade that is neither"),
    pytest.param({"import": {"partial": " "}}, "supplies.import: must be exact, or {partial: <what it misses>}",
                 id="a partial grade with no note"),
    pytest.param(["import"], "supplies: must be a mapping of facts", id="no mapping"),
])
def test_a_supply_that_is_not_what_the_key_takes_is_a_problem(supplies, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"supplies": supplies})
    assert caught.value.problems[0].removeprefix("presets/language/odd.yaml: ").startswith(problem)
