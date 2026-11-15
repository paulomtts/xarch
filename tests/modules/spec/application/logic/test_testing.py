"""How a profile file names what its test framework names: the `testing` key, and the framework's names the guards
scenario-coverage and stand-ins read from it."""
import pytest

from tests.modules.spec.profiles_v2 import TESTING, covered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.domain.values import Fixture

FILES = {"files": ["test_*.py"], "functions": "test_*"}
TABLE_OK = TESTING["table"]
MOCKS_OK = TESTING["mocks"]
SCENARIOS = {"results": "api", "tier": "integration", "suffix": "Result", "columns": ["given", "when", "then"],
             "file": "test_{name}.py"}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}
PATTERN = ("layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with `*` for "
           "any text")
FUNCTION = "layered.yaml: testing.functions: must be a function name pattern: a name with `*` for any text"
FIXTURES = ("layered.yaml: testing.mocks.fixtures: must be a mapping of parameter names to {calls}, and optionally "
            "autospec: the names of the methods that build a mock, and of those that build one from a spec given as "
            "an argument")
TABLE = ("layered.yaml: testing.table: must be a mapping {decorator, row, id}, and optionally keywords: the dotted "
         "names of the table's decorator and of its row, the keyword of a row's id, and the keywords the decorator's "
         "two arguments may be given by")
KEYWORDS = ("layered.yaml: testing.table.keywords: must be two keyword names, the decorator's names and its rows, "
            "such as [names, rows]")
MOCKS = ("layered.yaml: testing.mocks: must be a mapping {calls, spec_keywords}, and optionally autospec and "
         "fixtures: the dotted names of the calls that build a mock, the keywords a mock is given its spec by, and "
         "the parameters of a test function whose methods build one")
DOTTED = "must be a list of dotted names such as pkg.sub.Name"
METHODS = "must be a list of method names such as [build]"
WRITE = "write testing: <preset>, or testing: {files: [<pattern>, ...], functions: <pattern>}"


def with_testing(**changes) -> dict:
    return covered(testing=TESTING | changes)


def with_table(table) -> dict:
    return with_testing(table=table)


def with_mocks(mocks) -> dict:
    return with_testing(mocks=mocks)


def with_fixtures(fixtures) -> dict:
    return with_mocks(MOCKS_OK | {"fixtures": fixtures})


@pytest.mark.parametrize("testing, expected", [
    pytest.param(FILES | {"files": "test_*.py"}, PATTERN, id="file patterns given as one text are refused"),
    pytest.param(FILES | {"files": ["tests/test_*.py"]},
                 "layered.yaml: testing.files: 'tests/test_*.py' is not a file name pattern: a name ending in .py, "
                 "with `*` for any text", id="a file pattern holding a folder is refused"),
    pytest.param(FILES | {"files": ["test_*"]},
                 "layered.yaml: testing.files: 'test_*' is not a file name pattern: a name ending in .py, with `*` "
                 "for any text", id="a file pattern with no .py ending is refused"),
    pytest.param(FILES | {"functions": ""}, FUNCTION, id="an empty function pattern is refused"),
    pytest.param(FILES | {"functions": "9_*"}, FUNCTION, id="a function pattern starting with a digit is refused"),
    pytest.param(FILES | {"functions": ["test_*"]}, FUNCTION, id="function patterns given as a list are refused"),
])
def test_a_bad_framework_pattern_is_refused(testing, expected):
    assert problems(covered(testing=testing)) == [expected]


def test_the_keywords_of_the_table_decorator_are_optional():
    table = {key: value for key, value in TABLE_OK.items() if key != "keywords"}
    architecture = parsed(with_table(table) | {"guards": {"scenario-coverage": SCENARIOS}})
    assert architecture.guards[0].table.keywords is None


@pytest.mark.parametrize("table, expected", [
    pytest.param([], TABLE, id="a table that is no mapping is refused"),
    pytest.param({key: value for key, value in TABLE_OK.items() if key != "row"},
                 "layered.yaml: testing.table: missing `row`", id="a table with no row is refused"),
    pytest.param(TABLE_OK | {"x": 1}, "layered.yaml: testing.table: unknown key 'x': use decorator, id, keywords, row",
                 id="an unknown key is refused"),
    pytest.param(TABLE_OK | {"id": "a b"}, "layered.yaml: testing.table.id: must be a keyword name",
                 id="an id that is no keyword name is refused"),
    pytest.param(TABLE_OK | {"decorator": "parametrize"},
                 "layered.yaml: testing.table.decorator: 'parametrize' is not a dotted name such as pkg.sub.name",
                 id="a decorator that is not dotted is refused"),
    pytest.param(TABLE_OK | {"row": "pytest..param"},
                 "layered.yaml: testing.table.row: 'pytest..param' is not a dotted name such as pkg.sub.name",
                 id="a row with an empty step is refused"),
    pytest.param(TABLE_OK | {"row": 3}, "layered.yaml: testing.table.row: 3 is not a dotted name such as pkg.sub.name",
                 id="a row that is no text is refused"),
    pytest.param(TABLE_OK | {"keywords": ["argnames"]}, KEYWORDS, id="one keyword is refused"),
    pytest.param(TABLE_OK | {"keywords": ["a", "a"]}, KEYWORDS, id="the same keyword twice is refused"),
])
def test_a_bad_table_entry_is_refused(table, expected):
    assert problems(with_table(table)) == [expected]


def test_the_autospec_names_of_the_mocks_are_optional():
    mocks = {key: value for key, value in MOCKS_OK.items() if key != "autospec"}
    document = with_mocks(mocks) | {"guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].autospec == ()


def test_the_mocks_load_the_fixtures_whose_methods_build_mocks():
    fixtures = {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]},
                "factory": {"calls": ["build"]}}
    document = with_fixtures(fixtures) | {"guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].fixtures == (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),
                                                   Fixture("factory", ("build",)))


def test_the_fixtures_of_the_mocks_are_optional():
    mocks = {key: value for key, value in MOCKS_OK.items() if key != "fixtures"}
    document = with_mocks(mocks) | {"guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].fixtures == ()


@pytest.mark.parametrize("fixtures, expected", [
    pytest.param({}, FIXTURES, id="no fixture at all is refused"),
    pytest.param([], FIXTURES, id="fixtures that are no mapping are refused"),
    pytest.param({"a b": {"calls": ["Mock"]}}, "layered.yaml: testing.mocks.fixtures: 'a b' is not a parameter name",
                 id="a fixture that is no parameter name is refused"),
    pytest.param({"mocker": ["Mock"]},
                 "layered.yaml: testing.mocks.fixtures.mocker: must be a mapping {calls}, and optionally autospec",
                 id="a fixture that is no mapping is refused"),
    pytest.param({"mocker": {}}, "layered.yaml: testing.mocks.fixtures.mocker: missing `calls`",
                 id="a fixture with no calls is refused"),
    pytest.param({"mocker": {"calls": ["Mock"], "x": 1}},
                 "layered.yaml: testing.mocks.fixtures.mocker: unknown key 'x': use autospec, calls",
                 id="an unknown key of a fixture is refused"),
    pytest.param({"mocker": {"calls": []}}, f"layered.yaml: testing.mocks.fixtures.mocker.calls: {METHODS}",
                 id="no calls at all is refused"),
    pytest.param({"mocker": {"calls": "Mock"}}, f"layered.yaml: testing.mocks.fixtures.mocker.calls: {METHODS}",
                 id="calls given as one text are refused"),
    pytest.param({"mocker": {"calls": ["a.b"]}},
                 "layered.yaml: testing.mocks.fixtures.mocker.calls: 'a.b' is not a method name",
                 id="a call that is dotted is refused"),
    pytest.param({"mocker": {"calls": ["Mock", "Mock"]}},
                 "layered.yaml: testing.mocks.fixtures.mocker.calls: 'Mock' is listed twice",
                 id="a call listed twice is refused"),
    pytest.param({"mocker": {"calls": ["Mock"], "autospec": []}},
                 f"layered.yaml: testing.mocks.fixtures.mocker.autospec: {METHODS}",
                 id="no autospec at all is refused"),
    pytest.param({"mocker": {"calls": ["Mock"], "autospec": ["Mock"]}},
                 "layered.yaml: testing.mocks.fixtures.mocker.autospec: 'Mock' is also listed in calls",
                 id="an autospec that is also a call is refused"),
])
def test_a_bad_fixtures_entry_is_refused(fixtures, expected):
    assert problems(with_fixtures(fixtures)) == [expected]


@pytest.mark.parametrize("mocks, expected", [
    pytest.param([], MOCKS, id="mocks that are no mapping are refused"),
    pytest.param({"spec_keywords": ["spec"]}, "layered.yaml: testing.mocks: missing `calls`",
                 id="mocks with no calls are refused"),
    pytest.param({"calls": [MOCKS_OK["calls"][0]]}, "layered.yaml: testing.mocks: missing `spec_keywords`",
                 id="mocks with no spec keywords are refused"),
    pytest.param(MOCKS_OK | {"calls": "unittest.mock.Mock"}, f"layered.yaml: testing.mocks.calls: {DOTTED}",
                 id="calls given as one text are refused"),
    pytest.param(MOCKS_OK | {"calls": ["Mock"]},
                 "layered.yaml: testing.mocks.calls: 'Mock' is not a dotted name such as pkg.sub.name",
                 id="a call that is not dotted is refused"),
    pytest.param(MOCKS_OK | {"calls": ["a.B", "a.B"]}, "layered.yaml: testing.mocks.calls: 'a.B' is listed twice",
                 id="a call listed twice is refused"),
    pytest.param(MOCKS_OK | {"autospec": []}, f"layered.yaml: testing.mocks.autospec: {DOTTED}",
                 id="no autospec at all is refused"),
    pytest.param(MOCKS_OK | {"autospec": ["unittest.mock.Mock"]},
                 "layered.yaml: testing.mocks.autospec: 'unittest.mock.Mock' is also listed in calls",
                 id="an autospec that is also a call is refused"),
    pytest.param(MOCKS_OK | {"spec_keywords": ["spec", "spec"]},
                 "layered.yaml: testing.mocks.spec_keywords: 'spec' is listed twice",
                 id="a spec keyword listed twice is refused"),
    pytest.param(MOCKS_OK | {"spec_keywords": ["a b"]},
                 "layered.yaml: testing.mocks.spec_keywords: 'a b' is not a keyword name",
                 id="a spec keyword that is no keyword name is refused"),
])
def test_a_bad_mocks_entry_is_refused(mocks, expected):
    assert problems(with_mocks(mocks)) == [expected]


def test_mocks_with_neither_calls_nor_spec_keywords_report_each_one_missing():
    assert problems(with_mocks({"autospec": ["unittest.mock.create_autospec"]})) == [
        "layered.yaml: testing.mocks: missing `calls`", "layered.yaml: testing.mocks: missing `spec_keywords`"]


def test_stand_ins_with_fakes_that_name_no_prefix_is_refused():
    fakes = {"folder": "fakes", "for": ["store"]}
    assert problems(covered(guards={"stand-ins": {}}, fakes=fakes)) == [
        "layered.yaml: guards.stand-ins: needs `fakes` with a `prefix`, such as {folder: fakes, for: [<part>], "
        "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and how a fake is named"]


@pytest.mark.parametrize("guards, needs", [
    pytest.param({"scenario-coverage": SCENARIOS}, "`tiers` and `guards.scenario-coverage`",
                 id="scenario-coverage with tiers is named beside them"),
    pytest.param({"stand-ins": {}}, "`tiers` and `guards.stand-ins`", id="stand-ins with tiers is named beside them"),
    pytest.param({"scenario-coverage": SCENARIOS, "stand-ins": {}},
                 "`tiers`, `guards.scenario-coverage` and `guards.stand-ins`", id="both guards are named beside tiers"),
])
def test_a_guard_that_reads_test_files_needs_testing(guards, needs):
    document = covered(guards=guards, fakes=FAKES)
    del document["testing"]
    assert problems(document) == [f"layered.yaml: missing `testing`: {needs} must recognise a test file by its name: "
                                  + WRITE]


def test_the_file_of_the_scenario_guard_is_checked_against_the_testing_patterns_only_when_both_are_valid():
    document = covered(guards={"scenario-coverage": SCENARIOS | {"file": "spec_{name}.py"}},
                       testing={"files": [], "functions": "test_*"})
    assert problems(document) == [PATTERN]


@pytest.mark.parametrize("file, expected", [
    pytest.param("{name}_{name}.py", "must hold `{name}` once, such as a_{name}.py",
                 id="a file holding the name twice is refused"),
    pytest.param("a/{name}.py", "must be a file name below the test folders, such as a_{name}.py",
                 id="a file with a folder is refused"),
    pytest.param("spec_{name}.py", "'spec_{name}.py' is not a name `testing.files` recognises as a test file",
                 id="a file the framework does not recognise as a test file is refused"),
])
def test_a_bad_scenario_file_is_refused(file, expected):
    assert problems(covered(guards={"scenario-coverage": SCENARIOS | {"file": file}})) == [
        f"layered.yaml: guards.scenario-coverage.file: {expected}"]


def guard_lines(**changes) -> list[str]:
    document = covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES)
    document["testing"] = document["testing"] | changes.pop("testing", {})
    document["guards"] = document["guards"] | changes.pop("guards", {})
    return fill("{{guards}}", parsed(document), "layered.md").splitlines()[-2:]


def test_the_guards_lines_say_the_names_of_the_framework_the_file_declares():
    assert guard_lines() == [
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `api/` is the `then` of a row of "
        "the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section 5.2), "
        "or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a table test "
        "has no `if`, `match`, `try`, `for` or `while`.",
        "- `stand-ins`: every `Protocol` in `store/` is fire-only (every method returns `None`) or read (any method "
        "returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` "
        "(or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6)."]


def test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines():
    testing = {"files": ["*_spec.py"], "functions": "it_*",
               "table": {"decorator": "cases.table", "row": "cases.row", "id": "name"},
               "mocks": {"calls": ["doubles.Double"], "spec_keywords": ["of"]}}
    lines = guard_lines(testing=testing, guards={"scenario-coverage": SCENARIOS | {"file": "{name}_spec.py"}})
    assert "in `<name>_spec.py`" in lines[0]
    assert "every row is a `cases.row` with an `name`" in lines[0]
    assert "`Double(of=<Port>)`" in lines[1]


def test_testing_may_name_the_markers_and_calls_that_skip_a_test_or_expect_it_to_fail():
    skips = {"skips": ["pytest.mark.skip", "unittest.skip"]}
    assert parsed(with_testing(**skips)).framework.skips == (("pytest", "mark", "skip"), ("unittest", "skip"))
    assert parsed(covered(testing=FILES)).framework.skips == ()


@pytest.mark.parametrize("skips, expected", [
    pytest.param(["skip"], "'skip' is not a dotted name such as pkg.sub.name", id="a skip that is not dotted is refused"),
    pytest.param([], DOTTED, id="no skip at all is refused"),
    pytest.param(["a.b", "a.b"], "'a.b' is listed twice", id="a skip listed twice is refused"),
])
def test_a_bad_skips_entry_is_refused(skips, expected):
    assert problems(with_testing(skips=skips)) == [f"layered.yaml: testing.skips: {expected}"]
