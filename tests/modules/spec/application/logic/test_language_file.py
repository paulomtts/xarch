"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import re
from pathlib import Path

import pytest
import yaml

from xarch.modules.spec.application.logic.language_file import PARTIAL, first_language, language_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import EXACT, Supply
from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark

NAME = r"[A-Za-z_]\w*"
JOINS = {"name": NAME, "package": NAME, "member": "."}
DOCUMENT = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": [{"base": "sys.Contract"}],
            "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system", "cache": ".objs",
            "standard": "interpreter"} | JOINS
UNJOINED = {key: value for key, value in DOCUMENT.items() if key not in JOINS}
"""DOCUMENT with none of name, package and member."""
TEST_LANGUAGES = tuple(sorted((Path(__file__).resolve().parents[4] / "fakes" / "languages").glob("*.yaml")))
PERCENT = {"name": "%?[A-Za-z][A-Za-z0-9]*", "package": "%?[A-Za-z][A-Za-z0-9]*", "member": ".", "namespace": "%SYSTEM",
           "interface": [{"base": "%RegisteredObject"}], "dynamic": ["%SYSTEM.OBJ.Load"],
           "immutable": ["%SerialObject", "%Lib.Rec(frozen=yes)"]}
"""The lists of a language whose names may start with a percent, under its own patterns."""
INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", ".pas", "unit.pas",
                                  (InterfaceMark(("sys", "Contract")),),
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
        "standard, supplies, title, unannotated",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        "extension: must be a dot and a name, such as .pas",
        "package_file: must be a file name ending in the extension",
        INTERFACE,
        "dynamic: '' is not an outside name such as <package>.<name>",
        "dynamic: 'a b' is not an outside name such as <package>.<name>",
        "cache: must be a folder name"]


def test_a_document_that_is_no_mapping_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", ["x"])
    assert caught.value.problems == (
        "presets/language/odd.yaml: must be a mapping of keys, such as title, extension and package_file",)


def test_the_tokens_of_the_code_are_read_when_the_document_gives_them():
    tokens = {"name": "[A-Za-z]+", "private": "_", "special": r"(?=__)\w*(?<=__)", "call": "__call__", "nothing": ["None"],
              "comment": "//", "directives": ["lint: off"], "shebang": "#!", "encoding": "utf-8",
              "branching": ["if", "case"], "branching_expressions": ["?"]}
    language = language_of("pascal", DOCUMENT | tokens)
    checked = language.checked
    assert (language.names, checked.private, checked.special, checked.call, checked.nothing, checked.comment,
            checked.directives, checked.shebang, checked.encoding, checked.branching, checked.branching_expressions) == (
        "[A-Za-z]+", "_", r"(?=__)\w*(?<=__)", "__call__", ("None",), "//", ("lint: off",), "#!", "utf-8", ("if", "case"), ("?",))


@pytest.mark.parametrize("given, problem", [
    pytest.param({"name": "[a-"}, "name: must be a regular expression", id="a name that is no regular expression"),
    pytest.param({"directives": "noqa"}, "directives: must be a list of non-empty strings", id="directives not a list"),
    pytest.param({"branching": ["if", ""]}, "branching: must be a list of non-empty strings", id="an empty keyword"),
    pytest.param({"comment": ""}, "comment: must be a non-empty string", id="an empty comment marker"),
    pytest.param({"special": 3}, "special: must be a regular expression", id="a special name that is no text"),
    pytest.param({"special": ""}, "special: must be a regular expression", id="an empty special name"),
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

def test_a_special_name_that_is_no_regular_expression_says_why():
    with pytest.raises(re.error) as error:
        re.compile("(")
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"special": "("})
    assert caught.value.problems == (f"presets/language/odd.yaml: special: must be a regular expression: {error.value}",)


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
        "%SYSTEM", (InterfaceMark(("%RegisteredObject",)),), (("%SYSTEM", "OBJ", "Load"),),
        (RecordMark(("%SerialObject",)), RecordMark(("%Lib", "Rec"), (("frozen", "yes"),))))


def test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them():
    python = {"name": r"(?!\d)\w+", "package": r"(?!\d)\w+", "member": "."}
    lists = {key: PERCENT[key] for key in ("interface", "dynamic", "immutable")}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | lists | python)
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        INTERFACE,
        "dynamic: '%SYSTEM.OBJ.Load' is not an outside name such as <package>.<name>",
        "immutable: '%SerialObject' is not an outside name such as <package>.<name>, or one called with keywords such as "
        "<package>.<name>(<name>=<value>)",
        "immutable: '%Lib.Rec(frozen=yes)' is not an outside name such as <package>.<name>, or one called with keywords "
        "such as <package>.<name>(<name>=<value>)"]


def test_a_document_that_gives_none_of_name_package_and_member_reads_an_outside_name_as_its_whole_text():
    assert language_of("pascal", UNJOINED).checked.interface == (InterfaceMark(("sys.Contract",)),)


def test_a_namespace_is_a_name_the_language_allows():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"namespace": "2sys"})
    assert caught.value.problems == ("presets/language/odd.yaml: namespace: must be a name",)


@pytest.mark.parametrize("path", TEST_LANGUAGES, ids=lambda path: path.stem)
def test_a_test_only_language_loads_with_the_three_keys_that_say_how_an_outside_name_is_written(path):
    checked = language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.names and checked.package and checked.member


def test_the_percent_test_only_language_reads_its_lists_by_its_own_patterns():
    path = next(path for path in TEST_LANGUAGES if path.stem == "percent")
    checked = language_of("percent", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert (checked.interface, checked.dynamic, checked.immutable) == (
        (InterfaceMark(keyword="Abstract"),), (("%SYSTEM", "OBJ", "Load"),), (RecordMark(("%SerialObject",)),))


def test_the_brace_test_only_language_marks_an_interface_by_its_keyword():
    path = next(path for path in TEST_LANGUAGES if path.stem == "brace")
    checked = language_of("brace", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.interface == (InterfaceMark(keyword="interface"),)


def test_what_makes_a_class_an_interface_is_read_as_marks_in_the_order_written():
    marks = [{"keyword": "interface"}, {"base": "sys.Contract"}, {"base": "sys"}]
    assert language_of("pascal", DOCUMENT | {"interface": marks}).checked.interface == (
        InterfaceMark(keyword="interface"), InterfaceMark(("sys", "Contract")), InterfaceMark(("sys",)))


def test_a_language_that_marks_no_interface_has_none():
    left_out = {key: value for key, value in DOCUMENT.items() if key != "interface"}
    assert (language_of("pascal", DOCUMENT | {"interface": []}).checked.interface,
            language_of("pascal", left_out).checked.interface) == ((), ())


@pytest.mark.parametrize("interface", [
    pytest.param("sys.Contract", id="no list"),
    pytest.param(["sys.Contract"], id="the old shape, a list of outside names"),
    pytest.param([{"base": "sys.Contract", "keyword": "interface"}], id="a mark of two keys"),
    pytest.param([{"kind": "sys.Contract"}], id="a key that is neither"),
    pytest.param([{"base": "not a name!"}], id="a base that is no outside name"),
    pytest.param([{"base": 3}], id="a base that is no text"),
    pytest.param([{"keyword": "two words"}], id="a keyword with a space"),
    pytest.param([{"keyword": "2x"}], id="a keyword that is no name of the language"),
    pytest.param([{"keyword": ""}], id="an empty keyword"),
    pytest.param([{"base": "sys.Contract"}, "sys.Other", {"kind": "x"}], id="said once however many marks are wrong"),
])
def test_a_mark_of_an_interface_that_is_neither_a_base_nor_a_keyword_is_refused_once(interface):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"interface": interface})
    assert caught.value.problems == (f"presets/language/odd.yaml: {INTERFACE}",)


def test_the_marks_of_an_interface_are_not_read_when_the_keys_that_say_how_a_name_is_written_are_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"package": "[a-", "interface": ["sys.Contract"]})
    assert [p.removeprefix("presets/language/odd.yaml: ").split(":")[0] for p in caught.value.problems] == ["package"]


def test_the_annotations_of_no_value_and_the_word_on_none_are_read_when_the_document_gives_them():
    checked = language_of("pascal", DOCUMENT | {"nothing": ["void", "Promise<void>"], "unannotated": "nothing"}).checked
    left_out = language_of("pascal", DOCUMENT).checked
    assert ((checked.nothing, checked.unannotated), (left_out.nothing, left_out.unannotated)) == (
        (("void", "Promise<void>"), "nothing"), ((), ""))


@pytest.mark.parametrize("given, problem", [
    pytest.param({"nothing": "None"}, "nothing: must be a list of return annotations", id="the old shape, one text"),
    pytest.param({"nothing": []}, "nothing: must be a list of return annotations", id="an empty list"),
    pytest.param({"nothing": [""]}, "nothing: must be a list of return annotations", id="an empty annotation"),
    pytest.param({"nothing": [1]}, "nothing: must be a list of return annotations", id="an annotation that is no text"),
    pytest.param({"unannotated": "none"}, "unannotated: must be nothing", id="another word"),
    pytest.param({"unannotated": True}, "unannotated: must be nothing", id="no text"),
])
def test_annotations_of_no_value_and_a_word_on_none_that_are_not_what_their_key_takes_are_refused(given, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | given)
    assert caught.value.problems == (f"presets/language/odd.yaml: {problem}",)


def test_the_test_only_languages_say_their_annotations_of_no_value_or_their_word_on_none():
    loaded = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
              for path in TEST_LANGUAGES}
    assert ((loaded["brace"].nothing, loaded["brace"].unannotated),
            (loaded["percent"].nothing, loaded["percent"].unannotated, loaded["percent"].special)) == (
        (("void", "Promise<void>"), ""), ((), "nothing", r"%\w+"))
