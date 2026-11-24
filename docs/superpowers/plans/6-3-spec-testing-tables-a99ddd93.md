# 6.3 `testing.tables`: table forms in the framework file — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A framework writes `testing.tables`, a list of neutral table forms; the reader tags each table with the index
of its form; the guard keeps no copy of the table; a row is worded from the language's new `writing` templates; and
`testing.table` is refused through the retired-keys table, with every finding, golden doc and corpus byte for byte.

**Architecture:** `TableForm`, `Place` and `RowId` (in `xarch/profile_values/testing.py`) replace `CaseTable`;
`Framework.tables` holds them and `ScenarioCoverage` loses its table. The spec module parses `testing.tables` in
`profile_checks.table_forms`; the language file gains `writing` (`Writing` on `CheckedLanguage`); the reader adapter
reads only decorator forms and tags `Table.form`; `scenarios._rows` and `docs_template._guard_line` read the form at
`Table.form` and fill the language's templates, never branching on a form's kind. The work is additive first
(tasks 1-3 add the new shape beside the old), then task 4 switches the checks and docs over and retires the old key in
one commit, so every commit is green.

**Tech Stack:** Python 3, pytest, PyYAML, `ast` (reader only), ruff, xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/6-3-spec-testing-tables-a99ddd93.md` (reproduced in full below, under "The spec").

## Global Constraints

- Python is allowed only in the reader adapter (`xarch/modules/rules/adapters/fs_source_tree.py`) and in the data files
  under `xarch/architectures/presets/`. No docstring or literal elsewhere in `xarch/` says `pytest`, `param`,
  `parametrize`, `.py`, `Python` or writes Python syntax (`tests/architecture/test_language_seam.py` enforces it).
- An old shape is refused with a hint; there is no compatibility window. `testing.table` is refused, after task 4,
  with exactly: `testing: unknown key 'table': moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables); use files, functions, mocks, skips, tables`.
- No hidden pytest default: `tables` left out means the framework writes no form (`Framework.tables == ()`).
- `scenarios.py` keeps no Python call syntax in `_rows` and holds no string literal `"decorator"`, `"call"` or
  `"loop"`.
- A problem addresses an entry by its index from 0 (`testing.tables.0.call`); `profile explain` names the key with no
  index (`testing.tables.call`).
- Today's pytest behaviour stays byte for byte: the recorded corpora (`tests/bootstrap/corpora/`) and the golden docs
  (`docs/{cli,web,xarch}/`) do not change. Any change there is a defect, never something to re-record.
- No comments in xarch's code (docstrings only); a docstring on every public name; no dead code (`xarch check
  --strict`).
- Tests are written first. Tables use `pytest.param(..., id="<a sentence>")`. The `unit` and `integration` tiers set
  `plain_tables: true`: a table test's body holds no `if`, `for`, `while`, `try`, `match` statement and no `if`
  expression.
- `xarch/profile_values/` imports from neither module.
- Never `ruff --fix`; never edit `tests/bootstrap/corpora/`; `.claude/` stays out of commits; nothing is pushed.
- README and CHANGELOG lines go under `## [Unreleased]`.
- Gates, all green on this branch: `uv run pytest -q` (run in the background with `timeout`, record its PID, read the
  result at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
  `uv run xarch profile check architecture.yaml`.

## Review Focus

1. **One form written as a map instead of a list** (`tables: {decorator: ..., ...}`, the habit of the old
   `table:`) must give the one `must be a list of table forms` line, not a crash. Pinned in Task 2's refusal table
   (row "one form written as a map").
2. **A position that is `true`, negative or `null`** in a place or an id must be refused, never read as 1 or as
   absent. Pinned in Task 2 (rows "a position that is true is no number", "a negative position", "a place with
   neither").
3. **An id written the old way, `id: id`,** must get the id-shape refusal, not pass. Pinned in Task 2 (row "an id
   written as a bare keyword").
4. **A form the reader cannot read listed ahead of one it can, for the same decorator,** must read no table itself
   and leave the later form's index on the table. Pinned in Task 3
   (`test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does`).
5. **A `writing` template holding literal braces** (`'{..., {field}: "{text}"}'`) must be filled by plain
   replacement, not `str.format`, which would raise. Pinned in Task 4's wording table (row "a literal row whose id is
   a field").

---

## The spec (verbatim, `docs/superpowers/specs/6-3-spec-testing-tables-a99ddd93.md`)

<details open><summary>Spec</summary>

# 6.3 `testing.tables` describes table forms in the framework file: design spec

Card: a99ddd93 (subtask of 15e55316). Release step 19 of the merged order
(`~/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, section 3, line 282), split with 6.4 along
the note's steps 3 and 4. Blocked by 6.2 (e1ca2d5d), which is done on this branch (dd6090c, 705c3c9, cc8523c). 6.1
is in too (`Row.written`, `Table.form`, `Table.runs`, `xarch/modules/rules/domain/parsed.py:144-170`; the reader sets
`form=0, runs=0` at `xarch/modules/rules/adapters/fs_source_tree.py:626`).

Parent design: `~/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below, "the note"). This card
implements its sections 2.1 to 2.3 (lines 131-211), 2.5 (lines 231-249), 6 (lines 329-366, the rows that belong to
this step), 7 (the `testing.table` refusal, lines 365-378) and item 3 of section 8 (lines 399-403).

## 1. Goal

Today a framework says how a table of cases is written with one map, `testing.table: {decorator, row, id,
keywords}`, that only fits pytest's decorator. The guard `scenario-coverage` keeps a second copy of it, and the
checking code types Python's call syntax into its messages (`scenarios.py:186-187`).

After this card:

- A framework writes `testing.tables`, a list of table forms. Each entry has one holder key (`decorator`, `call` or
  `loop`) and the slots `columns_from`, `rows`, `row` and `id` (note 2.3).
- `pytest.yaml` writes its one form in that shape. The reader takes the list and tags each table it reads with the
  index of the form that read it.
- The guard reads the framework's forms and keeps no copy of its own.
- The words that name a row in a finding come from new `writing` templates in the language data file.
- `testing.table` is refused through the retired-keys table.

For every profile that exists today the findings, the generated docs and the recorded corpora stay byte for byte. The
only texts that change are the refusals and the `keys.yaml` texts of the key itself.

## 2. Inherited constraints

Each line cites its source.

- Owner ruling: neutral table forms in the framework data file. The slot that says where the column names come from
  is `columns_from` (note, "Rulings", lines 14-15).
- Python is allowed only in the reader adapter and in the data files under `xarch/architectures/presets/` (note,
  "Rulings", line 13; card).
- An old shape is refused with a hint. There is no compatibility window (note, "Rulings", lines 11-12; note 7,
  lines 377-378).
- The shape: `testing.tables` is a list, and each entry has exactly one holder key. Its slots and what each accepts
  are listed in note 2.3, lines 160-179. `position` and `keyword` are each optional, but at least one is given. A
  holder with `keyword` alone reads only the keyword (lines 177-179).
- `pytest.yaml` after the change is exactly the yaml of note 2.3, lines 189-196.
- A table carries `form`, the index of its form in the framework's list. The checking code uses it only to find the
  wording of that form and never branches on the kind of form (note 1, lines 126-127; "Dodges", lines 440-442).
- Row wording: the language data file says how a row is written, as `importing` already says how an import is.
  Python's templates are `call: "{callee}(...)"` and `keyword: '{callee}(..., {keyword}="{text}")'`. A TypeScript
  file would write `field: '{..., {field}: "{text}"}'`. The checking code fills the template that the row's `id` slot
  names. The docs sentence needs no syntax (note 2.5, lines 237-249).
- A problem addresses an entry by its index from 0 (`testing.tables.0.call`), and `profile explain` names the key
  with no index (`testing.tables.call`) (note, "Defaults", lines 31-32; review-2 Q14).
- The refusal, in the one wording of 0.3.0, through the retired-keys table, for a preset file and for an inline map.
  The "use ..." list is the list of its day (note 7, lines 370, 373-375).
- Named dodges this card must avoid (card; note, "Dodges", lines 445-446, 440-442):
  - a hidden pytest default, where `tables` left out means the decorator form (left out means no form);
  - keeping Python's call syntax in `_rows`;
  - a form kind name tested in the checking code.
- Today's pytest behaviour stays byte for byte. Any change in the recorded corpora or the golden docs is a defect
  (note 6, lines 361-366; "Dodges", line 451).
- Steps 3 and 4 are one release step. A main with step 3 and not step 4 never exists (note 8, lines 413-414).
  Section 3.9 relies on this.
- Gates on this branch alone, with the full suite green:
  - `uv run pytest -q` (over two minutes: run it in the background and read it at the end)
  - `uv run xarch check`
  - `uv run xarch check --strict`
  - `uv run ruff check` (never `--fix`)
  - `uv run xarch profile check architecture.yaml`

  (card; note 8, lines 390-392)
- Project rules (card):
  - no comments in xarch's code (docstrings only);
  - tests written first;
  - examples simple, with absolute `app.` imports;
  - the recorded corpora (`tests/bootstrap/corpora/`) are edited by hand only, and only as the note says (this card
    edits none);
  - `.claude/` stays out of commits;
  - nothing is pushed.
- README and CHANGELOG lines go under `[Unreleased]` (review 3, O4 and O5, `0.3.0-cohesion-review-3.md:228-229`).
  The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by hand
  (review 3, O8, line 232). For this card the diff must be empty.

## 3. Observable behaviour

### 3.1 The value: `TableForm` and `Framework.tables`

In `xarch/profile_values/testing.py`:

- `CaseTable` is removed and replaced by `TableForm`. No name `CaseTable` is left under `xarch/`.
- `TableForm` is a frozen dataclass. It holds exactly what note 2.3 lets an entry say, with no field that names a
  language:
  - The holder. One of three is set:
    - a decorator, as a dotted name;
    - a call, as one or more dotted names;
    - a loop, as a flag.
  - `columns_from`. One of:
    - a place in the holder's arguments: a position from 0 or None, and a keyword or "", with at least one of the two
      set;
    - the test's own parameters;
    - the names the loop binds;
    - the fields of each row.
  - `rows`: a place in the holder's arguments as above, or None for a loop.
  - `row`: a dotted name, meaning a row is a call of it, or none, meaning a row is a literal.
  - `id`. One of:
    - a keyword name;
    - a field name;
    - a position from 0.

  The plan picks the field names. A suggestion: `decorator: tuple[str, ...] = ()`,
  `call: tuple[tuple[str, ...], ...] = ()`, `loop: bool = False`, `columns_from: Place | str`, `rows: Place | None`,
  `row: tuple[str, ...] = ()`, and `id: Place`. Here `Place(position: int | None, keyword: str)` is shared by
  `columns_from` and `rows`, and `id` uses a small `RowId(keyword: str = "", field: str = "", position: int | None =
  None)`. The test that matters is that the checking code (3.6) reaches the wording without any `if` on which holder
  is set.
- `Framework.table` becomes `Framework.tables: tuple[TableForm, ...] = ()`. An empty tuple means the framework writes
  no form. Nothing anywhere stands in for a missing `tables`.
- `ScenarioCoverage.table` is removed. The guard is
  `ScenarioCoverage(results, tier, suffix, columns, file)`. Its docstring stops saying "how the table is written".
  Its `columns` stays required (making it optional is 6.6).
- The module docstring and `Framework`'s docstring say "the table forms it writes" in place of "how a test function
  holds a table of cases".

### 3.2 The key `testing.tables` and its parser

`testing` accepts `tables` in place of `table`. For each problem below, the message is given in full; `<i>` is the
entry's index from 0. The parser records every problem it finds in an entry (the style `case_table` follows today), and
an entry with any problem produces no `TableForm`.

- **Not a list.** `testing.tables: must be a list of table forms, each {decorator | call | loop, columns_from, rows,
  row, id}`.
- **An empty list** `[]` is accepted and gives `Framework.tables == ()`.
- **An entry that is not a mapping.** `testing.tables.<i>: must be a mapping with one of decorator, call or loop`.
- **Unknown key.** Through the existing `unknown_keys` with the new scope (3.3), so its "use ..." list is
  `call, columns_from, decorator, id, loop, row, rows`: `testing.tables.<i>: unknown key 'x': use call, columns_from,
  decorator, id, loop, row, rows`. The helper (`unknown_of`) says a key that is not retired with a colon before
  `use`, and several unknown keys as `unknown keys 'x', 'y': use ...`; only a retired key has the `; use` form. The
  test pins the exact line.
- **Holder.**
  - None, or more than one: `testing.tables.<i>: must have exactly one of decorator, call or loop`.
  - `decorator` must be an outside name, read by the existing `_outside_name_at`, with its existing message under
    `testing.tables.<i>.decorator`.
  - `call` must be a non-empty list of outside names (the existing `outside_names` and its message under
    `testing.tables.<i>.call`).
  - `loop` must be `true`: `testing.tables.<i>.loop: must be true: the rows are a list a loop of the test's body
    runs`.
- **Missing slot.** `testing.tables.<i>: missing `<slot>``, for each of `columns_from`, `row` and `id` that is
  missing, and for `rows` when the holder is `decorator` or `call`. These are the existing `required_of` messages for
  the three that are always required, plus one more line for `rows`.
- **`rows` given with `loop`.** `testing.tables.<i>.rows: a loop runs the rows it iterates: drop rows`.
- **A place** (`columns_from` as a map, and `rows`). It must be a mapping with only `position` (an int, 0 or more)
  and `keyword` (a keyword name, by `names.is_name` under the language), with at least one of them:
  `testing.tables.<i>.<slot>: must be {position: <n>, keyword: <name>}, at least one of them, of the holder's
  arguments`.
- **`columns_from`.** It is a place, or one of the words `parameters`, `bound` and `fields`. Any other value gives
  `testing.tables.<i>.columns_from: must be {position, keyword}, parameters, bound or fields`. A word that does not
  fit its entry is refused, with one message each:
  - a place with `loop`: `testing.tables.<i>.columns_from: a loop has no arguments: write bound or fields`;
  - `bound` without `loop`: `testing.tables.<i>.columns_from: bound is the names a loop binds: write it with loop`;
  - `parameters` with `loop`: `testing.tables.<i>.columns_from: a loop's columns are bound or fields`;
  - `fields` with a dotted `row`: `testing.tables.<i>.columns_from: fields needs row: literal`.
- **`row`.** It is an outside name (`_outside_name_at`, its message under `testing.tables.<i>.row`), or the word
  `literal`.
- **`id`.** It is a mapping with exactly one of `keyword` (a keyword name), `field` (a name) and `position` (an int,
  0 or more): `testing.tables.<i>.id: must be one of {keyword: <name>}, {field: <name>} or {position: <n>}`. A kind
  that does not fit the row is refused:
  - `keyword` with `row: literal`: `testing.tables.<i>.id: {keyword} names a keyword of a row call: write a dotted
    row`;
  - `field` with a dotted `row`: `testing.tables.<i>.id: {field} names a field of a literal row: write row:
    literal`.
- **The language must be able to say the row.** This uses the `writing` templates of 3.5. `<title>` is the
  language's `title` (Python). The check runs only on an entry with no other problem.
  - A dotted `row` needs `writing.call`: `testing.tables.<i>.row: the language <title> does not write
    `writing.call`, how a row call is named`.
  - An `id` by `keyword` needs `writing.keyword`: `testing.tables.<i>.id: the language <title> does not write
    `writing.keyword`, how a row's id is given by a keyword`.
  - An `id` by `field` needs `writing.field`: `testing.tables.<i>.id: the language <title> does not write
    `writing.field`, how a row's id is given by a field`.
  - An `id` by `position` needs no template (3.6).

`profile_checks.case_table` becomes `table_forms(value, where, problems, language) -> tuple[TableForm, ...] | None`
(note 6, "profile_checks.py" row, line 338). `profile_parsing._testing` reads `value["tables"]` and builds
`replace(framework, tables=forms)`. `_Testing` loses its `table` field. Code that used `testing.table` now reads
`testing.framework.tables`.

### 3.3 The key table, scopes and needs

In `xarch/modules/spec/domain/profile_keys.py`:

- `TABLE = "testing.table"` becomes `TABLES = "testing.tables"`, with the address `"testing.tables[]"` in `SCOPES`.
  This follows the precedent of `NAMING` / `"docs.naming[]"` (lines 42, 78).
- `RETIRED` gains
  `Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)")`.

In `xarch/modules/spec/domain/key_table.py`:

- `Key(TESTING, "table", ..., opens=TABLE)` becomes `Key(TESTING, "tables", rules=("scenario-coverage",),
  opens=TABLES)`.
- The four `TABLE` keys are replaced by seven `TABLES` keys, each with `rules=("scenario-coverage",)`:
  - `decorator`, `call` and `loop`, not required;
  - `columns_from`, `row` and `id`, required;
  - `rows`, not required, since it is required only for two holders and the parser says so.
- `NEEDS`:
  - `"testing.table": ("function.tables",)` becomes `"testing.tables": ("function.tables",)`;
  - `plain_tables` and the guard keep `function.tables`. Facts per form (`function.tables.decorator|call|loop`) are
    6.4.

The needs walker already walks the entries of a list scope (`profile_needs.py:51-56`), so it needs no change.

### 3.4 The refusals that named `testing.table`

- **The retired key.** A `testing` map that writes `table` is refused with exactly one problem:
  `testing: unknown key 'table': moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables); use files, functions, mocks, skips, tables`.
  - It reads the same for an inline map and for a preset that writes `table:`.
  - Under `profile check p.yaml` the line has the usual `p.yaml: ` prefix.
  - `xarch profile explain testing.table` answers from the retired entry, as step 1's mechanism does for every
    retired key.
- **`plain_tables` without forms.** The refusal at `profile_parsing.py:204-205` applies when `testing` is absent or
  `testing.framework.tables` is empty, and reads:
  `tiers.<tier>.plain_tables: needs `testing.tables`, the forms a table of cases is written in, to know a table test`.
  (Note 3.2's "needs a table form: the framework `<name>` writes none" is step 6, card 6.6.)
- **The guard without forms.** The refusal at `profile_parsing.py:784-786` applies under the same condition, and
  reads:
  `guards.scenario-coverage: needs `testing.tables`: the forms a table of cases is written in, such as [{decorator, columns_from, rows, row, id}]`.
  (The guard's no-form path is 6.6.)
- **No copy in the guard.** `_scenario_coverage` builds the guard without the table
  (`ScenarioCoverage(results, tier, suffix, columns, file)`).

### 3.5 The language's `writing` templates

The language data file gains an optional key `writing`. It is documented in `language_file.py`'s module docstring
next to `importing`, added to `KEYS`, parsed, and stored on `CheckedLanguage` (`xarch/profile_values/language.py`,
beside `importing`, line 91). It lives on `CheckedLanguage` because the checks read the language through
`profile.language`, which is the `CheckedLanguage`.

- **Shape.** A mapping with the keys `call`, `keyword` and `field`, each optional. Each is a one-line string that
  holds its placeholders:
  - `call` holds `{callee}`;
  - `keyword` holds `{callee}`, `{keyword}` and `{text}`;
  - `field` holds `{field}` and `{text}`.
- **Errors** (each is one problem, raised with the file's other problems as `InvalidArchitecture`, the way
  `importing` is refused):
  - not a mapping: `writing: must be a mapping {call, keyword, field}: how a row of a table of cases is written`;
  - an unknown key: `writing: unknown key 'x': use call, keyword, field` (a colon, as the file's own unknown-key
    problem at `language_file.py:123-126` says it; several are `unknown keys 'x', 'y': use ...`);
  - `writing.call: must be a line holding {callee}`;
  - `writing.keyword: must be a line holding {callee}, {keyword} and {text}`;
  - `writing.field: must be a line holding {field} and {text}`.
- **Left out:** the language writes no template. It still loads. Only a profile whose table forms need a template is
  refused (3.2).
- `xarch/architectures/presets/language/python.yaml` writes exactly:

  ```yaml
  writing:
    call: "{callee}(...)"
    keyword: '{callee}(..., {keyword}="{text}")'
  ```

  The comment block at the top of the file (lines 18-31) says what `writing` is, next to its sentence on
  `importing`. Python writes no `field`.
- The test fakes `tests/fakes/languages/{percent,brace}.yaml` gain a `writing` only where a test needs one (3.10).

### 3.6 The checks word a row from its form and the language

`xarch/modules/rules/application/logic/scenarios.py`, `_rows`:

- It reads `form = profile.framework.tables[table.form]` and `writing = profile.language.writing`. It no longer reads
  `guard.table`, so it takes the profile, or the form and the writing, in place of the guard's table.
- **The fix of a row** ("case") is `write ` followed by the filled template that the form's `id` kind names. Write `R`
  for `form.row` joined with the language's member separator (`.` for Python):
  - `keyword`: `writing.keyword` with `{callee}`=R, `{keyword}`=the id keyword, and `{text}`=`<a sentence stating
    the outcome>`;
  - `field`: `writing.field` with `{field}`=the id field and `{text}` as above;
  - `position n`: `write the row's id, a sentence stating the outcome, as its value at position <n>`. This needs no
    syntax, so no template.
- **The problem of a row** that is not written as the form writes one (`row.written` false):
  - dotted row: `row is not a ` followed by `writing.call` with `{callee}`=R;
  - literal row: `row is not a literal`.
- **Byte for byte.** For pytest these give exactly today's texts:
  - `write pytest.param(..., id="<a sentence stating the outcome>")`;
  - `row is not a pytest.param(...)`.

  The other messages of `_rows` and `_covered` do not change.
- **No form kind name in the checks.** `scenarios.py` holds no string literal `"decorator"`, `"call"` or `"loop"`.
  It picks the wording from the slots' values, not from a kind name compared in code. Telling a keyword id from a
  field id from a position id is the id slot's own data: a plan may give `RowId` a method that returns the template
  key, or store the kind, as long as the decision lives with the value and not as a kind name tested in
  `scenarios.py`.
- **The docstring.** The module docstring (`scenarios.py:6-15`) stops naming `CaseTable` and the decorator syntax. It
  says the table is read in one of the framework's forms (`testing.tables`), and that a row is written as its form
  writes one, with a literal text as its id. The decorator-specific lines move to, or are already said in, the
  reader's docstring.

`docs_template._guard_line` (`docs_template.py:478-484`):

- The pattern loses `table`: `case ScenarioCoverage(results, tier, suffix, columns, file)`.
- The row clause is built from `architecture.framework.tables`. It is one phrase per form, and the phrases are joined
  with ` or `:
  - dotted row, id by keyword or field `k`: `` a `R` with an `k` ``;
  - dotted row, id by position n: `` a `R` with its id at position n ``;
  - literal row, id by field `k`: `` a literal with an `k` ``;
  - literal row, id by position n: `` a literal with its id at position n ``.

  The clause is `every row is <phrases>`. For pytest this gives exactly today's
  ``every row is a `pytest.param` with an `id` ``, so the golden docs do not move.
- The function asserts `architecture.framework is not None`. The guard cannot parse without a framework.

### 3.7 The port, the service and the reader

- **The port.** `SourceTree.read` (`xarch/modules/rules/application/ports/source_tree.py:23`) takes
  `tables: tuple[TableForm, ...] = ()` in place of `table: CaseTable | None = None`. Its docstring says: "A function
  holds the tables written in one of the forms `tables` holds, each tagged with the index of its form; with none, no
  table is recognised."
- **The service.** `source_check.py:79-80` passes `rules.framework.tables if rules.framework is not None else ()`.
  There is no guard copy to prefer.
- **The reader** (`fs_source_tree.py`):
  - For each decorator of a function, it tries the forms in order and takes the first whose holder is a `decorator`
    matching that decorator. The table it reads is tagged `form=<that form's index>` (today `form=0` always).
  - Columns come from `columns_from`: the positional argument at `position` when there is one, else the keyword
    argument `keyword` when given. Rows come from `rows` in the same way.
  - A row is written when it is a call of `form.row`. Its id is the keyword `form.id.keyword`.

  This is exactly today's logic under the pytest form. `{position: 0, keyword: argnames}` reproduces "args[0] if any
  positional, else the `argnames` keyword". A place with no `keyword` reads only positions, and one with no `position`
  reads only the keyword. That keeps `test_without_keywords_only_positional_arguments_are_read`.
- **What the reader skips.** In this card the Python reader reads only `decorator` entries whose `columns_from` and
  `rows` are places, whose `row` is dotted and whose id is a keyword. Any other entry reads no table. 6.4 makes a form
  the language's reader cannot read a refused profile, through facts per form. 6.5 reads `loop`. See 3.9.
- `runs` stays 0.

### 3.8 The texts xarch says of the keys (`keys.yaml`)

In `xarch/architectures/presets/format/keys.yaml`, edited together with the key table (agreement is enforced by
`tests/modules/spec/domain/test_profile_keys.py` and `tests/bootstrap/test_needs_agree.py`):

- **The fragment `table`** (lines 33-36) becomes:

  ```yaml
    table: |2
        tables:
          - decorator: checks.cases
            columns_from: {position: 0, keyword: names}
            rows: {position: 1, keyword: cases}
            row: checks.case
            id: {keyword: id}
  ```

  Every example that uses `<<table>>` must still parse under the language the examples are checked with. Python
  writes `call` and `keyword`, so it does.
- **`testing.table`** and its four sub-keys (lines 796-832) are replaced by entries for `testing.tables` and
  `testing.tables[].<key>`, one for each of the seven keys of 3.3:
  - `testing.tables`: meaning "the forms a table of cases is written in"; accepts "a list of forms, each one of
    decorator, call or loop, with columns_from, rows, row and id; left out or empty: the framework writes no table".
  - Each slot's `accepts` says what note 2.3 says of it, in its words.
  - Each example uses `<<table>>`, or a short inline entry for `call` and `loop`.
- **`plain_tables`** (lines 589-592) says "as `testing.tables` writes one" and "needs `testing.tables`".
- **The guard** (line 920): "every row is written as its form in `testing.tables` writes one, with a literal id", in
  place of "every row is a `testing.table.row` call with a `testing.table.id`".
- The `testing` line of the shape in the format doc (explore: line 143) says `tables` in place of `table`.

`profile explain testing.tables.decorator` (no index) answers with the `testing.tables[].decorator` text, as
`docs.naming.kind` answers today (`tests/modules/spec/application/logic/test_profile_keys.py:104`).

### 3.9 The interim state within release step 19

Between this card and 6.4 there are two gaps:

- Under Python a profile may write a `call` or `loop` entry, or a decorator entry with literal rows. It is accepted,
  and the reader reads no table from it.
- A use case whose only table is of such a form gets "no table test whose parameters are ...". That is today's
  message for a table the reader does not see.

This is allowed only because steps 3 and 4 are one release step and nothing merges before it is green (note 8,
lines 413-414). 6.4 closes the gap with facts per form, and its spec must name these inputs. This card does not
pretend otherwise. No bundled profile writes such an entry.

### 3.10 Profiles, tests and fakes

- **`pytest.yaml`** (`xarch/architectures/presets/testing/pytest.yaml:8`) writes the block of note 2.3, lines
  190-196. Its header comment (lines 1-3) says "the table forms it writes" in place of "how a table of cases is
  written".
- **No bundled profile** writes `table:`, so `architecture.yaml`, `cli.yaml`, `web.yaml`, `stress.yaml` and the
  archived yaml do not change.
- **Every test, builder and fake that writes `testing.table`, a `table:` map, `CaseTable(...)`, `Framework(...,
  table=...)` or `ScenarioCoverage(..., table, ...)`** is rewritten to `tables:` / `TableForm` /
  `Framework(..., tables=(...))` / the five-field guard. The explore list covers the places to look:
  - `tests/modules/spec/application/logic/` `test_testing.py`, `test_profile_parsing_tests.py`,
    `test_profile_needs.py`, `test_profile_keys.py`, `test_libraries_and_guards.py`,
    `test_profile_parsing_substance.py`, `test_retired_keys.py`;
  - `tests/modules/spec/application/test_explain.py`;
  - `tests/modules/spec/profiles.py`;
  - `tests/modules/rules/builders.py`;
  - `tests/modules/rules/` `test_expansion.py`, `test_filters.py`, `test_vocabulary.py`, `test_spec_profile.py`;
  - `tests/fakes/filesystem.py`;
  - `tests/architecture/test_agnostic.py`;
  - `tests/bootstrap/` `test_other_framework.py`, `test_bundled_guards.py`, `test_profile_file.py`,
    `test_review_placement.py`.

  Find the rest with `grep -rn "CaseTable\|testing\.table\b\|table=\|\btable:" tests`. Each rewritten test keeps its
  own expectation, except the reworded refusals of 3.4.
- **`tests/bootstrap/test_other_framework.py:13`** becomes:

  ```yaml
  tables: [{decorator: cases.table, columns_from: {position: 0}, rows: {position: 1}, row: cases.row,
            id: {keyword: name}}]
  ```

  Its two tests keep their expectations word for word, so a fix text such as
  `write cases.row(..., name="<a sentence stating the outcome>")`, if one is pinned, is the same as today.
- **`tests/architecture/test_language_seam.py`** must still pass. The texts added to `keys.yaml` and `scenarios.py`
  use format words (`decorator`, `literal`, `field`, `position`), not words of the Python data file. Any new
  allowance needs its own reason.

### 3.11 README and CHANGELOG

- **README line 116:** `testing:  <preset> | {files*, functions*, skips, tables, mocks}`. No other README line quotes
  `testing.table` or the row wording (line 324 names `guards.scenario-coverage` and `tiers.plain_tables` only, and
  stays).
- **CHANGELOG,** under `## [Unreleased]`, `### Changed`, with the breaking change first. One entry, in substance:
  - A framework writes `testing.tables`, a list of table forms, each with one of `decorator`, `call` or `loop`, and
    `columns_from`, `rows`, `row` and `id`.
  - `testing.table` is refused with "moved in 0.3.0: write tables, ...". The bundled `pytest` preset writes its form
    in the new shape.
  - The guard `scenario-coverage` keeps no copy of the table.
  - A language data file says how a row is written with `writing: {call, keyword, field}`. Python writes `call` and
    `keyword`.
  - Findings and docs read as before.

## 4. Tests that prove it

Tests are written first: the refusal (T1, T2) and the pytest-table-read-the-same tests (T5, T6) before any production
change. Tables use `pytest.param(..., id="<a sentence>")`. Both `unit` and `integration` set `plain_tables: true`
(`architecture.yaml:267, 279`), so a table test's body must not branch.

| # | Test | Where | Tier, and why |
|---|---|---|---|
| T1 | `testing.table` refused: a table of two rows, an inline `testing: {files, functions, table: {...}}` and a preset dict holding `table:` passed as `presets`. Each gives exactly the one line of 3.4 and no other problem. The existing row `pytest.param(TABLE, writing(covered(), "testing", "table"), ...)` (line 420) is removed, and the `TESTING` row (line 396) expects `use files, functions, mocks, skips, tables` | `tests/modules/spec/application/logic/test_retired_keys.py` | unit: a pure check of the spec module |
| T2 | `profile check` on a file writing `testing: {..., table: {...}}` prints `p.yaml: testing: unknown key 'table': moved in 0.3.0: ...` in full, and `profile explain testing.table` prints the retired text | `tests/bootstrap/test_profile_file.py` and the explain test of retired keys (wherever step 1 pins `profile explain <old key>`) | wired: what the commands print, through bootstrap |
| T3 | `table_forms` accepts the pytest entry and returns the one `TableForm` of 3.1, and accepts `[]` as `()`. One row per refusal of 3.2 gives its exact message under `testing.tables.<i>...` (not a list, entry not a mapping, no holder, two holders, `loop: 1`, missing `row`/`id`/`columns_from`, `rows` missing with `call`, `rows` with `loop`, a bad place, `columns_from: bound` with a decorator, a place with `loop`, `fields` with a dotted row, `id` with two kinds, `{keyword}` with `literal`, `{field}` with a dotted row, an unknown key). An entry at index 1 is addressed `testing.tables.1` | `tests/modules/spec/application/logic/test_testing.py` | unit |
| T4 | The language check of 3.2: under a fake language with no `writing`, a dotted row is refused at `.row` and a keyword id at `.id`, with the full messages naming the language's title. A `{position}` id with `row: literal` is accepted with no template | same | unit |
| T5 | A pytest table is read the same as before: the existing reader tests (`test_fs_source_tree.py`, around line 390 and `test_without_keywords_only_positional_arguments_are_read` at 471) pass `tables=(<pytest form>,)` and expect the same `Table`/`Row` values, `form=0`. A new row: under two decorator forms (`a.cases`, then `pytest.mark.parametrize`) a pytest-decorated test's table has `form=1` | `tests/modules/rules/adapters/test_fs_source_tree.py` | adapter: the real reader on real source in `tmp_path` |
| T6 | Under a form with `columns_from: {keyword: argnames}` alone, a positional names argument is not read (no table), and a keyword one is | same | adapter |
| T7 | The wording comes from the form at `Table.form` and the language. Facts built by hand: a framework with two forms (form 0 `x.case`/`name`, form 1 `pytest.param`/`id`) and a table with `form=1`. The fix and problem texts are the pytest ones, byte for byte. A language whose `writing.keyword` is `'{callee}[{keyword}: {text}]'` yields `write pytest.param[id: <a sentence stating the outcome>]`. A literal-row form with a `{field: name}` id under a test language with `writing.field` gives `row is not a literal` and the filled field fix. A `{position: 0}` id gives the fixed position fix | `tests/modules/rules/application/logic/test_scenarios.py` | unit: the guard's logic over facts built by hand |
| T8 | `scenarios.py` holds no string literal `"decorator"`, `"call"` or `"loop"` (read its AST, list the `Constant` strings) | `tests/architecture/` beside `test_language_seam.py` | guard on xarch's own source: holds the dodge |
| T9 | `writing` in the language file: Python's two templates load onto `CheckedLanguage`. A file without `writing` loads with empty templates. One row per error of 3.5 gives its exact message | `tests/modules/spec/application/logic/test_language_file.py` | unit: the loader of the data file |
| T10 | Refusals reworded: `plain_tables` with `testing` writing no `tables`, and with `tables: []`. The guard with no forms. Each gives the exact line of 3.4 | `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (today's pins at lines 573, 640 move) | unit |
| T11 | `ScenarioCoverage` has no `table`: the parsed guard of a pytest profile equals `ScenarioCoverage(results, tier, suffix, columns, "test_{name:snake}.py")` | `test_profile_parsing_tests.py` or `test_libraries_and_guards.py` | unit |
| T12 | Needs: `testing.tables` under a language that does not supply `function.tables` is refused with the existing message, now naming `testing.tables` | `tests/modules/spec/application/logic/test_profile_needs.py` (line 136) and `tests/bootstrap/test_needs_agree.py` | unit, and wired agreement of the table with `keys.yaml` |
| T13 | `profile explain testing.tables` and `profile explain testing.tables.id` print the new texts. Every `<<table>>` example parses. The key-table and `keys.yaml` agreement tests pass with the seven new keys and no `testing.table*` entry | `tests/modules/spec/application/test_explain.py`, `test_profile_keys.py`, the keys.yaml example test | wired: what the command prints |
| T14 | `test_other_framework.py`, rewritten to `tables:`, keeps both expectations word for word | `tests/bootstrap/test_other_framework.py` | wired: another framework of the same form, end to end |
| T15 | The golden docs regenerate unchanged (existing `tests/bootstrap/test_docs_templates.py:30, 62`). A unit row in `test_docs_template.py` for the clause of a literal/position form | existing, plus `tests/modules/spec/application/logic/test_docs_template.py` | wired: byte-for-byte proof of 3.6; unit for the new phrase |
| T16 | The recorded corpora replay unchanged (existing `tests/bootstrap/test_recorded_corpora.py`) | existing | wired: byte-for-byte proof of the findings |

The existing tests of the bundled profiles (`test_bundled_guards.py`, `test_bundled_architectures.py`) keep passing.
They prove that `pytest.yaml` in its new shape parses and the shipped profiles still check.

## 5. Out of scope

- Facts per form: `function.tables.decorator|call|loop` in `supplies`, `capabilities.py` and `NEEDS`; refusing
  under Python a framework that writes `call` (6.4, note 2.4 and 8 item 4). Here `NEEDS` keeps the one fact
  `function.tables`.
- The `loop` form in the Python reader, and `runs` honoured by `_branches` (6.5, note 8 item 5). It is parsed here
  and read by nothing.
- The no-form path: the standalone rule alone, the guard's `columns` refused with no form, and `plain_tables` refused
  with note 3.2's wording (6.6, note 3 and 8 item 6). Here both keys are still refused without forms, with the
  re-pointed wording of 3.4.
- The test-only frameworks with a `call` and a `loop` form, the one-method-per-case framework, and the explain texts
  of note 8 item 7 (later card). T7 proves only that the checking code reads the form by index and the words from the
  language.
- The re-grep of note 8 item 7. This card already removes `CaseTable` and `testing.table` from `xarch/`, except the
  retired entry.
- Unnamed tests, `testing.declared`, `beside` and the `call` cross-check (release step 21). Spec forms in `writing`
  (step 22).
- The bundled prose `xarch/architectures/testing.md` and `docs/templates/testing.md` (note 6, lines 357-359).
- The `[i]` form of `docs.naming[i]` in its own problems. That key keeps its own form. `testing.tables` follows the
  note's `.<i>` (section 2).
- Any change to the recorded corpora, the golden docs or the profiles.

## 6. Hand-off notes for the plan

- **File map.**
  - Modify:
    - `xarch/profile_values/testing.py` and `xarch/profile_values/language.py`;
    - `profile_checks.py`, `profile_parsing.py`, `language_file.py`, `docs_template.py` under
      `xarch/modules/spec/application/logic/`;
    - `profile_keys.py` and `key_table.py` under `xarch/modules/spec/domain/`;
    - `presets/format/keys.yaml`, `presets/testing/pytest.yaml` and `presets/language/python.yaml` under
      `xarch/architectures/`;
    - `scenarios.py`, `ports/source_tree.py`, `services/source_check.py` and `adapters/fs_source_tree.py` under
      `xarch/modules/rules/`;
    - README.md and CHANGELOG.md;
    - the tests and fakes of 3.10.
  - Create: the grep test of T8.
- **Order.**
  1. T1 and T5/T6 first: the refusal and the pytest table read the same.
  2. The value, the parser and the key table, `keys.yaml` and `pytest.yaml` together, with every fixture that writes
     `table:`. One task: the retired refusal breaks every fixture still writing it.
  3. `writing` in the language file and `python.yaml`, with the language check of 3.2.
  4. The port, the service and the reader.
  5. `_rows` and the docs line (T7, T8, T15).
  6. README and CHANGELOG.
  7. The full gates last.
- **Watch out for:**
  - `xarch check --strict` holds xarch to its own rules: a docstring on every public name, no dead code, no
    comments, and `plain_tables` on the test tiers (no branch in a table test's body);
  - `TableForm`'s helpers must be used outside tests or they are dead code;
  - `profile_values` is read by both modules, so it must not import from either.
- **Running the suite.** `uv run pytest -q` takes over two minutes. Run it in the background with `timeout`, record
  its PID, and read the result at the end. Never `ruff --fix`.

</details>

---

## File map

- Modify `xarch/profile_values/language.py`: `Writing` (with its filling methods), `CheckedLanguage.writing`.
- Modify `xarch/profile_values/testing.py`: `Place`, `RowId`, `TableForm`, `PARAMETERS`/`BOUND`/`FIELDS`,
  `Framework.tables`; later remove `CaseTable`, `Framework.table`, `ScenarioCoverage.table`.
- Modify `xarch/modules/spec/application/logic/language_file.py`: key `writing`.
- Modify `xarch/modules/spec/application/logic/profile_checks.py`: `table_forms` (and later remove `case_table`).
- Modify `xarch/modules/spec/application/logic/profile_parsing.py`: `_testing`, `_Testing`, the two refusals, the guard.
- Modify `xarch/modules/spec/application/logic/docs_template.py`: `_guard_line`, `_row_phrase`.
- Modify `xarch/modules/spec/domain/profile_keys.py` and `key_table.py`: `TABLES`, its keys, `NEEDS`, `RETIRED`.
- Modify `xarch/architectures/presets/format/keys.yaml`, `presets/testing/pytest.yaml`, `presets/language/python.yaml`.
- Modify `xarch/modules/rules/application/logic/scenarios.py`, `ports/source_tree.py`, `services/source_check.py`,
  `adapters/fs_source_tree.py`.
- Modify README.md, CHANGELOG.md.
- Create `tests/architecture/test_table_forms.py`.
- Modify the tests and fakes named in each task.

---

## Task 1: The language says how a row is written (`writing`)

**Files:**
- Modify: `xarch/profile_values/language.py` (add `Writing` above `CheckedLanguage`; field and docstring of
  `CheckedLanguage`)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (module docstring, `KEYS`, `language_of`, new
  `_writing`)
- Modify: `xarch/architectures/presets/language/python.yaml` (comment block, new key)
- Modify: `tests/modules/rules/builders.py` (`PYTHON` gains `writing`)
- Test: `tests/modules/spec/application/logic/test_language_file.py`

**Interfaces:**
- Produces: `xarch.profile_values.language.Writing(call: str = "", keyword: str = "", field: str = "")`, frozen;
  `CheckedLanguage.writing: Writing = Writing()` (the last field); the data-file key `writing`; `builders.PYTHON.writing
  == Writing(call="{callee}(...)", keyword='{callee}(..., {keyword}="{text}")')`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Change the import line
`from xarch.profile_values.language import BLOCK, LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark` to

```python
from xarch.profile_values.language import BLOCK, LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, Writing
```

Change `KEYS_USED` to end in `writing`:

```python
KEYS_USED = ("branching, branching_expressions, cache, call, comments, directives, dynamic, encoding, extensions, "
             "immutable, importing, interface, member, name, namespace, nothing, package, package_files, private, "
             "shebang, special, standard, supplies, title, unannotated, writing")
```

Append at the end of the file:

```python
MAPPING = "writing: must be a mapping {call, keyword, field}: how a row of a table of cases is written"
CALL = "writing.call: must be a line holding {callee}"
KEYWORD = "writing.keyword: must be a line holding {callee}, {keyword} and {text}"
FIELD = "writing.field: must be a line holding {field} and {text}"


def test_python_writes_how_a_row_call_and_a_row_id_given_by_a_keyword_are_written():
    assert PYTHON_LANGUAGE.checked.writing == Writing(call="{callee}(...)", keyword='{callee}(..., {keyword}="{text}")')


def test_a_language_whose_file_writes_no_templates_loads_with_empty_ones():
    assert language_of("pascal", DOCUMENT).checked.writing == Writing()


def test_the_templates_a_data_file_writes_are_read_braces_and_all():
    field = '{..., {field}: "{text}"}'
    assert language_of("pascal", DOCUMENT | {"writing": {"field": field}}).checked.writing == Writing(field=field)


@pytest.mark.parametrize("writing, expected", [
    pytest.param("{callee}(...)", [MAPPING], id="a text is no mapping"),
    pytest.param({"row": "x"}, ["writing: unknown key 'row': use call, keyword, field"], id="an unknown key"),
    pytest.param({"row": "x", "cell": "y"}, ["writing: unknown keys 'cell', 'row': use call, keyword, field"],
                 id="two unknown keys are said together"),
    pytest.param({"call": "call()"}, [CALL], id="a call template without its callee"),
    pytest.param({"call": "{callee}\n(...)"}, [CALL], id="a call template over two lines"),
    pytest.param({"call": 3}, [CALL], id="a call template that is no text"),
    pytest.param({"keyword": "{callee}(..., {keyword}=x)"}, [KEYWORD], id="a keyword template without its text"),
    pytest.param({"field": "{text}"}, [FIELD], id="a field template without its field"),
])
def test_a_bad_writing_is_refused(writing, expected):
    assert refused(DOCUMENT | {"writing": writing}) == expected
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_language_file.py -q`
Expected: FAIL — `ImportError: cannot import name 'Writing'`.

- [ ] **Step 3: Add `Writing` and the field**

In `xarch/profile_values/language.py`, insert above `@dataclass(frozen=True)\nclass CheckedLanguage:`:

```python
@dataclass(frozen=True)
class Writing:
    """How the language writes a row of a table of cases, as its data file's `writing` says it, each template one
    line (empty: the file does not write it): call, a row that is a call, {callee} standing for what it calls; keyword,
    a row call whose id a keyword gives, {callee}, {keyword} and {text} standing for what it calls, the keyword and
    the id's text; field, a literal row whose id a field gives, {field} and {text} standing for the field and the
    id's text. A template is filled by `row_call`, `keyword_id` and `field_id`: each placeholder replaced in one pass,
    any other text, braces included, kept as it is."""
    call: str = ""
    keyword: str = ""
    field: str = ""

    def row_call(self, callee: str) -> str:
        """The `call` template for a row that calls callee."""
        return self._fill(self.call, callee=callee)

    def keyword_id(self, callee: str, keyword: str, text: str) -> str:
        """The `keyword` template for a row that calls callee, its id given by keyword with the value text."""
        return self._fill(self.keyword, callee=callee, keyword=keyword, text=text)

    def field_id(self, field: str, text: str) -> str:
        """The `field` template for a literal row, its id given by field with the value text."""
        return self._fill(self.field, field=field, text=text)

    @staticmethod
    def _fill(template: str, **values: str) -> str:
        """The template with each `{<name>}` of the values replaced in one pass, so that a value holding a
        placeholder is not filled again."""
        return re.sub("{(" + "|".join(values) + ")}", lambda found: values[found.group(1)], template)
```

(`re` is already imported by `language.py`. A top-level function would be a `parts.profile-values.holds` finding
under `xarch check`: `profile-values/` holds classes, so every helper of a value is a method of its class.)

In `CheckedLanguage`'s docstring replace
`{name} for the name (empty: its data file does not say); names is the pattern` with
`{name} for the name (empty: its data file does not say); writing is how it writes a row of a table of cases (see
Writing); names is the pattern` (re-wrap the lines at 120 columns). Add the last field after `standard_modules`:

```python
    standard_modules: frozenset[str] = frozenset()
    writing: Writing = Writing()
```

- [ ] **Step 4: Parse `writing` in the data file**

In `xarch/modules/spec/application/logic/language_file.py`:

1. In the module docstring, after the `importing` entry (its two lines ending `{name} for the name`), add:

```
    writing        how a row of a table of cases is written, a map of one-line templates, each optional: call, a
                   row that is a call, {callee} standing for what it calls; keyword, a row call whose id a keyword
                   gives, {callee}, {keyword} and {text}; field, a literal row whose id a field gives, {field} and
                   {text}. Left out, the language writes no template, and a profile whose table forms need one is
                   refused
```

2. Change the import `from xarch.profile_values.language import BLOCK, LINE, NOTHING, CheckedLanguage, CommentForm,
   InterfaceMark, RecordMark` to add `Writing` at the end of the list.

3. `KEYS`: append `"writing"` after `"branching_expressions"`.

4. Below the `STANDARD = (...)` constant and its docstring, add:

```python
WRITING = "writing: must be a mapping {call, keyword, field}: how a row of a table of cases is written"
"""What the loader says of a value of `writing` that is not a mapping, once for the key."""
_TEMPLATES = {"call": ("{callee}",), "keyword": ("{callee}", "{keyword}", "{text}"), "field": ("{field}", "{text}")}
"""The templates of `writing`, in the order a problem lists them, each with the placeholders it must hold."""
_HOLDING = {"call": "{callee}", "keyword": "{callee}, {keyword} and {text}", "field": "{field} and {text}"}
"""What a problem says each template must hold."""
```

5. In `language_of`, after the line `immutable = _marks(document, problems, joins, namespace)`, add
   `writing = _writing(document, problems)`, and add `writing=writing` to the `CheckedLanguage(...)` call (after
   `unannotated=unannotated`).

6. Add the function after `_text`:

```python
def _writing(document: Mapping[Any, Any], problems: list[str]) -> Writing:
    """How a row of a table of cases is written; empty templates when the key is left out or refused. Each template
    is a one-line text holding every placeholder of its own."""
    if "writing" not in document:
        return Writing()
    value = document["writing"]
    if not isinstance(value, Mapping):
        problems.append(WRITING)
        return Writing()
    unknown = sorted(str(key) for key in value if key not in _TEMPLATES)
    if unknown:
        problems.append(f"writing: unknown key{'s' if len(unknown) > 1 else ''} "
                        f"{', '.join(f'{key!r}' for key in unknown)}: use {', '.join(_TEMPLATES)}")
    found: dict[str, str] = {}
    for key, held in _TEMPLATES.items():
        line = value.get(key)
        if key in value and isinstance(line, str) and line.strip() and "\n" not in line and all(h in line for h in held):
            found[key] = line
        elif key in value:
            problems.append(f"writing.{key}: must be a line holding {_HOLDING[key]}")
    return Writing(**found)
```

- [ ] **Step 5: Python writes its two templates**

In `xarch/architectures/presets/language/python.yaml`, replace the comment lines

```
# how a file imports a name from another file of the app, {dotted} standing for that file's dotted path and {name} for
# the name.
```

with

```
# how a file imports a name from another file of the app, {dotted} standing for that file's dotted path and {name} for
# the name. writing, how a row of a table of cases is written: call, a row that is a call, {callee} standing for what
# it calls; keyword, a row call whose id a keyword gives, {keyword} and {text} standing for the keyword and the id's
# text; field, a literal row whose id a field gives, Python does not write.
```

and after the line `importing: "from {dotted} import {name}"` add:

```yaml
writing:
  call: "{callee}(...)"
  keyword: '{callee}(..., {keyword}="{text}")'
```

- [ ] **Step 6: The rules builders' Python writes them too**

In `tests/modules/rules/builders.py`, change
`from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark` to
`from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, Writing`, and
add `writing=Writing(**PYTHON_FILE["writing"]),` to the `PYTHON = CheckedLanguage(...)` call (after
`member=PYTHON_FILE["member"],`). Extend its docstring: `..., read from it; its standard modules the interpreter's, as
spec hands them; how it writes a row of a table, read from it.`

- [ ] **Step 7: Run the tests**

Run: `uv run pytest tests/modules/spec/application/logic/test_language_file.py tests/modules/rules tests/architecture -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/modules/rules/builders.py \
  tests/modules/spec/application/logic/test_language_file.py
git commit -m "A language's data file says how a row of a table of cases is written, writing: {call, keyword, field}; Python writes call and keyword"
```

---

## Task 2: `testing.tables` is parsed into table forms (beside `testing.table`, for now)

**Files:**
- Modify: `xarch/profile_values/testing.py` (new values; `Framework.tables`)
- Modify: `xarch/modules/spec/domain/profile_keys.py` (`TABLES`, `SCOPES`)
- Modify: `xarch/modules/spec/domain/key_table.py` (keys, `NEEDS`)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (`table_forms`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (`_testing`)
- Modify: `xarch/architectures/presets/format/keys.yaml` (fragment `tables`, eight entries)
- Modify: `tests/modules/spec/profiles.py` (`PYTEST_TABLE`, `PYTEST_FORM`)
- Test: `tests/modules/spec/application/logic/test_testing.py`, `tests/modules/spec/application/logic/test_profile_needs.py`,
  `tests/modules/spec/application/test_explain.py`, `tests/modules/spec/application/logic/test_retired_keys.py`

**Interfaces:**
- Consumes: `Writing` and `CheckedLanguage.writing` (Task 1).
- Produces, in `xarch/profile_values/testing.py`:
  - `PARAMETERS = "parameters"`, `BOUND = "bound"`, `FIELDS = "fields"`;
  - `Place(position: int | None = None, keyword: str = "")`;
  - `RowId(keyword: str = "", field: str = "", position: int | None = None)`;
  - `TableForm(columns_from: Place | str, rows: Place | None, row: tuple[str, ...], id: RowId, decorator: tuple[str,
    ...] = (), call: tuple[tuple[str, ...], ...] = (), loop: bool = False)` (`row == ()` means a literal row);
  - `Framework.tables: tuple[TableForm, ...] = ()` (after `table`, which stays until Task 4).
- Produces `profile_checks.table_forms(value, where, problems, language) -> tuple[TableForm, ...] | None`;
  `profile_keys.TABLES = "testing.tables"`; `tests.modules.spec.profiles.PYTEST_TABLE` (the pytest entry as a dict) and
  `PYTEST_FORM` (its `TableForm`).

- [ ] **Step 1: Shared test values**

In `tests/modules/spec/profiles.py`, add `from xarch.profile_values.testing import Place, RowId, TableForm` to the
imports, and above `TESTING = {...}` add:

```python
PYTEST_TABLE = {"decorator": "pytest.mark.parametrize", "columns_from": {"position": 0, "keyword": "argnames"},
                "rows": {"position": 1, "keyword": "argvalues"}, "row": "pytest.param", "id": {"keyword": "id"}}
"""The one form pytest writes a table of cases in, as an entry of `testing.tables`."""
PYTEST_FORM = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                        decorator=("pytest", "mark", "parametrize"))
"""PYTEST_TABLE as the loader reads it."""
```

- [ ] **Step 2: Write the failing parser tests (T3, T4, Review Focus 1-3)**

In `tests/modules/spec/application/logic/test_testing.py`, change the imports to:

```python
from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import PYTEST_FORM, PYTEST_TABLE, TESTING, covered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.application.logic.profile_checks import use_case_file
from xarch.profile_values.language import Writing
from xarch.profile_values.testing import BOUND, Fixture, Place, RowId, ScenarioCoverage, TableForm
```

and append:

```python
CALL = {"call": ["checks.each"], "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "checks.case",
        "id": {"keyword": "id"}}
"""A form whose rows a call that makes the test holds."""
LOOP = {"loop": True, "columns_from": "bound", "row": "literal", "id": {"position": 0}}
"""A form whose rows a loop of the test's body runs, each a literal whose id is its first value."""
FIELD_ROW = {"decorator": "checks.cases", "columns_from": "fields", "rows": {"position": 0}, "row": "literal",
             "id": {"field": "name"}}
"""A form of literal rows whose id is a field."""
POSITIONED = {"decorator": "checks.cases", "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "literal",
              "id": {"position": 0}}
"""A form of literal rows whose id is their first value."""
AT = "layered.yaml: testing.tables.0"
FORMS = ("layered.yaml: testing.tables: must be a list of table forms, each {decorator | call | loop, columns_from, "
         "rows, row, id}")
ENTRY = f"{AT}: must be a mapping with one of decorator, call or loop"
HOLDER = f"{AT}: must have exactly one of decorator, call or loop"
PLACE = "must be {position: <n>, keyword: <name>}, at least one of them, of the holder's arguments"
ROW_ID = f"{AT}.id: must be one of {{keyword: <name>}}, {{field: <name>}} or {{position: <n>}}"
SLOTS = "use call, columns_from, decorator, id, loop, row, rows"
TOY = replace(PYTHON, checked=replace(PYTHON.checked, title="Toy", writing=Writing()))
"""Python as a language whose data file writes no template: it cannot say a row."""


def with_tables(tables) -> dict:
    return with_testing(tables=tables)


def without(entry: dict, key: str) -> dict:
    return {k: v for k, v in entry.items() if k != key}


def test_the_forms_of_a_table_are_read_each_in_its_slots():
    assert parsed(with_tables([PYTEST_TABLE])).framework.tables == (PYTEST_FORM,)
    assert parsed(with_tables([CALL, LOOP])).framework.tables == (
        TableForm(Place(0), Place(1), ("checks", "case"), RowId(keyword="id"), call=(("checks", "each"),)),
        TableForm(BOUND, None, (), RowId(position=0), loop=True))


def test_an_empty_list_of_forms_and_a_framework_that_writes_none_have_no_form():
    assert parsed(with_tables([])).framework.tables == ()
    assert parsed(covered(testing=FILES)).framework.tables == ()


@pytest.mark.parametrize("tables, expected", [
    pytest.param(PYTEST_TABLE, FORMS, id="one form written as a map, not a list, is refused"),
    pytest.param(["pytest.mark.parametrize"], ENTRY, id="an entry that is no mapping is refused"),
    pytest.param([None], ENTRY, id="an empty entry is refused"),
    pytest.param([without(PYTEST_TABLE, "decorator")], HOLDER, id="an entry with no holder is refused"),
    pytest.param([PYTEST_TABLE | {"call": ["checks.each"]}], HOLDER, id="an entry with two holders is refused"),
    pytest.param([LOOP | {"loop": 1}], f"{AT}.loop: must be true: the rows are a list a loop of the test's body runs",
                 id="a loop that is not true is refused"),
    pytest.param([without(PYTEST_TABLE, "row")], f"{AT}: missing `row`", id="an entry with no row is refused"),
    pytest.param([without(PYTEST_TABLE, "id")], f"{AT}: missing `id`", id="an entry with no id is refused"),
    pytest.param([without(PYTEST_TABLE, "columns_from")], f"{AT}: missing `columns_from`",
                 id="an entry with no columns_from is refused"),
    pytest.param([without(CALL, "rows")], f"{AT}: missing `rows`", id="a call with no rows is refused"),
    pytest.param([LOOP | {"rows": {"position": 0}}], f"{AT}.rows: a loop runs the rows it iterates: drop rows",
                 id="rows given with a loop are refused"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": -1}}], f"{AT}.rows: {PLACE}", id="a negative position"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": True}}], f"{AT}.rows: {PLACE}",
                 id="a position that is true is no number"),
    pytest.param([PYTEST_TABLE | {"rows": {"position": None}}], f"{AT}.rows: {PLACE}",
                 id="a place with neither"),
    pytest.param([PYTEST_TABLE | {"rows": {"index": 1}}], f"{AT}.rows: {PLACE}", id="a place with another key"),
    pytest.param([PYTEST_TABLE | {"columns_from": {"keyword": "arg names"}}], f"{AT}.columns_from: {PLACE}",
                 id="a place whose keyword is no name"),
    pytest.param([PYTEST_TABLE | {"columns_from": "names"}],
                 f"{AT}.columns_from: must be {{position, keyword}}, parameters, bound or fields",
                 id="columns_from that is no place and no word of its own"),
    pytest.param([PYTEST_TABLE | {"columns_from": "bound"}],
                 f"{AT}.columns_from: bound is the names a loop binds: write it with loop", id="bound with a decorator"),
    pytest.param([LOOP | {"columns_from": {"position": 0}}],
                 f"{AT}.columns_from: a loop has no arguments: write bound or fields", id="a place with a loop"),
    pytest.param([LOOP | {"columns_from": "parameters"}], f"{AT}.columns_from: a loop's columns are bound or fields",
                 id="parameters with a loop"),
    pytest.param([PYTEST_TABLE | {"columns_from": "fields"}], f"{AT}.columns_from: fields needs row: literal",
                 id="fields with a dotted row"),
    pytest.param([PYTEST_TABLE | {"row": "param"}], f"{AT}.row: 'param' is not an outside name such as <package>.<name>",
                 id="a row that is neither dotted nor literal"),
    pytest.param([PYTEST_TABLE | {"decorator": "parametrize"}],
                 f"{AT}.decorator: 'parametrize' is not an outside name such as <package>.<name>",
                 id="a decorator that is not dotted"),
    pytest.param([CALL | {"call": []}], f"{AT}.call: must be a list of outside names such as <package>.<name>",
                 id="an empty list of calls"),
    pytest.param([PYTEST_TABLE | {"id": "id"}], ROW_ID, id="an id written as a bare keyword, as testing.table wrote it"),
    pytest.param([PYTEST_TABLE | {"id": {"keyword": "id", "field": "id"}}], ROW_ID, id="an id of two kinds"),
    pytest.param([PYTEST_TABLE | {"id": {"position": -1}}], ROW_ID, id="an id at a negative position"),
    pytest.param([PYTEST_TABLE | {"row": "literal"}],
                 f"{AT}.id: {{keyword}} names a keyword of a row call: write a dotted row", id="a keyword id of a literal row"),
    pytest.param([PYTEST_TABLE | {"id": {"field": "name"}}],
                 f"{AT}.id: {{field}} names a field of a literal row: write row: literal", id="a field id of a row call"),
    pytest.param([PYTEST_TABLE | {"x": 1}], f"{AT}: unknown key 'x': {SLOTS}", id="an unknown key"),
    pytest.param([PYTEST_TABLE, PYTEST_TABLE | {"x": 1}], f"layered.yaml: testing.tables.1: unknown key 'x': {SLOTS}",
                 id="an entry is addressed by its index from 0"),
    pytest.param([FIELD_ROW], f"{AT}.id: the language Python does not write `writing.field`, how a row's id is given "
                              "by a field", id="a field id under a language that writes no field"),
])
def test_a_bad_table_form_is_refused(tables, expected):
    assert problems(with_tables(tables)) == [expected]


def test_a_language_that_writes_no_template_cannot_say_a_row_call_nor_its_keyword_id():
    assert problems(with_tables([PYTEST_TABLE]), languages={"python": TOY}) == [
        f"{AT}.row: the language Toy does not write `writing.call`, how a row call is named",
        f"{AT}.id: the language Toy does not write `writing.keyword`, how a row's id is given by a keyword"]


def test_an_id_by_position_needs_no_template():
    assert parsed(with_tables([POSITIONED, LOOP]), languages={"python": TOY}).framework.tables == (
        TableForm(Place(0), Place(1), (), RowId(position=0), decorator=("checks", "cases")),
        TableForm(BOUND, None, (), RowId(position=0), loop=True))
```

`replace` is already imported at the top of the file (`from dataclasses import replace`).

- [ ] **Step 3: Write the failing key-table tests (T12, T13)**

In `tests/modules/spec/application/logic/test_profile_needs.py`, add `PYTEST_TABLE` to the import from
`tests.modules.spec.profiles` and append:

```python
def test_the_forms_of_a_table_need_the_tables_of_cases_of_a_test_function():
    document = layered(language="toy", testing={"files": ["test_*.py"], "functions": "test_*", "tables": [PYTEST_TABLE]})
    assert ("layered.yaml: testing.tables: its check reads function.tables (the tables of cases of a test function), "
            "which the language toy does not supply: drop testing.tables, or check the app with a language whose "
            "reader supplies function.tables") in problems(document, languages=LANGUAGES)
```

In `tests/modules/spec/application/test_explain.py`, add to `SHAPE` after the `testing.table` line:

```python
    Shown('testing.tables', 1, 'the forms a table of cases is written in', False, True),
```

and append:

```python
def test_the_forms_of_a_table_and_each_slot_of_a_form_are_keys_of_the_format():
    tables, slot = explained("testing.tables"), explained("testing.tables.id")
    assert (tables.key, tables.meaning, tables.rules) == (
        "testing.tables", "the forms a table of cases is written in", ("scenario-coverage",))
    assert [(held.key, held.required) for held in tables.keys] == [
        ("testing.tables.decorator", False), ("testing.tables.call", False), ("testing.tables.loop", False),
        ("testing.tables.columns_from", True), ("testing.tables.rows", False), ("testing.tables.row", True),
        ("testing.tables.id", True)]
    assert (slot.key, slot.where, slot.required, slot.meaning) == (
        "testing.tables.id", "testing.tables[]", True, "what gives a row its id")
```

In `tests/modules/spec/application/logic/test_retired_keys.py`, in the `TESTING` row of
`test_each_mapping_reads_the_entries_of_its_own_scope`, change
`use files, functions, mocks, skips, table",` to `use files, functions, mocks, skips, table, tables",`.

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, the row `id="an unknown key"` of the
`testing` table (line 49) says `unknown key 'colour': use files, functions, mocks, skips, table`: make it
`... skips, table, tables` (a new key of `testing` joins the list the unknown-key problem prints; Task 4 makes it
`skips, tables`). Run `grep -rn "mocks, skips" tests` to be sure these two are the only lines that print the list.

- [ ] **Step 4: Run them to verify they fail**

Run: `uv run pytest tests/modules/spec -q`
Expected: FAIL — `ImportError: cannot import name 'Place' from 'xarch.profile_values.testing'`.

- [ ] **Step 5: The values**

In `xarch/profile_values/testing.py`, add `tables: tuple[TableForm, ...] = ()` to `Framework` after `table`, and end its
docstring `...; how a test function holds a table of cases (None: the profile does not say); and the table forms it
writes (tables; none: it writes none)."""`. Add, between `Framework` and `CaseTable`:

```python
PARAMETERS = "parameters"
"""What columns_from says of a form whose column names are the test's own parameters."""
BOUND = "bound"
"""What columns_from says of a loop whose column names are the names it binds."""
FIELDS = "fields"
"""What columns_from says of a form whose column names are the fields of each row."""


@dataclass(frozen=True)
class Place:
    """Where a slot of a table form is among the arguments of its holder: the argument at position (from 0; None: none
    is read by its position), else the one its keyword gives ("": none is read by a keyword); one of the two at
    least."""
    position: int | None = None
    keyword: str = ""


@dataclass(frozen=True)
class RowId:
    """What gives a row of a table its id, exactly one of three: a keyword of the row call (keyword), a field of a
    literal row (field), or its value at a position from 0 (position)."""
    keyword: str = ""
    field: str = ""
    position: int | None = None


@dataclass(frozen=True)
class TableForm:
    """One form a table of cases is written in, as the framework's `testing.tables` says it. Its holder, one of three:
    a decorator of the test (decorator, its dotted name), a call that makes or wraps the test (call, one or more
    dotted names), or a loop of the test's body over a list literal (loop). Where the column names come from
    (columns_from: a place among the holder's arguments, or PARAMETERS, BOUND or FIELDS); where the rows are (rows: a
    place among the holder's arguments; None for a loop); how a row is written (row: the dotted name a row calls;
    empty: a row is a literal); and what gives a row its id."""
    columns_from: Place | str
    rows: Place | None
    row: tuple[str, ...]
    id: RowId
    decorator: tuple[str, ...] = ()
    call: tuple[tuple[str, ...], ...] = ()
    loop: bool = False
```

- [ ] **Step 6: The key table**

In `xarch/modules/spec/domain/profile_keys.py`, after `TABLE = "testing.table"` add `TABLES = "testing.tables"`, and in
`SCOPES` after `TABLE: "testing.table",` add `TABLES: "testing.tables[]",`.

In `xarch/modules/spec/domain/key_table.py`, add `TABLES,` to the import list after `TABLE,`; after
`Key(TESTING, "table", rules=("scenario-coverage",), opens=TABLE),` add

```python
    Key(TESTING, "tables", rules=("scenario-coverage",), opens=TABLES),
```

after `Key(TABLE, "keywords", rules=("scenario-coverage",)),` add

```python

    Key(TABLES, "decorator", rules=("scenario-coverage",)),
    Key(TABLES, "call", rules=("scenario-coverage",)),
    Key(TABLES, "loop", rules=("scenario-coverage",)),
    Key(TABLES, "columns_from", True, rules=("scenario-coverage",)),
    Key(TABLES, "rows", rules=("scenario-coverage",)),
    Key(TABLES, "row", True, rules=("scenario-coverage",)),
    Key(TABLES, "id", True, rules=("scenario-coverage",)),
```

and in `NEEDS` after `"testing.table": ("function.tables",),` add `"testing.tables": ("function.tables",),`.

- [ ] **Step 7: The texts of the new keys**

In `xarch/architectures/presets/format/keys.yaml`, after the `table` fragment (the block ending `        id: id`) add:

```yaml
  tables: |2
      tables:
        - decorator: checks.cases
          columns_from: {position: 0, keyword: names}
          rows: {position: 1, keyword: cases}
          row: checks.case
          id: {keyword: id}
```

and after the `testing.table.keywords` entry (ending `          keywords: [names, rows]`) add:

```yaml
  testing.tables:
    meaning: the forms a table of cases is written in
    accepts: >-
      a list of forms, each one of decorator, call or loop, with columns_from, rows, row and id; left out or empty:
      the framework writes no table
    example: |
      <<testing>>
      <<tables>>
  testing.tables[].decorator:
    meaning: the decorator that holds the table
    accepts: a dotted name, a decorator of the test whose arguments hold the column names and the rows
    example: |
      <<testing>>
      <<tables>>
  testing.tables[].call:
    meaning: the calls that hold the table
    accepts: a list of dotted names, each a call that makes or wraps the test and whose arguments hold the rows
    example: |
      <<testing>>
        tables:
          - call: [checks.each]
            columns_from: {position: 0}
            rows: {position: 1}
            row: checks.case
            id: {keyword: id}
  testing.tables[].loop:
    meaning: a loop of the test's body runs the rows
    accepts: "true: the rows are a list literal that a loop statement of the test's body iterates"
    example: |
      <<testing>>
        tables:
          - loop: true
            columns_from: bound
            row: literal
            id: {position: 0}
  testing.tables[].columns_from:
    meaning: where the column names come from
    accepts: >-
      {position: <n>, keyword: <name>} of the holder's arguments, at least one of them, a keyword alone reading only
      the keyword; or parameters, the test's own parameters; or bound, the names the loop binds; or fields, the
      fields of each row
    example: |
      <<testing>>
      <<tables>>
  testing.tables[].rows:
    meaning: where the rows are
    accepts: >-
      {position: <n>, keyword: <name>} of the holder's arguments, at least one of them; needed with decorator and
      call, refused with loop
    example: |
      <<testing>>
      <<tables>>
  testing.tables[].row:
    meaning: how a row is written
    accepts: "a dotted name, a row being a call of it; or literal, a row being a list or object literal"
    example: |
      <<testing>>
      <<tables>>
  testing.tables[].id:
    meaning: what gives a row its id
    accepts: >-
      {keyword: <name>}, a keyword of the row call; {field: <name>}, a field of a literal row; or {position: <n>}, its
      value at that position
    example: |
      <<testing>>
      <<tables>>
```

- [ ] **Step 8: The parser**

In `xarch/modules/spec/application/logic/profile_checks.py`:

1. Change the import `from xarch.modules.spec.domain.profile_keys import FILE, FIXTURE, NAMING, PAGE, RULE_ID, TABLE` to
   end `..., RULE_ID, TABLE, TABLES`, and `from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework`
   to

```python
from xarch.profile_values.testing import (
    BOUND,
    FIELDS,
    PARAMETERS,
    CaseTable,
    Fakes,
    Fixture,
    Framework,
    Place,
    RowId,
    TableForm,
)
```

2. Below `CALLED = "()"` and its docstring add:

```python
HOLDERS = ("decorator", "call", "loop")
"""The keys of a table form that say what holds its rows, exactly one of them in each."""
LITERAL = "literal"
"""What `row` says of a form whose rows are literals, not calls."""
PLACE = "must be {position: <n>, keyword: <name>}, at least one of them, of the holder's arguments"
"""What the loader says of a place of a table form that is none."""
```

3. After `case_table`, add:

```python
def table_forms(value: Any, where: str, problems: list[str], language: Language) -> tuple[TableForm, ...] | None:
    """The forms a table of cases is written in, each entry addressed `<where>.<i>`, i from 0; None when any entry
    has a problem."""
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of table forms, each {{decorator | call | loop, columns_from, rows, "
                        "row, id}")
        return None
    forms = [_table_form(entry, f"{where}.{index}", problems, language) for index, entry in enumerate(value)]
    found = tuple(form for form in forms if form is not None)
    return found if len(found) == len(forms) else None


def _table_form(entry: Any, where: str, problems: list[str], language: Language) -> TableForm | None:
    """One form: exactly one holder, its slots each in the shape the holder takes, and the language able to say its
    row."""
    if not isinstance(entry, Mapping):
        problems.append(f"{where}: must be a mapping with one of decorator, call or loop")
        return None
    count = len(problems)
    problems += unknown_keys(entry, names_of(TABLES), where, TABLES)
    holders = [key for key in HOLDERS if key in entry]
    if len(holders) != 1:
        problems.append(f"{where}: must have exactly one of decorator, call or loop")
    loop = holders == ["loop"]
    needed = (*required_of(TABLES), *(("rows",) if holders in (["decorator"], ["call"]) else ()))
    problems += [f"{where}: missing `{key}`" for key in needed if key not in entry]
    decorator = (_outside_name_at(entry["decorator"], f"{where}.decorator", problems, language)
                 if "decorator" in entry else ())
    calls = outside_names(entry["call"], f"{where}.call", problems, language) if "call" in entry else ()
    if "loop" in entry and entry["loop"] is not True:
        problems.append(f"{where}.loop: must be true: the rows are a list a loop of the test's body runs")
    if "rows" in entry and loop:
        problems.append(f"{where}.rows: a loop runs the rows it iterates: drop rows")
    rows = _place(entry["rows"], f"{where}.rows", problems, language) if "rows" in entry and not loop else None
    row = _row_of(entry["row"], f"{where}.row", problems, language) if "row" in entry else None
    columns = (_columns_from(entry["columns_from"], f"{where}.columns_from", loop, row, problems, language)
               if "columns_from" in entry else None)
    given = _row_id(entry["id"], f"{where}.id", row, problems, language) if "id" in entry else None
    if len(problems) != count or decorator is None or calls is None or row is None or columns is None or given is None:
        return None
    problems += _unwritten(row, given, where, language)
    if len(problems) != count:
        return None
    return TableForm(columns, rows, row, given, decorator, calls, loop)


def _counted(value: Any) -> bool:
    """Whether a value is a whole number from 0 (true and false are no numbers here)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _place(value: Any, where: str, problems: list[str], language: Language) -> Place | None:
    """A place among the holder's arguments: {position, keyword}, at least one of them given."""
    position = value.get("position") if isinstance(value, Mapping) else None
    keyword = value.get("keyword") if isinstance(value, Mapping) else None
    if not (isinstance(value, Mapping) and set(value) <= {"position", "keyword"}
            and (position is not None or keyword is not None)
            and (position is None or _counted(position))
            and (keyword is None or (isinstance(keyword, str) and names.is_name(keyword, language.names)))):
        problems.append(f"{where}: {PLACE}")
        return None
    return Place(position, keyword or "")


def _row_of(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, ...] | None:
    """How a row is written: the steps of the outside name a row calls, or none for a literal row."""
    return () if value == LITERAL else _outside_name_at(value, where, problems, language)


def _columns_from(value: Any, where: str, loop: bool, row: tuple[str, ...] | None, problems: list[str],
                  language: Language) -> Place | str | None:
    """Where the column names come from: a place of the holder's arguments, or one of PARAMETERS, BOUND and FIELDS,
    each where its holder and its row allow it (row None: refused already, and not looked at)."""
    if isinstance(value, Mapping) and loop:
        problems.append(f"{where}: a loop has no arguments: write bound or fields")
        return None
    if isinstance(value, Mapping):
        return _place(value, where, problems, language)
    if value not in (PARAMETERS, BOUND, FIELDS):
        problems.append(f"{where}: must be {{position, keyword}}, parameters, bound or fields")
        return None
    if value == BOUND and not loop:
        problems.append(f"{where}: bound is the names a loop binds: write it with loop")
        return None
    if value == PARAMETERS and loop:
        problems.append(f"{where}: a loop's columns are bound or fields")
        return None
    if value == FIELDS and row:
        problems.append(f"{where}: fields needs row: literal")
        return None
    return str(value)


def _row_id(value: Any, where: str, row: tuple[str, ...] | None, problems: list[str],
            language: Language) -> RowId | None:
    """What gives a row its id: exactly one of {keyword}, {field} and {position}, a keyword only of a row call and a
    field only of a literal row (row None: refused already, and not looked at)."""
    kind, item = next(iter(value.items())) if isinstance(value, Mapping) and len(value) == 1 else ("", None)
    named = isinstance(item, str) and names.is_name(item, language.names)
    if not ((kind in ("keyword", "field") and named) or (kind == "position" and _counted(item))):
        problems.append(f"{where}: must be one of {{keyword: <name>}}, {{field: <name>}} or {{position: <n>}}")
        return None
    if kind == "keyword" and row == ():
        problems.append(f"{where}: {{keyword}} names a keyword of a row call: write a dotted row")
        return None
    if kind == "field" and row:
        problems.append(f"{where}: {{field}} names a field of a literal row: write row: literal")
        return None
    return RowId(**{kind: item})


def _unwritten(row: tuple[str, ...], given: RowId, where: str, language: Language) -> list[str]:
    """The problems of a form the language cannot say: a row call with no `writing.call`, and an id by a keyword or a
    field with no template of its own; an id by position needs none."""
    writing, title = language.checked.writing, language.checked.title
    found: list[str] = []
    if row and not writing.call:
        found.append(f"{where}.row: the language {title} does not write `writing.call`, how a row call is named")
    if given.keyword and not writing.keyword:
        found.append(f"{where}.id: the language {title} does not write `writing.keyword`, how a row's id is given by "
                     "a keyword")
    if given.field and not writing.field:
        found.append(f"{where}.id: the language {title} does not write `writing.field`, how a row's id is given by a "
                     "field")
    return found
```

In `xarch/modules/spec/application/logic/profile_parsing.py`, `_testing`: replace

```python
    table = ck.case_table(value["table"], "testing.table", problems, language) if "table" in value else None
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None:
        return None
    return _Testing(replace(framework, table=table), table, mocks)
```

with

```python
    table = ck.case_table(value["table"], "testing.table", problems, language) if "table" in value else None
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None or tables is None:
        return None
    return _Testing(replace(framework, table=table, tables=tables), table, mocks)
```

- [ ] **Step 9: Run the tests**

Run: `uv run pytest tests/modules/spec tests/bootstrap/test_profile_explain.py tests/bootstrap/test_needs_agree.py tests/architecture -q`
Expected: PASS. If a `keys.yaml` example test fails, the failing example is printed with its problem: fix the yaml text,
never the test.

- [ ] **Step 10: Commit**

```bash
git add xarch/profile_values/testing.py xarch/modules/spec xarch/architectures/presets/format/keys.yaml \
  tests/modules/spec
git commit -m "A framework may write testing.tables, a list of table forms, each one of decorator, call or loop with columns_from, rows, row and id, refused entry by entry under testing.tables.<i>"
```

---

## Task 3: The reader reads the tables of the framework's forms and tags each with its form's index

**Files:**
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring end; imports; `read`, `parsed`, `_parsed`,
  `_functions`, `_function`, `_table`, `_row`; new `_reads`, `_argument`)
- Modify: `xarch/modules/rules/application/ports/source_tree.py` (`read`)
- Modify: `xarch/modules/rules/application/services/source_check.py:79-82`
- Modify: `tests/fakes/filesystem.py` (`FakeSourceTree.read`)
- Modify: `xarch/architectures/presets/testing/pytest.yaml` (gains `tables`, keeps `table` until Task 4)
- Modify: `tests/bootstrap/test_other_framework.py` (gains `tables`), `tests/bootstrap/test_bundled_guards.py`
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`

**Interfaces:**
- Consumes: `TableForm`, `Place`, `RowId`, `FIELDS` (Task 2).
- Produces: `SourceTree.read(root, paths, tables: tuple[TableForm, ...] = (), immutable=(), interface=(), *, standard,
  private, special)`; each `Table.form` is the index in `tables` of the form that read it.

- [ ] **Step 1: Write the failing tests (T5, T6, Review Focus 4)**

In `tests/modules/rules/adapters/test_fs_source_tree.py`:

Replace `from xarch.profile_values.testing import CaseTable` with

```python
from dataclasses import replace

from xarch.profile_values.testing import FIELDS, Place, RowId, TableForm
```

(put `from dataclasses import replace` with the other standard-library imports at the top). Replace the `PYTEST = ...`
line with

```python
PYTEST = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                   decorator=("pytest", "mark", "parametrize"))
```

Replace `parsed` with

```python
def parsed(tmp_path: Path, text: str, tables: tuple[TableForm, ...] = (PYTEST,)) -> SourceFile:
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], tables, standard=STANDARD, **HANDED)[0]
```

Replace the block from `OTHER = CaseTable(...)` to the end of `test_without_a_form_no_table_is_recognised` with:

```python
OTHER = TableForm(Place(0, "names"), Place(1, "rows"), ("cases", "row"), RowId(keyword="name"),
                  decorator=("cases", "table"))
OTHER_TEXT = ("import cases\nfrom cases import row\nimport pytest\n\n"
              "@cases.table('a, b', [row(1, 2, name='x'), cases.row(3, 4, id='y')])\ndef it_a(): ...\n\n"
              "@pytest.mark.parametrize('a', [1])\ndef it_b(): ...\n\n"
              "@cases.table(names='a', rows=[1])\ndef it_c(): ...\n")


def test_a_table_is_read_in_the_names_the_form_gives(tmp_path):
    functions = parsed(tmp_path, OTHER_TEXT, (OTHER,)).functions
    a, c = line_of(OTHER_TEXT, "@cases.table('a, b'"), line_of(OTHER_TEXT, "@cases.table(names=")
    assert [(f.name, f.tables) for f in functions] == [
        ("it_a", (Table(a, ("a", "b"), (Row(a, True, "x", (None, None)), Row(a, True, None, (None, None))), form=0, runs=0),)),
        ("it_b", ()),
        ("it_c", (Table(c, ("a",), (Row(c, False, None, ()),), form=0, runs=0),)),
    ]


def test_without_keywords_only_positional_arguments_are_read(tmp_path):
    form = TableForm(Place(0), Place(1), ("cases", "row"), RowId(keyword="name"), decorator=("cases", "table"))
    functions = parsed(tmp_path, OTHER_TEXT, (form,)).functions
    assert [len(f.tables) for f in functions] == [1, 0, 0]


def test_under_a_place_with_a_keyword_alone_only_the_keyword_is_read(tmp_path):
    form = TableForm(Place(keyword="names"), Place(keyword="rows"), ("cases", "row"), RowId(keyword="name"),
                     decorator=("cases", "table"))
    functions = parsed(tmp_path, OTHER_TEXT, (form,)).functions
    assert [len(f.tables) for f in functions] == [0, 0, 1]


def test_without_a_form_no_table_is_recognised(tmp_path):
    assert [f.tables for f in parsed(tmp_path, OTHER_TEXT, ()).functions] == [(), (), ()]


def test_each_table_is_tagged_with_the_index_of_the_form_that_read_it(tmp_path):
    functions = parsed(tmp_path, OTHER_TEXT, (OTHER, PYTEST)).functions
    assert [[t.form for t in f.tables] for f in functions] == [[0], [1], [0]]


def test_a_table_read_by_the_second_form_is_tagged_with_its_index_and_read_the_same(tmp_path):
    first = parsed(tmp_path, TABLE).functions[0].tables[0]
    second = parsed(tmp_path, TABLE, (replace(PYTEST, decorator=("a", "cases")), PYTEST)).functions[0].tables[0]
    assert second == replace(first, form=1)


@pytest.mark.parametrize("skipped", [
    pytest.param(replace(PYTEST, row=()), id="a form whose rows are literals"),
    pytest.param(replace(PYTEST, id=RowId(position=0)), id="a form whose id is a position"),
    pytest.param(replace(PYTEST, columns_from=FIELDS), id="a form whose columns are the fields of each row"),
    pytest.param(replace(PYTEST, decorator=(), call=(("pytest", "mark", "parametrize"),)), id="a call form"),
    pytest.param(TableForm(FIELDS, None, (), RowId(position=0), loop=True), id="a loop form"),
])
def test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does(tmp_path, skipped):
    assert parsed(tmp_path, TABLE, (skipped,)).functions[0].tables == ()
    assert [t.form for t in parsed(tmp_path, TABLE, (skipped, PYTEST)).functions[0].tables] == [1]
```

The existing tests above this block (`test_a_parametrized_function_lists_...`, the column, rows and
`test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement` tests, `ROWS`) keep their
expectations unchanged: they now read through the default `(PYTEST,)`.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/modules/rules/adapters/test_fs_source_tree.py -q`
Expected: FAIL — `AttributeError: 'tuple' object has no attribute 'decorator'` (the reader still takes one `CaseTable`).

- [ ] **Step 3: The reader**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

1. Replace `from xarch.profile_values.testing import CaseTable` with
   `from xarch.profile_values.testing import Place, TableForm`.
2. In `FsSourceTree.read`, rename the parameter `table: CaseTable | None = None` to
   `tables: tuple[TableForm, ...] = ()` and pass `tables` where it passed `table` to `_parsed`. In `parsed`, pass `()`
   where it passed `None`.
3. `_parsed`: parameter `form: CaseTable | None` becomes `forms: tuple[TableForm, ...]`, and
   `functions = _functions(tree, forms, private, where)`.
4. `_functions(tree, forms: tuple[TableForm, ...], private, where=None)`: pass `forms` to each `_function`.
5. `_function(node, scope, lists, forms: tuple[TableForm, ...], private, owner="")`: its tables line becomes

```python
    tables = tuple(table for d in node.decorator_list if (table := _table(d, scope, lists, forms)) is not None)
```

6. Replace `_table` and `_row` with:

```python
def _table(decorator: ast.expr, scope: list[Scope], lists: dict[str, ast.expr],
           forms: tuple[TableForm, ...]) -> Table | None:
    """The table a decorator holds, read in the first form the reader reads whose decorator it is and tagged with
    that form's index; None when no form is, or its column names cannot be read."""
    if not isinstance(decorator, ast.Call):
        return None
    called = _ref(decorator.func, scope)
    index = next((i for i, form in enumerate(forms) if _reads(form) and form.decorator == called), None)
    if index is None:
        return None
    form = forms[index]
    columns = _columns(_argument(decorator, form.columns_from))
    if columns is None:
        return None
    values = _argument(decorator, form.rows)
    if isinstance(values, ast.Name):
        values = lists.get(values.id)
    rows = None
    if isinstance(values, (ast.List, ast.Tuple)) and not any(isinstance(v, ast.Starred) for v in values.elts):
        rows = tuple(_row(v, scope, form) for v in values.elts)
    return Table(decorator.lineno, columns, rows, form=index, runs=0)


def _reads(form: TableForm) -> bool:
    """Whether the reader reads tables in the form: held by a decorator, the column names and the rows each at a
    place among its arguments, a row a call of a dotted name and its id a keyword of that call."""
    return (bool(form.decorator) and isinstance(form.columns_from, Place) and form.rows is not None and bool(form.row)
            and bool(form.id.keyword))


def _argument(call: ast.Call, place: Place | str | None) -> ast.expr | None:
    """The argument of the call at a place: the positional one at its position when the call has that many, else the
    one its keyword gives; None when neither is written, or when place is no place."""
    if not isinstance(place, Place):
        return None
    if place.position is not None and place.position < len(call.args):
        return call.args[place.position]
    given = {k.arg: k.value for k in call.keywords if k.arg}
    return given.get(place.keyword) if place.keyword else None
```

and, in `_row`, change the signature to `def _row(node: ast.expr, scope: list[Scope], form: TableForm) -> Row:` and
`ids = [k.value for k in node.keywords if k.arg == form.id]` to
`ids = [k.value for k in node.keywords if k.arg == form.id.keyword]`.

7. Append to the module docstring, before its closing `"""`, a paragraph:

```
A test function holds the tables of cases its decorators hold, each read in the first of the framework's forms
(`testing.tables`) whose decorator it is, and tagged with that form's index: its column names are the argument at
the form's `columns_from` (by its position when the call has an argument there, else by its keyword), one
comma-separated string or a list or tuple of strings; its rows the argument at its `rows`, a list or tuple literal or
the name of one assigned once at the top of the file (any other form leaves the rows unread); and a row is written
when it is a call of the form's `row`, its id the string literal the form's keyword gives. Only the forms whose
holder is a decorator, whose columns and rows are places, whose row is a call and whose id a keyword are read; any
other form reads no table.
```

- [ ] **Step 4: The port, the service and the fake**

In `xarch/modules/rules/application/ports/source_tree.py`, replace the import of `CaseTable` with
`from xarch.profile_values.testing import TableForm`, the parameter `table: CaseTable | None = None` with
`tables: tuple[TableForm, ...] = ()`, and in the docstring replace
`A function holds the tables written in the form `table` names; with none, no table is recognised.` with
`A function holds the tables written in one of the forms `tables` holds, each tagged with the index of its form; with
none, no table is recognised.` (re-wrap at 120 columns).

In `xarch/modules/rules/application/services/source_check.py`, replace

```python
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), table, marks, interface,
```

with

```python
        tables = rules.framework.tables if rules.framework is not None else ()
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), tables, marks, interface,
```

In `tests/fakes/filesystem.py`, replace `from xarch.profile_values.testing import CaseTable` with
`from xarch.profile_values.testing import TableForm` and `table: CaseTable | None = None` with
`tables: tuple[TableForm, ...] = ()` in `FakeSourceTree.read`.

- [ ] **Step 5: The bundled preset and the other framework write their forms**

In `xarch/architectures/presets/testing/pytest.yaml`, after the `table:` line add:

```yaml
tables:
  - decorator: pytest.mark.parametrize
    columns_from: {position: 0, keyword: argnames}
    rows: {position: 1, keyword: argvalues}
    row: pytest.param
    id: {keyword: id}
```

In `tests/bootstrap/test_other_framework.py`, after `  table: {decorator: cases.table, row: cases.row, id: name}`
add:

```yaml
  tables: [{decorator: cases.table, columns_from: {position: 0}, rows: {position: 1}, row: cases.row,
            id: {keyword: name}}]
```

In `tests/bootstrap/test_bundled_guards.py`, add `Place, RowId, TableForm` to the import from
`xarch.profile_values.testing`, and in `test_the_bundled_profiles_use_every_guard_of_their_own` change the framework
assertion to

```python
    form = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                     decorator=("pytest", "mark", "parametrize"))
    assert profile.framework == Framework(("test_*.py", "*_test.py"), "test_*",
                                              tuple(tuple(s.split(".")) for s in skips), table, (form,))
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/modules/rules tests/bootstrap/test_other_framework.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_source_checks.py tests/bootstrap/test_recorded_corpora.py tests/fakes -q`
Expected: PASS (the corpora replay unchanged: the reader reads the same tables under the pytest form).

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules xarch/architectures/presets/testing/pytest.yaml tests/fakes/filesystem.py \
  tests/modules/rules/adapters/test_fs_source_tree.py tests/bootstrap/test_other_framework.py \
  tests/bootstrap/test_bundled_guards.py
git commit -m "The reader reads the tables of the framework's forms, the first decorator form whose decorator a test carries, and tags each with that form's index"
```

---

## Task 4: The checks and the docs read the forms; the guard keeps no table; `testing.table` is retired

**Files:**
- Modify: `xarch/profile_values/testing.py` (remove `CaseTable`, `Framework.table`, `ScenarioCoverage.table`;
  `RowId.name`, `RowId.written`; docstrings)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (remove `case_table`; imports)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (imports, `_Testing`, `_testing`, plain_tables
  refusal at 204-205, `_scenario_coverage`)
- Modify: `xarch/modules/spec/application/logic/docs_template.py` (`_guard_line`, `_row_phrase`, import)
- Modify: `xarch/modules/spec/domain/profile_keys.py` (remove `TABLE`; `RETIRED`)
- Modify: `xarch/modules/spec/domain/key_table.py` (remove the `table` keys and `NEEDS` entry)
- Modify: `xarch/architectures/presets/format/keys.yaml`, `xarch/architectures/presets/testing/pytest.yaml`
- Modify: `xarch/modules/rules/application/logic/scenarios.py` (docstring, `_covered`, `_rows`)
- Create: `tests/architecture/test_table_forms.py`
- Modify tests: `tests/modules/spec/profiles.py`, `tests/modules/spec/application/logic/test_testing.py`,
  `test_profile_parsing_tests.py`, `test_libraries_and_guards.py`, `test_retired_keys.py`, `test_profile_needs.py`,
  `tests/modules/spec/application/test_explain.py`, `tests/modules/spec/domain/test_profile_keys.py`,
  `tests/modules/rules/builders.py`, `tests/modules/rules/application/logic/test_scenarios.py`,
  `tests/modules/rules/adapters/test_spec_profile.py`, `tests/bootstrap/test_bundled_guards.py`,
  `tests/bootstrap/test_profile_file.py`, `tests/bootstrap/test_profile_explain.py`,
  `tests/bootstrap/test_other_framework.py`, `tests/architecture/test_agnostic.py`

**Interfaces:**
- Consumes: everything of Tasks 1-3.
- Produces: `RowId.name -> str` (property); `RowId.written(writing: Writing, callee: str, text: str) -> str`;
  `ScenarioCoverage(results, tier, suffix, columns, file)`; `Framework(files, functions, skips=(), tables=())`;
  `tests.modules.rules.builders.PYTEST_FORM`.

- [ ] **Step 1: Write the failing tests**

**(a) T1, the retired key** — `tests/modules/spec/application/logic/test_retired_keys.py`:
- Remove `TABLE,` from the import of `xarch.modules.spec.domain.profile_keys`, and remove the row
  `pytest.param(TABLE, writing(covered(), "testing", "table"), "testing.table: unknown key 'banned'", id="testing.table"),`.
- In the `TESTING` row, change `use files, functions, mocks, skips, table, tables",` to `use files, functions, mocks, skips, tables",`.
- Add to `test_the_shipped_table_answers_each_name_in_its_scope`'s table:
  `pytest.param(TESTING, "table", TABLE_MOVED, id="the testing key table"),`, and to
  `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`'s:
  `pytest.param("testing.table", TABLE_MOVED, id="testing.table"),`.
- Add `PRESETS` to the import from `tests.modules.spec.profiles`, and append:

```python
TABLE_MOVED = "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"
OLD_TABLE = {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
             "keywords": ["argnames", "argvalues"]}
"""testing.table as profiles wrote it before 0.3.0."""


@pytest.mark.parametrize("testing, presets", [
    pytest.param({"files": ["test_*.py"], "functions": "test_*", "table": OLD_TABLE}, PRESETS, id="in an inline map"),
    pytest.param("old", {"old": {"files": ["test_*.py"], "functions": "test_*", "table": OLD_TABLE}},
                 id="in a preset"),
])
def test_the_table_of_testing_is_refused_with_the_list_of_forms_that_replaces_it(testing, presets):
    assert problems(layered(testing=testing), presets=presets) == [
        f"layered.yaml: testing: unknown key 'table': {TABLE_MOVED}; use files, functions, mocks, skips, tables"]
```

(`TABLE_MOVED` is used in the parametrize tables above it, so define it near the file's other text constants at the
top, not at the end.)

`tests/modules/spec/domain/test_profile_keys.py`: append to the `RETIRED == (...)` tuple of
`test_the_names_retired_are_tier_...` the entry
`Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),`
(import `TESTING` from `xarch.modules.spec.domain.profile_keys` if the file does not yet).

**(b) T2, through the commands** — `tests/bootstrap/test_profile_file.py`, append:

```python
OLD_TABLE_PROFILE = PRESET_PROFILE.replace("testing: pytest\n", 'testing:\n  files: ["test_*.py"]\n  functions: "test_*"\n'
                                           "  table: {decorator: pytest.mark.parametrize, row: pytest.param, id: id}\n")
RETIRED_TABLE = ("testing: unknown key 'table': moved in 0.3.0: write tables, a list of forms (xarch profile explain "
                 "testing.tables); use files, functions, mocks, skips, tables")


def test_a_profile_writing_the_table_of_testing_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, OLD_TABLE_PROFILE)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert checked.exit_code == 1
    assert f"    {path}: {RETIRED_TABLE}" in checked.output.splitlines()
```

`tests/bootstrap/test_profile_explain.py`, append:

```python
def test_the_table_of_testing_is_answered_from_the_table_of_retired_names():
    found = runner.invoke(app, ["profile", "explain", "testing.table", "--format", "json"])
    assert (found.exit_code, json.loads(found.output)["retired"]) == (
        2, "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)")
```

**(c) T7, the wording** — `tests/modules/rules/builders.py`: change the testing import to
`from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId, ScenarioCoverage, StandIns, TableForm`;
replace the line `TABLE = CaseTable(...)` with

```python
PYTEST_FORM = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                        decorator=("pytest", "mark", "parametrize"))
"""The one form pytest writes a table of cases in, as its preset says it."""
```

and in `PROFILE` replace `ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"), TABLE,
"test_{name:snake}.py")` with `ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"),
"test_{name:snake}.py")` and `framework=Framework(("test_*.py", "*_test.py"), "test_*"),` with
`framework=Framework(("test_*.py", "*_test.py"), "test_*", tables=(PYTEST_FORM,)),`. Run
`grep -rn "builders import" tests | grep -w TABLE` and drop `TABLE` from any import it shows.

`tests/modules/rules/application/logic/test_scenarios.py`: change the builders import to
`from tests.modules.rules.builders import PROFILE, PYTEST_FORM, PYTHON, in_tests, profile, source`, add
`from xarch.profile_values.language import Writing` and
`from xarch.profile_values.testing import FIELDS, Place, RowId, TableForm`, and append:

```python
NAMED = TableForm(Place(0), Place(1), ("x", "case"), RowId(keyword="name"), decorator=("x", "cases"))
"""A form ahead of pytest's in the framework's list: its row x.case, its id the keyword name."""
LITERAL = TableForm(FIELDS, Place(0), (), RowId(field="name"), decorator=("x", "cases"))
"""A form of literal rows whose id is the field name."""
FIRST = TableForm(Place(0), Place(1), ("x", "case"), RowId(position=0), decorator=("x", "cases"))
"""A form of x.case rows whose id is their first value."""
BRACKETS = Writing(call="{callee}(...)", keyword="{callee}[{keyword}: {text}]", field='{..., {field}: "{text}"}')
"""A language's templates other than Python's, the field one holding braces of its own."""


@pytest.mark.parametrize("form, writing, problem, fix", [
    pytest.param(PYTEST_FORM, PYTHON.writing, "row is not a pytest.param(...)",
                 'write pytest.param(..., id="<a sentence stating the outcome>")',
                 id="pytest's form in Python's words reads as before"),
    pytest.param(PYTEST_FORM, BRACKETS, "row is not a pytest.param(...)",
                 "write pytest.param[id: <a sentence stating the outcome>]", id="the keyword template of the language"),
    pytest.param(LITERAL, BRACKETS, "row is not a literal", 'write {..., name: "<a sentence stating the outcome>"}',
                 id="a literal row whose id is a field"),
    pytest.param(FIRST, PYTHON.writing, "row is not a x.case(...)",
                 "write the row's id, a sentence stating the outcome, as its value at position 0",
                 id="an id by position needs no template"),
])
def test_a_row_is_worded_as_the_form_at_its_index_writes_one_in_the_words_of_the_language(form, writing, problem, fix):
    checked = profile(framework=replace(PROFILE.framework, tables=(NAMED, form)),
                      language=replace(PYTHON, writing=writing))
    bare = replace(table(row("Published", written=False, id=None), row("Missing", 11)), form=1)
    found = violations([RESULTS], [publish_tests(Function(8, "test_publish", (bare,)))], checked)
    assert [(str(v), v.fix) for v in found] == [(f"{FILE}:10: {problem} (scenario-coverage)", fix)]
```

**(d) T8, no kind of form in the checks** — create `tests/architecture/test_table_forms.py`:

```python
"""The scenario-coverage checks word a row from the slots of its form and the language's templates, never from the
kind of form: their module holds no string literal that names a holder of a table form."""
import ast
from pathlib import Path

SCENARIOS = Path(__file__).resolve().parents[2] / "xarch" / "modules" / "rules" / "application" / "logic" / "scenarios.py"
HOLDERS = {"decorator", "call", "loop"}


def test_the_checks_of_scenario_coverage_name_no_kind_of_table_form():
    tree = ast.parse(SCENARIOS.read_text(encoding="utf-8"))
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    assert literals & HOLDERS == set()
```

**(e) T10, T11, the refusals and the guard** — `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:
- Change the import to `from xarch.profile_values.testing import Fakes, Fixture, Framework, ScenarioCoverage, StandIns`
  and add `PYTEST_FORM` to the import from `tests.modules.spec.profiles`.
- In the `testing` table's row `id="an unknown key"` (line 49), `use files, functions, mocks, skips, table,
  tables` becomes `use files, functions, mocks, skips, tables`.
- In `test_the_framework_is_a_preset_by_name_or_the_map_written_out`, the expected value becomes
  `Framework(("test_*.py", "*_test.py"), "test_*", (("pytest", "mark", "skip"), ("pytest", "skip")), (PYTEST_FORM,))`.
- In `test_the_table_of_cases_and_the_mocks_are_checked_with_the_framework_whether_or_not_a_guard_uses_them`, replace
  `document["testing"]["table"] = {"decorator": "x", "row": "y.z"}` with
  `document["testing"]["tables"] = [{"decorator": "x", "row": "y.z", "columns_from": {"position": 0}, "rows": {"position": 1}}]`
  and its two expected lines with `"layered.yaml: testing.tables.0: missing `id`",` and
  `"layered.yaml: testing.tables.0.decorator: 'x' is not an outside name such as <package>.<name>",`.
- In `test_the_guards_in_use_are_those_named_with_the_framework_s_words_taken_from_testing`, the guard becomes
  `ScenarioCoverage("api", "integration", "Result", ("given", "when", "then"), "test_{name:snake}.py"),`.
- Replace `test_scenario_coverage_reads_its_table_from_the_framework_and_says_so_when_there_is_none` with:

```python
NO_FORMS = ("layered.yaml: guards.scenario-coverage: needs `testing.tables`: the forms a table of cases is written in, "
            "such as [{decorator, columns_from, rows, row, id}]")


def test_scenario_coverage_reads_its_forms_from_the_framework_and_says_so_when_there_is_none():
    document = covered(guards={"scenario-coverage": GUARDS["scenario-coverage"]})
    del document["testing"]["tables"]
    assert problems(document) == [NO_FORMS]
    document["testing"]["tables"] = []
    assert problems(document) == [NO_FORMS]
```

- Replace the last two lines of `test_a_tier_whose_table_tests_are_plain_says_so_and_needs_the_form_of_a_table` with:

```python
    document["testing"] = {key: value for key, value in TESTING.items() if key != "tables"}
    assert problems(document) == [PLAIN_NEEDS]
    document["testing"] = TESTING | {"tables": []}
    assert problems(document) == [PLAIN_NEEDS]
```

  with, above the test, `PLAIN_NEEDS = ("layered.yaml: tiers.unit.plain_tables: needs `testing.tables`, the forms a
  table of cases is written in, to know a table test")`.

`tests/modules/spec/application/logic/test_libraries_and_guards.py`: change the import to
`from xarch.profile_values.testing import ScenarioCoverage`, and the expected guard to
`ScenarioCoverage("api", "integration", "Outcome", ("state", "command", "outcome"), FILE))`.

**(f) T15, the docs line** — `tests/modules/spec/application/logic/test_testing.py` (beside the existing guard-line
tests, which hold the `guard_lines` helper this needs; the spec names `test_docs_template.py`, whose tests have no
parsed profile with a guard):
- Remove `TABLE_OK`, `TABLE`, `KEYWORDS`, `with_table`, `test_the_keywords_of_the_table_decorator_are_optional` and
  `test_a_bad_table_entry_is_refused`.
- In `test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines`, replace
  `"table": {"decorator": "cases.table", "row": "cases.row", "id": "name"},` with
  `"tables": [{"decorator": "cases.table", "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "cases.row",
  "id": {"keyword": "name"}}],`. Its assertions do not change.
- Append:

```python
OTHER_FORM = {"decorator": "checks.cases", "columns_from": {"position": 0}, "rows": {"position": 1},
              "row": "checks.case", "id": {"keyword": "name"}}


@pytest.mark.parametrize("tables, clause", [
    pytest.param([POSITIONED], "every row is a literal with its id at position 0, and a table test",
                 id="a literal row whose id is its first value"),
    pytest.param([OTHER_FORM | {"id": {"position": 2}}], "every row is a `checks.case` with its id at position 2, and",
                 id="a row call whose id is its third value"),
    pytest.param([PYTEST_TABLE, OTHER_FORM],
                 "every row is a `pytest.param` with an `id` or a `checks.case` with an `name`, and",
                 id="two forms, said in the order written"),
])
def test_the_guard_line_says_a_row_as_each_form_writes_one(tables, clause):
    assert clause in guard_lines(testing={"tables": tables})[0]
```

**(g) The fixtures that wrote `table`** —
- `tests/modules/spec/profiles.py`: in `TESTING`, replace
  `"table": {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id", "keywords": ["argnames", "argvalues"]},`
  with `"tables": [PYTEST_TABLE],`.
- `tests/modules/spec/application/test_explain.py`: remove the `Shown('testing.table', ...)` line of `SHAPE`.
- `tests/modules/spec/application/logic/test_profile_needs.py`: in `configured`, replace
  `("testing.table", "testing.table")` with `("testing.tables", "testing.tables")`.
- `tests/modules/rules/adapters/test_spec_profile.py`: remove `CaseTable` from the import and the `TABLE = ...` line;
  `ScenarioCoverage("api", "unit", "Result", ("a", "b", "c"), TABLE, "test_{name:snake}.py")` becomes
  `ScenarioCoverage("api", "unit", "Result", ("a", "b", "c"), "test_{name:snake}.py")` (line 55), and the one at lines
  120-121 the same.
- `tests/bootstrap/test_bundled_guards.py`: remove `CaseTable` from the import and the `table = CaseTable(...)` line;
  the guard becomes `ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"),
  "test_{name:snake}.py")` and the framework `Framework(("test_*.py", "*_test.py"), "test_*", tuple(tuple(s.split("."))
  for s in skips), (form,))`.
- `tests/bootstrap/test_profile_file.py`: in both `test_the_preset_holds_exactly_what_the_bundled_profiles_spell_out`
  and `test_xarch_s_own_profile_spells_out_the_same_as_the_preset`, replace the two lines comparing `g.table` with

```python
    assert [g for g in preset.guards if isinstance(g, ScenarioCoverage)] == [
        g for g in spelled.guards if isinstance(g, ScenarioCoverage)]
```

  and the first test's docstring with `"""tests, the forms of a table, and the guards scenario-coverage and
  stand-ins."""`.
- `tests/bootstrap/test_other_framework.py`: delete the line `  table: {decorator: cases.table, row: cases.row, id: name}`,
  leaving exactly

```yaml
  tables: [{decorator: cases.table, columns_from: {position: 0}, rows: {position: 1}, row: cases.row,
            id: {keyword: name}}]
```

- `tests/architecture/test_agnostic.py`: add `Place` to its import from `xarch.profile_values.testing`, and replace
  `dotted = (guard.table.decorator, guard.table.row, tuple(guard.table.keywords or ()))` with

```python
                forms = architecture.framework.tables
                dotted = (*(form.decorator for form in forms), *(form.row for form in forms),
                          *(tuple(place.keyword for place in (form.columns_from, form.rows)
                                  if isinstance(place, Place) and place.keyword) for form in forms))
```

  (the same words as before: the decorator's and the row's steps, and the two keywords `argnames`, `argvalues`).

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/modules/spec tests/modules/rules tests/architecture -q`
Expected: FAIL — among others `TypeError` from `ScenarioCoverage(...)` taking five arguments and
`test_the_table_of_testing_is_refused_with_the_list_of_forms_that_replaces_it` failing because `table` is still read.

- [ ] **Step 3: The values**

In `xarch/profile_values/testing.py`:
- Module docstring: `"""How a project's tests are named and placed, as the profile says it: the test framework's names,
  the table forms it writes, the scenario-coverage and stand-ins guards, and where the fakes live."""`
- Add `from xarch.profile_values.language import Writing` below `from dataclasses import dataclass`.
- `Framework`: remove `table: CaseTable | None = None`; docstring `"""How the project's test framework names things:
  the patterns of a test file's name (matched against the file name alone, `*` for any text) and of a test
  function's, and the dotted names of what skips a test or expects it to fail (a marker or a call; empty: none is
  counted); and the table forms it writes (tables; none: it writes none, and no table is read)."""`
- Delete the class `CaseTable`.
- `ScenarioCoverage`: remove `table: CaseTable`; docstring `"""The guard scenario-coverage: the part holding the result
  unions, the tier holding their tables, how a union's name ends, the names of the three parameters of a table (its
  state, its command and its result, in that order), and the name of a use case's test file, `{name:<case>}` standing
  for the use case in the case it writes."""`
- Add to `RowId`:

```python
    @property
    def name(self) -> str:
        """The keyword or the field that gives the id; "" for an id by position."""
        return self.keyword or self.field

    def written(self, writing: Writing, callee: str, text: str) -> str:
        """The id as the language writes it, text its value: writing's keyword template, callee being what the row
        calls, or its field template; "" for an id by position, which no template writes."""
        if self.keyword:
            return writing.keyword_id(callee, self.keyword, text)
        return writing.field_id(self.field, text) if self.field else ""
```

- [ ] **Step 4: The key table and its texts**

`xarch/modules/spec/domain/profile_keys.py`: delete `TABLE = "testing.table"` and `TABLE: "testing.table",`; append to
`RETIRED`, after the last entry:

```python
    Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
```

`xarch/modules/spec/domain/key_table.py`: remove `TABLE,` from the import, the line
`Key(TESTING, "table", rules=("scenario-coverage",), opens=TABLE),`, the four `Key(TABLE, ...)` lines (and the blank
line after them), and `"testing.table": ("function.tables",),` from `NEEDS`.

`xarch/architectures/presets/format/keys.yaml`:
- Delete the old `table` fragment (`  table: |2`, its `      table:` line and the three below it: four lines of body, up to the line before `  mocks: |2`), then rename the fragment `  tables: |2` to
  `  table: |2`, and replace every `<<tables>>` with `<<table>>` (`sed -i 's/<<tables>>/<<table>>/' keys.yaml`). The
  fragment is now exactly:

```yaml
  table: |2
      tables:
        - decorator: checks.cases
          columns_from: {position: 0, keyword: names}
          rows: {position: 1, keyword: cases}
          row: checks.case
          id: {keyword: id}
```

- Delete the entries `testing.table`, `testing.table.decorator`, `testing.table.row`, `testing.table.id` and
  `testing.table.keywords`.
- `testing.accepts`: `a preset name, or a map {files, functions, skips, table, mocks}` becomes
  `a preset name, or a map {files, functions, skips, tables, mocks}`.
- `tiers.<tier>.plain_tables.accepts`: `(as `testing.table` writes one)` becomes `(as `testing.tables` writes one)` and
  `needs `testing.table`` becomes `needs `testing.tables``; re-wrap at 120 columns.
- `guards.scenario-coverage.accepts`: `every row is a `testing.table.row` call with a `testing.table.id`, and a` becomes
  `every row is written as its form in `testing.tables` writes one, with a literal id, and a`; re-wrap.

`xarch/architectures/presets/testing/pytest.yaml`: delete the `table:` line, and make the header

```
# The test framework pytest, as a profile names it with `testing: pytest`: the same map a profile writes out for another
# framework. How a test file and a test function are named, what skips a test or expects it to fail, the table forms
# it writes, and how a mock is built.
```

- [ ] **Step 5: The parser and its refusals**

`xarch/modules/spec/application/logic/profile_checks.py`: delete `case_table`; remove `TABLE` from the profile_keys
import (keeping `TABLES`) and `CaseTable` from the testing import.

`xarch/modules/spec/application/logic/profile_parsing.py`:
- Import: `from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns`.
- `_Testing`: docstring `"""What `testing` says: how test files and functions are named and the table forms the
  framework writes, and, when written, how a mock is built."""`; fields `framework: Framework` and
  `mocks: StandIns | None` only.
- `_testing`, the end becomes:

```python
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language, TESTING)
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None or tables is None:
        return None
    return _Testing(replace(framework, tables=tables), mocks)
```

- The plain_tables refusal (lines 204-205) becomes:

```python
    problems += [f"tiers.{tier.name}.plain_tables: needs `testing.tables`, the forms a table of cases is written in, "
                 "to know a table test" for tier in tiers
                 if tier.plain_tables and (testing is None or not testing.framework.tables)]
```

- In `_scenario_coverage`, replace

```python
    if testing is not None and testing.table is None:
        problems.append(f"{where}: needs `testing.table`: how a table of cases is written, such as "
                        "{decorator, row, id}")
```

with

```python
    if testing is not None and not testing.framework.tables:
        problems.append(f"{where}: needs `testing.tables`: the forms a table of cases is written in, such as "
                        "[{decorator, columns_from, rows, row, id}]")
```

  (with `testing` absent, `_needs_testing` already refuses the guard; a second line would be a duplicate), and the end:

```python
    if len(problems) != count or columns is None or file is None or testing is None or not testing.framework.tables:
        return None
    return ScenarioCoverage(spec["results"], spec["tier"], spec["suffix"], columns, file)
```

- [ ] **Step 6: The checks word a row from its form and the language**

In `xarch/modules/rules/application/logic/scenarios.py`:

- Replace the docstring lines 6-15 (from `among the files of the table tier ...` through
  `a row without an id or one whose id is not a literal is a violation.`) with:

```
among the files of the table tier in the same instance (see tier_of). That file must hold a table, read from its
syntax tree in one of the forms the framework writes (`testing.tables`; the reader says how each is read), a test
function being one whose name matches the profile's pattern:

    a test function holding a table whose columns include the three the guard is given (state, command, result);
    rows the reader cannot read are a violation, since a table that cannot be read cannot be checked.
    every row is written as its form writes one, with a non-empty string literal as its id: a row written otherwise,
    a row without an id or one whose id is not a literal is a violation, said and fixed in the words of the language
    (its data file's `writing`), as the form of the row's table writes a row.
```

- Below `Problem = ...` and its docstring add:

```python
_OUTCOME = "<a sentence stating the outcome>"
"""What the fix of a row writes as its id's text."""
```

- `_rows` has two callers, `_covered` and `_credited` (which `weak` calls); both pass the profile on.
  In `_covered`, change `_rows(table, union, variants, guard, covered)` to
  `_rows(table, union, variants, guard, profile, covered)`.
  In `weak`, change `_credited(test, union.name, union.members, guard, profile.framework.functions)` to
  `_credited(test, union.name, union.members, guard, profile)`. `_credited`'s signature becomes
  `_credited(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage, profile: Profile)
  -> list[Weak]:`, its first lines
  `assert profile.framework is not None` and
  `functions = [f for f in test.functions if fnmatchcase(f.name, profile.framework.functions)]`, and its call
  `_rows(table, union, variants, guard, covered)` becomes `_rows(table, union, variants, guard, profile, covered)`.
- Replace `_rows`'s signature and its first three lines with:

```python
def _rows(table: Table, union: str, variants: tuple[str, ...], guard: ScenarioCoverage, profile: Profile,
          covered: set[str]) -> list[Problem]:
    assert profile.framework is not None
    form = profile.framework.tables[table.form]
    writing = profile.language.writing
    callee = profile.language.member.join(form.row)
    result = guard.columns[-1]
    given = form.id.written(writing, callee, _OUTCOME)
    case = (f"write {given}" if given else
            f"write the row's id, a sentence stating the outcome, as its value at position {form.id.position}")
    shape = writing.row_call(callee) if form.row else "literal"
```

  and in its loop `problems.append((row.line, f"row is not a {written}(...)", case))` becomes
  `problems.append((row.line, f"row is not a {shape}", case))`.

- [ ] **Step 7: The docs line**

In `xarch/modules/spec/application/logic/docs_template.py`, change the import
`from xarch.profile_values.testing import ScenarioCoverage, StandIns` to
`from xarch.profile_values.testing import ScenarioCoverage, StandIns, TableForm`, replace the `ScenarioCoverage` case
of `_guard_line` with

```python
        case ScenarioCoverage(results, tier, suffix, columns, file):
            assert architecture.framework is not None
            shown = ", ".join(f"`{c}`" for c in columns)
            member = architecture.language.checked.member
            rows = " or ".join(_row_phrase(form, member) for form in architecture.framework.tables)
            return (f"`scenario-coverage`: every variant of a union named `<Name>{suffix}` in "
                    f"`{docs_name(architecture, architecture.parts[results])}` is the `{columns[-1]}` of a row of the "
                    f"table (columns {shown}) in `{_uncased(file)}` among the {tier} tests (section 5.2), "
                    f"or is named by a standalone test of that file; every row is {rows}, and a table test has no "
                    f"{_branches(architecture)}.")
```

and add after `_guard_line`:

```python
def _row_phrase(form: TableForm, member: str) -> str:
    """How the guard line says a row of a form: a `<row>` it calls, or a literal, with an `<id>` or with its id at a
    position."""
    what = f"a `{member.join(form.row)}`" if form.row else "a literal"
    given = f"an `{form.id.name}`" if form.id.name else f"its id at position {form.id.position}"
    return f"{what} with {given}"
```

- [ ] **Step 8: Check that nothing names the old shape**

Run: `grep -rn "CaseTable\|testing\.table\b\|\.table\b" xarch tests --include=*.py | grep -v corpora`
Expected: only `Retired(TESTING, "table", ...)`, test texts that quote the retired key (`test_retired_keys.py`,
`test_profile_file.py`, `test_profile_explain.py`, `test_profile_keys.py`) and matches that are no table of cases
(`cases.table` inside source text, `self.table` in `test_review_placement.py`). Nothing else may match.

- [ ] **Step 9: Run the tests**

Run: `timeout 900 uv run pytest -q tests/modules tests/architecture tests/bootstrap/test_other_framework.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_source_checks.py`
Expected: PASS. `test_docs_templates.py` and `test_recorded_corpora.py` passing is the byte-for-byte proof (T15, T16);
if either fails, the wording code is wrong — never re-record or hand-edit the golden docs or corpora. Then run
`git status docs/` — it must show no change under `docs/cli`, `docs/web`, `docs/xarch`.

- [ ] **Step 10: Commit**

```bash
git add xarch tests
git commit -m "The guard scenario-coverage keeps no copy of the table: the checks and the docs word a row from the form at its table's index and the language's templates, and testing.table is refused with moved in 0.3.0: write tables"
```

---

## Task 5: README and CHANGELOG

**Files:**
- Modify: `README.md:116`
- Modify: `CHANGELOG.md` (under `## [Unreleased]`, top of `### Changed`)
- Test: `tests/architecture/test_readme.py` (existing)

- [ ] **Step 1: README**

Line 116 becomes:

```
testing:  <preset> | {files*, functions*, skips, tables, mocks}
```

- [ ] **Step 2: CHANGELOG**

Under `## [Unreleased]` / `### Changed`, insert as the first entry (above the `{name:snake}` entry):

```markdown
- A framework says how a table of cases is written with `testing.tables`, a list of table forms, each with one of
  `decorator`, `call` or `loop` and the slots `columns_from`, `rows`, `row` and `id`; an entry's problem names it by
  its index, `testing.tables.0.id`. `testing.table` is refused with "moved in 0.3.0: write tables, a list of forms
  (xarch profile explain testing.tables)", and the bundled `pytest` preset writes its one form in the new shape. The
  guard `scenario-coverage` keeps no copy of the table: it reads the framework's forms. A language data file says how
  a row is written with `writing: {call, keyword, field}`; Python writes `call` and `keyword`. Findings and docs read
  as before.
```

- [ ] **Step 3: Run the README test**

Run: `uv run pytest tests/architecture/test_readme.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say testing.tables, the retired testing.table and the language's writing"
```

---

## Task 6: The full gates

- [ ] **Step 1: Start the suite in the background**

Run (background): `timeout 1200 uv run pytest -q > /tmp/xarch-6-3-pytest.log 2>&1; echo "exit $?" >> /tmp/xarch-6-3-pytest.log`
and record the PID it was started with.

- [ ] **Step 2: The other gates, meanwhile**

Run each and expect exit 0 with no finding:
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.
A `--strict` dead-code finding on `TableForm`, `RowId.name`, `RowId.written`, `Writing` and its three filling methods, `PARAMETERS`,
`BOUND`, `FIELDS` or `HOLDERS`/`LITERAL`/`PLACE` means a use was dropped: each is used by production code in Tasks 2-4.

- [ ] **Step 3: Read the suite's result**

Run: `tail -5 /tmp/xarch-6-3-pytest.log`
Expected: all passed and `exit 0`.

- [ ] **Step 4: Confirm the frozen files did not move**

Run: `git diff --stat main -- tests/bootstrap/corpora docs/cli docs/web docs/xarch`
Expected: empty.

- [ ] **Step 5: Commit any gate fix**

Only if a gate needed a fix: `git add <files>` and
`git commit -m "<what the gate found, in the repo's sentence style>"`. Otherwise nothing to commit.

---

## Self-review against the spec

- 3.1 values: Task 2 (Place, RowId, TableForm, Framework.tables), Task 4 (CaseTable, Framework.table and
  ScenarioCoverage.table removed; docstrings). `RowId.written` keeps the kind decision with the value (3.6).
- 3.2 parser and every refusal: Task 2 refusal table, one row per message; the language check (T4) in Task 2.
- 3.3 key table, scopes, NEEDS: Task 2 adds, Task 4 removes the old; RETIRED in Task 4.
- 3.4 refusals: Task 4 (T1, T2, T10); the guard is built without the table (T11).
- 3.5 `writing`: Task 1 (T9).
- 3.6 `_rows` and docs line: Task 4 (T7, T8, T15).
- 3.7 port, service, reader: Task 3 (T5, T6); `runs` stays 0.
- 3.8 keys.yaml: Task 2 (new entries), Task 4 (fragment renamed, old entries removed, plain_tables, guard, testing).
- 3.9 interim: Task 3 pins that call, loop and literal-row decorator forms read no table.
- 3.10 fixtures: Tasks 3 and 4; `test_other_framework.py` ends exactly as the spec writes it.
- 3.11 README, CHANGELOG: Task 5.
- Section 6 gates: Task 6. Deviation noted: the unit row for the literal/position docs phrase lives in
  `test_testing.py`, beside the guard-line helper it needs, not in `test_docs_template.py`; and `writing` is done
  first (Task 1) because the parser's language check of 3.2 reads it.

<!-- task-pipeline: validated -->
