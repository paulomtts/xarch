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
