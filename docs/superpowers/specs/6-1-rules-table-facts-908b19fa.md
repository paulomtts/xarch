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
