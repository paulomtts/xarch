# 4.6 spec: a tier's import keys move into its `imports` group

Card `20b1e1ce`, subtask of `c34d7f47`, blocked by `912dfd81` (4.5, a part's `imports` group, done on this branch).
Release step 14 of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`,
below **R3**, section 3, line 277).

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Ruling 8 (CS 41-43): every list under `imports`, on a tier too, takes references. The spelling is story 8 (card: out
  of scope), so this step keeps today's spelling (see "Spelling" below).
- Ruling 10 (CS 45-46) and the defaults (CS 65-66): an old key is refused with a hint from the one retired-keys table,
  in fixed text; one problem per retired key.
- Ruling 12 (CS 52-53): a tier keeps its own `types_only` list (no mark on a tier's entries).
- Ruling 14 (CS 57): a tier's extra-import list inside `imports` is `also`.
- No compatibility window (CS 72-73).
- 3.1 (CS 451-470), the tier half (CS 462-470): `imports: {may, also, must, types_only}`.
- 3.2 (CS 472-493), the tier rows (CS 480-483) and the rules of the group (CS 486-493): `may: []` stays valid
  (`tiers.guard`, CS 490).
- 3.8 (CS 600-623): rule ids unchanged; finding keys `tiers.<t>.imports.types_only`, `tiers.<t>.imports.must`,
  `tiers.<t>.imports.also` (CS 606-607); `Loosened` keys `imports.types_only`, `imports.also` (CS 609-614); `where`
  JSON keeps its words (CS 615-618); the check language's texts name `imports.also` (CS 619-620).
- 3.9 (CS 625-643), the tier refusals (CS 631-632; 640-641 are story 8's).
- 5.1 item 2 (CS 669-674), the `TIER` rows and `NEEDS`; item 13 (CS 696-697), looseness keys and sentences; item 15
  (CS 700-704), `keys.yaml` and the `tiered-part` fragment.
- 5.2 (CS 708-731), the tier rows (CS 721-722, 725-728).
- 5.5 (CS 769-785): the 694 `(tiers.unit.types_only)` lines (CS 782-783), a change of wording only.
- 6 (CS 786-793): retired entries on a tier: `may_import`, `may_also_import`, `must_import`, `types_only` (CS 790-791);
  `profile explain <old key>` answers from the table.
- 7 step 6 (CS 816): this step; step 7 (internal names) is release step 15, not this one.
- Dodges (CS 948-976) the card names: "a mode on tiers beside their `types_only` list" (CS 966); "loosening the 'use
  ...' lists" (CS 975).

R3 rules inherited: **O4**, **O5** (R3 228-229): README and CHANGELOG lines of this step go under `[Unreleased]`;
**O8** (R3 232): the golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by
hand; **O15** (R3 239): every inline test profile that writes a tier's import keys is rewritten for the group in this
step.

### Spelling of entries in this step

References (`parts.controller`, `module.domain`) are story 8 (card: "Out of scope: references inside `imports`").
So a tier's `types_only` and `must` keep taking bare part names (`[controller]`), `may` and `also` keep today's target
grammar (`[domain/values]`, `everything`). CS 3.9's hints `[parts.<part>, ...]` are written here `[<part>, ...]`, and
CS 640-641 (the bare-name and `module.` refusals) are not added. Step 24 changes only the spelling inside the lines this
step moves.

## 1. Goal

A tier says in one group what its tests may import (a tier with a `folder`), may also import, must import one of, and
may import only as types:

```yaml
tiers:
  integration:
    imports:
      must: [controller]
      also: [domain/values, domain/profile]
  wired:
    imports:
      types_only: [domain, logic]
      must: [bootstrap]
  guard:
    folder: architecture
    imports:
      types_only: [domain, logic]
      may: everything
```

The tier keys `may_import`, `may_also_import`, `must_import` and `types_only` leave the tier, each refused with the
form that replaces it. For every bundled profile and xarch's own, what `check` finds is the same as before, finding for
finding, but for the key named in parentheses. Rule ids, `where`'s JSON fields, the tier's other keys (`proves`,
`litmus`, `uses`, `plain_tables`, `folder`, `docs`) and every part key do not change.

## 2. Behavior

### 2.1 The shape

```yaml
tiers:
  <tier>:
    imports:
      may: [<target>, ...] | everything      # only with a folder
      also: [<target>, ...]
      must: [<part>, ...]
      types_only: [<part>, ...]
```

| Address | Was | Takes | Rule id |
|---|---|---|---|
| `tiers.<t>.imports` | (none) | a mapping holding at least one of `may`, `also`, `must`, `types_only` | (the ones below) |
| `tiers.<t>.imports.may` | `tiers.<t>.may_import` | as today: targets, or `everything`; only for a tier with a `folder` | `tiers` |
| `tiers.<t>.imports.also` | `tiers.<t>.may_also_import` | as today: targets read from the instance a test mirrors; not `everything` | `tiers` |
| `tiers.<t>.imports.must` | `tiers.<t>.must_import` | as today: a non-empty list of declared part names | `must-import` |
| `tiers.<t>.imports.types_only` | `tiers.<t>.types_only` | as today: a non-empty list of declared part names | `types-only` |

What each means is exactly what the old key meant; the values carried (`Tier.may_import`, `.may_also_import`,
`.must_import`, `.types_only`; `CheckedTier`) are the same for the same lists. No `imports`, or `imports` without a
key, carries what leaving the old key out carried. The order a profile writes the keys in does not matter; the order of
entries is kept.

### 2.2 Refusals

Each is a problem of the profile, address first, raised with every other problem as today. `{use}` is the "use ..."
list `ck.unknown_keys` ends with; for a tier it becomes `use docs, folder, imports, litmus, plain_tables, proves, uses`
(sorted, generated from the table; each test that spells it is edited, not loosened, CS 975).

Retired keys on a tier (one problem each, `RETIRED` in `spec/domain/profile_keys.py`, scope `TIER`):

    tiers.guard: unknown key 'may_import': moved in 0.3.0: write imports: {may: [...]}; use ...
    tiers.integration: unknown key 'may_also_import': moved in 0.3.0: write imports: {also: [...]}; use ...
    tiers.wired: unknown key 'must_import': moved in 0.3.0: write imports: {must: [...]}; use ...
    tiers.rendering: unknown key 'types_only': moved in 0.3.0: write imports: {types_only: [<part>, ...]}; use ...

A tier writing several gets one problem per key, in sorted order, as `unknown_of` says. These entries are keyed
`(TIER, name)` and do not touch the part entries of the same names (the part `types_only` hint stays the mark's).

Inside the group:

    tiers.wired.imports: must be a map of may, also, must and types_only, such as {must: [<part>]}
    tiers.wired.imports: says nothing: write may, also, must or types_only, or drop it
    tiers.wired.imports: unknown key 'libraries': use also, may, must, types_only

(The first for `imports` written as a list, a string, `true` or null; the example is `must`, since `may` is only for a
tier with a folder. `libraries`, `never`, `apply_never` and any other word get the plain unknown-key problem: no
retired entry under the new scope.)

Each key's own problems are today's, word for word, at the new address:

    tiers.unit.imports.may: only a tier with a `folder` has an allowance of its own: without one, its tests import what the part they mirror may
    tiers.unit.imports.also: `everything` is not taken, name each target the tests may also import
    tiers.unit.imports.also: must be a list of targets such as [<part>, shared/text, api@any]: `everything` is not taken, name each target the tests may also import
    tiers.unit.imports.must: must be a list of part names
    tiers.unit.imports.must: no part named 'nowhere'
    tiers.unit.imports.types_only: 'domain' is listed twice

and every target-grammar problem of `may` and `also` (unknown part, bad path, `@any` outside the repeating folder, a
name pattern where none is taken) names `tiers.<t>.imports.may` / `.also`. A one-key map entry such as
`{controller: types_only}` in a tier's `may` or `also` is refused as any non-target entry is today, with today's text:
a tier takes no mark (dodge, CS 966). `tiers.<t>.imports.may: []` loads (CS 490).

### 2.3 `profile explain` and the key catalogue

- `xarch profile explain tiers.imports`, `tiers.imports.may`, `tiers.imports.also`, `tiers.imports.must`,
  `tiers.imports.types_only`, and each with a tier (`tiers.unit.imports.must`), answer with the key's text from
  `xarch/architectures/presets/format/keys.yaml` and the rules the table keys it by: `imports` → `tiers`,
  `must-import`, `types-only`; `may` → `tiers`; `also` → `tiers`; `must` → `must-import`; `types_only` → `types-only`.
- `xarch profile explain tiers.may_import` (and `may_also_import`, `must_import`, `types_only`) answers from the retired
  table with the hint of 2.2, exit code as for any retired key today.
- `keys.yaml` gains one text per new address (meaning, accepts, example in the `imports:` form) and loses the four
  tier texts (`tiers.<tier>.types_only`, `.must_import`, `.may_import`, `.may_also_import`). Every other text that names
  a tier's import key (the `tiers` text around line 209, the `tiered-part` fragment if it does, the
  `parts.<part>.imports.may.types_only` text that calls a tier's `types_only` the list form) names the new address. The
  catalogue test holds one text per key.
- `expansion.KEYS` (line 426-432) replaces `tiers.may_also_import`, `tiers.types_only`, `tiers.must_import` by
  `tiers.imports.also`, `tiers.imports.types_only`, `tiers.imports.must`; `expandable` and `keyed` answer for the new
  keys and not the old. `tiers` stays as it is.

### 2.4 Needs

`key_table.NEEDS` (line 246-250), each address moved with today's facts:

| Address | Needs |
|---|---|
| `tiers.<tier>.imports.types_only` | `_TYPES_ONLY` |
| `tiers.<tier>.imports.must` | `*_IMPORTS`, `function.statements`, `file` |
| `tiers.<tier>.imports.may` | `_IMPORTS` |
| `tiers.<tier>.imports.also` | `_IMPORTS` |

`tiers.<tier>.imports` itself needs nothing. A language that lacks a fact of `_TYPES_ONLY` and a profile with a tier
`types_only` gets its shortfall at `tiers.<t>.imports.types_only` (the walker `profile_needs._configured` already
descends any `opens`).

### 2.5 Finding keys and texts

| Rule | Key in findings, before | After |
|---|---|---|
| `types-only` of a tier | `tiers.<t>.types_only` | `tiers.<t>.imports.types_only` |
| `must-import` of a tier | `tiers.<t>.must_import` | `tiers.<t>.imports.must` |
| `tiers` (import into the app) | `tiers` + `; tiers.<t>.may_also_import` per tier that sets it | `tiers` + `; tiers.<t>.imports.also` |
| `tiers` (others), every part rule | as today | unchanged |

Sentences and fixes are today's but for the key. Texts that cite a tier's import key name the new address:
`sentences.py:148` (`mirrored_may_import`'s tier half), `rules/domain/vocabulary.py:372-374` (its example
`parts.store.imports.may; tiers.unit.imports.also`), the docstrings of `expansion._tiers` and of
`profile_parsing.py` (lines 39-43: the tier line of the profile shape and its explanation). The `where` JSON fields
(`may_import`, `may_import_text`, `test.types_only`) keep their words (CS 615-618). Value and field names
(`Tier.may_also_import`, `CheckedTier.types_only`, ...) stay: release step 15 (CS 7 step 7).

### 2.6 `profile check`'s looser lines

`Loosened.key` (a JSON contract) for a tier:

| Before | After | Sentence |
|---|---|---|
| `types_only` | `imports.types_only` | `the {tier} tests may now call {what} (tiers.{tier}.imports.types_only)` |
| `may_also_import` | `imports.also` | `the {tier} tests may also import {what} (tiers.{tier}.imports.also)` |

What fires each is today's. A tier's `may` and `must` are not compared, as today (no new looser line: release step
16). `LOOSER` lists the new keys in place of the old; the module docstring and `domain/published.py:110-120` name them.

### 2.7 Profiles

Rewritten for the group with no other change, keys under `imports` in the order `may`, `also`, `must`,
`types_only`, the group written where the first old key stood:

- `xarch/architectures/cli.yaml:255`, `web.yaml:257`: `tiers.rendering`: `imports: {types_only: [controller]}`.
- `cli.yaml:270`, `web.yaml:272`: `tiers.guard`: `imports: {may: []}`.
- `architecture.yaml` (CS 725-728): `integration`: `imports: {also: [domain/values, domain/profile, domain/parsed,
  domain/outcomes], must: [controller]}`, its yaml comment kept above `also`; `wired`: `imports: {must: [bootstrap],
  types_only: [domain, logic, ports, services, controller, adapters, platform]}`; `guard`: `imports: {may: everything,
  types_only: [...]}`. `unit` writes none.
- Corpora profiles, as plain files: `stress.yaml` tiers (lines 212-262: `unit`, `integration`, `wired`, `guard`),
  `7cc6111.yaml` tiers (117-145), `df537ca.yaml` tiers (137-165).
- Every inline profile of the tests and `docs/examples/**` that writes a tier import key (O15).

### 2.8 Generated docs (CS 5.3, R3 O8)

`docs_template.py` prints the values (paths), so its lines do not move; its `{{guards}}` doc comment (line 33-35)
says "one line per tier with `types_only`" and becomes "`imports.types_only`" (a docstring, not output). The template
`xarch/architectures/testing.md` is edited by hand (it is the source, not a golden copy): line 47 says "A tier may name
more with `may_also_import`" and becomes `imports.also`; line 225 says "a tier that lost a `types_only` part or its
`uses.apply_never`, a target a tier's tests may also import (`may_also_import`)" and becomes "a tier that lost an
`imports.types_only` part ..., (`imports.also`)". Regenerate `docs/{cli,web,xarch}/testing.md`; the diff may move only
those two paragraphs (in `docs/cli` and `docs/web`: lines 57 and 370/371), in the copies that hold them. Any other
moved line is a defect to explain or fix.

### 2.9 Recorded corpora (CS 5.5, `test_recorded_corpora.py` docstring)

A change of wording only, edited by hand, the stress file decompressed to a scratch copy, edited, recompressed, the
text diff read (as `0f355bd` did):

- `stress-7cc6111.json.xz`: 694 × `(tiers.unit.types_only)` → `(tiers.unit.imports.types_only)`; 1 ×
  `(tiers.wired.must_import)` → `(tiers.wired.imports.must)`.
- `7cc6111.json`: 1 × `(tiers.wired.must_import)` → `(tiers.wired.imports.must)`.
- `df537ca.json`, `examples-cli.json`, `examples-web.json`: no tier import key; untouched. `tiers.<t>.uses.apply_never`
  lines stay.
- Anchored on `tiers.<t>.`; never a blind replace of `types_only)` (CS 974). Any recorded finding that differs in more
  than the key is a change of what a check finds: the plan reports it and does not edit it.

### 2.10 README and CHANGELOG (R3 O4, O5)

README: the profile block (line 122-123) writes a tier as `{proves, litmus, uses: {apply_never}, plain_tables, folder,
imports: {may, also, must, types_only}, docs}`; the rule table's key column (299, 301, 304) names `tiers.imports.may`,
`tiers.imports.also`, `tiers.imports.types_only`, `tiers.imports.must`; the `Loosened` keys and looser list (393-394,
439-441) name `imports.types_only` and `imports.also`. `where`'s JSON field names stay. CHANGELOG, under
`[Unreleased]`: the 4.5 entry's sentences "a tier's `types_only` list stays" and "the tier keys do not change" (line
64-72) are rewritten, and "Changed" says: a tier's `may_import`, `may_also_import`, `must_import`, `types_only` move
into `imports: {may, also, must, types_only}`; findings and the `Loosened` keys `imports.types_only`, `imports.also`
name the new addresses; the old keys are refused with the form that replaces them; rule ids and `where` unchanged.

## 3. Gates

Each passes on this branch alone with the full suite green:

- `uv run pytest -q` (over two minutes: run in the background, read at the end)
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check` (never `--fix`)
- `uv run xarch profile check architecture.yaml`

And the re-grep, scoped to tiers: `git grep -nE "may_also_import|^\s+(types_only|must_import|may_import):"` over
`xarch/ tests/ README.md CHANGELOG.md docs/ architecture.yaml` finds, for a tier, only the retired table, the refusal
tests, keys nested under `imports`, Python identifiers (fields, the `where` JSON field `test.types_only`), and
`docs/superpowers/**` (history, left alone).

## 4. Project rules

No comments in xarch's code (docstrings only; a yaml comment in a data file is not code); never `ruff --fix`; tests
written first; examples simple, with absolute `app.` imports; recorded corpora edited by hand only, as 2.9 says;
Python only in the reader adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays out of
commits; nothing is pushed; golden docs regenerated, never edited.

## 5. Tests

Each names its tier: **unit** (one module's pure logic, no I/O), **adapter** (one adapter's translation), **wired**
(the app through `xarch.bootstrap.app`, its CLI or controllers, on real files).

Wired first, `tests/bootstrap/` (it holds behavior across the change, so it must pass before and after):

1. `test_bundled_imports.py`, extended, written first and passing on the code before the change: for `cli`, `web` and
   `architecture.yaml`, each tier's import rules, as `profile explain` lists the checks of `tiers.<t>.imports.*` (before:
   of the old address), are the same text but for the key; and `where --format json` on a test file of each of xarch's
   tiers gives the same `may_import`, `may_import_text` and `test.types_only` before and after (literals recorded by
   hand from the pre-change run). Wired: it reads the bundled profiles as they ship.

Parsing, `tests/modules/spec/application/logic/` (unit: the parser is pure logic over a document):

2. `test_retired_keys.py`: each of `may_import`, `may_also_import`, `must_import`, `types_only` on a tier → its hint of
   2.2 with `{use}`; all four together → four problems, sorted; the part entries of the same names keep their hints.
   Replaces today's assertion that the four tier keys load.
3. `test_tiers.py` / `test_profile_parsing_tests.py`: `imports: {may, also, must, types_only}` gives the `Tier` values
   the old keys gave for the same lists; no `imports` gives the empties; `imports: {}` → "says nothing ..."; `imports:
   [x]`, `imports: true`, `imports: null` → "must be a map ..."; `imports: {libraries: [x]}` → plain unknown key ending
   "use also, may, must, types_only"; the tier "use ..." list of an unknown tier key names `imports`.
4. `test_tiers.py`: `imports.may` without a `folder` → the allowance refusal at `tiers.<t>.imports.may`; `imports:
   {may: []}` and `{may: everything}` with a folder load. (`tests/bootstrap/test_tier_folder.py`, wired, keeps holding
   what a folder tier's tests may import on real files, its profiles rewritten.)
5. `test_targets_written.py` / `test_tiers.py`: `also: everything` and a non-list `also` → today's texts at
   `tiers.<t>.imports.also`; `{controller: types_only}` in a tier's `may` or `also` → today's non-target refusal (no
   mark on a tier).
6. `test_tiers.py`: `must` / `types_only` empty, not a list, an undeclared part, a part twice → today's texts at the new
   addresses.
7. `test_profile_needs.py`: a language lacking a `_TYPES_ONLY` fact and a tier `imports.types_only` → shortfall at
   `tiers.<t>.imports.types_only`; `imports.must` likewise at its address.
8. `test_looseness.py`: a part dropped from a tier's `imports.types_only` → key `imports.types_only` and the new
   sentence; a target added to `imports.also` → key `imports.also` and its sentence.
9. `test_key_catalogue.py`, `test_explain.py`: the five new addresses have texts and the rules of 2.3; the four old
   tier addresses answer from the retired table; one text per key.

Domain, `tests/modules/spec/domain/test_profile_keys.py` (unit): the scope `tiers.<tier>.imports` exists with `may`,
`also`, `must`, `types_only`; the four keys are gone from `TIER` and present in `RETIRED` under `TIER`.

Rules, `tests/modules/rules/application/logic/` (unit: expansion over a built `Profile`):

10. `test_types_only.py`, `test_must_import.py`, `test_tier_imports.py`, `test_expansion.py`: a tier's types-only
    finding keyed `tiers.<t>.imports.types_only`, must-import `tiers.<t>.imports.must`, the tiers import rule
    `tiers; tiers.<t>.imports.also` for a tier with `also`; sentences unchanged otherwise.
11. `test_expandable.py`: `KEYS` holds `tiers.imports.also`, `tiers.imports.types_only`, `tiers.imports.must` and not
    the old.
12. `test_sentences.py`: `mirrored_may_import` text names `tiers.<t>.imports.also`.

Wired, `tests/bootstrap/` and `tests/cli/`:

13. `test_profile_explain.py`: `profile explain tiers.imports.also` and `tiers.may_also_import` (retired hint), exit
    codes as today.
14. `test_docs_templates.py` (or `test_docs.py`): the golden copies, regenerated, equal byte for byte (diff read per
    2.8).
15. `test_recorded_corpora.py`: the corpora replay with the edited profiles and findings (2.9).
16. `test_needs_agree.py`: `EVERY_KEY` writes a tier's `imports` with `may` (on a folder tier), `also`, `must`,
    `types_only`.
17. `test_bundled_tiers.py`, `test_bundled_architectures.py`, `test_rule_ids.py`, `tests/architecture/test_readme.py`:
    pass with the bundled profiles rewritten.
18. Every other test with an inline profile writing a tier import key (the files the exploration lists, among them
    `tests/architecture/test_language_seam.py`, `tests/cli/reports/test_where_report.py`,
    `test_vocabulary_report.py`, `tests/modules/spec/application/test_origin.py`): rewritten for the group (O15), each
    edit a key move only. Tests that build `Tier` / `CheckedTier` values by keyword keep their field names.

## 6. Risks the plan must settle

- `keys.yaml` and `key_table.py` change in one commit (the catalogue, needs and explain tests read both).
- The tier parser today reads `may_import` only when `folder` is in the spec and refuses it otherwise; keep both arms at
  the new address, and keep `may` read with `mirrored=False` and `also` with `mirrored=True`.
- Reuse the existing `_group` helper (profile_parsing.py:506) or a sibling of `imports_written.group`; its texts must be
  exactly 2.2's ("must be a map of may, also, must and types_only, such as {must: [<part>]}"), so `_group`'s generic
  "must be a mapping {...}" text does not fit as is.
- The `tiers` rule key concatenates one `; tiers.<t>.imports.also` per tier that sets it; the recorded corpora hold none
  of these, so only unit tests pin it.
- The part `Retired(PART, "types_only", ...)` and the new `Retired(TIER, "types_only", ...)` share a name; `advice`
  reads by scope, so check each scope gets its own hint.
- Every inline profile writing a tier import key is touched; the plan lists them by grep, not by memory.

## 7. Out of scope

- References inside `imports` (`parts.controller`, `module.domain`) and CS 640-641's refusals: story 8, release step 24.
- Renaming internal fields and functions (`Tier.may_import`, `may_also_import`, `must_import`, `types_only`,
  `CheckedTier`): release step 15.
- New looser lines (a tier's `may` or `must`): release step 16.
- A mark (`{x: types_only}`) on a tier's entries (dodge, CS 966).
- Any part key; `where`'s JSON fields; rule ids; the README id list.
- Retired hints for words never valid on a tier (`libraries`, `apply_never` under `imports`).

## 8. Plan hand-off

The plan follows `writing-plans` (header, global constraints, review focus, bite-sized TDD tasks with exact files and
code, commits per task), modelled on `docs/superpowers/plans/4-5-spec-a-part-s-912dfd81.md`. Suggested order, each
task green on the full suite at its end: (1) the wired hold of 5.1 against today's code; (2) `profile_keys` scope and
retired entries, `key_table` rows and needs, `keys.yaml`, the parser reading `tiers.<t>.imports`, every profile and
inline test profile rewritten, rules still keyed by the old strings; (3) finding keys, `KEYS`, sentences, vocabulary,
corpora findings edited; (4) looseness keys and sentences, `published.py`; (5) docs template comment, `testing.md`
template, golden docs regenerated and read, README, CHANGELOG; then the gates. The plan may merge or split these as the
gates require.

## 9. Dodges (card; CS 948-976)

- A mode on tiers beside their `types_only` list (CS 966): a map entry in a tier's `may`/`also` stays refused.
- Loosening the "use ..." lists in tests in place of editing each (CS 975).
- Accepting the old tier keys as aliases or with a warning.
- Keeping `Loosened` keys or finding keys on the old words.
- A blind replace of `types_only)` in recorded findings.
- Renaming rule ids or `where`'s JSON fields.
- Spelling entries as references in this step.
