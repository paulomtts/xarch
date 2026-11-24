# 6.7 rules: test-only frameworks prove the table forms neutral

Card: 68122345-e3ca-4a41-9ae0-bebe8687a23c (subtask of 15e55316), release step 20 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3). Blocked by 6.6 (0bfa131b), which is on this branch.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below "the note").
This card implements the note's 9.1 (lines 420-424) and 8 item 7 (lines 409-411: README, CHANGELOG, `profile explain`
texts, re-grep). The optional grep test of section 9 (lines 433-434) already exists as
`tests/architecture/test_table_forms.py` and is kept unchanged.

## Goal

The suite holds a test-only framework data file, `tests/fakes/frameworks/stub.yaml`, that writes a `loop` form and a
`call` form, both with literal rows. Read by the real profile loader under the TypeScript-like test-only language
`brace`, it yields the forms the rules tests use; the scenario-coverage and `plain_tables` checks run on facts built by
hand for each form (`Table(form=1)` for the call form, `Table(form=0, runs=<line>)` for the loop form) and give
findings worded from `brace.yaml`'s `writing`, never Python's. Nothing in `xarch/` changes behaviour; this step adds
test data, tests, and the README and CHANGELOG lines that say neutrality is proved this way.

## What is already done (verified on this branch, not to be redone)

- Note 9.2, the no-form framework end to end: `tests/bootstrap/test_no_table_form.py` (card 6.6).
- Note 9.3, the loop form read by the real Python reader: `tests/bootstrap/test_loop_tables.py` (card 6.5).
- `tests/bootstrap/test_other_framework.py:12-18` already writes `tables: [{decorator: cases.table, ...}]` (note line
  431). Confirm it still passes; do not edit it.
- The optional grep test: `tests/architecture/test_table_forms.py` (no string literal `decorator`, `call`, `loop` in
  `scenarios.py`).
- `Table.form` / `Table.runs` (`xarch/modules/rules/domain/parsed.py:169-178`), wording from
  `profile.language.writing` in `scenarios._rows` (`scenarios.py`, `_rows`), `Writing.field_id`
  (`xarch/profile_values/language.py:52-77`).

## Inherited constraints

- Neutrality is not claimed with one data file: the test-only framework of 9.1 is part of the work and this step is not
  done without it (note lines 442-443, card "dodges").
- No TypeScript case and no `{...}` syntax typed into xarch's code or into a fix text: syntax comes only from a
  language's `writing`; the checking code reads `Table.form` only to find wording (note lines 440-441). The `{...}`
  template lives in the test-only `brace.yaml` data file only.
- The facts are built by hand, as `tests/modules/rules/builders.py` builds them; no TypeScript reader is written
  (note lines 418-424, 461-464).
- The checks run on a `Table` with `form=1`, rows written as literals with a field id, cells in column order
  (note lines 421-422).
- Python's reader does not supply `function.tables.call` and gains no `call` support (note line 449-450).
- Recorded corpora (`tests/bootstrap/corpora/`) and the golden docs `docs/{cli,web,xarch}/testing.md` do not move
  (note lines 353, 355, 451; card O8): golden docs are regenerated and their diff read, never edited by hand;
  expected diff empty.
- Re-grep of note 8 item 7 (lines 409-411): `grep -rn "testing.table\b\|CaseTable\|_snake_name" xarch tests docs
  README.md architecture.yaml` returns only the retired-keys entry, its refusal tests, and the 0.2.0 history (see B4
  for the exact allowed set on this branch).
- Project rules (card): no comments in xarch's code (YAML data files under `tests/fakes/` carry a header comment, as
  `brace.yaml` does); never `ruff --fix`; tests written first; examples simple, with absolute `app.` imports; recorded
  corpora edited by hand only, and not at all here; Python only in the reader adapter and the data files under
  `xarch/architectures/presets/`; `.claude/` out of commits; nothing pushed; README and CHANGELOG lines under
  `[Unreleased]` (review 3, O4, O5).

## Behavior

### B1. The test-only framework data file

`tests/fakes/frameworks/stub.yaml` (new directory beside `tests/fakes/languages/`), with a header comment in the style
of `brace.yaml` saying: a test-only framework that imitates Vitest-like tests, which no profile names and no reader
reads; it writes two forms, a loop of the test's body over a list literal (index 0) and a call that wraps the test
(index 1), both with literal rows; the tests load it to show the checks word a table by its form's slots and the
language's `writing`. Content, in this order:

```yaml
files: ["*.test.ts"]
functions: "test*"
tables:
  - loop: true
    columns_from: bound
    row: literal
    id: {position: 0}
  - call: ["vitest#it.each", "vitest#test.each"]
    rows: {position: 0}
    columns_from: fields
    row: literal
    id: {field: name}
```

(`vitest#it.each` is an outside name under Brace's member `#`; the bare `it.each` is refused by Brace's patterns:
`testing.tables.0.call: 'it.each' is not an outside name such as <package>#<name>`, verified by a probe.)

### B2. The test-only language gains its words

`tests/fakes/languages/brace.yaml` gains two keys, and its header comment one sentence saying it writes a row's id by a
field and branches with if, switch, try, for and while:

```yaml
branching: [if, switch, try, for, while]
writing: {call: "{callee}(...)", field: '{..., {field}: "{text}"}'}
```

Everything that already loads `brace.yaml` keeps passing (`tests/modules/spec/languages.py`,
`tests/modules/spec/application/logic/test_language_file.py`, `tests/architecture/test_language_seam.py`,
`tests/modules/rules/builders.py`). `tests/modules/rules/builders.py`'s `BRACE` (a hand-built `CheckedLanguage`) gains
`branching=tuple(BRACE_FILE["branching"])` and `writing=Writing(**BRACE_FILE["writing"])`, and its docstring names
them.

### B3. The loader reads stub.yaml into these forms

Given as the `stub` preset of a profile that writes `language: brace` and `testing: stub`, under the spec-side `BRACE`
of `tests/modules/spec/languages.py`, the profile loads and `framework` is exactly:

```python
Framework(("*.test.ts",), "test*", tables=(
    TableForm("bound", None, (), RowId(position=0), loop=True),
    TableForm("fields", Place(0), (), RowId(field="name"), call=(("vitest", "it", "each"), ("vitest", "test", "each"))),
))
```

Under the same language with `writing` emptied (`Writing()`), the profile is refused, and the problems hold exactly
`testing.tables.1.id: the language Brace does not write \`writing.field\`, how a row's id is given by a field`
(with the loader's source prefix, as the neighbouring tests assert it).

### B4. The checks on hand-built facts, in Brace's words

Rules-side profile (call it `STUB_PROFILE`): `profile(...)` from `builders.py` with `language=BRACE` (B2),
`framework=STUB` (the B3 framework, built in `builders.py` from `STUB_FILE` the way `marks_of`/`forms_of` read a
language file, splitting each dotted name at Brace's member with `outside_steps`), and
`scenarios=replace(PROFILE.scenarios, file="{name:kebab}.test.ts")`. Columns stay `given, when, then`. The use case is
`PublishResult = Published | Missing` in `app/modules/docs/contract/results.py` line 4 (the existing `RESULTS`). The
test file is `tests/modules/docs/application/publish.test.ts`, built with `source(..., root=TESTS, language=BRACE)`
(below `FILE`). Rows are `Row(line, written, id, (None, "PublishDocument", then))`.

Call form (`form=1`, `runs=0`), table on line 9, test function `Function(8, "testPublish", (table,))`:

1. Rows `Published` (line 10) and `Missing` (line 11), both written, each with an id: no violation.
2. The first row not written, no id: exactly
   `(f"{TS}:10: row is not a literal (scenario-coverage)", 'write {..., name: "<a sentence stating the outcome>"}')`.
3. The first row written, id `None`: `(f"{TS}:10: row has no id (scenario-coverage)", <the fix of 2>)`.
4. Only the `Published` row: `(f"{TS}:9: PublishResult variant Missing has no row in the table and no standalone test
   naming it (scenario-coverage)", "add a row whose then is Missing, or a standalone test naming it")`.
5. Rows `None`: `(f"{TS}:9: the rows of the table cannot be read (scenario-coverage)", "write them as a list, or as
   the name of a list assigned at the top of the file")`.
6. Rows `Published` and `Missing`, both written with ids (so no variant is missing), and the function's `blocks=((14, "if"),)`: `(f"{TS}:14: testPublish has an \`if\` in its body
   (scenario-coverage)", "arrange from given, act with when, assert == then, and give the odd case its own test")`.
   (Proves the branch keywords come from Brace's `branching`.)

Loop form (`form=0`, `runs=9`), table on line 9:

7. Rows `Published` and `Missing`, both written with ids (a missing variant would add a line-9 violation), and `blocks=((9, "for"), (12, "if"))`: only the line-12 violation (`testPublish has an \`if\` in its
   body`); the `for` at the table's `runs` is no branch.
8. The first row not written, no id: `(f"{TS}:10: row is not a literal (scenario-coverage)", "write the row's id, a
   sentence stating the outcome, as its value at position 0")`.

Both forms in one file:

9. `testPublished` holds a call-form table whose one row covers `Published`; `testMissing` holds a loop-form table
   (`runs` its own line, a matching `for` block) whose one row covers `Missing`: no violation.

`weak` (call form):

10. A call-form table covering only `Published`, and `Function(20, "testMissing", mentions=frozenset({"Missing"}))`
    with no assert: `weak` is exactly `[Weak("scenario-coverage", FILE, 20, "PublishResult variant Missing is credited to
    testMissing by name only: no assert in their bodies")]`, and `violations` is `[]`.

`plain` (tiers `unit` and `integration` with `plain_tables`, as the existing `PLAIN`, under `STUB_PROFILE`'s language
and framework), test file `tests/modules/docs/domain/doc.test.ts`:

11. A call-form table test `Function(8, "testDoc", (Table(9, ("a", "b"), (...), 1, 0),), blocks=((12, "for"), (14,
    "if")))`: exactly
    `tests/modules/docs/domain/doc.test.ts:12: testDoc has a \`for\` in its body, and a table test of the unit tier holds
    no branch (tiers.unit.plain_tables; scenario-coverage)` and the same at line 14 with ``an `if` ``.
12. The same function with a loop-form table (`form=0`, `runs=12`): only the line-14 violation.

No string in these findings comes from Python's `writing` (`pytest.param`, `id="..."`), and none is typed into
`scenarios.py`.

### B5. Docs and texts

1. README, the paragraph on `supplies` near line 180 (after "refused at that entry (`testing.tables.0.call`).") or the
   Development section (line 1114 onward), one or two sentences: the table forms are proved neutral without a
   TypeScript reader by a test-only framework (`tests/fakes/frameworks/stub.yaml`, a loop form and a call form with
   literal rows) checked on hand-built facts and worded by the test-only language `brace.yaml`'s `writing`, beside a
   no-form framework and the loop form read by Python's reader. No other README line moves. README line 116 already
   says `tables`.
2. CHANGELOG `[Unreleased]`, `### Added` (after the no-form line, CHANGELOG.md:86-91): one line saying the same in
   release-note words (tests only; behaviour unchanged).
3. `profile explain` texts (`xarch/architectures/presets/format/keys.yaml`: `testing.tables*` at 805-870, the `table`
   fragment, `plain_tables` at 588-600, the guard texts): re-read for pytest- or Python-only wording and for any
   `{...}` syntax. Expected: no change (they were read for this spec and say "a dotted name", "a list or object
   literal", "a field of a literal row"). If a text does change, its golden-doc and explain tests are updated in the
   same commit and the golden docs regenerated.
4. Golden docs: regenerate `docs/{cli,web,xarch}/testing.md` with the repo's generator and read the diff: expected
   empty.

### B6. Re-grep (note 8 item 7)

`grep -rn "testing.table\b\|CaseTable\|_snake_name" xarch tests docs README.md architecture.yaml` returns only:

- `tests/modules/spec/application/logic/test_retired_keys.py`: the retired-keys entry's docstring (102) and its
  refusal test (202);
- `tests/bootstrap/test_profile_explain.py`: `test_the_table_of_testing_is_answered_from_the_table_of_retired_names`
  (368), the explain side of the same refusal;
- `tests/bootstrap/corpora/7cc6111.json` and `df537ca.json`: recorded findings of old commits naming `CaseTable`,
  which are never edited (note line 355); reported as the allowed exception;
- `docs/superpowers/plans/` and `docs/superpowers/specs/`: the step documents of this release, this one included;
  records, not edited.

The one hit to remove: `tests/modules/spec/application/logic/test_testing.py:489`, the `pytest.param` id `"an id
written as a bare keyword, as testing.table wrote it"`, reworded to `"an id written as a bare keyword, as the old
table map wrote it"` (the test itself unchanged). `CHANGELOG.md` is outside the grep's paths; its 0.3.0 refusal line
(97) and 0.2.0 line (281) stay.

## Out of scope

- `testing.declared` and unnamed tests (card 6.8; note section 5).
- Any change to `xarch/` behaviour: the parser, the reader, `scenarios.py`, `keys.yaml` (unless B5.3 finds a
  Python-only text), the Python language file.
- A TypeScript reader, a `call` form in Python's reader, a `unittest.yaml` or Vitest preset under
  `xarch/architectures/presets/` (note lines 29, 449-450).
- Note 9.2 and 9.3 and `test_other_framework.py` (done by 6.3-6.6; only confirmed green).
- The recorded corpora, the golden docs, the bundled profiles.

## Tests that prove it (written first)

Unit tier (`tests/modules/...`): pure functions over hand-built facts and in-memory documents; fast, and the only
place the checks can be run on a form no reader reads. Architecture tier: the existing grep test already guards the
checking code; nothing new.

### Unit, spec: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`

The tier fits: it already parses `testing` maps and presets through `parsed`/`problems` of
`tests/modules/spec/profiles.py`. Load `stub.yaml` with `yaml.safe_load` from `tests/fakes/frameworks/`.

- S1 `parsed(covered(testing="stub", language="brace"), presets={"stub": STUB}, languages={"python": PYTHON,
  "brace": BRACE}).framework` equals the B3 framework.
- S2 the same with `BRACE`'s `writing` replaced by `Writing()`: `problems(...)` holds the B3 refusal at
  `testing.tables.1.id`.

### Unit, rules: `tests/modules/rules/application/logic/test_scenarios.py` (a new section at the end)

The tier fits: the existing neutral cases (`NAMED`, `LITERAL`, `LOOP`, `BRACKETS`) live there; these replace in-Python
forms and templates with the data files. One test per B4 item, grouped as parametrised tests where items share a
shape:

- R1 (B4.1-6) call form: violations and fixes, parametrised over the six table/function shapes.
- R2 (B4.7-8) loop form: the `runs` exemption and the position-id fix.
- R3 (B4.9) both forms in one file cover the union.
- R4 (B4.10) `weak` under the call form.
- R5 (B4.11-12) `plain` for each form.

### Unit, builders: `tests/modules/rules/builders.py`

Not a test file; gains `STUB_FILE`, `STUB` (and the small helper that reads the file's `tables` into `TableForm`s) and
`BRACE`'s `branching` and `writing`. S1 pins that the loader reads `stub.yaml` into the same forms `STUB` holds:
the helper's result for `STUB_FILE` must equal S1's expected tuple (assert it in S1 only if it can be done without the
spec test importing `tests.modules.rules`; otherwise both hold the B3 tuple and the helper is the rules tests' only
reader).

### Existing tests that must stay green unchanged

`tests/architecture/test_table_forms.py`, `tests/architecture/test_language_seam.py`,
`tests/modules/spec/application/logic/test_language_file.py`, `tests/bootstrap/test_other_framework.py`,
`tests/bootstrap/test_loop_tables.py`, `tests/bootstrap/test_no_table_form.py`, `tests/bootstrap/test_docs_templates.py`,
`tests/bootstrap/test_recorded_corpora.py`, every existing `test_scenarios.py` case, every test using `BRACE`.

### Gates

`uv run pytest -q` (over two minutes: run in the background, read at the end), `uv run xarch check`,
`uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`, each green on
this branch alone. Plus the B6 grep, its output read against the allowed list.

## Notes for the planner

- Spec-side languages: `tests/modules/spec/languages.py` builds `BRACE` with `language_of("brace", BRACE_DOCUMENT)`;
  B2's keys flow in by themselves. Brace writes no `supplies`, so `profile_needs.short` checks no facts for it
  (`profile_needs.py:75`): a `call` form loads under Brace.
- A probe on this branch confirmed: `covered(testing="stub", language="brace")` with the B1 map and Brace given
  `writing.field` parses into the B3 forms; bare `it.each` is refused.
- Rules-side `BRACE` in `builders.py` is hand-built from `BRACE_FILE`; add the two fields there. `source()` takes
  `language=BRACE` so `read_as` applies Brace's rules.
- Check that `tested(profile, path)` places `tests/modules/docs/application/publish.test.ts` in the integration tier
  of instance `docs` under `STUB_PROFILE` (paths, not endings, decide it); if it does not, say so before changing
  anything in `xarch/`.
- `docs/superpowers/` holds the step documents; nothing there is edited but this spec and its plan.
- Commits: tests first per task; the README/CHANGELOG/re-grep reword in one docs task at the end.

---

# 6.7 rules: test-only frameworks prove the table forms neutral, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A test-only framework data file (`tests/fakes/frameworks/stub.yaml`, a loop form and a call form with literal rows) is loaded by the real profile loader under the test-only language Brace, and the scenario-coverage and `plain_tables` checks run on hand-built facts of each form, worded from Brace's `writing`; README and CHANGELOG say neutrality is proved this way.

**Architecture:** Nothing in `xarch/` changes. Task 1 adds the two data files' content (`stub.yaml` new, `brace.yaml` two keys) and pins the spec-side loader on them. Task 2 teaches the rules tests' builders to read `stub.yaml` and Brace's new keys and runs the checks on hand-built `Table(form=1)` / `Table(form=0, runs=...)` facts. Task 3 is docs, the one re-grep reword, and the gates.

**Tech Stack:** Python 3, pytest, PyYAML, `uv`, ruff.

**Spec:** `docs/superpowers/specs/6-7-rules-test-only-68122345.md` (prepended above).

## Global Constraints

- No comments in xarch's code (Python files); YAML data files under `tests/fakes/` carry a header comment, as `brace.yaml` does.
- Never `ruff --fix`; run `uv run ruff check` only.
- Tests written first: every task runs its new tests red before the code that greens them.
- No TypeScript case and no `{...}` syntax typed into xarch's code or into a fix text: syntax comes only from a language's `writing`; the `{...}` template lives in `tests/fakes/languages/brace.yaml` only.
- No TypeScript reader; facts are built by hand as `tests/modules/rules/builders.py` builds them.
- Python's reader gains no `call` support.
- Recorded corpora (`tests/bootstrap/corpora/`) and golden docs `docs/{cli,web,xarch}/testing.md` do not move; golden docs are regenerated (by their tests) and their diff read, never edited by hand; expected diff empty.
- `tests/architecture/test_table_forms.py` and `tests/bootstrap/test_other_framework.py` are kept unchanged.
- `.claude/` out of commits; nothing pushed; README and CHANGELOG lines under `[Unreleased]`.
- Line length 140 (`ruff.toml`).
- Long test runs in the background or under `timeout`; never `pkill`/`killall`.

## Review Focus

1. A branch keyword Brace lists and Python does not (`switch`) is reported in a Brace table test, and one Python lists and Brace does not (`match`) is not: proves `branching` is read from Brace, not Python. Pinned in Task 2, R1.
2. A row whose id is blanks alone (`"  "`) under the call form is "row has no id", fixed in Brace's field words, as it is under pytest. Pinned in Task 2, R1.
3. A use case's `.test.ts` file placed in another tier (`modules/docs/domain/publish.test.ts`) does not cover the use case: the violation and fix name `publish.test.ts` as the kebab file pattern writes it. Pinned in Task 2, R6.
4. Under the call form a variant a row covers is not weak even when a standalone test also names it without asserting. Pinned in Task 2, R4.
5. A Brace table test with branches in a tier without `plain_tables` gives no `plain` violation. Pinned in Task 2, R5.

---

## File Structure

- Create `tests/fakes/frameworks/stub.yaml` — the test-only framework data file (B1).
- Modify `tests/fakes/languages/brace.yaml` — header sentence plus `branching` and `writing` (B2).
- Modify `tests/modules/spec/application/logic/test_profile_parsing_tests.py` — S1, S2 (B3).
- Modify `tests/modules/rules/builders.py` — `BRACE` gains `branching` and `writing`; new `tables_of`, `_table_form`, `STUB_FILE`, `STUB` (B2, B4).
- Modify `tests/modules/rules/application/logic/test_scenarios.py` — new section at the end, R0-R6 (B4).
- Modify `tests/modules/spec/application/logic/test_testing.py:489` — one `pytest.param` id reworded (B6).
- Modify `README.md` (~line 181) and `CHANGELOG.md` (`[Unreleased]` / `### Added`, after line 91) (B5).

---

### Task 1: The test-only framework and Brace's words, read by the loader

**Files:**
- Create: `tests/fakes/frameworks/stub.yaml`
- Modify: `tests/fakes/languages/brace.yaml` (header comment, end of file)
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (imports at lines 1-20; new tests at end of file)

**Interfaces:**
- Consumes: `tests.modules.spec.languages.BRACE` (a `Language`; `.checked` is a `CheckedLanguage`), `PYTHON`; `tests.modules.spec.profiles.covered`, `parsed`, `problems` (each takes `presets=` and `languages=`).
- Produces: `tests/fakes/frameworks/stub.yaml` (read by Task 2's `builders.py` as `STUB_FILE`); `brace.yaml` keys `branching: [if, switch, try, for, while]` and `writing: {call: "{callee}(...)", field: '{..., {field}: "{text}"}'}` (read by Task 2 as `BRACE_FILE["branching"]`, `BRACE_FILE["writing"]`).

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, replace the import block's first lines:

```python
"""A profile file: the test framework (a preset or the map), the tiers and which part each covers, the
fakes, and the guards."""
import pytest

from tests.modules.spec.profiles import EX, PRESETS, PYTEST_FORM, TESTING, covered, layered, parsed, problems
```

with:

```python
"""A profile file: the test framework (a preset or the map), the tiers and which part each covers, the
fakes, and the guards."""
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import EX, PRESETS, PYTEST_FORM, TESTING, covered, layered, parsed, problems
```

and replace:

```python
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Fakes, Fixture, Framework, ScenarioCoverage, StandIns
```

with:

```python
from xarch.profile_values.language import Writing
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId, ScenarioCoverage, StandIns, TableForm
```

Append at the end of the file:

```python
STUB = yaml.safe_load((Path(__file__).resolve().parents[4] / "fakes" / "frameworks" / "stub.yaml").read_text(encoding="utf-8"))
"""The test-only framework of tests/fakes/frameworks/, a loop form and a call form with literal rows, as a preset."""


def test_the_test_only_framework_loads_under_brace_into_a_loop_form_and_a_call_form():
    framework = parsed(covered(testing="stub", language="brace"), presets={"stub": STUB},
                       languages={"python": PYTHON, "brace": BRACE}).framework
    assert framework == Framework(("*.test.ts",), "test*", tables=(
        TableForm("bound", None, (), RowId(position=0), loop=True),
        TableForm("fields", Place(0), (), RowId(field="name"), call=(("vitest", "it", "each"), ("vitest", "test", "each"))),
    ))


def test_the_test_only_framework_is_refused_under_a_brace_that_does_not_write_a_field_id():
    unwritten = replace(BRACE, checked=replace(BRACE.checked, writing=Writing()))
    assert problems(covered(testing="stub", language="brace"), presets={"stub": STUB},
                    languages={"python": PYTHON, "brace": unwritten}) == [
        "layered.yaml: testing.tables.1.id: the language Brace does not write `writing.field`, how a row's id is given "
        "by a field"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py`
Expected: collection ERROR with `FileNotFoundError: ... tests/fakes/frameworks/stub.yaml`.

- [ ] **Step 3: Write the framework data file**

Create `tests/fakes/frameworks/stub.yaml`:

```yaml
# A test-only framework that imitates Vitest-like tests: no profile names it and no reader reads it. It writes two
# forms of a table of cases, both with literal rows: a loop of the test's body over a list literal (index 0), each row's
# id its value at position 0, and a call that wraps the test (index 1), its rows the call's first argument, each row's
# id its field name. The tests load it to show that the checks word a table by its form's slots and the language's
# `writing`.
files: ["*.test.ts"]
functions: "test*"
tables:
  - loop: true
    columns_from: bound
    row: literal
    id: {position: 0}
  - call: ["vitest#it.each", "vitest#test.each"]
    rows: {position: 0}
    columns_from: fields
    row: literal
    id: {field: name}
```

- [ ] **Step 4: Run the tests to see the second red**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py -k test_only_framework`
Expected: `test_the_test_only_framework_loads_under_brace_into_a_loop_form_and_a_call_form` FAILS with `InvalidArchitecture` holding `testing.tables.1.id: the language Brace does not write \`writing.field\`...` (Brace has no `writing` yet); the refusal test PASSES.

- [ ] **Step 5: Give Brace its words**

In `tests/fakes/languages/brace.yaml`, replace the header's last three lines:

```yaml
# an export, never by a prefix. Its immutable records are marked by a keyword on every field, readonly. The tests load
# it to show that the profile and the checks read outside names and comments by a language's own patterns; later steps
# add their keys to it.
```

with

```yaml
# an export, never by a prefix. Its immutable records are marked by a keyword on every field, readonly. It writes a
# row's id by a field of a literal row, and branches with if, switch, try, for and while. The tests load it to show
# that the profile and the checks read outside names and comments by a language's own patterns; later steps add their
# keys to it.
```

and append at the end of the file (after `directives: ["@ts-expect-error", eslint-disable]`):

```yaml
branching: [if, switch, try, for, while]
writing: {call: "{callee}(...)", field: '{..., {field}: "{text}"}'}
```

- [ ] **Step 6: Run the tests to verify they pass, and every loader of brace.yaml with them**

Run: `uv run pytest -q tests/modules/spec tests/architecture/test_language_seam.py tests/architecture/test_table_forms.py`
Expected: PASS (both new tests and every existing one; the existing `test_language_file.py` and `test_language_seam.py` load `brace.yaml` and keep passing — verified by a probe on this branch).

- [ ] **Step 7: Lint**

Run: `uv run ruff check tests/modules/spec`
Expected: `All checks passed!`

- [ ] **Step 8: Commit**

```bash
git add tests/fakes/frameworks/stub.yaml tests/fakes/languages/brace.yaml tests/modules/spec/application/logic/test_profile_parsing_tests.py
git commit -m "A test-only framework writing a loop form and a call form with literal rows loads under the test-only language Brace, which now says how it writes a row's id by a field and how it branches

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The checks on hand-built facts of each form, in Brace's words

**Files:**
- Modify: `tests/modules/rules/builders.py` (imports line 21 area unchanged; `BRACE` at lines 87-97; new code right after `BRACE`'s docstring)
- Test: `tests/modules/rules/application/logic/test_scenarios.py` (import at line 7; new section appended at end, after line 390)

**Interfaces:**
- Consumes (Task 1): `tests/fakes/frameworks/stub.yaml`; `brace.yaml` keys `branching` and `writing`.
- Consumes (existing, `test_scenarios.py`): `COLUMNS`, `RESULTS`, `row(then, line=10, id="an outcome", written=True) -> Row`, `ARRANGE_FIX`, `PLAIN`, `LOOP`; `violations`, `plain`, `weak`.
- Produces (`builders.py`): `tables_of(file: dict, member: str) -> tuple[TableForm, ...]`; `STUB_FILE: dict`; `STUB: Framework`; `BRACE.branching == ("if", "switch", "try", "for", "while")`; `BRACE.writing == Writing(call="{callee}(...)", field='{..., {field}: "{text}"}')`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_scenarios.py` replace line 7:

```python
from tests.modules.rules.builders import PROFILE, PYTEST_FORM, PYTHON, in_tests, profile, source
```

with:

```python
from tests.modules.rules.builders import BRACE, PROFILE, PYTEST_FORM, PYTHON, STUB, TESTS, in_tests, profile, source
```

Append at the end of the file:

```python
STUB_PROFILE = profile(language=BRACE, framework=STUB, scenarios=replace(PROFILE.scenarios, file="{name:kebab}.test.ts"))
"""PROFILE under the test-only language Brace and the test-only framework of tests/fakes/frameworks/stub.yaml: a loop
form at index 0 and a call form at index 1, both of literal rows; a use case's test file is <name:kebab>.test.ts."""
TS = "tests/modules/docs/application/publish.test.ts"
FIELD_FIX = 'write {..., name: "<a sentence stating the outcome>"}'
POSITION_FIX = "write the row's id, a sentence stating the outcome, as its value at position 0"
MISSING_ROW = (f"{TS}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
               "(scenario-coverage)", "add a row whose then is Missing, or a standalone test naming it")


def called(*rows: Row, line: int = 9) -> Table:
    """A table of the call form, which no statement of the test's body runs."""
    return Table(line, COLUMNS, rows, 1, 0)


def looped(*rows: Row, line: int = 9, runs: int = 9) -> Table:
    """A table of the loop form, its rows run by the loop on line runs."""
    return Table(line, COLUMNS, rows, 0, runs)


def stub_tests(*functions: Function, path: str = "modules/docs/application/publish.test.ts"):
    return source(path, root=TESTS, language=BRACE, functions=functions)


def stub_found(*tests) -> list[tuple[str, str]]:
    return [(str(v), v.fix) for v in violations([RESULTS], list(tests), STUB_PROFILE)]


def test_the_test_only_framework_reads_into_a_loop_form_and_a_call_form_split_at_brace_s_member():
    assert STUB == Framework(("*.test.ts",), "test*", tables=(
        LOOP, TableForm("fields", Place(0), (), RowId(field="name"), call=(("vitest", "it", "each"), ("vitest", "test", "each")))))


def test_brace_says_how_it_branches_and_writes_a_row_as_its_data_file_does():
    assert (BRACE.branching, BRACE.writing) == (("if", "switch", "try", "for", "while"),
                                                Writing(call="{callee}(...)", field='{..., {field}: "{text}"}'))


@pytest.mark.parametrize("function, expected", [
    pytest.param(Function(8, "testPublish", (called(row("Published"), row("Missing", 11)),)), [],
                 id="a row per variant, each written with an id, covers the union"),
    pytest.param(Function(8, "testPublish", (called(row("Published", written=False, id=None), row("Missing", 11)),)),
                 [(f"{TS}:10: row is not a literal (scenario-coverage)", FIELD_FIX)],
                 id="a row not written as a literal is fixed by Brace's field template"),
    pytest.param(Function(8, "testPublish", (called(row("Published", id=None), row("Missing", 11)),)),
                 [(f"{TS}:10: row has no id (scenario-coverage)", FIELD_FIX)], id="a row without an id"),
    pytest.param(Function(8, "testPublish", (called(row("Published", id="  "), row("Missing", 11)),)),
                 [(f"{TS}:10: row has no id (scenario-coverage)", FIELD_FIX)], id="a row whose id is blanks alone"),
    pytest.param(Function(8, "testPublish", (called(row("Published")),)), [MISSING_ROW],
                 id="a variant with no row is reported at the table"),
    pytest.param(Function(8, "testPublish", (Table(9, COLUMNS, None, 1, 0),)),
                 [(f"{TS}:9: the rows of the table cannot be read (scenario-coverage)",
                   "write them as a list, or as the name of a list assigned at the top of the file")],
                 id="rows that cannot be read"),
    pytest.param(Function(8, "testPublish", (called(row("Published"), row("Missing", 11)),), blocks=((14, "if"),)),
                 [(f"{TS}:14: testPublish has an `if` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="a branch in the body of a table test"),
    pytest.param(Function(8, "testPublish", (called(row("Published"), row("Missing", 11)),),
                          blocks=((14, "switch"), (15, "match"))),
                 [(f"{TS}:14: testPublish has a `switch` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="the branch keywords are Brace's: switch is one, Python's match is none"),
])
def test_scenario_coverage_of_the_call_form_in_brace_s_words(function, expected):
    found = stub_found(stub_tests(function))
    assert found == expected
    assert not any("pytest" in text or 'id="' in text for pair in found for text in pair)


@pytest.mark.parametrize("function, expected", [
    pytest.param(Function(8, "testPublish", (looped(row("Published"), row("Missing", 11)),),
                          blocks=((9, "for"), (12, "if"))),
                 [(f"{TS}:12: testPublish has an `if` in its body (scenario-coverage)", ARRANGE_FIX)],
                 id="the for that runs the rows is no branch, and an if still is"),
    pytest.param(Function(8, "testPublish", (looped(row("Published", written=False, id=None), row("Missing", 11)),),
                          blocks=((9, "for"),)),
                 [(f"{TS}:10: row is not a literal (scenario-coverage)", POSITION_FIX)],
                 id="a row not written as a literal is fixed by its id's position"),
])
def test_scenario_coverage_of_the_loop_form_in_brace_s_words(function, expected):
    assert stub_found(stub_tests(function)) == expected


def test_a_call_form_table_and_a_loop_form_table_in_one_file_cover_the_union_together():
    published = Function(8, "testPublished", (called(row("Published")),))
    missing = Function(20, "testMissing", (looped(row("Missing", 22), line=21, runs=21),), blocks=((21, "for"),))
    assert stub_found(stub_tests(published, missing)) == []


@pytest.mark.parametrize("functions, expected", [
    pytest.param([Function(8, "testPublish", (called(row("Published")),)),
                  Function(20, "testMissing", mentions=frozenset({"Missing"}))],
                 [Weak("scenario-coverage", TS, 20, "PublishResult variant Missing is credited to testMissing by name "
                                                    "only: no assert in their bodies")],
                 id="a variant credited only to a standalone test with no assert is weak"),
    pytest.param([Function(8, "testPublish", (called(row("Published"), row("Missing", 11)),)),
                  Function(20, "testMissing", mentions=frozenset({"Missing"}))], [],
                 id="a variant a row covers is not weak"),
])
def test_weak_under_the_call_form(functions, expected):
    tests = [stub_tests(*functions)]
    assert (weak([RESULTS], tests, STUB_PROFILE), stub_found(*tests)) == (expected, [])


DOC_TS = "modules/docs/domain/doc.test.ts"
STUB_PLAIN = replace(STUB_PROFILE, tiers=PLAIN.tiers)
"""STUB_PROFILE with plain tables in the unit and integration tiers."""
DOC_ROWS = (Row(10, True, "a case", ("x", "y")),)


def plain_branch(keyword: str, line: int) -> str:
    article = "an" if keyword[:1] in "aeiou" else "a"
    return (f"tests/{DOC_TS}:{line}: testDoc has {article} `{keyword}` in its body, and a table test of the unit tier "
            "holds no branch (tiers.unit.plain_tables; scenario-coverage)")


@pytest.mark.parametrize("table, expected", [
    pytest.param(Table(9, ("a", "b"), DOC_ROWS, 1, 0), [plain_branch("for", 12), plain_branch("if", 14)],
                 id="the call form runs no statement: every branch is one"),
    pytest.param(Table(9, ("a", "b"), DOC_ROWS, 0, 12), [plain_branch("if", 14)],
                 id="the loop form's for at its runs is no branch"),
])
def test_a_table_test_of_a_plain_tier_in_brace_holds_no_branch(table, expected):
    doc = source(DOC_TS, root=TESTS, language=BRACE,
                 functions=(Function(8, "testDoc", (table,), blocks=((12, "for"), (14, "if"))),))
    assert [str(v) for v in plain([doc], STUB_PLAIN)] == expected
    assert plain([doc], STUB_PROFILE) == []


def test_a_test_file_of_another_tier_does_not_cover_the_use_case_and_the_fix_names_its_kebab_file():
    elsewhere = stub_tests(Function(8, "testPublish", (called(row("Published"), row("Missing", 11)),)),
                           path="modules/docs/domain/publish.test.ts")
    assert stub_found(elsewhere) == [
        ("app/modules/docs/contract/results.py:4: PublishResult has no test file publish.test.ts among the integration "
         "tests of docs (scenario-coverage)", "write publish.test.ts among the integration tests of docs")]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py`
Expected: collection ERROR with `ImportError: cannot import name 'STUB' from 'tests.modules.rules.builders'`.

- [ ] **Step 3: Read the framework file and Brace's new keys in the builders**

In `tests/modules/rules/builders.py`, replace the `BRACE` definition and its docstring:

```python
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extensions=tuple(BRACE_FILE["extensions"]),
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
                        immutable=records_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        comments=forms_of(BRACE_FILE), directives=tuple(BRACE_FILE["directives"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
"""The TypeScript-like test-only language as a check reads it, its endings, package files, patterns, member, interface
marks, marks of an immutable record, annotations of no value, comment forms, directives and standard modules read from
its data file."""
```

with:

```python
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extensions=tuple(BRACE_FILE["extensions"]),
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
                        immutable=records_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        comments=forms_of(BRACE_FILE), directives=tuple(BRACE_FILE["directives"]),
                        branching=tuple(BRACE_FILE["branching"]), writing=Writing(**BRACE_FILE["writing"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
"""The TypeScript-like test-only language as a check reads it, its endings, package files, patterns, member, interface
marks, marks of an immutable record, annotations of no value, comment forms, directives, branch keywords, how it writes
a row of a table and standard modules read from its data file."""


def tables_of(file: dict, member: str) -> tuple[TableForm, ...]:
    """The table forms a framework's data file writes, as its loader reads them: each dotted name split at member, a
    place written as a mapping read as one, a literal row as no row call."""
    return tuple(_table_form(form, member) for form in file.get("tables", ()))


def _table_form(form: dict, member: str) -> TableForm:
    columns, rows = form["columns_from"], form.get("rows")
    return TableForm(Place(**columns) if isinstance(columns, dict) else columns, Place(**rows) if rows else None,
                     () if form["row"] == "literal" else outside_steps(form["row"], member), RowId(**form["id"]),
                     decorator=outside_steps(form["decorator"], member) if "decorator" in form else (),
                     call=tuple(outside_steps(name, member) for name in form.get("call", ())),
                     loop=form.get("loop", False))


STUB_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "frameworks" / "stub.yaml")
                           .read_text(encoding="utf-8"))
STUB = Framework(tuple(STUB_FILE["files"]), STUB_FILE["functions"], tables=tables_of(STUB_FILE, BRACE_FILE["member"]))
"""The Vitest-like test-only framework as a check reads it under Brace: a loop form and a call form, both of literal
rows, read from its data file."""
```

(`Framework`, `Place`, `RowId`, `TableForm`, `Writing`, `outside_steps`, `Path`, `yaml` are already imported at the top of `builders.py`.)

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py`
Expected: PASS, every new and existing case.

- [ ] **Step 5: Run every rules test that uses BRACE**

Run: `timeout 600 uv run pytest -q tests/modules/rules tests/architecture`
Expected: PASS.

- [ ] **Step 6: Lint**

Run: `uv run ruff check tests/modules/rules`
Expected: `All checks passed!`

- [ ] **Step 7: Commit**

```bash
git add tests/modules/rules/builders.py tests/modules/rules/application/logic/test_scenarios.py
git commit -m "scenario-coverage and plain_tables run on hand-built tables of the test-only framework's call form and loop form, each worded from Brace's writing and branching, never Python's

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: README, CHANGELOG, the re-grep reword, key texts, golden docs, gates

**Files:**
- Modify: `README.md:181` (the `supplies` paragraph)
- Modify: `CHANGELOG.md:91` (after the no-form line of `[Unreleased]` / `### Added`)
- Modify: `tests/modules/spec/application/logic/test_testing.py:489`
- Read only: `xarch/architectures/presets/format/keys.yaml:588-600, 805-870`, `docs/{cli,web,xarch}/testing.md`

**Interfaces:**
- Consumes: Tasks 1-2's files (named in the README and CHANGELOG lines).
- Produces: nothing code relies on.

- [ ] **Step 1: Reword the one re-grep hit (test id only)**

In `tests/modules/spec/application/logic/test_testing.py` line 489 replace:

```python
    pytest.param([PYTEST_TABLE | {"id": "id"}], ROW_ID, id="an id written as a bare keyword, as testing.table wrote it"),
```

with:

```python
    pytest.param([PYTEST_TABLE | {"id": "id"}], ROW_ID, id="an id written as a bare keyword, as the old table map wrote it"),
```

- [ ] **Step 2: Run it**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_testing.py -k "old table map"`
Expected: `1 passed`.

- [ ] **Step 3: README sentence**

In `README.md`, replace:

```
refused at that entry (`testing.tables.0.call`). One fact is never written under
`supplies`: `file.package`, that a file stands for the
```

with:

```
refused at that entry (`testing.tables.0.call`). The table forms are proved neutral without a TypeScript reader: the
tests load a test-only framework, `tests/fakes/frameworks/stub.yaml`, which writes a loop form and a call form with
literal rows, run the checks on facts built by hand for each, and word the findings by the `writing` of the test-only
language `tests/fakes/languages/brace.yaml`, beside a framework with no form and the loop form read by Python's reader.
One fact is never written under
`supplies`: `file.package`, that a file stands for the
```

- [ ] **Step 4: CHANGELOG line**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Added`, replace:

```
  is its own test`), and `tiers.<tier>.plain_tables` says `needs a table form: the framework <framework> writes none
  in \`testing.tables\``.

### Changed
```

with:

```
  is its own test`), and `tiers.<tier>.plain_tables` says `needs a table form: the framework <framework> writes none
  in \`testing.tables\``.
- Tests only, behaviour unchanged: the table forms are proved neutral without a TypeScript reader. A test-only
  framework (`tests/fakes/frameworks/stub.yaml`) writes a loop form and a call form with literal rows; scenario-coverage
  and `plain_tables` run on facts built by hand for each, their findings worded by the test-only language
  `brace.yaml`'s `writing` and `branching`, never Python's.

### Changed
```

- [ ] **Step 5: Run the README and docs tests**

Run: `uv run pytest -q tests/architecture/test_readme.py tests/bootstrap/test_docs.py`
Expected: PASS.

- [ ] **Step 6: Re-read the `profile explain` texts for Python-only wording**

Run: `awk 'NR>=580 && NR<=880' xarch/architectures/presets/format/keys.yaml | grep -n "pytest\|Python\|param(\|{\.\.\."`
Expected: no output (the texts of `plain_tables` and `testing.tables*` say "a dotted name", "a list or object literal", "a field of a literal row"). No change to `keys.yaml`. If the grep does print a line, stop and report it: the spec's B5.3 then requires the text, its explain and golden-doc tests changed in this commit.

- [ ] **Step 7: Golden docs regenerate unchanged, and the protected tests stay green**

Run: `uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_loop_tables.py tests/bootstrap/test_no_table_form.py tests/bootstrap/test_recorded_corpora.py tests/architecture/test_table_forms.py`
Expected: PASS. Then run `git status --short docs/ tests/bootstrap/corpora/` and expect no output.

- [ ] **Step 8: The re-grep**

Run: `grep -rn "testing.table\b\|CaseTable\|_snake_name" xarch tests docs README.md architecture.yaml | grep -v "^docs/superpowers/"`
Expected exactly these hits (and no others):

```
tests/bootstrap/test_profile_explain.py:368:    found = runner.invoke(app, ["profile", "explain", "testing.table", "--format", "json"])
tests/bootstrap/corpora/df537ca.json:296:...CaseTable...
tests/bootstrap/corpora/df537ca.json:297:...CaseTable...
tests/bootstrap/corpora/7cc6111.json:536:...CaseTable...
tests/modules/spec/application/logic/test_retired_keys.py:102:"""testing.table as profiles wrote it before 0.3.0."""
tests/modules/spec/application/logic/test_retired_keys.py:202:    pytest.param("testing.table", TABLE_MOVED, id="testing.table"),
```

(`test_testing.py:489` is gone; the corpora are the allowed recorded exception; `docs/superpowers/` holds step records, not edited.)

- [ ] **Step 9: Full gates**

Run, in the background with `timeout 900 uv run pytest -q > /tmp/pytest-6-7.log 2>&1` and read the log's last lines at the end; meanwhile:

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```

Expected: pytest ends `N passed` with no failure or error; ruff `All checks passed!`; each `xarch` command exits 0.

- [ ] **Step 10: Commit**

```bash
git add README.md CHANGELOG.md tests/modules/spec/application/logic/test_testing.py
git commit -m "README and CHANGELOG say the table forms are proved neutral by a test-only framework checked on hand-built facts in Brace's words, and a test id no longer names testing.table

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-Review

1. **Spec coverage.** B1 → Task 1 Step 3. B2 (brace.yaml keys + header; builders' `BRACE` fields and docstring) → Task 1 Step 5, Task 2 Step 3, pinned by `test_brace_says_how_it_branches...`. B3 (S1, S2) → Task 1 Step 1. B4.1-6 → R1 (`test_scenario_coverage_of_the_call_form_in_brace_s_words`, plus the Python-wording assert); B4.7-8 → R2; B4.9 → R3; B4.10 → R4 (the spec's `FILE` there is read as the `.test.ts` file, `TS`, since the test file is Brace's); B4.11-12 → R5; the builders' reader → R0 (`test_the_test_only_framework_reads_into...`, held beside S1's identical tuple without the spec test importing rules builders). B5.1 → Task 3 Step 3; B5.2 → Step 4; B5.3 → Step 6 (probe already run: no output); B5.4 → Step 7. B6 → Steps 1 and 8. Gates → Step 9. Tier placement of `publish.test.ts` (integration, docs) and `doc.test.ts` (unit, docs) under `STUB_PROFILE` was probed on this branch: correct, so nothing in `xarch/` changes.
2. **Placeholders.** None; every code step holds its code.
3. **Type consistency.** `STUB`, `STUB_FILE`, `tables_of`, `BRACE.branching`, `BRACE.writing` named identically in Task 2's Interfaces, Step 1 imports and Step 3; `Table(line, columns, rows, form, runs)` positional order matches `parsed.py:169-178`; `row()`, `LOOP`, `PLAIN`, `ARRANGE_FIX`, `COLUMNS`, `RESULTS` exist earlier in `test_scenarios.py`.
4. **Review Focus.** Five lines, each with its test: `switch`/`match` row and blanks-id row in R1; R6 other-tier file; R4 second case; R5's `STUB_PROFILE` assert.
<!-- task-pipeline: validated -->
