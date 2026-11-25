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
