"""The table of retired names, read by every path that refuses an unknown name: the lookup by scope and name, and by
the address `profile explain` is typed with; every unknown key of a mapping, of the file, under `hints` and under
`guards` that has an entry under its scope gives one problem of its own with the entry's fixed text, ahead of today's
message for the others, which is unchanged. A table built for each test is set where the lookup reads it."""
import pytest

from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.application.logic.key_lookup import names_of, retired, retired_at
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
    NO_DUPLICATES,
    NO_TWINS,
    PAGE,
    PART,
    PASS_THROUGH,
    PLACEMENT,
    PROFILE,
    REVIEW,
    RULE_ID,
    SCENARIO_COVERAGE,
    SCOPES,
    TABLE,
    TESTING,
    TIER,
    TIER_DOCS,
    Retired,
)

RENAMED = "renamed in 0.3.0: write tier"
MOVED = "moved in 0.3.0: write uses: {never: <list>}"
MISPLACED = "a key of uses: write uses: {never: <list>}"
PART_USE = ("built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
            "package_only, path, role, shared, tests, types_only, untested, uses")
TIER_USE = "docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses"
PROFILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, "
               "parts, reserved, review, testing, tiers")
GUARD_USE = ("closed-tree, dead-code, no-comments, no-duplicates, no-twins, pass-through, private-imports, "
             "scenario-coverage, stand-ins")
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


def test_the_shipped_table_retires_the_part_key_tier_alone():
    renamed = "renamed in 0.3.0: write tests"
    assert (retired(PART, "tier"), retired_at("parts.tier"), retired_at("parts.<part>.tier")) == (renamed,) * 3
    assert (retired(TIER, "tier"), retired(SCENARIO_COVERAGE, "tier"), retired(PART, "tests")) == ("", "", "")


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
    assert unknown_keys({"path": "a", "banned": 1, "colour": 2}, names_of(PART), "parts.api", PART) == [
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
    assert unknown_keys({"role": "x", "path": "a"}, names_of(PART), "parts.api", PART) == []
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
    document["parts"]["api"] = ["x"]
    assert problems(document) == ["layered.yaml: parts.api: must be a mapping with `path` and `role`"]


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
    pytest.param(PART, writing(layered(), "parts", "api"),
                 f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}", id="a part"),
    pytest.param(TIER, writing(covered(), "tiers", "unit"),
                 f"tiers.unit: unknown key 'banned': {RENAMED}; use {TIER_USE}", id="a tier"),
    pytest.param(TESTING, writing(covered(), "testing"),
                 f"testing: unknown key 'banned': {RENAMED}; use files, functions, mocks, skips, table",
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
    pytest.param(TABLE, writing(covered(), "testing", "table"),
                 "testing.table: unknown key 'banned'", id="testing.table"),
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
