"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import re
from importlib import resources
from pathlib import Path

import pytest
import yaml

from tests.modules.spec.languages import BRACE
from tests.modules.spec.languages import PYTHON as PYTHON_LANGUAGE
from xarch.kernel.placement import Marks
from xarch.modules.spec.application.logic.language_file import DOC, PARTIAL, first_language, language_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language, StandardLists
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
from xarch.profile_values.language import (
    BLOCK,
    LINE,
    CheckedLanguage,
    CommentForm,
    InterfaceMark,
    RecordMark,
    SpecWriting,
    Worked,
    Writing,
)

NAME = r"[A-Za-z_]\w*"
JOINS = {"name": NAME, "package": NAME, "member": "."}
DOCUMENT = {"title": "Pascal", "extensions": [".pas"], "package_files": ["unit.pas"],
            "interface": [{"base": "sys.Contract"}], "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system",
            "cache": ".objs", "standard": "interpreter"} | JOINS
UNJOINED = {key: value for key, value in DOCUMENT.items() if key not in JOINS}
"""DOCUMENT with none of name, package and member."""
TEST_LANGUAGES = tuple(sorted((Path(__file__).resolve().parents[4] / "fakes" / "languages").glob("*.yaml")))
PERCENT = {"name": "%?[A-Za-z][A-Za-z0-9]*", "package": "%?[A-Za-z][A-Za-z0-9]*", "member": ".", "namespace": "%SYSTEM",
           "interface": [{"base": "%RegisteredObject"}], "dynamic": ["%SYSTEM.OBJ.Load"],
           "immutable": [{"base": "%SerialObject"}, {"decorator": "%Lib.Rec", "keywords": {"frozen": "yes"}}]}
"""The lists of a language whose names may start with a percent, under its own patterns."""
INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"
IMMUTABLE = "immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}"
STANDARD = "standard: must be interpreter, or a map of modules, reserved and builtins, each a list of names"
LISTS = {"modules": [], "reserved": [], "builtins": []}
"""A standard that lists nothing, to which a test adds the lists it needs."""
KEYS_USED = ("branching, branching_expressions, cache, call, comments, directives, dynamic, dynamic_attributes, encoding, extensions, "
             "immutable, importing, interface, member, name, namespace, nothing, package, package_files, private, "
             "shebang, special, standard, supplies, title, unannotated, worked, writing")
"""The keys of a data file, as the unknown-key text lists them."""
COMMENTS = "comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}"
EXTENSIONS = "extensions: must be a non-empty list of endings, each starting with a dot"
PACKAGE_FILES = "package_files: must be a list of file names, each ending in one of extensions"
UNLISTED = {key: value for key, value in DOCUMENT.items() if key != "package_files"}
"""DOCUMENT with no file standing for a folder."""


def refused(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", document)
    return [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems]


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", (".pas",), ("unit.pas",),
                                  (InterfaceMark(("sys", "Contract")),),
                                  (("sys", "load"), ("sys", "Contract", "load")), names=NAME, package=NAME, member="."),
        "system", "interpreter", ".objs", NAME)


def test_the_marks_of_a_language_are_its_extensions_and_its_package_files():
    assert language_of("pascal", DOCUMENT).checked.marks == Marks((".pas",), ("unit.pas",))


def test_every_problem_of_a_document_is_listed_naming_the_preset():
    broken = {"title": "", "extensions": "pas", "package_files": 3, "interface": "x", "dynamic": ["", "a b"],
              "cache": "a/b", "extra": 1} | JOINS
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        f"unknown key 'extra': use {KEYS_USED}",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        EXTENSIONS,
        PACKAGE_FILES,
        INTERFACE,
        "dynamic: '' is not an outside name such as <package>.<name>",
        "dynamic: 'a b' is not an outside name such as <package>.<name>",
        "cache: must be a folder name"]


def test_a_document_that_is_no_mapping_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", ["x"])
    assert caught.value.problems == (
        "presets/language/odd.yaml: must be a mapping of keys, such as title, extensions and package_files",)


def test_the_tokens_of_the_code_are_read_when_the_document_gives_them():
    tokens = {"name": "[A-Za-z]+", "private": "_", "special": r"(?=__)\w*(?<=__)", "call": "__call__", "nothing": ["None"],
              "comments": [{"line": "//"}], "directives": ["lint: off"], "shebang": "#!", "encoding": "utf-8",
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
    pytest.param({"special": 3}, "special: must be a regular expression", id="a special name that is no text"),
    pytest.param({"special": ""}, "special: must be a regular expression", id="an empty special name"),
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


def test_a_data_file_that_supplies_the_fact_of_tables_split_by_form_is_refused_as_supplying_an_unknown_fact():
    assert refused(DOCUMENT | {"supplies": {"function.tables": "exact"}}) == [
        f"supplies: 'function.tables' is not a fact a check reads: use {', '.join(sorted(FACTS))}"]
    assert "function.tables.call" in sorted(FACTS)


def test_a_special_name_that_is_no_regular_expression_says_why():
    with pytest.raises(re.error) as error:
        re.compile("(")
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"special": "("})
    assert caught.value.problems == (f"presets/language/odd.yaml: special: must be a regular expression: {error.value}",)


def test_what_makes_a_class_an_immutable_record_is_read_as_marks_of_four_forms_in_the_order_written():
    marks = [{"base": "pkg.Record"}, {"decorator": "pkg.record", "keywords": {"frozen": "yes", "slots": "no"}},
             {"decorator": "pkg.record"}, {"fields": "readonly"}, {"type": "pkg.Frozen"}]
    assert language_of("pascal", DOCUMENT | {"immutable": marks}).checked.immutable == (
        RecordMark(base=("pkg", "Record")),
        RecordMark(decorator=("pkg", "record"), keywords=(("frozen", "yes"), ("slots", "no"))),
        RecordMark(decorator=("pkg", "record")), RecordMark(fields="readonly"), RecordMark(type=("pkg", "Frozen")))
    assert language_of("pascal", DOCUMENT).checked.immutable == ()


@pytest.mark.parametrize("immutable", [
    pytest.param({"base": "pkg.Record"}, id="no list"),
    pytest.param(["pkg.Record"], id="the old shape, an outside name as a string"),
    pytest.param(["pkg.record(frozen=yes)"], id="the old shape, a decorator and its keywords as a string"),
    pytest.param([{"base": "pkg.Record", "type": "pkg.Frozen"}], id="two forms"),
    pytest.param([{"base": "pkg.Record", "keywords": {"frozen": "yes"}}], id="keywords beside a base"),
    pytest.param([{"keywords": {"frozen": "yes"}}], id="keywords alone"),
    pytest.param([{"kind": "pkg.Record"}], id="an unknown key"),
    pytest.param([{"decorator": "pkg.record", "frozen": "yes"}], id="an unknown key beside a form"),
    pytest.param([{"decorator": "pkg.record", "keywords": {}}], id="empty keywords"),
    pytest.param([{"decorator": "pkg.record", "keywords": ["frozen"]}], id="keywords that are no map"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"frozen": True}}],
                 id="a keyword value that is no string, as YAML reads True unquoted"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"frozen": ""}}], id="an empty keyword value"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"2x": "yes"}}], id="a keyword that is no name of the language"),
    pytest.param([{"base": "not a name!"}], id="a base that is no outside name"),
    pytest.param([{"type": 3}], id="a type that is no text"),
    pytest.param([{"fields": "pkg.readonly"}], id="a fields word holding the member"),
    pytest.param([{"fields": "two words"}], id="a fields word with a space"),
    pytest.param([{"base": "pkg.Record"}, "pkg.Other", {"kind": "x"}], id="said once however many marks are wrong"),
])
def test_a_mark_of_an_immutable_record_of_no_form_is_refused_once(immutable):
    assert refused(DOCUMENT | {"immutable": immutable}) == [IMMUTABLE]


def test_the_marks_of_an_immutable_record_are_not_read_when_the_keys_that_say_how_a_name_is_written_are_refused():
    assert [p.split(":")[0] for p in refused(DOCUMENT | {"package": "[a-", "immutable": ["pkg.Record"]})] == ["package"]


def test_how_a_file_imports_a_name_is_read_when_the_document_gives_it():
    assert language_of("pascal", DOCUMENT | {"importing": "uses {dotted}.{name};"}).checked.importing == "uses {dotted}.{name};"
    assert language_of("pascal", DOCUMENT).checked.importing == ""


def test_the_facts_its_reader_supplies_are_read_each_with_its_grade_and_file_package_follows_package_files():
    supplies = {"supplies": {"import": "exact", "class": {"partial": "nested classes are not read"}}}
    listed = (Supply("import", EXACT), Supply("class", PARTIAL, "nested classes are not read"))
    assert language_of("pascal", DOCUMENT | supplies).checked.supplies == (*listed, Supply("file.package", EXACT))
    assert language_of("pascal", UNLISTED | supplies).checked.supplies == listed


def test_a_document_that_says_nothing_of_its_reader_supplies_no_grade_whatever_package_files_says():
    assert (language_of("pascal", DOCUMENT).checked.supplies, language_of("pascal", UNLISTED).checked.supplies) == (
        None, None)


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
        (RecordMark(base=("%SerialObject",)), RecordMark(decorator=("%Lib", "Rec"), keywords=(("frozen", "yes"),))))


def test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them():
    python = {"name": r"(?!\d)\w+", "package": r"(?!\d)\w+", "member": "."}
    lists = {key: PERCENT[key] for key in ("interface", "dynamic", "immutable")}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | lists | python)
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        INTERFACE, "dynamic: '%SYSTEM.OBJ.Load' is not an outside name such as <package>.<name>", IMMUTABLE]


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
        (InterfaceMark(keyword="Abstract"),), (("%SYSTEM", "OBJ", "Load"),), (RecordMark(base=("%SerialObject",)),))


def test_the_brace_test_only_language_marks_an_interface_by_its_keyword():
    path = next(path for path in TEST_LANGUAGES if path.stem == "brace")
    checked = language_of("brace", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.interface == (InterfaceMark(keyword="interface"),)


def test_the_brace_test_only_language_marks_an_immutable_record_by_a_keyword_on_every_field():
    path = next(path for path in TEST_LANGUAGES if path.stem == "brace")
    checked = language_of("brace", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.immutable == (RecordMark(fields="readonly"),)


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


def test_a_language_that_lists_its_standard_library_reads_the_three_lists_in_the_order_written():
    standard = {"modules": ["strutils", "sysutils"], "reserved": ["begin", "end"], "builtins": ["writeln"]}
    assert (language_of("pascal", DOCUMENT | {"standard": standard}).standard,
            language_of("pascal", DOCUMENT | {"standard": LISTS}).standard,
            language_of("pascal", DOCUMENT).standard) == (
        StandardLists(("strutils", "sysutils"), ("begin", "end"), ("writeln",)), StandardLists(), "interpreter")


@pytest.mark.parametrize("standard", [
    pytest.param("node", id="another word"),
    pytest.param("", id="an empty string"),
    pytest.param(None, id="left empty"),
    pytest.param(3, id="a number"),
    pytest.param(["fs"], id="a list"),
    pytest.param({"modules": [], "reserved": []}, id="a map missing a list"),
    pytest.param(LISTS | {"keywords": []}, id="a map with a key besides the three"),
    pytest.param(LISTS | {"modules": "fs"}, id="a list that is no list"),
    pytest.param(LISTS | {"modules": [3]}, id="an item that is no text"),
    pytest.param(LISTS | {"reserved": [""]}, id="an empty item"),
])
def test_a_standard_that_is_neither_the_word_nor_the_three_lists_is_refused_once(standard):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"standard": standard})
    assert caught.value.problems == (f"presets/language/odd.yaml: {STANDARD}",)


@pytest.mark.parametrize("lists, problems", [
    pytest.param({"modules": ["x y"]}, ["standard.modules: 'x y' is not a package name the language allows"],
                 id="a module the package pattern refuses"),
    pytest.param({"modules": ["os.path"]}, ["standard.modules: 'os.path' is not a package name the language allows"],
                 id="a module below a top-level one"),
    pytest.param({"reserved": ["x y"]}, ["standard.reserved: 'x y' is not a name the language allows"],
                 id="a reserved word the name pattern refuses"),
    pytest.param({"builtins": ["1a"]}, ["standard.builtins: '1a' is not a name the language allows"],
                 id="a builtin the name pattern refuses"),
    pytest.param({"modules": ["x y", "fs", "2b"]}, ["standard.modules: 'x y' is not a package name the language allows",
                                                    "standard.modules: '2b' is not a package name the language allows"],
                 id="one problem for each item refused"),
])
def test_an_item_of_the_lists_is_checked_with_the_language_s_own_patterns(lists, problems):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"standard": LISTS | lists})
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == problems


def test_with_no_name_package_and_member_any_text_is_an_item_of_the_lists():
    standard = {"modules": ["x y", "os.path"], "reserved": ["1a"], "builtins": ["a b"]}
    assert language_of("pascal", UNJOINED | {"standard": standard}).standard == StandardLists(
        ("x y", "os.path"), ("1a",), ("a b",))


def test_the_items_of_the_lists_are_not_checked_when_the_keys_that_say_how_a_name_is_written_are_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"name": "[a-", "standard": LISTS | {"modules": ["x y"], "reserved": ["1a"]}})
    assert [p.removeprefix("presets/language/odd.yaml: ").split(":")[0] for p in caught.value.problems] == ["name"]


def test_the_brace_test_only_language_lists_its_standard_library_and_the_percent_one_says_interpreter():
    loaded = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8")))
              for path in TEST_LANGUAGES}
    assert (loaded["brace"].standard, loaded["percent"].standard) == (
        StandardLists(("fs", "path", "node:fs", "node:path"), ("class", "const", "function", "interface"),
                      ("globalThis", "fetch")), "interpreter")


def test_the_endings_and_the_package_files_are_read_in_the_order_written():
    checked = language_of("pascal", DOCUMENT | {"extensions": [".ts", ".tsx"], "package_files": ["index.ts"]}).checked
    assert (checked.extensions, checked.package_files) == ((".ts", ".tsx"), ("index.ts",))
    assert (checked.extension, checked.package_file) == (".ts", "index.ts")


def test_package_files_left_out_read_none_and_the_file_loads():
    checked = language_of("pascal", UNLISTED).checked
    assert (checked.package_files, checked.package_file, checked.marks) == ((), "", Marks((".pas",)))


@pytest.mark.parametrize("value", [
    pytest.param(".py", id="a string"),
    pytest.param([], id="an empty list"),
    pytest.param([3], id="a list holding a number"),
    pytest.param(["py"], id="an ending with no dot"),
    pytest.param([".py", ".py"], id="an ending listed twice"),
    pytest.param([".p y"], id="an ending with a space"),
])
def test_extensions_that_are_not_a_list_of_endings_are_one_problem(value):
    assert refused(UNLISTED | {"extensions": value}) == [EXTENSIONS]


def test_extensions_are_required():
    assert refused({key: value for key, value in UNLISTED.items() if key != "extensions"}) == ["missing `extensions`"]


@pytest.mark.parametrize("value, problems", [
    pytest.param(["index.js"], ["package_files: 'index.js' ends in none of extensions"], id="another ending"),
    pytest.param(["index.js", "main.rb"], ["package_files: 'index.js' ends in none of extensions",
                                          "package_files: 'main.rb' ends in none of extensions"], id="one problem each"),
    pytest.param([".ts"], ["package_files: '.ts' ends in none of extensions"], id="only the ending"),
    pytest.param("index.ts", [PACKAGE_FILES], id="no list"),
    pytest.param([], [PACKAGE_FILES], id="an empty list"),
    pytest.param(["index.ts", "index.ts"], [PACKAGE_FILES], id="a file listed twice"),
    pytest.param([""], [PACKAGE_FILES], id="an empty name"),
])
def test_package_files_must_each_end_in_one_of_the_extensions(value, problems):
    assert refused(DOCUMENT | {"extensions": [".ts"], "package_files": value}) == problems


def test_package_files_are_not_checked_against_extensions_that_are_refused_already():
    assert refused(DOCUMENT | {"extensions": "ts", "package_files": ["index.js"]}) == [EXTENSIONS]


def test_the_old_keys_of_one_ending_and_one_package_file_are_unknown_keys():
    old = {key: value for key, value in UNLISTED.items() if key != "extensions"} | {"extension": ".pas",
                                                                                    "package_file": "unit.pas"}
    assert refused(old) == [f"unknown keys 'extension', 'package_file': use {KEYS_USED}", "missing `extensions`"]


@pytest.mark.parametrize("grade", [pytest.param("exact", id="exact"), pytest.param({"partial": "some"}, id="partial")])
def test_file_package_is_never_written_under_supplies(grade):
    assert refused(DOCUMENT | {"supplies": {"import": "exact", "file.package": grade}}) == [
        "supplies: file.package follows package_files: drop it from supplies"]


def test_python_reads_one_ending_and_one_package_file_and_supplies_file_package_though_its_file_does_not_list_it():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    checked = PYTHON_LANGUAGE.checked
    assert (checked.extensions, checked.package_files) == ((".py",), ("__init__.py",))
    assert "file.package" not in document["supplies"]
    assert Supply("file.package", EXACT) in checked.supplies


def test_the_test_only_languages_say_several_endings_and_brace_two_package_files_percent_none():
    read = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
            for path in TEST_LANGUAGES}
    assert (read["brace"].extensions, read["brace"].package_files) == ((".ts", ".tsx", ".mts"), ("index.ts", "index.tsx"))
    assert (read["percent"].extensions, read["percent"].package_files) == ((".cls", ".mac"), ())


def test_the_test_only_languages_read_their_comment_forms_in_the_order_written():
    read = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
            for path in TEST_LANGUAGES}
    assert read["brace"].comments == (CommentForm(LINE, "//"), CommentForm(BLOCK, "/*", "*/"),
                                      CommentForm(DOC, "/**", "*/"))
    assert read["percent"].comments == (CommentForm(LINE, "//"), CommentForm(LINE, ";"), CommentForm(BLOCK, "/*", "*/"),
                                        CommentForm(DOC, "///", ""))
    assert (read["brace"].comment, read["percent"].comment) == ("//", "//")


@pytest.mark.parametrize("comments, comment", [
    pytest.param([{"block": ["/*", "*/"]}], "/*", id="a block form alone gives its opening"),
    pytest.param([{"doc": ["///", ""]}], "", id="a doc form alone gives none, a doc opening never being the comment"),
    pytest.param([{"doc": ["/**", "*/"]}, {"block": ["/*", "*/"]}, {"line": "--"}], "--",
                 id="a line form wins over a block form written before it"),
])
def test_the_comment_is_the_first_line_marker_else_the_first_block_opening(comments, comment):
    assert language_of("pascal", DOCUMENT | {"comments": comments}).checked.comment == comment


def test_comments_left_out_read_no_form_and_no_marker_and_the_file_loads():
    checked = language_of("pascal", DOCUMENT).checked
    assert (checked.comments, checked.comment) == ((), "")


@pytest.mark.parametrize("value", [
    pytest.param("#", id="a string"),
    pytest.param([{"hash": "#"}], id="a form of an unknown kind"),
    pytest.param([{"line": "#", "block": ["/*", "*/"]}], id="a form of two keys"),
    pytest.param([{"line": ""}], id="a line form with an empty marker"),
    pytest.param([{"line": 3}], id="a line form whose marker is no text"),
    pytest.param([{"block": ["/*"]}], id="a block form of one item"),
    pytest.param([{"block": ["/*", ""]}], id="a block form with an empty closing"),
    pytest.param([{"doc": ["", "*/"]}], id="a doc form with an empty opening"),
    pytest.param(["#"], id="a list holding a string"),
    pytest.param([{"line": "//"}, {"line": ""}], id="one wrong form among right ones"),
])
def test_comments_that_are_not_a_list_of_forms_are_one_problem(value):
    assert refused(DOCUMENT | {"comments": value}) == [COMMENTS]


def test_comments_that_list_no_form_are_refused():
    assert refused(DOCUMENT | {"comments": []}) == ["comments: needs one form at least"]


def test_the_old_key_of_one_comment_marker_is_an_unknown_key():
    assert refused(DOCUMENT | {"comment": "#"}) == [f"unknown key 'comment': use {KEYS_USED}"]
    assert "comments" in KEYS_USED.split(", ") and "comment" not in KEYS_USED.split(", ")


def test_python_writes_one_line_form_and_supplies_comment_doc_exactly():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    checked = PYTHON_LANGUAGE.checked
    assert (checked.comments, checked.comment) == ((CommentForm(LINE, "#"),), "#")
    assert list(document["supplies"])[list(document["supplies"]).index("comment") + 1] == "comment.doc"
    assert Supply("comment.doc", EXACT) in checked.supplies


def test_python_supplies_public_exactly_right_after_comment_doc_and_keeps_its_private_prefix():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    supplies = list(document["supplies"])
    assert supplies[supplies.index("comment.doc") + 1] == "public"
    assert Supply("public", EXACT) in PYTHON_LANGUAGE.checked.supplies
    assert PYTHON_LANGUAGE.checked.private == document["private"] == "_"


@pytest.mark.parametrize("path", TEST_LANGUAGES, ids=lambda path: path.stem)
def test_a_test_only_language_gives_no_private_prefix_its_reader_saying_which_names_are_public(path):
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert "private" not in document and language_of(path.stem, document).checked.private == ""


MAPPING = ("writing: must be a mapping {call, keyword, field, specs}: how a row of a table of cases is written, and "
           "how a call that builds a mock names its spec")
CALL = "writing.call: must be a line holding {callee}"
KEYWORD = "writing.keyword: must be a line holding {callee}, {keyword} and {text}"
FIELD = "writing.field: must be a line holding {field} and {text}"
SPECS_MAPPING = ("writing.specs: must be a mapping {keyword, position, type_argument}: how a call that builds a mock "
                 "names its spec")
SPEC_KEYWORD = "writing.specs.keyword: must be a line holding {callee}, {keyword} and {value}"
SPEC_PLACED = "writing.specs.{key}: must be a line holding {{callee}}, {{before}} and {{value}}"


def test_python_writes_how_a_row_call_and_a_row_id_given_by_a_keyword_are_written_and_a_spec_by_keyword_or_position():
    assert PYTHON_LANGUAGE.checked.writing == Writing(
        call="{callee}(...)", keyword='{callee}(..., {keyword}="{text}")',
        specs=SpecWriting(keyword="{callee}({keyword}={value})", position="{callee}({before}{value})"))


def test_the_typescript_like_test_only_language_writes_a_spec_by_a_type_argument_alone():
    assert BRACE.checked.writing.specs == SpecWriting(type_argument="{callee}<{before}{value}>()")


def test_a_language_whose_file_writes_no_templates_loads_with_empty_ones():
    assert language_of("pascal", DOCUMENT).checked.writing == Writing()


def test_the_templates_a_data_file_writes_are_read_braces_and_all():
    field = '{..., {field}: "{text}"}'
    assert language_of("pascal", DOCUMENT | {"writing": {"field": field}}).checked.writing == Writing(field=field)


@pytest.mark.parametrize("writing, expected", [
    pytest.param("{callee}(...)", [MAPPING], id="a text is no mapping"),
    pytest.param({"row": "x"}, ["writing: unknown key 'row': use call, keyword, field, specs"], id="an unknown key"),
    pytest.param({"row": "x", "cell": "y"}, ["writing: unknown keys 'cell', 'row': use call, keyword, field, specs"],
                 id="two unknown keys are said together"),
    pytest.param({"call": "call()"}, [CALL], id="a call template without its callee"),
    pytest.param({"call": "{callee}\n(...)"}, [CALL], id="a call template over two lines"),
    pytest.param({"call": 3}, [CALL], id="a call template that is no text"),
    pytest.param({"keyword": "{callee}(..., {keyword}=x)"}, [KEYWORD], id="a keyword template without its text"),
    pytest.param({"field": "{text}"}, [FIELD], id="a field template without its field"),
    pytest.param({"specs": "{callee}<{value}>()"}, [SPECS_MAPPING], id="specs that are no mapping"),
    pytest.param({"specs": {"generic": "x"}},
                 ["writing.specs: unknown key 'generic': use keyword, position, type_argument"],
                 id="an unknown key of specs"),
    pytest.param({"specs": {"keyword": "{callee}({value})"}}, [SPEC_KEYWORD], id="a keyword template without its keyword"),
    pytest.param({"specs": {"position": "{callee}({value})"}}, [SPEC_PLACED.format(key="position")],
                 id="a position template without the places before it"),
    pytest.param({"specs": {"type_argument": "{callee}<{before}>()"}}, [SPEC_PLACED.format(key="type_argument")],
                 id="a type argument template without its value"),
    pytest.param({"specs": {"type_argument": "{callee}<\n{before}{value}>()"}}, [SPEC_PLACED.format(key="type_argument")],
                 id="a spec template over two lines"),
])
def test_a_bad_writing_is_refused(writing, expected):
    assert refused(DOCUMENT | {"writing": writing}) == expected


def test_the_spec_templates_a_data_file_writes_are_read_each_under_its_form():
    specs = {"keyword": "{callee}({keyword}: {value})", "position": "{callee}({before}{value})",
             "type_argument": "{callee}<{before}{value}>()"}
    assert language_of("pascal", DOCUMENT | {"writing": {"specs": specs}}).checked.writing == Writing(
        specs=SpecWriting(**specs))


WORKED_MAPPING = ("worked: must be a mapping {subclass, function, defaulted, annotated, returning, keyword_call}: how "
                  "the code of the checks written for the explanation is written")
SUBCLASS = "worked.subclass: must be a line holding {name} and {base}"


def test_python_writes_how_the_checks_written_for_the_explanation_declare_a_class_with_a_base():
    assert PYTHON_LANGUAGE.checked.worked == Worked(
        subclass="class {name}({base}): ...", function="def {name}({parameter}): ...",
        defaulted="def {name}({parameter}={value}): ...", annotated="def {name}({parameter}: {annotation}): ...",
        returning="def {name}() -> {returns}: ...", keyword_call="{callee}({keyword}={value})")


def test_a_language_whose_file_writes_no_worked_templates_loads_with_empty_ones():
    assert language_of("pascal", DOCUMENT).checked.worked == Worked()


@pytest.mark.parametrize("worked, expected", [
    pytest.param("class {name}({base})", [WORKED_MAPPING], id="a text is no mapping"),
    pytest.param({"klass": "x"},
                 ["worked: unknown key 'klass': use subclass, function, defaulted, annotated, returning, keyword_call"],
                 id="an unknown key"),
    pytest.param({"subclass": "class {name}"}, [SUBCLASS], id="a subclass template without its base"),
    pytest.param({"subclass": "class {name}(\n{base})"}, [SUBCLASS], id="a subclass template over two lines"),
    pytest.param({"defaulted": "def {name}({parameter})"},
                 ["worked.defaulted: must be a line holding {name}, {parameter} and {value}"],
                 id="a defaulted template without its value"),
])
def test_a_bad_worked_is_refused(worked, expected):
    assert refused(DOCUMENT | {"worked": worked}) == expected
