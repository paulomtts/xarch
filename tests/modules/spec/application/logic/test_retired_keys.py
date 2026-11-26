"""The table of retired names, read by every path that refuses an unknown name: the lookup by scope and name, and by
the address `profile explain` is typed with; every unknown key of a mapping, of the file, under `hints` and under
`guards` that has an entry under its scope gives one problem of its own with the entry's fixed text, ahead of today's
message for the others, which is unchanged. A table built for each test is set where the lookup reads it."""
import pytest

from tests.modules.spec.profiles import PRESETS, covered, layered, parsed, part_of, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.application.logic.key_lookup import names_of, retired, retired_at, retired_value
from xarch.modules.spec.application.logic.profile_checks import rule_hints, unknown_keys
from xarch.modules.spec.domain.profile_keys import (
    DEAD_CODE,
    DOCS,
    EVAL,
    FAKES,
    FILE,
    FIXTURE,
    GUARD,
    HELD,
    MOCKS,
    NAMING,
    NO_CALLBACKS,
    NO_DUPLICATES,
    NO_TWINS,
    PAGE,
    PART,
    PART_HOLDS,
    PART_HOLDS_CLASSES,
    PART_HOLDS_EXCEPTIONS,
    PART_HOLDS_FUNCTIONS,
    PART_HOLDS_RECORDS,
    PART_IMPORTS,
    PART_IMPORTS_MAY,
    PART_USES,
    PASS_THROUGH,
    PLACEMENT,
    PROFILE,
    REVIEW,
    RULE_ID,
    SCENARIO_COVERAGE,
    SCOPES,
    TESTING,
    TIER,
    TIER_DOCS,
    TIER_IMPORTS,
    Retired,
)

RENAMED = "renamed in 0.3.0: write tier"
MOVED = "moved in 0.3.0: write uses: {never: <list>}"
MISPLACED = "a key of uses: write uses: {never: <list>}"
PART_USE = "holds, imports, litmus, name, optional, package_only, role, shared, tests, untested, uses"
TIER_USE = "accepted, docs, folder, imports, litmus, plain_tables, proves, uses"
PROFILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, "
               "parts, reserved, review, structure, testing, tiers")
GUARD_USE = ("closed-tree, dead-code, no-callbacks, no-comments, no-duplicates, no-twins, pass-through, "
             "private-imports, scenario-coverage, stand-ins")
EVAL_USE = "answer, ask, examples, fix, in, keep, line, message, no, reads, yes"
RULES_USE = ", ".join(sorted(RULES))
CODE = "def run(doc):\n    return doc\n"


def an_eval() -> dict:
    """An eval of the profile's own, `rule`, yes-no, reading functions of store, that loads as it is."""
    return {"rule": {"ask": "Does this function decide a rule of the document itself?", "answer": "yes-no",
                     "reads": "function", "in": {"part": "store"}, "message": "{name} may decide it ({value})",
                     "fix": "read it against the litmus of store",
                     "examples": {"flagged": {"store/a.py": CODE, "store/b.py": CODE},
                                  "clean": {"store/c.py": CODE, "store/d.py": CODE}}}}


def writing(document: dict, *steps: str) -> dict:
    """The document, with `banned: x` written in the mapping found at the steps."""
    held = document
    for step in steps:
        held = held[step]
    held["banned"] = "x"
    return document


def table(monkeypatch: pytest.MonkeyPatch, *entries: tuple[str, str, str]) -> None:
    """The table of retired names is the entries given, each (scope, name, text), for this test alone."""
    monkeypatch.setattr(key_lookup, "RETIRED", tuple(Retired(scope, name, text) for scope, name, text in entries))


def test_the_lookup_gives_the_text_of_the_entry_for_a_scope_and_a_name_or_nothing(monkeypatch):
    table(monkeypatch, (PART, "tested_by", RENAMED))
    assert (retired(PART, "tested_by"), retired(TIER, "tested_by"), retired(PART, "banned"), retired("", "tested_by")) \
        == (RENAMED, "", "", "")


TESTS = "renamed in 0.3.0: write tests"
LIST_MOVED = "moved in 0.3.0: write uses: {never: <list>}"
SWITCH_MOVED = "moved in 0.3.0: write uses: {apply_never: true}"
BLOCK = "renamed in 0.3.0: write never"
RULE = "renamed in 0.3.0: write never-use"
IMPORT_RULE = "renamed in 0.3.0: write may-import"
TABLE_MOVED = "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"
FUNCTIONS_MOVED = 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'
"""The hint of testing.functions, which testing.declared replaced in 0.3.0."""
SPECS_MOVED = "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"
OLD_TABLE = {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
             "keywords": ["argnames", "argvalues"]}
"""testing.table as profiles wrote it before 0.3.0."""
LIST_OUTSIDE = "a key of uses: write uses: {never: <list>}"
SWITCH_OUTSIDE = "a key of uses: write uses: {apply_never: true}"
CALLBACKS_MOVED = "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}"
IMMUTABLE_MOVED = "moved in 0.3.0: write it under the kind it applies to, such as holds: {records: {immutable: true}}"
NAMES_MOVED = 'moved in 0.3.0: write it under the kind it names, such as holds: {classes: {names: "*Service"}}'
BUILT_BY_MOVED = "moved in 0.3.0: write holds: {classes: {built_by: [<part>, ...]}}"
OF_CLASSES_AND_RECORDS = "a setting of classes and records"
OF_CLASSES = "a setting of classes"
HOLDS_FUNCTIONS = ("holds as one word was removed in 0.3.0: write holds: {functions: {}, records: {}, exceptions: {}}, "
                   "which allows what holds: functions allowed")
HOLDS_CLASSES = "holds as one word was removed in 0.3.0: write holds: {classes: {}}"


@pytest.mark.parametrize("scope, name, text", [
    pytest.param(PART, "tier", TESTS, id="the part key tier"),
    pytest.param(PART, "forbidden", LIST_MOVED, id="the part key forbidden"),
    pytest.param(TIER, "apply_forbidden", SWITCH_MOVED, id="the tier key apply_forbidden"),
    pytest.param(PROFILE, "forbidden", BLOCK, id="the block forbidden"),
    pytest.param(RULE_ID, "forbidden", RULE, id="the rule id forbidden"),
    pytest.param(RULE_ID, "rules", IMPORT_RULE, id="the rule id rules"),
    pytest.param(RULE_ID, "may-import", "", id="the rule id may-import, which xarch has"),
    pytest.param(PART, "never", LIST_OUTSIDE, id="never on a part"),
    pytest.param(TIER, "apply_never", SWITCH_OUTSIDE, id="apply_never on a tier"),
    pytest.param(PART, "no_callbacks", CALLBACKS_MOVED, id="the part key no_callbacks"),
    pytest.param(GUARD, "no-callbacks", "", id="the guard no-callbacks, which xarch has"),
    pytest.param(PART, "immutable", IMMUTABLE_MOVED, id="the part key immutable"),
    pytest.param(PART, "names", NAMES_MOVED, id="the part key names"),
    pytest.param(PART, "built_by", BUILT_BY_MOVED, id="the part key built_by"),
    pytest.param(PART_HOLDS_FUNCTIONS, "immutable", OF_CLASSES_AND_RECORDS, id="immutable under functions"),
    pytest.param(PART_HOLDS_FUNCTIONS, "built_by", OF_CLASSES, id="built_by under functions"),
    pytest.param(PART_HOLDS_RECORDS, "built_by", OF_CLASSES, id="built_by under records"),
    pytest.param(PART_HOLDS_EXCEPTIONS, "immutable", OF_CLASSES_AND_RECORDS, id="immutable under exceptions"),
    pytest.param(PART_HOLDS_EXCEPTIONS, "built_by", OF_CLASSES, id="built_by under exceptions"),
    pytest.param(PART_HOLDS_CLASSES, "immutable", "", id="immutable under classes, a key"),
    pytest.param(PART_HOLDS_RECORDS, "immutable", "", id="immutable under records, a key"),
    pytest.param(PART, "holds", "", id="the part key holds, whose one-word values are retired, not the key"),
    pytest.param(PART_HOLDS, "classes", "", id="the kind classes"),
    pytest.param(PART_USES, "never", "", id="never under a part's uses, a key"),
    pytest.param(TIER, "forbidden", "", id="forbidden under a tier, only unknown"),
    pytest.param(TIER, "tier", "", id="tier under a tier"),
    pytest.param(SCENARIO_COVERAGE, "tier", "", id="the tier of scenario-coverage"),
    pytest.param(PART, "tests", "", id="the part key tests"),
    pytest.param(PART, "may_import", "moved in 0.3.0: write imports: {may: [...]}", id="the part key may_import"),
    pytest.param(PART, "must_import", "moved in 0.3.0: write imports: {must: [...]}", id="the part key must_import"),
    pytest.param(PART, "libraries", "moved in 0.3.0: write imports: {libraries: [...]}", id="the part key libraries"),
    pytest.param(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                 "[{parts.ports: types_only}]", id="the part key types_only"),
    pytest.param(PART_IMPORTS, "never", "a key of uses, beside imports: write uses: {never: <list>}",
                 id="never in imports"),
    pytest.param(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                 "[{parts.ports: types_only}]", id="types_only in imports"),
    pytest.param(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}", id="the tier key may_import"),
    pytest.param(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}",
                 id="the tier key may_also_import"),
    pytest.param(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}", id="the tier key must_import"),
    pytest.param(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [parts.<part>, ...]}",
                 id="the tier key types_only, its own hint beside the part's"),
    pytest.param(TIER_IMPORTS, "types_only", "", id="types_only in a tier's imports, a key"),
    pytest.param(TIER_IMPORTS, "libraries", "", id="libraries in a tier's imports, only unknown"),
    pytest.param(PART_IMPORTS_MAY, "types_only", "", id="the mark, a key"),
    pytest.param(TESTING, "table", TABLE_MOVED, id="the testing key table"),
    pytest.param(MOCKS, "spec_keywords", SPECS_MOVED, id="the mocks key spec_keywords"),
    pytest.param(MOCKS, "spec_position", SPECS_MOVED, id="the mocks key spec_position"),
    pytest.param(MOCKS, "specs", "", id="the mocks key specs"),
])
def test_the_shipped_table_answers_each_name_in_its_scope(scope, name, text):
    assert retired(scope, name) == text


@pytest.mark.parametrize("address, text", [
    pytest.param("parts.tier", TESTS, id="parts.tier"),
    pytest.param("parts.<part>.tier", TESTS, id="parts.<part>.tier"),
    pytest.param("forbidden", BLOCK, id="forbidden"),
    pytest.param("parts.forbidden", LIST_MOVED, id="parts.forbidden"),
    pytest.param("parts.<part>.forbidden", LIST_MOVED, id="parts.<part>.forbidden"),
    pytest.param("tiers.apply_forbidden", SWITCH_MOVED, id="tiers.apply_forbidden"),
    pytest.param("tiers.<tier>.apply_forbidden", SWITCH_MOVED, id="tiers.<tier>.apply_forbidden"),
    pytest.param("parts.never", LIST_OUTSIDE, id="parts.never"),
    pytest.param("tiers.apply_never", SWITCH_OUTSIDE, id="tiers.apply_never"),
    pytest.param("parts.no_callbacks", CALLBACKS_MOVED, id="parts.no_callbacks"),
    pytest.param("parts.<part>.no_callbacks", CALLBACKS_MOVED, id="parts.<part>.no_callbacks"),
    pytest.param("guards.no-callbacks", "", id="guards.no-callbacks"),
    pytest.param("parts.immutable", IMMUTABLE_MOVED, id="parts.immutable"),
    pytest.param("parts.<part>.names", NAMES_MOVED, id="parts.<part>.names"),
    pytest.param("parts.built_by", BUILT_BY_MOVED, id="parts.built_by"),
    pytest.param("parts.holds.functions.immutable", OF_CLASSES_AND_RECORDS, id="parts.holds.functions.immutable"),
    pytest.param("parts.<part>.holds.exceptions.built_by", OF_CLASSES, id="parts.<part>.holds.exceptions.built_by"),
    pytest.param("parts.holds", "", id="parts.holds"),
    pytest.param("parts.holds.records.immutable", "", id="parts.holds.records.immutable"),
    pytest.param("parts.uses.never", "", id="parts.uses.never"),
    pytest.param("tiers.uses.apply_never", "", id="tiers.uses.apply_never"),
    pytest.param("never", "", id="never"),
    pytest.param("review.never", "", id="review.never"),
    pytest.param("parts.may_import", "moved in 0.3.0: write imports: {may: [...]}", id="parts.may_import"),
    pytest.param("parts.<part>.types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such "
                 "as [{parts.ports: types_only}]", id="parts.<part>.types_only"),
    pytest.param("parts.imports.may.types_only", "", id="parts.imports.may.types_only"),
    pytest.param("tiers.types_only", "moved in 0.3.0: write imports: {types_only: [parts.<part>, ...]}",
                 id="tiers.types_only"),
    pytest.param("tiers.<tier>.may_also_import", "moved in 0.3.0: write imports: {also: [...]}",
                 id="tiers.<tier>.may_also_import"),
    pytest.param("tiers.imports.types_only", "", id="tiers.imports.types_only"),
    pytest.param("testing.table", TABLE_MOVED, id="testing.table"),
    pytest.param("testing.functions", FUNCTIONS_MOVED, id="testing.functions"),
    pytest.param("testing.mocks.spec_keywords", SPECS_MOVED, id="testing.mocks.spec_keywords"),
    pytest.param("testing.mocks.spec_position", SPECS_MOVED, id="testing.mocks.spec_position"),
])
def test_the_shipped_table_answers_each_address_profile_explain_is_typed_with(address, text):
    assert retired_at(address) == text


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "parts.tested_by", id="a key of a part, typed plain"),
    pytest.param((PART, "tested_by", RENAMED), "parts.<part>.tested_by", id="with the placeholder of the part"),
    pytest.param((PART, "tested_by", RENAMED), " parts.tested_by. ", id="with spaces and a stray dot"),
    pytest.param((PROFILE, "banned", MOVED), "banned", id="a key of the file, by its bare name"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming[].level", id="a key of a row of a list, with []"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming.level", id="a key of a row of a list, typed plain"),
    pytest.param((EVAL, "asks", RENAMED), "evals.<id>.asks", id="a slot of an eval, with the placeholder of its id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.title-rule.asks", id="a slot of an eval, under an id"),
])
def test_an_address_of_an_entry_gives_its_text_however_it_is_typed(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == entry[2]


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "tiers.tested_by", id="the name under another scope"),
    pytest.param((PART, "tested_by", RENAMED), "tested_by", id="the name at the top of the file"),
    pytest.param((PROFILE, "banned", MOVED), "parts.banned", id="a key of the file, under a part"),
    pytest.param((EVAL, "asks", RENAMED), "evals.placement.asks", id="placement is a key of evals, not an eval's id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.asks", id="a slot of an eval, typed with no id step"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "hints.old-rule", id="a rule id has no address"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "old-rule", id="nor a bare one"),
])
def test_an_address_that_is_no_entry_gives_nothing(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == ""


def test_a_retired_key_gets_its_own_problem_ahead_of_the_one_only_unknown(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert unknown_keys({"role": "a", "banned": 1, "colour": 2}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}",
        f"parts.api: unknown key 'colour': use {PART_USE}"]


def test_two_retired_keys_give_two_problems_in_sorted_order_and_no_joined_one(monkeypatch):
    table(monkeypatch, (PART, "tested_by", RENAMED), (PART, "banned", MOVED))
    assert unknown_keys({"tested_by": 1, "banned": 2}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {MOVED}; use {PART_USE}",
        f"parts.api: unknown key 'tested_by': {RENAMED}; use {PART_USE}"]


def test_a_retired_key_beside_two_only_unknown_keeps_their_plural_message(monkeypatch):
    table(monkeypatch, (PART, "banned", MISPLACED))
    assert unknown_keys({"zone": 1, "banned": 2, "colour": 3}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {MISPLACED}; use {PART_USE}",
        f"parts.api: unknown keys 'colour', 'zone': use {PART_USE}"]


@pytest.mark.parametrize("entry, scope", [
    pytest.param((PART, "other", RENAMED), PART, id="an entry for another name of the scope"),
    pytest.param((PART, "colour", RENAMED), "", id="a mapping read with no scope"),
])
def test_with_no_entry_for_its_keys_a_mapping_gets_todays_message(monkeypatch, entry, scope):
    table(monkeypatch, entry)
    assert unknown_keys({"zone": 1, "colour": 2}, names_of(PART), "parts.api", scope) == [
        f"parts.api: unknown keys 'colour', 'zone': use {PART_USE}"]


def test_the_shipped_table_changes_no_message():
    assert unknown_keys({"colour": 1}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'colour': use {PART_USE}"]


@pytest.mark.parametrize("value", [True, False], ids=["true", "false"])
def test_a_part_writing_no_callbacks_is_refused_with_the_guard_that_replaces_it(value):
    document = layered()
    part_of(document, "service")["no_callbacks"] = value
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'no_callbacks': {CALLBACKS_MOVED}; use {PART_USE}"]


@pytest.mark.parametrize("value, text", [
    pytest.param("functions", HOLDS_FUNCTIONS, id="functions"),
    pytest.param("classes", HOLDS_CLASSES, id="classes"),
    pytest.param("records", "", id="a word that never was a value"),
])
def test_the_one_word_values_of_holds_have_entries_of_their_own(value, text):
    assert retired_value(PART, "holds", value) == text


@pytest.mark.parametrize("key, value, text", [
    pytest.param("immutable", True, IMMUTABLE_MOVED, id="immutable"),
    pytest.param("names", "*Service", NAMES_MOVED, id="names"),
    pytest.param("built_by", ["api"], BUILT_BY_MOVED, id="built_by"),
])
def test_a_part_writing_a_setting_of_holds_as_its_own_key_is_refused_with_the_form_that_replaces_it(key, value, text):
    document = layered()
    part_of(document, "service")[key] = value
    assert problems(document) == [f"layered.yaml: parts.service: unknown key '{key}': {text}; use {PART_USE}"]


def test_a_part_writing_the_three_settings_as_its_own_keys_gets_one_problem_each_in_sorted_order():
    document = layered()
    part_of(document, "service").update({"names": "*Service", "immutable": True, "built_by": ["api"]})
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'built_by': {BUILT_BY_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.service: unknown key 'immutable': {IMMUTABLE_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.service: unknown key 'names': {NAMES_MOVED}; use {PART_USE}"]


@pytest.mark.parametrize("value, text", [
    pytest.param("functions", HOLDS_FUNCTIONS, id="functions"),
    pytest.param("classes", HOLDS_CLASSES, id="classes"),
])
def test_holds_written_as_one_word_is_refused_with_the_map_that_allows_the_same(value, text):
    document = layered()
    part_of(document, "service")["holds"] = value
    assert problems(document) == [f"layered.yaml: parts.service.holds: '{value}': {text}"]


def test_a_part_writing_no_callbacks_beside_the_guard_gets_only_the_retired_key_s_problem():
    document = layered(guards={"no-callbacks": {"parts": ["service"]}})
    part_of(document, "service")["no_callbacks"] = True
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'no_callbacks': {CALLBACKS_MOVED}; use {PART_USE}"]


def test_an_entry_under_another_scope_does_not_apply(monkeypatch):
    table(monkeypatch, (TIER, "banned", RENAMED))
    assert unknown_keys({"banned": 1}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': use {PART_USE}"]


def test_an_entry_of_a_part_key_leaves_a_tier_and_the_file_alone(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert sorted(problems(writing(covered(banned=1), "tiers", "unit"))) == sorted([
        f"layered.yaml: unknown key 'banned': use {PROFILE_USE}",
        f"layered.yaml: tiers.unit: unknown key 'banned': use {TIER_USE}"])


def test_a_known_key_with_an_entry_is_accepted(monkeypatch):
    table(monkeypatch, (PART, "role", RENAMED))
    assert unknown_keys({"role": "x", "name": "a"}, names_of(PART), "parts.api", PART) == []
    assert parsed(layered()).parts["api"].role == "HTTP handlers"


def test_the_value_written_under_a_retired_key_is_not_in_its_problem(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert unknown_keys({"banned": "unit"}, names_of(PART), "parts.api", PART) \
        == unknown_keys({"banned": [1, 2]}, names_of(PART), "parts.api", PART) \
        == [f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}"]


def test_a_key_yaml_reads_as_no_string_is_looked_up_as_it_is_shown(monkeypatch):
    table(monkeypatch, (PART, "1", RENAMED))
    assert unknown_keys({1: "x"}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key '1': {RENAMED}; use {PART_USE}"]


def test_a_mapping_written_as_a_list_keeps_its_own_problem_and_reads_no_entry(monkeypatch):
    table(monkeypatch, (PART, "x", RENAMED))
    document = layered()
    document["parts"]["src/<module>/"]["api/"] = ["x"]
    assert problems(document) == ["layered.yaml: parts: 'src/<module>/api/': a folder is a map, one line of text (its "
                                  "note), or nothing"]


def test_a_retired_rule_id_under_hints_is_refused_with_its_text_and_another_keeps_todays(monkeypatch):
    table(monkeypatch, (RULE_ID, "old-rule", "renamed in 0.3.0: write may-import"))
    found: list[str] = []
    assert rule_hints({"old-rule": "see the docs", "odd-rule": "see the docs"}, found) == {}
    assert found == [
        f"hints.old-rule: unknown rule id 'old-rule': renamed in 0.3.0: write may-import; use {RULES_USE}",
        f"hints.odd-rule: unknown rule id 'odd-rule': use {RULES_USE}"]


def test_a_rule_id_of_the_profile_own_that_matches_an_entry_is_its_own(monkeypatch):
    table(monkeypatch, (RULE_ID, "old-rule", "renamed in 0.3.0: write may-import"))
    found: list[str] = []
    assert rule_hints({"old-rule": "see the docs"}, found, ("old-rule",)) == {"old-rule": "see the docs"}
    assert found == []


def test_the_file_gives_its_retired_keys_then_the_only_unknown_then_the_missing(monkeypatch):
    table(monkeypatch, (PROFILE, "banned", MOVED))
    assert problems({"name": "x", "colour": 1, "banned": 1}) == [
        f"layered.yaml: unknown key 'banned': {MOVED}; use {PROFILE_USE}",
        f"layered.yaml: unknown key 'colour': use {PROFILE_USE}",
        "layered.yaml: missing `parts`"]


def test_a_file_whose_only_unknown_keys_are_retired_gives_no_joined_problem(monkeypatch):
    table(monkeypatch, (PROFILE, "banned", MOVED))
    assert problems(layered(banned=1)) == [f"layered.yaml: unknown key 'banned': {MOVED}; use {PROFILE_USE}"]


@pytest.mark.parametrize("scope, document, problem", [
    pytest.param(PART, writing(layered(), "parts", "src/<module>/", "api/"),
                 f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}", id="a part"),
    pytest.param(TIER, writing(covered(), "tiers", "unit"),
                 f"tiers.unit: unknown key 'banned': {RENAMED}; use {TIER_USE}", id="a tier"),
    pytest.param(TESTING, writing(covered(), "testing"),
                 f"testing: unknown key 'banned': {RENAMED}; use beside, declared, files, globals, mocks, preset, "
                 "shared, skips, tables",
                 id="testing, through framework_patterns"),
    pytest.param(FIXTURE, writing(covered(), "testing", "mocks", "fixtures", "mocker"),
                 f"testing.mocks.fixtures.mocker: unknown key 'banned': {RENAMED}; use autospec, calls",
                 id="a fixture, whose keys are the language's word and autospec"),
    pytest.param(EVAL, writing(layered(evals=an_eval()), "evals", "rule"),
                 f"evals.rule: unknown key 'banned': {RENAMED}; use {EVAL_USE}", id="an eval of the profile's own"),
    pytest.param(PLACEMENT, writing(layered(evals={"placement": {}}), "evals", "placement"),
                 f"evals.placement: unknown key 'banned': {RENAMED}; use alike, examples, lines", id="evals.placement"),
    pytest.param(REVIEW, writing(layered(review={}), "review"),
                 f"review: unknown key 'banned': {RENAMED}; use mask, never", id="review"),
    pytest.param(DOCS, writing(layered(docs={}), "docs"),
                 f"docs: unknown key 'banned': {RENAMED}; use entry, example_notes, examples, naming, pages", id="docs"),
    pytest.param(NO_DUPLICATES, writing(layered(guards={"no-duplicates": {}}), "guards", "no-duplicates"),
                 f"guards.no-duplicates: unknown key 'banned': {RENAMED}; use min_statements", id="a guard's settings"),
])
def test_each_mapping_reads_the_entries_of_its_own_scope(monkeypatch, scope, document, problem):
    table(monkeypatch, (scope, "banned", RENAMED))
    assert problems(document) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("scope, document, problem", [
    pytest.param(MOCKS, writing(covered(), "testing", "mocks"),
                 "testing.mocks: unknown key 'banned'", id="testing.mocks"),
    pytest.param(TIER_DOCS, writing(covered(tiers={"unit": {"proves": "a rule", "docs": {}},
                                                   "integration": {"proves": "a request"}}), "tiers", "unit", "docs"),
                 "tiers.unit.docs: unknown key 'banned'", id="a tier's docs"),
    pytest.param(FAKES, writing(covered(fakes={}), "fakes"), "fakes: unknown key 'banned'", id="fakes"),
    pytest.param(SCENARIO_COVERAGE, writing(covered(guards={"scenario-coverage": {}}), "guards", "scenario-coverage"),
                 "guards.scenario-coverage: unknown key 'banned'", id="scenario-coverage"),
    pytest.param(DEAD_CODE, writing(layered(guards={"dead-code": {}}), "guards", "dead-code"),
                 "guards.dead-code: unknown key 'banned'", id="dead-code"),
    pytest.param(NO_TWINS, writing(layered(guards={"no-twins": {}}), "guards", "no-twins"),
                 "guards.no-twins: unknown key 'banned'", id="no-twins"),
    pytest.param(PASS_THROUGH, writing(layered(guards={"pass-through": {"parts": ["api"]}}), "guards", "pass-through"),
                 "guards.pass-through: unknown key 'banned'", id="pass-through"),
    pytest.param(NO_CALLBACKS, writing(layered(guards={"no-callbacks": {"parts": ["api"]}}), "guards", "no-callbacks"),
                 "guards.no-callbacks: unknown key 'banned'", id="no-callbacks"),
    pytest.param(NAMING, layered(docs={"naming": [{"kind": "x", "where": "api", "pattern": "x", "example": "x",
                                                   "banned": "x"}]}),
                 "docs.naming[0]: unknown key 'banned'", id="a row of docs.naming"),
    pytest.param(PAGE, layered(docs={"pages": {"a.md": {"banned": "x"}}}),
                 "docs.pages.a.md: unknown key 'banned'", id="a page of docs.pages"),
    pytest.param(FILE, layered(files={"a.md": {"banned": "x"}}), "files.a.md: unknown key 'banned'", id="a file"),
])
def test_every_other_mapping_reads_the_entries_of_its_own_scope(monkeypatch, scope, document, problem):
    table(monkeypatch, (scope, "banned", RENAMED))
    assert problems(document)[0].startswith(f"layered.yaml: {problem}: {RENAMED}; use ")


def test_a_retired_guard_is_refused_with_its_text_and_another_unknown_guard_keeps_todays(monkeypatch):
    table(monkeypatch, (GUARD, "no-comment", "renamed in 0.3.0: write no-comments"))
    assert problems(layered(guards={"no-comment": {}, "zzz": {}})) == [
        f"layered.yaml: guards: unknown guard 'no-comment': renamed in 0.3.0: write no-comments; use {GUARD_USE}",
        f"layered.yaml: guards: unknown guard 'zzz': use {GUARD_USE}"]


def test_the_examples_of_an_eval_have_no_scope_and_read_no_entry(monkeypatch):
    table(monkeypatch, *((scope, "flagged2", RENAMED) for scope in (*SCOPES, *HELD, RULE_ID)))
    document = an_eval()
    document["rule"]["examples"]["flagged2"] = {}
    assert problems(layered(evals=document)) == [
        "layered.yaml: evals.rule.examples: unknown key 'flagged2': use clean, flagged"]


@pytest.mark.parametrize("testing, presets", [
    pytest.param({"files": ["test_*.py"], "declared": [{"function": "test_*"}], "table": OLD_TABLE}, PRESETS, id="in an inline map"),
    pytest.param("old", {"old": {"files": ["test_*.py"], "declared": [{"function": "test_*"}], "table": OLD_TABLE}},
                 id="in a preset"),
])
def test_the_table_of_testing_is_refused_with_the_list_of_forms_that_replaces_it(testing, presets):
    assert problems(layered(testing=testing), presets=presets) == [
        f"layered.yaml: testing: unknown key 'table': {TABLE_MOVED}; use beside, declared, files, globals, mocks, preset, "
        "shared, skips, tables"]


@pytest.mark.parametrize("testing, presets", [
    pytest.param({"files": ["test_*.py"], "functions": "test_*", "declared": [{"function": "test_*"}]}, PRESETS,
                 id="in an inline map"),
    pytest.param("old", {"old": {"files": ["test_*.py"], "functions": "test_*", "declared": [{"function": "test_*"}]}},
                 id="in a preset"),
])
def test_the_functions_of_testing_are_refused_with_the_forms_that_declare_a_test(testing, presets):
    assert problems(layered(testing=testing), presets=presets) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use beside, declared, files, globals, mocks, preset, shared, skips, tables"]


def test_functions_written_in_place_of_declared_is_refused_with_its_hint_and_declared_is_missing():
    assert problems(layered(testing={"files": ["test_*.py"], "functions": "test_*"})) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use beside, declared, files, globals, mocks, preset, shared, skips, tables",
        "layered.yaml: testing: missing `declared`"]


def test_functions_beside_a_preset_is_refused_with_its_hint_alone():
    assert problems(layered(testing={"preset": "pytest", "functions": "test_*"})) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use beside, declared, files, globals, mocks, preset, shared, skips, tables"]


KNOWN = PART_USE


def test_path_and_folders_inside_a_node_say_how_the_tree_writes_them_and_nothing_else_of_the_node():
    document = layered()
    part_of(document, "shared")["path"] = "shared"
    part_of(document, "api")["folders"] = {"a": "n"}
    assert problems(document) == [
        "layered.yaml: parts.api: unknown key 'folders': moved in 0.3.0: write each folder below the part as a key "
        f"ending in /, with its note as its value; use {KNOWN}",
        "layered.yaml: parts.shared: unknown key 'path': moved in 0.3.0: a part is the folder or file it is written "
        f"as under parts: drop it; use {KNOWN}"]


OLD = {"domain": {"path": "modules/<module>/domain", "role": "r", "imports": {"may": ["nothing"]}},
       "platform": {"path": "platform", "role": "r"},
       "controller": {"path": "modules/<module>/application/controller.py", "role": "r"},
       "kernel-logic": {"path": "kernel/logic", "role": "r"}}
OLD_LINES = [
    "layered.yaml: parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the "
    f"folder it lies in (modules/<module>/); use {KNOWN}",
    "layered.yaml: parts.platform: unknown key 'path': moved in 0.3.0: write the part as the folder platform/: at the "
    f"top of parts; use {KNOWN}",
    "layered.yaml: parts.controller: unknown key 'path': moved in 0.3.0: write the part as the file controller.py: "
    f"under the folder it lies in (modules/<module>/application/); use {KNOWN}",
    "layered.yaml: parts.kernel-logic: unknown key 'path': moved in 0.3.0: write the part as the folder logic/: with "
    f"name: kernel-logic, under the folder it lies in (kernel/); use {KNOWN}"]


def test_an_old_flat_profile_is_refused_with_one_line_per_part_and_no_other_problem():
    assert problems(layered(parts=OLD, colour=1, layers={"a": ["nothing"]})) == OLD_LINES


def test_a_profile_mixing_tree_keys_with_an_old_part_gets_only_the_old_part_s_line():
    assert problems(layered(parts={"core/": {"rol": "x"}, "platform": {"path": "platform", "role": "r"}})) == [
        OLD_LINES[1]]
