# 4.6 A tier's import keys move into its `imports` group Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A tier writes `imports: {may, also, must, types_only}` in place of `may_import`, `may_also_import`,
`must_import` and `types_only`. The four old tier keys are refused with the form that replaces them. Findings,
`profile explain` and `profile check` name the new addresses. Every bundled profile, and xarch's own, finds the same
findings, but for the key.

**Architecture:** spec reads a tier's group with the helper that reads a part's, `imports_written.group`, made to take
the scope and example of the group it reads. Its texts come from the key table, so each scope gets its own words. The
tier parser then reads `may`, `also`, `must` and `types_only` from the group with today's code, at the new addresses.
The key table opens the scope `tiers.<tier>.imports`, with the facts the old keys needed. The four old names go into
the retired table under the scope `TIER`. rules keys its tier findings by the new addresses. Looseness says its two
tier lines under `imports.types_only` and `imports.also`. The internal names (`Tier.may_import`,
`.may_also_import`, `.must_import`, `.types_only`, `CheckedTier`) stay.

**Tech Stack:** Python 3.13, uv, pytest, ruff, PyYAML, typer's CliRunner; xarch's own `xarch check` and
`xarch profile check`.

**Spec:** `docs/superpowers/specs/4-6-spec-a-tier-s-20b1e1ce.md`. It is copied in full below. Section numbers in this
plan are the spec's.

<details>
<summary>The spec, verbatim</summary>

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

</details>

## Global Constraints

- No comments in xarch's code (docstrings only; a yaml comment in a data file is not code); never `ruff --fix`.
- Tests written first, each seen failing for the right reason; examples simple, with absolute `app.` imports.
- Recorded corpora (`tests/bootstrap/corpora/`) are edited by hand only, and only as spec 2.9 says. Each replacement
  is anchored on `(tiers.<t>.`. Never a blind replace of `types_only)` (CS 974). The stress file is decompressed to a
  scratch copy, edited, and recompressed, and the text diff is read.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`.
- `.claude/` stays out of commits; nothing is pushed.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never hand-edited (R3 O8). Their diff may move only
  the two paragraphs of spec 2.8, in the copies that hold them (`docs/cli` and `docs/web`: lines 57 and 370/371).
- README and CHANGELOG lines go under `## [Unreleased]` (R3 O4, O5).
- Every inline test profile that writes a tier's import keys is rewritten for the group in this step (R3 O15). Each
  edit is a key move only.
- No compatibility window: the old tier keys are never accepted as aliases or with a warning.
- Rule ids, `where`'s JSON fields (`may_import`, `may_import_text`, `test.types_only`), the tier's other keys
  (`proves`, `litmus`, `uses`, `plain_tables`, `folder`, `docs`) and every part key do not change.
- Internal Python names (`Tier.may_import`, `.may_also_import`, `.must_import`, `.types_only`, `CheckedTier` fields,
  functions such as `_must_import_tiers`) stay: release step 15.
- Entries keep today's spelling: `may` and `also` take the target grammar (`[domain/values]`, `everything`), `must` and
  `types_only` bare part names (`[controller]`). References are story 8.
- A map entry such as `{controller: types_only}` in a tier's `may` or `also` stays refused with today's text (dodge,
  CS 966).
- The tier "use ..." list is `use docs, folder, imports, litmus, plain_tables, proves, uses`. Each test that spells
  the old list is edited, never loosened (CS 975).
- Gates: `uv run pytest -q` (over two minutes: in the background), `uv run xarch check`, `uv run xarch check --strict`,
  `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## Review Focus

1. **A retired tier key written beside the group** (`must_import: [store]` and `imports: {must: [ghost]}` on one
   tier). A person expects exactly the retired-key problem, with `imports` still read and checked. Pinned in Task 2
   (`test_tiers.py::test_a_retired_key_beside_the_group_is_its_own_problem_and_the_group_is_still_read`).
2. **A folder tier writing both `may` and `also`** (`guard: {folder: architecture, imports: {may: [shared], also:
   [store@any]}}`). Today a folder tier may set both keys. A person expects both to load, each giving the value it gave
   before. Pinned in Task 2 (`test_tiers.py::test_a_folder_tier_may_write_may_and_also_together`).
3. **An empty `also` list** (`imports: {also: []}`). Today `may_also_import: []` loads and adds nothing. A person
   expects the same, not "says nothing" (the group holds a key). Pinned in Task 2
   (`test_tiers.py::test_an_empty_also_loads_and_adds_nothing`).
4. **A part's retired names written in a tier's group** (`imports: {libraries: [yaml]}`, `{never: pure}`). A person
   expects the plain unknown-key problem with the tier's own "use ..." list. They must never get the hint of the
   part's group, which would tell them to write a key a tier does not have. Pinned in Task 2
   (`test_tiers.py::test_the_group_is_refused_when_written_wrong`, ids `libraries` and `never`).
5. **`profile explain` with a tier name in the new address** (`tiers.unit.imports.must`). A person expects the key's
   text, as for `tiers.unit.uses.apply_never` today. Pinned in Task 2
   (`test_profile_explain.py::test_a_key_of_a_tier_s_group_is_explained_with_or_without_a_tier_name`).

---

### Task 1: A wired test holds what xarch's tiers import to what they import today

Spec: test 1. The test is written first and passes on the code before the change. Task 2 changes only `TIER_KEYS`.

**Files:**
- Modify: `tests/bootstrap/test_bundled_imports.py`

**Interfaces:**
- Produces: in `tests/bootstrap/test_bundled_imports.py`, the dict `TIER_KEYS = {"types_only": ..., "must": ...,
  "also": ..., "tiers": "tiers"}` of explain addresses, and `explained(address: str, profile: str) -> tuple[int, str]`.
  Task 2 changes only `TIER_KEYS`.

- [ ] **Step 1: Extend the test, with the literals recorded from today's code**

The literals were recorded from the code at `080953d` with `xarch where --format json` and
`xarch profile explain <key> --rule --profile <profile> --format json`. Each `checks` text is hashed (SHA-256, first 16
hex digits; `e3b0c44298fc1c14` is the empty text of a profile that sets no such key). Each `may_import` list of
`where` is hashed as `json.dumps(found["may_import"], sort_keys=True)`. The rules texts write `{key}`, not the key, so
the hashes do not move when the keys do.

In `tests/bootstrap/test_bundled_imports.py`:

1. Replace the module docstring with:

```python
"""What a part, or a tier, of a bundled profile or of xarch's own may import, must import and may import from outside
stays what it was before the import keys moved into `imports` groups: `where` says the same of a file of every part of
xarch's own profile and of a test of each of its tiers, and the rules the keys expand to are, as checks, the same text
for each profile but for the key."""
```

2. Replace the function `explained` and the test that calls it with:

```python
def explained(address: str, profile: str) -> tuple[int, str]:
    found = json.loads(runner.invoke(app, ["profile", "explain", address, "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    text = found["checks"].replace(".imports.libraries)", ".libraries)")
    return found["rules"], hashlib.sha256(text.encode()).hexdigest()[:16]
```

```python
@pytest.mark.parametrize("profile, key", list(RULES))
def test_each_key_of_the_group_expands_to_the_rules_of_before(profile, key):
    assert explained(KEYS[key], profile) == RULES[profile, key]
```

3. After the `RULES` dict and its docstring, add:

```python
TIER_KEYS = {"types_only": "tiers.types_only", "must": "tiers.must_import", "also": "tiers.may_also_import",
             "tiers": "tiers"}
"""The address `profile explain` is asked for each key of a tier's group that rules are keyed by, and for `tiers`,
whose rule a tier's `also` keys too."""
TIER_RULES = {
    ("cli", "types_only"): (1, "29bdb75af0440d40"), ("cli", "must"): (0, "e3b0c44298fc1c14"),
    ("cli", "also"): (0, "e3b0c44298fc1c14"), ("cli", "tiers"): (3, "07ebde882b66c963"),
    ("web", "types_only"): (1, "29bdb75af0440d40"), ("web", "must"): (0, "e3b0c44298fc1c14"),
    ("web", "also"): (0, "e3b0c44298fc1c14"), ("web", "tiers"): (3, "07ebde882b66c963"),
    ("architecture.yaml", "types_only"): (2, "329ba93378533550"), ("architecture.yaml", "must"): (2, "0083c4a5a67770c5"),
    ("architecture.yaml", "also"): (1, "297bcd04b21ab4d8"), ("architecture.yaml", "tiers"): (3, "07ebde882b66c963"),
}
"""For each profile and key of a tier: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change."""
TESTS = {"unit": "tests/modules/spec/domain/test_x.py", "integration": "tests/modules/spec/application/test_x.py",
         "wired": "tests/bootstrap/test_x.py", "guard": "tests/architecture/test_x.py",
         "wired, of cli": "tests/cli/test_x.py"}
"""A test of each tier of xarch's own profile, the wired one twice: once below bootstrap/, once mirroring cli/."""
TYPES = ["domain", "logic", "ports", "services", "controller", "adapters", "platform"]
TIER_WHERE = {
    "unit": ("unit", "its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", [], "5e0f441d9899ecd1"),
    "integration": ("integration", "its own module's `application/controller.py`, `application/services/`, `contract/` "
                    "and `domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`, its own module's "
                    "`domain/values`, `domain/profile`, `domain/parsed` and `domain/outcomes`", [], "ae600445e22537b0"),
    "wired": ("wired", "everything", TYPES, "2a05a9860791084b"),
    "guard": ("guard", "everything", TYPES, "4f53cda18c2baa0c"),
    "wired, of cli": ("wired", "`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, "
                      "`kernel/`, `kernel/logic/`", TYPES, "46205533adc1e5b6"),
}
"""What `where` said of each test before the change: its tier, may_import_text, test.types_only, and the first 16 hex
digits of the SHA-256 of its may_import list."""
```

4. At the end of the file, add:

```python
@pytest.mark.parametrize("test", list(TESTS))
def test_where_says_what_a_test_of_each_tier_of_xarch_may_import_as_before(test):
    found = json.loads(runner.invoke(app, ["where", TESTS[test], "--format", "json"]).output)
    reached = hashlib.sha256(json.dumps(found["may_import"], sort_keys=True).encode()).hexdigest()[:16]
    assert (found["tier"]["name"], found["may_import_text"], found["test"]["types_only"], reached) == TIER_WHERE[test]


@pytest.mark.parametrize("profile, key", list(TIER_RULES))
def test_each_key_of_a_tier_s_group_expands_to_the_rules_of_before(profile, key):
    assert explained(TIER_KEYS[key], profile) == TIER_RULES[profile, key]
```

- [ ] **Step 2: Run it on today's code**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_bundled_imports.py`
Expected: PASS (41 tests: the 24 of before and 17 new). If a hash differs, the code has moved since `080953d`.
Re-record that literal on this commit, before anything else changes, and say so in the commit message.

- [ ] **Step 3: Commit**

```bash
git add tests/bootstrap/test_bundled_imports.py
git commit -m "A wired test holds what where says a test of each tier of xarch's own profile may import, and the rules types_only, must_import, may_also_import and tiers expand to in the bundled profiles and xarch's own, to what they are before a tier's import keys move into its imports group"
```

---

### Task 2: The `imports` group replaces the four tier keys

Spec: 2.1-2.5, 2.7, 2.9; tests 1 (keys switched), 2-7, 9-13, 15-18; the domain test. This is one task because the suite
is green only when the parser, the key table, every profile and the rule keys move together. `profile explain
tiers.imports.must --rule` must find the rules keyed `tiers.<t>.imports.must`, and the old address no longer exists.

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py` (scope `TIER_IMPORTS`; `SCOPES`; `RETIRED`)
- Modify: `xarch/modules/spec/domain/key_table.py` (the `TIER` rows, the `TIER_IMPORTS` rows, `NEEDS` lines 246-250)
- Modify: `xarch/architectures/presets/format/keys.yaml` (in the same commit as `key_table.py`: the catalogue test reads both)
- Modify: `xarch/modules/spec/application/logic/imports_written.py` (`group` takes the scope and the example)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (docstring lines 39-43; the import of `TIER_IMPORTS`; `_tier` lines 645-657)
- Modify: `xarch/modules/rules/application/logic/expansion.py` (lines 137-142, 163-167, 188, 347-359, 426-432)
- Modify: `xarch/modules/rules/application/logic/sentences.py:148`
- Modify: `xarch/modules/rules/domain/vocabulary.py:372-374`
- Modify (profiles): `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`, `tests/bootstrap/corpora/stress.yaml`
- Modify (recorded findings, anchored replace): `tests/bootstrap/corpora/7cc6111.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz`
- Modify (tests): `tests/bootstrap/test_bundled_imports.py` (`TIER_KEYS` only), `tests/modules/spec/domain/test_profile_keys.py`, `tests/modules/spec/application/logic/test_tiers.py`, `test_profile_parsing_tests.py`, `test_profile_parsing_substance.py`, `test_retired_keys.py`, `test_never_use.py`, `test_profile_needs.py`, `test_targets_written.py`, `test_checked_tier.py`, `test_looseness.py` (profiles only), `tests/modules/spec/application/origins.py`, `tests/modules/spec/application/test_origin.py` (profile only), `tests/modules/spec/application/test_explain.py`, `tests/modules/rules/application/logic/test_types_only.py`, `test_must_import.py`, `test_tier_imports.py`, `test_sentences.py`, `test_expandable.py`, `test_expansion.py`, `tests/bootstrap/test_needs_agree.py`, `test_rule_ids.py`, `test_source_checks.py`, `test_profile_explain.py`

**Interfaces:**
- Consumes: `targets_written.may_import(value, owner, parts, declared, where, problems, patterns=False, mirrored=False) -> tuple[Target, ...]`; `ck.part_names(value, declared, where, problems) -> list[str]`; `ck.unknown_keys(spec, known, where, scope)`; `key_lookup.keys_of(scope) -> tuple[Key, ...]`, `key_lookup.names_of(scope) -> set[str]`.
- Produces:
  - `profile_keys.TIER_IMPORTS = "tier.imports"`, `SCOPES[TIER_IMPORTS] == "tiers.<tier>.imports"`.
  - `imports_written.group(spec: Mapping, where: str, problems: list[str], scope: str = PART_IMPORTS, example: str = "{may: [<part>]}") -> Mapping`.
  - Rule keys `tiers.<t>.imports.types_only`, `tiers.<t>.imports.must`, and `tiers` + `; tiers.<t>.imports.also` per
    tier that sets `also`. `expansion.KEYS` holds `tiers.imports.also`, `tiers.imports.types_only`,
    `tiers.imports.must` in the places of the old three.
  - `Tier` and `CheckedTier` values and field names unchanged.
  - The `Loosened` keys `types_only` and `may_also_import` are not changed in this task (Task 3 changes them).

- [ ] **Step 1: Write the failing domain test for the scope and the retired entries**

In `tests/modules/spec/domain/test_profile_keys.py`, add `TIER_IMPORTS` to the names imported from
`xarch.modules.spec.domain.profile_keys` (keep the list sorted as it is written). Then:

1. In `test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules`
   (line 50), the expected tuple ends with the entry `Retired(PART_IMPORTS, "types_only", ...)`. Add these four after
   it, before the closing parenthesis:

```python
        Retired(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
        Retired(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}"),
        Retired(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
        Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}"))
```

   (the closing parenthesis moves from the old last entry to the new one).

2. In `test_imports_opens_a_scope_of_may_must_and_libraries_and_may_opens_the_scope_of_its_mark` (line 130), replace
   the last line

```python
    assert {"may_import", "must_import", "types_only", "may_also_import"} <= set(names(TIER))
```

   with

```python
    assert not {"may_import", "must_import", "types_only", "may_also_import"} & set(names(TIER))
```

3. At the end of the file, add:

```python
def test_a_tier_s_imports_opens_a_scope_of_may_also_must_and_types_only():
    def held(scope):
        return [(key.name, key.rules) for key in KEYS if key.scope == scope]

    imports = next(key for key in KEYS if (key.scope, key.name) == (TIER, "imports"))
    assert (imports.opens, imports.rules) == (TIER_IMPORTS, ("tiers", "must-import", "types-only"))
    assert held(TIER_IMPORTS) == [("may", ("tiers",)), ("also", ("tiers",)), ("must", ("must-import",)),
                                  ("types_only", ("types-only",))]
    assert SCOPES[TIER_IMPORTS] == "tiers.<tier>.imports"
    assert [key.name for key in KEYS if key.scope == TIER] == ["proves", "litmus", "uses", "plain_tables", "folder",
                                                               "imports", "docs"]


def test_the_tier_import_keys_need_what_the_keys_they_replace_needed():
    imports = ("import", "import.relative")
    assert {address: facts for address, facts in NEEDS.items() if address.startswith("tiers.<tier>.imports")} == {
        "tiers.<tier>.imports.types_only": ("call", "use", "module_functions", "import.resolved"),
        "tiers.<tier>.imports.must": (*imports, "function.statements", "file"),
        "tiers.<tier>.imports.may": imports,
        "tiers.<tier>.imports.also": imports}
    assert not [address for address in NEEDS if address.startswith("tiers.<tier>.") and address.count(".") == 2
                and address.rsplit(".", 1)[1] in ("may_import", "may_also_import", "must_import", "types_only")]
```

- [ ] **Step 2: Run it to see it fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py`
Expected: FAIL with `ImportError: cannot import name 'TIER_IMPORTS'`.

- [ ] **Step 3: Add the scope and the retired entries**

In `xarch/modules/spec/domain/profile_keys.py`, after `TIER_USES = "tier.uses"`:

```python
TIER_IMPORTS = "tier.imports"
```

In `SCOPES`, after `TIER_USES: "tiers.<tier>.uses",`:

```python
    TIER_IMPORTS: "tiers.<tier>.imports",
```

At the end of `RETIRED`, after the entry `Retired(PART_IMPORTS, "types_only", ...)` and before the closing
parenthesis, add the entries word for word (spec 2.2):

```python
    Retired(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
    Retired(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}"),
    Retired(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
    Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}"),
```

The part entry `Retired(PART, "types_only", ...)` stays. `retired` and `retired_at` read by scope, so each scope keeps
its own hint (spec risk 5; Step 7 pins both).

- [ ] **Step 4: Change the key table**

In `xarch/modules/spec/domain/key_table.py`, add `TIER_IMPORTS,` to the names imported from `profile_keys`, after
`TIER_DOCS,` (the list is sorted: `TIER`, `TIER_DOCS`, `TIER_IMPORTS`, `TIER_USES`).

Replace the ten `TIER` rows (lines 114-123) with:

```python
    Key(TIER, "proves", False, False),
    Key(TIER, "litmus", False, False),
    Key(TIER, "uses", opens=TIER_USES),
    Key(TIER, "plain_tables", rules=("scenario-coverage",)),
    Key(TIER, "folder", rules=("tiers", "test-tree")),
    Key(TIER, "imports", rules=("tiers", "must-import", "types-only"), opens=TIER_IMPORTS),
    Key(TIER, "docs", False, False, opens=TIER_DOCS),
```

After the line `    Key(TIER_USES, "apply_never", rules=("never-use",)),` and its blank line, insert:

```python
    Key(TIER_IMPORTS, "may", rules=("tiers",)),
    Key(TIER_IMPORTS, "also", rules=("tiers",)),
    Key(TIER_IMPORTS, "must", rules=("must-import",)),
    Key(TIER_IMPORTS, "types_only", rules=("types-only",)),

```

In `NEEDS`, replace the five lines

```python
    "tiers.<tier>.types_only": _TYPES_ONLY,
    "tiers.<tier>.must_import": (*_IMPORTS, "function.statements", "file"),
    "tiers.<tier>.plain_tables": ("function.tables", "function.blocks", "function.expressions"),
    "tiers.<tier>.may_import": _IMPORTS,
    "tiers.<tier>.may_also_import": _IMPORTS,
```

with

```python
    "tiers.<tier>.imports.types_only": _TYPES_ONLY,
    "tiers.<tier>.imports.must": (*_IMPORTS, "function.statements", "file"),
    "tiers.<tier>.plain_tables": ("function.tables", "function.blocks", "function.expressions"),
    "tiers.<tier>.imports.may": _IMPORTS,
    "tiers.<tier>.imports.also": _IMPORTS,
```

`tiers.<tier>.imports` itself needs nothing (spec 2.4).

- [ ] **Step 5: Change the catalogue texts (`keys.yaml`), in the same commit**

`catalogue.texts` must list the addresses in the order of `KEYS` (`test_key_catalogue.py`, line 39). The new order of
the tier texts is: `proves`, `litmus`, `uses`, `plain_tables`, `folder`, `imports`, `docs`, `docs.subject` ...
`docs.helpers`, `uses.apply_never`, `imports.may`, `imports.also`, `imports.must`, `imports.types_only`, then
`testing.files`. In `xarch/architectures/presets/format/keys.yaml`:

1. The `tiers` text (line 209): "then what its tier's\n      `may_also_import` adds" becomes "then what its tier's
   `imports.also` adds". The block is folded (`>-`), so the line may be rewrapped. Keep it within the file's width.
2. The `parts.<part>.imports.may.types_only` text (lines 351-352): "A tier's `types_only` is the list form of the same
   idea, read on a test" becomes "A tier's `imports.types_only` is the list form of the same idea, read on a test".
3. Delete the whole blocks `tiers.<tier>.types_only` (from line 597), `tiers.<tier>.must_import` (from line 609),
   `tiers.<tier>.may_import` (from line 632) and `tiers.<tier>.may_also_import` (from line 643, through the
   `tests: unit` line before `tiers.<tier>.docs:`). Each block runs from its address line to the line before the next
   address at the same indent.
4. Between the block `tiers.<tier>.folder` and the block `tiers.<tier>.docs`, insert:

```yaml
  tiers.<tier>.imports:
    meaning: what its tests may import, may also import, must import one of, and may import only as types
    accepts: >-
      a map {may, also, must, types_only}, at least one of them, in any order: `may` what the tests in its folder may
      import of the app (only for a tier with a `folder`), `also` what its tests may import besides, `must` the parts
      one of which each of its test files reaches, `types_only` the parts its tests may import only as types. Without
      `imports`, a test imports what the part it mirrors may, and a test of the tier's folder nothing of the app
    example: |
      <<testing>>
      tiers:
        unit:
          imports:
            must: [documents]
      <<tiered-part>>
```

5. After the block `tiers.<tier>.uses.apply_never` and before `testing.files:`, insert:

```yaml
  tiers.<tier>.imports.may:
    meaning: what the tests in its folder may import of the app
    accepts: as a part's `imports.may`, with no mode; only for a tier with a `folder`
    example: |
      <<testing>>
      tiers:
        unit: {}
        guard:
          folder: architecture
          imports:
            may: everything
      <<tiered-part>>
  tiers.<tier>.imports.also:
    meaning: what its tests may also import of the app
    accepts: >-
      targets, as a part's `imports.may`, read from the instance a test mirrors, and added to what each test of the
      tier may import of the app, such as the values a test builds its fakes' answers with; not `everything`. A target
      the bundled profile's tier does not give is listed by `profile check` as looser
    example: |
      <<testing>>
      tiers:
        unit:
          imports:
            also: [core]
      parts:
        core:
          path: core
          role: the rules of the documents
          tests: unit
        documents:
          path: documents
          role: the documents
          tests: unit
  tiers.<tier>.imports.must:
    meaning: what each of its test files has to reach
    accepts: >-
      [<part>, ...]: each test file of the tier (a file whose name `testing.files` matches) imports from one of those
      parts, in any instance, or imports test code that is no test file and does, however far the chain goes; a test
      file with no function holding a real statement is exempt, and a file failing is reported once, as a whole. Silent
      on what a test is handed without importing it, such as a fixture
    example: |
      <<testing>>
      tiers:
        unit:
          imports:
            must: [documents]
      <<tiered-part>>
  tiers.<tier>.imports.types_only:
    meaning: the parts its tests may import only as types
    accepts: >-
      [<part>, ...]: a test may import them to annotate, never to call: `def build(c: Controller)` is fine,
      `Controller(...)` is not; a plain function of such a part may not be referenced at all, while `isinstance`,
      exception matching and enum members stay allowed
    example: |
      <<testing>>
      tiers:
        unit:
          imports:
            types_only: [documents]
      <<tiered-part>>
```

   (The `meaning` and `accepts` of the four are the old keys' texts, word for word. Only the examples write the group.)
6. Run `grep -nE "may_import|may_also_import|must_import|types_only" xarch/architectures/presets/format/keys.yaml`.
   Every hit left must be a part's `imports.may` text, the mark `types_only`, or an `imports.*` address of a tier.

- [ ] **Step 6: Run the key table and catalogue tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_key_catalogue.py`
Expected: PASS. If the catalogue test fails on the order of `catalogue.texts`, move the new blocks in `keys.yaml` until
the order of addresses matches `[key.address for key in KEYS]`.

- [ ] **Step 7: Write the failing parser tests**

In `tests/modules/spec/application/logic/test_tiers.py`, add `from xarch.profile_values.placement import Target` to
the imports. After the helper `with_docs`, add:

```python
TIER_USE = "use docs, folder, imports, litmus, plain_tables, proves, uses"
"""What every unknown-key problem of a tier ends with."""
NO_MAP = "must be a map of may, also, must and types_only, such as {must: [<part>]}"


def with_imports(imports) -> dict:
    """covered(), its integration tier writing the imports given."""
    document = covered()
    document["tiers"]["integration"]["imports"] = imports
    return document


def with_guard(imports) -> dict:
    """covered(), with a third tier, guard, whose folder is architecture, writing the imports given."""
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture", "imports": imports}
    return document
```

Replace `test_a_bad_types_only_entry_is_refused` (lines 63-74) with:

```python
@pytest.mark.parametrize("types_only, expected", [
    pytest.param(["repo", "service"], ["layered.yaml: tiers.integration.imports.types_only: no part named 'repo'"],
                 id="a part that does not exist is refused"),
    pytest.param(["service", "service"],
                 ["layered.yaml: tiers.integration.imports.types_only: 'service' is listed twice"],
                 id="a part listed twice is refused"),
    pytest.param("service", ["layered.yaml: tiers.integration.imports.types_only: must be a list of part names"],
                 id="a part given as one text is refused"),
    pytest.param([], ["layered.yaml: tiers.integration.imports.types_only: must be a list of part names"],
                 id="no part at all is refused"),
])
def test_a_bad_types_only_entry_is_refused(types_only, expected):
    assert problems(with_imports({"types_only": types_only})) == expected
```

At the end of the file, add:

```python
def test_the_group_gives_the_values_the_old_keys_gave_for_the_same_lists():
    document = with_guard({"may": ["shared", "api@any"]})
    document["tiers"]["integration"]["imports"] = {"also": ["service", "shared"], "must": ["api", "store"],
                                                   "types_only": ["service", "store"]}
    tiers = {tier.name: tier for tier in parsed(document).tiers}
    integration = tiers["integration"]
    assert (integration.may_import, integration.may_also_import, integration.must_import, integration.types_only) == (
        None, (Target("service", "own"), Target("shared")), ("api", "store"), ("service", "store"))
    assert tiers["guard"].may_import == (Target("shared"), Target("api", "any"))


def test_a_tier_with_no_imports_has_what_leaving_the_old_keys_out_gave():
    assert [(t.may_import, t.may_also_import, t.must_import, t.types_only) for t in parsed(covered()).tiers] == [
        (None, (), (), ()), (None, (), (), ())]


def test_the_order_of_the_keys_of_the_group_does_not_matter_and_the_order_of_entries_is_kept():
    first = parsed(with_imports({"types_only": ["store", "service"], "must": ["store", "api"]})).tiers[1]
    second = parsed(with_imports({"must": ["store", "api"], "types_only": ["store", "service"]})).tiers[1]
    assert first == second
    assert (first.must_import, first.types_only) == (("store", "api"), ("store", "service"))


@pytest.mark.parametrize("imports, problem", [
    pytest.param({}, "tiers.integration.imports: says nothing: write may, also, must or types_only, or drop it",
                 id="empty"),
    pytest.param(["store"], f"tiers.integration.imports: {NO_MAP}", id="a list"),
    pytest.param("store", f"tiers.integration.imports: {NO_MAP}", id="a string"),
    pytest.param(True, f"tiers.integration.imports: {NO_MAP}", id="true"),
    pytest.param(None, f"tiers.integration.imports: {NO_MAP}", id="null"),
    pytest.param({"libraries": ["yaml"]},
                 "tiers.integration.imports: unknown key 'libraries': use also, may, must, types_only", id="libraries"),
    pytest.param({"never": "pure"}, "tiers.integration.imports: unknown key 'never': use also, may, must, types_only",
                 id="never"),
    pytest.param({"apply_never": True},
                 "tiers.integration.imports: unknown key 'apply_never': use also, may, must, types_only",
                 id="apply_never"),
])
def test_the_group_is_refused_when_written_wrong(imports, problem):
    assert problems(with_imports(imports)) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("key, value, hint", [
    pytest.param("may_import", ["shared"], "moved in 0.3.0: write imports: {may: [...]}", id="may_import"),
    pytest.param("may_also_import", ["shared"], "moved in 0.3.0: write imports: {also: [...]}", id="may_also_import"),
    pytest.param("must_import", ["store"], "moved in 0.3.0: write imports: {must: [...]}", id="must_import"),
    pytest.param("types_only", ["store"], "moved in 0.3.0: write imports: {types_only: [<part>, ...]}",
                 id="types_only"),
])
def test_an_old_tier_key_is_refused_with_the_form_that_replaces_it(key, value, hint):
    assert problems(with_tier(**{key: value})) == [
        f"layered.yaml: tiers.integration: unknown key '{key}': {hint}; {TIER_USE}"]


def test_a_tier_writing_the_four_old_keys_gets_one_problem_for_each_in_sorted_order():
    document = with_tier(types_only=["store"], may_import=["shared"], must_import=["store"], may_also_import=["shared"])
    assert problems(document) == [
        f"layered.yaml: tiers.integration: unknown key 'may_also_import': moved in 0.3.0: write imports: "
        f"{{also: [...]}}; {TIER_USE}",
        f"layered.yaml: tiers.integration: unknown key 'may_import': moved in 0.3.0: write imports: {{may: [...]}}; "
        f"{TIER_USE}",
        f"layered.yaml: tiers.integration: unknown key 'must_import': moved in 0.3.0: write imports: "
        f"{{must: [...]}}; {TIER_USE}",
        f"layered.yaml: tiers.integration: unknown key 'types_only': moved in 0.3.0: write imports: "
        f"{{types_only: [<part>, ...]}}; {TIER_USE}"]


def test_a_retired_key_beside_the_group_is_its_own_problem_and_the_group_is_still_read():
    document = with_imports({"must": ["ghost"]})
    document["tiers"]["integration"]["must_import"] = ["store"]
    assert problems(document) == [
        f"layered.yaml: tiers.integration: unknown key 'must_import': moved in 0.3.0: write imports: "
        f"{{must: [...]}}; {TIER_USE}",
        "layered.yaml: tiers.integration.imports.must: no part named 'ghost'"]


def test_may_in_a_tier_with_no_folder_is_refused_at_its_address():
    assert problems(with_imports({"may": ["shared"]})) == [
        "layered.yaml: tiers.integration.imports.may: only a tier with a `folder` has an allowance of its own: "
        "without one, its tests import what the part they mirror may"]


@pytest.mark.parametrize("may, allowed", [
    pytest.param([], (), id="nothing"),
    pytest.param("everything", (Target("*"),), id="everything"),
])
def test_may_in_a_tier_with_a_folder_loads(may, allowed):
    assert parsed(with_guard({"may": may})).tiers[2].may_import == allowed


def test_a_folder_tier_may_write_may_and_also_together():
    guard = parsed(with_guard({"may": ["shared"], "also": ["store@any"]})).tiers[2]
    assert (guard.may_import, guard.may_also_import) == ((Target("shared"),), (Target("store", "any"),))


def test_an_empty_also_loads_and_adds_nothing():
    assert parsed(with_imports({"also": []})).tiers[1].may_also_import == ()


@pytest.mark.parametrize("imports, problem", [
    pytest.param({"also": "everything"}, "tiers.integration.imports.also: must be a list of targets such as "
                 "[<part>, shared/text, api@any]: `everything` is not taken, name each target the tests may also "
                 "import", id="also everything"),
    pytest.param({"also": ["shared", "everything"]}, "tiers.integration.imports.also: `everything` is not taken, "
                 "name each target the tests may also import", id="everything in a list of also"),
    pytest.param({"also": [{"store": "types_only"}]}, "tiers.integration.imports.also: {'store': 'types_only'} is not "
                 "a target: use <part>, <part>@any, optionally followed by /<path>", id="a mark in also"),
    pytest.param({"must": "store"}, "tiers.integration.imports.must: must be a list of part names",
                 id="must not a list"),
    pytest.param({"must": []}, "tiers.integration.imports.must: must be a list of part names", id="must empty"),
    pytest.param({"must": ["nowhere"]}, "tiers.integration.imports.must: no part named 'nowhere'",
                 id="must of no part"),
    pytest.param({"must": ["store", "store"]}, "tiers.integration.imports.must: 'store' is listed twice",
                 id="must twice"),
])
def test_each_key_of_the_group_is_refused_with_today_s_text_at_its_new_address(imports, problem):
    assert problems(with_imports(imports)) == [f"layered.yaml: {problem}"]


def test_a_mark_in_a_folder_tier_s_may_is_refused_as_any_entry_that_is_no_target():
    assert problems(with_guard({"may": [{"store": "types_only"}]})) == [
        "layered.yaml: tiers.guard.imports.may: {'store': 'types_only'} is not a target: use <part>, <part>@any, "
        "optionally followed by /<path>"]
```

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, rewrite each tier key as the group. Each
edit is a key move only:

- Line 132: `document["tiers"]["integration"]["types_only"] = ["service", "store"]` becomes
  `document["tiers"]["integration"]["imports"] = {"types_only": ["service", "store"]}`.
- Line 139: `document["tiers"]["guard"] = {"folder": "architecture", "may_import": ["shared", "api@any"]}` becomes
  `document["tiers"]["guard"] = {"folder": "architecture", "imports": {"may": ["shared", "api@any"]}}`.
- Line 146: `document["tiers"]["integration"]["may_also_import"] = [...]` becomes
  `document["tiers"]["integration"]["imports"] = {"also": ["service", "shared", "api@any"]}`.
- Line 155: `document["tiers"]["guard"]["may_import"] = "everything"` becomes
  `document["tiers"]["guard"]["imports"] = {"may": "everything"}`.
- The parametrize of `test_a_bad_tier_is_refused` (lines 181-200): the `colour` case ends
  `"use docs, folder, imports, litmus, plain_tables, proves, uses"`. Each case of a tier import key writes the group,
  and its expected text names the new address with the same words:

```python
    pytest.param({"colour": 1}, "layered.yaml: tiers.unit: unknown key 'colour': use docs, folder, imports, litmus, "
                                "plain_tables, proves, uses", id="an unknown key"),
```
```python
    pytest.param({"imports": {"types_only": ["repo"]}}, "layered.yaml: tiers.unit.imports.types_only: no part named "
                                                        "'repo'", id="types_only of no part"),
    pytest.param({"imports": {"may": ["shared"]}}, "layered.yaml: tiers.unit.imports.may: only a tier with a "
                                                   "`folder` has an allowance of its own: without one, its tests "
                                                   "import what the part they mirror may", id="may without a folder"),
    pytest.param({"imports": {"also": "everything"}}, "layered.yaml: tiers.unit.imports.also: must be a list of "
                                                      "targets such as [<part>, shared/text, api@any]: `everything` "
                                                      "is not taken, name each target the tests may also import",
                 id="also of everything"),
    pytest.param({"imports": {"also": ["shared", "everything"]}}, "layered.yaml: tiers.unit.imports.also: "
                                                                  "`everything` is not taken, name each target the "
                                                                  "tests may also import",
                 id="everything in a list of also"),
    pytest.param({"imports": {"also": ["repo"]}}, "layered.yaml: tiers.unit.imports.also: 'repo' names no part "
                                                  "'repo'", id="also of no part"),
    pytest.param({"imports": {"also": ["service@own"]}}, "layered.yaml: tiers.unit.imports.also: 'service@own' says "
                                                         "what a bare name already says: write service",
                 id="also of the mirrored instance written out"),
```

- `test_a_tier_folder_follows_the_rules_it_had_and_its_allowance_is_a_part_s_may_import` (line 209):
  `{"folder": "src/billing/api", "may_import": [...]}` becomes
  `{"folder": "src/billing/api", "imports": {"may": ["api", "service@own", "repo", "shared/"]}}`, and each of the four
  expected `tiers.guard.may_import:` becomes `tiers.guard.imports.may:` (the words after it stay).
- `test_tier_under_a_tier_is_only_unknown_with_the_plain_message` (line 343): the expected text becomes
  `"layered.yaml: tiers.unit: unknown key 'tier': use docs, folder, imports, litmus, plain_tables, proves, uses"`.

In `tests/modules/spec/application/logic/test_profile_parsing_substance.py`:
- Line 178: `document["tiers"]["integration"]["must_import"] = ["api", "store"]` becomes
  `document["tiers"]["integration"]["imports"] = {"must": ["api", "store"]}`.
- Line 185: `document["tiers"]["unit"]["must_import"] = ["ghost"]` becomes
  `document["tiers"]["unit"]["imports"] = {"must": ["ghost"]}`, and line 186's expected text becomes
  `"layered.yaml: tiers.unit.imports.must: no part named 'ghost'"`.

In `tests/modules/spec/application/logic/test_retired_keys.py`:
- Line 54: `TIER_USE = "docs, folder, imports, litmus, plain_tables, proves, uses"`.
- In the parametrize of `test_the_shipped_table_answers_each_name_in_its_scope`, replace the two cases
  `pytest.param(TIER, "types_only", "", id="the tier key types_only, a key")` and
  `pytest.param(TIER, "may_import", "", id="the tier key may_import, a key")` with:

```python
    pytest.param(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}", id="the tier key may_import"),
    pytest.param(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}",
                 id="the tier key may_also_import"),
    pytest.param(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}", id="the tier key must_import"),
    pytest.param(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}",
                 id="the tier key types_only, its own hint beside the part's"),
    pytest.param(TIER_IMPORTS, "types_only", "", id="types_only in a tier's imports, a key"),
    pytest.param(TIER_IMPORTS, "libraries", "", id="libraries in a tier's imports, only unknown"),
```

  and add `TIER_IMPORTS` to the names imported from `profile_keys`.
- In the parametrize of `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`, replace
  `pytest.param("tiers.types_only", "", id="tiers.types_only")` with:

```python
    pytest.param("tiers.types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}",
                 id="tiers.types_only"),
    pytest.param("tiers.<tier>.may_also_import", "moved in 0.3.0: write imports: {also: [...]}",
                 id="tiers.<tier>.may_also_import"),
    pytest.param("tiers.imports.types_only", "", id="tiers.imports.types_only"),
```

In `tests/modules/spec/application/logic/test_never_use.py`, line 63:
`TIER_USE = "docs, folder, imports, litmus, plain_tables, proves, uses"`.

In `tests/modules/spec/application/logic/test_targets_written.py`,
`test_a_tier_folder_s_may_import_refuses_a_marked_entry_as_any_entry_that_is_no_target` (line 51): the where given
and expected, `"tiers.guard.may_import"` and `"tiers.guard.may_import: ..."`, become `"tiers.guard.imports.may"` and
`"tiers.guard.imports.may: ..."` (the label the parser now passes).

In `tests/modules/spec/application/logic/test_checked_tier.py`, line 24:
`document["tiers"]["unit"]["may_also_import"] = ["service", "shared"]` becomes
`document["tiers"]["unit"]["imports"] = {"also": ["service", "shared"]}`.

In `tests/modules/spec/application/logic/test_profile_needs.py`:
- Line 87: `document["tiers"]["unit"]["must_import"] = ["service"]` becomes
  `document["tiers"]["unit"]["imports"] = {"must": ["service"]}`.
- Line 144: `("tiers.unit.must_import", "tiers.<tier>.must_import"),` becomes
  `("tiers.unit.imports.must", "tiers.<tier>.imports.must"),`.
- After `test_a_tier_that_applies_the_never_lists_needs_the_facts_their_check_reads`, add (spec test 7; Toy supplies
  neither `function.statements` nor any fact of types-only):

```python
def test_a_tier_s_imports_need_what_the_old_tier_keys_needed_at_their_new_addresses():
    document = tiered(imports={"must": ["service"], "types_only": ["store"]})
    assert [(item.address, item.fact) for item in short(document, {}, TOY)] == [
        ("tiers.unit.imports.must", "function.statements"),
        *(("tiers.unit.imports.types_only", fact) for fact in ("call", "use", "module_functions", "import.resolved"))]


def test_a_tier_s_imports_that_is_no_map_needs_nothing():
    assert short(tiered(imports=["store"]), {}, TOY) == []
```

In `tests/modules/spec/application/origins.py`, line 4: `"types_only": ["store"]` becomes
`"imports": {"types_only": ["store"]}`.

In `tests/modules/spec/application/logic/test_looseness.py` (profiles only; the expected `Loosened` stay until Task 3):
- Lines 66-67 and 169-170: `{key: value for key, value in TIER.items() if key != "types_only"}` becomes
  `{key: value for key, value in TIER.items() if key != "imports"}`, and `"may_also_import": ["edge"]` becomes
  `"imports": {"also": ["edge"]}`.
- Lines 99-100: `base["tiers"]["unit"]["may_also_import"] = bundled` and the same for `mine` become
  `base["tiers"]["unit"]["imports"] = {"also": bundled}` and `mine["tiers"]["unit"]["imports"] = {"also": custom}`.

In `tests/modules/spec/application/test_origin.py`, lines 42-43: the same two edits as test_looseness lines 66-67.

- [ ] **Step 8: Run the parser tests to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_needs.py`
Expected: FAIL. The group tests fail with `unknown key 'imports'`, since the parser does not read the group yet. Some
old-key tests also fail, with an extra problem from the old reading of the key (such as the allowance refusal of
`may_import` on a tier with no folder). The `retired` lookups of `test_retired_keys.py` pass already.

- [ ] **Step 9: Read a tier's group with the part's helper**

In `xarch/modules/spec/application/logic/imports_written.py`:

1. Change the import `from xarch.modules.spec.application.logic.key_lookup import names_of` to
   `from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of`.
2. Append to the module docstring, before its closing `"""`, the paragraph:

```
A tier's `imports`, {may, also, must, types_only}, is checked as a group by the same `group`, under its own scope and
with its own example; the tier parser reads its keys (see profile_parsing).
```

3. Replace `group` with:

```python
def group(spec: Mapping[Any, Any], where: str, problems: list[str], scope: str = PART_IMPORTS,
          example: str = "{may: [<part>]}") -> Mapping[Any, Any]:
    """The `imports` of the part or tier at where, its keys those of the scope: {} when it writes none, or when it is
    no map or says nothing, each problem added, naming the keys in the order of the table and showing the example;
    its unknown keys are refused under the scope."""
    if "imports" not in spec:
        return {}
    value, at = spec["imports"], f"{where}.imports"
    names = [key.name for key in keys_of(scope)]
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a map of {_joined(names, 'and')}, such as {example}")
        return {}
    if not value:
        problems.append(f"{at}: says nothing: write {_joined(names, 'or')}, or drop it")
        return {}
    problems += ck.unknown_keys(value, names_of(scope), at, scope)
    return value


def _joined(names: list[str], word: str) -> str:
    """The names in order, the last after the word: may, must and libraries."""
    return f"{', '.join(names[:-1])} {word} {names[-1]}"
```

   For a part, the keys of `PART_IMPORTS` are `may`, `must`, `libraries`, so its two texts do not change.

In `xarch/modules/spec/application/logic/profile_parsing.py`:

1. Add `TIER_IMPORTS,` to the names imported from `xarch.modules.spec.domain.profile_keys`, after `TIER_DOCS,`.
2. In the module docstring, replace the tiers entry (lines 39-43, from `    tiers: {<tier>: {proves, ...` through
   `mirror; `docs` holds what only fills the generated docs`) with:

```
    tiers: {<tier>: {proves, litmus, uses, plain_tables, folder, imports: {may, also, must, types_only}, docs}}
                               the kinds of test, in the order their litmus tests run. A tier with a `folder` below
                               the tests folder says in `imports.may` what the tests there may import; `imports.also`
                               what each of its tests may import beyond that or what the part it mirrors may;
                               `imports.must` the parts one of which each of its test files reaches;
                               `imports.types_only` the parts its tests may import only as types;
                               `uses: {apply_never: true}` holds its tests to the `uses.never` list of the part they
                               mirror; `docs` holds what only fills the generated docs
```

3. In `_tier`, replace the lines from `    types_only = (ck.part_names(spec["types_only"], ...` (line 645) through
   `             if "must_import" in spec else [])` (line 657) with:

```python
    imports = iw.group(spec, where, problems, TIER_IMPORTS, "{must: [<part>]}")
    types_only = (ck.part_names(imports["types_only"], declared, f"{where}.imports.types_only", problems)
                  if "types_only" in imports else [])
    folder = ck.tier_folder(spec["folder"], parts, f"{where}.folder", problems, language) if "folder" in spec else None
    if "folder" not in spec and "may" in imports:
        problems.append(f"{where}.imports.may: only a tier with a `folder` has an allowance of its own: without one, "
                        "its tests import what the part they mirror may")
    allowance = (may_import(imports.get("may"), None, parts, declared, f"{where}.imports.may", problems)
                 if "folder" in spec else None)
    also = may_import(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems, mirrored=True)
    docs = _tier_docs(spec["docs"], folder, examples, f"{where}.docs", problems, language) if "docs" in spec else {}
    reach = (ck.part_names(imports["must"], declared, f"{where}.imports.must", problems)
             if "must" in imports else [])
```

   The `return Tier(...)` after it is unchanged: it reads `types_only`, `folder`, `allowance`, `reach`, `plain` and
   `also`, as before. `may` is read with `mirrored=False` and `also` with `mirrored=True`, as before (spec risk 2).

- [ ] **Step 10: Run the parser tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_never_use.py tests/modules/spec/application/logic/test_targets_written.py tests/modules/spec/application/logic/test_checked_tier.py`
Expected: PASS. `test_imports_written.py` must pass unchanged: the part's two texts did not move.

- [ ] **Step 11: Rewrite the bundled, xarch's own and the corpora profiles**

The group is written where the first old key stood. Its keys go in the order `may`, `also`, `must`, `types_only`.
Nothing else in the files moves (spec 2.7).

`xarch/architectures/cli.yaml` line 255 and `xarch/architectures/web.yaml` line 257 (tier `rendering`):
`    types_only: [controller]` becomes `    imports: {types_only: [controller]}`.
`cli.yaml` line 270 and `web.yaml` line 272 (tier `guard`): `    may_import: []` becomes `    imports: {may: []}`.

`architecture.yaml`, tier `integration` (lines 280-282). The three lines

```yaml
    must_import: [controller]
    # the values the ports hand back, which a test of a controller builds its fakes' answers with
    may_also_import: [domain/values, domain/profile, domain/parsed, domain/outcomes]
```

become

```yaml
    imports:
      # the values the ports hand back, which a test of a controller builds its fakes' answers with
      also: [domain/values, domain/profile, domain/parsed, domain/outcomes]
      must: [controller]
```

Tier `wired` (lines 292-293):

```yaml
    imports:
      must: [bootstrap]
      types_only: [domain, logic, ports, services, controller, adapters, platform]
```

Tier `guard` (lines 303-305). The lines `types_only: [...]`, `folder: architecture`, `may_import: everything` become

```yaml
    imports:
      may: everything
      types_only: [domain, logic, ports, services, controller, adapters, platform]
    folder: architecture
```

`tests/bootstrap/corpora/7cc6111.yaml` (lines 128-145) and `tests/bootstrap/corpora/df537ca.yaml` (lines 148-165): the
same three tiers, written as `architecture.yaml` is. `integration` there has no `may_also_import`, so it becomes
`    imports:` / `      must: [controller]`. `wired` and `guard` are as above.

`tests/bootstrap/corpora/stress.yaml` (lines 212-262) writes block lists. Keep that style:
- `unit`: the lines `types_only:` / `- domain` / `must_import:` / `- domain` / `- logic` / `- kernel` become

```yaml
    imports:
      must:
      - domain
      - logic
      - kernel
      types_only:
      - domain
```

- `integration`: `must_import:` / `- controller` becomes `    imports:` / `      must:` / `      - controller`.
- `wired`: `types_only:` (seven entries) then `must_import:` / `- bootstrap` become `imports:` holding `must:` /
  `- bootstrap` then `types_only:` with the same seven entries in the same order.
- `guard`: `types_only:` (seven entries), `folder: architecture`, `may_import: everything` become `imports:` holding
  `may: everything` then `types_only:` with the seven entries, then `folder: architecture`.

Then `uv run xarch profile check architecture.yaml` prints "OK: the profile is valid", and this prints nothing (a
tier's own keys sit at four spaces; the group's keys at six):
`git grep -nE "^ {4}(types_only|must_import|may_import|may_also_import):" -- xarch/architectures architecture.yaml tests/bootstrap/corpora/*.yaml`.

- [ ] **Step 12: Key the tier rules by the new addresses**

First the tests. In `tests/modules/rules/application/logic/`:
- `test_types_only.py` lines 44, 46, 81, 97, 101: `(tiers.rendering.types_only)` becomes
  `(tiers.rendering.imports.types_only)`.
- `test_must_import.py` line 94: `(tiers.integration.must_import)` becomes `(tiers.integration.imports.must)`.
- `test_tier_imports.py` line 161: `tiers.integration.may_also_import)` becomes `tiers.integration.imports.also)`.
- `test_sentences.py` line 56: `"parts.domain.imports.may; tiers.unit.may_also_import"` becomes
  `"parts.domain.imports.may; tiers.unit.imports.also"`.
- `test_expandable.py` line 31: `pytest.param("tiers.unit.types_only", True, id="a key of a tier")` becomes
  `pytest.param("tiers.unit.imports.types_only", True, id="a key of a tier")`. Line 71:
  `assert expands("tiers.types_only") and expands("tiers.must_import")` becomes
  `assert expands("tiers.imports.types_only") and expands("tiers.imports.must")`. At the end of the file add (spec
  test 11):

```python
def test_the_keys_of_a_tier_s_group_are_expanded_and_the_old_tier_keys_are_not():
    assert all(expands(key) for key in ("tiers.imports.also", "tiers.imports.types_only", "tiers.imports.must",
                                        "tiers.unit.imports.must"))
    assert not any(expands(key) for key in ("tiers.may_also_import", "tiers.types_only", "tiers.must_import"))
    assert {"tiers.imports.also", "tiers.imports.types_only", "tiers.imports.must"} <= set(KEYS)
    assert not {"tiers.may_also_import", "tiers.types_only", "tiers.must_import"} & set(KEYS)
```

  (`KEYS` and `expands` are already imported there; check with `grep -n "^from\|^def expands" tests/modules/rules/application/logic/test_expandable.py`).
- `test_expansion.py`: at the end of the file add (spec test 10; `PROFILE`'s tier `rendering` lists `types_only`
  already):

```python
def test_the_rules_of_a_tier_s_imports_are_keyed_by_their_addresses_in_the_group():
    tiers = tuple(replace(t, must_import=("controller",), may_also_import=(Target("adapters", "own"),))
                  if t.name == "integration" else t for t in PROFILE.tiers)
    keys = [rule.key for rules in expansion.book(replace(PROFILE, tiers=tiers)).values() for rule in rules
            if rule.id in ("types-only", "must-import", "tiers") and rule.key.startswith("tiers")]
    assert "tiers.rendering.imports.types_only" in keys and "tiers.integration.imports.must" in keys
    assert "tiers; tiers.integration.imports.also" in keys
    assert not [key for key in keys if re.search(r"tiers\.[a-z]+\.(types_only|must_import|may_also_import)", key)]
```

  and add `import re` at the top of the file, above `from dataclasses import replace`.

In `tests/bootstrap/test_source_checks.py`, line 29: `(tiers.rendering.types_only)` becomes
`(tiers.rendering.imports.types_only)`.

Then the code:

In `xarch/modules/rules/application/logic/expansion.py`:
- `_types_only_tiers` (lines 137-142): its docstring "A test of a tier that names parts in `types_only`" becomes "A test
  of a tier that names parts in `imports.types_only`". The key `f"tiers.{tier.name}.types_only"` becomes
  `f"tiers.{tier.name}.imports.types_only"`.
- `_tiers` docstring (lines 163-167): "keyed by each tier's may_also_import too" becomes "keyed by each tier's
  imports.also too". Line 188: `also = "".join(f"; tiers.{tier.name}.may_also_import" ...)` becomes
  `also = "".join(f"; tiers.{tier.name}.imports.also" for tier in profile.tiers if tier.may_also_import)`.
- `_must_import_tiers` (lines 347-359): its docstring "Each test file of a tier that lists `must_import`" becomes "Each
  test file of a tier that lists `imports.must`". The key `f"tiers.{tier.name}.must_import"` becomes
  `f"tiers.{tier.name}.imports.must"`.
- `KEYS` (lines 426-432): `"tiers.may_also_import", "tiers.types_only",` becomes
  `"tiers.imports.also", "tiers.imports.types_only",`, and `"tiers.must_import"` becomes `"tiers.imports.must"`. Each
  stays in its place, since the book's order is what `test_expandable.py` holds.

In `xarch/modules/rules/application/logic/sentences.py`, line 148:

```python
    return f"{parts}; tiers.{tier.name}.imports.also" if tier is not None and tier.may_also_import else parts
```

In `xarch/modules/rules/domain/vocabulary.py`, lines 372-374: the example at the end of `mirrored_may_import`'s text,
`"parts.store.imports.may; tiers.unit.may_also_import"`, becomes `"parts.store.imports.may; tiers.unit.imports.also"`.

- [ ] **Step 13: The remaining tests that write or name a tier's import key**

- `tests/bootstrap/test_bundled_imports.py`: `TIER_KEYS` becomes
  `{"types_only": "tiers.imports.types_only", "must": "tiers.imports.must", "also": "tiers.imports.also", "tiers": "tiers"}`.
  Nothing else in the file changes.
- `tests/bootstrap/test_needs_agree.py`, the `EVERY_KEY` yaml (lines 37-46): the tiers become

```yaml
tiers:
  unit:
    uses: {apply_never: true}
    imports:
      also: [api]
      must: [core]
      types_only: [api]
  guard:
    folder: architecture
    imports:
      may: [core]
```

- `tests/bootstrap/test_rule_ids.py` line 171: `"  integration:\n    must_import: [controller]\n"` becomes
  `"  integration:\n    imports: {must: [controller]}\n"`.
- `tests/modules/spec/application/test_explain.py`, the `Shown` rows (lines 70-74): delete the rows of
  `tiers.types_only`, `tiers.must_import`, `tiers.may_import` and `tiers.may_also_import`. After the row of
  `tiers.folder`, put:

```python
    Shown('tiers.imports', 1, 'what its tests may import, may also import, must import one of, and may import only '
                              'as types', False, True),
```

  Line 120: `UnknownKey("parts.may_imports", ("parts.imports", "tiers.may_import", "parts.imports.may"))` becomes
  `UnknownKey("parts.may_imports", ("parts.imports", "parts.imports.may", "parts.imports.must"))`. This was computed
  with `difflib.get_close_matches` over the new key list, the way `explain.nearest` computes it.
- `tests/bootstrap/test_profile_explain.py`: at the end of the file add (spec test 13; Review Focus 5):

```python
@pytest.mark.parametrize("address, key", [
    pytest.param("tiers.imports.also", "tiers.imports.also", id="the plain address"),
    pytest.param("tiers.<tier>.imports.must", "tiers.imports.must", id="with the placeholder"),
    pytest.param("tiers.unit.imports.must", "tiers.imports.must", id="with a tier's name"),
])
def test_a_key_of_a_tier_s_group_is_explained_with_or_without_a_tier_name(address, key):
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 0 and json.loads(found.output)["key"] == key


def test_the_group_of_a_tier_lists_its_keys_and_the_rules_they_feed():
    shown = json.loads(runner.invoke(app, ["profile", "explain", "tiers.imports", "--format", "json"]).output)
    assert shown["rules"] == ["tiers", "must-import", "types-only"]
    assert json.loads(runner.invoke(app, ["profile", "explain", "tiers.imports.types_only", "--format",
                                          "json"]).output)["rules"] == ["types-only"]


@pytest.mark.parametrize("address, text", [
    pytest.param("tiers.may_import", "moved in 0.3.0: write imports: {may: [...]}", id="may_import"),
    pytest.param("tiers.may_also_import", "moved in 0.3.0: write imports: {also: [...]}", id="may_also_import"),
    pytest.param("tiers.must_import", "moved in 0.3.0: write imports: {must: [...]}", id="must_import"),
    pytest.param("tiers.types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}", id="types_only"),
])
def test_an_old_tier_key_answers_with_the_form_that_replaces_it(address, text):
    said = runner.invoke(app, ["profile", "explain", address])
    assert said.exit_code == 2 and f"error: no key `{address}` in the format: {text}; the nearest are " in said.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] == text
```

  (the exit code 2 and the `retired` field are those `test_an_old_name_of_never_is_refused_with_its_text_exit_2_and_retired_in_json`
  asserts for every retired address today; `pytest`, `json`, `runner` and `app` are imported at the top of the file).

Then sweep for anything left:

```bash
git grep -nE "[\"'](may_also_import|must_import|may_import|types_only)[\"']\s*:|\b(may_also_import|must_import|may_import|types_only): |tiers\.[a-z<>]+\.(may_also_import|must_import|may_import|types_only)\b|tiers\.(may_also_import|must_import|may_import|types_only)\b|may_also_import, may_import" -- tests ':!tests/bootstrap/corpora'
```

Each hit left must be one of these: a part's mark (`{"x": "types_only"}`, `{x: types_only}`); a part's retired key in
the part refusal tests (`test_imports_written.py`, `test_retired_keys.py`'s `PART` cases, `test_profile_keys.py`); a
tier retired key in the refusal tests of Steps 1, 7 and 13; the expected `Loosened` keys and sentences of
`test_looseness.py` and `test_origin.py` (Task 3 moves them); the `where` JSON field `"types_only"` of
`tests/bootstrap/test_where.py` and `test_repeating_folders.py`; the `KeyFacts(..., "types_only", "part")` of
`tests/cli/reports/test_vocabulary_report.py`, `tests/modules/rules/adapters/test_spec_profile.py` and
`tests/modules/rules/application/test_rule.py` (a part key's name, not a tier's); and the retired-hint text of
`tests/modules/rules/domain/test_rule.py:147` (a `keep` slot, not a key). Edit any other hit as the lines above.
`tests/architecture/test_language_seam.py`, `tests/cli/reports/test_where_report.py` and the `CheckedTier`/`Tier`
values built by keyword keep their field names. Spec test 18 names them, but they write no tier key.

- [ ] **Step 14: Edit the recorded findings, anchored on `(tiers.<t>.`**

```bash
cd tests/bootstrap/corpora
xz -dc stress-7cc6111.json.xz > /tmp/stress46-before.json
cp /tmp/stress46-before.json /tmp/stress46-after.json
cp 7cc6111.json /tmp/7cc6111-46-before.json
perl -pi -e 's/\(tiers\.([A-Za-z0-9_-]+)\.types_only\)/(tiers.$1.imports.types_only)/g;
             s/\(tiers\.([A-Za-z0-9_-]+)\.must_import\)/(tiers.$1.imports.must)/g;
             s/\(tiers\.([A-Za-z0-9_-]+)\.may_also_import\)/(tiers.$1.imports.also)/g' \
     7cc6111.json /tmp/stress46-after.json
xz -9 -c /tmp/stress46-after.json > stress-7cc6111.json.xz
for pair in "/tmp/7cc6111-46-before.json 7cc6111.json" "/tmp/stress46-before.json /tmp/stress46-after.json"; do
  set -- $pair; echo "$2 $(diff $1 $2 | grep -c '^<') $(diff $1 $2 | grep -c '^>')"; done
diff /tmp/stress46-before.json /tmp/stress46-after.json | grep '^>' | grep -oE '\(tiers\.[a-z]+\.[a-z_.]+\)' | sort | uniq -c
cd -
```

Expected: `7cc6111.json 1 1` and `/tmp/stress46-after.json 695 695`, then `694 (tiers.unit.imports.types_only)` and
`1 (tiers.wired.imports.must)`. Read each diff (`diff /tmp/7cc6111-46-before.json tests/bootstrap/corpora/7cc6111.json`,
`diff /tmp/stress46-before.json /tmp/stress46-after.json | less`). Every changed line must differ only by the key inside
the parentheses. `df537ca.json`, `examples-cli.json` and `examples-web.json` hold no tier import key and are not
touched. Check that with
`grep -cE "\(tiers\.[a-z]+\.(types_only|must_import|may_also_import)\)" tests/bootstrap/corpora/df537ca.json tests/bootstrap/corpora/examples-*.json`
(each prints 0). The `tiers.<t>.uses.apply_never` lines stay. The recorded counts in the docstring of
`test_recorded_corpora.py` do not change. If any recorded finding differs in more than the key, the check now finds
something else. Do not edit that finding: stop and report it (spec 2.9).

- [ ] **Step 15: Run the spec, rules and wired tests of this task**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/modules/rules tests/bootstrap/test_bundled_imports.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_source_checks.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_bundled_tiers.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_tier_folder.py`
Expected: PASS. `test_bundled_imports.py` passes with only `TIER_KEYS` changed: xarch's tiers import what they
imported. `test_docs_templates.py` passes with no doc regenerated: the docs print values, not keys, and no template
text has changed yet. On a failure, read it. An expected text still on an old key is Step 13's to change. A `where` or
rules hash that differs is a defect of the profile rewrite: fix the profile, never the literal.

- [ ] **Step 16: Run the whole suite and the gates**

Run: `timeout 900 uv run pytest -q > /tmp/xarch-46-t2.log 2>&1; echo EXIT $?; tail -5 /tmp/xarch-46-t2.log` (in the
background), then
`uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: `EXIT 0`; "All checks passed!"; both checks exit 0; "OK: the profile is valid". Fix each failure by the rule
of Step 15.

- [ ] **Step 17: Commit**

```bash
git add xarch tests architecture.yaml
git status --short   # nothing under .claude/, nothing else left unstaged
git commit -m "A tier's may_import, may_also_import, must_import and types_only move into one imports group, {may, also, must, types_only}, with the same meaning and values, may still only for a tier with a folder; the old tier keys are refused with the form that replaces them from the table of retired names, under the tier's scope beside the part's entries of the same names, and the group written wrong in fixed text read by the part's helper under the tier's scope; the key table opens tiers.<tier>.imports with the facts the old keys needed; rules and findings are keyed by tiers.<t>.imports.types_only, tiers.<t>.imports.must and tiers; tiers.<t>.imports.also; every profile and test profile writes the group, and the recorded corpora change by anchored replace in the 696 lines that named a tier's import key"
```

---

### Task 3: `profile check` says a tier's looser lines under the group's keys

Spec: 2.6; test 8.

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (docstring lines 13-15; `LOOSER` lines 37-39; `_looser` lines 92-93; the sentences lines 172-175)
- Modify: `xarch/modules/spec/domain/published.py:118-119`
- Test: `tests/modules/spec/application/logic/test_looseness.py`, `tests/modules/spec/application/test_origin.py`

**Interfaces:**
- Consumes: the tier profiles of Task 2 (`imports: {also, types_only}`).
- Produces: `Loosened.key` `"imports.types_only"` and `"imports.also"` for a tier, in place of `"types_only"` and
  `"may_also_import"`; `LOOSER` holds the new keys in the places of the old.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_looseness.py`:
- Lines 76-77 become

```python
        Loosened("imports.types_only", "unit", "store",
                 "the unit tests may now call store (tiers.unit.imports.types_only)"),
        Loosened("imports.also", "unit", "edge", "the unit tests may also import edge (tiers.unit.imports.also)"),
```

- Lines 88-91 become

```python
        Loosened("imports.also", "unit", "shared/text",
                 "the unit tests may also import shared/text (tiers.unit.imports.also)"),
        Loosened("imports.also", "unit", "store@any",
                 "the unit tests may also import store@any (tiers.unit.imports.also)")),
```

- At the end of the file add:

```python
def test_a_tier_s_looser_keys_are_those_of_its_group_and_the_old_words_are_gone():
    assert LOOSER.index("imports.types_only") < LOOSER.index("imports.also") < LOOSER.index("uses.apply_never")
    assert not {"types_only", "may_also_import"} & set(LOOSER)
```

In `tests/modules/spec/application/test_origin.py`, lines 57-58 become the same two `Loosened` lines as
test_looseness's lines 76-77 above.

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py`
Expected: FAIL. The found `Loosened` have the key `types_only` and the sentence `(tiers.unit.types_only)`.

- [ ] **Step 3: Rename the two keys and their sentences**

In `xarch/modules/spec/application/logic/looseness.py`:
- `LOOSER` (lines 37-39): `"types_only", "may_also_import"` becomes `"imports.types_only", "imports.also"`, in the
  same place.
- `_looser` (lines 92-93):

```python
            found += [("imports.types_only", tier.name, part) for part in tier.types_only if part not in mine.types_only]
            found += [("imports.also", tier.name, _shown(t)) for t in mine.may_also_import
                      if not any(_covers(b, t) for b in tier.may_also_import)]
```

- The sentences (lines 172-175):

```python
        case "imports.types_only":
            return f"the {part} tests may now call {what} (tiers.{part}.imports.types_only)"
        case "imports.also":
            return f"the {part} tests may also import {what} (tiers.{part}.imports.also)"
```

- The module docstring (lines 13-15): "a part dropped from a tier's `types_only`; a target added to a tier's
  `may_also_import` that no target of the bundled tier's covers" becomes "a part dropped from a tier's
  `imports.types_only`; a target added to a tier's `imports.also` that no target of the bundled tier's covers".
  Rewrap the paragraph's lines to the file's width (120).

In `xarch/modules/spec/domain/published.py`, the `Loosened` docstring (lines 118-119):

```
        imports.types_only
                        the tests of tier part may now call what
        imports.also    the tests of tier part may also import what (a target as written)
```

A tier's `may` and `must` are not compared, as today (release step 16).

- [ ] **Step 4: Run the tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py tests/bootstrap tests/cli`
Expected: PASS, `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own` among them. If a test under
`tests/bootstrap` or `tests/cli` prints a tier looser line with the old key, change its expected text to the new key
and sentence. Find them with `git grep -nE "\(tiers\.[a-z]+\.(types_only|may_also_import)\)|\"(types_only|may_also_import)\", \"" -- tests`.

- [ ] **Step 5: Commit**

```bash
git add xarch tests
git commit -m "profile check lists a part dropped from a tier's imports.types_only under the key imports.types_only, and a target added to its imports.also under imports.also, each sentence naming the address in the group; a tier's may and must are compared in no way, as before"
```

---

### Task 4: The docs say a tier's group

Spec: 2.8, 2.10; test 14, test 17 (`test_readme.py`).

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:35` (a docstring)
- Modify: `xarch/architectures/testing.md:47,225` (the template, the source of the golden copies)
- Regenerate: `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Modify: `README.md`, `CHANGELOG.md`
- Test: `tests/bootstrap/test_docs_templates.py`, `tests/architecture/test_readme.py`

- [ ] **Step 1: Change the template sources**

`xarch/modules/spec/application/logic/docs_template.py` line 35, in the `{{guards}}` entry of the module docstring:
"(one line per tier with `types_only`)" becomes "(one line per tier with `imports.types_only`)". The code prints values,
so no output moves.

`xarch/architectures/testing.md` line 47: "A tier may name more with `may_also_import`, such as the values a test
builds its fakes' answers with" becomes "A tier may name more with `imports.also`, such as the values a test builds its
fakes' answers with".

`xarch/architectures/testing.md` line 225: "a tier that lost a `types_only` part or its `uses.apply_never`, a target a
tier's tests may also import (`may_also_import`)" becomes "a tier that lost an `imports.types_only` part or its
`uses.apply_never`, a target a tier's tests may also import (`imports.also`)".

- [ ] **Step 2: Run the docs test to see it fail**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py`
Expected: FAIL. The golden copies `docs/cli/testing.md` and `docs/web/testing.md` differ from what the template now
gives at lines 57 and 370 (web: 371).

- [ ] **Step 3: Regenerate the golden docs and read the diff**

```bash
uv run python - <<'EOF'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for profile, out in (("cli", "docs/cli"), ("web", "docs/web"), ("architecture.yaml", "docs/xarch")):
    for found in spec.docs(profile).files:
        Path(out, *found.path).write_text(found.template, encoding="utf-8")
EOF
git diff --stat docs/
git diff docs/ | grep '^[-+]' | grep -v '^[-+][-+]' | cut -c1-160
```

Expected: only `docs/cli/testing.md` and `docs/web/testing.md` change, each by 2 lines out and 2 in: line 57 (the
`imports.also` sentence) and line 370 (web: 371, the enforcement paragraph). `docs/xarch/testing.md` holds neither
paragraph and does not change. Any other moved line or file is a defect to explain or fix, never to accept. Restore an
unexpected file with `git checkout -- <file>` and find its cause.

- [ ] **Step 4: README**

Make these edits, each at the line the spec names (2.10):
- Lines 122-123, the tiers line of the profile shape, become

```
tiers:    {<tier>: {proves, litmus, uses: {apply_never}, plain_tables, folder, imports: {may, also, must, types_only},
                    docs}}
```

- Line 299, the `tiers` row's key column: `` `tiers.may_import`, `tiers.may_also_import` `` becomes
  `` `tiers.imports.may`, `tiers.imports.also` ``.
- Line 301, the `types-only` row: `` `tiers.types_only` `` becomes `` `tiers.imports.types_only` ``.
- Line 304, the `must-import` row: `` `tiers.must_import` `` becomes `` `tiers.imports.must` ``.
- Lines 393-394, the `profile.looser` key list: `` `types_only`, `may_also_import` `` becomes
  `` `imports.types_only`, `imports.also` ``.
- Lines 440-441: "a part dropped from a tier's `types_only`, a target added to a tier's `may_also_import`" becomes "a
  part dropped from a tier's `imports.types_only`, a target added to a tier's `imports.also`".

The JSON field names of `where` (lines 535-567: `may_import`, `may_import_text`, `"types_only"` under `test`) stay.
Then `grep -nE "may_also_import|tiers\.(types_only|must_import|may_import)|tier's \`(types_only|may_also_import)\`" README.md`
prints nothing.

- [ ] **Step 5: CHANGELOG**

Under `## [Unreleased]`, `### Changed`, in the entry that begins "A part's `may_import`, `must_import` and `libraries`
move into one group" (lines 62-72):
- "in any instance; a tier's `types_only` list stays. Findings name" becomes "in any instance. Findings name".
- "Rule ids, `where`'s JSON fields and the tier keys do not change." becomes "Rule ids and `where`'s JSON fields do not
  change."

Then add, right after that entry:

```markdown
- A tier's `may_import`, `may_also_import`, `must_import` and `types_only` move into one group, `imports: {may, also,
  must, types_only}`, with the same meaning: `may` what the tests in the tier's `folder` may import (only for a tier
  with a `folder`), `also` what its tests may import besides what the part they mirror may, `must` the parts one of
  which each of its test files reaches, `types_only` the parts its tests may import only as types. Findings name the
  new addresses (`tiers.<tier>.imports.types_only`, `tiers.<tier>.imports.must`, and `tiers.<tier>.imports.also` beside
  `tiers`), and so do `profile explain` and the `Loosened` keys of `profile check` (`imports.types_only`,
  `imports.also`). The old keys are refused with the form that replaces them (`unknown key 'may_also_import': moved in
  0.3.0: write imports: {also: [...]}`, and the same for `may_import`, `must_import` and `types_only`); `profile
  explain tiers.may_import` says the same. Rule ids and `where`'s JSON fields do not change.
```

- [ ] **Step 6: Run the docs tests**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_docs.py tests/modules/spec/application/logic/test_docs_template.py tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add xarch docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md README.md CHANGELOG.md
git status --short   # nothing under .claude/
git commit -m "The docs say a tier's imports group: the testing docs name imports.also where a tier names more for its tests, and imports.types_only and imports.also among the ways a profile is looser; the README writes imports: {may, also, must, types_only} on a tier and names the new addresses in its rule table and looser keys; the CHANGELOG says, under Unreleased, that a tier's import keys moved into the group, that findings, profile explain and the Loosened keys name the new addresses, and how the old keys are refused, and the part entry no longer says the tier keys stay; the golden docs regenerate moving those two paragraphs alone"
```

---

### Task 5: Gates and the re-grep

Spec: section 3.

- [ ] **Step 1: Run every gate**

Run, the suite in the background:
`timeout 900 uv run pytest -q > /tmp/xarch-46-pytest.log 2>&1; echo EXIT $?; tail -3 /tmp/xarch-46-pytest.log`, then
`uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`.
Expected: `EXIT 0` with no failure; "All checks passed!"; both checks exit 0; "OK: the profile is valid".

- [ ] **Step 2: The re-grep, scoped to tiers**

Run: `git grep -nE "may_also_import|^\s+(types_only|must_import|may_import):" -- xarch tests README.md CHANGELOG.md docs architecture.yaml`
Expected: for a tier, every hit is one of these: the retired table (`profile_keys.py`); the refusal tests (Task 2 Steps
1, 7, 13); a key nested under `imports` (six or more spaces of indent in a profile); a Python identifier (the fields
`Tier.may_also_import`, `CheckedTier.may_also_import`, `types_only`, `must_import`, `may_import`, keyword arguments,
`docs/examples/profile_values/tiers.py`, `docs/xarch/architecture.md`'s copy of it); the `where` JSON field
`test.types_only`; the CHANGELOG's own lines about the move; and `docs/superpowers/**` (history, left alone). Fix any
other hit in the commit of the task that owns its file (a new commit in that task's message style).

- [ ] **Step 3: Commit (only if a fix was needed)**

```bash
git add <the files fixed>
git commit -m "<what the fix makes true, in the style of the task that owns the file>"
```
<!-- task-pipeline: validated -->
