"""How an architecture file names what its test framework names: the top-level `tests` key, and the framework's names in
the guards scenario-coverage and stand-ins."""
import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import CaseTable, Fixture, Framework, ScenarioCoverage, StandIns

TESTS = {"files": ["test_*.py", "*_test.py"], "functions": "test_*"}
TABLE = {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
         "keywords": ["argnames", "argvalues"]}
SCENARIOS = {"results": "contract", "tier": "wired", "suffix": "Result", "columns": ["given", "when", "then"],
             "table": TABLE, "file": "test_{name}.py"}
MOCKS = ["unittest.mock.Mock", "unittest.mock.MagicMock"]
STAND_INS = {"mocks": MOCKS, "autospec": ["unittest.mock.create_autospec"], "spec": ["spec", "spec_set"]}
TIERS = [{"name": "wired", "subject": ["service", "contract", "store"], "proves": "a use case", "may_touch": "all",
          "litmus": "Does it run a use case?"}]


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"contract": {}, "service": {}, "store": {}}}},
        "parts": {"contract": {"path": "src/*/contract", "role": "what callers send and get back"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {},
        **extra,
    }


def load(document):
    return parse_architecture(document, "layered.yaml", lambda relative: True)


def problems(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        load(document)
    return list(caught.value.problems)


def test_tests_name_the_test_files_and_the_test_functions_by_patterns():
    assert load(layered(tests=TESTS)).framework == Framework(("test_*.py", "*_test.py"), "test_*")


def test_a_profile_with_no_tiers_and_no_guard_needing_them_loads_without_tests():
    assert load(layered()).framework is None


@pytest.mark.parametrize("tests, problem", [
    ([], "tests: must be a mapping {files, functions}: the patterns of a test file's name and of a test function's"),
    ({"functions": "test_*"}, "tests: missing `files`"),
    ({"files": ["test_*.py"]}, "tests: missing `functions`"),
    ({**TESTS, "x": 1}, "tests: unknown key 'x': use files, functions, skips"),
    ({**TESTS, "files": []}, "tests.files: must be a non-empty list of file name patterns, each a .py name with `*` for any text"),
    ({**TESTS, "files": "test_*.py"}, "tests.files: must be a non-empty list of file name patterns, each a .py name with `*` for any text"),
    ({**TESTS, "files": ["tests/test_*.py"]},
     "tests.files: 'tests/test_*.py' is not a file name pattern: a name ending in .py, with `*` for any text"),
    ({**TESTS, "files": ["test_*"]},
     "tests.files: 'test_*' is not a file name pattern: a name ending in .py, with `*` for any text"),
    ({**TESTS, "files": ["a_*.py", "a_*.py"]}, "tests.files: 'a_*.py' is listed twice"),
    ({**TESTS, "functions": ""}, "tests.functions: must be a function name pattern: a name with `*` for any text"),
    ({**TESTS, "functions": "a b*"}, "tests.functions: must be a function name pattern: a name with `*` for any text"),
    ({**TESTS, "functions": "9_*"}, "tests.functions: must be a function name pattern: a name with `*` for any text"),
    ({**TESTS, "functions": ["test_*"]}, "tests.functions: must be a function name pattern: a name with `*` for any text"),
])
def test_a_bad_tests_entry_is_rejected(tests, problem):
    assert problems(layered(tests=tests)) == [f"layered.yaml: {problem}"]


def test_tiers_need_tests_to_tell_a_test_file():
    assert problems(layered(tiers=TIERS)) == [
        "layered.yaml: missing `tests`: `tiers` must recognise a test file by its name: add "
        "tests: {files: [<pattern>, ...], functions: <pattern>}"]


def test_the_scenario_coverage_guard_loads_the_names_of_its_framework():
    architecture = load(layered(tiers=TIERS, tests=TESTS, guards={"scenario-coverage": SCENARIOS}))
    assert architecture.guards == (ScenarioCoverage(
        "contract", "wired", "Result", ("given", "when", "then"),
        CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues")),
        "test_{name}.py"),)


def test_the_keywords_of_the_table_decorator_are_optional():
    table = {key: value for key, value in TABLE.items() if key != "keywords"}
    architecture = load(layered(tiers=TIERS, tests=TESTS,
                                guards={"scenario-coverage": {**SCENARIOS, "table": table}}))
    assert architecture.guards[0].table.keywords is None


def test_the_stand_ins_guard_loads_the_names_of_its_framework():
    architecture = load(layered(tiers=TIERS, tests=TESTS, fakes={"path": "tests/fakes", "for": ["store"],
                                                                 "prefix": "Fake"},
                                guards={"stand-ins": STAND_INS}))
    assert architecture.guards == (StandIns((("unittest", "mock", "Mock"), ("unittest", "mock", "MagicMock")),
                                            (("unittest", "mock", "create_autospec"),), ("spec", "spec_set")),)


def test_the_autospec_names_of_the_stand_ins_guard_are_optional():
    architecture = load(layered(tests=TESTS, fakes={"path": "tests/fakes", "for": ["store"], "prefix": "Fake"},
                                guards={"stand-ins": {"mocks": MOCKS, "spec": ["spec"]}}))
    assert architecture.guards[0].autospec == ()


FIXTURES = {"mocker": {"mocks": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}


def test_the_stand_ins_guard_loads_the_fixtures_whose_methods_build_mocks():
    architecture = load(layered(tests=TESTS, fakes=FAKES, guards={"stand-ins": {**STAND_INS, "fixtures": {
        **FIXTURES, "factory": {"mocks": ["build"]}}}}))
    assert architecture.guards[0].fixtures == (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),
                                               Fixture("factory", ("build",)))


def test_the_fixtures_of_the_stand_ins_guard_are_optional():
    assert load(layered(tests=TESTS, fakes=FAKES, guards={"stand-ins": STAND_INS})).guards[0].fixtures == ()


@pytest.mark.parametrize("fixtures, problem", [
    ({}, "guards.stand-ins.fixtures: must be a mapping of parameter names to {mocks}, and optionally autospec: "
         "the names of the methods that build a mock, and of those that build one from a spec given as an argument"),
    ([], "guards.stand-ins.fixtures: must be a mapping of parameter names to {mocks}, and optionally autospec: "
         "the names of the methods that build a mock, and of those that build one from a spec given as an argument"),
    ({"a b": {"mocks": ["Mock"]}}, "guards.stand-ins.fixtures: 'a b' is not a parameter name"),
    ({"mocker": ["Mock"]}, "guards.stand-ins.fixtures.mocker: must be a mapping {mocks}, and optionally autospec"),
    ({"mocker": {}}, "guards.stand-ins.fixtures.mocker: missing `mocks`"),
    ({"mocker": {"mocks": ["Mock"], "x": 1}},
     "guards.stand-ins.fixtures.mocker: unknown key 'x': use autospec, mocks"),
    ({"mocker": {"mocks": []}}, "guards.stand-ins.fixtures.mocker.mocks: must be a list of method names such as "
                                "[build]"),
    ({"mocker": {"mocks": "Mock"}}, "guards.stand-ins.fixtures.mocker.mocks: must be a list of method names such "
                                    "as [build]"),
    ({"mocker": {"mocks": ["a.b"]}}, "guards.stand-ins.fixtures.mocker.mocks: 'a.b' is not a method name"),
    ({"mocker": {"mocks": ["Mock", "Mock"]}}, "guards.stand-ins.fixtures.mocker.mocks: 'Mock' is listed twice"),
    ({"mocker": {"mocks": ["Mock"], "autospec": []}},
     "guards.stand-ins.fixtures.mocker.autospec: must be a list of method names such as [build]"),
    ({"mocker": {"mocks": ["Mock"], "autospec": ["Mock"]}},
     "guards.stand-ins.fixtures.mocker.autospec: 'Mock' is also listed in mocks"),
])
def test_a_bad_fixtures_entry_is_rejected(fixtures, problem):
    assert problems(layered(tests=TESTS, fakes=FAKES, guards={"stand-ins": {**STAND_INS, "fixtures": fixtures}})) == [
        f"layered.yaml: {problem}"]


def scenarios(**changes) -> dict:
    return {"scenario-coverage": {**SCENARIOS, **changes}}


def table(**changes) -> dict:
    return scenarios(table={**TABLE, **changes})


@pytest.mark.parametrize("guards, problem", [
    ({"scenario-coverage": {k: v for k, v in SCENARIOS.items() if k != "table"}},
     "guards.scenario-coverage: missing `table`"),
    ({"scenario-coverage": {k: v for k, v in SCENARIOS.items() if k != "file"}},
     "guards.scenario-coverage: missing `file`"),
    (scenarios(x=1), "guards.scenario-coverage: unknown key 'x': use columns, file, results, suffix, table, tier"),
    (scenarios(file="test.py"), "guards.scenario-coverage.file: must hold `{name}` once, such as a_{name}.py"),
    (scenarios(file="{name}_{name}.py"), "guards.scenario-coverage.file: must hold `{name}` once, such as a_{name}.py"),
    (scenarios(file="a/{name}.py"), "guards.scenario-coverage.file: must be a file name below the test folders, "
                                    "such as a_{name}.py"),
    (scenarios(file="spec_{name}.py"), "guards.scenario-coverage.file: 'spec_{name}.py' is not a name `tests.files` "
                                       "recognises as a test file"),
    (scenarios(table=[]), "guards.scenario-coverage.table: must be a mapping {decorator, row, id}, and optionally "
                          "keywords: the dotted names of the table's decorator and of its row, the keyword of a "
                          "row's id, and the keywords the decorator's two arguments may be given by"),
    (table(id="a b"), "guards.scenario-coverage.table.id: must be a keyword name"),
    (table(decorator="parametrize"), "guards.scenario-coverage.table.decorator: 'parametrize' is not a dotted name "
                                     "such as pkg.sub.name"),
    (table(row="pytest..param"), "guards.scenario-coverage.table.row: 'pytest..param' is not a dotted name such "
                                 "as pkg.sub.name"),
    (table(row=3), "guards.scenario-coverage.table.row: 3 is not a dotted name such as pkg.sub.name"),
    (table(keywords=["argnames"]), "guards.scenario-coverage.table.keywords: must be two keyword names, the "
                                   "decorator's names and its rows, such as [names, rows]"),
    (table(keywords=["a", "a"]), "guards.scenario-coverage.table.keywords: must be two keyword names, the "
                                 "decorator's names and its rows, such as [names, rows]"),
    ({"scenario-coverage": {**SCENARIOS, "table": {k: v for k, v in TABLE.items() if k != "row"}}},
     "guards.scenario-coverage.table: missing `row`"),
    ({"scenario-coverage": {**SCENARIOS, "table": {**TABLE, "x": 1}}},
     "guards.scenario-coverage.table: unknown key 'x': use decorator, id, keywords, row"),
])
def test_a_bad_scenario_coverage_entry_is_rejected(guards, problem):
    assert problems(layered(tiers=TIERS, tests=TESTS, guards=guards)) == [f"layered.yaml: {problem}"]


FAKES = {"path": "tests/fakes", "for": ["store"], "prefix": "Fake"}


@pytest.mark.parametrize("stand_ins, problem", [
    ({"spec": ["spec"]}, "guards.stand-ins: missing `mocks`"),
    ({"mocks": MOCKS}, "guards.stand-ins: missing `spec`"),
    ({"mocks": MOCKS, "spec": ["spec"], "x": 1},
     "guards.stand-ins: unknown key 'x': use autospec, fixtures, mocks, spec"),
    ({"mocks": [], "spec": ["spec"]}, "guards.stand-ins.mocks: must be a list of dotted names such as "
                                      "pkg.sub.Name"),
    ({"mocks": "unittest.mock.Mock", "spec": ["spec"]},
     "guards.stand-ins.mocks: must be a list of dotted names such as pkg.sub.Name"),
    ({"mocks": ["Mock"], "spec": ["spec"]},
     "guards.stand-ins.mocks: 'Mock' is not a dotted name such as pkg.sub.name"),
    ({"mocks": [MOCKS[0], MOCKS[0]], "spec": ["spec"]}, "guards.stand-ins.mocks: 'unittest.mock.Mock' is listed twice"),
    ({"mocks": MOCKS, "autospec": [], "spec": ["spec"]},
     "guards.stand-ins.autospec: must be a list of dotted names such as pkg.sub.Name"),
    ({"mocks": MOCKS, "autospec": [MOCKS[0]], "spec": ["spec"]},
     "guards.stand-ins.autospec: 'unittest.mock.Mock' is also listed in mocks"),
    ({"mocks": MOCKS, "spec": []}, "guards.stand-ins.spec: must be a list of keyword names such as [spec]"),
    ({"mocks": MOCKS, "spec": ["spec", "spec"]}, "guards.stand-ins.spec: 'spec' is listed twice"),
    ({"mocks": MOCKS, "spec": ["a b"]}, "guards.stand-ins.spec: 'a b' is not a keyword name"),
    ([], "guards.stand-ins: must be a mapping {mocks, spec}, and optionally autospec and fixtures: the dotted names "
         "of the calls that build a mock, the keywords a mock is given its spec by, and the parameters of a test "
         "function whose methods build one"),
])
def test_a_bad_stand_ins_entry_is_rejected(stand_ins, problem):
    assert problems(layered(tiers=TIERS, tests=TESTS, fakes=FAKES, guards={"stand-ins": stand_ins})) == [
        f"layered.yaml: {problem}"]


def test_stand_ins_with_no_names_reports_each_one_missing():
    assert problems(layered(tests=TESTS, fakes=FAKES, guards={"stand-ins": {}})) == [
        "layered.yaml: guards.stand-ins: missing `mocks`", "layered.yaml: guards.stand-ins: missing `spec`"]


def test_stand_ins_without_fakes_is_rejected_beside_any_missing_name():
    assert problems(layered(tiers=TIERS, tests=TESTS, guards={"stand-ins": STAND_INS})) == [
        "layered.yaml: guards.stand-ins: needs `fakes` with a `prefix`, such as {path: tests/fakes, for: [<part>], "
        "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and how a fake is named"]


def test_stand_ins_with_fakes_that_name_no_prefix_is_rejected():
    fakes = {"path": "tests/fakes", "for": ["store"]}
    assert problems(layered(tiers=TIERS, tests=TESTS, fakes=fakes, guards={"stand-ins": STAND_INS})) == [
        "layered.yaml: guards.stand-ins: needs `fakes` with a `prefix`, such as {path: tests/fakes, for: [<part>], "
        "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and how a fake is named"]


@pytest.mark.parametrize("guards, needs", [
    ({"scenario-coverage": SCENARIOS}, "`tiers` and `guards.scenario-coverage`"),
    ({"stand-ins": STAND_INS}, "`tiers` and `guards.stand-ins`"),
    ({"scenario-coverage": SCENARIOS, "stand-ins": STAND_INS},
     "`tiers`, `guards.scenario-coverage` and `guards.stand-ins`"),
])
def test_a_guard_that_reads_test_files_needs_tests(guards, needs):
    document = layered(tiers=TIERS, fakes=FAKES, guards=guards)
    assert problems(document) == [f"layered.yaml: missing `tests`: {needs} must recognise a test file by its name: "
                                  "add tests: {files: [<pattern>, ...], functions: <pattern>}"]


def test_the_file_of_the_scenario_guard_is_checked_against_the_tests_patterns_only_when_both_are_valid():
    guards = scenarios(file="spec_{name}.py")
    assert problems(layered(tiers=TIERS, tests={"files": [], "functions": "test_*"}, guards=guards)) == [
        "layered.yaml: tests.files: must be a non-empty list of file name patterns, each a .py name with `*` for any text"]


def guard_lines(**extra) -> list[str]:
    architecture = load(layered(tiers=TIERS, fakes=FAKES, **extra))
    return fill("{{guards}}", architecture, "layered.md").splitlines()[-2:]


def test_the_guards_lines_say_the_names_of_the_framework_the_file_declares():
    lines = guard_lines(tests=TESTS, guards={"scenario-coverage": SCENARIOS, "stand-ins": STAND_INS})
    assert lines == [
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the "
        "`then` of a row of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the wired tests "
        "(section 5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, "
        "and a table test has no `if`, `match`, `try`, `for` or `while`.",
        "- `stand-ins`: every `Protocol` in `store/` is fire-only (every method returns `None`) or read "
        "(any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the wired tests names what it stands in for, `Mock(spec=<Port>)`, never a "
        "read port (section 6)."]


def test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines():
    table = {"decorator": "cases.table", "row": "cases.row", "id": "name"}
    stand_ins = {"mocks": ["doubles.Double"], "spec": ["of"]}
    scenario = {**SCENARIOS, "table": table, "file": "{name}_spec.py"}
    lines = guard_lines(tests={"files": ["*_spec.py"], "functions": "it_*"},
                        guards={"scenario-coverage": scenario, "stand-ins": stand_ins})
    assert "in `{name}_spec.py`".replace("{name}", "<name>") in lines[0]
    assert "every row is a `cases.row` with an `name`" in lines[0]
    assert "`Double(of=<Port>)`" in lines[1]


def test_tests_may_name_the_markers_and_calls_that_skip_a_test_or_expect_it_to_fail():
    tests = {**TESTS, "skips": ["pytest.mark.skip", "unittest.skip"]}
    assert load(layered(tests=tests)).framework.skips == (("pytest", "mark", "skip"), ("unittest", "skip"))
    assert load(layered(tests=TESTS)).framework.skips == ()


@pytest.mark.parametrize("skips, problem", [
    (["skip"], "tests.skips: 'skip' is not a dotted name such as pkg.sub.name"),
    ([], "tests.skips: must be a list of dotted names such as pkg.sub.Name"),
    (["a.b", "a.b"], "tests.skips: 'a.b' is listed twice"),
])
def test_a_bad_skips_entry_is_rejected(skips, problem):
    assert problems(layered(tests={**TESTS, "skips": skips})) == [f"layered.yaml: {problem}"]
