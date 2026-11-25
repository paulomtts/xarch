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
