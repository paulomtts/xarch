# 6.11 spec: a table `call` form must name a callee a declared call form lists

Card: 630cd9f2-2544-42eb-81b5-bab6546b92d8 (subtask of 15e55316), release step 21 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3, row 21 at line 284: "the table `call` cross-check"). Blocked by 06615c54,
which is on this branch (HEAD fdd3da9).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note").
This card implements 2.7 item 2 (lines 413-416). From `0.3.0-cohesion-review-3.md` ("review 3"): overlap O14 (line
238), section 5 clash 11 (lines 381-382), and O4, O5, O8 (lines 228-232) for docs.

## Goal

A table form written as `call` says which call makes or wraps a test. That call must be one the framework says
declares a test. When a callee of a table `call` form is listed by no `call` form of `testing.declared`, the profile
is refused at that entry, naming the callee and what to write. The check lives in the profile loader, for any
framework (inline map, `testing: <preset>`, `testing: {preset: ...}`), not in a test of a bundled preset.

## What is already done (not to be redone)

- Table forms parse into `TableForm` (`xarch/profile_values/testing.py:69-83`); `call` is a tuple of callees, each a
  tuple of outside-name steps, at least two steps (`profile_checks.py:453`, `outside_names(..., least=2)`).
- Declared forms parse into `TestForm` (`testing.py:30-43`); a `call` form's `call` has the same shape, at least one
  step (`profile_checks.py:669`). A `function` form has `call == ()`.
- `_testing` (`xarch/modules/spec/application/logic/profile_parsing.py:537-566`) resolves a preset to its map first,
  then parses the framework (`ck.framework_patterns`) and the table forms (`ck.table_forms`, entries addressed
  `testing.tables.<i>`, i from 0, counting entries that fail too). Both lists are in hand there.
- The needs refusal of `testing.tables.<n>.call` (fact `function.tables.call`) is given at document level before
  `_testing` runs (`profile_parsing.py:187-188`). Python's reader does not supply `function.tables.call` nor
  `test.call` (README lines 179-181). The test-only language Brace (`tests/fakes/languages/brace.yaml`, member `#`)
  says nothing of its reader, so no needs refusal is given under it.
- `outside_text(steps, member)` (`xarch/kernel/logic/names.py:33`) prints an outside name as a profile writes it.
- The test-only framework `tests/fakes/frameworks/stub.yaml` already lists `vitest#it.each` and `vitest#test.each`
  under its declared `call` form and under its table `call` form.

## Inherited constraints

- Refusal (note 2.7 item 2, line 415-416; card deliverable): "`testing.tables.<n>.call`: `it.each` declares no test:
  list it under a `call` form of `testing.declared`".
- One test per declared call: `it.each(rows)("title", fn)` is one test of form `call` whose callee is `it.each`,
  holding one table (note 2.7 item 2, lines 413-414). The two holders name the same callee for one test (review 3
  clash 11, lines 381-382).
- A problem addresses a list entry by its index from 0 (note 2.4, lines 319-321).
- Card dodge: checking it only in a test of the bundled preset. The check is in the loader and is tested on a
  test-only framework.
- The bundled pytest preset writes only a `decorator` table form and a `function` declared form; the bundled `cli` and
  `web` profiles and `architecture.yaml` keep pytest (note lines 325-327, owner clarification). They load unchanged.
- The recorded corpora (`tests/bootstrap/corpora/`) do not change. The golden docs `docs/{cli,web,xarch}/testing.md`
  are regenerated and their diff read, never edited by hand; expected diff: none (note 2.9 line 454; review 3 O8, line
  232).
- README and CHANGELOG lines go under `[Unreleased]` (review 3 O4, O5, lines 228-229).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; Python only in the reader adapter and the data files under `xarch/architectures/presets/`;
  `.claude/` stays out of commits; nothing is pushed.

## Behavior

### B1. The cross-check

For each table form at index `n` of `testing.tables` whose holder is `call`, each of its callees is looked up among the
callees of every `call` form of `testing.declared` (their union). Callees compare by their steps, so the same name
written the same way matches. A callee found there is accepted. A callee found in none gives one problem:

```
<file>: testing.tables.<n>.call: `<callee>` declares no test: list it under a `call` form of `testing.declared`
```

- `<file>` is the profile's file name, prefixed by the loader as for every problem (`layered.yaml: ...`). The address
  is written bare, as every other loader problem writes it; the backticks of the card around the address are the
  card's markdown.
- `<callee>` is `outside_text(steps, language.checked.member)`: under Brace, `vitest#it.each`; under a language with
  member `.`, `checks.each`. It sits in backticks, as the note writes it.
- One problem per undeclared callee, in the order the table form lists them; the forms in index order.
- A framework whose declared forms are all `function` forms has no declared callee, so every callee of every table
  `call` form is refused.
- `decorator` and `loop` table forms are never checked.

### B2. When the check does not run

- When `testing` already has a problem from the framework map or any table form (the existing guard of `_testing`),
  the cross-check gives nothing: the profile is refused with those problems alone. Problems of `testing.mocks` do not
  stop it.
- For an entry whose needs refusal of `testing.tables.<n>.call` is given (the language's reader is known not to supply
  `function.tables.call`, such as Python), the cross-check gives nothing for that entry: the needs refusal already says
  to drop `testing.tables.<n>.call`, which settles both. A language that supplies the fact partly still gets the
  cross-check. Mechanism: `parse` already holds the shortfalls (`profile_parsing.py:187`); `_testing` is given the
  addresses of those without a note (the refused ones, the same filter as `needs.refused`, `profile_needs.py:100`) and
  skips entry `n` when `testing.tables.<n>.call` is among them. A shortfall of a table entry resolved from a preset
  carries the same address, so it skips the same way. Without this skip, Python would give both problems for one entry
  and the existing tests of `test_profile_needs.py` (lines 609-655) would fail.

### B3. Every route to the framework

The same problem, at the same address, is given for an inline map, for `testing: <name>` naming a preset, and for
`testing: {preset: <name>}`, since the preset is resolved to its map before the check.

### B4. What a profile says of the key

- `xarch/architectures/presets/format/keys.yaml`, `testing.tables[].call` (lines 893-903): `accepts` gains that each
  callee must be listed under a `call` form of `testing.declared`. Its example gains a `declared` call form listing
  `checks.each`, so the example is a framework the loader accepts apart from the needs of a language.
- README (around lines 179-183) gains one sentence: a table `call` form's callees must each be listed under a `call`
  form of `testing.declared`, with the refusal text. CHANGELOG `[Unreleased]` `### Added` gains one line saying the same.

## Tests

All new tests are unit tests of the profile loader (tier: unit, `tests/modules/spec/application/logic/`): the rule is
a pure function of the parsed profile, so a loaded document in memory proves it; no reader and no files are needed.
They run under the test-only language Brace (`declaring()`, `covered(..., language="brace")`, `languages=BRACED`)
because Python refuses any table `call` form for its needs first (B2), and the card asks for a test-only framework.

New, in `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

1. A table `call` form whose callee no declared `call` form lists is refused with the exact text of B1, under Brace,
   e.g. declared `[{function: "test*"}, {call: ["vitest#it"], ...}]` and table call `["vitest#it.each"]` gives
   ``layered.yaml: testing.tables.0.call: `vitest#it.each` declares no test: list it under a `call` form of
   `testing.declared` ``.
2. The address carries the entry's index: a loop form at 0 and the bad call form at 1 gives `testing.tables.1.call`,
   and nothing at `testing.tables.0`.
3. A callee listed by any declared `call` form is accepted: two declared call forms, the table's two callees one in
   each, loads and its `framework.tables` holds the form.
4. Two undeclared callees in one form give two problems, in the order written; one declared and one not gives one.
5. A framework with only a `function` declared form and a table `call` form is refused (B1, last-but-one bullet).
6. A `decorator` and a `loop` table form are not checked: each loads beside a declared set with no `call` form.
7. The stub framework (`STUB`) loads unchanged under Brace: the existing test at line 869 stays green as the positive
   case of a test-only framework.
8. The same refusal for the framework given as a preset, by name and by `{preset: ...}` (B3), addressed the same.
9. When another table form of the same framework has a problem (e.g. `missing \`row\``), only that problem is given,
   not the cross-check (B2, first bullet).
10. Under Python, a table `call` form with a function-only declared set gives the needs refusal alone (B2, second
    bullet). This is pinned by the existing tests of `tests/modules/spec/application/logic/test_profile_needs.py`
    (lines 609-655), which must pass unchanged; no new test is needed beyond leaving them as they are.

Existing tests that will need a declared `call` form added (the table form under test then stays valid), because
they write a table `call` form under a language that reads it (tests updated first, then the code):

- `tests/modules/spec/application/logic/test_testing.py`: `test_the_forms_of_a_table_are_read_each_in_its_slots`
  (around line 428, `CALL` under `EVERY_FORM`), and any other test there loading `CALL` under `EVERY_FORM` or `TOY`.
  Tests whose form is already refused (two holders, missing keys) are unaffected by B2.
- Any other failure the full suite shows (candidates named by exploration: `tests/bootstrap/test_other_framework.py`,
  `test_loop_tables.py`, `test_no_table_form.py`, `test_profile_explain.py:399-428`,
  `tests/modules/spec/application/test_profile_loading.py`, `tests/modules/rules/builders.py`). Each is fixed by
  declaring the callee, never by weakening the check. If `test_profile_explain.py` pins the `accepts` text or example
  of `testing.tables[].call`, it is updated to the B4 text.

Gates, each passing on this branch alone: `uv run pytest -q` (in the background, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check
architecture.yaml`. The golden docs are regenerated and show no diff.

## Out of scope

- Mock specs, `testing.mocks.specs`, `Call.types` (card 6.12, release step 22).
- Any check that a declared `call` callee has a table form (the converse); a declared call with no table is a plain test.
- The rules' reading of tests (`scenario-coverage`, `plain_tables`, `weak`) and the `Test` fact: done by earlier cards.
- Changes to the needs walker, `key_table.py`, the reader, the bundled pytest preset, the bundled profiles, the
  recorded corpora, or `tests/fakes/frameworks/stub.yaml` (it already passes).
- Version bump and the 0.3.0 CHANGELOG lead (release step 25).
