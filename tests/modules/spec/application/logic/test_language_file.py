"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import pytest

from xarch.modules.spec.application.logic.language_file import language_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language

DOCUMENT = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
            "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system", "cache": ".objs",
            "standard": "interpreter"}


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", "Pascal", ".pas", "unit.pas", (("sys", "Contract"),), (("sys", "load"), ("sys", "Contract", "load")),
        "system", "interpreter", ".objs")


def test_the_marks_of_a_language_are_its_extension_and_its_package_file():
    assert language_of("pascal", DOCUMENT).marks.extension == ".pas"
    assert language_of("pascal", DOCUMENT).marks.package_file == "unit.pas"


def test_every_problem_of_a_document_is_listed_naming_the_preset():
    broken = {"title": "", "extension": "pas", "package_file": 3, "interface": "x", "dynamic": ["", "a b"], "cache": "a/b", "extra": 1}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        "unknown key 'extra': use cache, dynamic, extension, interface, namespace, package_file, standard, title",
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
