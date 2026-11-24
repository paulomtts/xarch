# 6.5 The loop form of a table, read by the Python reader: design spec

Card: d04cc54c (subtask of 15e55316). Release step 20 of the merged order
(`~/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, section 3). Step 20 is split into 6.5, 6.6 and
6.7 along the note's steps 5 to 7, and each one is green on its own. Blocked by 6.4 (12450ac3), which is done on this
branch (HEAD 59a882f).

Parent design: `~/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below, "the note"). This card
implements item 5 of section 8 (line 406: "The loop form in the Python reader, `runs` honoured by `_branches`. Tests on
Python source.") and item 3 of section 9 (lines 428-429: "The `loop` form read for real by the Python reader, under a
test-only framework (`for given, when, then in CASES:`). This proves a second form end to end through a real reader,
and the `runs` exemption.").

## 1. Goal

Today a `loop` entry of `testing.tables` is refused under Python, because `python.yaml` does not supply
`function.tables.loop` (6.4). The reader has no code for the form either. `_reads`
(`xarch/modules/rules/adapters/fs_source_tree.py:642-646`) accepts only decorator forms, and every `Table` is built with
`runs=0` (`fs_source_tree.py:639`). `_branches` (`xarch/modules/rules/application/logic/scenarios.py:174-182`) reports
every `for` of a table test's body, including the one that runs the rows.

After this card:

- Python's data file supplies `function.tables.loop` exactly, and a profile whose framework writes a `loop` form loads
  under Python (note 2.4, line 224).
- The Python reader reads a table from the loop of a test's body, `for given, when, then in CASES:`, in the forms it can
  read (section 3.2). The table's `runs` is the line of that `for` statement (note 1, fact 6, lines 118-124).
- `_branches` drops the one `for` block at a table's `runs`. Every other branch of the body is reported as today
  (note 3.2, line 281).
- Nothing changes for any profile that writes only decorator forms. That covers every bundled profile and preset.

## 2. Inherited constraints

- Python appears only in the reader adapter and in the data files under `xarch/architectures/presets/` (note,
  "Rulings", line 13; card). The loop's syntax (`ast.For`, its target, its iterable) is read only in
  `fs_source_tree.py`.
- The checking code names no kind of form. `scenarios.py` holds no string literal `"decorator"`, `"call"` or `"loop"`,
  and `tests/architecture/test_table_forms.py` pins this. It honours `Table.runs` as a line and never asks which form
  read the table (note, "Dodges", lines 441-443; note 9, lines 433-434).
- Python's reader does not gain `call` support. `function.tables.call` stays unsupplied, and its refusal stays tested
  (note 2.4, lines 224-225; note, "Dodges", line 449).
- Today's pytest behaviour stays byte for byte for existing profiles: the same files read, the same tables found, the
  same findings in the same words. The recorded corpora and the golden docs prove it, and any change in them is a defect
  of the branch (note 6, lines 361-363; note, "Dodges", line 451: "Letting the recorded findings or golden docs change
  'a little' in steps 1 to 5"; card).
- The meaning of `Table.runs` is already fixed by 6.1. It is "the line of the statement of the test's own body that runs
  its rows, 0 when none does" (`xarch/modules/rules/domain/parsed.py:169-178`). This card adds no field.
- The shape of a loop form is what 6.3's loader accepts (`xarch/modules/spec/application/logic/profile_checks.py:432-463`).
  `loop: true` is required, `rows` is refused, and `columns_from` is `bound` or `fields`. `row` is a dotted name or
  `literal`. `id` is `{keyword}` (only with a dotted row), `{field}` (only with a literal row) or `{position}`. This card
  does not change the loader.
- Project rules (card):
  - no comments in xarch's code, only docstrings;
  - never run `ruff --fix`;
  - tests are written first;
  - examples are simple and use absolute `app.` imports;
  - recorded corpora are edited by hand only, and only as the note says (this card edits none);
  - `.claude/` stays out of commits, and nothing is pushed.
- README and CHANGELOG lines go under `[Unreleased]` (review 3, O4 and O5, lines 228-229). The golden docs
  `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by hand. They move only where the
  note says, which here is nowhere (review 3, O8, line 232).
- Gates, each passing on this branch alone with the full suite green:
  - `uv run pytest -q` (over two minutes: run it in the background with a `timeout` and read it at the end);
  - `uv run xarch check`;
  - `uv run xarch check --strict`;
  - `uv run ruff check`;
  - `uv run xarch profile check architecture.yaml`.

## 3. Observable behavior

### 3.1 What Python supplies

The `supplies` block of `xarch/architectures/presets/language/python.yaml` lists `function.tables.loop: exact`, next to
`function.tables.decorator: exact` (line 102). Python's reader therefore supplies every fact exactly except
`function.tables.call`.

Under Python, a profile whose framework writes a `loop` entry (for example `{loop: true, columns_from: bound, row:
literal, id: {position: 0}}`) loads with no problem and no `approximate` line. A `call` entry is still refused at
`testing.tables.<i>.call` with the existing message (6.4, section 3.4). `xarch profile explain testing.tables.loop`
says that Python supplies `function.tables.loop` exactly.

### 3.2 The forms of a loop the reader reads

A loop form (`TableForm.loop` true) is read by the Python reader when:

- its `columns_from` is `bound`; and
- its rows are either:
  - calls (`row` is a dotted name) with an id given by `{keyword}`; or
  - literals (`row: literal`) with an id given by `{position}`.

Any other loop form reads no table, and the next form in the list is still tried. That covers `columns_from: fields`,
a call row with `{position}`, and a literal row with `{field}`. The reader does this already for the forms it cannot
read (`test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does`). The forms it reads for a
decorator do not change.

### 3.3 Which statement is a table's loop

For a function, and for each method of a class (the reader finds both as today, `fs_source_tree.py:354-365`), the
reader looks at the **first `for` statement among the body's own statements**. A `for` is one of the body's own
statements when it is directly in the function's body, not nested inside another block, another function or a class.
The docstring and any other statements may come before it. `async for` is not such a statement: it cannot iterate a
literal list.

That `for` holds a table when both of these hold:

1. **Its target binds plain names.** The target is one name (`for case in CASES:`, columns `("case",)`), or a tuple or
   list of names with no nesting and no starred name (`for given, when, then in CASES:` or `for (given, when, then) in
   CASES:`, columns `("given", "when", "then")`). The columns are those names, in order.
2. **Its iterable is a list of the file's.** The iterable is a list or tuple literal written in the `for` statement, or
   a bare name that the file binds at its top level (by an assignment or an import, as the file's scope reads it), which
   the function does not bind itself (as a parameter or in its body).

If either condition fails, the `for` holds no table. It stays an ordinary branch, and no later `for` of the body is
tried. Some examples:

- `for i, (a, b) in enumerate(CASES):` holds no table.
- `for x in range(3):` holds no table.
- `for item in result.items:` holds no table.
- `for case in cases:` holds no table when `cases` is a parameter (a fixture) or a name assigned in the body.

### 3.4 The rows of a loop's table

The rows are read when the iterable is one of:

- a list or tuple literal with no starred element; or
- a name assigned exactly once at the top of the file to such a literal. This is the rule the decorator form follows
  through `_lists` (`fs_source_tree.py:607-616`).

Otherwise the table's `rows` is None, the table "cannot be read". Examples: a name assigned twice, a name assigned to
`load()`, an imported name, a literal holding `*MORE`.

Each element of the list is one row, on the element's own line:

- **Call rows** (`row` a dotted name, `id` a keyword) are read exactly as the decorator form reads them
  (`_row`, `fs_source_tree.py:669-675`). A call of the form's `row` is written. Its id is the string literal at the
  form's keyword, and its cells are the heads of its positional arguments. Any other element is not written. A tuple
  element then keeps the heads of its elements as cells, and any other element has no cells.
- **Literal rows** (`row: literal`, `id` a position `p`):
  - A tuple or list literal with no starred element is written. Its cells are the heads of its elements in order
    (`_head`: a call's callee, a bare name, an attribute's last name, else None). Its id is the element at `p` when that
    element is a string literal, else None (also when the row has no element at `p`).
  - Any other element is not written, with id None and no cells. This includes a bare name, a call, a dict, and a tuple
    holding a starred element.

Since the columns are every name the loop binds, an id written at a position is also a column, and its head is a cell
like any other. The result column is still found by the guard's `columns[-1]` in `table.columns`.

### 3.5 The table

The table read from a loop is `Table(line, columns, rows, form, runs)` where:

- `line` and `runs` are both the line of the `for` statement;
- `columns` are the bound names (3.3);
- `rows` are the rows of 3.4, or None;
- `form` is the index of the first form in the framework's list that the reader reads (3.2) and that is a loop form.

A function holds its decorator tables first, in decorator order, as today, and then the table of its loop, if it has
one. With no readable loop form in the list, no loop is read, and a function holds only its decorator tables with
`runs=0`, as today. The existing case "a test whose own body loops over cases", under the pytest form only, still gives
one table with `runs == 0`.

The reader's module docstring (`fs_source_tree.py:106-113`) is rewritten to say how a loop's table is read, in the
terms of 3.2 to 3.5. It no longer says "Only the forms whose holder is a decorator ... are read".

### 3.6 `runs` honoured by the checks

`_branches` drops the block at line `runs` whose keyword is `for`, for each table of the function whose `runs` is not 0.
Line 0 never matches a real line, so a decorator table changes nothing. Both callers use `_branches` and behave the same:

- the guard `scenario-coverage` (`_covered`, `scenarios.py:152-171`), with its problem "`<test>` has a `for` in its
  body";
- `tiers.<tier>.plain_tables` (`plain`, `scenarios.py:64-82`).

Concretely, for a table test whose body is:

```python
def test_publish(subtests):
    for given, when, then in CASES:
        with subtests.test(given):
            if given:
                pass
            for step in when:
                assert step
            assert then
```

the loop at the `for given, when, then` line is not reported. The `if` and the inner `for step in when` are each
reported, at their own lines, in today's words. A `with` is reported only if the language lists it under `branching`
(Python lists `if, match, try, for, while`, `python.yaml:55`).

The rest of scenario-coverage works on a loop's table as on any table:

- Its rows are checked by `_rows`, and its result heads cover variants.
- A variant with no row and no standalone test is reported at `table.line`, which is the `for` line.
- Rows that cannot be read are reported at that line with today's words and fix ("the rows of the table cannot be
  read").
- A row that is not written is reported as "row is not a literal" for a literal form, and as "row is not a
  `<row>(...)`" for a call form. Both words exist today (`scenarios.py:193`).
- A function that holds a loop's table is no standalone test, just as a function with a decorator table is not.

The module docstring of `scenarios.py` (lines 15-17) and the docstring of `plain` say that the statement that runs a
table's rows is not a branch of its test. They say this without naming the kind of form.

### 3.7 What does not change

- The bundled profiles `cli`, `web` and `xarch`, `architecture.yaml` and the `pytest` preset write only the decorator
  form. Their findings, the golden docs and the recorded corpora under `tests/bootstrap/corpora/` stay byte for byte.
- The form loader, `keys.yaml`, `FACTS`, `NEEDS`, the `writing` templates and `docs_template.py` are untouched.
- `tests/bootstrap/test_needs_agree.py` stays green unchanged. If it fails, that is a finding to diagnose, not a test to
  edit.

### 3.8 Docs

- CHANGELOG, under `## [Unreleased]` / `### Changed`. In the 6.4 bullet (`CHANGELOG.md:100-104`), the sentence "Python
  supplies `function.tables.decorator`, and not `call` or `loop`." becomes "Python supplies `function.tables.decorator`
  and `function.tables.loop`, and not `call`." Nothing else in that bullet changes. Then add a new bullet, after it,
  which says:
  - Python's reader reads a table from the first `for` of a test's own body over a list literal of the file (`for
    given, when, then in CASES:`), its columns the names the loop binds. Its rows are calls of the form's `row` with a
    keyword id, or tuple or list literals with an id at a position.
  - That `for` is not reported as a branch by scenario-coverage or `plain_tables`.
- README: two sentences say Python supplies every fact exactly "but `function.tables.call` and
  `function.tables.loop`" (`README.md:180-181` and `README.md:511-512`). Both now say "but `function.tables.call`". The
  first says that a framework writing a `call` form under Python is refused at that entry (`testing.tables.0.call`),
  and drops "or `loop`". Neither sentence gets any other edit.
- Golden docs: regenerated, the diff read, and no change expected.

## 4. Tests

The tiers follow the repository's layout:

- unit (adapter): `tests/modules/rules/adapters/...`, which runs the real reader on Python text written to `tmp_path`.
  This is the only place Python source is parsed.
- unit (logic): `tests/modules/rules/application/logic/...` and `tests/modules/spec/...`, which run the checks or the
  profile loader on hand-built values.
- wired: `tests/bootstrap/...`, which drives the source check with a profile file on disk, through the real reader.

Every new or changed test is written first and seen to fail. Parametrized tests use `pytest.param(..., id=...)`. The
examples are simple, and the Python source uses absolute `app.` imports.

In the table below, `LOOP` is `TableForm("bound", None, (), RowId(position=0), loop=True)` and `LOOP_CALL` is
`TableForm("bound", None, ("case",), RowId(keyword="name"), loop=True)`.

| # | Test | Tier, file | Why this tier |
|---|---|---|---|
| R1 | Under `(LOOP,)`, `CASES = [("a document is published", Go(1), Published), ("gone", Go(2), Gone)]` at the top and `def test_go(subtests):` with `for name, when, then in CASES:` in the body give exactly one table: `Table(<for line>, ("name", "when", "then"), (Row(<line>, True, "a document is published", (None, "Go", "Published")), Row(<line>, True, "gone", (None, "Go", "Gone"))), form=0, runs=<for line>)` | unit (adapter), `tests/modules/rules/adapters/test_fs_source_tree.py` | The card's named deliverable, read by the real reader |
| R2 | Parametrized over iterables. `CASES` (assigned once), `[(...)]`, and `((...),)` give readable rows. `load()`, `CASES` assigned twice, `CASES = load()`, an imported `CASES`, and `[*MORE]` give a table with `rows is None` | same file | It pins 3.3 condition 2 together with 3.4 |
| R3 | Parametrized over loops that hold no table, each giving `tables == ()`: a nested target, `for x in range(3)`, `for x in obj.items`, `for c in cases` with `cases` a parameter, `for c in cases` with `cases` assigned in the body, a `for` nested in an `if` or a `with`, an `async for`, and a body with no `for` | same file | It pins 3.3. An ordinary loop is not taken for a table |
| R4 | A body with two top-level `for` statements over `CASES` gives one table, whose `runs` is the first `for`'s line | same file | "The first `for`" (3.3) |
| R5 | Parametrized over literal rows: a list row is written; a bare name, a call, a dict and `(*BASE, x)` are not written (id None, cells `()`); a row whose position-0 element is no string has id None; a row shorter than the id's position has id None | same file | It pins 3.4's literal rows |
| R6 | Under `(LOOP_CALL,)`, rows `[case("a", Go(1), Published, name="x"), ("b", Go(2), Gone)]` give `Row(.., True, "x", (None, "Go", "Published"))` and `Row(.., False, None, (None, "Go", "Gone"))` | same file | Call rows of a loop are read as a decorator's are |
| R7 | Under `(PYTEST, LOOP)`, a function with `@pytest.mark.parametrize(...)` and a top-level loop over `CASES` holds two tables, `[(0, 0), (1, <for line>)]` as `(form, runs)`, the decorator's first | same file | Mixed forms, index tagging and order (3.5) |
| R8 | Update of `test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does` (`:500-511`). Its "a loop form" case becomes `TableForm("fields", None, (), RowId(position=0), loop=True)`, renamed to the id "a loop form whose columns are the fields of each row", and it stays unread. Add the cases "a loop form whose call row has an id by position" (`TableForm("bound", None, ("case",), RowId(position=0), loop=True)`) and "a loop form whose literal row has an id by field" (`TableForm("bound", None, (), RowId(field="name"), loop=True)`). Each is run on a text whose `test_go` loops over `CASES`, so that each case fails only because of the form | same file | It pins 3.2's boundary. The current case uses `TABLE`, which has no loop, so it would pass vacuously |
| R9 | Unchanged: `test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement`, the case "a test whose own body loops over cases" under `(PYTEST,)`, which keeps `runs == 0` | same file (existing) | A decorator-only framework reads no loop |
| S1 | `_covered` through `violations`. A test holding `table(...)` with `runs=15` and `blocks=((14, "if"), (15, "for"), (16, "for"))` reports the `if` at 14 and the `for` at 16, not the `for` at 15 | unit (logic), `tests/modules/rules/application/logic/test_scenarios.py` (`replace(table, runs=15)`, as at `:280`) | The exemption is pure logic on facts |
| S2 | The same function with `runs=0` reports all three (today's behaviour) | same file | Line 0 matches nothing |
| S3 | `runs=15` with `blocks=((15, "while"),)` still reports the `while`. Only a `for` at `runs` is dropped | same file | It pins "whose keyword is `for`" |
| S4 | `plain` on `BRANCHED` with `runs=12` reports only the `if` expression at 11. With `runs=0` it is unchanged (the existing test at `:236-245`) | same file | The second caller of `_branches` |
| S5 | A loop table (`runs=9`, `form=1`) under a framework whose `tables` are `(PYTEST_FORM, LOOP)` gets its unwritten literal row reported as "row is not a literal". A variant with no row is reported at the table's line 9 | same file | The rest of the guard reads a loop table by its slots, not its kind |
| N1 | Flip of `test_a_loop_form_under_python_is_refused_at_its_index_for_the_tables_of_cases_a_loop_runs` (`test_profile_needs.py:606-607`). Under Python, `framed(LOOP_FORM)` has no problems and `approximate == ()`. Rename it `test_a_loop_form_under_python_loads` | unit (logic), `tests/modules/spec/application/logic/test_profile_needs.py` | It pins 3.1 |
| N2 | Update of `test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call_and_of_a_loop` (`:129-131`). It becomes `..._but_the_tables_of_a_call`, with the exception `("function.tables.call",)` only | same file | It pins 3.1 |
| N3 | Unchanged and green: the call-form refusals (`:601-604`, `:609-612`, `:624-631`) and `unread(0, "decorator")` under `UNTABLED` | same file (existing) | `call` stays unsupplied (a named dodge) |
| N4 | `xarch profile explain testing.tables.loop --format json` gives `needs == [{"fact": "function.tables.loop", "meaning": FACTS["function.tables.loop"], "grade": "exact"}]` | wired, `tests/bootstrap/test_profile_explain.py` | What a user sees with the bundled Python file |
| E1 | End to end, under a test-only framework written inline in the profile, as `test_other_framework.py` writes one. Its `testing` is `{files: ["test_*.py"], functions: "test_*", tables: [{loop: true, columns_from: bound, row: literal, id: {position: 0}}]}`, with the guard `scenario-coverage` (`columns: [given, when, then]`, `file: "test_{name:snake}.py"`; the id at position 0 is the `given` text) and `plain_tables` on its tier. A test file whose `test_publish` loops `for given, when, then in CASES:` over a module-level `CASES` with a row per variant of `PublishResult` gets no violation. The `for` is not reported | wired, new `tests/bootstrap/test_loop_tables.py` | The note's 9.3 proof, through the real reader and the profile loader |
| E2 | Same project, `CASES` missing the `Missing` row and no standalone test naming it: exactly one violation, "PublishResult variant Missing has no row in the table and no standalone test naming it (scenario-coverage)", at the `for` line. Adding a standalone `test_missing` that names `Missing` clears it | same file | Variants covered by rows and by standalone tests, end to end |
| E3 | Same project, an `if` inside the loop: exactly one branch violation, at the `if`'s line, "test_publish has an `if` in its body". No violation names the `for` line | same file | The `runs` exemption end to end, for both the guard and `plain_tables` (the second is not said again, `plain(..., said)`) |
| E4 | Same project, `CASES = load()`: one violation "the rows of the table cannot be read" at the `for` line | same file | The unreadable path end to end |
| G1 | Existing suites stay green unchanged: `test_table_forms.py` (no holder name in `scenarios.py`), `test_needs_agree.py`, `test_docs_templates.py` (golden docs byte for byte), `test_recorded_corpora.py`, and the bundled-profile checks | wired / architecture, existing | They prove 3.7 |

## 5. Out of scope

- A framework with no form: the guard's standalone path, `columns` refused with no form, and `plain_tables` refused
  with no form. These belong to card 6.6 (note 8, item 6; note 3).
- The second frameworks of note section 9, items 1 and 2: the test-only `stub.yaml` with a `call` and a `loop` form on
  hand-built facts, a test-only language file's `writing`, and the no-form framework. Also README, CHANGELOG and
  `profile explain` texts beyond the lines of 3.8, and the closing re-grep. These belong to card 6.7 (note 8, item 7).
  E1 to E4 here write their framework inline, so they need no `stub.yaml`.
- Any `call` support in the Python reader (a named dodge, note line 449).
- Loop forms whose `columns_from` is `fields`, call rows with an id by position, and literal rows with an id by field.
  The reader does not read them (3.2). They are not refused either: they load, and read no table.
- A list assigned inside the test's body, or a loop nested in another block, as a table (3.3).
- Golden-doc wording for a loop form (`docs_template.py`). No bundled profile writes one.
- Any change to the form loader, `keys.yaml`, `FACTS`, `NEEDS`, the `writing` templates, the recorded corpora, the
  golden docs or the bundled profiles.

## 6. Files the work touches

- `xarch/architectures/presets/language/python.yaml`: `supplies` gains `function.tables.loop: exact`.
- `xarch/modules/rules/adapters/fs_source_tree.py`: the loop read in `_function` (`:368-382`), a reads-check for loop
  forms beside `_reads` (`:642-646`), literal rows beside `_row` (`:669-675`), and the module docstring (`:106-113`).
- `xarch/modules/rules/application/logic/scenarios.py`: `_branches` (`:174-182`) takes the `runs` lines of the
  function's tables, plus the module docstring and `plain`'s docstring. No string literal naming a holder.
- Tests:
  - `tests/modules/rules/adapters/test_fs_source_tree.py`;
  - `tests/modules/rules/application/logic/test_scenarios.py`;
  - `tests/modules/spec/application/logic/test_profile_needs.py`;
  - `tests/bootstrap/test_profile_explain.py`;
  - new `tests/bootstrap/test_loop_tables.py`.
- `CHANGELOG.md` and `README.md`, as in 3.8.

## 7. Review focus for the planner

These are input classes the spec implies and that are easy to miss:

- **A standalone test that happens to loop.** Under a framework with a loop form, a test whose first own `for` runs
  over a file-level list (`for v in VARIANTS: assert v`) becomes a table test. It loses its standalone credit and falls
  under `plain_tables`. This is by design (3.3). E2 should show that a standalone test which does not loop over a
  file-level list still credits its variant.
- **The `for` exemption is per line, not per keyword.** A second `for` over the same `CASES`, nested in the loop or
  after it, is still a branch (R4, S1).
- **A shadowed name.** `def test_a(CASES): for a, b in CASES:` or `CASES = [...]` inside the body, with a module-level
  `CASES` also present, holds no table: the function binds the name itself (R3).
- **The docstring before the loop**, and a loop with an `else:` clause. Both hold a table. The `else` block is part of
  the `for` statement, and the reader records no separate block for it.
- **Two loop forms in the list.** The first readable loop form reads the loop, and its index is the table's `form`.
  A loop form the reader cannot read, written first, is skipped (R8).

---

# 6.5 The loop form of a table, read by the Python reader: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python's reader reads a table of cases from the first `for` of a test's own body over a list of the file's (`for given, when, then in CASES:`), Python's data file supplies `function.tables.loop`, and scenario-coverage and `plain_tables` stop reporting the loop that runs a table's rows as a branch.

**Architecture:** The reader adapter (`fs_source_tree.py`) gains `_loop`, `_reads_loop`, `_loop_columns` and `_literal`. `_function` appends the loop's table after the decorator tables, with `runs` set to the `for` line. The checks (`scenarios.py`) learn only one thing: `_branches` drops the `for` block at a table's `runs` line. It never asks which form read the table. `python.yaml` gains one `supplies` line.

**Tech Stack:** Python 3, `ast`, pytest, uv, ruff.

**Spec:** `docs/superpowers/specs/6-5-reader-the-loop-d04cc54c.md`. It is reproduced in full above this plan. Executors read both.

## Global Constraints

- Python appears only in the reader adapter (`xarch/modules/rules/adapters/fs_source_tree.py`) and in the data files under `xarch/architectures/presets/`. The loop's syntax (`ast.For`, its target, its iterable) is read only in `fs_source_tree.py`.
- `scenarios.py` holds no string literal `"decorator"`, `"call"` or `"loop"` (`tests/architecture/test_table_forms.py` pins this). It honours `Table.runs` as a line and never asks which form read the table.
- Docstrings in `scenarios.py` must not write a branching keyword quoted as code (`` `for` ``, `` `if` ``...): `tests/architecture/test_language_seam.py` fails on it. Say "the statement that runs a table's rows" or "the loop" in plain prose.
- Python's reader does not gain `call` support. `function.tables.call` stays unsupplied and its refusal stays tested.
- Today's pytest behaviour stays byte for byte for existing profiles. The recorded corpora (`tests/bootstrap/corpora/`) and the golden docs (`docs/{cli,web,xarch}/testing.md`) must not change. Any change in them is a defect of the branch.
- `Table.runs` keeps its meaning: "the line of the statement of the test's own body that runs its rows, 0 when none does". No new field.
- The form loader (`profile_checks.py`), `keys.yaml`, `FACTS`, `NEEDS`, the `writing` templates and `docs_template.py` are not touched.
- `tests/bootstrap/test_needs_agree.py` stays green unchanged. If it fails, diagnose it. Do not edit it.
- No comments in xarch's code, only docstrings. Never run `ruff --fix`. Tests are written first and seen to fail. Examples are simple and use absolute `app.` imports. Parametrized tests use `pytest.param(..., id=...)`.
- README and CHANGELOG lines go under `## [Unreleased]`. Golden docs are regenerated and their diff read, never edited by hand.
- `.claude/` stays out of commits. Nothing is pushed. Line length is 140 (`ruff.toml`).
- Gates, each passing on this branch alone with the full suite green: `uv run pytest -q` (over two minutes: run it in the background with a `timeout` and read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## Facts the spec gets slightly wrong (verified by prototype; follow these)

The whole plan was prototyped on a scratch copy of this branch. The full suite passed (6101 tests), and so did all five gates.

1. **`LOOP_CALL`'s row cannot be `("case",)`.** A row is matched by the path its import binds. `from app.cases import case` binds `("app", "cases", "case")`, and no `from` import binds `("case",)`. The plan uses `LOOP_CALL = TableForm("bound", None, ("app", "cases", "case"), RowId(keyword="name"), loop=True)`, with `from app.cases import case` in the test text (absolute `app.` imports, as the project rules ask).
2. **A loop directly over `load()` holds no table.** It does not hold a table whose rows cannot be read. Spec 3.3 condition 2 says the iterable must be a list or tuple literal or a bare name. R2 lists "`load()`" among the iterables whose rows are None, but that contradicts 3.3, and 3.3 wins, just as `for x in range(3):` holds no table. `CASES = load()` (a *name* of the file bound to a call) does hold a table whose rows are None. The plan tests `load()` in the "holds no table" test and `CASES = load()` in the "rows cannot be read" test.
3. **The JSON `needs` entry also carries `"note": None`.** N4 expects `[{"fact": "function.tables.loop", "meaning": FACTS["function.tables.loop"], "grade": "exact", "note": None}]`.
4. **`problems()` in `tests/modules/spec/profiles.py` raises when the profile loads.** It wraps `pytest.raises(InvalidArchitecture)`. So N1 asserts only `parsed(framed(LOOP_FORM)).approximate == ()`, and `parsed` itself fails if the profile is refused.
5. **`_covered` calls `_branches` once per matching table.** This is existing behaviour: a function with two tables that both carry the guard's columns reports each branch twice. This card does not change it, and no test here pins a function with two guard tables.
6. **The literal `"for"` in `scenarios.py` passes both architecture guards.** `test_language_seam.py` flags only tokens (the private prefix, `__call__`, the shebang, `None`, comment markers) and keywords quoted in backticks. A bare `"for"` literal is neither. The spec asks for exactly this ("drops the block at line `runs` whose keyword is `for`"), and S3 pins it.
7. **Task order makes every new test fail first.** Task 3's end-to-end tests fail before Task 3's `_branches` change (they report the `for` line), so they belong in Task 3, after the reader of Task 2. Some negative reader tests ("holds no table", R3) pass before Task 2 as well. They pin that ordinary loops stay untouched, and the step that runs them says so.

## Review Focus

1. **A standalone test that happens to loop.** A test whose first own `for` runs over a list of the file's becomes a table test and loses its standalone credit. One that does not loop over such a list keeps it. The test is in Task 3: `test_a_standalone_test_that_names_the_variant_and_runs_over_no_list_of_the_file_covers_it`.
2. **The exemption is per line, not per keyword.** A second `for` over the same `CASES`, nested in the loop or written after it, is still a branch. Only a `for` at `runs` is dropped, and a `while` there is not. The tests are in Task 2 (`test_the_first_loop_of_the_body_s_own_statements_is_the_table_and_only_it`, the case "a second loop over the same list, nested and after") and Task 3 (`test_the_statement_that_runs_a_table_s_rows_is_no_branch_of_its_test`).
3. **A shadowed name.** `def test_a(CASES):` or `CASES = [...]` in the body, with a module-level `CASES` also present, holds no table. The tests are in Task 2 (`test_a_loop_that_binds_no_plain_names_or_runs_over_no_list_of_the_file_holds_no_table`, the cases "a loop over a parameter named as the file's list" and "a loop over a name the body rebinds").
4. **The docstring before the loop, and a loop with an `else:`.** Both hold a table. The test is in Task 2 (`test_the_first_loop_of_the_body_s_own_statements_is_the_table_and_only_it`).
5. **Two loop forms in the list, the first unreadable.** The first loop form the reader reads gives the table its `form` index, and an unreadable one written first is skipped. The test is in Task 2 (`test_a_loop_is_read_by_the_first_loop_form_the_reader_reads_and_tagged_with_its_index`).

---

### Task 1: Python's data file supplies `function.tables.loop`

The loop form now loads under Python. The reader does not read it until Task 2, so for one commit a loop form loads and reads no table. The full suite stays green, because no bundled profile writes a loop form.

**Files:**
- Modify: `xarch/architectures/presets/language/python.yaml:102`
- Modify: `tests/modules/spec/application/logic/test_profile_needs.py:129-131` (N2), `:606-607` (N1)
- Modify: `tests/bootstrap/test_profile_explain.py` (append after the last line, `:389`) (N4)
- Modify: `README.md:179-181`, `README.md:511-512`
- Modify: `CHANGELOG.md:102-103`

**Interfaces:**
- Consumes: nothing new.
- Produces: `python.yaml`'s `supplies` holds `function.tables.loop: exact`. `PYTHON.checked.supplies` (from `tests.modules.spec.languages`) then grades every fact of `FACTS` `EXACT` except `function.tables.call`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_needs.py`, replace lines 129-131:

```python
def test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call_and_of_a_loop():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {
        fact: EXACT for fact in FACTS if fact not in ("function.tables.call", "function.tables.loop")}
```

with:

```python
def test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {
        fact: EXACT for fact in FACTS if fact != "function.tables.call"}
```

In the same file, replace lines 606-607:

```python
def test_a_loop_form_under_python_is_refused_at_its_index_for_the_tables_of_cases_a_loop_runs():
    assert problems(framed(LOOP_FORM)) == [unread(0, "loop")]
```

with:

```python
def test_a_loop_form_under_python_loads():
    assert parsed(framed(LOOP_FORM)).approximate == ()


def test_a_loop_form_written_after_a_call_form_loads_and_the_call_form_is_still_refused_at_its_own_index():
    assert problems(framed(CALL_FORM, LOOP_FORM)) == [unread(0, "call")]
```

(`parsed` raises `InvalidArchitecture` when the profile is refused. `problems` raises when it loads. So N1 uses `parsed` alone.)

Append to `tests/bootstrap/test_profile_explain.py`, after `test_the_list_of_table_forms_needs_no_fact_of_its_own`:

```python


def test_the_loop_holder_of_a_table_form_says_python_supplies_its_fact_exactly():
    loop = json.loads(runner.invoke(app, ["profile", "explain", "testing.tables.loop", "--format", "json"]).output)
    assert loop["needs"] == [{"fact": "function.tables.loop", "meaning": FACTS["function.tables.loop"], "grade": "exact",
                              "note": None}]
    text = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.loop"]).output.split())
    assert ("needs: function.tables.loop: the facts of the source its check reads, which Python supplies "
            "exactly") in text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py`
Expected: 4 FAIL:
- `test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call` (the dict holds no `function.tables.loop`);
- `test_a_loop_form_under_python_loads` (`InvalidArchitecture`: `testing.tables.0.loop: its check reads function.tables.loop ...`);
- `test_a_loop_form_written_after_a_call_form_loads_and_the_call_form_is_still_refused_at_its_own_index` (an extra `testing.tables.1.loop` problem);
- `test_the_loop_holder_of_a_table_form_says_python_supplies_its_fact_exactly` (`"grade": "absent"`).

The call-form refusals (`test_a_call_form_under_python_is_refused_at_its_index_for_the_tables_of_cases_a_call_holds`, `test_a_call_form_written_after_the_decorator_form_is_refused_at_its_own_index_and_the_decorator_form_is_not`, `test_a_call_form_written_in_a_testing_preset_is_refused_at_its_index`) and `test_the_keys_that_read_tables_add_no_table_fact_of_their_own_beside_the_form_that_needs_it` (`unread(0, "decorator")` under `UNTABLED`) pass, and stay unchanged (N3).

- [ ] **Step 3: Supply the fact**

In `xarch/architectures/presets/language/python.yaml`, replace line 102:

```yaml
  function.tables.decorator: exact
```

with:

```yaml
  function.tables.decorator: exact
  function.tables.loop: exact
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_needs_agree.py`
Expected: PASS.

- [ ] **Step 5: Say it in README and CHANGELOG**

In `README.md`, replace lines 179-181:

```markdown
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call` and `function.tables.loop`, so a framework that writes a `call`
or `loop` form under Python is refused at that entry (`testing.tables.0.call`). One fact is never written under
```

with:

```markdown
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call`, so a framework that writes a `call` form under Python is
refused at that entry (`testing.tables.0.call`). One fact is never written under
```

In `README.md`, replace lines 511-512:

```markdown
  key and the fact. Python's reader supplies every fact exactly but `function.tables.call` and
  `function.tables.loop`, and none partly, so a Python project never sees this line.
```

with:

```markdown
  key and the fact. Python's reader supplies every fact exactly but `function.tables.call`, and none partly, so a
  Python project never sees this line.
```

In `CHANGELOG.md` (the 6.4 bullet under `## [Unreleased]` / `### Changed`), replace lines 102-103:

```markdown
  function.tables.call ...`). Python supplies `function.tables.decorator`, and not `call` or `loop`. A language data
  file that writes `function.tables` under `supplies` is refused as an unknown fact.
```

with:

```markdown
  function.tables.call ...`). Python supplies `function.tables.decorator` and `function.tables.loop`, and not
  `call`. A language data file that writes `function.tables` under `supplies` is refused as an unknown fact.
```

Nothing else in that bullet changes.

- [ ] **Step 6: Run the README and docs guards**

Run: `timeout 600 uv run pytest -q tests/architecture tests/bootstrap/test_docs_templates.py tests/bootstrap/test_docs.py`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add xarch/architectures/presets/language/python.yaml tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py README.md CHANGELOG.md
git commit -m "Python's data file supplies function.tables.loop, so a framework that writes a loop form loads under Python, and only a call form is refused

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The Python reader reads the table of a test's loop

**Files:**
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:106-113` (the last paragraph of the module docstring), `:375` (`_function`), and insert new functions before `_argument` (`:649`)
- Line numbers are as of the start of this task. Step 1 inserts lines near the top of the test file and Step 5 inserts lines in the reader, so find each later place by the text quoted in its step.
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`: constants after `PYTEST` (`:33-34`); `LOOPED_TABLE` before `test_a_parametrized_function_lists_its_rows_with_their_ids_and_the_names_heading_their_values` (`:388`); the parametrize list and body of `test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does` (`:501-510`); new tests appended at the end of the file

**Interfaces:**
- Consumes: `TableForm(columns_from, rows, row, id, decorator=(), call=(), loop=False)` and `RowId(keyword="", field="", position=None)` from `xarch.profile_values.testing`; `Table(line, columns, rows, form, runs)` and `Row(line, written, id, cells)` from `xarch.modules.rules.domain.parsed`; the existing helpers in `fs_source_tree.py`: `_scope(node) -> Scope`, `_row(node, scope, form) -> Row`, `_head(node) -> str | None`, and `Scope = dict[str, Ref]`.
- Produces: `Function.tables` holds, after the decorator tables, at most one table read from the body's first own `for`: `Table(for_line, bound_names, rows_or_None, form=<index of the first loop form _reads_loop accepts>, runs=for_line)`. Task 3 relies on `runs` being the `for` statement's line, the same line the reader records for that `for` in `Function.blocks` as `(line, "for")`.
- New private functions in `fs_source_tree.py`: `_loop(node, scope, lists, forms) -> Table | None`, `_reads_loop(form: TableForm) -> bool`, `_loop_columns(target: ast.expr) -> tuple[str, ...] | None`, `_literal(node: ast.expr, position: int | None) -> Row`.

- [ ] **Step 1: Add the loop forms the tests read with**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, after lines 33-34 (`PYTEST = TableForm(...)`, ending `decorator=("pytest", "mark", "parametrize"))`), insert:

```python
LOOP = TableForm("bound", None, (), RowId(position=0), loop=True)
"""A form whose rows a loop of the test's body runs, each a tuple or list literal whose id is its first value."""
LOOP_CALL = TableForm("bound", None, ("app", "cases", "case"), RowId(keyword="name"), loop=True)
"""A form whose rows a loop of the test's body runs, each a call of app.cases.case whose id is its keyword name."""
```

- [ ] **Step 2: Write the failing test of the forms the reader cannot read (R8)**

Before `def test_a_parametrized_function_lists_its_rows_with_their_ids_and_the_names_heading_their_values` (line 388, just after the closing `'''` of `TABLE`), insert:

```python
LOOPED_TABLE = TABLE.replace("    if given:\n        pass\n", "    for each in CASES:\n        pass\n")
"""TABLE, the body of its test a loop over the list CASES of the file."""


```

Replace the last parametrize entry and the body of `test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does` (lines 506-510):

```python
    pytest.param(TableForm("fields", None, (), RowId(position=0), loop=True), id="a loop form"),
])
def test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does(tmp_path, skipped):
    assert parsed(tmp_path, TABLE, (skipped,)).functions[0].tables == ()
    assert [t.form for t in parsed(tmp_path, TABLE, (skipped, PYTEST)).functions[0].tables] == [1]
```

with:

```python
    pytest.param(TableForm("fields", None, (), RowId(position=0), loop=True),
                 id="a loop form whose columns are the fields of each row"),
    pytest.param(TableForm("bound", None, ("pytest", "param"), RowId(position=0), loop=True),
                 id="a loop form whose call row has an id by position"),
    pytest.param(TableForm("bound", None, (), RowId(field="name"), loop=True),
                 id="a loop form whose literal row has an id by field"),
])
def test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does(tmp_path, skipped):
    assert parsed(tmp_path, LOOPED_TABLE, (skipped,)).functions[0].tables == ()
    assert [t.form for t in parsed(tmp_path, LOOPED_TABLE, (skipped, PYTEST)).functions[0].tables] == [1]


def test_the_text_the_forms_the_reader_cannot_read_are_tried_on_is_read_by_the_forms_it_reads(tmp_path):
    tables = parsed(tmp_path, LOOPED_TABLE, (PYTEST, LOOP)).functions[0].tables
    assert [(t.form, t.runs) for t in tables] == [(0, 0), (1, line_of(LOOPED_TABLE, "for each in CASES"))]
```

The last test proves that `LOOPED_TABLE` is read by a loop form the reader *does* read. So each unread case fails only because of its form, not because of the text.

Leave `test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement` unchanged (R9). Its case "a test whose own body loops over cases" runs under `(PYTEST,)` and keeps `runs == 0`.

- [ ] **Step 3: Write the failing tests of the loop's table (R1-R7)**

Append at the end of `tests/modules/rules/adapters/test_fs_source_tree.py`:

```python


LOOPED = '''from app.results import Gone, Go, Published

CASES = [
    ("a document is published", Go(1), Published),
    ("gone", Go(2), Gone),
]


def test_go(subtests):
    """Each case."""
    for name, when, then in CASES:
        assert run(when) == then
'''


def test_a_loop_of_a_test_s_own_body_over_a_list_of_the_file_is_its_table_run_by_that_loop(tmp_path):
    loop = line_of(LOOPED, "for name, when, then")
    assert parsed(tmp_path, LOOPED, (LOOP,)).functions[0].tables == (Table(loop, ("name", "when", "then"), (
        Row(line_of(LOOPED, "Go(1)"), True, "a document is published", (None, "Go", "Published")),
        Row(line_of(LOOPED, "Go(2)"), True, "gone", (None, "Go", "Gone"))), form=0, runs=loop),)


def looping(iterable: str = "CASES", head: str = "CASES = [('x', 1)]\n", signature: str = "subtests",
            body: str = "    for a, b in {iterable}:\n        assert a == b\n") -> str:
    """A file whose top level is head, then a test of that signature whose body is body, over the iterable."""
    return f"{head}\n\ndef test_a({signature}):\n{body.format(iterable=iterable)}"


@pytest.mark.parametrize("text", [
    pytest.param(looping(), id="a name assigned once at the top of the file"),
    pytest.param(looping("[('x', 1)]"), id="a list literal written in the loop"),
    pytest.param(looping("(('x', 1),)"), id="a tuple literal written in the loop"),
    pytest.param(looping(head="CASES: list = [('x', 1)]\n"), id="a name annotated and assigned once"),
])
def test_the_rows_of_a_loop_are_read_from_a_literal_or_the_name_of_a_module_level_one(tmp_path, text):
    rows = parsed(tmp_path, text, (LOOP,)).functions[0].tables[0].rows
    assert [(row.written, row.id, row.cells) for row in rows] == [(True, "x", (None, None))]


@pytest.mark.parametrize("text", [
    pytest.param(looping(head="CASES = [('x', 1)]\nCASES = [('y', 2)]\n"), id="a name assigned twice"),
    pytest.param(looping(head="CASES = load()\n"), id="a name assigned to a call"),
    pytest.param(looping(head="from app.cases import CASES\n"), id="an imported name"),
    pytest.param(looping("[*MORE]"), id="a list literal holding a starred value"),
    pytest.param(looping(head="CASES = [*MORE]\n"), id="a name assigned to a list holding a starred value"),
])
def test_a_loop_over_a_name_of_the_file_whose_rows_are_no_literal_holds_a_table_whose_rows_cannot_be_read(tmp_path,
                                                                                                        text):
    tables = parsed(tmp_path, text, (LOOP,)).functions[0].tables
    assert [(table.columns, table.rows, table.runs) for table in tables] == [(("a", "b"), None, line_of(text, "for a"))]


@pytest.mark.parametrize("text", [
    pytest.param(looping(body="    for i, (a, b) in enumerate(CASES):\n        assert a\n"), id="a nested target"),
    pytest.param(looping(body="    for a, (b, c) in CASES:\n        assert a\n"), id="a target holding a tuple"),
    pytest.param(looping(body="    for a, *b in CASES:\n        assert a\n"), id="a target holding a starred name"),
    pytest.param(looping(body="    for a.b in CASES:\n        assert a\n"), id="a target that is an attribute"),
    pytest.param(looping("range(3)"), id="a loop over a call"),
    pytest.param(looping("load()"), id="a loop over a call of the file's"),
    pytest.param(looping("result.items"), id="a loop over an attribute"),
    pytest.param(looping("CASES + MORE"), id="a loop over an expression"),
    pytest.param(looping("[x for x in CASES]"), id="a loop over a comprehension"),
    pytest.param(looping("cases", signature="cases"), id="a loop over a parameter"),
    pytest.param(looping("CASES", signature="CASES"), id="a loop over a parameter named as the file's list"),
    pytest.param(looping(body="    cases = [('x', 1)]\n    for a, b in cases:\n        assert a\n"),
                 id="a loop over a name the body assigns"),
    pytest.param(looping(body="    CASES = [('y', 2)]\n    for a, b in CASES:\n        assert a\n"),
                 id="a loop over a name the body rebinds"),
    pytest.param(looping("MISSING"), id="a loop over a name the file does not bind"),
    pytest.param(looping(body="    if True:\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop nested in an if"),
    pytest.param(looping(body="    with x:\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop nested in a with"),
    pytest.param(looping(body="    def inner():\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop of a function nested in the test"),
    pytest.param(looping(body="    async for a, b in CASES:\n        assert a\n"), id="an async for"),
    pytest.param(looping(body="    assert CASES\n"), id="a body with no loop"),
    pytest.param(looping(body="    while CASES:\n        assert CASES\n"), id="a body with a while"),
    pytest.param(looping(body="    for x in range(3):\n        assert x\n    for a, b in CASES:\n        assert a\n"),
                 id="a first loop that holds no table, and a later one is not tried"),
])
def test_a_loop_that_binds_no_plain_names_or_runs_over_no_list_of_the_file_holds_no_table(tmp_path, text):
    assert parsed(tmp_path, text, (LOOP,)).functions[0].tables == ()


@pytest.mark.parametrize("body, columns", [
    pytest.param("    for a in CASES:\n        assert a\n", ("a",), id="one name"),
    pytest.param("    for a, b in CASES:\n        assert a\n", ("a", "b"), id="a tuple of names"),
    pytest.param("    for (a, b) in CASES:\n        assert a\n", ("a", "b"), id="a tuple of names in brackets"),
    pytest.param("    for [b, a] in CASES:\n        assert a\n", ("b", "a"), id="a list of names, in its order"),
])
def test_the_columns_of_a_loop_are_the_names_it_binds_in_order(tmp_path, body, columns):
    assert parsed(tmp_path, looping(body=body), (LOOP,)).functions[0].tables[0].columns == columns


@pytest.mark.parametrize("body", [
    pytest.param("    \"\"\"Each case.\"\"\"\n    x = 1\n    for a, b in CASES:\n        assert a\n",
                 id="a docstring and a statement before the loop"),
    pytest.param("    for a, b in CASES:\n        assert a\n    else:\n        assert CASES\n",
                 id="a loop with an else"),
    pytest.param("    for a, b in CASES:\n        for c in a:\n            assert c\n    for a, b in CASES:\n"
                 "        assert b\n", id="a second loop over the same list, nested and after"),
])
def test_the_first_loop_of_the_body_s_own_statements_is_the_table_and_only_it(tmp_path, body):
    text = looping(body=body)
    first = line_of(text, "for a, b in CASES")
    assert [(t.line, t.runs) for t in parsed(tmp_path, text, (LOOP,)).functions[0].tables] == [(first, first)]


@pytest.mark.parametrize("row, written, id, cells", [
    pytest.param("('an outcome', Go(1), Published)", True, "an outcome", (None, "Go", "Published"), id="a tuple"),
    pytest.param("['an outcome', Go(1), results.Published]", True, "an outcome", (None, "Go", "Published"),
                 id="a list"),
    pytest.param("(1, Go(1), Published)", True, None, (None, "Go", "Published"), id="a tuple whose first value is no text"),
    pytest.param("()", True, None, (), id="a tuple shorter than the id's position"),
    pytest.param("Published", False, None, (), id="a bare name"),
    pytest.param("case('an outcome', Go(1), Published)", False, None, (), id="a call"),
    pytest.param("{'id': 'an outcome'}", False, None, (), id="a dict"),
    pytest.param("(*BASE, Published)", False, None, (), id="a tuple holding a starred value"),
])
def test_a_literal_row_of_a_loop_is_written_when_it_is_a_tuple_or_list_its_id_the_text_at_the_position(
        tmp_path, row, written, id, cells):
    text = looping(head=f"CASES = [\n    {row},\n]\n", body="    for a, b, c in CASES:\n        assert a\n")
    assert parsed(tmp_path, text, (LOOP,)).functions[0].tables[0].rows == (Row(2, written, id, cells),)


def test_an_id_by_position_reads_the_text_at_that_position(tmp_path):
    text = looping(head="CASES = [(Go(1), 'an outcome', Published)]\n")
    second = replace(LOOP, id=RowId(position=1))
    assert [row.id for row in parsed(tmp_path, text, (second,)).functions[0].tables[0].rows] == ["an outcome"]


def test_a_call_row_of_a_loop_is_read_as_a_decorator_s_row_is(tmp_path):
    text = looping(head="from app.cases import case\n\nCASES = [\n    case('a', Go(1), Published, name='x'),\n"
                        "    ('b', Go(2), Gone),\n]\n", body="    for a, b, c in CASES:\n        assert a\n")
    assert parsed(tmp_path, text, (LOOP_CALL,)).functions[0].tables[0].rows == (
        Row(4, True, "x", (None, "Go", "Published")), Row(5, False, None, (None, "Go", "Gone")))


def test_a_call_row_of_a_loop_is_its_form_s_row_by_the_import_that_binds_it(tmp_path):
    text = looping(head="from other import case\n\nCASES = [case('a', name='x')]\n",
                   body="    for a in CASES:\n        assert a\n")
    assert [row.written for row in parsed(tmp_path, text, (LOOP_CALL,)).functions[0].tables[0].rows] == [False]


MIXED = '''import pytest

CASES = [("a", 1)]


@pytest.mark.parametrize("x", [pytest.param(1, id="one")])
def test_a(x):
    for a, b in CASES:
        assert a == x
'''


def test_a_function_holds_its_decorator_s_tables_first_then_its_loop_s_each_by_its_own_form(tmp_path):
    tables = parsed(tmp_path, MIXED, (PYTEST, LOOP)).functions[0].tables
    assert [(t.form, t.line, t.runs) for t in tables] == [
        (0, line_of(MIXED, "@pytest"), 0), (1, line_of(MIXED, "for a, b"), line_of(MIXED, "for a, b"))]


@pytest.mark.parametrize("forms, index", [
    pytest.param((LOOP, LOOP_CALL), 0, id="the first of two loop forms"),
    pytest.param((replace(LOOP, columns_from="fields", id=RowId(field="name")), LOOP), 1,
                 id="a loop form the reader cannot read, written first, is skipped"),
    pytest.param((PYTEST, LOOP), 1, id="a decorator form before it"),
])
def test_a_loop_is_read_by_the_first_loop_form_the_reader_reads_and_tagged_with_its_index(tmp_path, forms, index):
    assert [t.form for t in parsed(tmp_path, looping(), forms).functions[0].tables] == [index]


def test_a_method_s_loop_is_read_too(tmp_path):
    text = "CASES = [('x', 1)]\n\nclass TestA:\n    def test_a(self):\n        for a, b in CASES:\n            assert a\n"
    assert [(f.name, len(f.tables)) for f in parsed(tmp_path, text, (LOOP,)).functions] == [("test_a", 1)]
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py`
Expected: 34 FAIL, all of them new tests that expect a table from a loop (`test_a_loop_of_a_test_s_own_body_...`, `test_the_rows_of_a_loop_...`, `test_a_loop_over_a_name_of_the_file_whose_rows_are_no_literal_...`, `test_the_columns_of_a_loop_...`, `test_the_first_loop_of_the_body_s_own_statements_...`, `test_a_literal_row_of_a_loop_...`, `test_an_id_by_position_...`, `test_a_call_row_of_a_loop_...` (both), `test_a_function_holds_its_decorator_s_tables_first_...`, `test_a_loop_is_read_by_the_first_loop_form_...`, `test_a_method_s_loop_is_read_too`, `test_the_text_the_forms_the_reader_cannot_read_are_tried_on_...`). They fail with `assert () == (Table(...),)`, an `IndexError: tuple index out of range` on `tables[0]`, or a list missing the loop's entry.
`test_a_loop_that_binds_no_plain_names_or_runs_over_no_list_of_the_file_holds_no_table` and the updated `test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does` PASS already. Today's reader reads no loop at all. These tests pin that the new reader still reads none from these.

- [ ] **Step 5: Read the loop in `_function`**

In `xarch/modules/rules/adapters/fs_source_tree.py`, `_function`, replace line 375:

```python
    tables = tuple(table for d in node.decorator_list if (table := _table(d, scope, lists, forms)) is not None)
```

with:

```python
    tables = tuple(table for d in node.decorator_list if (table := _table(d, scope, lists, forms)) is not None)
    loop = _loop(node, scope, lists, forms)
    tables += (loop,) if loop is not None else ()
```

- [ ] **Step 6: Add the loop's reading**

In the same file, insert immediately before `def _argument(call: ast.Call, place: Place | str | None) -> ast.expr | None:` (line 649, right after `_reads`):

```python
def _loop(node: ast.FunctionDef | ast.AsyncFunctionDef, scope: list[Scope], lists: dict[str, ast.expr],
          forms: tuple[TableForm, ...]) -> Table | None:
    """The table the first `for` of the function's own body holds, read in the first loop form the reader reads and
    tagged with that form's index, its line and the line that runs its rows that of the `for`; None when no such form
    is in the list, the body holds no `for` of its own, or that `for` binds no plain names or runs over no list of the
    file's."""
    index = next((i for i, form in enumerate(forms) if _reads_loop(form)), None)
    statement = next((s for s in node.body if isinstance(s, ast.For)), None)
    if index is None or statement is None:
        return None
    columns = _loop_columns(statement.target)
    values: ast.expr | None = statement.iter
    own = _scope(node)
    if columns is None:
        return None
    if isinstance(values, ast.Name):
        if values.id in own or values.id not in scope[0]:
            return None
        values, chain = lists.get(values.id), scope
    elif isinstance(values, (ast.List, ast.Tuple)):
        chain = [own, *scope]
    else:
        return None
    form = forms[index]
    rows = None
    if isinstance(values, (ast.List, ast.Tuple)) and not any(isinstance(v, ast.Starred) for v in values.elts):
        rows = tuple(_row(v, chain, form) if form.row else _literal(v, form.id.position) for v in values.elts)
    return Table(statement.lineno, columns, rows, form=index, runs=statement.lineno)


def _reads_loop(form: TableForm) -> bool:
    """Whether the reader reads tables in the form: a loop of the test's body, its column names the names the loop
    binds, a row either a call of a dotted name with its id a keyword of that call, or a literal with its id at a
    position."""
    return (form.loop and form.columns_from == "bound"
            and ((bool(form.row) and bool(form.id.keyword)) or (not form.row and form.id.position is not None)))


def _loop_columns(target: ast.expr) -> tuple[str, ...] | None:
    """The names a loop binds, in order: one name, or a tuple or list of names with none nested or starred; None for
    any other target."""
    if isinstance(target, ast.Name):
        return (target.id,)
    if isinstance(target, (ast.Tuple, ast.List)) and target.elts and all(isinstance(e, ast.Name) for e in target.elts):
        return tuple(e.id for e in target.elts if isinstance(e, ast.Name))
    return None


def _literal(node: ast.expr, position: int | None) -> Row:
    """A literal row: a tuple or list with no starred value is written, its cells the names heading its values and
    its id the string literal at position; any other value is not written, and has no id and no cells."""
    if not isinstance(node, (ast.Tuple, ast.List)) or any(isinstance(e, ast.Starred) for e in node.elts):
        return Row(node.lineno, False, None, ())
    at = node.elts[position] if position is not None and position < len(node.elts) else None
    given = at.value if isinstance(at, ast.Constant) and isinstance(at.value, str) else None
    return Row(node.lineno, True, given, tuple(_head(e) for e in node.elts))


```

Notes for the implementer:
- `node.body` is the function's own statements. A `for` nested in an `if`, a `with` or a nested `def` is not among them. `ast.AsyncFor` is a different class from `ast.For`, so an `async for` is skipped.
- `scope[0]` is the module's scope (`_functions` passes `[_scope(tree, where)]`). It holds every name the file binds at its top level, by assignment or import. `own = _scope(node)` holds the function's parameters and every name its body binds. A name in `own` is shadowed, so the loop holds no table.
- `lists` is `_lists(tree)`: the names assigned exactly once at the top level to a list or tuple literal. A name the file binds otherwise (twice, to a call, by an import) is in `scope[0]` but not in `lists`, so its table's rows are None.
- Rows written inline in the `for` are read in the function's scope chain (`[own, *scope]`). Rows of a module-level list are read in the module scope, as a decorator's are.
- `_row` is the decorator form's row reader, reused unchanged for call rows.

- [ ] **Step 7: Rewrite the reader's module docstring**

Replace the last paragraph of the module docstring, lines 106-113, from `A test function holds the tables of cases its decorators hold,` through the closing `"""`:

```text
A test function holds the tables of cases its decorators hold, each read in the first of the framework's forms
(`testing.tables`) whose decorator it is, and tagged with that form's index: its column names are the argument at
the form's `columns_from` (by its position when the call has an argument there, else by its keyword), one
comma-separated string or a list or tuple of strings; its rows the argument at its `rows`, a list or tuple literal or
the name of one assigned once at the top of the file (any other form leaves the rows unread); and a row is written
when it is a call of the form's `row`, its id the string literal the form's keyword gives. Only the forms whose
holder is a decorator, whose columns and rows are places, whose row is a call and whose id a keyword are read; any
other form reads no table.
"""
```

with:

```text
A test function holds the tables of cases its decorators hold, each read in the first of the framework's forms
(`testing.tables`) whose decorator it is, and tagged with that form's index: its column names are the argument at
the form's `columns_from` (by its position when the call has an argument there, else by its keyword), one
comma-separated string or a list or tuple of strings; its rows the argument at its `rows`, a list or tuple literal or
the name of one assigned once at the top of the file (any other form leaves the rows unread); and a row is written
when it is a call of the form's `row`, its id the string literal the form's keyword gives. A decorator's form is read
when its columns and rows are places, its row a call and its id a keyword; no statement of the body runs the rows of
its table (runs 0).

After those, a test function holds the table of the first `for` among its body's own statements, one not nested in
another block, function or class (an `async for` is none), read in the first loop form of the list the reader reads
and tagged with that form's index. That `for` holds a table when it binds plain names, one name or a tuple or list of
names with none nested or starred, which are the column names in order; and when it runs over a list or tuple literal
written in it, or over a bare name the file binds at its top level and the function does not bind. The table's line,
and the line of the statement that runs its rows, are the `for`'s. Its rows are that literal's values, or those of
the literal the name is assigned once at the top of the file (any other value, or a starred one among them, leaves
the rows unread). A loop form is read when its columns are `bound` and either its row is a call of a dotted name and
its id a keyword, each row read as a decorator's is, or its row is a literal and its id a position: a tuple or list
with no starred value is written, its cells the names heading its values and its id the string literal at that
position; any other value is not written, and has no id and no cells. A `for` that binds other names or runs over
anything else holds no table, and no later `for` is tried.

Any other form reads no table, and the next form of the list is still tried.
"""
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py`
Expected: PASS (360 tests).

Run: `timeout 600 uv run pytest -q tests/architecture tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_docs_templates.py && uv run ruff check`
Expected: PASS, and `All checks passed!`. The reader names Python's syntax only inside the seam file. The bundled profiles write no loop form, so the corpora and golden docs do not move.

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/rules/adapters/fs_source_tree.py tests/modules/rules/adapters/test_fs_source_tree.py
git commit -m "The Python reader reads the table of the first for of a test's own body over a list of the file's, its columns the names it binds and its runs the line of that for

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The statement that runs a table's rows is no branch of its test

**Files:**
- Modify: `xarch/modules/rules/application/logic/scenarios.py:174-177` (`_branches`), `:18-19` and `:21-23` (module docstring), `:65-66` (`plain`'s docstring). Line numbers are as of the start of this task. Step 5's first edit adds two lines, so find `plain`'s docstring by its text.
- Test: `tests/modules/rules/application/logic/test_scenarios.py` (append at the end, after line 282)
- Create: `tests/bootstrap/test_loop_tables.py`
- Modify: `CHANGELOG.md` (a new bullet after the 6.4 bullet edited in Task 1)

**Interfaces:**
- Consumes: from Task 2, a table the reader reads from a loop has `runs` equal to the line of the `for`, and the reader records that `for` in `Function.blocks` as `(runs, "for")`. From Task 1, Python supplies `function.tables.loop`, so a profile with a loop form loads. From the test helpers: `tests.modules.rules.builders` (`PROFILE`, `PYTEST_FORM`, `in_tests`, `profile`) and `tests.bootstrap.project` (`source_check(root, profile_path, tests) -> AppChecked`, `line_of(text, marker) -> int`).
- Produces: `_branches(function, profile)` drops every block `(line, "for")` whose line is the `runs` of one of the function's tables, when that `runs` is not 0. Both callers, `_covered` (the guard) and `plain`, use it.

- [ ] **Step 1: Write the failing logic tests (S1-S5)**

Append at the end of `tests/modules/rules/application/logic/test_scenarios.py`:

```python


RUN = replace(TABLE, runs=15)
"""TABLE, its rows run by the statement on line 15 of its test's body."""


@pytest.mark.parametrize("tables, blocks, expected", [
    pytest.param((RUN,), ((14, "if"), (15, "for"), (16, "for")), [14, 16],
                 id="the loop that runs the rows is no branch, and every other block still is"),
    pytest.param((TABLE,), ((14, "if"), (15, "for"), (16, "for")), [14, 15, 16],
                 id="a table no statement runs drops nothing"),
    pytest.param((RUN,), ((15, "while"),), [15], id="only a loop at the line that runs the rows is dropped"),
])
def test_the_statement_that_runs_a_table_s_rows_is_no_branch_of_its_test(tables, blocks, expected):
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", tables, blocks=blocks))], PROFILE)
    assert [v.line for v in found] == expected


def test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_statement_that_runs_its_rows():
    ran = replace(BRANCHED, tables=(replace(BRANCHED.tables[0], runs=12),))
    assert [str(v) for v in plain([in_tests(UNIT_TEST, functions=(ran,))], PLAIN)] == [
        "tests/modules/docs/domain/test_doc.py:11: test_doc has an `if` expression in its body, and a table test of "
        "the unit tier holds no branch (tiers.unit.plain_tables; scenario-coverage)"]


LOOP = TableForm("bound", None, (), RowId(position=0), loop=True)
"""A form whose rows a loop of the test's body runs, each a literal whose id is its first value."""


def test_a_table_a_loop_runs_is_checked_as_any_table_by_its_form_s_slots():
    checked = profile(framework=replace(PROFILE.framework, tables=(PYTEST_FORM, LOOP)))
    looped = Table(9, COLUMNS, (row("Published", written=False, id=None),), form=1, runs=9)
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", (looped,), blocks=((9, "for"),)))], checked)
    assert [(str(v), v.fix) for v in found] == [
        (f"{FILE}:10: row is not a literal (scenario-coverage)",
         "write the row's id, a sentence stating the outcome, as its value at position 0"),
        (f"{FILE}:9: PublishResult variant Missing has no row in the table and no standalone test naming it "
         "(scenario-coverage)", "add a row whose then is Missing, or a standalone test naming it")]
```

- S1 is the case "the loop that runs the rows is no branch, and every other block still is". S2 is "a table no statement runs drops nothing". S3 is "only a loop at the line that runs the rows is dropped".
- S4 is `test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_statement_that_runs_its_rows`. The `runs=0` half of S4 is the existing `test_a_table_test_of_a_tier_whose_tables_are_plain_holds_no_branch_and_one_of_another_tier_may`, unchanged.
- S5 is `test_a_table_a_loop_runs_is_checked_as_any_table_by_its_form_s_slots`.

- [ ] **Step 2: Write the failing end-to-end tests (E1-E4)**

Create `tests/bootstrap/test_loop_tables.py`:

```python
"""A framework whose table is the loop of a test's body over a list of the file's (`for given, when, then in CASES:`),
read for real by the Python reader: scenario-coverage checks its rows, and neither it nor plain_tables takes that loop
for a branch of the test."""
from pathlib import Path

from tests.bootstrap.project import line_of, source_check

PROFILE = """
name: looped
testing:
  files: ["test_*.py"]
  functions: "test_*"
  tables: [{loop: true, columns_from: bound, row: literal, id: {position: 0}}]
  mocks: {calls: [doubles.Double], spec_keywords: [of]}
parts:
  contract:   {path: modules/<module>/contract, role: results, tests: integration}
  controller:
    path: modules/<module>/application/controller.py
    role: maps
    imports:
      may: [contract, ports]
    tests: integration
  ports:      {path: modules/<module>/application/ports, role: ports, tests: integration}
tiers:
  integration: {proves: a use case, litmus: "Does it drive a controller?", plain_tables: true}
fakes: {folder: fakes, for: [ports], prefix: Fake}
guards:
  scenario-coverage:
    results: contract
    tier: integration
    suffix: Result
    columns: [given, when, then]
    file: "test_{name:snake}.py"
  stand-ins: {}
"""

APP = {
    "modules/docs/contract/__init__.py": "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "",
    "modules/docs/application/ports/repo.py":
        "from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self) -> str: ...\n",
}

PUBLISHED = '    ("a document is published", 1, Published()),\n'
MISSING = '    ("a document that is not there is missing", 2, Missing()),\n'
BODY = "        assert given and when and then\n"

TEST = '''from app.modules.docs.contract import Missing, Published

CASES = {cases}


def test_publish():
    for given, when, then in CASES:
{body}{more}'''


def publish(cases: str = f"[\n{PUBLISHED}{MISSING}]", body: str = BODY, more: str = "") -> str:
    return TEST.format(cases=cases, body=body, more=more)


TESTED = "tests/modules/docs/application/test_publish.py"


def check(tmp_path: Path, test: str) -> list[str]:
    files = {"app": APP, "tests": {"modules/docs/application/test_publish.py": test, "fakes/repo.py": "class FakeRepo: ...\n"}}
    for root, written in files.items():
        for rel, body in written.items():
            (tmp_path / root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / root / rel).write_text(body)
    (tmp_path / "looped.yaml").write_text(PROFILE)
    result = source_check(tmp_path / "app", str(tmp_path / "looped.yaml"), tmp_path / "tests")
    return [f"{v}; fix: {v.fix}" for v in result.violations]


def test_a_loop_over_a_list_of_the_file_with_a_row_per_variant_covers_the_use_case_and_is_no_branch(tmp_path):
    assert check(tmp_path, publish()) == []


def test_a_variant_with_no_row_is_reported_at_the_loop(tmp_path):
    test = publish(cases=f"[\n{PUBLISHED}]")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'for given')}: PublishResult variant Missing has no row in the table and no "
        "standalone test naming it (scenario-coverage); fix: add a row whose then is Missing, or a standalone test "
        "naming it"]


def test_a_standalone_test_that_names_the_variant_and_runs_over_no_list_of_the_file_covers_it(tmp_path):
    more = "\n\ndef test_missing():\n    assert Missing()\n"
    assert check(tmp_path, publish(cases=f"[\n{PUBLISHED}]", more=more)) == []


def test_a_branch_inside_the_loop_is_reported_once_at_its_own_line_and_the_loop_is_not(tmp_path):
    test = publish(body="        if when:\n            pass\n" + BODY)
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'if when')}: test_publish has an `if` in its body (scenario-coverage); fix: arrange "
        "from given, act with when, assert == then, and give the odd case its own test"]


def test_a_loop_over_a_name_of_the_file_bound_to_no_list_is_reported_at_the_loop_as_rows_that_cannot_be_read(tmp_path):
    test = "from app.cases import load\n" + publish(cases="load()")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'for given')}: the rows of the table cannot be read (scenario-coverage); fix: write "
        "them as a list, or as the name of a list assigned at the top of the file"]


def test_a_row_that_is_not_a_literal_is_reported_in_the_words_of_the_form(tmp_path):
    test = publish(cases=f"[\n{PUBLISHED}{MISSING}    Published,\n]")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, '    Published,')}: row is not a literal (scenario-coverage); fix: write the row's "
        "id, a sentence stating the outcome, as its value at position 0"]
```

- E1 is `test_a_loop_over_a_list_of_the_file_with_a_row_per_variant_covers_the_use_case_and_is_no_branch`.
- E2 is `test_a_variant_with_no_row_is_reported_at_the_loop`, plus `test_a_standalone_test_that_names_the_variant_and_runs_over_no_list_of_the_file_covers_it`.
- E3 is `test_a_branch_inside_the_loop_is_reported_once_at_its_own_line_and_the_loop_is_not`. `plain_tables` says the same `if` at the same line, and `plain(..., said)` drops it as already said.
- E4 is `test_a_loop_over_a_name_of_the_file_bound_to_no_list_is_reported_at_the_loop_as_rows_that_cannot_be_read`.
- The last test, `test_a_row_that_is_not_a_literal_is_reported_in_the_words_of_the_form`, is the "row is not a literal" path end to end.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py tests/bootstrap/test_loop_tables.py`
Expected: 9 FAIL:
- the S1 case of `test_the_statement_that_runs_a_table_s_rows_is_no_branch_of_its_test` (`[14, 15, 16] != [14, 16]`);
- `test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_statement_that_runs_its_rows` (an extra violation at line 12);
- `test_a_table_a_loop_runs_is_checked_as_any_table_by_its_form_s_slots` (an extra violation at line 9, "test_publish has a `for` in its body");
- all 6 tests of `test_loop_tables.py`, each with an extra violation "test_publish has a `for` in its body" at the `for` line.

The S2 and S3 cases PASS already. They pin what must not change.

- [ ] **Step 4: Drop the loop at a table's runs in `_branches`**

In `xarch/modules/rules/application/logic/scenarios.py`, replace lines 174-177:

```python
def _branches(function: Function, profile: Profile) -> list[Problem]:
    fix = "arrange from given, act with when, assert == then, and give the odd case its own test"
    language = profile.language
    found = [(line, keyword, "") for line, keyword in function.blocks if keyword in language.branching]
```

with:

```python
def _branches(function: Function, profile: Profile) -> list[Problem]:
    """Each block and each expression of the function's body that branches, in line order, but the loop at the line
    that runs the rows of one of its tables (its runs; 0 is no line)."""
    fix = "arrange from given, act with when, assert == then, and give the odd case its own test"
    language = profile.language
    runs = {(table.runs, "for") for table in function.tables if table.runs}
    found = [(line, keyword, "") for line, keyword in function.blocks
             if keyword in language.branching and (line, keyword) not in runs]
```

The rest of `_branches` is unchanged. Do not write `` `for` `` in backticks in any docstring of this file (see Global Constraints).

- [ ] **Step 5: Say it in the docstrings**

In the module docstring, replace lines 18-19:

```text
    the body of a table test holds no statement that branches (one of the language's `branching` keywords), and no
    expression that chooses between values (one of its `branching_expressions`): the odd case is its own test.
```

with:

```text
    the body of a table test holds no statement that branches (one of the language's `branching` keywords), and no
    expression that chooses between values (one of its `branching_expressions`): the odd case is its own test. The
    statement that runs a table's rows, at the line the reader gives as the table's runs, is the table and no branch
    of its test.
```

and replace lines 21-23:

```text
plain holds every table test of a tier that says `plain_tables` to the same rule as a use case's: no statement that
branches and no expression that chooses between values in its body, said once where scenario-coverage already says
it of a use case's table.
```

with:

```text
plain holds every table test of a tier that says `plain_tables` to the same rule as a use case's: no statement that
branches and no expression that chooses between values in its body, but the statement that runs a table's rows, said
once where scenario-coverage already says it of a use case's table.
```

Replace `plain`'s docstring (lines 65-66):

```python
    """The branches in the body of each table test of a tier whose tables are plain, but where said already holds a
    violation of the rule at that file and line."""
```

with:

```python
    """The branches in the body of each table test of a tier whose tables are plain, the statement that runs a table's
    rows being none, but where said already holds a violation of the rule at that file and line."""
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py tests/bootstrap/test_loop_tables.py`
Expected: PASS.

Run: `timeout 600 uv run pytest -q tests/architecture tests/bootstrap/test_other_framework.py tests/bootstrap/test_bundled_guards.py && uv run ruff check`
Expected: PASS, and `All checks passed!`. `test_table_forms.py` still finds no `"decorator"`, `"call"` or `"loop"` literal in `scenarios.py`. `test_language_seam.py` finds no keyword quoted in backticks in its docstrings.

- [ ] **Step 7: Add the CHANGELOG bullet**

In `CHANGELOG.md`, directly after the 6.4 bullet (whose last line, after Task 1, is `` `call`. A language data file that writes `function.tables` under `supplies` is refused as an unknown fact.``), insert:

```markdown
- Python's reader reads a table from the first `for` of a test's own body over a list literal of the file (`for
  given, when, then in CASES:`), its columns the names the loop binds. Its rows are calls of the form's `row` with a
  keyword id, or tuple or list literals with an id at a position. That `for` is not reported as a branch by
  scenario-coverage or `plain_tables`.
```

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/rules/application/logic/scenarios.py tests/modules/rules/application/logic/test_scenarios.py tests/bootstrap/test_loop_tables.py CHANGELOG.md
git commit -m "scenario-coverage and plain_tables take the loop that runs a table's rows for the table, not a branch of its test, and a loop table is checked end to end under a framework written inline

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Golden docs, corpora and every gate

No code changes. This task proves spec 3.7: nothing moves for the bundled profiles.

**Files:**
- None modified. If any step below changes a file, stop: that is a defect of the branch, to diagnose and not to commit.

- [ ] **Step 1: Regenerate and read the golden docs**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_needs_agree.py tests/architecture`
Expected: PASS. The golden docs generate byte for byte, so nothing needs regenerating.

Run: `git status --short docs/cli docs/web docs/xarch tests/bootstrap/corpora`
Expected: no output.

- [ ] **Step 2: Run the full suite in the background**

Run, in the background: `timeout 900 uv run pytest -q > /tmp/pytest-6-5.log 2>&1; echo EXIT $? >> /tmp/pytest-6-5.log`
Read `/tmp/pytest-6-5.log` when it ends.
Expected: every test passes (about 6100), `EXIT 0`.

- [ ] **Step 3: Run the other gates**

Run: `uv run ruff check`
Expected: `All checks passed!`

Run: `timeout 300 uv run xarch check; echo $?`
Expected: exit 0.

Run: `timeout 300 uv run xarch check --strict; echo $?`
Expected: exit 0.

Run: `timeout 120 uv run xarch profile check architecture.yaml`
Expected: ends with `OK: the profile is valid`.

- [ ] **Step 4: Confirm the branch is clean**

Run: `git status --short`
Expected: no output. The spec and plan under `docs/superpowers/` are committed by the workflow's docs step, not by this task. If they show as untracked, leave them. Nothing to commit here.
<!-- task-pipeline: validated -->
