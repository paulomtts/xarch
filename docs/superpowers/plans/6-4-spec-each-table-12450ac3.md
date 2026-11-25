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

---

# 6.4 Each table form is held to its own fact: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the fact `function.tables` into `function.tables.decorator`, `function.tables.call` and `function.tables.loop`. Each holder of an entry of `testing.tables` needs its own fact. Python supplies the decorator fact only, so a `call` or `loop` form under Python is refused at `testing.tables.<i>.<holder>` with the existing needs refusal.

**Architecture:** The work is data in three places: `FACTS` (`xarch/profile_values/capabilities.py`), the `supplies` block of `python.yaml`, and `NEEDS` (`xarch/modules/spec/domain/key_table.py`). Release step 11 built the needs walker (`profile_needs._configured`/`_held`), and it already walks into list entries by index. A prototype of this exact change showed that it needs no code change. Tests that exercise the *form loader* with `call`/`loop` forms under Python now hit the needs refusal. They move to a test-only "Python reading every fact" language first, so they keep testing the loader alone.

**Tech Stack:** Python 3.13, pytest, uv, ruff, YAML data files.

**Spec:** `docs/superpowers/specs/6-4-spec-each-table-12450ac3.md` (prepended in full above this plan).

## Global Constraints

- No comments in xarch's code, only docstrings (this holds for test files too: no `#` comments).
- Never run `ruff --fix`.
- Tests are written first and seen to fail.
- Fact text is language-neutral. It contains none of `decorat`, `param`, `keyword`, `pytest`, `tuple literal`, `list literal`.
- Python appears only in the reader adapter and in the data files under `xarch/architectures/presets/`.
- The refusal is the existing `profile_needs.refused` with its existing wording. It prints `language.name` (`python`), not the title. Add no new message.
- No `call` support in the Python reader. No loop support (that is 6.5).
- Recorded corpora under `tests/bootstrap/corpora/`, the golden docs `docs/{cli,web,xarch}/testing.md`, `keys.yaml`, the `writing` templates, the rules side and the bundled profiles are not edited.
- README and CHANGELOG lines go under `## [Unreleased]`.
- `.claude/` stays out of commits. Nothing is pushed.
- Line length is 140 (`ruff.toml`).
- Gates, each passing on this branch with the full suite green: `uv run pytest -q` (over two minutes: run it in the background), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## Facts the spec gets slightly wrong (verified by prototype; follow these)

1. **The table keys' addresses carry `[]`.** `Key(TABLES, "decorator").address` is `testing.tables[].decorator`, not `testing.tables.decorator`. You can confirm this with `uv run python -c "from xarch.modules.spec.domain.key_table import KEYS; print([k.address for k in KEYS if 'tables' in k.address])"`. `profile explain` shows it as `testing.tables.decorator` (its plain address), but `NEEDS` is looked up by `key.address`. So the `NEEDS` rows are `"testing.tables[].decorator"`, `"testing.tables[].call"` and `"testing.tables[].loop"`. A row keyed `"testing.tables.decorator"` silently matches no key. T8's second tuple element is likewise `"testing.tables[].decorator"`.
2. **The JSON `needs` entry also carries `"note": None`.** `profile_report.key_document` always writes `note`. So T12 expects `[{"fact": "function.tables.call", "meaning": FACTS["function.tables.call"], "grade": "absent", "note": None}]`.
3. **Two more test files break, beyond those the spec lists.** `tests/modules/spec/application/logic/test_testing.py` has 8 failures: the form-loader tests that parse `CALL`/`LOOP` under Python. `tests/modules/spec/application/logic/test_profile_keys.py` has 2: the keys.yaml examples of `testing.tables.call` and `testing.tables.loop` no longer load under Python. They are not wrong. They test the loader, not the language. Task 1 moves them to a language that reads every fact, before the behaviour changes.
4. `tests/bootstrap/test_needs_agree.py` is unaffected. `testing.tables*` expands to no engine rule in `EVERY_KEY`, so it is filtered out. Full bootstrap, architecture, kernel, platform and profile_values suites passed in the prototype.

## Review Focus

1. **An entry with two holders** (`decorator` and `call`) under Python must give both the loader's "must have exactly one of decorator, call or loop" and the needs refusal at `testing.tables.0.call`, with no crash. The test is in Task 2 (`test_an_entry_with_two_holders_is_refused_by_the_form_loader_and_for_the_holder_python_does_not_read`).
2. **A non-mapping entry before a call form** must not shift the index. `["x", CALL]` is refused at `testing.tables.1.call`, beside the loader's problem at `testing.tables.0`. The test is in Task 2 (`test_an_entry_that_is_no_mapping_still_counts_so_a_later_call_form_keeps_its_index`).
3. **`testing` written as the name of a preset whose form is `call`** must be refused at `testing.tables.0.call`. The test is in Task 2 (`test_a_call_form_written_in_a_testing_preset_is_refused_at_its_index`).
4. **`tables: []` or `tables` left out** gives no table-fact problem, and the profile loads. The test is in Task 2 (`test_a_framework_that_writes_no_form_needs_no_table_fact`).
5. **A holder written as `null`** configures nothing, so it adds no needs problem. The loader's own problems are unchanged. The test is in Task 2 (`test_a_holder_written_as_null_adds_no_table_fact_problem`).

---

### Task 1: The form loader's tests read under a language whose reader supplies every fact

No behaviour changes. This task only makes the tests of the form loader and of the keys.yaml examples independent of which table facts Python's reader supplies. Every test passes before and after this task. Its "failing test" is the prototype result in point 3 above, which is shown failing in Task 2, Step 6 if this task is skipped.

**Files:**
- Modify: `tests/modules/spec/languages.py` (imports at lines 15-17; append after `PERCENT`, the last line)
- Modify: `tests/modules/spec/application/logic/test_testing.py:8` (import), `:410` (`TOY`), `:420-424` (`test_the_forms_of_a_table_are_read_each_in_its_slots`), `:484-485` (`test_a_bad_table_form_is_refused`)
- Modify: `tests/modules/spec/application/logic/test_profile_keys.py:9` (import), `:63-64` (`load`)

**Interfaces:**
- Produces: `tests.modules.spec.languages.READS_EVERY_FACT: Language`. It is `PYTHON` (name `python`, title `Python`) whose `checked.supplies` is `Supply(fact, EXACT)` for every fact of `FACTS`.

- [ ] **Step 1: Add `READS_EVERY_FACT` to the test languages**

In `tests/modules/spec/languages.py`, add this import after `from tests.fakes.runtime import FakeRuntime`, keeping the `xarch` imports sorted:

```python
from tests.fakes.runtime import FakeRuntime
from xarch.modules.spec.application.logic.language_file import language_of
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
```

Append at the end of the file:

```python
READS_EVERY_FACT = replace(PYTHON, checked=replace(PYTHON.checked, supplies=tuple(Supply(fact, EXACT) for fact in FACTS)))
"""Python, its reader supplying every fact exactly, the forms of a table its own reader does not read included: for the
tests of what the loader reads of a profile, not of what the language's reader reads."""
```

- [ ] **Step 2: Move the form loader's tests to it**

In `tests/modules/spec/application/logic/test_testing.py`:

Change line 8 from

```python
from tests.modules.spec.languages import BRACE, PYTHON
```

to

```python
from tests.modules.spec.languages import BRACE, PYTHON, READS_EVERY_FACT
```

Replace lines 410-411:

```python
TOY = replace(PYTHON, checked=replace(PYTHON.checked, title="Toy", writing=Writing()))
"""Python as a language whose data file writes no template: it cannot say a row."""
```

with

```python
EVERY_FORM = {"python": READS_EVERY_FACT}
"""The languages of a profile whose forms the loader is tested on, Python's reader read as supplying every form."""
TOY = replace(READS_EVERY_FACT, checked=replace(READS_EVERY_FACT.checked, title="Toy", writing=Writing()))
"""Python, reading every form, as a language whose data file writes no template: it cannot say a row."""
```

Replace `test_the_forms_of_a_table_are_read_each_in_its_slots` (lines 420-424) with:

```python
def test_the_forms_of_a_table_are_read_each_in_its_slots():
    assert parsed(with_tables([PYTEST_TABLE])).framework.tables == (PYTEST_FORM,)
    assert parsed(with_tables([CALL, LOOP]), languages=EVERY_FORM).framework.tables == (
        TableForm(Place(0), Place(1), ("checks", "case"), RowId(keyword="id"), call=(("checks", "each"),)),
        TableForm("bound", None, (), RowId(position=0), loop=True))
```

Replace the body of `test_a_bad_table_form_is_refused` (lines 484-485):

```python
def test_a_bad_table_form_is_refused(tables, expected):
    assert problems(with_tables(tables), languages=EVERY_FORM) == [expected]
```

`test_an_id_by_position_needs_no_template` needs no edit: it uses `TOY`, which now reads every form.

- [ ] **Step 3: Load the keys.yaml examples under it**

In `tests/modules/spec/application/logic/test_profile_keys.py`, change line 9 from

```python
from tests.modules.spec.languages import BRACE, PERCENT, PYTHON
```

to

```python
from tests.modules.spec.languages import BRACE, PERCENT, PYTHON, READS_EVERY_FACT
```

Replace `load` (lines 63-64):

```python
def load(document: dict):
    """The document parsed under Python, its reader read as supplying every fact: an example shows its key loading,
    whatever Python's own reader reads."""
    return parsed(document, bundled=BUNDLED, folders=every_folder(document), languages={"python": READS_EVERY_FACT})
```

- [ ] **Step 4: Run the touched suites and see them pass**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_keys.py`
Expected: PASS, every test. This step changes no behaviour.

Run: `uv run ruff check tests/modules/spec`
Expected: `All checks passed!`

- [ ] **Step 5: Commit**

```bash
git add tests/modules/spec/languages.py tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_keys.py
git commit -m "The tests of the table form loader and of the keys' examples read under Python supplying every fact, so they test the loader, not what Python's reader reads"
```

---

### Task 2: One fact per table form, Python supplying the decorator one, and each holder held to its own fact

**Files:**
- Modify: `xarch/profile_values/capabilities.py:63` (`FACTS`)
- Modify: `xarch/architectures/presets/language/python.yaml:102` (`supplies`)
- Modify: `xarch/modules/spec/domain/key_table.py:254, 258, 260-261` (`NEEDS`)
- Not modified: `xarch/modules/spec/application/logic/profile_needs.py`. The prototype showed the walker already yields `testing.tables.<i>.<holder>`. Touch it only if Step 6 shows a T1/T4 failure that the `NEEDS` rows do not explain.
- Test: `tests/modules/rules/domain/test_parsed.py:41-54`
- Test: `tests/modules/spec/application/logic/test_language_file.py` (import at line 14; new test after line 198)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py:129-130, 133-151, 543-547`, plus new tests at the end
- Test: `tests/bootstrap/test_profile_explain.py` (new tests at the end)

**Interfaces:**
- Consumes: `READS_EVERY_FACT` (Task 1). Not used here directly, but Task 1 must be in place or 10 loader tests fail in Step 6.
- Produces: `FACTS["function.tables.decorator"]`, `FACTS["function.tables.call"]` and `FACTS["function.tables.loop"]`, and no `FACTS["function.tables"]`. The `NEEDS` rows are `"testing.tables[].decorator": ("function.tables.decorator",)`, `"testing.tables[].call": ("function.tables.call",)` and `"testing.tables[].loop": ("function.tables.loop",)`. The `"testing.tables"` row is gone.

- [ ] **Step 1: Write the failing test of the vocabulary of facts (T10)**

In `tests/modules/rules/domain/test_parsed.py`, replace lines 44-54. That is the parametrized neutrality test from `@pytest.mark.parametrize("text", [` through the end of `test_the_fact_of_tables_reads_the_tables_of_cases_of_a_test_function`. The new text:

```python
TABLE_FACTS = {
    "function.tables.decorator": "the tables of cases a mark on a test function's definition holds",
    "function.tables.call": "the tables of cases a call that makes or wraps a test function holds",
    "function.tables.loop": "the tables of cases a test function's body runs through in a loop",
}
"""The facts of the tables of cases, one per form a table is written in, and what each is."""


@pytest.mark.parametrize("text", [
    pytest.param(Row.__doc__, id="the docstring of a row"),
    pytest.param(Table.__doc__, id="the docstring of a table"),
    *(pytest.param(FACTS[fact], id=f"the text of the fact {fact}") for fact in TABLE_FACTS),
])
def test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python(text):
    assert [word for word in PYTHON_WORDS if word in text.lower()] == []


def test_the_fact_of_tables_is_one_fact_per_form_each_saying_where_the_table_is_held():
    assert "function.tables" not in FACTS
    assert {fact: FACTS.get(fact) for fact in TABLE_FACTS} == TABLE_FACTS
```

- [ ] **Step 2: Write the failing test of the old fact in a language file (T11)**

In `tests/modules/spec/application/logic/test_language_file.py`, change line 14 from

```python
from xarch.profile_values.capabilities import EXACT, Supply
```

to

```python
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
```

After `test_a_supply_that_is_not_what_the_key_takes_is_a_problem` (it ends at line 198), add:

```python
def test_a_data_file_that_supplies_the_fact_of_tables_split_by_form_is_refused_as_supplying_an_unknown_fact():
    assert refused(DOCUMENT | {"supplies": {"function.tables": "exact"}}) == [
        f"supplies: 'function.tables' is not a fact a check reads: use {', '.join(sorted(FACTS))}"]
    assert "function.tables.call" in sorted(FACTS)
```

- [ ] **Step 3: Write the failing tests of what Python supplies and what each key needs (T9, T8, T5, the NEEDS rows)**

In `tests/modules/spec/application/logic/test_profile_needs.py`:

Replace `test_python_supplies_every_fact_a_bundled_check_reads` (lines 129-130) with:

```python
def test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call_and_of_a_loop():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {
        fact: EXACT for fact in FACTS if fact not in ("function.tables.call", "function.tables.loop")}
```

In `test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once` (lines 133-151), change the first line of `configured` from

```python
    configured = [("testing.skips", "testing.skips"), ("testing.tables", "testing.tables"),
```

to

```python
    configured = [("testing.skips", "testing.skips"), ("testing.tables.0.decorator", "testing.tables[].decorator"),
```

Leave everything else in that test as it is.

Replace `test_the_forms_of_a_table_need_the_tables_of_cases_of_a_test_function` (lines 543-547, the end of the file) with the T5 rewrite below. Then append the new helpers and tests after it:

```python
def test_a_decorator_form_needs_the_tables_of_cases_a_mark_holds_at_its_index_and_testing_tables_needs_none():
    document = layered(language="toy", testing={"files": ["test_*.py"], "functions": "test_*", "tables": [PYTEST_TABLE]})
    found = problems(document, languages=LANGUAGES)
    assert refusal("testing.tables.0.decorator", "function.tables.decorator") in found
    assert [problem for problem in found if problem.startswith("layered.yaml: testing.tables: its check reads")] == []


def test_each_holder_of_a_table_form_needs_its_own_fact_and_the_keys_that_read_tables_need_no_table_fact():
    needs = {key.address: key.needs for key in KEYS}
    assert {address: needs[address] for address in (
        "testing.tables", "testing.tables[].decorator", "testing.tables[].call", "testing.tables[].loop",
        "testing.tables[].columns_from", "testing.tables[].rows", "testing.tables[].row", "testing.tables[].id")} == {
        "testing.tables": (), "testing.tables[].decorator": ("function.tables.decorator",),
        "testing.tables[].call": ("function.tables.call",), "testing.tables[].loop": ("function.tables.loop",),
        "testing.tables[].columns_from": (), "testing.tables[].rows": (), "testing.tables[].row": (),
        "testing.tables[].id": ()}
    assert needs["tiers.<tier>.plain_tables"] == ("function.blocks", "function.expressions")
    assert needs["guards.scenario-coverage"] == ("union", "function.blocks", "function.expressions", "function.asserts",
                                                 "function.mentions")
```

- [ ] **Step 4: Write the failing tests of the refusal of a form the language cannot read (T1-T4, T6, T7, Review Focus 1-5)**

Append to the end of `tests/modules/spec/application/logic/test_profile_needs.py`:

```python
FILES = {"files": ["test_*.py"], "functions": "test_*"}
CALL_FORM = {"call": ["checks.each"], "columns_from": {"position": 0}, "rows": {"position": 1}, "row": "checks.case",
             "id": {"keyword": "id"}}
"""A form whose rows a call that makes the test holds."""
LOOP_FORM = {"loop": True, "columns_from": "bound", "row": "literal", "id": {"position": 0}}
"""A form whose rows a loop of the test's body runs."""
SCENARIO = {"results": "api", "tier": "integration", "suffix": "Result", "columns": ["given", "when", "then"],
            "file": "test_{name:snake}.py"}
UNTABLED = replace(PYTHON, checked=replace(PYTHON.checked, title="Untabled", supplies=tuple(
    Supply(fact, EXACT) for fact in FACTS if not fact.startswith("function.tables."))))
"""Python, its reader supplying every fact but the tables of cases of every form."""
LOOP_MISSED = "a table built in a loop is not read"
LOOSE = replace(PYTHON, checked=replace(PYTHON.checked, supplies=tuple(
    Supply(supply.fact, PARTIAL, LOOP_MISSED) if supply.fact == "function.tables.decorator" else supply
    for supply in PYTHON.checked.supplies)))
"""Python, its reader supplying the tables a mark holds only partly."""


def framed(*tables) -> dict:
    """layered(), its framework writing the forms given."""
    return layered(testing=FILES | {"tables": list(tables)})


def unread(index: int, holder: str) -> str:
    """The refusal of the holder of the entry at the index, under Python, which does not read its form."""
    fact, address = f"function.tables.{holder}", f"testing.tables.{index}.{holder}"
    return (f"layered.yaml: {address}: its check reads {fact} ({FACTS[fact]}), which the language python does not "
            f"supply: drop {address}, or check the app with a language whose reader supplies {fact}")


def test_a_call_form_under_python_is_refused_at_its_index_for_the_tables_of_cases_a_call_holds():
    assert problems(framed(CALL_FORM)) == [
        "layered.yaml: testing.tables.0.call: its check reads function.tables.call (the tables of cases a call that "
        "makes or wraps a test function holds), which the language python does not supply: drop testing.tables.0.call, "
        "or check the app with a language whose reader supplies function.tables.call"]


def test_a_decorator_form_under_python_loads():
    assert parsed(framed(PYTEST_TABLE)).approximate == ()


def test_a_loop_form_under_python_is_refused_at_its_index_for_the_tables_of_cases_a_loop_runs():
    assert problems(framed(LOOP_FORM)) == [unread(0, "loop")]


def test_a_call_form_written_after_the_decorator_form_is_refused_at_its_own_index_and_the_decorator_form_is_not():
    found = problems(framed(PYTEST_TABLE, CALL_FORM))
    assert found == [unread(1, "call")]
    assert [problem for problem in found if problem.startswith("layered.yaml: testing.tables.0.")] == []


def test_the_keys_that_read_tables_add_no_table_fact_of_their_own_beside_the_form_that_needs_it():
    document = covered(guards={"scenario-coverage": SCENARIO})
    document["tiers"]["unit"]["plain_tables"] = True
    assert problems(document, languages={"python": UNTABLED}) == [unread(0, "decorator")]


def test_a_form_whose_tables_the_language_supplies_partly_loads_and_is_approximate_at_its_index():
    assert parsed(covered(), languages={"python": LOOSE}).approximate == (
        Shortfall("testing.tables.0.decorator", "function.tables.decorator", LOOP_MISSED),)


def test_an_entry_with_two_holders_is_refused_by_the_form_loader_and_for_the_holder_python_does_not_read():
    assert sorted(problems(framed(PYTEST_TABLE | {"call": ["checks.each"]}))) == sorted([
        unread(0, "call"), "layered.yaml: testing.tables.0: must have exactly one of decorator, call or loop"])


def test_an_entry_that_is_no_mapping_still_counts_so_a_later_call_form_keeps_its_index():
    assert sorted(problems(framed("pytest.mark.parametrize", CALL_FORM))) == sorted([
        unread(1, "call"), "layered.yaml: testing.tables.0: must be a mapping with one of decorator, call or loop"])


def test_a_call_form_written_in_a_testing_preset_is_refused_at_its_index():
    assert problems(layered(testing="each"), presets={"each": FILES | {"tables": [CALL_FORM]}}) == [unread(0, "call")]


@pytest.mark.parametrize("testing", [pytest.param(FILES | {"tables": []}, id="an empty list of forms"),
                                     pytest.param(FILES, id="no tables")])
def test_a_framework_that_writes_no_form_needs_no_table_fact(testing):
    assert parsed(layered(testing=testing)).framework.tables == ()


def test_a_holder_written_as_null_adds_no_table_fact_problem():
    found = problems(framed(PYTEST_TABLE | {"call": None}))
    assert found and [problem for problem in found if "function.tables" in problem] == []
```

Check that the names used are already imported at the top of the file: `replace`, `pytest`, `PYTHON`, `PYTEST_TABLE`, `covered`, `layered`, `parsed`, `problems`, `PARTIAL`, `KEYS`, `EXACT`, `FACTS`, `Shortfall` and `Supply`. They all are (lines 1-14). `refusal` and `LANGUAGES` are the module's own (lines 18, 61-63). None of the new names (`FILES`, `CALL_FORM`, `LOOP_FORM`, `SCENARIO`, `UNTABLED`, `LOOP_MISSED`, `LOOSE`, `framed`, `unread`) exists in the file yet. Confirm with `grep -nE "^(FILES|CALL_FORM|LOOP_FORM|SCENARIO|UNTABLED|LOOP_MISSED|LOOSE) |^def (framed|unread)" tests/modules/spec/application/logic/test_profile_needs.py`, which must print nothing before you append.

- [ ] **Step 5: Write the failing wired test of `profile explain` (T12)**

Append to `tests/bootstrap/test_profile_explain.py` (`json`, `runner` and `app` are already there), and add `from xarch.profile_values.capabilities import FACTS` to the imports after `from xarch.modules.spec.domain.profile_keys import PART`:

```python
def test_a_holder_of_a_table_form_says_the_fact_of_its_form_and_whether_python_supplies_it():
    call = json.loads(runner.invoke(app, ["profile", "explain", "testing.tables.call", "--format", "json"]).output)
    assert call["needs"] == [{"fact": "function.tables.call", "meaning": FACTS["function.tables.call"], "grade": "absent",
                              "note": None}]
    text = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.call"]).output.split())
    assert ("needs: function.tables.call: the facts of the source its check reads; Python supplies not "
            "function.tables.call") in text
    decorator = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.decorator"]).output.split())
    assert ("needs: function.tables.decorator: the facts of the source its check reads, which Python supplies "
            "exactly") in decorator


def test_the_list_of_table_forms_needs_no_fact_of_its_own():
    found = runner.invoke(app, ["profile", "explain", "testing.tables", "--format", "json"])
    assert json.loads(found.output)["needs"] == []
    text = runner.invoke(app, ["profile", "explain", "testing.tables"]).output
    assert not any(line.startswith("  needs:") for line in text.splitlines())
```

- [ ] **Step 6: Run the new tests and see them fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/domain/test_parsed.py tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py`

Expected:
- `test_parsed.py`: collection ERROR, `KeyError: 'function.tables.decorator'`.
- `test_language_file.py::test_a_data_file_that_supplies_the_fact_of_tables_split_by_form_...`: FAIL, `DID NOT RAISE`.
- `test_profile_needs.py`: these FAIL: `test_python_supplies_every_fact_..._but_the_tables_of_a_call_and_of_a_loop`, `test_the_keys_a_profile_sets_are_found_...`, `test_a_decorator_form_needs_...`, `test_each_holder_of_a_table_form_needs_its_own_fact_...`, `test_a_call_form_under_python_...`, `test_a_loop_form_under_python_...`, `test_a_call_form_written_after_...`, `test_the_keys_that_read_tables_add_no_table_fact_...`, `test_a_form_whose_tables_the_language_supplies_partly_...`, `test_an_entry_with_two_holders_...`, `test_an_entry_that_is_no_mapping_...` and `test_a_call_form_written_in_a_testing_preset_...`. Many fail with `KeyError: 'function.tables.call'` or `DID NOT RAISE`.
- These PASS already, pinning behaviour that must hold: `test_a_decorator_form_under_python_loads`, `test_a_framework_that_writes_no_form_needs_no_table_fact[*]` and `test_a_holder_written_as_null_adds_no_table_fact_problem`.
- `test_profile_explain.py`: both new tests FAIL (`needs` is `[]` for `testing.tables.call`, and `testing.tables` has a `needs:` line).

- [ ] **Step 7: Split the fact in `FACTS`**

In `xarch/profile_values/capabilities.py`, replace line 63:

```python
    "function.tables": "the tables of cases of a test function",
```

with

```python
    "function.tables.decorator": "the tables of cases a mark on a test function's definition holds",
    "function.tables.call": "the tables of cases a call that makes or wraps a test function holds",
    "function.tables.loop": "the tables of cases a test function's body runs through in a loop",
```

- [ ] **Step 8: Python supplies the decorator fact only**

In `xarch/architectures/presets/language/python.yaml`, replace line 102:

```yaml
  function.tables: exact
```

with

```yaml
  function.tables.decorator: exact
```

Do not add `function.tables.call` or `function.tables.loop`.

- [ ] **Step 9: Each holder needs its own fact in `NEEDS`**

In `xarch/modules/spec/domain/key_table.py`, in `NEEDS`:

Replace line 254

```python
    "tiers.<tier>.plain_tables": ("function.tables", "function.blocks", "function.expressions"),
```

with

```python
    "tiers.<tier>.plain_tables": ("function.blocks", "function.expressions"),
```

Replace line 258

```python
    "testing.tables": ("function.tables",),
```

with

```python
    "testing.tables[].decorator": ("function.tables.decorator",),
    "testing.tables[].call": ("function.tables.call",),
    "testing.tables[].loop": ("function.tables.loop",),
```

Replace lines 260-261

```python
    "guards.scenario-coverage": ("union", "function.tables", "function.blocks", "function.expressions",
                                 "function.asserts", "function.mentions"),
```

with

```python
    "guards.scenario-coverage": ("union", "function.blocks", "function.expressions", "function.asserts",
                                 "function.mentions"),
```

- [ ] **Step 10: Run the new tests and see them pass**

Run: `timeout 600 uv run pytest -q tests/modules/rules/domain/test_parsed.py tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py`
Expected: PASS, every test.

If `test_a_call_form_written_after_...` or `test_a_call_form_under_python_...` still fails, check that the `NEEDS` keys carry `[]`. Change `profile_needs.py` only if they do and the failure persists.

- [ ] **Step 11: Run the spec, rules and cli suites**

Run: `timeout 900 uv run pytest -q tests/modules tests/cli tests/kernel tests/platform tests/profile_values tests/architecture`
Expected: PASS. If anything in `test_testing.py` or `test_profile_keys.py` fails here, Task 1 is missing.

Run: `uv run ruff check`
Expected: `All checks passed!`

- [ ] **Step 12: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml xarch/modules/spec/domain/key_table.py tests/modules/rules/domain/test_parsed.py tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain.py
git commit -m "The fact function.tables is one fact per form, each holder of testing.tables needs its own, and Python supplies the decorator's alone, so a call or loop form under Python is refused at testing.tables.<i>.<holder>"
```

---

### Task 3: README and CHANGELOG say the facts per form, and every gate passes

**Files:**
- Modify: `CHANGELOG.md:100-101`
- Modify: `README.md:179-180`, `README.md:509`
- Verify (no edit): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`, `tests/bootstrap/corpora/`

**Interfaces:**
- Consumes: the fact names of Task 2.
- Produces: docs only.

- [ ] **Step 1: The CHANGELOG bullet**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Changed`, replace lines 100-101:

```markdown
- The description of the fact `function.tables`, shown by `profile explain` and in a refusal of a fact the language
  does not supply, reads "the tables of cases of a test function".
```

with

```markdown
- The fact `function.tables` is now three facts, one per form a table is written in: `function.tables.decorator`,
  `function.tables.call` and `function.tables.loop`. Each holder of an entry of `testing.tables` needs its own fact,
  and is refused at its index when the language does not supply it (`testing.tables.0.call: its check reads
  function.tables.call ...`). Python supplies `function.tables.decorator`, and not `call` or `loop`. A language data
  file that writes `function.tables` under `supplies` is refused as an unknown fact.
```

- [ ] **Step 2: The two README sentences**

In `README.md`, replace (lines 179-180)

```markdown
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly. One fact is never written under `supplies`: `file.package`, that a file stands for the
```

with

```markdown
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call` and `function.tables.loop`, so a framework that writes a `call`
or `loop` form under Python is refused at that entry (`testing.tables.0.call`). One fact is never written under
`supplies`: `file.package`, that a file stands for the
```

Replace (line 509)

```markdown
  key and the fact. Python's reader supplies every fact exactly, so a Python project never sees this line.
```

with

```markdown
  key and the fact. Python's reader supplies every fact exactly but `function.tables.call` and
  `function.tables.loop`, and none partly, so a Python project never sees this line.
```

- [ ] **Step 3: Regenerate and read the golden docs**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/architecture`
Expected: PASS. The golden docs generate byte for byte, so nothing needs regenerating.

Run: `git status --short docs/cli docs/web docs/xarch tests/bootstrap/corpora`
Expected: no output.

- [ ] **Step 4: Run every gate**

Run in the background, then read the result at the end: `timeout 1800 uv run pytest -q > /tmp/6-4-pytest.log 2>&1`
Expected: tail of `/tmp/6-4-pytest.log` shows `passed` and no `failed`/`error`.

Run each, expecting exit 0:
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check`
- `uv run xarch profile check architecture.yaml`

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md README.md
git commit -m "README and CHANGELOG say function.tables is one fact per form and Python supplies the decorator's alone"
```

---

## Self-review

- **Spec coverage:**
  - 3.1 (FACTS, texts, neutrality, old name refused as unknown): Task 2, Steps 1, 2 and 7.
  - 3.2 (python.yaml): Task 2, Steps 3 (T9) and 8.
  - 3.3 (NEEDS table and explain lines): Task 2, Steps 3, 5 (T12) and 9.
  - 3.4 (refusal wording, index counting, decorator loads, loop refused, null holder, no bare `testing.tables`, no own problem from plain_tables/guard, partial is approximate): Task 2, Step 4 (T1-T4, T6, T7, RF1-RF5) and Step 3 (T5).
  - 3.5 (nothing else moves): Task 2, Step 11 and Task 3, Steps 3-4.
  - 3.6 (CHANGELOG, README, golden docs): Task 3.
  - T13 (existing suites green): Task 3, Step 4.
- **Deviations, all forced by the code:** the `[]` in the `NEEDS` keys and in T8, `"note": None` in T12, and Task 1 for the two loader test files the spec did not foresee.
- **Placeholders:** none.
- **Prototype:** the three data changes and every test of this plan were applied to a scratch copy. `tests/modules`, `tests/cli` and the new explain tests (4726) passed, as did the full `tests/bootstrap` (882) and the rest (475). `ruff check`, `xarch check` and `xarch check --strict` were clean.
- **Names:** `READS_EVERY_FACT`, `EVERY_FORM`, `unread`, `framed`, `UNTABLED` and `LOOSE` are used as defined.

<!-- task-pipeline: validated -->
