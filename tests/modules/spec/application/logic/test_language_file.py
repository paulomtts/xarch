"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import pytest

from xarch.modules.spec.application.logic.language_file import PARTIAL, first_language, language_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import EXACT, Supply
from xarch.profile_values.language import CheckedLanguage, RecordMark

NAME = r"[A-Za-z_]\w*"
JOINS = {"name": NAME, "package": NAME, "member": "."}
DOCUMENT = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
            "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system", "cache": ".objs",
            "standard": "interpreter"} | JOINS
UNJOINED = {key: value for key, value in DOCUMENT.items() if key not in JOINS}
"""DOCUMENT with none of name, package and member."""
PERCENT = {"name": "%?[A-Za-z][A-Za-z0-9]*", "package": "%?[A-Za-z][A-Za-z0-9]*", "member": ".", "namespace": "%SYSTEM",
           "interface": ["%RegisteredObject"], "dynamic": ["%SYSTEM.OBJ.Load"],
           "immutable": ["%SerialObject", "%Lib.Rec(frozen=yes)"]}
"""The lists of a language whose names may start with a percent, under its own patterns."""


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", ".pas", "unit.pas", (("sys", "Contract"),),
                                  (("sys", "load"), ("sys", "Contract", "load")), names=NAME, package=NAME, member="."),
        "system", "interpreter", ".objs", NAME)


def test_the_marks_of_a_language_are_its_extension_and_its_package_file():
    assert language_of("pascal", DOCUMENT).checked.marks.extension == ".pas"
    assert language_of("pascal", DOCUMENT).checked.marks.package_file == "unit.pas"


def test_every_problem_of_a_document_is_listed_naming_the_preset():
    broken = {"title": "", "extension": "pas", "package_file": 3, "interface": "x", "dynamic": ["", "a b"], "cache": "a/b",
              "extra": 1} | JOINS
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        "unknown key 'extra': use branching, branching_expressions, cache, call, comment, directives, dynamic, encoding, extension, "
        "immutable, importing, interface, member, name, namespace, nothing, package, package_file, private, shebang, special, "
        "standard, supplies, title",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        "extension: must be a dot and a name, such as .pas",
        "package_file: must be a file name ending in the extension",
        "interface: must be a list of outside names, such as [<package>.<name>]",
        "dynamic: '' is not an outside name such as <package>.<name>",
        "dynamic: 'a b' is not an outside name such as <package>.<name>",
        "cache: must be a folder name"]


def test_a_document_that_is_no_mapping_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", ["x"])
    assert caught.value.problems == (
        "presets/language/odd.yaml: must be a mapping of keys, such as title, extension and package_file",)


def test_the_tokens_of_the_code_are_read_when_the_document_gives_them():
    tokens = {"name": "[A-Za-z]+", "private": "_", "special": "__", "call": "__call__", "nothing": "None",
              "comment": "//", "directives": ["lint: off"], "shebang": "#!", "encoding": "utf-8",
              "branching": ["if", "case"], "branching_expressions": ["?"]}
    language = language_of("pascal", DOCUMENT | tokens)
    checked = language.checked
    assert (language.names, checked.private, checked.special, checked.call, checked.nothing, checked.comment,
            checked.directives, checked.shebang, checked.encoding, checked.branching, checked.branching_expressions) == (
        "[A-Za-z]+", "_", "__", "__call__", "None", "//", ("lint: off",), "#!", "utf-8", ("if", "case"), ("?",))


@pytest.mark.parametrize("given, problem", [
    pytest.param({"name": "[a-"}, "name: must be a regular expression", id="a name that is no regular expression"),
    pytest.param({"directives": "noqa"}, "directives: must be a list of non-empty strings", id="directives not a list"),
    pytest.param({"branching": ["if", ""]}, "branching: must be a list of non-empty strings", id="an empty keyword"),
    pytest.param({"comment": ""}, "comment: must be a non-empty string", id="an empty comment marker"),
    pytest.param({"immutable": "pkg.Record"}, "immutable: must be a list of outside names",
                 id="marks of an immutable record not a list"),
    pytest.param({"immutable": ["pkg.record(frozen)"]}, "immutable: 'pkg.record(frozen)' is not an outside name",
                 id="a keyword with no value"),
    pytest.param({"immutable": ["pkg.record(2x=yes)"]}, "immutable: 'pkg.record(2x=yes)' is not an outside name",
                 id="a keyword that is no name of the language"),
    pytest.param({"package": "[a-"}, "package: must be a regular expression: ",
                 id="a package that is no regular expression, and no list checked after it"),
    pytest.param({"member": "a b"}, "member: must be a non-empty string with no space", id="a member with a space"),
    pytest.param({"member": ""}, "member: must be a non-empty string with no space", id="an empty member"),
    pytest.param({"member": 3}, "member: must be a non-empty string with no space", id="a member that is no text"),
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


def test_what_makes_a_class_an_immutable_record_is_read_as_an_outside_name_and_the_keywords_a_decorator_is_called_with():
    marks = ["pkg.Record", "pkg.record(frozen=yes, slots=no)"]
    assert language_of("pascal", DOCUMENT | {"immutable": marks}).checked.immutable == (
        RecordMark(("pkg", "Record")), RecordMark(("pkg", "record"), (("frozen", "yes"), ("slots", "no"))))
    assert language_of("pascal", DOCUMENT).checked.immutable == ()


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


def test_the_language_of_an_app_is_the_first_by_name_and_none_when_xarch_reads_none():
    assert (first_language({"python": 1, "pascal": 2}), first_language({})) == ("pascal", "")


@pytest.mark.parametrize("given", [
    pytest.param(["name"], id="a name alone"),
    pytest.param(["package"], id="a package alone"),
    pytest.param(["member"], id="a member alone"),
    pytest.param(["name", "package"], id="no member"),
    pytest.param(["name", "member"], id="no package"),
    pytest.param(["package", "member"], id="no name"),
])
def test_name_package_and_member_are_given_together(given):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", UNJOINED | {key: JOINS[key] for key in given})
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        f"missing `{key}`: name, package and member are given together" for key in ("name", "package", "member")
        if key not in given]


def test_the_lists_of_a_language_are_read_by_its_own_patterns():
    language = language_of("percent", DOCUMENT | PERCENT)
    assert (language.namespace, language.checked.interface, language.checked.dynamic, language.checked.immutable) == (
        "%SYSTEM", (("%RegisteredObject",),), (("%SYSTEM", "OBJ", "Load"),),
        (RecordMark(("%SerialObject",)), RecordMark(("%Lib", "Rec"), (("frozen", "yes"),))))


def test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them():
    python = {"name": r"(?!\d)\w+", "package": r"(?!\d)\w+", "member": "."}
    lists = {key: PERCENT[key] for key in ("interface", "dynamic", "immutable")}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | lists | python)
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        "interface: '%RegisteredObject' is not an outside name such as <package>.<name>",
        "dynamic: '%SYSTEM.OBJ.Load' is not an outside name such as <package>.<name>",
        "immutable: '%SerialObject' is not an outside name such as <package>.<name>, or one called with keywords such as "
        "<package>.<name>(<name>=<value>)",
        "immutable: '%Lib.Rec(frozen=yes)' is not an outside name such as <package>.<name>, or one called with keywords "
        "such as <package>.<name>(<name>=<value>)"]


def test_a_document_that_gives_none_of_name_package_and_member_reads_an_outside_name_as_its_whole_text():
    assert language_of("pascal", UNJOINED).checked.interface == (("sys.Contract",),)


def test_a_namespace_is_a_name_the_language_allows():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"namespace": "2sys"})
    assert caught.value.problems == ("presets/language/odd.yaml: namespace: must be a name",)
