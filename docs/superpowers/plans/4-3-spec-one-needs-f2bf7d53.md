# 4.3 spec: one needs walker descends into every nested scope, mapping or list

Card `f2bf7d53`, subtask of `c34d7f47`, blocked by `546386b1` (4.2, the guard `no-callbacks`, done on this branch).
Release step 11 of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`,
below **R3**, section 3, line 274: "The needs walker: any key that opens a scope, a mapping or a list. | code-shape 3 |
Before its users (12, 19, 21); walks step 3's `uses` from then.").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Section 2.9, the walker paragraph (CS lines 420-421): "`profile_needs._configured` walks one level deep today. It
  must descend into `holds` and each kind (release step 11, the walker shared with test-tables and
  language-neutral)." The descent is built here; `holds` as a map of kinds is not (see Out of scope).
- Section 2.9 (CS lines 405-412): a nested key the language does not supply is refused at load by the existing
  `refused` with the nested address, in the existing wording ("`<address>`: its check reads `<fact>` (...), which the
  language `<language>` does not supply: drop `<address>`, or check the app with a language whose reader supplies
  `<fact>`").
- Section 5.1 item 5 (CS line 682): "`_configured` descends into `holds`, each kind, and `imports`."
- Section 7 step 3 (CS lines 804-805): "The needs walker (release step 11), descending into `holds`, its kinds,
  `imports`, and list entries (shared with test-tables and language-neutral)."
- Section 7 gates (CS line 828): `uv run ruff check` (no `--fix`), `uv run xarch check`, `uv run xarch check --strict`,
  and the rest of the card's gates.
- Dodge (CS line 963): "Leaving `profile_needs` one level deep, so nested settings are never held to their facts."

Other users of the walker, each citing it:

- R3 **O6** (line 230): sub-scopes (`uses`, `holds`, its kinds, `imports`) and list entries (`testing.tables`,
  `testing.declared`, `testing.mocks.specs`); "Step 11 builds one walker. Step 3's `uses` scope is walked from then."
- `test-tables-design.md` section 2.4 (lines 216-221): a problem prints a list entry's index,
  `testing.tables.0.decorator`; "`profile_needs._configured` must walk the entries of a list key as it walks a mapping;
  today it walks only mappings. Release step 11 builds that walker once".
- `language-neutral-design.md` section 2.4 (lines 318-320) and section 12 (line 1069): "A problem addresses an entry
  by its index from 0 (`testing.declared.0.call`), and `profile explain` the key with no index
  (`testing.declared.call`)"; the walker is "Reused, no change".

R3 rules inherited: **O4**, **O5** (lines 228-229): this step's README and CHANGELOG lines go under `[Unreleased]`;
**O8** (line 232): the golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read, never edited
by hand; this step moves no line of them; **O10** (line 234): the recorded findings change in no line in this step.

## 1. Goal

Every key a profile sets that configures a check is held to the facts its check reads, however deep it sits: in a
scope one key opens, in a scope a key of that scope opens, and so on down, and in each entry of a list a key opens.
Today `profile_needs` reaches the file's keys, a part's and a tier's keys, one group below them (`uses`), the
`testing` keys and one level under each guard, by hand, scope by scope. After this step one walker reads the key table
and goes as deep as the table's `opens` go, so steps 12 (`holds` kinds), 19 (`testing.tables`) and 21
(`testing.declared`, `testing.mocks.specs`) only add rows to the table and to `NEEDS`, and their keys are held to
their facts with no change to `profile_needs`.

No profile the repository ships, no bundled profile, no recorded corpus and no golden doc changes in what it loads,
refuses or finds: the real key table has no key with needs deeper than the walker reaches today. What the step proves
it proves with a key table of the tests' own.

## 2. Behaviour

### 2.1 What the walker walks

The walker starts at the file's scope (`profile`) with the whole document. In a scope, it takes the scope's keys in
the order of the key table (the order `KEYS` lists them, the order a file writes them) and, for each key the value
in hand holds:

1. If the key is configured (2.2) and needs facts, it yields the key with its address (2.4).
2. If the key is configured and opens a scope, it descends into that scope with the key's value, shaped as the opened
   scope's address says (2.3), before going on to the next key of the scope.

So the order is depth first, a key before the keys of the scope it opens, and a scope's keys in table order. Entries of
a map the profile names (parts, tiers, ...) come in the document's order; entries of a list in index order.

The walker reads the table it is handed. By default that is the table of every key of the format; a caller, the tests
first among them, may hand it another (section 3).

### 2.2 When a key is configured

- A key the mapping does not hold is not configured, and nothing below it is walked.
- A key whose value is `false` or null configures nothing, and nothing below it is walked.
- Any other value configures the key.
- The one exception is the scope of the guards (`guards`): a guard named there is configured whatever its value,
  `false` and null included, as today (`profile_needs.py:34-37`). Below a guard, its own keys follow the general rule.
- The key `testing` of the file, when its value is a string, stands for the preset of that name: the walker walks the
  preset's mapping in its place, as today (`profile_needs.py:30-31`). A string that names no preset walks nothing.
  The `testing` key itself has no needs; the rule is about what is walked below it.

### 2.3 The shape of an opened scope

What the walker expects under a key that opens a scope is read from the opened scope's address (`SCOPES`, or the
scope's own name for a scope `SCOPES` does not list, as `Key.where` reads it):

| The opened scope's address | What the key's value must be | What is walked |
|---|---|---|
| ends in `[]` (`docs.naming[]`) | a list | each entry that is a mapping, by its index from 0 |
| ends in a placeholder step `.<...>` (`parts.<part>`, `files.<path>`, `testing.mocks.fixtures.<parameter>`) | a mapping of names the profile chooses | each entry whose value is a mapping, under its name |
| anything else (`testing`, `parts.<part>.uses`, `guards`, `guards.no-twins`) | a mapping | the mapping itself |

A value of another shape walks nothing below the key, and is no error of the walker (the parser reports a malformed
value on its own): a `uses` that is a string or a list (it opens a mapping scope), a list scope written as a mapping,
an entry of a list that is a string, an entry of a map of parts that is no mapping. The key itself, if it needs facts
and is configured, is still yielded: shape decides only the descent.

The notes write a list entry's step in `NEEDS` as `<n>` (`testing.tables.<n>.decorator`); in the key table a list
scope's address is written with `[]`, as `docs.naming[]` already is, so that a list scope is told from a map of names.
A list scope's keys therefore sit in `NEEDS` at `<list address>[].<key>` (`testing.declared[].call`), which `plain`
turns into the address `profile explain` shows (`testing.declared.call`), as language-neutral 2.4 wants. Steps 19 and
21 add their scopes and rows in that form.

### 2.4 The address of a key found

The address is the path to the key in the document, its steps joined with `.`: each key's name, each name of an
entry of a map of names, and each list entry's index from 0, counting every entry of the list (a string entry at index
0 makes the first mapping entry index 1). A key of the file has its bare name (`reserved`). Examples:

- `parts.service.uses.never`, `tiers.unit.uses.apply_never` (as today)
- `guards.dead-code.untested` (as today)
- in a list: `testing.declared.0.call`, `docs.naming.1.<key>`
- three scopes down: `parts.logic.holds.records.immutable` (once step 12 adds the scopes)

The address is what the shortfall carries (`Shortfall.address`), so the refusal and the `approximate` line of the
enforcement section print it unchanged: `testing.declared.0.call: its check reads test.call (...), which the language
toy does not supply: drop testing.declared.0.call, or check the app with a language whose reader supplies test.call`.

### 2.5 What changes for a profile the repository has

- Which keys are yielded, for every profile: the same as today, but for one case: a key of a file's, part's or tier's
  scope written with no value (null) was yielded and now configures nothing (2.2, test 12); no profile the repository
  ships writes one, which the suite proves. Every key with needs in today's table sits at a depth
  the hand-made walk reaches; the scopes the walker newly enters (`fakes`, `files.<path>`, `docs`, `review`, `evals`,
  `testing.table`, `testing.mocks`, `testing.mocks.fixtures.<parameter>`, `tiers.<tier>.docs`) hold no key with needs.
- The order of the yielded keys, which is the order of the refusals printed for one profile and of its `approximate`
  tuple, becomes the order of 2.1. Against today's order this moves the `testing` keys first (the file's key `testing`
  is first in the table), the file keys `reserved` and `tiers` among the opening keys where the table lists them, and
  within a tier `uses` before `must_import` (table order). Only a profile with two or more keys short of facts sees a
  difference, and only in order. Python supplies every fact exactly, so no Python profile sees one.
- No finding of `xarch check` changes; no golden doc line changes; no recorded corpus line changes.

## 3. The interface the tests and steps 12, 19, 21 rely on

- `profile_needs.short(document, presets, language, keys=...)`: the facts the keys the document sets need that its
  language supplies partly or not at all, as today, with a new keyword-only parameter `keys: tuple[Key, ...]`, the key
  table to walk, whose default is the table of every key of the format (`KEYS` and `SLOTS`, as `keys_of` reads them).
  The two positional parameters and the return value are unchanged; its one caller (`profile_parsing.py:173`) does
  not change.
- `refused` and `approximate` are unchanged.
- The walker's root scope is `PROFILE`; the preset rule applies to the root key named `testing`, the guard rule to the
  scope `GUARD`, whatever table is handed. A table of the tests' own uses scope names of its own (not in `SCOPES`), so
  their addresses are their names, and writes each key's `needs` on the key itself.
- The module docstring and the walker's docstring say the new behaviour (any depth, the three shapes, the index
  address); docstrings are the only prose in code (no comments, a project rule).

## 4. Tests

All in `tests/modules/spec/application/logic/test_profile_needs.py`, the unit tier of `spec`'s logic: the walker is a
pure function of a document, a preset map, a language and a key table, and that file already holds every test of
`profile_needs` and its helpers (`TOY`, `layered`, `parsed`, `problems`, `refusal`). Written first, each failing before
the walker changes (except those marked "stays green", which pin today's behaviour through the change).

A test-only table, defined in the test module, has (scope names are its own):

- file keys: `outer` opening `outer`; `rows` opening `rows[]`; `items` opening `items.<item>`; `flat` needing `use`.
- `outer`: `inner` opening `outer.inner`; `own` needing `call`.
- `outer.inner`: `deep` needing `call`.
- `rows[]`: `form` needing `call`.
- `items.<item>`: `cells` opening `items.<item>.cells[]`.
- `items.<item>.cells[]`: `kind` needing `use`.

With `TOY`, which supplies neither `call` nor `use`, so every key of the table that is yielded gives one refused
shortfall (`note` None):

1. **A key three scopes down is held to its facts, at its full address**: `{outer: {inner: {deep: x}}}` gives one
   shortfall at `outer.inner.deep` for `call`. Unit: the descent past one level is the step's deliverable.
2. **Each entry of a list is held to its facts, addressed by its index from 0**: `{rows: [{form: a}, {form: b}]}`
   gives `rows.0.form`, `rows.1.form`. Unit.
3. **The index counts every entry, not only the mappings**: `{rows: ["x", {form: a}]}` gives `rows.1.form` alone.
   Unit: pins 2.4's counting rule.
4. **A list inside an entry of a map of names, under the entry's name and the index**:
   `{items: {a: {cells: [{kind: k}]}}}` gives `items.a.cells.0.kind` for `use`. Unit: two shapes composed.
5. **Depth first, and a scope's keys in table order, not the document's**:
   `{flat: 1, outer: {own: 1, inner: {deep: 1}}}` gives `outer.inner.deep`, `outer.own`, `flat`: the table lists
   `outer` before `flat` and `inner` before `own`, and `deep` comes before `own` because the walk finishes `inner`'s
   scope first. Unit: pins 2.1's order.
6. **What configures nothing, parametrized with ids**, each giving no shortfall: a nested key set to `false`
   (`{outer: {inner: {deep: false}}}`); set to null; an opening key set to `false` (`{outer: false}`, nothing below
   walked); a list entry that is no mapping (`{rows: ["x"]}`); a list scope written as a mapping
   (`{rows: {form: a}}`); a mapping scope written as a list (`{outer: [{own: 1}]}`); a map-of-names entry that is no
   mapping (`{items: {a: "x"}}`); a key the table does not list (`{outer: {stray: 1}}`). Unit.
7. **A key that is yielded keeps being yielded when its value's shape stops the descent**: in a variant where
   `rows` itself needs `use`, `{rows: "x"}` gives `rows` alone. Unit: shape decides only the descent (2.3).
8. **The default table is every key of the format**: `short(document, presets, language)` and
   `short(document, presets, language, keys=(*KEYS, *SLOTS))` give the same list for the ordered document of
   test 10. Unit: pins the default of section 3.
9. **A list entry's refusal reads as every refusal does, end to end**: through the parser with a test-only table is
   not possible (the parser uses the default), so this test calls `refused(short(..., keys=TABLE), TOY)` on
   `{rows: [{form: a}]}` and checks the exact text `rows.0.form: its check reads call (...), which the language toy
   does not supply: drop rows.0.form, or check the app with a language whose reader supplies call`. Unit: the address
   flows into the existing message unchanged (CS lines 405-412).
10. **The keys a profile sets are found in every scope and through a testing preset, each once** (the existing test
    at `test_profile_needs.py:87-112`): its expected list is rewritten in the order of 2.1 and 2.5, the same pairs
    in the new order: `testing.skips`, `testing.table`, `testing.mocks`, `parts.api.may_import`,
    `parts.service.may_import`, `parts.service.holds`, `parts.service.uses.never`, `parts.store.may_import`,
    `parts.store.libraries`, `reserved`, `tiers`, `tiers.unit.uses.apply_never`, `tiers.unit.must_import`,
    `guards.no-comments`, `guards.no-twins`, `guards.no-twins.translated`, `guards.dead-code`,
    `guards.dead-code.untested`, `guards.dead-code.tests_only`, `guards.dead-code.known`. Unit: the one real-table
    pin of the walk.
11. **A guard is configured by being named, whatever its value** (new, real table): `guards: {no-callbacks: false}`
    in toy still gives the shortfall at `guards.no-callbacks` for `callback`. Unit: pins the exception of 2.2.
12. **A null leaf configures nothing** (new, real table): a part with `holds: null` gives no shortfall for
    `parts.service.holds` in `short(...)` with `TOY`. Unit: pins 2.2's null rule on a real key.
13. Stay green, unchanged: `test_a_part_s_never_list_under_uses_needs_the_facts_its_check_reads`,
    `test_a_tier_that_applies_the_never_lists_needs_the_facts_their_check_reads`,
    `test_apply_never_false_configures_nothing`, and
    `test_a_uses_that_is_no_mapping_configures_nothing_in_any_language` (both ids: a string, a list): `uses` opens a
    mapping scope, so a list under it walks nothing. These prove step 3's `uses` is walked by the one walker (R3 O6).

Other tiers: `tests/bootstrap/test_needs_agree.py` (end to end, the CLI against the rules' needs) stays green with no
change; the full suite, `xarch check`, `xarch check --strict`, `ruff check` and `xarch profile check
architecture.yaml` pass, which proves 2.5 for every shipped profile and corpus. A test whose expected text lists two
or more needs refusals of one profile in today's order, if the suite has one, is updated in order only, and the plan
names it.

## 5. Docs

- README, the paragraph on `supplies` (README lines 167-176): one clause saying a key is held to its facts wherever it
  sits, in a scope any key opens and in each entry of a list, and that a problem addresses a list entry by its index
  from 0 (`testing.declared.0.call` style, with a key the table has today only if one exists; otherwise the form is
  described without a key that does not yet exist). Under `[Unreleased]` per R3 O4: the README has no release
  heading, so "under `[Unreleased]`" means the line lands in this step's commit with the rest.
- CHANGELOG, `[Unreleased]`, `### Changed`: one line: a profile's keys are held to the facts their checks read at
  any depth, in every scope a key opens and in each entry of a list (addressed by its index from 0), by one walk of the
  key table; the refusals of a profile with several keys short of facts are now listed in the order the key table
  lists the keys.
- Golden docs: regenerated, the diff read: none expected (no key table text changes).

## 6. Out of scope

- The scopes of `holds` and its kinds (step 12, card 4.4) and of `imports` on parts and tiers (steps 13 and 14, card
  4.5): this step adds no scope, no key and no `NEEDS` row to the real table.
- The list scopes `testing.tables` (step 19), `testing.declared` and `testing.mocks.specs` (step 21): their scopes,
  keys and `NEEDS` rows are their steps' work; they use 2.3's `[]` form.
- `profile explain` (`explain.short`, `explanation.py`): it reads a key's needs by its address, not by walking a
  document; unchanged.
- The parser's own validation of nested values and list entries: unchanged; the walker reports no shape error.
- The retired-keys table, `test_needs_agree.py`'s `EVERY_KEY`, recorded corpora: untouched.

## 7. Review focus for the planner

- A YAML key written with no value (`holds:`) is null: it must configure nothing, below the guards scope as above it
  (today a null leaf of a part is yielded, a null guard sub-key is not; 2.2 makes both "nothing").
- A preset name that is no preset, and a `testing` that is neither a string nor a mapping: nothing walked, no crash.
- Document keys that are not strings (YAML `1:` or `true:` as a part name): the address is built with `str` of the
  name, no crash.
- A list scope holding a list (`rows: [[...]]`): the inner list is no mapping, so nothing below it.
- Recursion depth is bounded by the table, not the document: a document nested deeper than the table's scopes walks
  no further than the table says.

---

# 4.3 spec: one needs walker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `profile_needs.short` holds every key a profile sets to the facts its check reads at any depth, by one recursive walk of a key table (a mapping scope, a map of names, a list), with the table a keyword-only parameter.

**Architecture:** One recursive generator, `_configured(mapping, scope, at, presets, keys)`, replaces the hand-made walk (`_configured`, `_set`, `_grouped`, `_guard_keys`) in `xarch/modules/spec/application/logic/profile_needs.py`. A second helper, `_held(value, where, address)`, reads the opened scope's address (`SCOPES.get(opens, opens)`) to decide the shape: `[]` → list by index, a trailing `.<...>` → map of names, else the mapping itself. `short` gains `*, keys: tuple[Key, ...] = (*KEYS, *SLOTS)`. No key, scope or `NEEDS` row changes.

**Tech Stack:** Python 3.13, pytest, ruff, `uv run`; xarch checks itself with `uv run xarch check`.

**Spec:** `docs/superpowers/specs/4-3-spec-one-needs-f2bf7d53.md` (prepended above).

## Global Constraints

- Gates: `uv run ruff check` (no `--fix`), `uv run xarch check`, `uv run xarch check --strict`, `uv run pytest -q`, `uv run xarch profile check architecture.yaml` (CS line 828).
- Docstrings are the only prose in code: no `#` comments (project rule; `guards.no-comments` enforces it on xarch itself).
- Line length 120 (ruff config); the repo's own `xarch check` must stay clean (it passed on a prototype of exactly the code below).
- `profile_parsing.py:173` (`needs.short(document, presets or {}, language)`) does not change.
- `refused` and `approximate` do not change.
- No `KEYS`/`SCOPES`/`NEEDS` row is added or changed; no retired-keys entry; `test_needs_agree.py` untouched.
- R3 O8: `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read, never edited by hand; expected diff: none.
- R3 O10: recorded corpora (`tests/bootstrap/corpora/*`) change in no line.
- README and CHANGELOG lines go under `[Unreleased]` (CHANGELOG `## [Unreleased]` → `### Changed`), R3 O4/O5.
- Never `git stash` bare; never `pkill`/`killall`; stop a stuck run with `timeout`.

### Readings of the spec fixed here

- "`false` or null configures nothing" is tested by identity (`value is None or value is False`), not by `in (None, False)`: `0 == False` in Python, and the spec says "Any other value configures the key", so `0`, `""`, `[]` and `{}` configure a key. Pinned by `test_any_value_but_false_and_null_configures_a_key`. (Today a guard sub-key set to `0` is not yielded; after this step it is. No profile in the repo writes one with needs, and Python supplies every fact, so nothing observable moves.)
- Spec test 11 (a guard named with `false`) and the null-guard-sub-key / preset tests of the Review Focus already hold today: they are written with the rest and pass before the change ("stays green"); they pin behaviour through the rewrite. Every other new test fails first (most with `TypeError: short() got an unexpected keyword argument 'keys'`).
- Spec section 4's closing sentence: a prototype of exactly the Task 1 code was run against the full suite (5350 tests): the **only** existing test whose expectation changes is `tests/modules/spec/application/logic/test_profile_needs.py::test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once` (spec test 10). No other test lists two or more needs refusals of one profile in an order that moves. `xarch check`, `xarch check --strict`, `ruff check` and `xarch profile check architecture.yaml` all passed on the prototype.

## Review Focus

1. A YAML key written with no value (`holds:`, `translated:`) is null and configures nothing, above and below the guards scope — `test_a_key_of_a_part_written_with_no_value_configures_nothing`, `test_a_key_of_a_guard_written_with_no_value_configures_nothing` (Task 1).
2. `testing` naming no preset, or being a number or a list, walks nothing and does not crash; naming a preset walks the preset — `test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing`, `test_a_testing_that_names_a_preset_is_walked_as_the_preset` (Task 1).
3. Entry names that are not strings (YAML `7:` or `false:` as a name) are addressed by `str` of the name, no crash — `test_an_entry_named_by_no_string_is_addressed_by_its_name_as_text` (Task 1).
4. A list entry that is itself a list walks nothing below it — the `a list entry that is a list` id of `test_what_configures_nothing_is_held_to_no_fact` (Task 1).
5. A document nested deeper than the table's scopes walks no deeper than the table — `test_a_document_nested_deeper_than_the_table_is_walked_no_deeper_than_the_table` (Task 1).

---

## File Structure

- Modify `xarch/modules/spec/application/logic/profile_needs.py` (whole file rewritten below): the walker and `short`'s new parameter.
- Modify `tests/modules/spec/application/logic/test_profile_needs.py`: imports, a test-only table `NESTED`, helpers, the rewritten order test, new tests.
- Modify `README.md:170-171` (the `supplies` paragraph) and `CHANGELOG.md:44-46` (top of `### Changed` under `## [Unreleased]`).
- Regenerate (expect no change) `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`.

---

### Task 1: One walker, any depth, the key table a parameter

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_needs.py` (all of it)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: `Key` (`scope`, `name`, `opens`, `needs`, `address`), `PROFILE`, `GUARD`, `SCOPES` from `xarch.modules.spec.domain.profile_keys`; `KEYS`, `SLOTS` from `xarch.modules.spec.domain.key_table`; `shortfalls(address, needs, supplies) -> list[Shortfall]` from `xarch.kernel.logic.capabilities`.
- Produces: `short(document: Mapping[Any, Any], presets: Mapping[str, Any], language: Language, *, keys: tuple[Key, ...] = (*KEYS, *SLOTS)) -> list[Shortfall]` — steps 12, 19 and 21 rely on it walking any scope they add to the table. `refused(found, language) -> list[str]` and `approximate(found) -> tuple[Shortfall, ...]` unchanged.

- [ ] **Step 1: Update the test module's imports and shared helpers**

In `tests/modules/spec/application/logic/test_profile_needs.py`, replace the import block

```python
from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.language_file import PARTIAL
from xarch.modules.spec.application.logic.profile_needs import short
from xarch.modules.spec.domain.key_table import KEYS
from xarch.profile_values.capabilities import EXACT, FACTS, Shortfall, Supply
```

with

```python
from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.language_file import PARTIAL
from xarch.modules.spec.application.logic.profile_needs import refused, short
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import PROFILE, Key
from xarch.profile_values.capabilities import EXACT, FACTS, Shortfall, Supply
```

Then, directly after the line `FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}`, add:

```python
PARTLY = replace(PYTHON, checked=replace(PYTHON.checked, supplies=tuple(Supply(f, PARTIAL, "partly") for f in FACTS)))
"""Python, its reader supplying every fact only partly: every key the walk finds gives one shortfall per fact."""
OUTER, INNER, ROWS, ITEMS, CELLS = "outer", "outer.inner", "rows[]", "items.<item>", "items.<item>.cells[]"
NESTED = (
    Key(PROFILE, "outer", opens=OUTER), Key(PROFILE, "rows", opens=ROWS), Key(PROFILE, "items", opens=ITEMS),
    Key(PROFILE, "flat", needs=("use",)),
    Key(OUTER, "inner", opens=INNER), Key(OUTER, "own", needs=("call",)),
    Key(INNER, "deep", needs=("call",)),
    Key(ROWS, "form", needs=("call",)),
    Key(ITEMS, "cells", opens=CELLS),
    Key(CELLS, "kind", needs=("use",)),
)
"""A key table of the tests' own, its scopes named by their addresses (none is in SCOPES): a mapping in a mapping, a
list, and a list in each entry of a map of names. Toy supplies neither call nor use."""
RANKED = tuple(replace(key, needs=("use",)) if key.address == "rows" else key for key in NESTED)
"""NESTED, its key rows needing use itself."""
```

And directly after the existing function `refusal(address, fact)` (it ends with `... whose reader supplies {fact}")`), add:

```python
def walked(document: dict, keys: tuple[Key, ...] = NESTED) -> list[str]:
    """The address of each shortfall of the document under the table in Toy, in the order found; each is refused (no
    note), as Toy supplies neither call nor use."""
    found = short(document, {}, TOY, keys=keys)
    assert all(item.note is None for item in found)
    return [item.address for item in found]


def everywhere() -> tuple[dict, dict]:
    """A profile setting keys that need facts in every scope, its testing written as the name of a preset, and the
    presets."""
    document = covered(guards={"dead-code": {"untested": True, "tests_only": True, "known": ["shared/wiring.py:build"]},
                               "no-comments": {}, "no-twins": {"translated": ["api"]}},
                       reserved={"json": "only io"})
    document["parts"]["service"]["holds"] = "classes"
    document["tiers"]["unit"]["must_import"] = ["service"]
    document["parts"]["service"]["uses"] = {"never": "pure"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    return document | {"testing": "pytest"}, {"pytest": document["testing"]}
```

- [ ] **Step 2: Rewrite the order test (spec test 10) and add the default-table test (spec test 8)**

Replace the whole existing function `test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once` with:

```python
def test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once():
    document, presets = everywhere()
    found = short(document, presets, PARTLY)
    configured = [("testing.skips", "testing.skips"), ("testing.table", "testing.table"),
                  ("testing.mocks", "testing.mocks"), ("parts.api.may_import", "parts.<part>.may_import"),
                  ("parts.service.may_import", "parts.<part>.may_import"), ("parts.service.holds", "parts.<part>.holds"),
                  ("parts.service.uses.never", "parts.<part>.uses.never"),
                  ("parts.store.may_import", "parts.<part>.may_import"),
                  ("parts.store.libraries", "parts.<part>.libraries"), ("reserved", "reserved"), ("tiers", "tiers"),
                  ("tiers.unit.uses.apply_never", "tiers.<tier>.uses.apply_never"),
                  ("tiers.unit.must_import", "tiers.<tier>.must_import"),
                  ("guards.no-comments", "guards.no-comments"), ("guards.no-twins", "guards.no-twins"),
                  ("guards.no-twins.translated", "guards.no-twins.translated"), ("guards.dead-code", "guards.dead-code"),
                  ("guards.dead-code.untested", "guards.dead-code.untested"),
                  ("guards.dead-code.tests_only", "guards.dead-code.tests_only"),
                  ("guards.dead-code.known", "guards.dead-code.known")]
    needs = {key.address: key.needs for key in KEYS}
    assert found == [Shortfall(address, fact, "partly") for address, key in configured for fact in needs[key]]


def test_the_table_walked_is_every_key_of_the_format_unless_another_is_given():
    document, presets = everywhere()
    assert short(document, presets, PARTLY) == short(document, presets, PARTLY, keys=(*KEYS, *SLOTS))
```

- [ ] **Step 3: Add the walker's tests (spec tests 1-7, 9, 11, 12 and the Review Focus)**

Directly after the existing function `test_a_uses_that_is_no_mapping_configures_nothing_in_any_language` (it ends with `assert short(document, {}, TOY) == []`), add:

```python
def test_a_key_three_scopes_down_is_held_to_its_facts_at_its_full_address():
    assert short({"outer": {"inner": {"deep": "x"}}}, {}, TOY, keys=NESTED) == [
        Shortfall("outer.inner.deep", "call", None)]


def test_each_entry_of_a_list_is_held_to_its_facts_addressed_by_its_index_from_0():
    assert walked({"rows": [{"form": "a"}, {"form": "b"}]}) == ["rows.0.form", "rows.1.form"]


def test_the_index_of_a_list_entry_counts_every_entry_not_only_the_mappings():
    assert walked({"rows": ["x", {"form": "a"}]}) == ["rows.1.form"]


def test_a_list_inside_an_entry_of_a_map_of_names_is_addressed_by_the_entry_s_name_and_the_index():
    assert short({"items": {"a": {"cells": [{"kind": "k"}]}}}, {}, TOY, keys=NESTED) == [
        Shortfall("items.a.cells.0.kind", "use", None)]


def test_the_walk_is_depth_first_and_takes_a_scope_s_keys_in_the_order_of_the_table():
    assert walked({"flat": 1, "outer": {"own": 1, "inner": {"deep": 1}}}) == ["outer.inner.deep", "outer.own", "flat"]


@pytest.mark.parametrize("document", [
    pytest.param({"outer": {"inner": {"deep": False}}}, id="a nested key set to false"),
    pytest.param({"outer": {"inner": {"deep": None}}}, id="a nested key set to null"),
    pytest.param({"outer": False}, id="an opening key set to false"),
    pytest.param({"outer": None}, id="an opening key set to null"),
    pytest.param({"rows": ["x"]}, id="a list entry that is no mapping"),
    pytest.param({"rows": [["x", {"form": "a"}]]}, id="a list entry that is a list"),
    pytest.param({"rows": {"form": "a"}}, id="a list scope written as a mapping"),
    pytest.param({"outer": [{"own": 1}]}, id="a mapping scope written as a list"),
    pytest.param({"items": {"a": "x"}}, id="an entry of a map of names that is no mapping"),
    pytest.param({"items": [{"cells": [{"kind": "k"}]}]}, id="a map of names written as a list"),
    pytest.param({"outer": {"stray": 1}}, id="a key the table does not list"),
])
def test_what_configures_nothing_is_held_to_no_fact(document):
    assert walked(document) == []


@pytest.mark.parametrize("value", [pytest.param(0, id="zero"), pytest.param("", id="an empty string"),
                                   pytest.param([], id="an empty list"), pytest.param({}, id="an empty mapping")])
def test_any_value_but_false_and_null_configures_a_key(value):
    assert walked({"outer": {"own": value}}) == ["outer.own"]


def test_a_key_that_needs_facts_is_held_to_them_whatever_the_shape_of_its_value():
    assert walked({"rows": "x"}, RANKED) == ["rows"]
    assert walked({"rows": [{"form": "a"}]}, RANKED) == ["rows", "rows.0.form"]


def test_an_entry_named_by_no_string_is_addressed_by_its_name_as_text():
    assert walked({"items": {7: {"cells": [{"kind": "k"}]}, False: {"cells": [{"kind": "k"}]}}}) == [
        "items.7.cells.0.kind", "items.False.cells.0.kind"]


def test_a_document_nested_deeper_than_the_table_is_walked_no_deeper_than_the_table():
    assert walked({"outer": {"inner": {"deep": {"inner": {"deep": 1}}}}}) == ["outer.inner.deep"]


def test_a_list_entry_s_refusal_reads_as_every_refusal_does():
    assert refused(short({"rows": [{"form": "a"}]}, {}, TOY, keys=NESTED), TOY) == [
        f"rows.0.form: its check reads call ({FACTS['call']}), which the language toy does not supply: drop "
        "rows.0.form, or check the app with a language whose reader supplies call"]


@pytest.mark.parametrize("value", [pytest.param(False, id="false"), pytest.param(None, id="null")])
def test_a_guard_is_configured_by_being_named_whatever_its_value(value):
    assert short(layered(language="toy", guards={"no-callbacks": value}), {}, TOY) == [
        Shortfall("guards.no-callbacks", "callback", None)]


def test_a_key_of_a_part_written_with_no_value_configures_nothing():
    assert short(services(holds=None), {}, TOY) == []


def test_a_key_of_a_guard_written_with_no_value_configures_nothing():
    found = short(layered(language="toy", guards={"no-twins": {"translated": None}}), {}, TOY)
    assert {item.address for item in found} == {"guards.no-twins"}


@pytest.mark.parametrize("testing", [pytest.param("nosuch", id="a name that is no preset"),
                                     pytest.param(3, id="a number"), pytest.param(["pytest"], id="a list")])
def test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing(testing):
    assert short(layered(language="toy", testing=testing), {"pytest": {"skips": ["x"]}}, TOY) == []


def test_a_testing_that_names_a_preset_is_walked_as_the_preset():
    found = short(layered(language="toy", testing="pytest"), {"pytest": {"skips": ["x"]}}, TOY)
    assert [(item.address, item.fact) for item in found] == [("testing.skips", "use"),
                                                             ("testing.skips", "import.resolved")]
```

(`services(**keys)` is the module's existing helper: `layered(language="toy")` with the keys added to `parts.service`.)

- [ ] **Step 4: Run the module to see the new tests fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py`

Expected: FAIL. Failing, with `TypeError: short() got an unexpected keyword argument 'keys'`: every test calling `walked(...)` or `short(..., keys=...)` (the three-scopes, list, index, map-of-names, depth-first, every id of `test_what_configures_nothing_is_held_to_no_fact` and `test_any_value_but_false_and_null_configures_a_key`, whatever-shape, no-string-name, deeper-document, refusal-text, default-table). Failing with an `AssertionError`: the order test (index 0: `testing.skips` expected, `reserved` found) and `test_a_key_of_a_part_written_with_no_value_configures_nothing` (today a null `holds` is yielded). Passing already (they pin today's behaviour through the rewrite): both ids of `test_a_guard_is_configured_by_being_named_whatever_its_value`, `test_a_key_of_a_guard_written_with_no_value_configures_nothing`, the three ids of `test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing`, `test_a_testing_that_names_a_preset_is_walked_as_the_preset`, and every test that was in the file before Step 1 but the order test. If any other test fails, stop and report it.

- [ ] **Step 5: Rewrite the walker**

Replace the whole content of `xarch/modules/spec/application/logic/profile_needs.py` with:

```python
"""What the keys a profile sets need of the language's reader: every key that configures a check needs the facts of
the source that check reads (see capabilities and key_table). One walk of the key table finds those keys however deep
they sit: from the file's keys into the scope each key opens, and from there as far down as the table's scopes go,
into a mapping, each entry of a map of names (parts.<part>) and each entry of a list (docs.naming[]), which is
addressed by its index from 0 (<list>.0.<key>). A key set to false or null configures nothing, but a guard, which its
name alone configures. A key whose language does not supply one of its facts is a problem of the profile, naming the
key, the fact and what to do; one whose language supplies a fact partly is kept, and listed as approximate where the
check is run.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Any

from xarch.kernel.logic.capabilities import shortfalls
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import GUARD, PROFILE, SCOPES, Key
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import FACTS, Shortfall

_NAMED = re.compile(r"\.<[^.>]*>$")
"""The end of the address of a scope whose entries the profile names (parts.<part>): a placeholder step."""


def _configured(mapping: Mapping[Any, Any], scope: str, at: str, presets: Mapping[str, Any],
                keys: tuple[Key, ...]) -> Iterator[tuple[str, Key]]:
    """Each key of the table that the mapping of the scope sets and that needs facts, with its address in the file (at
    is the mapping's address and a dot, "" for the file), in the order of the table, each followed by those of the
    scope it opens: depth first. A key the mapping does not hold, or holds as false or null, configures nothing, and
    nothing below it is walked; a guard is configured by its name alone. The file's testing, written as the name of a
    preset, is walked as the preset's mapping."""
    for key in (key for key in keys if key.scope == scope):
        value = mapping.get(key.name)
        if key.name not in mapping or (scope != GUARD and (value is None or value is False)):
            continue
        address = f"{at}{key.name}"
        if key.needs:
            yield address, key
        if scope == PROFILE and key.name == "testing" and isinstance(value, str):
            value = presets.get(value)
        for where, held in _held(value, SCOPES.get(key.opens, key.opens), address) if key.opens else ():
            yield from _configured(held, key.opens, f"{where}.", presets, keys)


def _held(value: Any, where: str, address: str) -> list[tuple[str, Mapping[Any, Any]]]:
    """The mappings a key's value holds for the scope it opens, each with its address, by the shape the scope's
    address (where) says: for one ending in [], a list, each entry by its index from 0, every entry counted; for one
    ending in a placeholder step, a mapping of names the profile chooses, each entry by its name; else the mapping
    itself. A value of another shape, and an entry that is no mapping, hold none."""
    if where.endswith("[]"):
        entries = [(f"{address}.{index}", entry) for index, entry in enumerate(value)] if isinstance(value, list) else []
    elif _NAMED.search(where):
        entries = [(f"{address}.{name}", entry) for name, entry in value.items()] if isinstance(value, Mapping) else []
    else:
        entries = [(address, value)]
    return [(found, entry) for found, entry in entries if isinstance(entry, Mapping)]


def short(document: Mapping[Any, Any], presets: Mapping[str, Any], language: Language, *,
          keys: tuple[Key, ...] = (*KEYS, *SLOTS)) -> list[Shortfall]:
    """The facts the keys the document sets need that its language supplies partly or not at all, in the order of the
    walk (see _configured); none when no language is known. keys is the table walked: every key of the format unless
    another is given."""
    if language.checked.supplies is None:
        return []
    supplies = {supply.fact: supply for supply in language.checked.supplies}
    return [found for address, key in _configured(document, PROFILE, "", presets, keys)
            for found in shortfalls(address, key.needs, supplies)]


def refused(found: list[Shortfall], language: Language) -> list[str]:
    """A problem for each fact a key needs that the language does not supply."""
    return [f"{item.address}: its check reads {item.fact} ({FACTS[item.fact]}), which the language {language.name} "
            f"does not supply: drop {item.address}, or check the app with a language whose reader supplies {item.fact}"
            for item in found if item.note is None]


def approximate(found: list[Shortfall]) -> tuple[Shortfall, ...]:
    """The keys whose check reads a fact the language supplies only partly."""
    return tuple(item for item in found if item.note is not None)
```

Notes for the implementer: the identity test `value is None or value is False` is deliberate (`0 == False`; `0` configures a key, pinned by `test_any_value_but_false_and_null_configures_a_key`); `presets.get(value)` returns `None` for a name that is no preset, which `_held` turns into nothing walked; the root key `testing` has no needs, so only what is walked below it changes. `keys_of` (in `key_lookup`) is no longer imported here: it reads the module-level table, and the walker must read the table it is handed.

- [ ] **Step 6: Run the module to see it pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py`
Expected: PASS, every test.

- [ ] **Step 7: Run the whole suite and the gates**

```bash
mkdir -p /tmp/xarch-4-3
timeout 1800 uv run pytest -q > /tmp/xarch-4-3/pytest.log 2>&1; tail -3 /tmp/xarch-4-3/pytest.log
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
git status --short
```

Expected: the suite passes (5383 tests, ~3 minutes; `tests/bootstrap/test_needs_agree.py`, `tests/bootstrap/test_recorded_corpora.py`, `tests/bootstrap/test_docs_templates.py` and `tests/architecture/test_self_check.py` among them, unchanged); ruff prints `All checks passed!`; both `xarch check` runs exit 0 with no violation; the profile check prints `OK: the profile is valid`; `git status --short` lists only the two files of this task (and the untracked spec/plan, which are not yours to commit). If a test outside `test_profile_needs.py` fails, stop and report it with its output: the spec says no other test's expectation moves (verified on a prototype), so a failure means the code differs from Step 5.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_needs.py tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'MSG'
One walk of the key table holds a profile's keys to the facts their checks read at any depth, into every scope a key opens, a mapping, each entry of a map of names and each entry of a list addressed by its index from 0, and short takes the table to walk as the keyword keys, every key of the format by default; a key written with no value configures nothing as false does, a guard is still configured by its name alone, and the keys short of facts come in the order of the table, each before those of the scope it opens

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 2: README, CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `README.md:170-171`
- Modify: `CHANGELOG.md:44-46` (top of `### Changed` under `## [Unreleased]`)
- Regenerate (expect no change): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: Task 1's behaviour (any depth, list entries by index from 0, null configures nothing, table order).
- Produces: nothing code reads.

- [ ] **Step 1: README**

In `README.md`, replace these two lines (170-171):

```
fields its words read, as `xarch profile explain kinds.<kind>` shows). A profile that sets a key whose facts its language does not
supply is refused when it loads, naming the key, the fact and what to do; a key whose facts are supplied only partly
```

with these four:

```
fields its words read, as `xarch profile explain kinds.<kind>` shows). A key is held to its facts wherever it sits: in
a scope any key opens, however deep, and in each entry of a list, which a problem names by its index from 0
(`<list>.0.<key>`). A profile that sets a key whose facts its language does not
supply is refused when it loads, naming the key, the fact and what to do; a key whose facts are supplied only partly
```

Then `grep -n "however deep" README.md` prints one line.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]` → `### Changed` (line 44), insert as the first item, after the blank line that follows `### Changed` and before the line starting `- \`no_callbacks\` on a part is now the guard`:

```
- A profile's keys are held to the facts their checks read at any depth, in every scope a key opens and in each
  entry of a list (addressed by its index from 0, as `<list>.0.<key>`), by one walk of the key table in place of a
  walk of the file's scopes one by one; a key written with no value configures nothing, as one set to `false` does.
  The refusals of a profile with several keys short of facts are now listed in the order the key table lists the
  keys, each key before those of the scope it opens.
```

Keep one blank line between this item's end and the next `- ` item only if the existing items are separated by blank lines; they are not (`### Changed` items follow each other directly), so insert the five lines with no blank line after them.

- [ ] **Step 3: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-4-3/regenerate_docs.py` (never committed):

```python
"""Write docs/{cli,web,xarch}/testing.md from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        if "/".join(file.path) == "testing.md":
            (root / "docs" / folder / "testing.md").write_text(file.template, encoding="utf-8")
            print(f"docs/{folder}/testing.md written")
```

Run:

```bash
uv run python -I /tmp/xarch-4-3/regenerate_docs.py "$PWD"
git status --short -- docs
```

Expected: three `written` lines and no output from `git status` (nothing under `docs/` changed; the spec and plan under `docs/superpowers/` are untracked and may show as `??` — those are not yours, leave them). If any of `docs/{cli,web,xarch}/testing.md` shows as modified, stop and report the diff (`git diff -- docs/cli docs/web docs/xarch`); restore with `git checkout -- docs/cli docs/web docs/xarch`. The fix belongs in the code, never in the docs.

- [ ] **Step 4: Run the gates**

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-4-3/pytest.log 2>&1; tail -3 /tmp/xarch-4-3/pytest.log
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
git diff HEAD~1 --stat -- tests/bootstrap/corpora
```

Expected: the suite passes (`tests/architecture/test_readme.py` included); ruff prints `All checks passed!`; both checks exit 0 with no violation; the profile check prints `OK: the profile is valid`; the corpora diff prints nothing (R3 O10).

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'MSG'
The README's supplies paragraph says a key is held to its facts wherever it sits, in a scope any key opens however deep and in each entry of a list, which a problem names by its index from 0; the CHANGELOG says the keys are held at any depth by one walk of the key table, that a key with no value configures nothing, and that the refusals come in the table's order; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

## Self-review against the spec

- 2.1 (root `profile`, table order, depth first, document order of map entries, index order of lists): `_configured` + `_held`; tests: depth-first, order test (10), map-of-names, list.
- 2.2 (absent, false, null configure nothing; guard exception; `testing` preset; missing preset): identity check, `scope != GUARD`, preset substitution; tests: what-configures-nothing (false/null nested and opening), any-value-configures, guard-named-false/null, part null leaf (12), guard sub-key null, testing presets.
- 2.3 (three shapes, other shapes walk nothing, key still yielded): `_held`; tests: what-configures-nothing ids (list as mapping, mapping as list, non-mapping entries, list in list, map as list), whatever-shape (7).
- 2.4 (address, index counts every entry, `str` of names): `_held` enumerate before filter, f-strings; tests: index counts every entry (3), no-string names, refusal text (9).
- 2.5 (only order and null-leaf change; no finding/golden/corpus change): prototype run; Task 1 Step 7 and Task 2 Steps 3-4.
- 3 (keyword-only `keys`, default `(*KEYS, *SLOTS)`, caller unchanged, `refused`/`approximate` unchanged, `PROFILE` root, `GUARD` rule whatever table, docstrings): Task 1 Step 5; test 8.
- 4 tests 1-13: Task 1 Steps 2-3 (13 = the four existing tests, untouched, run in Steps 4/6). The one existing test updated in order only is named under "Readings of the spec fixed here".
- 5 docs: Task 2 Steps 1-3. 6 out of scope: no table rows, `explain`, parser, retired keys, corpora touched.
- 7 review focus: the five Review Focus lines, each with its test in Task 1 Step 3.
- Placeholders: none; every code step shows its code. Names: `walked`, `everywhere`, `PARTLY`, `NESTED`, `RANKED`, `_configured(mapping, scope, at, presets, keys)`, `_held(value, where, address)` used consistently.
<!-- task-pipeline: validated -->
