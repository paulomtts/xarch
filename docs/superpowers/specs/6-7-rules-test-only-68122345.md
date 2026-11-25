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
