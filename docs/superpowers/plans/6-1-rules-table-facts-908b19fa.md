# 6.1: table facts record each table's form, its rows as written, and the statement that runs them — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `Row.param` becomes `Row.written`, `Table` gains `form` and `runs` with no default (the reader always passes `form=0, runs=0`), the two docstrings and the `function.tables` fact text hold no Python wording, and no output changes.

**Architecture:** The domain values live in `xarch/modules/rules/domain/parsed.py`. They are built in one place, the Python reader (`xarch/modules/rules/adapters/fs_source_tree.py`), and read in one place, the scenario-coverage logic (`xarch/modules/rules/application/logic/scenarios.py`). The fact text is one entry of `FACTS` in `xarch/profile_values/capabilities.py`. Each task changes one fact of the domain value and every builder and reader of it in the same commit, so the suite is green after every task.

**Tech Stack:** Python ≥ 3.13, frozen dataclasses, `ast`, pytest, ruff (line length 140), `uv`.

**Spec:** `docs/superpowers/specs/6-1-rules-table-facts-908b19fa.md`. It is copied in full below, before the tasks.

## Global Constraints

- No comments in xarch's code; docstrings only.
- Never run `ruff --fix`; fix by hand what `uv run ruff check` reports.
- Tests are written first. Each one must fail, for the reason named, before the code changes.
- Python wording belongs only in the reader adapter and `xarch/architectures/presets/`. The docstrings of `Row` and `Table` and the text `FACTS["function.tables"]` hold none of `decorat`, `param`, `keyword`, `pytest`, `tuple literal`, `list literal` (case-insensitive). Annotated field types are not wording.
- `Row(line: int, written: bool, id: str | None, cells: tuple[str | None, ...])`, in that order.
- `Table(line: int, columns: tuple[str, ...], rows: tuple[Row, ...] | None, form: int, runs: int)`, in that order, with no default on `form` or `runs`.
- The checking code reads neither `form` nor `runs` in this step.
- No output changes: the recorded corpora (`tests/bootstrap/corpora/`) and the golden docs (`docs/{cli,web,xarch}/`) stay byte for byte, and neither is ever edited by hand.
- Gates, each green on this branch alone: `uv run pytest -q` (over two minutes, so run it in the background and read the result at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.
- `.claude/` stays out of commits, and nothing is pushed.
- Process safety: never `pkill`/`killall`/`kill` by pattern. Stop a stuck run with `timeout`, e.g. `timeout 600 uv run pytest -q`.

## Review Focus

1. **Tables whose rows cannot be read, or whose rows come from a name assigned at the top of the file.** The reader takes those branches too, and they must also carry `form=0, runs=0`. Pinned by `test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement` (Task 2).
2. **A test whose own body loops over its cases** (`for case in CASES: ...`). Today no form loops, so `runs` must stay 0 even then. Setting it is release step 20. Pinned by the same test (Task 2).
3. **A function with two tables.** Each is read by form 0. Pinned by the same test (Task 2).
4. **A caller still passing the old name** (`Row(..., param=True, ...)`). It must fail loudly, not be ignored. Pinned by `test_a_row_is_no_longer_built_with_param` (Task 1).
5. **The fact text people see in a refusal or in `profile explain`.** It must read exactly "the tables of cases of a test function". Pinned by `test_the_fact_of_tables_reads_the_tables_of_cases_of_a_test_function` (Task 3).

---

# 6.1: table facts record each table's form, its rows as written, and the statement that runs them

Card `908b19fa`, subtask of `15e55316`, release step 17 of the merged order (`0.3.0-cohesion-review-3.md`, section 3),
the first of the four steps of the tables note. Parent design:
`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md`, cited below as "note line L"; the third
cohesion review in the same folder as "review 3 line L".

This step builds note §1 (lines 105-127: the facts of a table, the rename `Row.param` → `Row.written`, the new
`Table.runs` and `Table.form`), the fact-text half of §2.4 (lines 213-229; only the neutral text of today's single
fact, see §2.3), the `parsed.py` row of §6 (line 345) and the `capabilities.py` row (line 343), and §8 item 1 (lines
395-396).

## 1. What changes for a person

Nothing they check with. The same files are read, the same tables found, the same findings given with the same words;
the recorded corpora and the golden docs stay byte for byte (note lines 361-363; card deliverable "No output
changes"; dodge note line 451).

One sentence changes: the description of the fact `function.tables`. It is shown wherever a fact's description is
shown: after the fact's name in the refusal `... its check reads function.tables (<text>), which the language <L> does
not supply` (`spec/application/logic/profile_needs.py:93`), in `... needs function.tables (<text>), which the reader of
<L> does not supply` (`rules/application/logic/own_checks.py:85`), and in the needs that `profile explain` holds for a
key that reads the fact (`spec/application/services/explanation.py:58`). No bundled language triggers either refusal
and no golden doc or recorded corpus holds the text. It goes from "the tables of cases decorating a test function" to
"the tables of cases of a test function" (§2.3).

For the code, the facts of a table say what a table is with no word of Python (note lines 107-127): a row says whether
it is *written* as the form writes a row, and a table says by which *form* it was read and on which line its rows are
*run*, if a statement of the test's own body runs them.

## 2. Behavior (normative)

### 2.1 `Row`

`xarch/modules/rules/domain/parsed.py` (today lines 157-165). The fields become, in this order:

```
Row(line: int, written: bool, id: str | None, cells: tuple[str | None, ...])
```

- `written` replaces `param`, same position, same meaning: true when the row is written the way the form writes a row
  (today: a call of the form's `row`), false otherwise (note line 121). There is no `param` attribute left.
- `line`, `id`, `cells` keep their meaning and type.
- The docstring is rewritten neutrally (§2.4). It says: one row of a table and its line; `written` is whether it is
  written the way the table's form writes a row; `id` is its id when written as a literal text, as written, else
  None; `cells` holds, in column order, the name that heads each value (the callee of a call, a bare name, the last
  name of a dotted one), None where a value has none (note lines 116-117, 121-123).

### 2.2 `Table`

The fields become, in this order:

```
Table(line: int, columns: tuple[str, ...], rows: tuple[Row, ...] | None, form: int, runs: int)
```

- `form` is the index, from 0, of the form the table was read by in the framework's list of forms (note lines
  126-127). Today the framework has one form (`testing.table`), so every table has `form == 0`.
- `runs` is the line of the statement of the test's own body that runs the rows, when the form runs them with a loop;
  0 when none (note lines 118-119, 124). Today no form loops, so every table has `runs == 0`.
- Neither field has a default: each place that builds a `Table` says both (the reader says `form=0`, `runs=0`, card;
  note line 395). A hidden default is what the note's dodges warn against (note line 445, the same
  rule for a form left out).
- `line`, `columns`, `rows` keep their meaning and type (`rows` None when they cannot be read).
- The docstring is rewritten neutrally (§2.4): one table of cases of a test function and its line; its columns, the
  names of the values each row gives, in order; its rows, None when they cannot be read; `form`; `runs`. It does not
  say "decorating", "decorator", "parameter" or what Python literal a row list may be; *when* rows cannot be read is
  the reader's to say, not the domain's.

### 2.3 The fact text

`xarch/profile_values/capabilities.py:63` becomes:

```
"function.tables": "the tables of cases of a test function",
```

Only the text changes; the fact keeps its name. Splitting it into `function.tables.decorator|call|loop` is release
step 19 (note §2.4 lines 215-222, §8 item 4) and out of scope.

### 2.4 Neutral wording

Neither docstring of §2.1-2.2 nor the fact text of §2.3 holds the words `decorat`, `param`, `keyword`, `pytest`,
`tuple literal` or `list literal` (note line 345: "docstrings say 'a table' not 'decorating'"; the rule that Python
belongs only in the reader adapter and the presets, note line 13). Field *types* written in Python annotations are not
wording and are not concerned.

### 2.5 The reader

`xarch/modules/rules/adapters/fs_source_tree.py`:

- `_table` (today line 626) builds `Table(decorator.lineno, columns, rows, form=0, runs=0)`, by keyword so the two
  zeros are readable. Tables still come only from `node.decorator_list`; what is read and which tables are found is
  unchanged.
- `_row` (today lines 640, 643) keeps its two positional `Row(...)` calls; only the field's name changed. No call in
  `xarch/` passes `param=`.

### 2.6 The checking code

`xarch/modules/rules/application/logic/scenarios.py:199, 203` read `row.written` where they read `row.param`. Nothing
else changes in the checking code. It does **not** read `form` or `runs` in this step: `runs` is honoured by
`_branches` in release step 20 (note §8 item 5), and `form` is read only to find wording, in step 19 (note §8 item 3,
dodge note lines 440-442).

### 2.7 Error paths

None new. No input is refused that was accepted before, and no new message exists. A `Table` built without `form` or
`runs` is a `TypeError` at construction, which is the intent (§2.2): every builder names both.

## 3. Tests

Tests are written first; each fails before the change for the reason named. Tiers follow the repo's mirror of the
source path (`tests/modules/rules/{domain,application,adapters}/...`).

| # | Test | Tier, file | Why this tier | Fails first because |
|---|------|------------|---------------|---------------------|
| T1 | `Row`'s fields are `line, written, id, cells` and `Table`'s are `line, columns, rows, form, runs`, in order (`dataclasses.fields`) | unit, `tests/modules/rules/domain/test_parsed.py` | a fact of the domain value alone, no I/O | `Row` has `param`; `Table` has three fields |
| T2 | A `Table` built without `form` and `runs` raises `TypeError` | unit, same file | the no-default rule of §2.2 is a property of the value | `Table(1, ("a",), None)` builds today |
| T3 | The docstrings of `Row` and `Table` and `FACTS["function.tables"]` hold none of the words of §2.4 | unit, same file (`FACTS` imported from `xarch.profile_values.capabilities`) | a text property of the two values and of the fact they are the reading of; kept beside the values it guards | today's texts hold `param`, `keyword`, `decorating`, `tuple literal` |
| T4 | The reader's table for the existing `TABLE` source equals the expected `Table(..., form=0, runs=0)` with rows built by `written` | adapter, `tests/modules/rules/adapters/test_fs_source_tree.py:390-395` (edited) | only the real reader on real Python source can show the reader sets both zeros | the expected value names fields that do not exist |
| T5 | Under the other framework (`OTHER`, `cases.table`), the expected tables at lines 451, 453 gain `form=0, runs=0` | adapter, same file (edited) | the reader's zeros do not depend on which names the form uses | as T4 |
| T6 | `[r.written for r in ...]` gives what `[r.param ...]` gave (line 527-532); the source text `other.param(...)` there is Python under test and stays | adapter, same file (edited) | the flag's meaning is unchanged through the real reader | `written` does not exist |
| T7 | Every existing scenario-coverage and `plain_tables` test passes with the helpers `row(..., written=...)` and `table(...)` building `Table(line, columns, rows, 0, 0)`; the direct `Row(12, False, None, ())` and `Table(9, COLUMNS, None)` sites gain the two zeros; callers passing `param=` (lines 73, 202) pass `written=` | unit, `tests/modules/rules/application/logic/test_scenarios.py` (edited) | the checking code on hand-built facts, as today | the helpers build fields that do not exist |
| T8 | The recorded corpora are unchanged | bootstrap, `tests/bootstrap/test_recorded_corpora.py` (unchanged) | end-to-end proof that findings did not move (note lines 361-363) | — (must stay green) |
| T9 | The golden docs regenerate byte for byte | bootstrap, `tests/bootstrap/test_docs_templates.py`, `tests/bootstrap/test_docs.py` (unchanged), then `git status --short docs/cli docs/web docs/xarch` lists nothing | proof that docs did not move (note lines 361-363, review 3 O8 line 232) | — (must stay green) |

No test pins the old fact text today (grep `tables of cases` over `tests/`, `docs/`, `README.md` finds none), so none is
edited for §2.3 beyond T3.

## 4. Docs

- CHANGELOG, under `[Unreleased]` → `### Changed` (review 3 O5 line 229): one line, e.g. "The description of the fact
  `function.tables`, shown by `profile explain` and in a refusal of a fact the language does not supply, reads 'the
  tables of cases of a test function'." No line claims a change of findings or docs.
- README: no line. It neither quotes the fact text nor names `Row`/`Table` fields (review 3 O4 line 228: each step its
  tokens; this step has none in the README).
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated, diff read, expected empty (review 3 O8 line 232). Never
  edited by hand.
- Recorded corpora `tests/bootstrap/corpora/`: not edited.

## 5. Constraints (inherited)

- No comments in xarch's code; docstrings only (card).
- Never `ruff --fix` (card; note line 390).
- Tests written first (card).
- Python only in the reader adapter and `xarch/architectures/presets/` (note line 13): the domain values and the fact
  text carry no Python wording (§2.4).
- Gates, each green on this branch alone: `uv run pytest -q` (over two minutes; in the background, read at the end),
  `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check
  architecture.yaml` (card; note lines 390-392).
- `.claude/` stays out of commits; nothing is pushed (card).

## 6. Out of scope

- Table forms: `TableForm`, `testing.tables`, `columns_from`, the port and reader taking a list, `pytest.yaml`
  rewritten, `testing.table` refused (card 6.3; note §8 item 3, release step 19).
- The case of `{name}`: `{name:<case>}`, the bare `{name}` refusal, the kernel helper replacing `_snake_name`, the six
  profile `file:` lines (card 6.2; note §8 item 2, release step 18).
- Facts per form `function.tables.decorator|call|loop` in `supplies` and `NEEDS` (`key_table.py`, `python.yaml:97`
  keep the single fact) (note §8 item 4).
- The loop form in the Python reader and `runs` honoured by `_branches` (note §8 item 5); any read of `form` or `runs`
  in the checking code (dodge note lines 440-442).
- The no-form path, the `writing` templates, `_rows` wording from the language (note §8 items 3, 6).
- `tests/bootstrap/test_other_framework.py` and the inline `table:` maps (`testing.table.row` is a profile key, not
  `Row.param`).

---

## File Structure

| File | Change | Responsibility |
|------|--------|----------------|
| `xarch/modules/rules/domain/parsed.py` | Modify `Row` (lines 157-165) and `Table` (lines 168-174) | the neutral facts of a table |
| `xarch/modules/rules/adapters/fs_source_tree.py` | Modify `_table` (line 626) | the only builder of `Table`, now naming `form=0, runs=0` |
| `xarch/modules/rules/application/logic/scenarios.py` | Modify lines 199, 203 | reads `row.written` |
| `xarch/profile_values/capabilities.py` | Modify line 63 | the fact text |
| `CHANGELOG.md` | Add one line under `[Unreleased]` → `### Changed` (line 87) | the one changed sentence |
| `tests/modules/rules/domain/test_parsed.py` | Add tests | T1, T2, T3, Review Focus 4 and 5 |
| `tests/modules/rules/adapters/test_fs_source_tree.py` | Edit lines 390-395, 451, 453, 532; add a test | T4, T5, T6, Review Focus 1-3 |
| `tests/modules/rules/application/logic/test_scenarios.py` | Edit lines 16-21, 70, 73, 199, 202 | T7 |

There are four tasks. Each leaves the full suite green.

---

### Task 1: `Row.param` becomes `Row.written`

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py:157-165`
- Modify: `xarch/modules/rules/application/logic/scenarios.py:199,203`
- Modify (tests): `tests/modules/rules/domain/test_parsed.py`, `tests/modules/rules/adapters/test_fs_source_tree.py:532`, `tests/modules/rules/application/logic/test_scenarios.py:16-17,73,202`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `Row(line: int, written: bool, id: str | None, cells: tuple[str | None, ...])`. There is no `param` attribute. The reader's two `Row(...)` calls in `fs_source_tree.py:640,643` are positional and do not change. The test helper `row(then, line=10, id="an outcome", written=True)` in `test_scenarios.py`.

- [ ] **Step 1: Write the failing domain tests**

Replace the whole of `tests/modules/rules/domain/test_parsed.py` with the following. The first three tests are unchanged and the last two are new. The docstring gains a clause about rows.

```python
"""The rules the values of a parsed file keep about themselves: which statements are real, that a value built by
hand is public, and an import withholds no name, unless it says otherwise, and what a row of a table says."""
from dataclasses import fields

import pytest

from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3


def test_a_value_built_with_a_name_alone_is_public_and_an_import_withholds_nothing():
    assert (Class(1, "_A").public, Function(1, "_f").public, Constant(1, "_X").public) == (True, True, True)
    assert Import(1, ("m",), ("_x",)).withheld == frozenset()
    assert (Class(1, "A", public=False).public, Import(1, ("m",), ("x",), withheld=frozenset({"x"})).withheld) == (
        False, frozenset({"x"}))


def test_a_row_says_its_line_whether_it_is_written_as_a_row_its_id_and_its_cells():
    assert [f.name for f in fields(Row)] == ["line", "written", "id", "cells"]


def test_a_row_is_no_longer_built_with_param():
    with pytest.raises(TypeError):
        Row(1, param=True, id=None, cells=())
```

- [ ] **Step 2: Rename the flag in the adapter test**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, line 532, replace

```python
    assert [r.param for r in parsed(tmp_path, ROWS).functions[0].tables[0].rows] == [False, False, True]
```

with

```python
    assert [r.written for r in parsed(tmp_path, ROWS).functions[0].tables[0].rows] == [False, False, True]
```

The source text `other.param(1, id='x')` in `ROWS` (lines 527-528) is Python under test and stays as it is.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters/test_fs_source_tree.py::test_only_a_call_of_the_forms_row_is_a_row -v`
Expected: 3 FAIL.
- `test_a_row_says_its_line_...` fails with `['line', 'param', 'id', 'cells'] != ['line', 'written', 'id', 'cells']`.
- `test_a_row_is_no_longer_built_with_param` fails with `DID NOT RAISE <class 'TypeError'>`.
- `test_only_a_call_of_the_forms_row_is_a_row` fails with `AttributeError: 'Row' object has no attribute 'written'`.

- [ ] **Step 4: Rename the field in the domain**

In `xarch/modules/rules/domain/parsed.py`, replace the `Row` class (lines 156-165) with the following. The docstring changes only in the field's name here; Task 3 rewrites it.

```python
@dataclass(frozen=True)
class Row:
    """One element of the rows of a table, and the line it is on. written is whether it is a call of the table's row
    (a bare tuple or anything else is not); id is its id keyword when that is a string literal, as written, else None;
    cells holds the name that heads each positional value (the callee of a call, a bare name, the last name of an
    attribute), None where a value has none."""
    line: int
    written: bool
    id: str | None
    cells: tuple[str | None, ...]
```

- [ ] **Step 5: Read the new name in the checking code**

In `xarch/modules/rules/application/logic/scenarios.py`, replace lines 198-204

```python
    for row in table.rows:
        if not row.param:
            problems.append((row.line, f"row is not a {written}(...)", case))
        elif _given_id(row) is None:
            problems.append((row.line, "row has no id", case))
        if row.param or row.cells:
```

with

```python
    for row in table.rows:
        if not row.written:
            problems.append((row.line, f"row is not a {written}(...)", case))
        elif _given_id(row) is None:
            problems.append((row.line, "row has no id", case))
        if row.written or row.cells:
```

The local variable `written` (line 191, the dotted text of the form's row) and the field `row.written` share a word but not a scope: one is a string, the other is read through `row.`. Leave both as they are.

- [ ] **Step 6: Rename the helper's flag in the scenario tests**

In `tests/modules/rules/application/logic/test_scenarios.py`, replace lines 16-17

```python
def row(then: str | None, line: int = 10, id: str | None = "an outcome", param: bool = True) -> Row:
    return Row(line, param, id, (None, "PublishDocument", then))
```

with

```python
def row(then: str | None, line: int = 10, id: str | None = "an outcome", written: bool = True) -> Row:
    return Row(line, written, id, (None, "PublishDocument", then))
```

On line 73 and on line 202, replace `row("Published", param=False, id=None)` with `row("Published", written=False, id=None)`. Each line has exactly one occurrence. The text `pytest.param(...)` in the expected messages and in the `pytest.param(` wrappers of the tables stays.

Check that no `param=` is left in the three edited files and in `xarch/` outside the examples:

Run: `grep -rnE "\bparam=|\.param\b" xarch/modules tests/modules/rules | grep -vE "pytest\.param|other\.param"`
Expected: no output.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/rules -q`
Expected: all pass, including the 3 tests from Step 3.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/modules/rules/application/logic/scenarios.py \
  tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters/test_fs_source_tree.py \
  tests/modules/rules/application/logic/test_scenarios.py
git commit -m "A row of a table says whether it is written the way the table's form writes a row (Row.written), no longer Row.param; the checks read it unchanged"
```

---

### Task 2: `Table` gains `form` and `runs`, with no default

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py:168-174`
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:626`
- Modify (tests): `tests/modules/rules/domain/test_parsed.py`, `tests/modules/rules/adapters/test_fs_source_tree.py:390-395,451,453` plus a new test, `tests/modules/rules/application/logic/test_scenarios.py:20-21,70,199`

**Interfaces:**
- Consumes: `Row(line, written, id, cells)` from Task 1.
- Produces: `Table(line: int, columns: tuple[str, ...], rows: tuple[Row, ...] | None, form: int, runs: int)`, with no defaults. The reader builds `Table(decorator.lineno, columns, rows, form=0, runs=0)`. The test helper `table(*rows, columns=COLUMNS, line=9)` returns `Table(line, columns, rows, 0, 0)`.

- [ ] **Step 1: Write the failing domain tests**

In `tests/modules/rules/domain/test_parsed.py`, change the import line to

```python
from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row, Table
```

and append

```python


def test_a_table_says_its_line_its_columns_its_rows_its_form_and_the_line_that_runs_them():
    assert [f.name for f in fields(Table)] == ["line", "columns", "rows", "form", "runs"]


def test_a_table_built_without_its_form_and_the_line_that_runs_it_is_refused():
    with pytest.raises(TypeError):
        Table(1, ("a",), None)
```

- [ ] **Step 2: Write the failing reader tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, replace lines 390-395

```python
    assert function.tables == (Table(line_of(TABLE, "@pytest.mark.parametrize"), ("given", "when", "then"), (
        Row(line_of(TABLE, "Go(1)"), True, "a", (None, "Go", "Missing")),
        Row(line_of(TABLE, "Go(2)"), True, None, (None, "Go", "Published")),
        Row(line_of(TABLE, "Go(3)"), True, "", (None, "Go", "Gone")),
        Row(line_of(TABLE, "Go(4)"), False, None, (None, "Go", None)),
        Row(line_of(TABLE, "other,"), False, None, ()))),)
```

with

```python
    assert function.tables == (Table(line_of(TABLE, "@pytest.mark.parametrize"), ("given", "when", "then"), (
        Row(line_of(TABLE, "Go(1)"), written=True, id="a", cells=(None, "Go", "Missing")),
        Row(line_of(TABLE, "Go(2)"), written=True, id=None, cells=(None, "Go", "Published")),
        Row(line_of(TABLE, "Go(3)"), written=True, id="", cells=(None, "Go", "Gone")),
        Row(line_of(TABLE, "Go(4)"), written=False, id=None, cells=(None, "Go", None)),
        Row(line_of(TABLE, "other,"), written=False, id=None, cells=())), form=0, runs=0),)
```

Replace lines 451 and 453

```python
        ("it_a", (Table(a, ("a", "b"), (Row(a, True, "x", (None, None)), Row(a, True, None, (None, None)))),)),
        ("it_b", ()),
        ("it_c", (Table(c, ("a",), (Row(c, False, None, ()),)),)),
```

with

```python
        ("it_a", (Table(a, ("a", "b"), (Row(a, True, "x", (None, None)), Row(a, True, None, (None, None))), form=0, runs=0),)),
        ("it_b", ()),
        ("it_c", (Table(c, ("a",), (Row(c, False, None, ()),), form=0, runs=0),)),
```

The `it_a` line is 129 characters, under the limit of 140.

Directly after `test_only_the_parametrize_of_pytest_makes_a_table` (ending at line 432), insert this new test. It covers Review Focus 1-3.

```python


@pytest.mark.parametrize("text, count", [
    pytest.param("import pytest\n\n@pytest.mark.parametrize('a', load())\ndef test_a(): ...\n", 1,
                 id="a table whose rows cannot be read"),
    pytest.param("import pytest\nCASES = [pytest.param(1, id='a')]\n\n@pytest.mark.parametrize('a', CASES)\n"
                 "def test_a(): ...\n", 1, id="a table whose rows are a name assigned at the top of the file"),
    pytest.param("import pytest\n\n@pytest.mark.parametrize('a', [1])\n@pytest.mark.parametrize('b', [2])\n"
                 "def test_a(a, b): ...\n", 2, id="two tables of one function"),
    pytest.param("import pytest\nCASES = [1]\n\n@pytest.mark.parametrize('a', [1])\ndef test_a(a):\n"
                 "    for case in CASES:\n        assert case\n", 1, id="a test whose own body loops over cases"),
])
def test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement(tmp_path, text, count):
    assert [(t.form, t.runs) for t in parsed(tmp_path, text).functions[0].tables] == [(0, 0)] * count
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters/test_fs_source_tree.py -k "table or parametrized" -v`
Expected: these FAIL.
- `test_a_table_says_its_line_...` fails on `['line', 'columns', 'rows'] != [...]`.
- `test_a_table_built_without_...` fails with `DID NOT RAISE`.
- `test_a_parametrized_function_lists_its_rows_...` and `test_a_table_is_read_in_the_names_the_form_gives` fail with `TypeError: Table.__init__() got an unexpected keyword argument 'form'`.
- The four cases of `test_every_table_...` fail with `AttributeError: 'Table' object has no attribute 'form'`.

- [ ] **Step 4: Add the two fields to the domain**

In `xarch/modules/rules/domain/parsed.py`, replace the `Table` class (lines 167-174) with the following. The docstring gains the two fields only; Task 3 rewrites it.

```python
@dataclass(frozen=True)
class Table:
    """One table decorating a test function (the decorator the profile names), and the line it is on: its parameter names, and its rows
    (None when the rows are neither a list or tuple literal nor the name of one assigned at the top of the file); form, the
    index from 0 of the form it was read by in the framework's list of forms; and runs, the line of the statement of the
    test's own body that runs its rows, 0 when none does."""
    line: int
    columns: tuple[str, ...]
    rows: tuple[Row, ...] | None
    form: int
    runs: int
```

- [ ] **Step 5: The reader names both zeros**

In `xarch/modules/rules/adapters/fs_source_tree.py`, line 626, replace

```python
    return Table(decorator.lineno, columns, rows)
```

with

```python
    return Table(decorator.lineno, columns, rows, form=0, runs=0)
```

Nothing else in `_table` changes. Tables still come only from `node.decorator_list`.

- [ ] **Step 6: The scenario tests build tables with both zeros**

In `tests/modules/rules/application/logic/test_scenarios.py`, replace lines 20-21

```python
def table(*rows: Row, columns=COLUMNS, line: int = 9) -> Table:
    return Table(line, columns, rows)
```

with

```python
def table(*rows: Row, columns=COLUMNS, line: int = 9) -> Table:
    return Table(line, columns, rows, 0, 0)
```

On line 70 and on line 199, replace `Table(9, COLUMNS, None)` with `Table(9, COLUMNS, None, 0, 0)`. Each line has exactly one occurrence.

Check that no three-argument `Table(` is left:

Run: `grep -rnE "\bTable\(" xarch/modules tests/modules`
Expected: every line that prints shows `form=0, runs=0` or `, 0, 0)`. The helper on line 21 is `Table(line, columns, rows, 0, 0)`.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/rules -q`
Expected: all pass, including every test from Step 3.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/modules/rules/adapters/fs_source_tree.py \
  tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters/test_fs_source_tree.py \
  tests/modules/rules/application/logic/test_scenarios.py
git commit -m "A table says by which form it was read (Table.form) and on which line of the test's own body its rows run (Table.runs), with no default; the reader says 0 for both, and the checks read neither"
```

---

### Task 3: The docstrings and the fact text say a table with no word of Python

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py` (the two docstrings of `Row` and `Table`)
- Modify: `xarch/profile_values/capabilities.py:63`
- Modify: `CHANGELOG.md` (under `## [Unreleased]` → `### Changed`, line 87)
- Test: `tests/modules/rules/domain/test_parsed.py`

**Interfaces:**
- Consumes: `Row` and `Table` with the fields of Tasks 1-2; `FACTS: dict[str, str]` from `xarch.profile_values.capabilities`.
- Produces: `FACTS["function.tables"] == "the tables of cases of a test function"`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/domain/test_parsed.py`, add this import below the other `xarch` imports:

```python
from xarch.profile_values.capabilities import FACTS
```

and append

```python


PYTHON_WORDS = ("decorat", "param", "keyword", "pytest", "tuple literal", "list literal")


@pytest.mark.parametrize("text", [
    pytest.param(Row.__doc__, id="the docstring of a row"),
    pytest.param(Table.__doc__, id="the docstring of a table"),
    pytest.param(FACTS["function.tables"], id="the text of the fact of tables"),
])
def test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python(text):
    assert [word for word in PYTHON_WORDS if word in text.lower()] == []


def test_the_fact_of_tables_reads_the_tables_of_cases_of_a_test_function():
    assert FACTS["function.tables"] == "the tables of cases of a test function"
```

The test body has no `if` statement and no conditional expression. The comprehension's filter is neither, so the unit tier's `plain_tables` rule is kept.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/rules/domain/test_parsed.py -v`
Expected: 4 FAIL.
- The row docstring lists `['keyword']`. It has no `param`, because Task 1 renamed the field.
- The table docstring lists `['decorat', 'param', 'tuple literal']`. The text "list or tuple literal" holds `tuple literal`; it does not hold `list literal`, but no assertion depends on that.
- The fact text lists `['decorat']`.
- `test_the_fact_of_tables_reads_...` fails on `'the tables of cases decorating a test function' != 'the tables of cases of a test function'`.

Each case only has to fail; the exact lists are what the current texts give.

- [ ] **Step 3: Rewrite the two docstrings neutrally**

In `xarch/modules/rules/domain/parsed.py`, replace the `Row` and `Table` classes with:

```python
@dataclass(frozen=True)
class Row:
    """One row of a table, and the line it is on. written is whether it is written the way the table's form writes a
    row; id is its id when that is written as a literal text, as written, else None; cells holds, in column order, the
    name that heads each value (the callee of a call, a bare name, the last name of a dotted one), None where a value
    has none."""
    line: int
    written: bool
    id: str | None
    cells: tuple[str | None, ...]


@dataclass(frozen=True)
class Table:
    """One table of cases of a test function, and the line it is on: its columns, the names of the values each row
    gives, in order; its rows, None when they cannot be read; form, the index from 0 of the form it was read by in the
    framework's list of forms; and runs, the line of the statement of the test's own body that runs its rows, 0 when
    none does."""
    line: int
    columns: tuple[str, ...]
    rows: tuple[Row, ...] | None
    form: int
    runs: int
```

- [ ] **Step 4: Change the fact text**

In `xarch/profile_values/capabilities.py`, line 63, replace

```python
    "function.tables": "the tables of cases decorating a test function",
```

with

```python
    "function.tables": "the tables of cases of a test function",
```

- [ ] **Step 5: Run the tests to verify they pass, along with the language guards**

Run: `timeout 300 uv run pytest tests/modules/rules/domain/test_parsed.py tests/architecture -q`
Expected: all pass. `tests/architecture/test_language_seam.py` scans every docstring for words of the language. The new docstrings only drop words, so it stays green.

- [ ] **Step 6: Add the CHANGELOG line**

In `CHANGELOG.md`, under `## [Unreleased]` → `### Changed` (line 87), insert this as the first bullet, directly after the blank line that follows `### Changed`:

```markdown
- The description of the fact `function.tables`, shown by `profile explain` and in a refusal of a fact the language
  does not supply, reads "the tables of cases of a test function".
```

Then put the blank line back between it and the next bullet. The README gets no line.

- [ ] **Step 7: Check that the old text is gone**

Run: `grep -rn "tables of cases decorating" xarch tests docs README.md CHANGELOG.md | grep -v docs/superpowers`
Expected: no output.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/profile_values/capabilities.py tests/modules/rules/domain/test_parsed.py CHANGELOG.md
git commit -m "A table and its rows are said with no word of Python, and the fact function.tables reads the tables of cases of a test function, as profile explain and a refusal of the fact show it"
```

---

### Task 4: No output changes, and every gate is green

**Files:**
- None changed. If a gate fails, fix the cause in the file of the task that owns it and amend nothing: make a new commit.

**Interfaces:**
- Consumes: everything from Tasks 1-3.
- Produces: nothing new.

- [ ] **Step 1: Run the full suite in the background**

Run, in the background: `timeout 900 uv run pytest -q > /tmp/pytest-908b19fa.log 2>&1; echo "exit $?" >> /tmp/pytest-908b19fa.log`
It takes over two minutes. Do Steps 2-5 while it runs.

- [ ] **Step 2: Run xarch on itself**

Run: `uv run xarch check && uv run xarch check --strict`
Expected: both exit 0 and report no violation.

- [ ] **Step 3: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!`. If not, fix by hand. Never run `ruff --fix`.

- [ ] **Step 4: Check the profile**

Run: `uv run xarch profile check architecture.yaml`
Expected: exit 0.

- [ ] **Step 5: Wait for the suite and read its result**

Run: `tail -5 /tmp/pytest-908b19fa.log`
Expected: `N passed` with no failure or error, and the last line `exit 0`. That run includes `tests/bootstrap/test_recorded_corpora.py` (T8), plus `tests/bootstrap/test_docs_templates.py` and `tests/bootstrap/test_docs.py` (T9). They prove that the findings and the golden docs did not move.

- [ ] **Step 6: The golden docs and corpora are untouched**

Run: `git status --short docs/cli docs/web docs/xarch tests/bootstrap/corpora`
Expected: no output. Never edit these by hand. If the docs tests failed, find the cause in Tasks 1-3: this step changes no output.

- [ ] **Step 7: Nothing stray to commit**

Run: `git status --short`
Expected: no tracked file modified. `.claude/` must not appear among the staged files. The spec and plan under `docs/superpowers/` are committed by the workflow, not by you.

No commit in this task unless a gate needed a fix. If it did, commit the fix with a message that says what it changes, for example:

```bash
git add <the fixed files>
git commit -m "<what the fix changes, in the repo's sentence style>"
```
<!-- task-pipeline: validated -->
