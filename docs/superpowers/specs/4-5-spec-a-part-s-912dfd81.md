# 4.5 spec: a part's import keys move into one `imports` group

Card `912dfd81`, subtask of `c34d7f47`, blocked by `468cc608` (4.4, `holds` as a map of kinds, done on this branch at
`5d9429b`/`84ebb5a`/`f6d8b32`). Release step 13 of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3).

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Ruling 5 (CS 33-35): a part's import rules sit in one `imports` group, `may`, `must`, `libraries`; a use only as a
  type is said per entry of `imports.may`, so `types_only` stops repeating entries of `may`.
- Ruling 9 (CS 44): the rule id `may-import` (already renamed from `rules` in release step 2.3: `key_table.py:78`,
  `expansion.py:128`); no other rule id changes.
- Ruling 10 (CS 45-46) and the defaults (CS 65-66): an old key is refused with a hint from the one retired-keys
  table, in fixed text, one wording, one problem per retired key.
- Ruling 12 (CS 52-53): "only as a type" is a mark on an entry of `imports.may`, `{<target>: types_only}`; a tier
  keeps its own `types_only` list.
- Defaults (CS 66-69): `must` is its own list, each entry also in `may`; `where`'s JSON fields keep their words.
- No compatibility window (CS 72-73).
- 3.1 (CS 451-470), the part half only: the shape of the group.
- 3.2 (CS 472-493), the part rows and the rules of the group.
- 3.3 (CS 495-539): form B, a list whose entries are a target or a one-key map of a target to its mode; one target
  per map; the only mode `types_only`; the rule reads what the entry reaches; `/path` and `:pattern` kept on a marked
  entry.
- 3.4 (CS 541-551): `must` stays a list, never a mode.
- 3.6 (CS 574-579): `package_only`, `holds.classes.built_by`, `reserved` stay outside the group; `reserved`'s message
  names `imports.libraries`.
- 3.7 (CS 581-598): only as far as it says what is under `imports`; the spelling of entries as references is story 8
  and release step 24 (CS 815-820), out of scope.
- 3.8 (CS 600-623), the part half: rule ids unchanged; finding keys follow the addresses; `Loosened` keys move;
  `where` JSON keeps its words; the filter `may-import-everything` keeps its name; the check language's texts and the
  docs' `may-import` line name `imports.may`.
- 3.9 (CS 625-643), the part refusals.
- 5.1 items 2-4, 13, 15 (CS 664-706), their import parts; 5.2 (CS 708-731), the import rows of parts; 5.4 (CS
  752-767), the import tests; 5.5 (CS 769-785), the import lines of the profiles and of the findings.
- 6 (CS 786-793): the retired entries on a part; `profile explain <old key>` answers from the table.
- 7 step 5 (CS 809-816): this step, before part references.
- Dodges (CS 948-976) that apply, as the card lists them (section 9 below).

R3 rules inherited: **O4**, **O5** (R3 228-229): README and CHANGELOG lines of this step go under `[Unreleased]`;
**O8** (R3 232): the golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited
by hand, and move only where section 2.10 says; **O15** (R3 239): every inline test profile that writes `may_import`
is rewritten for the group in this step (the spelling of its entries is step 24's).

### Spelling of entries in this step

References (`parts.kernel`, `module.domain`) are story 8. Until then a target is written as today: `kernel`,
`contract@any`, `domain/values:*Id`. So CS's `{module.ports: types_only}` is written in this step
`{ports: types_only}`, and every message and hint below quotes today's spelling. Step 24 changes only the spelling
inside the lines this step moves.

## 1. Goal

A part says what it may import, what each file must import one of, and the outside packages it may import, in one
group, and marks on an entry of `may` a target it may use only as a type:

```yaml
adapters:
  imports:
    may: [ports, domain, kernel, kernel-logic, platform, contract@any]
    must: [platform, contract@any]
    libraries: [sqlmodel]
services:
  imports:
    may: [logic, domain, ports, {contract: types_only}, kernel]
    must: [ports]
```

The part keys `may_import`, `must_import`, `libraries` and `types_only` leave the part, each refused with the form that
replaces it. For every bundled profile and xarch's own, what `check` finds is the same as before, finding for finding,
but for the key named in parentheses. Rule ids, `where`'s JSON fields, and the tier keys (`tiers.<t>.may_import`,
`may_also_import`, `must_import`, `types_only`) do not change.

## 2. Behavior

### 2.1 The shape

```yaml
parts:
  <part>:
    imports:
      may: [<target> | {<target>: types_only}, ...] | everything
      must: [<target>, ...]
      libraries: [<package>, ...] | everything
```

| Address | Was | Takes | Rule id |
|---|---|---|---|
| `parts.<p>.imports` | (none) | a mapping holding at least one of `may`, `must`, `libraries` | (the three below) |
| `parts.<p>.imports.may` | `parts.<p>.may_import` | a list of targets, each alone or as `{<target>: types_only}`; or `everything` | `may-import` |
| `parts.<p>.imports.must` | `parts.<p>.must_import` | a non-empty list of targets, each one an entry of `may`, none with a mark | `must-import` |
| `parts.<p>.imports.libraries` | `parts.<p>.libraries` | top-level package names, or `everything` | `libraries` |
| `parts.<p>.imports.may.types_only` (the mark) | `parts.<p>.types_only` | the word `types_only` as the value of a one-key map entry of `may` | `types-only` |

What each means is what the old key meant:

- No `imports`, or `imports` without `may`: the part may import nothing but itself (as no `may_import` today).
- `may: []` is valid (a part that imports nothing else).
- `libraries` left out: no outside package; the `libraries` rule runs only when some part lists `libraries`, as today.
- `must`: each file of the part reaches one of the entries, or an outside package, as `must_import` today.
- The order a profile writes `may`, `must`, `libraries` in does not matter; the order of entries in a list is kept.

### 2.2 The mark

- An entry of `may` is either a target as today, or a mapping of exactly one target to the word `types_only`:
  `{contract: types_only}`, `{"domain/values:*Id": types_only}`, `{contract@any: types_only}`.
- A marked entry is an entry of `may` like any other: the `may-import` rule, `where`, the docs' rules table,
  `layers` and `profile check`'s looser lines read it as the target alone (its name pattern included).
- The `types-only` rule on a part reads the marked entries: a file of the part may not call, nor reference as a
  function, anything it reaches through a marked entry. The rule reads **what the entry reaches** (its part, instance
  scope and path), not the part by name in any instance (CS 3.3, line 528-532). The name pattern of a marked entry
  narrows what may be imported (the `may-import` rule's work) and does not narrow what the `types-only` rule reads.
- The sentences of the rule are today's word for word but for the key:

      {where} uses {target_part} only as a type: it may not call {path} (parts.<p>.imports.may.types_only)
      {where} uses {target_part} only as a type: it may not reference {target}, a function (parts.<p>.imports.may.types_only)

  and its fix (`{type_only_fix}`) is today's.
- The fix of a types-only finding that names "a part that may import it and does not list it as a type only"
  (`sentences.py:_caller_fix`, line 162-170) reads the parts whose `may` reaches the target with no mark on that
  entry.
- No bundled profile and not xarch's own gains a mark (CS 5.2, line 729-731; dodge, CS 976).

The finding key of the mark is `parts.<p>.imports.may.types_only`, not CS 3.8's `parts.<p>.imports.may` (CS 606):
one address per rule group, the same address the key table, `profile explain`, `KEYS` and the card's `Loosened` key
`imports.may.types_only` use, as 4.4 keyed `names` by `parts.<p>.holds.classes.names`. Explaining
`parts.<p>.imports.may` then lists the `may-import` rule alone.

### 2.3 Refusals

Each is a problem of the profile, address first, raised as `InvalidArchitecture` with every other problem, as today.
The texts are fixed; `{use}` stands for the "use ..." list of the scope's keys that every unknown-key problem ends with
today (`ck.unknown_keys`).

Retired keys on a part (one problem each, from `RETIRED` in `spec/domain/profile_keys.py`):

    parts.adapters: unknown key 'may_import': moved in 0.3.0: write imports: {may: [...]}; use ...
    parts.adapters: unknown key 'must_import': moved in 0.3.0: write imports: {must: [...]}; use ...
    parts.adapters: unknown key 'libraries': moved in 0.3.0: write imports: {libraries: [...]}; use ...
    parts.adapters: unknown key 'types_only': moved in 0.3.0: write it as the mode of its entry in imports.may, such as [{ports: types_only}]; use ...

`tiers.<t>.types_only`, `tiers.<t>.may_import`, `tiers.<t>.must_import` and `tiers.<t>.may_also_import` stay valid
(scope `TIER`); a part that writes several retired keys gets one problem per key.

Inside the group:

    parts.adapters.imports: must be a map of may, must and libraries, such as {may: [kernel]}
    parts.adapters.imports: says nothing: write may, must or libraries, or drop it
    parts.adapters.imports: unknown key 'never': a key of uses, beside imports: write uses: {never: <list>}; use libraries, may, must
    parts.adapters.imports: unknown key 'types_only': write it as the mode of its entry in imports.may, such as [{ports: types_only}]; use libraries, may, must
    parts.adapters.imports: unknown key 'also': ...; use libraries, may, must

(`also` and any other word get the plain unknown-key problem; `never` and `types_only` carry the two hints above, as
`Retired` entries of the scope `parts.<part>.imports`. The first line is for `imports` written as a list, a string,
`true` or null.)

In `may` (each a new problem; the rest of `may`'s problems are today's `may_import` ones at the new address):

    parts.adapters.imports.may: {ports: types}: no mode 'types': write types_only, or the reference alone
    parts.adapters.imports.may: {ports: true}: no mode True: write types_only, or the reference alone
    parts.adapters.imports.may: {ports: types_only, domain: types_only}: one reference per entry: write each in its own {...}
    parts.adapters.imports.may: {}: one reference per entry: write each in its own {...}
    parts.bootstrap.imports.may: everything takes no mode: list the entries to give one a mode

(the last for `{everything: types_only}` as an entry; `[everything, ...]` keeps today's "stands alone" refusal). The
value is quoted as the profile wrote it, as today's target problems quote it. A target in a marked entry is checked by
the target grammar exactly as a plain entry is (unknown part, bad path, `@any` on a part outside the repeating
folder, ...), and its problem names `parts.<p>.imports.may`.

In `must`:

    parts.adapters.imports.must: must be a list of targets such as [<part>, <part>@any]
    parts.adapters.imports.must: {platform: types_only}: must takes references only, with no mode
    parts.adapters.imports.must: 'platform' is not in imports.may, so no file could import it: add it there, or name a part the part may import

The check that a `must` entry is an entry of `may` stays (dodge, CS 968): a marked `may` entry counts, its mark aside.

In `libraries`: today's problems, at `parts.<p>.imports.libraries`. The reserved-module problem, and the
first-naming place a `never` list's or `reserved`'s problem cites for a package (`_named_packages`), name
`parts.<p>.imports.libraries`.

Gone with no replacement: today's `parts.<p>.types_only: '<name>' is not in may_import ...` (CS 3.3, line 523-525: the
mark sits on the entry, so it cannot name a part `may` does not list).

A tier's folder list (`tiers.<t>.may_import`) is unchanged: an entry written `{x: types_only}` there is refused as any
non-target entry is today, with today's text. The mark is read on a part's `may` only.

### 2.4 `profile explain` and the key catalogue

- `xarch profile explain parts.imports`, `parts.imports.may`, `parts.imports.must`, `parts.imports.libraries`,
  `parts.imports.may.types_only`, and each with a part (`parts.adapters.imports.may`), answer with the key's text from
  `xarch/architectures/presets/format/keys.yaml` and the rules it is keyed by (`may-import`, `must-import`,
  `libraries`, `types-only`).
- `xarch profile explain parts.may_import` (and `must_import`, `libraries`, `types_only`) answers from the retired
  table with the hint of 2.3 (CS 6).
- `keys.yaml` gains one text per new address and loses the four part texts (`parts.<part>.may_import`,
  `.must_import`, `.types_only`, `.libraries`); every other text that names a part's import key (the `part` and
  `tiered-part` fragments, `reserved`, `layers`, the tiers' texts that say "what the part may import", the explanations
  around lines 24, 115-119, 163, 182-205, 528) names the new address. Tier keys keep their texts and names. The mark's
  text says what CS 3.3 says (a target the part may import only to use as a type; the rule reads what the entry
  reaches) and that a tier's `types_only` is the list form of the same idea. The catalogue test holds one text per key.
- The example address in `profile explain`'s help (`cli/commands/profile.py:66`), in `profile_report.py:44` and in
  `key_lookup.py:13-14` becomes `parts.imports.may`.
- `expansion.KEYS` (line 421-427) replaces `parts.may_import`, `parts.libraries`, `parts.must_import`,
  `parts.types_only` by `parts.imports.may`, `parts.imports.libraries`, `parts.imports.must`,
  `parts.imports.may.types_only`; `expandable` and `keyed` answer for the new keys and not the old.

### 2.5 Needs

The facts each key needs move with it (`key_table.NEEDS`, line 218-235):

| Address | Needs (today's of the key it replaces) |
|---|---|
| `parts.<part>.imports.may` | `_IMPORTS` |
| `parts.<part>.imports.must` | `_IMPORTS`, `import.standard`, `function.statements`, `file`, `file.package` |
| `parts.<part>.imports.libraries` | `_IMPORTS`, `import.standard` |
| `parts.<part>.imports.may.types_only` | `_TYPES_ONLY` |

`imports` itself needs nothing. The needs walker (`profile_needs._configured`) reaches the three keys under
`imports`, and reaches the mark when an entry of `may` carries one: a profile whose language lacks a fact of
`_TYPES_ONLY` and that marks an entry gets the shortfall at `parts.<p>.imports.may.types_only`, as today at
`parts.<p>.types_only`; one with no mark gets none for it. How the walker sees the mark (a `Key` row for it plus a
reading of a `may` list's marked entries) is the plan's; the address and the outcome are fixed here.

### 2.6 Values carried

- `Part.types_only` (`spec/domain/values.py:95`) holds the marked targets (`tuple[Target, ...]`, in the order of
  `may`), not part names; `PartView.types_only` (`spec/contract/__init__.py:110`) and the rules `Profile.types_only`
  (`rules/domain/profile.py:108`, by part) carry the same targets. `Target` (`profile_values/placement.py`) does not
  change, so its equality, used by `_must_import` and `looseness`, is untouched (CS 5.1 item 4, line 678-679).
- `Architecture.rules[part]` (what `may` allows) holds every entry of `may`, marked or not, as plain targets.
- The `types-only parts` rule group (`expansion._types_only_parts`) matches what a fact reaches against the marked
  targets with their name patterns dropped (a `place` match), not against part names (`Match("part")`). The tier
  group is unchanged.
- Internal names (`must_import`, `types_only`, `libraries`, `rules`, `may_import` fields and functions) stay; they
  are release step 15's (CS 7 step 7, line 821).

### 2.7 Finding keys and texts

| Rule | Key in findings, before | After |
|---|---|---|
| `may-import` (a part) | `parts.<p>.may_import` | `parts.<p>.imports.may` |
| `libraries` | `parts.<p>.libraries` | `parts.<p>.imports.libraries` |
| `must-import` (a part) | `parts.<p>.must_import` | `parts.<p>.imports.must` |
| `types-only` (a part) | `parts.<p>.types_only` | `parts.<p>.imports.may.types_only` |
| `tiers`, `types-only`/`must-import` of a tier | `tiers.<t>.*` | unchanged |

Texts that cite a part's import key name the new address and nothing else moves in them:

- `sentences.py` (line 88, 144-147): the `mirrored_may_import` value, `parts.<p>.may_import` →
  `parts.<p>.imports.may` (its tier half `tiers.<t>.may_also_import` stays).
- `example_imports.py` (line 6, 68): `(parts.<p>.may_import)` → `(parts.<p>.imports.may)`.
- `rules/domain/vocabulary.py` (line 35, 259, 307, 334, 372-374, 406): the descriptions of the `place` target kind
  ("written as an entry of `imports.may` writes a target, with no name pattern and no mode"), of
  `mirrored_may_import`, and of the filter `may-import-everything` name `imports.may`. The names of variables and
  filters do not change.
- `profile_checks.py:601`, `kernel/logic/targets.py`, `kernel/violations.py`, `source_check.py`, `filters.py`: each
  hit of a part's import key in a message is judged by scope and moved when it names the profile key.
- `where`'s JSON fields `may_import`, `may_import_text`, `libraries`, `test.types_only` keep their words; only prose
  that cites the profile key moves (dodge, CS 970).

### 2.8 `profile check`'s looser lines

`Loosened.key` (a JSON contract, README 392-394) for a part's import keys:

| Before | After | Sentence |
|---|---|---|
| `may_import` | `imports.may` | `{part} may also import {what} (parts.{part}.imports.may)` |
| `libraries` | `imports.libraries` | `{part} may also import {what} (parts.{part}.imports.libraries)`, `{part} may import any outside package (parts.{part}.imports.libraries)`, `outside packages are not checked` |
| `must_import` | `imports.must` | `{part} may also meet imports.must with {what} (parts.{part}.imports.must)`, `{part} no longer has to import anything (parts.{part}.imports.must)` |
| (none) | `imports.may.types_only` | `{part} may now call {what}, which it used only as a type (parts.{part}.imports.may.types_only)` |

The new line, as the card's deliverable names the key: for a part both profiles have, a marked target of the compared
profile's part that the custom part still allows (some target of its `may` covers it, as `_covers` reads) and that no
marked target of the custom part covers is one loosening, `what` the target as `_shown` writes it. A mark dropped
together with its entry is stricter and not listed. No bundled profile marks an entry, so the line fires only between
custom and constructed profiles in tests; release step 16 may restate it with that note's other lines.

The tier keys `types_only`, `may_also_import` and their sentences stay. `LOOSER` (line 35) lists the new keys in place
of the old, `imports.may.types_only` beside `imports.may`. The module docstring and `domain/published.py:109-115`
name the new keys.

### 2.9 Profiles

Rewritten for the group, with no other change (keys under `imports` in the order `may`, `must`, `libraries`):
`architecture.yaml`, `xarch/architectures/web.yaml`, `xarch/architectures/cli.yaml`, the corpora profiles
`tests/bootstrap/corpora/{7cc6111,df537ca,stress}.yaml`, every inline profile of the tests and `docs/examples/**`.
`may_import: everything` becomes `imports: {may: everything}`.

Marks, only where a part writes `types_only` today:

- `7cc6111.yaml:36` and `df537ca.yaml:36` (services, `types_only: [contract]`): `{contract: types_only}` in place of
  `contract` in `may`.
- `stress.yaml` services (line 44, `[contract]`): `{contract: types_only}`; adapters (line 81, `[domain]`):
  `{domain: types_only}`. Lines 211, 228, 244 are tiers' and stay.

Tiers keep their keys in every profile.

### 2.10 Generated docs (CS 5.3, R3 O8)

`docs_template.py` line 403-405 says "`may-import`: every import between parts is one that the `imports.may` of the
importing part allows"; `_part_lines` (line 566-568) reads the marked targets for the `types-only` line (no bundled
profile marks, so no golden line shows it). The template `xarch/architectures/testing.md`'s enforcement paragraph
names `imports.may`, `imports.libraries`, `imports.must` for a part, and adds "a `types_only` mark dropped from an
entry of a part's `imports.may`" to its list of looser ways; its tier words stay. Other templates under
`xarch/architectures/` (`agents.md`, `architecture.md`) that name a part's import key name the new one.

Regenerate `docs/{cli,web,xarch}/testing.md`; the diff may move only the `may-import` line and the enforcement
paragraph, in each of the three copies. Any other moved line is a defect to explain or fix, not to accept.

### 2.11 Recorded corpora (CS 5.5, `test_recorded_corpora.py` docstring)

A change of wording only. Edited by hand, line by line, the stress file decompressed to a scratch copy, edited and
recompressed, with the text diff read (as 4.4 did, `84ebb5a`):

- `(parts.<p>.may_import)` → `(parts.<p>.imports.may)`; `(parts.<p>.must_import)` → `(parts.<p>.imports.must)`;
  `(parts.<p>.libraries)` → `(parts.<p>.imports.libraries)`; `(parts.<p>.types_only)` →
  `(parts.<p>.imports.may.types_only)`; and the same inside a fix's text (e.g. `mirrored_may_import`'s `parts.<p>.`
  half).
- `(tiers.<t>.types_only)` (694 lines of stress), `tiers.<t>.must_import`, `tiers.<t>.may_also_import` stay.
- The three lines naming the source module `xarch.modules.rules.application.logic.must_import` stay.
- Never a blind replace of `types_only)` (dodge, CS 974): each replacement is anchored on `parts.<p>.`.

If any recorded finding differs in more than the key (the types-only rule now reading the own instance, 2.2), that is
a change of what a check finds, recorded only from an oracle extended by the same change (`test_recorded_corpora.py`
docstring); the plan reports it rather than editing the finding.

### 2.12 README and CHANGELOG (CS 5.3, R3 O4, O5)

README: the profile block (117-123) writes `imports: {may, must, libraries}` on a part and drops the four keys; the
symbols list (199-202) names `imports.may` and the mark; the explain examples (210, 223, 321) name
`parts.imports.may` / `parts.imports.must`; the rule table's key column (295, 296, 300, 303) names
`parts.imports.may`, `parts.imports.libraries`, `parts.imports.may.types_only`, `parts.imports.must`; the looser keys
and sentences (392-394, 420, 437-440) name the new keys and the new line; the sample finding (338) and the `where`
text (506) name `parts.<p>.imports.may`; the linter line (1069) names `imports.may` and `imports.libraries`. The
`where` JSON field names (535-565) stay. CHANGELOG, under `[Unreleased]`: "Changed": a part's `may_import`,
`must_import`, `libraries` move into `imports: {may, must, libraries}`; a part's `types_only` becomes the mark
`{<target>: types_only}` on its entry of `imports.may`, read on what the entry reaches; findings and `Loosened` keys
name the new addresses; the old keys are refused with the form that replaces them; tier keys unchanged. "Added": the
looser line `imports.may.types_only`.

## 3. Gates

Each passes on this branch alone with the full suite green:

- `uv run pytest -q` (over two minutes: run in the background, read at the end)
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check` (never `--fix`)
- `uv run xarch profile check architecture.yaml`

And the re-grep (CS 7 step 8, scoped to this step): `git grep -nE "may_import|must_import|libraries|types_only"` over
`xarch/ tests/ README.md CHANGELOG.md docs/ architecture.yaml` finds, for a part, only the retired table, the refusal
tests, keys under `imports`, `where`'s JSON fields, Python identifiers (fields, functions, the filter
`may-import-everything`), the source module `must_import`, plans/specs under `docs/superpowers/**` (history, left
alone), and prose about tiers.

## 4. Project rules

No comments in xarch's code (docstrings only); tests written first; examples simple, with absolute `app.` imports;
recorded corpora edited by hand only, as 2.11 says; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed; golden docs regenerated, never
edited.

## 5. Tests

Each names its tier: **unit** (one module's pure logic, no I/O), **adapter** (one adapter's translation), **wired**
(the app through `xarch.bootstrap.app`, its CLI or its controllers, on real files).

Parsing, `tests/modules/spec/application/logic/` (unit: the parser is pure logic over a document):

1. `test_profile_parsing.py`: `imports: {may: [...], must: [...], libraries: [...]}` gives the `Architecture.rules`,
   `Part.must_import`, `Architecture.libraries` that the old keys gave for the same lists; `may: everything`;
   `may: []`; no `imports`; `imports: {libraries: [x]}` alone leaves `rules` empty.
2. `test_profile_parsing.py`: `imports: {}` → "says nothing ..."; `imports: [kernel]` and `imports: true` → "must be a
   map ..."; `imports: {never: pure}` and `imports: {types_only: [x]}` → their hints; `imports: {also: [x]}` → plain
   unknown key ending in "use libraries, may, must".
3. `test_profile_parsing_substance.py`: a marked entry `{contract: types_only}` gives `Part.types_only ==
   (Target("contract", "own"),)` and leaves `contract` in `rules`; `{contract@any: types_only}` keeps the scope;
   `{"domain/values:*Id": types_only}` keeps path and pattern; two marks keep the order of `may`.
4. `test_profile_parsing_substance.py`: `{ports: types}`, `{ports: true}`, `{ports: types_only, domain: types_only}`,
   `{}`, `{everything: types_only}` → the texts of 2.3; a marked entry naming an undeclared part → the target
   grammar's problem at `parts.<p>.imports.may`.
5. `test_profile_parsing.py` (or `test_targets_written.py`): `must` entry not in `may` → the new text; a `must` entry
   equal to a marked `may` entry passes; `{platform: types_only}` in `must` → "must takes references only, with no
   mode"; `must: []` → "must be a list of targets ...".
6. `test_targets_written.py`: a tier folder's `may_import` with a map entry is refused with today's text (the mark is
   a part's only).
7. `test_retired_keys.py`: each of `may_import`, `must_import`, `libraries`, `types_only` on a part → its hint, one
   problem each when written together; `types_only`, `may_import`, `must_import`, `may_also_import` on a tier load.
8. `test_profile_parsing.py`: the reserved-module problem and a `never` list's first-naming place cite
   `parts.<p>.imports.libraries`.
9. `test_profile_needs.py`: a language without `call` and a profile with a mark → shortfall at
   `parts.<p>.imports.may.types_only`; the same profile without the mark → none for it; `imports.must` and
   `imports.libraries` shortfalls at their new addresses.
10. `test_looseness.py`: each of the moved keys gives its new key and sentence; the new line fires for a dropped
    mark whose entry stays, not when the entry is dropped too, not when a custom mark covers it.
11. `test_explain.py` / `test_key_catalogue.py`: the new addresses have texts and rules; the old part addresses answer
    from the retired table; one text per key.

Domain, `tests/modules/spec/domain/test_profile_keys.py` (unit): the scope `parts.<part>.imports` exists with `may`,
`must`, `libraries`; the four part keys are gone from `PART` and present in `RETIRED`; tier keys unchanged.

Rules, `tests/modules/rules/application/logic/` (unit: expansion and matching over a built `Profile`):

12. `test_types_only.py`: a part with a marked own-instance target: calling a function of its own instance of that
    part is a finding keyed `parts.<p>.imports.may.types_only`, with today's sentence; calling one of another instance
    (reached through an unmarked `@any` entry) is not; a marked patterned entry still catches a call on a name it
    allows.
13. `test_expansion.py` / `test_imports.py` / `test_libraries.py` / `test_must_import.py`: the keys of 2.7 on each
    rule; tier rules keep their keys.
14. `test_expandable.py` / `test_explained.py`: `KEYS` holds the four new keys and not the old; `keyed(rules,
    "parts.imports.may")` lists `may-import` only.
15. `test_sentences.py`: `mirrored_may_import` text names `parts.<p>.imports.may`; `_caller_fix` skips a part whose
    entry for the target is marked.

Adapter, `tests/modules/rules/adapters/test_spec_profile.py` (adapter: the translation from `ProfileView` to
`Profile`): `Profile.types_only` holds each part's marked targets.

Wired, `tests/bootstrap/` (the CLI or controllers on real profile files):

16. `test_bundled_imports.py`, new, written first and passing on the code before the change: for each bundled profile
    and `architecture.yaml`, `xarch where --format json` on one file of every part gives the same `may_import`,
    `may_import_text` and `libraries` before and after (literals recorded in the test from the pre-change run, by
    hand), and `profile explain` lists, per part, the same `may-import`/`must-import`/`libraries` rules but for the key.
17. `test_profile_explain.py`: `xarch profile explain parts.imports.may.types_only` and `parts.may_import` (retired
    hint), exit codes as today.
18. `test_profile_check.py` / `test_check_json.py`: a custom profile adding a target to a part's `may` reports key
    `imports.may` and the new sentence in text and JSON.
19. `test_docs_templates.py`: the golden copies, regenerated, equal byte for byte (the diff read per 2.10).
20. `test_recorded_corpora.py`: the corpora replay with the edited profiles and findings (2.11).
21. `test_needs_agree.py`: `EVERY_KEY` writes `imports` with `may` (one marked entry), `must`, `libraries`.
22. `tests/bootstrap/test_rule_ids.py`, `tests/architecture/test_readme.py`: unchanged ids pass.
23. `tests/architecture/test_language_seam.py` and every other test with an inline profile: rewritten for the group
    (O15), each edit a key move only.

## 6. Risks the plan must settle

- The types-only rule's reach narrows from "the part by name, any instance" to "what the entry reaches". The
  recorded corpora (7cc6111 services, stress services and adapters) are the test: if a recorded types-only finding
  was on a call into another instance, it would vanish (2.11). Check before editing the findings.
- `Match("place")` with a target that holds a name pattern never matches (`kernel/logic/placement.py:95`): drop the
  pattern for the types-only match (2.6).
- `targets_written.may_import` is shared with tiers (`profile_parsing.py:645-647`): the mark must be read on a part's
  `may` only, with tiers' texts unchanged.
- `_named_packages` reads a raw document before validation: it must read `imports.libraries` defensively (a non-map
  `imports` names nothing) and stay silent.
- The needs walker reaches mappings only; the mark is a list entry keyed by a target. 2.5 fixes the outcome.
- `keys.yaml` and `key_table.py` change in one commit (the catalogue test reads both).
- Every inline profile is touched; O15 says one pass for the group, and the part-references step re-spells later.

## 7. Out of scope

- A tier's `imports` group (`tiers.<t>.imports: {may, also, must, types_only}`): card 4.6, release step 14.
- The reference grammar (`parts.<p>`, `module.<p>`), and re-spelling entries: story 8, release step 24.
- Renaming internal fields and functions (`must_import`, `types_only`, `rules`, `may_import`, `libraries`): release
  step 15.
- Other new looser lines of the comparison: release step 16.
- `where`'s JSON fields; rule ids; the README id list.
- Adding a mark to a bundled profile or to xarch's own.

## 8. Plan hand-off

The plan follows `writing-plans` (header, global constraints, review focus, bite-sized TDD tasks with exact files and
code, commits per task). Suggested order, each task green on the full suite at its end: (1) `profile_keys`/
`key_table`/`keys.yaml` scope, rows, needs and retired entries, the parser reading `imports` and the mark, every
profile and inline test profile rewritten, the adapter carrying marked targets, rules still keyed by the old strings
until (2); (2) rules keyed and worded by the new addresses, `KEYS`, sentences, vocabulary, the types-only rule on
places, corpora findings edited; (3) looseness keys and the new line; (4) docs template, templates, golden docs
regenerated, README, CHANGELOG. The plan may merge or split these as the gates require.

## 9. Dodges (card; CS 948-976)

- A second list for a part's `types_only` beside the mark (`imports.types_only` is refused with a hint).
- A mode word other than `types_only`, or `must` as a mode.
- Dropping the check that a `must` entry is in `may`.
- Putting `never` in `imports`.
- Renaming rule ids or `where`'s JSON fields.
- Keeping `Loosened` keys on the old words.
- A blind replace of `types_only)` in findings.
- Accepting the old keys as aliases or with a warning.
- Adding a mark to a bundled profile in this change.
