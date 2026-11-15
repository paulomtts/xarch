"""The `libraries` and `guards` keys of an architecture file: what each part may import from outside, and which
pre-built checks are in use."""
import pytest

from xarch.modules.spec.domain.architecture_file import GUARDS, parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import CaseTable, ClosedTree, Fakes, NoComments, PackageOnly, ScenarioCoverage, StandIns


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"contract": {}, "service": {}, "store": {}}}},
        "parts": {"contract": {"path": "src/*/contract", "role": "what callers send and get back"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {"service": ["store@own", "contract@own"], "store": []},
        **extra,
    }


def load(document):
    return parse_architecture(document, "layered.yaml", lambda relative: True)


def problems(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        load(document)
    return list(caught.value.problems)


def test_libraries_give_each_part_its_outside_packages_and_an_unlisted_part_none():
    architecture = load(layered(libraries={"store": ["sqlmodel", "sqlalchemy"], "service": []}))
    assert architecture.libraries == {"contract": (), "service": (), "store": ("sqlmodel", "sqlalchemy")}


def test_without_libraries_outside_packages_are_not_checked():
    assert load(layered()).libraries is None


@pytest.mark.parametrize("libraries, problem", [
    ({"nowhere": ["x"]}, "libraries.nowhere: no part named 'nowhere'"),
    ({"store": "sqlmodel"}, "libraries.store: must be a list of top-level import names, such as [sqlmodel]"),
    ({"store": ["sql-model"]}, "libraries.store: 'sql-model' is not a top-level import name, such as sqlmodel"),
    ({"store": ["sqlalchemy.orm"]}, "libraries.store: 'sqlalchemy.orm' is not a top-level import name, such as sqlmodel"),
    ({"store": ["json"]}, "libraries.store: 'json' is in the standard library, which every part may import"),
    ({"store": ["x", "x"]}, "libraries.store: 'x' is listed twice"),
    (["store"], "libraries: must be a mapping of part names to lists of top-level import names"),
])
def test_a_bad_libraries_entry_is_rejected(libraries, problem):
    assert problems(layered(libraries=libraries)) == [f"layered.yaml: {problem}"]


TIERS = [{"name": "wired", "subject": ["service", "contract", "store"], "proves": "a use case", "may_touch": "all",
          "litmus": "Does it run a use case?"}]


COLUMNS = ["given", "when", "then"]
TESTS = {"files": ["test_*.py"], "functions": "test_*"}
TABLE = {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id"}
FILE = "test_{name}.py"


def scenarios(**changes) -> dict:
    return {"results": "contract", "tier": "wired", "suffix": "Result", "columns": COLUMNS, "table": TABLE,
            "file": FILE} | changes


def test_guards_name_the_pre_built_checks_in_use_with_their_parameters():
    outcomes = scenarios(suffix="Outcome", columns=["state", "command", "outcome"])
    document = layered(tiers=TIERS, tests=TESTS, guards={"no-comments": {}, "package-only": ["contract"],
                                                         "scenario-coverage": outcomes})
    assert load(document).guards == (NoComments(), PackageOnly(("contract",)),
                                     ScenarioCoverage("contract", "wired", "Outcome", ("state", "command", "outcome"),
                                                      CaseTable(("pytest", "mark", "parametrize"),
                                                                ("pytest", "param"), "id"), FILE))
    assert load(layered()).guards == ()


def test_the_pre_built_checks_are_known_by_name_with_one_line_each():
    assert list(GUARDS) == ["package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree"]
    assert all(text and "\n" not in text for text in GUARDS.values())


@pytest.mark.parametrize("guards, problem", [
    ({"no-comment": {}}, "guards: unknown guard 'no-comment': use package-only, scenario-coverage, no-comments, "
                         "stand-ins, closed-tree"),
    ({"closed-tree": []}, "guards.closed-tree: takes no parameters: write {}"),
    ({"no-comments": {"x": 1}}, "guards.no-comments: takes no parameters: write {}"),
    (["no-comments"], "guards: must be a mapping of guard names to their parameters, such as {no-comments: {}}"),
    ({"package-only": ["nowhere"]}, "guards.package-only: no part named 'nowhere'"),
    ({"package-only": "contract"}, "guards.package-only: must be a list of part names"),
    ({"package-only": ["contract", "contract"]}, "guards.package-only: 'contract' is listed twice"),
    ({"package-only": []}, "guards.package-only: must be a list of part names"),
    ({"scenario-coverage": []},
     "guards.scenario-coverage: must be a mapping {results, tier, suffix, columns, table, file}: the part holding "
     "the result unions, the tier whose test files hold their tables, how a union's name ends, the three names of a "
     "table's parameters (its state, its command and its result), how the table is written, and the name of a use "
     "case's test file"),
    ({"scenario-coverage": scenarios(results="nowhere", tier="wired", suffix="Result", columns=COLUMNS)},
     "guards.scenario-coverage.results: no part named 'nowhere'"),
    ({"scenario-coverage": scenarios(results="contract", tier="unit", suffix="Result", columns=COLUMNS)},
     "guards.scenario-coverage.tier: no tier named 'unit'"),
    ({"scenario-coverage": scenarios(results="contract", tier="wired", suffix="a b", columns=COLUMNS)},
     "guards.scenario-coverage.suffix: must be the end of a name, such as Result"),
    ({"scenario-coverage": scenarios(results="contract", tier="wired", suffix="Result", columns="given, when")},
     "guards.scenario-coverage.columns: must be a list of three names, such as [given, when, then]"),
    ({"scenario-coverage": scenarios(results="contract", tier="wired", suffix="Result", columns=["a", "b"])},
     "guards.scenario-coverage.columns: must be a list of three names, such as [given, when, then]"),
    ({"scenario-coverage": scenarios(results="contract", tier="wired", suffix="Result", columns=["a", "b", "a"])},
     "guards.scenario-coverage.columns: 'a' is listed twice"),
    ({"scenario-coverage": scenarios(results="contract", tier="wired", suffix="Result", columns=["a", "b c", "d"])},
     "guards.scenario-coverage.columns: 'b c' is not a name a parameter can have"),
])
def test_a_bad_guards_entry_is_rejected(guards, problem):
    assert problems(layered(tiers=TIERS, tests=TESTS, guards=guards)) == [f"layered.yaml: {problem}"]


def test_scenario_coverage_needs_its_tier_to_test_the_results_part():
    tiers = [dict(TIERS[0], subject=["service", "store"]),
             {"name": "api", "subject": ["contract"], "proves": "x", "may_touch": "y", "litmus": "z"}]
    guards = {"scenario-coverage": scenarios(results="contract", tier="wired", suffix="Result", columns=COLUMNS)}
    assert problems(layered(tiers=tiers, tests=TESTS, guards=guards)) == [
        "layered.yaml: guards.scenario-coverage.tier: tier 'wired' does not test part 'contract'"]


def test_scenario_coverage_needs_its_results_part_in_the_each_folder():
    document = layered(tiers=[dict(TIERS[0], subject=["service", "contract", "store", "shared"])], tests=TESTS,
                       guards={"scenario-coverage": scenarios(results="shared")})
    document["layout"]["shared"] = {}
    document["parts"]["shared"] = {"path": "shared", "role": "shared code"}
    assert problems(document) == [
        "layered.yaml: guards.scenario-coverage.results: part 'shared' does not lie in the `each` folder: its unions "
        "are matched to the tests of the same folder"]


def test_the_closed_tree_guard_takes_no_parameters_and_is_listed_in_the_guards_section():
    architecture = load(layered(guards={"closed-tree": {}}))
    assert architecture.guards == (ClosedTree(),)
    assert fill("{{guards}}", architecture, "layered.md").splitlines()[-1] == (
        "- `closed-tree`: every Python file of the app lies in a part, or is the package file (`__init__.py`) of a "
        "folder of the layout.")


def test_fakes_name_their_folder_and_the_parts_they_stand_in_for():
    assert load(layered(fakes={"path": "tests/fakes", "for": ["store"]})).fakes == Fakes(("tests", "fakes"), ("store",))
    assert load(layered()).fakes is None


def test_fakes_may_say_how_a_fake_is_named_and_then_the_stand_ins_guard_applies():
    fakes = {"path": "tests/fakes", "for": ["store"], "prefix": "Fake"}
    stand_ins = {"mocks": ["unittest.mock.Mock"], "spec": ["spec"]}
    architecture = load(layered(tests=TESTS, fakes=fakes, guards={"stand-ins": stand_ins}))
    assert architecture.fakes == Fakes(("tests", "fakes"), ("store",), "Fake")
    assert architecture.guards == (StandIns((("unittest", "mock", "Mock"),), (), ("spec",)),)


@pytest.mark.parametrize("fakes, problem", [
    ({"path": "tests/fakes"}, "fakes: must be a mapping {path, for} and optionally prefix: the folder of the fakes, "
                              "such as tests/fakes, the parts they stand in for, and how a fake's name starts"),
    ({"path": "tests/fakes", "for": ["store"], "suffix": "Fake"},
     "fakes: must be a mapping {path, for} and optionally prefix: the folder of the fakes, such as tests/fakes, the "
     "parts they stand in for, and how a fake's name starts"),
    ({"path": "tests/fakes", "for": ["store"], "prefix": "a fake"},
     "fakes.prefix: must be the start of a class name, such as Fake"),
    ({"path": "fakes", "for": ["store"]}, "fakes.path: must be a folder below the tests root, such as tests/fakes"),
    ({"path": "tests/fakes", "for": ["nowhere"]}, "fakes.for: no part named 'nowhere'"),
    ({"path": "tests/fakes", "for": []}, "fakes.for: must be a list of part names"),
    ({"path": "tests/fakes", "for": ["store"], "prefix": ""}, "fakes.prefix: must be the start of a class name, such as Fake"),
    ({"path": "tests/*/fakes", "for": ["store"]}, "fakes.path: must be a folder below the tests root, such as tests/fakes"),
])
def test_a_bad_fakes_entry_is_rejected(fakes, problem):
    assert problems(layered(fakes=fakes)) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("path", [
    pytest.param("tests", id="the tests root alone names no folder below it"),
    pytest.param("tests/", id="the tests root with a slash names no folder below it"),
    pytest.param("/fakes", id="a leading slash leaves one step, which is no folder below the tests root"),
    pytest.param("tests//fakes", id="an empty step is rejected"),
    pytest.param("tests/../fakes", id="a step climbing out is rejected"),
    pytest.param("tests/./fakes", id="a step that is the folder itself is rejected"),
    pytest.param(3, id="a path that is no text is rejected"),
])
def test_the_fakes_folder_below_the_tests_root_is_never_empty(path):
    assert problems(layered(fakes={"path": path, "for": ["store"]})) == [
        "layered.yaml: fakes.path: must be a folder below the tests root, such as tests/fakes"]


def test_the_guards_placeholder_leaves_out_what_the_architecture_does_not_check():
    text = fill("{{guards}}", load(layered()), "layered.md")
    assert text.splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `src/<name>/`.",
        "- `rules`: every import between parts is one that `rules` allows (architecture.md, section 5).",
        "- `test tree`: every folder below `tests/src/` mirrors a folder of the app.",
        "- `cycles`: no `src/<name>/` imports from another that imports, directly or through others, from it; each "
        "cycle is reported once, with the imports that close it."]
