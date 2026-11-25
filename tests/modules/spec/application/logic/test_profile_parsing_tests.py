"""A profile file: the test framework (a preset or the map), the tiers and which part each covers, the
fakes, and the guards."""
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import EX, PRESETS, PYTEST_FORM, TESTING, covered, layered, parsed, problems
from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    NoCallbacks,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    Subject,
    Tier,
    TierExample,
)
from xarch.profile_values.language import Writing
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import (
    Fakes,
    Fixture,
    Framework,
    Place,
    RowId,
    ScenarioCoverage,
    SpecEntry,
    StandIns,
    TableForm,
)
from xarch.profile_values.testing import TestForm as DeclaredForm

SPECS = ("must be a list of {keyword}, {position} or {type_argument}: the ways a call that builds a mock names its spec, "
         "in order, such as [{keyword: spec}]")
"""What the loader says of a `testing.mocks.specs` that is no list of entries."""
PRESET_PROBLEM = ("layered.yaml: testing: must be a preset name or a mapping {files, declared}: the patterns of a "
                  "test file's name and the forms that declare a test")
BY_NAME = [{"function": "test_*"}]
"""The one form that declares a test by its function's name, as an entry of `testing.declared`."""


def test_the_framework_is_a_preset_by_name_or_the_map_written_out():
    named = parsed(covered(testing="pytest"))
    written = parsed(covered())
    assert named.framework == written.framework == Framework(
        ("test_*.py", "*_test.py"), (DeclaredForm(function="test_*"),), (("pytest", "mark", "skip"), ("pytest", "skip")),
        (PYTEST_FORM,))


def test_a_preset_is_the_same_map_validated_like_one_written_in_the_file():
    broken = {"files": ["test_*.py"], "declared": [{"function": 3}]}
    assert problems(covered(testing="odd"), presets={"odd": broken}) == [
        "layered.yaml: testing.declared.0.function: must be a function name pattern: a name with `*` for any text"]


@pytest.mark.parametrize("testing, presets, expected", [
    pytest.param("rspec", PRESETS, ["layered.yaml: testing: no preset 'rspec': use pytest, or write the map "
                                    "{files, declared}"], id="a preset that does not exist"),
    pytest.param("rspec", {}, ["layered.yaml: testing: no preset 'rspec': write the map {files, declared}"],
                 id="no preset at all"),
    pytest.param(3, PRESETS, [PRESET_PROBLEM], id="not a name or a map"),
    pytest.param({"declared": BY_NAME}, PRESETS, ["layered.yaml: testing: missing `files`"], id="no files"),
    pytest.param({"files": ["test_*.py"]}, PRESETS, ["layered.yaml: testing: missing `declared`"], id="no declared"),
    pytest.param({"files": ["test_*.py"], "declared": BY_NAME, "colour": 1}, PRESETS,
                 ["layered.yaml: testing: unknown key 'colour': use beside, declared, files, globals, mocks, preset, skips, "
                  "tables"],
                 id="an unknown key"),
    pytest.param({"files": ["x"], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: 'x' is not a file name pattern: a name ending in .py, with `*` for any "
                  "text"], id="a file pattern that is no .py name"),
    pytest.param({"files": [], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with "
                  "`*` for any text"], id="no file patterns"),
    pytest.param({"files": ["a.py", "a.py"], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: 'a.py' is listed twice"], id="a pattern twice"),
    pytest.param({"files": ["a.py"], "declared": [{"function": "a b"}]}, PRESETS,
                 ["layered.yaml: testing.declared.0.function: must be a function name pattern: a name with `*` for any "
                  "text"], id="a function pattern with a space"),
    pytest.param({"files": ["a.py"], "declared": [{"function": "t_*"}], "skips": ["skip"]}, PRESETS,
                 ["layered.yaml: testing.skips: 'skip' is not an outside name such as <package>.<name>"], id="a skip that is not dotted"),
])
def test_a_bad_testing_key_is_refused(testing, presets, expected):
    assert problems(covered(testing=testing), presets=presets) == expected


def test_a_map_that_names_a_preset_is_the_preset_by_name():
    named, mapped = parsed(covered(testing="pytest")), parsed(covered(testing={"preset": "pytest"}))
    assert mapped.framework == named.framework
    assert mapped == named


BESIDE = "drop it, or drop preset and write the whole map"
NO_RSPEC = "layered.yaml: testing.preset: no preset 'rspec': use pytest, or write the map {files, declared}"
NOT_A_NAME = "layered.yaml: testing.preset: must be a preset name: use pytest, or write the map {files, declared}"
UNKNOWN_COLOUR = "layered.yaml: testing: unknown key 'colour': use beside, declared, files, globals, mocks, preset, skips, tables"
CHECK_FILES = ["check_*.py"]


@pytest.mark.parametrize("testing, presets, expected", [
    pytest.param({"preset": "rspec"}, PRESETS, [NO_RSPEC], id="a preset that does not exist"),
    pytest.param({"preset": "rspec"}, {}, ["layered.yaml: testing.preset: no preset 'rspec': write the map "
                                           "{files, declared}"], id="no preset at all"),
    pytest.param({"preset": ""}, PRESETS, ["layered.yaml: testing.preset: no preset '': use pytest, or write the map "
                                           "{files, declared}"], id="an empty name"),
    pytest.param({"preset": 3}, PRESETS, [NOT_A_NAME], id="a number"),
    pytest.param({"preset": ["pytest"]}, PRESETS, [NOT_A_NAME], id="a list"),
    pytest.param({"preset": {"name": "pytest"}}, PRESETS, [NOT_A_NAME], id="a map"),
    pytest.param({"preset": True}, PRESETS, [NOT_A_NAME], id="true"),
    pytest.param({"preset": None}, PRESETS, [NOT_A_NAME], id="null"),
    pytest.param({"preset": 3}, {}, ["layered.yaml: testing.preset: must be a preset name: write the map "
                                     "{files, declared}"], id="no name, and no preset at all"),
    pytest.param({"preset": "pytest", "files": CHECK_FILES}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}"], id="files beside it"),
    pytest.param({"preset": "pytest", "declared": [{"function": "check_*"}]}, PRESETS,
                 [f"layered.yaml: testing.declared: the preset pytest gives declared: {BESIDE}"],
                 id="declared beside it"),
    pytest.param({"preset": "pytest", "mocks": {"calls": ["unittest.mock.Mock"], "specs": [{"keyword": "spec"}]}}, PRESETS,
                 [f"layered.yaml: testing.mocks: the preset pytest gives mocks: {BESIDE}"], id="mocks beside it"),
    pytest.param({"preset": "pytest", "skips": None}, PRESETS,
                 [f"layered.yaml: testing.skips: the preset pytest gives skips: {BESIDE}"],
                 id="a key beside it written null"),
    pytest.param({"preset": "pytest", "files": "broken"}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}"],
                 id="a broken value beside it is not parsed"),
    pytest.param({"preset": "pytest", "globals": ["x"]}, PRESETS,
                 [f"layered.yaml: testing.globals: the preset pytest writes no globals: {BESIDE}"],
                 id="a key the preset does not hold"),
    pytest.param({"preset": "pytest", "declared": BY_NAME, "files": CHECK_FILES}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}",
                  f"layered.yaml: testing.declared: the preset pytest gives declared: {BESIDE}"],
                 id="two keys beside it, in the order of the table"),
    pytest.param({"preset": "rspec", "files": CHECK_FILES}, PRESETS,
                 [NO_RSPEC, f"layered.yaml: testing.files: written beside preset: {BESIDE}"],
                 id="a key beside a preset that does not exist"),
    pytest.param({"preset": "pytest", "colour": 1}, PRESETS, [UNKNOWN_COLOUR], id="an unknown key beside it"),
    pytest.param({"files": CHECK_FILES, "preset": 3, "colour": 1}, PRESETS,
                 [UNKNOWN_COLOUR, NOT_A_NAME, f"layered.yaml: testing.files: written beside preset: {BESIDE}"],
                 id="every problem, in order"),
])
def test_a_map_that_names_a_preset_holds_nothing_else(testing, presets, expected):
    assert problems(covered(testing=testing), presets=presets) == expected


def test_a_preset_may_not_name_a_preset_whichever_form_names_it():
    presets = {"old": {"preset": "pytest", "files": ["test_*.py"], "declared": BY_NAME}} | PRESETS
    expected = ["layered.yaml: testing.preset: the preset old names a preset: a preset writes the whole framework"]
    assert problems(covered(testing="old"), presets=presets) == expected
    assert problems(covered(testing={"preset": "old"}), presets=presets) == expected


def test_a_test_declared_by_a_function_form_is_its_name_pattern():
    document = covered(testing={"files": ["test_*.py"], "declared": BY_NAME})
    assert parsed(document).framework == Framework(("test_*.py",), (DeclaredForm(function="test_*"),))


BRACED = {"python": PYTHON, "brace": BRACE}
"""Brace beside Python: Brace's data file says nothing of its reader, so no form is refused there for a fact."""
CALL_FORM = {"call": ["it"], "title": {"position": 0}, "body": {"position": 1}}
"""A call form whose one callee is a name the framework binds without an import."""
TS_FILES = {"files": ["*.test.ts"]}
"""The file pattern of a test file of Brace."""


def declaring(declared, **more) -> dict:
    """covered() in Brace, its test files *.test.ts and its tests declared by the forms given."""
    return covered(testing=TS_FILES | {"declared": declared} | more, language="brace")


def test_a_test_declared_by_a_call_form_is_its_callees_title_and_body_and_globals_are_names_bound_without_an_import():
    framework = parsed(declaring([CALL_FORM], globals=["it", "expect"]), languages=BRACED).framework
    assert framework == Framework(("*.test.ts",), (DeclaredForm(call=(("it",),), title=Place(0), body=Place(1)),),
                                  globals=(("it",), ("expect",)))


def test_globals_left_out_are_none():
    assert parsed(declaring([CALL_FORM]), languages=BRACED).framework.globals == ()


DECLARED_AT = "layered.yaml: testing.declared"
NOT_A_LIST = f"{DECLARED_AT}: must be a non-empty list of test forms, each {{function}} or {{call, title, body}}"


@pytest.mark.parametrize("testing, expected", [
    pytest.param(TS_FILES, "layered.yaml: testing: missing `declared`", id="no declared"),
    pytest.param(TS_FILES | {"declared": []}, NOT_A_LIST, id="an empty list"),
    pytest.param(TS_FILES | {"declared": "test*"}, NOT_A_LIST, id="a pattern that is no list"),
    pytest.param(TS_FILES | {"declared": [CALL_FORM | {"function": "test*"}]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry with both holders"),
    pytest.param(TS_FILES | {"declared": [{"title": {"position": 0}}]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry with no holder"),
    pytest.param(TS_FILES | {"declared": [None]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry that is no mapping"),
    pytest.param(TS_FILES | {"declared": [{"function": "a b"}]},
                 f"{DECLARED_AT}.0.function: must be a function name pattern: a name with `*` for any text",
                 id="a bad function pattern"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*", "title": {"position": 0}}]},
                 f"{DECLARED_AT}.0.title: a function form takes no slot: drop title", id="a function form with a title"),
    pytest.param(TS_FILES | {"declared": [{"call": ["it"], "body": {"position": 1}}]}, f"{DECLARED_AT}.0: missing `title`",
                 id="a call form with no title"),
    pytest.param(TS_FILES | {"declared": [{"call": ["it"], "title": {"position": 0}}]}, f"{DECLARED_AT}.0: missing `body`",
                 id="a call form with no body"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*"}, CALL_FORM | {"call": []}]},
                 f"{DECLARED_AT}.1.call: must list at least one callee", id="a call form with no callee, at its index"),
    pytest.param(TS_FILES | {"declared": [CALL_FORM | {"title": {"position": -1}}]},
                 f"{DECLARED_AT}.0.title: must be {{position: <n>, keyword: <name>}}, at least one of them, of the "
                 "holder's arguments", id="a bad title place"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*", "colour": 1}]},
                 f"{DECLARED_AT}.0: unknown key 'colour': use body, call, function, title", id="an unknown key of an entry"),
])
def test_a_bad_declared_is_refused(testing, expected):
    assert problems(covered(testing=testing, language="brace"), languages=BRACED) == [expected]


def test_the_table_of_cases_and_the_mocks_are_checked_with_the_framework_whether_or_not_a_guard_uses_them():
    document = covered()
    document["testing"]["tables"] = [{"decorator": "x", "row": "y.z", "columns_from": {"position": 0},
                                      "rows": {"position": 1}}]
    document["testing"]["mocks"] = {"calls": [], "autospec": ["a.b"], "specs": [], "fixtures": {}, "colour": 1}
    assert problems(document) == [
        "layered.yaml: testing.tables.0: missing `id`",
        "layered.yaml: testing.tables.0.decorator: 'x' is not an outside name such as <package>.<name>",
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
        "layered.yaml: testing.mocks.calls: must be a list of outside names such as <package>.<name>",
        f"layered.yaml: testing.mocks.specs: {SPECS}",
        "layered.yaml: testing.mocks.fixtures: must be a mapping of parameter names to {calls}, and optionally "
        "autospec: the names of the methods that build a mock, and of those that build one from a spec given as an "
        "argument"]


def test_a_fixture_names_its_methods_by_calls_and_autospec():
    document = covered()
    document["testing"]["mocks"]["fixtures"] = {"mocker": {"calls": ["Mock"], "autospec": ["Mock"]}, "x": {"mocks": ["a"]}}
    assert problems(document) == [
        "layered.yaml: testing.mocks.fixtures.mocker.autospec: 'Mock' is also listed in calls",
        "layered.yaml: testing.mocks.fixtures.x: unknown key 'mocks': use autospec, calls",
        "layered.yaml: testing.mocks.fixtures.x: missing `calls`"]


def test_tiers_load_in_order_with_what_each_part_says_and_their_litmus_lines_kept():
    architecture = parsed(covered())
    assert architecture.tiers == (
        Tier("unit", (Subject("service"),), "a rule", "", "Does it decide?\nIf yes, it is a unit test."),
        Tier("integration", (Subject("api"), Subject("store")), "a request", "", "Does it need the database?"),
    )
    assert architecture.parts["shared"].untested == "reached through the parts that use it"


def test_the_subject_of_a_tier_is_its_parts_in_the_order_of_the_parts():
    document = covered()
    document["parts"] = {name: document["parts"][name] for name in ("store", "shared", "service", "api")}
    assert [t.subject for t in parsed(document).tiers] == [(Subject("service"),), (Subject("store"), Subject("api"))]


def test_a_tier_may_hold_nothing_and_a_profile_with_no_tiers_needs_no_tier_on_a_part():
    document = covered()
    document["tiers"]["empty"] = {}
    assert parsed(document).tiers[2] == Tier("empty", (), "", "", "")
    assert parsed(layered()).tiers == ()


def test_what_only_fills_the_docs_sits_under_docs_and_loads_into_the_same_fields_as_before():
    example, helper = "tests/src/billing/service/test_rules.py", "tests/src/billing/builders.py"
    document = covered(docs={"examples": ["ex"], "example_notes": {example: "one per rule"}})
    document["tiers"]["unit"]["docs"] = {
        "subject": "the services", "may_touch": "nothing", "one_file_per": "rule", "cases_from": "the invariants",
        "data": "built in the test", "example": example, "helpers": [helper]}
    assert parsed(document, folders=EX).tiers[0] == Tier(
        "unit", (Subject("service"),), "a rule", "nothing", "Does it decide?\nIf yes, it is a unit test.",
        "the services", "rule", "the invariants", "built in the test",
        TierExample(("tests", "src", "billing", "service", "test_rules.py"), "ex/" + example, "one per rule"),
        (TierExample(("tests", "src", "billing", "builders.py"), "ex/" + helper),))


def test_the_tests_of_a_tier_are_held_to_forbidden_and_may_use_parts_as_types_only_when_it_says_so():
    document = covered(never={"pure": ["socket"]})
    document["parts"]["service"]["uses"] = {"never": "pure"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    document["tiers"]["integration"]["imports"] = {"types_only": ["service", "store"]}
    tiers = parsed(document).tiers
    assert [(t.apply_never, t.imports_types_only) for t in tiers] == [(True, ()), (False, ("service", "store"))]


def test_a_tier_with_a_folder_of_its_own_says_what_its_tests_may_import_there():
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture", "imports": {"may": ["shared", "api@any"]}}
    tier = parsed(document).tiers[2]
    assert (tier.folder, tier.subject, tier.imports_may) == (("architecture",), (), (Target("shared"), Target("api", "any")))


def test_what_the_tests_of_a_tier_may_also_import_are_targets_a_bare_name_in_the_repeating_folder_the_mirrored_one():
    document = covered()
    document["tiers"]["integration"]["imports"] = {"also": ["service", "shared", "api@any"]}
    tiers = parsed(document).tiers
    assert [t.imports_also for t in tiers] == [(), (Target("service", "own"), Target("shared"), Target("api", "any"))]


def test_a_tier_with_a_folder_and_no_may_import_may_import_nothing_and_everything_is_allowed_too():
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture"}
    assert parsed(document).tiers[2].imports_may == ()
    document["tiers"]["guard"]["imports"] = {"may": "everything"}
    assert parsed(document).tiers[2].imports_may == (Target("*"),)


def test_tiers_that_is_no_mapping_is_refused_and_the_parts_are_not_blamed_for_it():
    assert problems(covered(tiers=3)) == [
        "layered.yaml: tiers: must be a mapping of tier names to {proves, litmus, ...}, in the order their litmus tests run"]


def test_a_tier_name_is_one_line_of_text_and_a_tier_is_a_mapping():
    document = covered()
    document["tiers"] |= {3: {}, "other": 3}
    assert problems(document) == [
        "layered.yaml: tiers: 3 is not a tier name: one line of text",
        "layered.yaml: tiers.other: must be a mapping, {} if it takes nothing"]


@pytest.mark.parametrize("tier, expected", [
    pytest.param({"colour": 1}, "layered.yaml: tiers.unit: unknown key 'colour': use docs, folder, imports, "
                                "litmus, plain_tables, proves, uses", id="an unknown key"),
    pytest.param({"plain_tables": "yes"}, "layered.yaml: tiers.unit.plain_tables: must be true or false: whether "
                                          "every table test of the tier holds no branch in its body",
                 id="plain_tables that is no boolean"),
    pytest.param({"proves": "a\nb"}, "layered.yaml: tiers.unit.proves: must be one line of text", id="proves of two lines"),
    pytest.param({"litmus": 3}, "layered.yaml: tiers.unit.litmus: must be text: the question that tells a test "
                                "belongs to the tier", id="a litmus that is no text"),
    pytest.param({"uses": {"apply_never": "yes"}}, "layered.yaml: tiers.unit.uses.apply_never: must be true or false: "
                                                   "whether its tests are held to the `uses.never` list of the part "
                                                   "they mirror", id="apply_never that is no boolean"),
    pytest.param({"imports": {"types_only": ["repo"]}}, "layered.yaml: tiers.unit.imports.types_only: no part named "
                                                        "'repo'", id="types_only of no part"),
    pytest.param({"imports": {"may": ["shared"]}}, "layered.yaml: tiers.unit.imports.may: only a tier with a "
                                                   "`folder` has an allowance of its own: without one, its tests "
                                                   "import what the part they mirror may", id="may without a folder"),
    pytest.param({"imports": {"also": "everything"}}, "layered.yaml: tiers.unit.imports.also: must be a list of "
                                                      "targets such as [<part>, shared/text, api@any]: `everything` "
                                                      "is not taken, name each target the tests may also import",
                 id="also of everything"),
    pytest.param({"imports": {"also": ["shared", "everything"]}}, "layered.yaml: tiers.unit.imports.also: "
                                                                  "`everything` is not taken, name each target the "
                                                                  "tests may also import",
                 id="everything in a list of also"),
    pytest.param({"imports": {"also": ["repo"]}}, "layered.yaml: tiers.unit.imports.also: 'repo' names no part "
                                                  "'repo'", id="also of no part"),
    pytest.param({"imports": {"also": ["service@own"]}}, "layered.yaml: tiers.unit.imports.also: 'service@own' says "
                                                         "what a bare name already says: write service",
                 id="also of the mirrored instance written out"),
])
def test_a_bad_tier_is_refused(tier, expected):
    document = covered()
    document["tiers"]["unit"] |= tier
    assert problems(document) == [expected]


def test_a_tier_folder_follows_the_rules_it_had_and_its_allowance_is_a_part_s_may_import():
    document = covered()
    document["tiers"]["guard"] = {"folder": "src/billing/api", "imports": {"may": ["api", "service@own", "repo", "shared/"]}}
    assert problems(document) == [
        "layered.yaml: tiers.guard.folder: 'src/billing/api' is the folder of part 'api', which places its tests: give "
        "`folder` only to a folder that mirrors no part",
        "layered.yaml: tiers.guard.imports.may: 'api' lies in the repeating folder, which a tier's folder is not in: "
        "say api@any",
        "layered.yaml: tiers.guard.imports.may: 'service@own' lies in the repeating folder, which a tier's folder is "
        "not in: say service@any",
        "layered.yaml: tiers.guard.imports.may: 'repo' names no part 'repo'",
        "layered.yaml: tiers.guard.imports.may: 'shared/' has an invalid path after the part"]


def test_the_folders_of_two_tiers_or_a_tier_and_the_fakes_may_not_overlap():
    document = covered(fakes={"folder": "checks/fakes", "for": ["service"]})
    document["tiers"]["guard"] = {"folder": "checks"}
    document["tiers"]["other"] = {"folder": "checks/x"}
    assert problems(document) == [
        "layered.yaml: tiers: the folder 'checks' of tier 'guard' overlaps the fakes' folder 'checks/fakes': give each "
        "its own folder",
        "layered.yaml: tiers: the folder 'checks/x' of tier 'other' overlaps the folder 'checks' of tier 'guard': give "
        "each its own folder"]


def test_the_example_of_a_tier_with_a_folder_may_lie_in_it():
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["guard"] = {"folder": "checks", "docs": {"example": "tests/checks/rules/test_x.py"}}
    assert parsed(document, folders=EX).tiers[2].example == TierExample(
        ("tests", "checks", "rules", "test_x.py"), "ex/tests/checks/rules/test_x.py")


@pytest.mark.parametrize("example", ["tests/other/test_x.py", "test_x.py", "tests/test_x.py"])
def test_the_example_of_a_tier_with_a_folder_may_not_lie_outside_it(example):
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["guard"] = {"folder": "checks", "docs": {"example": example}}
    assert problems(document, folders={"ex": (example,)}) == [
        f"layered.yaml: tiers.guard.docs.example: '{example}' is not inside the tier's folder 'checks' below the "
        "tests folder: the docs would show a place `check` places in no tier"]


def test_a_bad_docs_of_a_tier_is_refused_with_the_address_of_each_key():
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["unit"]["docs"] = {"may_touch": "a\nb", "colour": 1, "example": 3, "helpers": ["x/../y.py", 4],
                                         "data": 3}
    assert problems(document, folders=EX) == [
        "layered.yaml: tiers.unit.docs: unknown key 'colour': use cases_from, data, example, helpers, may_touch, "
        "one_file_per, subject",
        "layered.yaml: tiers.unit.docs.may_touch: must be one line of text",
        "layered.yaml: tiers.unit.docs.data: must be one line of text",
        "layered.yaml: tiers.unit.docs.example: must be a path in an example project, such as src/billing/charge.py",
        "layered.yaml: tiers.unit.docs.helpers[0]: must be a path in an example project, such as src/billing/charge.py",
        "layered.yaml: tiers.unit.docs.helpers[1]: must be a path in an example project, such as src/billing/charge.py"]


def test_the_example_and_helpers_of_a_tier_must_be_files_of_an_example_project():
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["unit"]["docs"] = {"example": "tests/x.py", "helpers": ["tests/y.py"]}
    assert problems(document, folders=EX) == [
        "layered.yaml: tiers.unit.docs.example: no file 'tests/x.py' in any folder of docs.examples",
        "layered.yaml: tiers.unit.docs.helpers[0]: no file 'tests/y.py' in any folder of docs.examples"]
    document = covered()
    document["tiers"]["unit"]["docs"] = {"example": "tests/x.py"}
    assert problems(document) == [
        "layered.yaml: tiers.unit.docs.example: no file 'tests/x.py' in any folder of docs.examples"]


def test_a_part_names_its_tier_or_says_why_it_has_none_when_the_profile_has_tiers():
    document = covered()
    document["parts"]["shared"].pop("untested")
    document["parts"]["store"].pop("tests")
    document["parts"]["api"]["untested"] = "no need"
    document["parts"]["service"]["tests"] = "nope"
    assert problems(document) == [
        "layered.yaml: parts.api: has `tests` and is `untested`: drop one",
        "layered.yaml: parts.service.tests: no tier named 'nope': use unit, integration",
        "layered.yaml: parts.store: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`",
        "layered.yaml: parts.shared: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"]


def test_a_part_naming_a_tier_in_a_profile_with_no_tiers_is_refused():
    document = layered()
    document["parts"]["api"]["tests"] = "unit"
    assert problems(document) == [
        "layered.yaml: parts.api.tests: the profile has no `tiers`: add them, or drop the key"]


def test_a_part_that_is_not_a_text_for_its_tier_is_refused():
    document = covered()
    document["parts"]["api"]["tests"] = 3
    assert problems(document) == ["layered.yaml: parts.api.tests: must be the name of a tier: use unit, integration"]


PART_KEYS = ("folders, holds, imports, litmus, package_only, path, role, shared, tests, untested, uses")
RETIRED_TIER = f"unknown key 'tier': renamed in 0.3.0: write tests; use {PART_KEYS}"
NO_TIER = "no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"


def test_a_part_still_writing_tier_is_refused_with_the_rename_and_is_tested_by_no_tier():
    document = covered()
    document["parts"]["store"].pop("tests")
    document["parts"]["store"]["tier"] = "integration"
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}", f"layered.yaml: parts.store: {NO_TIER}"]


def test_a_part_writing_tier_beside_tests_is_refused_for_tier_alone():
    document = covered()
    document["parts"]["store"]["tier"] = "integration"
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}"]


def test_a_part_writing_tier_and_a_key_only_unknown_gets_the_retired_problem_first():
    document = covered()
    document["parts"]["store"]["tier"] = "integration"
    document["parts"]["store"]["tierr"] = 1
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}",
                                  f"layered.yaml: parts.store: unknown key 'tierr': use {PART_KEYS}"]


def test_the_value_written_under_tier_is_in_no_problem():
    document = covered()
    document["parts"]["store"].pop("tests")
    document["parts"]["store"]["tier"] = "secret-value"
    found = problems(document)
    assert found == [f"layered.yaml: parts.store: {RETIRED_TIER}", f"layered.yaml: parts.store: {NO_TIER}"]
    assert not any("secret-value" in problem for problem in found)


def test_a_part_writing_tier_in_a_profile_with_no_tiers_gets_the_retired_problem_alone():
    document = layered()
    document["parts"]["api"]["tier"] = "unit"
    assert problems(document) == [f"layered.yaml: parts.api: {RETIRED_TIER}"]


def test_tier_under_a_tier_is_only_unknown_with_the_plain_message():
    document = covered()
    document["tiers"]["unit"]["tier"] = "x"
    assert problems(document) == [
        "layered.yaml: tiers.unit: unknown key 'tier': use docs, folder, imports, litmus, plain_tables, proves, uses"]


def test_a_path_written_for_tests_is_told_it_names_a_tier_not_a_folder():
    document = covered()
    document["parts"]["api"]["tests"] = "tests/units"
    assert problems(document) == [
        "layered.yaml: parts.api.tests: no tier named 'tests/units': it names a tier of `tiers`, not a folder: "
        "use unit, integration"]


FOLDER = ": it names a tier of `tiers`, not a folder"


@pytest.mark.parametrize("value, clause", [
    pytest.param("tests/units", FOLDER, id="a folder of the tests"),
    pytest.param("a/b", FOLDER, id="any text holding a slash"),
    pytest.param("unit/", FOLDER, id="a tier name with a trailing slash"),
    pytest.param("units", "", id="no slash: the plain message"),
    pytest.param("tests", "", id="the tests folder's name, with no slash"),
    pytest.param("tests\\units", "", id="a backslash is no slash"),
])
def test_a_value_of_tests_that_is_no_tier_name(value, clause):
    document = covered()
    document["parts"]["api"]["tests"] = value
    assert problems(document) == [
        f"layered.yaml: parts.api.tests: no tier named {value!r}{clause}: use unit, integration"]


def test_a_tier_whose_name_holds_a_slash_is_named_by_tests_with_no_problem():
    document = covered()
    document["tiers"]["a/b"] = {}
    document["parts"]["api"]["tests"] = "a/b"
    architecture = parsed(document)
    assert [subject.part for tier in architecture.tiers if tier.name == "a/b" for subject in tier.subject] == ["api"]


@pytest.mark.parametrize("value", [
    pytest.param(None, id="null"),
    pytest.param(["tests/units"], id="a list holding a path"),
])
def test_a_value_of_tests_that_is_no_string_must_be_the_name_of_a_tier(value):
    document = covered()
    document["parts"]["api"]["tests"] = value
    assert problems(document) == ["layered.yaml: parts.api.tests: must be the name of a tier: use unit, integration"]


def test_tiers_need_the_framework_to_tell_a_test_from_a_helper():
    document = covered()
    del document["testing"]
    assert problems(document) == ["layered.yaml: missing `testing`: `tiers` must recognise a test file by its name: "
                                  "write testing: <preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]


def test_fakes_name_their_folder_below_the_tests_folder_the_parts_they_stand_in_for_and_how_a_fake_is_named():
    architecture = parsed(covered(fakes={"folder": "fakes", "for": ["store"], "prefix": "Fake"}))
    assert architecture.fakes == Fakes(("fakes",), ("store",), "Fake")
    assert parsed(covered(fakes={"folder": "support/fakes", "for": ["store"]})).fakes == Fakes(
        ("support", "fakes"), ("store",))


@pytest.mark.parametrize("fakes, expected", [
    pytest.param(3, "layered.yaml: fakes: must be a mapping {folder, for} and optionally prefix: the folder of the "
                    "fakes below the tests folder, the parts they stand in for, and how a fake's name starts"),
    pytest.param({"for": ["store"]}, "layered.yaml: fakes: missing `folder`"),
    pytest.param({"folder": "fakes"}, "layered.yaml: fakes: missing `for`"),
    pytest.param({"folder": "fakes", "for": ["store"], "colour": 1},
                 "layered.yaml: fakes: unknown key 'colour': use folder, for, prefix"),
    pytest.param({"folder": "../fakes", "for": ["store"]},
                 "layered.yaml: fakes.folder: must be a folder below the tests folder, such as fakes: relative, with "
                 "no `..`, no empty step and no `*`"),
    pytest.param({"folder": "", "for": ["store"]},
                 "layered.yaml: fakes.folder: must be a folder below the tests folder, such as fakes: relative, with "
                 "no `..`, no empty step and no `*`"),
    pytest.param({"folder": "a/*/b", "for": ["store"]},
                 "layered.yaml: fakes.folder: must be a folder below the tests folder, such as fakes: relative, with "
                 "no `..`, no empty step and no `*`"),
    pytest.param({"folder": "fakes", "for": ["repo"]}, "layered.yaml: fakes.for: no part named 'repo'"),
    pytest.param({"folder": "fakes", "for": []}, "layered.yaml: fakes.for: must be a list of part names"),
    pytest.param({"folder": "fakes", "for": ["store"], "prefix": "a b"},
                 "layered.yaml: fakes.prefix: must be the start of a class name, such as Fake"),
])
def test_bad_fakes_are_refused(fakes, expected):
    assert problems(covered(fakes=fakes)) == [expected]


GUARDS = {
    "scenario-coverage": {"results": "api", "tier": "integration", "suffix": "Result",
                          "columns": ["given", "when", "then"], "file": "test_{name:snake}.py"},
    "stand-ins": {}, "no-comments": {}, "closed-tree": {},
}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}


def test_the_guards_in_use_are_those_named_with_the_framework_s_words_taken_from_testing():
    architecture = parsed(covered(guards=GUARDS, fakes=FAKES))
    assert architecture.guards == (
        ScenarioCoverage("api", "integration", "Result", ("given", "when", "then"), "test_{name:snake}.py"),
        StandIns((("unittest", "mock", "Mock"), ("unittest", "mock", "MagicMock")),
                 (("unittest", "mock", "create_autospec"),),
                 (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"), SpecEntry(position=0)),
                 (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),)),
        NoComments(), ClosedTree())


def test_guards_are_off_unless_named_and_package_only_comes_first():
    document = covered(guards={"no-comments": {}})
    document["parts"]["store"]["package_only"] = True
    assert parsed(document).guards == (PackageOnly(("store",)), NoComments())
    assert parsed(covered()).guards == ()


@pytest.mark.parametrize("guards, expected", [
    pytest.param(3, ["layered.yaml: guards: must be a mapping of guard names to their parameters, such as "
                     "{no-comments: {}}"], id="not a mapping"),
    pytest.param({"colour": {}}, ["layered.yaml: guards: unknown guard 'colour': use closed-tree, dead-code, "
                                  "no-callbacks, no-comments, no-duplicates, no-twins, pass-through, private-imports, "
                                  "scenario-coverage, stand-ins"],
                 id="an unknown guard"),
    pytest.param({"package-only": ["api"]}, ["layered.yaml: guards.package-only: a fact about a part: write "
                                             "`package_only: true` on each part"], id="package-only moved to the parts"),
    pytest.param({"no-comments": {"x": 1}}, ["layered.yaml: guards.no-comments: takes no parameters: write {}"],
                 id="a parameter where none is taken"),
    pytest.param({"closed-tree": True}, ["layered.yaml: guards.closed-tree: takes no parameters: write {}"],
                 id="a value that is no mapping"),
    pytest.param({"stand-ins": {"x": 1}}, ["layered.yaml: guards.stand-ins: takes no parameters: write {}"],
                 id="stand-ins takes none now: its names are the framework's"),
])
def test_a_bad_guard_is_refused(guards, expected):
    assert problems(covered(guards=guards, fakes=FAKES)) == expected


def test_the_new_guards_take_their_parameters_and_dead_code_needs_fakes():
    document = covered(guards={"no-duplicates": {"min_statements": 6}, "dead-code": {},
                               "pass-through": {"parts": ["service", "api"]}}, fakes=FAKES)
    assert parsed(document).guards == (NoDuplicates(6), DeadCode(), PassThrough(("service", "api")))
    assert parsed(covered(guards={"no-duplicates": {}})).guards == (NoDuplicates(4),)
    assert parsed(covered(guards={"no-twins": {"min_fields": 5}})).guards == (NoTwins(5),)
    assert parsed(covered(guards={"no-twins": {}})).guards == (NoTwins(3),)
    assert parsed(covered(guards={"no-twins": {"min_renamed": 4, "min_subset": 3}})).guards == (NoTwins(3, 4, 3),)
    assert parsed(covered(guards={"no-twins": {"translated": ["store", "api"]}})).guards == (
        NoTwins(translated=("store", "api")),)


def test_no_callbacks_takes_the_parts_it_reads_in_the_order_written():
    assert parsed(covered(guards={"no-callbacks": {"parts": ["service", "api"]}})).guards == (
        NoCallbacks(("service", "api")),)
    assert parsed(covered(guards={"pass-through": {"parts": ["api"]}, "no-callbacks": {"parts": ["service"]}})).guards \
        == (PassThrough(("api",)), NoCallbacks(("service",)))


@pytest.mark.parametrize("guards, expected", [
    pytest.param({"no-duplicates": 3}, ["layered.yaml: guards.no-duplicates: must be a mapping "
                                        "{min_statements: <number>}, or {} for the default"], id="no-duplicates, no map"),
    pytest.param({"no-duplicates": {"min": 3}}, ["layered.yaml: guards.no-duplicates: unknown key 'min': use "
                                                 "min_statements"], id="no-duplicates, an unknown key"),
    pytest.param({"no-duplicates": {"min_statements": 0}},
                 ["layered.yaml: guards.no-duplicates.min_statements: must be a whole number of statements, at least "
                  "1, such as 4"], id="no-duplicates, zero"),
    pytest.param({"no-twins": [3]}, ["layered.yaml: guards.no-twins: must be a mapping {min_fields: <number>, "
                                     "min_renamed: <number>, min_subset: <number>, translated: [<part>, ...]}, or {} "
                                     "for the default"],
                 id="no-twins, no map"),
    pytest.param({"no-twins": {"min_renamed": 1, "min_subset": "3"}},
                 ["layered.yaml: guards.no-twins.min_renamed: must be a whole number of fields, at least 2, such as 3; "
                  "leave it out to switch this case off",
                  "layered.yaml: guards.no-twins.min_subset: must be a whole number of fields, at least 2, such as 3; "
                  "leave it out to switch this case off"], id="no-twins, a case's minimum below two or no number"),
    pytest.param({"no-twins": {"fields": 3}}, ["layered.yaml: guards.no-twins: unknown key 'fields': use min_fields, "
                                               "min_renamed, min_subset, translated"],
                 id="no-twins, an unknown key"),
    pytest.param({"no-twins": {"translated": ["adapters", "store", "store"]}},
                 ["layered.yaml: guards.no-twins.translated: no part named 'adapters'",
                  "layered.yaml: guards.no-twins.translated: 'store' is listed twice"],
                 id="no-twins, translated names no part or one twice"),
    pytest.param({"no-twins": {"translated": "store"}},
                 ["layered.yaml: guards.no-twins.translated: must be a list of part names"],
                 id="no-twins, translated no list"),
    pytest.param({"no-twins": {"min_fields": 0}}, ["layered.yaml: guards.no-twins.min_fields: must be a whole number "
                                                   "of fields, at least 1, such as 3"], id="no-twins, zero"),
    pytest.param({"no-duplicates": {"min_statements": True}},
                 ["layered.yaml: guards.no-duplicates.min_statements: must be a whole number of statements, at least "
                  "1, such as 4"], id="no-duplicates, a boolean"),
    pytest.param({"dead-code": {"x": 1}}, ["layered.yaml: guards.dead-code: unknown key 'x': use known, tests_only, untested"],
                 id="dead-code, a parameter"),
    pytest.param({"pass-through": {}}, ["layered.yaml: guards.pass-through: missing `parts`"],
                 id="pass-through, no parts"),
    pytest.param({"pass-through": []}, ["layered.yaml: guards.pass-through: must be a mapping {parts: [<part>, ...]}: "
                                        "the parts whose methods are listed when they only forward"],
                 id="pass-through, no map"),
    pytest.param({"pass-through": {"parts": ["ghost"]}}, ["layered.yaml: guards.pass-through.parts: no part named "
                                                          "'ghost'"], id="pass-through, a part that is not there"),
    pytest.param({"no-callbacks": []}, ["layered.yaml: guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: "
                                        "the parts whose functions call none of their parameters annotated as callables"],
                 id="no-callbacks, no map"),
    pytest.param({"no-callbacks": None}, ["layered.yaml: guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: "
                                          "the parts whose functions call none of their parameters annotated as "
                                          "callables"],
                 id="no-callbacks, no value"),
    pytest.param({"no-callbacks": {}}, ["layered.yaml: guards.no-callbacks: missing `parts`"],
                 id="no-callbacks, no parts"),
    pytest.param({"no-callbacks": {"parts": []}}, ["layered.yaml: guards.no-callbacks.parts: must be a list of part "
                                                   "names"], id="no-callbacks, an empty list"),
    pytest.param({"no-callbacks": {"parts": "service"}}, ["layered.yaml: guards.no-callbacks.parts: must be a list of "
                                                          "part names"], id="no-callbacks, a name and no list"),
    pytest.param({"no-callbacks": {"parts": ["ghost"]}}, ["layered.yaml: guards.no-callbacks.parts: no part named "
                                                          "'ghost'"], id="no-callbacks, a part that is not there"),
    pytest.param({"no-callbacks": {"parts": ["service", "service"]}},
                 ["layered.yaml: guards.no-callbacks.parts: 'service' is listed twice"], id="no-callbacks, a part twice"),
    pytest.param({"no-callbacks": {"parts": ["service"], "also": 1}},
                 ["layered.yaml: guards.no-callbacks: unknown key 'also': use parts"], id="no-callbacks, an unknown key"),
])
def test_a_bad_new_guard_is_refused(guards, expected):
    assert problems(covered(guards=guards, fakes=FAKES)) == expected


def test_dead_code_without_fakes_is_refused():
    assert problems(covered(guards={"dead-code": {}})) == [
        "layered.yaml: guards.dead-code: needs `fakes`: it reads the Protocols of the parts `fakes.for` names and the "
        "classes in `fakes.folder`"]


DROP_COLUMNS = ("layered.yaml: guards.scenario-coverage.columns: drop `columns`: the framework writes no table, so "
                "each result is its own test")
NO_COLUMNS = {key: value for key, value in GUARDS["scenario-coverage"].items() if key != "columns"}


def no_form(document: dict, tables: str) -> dict:
    if tables == "absent":
        del document["testing"]["tables"]
    else:
        document["testing"]["tables"] = []
    return document


@pytest.mark.parametrize("tables", ["absent", "empty"])
def test_scenario_coverage_under_a_framework_with_no_table_form_takes_no_columns(tables):
    document = no_form(covered(guards={"scenario-coverage": NO_COLUMNS}), tables)
    assert parsed(document).guards == (ScenarioCoverage("api", "integration", "Result", (), "test_{name:snake}.py"),)


def test_scenario_coverage_under_a_preset_with_no_table_form_takes_no_columns():
    presets = {"pytest": {"files": ["test_*.py"], "declared": BY_NAME}}
    document = covered(testing="pytest", guards={"scenario-coverage": NO_COLUMNS})
    assert parsed(document, presets=presets).guards == (
        ScenarioCoverage("api", "integration", "Result", (), "test_{name:snake}.py"),)


@pytest.mark.parametrize("columns", [["given", "when", "then"], "anything", None])
@pytest.mark.parametrize("tables", ["absent", "empty"])
def test_scenario_coverage_under_a_framework_with_no_table_form_refuses_columns(tables, columns):
    document = no_form(covered(guards={"scenario-coverage": NO_COLUMNS | {"columns": columns}}), tables)
    assert problems(document) == [DROP_COLUMNS]


def test_scenario_coverage_under_a_framework_with_a_table_form_still_needs_columns():
    assert problems(covered(guards={"scenario-coverage": NO_COLUMNS})) == [
        "layered.yaml: guards.scenario-coverage: missing `columns`"]


def test_scenario_coverage_under_a_framework_with_no_table_form_needs_every_other_key():
    guard = {key: value for key, value in NO_COLUMNS.items() if key != "file"}
    assert problems(no_form(covered(guards={"scenario-coverage": guard}), "empty")) == [
        "layered.yaml: guards.scenario-coverage: missing `file`"]
    assert problems(no_form(covered(guards={"scenario-coverage": {}}), "absent")) == [
        "layered.yaml: guards.scenario-coverage: missing `file`",
        "layered.yaml: guards.scenario-coverage: missing `results`",
        "layered.yaml: guards.scenario-coverage: missing `suffix`",
        "layered.yaml: guards.scenario-coverage: missing `tier`"]


def test_scenario_coverage_with_a_refused_framework_still_lists_columns_as_missing():
    document = covered(testing="odd", guards={"scenario-coverage": NO_COLUMNS})
    assert problems(document) == [
        "layered.yaml: testing: no preset 'odd': use pytest, or write the map {files, declared}",
        "layered.yaml: guards.scenario-coverage: missing `columns`"]


SCENARIOS = "layered.yaml: guards.scenario-coverage"


@pytest.mark.parametrize("change, expected", [
    pytest.param({"results": "repo"}, [f"{SCENARIOS}.results: no part named 'repo'"]),
    pytest.param({"results": "shared"}, [
        f"{SCENARIOS}.results: part 'shared' does not lie in the repeating folder: its unions are matched to the tests "
        "of the same folder",
        f"{SCENARIOS}.tier: tier 'integration' does not test part 'shared'"]),
    pytest.param({"tier": "nope"}, [f"{SCENARIOS}.tier: no tier named 'nope'"]),
    pytest.param({"tier": "unit"}, [f"{SCENARIOS}.tier: tier 'unit' does not test part 'api'"]),
    pytest.param({"suffix": "a b"}, [f"{SCENARIOS}.suffix: must be the end of a name, such as Result"]),
    pytest.param({"columns": ["a", "a", "b"]}, [f"{SCENARIOS}.columns: 'a' is listed twice"]),
    pytest.param({"file": "test.py"}, [
        f"{SCENARIOS}.file: must hold `{{name:<case>}}` once, <case> one of snake, kebab, camel, pascal, such as "
        "a_{name:snake}.py"]),
    pytest.param({"file": "{name:snake}.rb"}, [
        f"{SCENARIOS}.file: must be a file name below the test folders, such as a_{{name:snake}}.py"]),
    pytest.param({"file": "{name:snake}.py"}, [
        f"{SCENARIOS}.file: '{{name:snake}}.py' is not a name `testing.files` recognises as a test file"]),
    pytest.param({"file": "test_{name}.py"}, [
        f"{SCENARIOS}.file: 'test_{{name}}.py': {{name}} with no case was removed in 0.3.0: write {{name:snake}} for "
        "what {name} meant"]),
    pytest.param({"colour": 1}, [f"{SCENARIOS}: unknown key 'colour': use columns, file, results, suffix, tier"]),
])
def test_a_bad_scenario_coverage_is_refused(change, expected):
    guard = GUARDS["scenario-coverage"] | change
    assert problems(covered(guards={"scenario-coverage": guard})) == expected


def test_scenario_coverage_needs_all_its_keys():
    assert problems(covered(guards={"scenario-coverage": {}})) == [
        "layered.yaml: guards.scenario-coverage: missing `columns`",
        "layered.yaml: guards.scenario-coverage: missing `file`",
        "layered.yaml: guards.scenario-coverage: missing `results`",
        "layered.yaml: guards.scenario-coverage: missing `suffix`",
        "layered.yaml: guards.scenario-coverage: missing `tier`"]


def test_stand_ins_needs_fakes_with_a_prefix_and_the_framework_s_mocks():
    assert problems(covered(guards={"stand-ins": {}})) == [
        "layered.yaml: guards.stand-ins: needs `fakes` with a `prefix`, such as {folder: fakes, for: [<part>], "
        "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and how a fake is named"]
    document = covered(guards={"stand-ins": {}}, fakes=FAKES)
    del document["testing"]["mocks"]
    assert problems(document) == [
        "layered.yaml: guards.stand-ins: needs `testing.mocks`: the calls that build a mock and the keywords a mock "
        "is given its spec by"]


def test_a_guard_that_reads_tests_needs_the_framework_even_without_tiers():
    document = layered(guards={"stand-ins": {}}, fakes=FAKES)
    assert problems(document) == [
        "layered.yaml: missing `testing`: `guards.stand-ins` must recognise a test file by its name: write testing: "
        "<preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]



PLAIN_NEEDS = ("layered.yaml: tiers.unit.plain_tables: needs a table form: the framework of `testing` writes none in "
               "`testing.tables`")


def test_a_tier_whose_table_tests_are_plain_says_so_and_needs_a_framework_that_writes_a_table_form():
    document = covered()
    document["tiers"]["unit"]["plain_tables"] = True
    assert [tier.plain_tables for tier in parsed(document).tiers] == [True, False]
    document["testing"] = {key: value for key, value in TESTING.items() if key != "tables"}
    assert problems(document) == [PLAIN_NEEDS]
    document["testing"] = TESTING | {"tables": []}
    assert problems(document) == [PLAIN_NEEDS]


def test_a_plain_tier_under_a_preset_that_writes_no_table_form_names_the_preset():
    document = covered(testing="pytest")
    document["tiers"]["unit"]["plain_tables"] = True
    presets = {"pytest": {"files": ["test_*.py"], "declared": BY_NAME}}
    assert problems(document, presets=presets) == [
        "layered.yaml: tiers.unit.plain_tables: needs a table form: the framework `pytest` writes none in "
        "`testing.tables`"]


def test_a_plain_tier_under_a_map_that_names_a_preset_names_the_preset():
    document = covered(testing={"preset": "pytest"})
    document["tiers"]["unit"]["plain_tables"] = True
    presets = {"pytest": {"files": ["test_*.py"], "declared": BY_NAME}}
    assert problems(document, presets=presets) == [
        "layered.yaml: tiers.unit.plain_tables: needs a table form: the framework `pytest` writes none in "
        "`testing.tables`"]


def test_a_plain_tier_with_no_framework_is_told_only_what_is_wrong_with_testing():
    document = covered()
    del document["testing"]
    document["tiers"]["unit"]["plain_tables"] = True
    assert problems(document) == [
        "layered.yaml: missing `testing`: `tiers` must recognise a test file by its name: write testing: <preset>, "
        "or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]
    document["testing"] = "odd"
    assert problems(document) == [
        "layered.yaml: testing: no preset 'odd': use pytest, or write the map {files, declared}"]


STUB = yaml.safe_load((Path(__file__).resolve().parents[4] / "fakes" / "frameworks" / "stub.yaml").read_text(encoding="utf-8"))
"""The test-only framework of tests/fakes/frameworks/, a loop form and a call form with literal rows, as a preset."""


def test_the_test_only_framework_loads_under_brace_into_two_forms_of_a_test_two_forms_of_a_table_and_a_global():
    framework = parsed(covered(testing="stub", language="brace"), presets={"stub": STUB},
                       languages={"python": PYTHON, "brace": BRACE}).framework
    assert framework == Framework(("*.test.ts",), (
        DeclaredForm(function="test*"),
        DeclaredForm(call=(("vitest", "it"), ("vitest", "test"), ("vitest", "it", "each"), ("vitest", "test", "each")),
                     title=Place(0), body=Place(1)),
    ), tables=(
        TableForm("bound", None, (), RowId(position=0), loop=True),
        TableForm("fields", Place(0), (), RowId(field="name"), call=(("vitest", "it", "each"), ("vitest", "test", "each"))),
    ), globals=(("expect",),))


def test_the_test_only_framework_is_refused_under_a_brace_that_does_not_write_a_field_id():
    unwritten = replace(BRACE, checked=replace(BRACE.checked, writing=Writing()))
    assert problems(covered(testing="stub", language="brace"), presets={"stub": STUB},
                    languages={"python": PYTHON, "brace": unwritten}) == [
        "layered.yaml: testing.tables.1.id: the language Brace does not write `writing.field`, how a row's id is "
        "given by a field"]


BESIDE_TYPE = ("layered.yaml: testing.beside: must be true or false: whether every test of a part sits beside the code "
               "it tests")
FOLDER_TIER = {"proves": "the architecture", "litmus": "Does it read the source?", "folder": "architecture"}


def beside(**testing) -> dict:
    """covered(), its testing the preset pytest with the keys given beside it."""
    return covered(testing={"preset": "pytest", **testing})


def guarded(testing: dict, *parts: str) -> dict:
    """covered() with testing as given, a tier guard whose tests live in tests/architecture, and the parts given
    tested by guard."""
    document = covered(testing=testing)
    document["tiers"]["guard"] = dict(FOLDER_TIER)
    for name in parts:
        document["parts"][name]["tests"] = "guard"
    return document


def test_beside_beside_a_preset_is_the_preset_s_framework_with_its_tests_beside_the_code():
    framework = parsed(beside(beside=True)).framework
    assert framework == replace(parsed(covered(testing="pytest")).framework, beside=True)
    assert framework.beside is True


def test_beside_in_a_whole_framework_keeps_the_framework_written():
    framework = parsed(covered(testing={"files": ["test_*.py"], "declared": BY_NAME, "beside": True})).framework
    assert (framework.files, framework.beside) == (("test_*.py",), True)


def test_beside_false_and_no_beside_mean_the_same_as_the_short_form():
    short = parsed(covered(testing="pytest"))
    assert parsed(beside()) == short
    assert parsed(beside(beside=False)) == short
    assert short.framework.beside is False


@pytest.mark.parametrize("value", [
    pytest.param("yes", id="a word"), pytest.param(1, id="a number"), pytest.param(None, id="null"),
    pytest.param([], id="a list"), pytest.param("true", id="the word true, quoted"),
])
def test_beside_that_is_no_bool_is_refused(value):
    assert problems(beside(beside=value)) == [BESIDE_TYPE]


def test_beside_with_no_tiers_is_refused():
    assert problems(layered(testing={"preset": "pytest", "beside": True})) == [
        "layered.yaml: testing.beside: the profile has no `tiers`: add them, or drop the key"]


def test_a_part_naming_a_tier_with_a_folder_is_refused_under_beside_and_loads_without_it():
    assert problems(guarded({"preset": "pytest", "beside": True}, "service")) == [
        "layered.yaml: tiers.guard: parts.service says tests: guard, and guard keeps its tests in tests/architecture: "
        "under testing.beside a part's tests sit beside its code; give the part a tier with no folder"]
    loaded = parsed(guarded({"preset": "pytest"}, "service"))
    assert [s.part for t in loaded.tiers if t.name == "guard" for s in t.subject] == ["service"]


def test_each_part_naming_a_tier_with_a_folder_is_refused_in_the_order_of_parts():
    assert problems(guarded({"preset": "pytest", "beside": True}, "service", "api")) == [
        f"layered.yaml: tiers.guard: parts.{name} says tests: guard, and guard keeps its tests in tests/architecture: "
        "under testing.beside a part's tests sit beside its code; give the part a tier with no folder"
        for name in ("api", "service")]


def test_a_tier_with_a_folder_no_part_names_is_kept_under_beside():
    assert parsed(guarded({"preset": "pytest", "beside": True})).framework.beside is True


def test_beside_is_no_key_of_the_framework_written_beside_preset_but_files_still_is():
    assert problems(beside(beside=True, files=["check_*.py"])) == [
        "layered.yaml: testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map"]


def test_a_broken_framework_and_a_broken_beside_are_both_reported_beside_last():
    assert problems(covered(testing={"files": "broken", "declared": BY_NAME, "beside": "yes"})) == [
        "layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with `*` for "
        "any text", BESIDE_TYPE]


def test_an_unknown_key_beside_preset_lists_beside_among_the_keys():
    assert problems(beside(beside=True, colour=1)) == [
        "layered.yaml: testing: unknown key 'colour': use beside, declared, files, globals, mocks, preset, skips, tables"]


def test_a_preset_may_not_say_beside_whichever_form_names_it():
    presets = {"near": {"files": ["test_*.py"], "declared": BY_NAME, "beside": True}} | PRESETS
    expected = ["layered.yaml: testing.beside: the preset near says beside: a preset writes the framework; write "
                "beside in the profile, beside preset"]
    assert problems(covered(testing="near"), presets=presets) == expected
    assert problems(covered(testing={"preset": "near"}), presets=presets) == expected


def test_beside_under_a_tier_is_an_unknown_key_with_no_hint():
    document = covered()
    document["tiers"]["unit"]["beside"] = True
    found = problems(document)
    assert len(found) == 1 and found[0].startswith("layered.yaml: tiers.unit: unknown key 'beside': use ")
    assert "moved" not in found[0]


EACH = {"call": ["vitest#it.each"], "rows": {"position": 0}, "columns_from": "fields", "row": "literal",
        "id": {"field": "name"}}
"""A table form a call that makes the test holds, its one callee vitest#it.each, its rows literals with a field id."""
LOOP_ROWS = {"loop": True, "columns_from": "bound", "row": "literal", "id": {"position": 0}}
"""A table form whose rows a loop of the test's body runs."""
CASES = {"decorator": "vitest#cases", "rows": {"position": 0}, "columns_from": "fields", "row": "literal",
         "id": {"field": "name"}}
"""A table form a decorator of the test holds."""
BY_TEST = {"function": "test*"}
"""A declared form of a function whose name starts with test."""


def called(*callees: str) -> dict:
    """A declared form of a call of the callees given, the title its first argument and the body its second."""
    return {"call": list(callees), "title": {"position": 0}, "body": {"position": 1}}


def undeclared(index: int, callee: str) -> str:
    """The refusal of a callee of the table call form at the index that no declared call form lists."""
    return (f"layered.yaml: testing.tables.{index}.call: `{callee}` declares no test: list it under a `call` form of "
            "`testing.declared`")


def tabled(declared: list, *tables) -> dict:
    """declaring() with the declared forms given and the table forms given."""
    return declaring(declared, tables=list(tables))


def test_a_table_call_form_whose_callee_no_declared_call_form_lists_is_refused_naming_the_callee():
    assert problems(tabled([BY_TEST, called("vitest#it")], EACH), languages=BRACED) == [undeclared(0, "vitest#it.each")]


def test_the_refusal_of_an_undeclared_callee_is_addressed_by_the_index_of_its_table_form():
    found = problems(tabled([BY_TEST, called("vitest#it")], LOOP_ROWS, EACH), languages=BRACED)
    assert found == [undeclared(1, "vitest#it.each")]
    assert [problem for problem in found if problem.startswith("layered.yaml: testing.tables.0")] == []


def test_a_table_call_form_loads_when_each_callee_is_listed_by_some_declared_call_form():
    two = EACH | {"call": ["vitest#it.each", "vitest#test.each"]}
    framework = parsed(tabled([called("vitest#it.each"), BY_TEST, called("vitest#test.each")], two),
                       languages=BRACED).framework
    assert framework.tables == (TableForm("fields", Place(0), (), RowId(field="name"),
                                          call=(("vitest", "it", "each"), ("vitest", "test", "each"))),)


@pytest.mark.parametrize("declared, expected", [
    pytest.param([called("vitest#it")], [undeclared(0, "vitest#it.each"), undeclared(0, "vitest#test.each")],
                 id="two undeclared callees, in the order the form writes them"),
    pytest.param([called("vitest#test.each")], [undeclared(0, "vitest#it.each")],
                 id="one declared callee and one not"),
])
def test_each_undeclared_callee_of_a_table_call_form_is_its_own_problem(declared, expected):
    two = EACH | {"call": ["vitest#it.each", "vitest#test.each"]}
    assert problems(tabled(declared, two), languages=BRACED) == expected


def test_a_table_call_form_under_a_framework_that_declares_tests_only_by_function_is_refused():
    assert problems(tabled([BY_TEST], EACH), languages=BRACED) == [undeclared(0, "vitest#it.each")]


@pytest.mark.parametrize("form", [pytest.param(CASES, id="a decorator form"), pytest.param(LOOP_ROWS, id="a loop form")])
def test_a_decorator_or_loop_table_form_is_not_checked_against_the_declared_calls(form):
    assert len(parsed(tabled([BY_TEST], form), languages=BRACED).framework.tables) == 1


@pytest.mark.parametrize("testing", [pytest.param("each", id="a preset by its name"),
                                     pytest.param({"preset": "each"}, id="a preset under preset")])
def test_a_table_call_form_of_a_preset_is_refused_the_same_at_the_same_address(testing):
    preset = TS_FILES | {"declared": [BY_TEST, called("vitest#it")], "tables": [EACH]}
    assert problems(covered(testing=testing, language="brace"), presets={"each": preset}, languages=BRACED) == [
        undeclared(0, "vitest#it.each")]


def test_a_problem_of_another_table_form_is_given_alone_and_the_callees_are_not_checked():
    broken = {key: value for key, value in LOOP_ROWS.items() if key != "row"}
    assert problems(tabled([BY_TEST], broken, EACH), languages=BRACED) == [
        "layered.yaml: testing.tables.0: missing `row`"]


def test_a_problem_of_the_mocks_does_not_stop_the_callees_being_checked():
    document = tabled([BY_TEST], EACH)
    document["testing"]["mocks"] = {"calls": ["vitest#vi.fn"], "specs": [], "colour": 1}
    assert problems(document, languages=BRACED) == [
        undeclared(0, "vitest#it.each"),
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
        f"layered.yaml: testing.mocks.specs: {SPECS}"]


def mocked(*specs: dict) -> dict:
    """declaring() with a function form, its mocks built by vitest#vi.fn and naming their spec by the specs given, and
    the guard stand-ins on."""
    return declaring([BY_TEST], mocks={"calls": ["vitest#vi.fn"], "specs": list(specs)}) | {
        "guards": {"stand-ins": {}}, "fakes": FAKES}


def test_under_brace_a_mock_may_name_its_spec_by_a_type_argument():
    stand_ins = next(guard for guard in parsed(mocked({"type_argument": 0}, {"type_argument": 1}),
                                               languages=BRACED).guards if isinstance(guard, StandIns))
    assert stand_ins.specs == (SpecEntry(type_argument=0), SpecEntry(type_argument=1))


@pytest.mark.parametrize("specs, said", [
    pytest.param([{"keyword": "of"}], ["0: the language Brace does not write `writing.specs.keyword`, how a mock is given "
                                       "its spec by a keyword"], id="a keyword"),
    pytest.param([{"type_argument": 0}, {"position": 0}],
                 ["1: the language Brace does not write `writing.specs.position`, how a mock is given its spec by a "
                  "position"], id="a position, at its index"),
])
def test_under_brace_a_spec_form_it_does_not_write_is_refused_at_its_entry(specs, said):
    assert problems(mocked(*specs), languages=BRACED) == [f"layered.yaml: testing.mocks.specs.{text}" for text in said]


def test_under_python_a_type_argument_is_refused_as_written_by_no_template():
    assert problems(covered(testing=TESTING | {"mocks": TESTING["mocks"] | {"specs": [{"type_argument": 0}]}}),
                    languages={"python": replace(PYTHON, checked=replace(PYTHON.checked, supplies=None))}) == [
        "layered.yaml: testing.mocks.specs.0: the language Python does not write `writing.specs.type_argument`, how a "
        "mock is given its spec by a type argument"]
