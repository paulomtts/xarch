<!-- The spec this plan implements, prepended verbatim: docs/superpowers/specs/6-11-spec-a-table-call-630cd9f2.md -->

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

---

# 6.11 A table `call` form must name a callee a declared call form lists: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The profile loader refuses a table `call` form whose callee no `call` form of `testing.declared` lists, at
`testing.tables.<n>.call`, naming the callee and what to write.

**Architecture:** One pure helper `_undeclared` in `profile_parsing.py`, called from `_testing` right after the
framework and the table forms parse cleanly and before the mocks are parsed; `parse_profile` hands `_testing` the
addresses its needs refuse, so an entry already refused for its language's reader is not refused twice. The format's
text of `testing.tables[].call` and its example move with it, so the example still loads.

**Tech Stack:** Python 3, pytest, uv, ruff; xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/6-11-spec-a-table-call-630cd9f2.md` (prepended above).

## Global Constraints

- Refusal text, exact: `<file>: testing.tables.<n>.call: `<callee>` declares no test: list it under a `call` form of `testing.declared``
  (the loader prefixes `layered.yaml: `; `<callee>` is `outside_text(steps, language.checked.member)`).
- A problem addresses a list entry by its index from 0.
- The check lives in the loader and is tested on a test-only framework under Brace, never in a test of a bundled preset.
- The bundled pytest preset, the bundled `cli`/`web` profiles, `architecture.yaml`, `tests/fakes/frameworks/stub.yaml`
  and `tests/bootstrap/corpora/` do not change.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by hand; expected diff: none.
- README and CHANGELOG lines go under `[Unreleased]`.
- No comments in xarch's code; never `ruff --fix`; tests written first; `.claude/` stays out of commits; nothing is pushed.
- Process safety: never `pkill`/`killall`/pattern `kill`; stop a stuck test with `timeout`.

## Review Focus

1. A framework whose table `call` form is also refused by the needs of Python: the needs refusal alone, never both.
   Pinned by the existing tests `test_profile_needs.py:607-655`, which must pass unchanged (run in Task 1 Step 6).
2. A language that supplies `function.tables.call` only partly: the cross-check still runs (only refused shortfalls,
   those with `note is None`, skip). Test added in Task 1 Step 1b.
3. A problem of `testing.mocks` beside an undeclared callee: both are given, the cross-check first. Test in Task 1 Step 1a.
4. A table form at a later index while an earlier entry is broken: only the broken entry's problem, no misaddressed
   cross-check problem. Test in Task 1 Step 1a.
5. The framework from a preset, by name and under `preset`: the same text at the same address. Test in Task 1 Step 1a.

---

## File Structure

- Modify `xarch/modules/spec/application/logic/profile_parsing.py`: `parse_profile` (line 209) passes the refused
  addresses; `_testing` (lines 537-566) takes them and runs the check; new `_undeclared` after `_testing`; import
  `TableForm` (line 137).
- Modify `xarch/architectures/presets/format/keys.yaml:893-903`: `testing.tables[].call` accepts text and example.
- Test `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (append at end, after line 989).
- Test `tests/modules/spec/application/logic/test_profile_needs.py` (append at end).
- Modify `tests/modules/spec/application/logic/test_testing.py:399-436` (one existing test gains a declared call form).
- Modify `README.md:183`, `CHANGELOG.md:122`.

A prototype of exactly this change was run against the whole suite while planning: only
`test_testing.py::test_the_forms_of_a_table_are_read_each_in_its_slots` and
`test_profile_keys.py::test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs[testing.tables.call]`
broke (2 failed, 6334 passed); `ruff check`, `xarch check`, `xarch check --strict` and `xarch profile check
architecture.yaml` passed and the golden docs regenerated unchanged.

---

### Task 1: The loader refuses a table `call` callee no declared `call` form lists

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:137`, `:209`, `:537-566`
- Modify: `xarch/architectures/presets/format/keys.yaml:893-903`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (append)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py` (append)
- Test: `tests/modules/spec/application/logic/test_testing.py:399-436`

**Interfaces:**
- Consumes: `Framework.declared: tuple[TestForm, ...]` and `TestForm.call: tuple[tuple[str, ...], ...]`;
  `TableForm.call: tuple[tuple[str, ...], ...]` (`xarch/profile_values/testing.py`); `outside_text(steps, member)`
  (`xarch/kernel/logic/names.py:33`, already imported in `profile_parsing.py:80`); `Shortfall.address`, `Shortfall.note`
  (`xarch/profile_values/capabilities.py:87`).
- Produces: `_testing(value, presets, problems, language, unread: Collection[str] = frozenset()) -> _Testing | None`;
  `_undeclared(framework: Framework, tables: tuple[TableForm, ...], unread: Collection[str], language: Language) -> list[str]`.
  Both private to `profile_parsing.py`; Task 2 only quotes the refusal text.

- [ ] **Step 1a: Write the failing loader tests (Brace, test-only framework)**

Append to the end of `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (after line 989). Every name
used is already imported or defined in that file (`pytest`, `TableForm`, `Place`, `RowId`, `covered`, `parsed`,
`problems`, `declaring`, `BRACED`, `TS_FILES`):

```python


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
    document["testing"]["mocks"] = {"calls": ["vitest#vi.fn"], "spec_keywords": [], "colour": 1}
    assert problems(document, languages=BRACED) == [
        undeclared(0, "vitest#it.each"),
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, spec_keywords, spec_position",
        "layered.yaml: testing.mocks.spec_keywords: must be a list of keyword names such as [spec]"]
```

The existing `test_the_test_only_framework_loads_under_brace_into_two_forms_of_a_test_two_forms_of_a_table_and_a_global`
(line 869) is left as it is: it is the positive case of the stub framework (spec test 7).

- [ ] **Step 1b: Write the failing needs tests (a language that supplies the fact partly)**

Append to the end of `tests/modules/spec/application/logic/test_profile_needs.py`. `replace`, `PYTHON`, `PARTIAL`,
`EXACT`, `Supply`, `Shortfall`, `FILES`, `CALL_FORM`, `framed`, `layered`, `parsed`, `problems` are already in that file:

```python


CALLS_MISSED = "a table a call held in a name holds is not read"
PARTLY_CALLED = replace(PYTHON, checked=replace(PYTHON.checked, supplies=(
    *PYTHON.checked.supplies, Supply("function.tables.call", PARTIAL, CALLS_MISSED))))
"""Python, its reader supplying the tables a call holds partly, and every other fact as Python's does."""


def test_a_call_form_whose_tables_the_language_supplies_partly_is_still_checked_against_the_declared_calls():
    assert problems(framed(CALL_FORM), languages={"python": PARTLY_CALLED}) == [
        "layered.yaml: testing.tables.0.call: `checks.each` declares no test: list it under a `call` form of "
        "`testing.declared`"]


def test_a_call_form_whose_tables_the_language_supplies_partly_loads_once_its_callee_is_declared():
    declared = [*FILES["declared"], {"call": ["checks.each"], "title": {"position": 0}, "body": {"position": 1}}]
    document = layered(testing=FILES | {"declared": declared, "tables": [CALL_FORM]})
    languages = {"python": replace(PARTLY_CALLED, checked=replace(PARTLY_CALLED.checked, supplies=(
        *PARTLY_CALLED.checked.supplies, Supply("test.call", EXACT))))}
    assert parsed(document, languages=languages).approximate == (
        Shortfall("testing.tables.0.call", "function.tables.call", CALLS_MISSED),)
```

- [ ] **Step 1c: Update the existing test whose table `call` form would now be refused**

In `tests/modules/spec/application/logic/test_testing.py`, after the docstring of `CALL` (line 401,
`"""A form whose rows a call that makes the test holds."""`), add:

```python
DECLARED_EACH = {"call": ["checks.each"], "title": {"position": 0}, "body": {"position": 1}}
"""The declared call form that lists CALL's callee, without which CALL is refused: checks.each declares no test."""
```

and in `test_the_forms_of_a_table_are_read_each_in_its_slots` (line 432) replace

```python
    assert parsed(with_tables([CALL, LOOP]), languages=EVERY_FORM).framework.tables == (
```

with

```python
    assert parsed(with_testing(tables=[CALL, LOOP], declared=[*FILES["declared"], DECLARED_EACH]),
                  languages=EVERY_FORM).framework.tables == (
```

Do not append to `with_tables(...)["testing"]["declared"]`: `with_testing` copies `TESTING` shallowly, so appending
to its `declared` list mutates the module-level `TESTING` and breaks unrelated tests (seen while planning). The two
`TableForm(...)` lines of the expected tuple stay as they are.

- [ ] **Step 1d: Update the format's text of `testing.tables[].call` (its example must keep loading)**

`tests/modules/spec/application/logic/test_profile_keys.py::test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs`
loads every key's example under a Python that reads every fact; once the check exists, the current example (`<<testing>>`,
whose declared set is a function form only) is refused. In `xarch/architectures/presets/format/keys.yaml`, replace
lines 893-898:

```yaml
  testing.tables[].call:
    meaning: the calls that hold the table
    accepts: a list of dotted names, each a call that makes or wraps the test and whose arguments hold the rows
    example: |
      <<testing>>
        tables:
```

with:

```yaml
  testing.tables[].call:
    meaning: the calls that hold the table
    accepts: >-
      a list of dotted names, each a call that makes or wraps the test and whose arguments hold the rows; each must be
      listed under a `call` form of testing.declared, else it is refused, testing.tables.0.call: `checks.each` declares
      no test
    example: |
      testing:
        files: [check_*%extension%]
        declared:
          - call: [checks.each]
            title: {position: 0}
            body: {position: 1}
        tables:
```

The five lines after it (`- call: [checks.each]` ... `id: {keyword: id}`) stay as they are.

- [ ] **Step 2: Run the new and updated tests to verify they fail**

Run:
```bash
timeout 300 uv run pytest -q -p no:cacheprovider tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_profile_needs.py 2>&1 | grep -E "FAILED|passed|failed"
```
Expected: 9 FAILED, each `assert` or `DID NOT RAISE InvalidArchitecture` on the old loader:
`test_a_table_call_form_whose_callee_no_declared_call_form_lists_is_refused_naming_the_callee`,
`test_the_refusal_of_an_undeclared_callee_is_addressed_by_the_index_of_its_table_form`, both params of
`test_each_undeclared_callee_of_a_table_call_form_is_its_own_problem`,
`test_a_table_call_form_under_a_framework_that_declares_tests_only_by_function_is_refused`, both params of
`test_a_table_call_form_of_a_preset_is_refused_the_same_at_the_same_address`,
`test_a_problem_of_the_mocks_does_not_stop_the_callees_being_checked`,
`test_a_call_form_whose_tables_the_language_supplies_partly_is_still_checked_against_the_declared_calls`.
The others (the accepted case, decorator/loop, the broken-entry case, the partly-supplied load) already pass: they
guard what the check must not refuse.

- [ ] **Step 3: Write the implementation**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

(a) Line 137, replace

```python
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns
```

with

```python
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns, TableForm
```

(b) In `parse_profile`, replace line 209

```python
    testing = _testing(document["testing"], presets or {}, problems, language) if "testing" in document else None
```

with

```python
    unread = frozenset(item.address for item in shortfalls if item.note is None)
    testing = _testing(document["testing"], presets or {}, problems, language, unread) if "testing" in document else None
```

(`shortfalls` is the list `needs.short(...)` returns at line 187; `item.note is None` is the same filter
`needs.refused` uses, `profile_needs.py:100`.)

(c) Replace the signature and docstring of `_testing` (lines 537-539)

```python
def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, named by its name or under
    `preset`, validated the same; a preset's map that names a preset in turn, or says beside, is refused."""
```

with

```python
def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language,
             unread: Collection[str] = frozenset()) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, named by its name or under
    `preset`, validated the same; a preset's map that names a preset in turn, or says beside, is refused. Once the
    framework and its table forms are sound, each callee of a table `call` form must be listed by a `call` form of
    `testing.declared` (see _undeclared); unread are the addresses the needs of the profile refuse."""
```

(d) In the body of `_testing`, replace

```python
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
```

with

```python
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    if len(problems) == count and framework is not None and tables is not None:
        problems += _undeclared(framework, tables, unread, language)
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
```

The guard below it (`if len(problems) != count ... return None`) stays; it now also returns None on a cross-check
problem.

(e) Insert this function between the end of `_testing` and `def _instead(` (blank lines as around it):

```python
def _undeclared(framework: Framework, tables: tuple[TableForm, ...], unread: Collection[str],
                language: Language) -> list[str]:
    """A problem for each callee of a table `call` form that no `call` form of `testing.declared` lists, the forms in
    the order of the list and the callees in the order each writes them; none for a form whose `call` the language's
    reader does not read (unread), which the needs of the profile refuse already."""
    declared = {callee for form in framework.declared for callee in form.call}
    return [f"testing.tables.{index}.call: `{outside_text(callee, language.checked.member)}` declares no test: list it "
            "under a `call` form of `testing.declared`" for index, form in enumerate(tables)
            if f"testing.tables.{index}.call" not in unread for callee in form.call if callee not in declared]
```

`enumerate(tables)` gives the entry's index only because the check runs when no table entry had a problem, so
`ck.table_forms` returned one form per entry.

- [ ] **Step 4: Run the touched test files to verify they pass**

Run:
```bash
timeout 300 uv run pytest -q -p no:cacheprovider tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_testing.py \
  tests/modules/spec/application/logic/test_profile_keys.py tests/bootstrap/test_profile_explain.py \
  tests/modules/spec/application/test_explain.py 2>&1 | tail -3
```
Expected: all passed, no failure.

- [ ] **Step 5: Check the explained key reads well**

Run: `uv run xarch profile explain testing.tables.call | head -20`
Expected: `accepts:` ends `... testing.tables.0.call: `checks.each` declares no test`, and the example shows the
`declared:` call form listing `checks.each` above `tables:`.

- [ ] **Step 6: Run the full suite and lint**

Run:
```bash
uv run ruff check
mkdir -p /tmp/xarch-6-11
timeout 900 uv run pytest -q -p no:cacheprovider > /tmp/xarch-6-11/task1.log 2>&1; echo "exit $?" >> /tmp/xarch-6-11/task1.log
tail -5 /tmp/xarch-6-11/task1.log
```
(The suite takes about 3.5 minutes; run it in the background and read the log at the end.)
Expected: `All checks passed!`; `N passed`, no failure, last line `exit 0`. The tests of `test_profile_needs.py`
lines 607-655 (Python's needs refusal alone) pass unchanged. Any other failure is fixed by declaring the callee in
that test's framework, never by weakening the check.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_parsing.py xarch/architectures/presets/format/keys.yaml \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_testing.py
git commit -m "A table call form whose callee no call form of testing.declared lists is refused at testing.tables.<n>.call, for any framework, unless its needs refuse that entry already"
```

---

### Task 2: README, CHANGELOG, golden docs, gates

**Files:**
- Modify: `README.md:183` (after the sentence ending `` `testing.globals` names what it binds without an import. ``)
- Modify: `CHANGELOG.md:122` (end of `[Unreleased]` / `### Added`, before the blank line and `### Changed` at line 124)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: the refusal text of Task 1.
- Produces: nothing code reads.

- [ ] **Step 1: README sentence**

In `README.md`, line 183 reads:

```
a call whose arguments hold the test's `title` and its `body`; `testing.globals` names what it binds without an import.
```

and line 184 starts `` `testing: {preset: pytest}` names a preset as a map, ``. Insert between them, on their own lines:

```
A table `call` form's callees must each be listed under a `call` form of `testing.declared`, the call that declares
the test it makes or wraps; one that is not is refused at its entry (`testing.tables.0.call: `it.each` declares no
test: list it under a `call` form of `testing.declared``).
```

- [ ] **Step 2: CHANGELOG line**

In `CHANGELOG.md`, after line 122 (`` profile explain testing.beside` explains it, and the "use ..." list of `testing` gains `beside`. ``)
and before the blank line and `### Changed`, add:

```
- A table `call` form's callees must each be listed under a `call` form of `testing.declared`, for a framework written
  out or named as a preset: one that is not is refused at its entry (`testing.tables.0.call: `it.each` declares no
  test: list it under a `call` form of `testing.declared``), unless the language's reader is known not to read that
  form, which refuses the entry already. `xarch profile explain testing.tables.call` says so.
```

- [ ] **Step 3: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-6-11/regenerate_docs.py` (outside the worktree):

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:
```bash
mkdir -p /tmp/xarch-6-11
uv run python -I /tmp/xarch-6-11/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
```
Expected: `written`; no file under `docs/cli`, `docs/web` or `docs/xarch` listed (only untracked files under
`docs/superpowers` may show); `git diff --stat -- docs` prints nothing. If a golden doc moved, do not hand-edit it:
restore it with `git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 4: Run every gate**

Run:
```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
git diff --quiet fdd3da9 -- xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml tests/bootstrap/corpora \
  tests/fakes/frameworks/stub.yaml xarch/architectures/presets/testing && echo "profiles, presets, stub and corpora unchanged"
timeout 900 uv run pytest -q -p no:cacheprovider > /tmp/xarch-6-11/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-6-11/suite.log
tail -5 /tmp/xarch-6-11/suite.log
```
(`xarch/architectures/presets/testing` holds the bundled `pytest.yaml` preset.)
Expected: `All checks passed!`; exit 0 for each `xarch` command; the unchanged line; the suite `N passed` with no
failure and last line `exit 0`. Run the suite in the background and read it at the end.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say a table call form's callees must each be listed under a call form of testing.declared, with the refusal; the golden docs regenerate unchanged"
```

---

## Self-Review

**Spec coverage:**
- B1 (the check, text, order, function-only framework, decorator/loop unchecked): Task 1 Step 1a tests 1-6; Step 3 (e).
- B2 first bullet (another table problem stops it; mocks do not): Step 1a `..._another_table_form_...` and
  `..._mocks_does_not_stop_...`; Step 3 (d) places the check before `_mocks`.
- B2 second bullet (skip refused entries; partial still checked): Step 3 (b)/(e); existing `test_profile_needs.py:607-655`
  run in Step 6; Step 1b for the partial case.
- B3 (inline, preset by name, `{preset: ...}`): Step 1a preset test (two params); inline in the others.
- B4 (`keys.yaml` accepts and example; README; CHANGELOG): Task 1 Step 1d; Task 2 Steps 1-2.
- Spec test 7 (stub loads under Brace): the existing test at line 869, run in Step 4.
- Existing tests to update: exactly the two the prototype run broke, Steps 1c and 1d.
- Gates and golden docs: Task 1 Step 6, Task 2 Steps 3-4.

**Placeholder scan:** no TBD/TODO; every code step shows its code.

**Type consistency:** `unread: Collection[str]` in `_testing` and `_undeclared`; `Collection` is already imported in
`profile_parsing.py:76`; `TableForm` imported by Step 3 (a); `outside_text` already imported (line 80).

**Review Focus:** the five lines above each name the test that pins it (line 1 by existing tests).
<!-- task-pipeline: validated -->
