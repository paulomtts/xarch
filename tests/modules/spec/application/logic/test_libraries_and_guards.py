"""The `libraries` of a part and the `guards` and `fakes` keys of a profile: what a part may import from
outside, which pre-built checks are in use and where the fakes live."""
import pytest

from tests.modules.spec.format_files import CATALOGUE, FILE_TYPES
from tests.modules.spec.languages import BRACE
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.domain.guards import ORDER
from xarch.modules.spec.domain.values import ClosedTree, NoComments, PackageOnly
from xarch.profile_values.testing import CaseTable, ScenarioCoverage

FILE = "test_{name}.py"
SCENARIOS = {"results": "api", "tier": "integration", "suffix": "Result", "columns": ["given", "when", "then"],
             "file": FILE}
FAKES = {"folder": "fakes", "for": ["store"]}


def test_a_part_that_lists_no_package_may_import_none_and_says_so_with_an_empty_list():
    document = layered()
    document["parts"]["store"].setdefault("imports", {})["libraries"] = []
    assert parsed(document).imports_libraries == {"api": (), "service": (), "store": (), "shared": ()}


def test_a_library_name_with_a_dash_is_refused_since_it_is_no_import_name():
    document = layered()
    document["parts"]["store"].setdefault("imports", {})["libraries"] = ["sql-model"]
    assert problems(document) == [
        "layered.yaml: parts.store.imports.libraries: 'sql-model' is not a package name the language Python allows"]


def test_guards_name_the_pre_built_checks_in_use_with_their_parameters_and_package_only_is_a_part_s_fact():
    scenarios = SCENARIOS | {"suffix": "Outcome", "columns": ["state", "command", "outcome"]}
    document = covered(guards={"no-comments": {}, "scenario-coverage": scenarios})
    document["parts"]["api"]["package_only"] = True
    assert parsed(document).guards == (
        PackageOnly(("api",)), NoComments(),
        ScenarioCoverage("api", "integration", "Outcome", ("state", "command", "outcome"),
                         CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id",
                                   ("argnames", "argvalues")), FILE))
    assert parsed(layered()).guards == ()


def test_the_pre_built_checks_are_known_by_name_with_one_line_each():
    assert list(ORDER) == ["package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates",
                             "no-twins", "dead-code", "pass-through", "no-callbacks", "private-imports"]
    texts = [CATALOGUE.texts[f"guards.{name}"].accepts for name in ORDER if name != "package-only"]
    assert all(text and "\n" not in text for text in texts)


@pytest.mark.parametrize("guards, problem", [
    pytest.param({"closed-tree": []}, "guards.closed-tree: takes no parameters: write {}",
                 id="a list where a guard takes no parameters"),
    pytest.param(["no-comments"], "guards: must be a mapping of guard names to their parameters, such as "
                                  "{no-comments: {}}", id="a list of guard names instead of a mapping"),
    pytest.param({"scenario-coverage": []},
                 "guards.scenario-coverage: must be a mapping {results, tier, suffix, columns, file}: the part holding "
                 "the result unions, the tier whose test files hold their tables, how a union's name ends, the three "
                 "names of a table's parameters (its state, its command and its result), and the name of a use "
                 "case's test file", id="scenario-coverage that is no mapping"),
    pytest.param({"scenario-coverage": SCENARIOS | {"columns": "given, when"}},
                 "guards.scenario-coverage.columns: must be a list of three names, such as [given, when, then]",
                 id="columns that are no list"),
    pytest.param({"scenario-coverage": SCENARIOS | {"columns": ["a", "b"]}},
                 "guards.scenario-coverage.columns: must be a list of three names, such as [given, when, then]",
                 id="two columns instead of three"),
    pytest.param({"scenario-coverage": SCENARIOS | {"columns": ["a", "b c", "d"]}},
                 "guards.scenario-coverage.columns: 'b c' is not a name a parameter can have",
                 id="a column that is no parameter name"),
])
def test_a_bad_guards_entry_is_refused_saying_what_to_write(guards, problem):
    assert problems(covered(guards=guards)) == [f"layered.yaml: {problem}"]


def test_the_closed_tree_guard_is_listed_last_in_the_guards_section_of_the_docs():
    architecture = parsed(layered(guards={"closed-tree": {}}))
    assert architecture.guards == (ClosedTree(),)
    assert fill("{{guards}}", architecture, "layered.md", file_types=FILE_TYPES).splitlines()[-1] == (
        "- `closed-tree`: every Python file of the app lies in a part, or is the package file (`__init__.py`) of a "
        "folder of the layout.")


@pytest.mark.parametrize("fakes, problem", [
    pytest.param(FAKES | {"prefix": ""}, "fakes.prefix: must be the start of a class name, such as Fake",
                 id="an empty prefix"),
    pytest.param(FAKES | {"folder": "a//b"},
                 "fakes.folder: must be a folder below the tests folder, such as fakes: relative, with no `..`, no "
                 "empty step and no `*`", id="a folder with an empty step"),
    pytest.param(FAKES | {"folder": "a/./b"},
                 "fakes.folder: must be a folder below the tests folder, such as fakes: relative, with no `..`, no "
                 "empty step and no `*`", id="a folder with a step that is the folder itself"),
    pytest.param(FAKES | {"folder": "/fakes"},
                 "fakes.folder: must be a folder below the tests folder, such as fakes: relative, with no `..`, no "
                 "empty step and no `*`", id="a folder starting with a slash"),
    pytest.param(FAKES | {"folder": 3},
                 "fakes.folder: must be a folder below the tests folder, such as fakes: relative, with no `..`, no "
                 "empty step and no `*`", id="a folder that is no text"),
])
def test_a_bad_fakes_folder_or_prefix_is_refused_saying_what_to_write(fakes, problem):
    assert problems(covered(fakes=fakes)) == [f"layered.yaml: {problem}"]


def test_the_guards_placeholder_leaves_out_what_the_profile_does_not_check():
    text = fill("{{guards}}", parsed(layered()), "layered.md", file_types=FILE_TYPES)
    assert text.splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `src/<name>/`.",
        "- `may-import`: every import between parts is one that the `imports.may` of the importing part allows "
        "(architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`store/`: sqlmodel); the standard "
        "library is always allowed, and tests are not checked.",
        "- `test tree`: every folder below `tests/src/` mirrors a folder of the app.",
        "- `cycles`: no `src/<name>/` imports from another that imports, directly or through others, from it; each "
        "cycle is reported once, with the imports that close it."]


def reserving(reserved, libraries=None) -> dict:
    """The layered profile reserving modules, with the store part's libraries when given."""
    document = layered(reserved=reserved)
    if libraries is not None:
        document["parts"]["store"].setdefault("imports", {})["libraries"] = libraries
    return document


def test_a_reserved_module_of_the_standard_library_loads_with_its_reason_and_a_part_may_list_it():
    architecture = parsed(reserving({"ast": "the reader's", "tokenize": "the reader's"}, ["ast", "tokenize"]))
    assert (architecture.reserved, architecture.imports_libraries["store"]) == (
        {"ast": "the reader's", "tokenize": "the reader's"}, ("ast", "tokenize"))


@pytest.mark.parametrize("reserved, libraries, problem", [
    pytest.param(["ast"], None, "reserved: must be a mapping of standard-library names to why they are reserved, "
                                "such as {ast: only the reader parses the language}", id="a list"),
    pytest.param({"yaml": "x"}, None, "reserved: 'yaml' is not in the Python standard library: an outside package "
                                      "is imported only by the parts whose `imports.libraries` list it already",
                 id="an outside package"),
    pytest.param({"os.path": "x"}, None, "reserved: 'os.path' is not a package name the language Python allows",
                 id="a module below a top-level one"),
    pytest.param({"ast": ""}, None, "reserved.ast: must say in one line why it is reserved", id="no reason"),
    pytest.param({}, ["ast"], "parts.store.imports.libraries: 'ast' is in the standard library, which every part may import "
                              "unless `reserved` names it", id="a standard module listed but not reserved"),
])
def test_a_bad_reserved_module_is_refused_saying_what_to_write(reserved, libraries, problem):
    assert problems(reserving(reserved, libraries)) == [f"layered.yaml: {problem}"]


def test_the_standard_library_a_profile_reserves_from_is_the_one_of_the_language_of_the_app():
    braced = {"brace": BRACE}
    assert parsed(reserving({"fs": "the runtime's"}), languages=braced).reserved == {"fs": "the runtime's"}
    assert problems(reserving({"fs": "the runtime's"})) == [
        "layered.yaml: reserved: 'fs' is not in the Python standard library: an outside package is imported only by the "
        "parts whose `imports.libraries` list it already"]
    assert parsed(reserving({"pickle": "the runtime's"})).reserved == {"pickle": "the runtime's"}
    assert problems(reserving({"pickle": "the runtime's"}), languages=braced) == [
        "layered.yaml: reserved: 'pickle' is not in the Brace standard library: an outside package is imported only by "
        "the parts whose `imports.libraries` list it already"]


def test_the_guards_section_says_which_parts_may_import_a_reserved_module():
    lines = fill("{{guards}}", parsed(reserving({"ast": "the reader's"}, ["ast"])), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[2] == ("- `libraries`: a part imports only the outside packages listed for it (`store/`: ast); the "
                        "standard library is always allowed but what `reserved` names (`ast`: the reader's), "
                        "and tests are not checked.")


@pytest.mark.parametrize("library", [
    pytest.param("lodash-es", id="a package name with a dash"),
    pytest.param("@scope/pkg", id="a scoped package name"),
])
def test_a_library_the_package_pattern_of_the_language_refuses_is_refused_naming_the_language(library):
    document = layered()
    document["parts"]["store"].setdefault("imports", {})["libraries"] = [library]
    assert problems(document) == [
        f"layered.yaml: parts.store.imports.libraries: '{library}' is not a package name the language Python allows"]
