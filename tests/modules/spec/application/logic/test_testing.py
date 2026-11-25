"""How a profile file names what its test framework names: the `testing` key, and the framework's names the guards
scenario-coverage and stand-ins read from it."""
from dataclasses import replace

import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.languages import BRACE, PYTHON, READS_EVERY_FACT
from tests.modules.spec.profiles import PYTEST_FORM, PYTEST_TABLE, TESTING, covered, parsed, part_of, problems
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.application.logic.profile_checks import use_case_file
from xarch.profile_values.language import SpecWriting, Writing
from xarch.profile_values.testing import Fixture, Place, RowId, ScenarioCoverage, SpecEntry, StandIns, TableForm

FILES = {"files": ["test_*.py"], "declared": [{"function": "test_*"}]}
MOCKS_OK = TESTING["mocks"]
SCENARIOS = {"results": "api", "tier": "integration", "suffix": "Result", "columns": ["given", "when", "then"],
             "file": "test_{name:snake}.py"}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}
PATTERN = ("layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with `*` for "
           "any text")
FUNCTION = "layered.yaml: testing.declared.0.function: must be a function name pattern: a name with `*` for any text"
FIXTURES = ("layered.yaml: testing.mocks.fixtures: must be a mapping of parameter names to {calls}, and optionally "
            "autospec: the names of the methods that build a mock, and of those that build one from a spec given as "
            "an argument")
MOCKS = ("layered.yaml: testing.mocks: must be a mapping {calls, specs}, and optionally autospec and fixtures: the "
         "dotted names of the calls that build a mock, the ways a mock is given its spec, in order, and the parameters "
         "of a test function whose methods build one")
SPECS = ("layered.yaml: testing.mocks.specs: must be a list of {keyword}, {position} or {type_argument}: the ways a "
         "call that builds a mock names its spec, in order, such as [{keyword: spec}]")
SPEC_ENTRY = ("layered.yaml: testing.mocks.specs.{index}: must be one of {{keyword: <name>}}, {{position: <n>}} or "
              "{{type_argument: <n>}}")
WHOLE = "layered.yaml: testing.mocks.specs.{index}.{key}: must be a whole number, at least 0, such as 0"
RETIRED = ("layered.yaml: testing.mocks: unknown key '{key}': moved in 0.3.0: write specs: [{{keyword: spec}}, "
           "{{position: 0}}]; use autospec, calls, fixtures, specs")
DOTTED = "must be a list of outside names such as <package>.<name>"
METHODS = "must be a list of method names such as [build]"
WRITE = "write testing: <preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"
BARE = "{name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant"
ONCE = "must hold `{name:<case>}` once, <case> one of snake, kebab, camel, pascal, such as a_{name:snake}"


def with_testing(**changes) -> dict:
    return covered(testing=TESTING | changes)


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
    pytest.param(FILES | {"declared": [{"function": ""}]}, FUNCTION, id="an empty function pattern is refused"),
    pytest.param(FILES | {"declared": [{"function": "9_*"}]}, FUNCTION, id="a function pattern starting with a digit is refused"),
    pytest.param(FILES | {"declared": [{"function": ["test_*"]}]}, FUNCTION, id="function patterns given as a list are refused"),
])
def test_a_bad_framework_pattern_is_refused(testing, expected):
    assert problems(covered(testing=testing)) == [expected]


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


def test_the_mocks_load_the_ways_a_call_names_its_spec_in_the_order_written():
    document = with_mocks(MOCKS_OK) | {"guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].specs == (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"),
                                                SpecEntry(position=0))
    document = with_mocks(MOCKS_OK | {"specs": [{"position": 2}, {"keyword": "spec"}]}) | {
        "guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].specs == (SpecEntry(position=2), SpecEntry(keyword="spec"))


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
    pytest.param({"specs": [{"keyword": "spec"}]}, "layered.yaml: testing.mocks: missing `calls`",
                 id="mocks with no calls are refused"),
    pytest.param({"calls": [MOCKS_OK["calls"][0]]}, "layered.yaml: testing.mocks: missing `specs`",
                 id="mocks with no specs are refused, none being filled in"),
    pytest.param(MOCKS_OK | {"calls": "unittest.mock.Mock"}, f"layered.yaml: testing.mocks.calls: {DOTTED}",
                 id="calls given as one text are refused"),
    pytest.param(MOCKS_OK | {"calls": ["Mock"]},
                 "layered.yaml: testing.mocks.calls: 'Mock' is not an outside name such as <package>.<name>",
                 id="a call that is not dotted is refused"),
    pytest.param(MOCKS_OK | {"calls": ["a.B", "a.B"]}, "layered.yaml: testing.mocks.calls: 'a.B' is listed twice",
                 id="a call listed twice is refused"),
    pytest.param(MOCKS_OK | {"autospec": []}, f"layered.yaml: testing.mocks.autospec: {DOTTED}",
                 id="no autospec at all is refused"),
    pytest.param(MOCKS_OK | {"autospec": ["unittest.mock.Mock"]},
                 "layered.yaml: testing.mocks.autospec: 'unittest.mock.Mock' is also listed in calls",
                 id="an autospec that is also a call is refused"),
    pytest.param(MOCKS_OK | {"specs": []}, SPECS, id="an empty list of specs is refused"),
    pytest.param(MOCKS_OK | {"specs": "spec"}, SPECS, id="specs that are no list are refused"),
    pytest.param(MOCKS_OK | {"specs": {"keyword": "spec"}}, SPECS, id="one entry written as a map, not a list"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"keyword": "spec", "position": 0}]},
                 SPEC_ENTRY.format(index=1), id="an entry with two keys, at its index"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {}]}, SPEC_ENTRY.format(index=1),
                 id="an entry with no key"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"generic": 0}]}, SPEC_ENTRY.format(index=1),
                 id="an entry whose key is none of the three"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, "spec_set"]}, SPEC_ENTRY.format(index=1),
                 id="an entry that is no mapping"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "a b"}]},
                 "layered.yaml: testing.mocks.specs.0.keyword: 'a b' is not a keyword name",
                 id="a keyword that is no keyword name is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": 3}]},
                 "layered.yaml: testing.mocks.specs.0.keyword: 3 is not a keyword name",
                 id="a keyword that is no text is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": -1}]}, WHOLE.format(index=0, key="position"),
                 id="a position below 0 is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": "0"}]}, WHOLE.format(index=0, key="position"),
                 id="a position that is text is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": True}]}, WHOLE.format(index=0, key="position"),
                 id="a position that is true is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"position": 0}, {"keyword": "spec"}]},
                 "layered.yaml: testing.mocks.specs.2: {keyword: spec} is listed twice",
                 id="a keyword entry listed twice is refused at its second index"),
    pytest.param(MOCKS_OK | {"specs": [{"position": 0}, {"position": 0}]},
                 "layered.yaml: testing.mocks.specs.1: {position: 0} is listed twice",
                 id="a position entry listed twice is refused"),
    pytest.param(MOCKS_OK | {"spec_keywords": ["spec"]}, RETIRED.format(key="spec_keywords"),
                 id="spec_keywords is retired with what to write"),
    pytest.param(MOCKS_OK | {"spec_position": 0}, RETIRED.format(key="spec_position"),
                 id="spec_position is retired with what to write"),
    pytest.param(MOCKS_OK | {"colour": 1},
                 "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
                 id="an unknown key is told the keys of mocks"),
])
def test_a_bad_mocks_entry_is_refused(mocks, expected):
    assert problems(with_mocks(mocks)) == [expected]


def test_a_type_argument_place_that_is_no_whole_number_is_refused():
    assert problems(with_mocks(MOCKS_OK | {"specs": [{"type_argument": 1.5}]}),
                    languages={"python": READS_EVERY_FACT}) == [WHOLE.format(index=0, key="type_argument")]


def test_mocks_with_neither_calls_nor_specs_report_each_one_missing():
    assert problems(with_mocks({"autospec": ["unittest.mock.create_autospec"]})) == [
        "layered.yaml: testing.mocks: missing `calls`", "layered.yaml: testing.mocks: missing `specs`"]


def test_both_retired_keys_written_give_one_problem_each_in_sorted_order():
    assert problems(with_mocks(MOCKS_OK | {"spec_position": 0, "spec_keywords": ["spec"]})) == [
        RETIRED.format(key="spec_keywords"), RETIRED.format(key="spec_position")]


def test_the_retired_keys_written_in_place_of_specs_are_refused_beside_the_missing_specs():
    mocks = {"calls": MOCKS_OK["calls"], "spec_keywords": ["spec", "spec_set"], "spec_position": 0}
    assert problems(with_mocks(mocks)) == [RETIRED.format(key="spec_keywords"), RETIRED.format(key="spec_position"),
                                           "layered.yaml: testing.mocks: missing `specs`"]


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
    document = covered(guards={"scenario-coverage": SCENARIOS | {"file": "spec_{name:snake}.py"}},
                       testing={"files": [], "declared": [{"function": "test_*"}]})
    assert problems(document) == [PATTERN]


@pytest.mark.parametrize("file, expected", [
    pytest.param("{name:snake}_{name:snake}.py", f"{ONCE}.py", id="a file holding the name twice is refused"),
    pytest.param("a/{name:snake}.py", "must be a file name below the test folders, such as a_{name:snake}.py",
                 id="a file with a folder is refused"),
    pytest.param("spec_{name:snake}.py", "'spec_{name:snake}.py' is not a name `testing.files` recognises as a test file",
                 id="a file the framework does not recognise as a test file is refused"),
])
def test_a_bad_scenario_file_is_refused(file, expected):
    assert problems(covered(guards={"scenario-coverage": SCENARIOS | {"file": file}})) == [
        f"layered.yaml: guards.scenario-coverage.file: {expected}"]


def guard_lines(**changes) -> list[str]:
    document = covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES)
    document["testing"] = document["testing"] | changes.pop("testing", {})
    document["guards"] = document["guards"] | changes.pop("guards", {})
    return fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()[-2:]


def test_the_guards_lines_say_the_names_of_the_framework_the_file_declares():
    assert guard_lines() == [
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `api/` is the `then` of a row of "
        "the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section 5.2), "
        "or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a table test "
        "has no `if`, `match`, `try`, `for` or `while` statement and no `if` expression.",
        "- `stand-ins`: every `Protocol` in `store/` is fire-only (every method returns `None`) or read (any method "
        "returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` "
        "(or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6)."]


def test_the_stand_ins_line_names_a_fake_by_each_prefix_the_fakes_list():
    document = covered(guards={"stand-ins": {}}, fakes=FAKES | {"prefix": ["InMemory", "Fake"]})
    line = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()[-1]
    assert "every read port `<Port>` has a fake `InMemory<Port>` or `Fake<Port>` in `tests/fakes/`" in line


def test_the_scenario_coverage_line_of_a_framework_with_no_table_form_says_each_result_is_its_own_test():
    guard = {key: value for key, value in SCENARIOS.items() if key != "columns"}
    assert guard_lines(testing={"tables": []}, guards={"scenario-coverage": guard})[0] == (
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `api/` is named by a test of "
        "`test_<name>.py` among the integration tests (section 5.2); the framework writes no table, so each result "
        "is its own test.")


def test_the_stand_ins_line_says_each_annotation_of_no_value_of_the_language():
    architecture = parsed(covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES))
    checked = replace(architecture.language.checked, nothing=("void", "Promise<void>"))
    brace = replace(architecture, language=replace(architecture.language, checked=checked))
    lines = fill("{{guards}}", brace, "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if line.startswith("- `stand-ins`"))
    assert "is fire-only (every method returns `void` or `Promise<void>`) or read" in line


def test_the_stand_ins_line_writes_a_mock_by_the_language_s_template_of_the_first_spec_form():
    architecture = parsed(covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES))
    guards = tuple(replace(guard, specs=(SpecEntry(type_argument=0), SpecEntry(keyword="spec")))
                   if isinstance(guard, StandIns) else guard for guard in architecture.guards)
    writing = Writing(specs=SpecWriting(type_argument="{callee}<{before}{value}>()"))
    typed = replace(architecture, guards=guards, language=replace(
        architecture.language, checked=replace(architecture.language.checked, writing=writing)))
    lines = fill("{{guards}}", typed, "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if line.startswith("- `stand-ins`"))
    assert "names what it stands in for, `Mock<<Port>>()` (or, from a fixture, `mocker.Mock<<Port>>()`)" in line


def test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines():
    testing = {"files": ["*_spec.py"], "declared": [{"function": "it_*"}],
               "tables": [{"decorator": "cases.table", "columns_from": {"position": 0}, "rows": {"position": 1},
                          "row": "cases.row", "id": {"keyword": "name"}}],
               "mocks": {"calls": ["doubles.Double"], "specs": [{"keyword": "of"}]}}
    lines = guard_lines(testing=testing, guards={"scenario-coverage": SCENARIOS | {"file": "{name:snake}_spec.py"}})
    assert "in `<name>_spec.py`" in lines[0]
    assert "every row is a `cases.row` with an `name`" in lines[0]
    assert "`Double(of=<Port>)`" in lines[1]


def test_testing_may_name_the_markers_and_calls_that_skip_a_test_or_expect_it_to_fail():
    skips = {"skips": ["pytest.mark.skip", "unittest.skip"]}
    assert parsed(with_testing(**skips)).framework.skips == (("pytest", "mark", "skip"), ("unittest", "skip"))
    assert parsed(covered(testing=FILES)).framework.skips == ()


@pytest.mark.parametrize("skips, expected", [
    pytest.param(["skip"], "'skip' is not an outside name such as <package>.<name>", id="a skip that is not dotted is refused"),
    pytest.param([], DOTTED, id="no skip at all is refused"),
    pytest.param(["a.b", "a.b"], "'a.b' is listed twice", id="a skip listed twice is refused"),
])
def test_a_bad_skips_entry_is_refused(skips, expected):
    assert problems(with_testing(skips=skips)) == [f"layered.yaml: testing.skips: {expected}"]


def test_a_tier_with_plain_tables_and_a_part_of_immutable_records_each_have_a_line_of_the_guards():
    document = covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES)
    document["tiers"]["unit"]["plain_tables"] = True
    part_of(document, "service")["holds"] = {"functions": {}, "records": {"immutable": True}, "exceptions": {}}
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert ("- `plain tables`: no table test of the unit tests holds a branch in its body: no `if`, `match`, `try`, "
            "`for` or `while` statement and no `if` expression.") in lines
    assert ("- `immutable`: every record of `service/` is an immutable record, as the Python data file marks one; "
            "listed in the enforcement section, and fails `check --strict` only.") in lines


def test_dead_code_s_names_used_only_by_the_tests_are_said_when_they_are_listed():
    document = covered(guards={"dead-code": {"tests_only": True}}, fakes=FAKES)
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if "dead-code" in line)
    assert line.endswith("A public class or function of the app that no other file of the app names, so that only "
                         "the tests use it, or nothing does, is listed in the enforcement section, and fails `check "
                         "--strict` only.")


def test_dead_code_s_names_accepted_as_only_the_tests_are_said_by_their_entries():
    document = covered(guards={"dead-code": {"tests_only": True, "known": ["shared/text.py:clean", "shared/wiring.py:build"]}},
                       fakes=FAKES)
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if "dead-code" in line)
    assert line.endswith("is listed in the enforcement section, and fails `check --strict` only. `shared/text.py:clean` "
                         "and `shared/wiring.py:build` are accepted as only the tests' (`guards.dead-code.known`) and "
                         "named in the enforcement section instead; an entry that no longer holds is listed.")


BRACED = {"python": PYTHON, "brace": BRACE}


def braced(files) -> dict:
    return covered(testing={"files": files, "declared": [{"function": "test*"}]}, language="brace")


def test_under_several_endings_a_file_pattern_may_end_in_any_of_them():
    assert parsed(braced(["*.test.tsx", "*.test.mts", "*.test.ts"]), languages=BRACED).framework.files == (
        "*.test.tsx", "*.test.mts", "*.test.ts")


@pytest.mark.parametrize("files, expected", [
    pytest.param(["*.test.js"], "layered.yaml: testing.files: '*.test.js' is not a file name pattern: a name ending in "
                                ".ts, .tsx or .mts, with `*` for any text", id="an ending the language does not have"),
    pytest.param("*.test.ts", "layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .ts, "
                              ".tsx or .mts name with `*` for any text", id="no list"),
])
def test_under_several_endings_a_refusal_lists_every_ending(files, expected):
    assert problems(braced(files), languages=BRACED) == [expected]


def test_a_file_pattern_may_hold_any_character_but_a_slash():
    assert parsed(covered(testing={"files": ["tést_*.py"], "declared": [{"function": "test_*"}]})).framework.files == ("tést_*.py",)
    assert problems(covered(testing={"files": [".py"], "declared": [{"function": "test_*"}]})) == [
        "layered.yaml: testing.files: '.py' is not a file name pattern: a name ending in .py, with `*` for any text"]


@pytest.mark.parametrize("file, kept, expected", [
    pytest.param("{name:snake}.test.tsx", "{name:snake}.test.tsx", [], id="a file of the second ending"),
    pytest.param("{name:snake}.test.mts", "{name:snake}.test.mts", [], id="a file of the third ending"),
    pytest.param("{name:snake}.test.js", None,
                 ["scenarios: must be a file name below the test folders, such as a_{name:snake}.ts"],
                 id="an ending the language does not have, the refusal printing the first"),
])
def test_under_several_endings_the_scenario_file_may_end_in_any_of_them(file, kept, expected):
    found: list[str] = []
    assert (use_case_file(file, None, "scenarios", found, BRACE), found) == (kept, expected)


@pytest.mark.parametrize("file", [
    pytest.param("test_{name}.py", id="a bare name"),
    pytest.param("test_{name}_{name:snake}.py", id="a bare name beside a cased one gets the one refusal"),
])
def test_a_bare_name_is_refused_with_its_hint(file):
    found: list[str] = []
    assert (use_case_file(file, None, "guards.scenario-coverage.file", found, PYTHON), found) == (
        None, [f"guards.scenario-coverage.file: {file!r}: {BARE}"])


@pytest.mark.parametrize("file", [
    pytest.param("a_{name:snake}.py", id="snake"),
    pytest.param("a_{name:kebab}.py", id="kebab"),
    pytest.param("a_{name:camel}.py", id="camel"),
    pytest.param("a_{name:pascal}.py", id="pascal"),
])
def test_each_case_is_accepted(file):
    found: list[str] = []
    assert (use_case_file(file, None, "scenarios", found, PYTHON), found) == (file, [])


@pytest.mark.parametrize("file", [
    pytest.param("a_x.py", id="no placeholder"),
    pytest.param("{name:snake}_{name:snake}.py", id="two of one case"),
    pytest.param("{name:snake}_{name:kebab}.py", id="two of two cases"),
    pytest.param("a_{name:upper}.py", id="a case that does not exist"),
    pytest.param("a_{name:Snake}.py", id="a case written with a capital"),
    pytest.param("a_{name:}.py", id="no case after the colon"),
    pytest.param("a_{name: snake}.py", id="a blank before the case"),
    pytest.param(3, id="not a string"),
])
def test_a_file_without_one_case_is_refused(file):
    found: list[str] = []
    assert (use_case_file(file, None, "scenarios", found, PYTHON), found) == (None, [f"scenarios: {ONCE}.py"])


@pytest.mark.parametrize("file", [
    pytest.param("test_{name:snake}.py", id="snake"),
    pytest.param("test_{name:kebab}.py", id="kebab"),
    pytest.param("test_{name:camel}.py", id="camel"),
    pytest.param("test_{name:pascal}.py", id="pascal, its name filled with a capital"),
])
def test_a_file_in_any_case_is_checked_against_the_testing_patterns(file):
    kept = parsed(covered(guards={"scenario-coverage": SCENARIOS | {"file": file}})).guards
    assert tuple(guard.file for guard in kept if isinstance(guard, ScenarioCoverage)) == (file,)


@pytest.mark.parametrize("case", [
    pytest.param("snake", id="snake"),
    pytest.param("kebab", id="kebab"),
    pytest.param("camel", id="camel"),
    pytest.param("pascal", id="pascal"),
])
def test_the_guard_line_shows_the_name_as_name_whatever_its_case(case):
    testing = {"files": ["*_spec.py"], "declared": [{"function": "it_*"}]}
    lines = guard_lines(testing=testing, guards={"scenario-coverage": SCENARIOS | {"file": f"{{name:{case}}}_spec.py"}})
    assert "in `<name>_spec.py`" in lines[0]


CALL = {"call": ["checks.each"], "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "checks.case",
        "id": {"keyword": "id"}}
"""A form whose rows a call that makes the test holds."""
DECLARED_EACH = {"call": ["checks.each"], "title": {"position": 0}, "body": {"position": 1}}
"""The declared call form that lists CALL's callee, without which CALL is refused: checks.each declares no test."""
LOOP = {"loop": True, "columns_from": "bound", "row": "literal", "id": {"position": 0}}
"""A form whose rows a loop of the test's body runs, each a literal whose id is its first value."""
FIELD_ROW = {"decorator": "checks.cases", "columns_from": "fields", "rows": {"position": 0}, "row": "literal",
             "id": {"field": "name"}}
"""A form of literal rows whose id is a field."""
POSITIONED = {"decorator": "checks.cases", "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "literal",
              "id": {"position": 0}}
"""A form of literal rows whose id is their first value."""
AT = "layered.yaml: testing.tables.0"
FORMS = ("layered.yaml: testing.tables: must be a list of table forms, each {decorator | call | loop, columns_from, "
         "rows, row, id}")
ENTRY = f"{AT}: must be a mapping with one of decorator, call or loop"
HOLDER = f"{AT}: must have exactly one of decorator, call or loop"
PLACE = "must be {position: <n>, keyword: <name>}, at least one of them, of the holder's arguments"
ROW_ID = f"{AT}.id: must be one of {{keyword: <name>}}, {{field: <name>}} or {{position: <n>}}"
SLOTS = "use call, columns_from, decorator, id, loop, row, rows"
EVERY_FORM = {"python": READS_EVERY_FACT}
"""The languages of a profile whose forms the loader is tested on, Python's reader read as supplying every form."""
TOY = replace(READS_EVERY_FACT, checked=replace(READS_EVERY_FACT.checked, title="Toy",
                                                  writing=Writing(specs=READS_EVERY_FACT.checked.writing.specs)))
"""Python, reading every form, as a language whose data file writes no template of a row: it cannot say a row; it
writes a mock's spec as Python does."""


def with_tables(tables) -> dict:
    return with_testing(tables=tables)


def without(entry: dict, key: str) -> dict:
    return {k: v for k, v in entry.items() if k != key}


def test_the_forms_of_a_table_are_read_each_in_its_slots():
    assert parsed(with_tables([PYTEST_TABLE])).framework.tables == (PYTEST_FORM,)
    assert parsed(with_testing(tables=[CALL, LOOP], declared=[*FILES["declared"], DECLARED_EACH]),
                  languages=EVERY_FORM).framework.tables == (
        TableForm(Place(0), Place(1), ("checks", "case"), RowId(keyword="id"), call=(("checks", "each"),)),
        TableForm("bound", None, (), RowId(position=0), loop=True))


def test_an_empty_list_of_forms_and_a_framework_that_writes_none_have_no_form():
    assert parsed(with_tables([])).framework.tables == ()
    assert parsed(covered(testing=FILES)).framework.tables == ()


@pytest.mark.parametrize("tables, expected", [
    pytest.param(PYTEST_TABLE, FORMS, id="one form written as a map, not a list, is refused"),
    pytest.param(["pytest.mark.parametrize"], ENTRY, id="an entry that is no mapping is refused"),
    pytest.param([None], ENTRY, id="an empty entry is refused"),
    pytest.param([without(PYTEST_TABLE, "decorator")], HOLDER, id="an entry with no holder is refused"),
    pytest.param([PYTEST_TABLE | {"call": ["checks.each"]}], HOLDER, id="an entry with two holders is refused"),
    pytest.param([LOOP | {"loop": 1}], f"{AT}.loop: must be true: the rows are a list a loop of the test's body runs",
                 id="a loop that is not true is refused"),
    pytest.param([without(PYTEST_TABLE, "row")], f"{AT}: missing `row`", id="an entry with no row is refused"),
    pytest.param([without(PYTEST_TABLE, "id")], f"{AT}: missing `id`", id="an entry with no id is refused"),
    pytest.param([without(PYTEST_TABLE, "columns_from")], f"{AT}: missing `columns_from`",
                 id="an entry with no columns_from is refused"),
    pytest.param([without(CALL, "rows")], f"{AT}: missing `rows`", id="a call with no rows is refused"),
    pytest.param([LOOP | {"rows": {"position": 0}}], f"{AT}.rows: a loop runs the rows it iterates: drop rows",
                 id="rows given with a loop are refused"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": -1}}], f"{AT}.rows: {PLACE}", id="a negative position"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": True}}], f"{AT}.rows: {PLACE}",
                 id="a position that is true is no number"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": None}}], f"{AT}.rows: {PLACE}",
                 id="a place with neither"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": None, "keyword": "argvalues"}}], f"{AT}.rows: {PLACE}",
                 id="a position that is null beside a keyword is not read as absent"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": 1, "keyword": None}}], f"{AT}.rows: {PLACE}",
                 id="a keyword that is null beside a position is not read as absent"),
    pytest.param([PYTEST_TABLE | {"rows": {"index": 1}}], f"{AT}.rows: {PLACE}", id="a place with another key"),
    pytest.param([PYTEST_TABLE | {"columns_from": {"keyword": "arg names"}}], f"{AT}.columns_from: {PLACE}",
                 id="a place whose keyword is no name"),
    pytest.param([PYTEST_TABLE | {"columns_from": "names"}],
                 f"{AT}.columns_from: must be {{position, keyword}}, parameters, bound or fields",
                 id="columns_from that is no place and no word of its own"),
    pytest.param([PYTEST_TABLE | {"columns_from": "bound"}],
                 f"{AT}.columns_from: bound is the names a loop binds: write it with loop", id="bound with a decorator"),
    pytest.param([LOOP | {"columns_from": {"position": 0}}],
                 f"{AT}.columns_from: a loop has no arguments: write bound or fields", id="a place with a loop"),
    pytest.param([LOOP | {"columns_from": "parameters"}], f"{AT}.columns_from: a loop's columns are bound or fields",
                 id="parameters with a loop"),
    pytest.param([PYTEST_TABLE | {"columns_from": "fields"}], f"{AT}.columns_from: fields needs row: literal",
                 id="fields with a dotted row"),
    pytest.param([PYTEST_TABLE | {"row": "param"}], f"{AT}.row: 'param' is not an outside name such as <package>.<name>",
                 id="a row that is neither dotted nor literal"),
    pytest.param([PYTEST_TABLE | {"decorator": "parametrize"}],
                 f"{AT}.decorator: 'parametrize' is not an outside name such as <package>.<name>",
                 id="a decorator that is not dotted"),
    pytest.param([CALL | {"call": []}], f"{AT}.call: must be a list of outside names such as <package>.<name>",
                 id="an empty list of calls"),
    pytest.param([PYTEST_TABLE | {"id": "id"}], ROW_ID, id="an id written as a bare keyword, as the old table map wrote it"),
    pytest.param([PYTEST_TABLE | {"id": {"keyword": "id", "field": "id"}}], ROW_ID, id="an id of two kinds"),
    pytest.param([PYTEST_TABLE | {"id": {"position": -1}}], ROW_ID, id="an id at a negative position"),
    pytest.param([PYTEST_TABLE | {"row": "literal"}],
                 f"{AT}.id: {{keyword}} names a keyword of a row call: write a dotted row", id="a keyword id of a literal row"),
    pytest.param([PYTEST_TABLE | {"id": {"field": "name"}}],
                 f"{AT}.id: {{field}} names a field of a literal row: write row: literal", id="a field id of a row call"),
    pytest.param([PYTEST_TABLE | {"x": 1}], f"{AT}: unknown key 'x': {SLOTS}", id="an unknown key"),
    pytest.param([PYTEST_TABLE, PYTEST_TABLE | {"x": 1}], f"layered.yaml: testing.tables.1: unknown key 'x': {SLOTS}",
                 id="an entry is addressed by its index from 0"),
    pytest.param([FIELD_ROW], f"{AT}.id: the language Python does not write `writing.field`, how a row's id is given "
                              "by a field", id="a field id under a language that writes no field"),
])
def test_a_bad_table_form_is_refused(tables, expected):
    assert problems(with_tables(tables), languages=EVERY_FORM) == [expected]


def test_a_language_that_writes_no_template_cannot_say_a_row_call_nor_its_keyword_id():
    assert problems(with_tables([PYTEST_TABLE]), languages={"python": TOY}) == [
        f"{AT}.row: the language Toy does not write `writing.call`, how a row call is named",
        f"{AT}.id: the language Toy does not write `writing.keyword`, how a row's id is given by a keyword"]


def test_an_id_by_position_needs_no_template():
    assert parsed(with_tables([POSITIONED, LOOP]), languages={"python": TOY}).framework.tables == (
        TableForm(Place(0), Place(1), (), RowId(position=0), decorator=("checks", "cases")),
        TableForm("bound", None, (), RowId(position=0), loop=True))


OTHER_FORM = {"decorator": "checks.cases", "columns_from": {"position": 0}, "rows": {"position": 1},
              "row": "checks.case", "id": {"keyword": "name"}}


@pytest.mark.parametrize("tables, clause", [
    pytest.param([POSITIONED], "every row is a literal with its id at position 0, and a table test",
                 id="a literal row whose id is its first value"),
    pytest.param([OTHER_FORM | {"id": {"position": 2}}], "every row is a `checks.case` with its id at position 2, and",
                 id="a row call whose id is its third value"),
    pytest.param([PYTEST_TABLE, OTHER_FORM],
                 "every row is a `pytest.param` with an `id` or a `checks.case` with an `name`, and",
                 id="two forms, said in the order written"),
])
def test_the_guard_line_says_a_row_as_each_form_writes_one(tables, clause):
    assert clause in guard_lines(testing={"tables": tables})[0]


def guards_text(fakes: dict) -> list[str]:
    """The lines of the guards section of covered() with stand-ins and the fakes given."""
    document = covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=fakes)
    return fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()


def test_the_tiers_fakes_tiers_lists_are_said_among_those_that_import_the_fakes_and_have_their_mocks_held():
    lines = guards_text(FAKES | {"tiers": ["unit"]})
    tiers = next(line for line in lines if line.startswith("- `tiers`"))
    stand_ins = next(line for line in lines if line.startswith("- `stand-ins`"))
    assert "; only a test whose tier tests `store/`, or a unit test, imports the fakes in `tests/fakes/`;" in tiers
    assert "and every mock in the unit and integration tests names what it stands in for" in stand_ins


def test_without_fakes_tiers_the_lines_are_those_of_the_fakes_alone():
    lines = guards_text(FAKES)
    tiers = next(line for line in lines if line.startswith("- `tiers`"))
    assert "; only a test whose tier tests `store/` imports the fakes in `tests/fakes/`;" in tiers
    assert guards_text(FAKES | {"tiers": ["integration"]}) == lines
