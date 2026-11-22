"""A profile file: the test framework (a preset or the map), the tiers and which part each covers, the
fakes, and the guards."""
import pytest

from tests.modules.spec.profiles import EX, PRESETS, TESTING, covered, layered, parsed, problems
from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    Subject,
    Tier,
    TierExample,
)
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns

PRESET_PROBLEM = ("layered.yaml: testing: must be a preset name or a mapping {files, functions}: the patterns of a "
                  "test file's name and of a test function's")


def test_the_framework_is_a_preset_by_name_or_the_map_written_out():
    named = parsed(covered(testing="pytest"))
    written = parsed(covered())
    assert named.framework == written.framework == Framework(
        ("test_*.py", "*_test.py"), "test_*", (("pytest", "mark", "skip"), ("pytest", "skip")),
        CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues")))


def test_a_preset_is_the_same_map_validated_like_one_written_in_the_file():
    broken = {"files": ["test_*.py"], "functions": 3}
    assert problems(covered(testing="odd"), presets={"odd": broken}) == [
        "layered.yaml: testing.functions: must be a function name pattern: a name with `*` for any text"]


@pytest.mark.parametrize("testing, presets, expected", [
    pytest.param("rspec", PRESETS, ["layered.yaml: testing: no preset 'rspec': use pytest, or write the map "
                                    "{files, functions}"], id="a preset that does not exist"),
    pytest.param("rspec", {}, ["layered.yaml: testing: no preset 'rspec': write the map {files, functions}"],
                 id="no preset at all"),
    pytest.param(3, PRESETS, [PRESET_PROBLEM], id="not a name or a map"),
    pytest.param({"functions": "test_*"}, PRESETS, ["layered.yaml: testing: missing `files`"], id="no files"),
    pytest.param({"files": ["test_*.py"]}, PRESETS, ["layered.yaml: testing: missing `functions`"], id="no functions"),
    pytest.param({"files": ["test_*.py"], "functions": "test_*", "colour": 1}, PRESETS,
                 ["layered.yaml: testing: unknown key 'colour': use files, functions, mocks, skips, table"],
                 id="an unknown key"),
    pytest.param({"files": ["x"], "functions": "test_*"}, PRESETS,
                 ["layered.yaml: testing.files: 'x' is not a file name pattern: a name ending in .py, with `*` for any "
                  "text"], id="a file pattern that is no .py name"),
    pytest.param({"files": [], "functions": "test_*"}, PRESETS,
                 ["layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with "
                  "`*` for any text"], id="no file patterns"),
    pytest.param({"files": ["a.py", "a.py"], "functions": "test_*"}, PRESETS,
                 ["layered.yaml: testing.files: 'a.py' is listed twice"], id="a pattern twice"),
    pytest.param({"files": ["a.py"], "functions": "a b"}, PRESETS,
                 ["layered.yaml: testing.functions: must be a function name pattern: a name with `*` for any text"],
                 id="a function pattern with a space"),
    pytest.param({"files": ["a.py"], "functions": "t_*", "skips": ["skip"]}, PRESETS,
                 ["layered.yaml: testing.skips: 'skip' is not a dotted name such as pkg.sub.name"], id="a skip that is not dotted"),
])
def test_a_bad_testing_key_is_refused(testing, presets, expected):
    assert problems(covered(testing=testing), presets=presets) == expected


def test_the_table_of_cases_and_the_mocks_are_checked_with_the_framework_whether_or_not_a_guard_uses_them():
    document = covered()
    document["testing"]["table"] = {"decorator": "x", "row": "y.z"}
    document["testing"]["mocks"] = {"calls": [], "autospec": ["a.b"], "spec_keywords": [], "fixtures": {}, "colour": 1}
    assert problems(document) == [
        "layered.yaml: testing.table: missing `id`",
        "layered.yaml: testing.table.decorator: 'x' is not a dotted name such as pkg.sub.name",
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, spec_keywords, spec_position",
        "layered.yaml: testing.mocks.calls: must be a list of dotted names such as pkg.sub.Name",
        "layered.yaml: testing.mocks.spec_keywords: must be a list of keyword names such as [spec]",
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
    document = covered(forbidden={"pure": ["socket"]})
    document["parts"]["service"]["forbidden"] = "pure"
    document["tiers"]["unit"]["apply_forbidden"] = True
    document["tiers"]["integration"]["types_only"] = ["service", "store"]
    tiers = parsed(document).tiers
    assert [(t.forbidden, t.types_only) for t in tiers] == [(True, ()), (False, ("service", "store"))]


def test_a_tier_with_a_folder_of_its_own_says_what_its_tests_may_import_there():
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture", "may_import": ["shared", "api@any"]}
    tier = parsed(document).tiers[2]
    assert (tier.folder, tier.subject, tier.may_import) == (("architecture",), (), (Target("shared"), Target("api", "any")))


def test_what_the_tests_of_a_tier_may_also_import_are_targets_a_bare_name_in_the_repeating_folder_the_mirrored_one():
    document = covered()
    document["tiers"]["integration"]["may_also_import"] = ["service", "shared", "api@any"]
    tiers = parsed(document).tiers
    assert [t.may_also_import for t in tiers] == [(), (Target("service", "own"), Target("shared"), Target("api", "any"))]


def test_a_tier_with_a_folder_and_no_may_import_may_import_nothing_and_everything_is_allowed_too():
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture"}
    assert parsed(document).tiers[2].may_import == ()
    document["tiers"]["guard"]["may_import"] = "everything"
    assert parsed(document).tiers[2].may_import == (Target("*"),)


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
    pytest.param({"colour": 1}, "layered.yaml: tiers.unit: unknown key 'colour': use apply_forbidden, docs, folder, "
                                "litmus, may_also_import, may_import, must_import, plain_tables, proves, "
                                "types_only", id="an unknown key"),
    pytest.param({"plain_tables": "yes"}, "layered.yaml: tiers.unit.plain_tables: must be true or false: whether "
                                          "every table test of the tier holds no branch in its body",
                 id="plain_tables that is no boolean"),
    pytest.param({"proves": "a\nb"}, "layered.yaml: tiers.unit.proves: must be one line of text", id="proves of two lines"),
    pytest.param({"litmus": 3}, "layered.yaml: tiers.unit.litmus: must be text: the question that tells a test "
                                "belongs to the tier", id="a litmus that is no text"),
    pytest.param({"apply_forbidden": "yes"}, "layered.yaml: tiers.unit.apply_forbidden: must be true or false: "
                                             "whether its tests are held to the `forbidden` list of the part they "
                                             "mirror", id="apply_forbidden that is no boolean"),
    pytest.param({"types_only": ["repo"]}, "layered.yaml: tiers.unit.types_only: no part named 'repo'", id="types_only of no part"),
    pytest.param({"may_import": ["shared"]}, "layered.yaml: tiers.unit.may_import: only a tier with a `folder` has an "
                                             "allowance of its own: without one, its tests import what the part "
                                             "they mirror may", id="may_import without a folder"),
    pytest.param({"may_also_import": "everything"}, "layered.yaml: tiers.unit.may_also_import: must be a list of "
                                                    "targets such as [<part>, shared/text, api@any]: `everything` is "
                                                    "not taken, name each target the tests may also import",
                 id="may_also_import of everything"),
    pytest.param({"may_also_import": ["shared", "everything"]}, "layered.yaml: tiers.unit.may_also_import: "
                                                                "`everything` is not taken, name each target the "
                                                                "tests may also import",
                 id="everything in a list of may_also_import"),
    pytest.param({"may_also_import": ["repo"]}, "layered.yaml: tiers.unit.may_also_import: 'repo' names no part "
                                                "'repo'", id="may_also_import of no part"),
    pytest.param({"may_also_import": ["service@own"]}, "layered.yaml: tiers.unit.may_also_import: 'service@own' says "
                                                       "what a bare name already says: write service",
                 id="may_also_import of the mirrored instance written out"),
])
def test_a_bad_tier_is_refused(tier, expected):
    document = covered()
    document["tiers"]["unit"] |= tier
    assert problems(document) == [expected]


def test_a_tier_folder_follows_the_rules_it_had_and_its_allowance_is_a_part_s_may_import():
    document = covered()
    document["tiers"]["guard"] = {"folder": "src/billing/api", "may_import": ["api", "service@own", "repo", "shared/"]}
    assert problems(document) == [
        "layered.yaml: tiers.guard.folder: 'src/billing/api' is the folder of part 'api', which places its tests: give "
        "`folder` only to a folder that mirrors no part",
        "layered.yaml: tiers.guard.may_import: 'api' lies in the repeating folder, which a tier's folder is not in: "
        "say api@any",
        "layered.yaml: tiers.guard.may_import: 'service@own' lies in the repeating folder, which a tier's folder is "
        "not in: say service@any",
        "layered.yaml: tiers.guard.may_import: 'repo' names no part 'repo'",
        "layered.yaml: tiers.guard.may_import: 'shared/' has an invalid path after the part"]


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


PART_KEYS = ("built_by, folders, forbidden, holds, immutable, libraries, litmus, may_import, must_import, names, "
             "no_callbacks, package_only, path, role, shared, tests, types_only, untested")
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
        "layered.yaml: tiers.unit: unknown key 'tier': use apply_forbidden, docs, folder, litmus, may_also_import, "
        "may_import, must_import, plain_tables, proves, types_only"]


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
                                  "write testing: <preset>, or testing: {files: [<pattern>, ...], functions: <pattern>}"]


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
                          "columns": ["given", "when", "then"], "file": "test_{name}.py"},
    "stand-ins": {}, "no-comments": {}, "closed-tree": {},
}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}


def test_the_guards_in_use_are_those_named_with_the_framework_s_words_taken_from_testing():
    architecture = parsed(covered(guards=GUARDS, fakes=FAKES))
    assert architecture.guards == (
        ScenarioCoverage("api", "integration", "Result", ("given", "when", "then"),
                         CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id",
                                   ("argnames", "argvalues")), "test_{name}.py"),
        StandIns((("unittest", "mock", "Mock"), ("unittest", "mock", "MagicMock")),
                 (("unittest", "mock", "create_autospec"),), ("spec", "spec_set"),
                 (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),), 0),
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
                                  "no-comments, no-duplicates, no-twins, pass-through, private-imports, "
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
])
def test_a_bad_new_guard_is_refused(guards, expected):
    assert problems(covered(guards=guards, fakes=FAKES)) == expected


def test_dead_code_without_fakes_is_refused():
    assert problems(covered(guards={"dead-code": {}})) == [
        "layered.yaml: guards.dead-code: needs `fakes`: it reads the Protocols of the parts `fakes.for` names and the "
        "classes in `fakes.folder`"]


def test_scenario_coverage_reads_its_table_from_the_framework_and_says_so_when_there_is_none():
    document = covered(guards={"scenario-coverage": GUARDS["scenario-coverage"]})
    del document["testing"]["table"]
    assert problems(document) == ["layered.yaml: guards.scenario-coverage: needs `testing.table`: how a table of cases "
                                  "is written, such as {decorator, row, id}"]


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
    pytest.param({"file": "test.py"}, [f"{SCENARIOS}.file: must hold `{{name}}` once, such as a_{{name}}.py"]),
    pytest.param({"file": "{name}.rb"}, [
        f"{SCENARIOS}.file: must be a file name below the test folders, such as a_{{name}}.py"]),
    pytest.param({"file": "{name}.py"}, [
        f"{SCENARIOS}.file: '{{name}}.py' is not a name `testing.files` recognises as a test file"]),
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
        "<preset>, or testing: {files: [<pattern>, ...], functions: <pattern>}"]



def test_a_tier_whose_table_tests_are_plain_says_so_and_needs_the_form_of_a_table():
    document = covered()
    document["tiers"]["unit"]["plain_tables"] = True
    assert [tier.plain_tables for tier in parsed(document).tiers] == [True, False]
    document["testing"] = {key: value for key, value in TESTING.items() if key != "table"}
    assert problems(document) == ["layered.yaml: tiers.unit.plain_tables: needs `testing.table`, how a table of cases "
                                  "is written, to know a table test"]
