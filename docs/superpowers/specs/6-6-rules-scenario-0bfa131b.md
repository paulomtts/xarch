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
