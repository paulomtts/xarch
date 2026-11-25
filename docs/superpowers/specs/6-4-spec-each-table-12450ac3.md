# 6.4 Each table form is held to its own fact: design spec

Card: 12450ac3 (subtask of 15e55316). Release step 19 of the merged order
(`~/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, section 3), split with 6.3 along the note's
steps 3 and 4. Blocked by 6.3 (a99ddd93), which is done on this branch (75db990, 918790c, 551954b, e7334a2, d7e3634).

Parent design: `~/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below, "the note"). This card
implements its section 2.4 (lines 213-229) and item 4 of section 8 (lines 404-405), with the rows of section 6 that
belong to this step (line 336, `python.yaml`; line 342, `profile_needs.py`). The note says steps 3 and 4 are one
release step (lines 413-414).

## 1. Goal

Today one fact, `function.tables` ("the tables of cases of a test function", `xarch/profile_values/capabilities.py:63`),
stands for every table form. `python.yaml:102` supplies it exactly, so a profile whose framework writes a `call` form
loads under Python even though Python's reader cannot read a `call` form.

After this card:

- `FACTS` has three facts in place of `function.tables`: `function.tables.decorator`, `function.tables.call` and
  `function.tables.loop` (note 2.3, lines 164-166; note 2.4, lines 215-216).
- Each holder key of a table form needs its own fact. `testing.tables.decorator` needs `function.tables.decorator`,
  and `call` and `loop` follow the same pattern (note 2.4, lines 216-217).
- The walk of the keys a profile sets goes into each entry of `testing.tables` and names the entry by its index,
  `testing.tables.0.call` (note 2.4, lines 217-221).
- Python's data file supplies `function.tables.decorator` only. A profile whose framework writes a `call` or `loop`
  form under Python is refused. The refusal is the existing needs refusal, with its existing wording (note 2.4, lines
  218-220 and 224-225; note 8, item 4).

For every bundled profile and preset, findings, docs and recorded corpora stay byte for byte. They all write only the
pytest `decorator` form (`xarch/architectures/presets/testing/pytest.yaml:8-13`).

## 2. Inherited constraints

- The refusal of a form the language cannot read is the existing one, `profile_needs.refused`
  (`xarch/modules/spec/application/logic/profile_needs.py:90-95`). This card adds no new message (note 2.4, lines
  218-220; note 8, item 4, line 405).
- Python's reader does not supply `call`. The gap is deliberate: it shows that the refusal works for a form one
  language lacks (note 2.4, lines 224-225). Adding `call` support to the Python reader to make every form "supplied" is
  a named dodge (card).
- `loop` is supplied by Python only once 6.5 builds the loop form in the reader (note 2.4, line 224; note 8, item 5,
  lines 406-407; card: "Out of scope: the loop form (6.5)"). Until then, Python does not supply
  `function.tables.loop`.
- `plain_tables` and the guard `scenario-coverage` need the table facts of every form the framework writes, worked
  out from the list. Their own `NEEDS` entries list `function.blocks`, `function.expressions` and the rest, and the
  table facts come in through `testing.tables`, which a profile must set for those keys to apply (note 2.4, lines
  227-229; note 3.2, lines 276-281).
- The walker is the one release step 11 built (`profile_needs._configured` and `_held`, `profile_needs.py:29-62`). It
  already walks a scope ending in `[]` entry by entry. This card only adds rows, and changes the walker's code only if
  a failing test shows a gap (note 2.4, lines 220-222).
- Fact text is language-neutral. It contains none of `decorat`, `param`, `keyword`, `pytest`, `tuple literal` or
  `list literal` (6.1, `tests/modules/rules/domain/test_parsed.py:41-50`).
- Python appears only in the reader adapter and in the data files under `xarch/architectures/presets/` (note,
  "Rulings", line 13; card). `python.yaml` is such a data file.
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
  - `uv run pytest -q` (over two minutes: run it in the background and read it at the end);
  - `uv run xarch check`;
  - `uv run xarch check --strict`;
  - `uv run ruff check`;
  - `uv run xarch profile check architecture.yaml`.

## 3. Observable behavior

### 3.1 The vocabulary of facts

`FACTS` (`xarch/profile_values/capabilities.py`) no longer holds `function.tables`. In its place, in the same
position, it holds:

| fact | text |
|---|---|
| `function.tables.decorator` | `the tables of cases a mark on a test function's definition holds` |
| `function.tables.call` | `the tables of cases a call that makes or wraps a test function holds` |
| `function.tables.loop` | `the tables of cases a test function's body runs through in a loop` |

Each text contains no Python word (section 2). `profile explain` shows each text, and so does a refusal of a fact the
language does not supply.

A language data file that still writes `function.tables` under `supplies` is refused with the existing unknown-fact
problem of `language_file._supplies` (`xarch/modules/spec/application/logic/language_file.py:443-444`): `supplies:
'function.tables' is not a fact a check reads: use <every fact, sorted>`. The list it prints includes the three new
facts. There is no special hint for the old name. Language files are not a user-facing format with a retired-keys
table, and the only one that exists is bundled and changes in this card.

### 3.2 What Python supplies

The `supplies` block of `xarch/architectures/presets/language/python.yaml` has `function.tables.decorator: exact` in
place of `function.tables: exact`. It does not list `function.tables.call` or `function.tables.loop`. Python's reader
therefore supplies every fact exactly except those two (6.5 adds `loop`).

### 3.3 What each key needs

`NEEDS` (`xarch/modules/spec/domain/key_table.py:227-277`):

| address | needs before | needs after |
|---|---|---|
| `testing.tables` | `function.tables` | nothing (the entry is dropped) |
| `testing.tables.decorator` | nothing | `function.tables.decorator` |
| `testing.tables.call` | nothing | `function.tables.call` |
| `testing.tables.loop` | nothing | `function.tables.loop` |
| `tiers.<tier>.plain_tables` | `function.tables`, `function.blocks`, `function.expressions` | `function.blocks`, `function.expressions` |
| `guards.scenario-coverage` | `union`, `function.tables`, `function.blocks`, `function.expressions`, `function.asserts`, `function.mentions` | `union`, `function.blocks`, `function.expressions`, `function.asserts`, `function.mentions` |

No other key's needs change. `columns_from`, `rows`, `row` and `id` need nothing: an entry's slots are read by the
check of its holder.

`xarch profile explain` shows the new needs:

- `testing.tables.call` prints `needs: function.tables.call: the facts of the source its check reads; Python supplies
  not function.tables.call`. In its JSON, `needs` has one entry `{"fact": "function.tables.call", "meaning": <its
  text>, "grade": "absent"}` (the value of `ABSENT`).
- `testing.tables.decorator` prints that Python supplies it exactly.
- `testing.tables` prints no `needs:` line.
- `tiers.<tier>.plain_tables` and `guards.scenario-coverage` print their needs without any table fact.

### 3.4 Refusal of a form the language cannot read

A profile loads (`profile check`, `check`, and every command that loads a profile). If its framework, written inline
or as the name of a testing preset, writes an entry of `testing.tables` whose holder needs a fact the language does not
supply, the profile is refused with one problem per such entry. The problem uses the existing wording, with the entry's
index:

```
<file>: testing.tables.<i>.<holder>: its check reads function.tables.<holder> (<text of the fact>), which the language <name> does not supply: drop testing.tables.<i>.<holder>, or check the app with a language whose reader supplies function.tables.<holder>
```

Concretely, under Python, a framework with `tables: [{call: [checks.each], columns_from: {position: 0}, rows:
{position: 1}}]` is refused with:

```
layered.yaml: testing.tables.0.call: its check reads function.tables.call (the tables of cases a call that makes or wraps a test function holds), which the language python does not supply: drop testing.tables.0.call, or check the app with a language whose reader supplies function.tables.call
```

- The index counts every entry from 0, including entries that are refused for other reasons and entries that are not
  mappings (`_held`, `profile_needs.py:50-52`). A call form written second, after the pytest form, is refused at
  `testing.tables.1.call`. The pytest entry is not refused.
- A `decorator` form under Python is not refused.
- A `loop` form under Python is refused at `testing.tables.<i>.loop`, with `function.tables.loop`, until 6.5.
- A holder written as `null` or `false` configures nothing, so it adds no needs problem (`profile_needs.py:36-38`).
  Whatever 6.3's form loader says about such an entry, it still says.
- No problem is ever addressed at a bare `testing.tables` for a missing table fact.
- `plain_tables` and `scenario-coverage` add no table-fact problem of their own. Take a language that supplies none of
  the three table facts, and a profile that sets `plain_tables`, the guard and one decorator form. It gets exactly one
  table-fact problem, at `testing.tables.0.decorator`.
- A partly supplied table fact (a language grading it `{partial: ...}`) is not refused. The holder is listed under
  `approximate` at `testing.tables.<i>.<holder>`, as for any key (`profile_needs.approximate`).

### 3.5 What does not change

- The bundled profiles `cli`, `web` and `xarch`, `architecture.yaml` and the `pytest` preset load and check as before.
  Their findings, the golden docs and the recorded corpora under `tests/bootstrap/corpora/` stay byte for byte.
- The rules side (`xarch/modules/rules/application/logic/scenarios.py`) is untouched. It reads `Table.form` to index
  the framework's forms and never names a fact.
- `tests/bootstrap/test_needs_agree.py` stays green unchanged. Its `EVERY_KEY` profile sets `testing: pytest`, whose
  one entry is a decorator form that Python supplies. If it fails, that is a finding to diagnose, not a test to edit.

### 3.6 Docs

- CHANGELOG, under `## [Unreleased]` / `### Changed`: the bullet that says the description of `function.tables` reads
  "the tables of cases of a test function" (`CHANGELOG.md:100-101`, written by 6.1 in this same unreleased version)
  is replaced. The new bullet says that:
  - the fact `function.tables` is now three facts, one per form: `function.tables.decorator`, `function.tables.call`
    and `function.tables.loop`;
  - each holder of an entry of `testing.tables` needs its own fact, and is refused at its index
    (`testing.tables.0.call: its check reads function.tables.call ...`) when the language does not supply it;
  - Python supplies `function.tables.decorator` and not `call` or `loop`;
  - a language file writing `function.tables` under `supplies` is refused as an unknown fact.
- README: two sentences say "Python's reader supplies every fact exactly" (`README.md:179-180` and `README.md:509`).
  Both become false, so both say it supplies every fact exactly except `function.tables.call` and
  `function.tables.loop`. The first also says that a framework writing a `call` or `loop` form under Python is refused
  at that entry. The second says that a Python project never sees the `approximate` line, which stays true because
  nothing is partly supplied. Neither sentence gets any other edit.
- Golden docs: regenerated, the diff read, and no change expected. None of them names `function.tables`.

## 4. Tests

The tiers follow the repository's layout:

- unit: `tests/modules/...`, which runs the logic on hand-built values;
- wired: `tests/bootstrap/...`, which drives the CLI app and the bundled files.

Every new or changed test is written first and seen to fail.

| # | Test | Tier, file | Why this tier |
|---|---|---|---|
| T1 | Under Python, a framework whose one form is `call` is refused with exactly the message of 3.4 at `testing.tables.0.call` | unit, `tests/modules/spec/application/logic/test_profile_needs.py` (via `problems(layered(testing=...))`) | The card's named test. It is the needs walk plus the refusal text, both pure logic |
| T2 | Under Python, a framework whose one form is `PYTEST_TABLE` has no problems | unit, same file | It pins that `decorator` is supplied, the other half of T1 |
| T3 | Under Python, a `loop` form is refused at `testing.tables.0.loop` with `function.tables.loop` | unit, same file | It pins that loop is not supplied before 6.5 (6.5 flips this test) |
| T4 | Under Python, `tables: [PYTEST_TABLE, <call form>]` gives one table-fact problem, at `testing.tables.1.call`, and none at `testing.tables.0.*` | unit, same file | It pins the walk into list entries and the index |
| T5 | Rewrite of `test_the_forms_of_a_table_need_the_tables_of_cases_of_a_test_function` (`:543-547`): under `toy`, a `PYTEST_TABLE` form is refused at `testing.tables.0.decorator` with `function.tables.decorator` and its text, and no problem starts `layered.yaml: testing.tables: its check reads` | unit, same file | The old expectation names a fact that no longer exists |
| T6 | Under a language that supplies every fact except the three table facts, a profile setting `tiers.<tier>.plain_tables`, `guards.scenario-coverage` and one decorator form has exactly one problem naming a `function.tables.*` fact, at `testing.tables.0.decorator` | unit, same file | It pins note 2.4's "the table facts come in through `testing.tables`" |
| T7 | Under a language grading `function.tables.decorator` partly, the decorator form loads and is approximate at `testing.tables.0.decorator` | unit, same file | It covers the partial path for a list entry |
| T8 | Update of `test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once` (`:133-151`): `configured` has `("testing.tables.0.decorator", "testing.tables.decorator")` in place of `("testing.tables", "testing.tables")` | unit, same file | The walk through a preset into list entries, at its new address |
| T9 | Update of `test_python_supplies_every_fact_a_bundled_check_reads` (`:129-130`): Python supplies every fact of `FACTS` exactly except `function.tables.call` and `function.tables.loop` | unit, same file | It pins 3.2. 6.5 drops `loop` from the exception |
| T10 | `FACTS` has no `function.tables`. Each of the three facts has the text of 3.1, and none of the three texts holds a Python word. This replaces the parametrized row and `test_the_fact_of_tables_reads_...` at `test_parsed.py:47,53-54` | unit, `tests/modules/rules/domain/test_parsed.py` | It is the vocabulary of facts and its neutrality |
| T11 | A language data file with `function.tables: exact` under `supplies` is refused with `supplies: 'function.tables' is not a fact a check reads: use ...`, and the list names `function.tables.call` | unit, the existing language-file tests next to `language_file.py` (`tests/modules/spec/application/logic/test_language_file.py`) | It pins that the old fact is not silently accepted |
| T12 | `xarch profile explain testing.tables.call --format json` gives `needs == [{"fact": "function.tables.call", "meaning": FACTS[...], "grade": "absent"}]`. The text form holds `Python supplies not function.tables.call`. `xarch profile explain testing.tables --format json` has an empty `needs` | wired, `tests/bootstrap/test_profile_explain.py` | It is what a user sees through the CLI, with the bundled Python file |
| T13 | Existing suites stay green unchanged: `test_needs_agree.py`, `test_docs_templates.py` (golden docs byte for byte), the corpora tests and the bundled-profile checks | wired, existing | They prove 3.5 |

The existing parametrized `test_a_key_needs_only_facts_of_the_vocabulary_of_facts` (`test_profile_needs.py:159`)
covers the three new `NEEDS` rows with no edit.

## 5. Out of scope

- The loop form in the Python reader, `Table.runs` honoured by `_branches`, and `python.yaml` supplying
  `function.tables.loop`: card 6.5 (note 8, item 5).
- Any `call` support in the Python reader (a named dodge).
- A framework with no form: the guard's standalone path, `columns` refused with no form, and `plain_tables` refused
  with no form, "needs a table form: the framework `<name>` writes none in `testing.tables`": card 6.6 (note 8, item 6;
  note 3).
- The second frameworks of note section 9, and `profile explain` texts beyond the needs lines: step 7 of note 8.
- A retired-name hint for `function.tables` in language data files (3.1).
- Any change to the form loader of 6.3, `keys.yaml` texts, the `writing` templates, the rules side, the recorded
  corpora, the golden docs or the bundled profiles.

## 6. Files the work touches

- `xarch/profile_values/capabilities.py`: `FACTS`.
- `xarch/architectures/presets/language/python.yaml`: `supplies`.
- `xarch/modules/spec/domain/key_table.py`: `NEEDS`.
- `xarch/modules/spec/application/logic/profile_needs.py`: only if T1 or T4 fails for a reason other than the
  missing `NEEDS` rows. The module docstring already says it walks list entries.
- Tests:
  - `tests/modules/spec/application/logic/test_profile_needs.py`;
  - `tests/modules/rules/domain/test_parsed.py`;
  - `tests/modules/spec/application/logic/test_language_file.py` (T11);
  - `tests/bootstrap/test_profile_explain.py`.
- `CHANGELOG.md` and `README.md`, as in 3.6.

## 7. Review focus for the planner

These are input classes the spec implies and that are easy to miss:

- An entry that writes two holders, for example `decorator` and `call`. 6.3's loader refuses it. The needs walk may
  also refuse the unsupplied holder. Both problems are acceptable, and neither may crash.
- An entry that is not a mapping, for example a string. The needs walk skips it but still counts its index, so a later
  entry keeps its true index.
- `testing` written as the name of a preset whose form is `call`. The refusal is still addressed
  `testing.tables.<i>.call`, as T8 pins for the walk through a preset.
- `tables: []`, or `tables` left out. There are no table-fact problems (6.6 owns what else is said).
- Message wording: `refused` prints `language.name` (`python`), not the title (`Python`). The note's quotation
  "language Python" is illustrative, and the existing message is kept as is.
