# 6.6 rules: scenario-coverage works for a framework with no table form

Card: 0bfa131b-0afc-483e-aee4-53087ee5685b (subtask of 15e55316), release step 20 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below "the note").
This card implements the note's 3.1 (lines 253-272), 3.2 (lines 274-281), 8 item 6 (lines 407-408) and 9.2
(lines 425-427), under the defaults at lines 27-28.

## Goal

A profile whose test framework writes no table form (`testing.tables: []`, or `tables` left out) can switch on
`guards.scenario-coverage`. The guard then checks the standalone rule alone: every variant of a use case's union is
named by a test of the use case's test file; a variant named only by tests that never assert is `weak`. The guard's
`columns` is refused for such a framework, and `tiers.<tier>.plain_tables` stays refused, in new words. Every profile
with a table form (pytest, the loop form, the bundled cli, web and xarch profiles) behaves byte for byte as today.

## Inherited constraints

- "Left out means no form": `tables` absent and `tables: []` are the same framework, with no form; no hidden pytest
  default (note line 445).
- With no form, "named by at least one test" is enough, with `weak` for tests that never assert; not one test per
  variant (note lines 27, 270-272).
- `plain_tables` is refused, never accepted and silent, for a framework with no form (note lines 28, 276-280, 447).
- The guard's `columns` stays required with a form; `file` stays required in both cases (note lines 264-266).
- The message "no table test whose parameters are given, when, then" stays for a framework with forms, so the
  recorded findings of `examples-cli.json` and `examples-web.json` do not move (note lines 268-269, 355).
- The golden docs `docs/{cli,web,xarch}/testing.md` stay byte for byte (note line 353; card: regenerated and their
  diff read, never edited by hand). They keep pytest forms (note lines 38-40).
- The checking code (`scenarios.py`) names no form kind (`decorator`, `call`, `loop`) (note lines 430-431, 440-441).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; recorded corpora untouched; Python only in the reader adapter and the data files under
  `xarch/architectures/presets/`; `.claude/` out of commits; nothing pushed; README and CHANGELOG lines under
  `[Unreleased]`.

## Behavior

"With a form" below means `testing` was read and its framework writes at least one table form. "With no form" means
`testing` was read and writes none. When `testing` is missing or refused, its own problem stands
(`missing \`testing\`: ...` or the `testing: ...` problem) and the rules below add nothing about forms.

### B1. Parsing `guards.scenario-coverage`

1. With a form: exactly as today. All five keys `results`, `tier`, `suffix`, `columns`, `file` are required; a
   missing one gives `guards.scenario-coverage: missing \`<key>\``, in the same order and words as today (sorted by
   key name). The parsed guard is `ScenarioCoverage(results, tier, suffix, (state, command, result), file)`.
2. With no form, `columns` absent: the guard is accepted. `results`, `tier`, `suffix` and `file` are required and
   checked as today. The parsed guard carries `columns == ()`.
3. With no form, `columns` written (any value, including a valid list of three): one problem,
   `guards.scenario-coverage.columns: drop \`columns\`: the framework writes no table, so each result is its own test`,
   and no guard is built. Its value is not otherwise checked.
4. The old refusal `guards.scenario-coverage: needs \`testing.tables\`: the forms a table of cases is written in, such
   as [{decorator, columns_from, rows, row, id}]` is never given any more.
5. `testing` missing or refused: as today (`columns` required in the missing-keys list; no guard built).
6. `profile explain guards.scenario-coverage.columns` says `required: no`, and its accepts text says it is required
   when `testing.tables` writes a form and refused when it writes none.

### B2. Parsing `tiers.<tier>.plain_tables`

1. With a form: accepted as today.
2. With no form and `plain_tables: true`: one problem per such tier,
   `tiers.<tier>.plain_tables: needs a table form: the framework <framework> writes none in \`testing.tables\``,
   where `<framework>` is `` `<preset>` `` (backticked) when `testing` names a preset, and `of \`testing\`` when
   `testing` is an inline map. Examples: `the framework \`pytest\` writes none` (a preset that wrote no form), and
   `the framework of \`testing\` writes none` (an inline map).
3. `testing` missing or refused: no `plain_tables` problem is added (today one was; the `testing` problem already
   stands and the framework has no name to give). This is the only change to an error path besides the new words.
4. `plain_tables: false` or absent: no problem in any case.

### B3. Checking: `violations` (scenario-coverage) with no form

For each use case found as today (a union `<Name><suffix>` of two names or more in an instance of the results part):

1. No test file of the guard's `file` name in the tier of that instance: the existing violation
   `<Union> has no test file <name> among the <tier> tests of <instance> (scenario-coverage)`, fix as today.
2. Each test file found: the test functions are its functions whose name matches `testing.functions` (methods of a
   class included, as the reader already gives them). A variant is named by a test when it is among a test
   function's `mentions`. For each variant named by no test function, in the union's order, one violation in the
   test file at line 1:
   `<Union> variant <V> is named by no test (scenario-coverage)`, fix `write a test naming <V>`.
   A function whose name does not match `testing.functions` names nothing.
3. No violation about tables, rows, ids or branches is ever given with no form: the "no table test whose parameters
   are ..." violation, the row checks and the branch check of table tests are reached only with a form.
4. The checking code never reads the guard's `columns` with no form (it is empty).

### B4. Checking: `weak` with no form

Unchanged rule, now reachable: a variant named by at least one test function, every one of which holds no assert
(`Function.asserts` false), is listed as
`Weak("scenario-coverage", <test file>, <line of the first such function>, "<Union> variant <V> is credited to
<names> by name only: no assert in their bodies")`, `<names>` the functions joined by `, `. One test function that
asserts is enough to make it not weak. A variant named by no test is a violation (B3.2), not weak.

### B5. Checking with a form

`violations`, `weak` and `plain` give exactly what they give today, for every input.

### B6. Docs

1. The guard line of the generated testing docs for a framework with no form reads:
   ``- `scenario-coverage`: every variant of a union named `<Name><suffix>` in `<results part>` is named by a test of
   `<file uncased>` among the <tier> tests (section 5.2); the framework writes no table, so each result is its own
   test.`` It does not raise (today it would read `columns[-1]` of an empty tuple).
2. With a form, the line is byte for byte today's; `docs/{cli,web,xarch}/testing.md` regenerate with no diff.

### B7. Key texts, README, CHANGELOG

1. `keys.yaml`: `guards.scenario-coverage` accepts text says `columns` is written only when `testing.tables` writes a
   form, and with none every variant must be named by a test of the file; `guards.scenario-coverage.columns` accepts
   text as B1.6; `tiers.<tier>.plain_tables` ends "refused when `testing.tables` writes no form" in place of "needs
   `testing.tables`".
2. README: the `scenario-coverage` row of the checks table (README.md:326) adds "with no table form, a variant named
   by no test"; nothing else in README moves.
3. CHANGELOG `[Unreleased]`, `### Added`: one line: a framework with no table form (`tables: []` or left out) can use
   scenario-coverage, which then asks every variant to be named by a test (weak when none asserts); `columns` is
   refused for it and `plain_tables` says it needs a table form.

## Out of scope

- The test-only call-form framework and the `stub.yaml` of note 9.1 (card 6.7, release step 21's neighbour).
- A stricter no-form rule (one test per variant, a test naming no other variant): ruled out (note lines 270-272).
- Any change to the Python reader, to `asserts` (it stays the reader's `assert` statements), or to how test files are
  found (`file`, `{name:<case>}`).
- A `unittest.yaml` preset (note line 29); `testing.beside`, `testing.declared` (later steps).
- The recorded corpora, the golden docs and the bundled profiles: they must not move.

## Tests that prove it (written first)

Unit tier: pure functions over hand-built facts and in-memory documents; fast and the place each rule is pinned.
Bootstrap tier: the real Python reader and the real parser on files on disk; the only way to prove 9.2 end to end.

### Unit: `tests/modules/rules/application/logic/test_scenarios.py`

Build a no-form profile with `profile(framework=Framework(("test_*.py",), "test_*"))` and
`scenarios=ScenarioCoverage(..., (), "test_{name:snake}.py")` from `tests/modules/rules/builders.py`.

- U1 every variant named by some test function: `violations` is `[]`.
- U2 a variant named by none: exactly `modules/docs/application/test_publish.py:1: PublishResult variant Missing is
  named by no test (scenario-coverage)`, fix `write a test naming Missing` (prefix as the existing `FILE`).
- U3 both variants named by none: two violations, in the union's order.
- U4 a variant named only in a function whose name does not match `testing.functions`: violation as U2.
- U5 a function that holds a `Table` (facts built by hand) under a no-form framework: no table, row or branch
  violation; only the naming rule applies (proves B3.3 without reading `columns`).
- U6 `weak`: named only by a test with no assert is weak (exact `Weak`); one asserting test is enough; named by none
  is not weak.
- U7 no test file: the existing "has no test file" violation is given with no form.
- U8 existing cases with a form stay green unchanged (B5).

### Unit: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`

- P1 replace `NO_FORMS`: with `tables` deleted and with `tables: []`, a guard without `columns` parses with no problem
  and `columns == ()`.
- P2 with no form and `columns` written: exactly `[layered.yaml: guards.scenario-coverage.columns: drop \`columns\`:
  the framework writes no table, so each result is its own test]`, both for `tables` deleted and `tables: []`.
- P3 with a form and `columns` missing: `[layered.yaml: guards.scenario-coverage: missing \`columns\`]` (today's
  words, kept).
- P4 with no form and `file` missing: `missing \`file\`` still given; `columns` not listed as missing.
- P5 replace `PLAIN_NEEDS`: inline map with `tables` deleted and with `tables: []`: `layered.yaml:
  tiers.unit.plain_tables: needs a table form: the framework of \`testing\` writes none in \`testing.tables\``.
- P6 a preset with no form (a preset map given to the parser's presets) named by `testing: <preset>`:
  the message names `` `<preset>` ``.
- P7 `plain_tables: true` with `testing` missing: only the `missing \`testing\`` problem.

### Unit: docs line

- D1 in `tests/modules/spec/application/logic/test_testing.py` (it already asserts the guard line at line 219; or
  `test_docs_template.py`): a no-form framework and a guard with `columns == ()` render the B6.1 line exactly.
- D2 the golden-doc tests (`tests/bootstrap/test_docs_templates.py`), `test_bundled_guards.py`'s line (125) and
  `test_testing.py`'s existing line (219) stay green unchanged (B6.2).

### Unit: key texts

- K1 `profile explain guards.scenario-coverage.columns` reports `required: no` (in the existing explain tests,
  `tests/bootstrap/test_profile_explain.py` or `tests/modules/spec/application/test_explain.py`, whichever already
  asserts a key's `required`).

### Bootstrap: `tests/bootstrap/test_no_table_form.py` (new, note 9.2)

Modelled on `tests/bootstrap/test_loop_tables.py`: an inline profile string, files on disk, `source_check` from
`tests/bootstrap/project.py`. The framework is test-only and %UnitTest-like:
`testing: {files: ["*Test.py"], functions: "Test*", tables: []}`, guard `{results: contract, tier: integration,
suffix: Result, file: "{name:pascal}Test.py"}`, no `columns`. The app has `PublishResult = Published | Missing` in
`modules/docs/contract/__init__.py`; the test file `tests/modules/docs/application/PublishTest.py` is a class with one
method per case (`def TestPublished(self): assert Published()`), imports absolute `from app.modules.docs.contract
import ...`.

- E1 one asserting method per variant: no violation.
- E2 the `Missing` method removed: exactly `<file>:1: PublishResult variant Missing is named by no test
  (scenario-coverage); fix: write a test naming Missing`.
- E3 the `Missing` method kept but with no assert (`Missing()` alone): no violation, and the result's enforcement (`AppChecked.enforcement`, its `weak`
  list) holds the B4 entry for `Missing` at that method's line.
- E4 the same profile with `columns: [given, when, then]` added: loading it is refused, and the refusal holds the
  B1.3 problem (asserted the way the existing bootstrap tests assert a refused profile, e.g. the problems `profile
  check` reports for the file).
- E5 the same profile with `plain_tables: true` on the tier: refused the same way, with the B2.2 problem
  (`of \`testing\``).

### Gates

`uv run pytest -q` (background, read at the end), `uv run xarch check`, `uv run xarch check --strict`,
`uv run ruff check`, `uv run xarch profile check architecture.yaml`, each green on this branch alone. The recorded
corpora tests and golden-doc tests pass with no edit to `tests/bootstrap/corpora/` or `docs/{cli,web,xarch}/`.

## Notes for the planner

- `ScenarioCoverage.columns` (`xarch/profile_values/testing.py:77`) becomes `tuple[str, ...]`, `()` with no form;
  keep the field order so positional construction and the `match` in `docs_template.py:483` still work; update the
  docstring.
- `Key(SCENARIO_COVERAGE, "columns", True, ...)` (`xarch/modules/spec/domain/key_table.py:179`) becomes not
  required; `_scenario_coverage` (`profile_parsing.py:771-796`) adds `columns` to the required keys itself when the
  framework writes a form or `testing` is None, keeping the sorted order of today's missing-key problems.
- `_Testing` (`profile_parsing.py:148`) needs the preset's name ("" for an inline map) for B2.2; the refusal is at
  `profile_parsing.py:203-205`.
- `scenarios.py`: `_covered` and `_credited` take the no-form path when `profile.framework.tables` is empty; the
  existing `_rows`/`guard.columns[-1]` path is reached only with a form. Do not write form kind names in it
  (`tests/architecture/test_language_seam.py`). Update the module docstring for the no-form rule.
- Docs line: `docs_template.py:476-490`. Golden docs regenerated by the repo's generator, diff read, expected empty.

---

# 6.6 rules: scenario-coverage for a framework with no table form, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A profile whose test framework writes no table form can switch on `guards.scenario-coverage`, which then
asks every variant of a use case's union to be named by a test of its test file (weak when none of them asserts),
refuses the guard's `columns`, and refuses `plain_tables` in new words; every profile with a form behaves as today.

**Architecture:** The parser (`profile_parsing.py`) decides whether `columns` is required from whether `testing`
writes a form, and remembers the preset's name for the `plain_tables` message. The checker (`scenarios.py`) branches
on `profile.framework.tables` being empty: the empty case uses only `Function.mentions` and `Function.asserts`, and
never reaches `_rows`, `_branches` or `guard.columns`. The docs line (`docs_template.py`) gets a no-form sentence.

**Tech Stack:** Python 3, pytest, ruff, `uv`; xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/6-6-rules-scenario-0bfa131b.md` (prepended above; read both).

## Global Constraints

- No comments in xarch's code (`#` comments); docstrings only. Tests may not hold comments either (the repo's own
  `no-comments` guard covers tests).
- Never run `ruff --fix`. Fix lint by hand.
- Tests are written first, and each is run and seen to FAIL before the code is written.
- Examples are simple, with absolute `app.` imports.
- `scenarios.py` holds no string literal equal to `decorator`, `call` or `loop` (`tests/architecture/test_table_forms.py`).
- Python is named only in the reader adapter and the data files under `xarch/architectures/presets/`.
- Untouched: `tests/bootstrap/corpora/`, `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`, the
  bundled profiles, the Python reader.
- `.claude/` stays out of commits. Nothing is pushed.
- README and CHANGELOG lines go under `## [Unreleased]`.
- Exact message texts (copy verbatim):
  - `guards.scenario-coverage.columns: drop \`columns\`: the framework writes no table, so each result is its own test`
  - `tiers.<tier>.plain_tables: needs a table form: the framework <framework> writes none in \`testing.tables\``,
    `<framework>` = `` `<preset>` `` for a named preset, `of \`testing\`` for an inline map.
  - `<Union> variant <V> is named by no test (scenario-coverage)`, fix `write a test naming <V>`, at line 1 of the
    test file.
  - Docs line: ``- `scenario-coverage`: every variant of a union named `<Name><suffix>` in `<results part>` is named by
    a test of `<file uncased>` among the <tier> tests (section 5.2); the framework writes no table, so each result is
    its own test.``
- Gates, each green on this branch alone: `uv run pytest -q` (over two minutes: background with `timeout`, read at the
  end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
  `uv run xarch profile check architecture.yaml`.
- Process safety: never `pkill`/`killall`/`kill` by pattern. Stop a stuck test with `timeout`.

## Review Focus

1. `columns` written as `null` (or any non-list) under a framework with no form: refused with the one `drop` problem,
   not the "must be a list of three names" problem. Pinned in Task 1 (P2 param `None` and `"anything"`).
2. A framework named by preset (`testing: pytest` resolving to a map with no `tables`) with the guard and no
   `columns`: loads, exactly as an inline map does. Pinned in Task 1
   (`test_scenario_coverage_under_a_preset_with_no_table_form_takes_no_columns`).
3. A variant that is imported by the test file but named in no test's body: still a violation (an import is no
   test). Pinned in Task 4 (E2: `Missing` stays imported).
4. Two test files of the use case's name in the same instance and tier: each is checked on its own, so a variant
   named in one file only is reported for the other. Pinned in Task 2 (`test_each_test_file_of_a_use_case_names_every_variant_on_its_own`).
5. A test function holding a table (hand-built facts) under a no-form framework: no IndexError from
   `profile.framework.tables[table.form]`, no row or branch problem, and its `mentions` count like any test's. Pinned
   in Task 2 (U5 cases, and the weak case "a test holding a table is a test like any other").

---

## File Structure

- Modify `xarch/profile_values/testing.py` (ScenarioCoverage: `columns: tuple[str, ...]`, docstring).
- Modify `xarch/modules/spec/domain/key_table.py:179` (columns not required).
- Modify `xarch/modules/spec/application/logic/profile_parsing.py` (`_Testing.preset`, `_testing`, plain_tables
  refusal, `_scenario_coverage`, a helper `_framework_named`).
- Modify `xarch/architectures/presets/format/keys.yaml` (three accepts texts).
- Modify `xarch/modules/rules/application/logic/scenarios.py` (no-form path, `_tests`, `_named`, docstring).
- Modify `xarch/modules/spec/application/logic/docs_template.py:482-490` (no-form line).
- Modify `README.md:326`, `CHANGELOG.md` (`[Unreleased]` / `### Added`).
- Tests: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`,
  `tests/modules/spec/application/test_explain.py`, `tests/modules/rules/application/logic/test_scenarios.py`,
  `tests/modules/spec/application/logic/test_testing.py`, new `tests/bootstrap/test_no_table_form.py`.

---

### Task 1: Parsing: `columns` only with a form, `plain_tables` in new words, key texts

**Files:**
- Modify: `xarch/profile_values/testing.py:69-79`
- Modify: `xarch/modules/spec/domain/key_table.py:179`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:146-152` (`_Testing`), `:203-205` (plain_tables
  refusal), `:528-546` (`_testing`), `:771-796` (`_scenario_coverage`)
- Modify: `xarch/architectures/presets/format/keys.yaml:588-594`, `:951-958`, `:1095-1099`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py:569-578` and `:639-650`
- Test: `tests/modules/spec/application/test_explain.py` (new test after the one at line 224)

**Interfaces:**
- Consumes: nothing new.
- Produces: `ScenarioCoverage.columns: tuple[str, ...]`, `()` when `testing` writes no form (Tasks 2, 3, 4 rely on
  this). The parsed `Architecture.framework.tables == ()` for such a framework (already so today).

- [ ] **Step 1: Write the failing parsing tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, replace the block from
`NO_FORMS = (...` (line 569) through the end of
`test_scenario_coverage_reads_its_forms_from_the_framework_and_says_so_when_there_is_none` (line 578) with:

```python
DROP_COLUMNS = ("layered.yaml: guards.scenario-coverage.columns: drop `columns`: the framework writes no table, so "
                "each result is its own test")
NO_COLUMNS = {key: value for key, value in GUARDS["scenario-coverage"].items() if key != "columns"}
"""The guard scenario-coverage as a framework with no table form writes it: every key but `columns`."""


def no_form(document: dict, tables: str) -> dict:
    """The document, its framework writing no table form: `tables` left out ("absent") or written empty ("empty")."""
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
    presets = {"pytest": {"files": ["test_*.py"], "functions": "test_*"}}
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
        "layered.yaml: testing: no preset 'odd': use pytest, or write the map {files, functions}",
        "layered.yaml: guards.scenario-coverage: missing `columns`"]
```

Then replace the block from `PLAIN_NEEDS = (...` (line 639) through the end of
`test_a_tier_whose_table_tests_are_plain_says_so_and_needs_the_form_of_a_table` (line 650) with:

```python
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
    presets = {"pytest": {"files": ["test_*.py"], "functions": "test_*"}}
    assert problems(document, presets=presets) == [
        "layered.yaml: tiers.unit.plain_tables: needs a table form: the framework `pytest` writes none in "
        "`testing.tables`"]


def test_a_plain_tier_with_no_framework_is_told_only_what_is_wrong_with_testing():
    document = covered()
    del document["testing"]
    document["tiers"]["unit"]["plain_tables"] = True
    assert problems(document) == [
        "layered.yaml: missing `testing`: `tiers` must recognise a test file by its name: write testing: <preset>, "
        "or testing: {files: [<pattern>, ...], functions: <pattern>}"]
    document["testing"] = "odd"
    assert problems(document) == [
        "layered.yaml: testing: no preset 'odd': use pytest, or write the map {files, functions}"]
```

`ScenarioCoverage`, `TESTING`, `PRESETS`, `covered`, `parsed`, `problems` and `pytest` are already imported at the top
of the file (lines 3-20); `GUARDS` is defined at line 434. Add no import.

- [ ] **Step 2: Write the failing explain test**

In `tests/modules/spec/application/test_explain.py`, after
`test_the_tier_of_scenario_coverage_is_still_a_key_of_the_format` (ends line 227), add:

```python
def test_the_columns_of_scenario_coverage_are_required_only_where_the_framework_writes_a_table_form():
    found = explained("guards.scenario-coverage.columns")
    assert (found.key, found.where, found.required) == (
        "guards.scenario-coverage.columns", "guards.scenario-coverage", False)
    assert found.accepts == ("[<state>, <command>, <result>]: required when `testing.tables` writes a form, refused "
                             "when it writes none")
    assert explained("tiers.<tier>.plain_tables").accepts.endswith("refused when `testing.tables` writes no form")
    assert "`columns` is written only when `testing.tables` writes a form" in explained(
        "guards.scenario-coverage").accepts
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/test_explain.py`
Expected: FAIL. The no-form cases fail with the old `needs \`testing.tables\`` problem; the preset-named and
refused-testing plain cases fail on the old plain words (or an extra old plain problem); the explain test fails on
`required` being `True`.

- [ ] **Step 4: Change `ScenarioCoverage`**

In `xarch/profile_values/testing.py`, replace the `ScenarioCoverage` class (lines 69-79) with:

```python
@dataclass(frozen=True)
class ScenarioCoverage:
    """The guard scenario-coverage: the part holding the result unions, the tier holding their tables, how a union's
    name ends, the names of the three parameters of a table (its state, its command and its result, in that order;
    none for a framework that writes no table form, where each result is its own test), and the name of a use case's
    test file, `{name:<case>}` standing for the use case in the case it writes."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, ...]
    file: str
```

- [ ] **Step 5: Make `columns` not required in the key table**

In `xarch/modules/spec/domain/key_table.py:179` replace

```python
    Key(SCENARIO_COVERAGE, "columns", True, rules=("scenario-coverage",)),
```

with

```python
    Key(SCENARIO_COVERAGE, "columns", rules=("scenario-coverage",)),
```

- [ ] **Step 6: Remember the preset's name in `_Testing`**

In `xarch/modules/spec/application/logic/profile_parsing.py` replace the `_Testing` class (lines 146-152) with:

```python
@dataclass(frozen=True)
class _Testing:
    """What `testing` says: how test files and functions are named and the table forms the framework writes, and,
    when written, how a mock is built; preset: the name of the preset it names, "" when written as a map."""
    framework: Framework
    mocks: StandIns | None
    preset: str = ""
```

In `_testing` (line 528 on), keep everything but capture the name before `value` is replaced and pass it on. The
function becomes:

```python
def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, validated the same."""
    preset = ""
    if isinstance(value, str):
        if value not in presets:
            names = f"use {', '.join(sorted(presets))}, or write" if presets else "write"
            problems.append(f"testing: no preset {value!r}: {names} the map {_PRESET_MAP}")
            return None
        preset, value = value, presets[value]
    elif not isinstance(value, Mapping):
        problems.append(f"testing: must be a preset name or a mapping {_PRESET_MAP}: the patterns of a test file's name "
                        "and of a test function's")
        return None
    count = len(problems)
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language, TESTING)
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None or tables is None:
        return None
    return _Testing(replace(framework, tables=tables), mocks, preset)
```

Right after `_testing`, add:

```python
def _framework_named(testing: _Testing) -> str:
    """How a problem names the framework `testing` says: the preset it names, or `testing` itself when written out."""
    return f"`{testing.preset}`" if testing.preset else "of `testing`"
```

- [ ] **Step 7: Reword the `plain_tables` refusal**

In `parse_profile` replace lines 203-205:

```python
    problems += [f"tiers.{tier.name}.plain_tables: needs `testing.tables`, the forms a table of cases is written in, "
                 "to know a table test" for tier in tiers
                 if tier.plain_tables and (testing is None or not testing.framework.tables)]
```

with:

```python
    problems += [f"tiers.{tier.name}.plain_tables: needs a table form: the framework {_framework_named(testing)} "
                 "writes none in `testing.tables`" for tier in tiers
                 if tier.plain_tables and testing is not None and not testing.framework.tables]
```

- [ ] **Step 8: `_scenario_coverage` takes `columns` only with a form**

Replace the body of `_scenario_coverage` from `count = len(problems)` (line 781) through the final `return` (line 796)
with:

```python
    count = len(problems)
    forms = testing is None or bool(testing.framework.tables)
    required = {*required_of(SCENARIO_COVERAGE), *(("columns",) if forms else ())}
    problems += ck.unknown_keys(spec, names_of(SCENARIO_COVERAGE), where, SCENARIO_COVERAGE)
    problems += [f"{where}: missing `{key}`" for key in sorted(required) if key not in spec]
    if not forms and "columns" in spec:
        problems.append(f"{where}.columns: drop `columns`: the framework writes no table, so each result is its own "
                        "test")
    if len(problems) != count:
        return None
    ck.scenario_places(spec["results"], spec["tier"], spec["suffix"], parts, declared, tiers, where, problems,
                       language)
    columns = ck.column_names(spec["columns"], f"{where}.columns", problems, language) if forms else ()
    framework = testing.framework if testing is not None else None
    file = ck.use_case_file(spec["file"], framework, f"{where}.file", problems, language, "testing.files")
    if len(problems) != count or columns is None or file is None or testing is None:
        return None
    return ScenarioCoverage(spec["results"], spec["tier"], spec["suffix"], columns, file)
```

The `if not isinstance(spec, Mapping)` block above it (lines 774-779) stays as it is.

- [ ] **Step 9: Change the key texts**

In `xarch/architectures/presets/format/keys.yaml`:

`tiers.<tier>.plain_tables` (line 590 on): replace its `accepts` with

```yaml
    accepts: >-
      true: no test function of the tier that holds a table of cases (as `testing.tables` writes one) holds, in its body,
      a statement that branches (the language's `branching`) or an expression that chooses between values (its
      `branching_expressions`), as scenario-coverage holds the tables of a use case: the odd case is a test of its own;
      refused when `testing.tables` writes no form
```

`guards.scenario-coverage` (line 953 on): replace its `accepts` with

```yaml
    accepts: >-
      {results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], file: <name>}: every
      variant of a union named <Name><suffix> in a results part is the result column of a row of the table in its use
      case's test file <file> (`{name:<case>}` is <Name> in that case: snake, kebab, camel or pascal) of that tier, or
      is named by a standalone test of it; every row is written as its form in `testing.tables` writes one, with a literal id,
      and a table test has no branching; `columns` is written only when `testing.tables` writes a form, and with none
      every variant must be named by a test of the file; read from the syntax tree, never run
```

`guards.scenario-coverage.columns` (line 1097): replace

```yaml
    accepts: "[<state>, <command>, <result>]"
```

with

```yaml
    accepts: "[<state>, <command>, <result>]: required when `testing.tables` writes a form, refused when it writes none"
```

- [ ] **Step 10: Run the tests to verify they pass**

Run: `uv run pytest -q tests/modules/spec tests/bootstrap/test_profile_explain.py tests/bootstrap/test_architecture_files.py`
Expected: PASS. Then run
`uv run pytest -q tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_libraries_and_guards.py`
and expect PASS unchanged (they cover the guard with a form).

- [ ] **Step 11: Lint**

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 12: Commit**

```bash
git add xarch/profile_values/testing.py xarch/modules/spec/domain/key_table.py \
  xarch/modules/spec/application/logic/profile_parsing.py xarch/architectures/presets/format/keys.yaml \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/test_explain.py
git commit -m "scenario-coverage takes no columns under a framework that writes no table form and refuses them, and plain_tables says it needs a table form, naming the framework

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Checking: every variant named by a test, with no form

**Files:**
- Modify: `xarch/modules/rules/application/logic/scenarios.py` (module docstring, `violations`, `_credited`,
  `_covered`, new `_tests`, new `_named`)
- Test: `tests/modules/rules/application/logic/test_scenarios.py` (append at the end)

**Interfaces:**
- Consumes: `ScenarioCoverage.columns == ()` with no form (Task 1); `Profile.framework.tables` (`()` with no form).
- Produces: `violations(app, tests, profile)` and `weak(app, tests, profile)` keep their signatures; with
  `profile.framework.tables == ()` they give only the "has no test file", "is named by no test" violations and the
  `Weak` entries of B4.

- [ ] **Step 1: Write the failing tests**

At the top of `tests/modules/rules/application/logic/test_scenarios.py`, change the import line

```python
from xarch.profile_values.testing import Place, RowId, TableForm
```

to

```python
from xarch.profile_values.testing import Framework, Place, RowId, TableForm
```

Append at the end of the file:

```python
NO_FORM = profile(framework=Framework(("test_*.py",), "test_*"), scenarios=replace(PROFILE.scenarios, columns=()))
"""PROFILE under a framework that writes no table form: the guard has no columns, and each result is its own test."""
PUBLISHED = Function(8, "test_published", mentions=frozenset({"Published"}), asserts=True)
MISSING = Function(12, "test_missing", mentions=frozenset({"Missing"}), asserts=True)


def unnamed(variant: str, file: str = FILE) -> tuple[str, str]:
    return (f"{file}:1: PublishResult variant {variant} is named by no test (scenario-coverage)",
            f"write a test naming {variant}")


def no_form(*tests) -> list[tuple[str, str]]:
    return [(str(v), v.fix) for v in violations([RESULTS], list(tests), NO_FORM)]


@pytest.mark.parametrize("functions, expected", [
    pytest.param([PUBLISHED, MISSING], [], id="every variant named by a test of the file is covered"),
    pytest.param([Function(8, "test_both", mentions=frozenset({"Published", "Missing"}), asserts=True)], [],
                 id="one test may name every variant"),
    pytest.param([PUBLISHED], [unnamed("Missing")], id="a variant named by no test is reported at the top of the file"),
    pytest.param([], [unnamed("Published"), unnamed("Missing")],
                 id="each variant named by no test is reported, in the union's order"),
    pytest.param([PUBLISHED, replace(MISSING, name="check_missing")], [unnamed("Missing")],
                 id="a function the test pattern does not match names nothing"),
    pytest.param([PUBLISHED, replace(MISSING, owner="PublishTests")], [],
                 id="a method of a class is a test like a function"),
    pytest.param([Function(8, "test_publish", (table(row("Gone", written=False, id=None)),),
                           mentions=frozenset({"Published", "Missing"}), blocks=((14, "if"), (15, "for")),
                           expressions=((16, "if"),))], [],
                 id="a test holding a table is held to naming alone: no row, id or branch is checked"),
    pytest.param([Function(8, "test_publish", (Table(9, COLUMNS, None, 0, 0),), mentions=frozenset({"Published"}))],
                 [unnamed("Missing")], id="a table whose rows cannot be read is not reported, only the naming"),
    pytest.param([Function(8, "test_publish", (TABLE,), mentions=frozenset({"Published"}))], [unnamed("Missing")],
                 id="the rows of a table name no variant: only a test's body does"),
])
def test_scenario_coverage_under_a_framework_with_no_table_form(functions, expected):
    assert no_form(publish_tests(*functions)) == expected


def test_a_use_case_with_no_test_file_is_reported_with_no_form_as_with_one():
    assert no_form() == [("app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py "
                          "among the integration tests of docs (scenario-coverage)",
                          "write test_publish.py among the integration tests of docs")]


def test_each_test_file_of_a_use_case_names_every_variant_on_its_own():
    nested = "modules/docs/application/services/test_publish.py"
    assert no_form(publish_tests(PUBLISHED, MISSING), publish_tests(PUBLISHED, path=nested)) == [
        unnamed("Missing", "tests/modules/docs/application/services/test_publish.py")]


@pytest.mark.parametrize("functions, expected", [
    pytest.param([PUBLISHED, replace(MISSING, asserts=False)],
                 [Weak("scenario-coverage", FILE, 12, "PublishResult variant Missing is credited to test_missing by "
                                                      "name only: no assert in their bodies")],
                 id="a variant named only by a test with no assert is weak"),
    pytest.param([PUBLISHED, replace(MISSING, asserts=False),
                  Function(20, "test_missing_again", mentions=frozenset({"Missing"}), asserts=True)], [],
                 id="one test that asserts is enough"),
    pytest.param([PUBLISHED], [], id="a variant named by no test is a violation, not weak"),
    pytest.param([Function(8, "test_publish", (TABLE,), mentions=frozenset({"Published", "Missing"}))],
                 [Weak("scenario-coverage", FILE, 8, "PublishResult variant Published is credited to test_publish by "
                                                     "name only: no assert in their bodies"),
                  Weak("scenario-coverage", FILE, 8, "PublishResult variant Missing is credited to test_publish by "
                                                     "name only: no assert in their bodies")],
                 id="a test holding a table is a test like any other, its rows covering nothing"),
])
def test_weak_under_a_framework_with_no_table_form(functions, expected):
    assert weak([RESULTS], [publish_tests(*functions)], NO_FORM) == expected
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py`
Expected: FAIL. The new no-form cases fail with `IndexError` (from `profile.framework.tables[table.form]` in `_rows`)
or with the `no table test whose parameters are` violation (`, ` joined over no columns); the no-test-file case may
already pass. The existing cases above stay green.

- [ ] **Step 3: Implement the no-form path**

In `xarch/modules/rules/application/logic/scenarios.py`:

(a) In the module docstring, after the paragraph that ends `... is the table and no branch of its test.` (before the
`plain holds ...` paragraph), add this paragraph:

```text
A framework that writes no table form (its `testing.tables` empty) has no table to read, and each result is its own
test: the guard has no columns, and every variant of the union must be named in the body of a test function of the
file, its name matching the profile's pattern; a variant named by none is a violation at the top of the file. No row,
id or branch is checked then, whatever the facts of a function hold.
```

and replace the last paragraph (`weak lists, ...`) with:

```text
weak lists, without failing, a variant met to the letter only: one no row covers, credited only to standalone tests
of the file that name it (to any test function of the file that names it, for a framework that writes no table form),
none of which holds an `assert` statement in its body.
```

(b) In `violations`, replace

```python
        for test in files:
            found += _covered(test, union.name, union.members, guard, profile)
```

with

```python
        for test in files:
            found += (_covered(test, union.name, union.members, guard, profile) if profile.framework.tables
                      else _named(test, union.name, union.members, profile))
```

(c) Add, right after `_given_id`:

```python
def _tests(test: SourceFile, profile: Profile) -> list[Function]:
    """The test functions of a test file: those whose name matches the framework's pattern."""
    assert profile.framework is not None
    return [f for f in test.functions if fnmatchcase(f.name, profile.framework.functions)]


def _named(test: SourceFile, union: str, variants: tuple[str, ...], profile: Profile) -> list[Violation]:
    """Each variant no test function of the file names, for a framework that writes no table form, in the union's
    order, at the top of the file."""
    named = set().union(*(f.mentions for f in _tests(test, profile)))
    return [Violation(test.name, 1, f"{union} variant {v} is named by no test ({RULE})", RULE,
                      f"write a test naming {v}") for v in variants if v not in named]
```

(d) Replace `_credited` with:

```python
def _credited(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
              profile: Profile) -> list[Weak]:
    assert profile.framework is not None
    functions = _tests(test, profile)
    covered: set[str] = set()
    standalone = functions
    if profile.framework.tables:
        for function in functions:
            for table in function.tables:
                if set(guard.columns) <= set(table.columns):
                    _rows(table, union, variants, guard, profile, covered)
        standalone = [f for f in functions if not f.tables]
    found: list[Weak] = []
    for variant in variants:
        credit = [f for f in standalone if variant in f.mentions]
        if variant not in covered and credit and not any(f.asserts for f in credit):
            names = ", ".join(f.name for f in credit)
            found.append(Weak(RULE, test.name, credit[0].line, f"{union} variant {variant} is credited to {names} by "
                                                               "name only: no assert in their bodies"))
    return found
```

(e) In `_covered`, replace its first four lines

```python
    columns = guard.columns
    assert profile.framework is not None
    functions = [f for f in test.functions if fnmatchcase(f.name, profile.framework.functions)]
    tables = [(f, t) for f in functions for t in f.tables if set(columns) <= set(t.columns)]
```

with

```python
    columns = guard.columns
    functions = _tests(test, profile)
    tables = [(f, t) for f in functions for t in f.tables if set(columns) <= set(t.columns)]
```

Nothing else in `_covered`, `_rows`, `_branches`, `_result` or `plain` changes. Write no string literal equal to
`decorator`, `call` or `loop`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py tests/architecture/test_table_forms.py`
Expected: PASS (every case, old and new).

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/application/logic/scenarios.py tests/modules/rules/application/logic/test_scenarios.py
git commit -m "Under a framework that writes no table form, scenario-coverage asks every variant to be named by a test of the use case's file, weak when none of them asserts, and checks no row, id or branch

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Docs: the guard line for a framework with no form

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:482-490`
- Test: `tests/modules/spec/application/logic/test_testing.py` (new test after
  `test_the_guards_lines_say_the_names_of_the_framework_the_file_declares`, which ends at line 229)

**Interfaces:**
- Consumes: `ScenarioCoverage.columns == ()` and `Architecture.framework.tables == ()` with no form (Task 1).
- Produces: `_guard_line` returns the B6.1 sentence for such a framework.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/application/logic/test_testing.py`, after
`test_the_guards_lines_say_the_names_of_the_framework_the_file_declares`, add:

```python
def test_the_scenario_coverage_line_of_a_framework_with_no_table_form_says_each_result_is_its_own_test():
    guard = {key: value for key, value in SCENARIOS.items() if key != "columns"}
    assert guard_lines(testing={"tables": []}, guards={"scenario-coverage": guard})[0] == (
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `api/` is named by a test of "
        "`test_<name>.py` among the integration tests (section 5.2); the framework writes no table, so each result "
        "is its own test.")
```

(`guard_lines` at line 210 merges `testing` changes into the document's framework and replaces the guard; it returns
the last two lines of `{{guards}}`, the scenario-coverage line first.)

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_testing.py -k no_table_form`
Expected: FAIL with `IndexError: tuple index out of range` (from `columns[-1]` in `docs_template.py:488`).

- [ ] **Step 3: Implement the no-form line**

In `xarch/modules/spec/application/logic/docs_template.py`, replace the `case ScenarioCoverage(...)` arm (lines
482-490) with:

```python
        case ScenarioCoverage(results, tier, suffix, columns, file):
            assert architecture.framework is not None
            part = docs_name(architecture, architecture.parts[results])
            if not architecture.framework.tables:
                return (f"`scenario-coverage`: every variant of a union named `<Name>{suffix}` in `{part}` is named "
                        f"by a test of `{_uncased(file)}` among the {tier} tests (section 5.2); the framework writes "
                        "no table, so each result is its own test.")
            shown = ", ".join(f"`{c}`" for c in columns)
            member = architecture.language.checked.member
            rows = " or ".join(_row_phrase(form, member) for form in architecture.framework.tables)
            return (f"`scenario-coverage`: every variant of a union named `<Name>{suffix}` in "
                    f"`{part}` is the `{columns[-1]}` of a row of the "
                    f"table (columns {shown}) in `{_uncased(file)}` among the {tier} tests (section 5.2), "
                    f"or is named by a standalone test of that file; every row is {rows}, and a table test has no "
                    f"{_branches(architecture)}.")
```

The with-form text is unchanged character for character (only `docs_name(...)` moved into `part`).

- [ ] **Step 4: Run the tests to verify they pass, golden docs included**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_docs_template.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_bundled_guards.py`
Expected: PASS. Then run `git status --short docs/` and expect no
output: `docs/{cli,web,xarch}/testing.md` regenerate byte for byte (the golden-doc tests compare them) and are not
edited.

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/docs_template.py tests/modules/spec/application/logic/test_testing.py
git commit -m "The testing docs say scenario-coverage of a framework that writes no table form asks every variant to be named by a test, each result its own test

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: End to end under a test-only framework with no form, README, CHANGELOG, gates

**Files:**
- Create: `tests/bootstrap/test_no_table_form.py`
- Modify: `README.md:326`
- Modify: `CHANGELOG.md` (`## [Unreleased]` / `### Added`, after the last bullet, the one ending
  `(parts.<part>.imports.may.types_only)\`.` at line 85)

**Interfaces:**
- Consumes: Tasks 1-3; `source_check`, `line_of` from `tests/bootstrap/project.py`; `load_architecture` from
  `xarch.bootstrap.wiring`; `InvalidArchitecture` from `xarch.modules.spec.domain.errors`; `Weak` from
  `xarch.modules.rules.contract`; `AppChecked.enforcement.weak` (a tuple of `Weak`).
- Produces: nothing other tasks use.

- [ ] **Step 1: Write the test file**

Create `tests/bootstrap/test_no_table_form.py`:

```python
"""A test-only framework that writes no table form, its tests methods of a class (`*Test.py` files, `Test*` names),
read for real by the Python reader: scenario-coverage asks every variant of a use case's union to be named by a test
of its file, weak when none of them asserts, and the profile is refused when it writes the guard's columns or a tier's
plain_tables."""
from pathlib import Path

import pytest

from tests.bootstrap.project import line_of, source_check
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.rules.contract import AppChecked, Weak
from xarch.modules.spec.domain.errors import InvalidArchitecture

PROFILE = """name: untabled
testing:
  files: ["*Test.py"]
  functions: "Test*"
  tables: []
parts:
  contract:   {path: modules/<module>/contract, role: results, tests: integration}
  controller:
    path: modules/<module>/application/controller.py
    role: maps
    imports:
      may: [contract]
    tests: integration
tiers:
  integration:
    proves: a use case
    litmus: "Does it drive a controller?"
guards:
  scenario-coverage:
    results: contract
    tier: integration
    suffix: Result
    file: "{name:pascal}Test.py"
"""

APP = {
    "modules/docs/contract/__init__.py": "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "",
}

PUBLISHED = "    def TestPublished(self):\n        assert Published()\n"
MISSING = "    def TestMissing(self):\n        assert Missing()\n"
TESTED = "tests/modules/docs/application/PublishTest.py"


def publish(*methods: str) -> str:
    return "from app.modules.docs.contract import Missing, Published\n\n\nclass PublishTest:\n" + "\n".join(methods)


def checked(tmp_path: Path, test: str) -> AppChecked:
    files = {"app": APP, "tests": {"modules/docs/application/PublishTest.py": test}}
    for root, written in files.items():
        for rel, body in written.items():
            (tmp_path / root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / root / rel).write_text(body)
    (tmp_path / "untabled.yaml").write_text(PROFILE)
    return source_check(tmp_path / "app", str(tmp_path / "untabled.yaml"), tmp_path / "tests")


def check(tmp_path: Path, test: str) -> list[str]:
    return [f"{v}; fix: {v.fix}" for v in checked(tmp_path, test).violations]


def refused(tmp_path: Path, profile: str) -> tuple[Path, tuple[str, ...]]:
    path = tmp_path / "untabled.yaml"
    path.write_text(profile)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    return path, tuple(caught.value.problems)


def test_a_test_method_naming_each_variant_covers_the_use_case(tmp_path):
    assert check(tmp_path, publish(PUBLISHED, MISSING)) == []


def test_a_variant_no_test_names_is_reported_at_the_top_of_the_file_though_the_file_imports_it(tmp_path):
    assert check(tmp_path, publish(PUBLISHED)) == [
        f"{TESTED}:1: PublishResult variant Missing is named by no test (scenario-coverage); fix: write a test naming "
        "Missing"]


def test_a_variant_named_only_by_a_test_that_never_asserts_is_weak_and_no_violation(tmp_path):
    test = publish(PUBLISHED, "    def TestMissing(self):\n        Missing()\n")
    result = checked(tmp_path, test)
    assert [str(v) for v in result.violations] == []
    assert result.enforcement.weak == (
        Weak("scenario-coverage", TESTED, line_of(test, "def TestMissing"),
             "PublishResult variant Missing is credited to TestMissing by name only: no assert in their bodies"),)


def test_the_guard_s_columns_are_refused_under_a_framework_that_writes_no_table_form(tmp_path):
    path, problems = refused(tmp_path, PROFILE + "    columns: [given, when, then]\n")
    assert problems == (f"{path}: guards.scenario-coverage.columns: drop `columns`: the framework writes no table, so "
                        "each result is its own test",)


def test_plain_tables_is_refused_under_a_framework_that_writes_no_table_form(tmp_path):
    litmus = '    litmus: "Does it drive a controller?"\n'
    path, problems = refused(tmp_path, PROFILE.replace(litmus, litmus + "    plain_tables: true\n"))
    assert problems == (f"{path}: tiers.integration.plain_tables: needs a table form: the framework of `testing` "
                        "writes none in `testing.tables`",)
```

- [ ] **Step 2: Run it**

Run: `uv run pytest -q tests/bootstrap/test_no_table_form.py`
Expected: PASS, since Tasks 1-3 are in (this file proves the tasks together through the real reader and loader;
each rule was already seen RED in its unit test). To see that the file can fail, temporarily change the expected list
of `test_a_test_method_naming_each_variant_covers_the_use_case` to call `publish(PUBLISHED)`, see the one `Missing`
violation, and put it back. If the clean case reports a violation of another rule (for example `tiers`,
`must-import` or `test-tree`), fix the throwaway project (the profile string or `APP`) so the clean case is clean;
never loosen an expected message of scenario-coverage. If a refusal holds an extra problem, read it: it is a defect of
the profile string, unless it is a scenario-coverage or plain_tables problem, which is a defect of Task 1.

- [ ] **Step 3: README**

In `README.md:326`, replace the description cell of the `scenario-coverage` row

```text
| `scenario-coverage` | a variant of a result union with no row in its use case's test table, or a branch (a statement of `branching`, an expression of `branching_expressions`) in a table test's body; with `plain_tables`, in any table test of that tier | `guards.scenario-coverage`, `tiers.plain_tables` |
```

with

```text
| `scenario-coverage` | a variant of a result union with no row in its use case's test table, or a branch (a statement of `branching`, an expression of `branching_expressions`) in a table test's body; with `plain_tables`, in any table test of that tier; with no table form, a variant named by no test | `guards.scenario-coverage`, `tiers.plain_tables` |
```

Nothing else in README changes.

- [ ] **Step 4: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Added`, after the bullet that ends
`` <target>, which it used only as a type (parts.<part>.imports.may.types_only)`. `` (line 85) and before the blank
line and `### Changed`, add:

```markdown
- A test framework that writes no table form (`testing.tables: []`, or `tables` left out) can switch on
  `guards.scenario-coverage`: every variant of a use case's union must then be named by a test of its test file
  (`<Union> variant <V> is named by no test`), and a variant named only by tests that never assert is weak. The
  guard's `columns` is refused for such a framework (`drop \`columns\`: the framework writes no table, so each result
  is its own test`), and `tiers.<tier>.plain_tables` says `needs a table form: the framework <framework> writes none
  in \`testing.tables\``.
```

- [ ] **Step 5: Run the gates**

Run, in the background, and read the log at the end:
`timeout 1200 uv run pytest -q > /tmp/pytest-6-6.log 2>&1; echo "exit $?" >> /tmp/pytest-6-6.log`
Meanwhile run, each expected to exit 0:
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check`
- `uv run xarch profile check architecture.yaml`

Then: `tail -5 /tmp/pytest-6-6.log` — expected: all passed, `exit 0`.
And: `git status --short docs/ tests/bootstrap/corpora/` — expected: no output.

- [ ] **Step 6: Commit**

```bash
git add tests/bootstrap/test_no_table_form.py README.md CHANGELOG.md
git commit -m "A test-only framework with no table form is checked end to end: each variant named by a test of its class, weak when none asserts, and columns and plain_tables refused; README and CHANGELOG say so

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-Review

- Spec coverage: B1.1/B1.5 → Task 1 (P3, refused-testing test, existing `test_scenario_coverage_needs_all_its_keys`);
  B1.2 → P1 and the preset test; B1.3 → P2, E4; B1.4 → the NO_FORMS test removed and every no-form test now passes;
  B1.6 → K1. B2.1 → existing plain tests; B2.2 → P5, P6, E5; B2.3 → P7 (missing and refused); B2.4 → existing tests.
  B3.1 → `test_a_use_case_with_no_test_file_is_reported_with_no_form_as_with_one`; B3.2 → U2-U4, E2; B3.3/B3.4 →
  U5 cases (a table of unreadable rows, bad rows and branches, with `tables[table.form]` absent); B4 → U6, E3; B5 →
  every existing case in `test_scenarios.py`; B6.1 → D1; B6.2 → golden-doc and existing line tests in Task 3 Step 4;
  B7.1 → Task 1 Step 9 with K1; B7.2/B7.3 → Task 4 Steps 3-4. Gates → Task 4 Step 5.
- Placeholders: none; every code step has its code.
- Names: `_Testing.preset`, `_framework_named`, `_tests`, `_named`, `NO_FORM`, `no_form`, `unnamed`, `NO_COLUMNS`,
  `DROP_COLUMNS` are each defined where first used and used with the same spelling after.
- Note: the spec names `tests/architecture/test_language_seam.py`; the test that pins no form kind in `scenarios.py`
  is `tests/architecture/test_table_forms.py` (run in Task 2 Step 4).
<!-- task-pipeline: validated -->
