# 5.2 The looser lines cover every loosening of 0.3.0 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `profile check` and `check`'s enforcement section list every way a custom profile is looser than the one it
is compared with: a kind a part's `holds` newly allows, a setting of a held kind dropped or widened, a part's `shared`
dropped or lowered, a tier's `imports.must` dropped or widened, a tier no longer `plain_tables`, and (its sentence
only, its branch lands with 6.10) `testing.beside`.

**Architecture:** Everything is in `_looser(custom, base)` and `_sentence` of
`xarch/modules/spec/application/logic/looseness.py`, on the parts and tiers 5.1 pairs (`_paired_parts`,
`_paired_tiers`), part names read through the pairing. Four small private helpers join it in the same file:
`_allowed` (the kinds a part's `holds` allows), `_held_to` (the settings a part holds a kind to), `_settings_looser`
(the seven `holds.<kind>.<setting>` ways for one paired part) and `_added` (a list of part names dropped or widened,
shared by `built_by` and a tier's `imports.must`), plus `_held_sentence` for the seven settings keys. `LOOSER` gains
the new keys in the order lines are found. Tests are all logic-tier, in
`tests/modules/spec/application/logic/test_looseness.py`, through the public `origin_of` (the file's `loosened()`).

**Tech Stack:** Python 3.13, `uv`, `pytest`, `ruff`, xarch's own `xarch check` / `xarch profile check`.

**Spec:** `docs/superpowers/specs/5-2-spec-the-looser-aabea037.md` (prepended below, verbatim).

Every test and expectation in this plan was reproduced by running this plan's code on a scratch copy of the branch
(HEAD `3e3d4dc`): the 98 tests of `test_looseness.py` green, the whole suite green, `ruff check` clean, `xarch check`
and `xarch check --strict` exiting 0, `xarch profile check architecture.yaml` printing output byte-identical to
today's, and the golden docs `docs/{cli,web,xarch}` regenerating with no change.

## Global Constraints

- No comments in xarch's code (docstrings are the place); never `ruff --fix`; tests written first.
- Examples simple, with absolute `app.` imports (no example is touched by this step).
- Python only in the reader adapter and the data files under `xarch/architectures/presets/` (nothing here changes that).
- `.claude/` stays out of commits; nothing is pushed.
- README and CHANGELOG lines under `[Unreleased]`; golden docs regenerated and their diff read, never edited by hand.
- Commit messages: one long descriptive sentence, no prefix, then a blank line and
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- `--strict` still fails only on the `litmus` key (`xarch/modules/rules/application/logic/enforcement.py:82-85`): do
  not touch it. Every new line is information.
- The match's counting (`_items`, `_part_keys`, `_tier_keys`, `_counted`, `_counts`) is 5.1's: do not touch it.
- The tier key is `tiers.imports.must`, never `imports.must` (that is the part key); the other tier keys keep their
  bare names (`plain_tables`).
- `testing.beside` gets only its `LOOSER` entry and its `_sentence` case: no `_looser` branch, no `getattr`, no field.
- xarch's own profile holds the unit tier to `plain_tables`: a parametrized test in `test_looseness.py` must have no
  `if` (statement or expression) anywhere in its body, nested functions included. `xarch check --strict` flags one.
  Put each case's documents in the table instead.
- Run the full suite only in the background with `timeout` (about three and a half minutes):
  `timeout 900 uv run pytest -q -p no:cacheprovider`.
- Never use `pkill`/`killall`/pattern `kill`; stop a stuck run with `timeout` or the PID you recorded.

## Review Focus

1. A part that listed `classes` with `names` in the base and lists only `exceptions: {}` in the custom profile:
   exceptions were held to `classes.names` and now to none, so `holds.exceptions.names` is listed dropped, and no
   `holds` line (exceptions were allowed). Test: row `exceptions listed alone, held to the names of classes before`,
   Task 2.
2. A base `names` pattern of `*`: it covers every custom pattern, so no widened line whatever the custom profile
   writes. Test: row `a pattern of the base of * covers every pattern`, Task 2.
3. A `built_by` naming a part renamed in place, widened by one more part: the renamed part reads as itself and only
   the new part is listed. Test: row `a built_by naming it widened, it read as itself`, Task 2.
4. A part renamed *and* moved (it pairs with none) whose base counterpart had `holds` settings and `shared`: compared
   in no way, no line. Test:
   `test_a_part_that_pairs_with_none_is_compared_neither_on_what_it_holds_nor_on_how_widely_it_is_shared`, Task 3.
5. `shared` kept at the same number: no line (equal is not lower). Test: row `kept`, Task 3.

---

## The spec

# 5.2: the looser lines cover every loosening of 0.3.0

Card `aabea037`, subtask of `3c8f968f`, release step 16 of the merged order (`0.3.0-cohesion-review-3.md`, section 3,
row 16, line 279), after 5.1 (`f004b3d1`, pairing and the match, already on this branch). Parent design:
`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-comparison-design.md`, cited below as "note §n, line L";
the third cohesion review, `0.3.0-cohesion-review-3.md` in the same folder, as "review 3".

This step builds note §5 item 9 (lines 346-353), the `_looser` half of item 1 (lines 322-325: a renamed part's
targets read through the pairing, for the new keys), the CHANGELOG line of item 12 (lines 362-365, "Changed: the
looser lines cover every loosening of 0.3.0"), and review 3's C12 (lines 191-197) and the soft cycle of row 16 (lines
292-294).

## 1. What changes for a person

`profile check` and `check`'s enforcement section list every way a custom profile is looser than the profile it is
compared with. Today a profile can loosen a part's `holds`, its `shared`, a tier's `imports.must` or `plain_tables`,
and `profile check` says nothing (note, facts, lines 52-55). After this step each of these is one line, under its own
key, said by its own sentence ending in the 0.3.0 address that says it (ruling, note lines 31-33; vocabulary, review
3 line 349):

| Key (`Loosened.key`) | When it is listed | `part` | `what` |
|---|---|---|---|
| `holds` | a kind the custom part's `holds` allows that the base part's does not | the custom part | the kind |
| `holds.<kind>.<setting>` (7 keys, §2.2) | a setting of a kind dropped or widened | the custom part | `""` dropped; the pattern or part added |
| `shared` | a part's `shared` dropped, or lowered | the custom part | `""` dropped; the custom number lowered |
| `tiers.imports.must` | a tier's `imports.must` dropped, or a part added to it | the custom tier | `""` dropped; the part added |
| `plain_tables` | a tier no longer `plain_tables` | the custom tier | `""` |
| `testing.beside` | `testing.beside` set where the compared profile leaves it out | `""` | `""` |

`imports.may.types_only` (a dropped `types_only` mark) is already listed, built in 4.5. This step only checks that it
still holds and that it is read through the pairing (the existing tests at
`tests/modules/spec/application/logic/test_looseness.py:185-212` and `:418-428`); no new code.

Nothing changes for `--strict`: it still fails only on the `litmus` key (`xarch/modules/rules/application/logic/enforcement.py:82-85`).
Every new line is information (note, facts, line 70).

## 2. The comparison (normative)

All comparison is in `_looser(custom, base)` (`xarch/modules/spec/application/logic/looseness.py:222-283`), on the
parts and tiers that pair as 5.1 pairs them (`_paired_parts`, `_paired_tiers`), never on a part or tier that pairs
with none (note §5 item 1, line 322-325; module docstring lines 16-17). Where a value names a part, the custom
profile's part name is read through the part pairing (`pairs`: custom name to base name) before it is compared, and
said under the custom profile's name (`back`: base name to custom name). Each new way is appended in the order of
the table above, the part ways inside the existing per-part ways after `LITMUS`, the tier ways after
`uses.apply_never`, and `testing.beside` after `testing.skips` (so `LOOSER`'s order, which is the order lines are
found in, stays "part keys, tier keys, profile keys").

### 2.1 `holds`: a kind added

The kinds a part's `holds` **allows**: when `holds` is empty (no key written), every one of `KINDS`
(`xarch/modules/spec/domain/published.py:49`); otherwise the kinds it lists, plus `records` and `exceptions` when it
lists `classes` (a class of a narrower kind is a class; `holds_written.py:36`, `NARROWER`; the rule at
`xarch/modules/rules/application/logic/expansion.py:264-287` exempts them).

One line, key `holds`, for each kind of `KINDS`, in `KINDS` order, that the custom part allows and the base part does
not. So:

- base `{functions: {}}`, custom `{functions: {}, classes: {}}`: three lines, `classes`, `records`, `exceptions`.
  Each kind is its own line because `check` reads each as a kind of its own (the match counts one item per kind,
  `_part_keys` lines 138-140), and each is a kind of definition the part may now hold.
- base `{classes: {}}`, custom `{classes: {}, records: {immutable: true}}`: no `holds` line (records were allowed).
- base `{classes: {}}`, custom no `holds`: `functions` (records and exceptions were allowed through classes).
- base no `holds`, custom anything: no `holds` line (everything was allowed).
- a kind dropped: stricter, no line.

Sentence: `{part} may also define {what} at the top level (parts.{part}.holds)`.

### 2.2 `holds.<kind>.<setting>`: a setting dropped or widened

The keys, in this order, one per setting each kind takes (`holds_written.py:1-4`): `holds.classes.names`,
`holds.classes.immutable`, `holds.classes.built_by`, `holds.functions.names`, `holds.records.names`,
`holds.records.immutable`, `holds.exceptions.names`.

**The settings a part holds a kind to** (its *effective* settings), as `check` holds a definition to the settings of
the narrowest kind listed that it fits and to no other's (CHANGELOG `[Unreleased]`, Added, the `records`/`exceptions`
entry): the settings written under that kind when the part lists it; else, for `records` or `exceptions`, those
written under `classes` when the part lists `classes` (`immutable` never applies to `exceptions`: `classes.immutable`
says "every class but an exception"); else none.

A kind is compared when **either** profile's part lists it and **both** allow it. A kind neither lists is not
compared even if it reaches settings through `classes` (otherwise one edit of `classes.names` would print the same
loss three times). For each compared kind, its effective settings in the base against those in the custom part:

- `names` (a tuple of patterns, `*` any text): **dropped** when the base has patterns and the custom has none: one
  line, `what` `""`. **Widened** when both have patterns: one line per custom pattern that no base pattern covers,
  `what` the pattern. A base pattern `q` covers a custom pattern `p` when `p`, read as a name, matches `q`
  (`name_matches(q, p)`, `xarch/kernel/logic/placement.py:83`): `FooService` and `*Service` are covered by
  `*Service`; `*` is not. A pattern dropped from a list that keeps others is stricter: no line.
- `immutable`: **dropped** when the base is true and the custom false: one line, `what` `""`.
- `built_by` (part names; empty means any part): **dropped** when the base names parts and the custom names none:
  one line, `what` `""`. **Widened** when both name parts: one line per custom part whose name, read through the
  pairing, the base does not name, `what` the custom part's name as written.

Sentences (`{kind}` from the key):

- `holds.<kind>.names`, dropped: `the {kind} of {part} may be named anything (parts.{part}.holds.{kind}.names)`
- `holds.<kind>.names`, widened: `the {kind} of {part} may also be named {what} (parts.{part}.holds.{kind}.names)`
- `holds.<kind>.immutable`: `the {kind} of {part} need no longer be immutable records (parts.{part}.holds.{kind}.immutable)`
- `holds.classes.built_by`, dropped: `the classes of {part} may be built by any part (parts.{part}.holds.classes.built_by)`
- `holds.classes.built_by`, widened: `the classes of {part} may also be built by {what} (parts.{part}.holds.classes.built_by)`

The address names the kind compared, the place the custom profile would write the setting back, even when the base's
setting came through `classes`.

### 2.3 `shared`

`Part.shared` (`values.py:84`, `int | None`): one line when the base part sets it and the custom part does not
(**dropped**, `what` `""`), or sets a lower number (**lowered**, `what` the custom number as `str`). A higher number,
or the base setting none, gives no line.

- dropped: `{part} is no longer held to be shared (parts.{part}.shared)`
- lowered: `the public names of {part} need only {what} users, fewer than the profile it is compared with asks (parts.{part}.shared)`

### 2.4 `tiers.imports.must`

`Tier.imports_must` (`values.py:231`, part names; empty: no such rule). Compared on paired tiers. **Dropped** when the
base tier names parts and the custom names none: one line, `what` `""`. **Widened** when both name parts: one line per
custom part whose name, read through the pairing, the base does not name, `what` the custom name (each test file may
now meet the rule through it). The key is `tiers.imports.must`, not `imports.must`: `imports.must` is already the part
key (`LOOSER`, line 51) and a key says one sentence (`_sentence` is a `match` on the key, line 338). It is the one key
two holders share in 0.3.0, so the prefix its address starts with separates them; the other tier keys
(`imports.types_only`, `imports.also`, `uses.apply_never`, `plain_tables`) belong to tiers only and keep their bare
names.

- dropped: `the {part} tests no longer have to reach any part (tiers.{part}.imports.must)`
- widened: `the {part} tests may also meet imports.must by reaching {what} (tiers.{part}.imports.must)`

### 2.5 `plain_tables`

One line when the base tier is `plain_tables` and the paired custom tier is not:
`the table tests of the {part} tests may now branch (tiers.{part}.plain_tables)`.

### 2.6 `testing.beside` (written now, tested with 6.10)

`testing.beside` does not exist on this branch: no key in `xarch/architectures/presets/format/keys.yaml`, no field
on the `Framework` value (explore finding; review 3 row 21, line 284). It lands in step 21, card 6.10 (`06615c54`),
whose deliverable says it "adds the test of 5.2's `testing.beside` looser line". Review 3, lines 292-294: "The looser
line is written in 16 against the key's address and its test is added in 21."

So this step adds, and only adds:

- `"testing.beside"` to `LOOSER`, after `"testing.skips"`;
- its `_sentence` case: `tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)`
  (review 3 C12, line 196: a profile-wide item, "set where the compared profile leaves it out"; note line 350).

The `_looser` branch that reads the setting is **not** written here: there is no field to read, and a branch reading
an attribute that does not exist (`getattr`) is code no test can reach. 6.10 adds the field, the branch (one line,
key `testing.beside`, `part` and `what` `""`, when the custom profile's `testing.beside` is true and the base's is
not), and its test. The sentence is the contract 6.10 builds against.

The every-key test (§4, T10) therefore reaches every key of `LOOSER` but this one, which it names as the one key it
cannot reach until 6.10, so that 6.10 deletes the exception and the test then demands the line.

### 2.7 What is not listed

- A kind dropped from `holds`, a setting added, a pattern dropped from a `names` list that keeps others, a part dropped
  from `built_by` that keeps others, `shared` raised or newly set, a part dropped from a tier's `imports.must` that
  keeps others, `plain_tables` newly set: stricter.
- A part or tier that pairs with none: compared in no way (unchanged from 5.1).
- `records` or `exceptions` written beside `classes` frees its definitions from `classes.built_by` (neither kind takes
  `built_by`, `holds_written.py:1-4`). No 0.3.0 key says that setting for those kinds, so it is not listed; named
  here so the planner does not invent a key for it.
- `no-callbacks`: a dropped guard already shows under `guards off` (card, out of scope; note line 351).
- `holds` patterns are compared by the coverage test of §2.2, not as sets of names: a custom pattern that narrows by
  another shape (`A*` against `*B`) is listed. Stated, not fixed: `check`'s patterns have no containment test.

### 2.8 The dodge

Note, dodges, lines 421-423: "Counting a key one side drops as a mismatch ..., or as comparable without `_looser`
reading it." After this step every part key and tier key that the match counts as comparable when one side drops it
(`_part_keys` lines 128-141: `holds`, each setting, `shared`; `_tier_keys` lines 144-149: `imports.must`,
`plain_tables`) is read by `_looser` in the direction that loosens. The match's counting is not touched (5.1's).
Keys the match counts that are not read, each for a reason already in the module docstring: `entry` and
`package_only` (dropping them is no loosening of a part's own rules: `package_only` is a guard, shown under `guards
off` when no part keeps it), a tier's `imports.may` (its folder's allowance: compared nowhere in 0.3.0, note line
34 "the layout"), `fakes`, `excluded`, checks of the profile's own.

## 3. Docs

- `looseness.py` module docstring (lines 16-34): the list of ways gains, in the words of §2, a kind added to a part's
  `holds` (classes allowing records and exceptions); a setting of a kind dropped or widened (`names`, `immutable`,
  `built_by`, compared kind by kind on the settings the part holds the kind to, for a kind either lists); `shared`
  dropped or lowered; a tier's `imports.must` dropped or widened; a tier no longer `plain_tables`; `testing.beside`
  set where the other leaves it out. No comment in code (project rule); the docstring is the place.
- README, the enforcement paragraph (README.md:451-457, `profile check` section): the same additions in its list
  (O4: this step's tokens only).
- CHANGELOG `[Unreleased]`, `### Changed` (O5; note line 365): one entry, "the looser lines cover every loosening of
  0.3.0", naming each new key and quoting one sentence, `holds.classes.names` as the example.
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated, diff read, expected **unchanged** (O8, review 3 line
  232). Their list of looser ways comes from `xarch/architectures/testing.md`; note §5 (items 10-12) names no doc
  for item 9, so the template is not edited here. Its list is stale (it also still says "the one sharing the most
  parts", from before 5.1); that is for step 25's read of the docs, and is said in the result note.
- `keys.yaml` and `profile explain`: unchanged (no key of the format changes).

## 4. Tests

All in `tests/modules/spec/application/logic/test_looseness.py`, tier **logic** (this file's tier): `_looser` is a
pure function of two parsed architectures, reached through the public `origin_of` via the file's `loosened()`
helper, fed from `layered()` / `BASE` documents through `parsed()`; nothing touches disk or the CLI. Tests are
written first (project rule). Each asserts the whole `Loosened` (key, part, what, sentence) for the line it pins, and
`()` or no line of that key for the stricter cases.

T1 `holds`, a kind added (parametrized, one id per row):
- base `{functions: {}}` → custom `{functions: {}, classes: {}}`: lines `classes`, `records`, `exceptions`, in that order.
- base `{classes: {}}` → custom `{classes: {}, records: {immutable: true}}`: no `holds` line.
- base `{classes: {}}` → custom no `holds`: one line, `functions`.
- base no `holds` → custom `{functions: {}}`: none.
- base `{functions: {}, classes: {}}` → custom `{functions: {}}`: none (dropped is stricter).

T2 `holds.<kind>.names` (parametrized):
- base `classes: {names: "*Service"}` → custom `classes: {}`: dropped, `what` `""`.
- → custom `classes: {names: ["*Service", "*"]}`: widened, `what` `*`.
- → custom `classes: {names: "FooService"}`: none (covered).
- base `names: ["*Service", "*Store"]` → custom `names: "*Service"`: none (a pattern dropped from a list is stricter).
- base `functions: {names: "is_*"}` → custom `functions: {}`: key `holds.functions.names`.
- base `classes: {names: "*Service"}` → custom `classes: {names: "*Service"}, records: {immutable: true}`: one line,
  `holds.records.names`, dropped (records were held to `*Service` through classes, and now to nothing).
- base `classes: {names: "*Service"}` → custom the same: none (records not listed by either, not compared).

T3 `holds.<kind>.immutable`: base `records: {immutable: true}` → custom `records: {}`: one line; base `classes:
{immutable: true}` → custom `classes: {}`: `holds.classes.immutable`; base `classes: {immutable: true}` → custom
`classes: {immutable: true}, exceptions: {names: "*Error"}`: no `immutable` line (exceptions are never immutable).

T4 `holds.classes.built_by`: base `[bootstrap]` → custom `{}`: dropped; → custom `[bootstrap, api]`: widened, `what`
`api`; → custom `[bootstrap]`: none; base `{}` → custom `[bootstrap]`: none.

T5 `shared`: base 3 → custom none: dropped; base 3 → custom 2: lowered, `what` `2`; base 2 → custom 3: none; base none
→ custom 2: none.

T6 `tiers.imports.must`: on the tier of `BASE` (`tests/modules/spec/application/origins.py`) given `imports: {must:
[core]}`: custom without `must`: dropped; custom `must: [core, store]`: widened, `what` `store`; custom `must: [core]`:
none; base without `must`, custom with: none.

T7 `plain_tables`: base tier `plain_tables: true` → custom without: one line; base without → custom with: none.

T8 Renamed in place (extend the two existing parametrized tests at `test_looseness.py:412` and `:424`):
- no line when only a part is renamed (`as_routes`), for each new key: `holds` with settings on `api`
  (`classes: {names: "*Api", built_by: [service]}`, `shared: 2`), a `built_by` naming `api` on another part, a tier
  `imports.must` naming `api`;
- a line under the new name: `built_by: [service]` dropped on the renamed part (part `routes`); a tier
  `imports.must: [api]` widened to `[routes, store]` reads `routes` as `api` and lists only `store`.

T9 A tier renamed in place (paired by subject, 5.1's `test_a_tier_renamed_with_the_same_subject_pairs_by_subject`
shape): `plain_tables` dropped on it is listed under the custom tier's name.

T10 Every key has a sentence of its own: extend
`test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own` (line 156) with one pair per new key family, so
`sorted({item.key for item in found}) == sorted(key for key in LOOSER if key not in LATER)` where `LATER =
{"testing.beside"}`, a constant of the test file whose docstring says it is reached by 6.10, which empties it. Its
existing sentence-uniqueness assertion is kept. All seven `holds.<kind>.<setting>` keys are reached.

T11 Order: one test that a custom profile loosening a part's `holds` kind, `classes.names`, `shared`, a tier's
`imports.must` and its `plain_tables` lists them in that order, after the part's existing keys and the tier's
`uses.apply_never` (the shape of `test_every_way_a_profile_is_looser_than_another_is_found_in_order`, line 54).

T12 The dodge (extend `test_a_key_one_side_drops_on_a_paired_part_is_comparable_and_listed_looser`, line 244, or a
parametrized sibling): for `holds` dropped wholesale, a `names` setting dropped, `shared` dropped, a tier's
`imports.must` dropped and `plain_tables` dropped, the match still counts the item comparable (unchanged) **and**
`loosened` lists it.

Not tested here: the `testing.beside` sentence (no field reaches it; 6.10, §2.6). Not affected, expected to pass
unchanged: `tests/modules/spec/application/test_origin.py`, `tests/bootstrap/test_profile_check.py`,
`tests/cli/reports/test_profile_report.py`, `tests/bootstrap/test_docs_templates.py`, the recorded corpora.

## 5. Gates

`uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile
check architecture.yaml`, then `uv run pytest -q` in the background, read at the end (card). `profile check
architecture.yaml` is expected to print the same `compared:` list as before this step (inferred: against cli, xarch's
profile writes the same `holds`, adds `plain_tables` and tier `imports.must`, which is stricter, and no lower
`shared`); any new line it prints must be read and be a true loosening, and is named in the result.

## 6. Out of scope

- The match, pairing, `LOW`, `Origin`'s fields: 5.1 (done).
- `--against`, `origin(location, against)`, the `--strict` refusal, help texts: 5.3 (`e53507eb`).
- `based_on` as a path, the anchor, `unplaced` on the chain, `keys.yaml`'s `based_on`: 5.4 (`1fe75b29`).
- The `testing.beside` key, field, its `_looser` branch and the test of its line: 6.10 (`06615c54`).
- `_shown`'s form of a target: step 24, part references (review 3 row 24).
- A `no-callbacks` line (card).
- Editing `xarch/architectures/testing.md` or the golden docs (§3).
- Comparing a tier's `imports.may` (a folder's allowance), `entry`, `package_only`, `fakes`, guards' other parameters.

## 7. For the planner (writing-plans format)

Global constraints, verbatim from the card: no comments in xarch's code; never `ruff --fix`; tests written first;
examples simple, with absolute `app.` imports; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed; README and CHANGELOG lines under
`[Unreleased]`; golden docs regenerated and their diff read, never edited by hand. Commit messages: one long
descriptive sentence, no prefix, the Co-Authored-By line.

Files: `xarch/modules/spec/application/logic/looseness.py` (LOOSER, `_looser`, `_sentence`, docstring; a helper
for allowed kinds and effective settings stays in this file, it is comparison logic),
`tests/modules/spec/application/logic/test_looseness.py`, `README.md`, `CHANGELOG.md`.

Task shape suggested: (1) `holds` kinds; (2) `holds` settings; (3) `shared`; (4) tier `imports.must` and
`plain_tables`; (5) `testing.beside` key and sentence, the every-key and order tests, renamed-in-place rows; (6) docs
(docstring, README, CHANGELOG) and the golden-doc regeneration check. `_sentence` for the seven settings keys may
share one `case` guarded on the key's prefix, so long as each key yields its own sentence.

---

## File structure

- `xarch/modules/spec/application/logic/looseness.py` — modified in Tasks 1-5 (imports, `HELD`, `LOOSER`, `_looser`,
  `_allowed`, `_held_to`, `_settings_looser`, `_added`, `_sentence`, `_held_sentence`) and Task 6 (module docstring).
  All comparison logic stays in this one file, as the spec says.
- `tests/modules/spec/application/logic/test_looseness.py` — modified in Tasks 1-5: helpers `holding`, `reaching`,
  `plain`, `tight`, `tiered`; constant `LATER`; new tests appended at the end of the file; rows added to two existing
  parametrized tests; one pair per new key family added to the every-key test.
- `README.md`, `CHANGELOG.md` — Task 6.
- `docs/{cli,web,xarch}/**` — regenerated in Task 6, expected unchanged.

Not touched: `tests/modules/spec/application/origins.py`, `tests/modules/spec/profiles.py`,
`xarch/architectures/testing.md`, `keys.yaml`, the recorded corpora.

How to read the test file: `loosened(custom, base)` (line 17) returns `origin_of(...).looser`, a tuple of
`Loosened(key, part, what, sentence)`. `parsed(document)` parses a profile document (a dict). `layered()` (parts
`api`, `service`, `store`, `shared`, no tiers), `covered()` (`layered()` plus `testing` with a table, tiers `unit`
— subject `service` — and `integration` — subjects `api`, `store`) live in `tests/modules/spec/profiles.py`.
`BASE`, `TIER`, `PARTS`, `TESTING` live in `tests/modules/spec/application/origins.py` (`BASE`'s testing has no
`table`, so a `plain_tables` tier cannot be written on it: use `covered()` for that). `given(document, name,
**keys)` (line 385) merges keys into one part, `renamed(document, old, new)` (line 231) renames a part in place,
`as_routes(value)` (line 391) renames every `api` to `routes`, `compared(custom, base)` (line 226) returns the whole
`Origin`. A parametrize table's arguments are evaluated at import, so a helper a table calls must be defined above
that table in the file.

---

### Task 1: A kind a part's `holds` newly allows is looser

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (imports at lines 42-46, `LOOSER` at 51-53, `_looser`
  after line 255, a new `_allowed` before `_known` at line 286, `_sentence` after the `litmus` case at 357-358)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: `KINDS = ("classes", "functions", "records", "exceptions")` from `xarch.modules.spec.domain.published`;
  `NARROWER = ("records", "exceptions")` from `xarch.modules.spec.application.logic.holds_written`;
  `Part.holds: tuple[Held, ...]` (empty when no `holds` is written).
- Produces: `_allowed(part: Part) -> tuple[str, ...]` (used again in Task 2); key `"holds"` in `LOOSER`, right after
  `LITMUS`; test helper `holding(**holds) -> dict` (used in Tasks 2-4).

- [ ] **Step 1: Record today's `profile check` output (compared in Task 6)**

```bash
uv run xarch profile check architecture.yaml > /tmp/5-2-profile-check-before.txt; echo "exit $?"
```

Expected: `exit 0`.

- [ ] **Step 2: Write the failing tests**

In `tests/modules/spec/application/logic/test_looseness.py`, add the helper right after `as_routes` (after the line
`    return "routes" if value == "api" else value` and its two blank lines, before
`@pytest.mark.parametrize("profile", [`):

```python
def holding(**holds) -> dict:
    """layered(), its part service holding the kinds given, each with its settings; no holds, every kind, when none is
    given."""
    return given(layered(), "service", holds=holds) if holds else layered()


```

Append at the end of the file (after `test_a_way_a_copy_renaming_a_part_in_place_is_looser_is_said_under_the_new_name`,
two blank lines before):

```python


@pytest.mark.parametrize("base, custom, kinds", [
    pytest.param(holding(functions={}), holding(functions={}, classes={}), ["classes", "records", "exceptions"],
                 id="classes added allow records and exceptions too, each a kind of its own"),
    pytest.param(holding(classes={}), holding(classes={}, records={"immutable": True}), [],
                 id="records written beside classes were allowed already"),
    pytest.param(holding(classes={}), holding(), ["functions"],
                 id="holds dropped allows the kinds classes did not, records and exceptions coming through classes"),
    pytest.param(holding(), holding(functions={}), [], id="a base with no holds allowed every kind"),
    pytest.param(holding(functions={}, classes={}), holding(functions={}), [], id="a kind dropped is stricter"),
])
def test_a_kind_a_part_may_now_define_at_the_top_level_is_looser(base, custom, kinds):
    assert [item for item in loosened(parsed(custom), parsed(base)) if item.key == "holds"] == [
        Loosened("holds", "service", kind, f"service may also define {kind} at the top level (parts.service.holds)")
        for kind in kinds]
```

In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, add one pair as the last entry of `pairs`,
after `(parsed(marked(["store", "shared"])), parsed(marked(["store", {"shared": "types_only"}]))),`:

```python
        (parsed(holding()), parsed(holding(classes={}))),
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q -k "top_level or every_key"`
Expected: FAIL for the two rows `classes added allow records ...` and `holds dropped allows ...` (`assert [] == [Loosened('holds', ...`);
the other three rows and the every-key test PASS (no `holds` key in `LOOSER` yet, none found).

- [ ] **Step 4: Write the implementation**

In `xarch/modules/spec/application/logic/looseness.py`, replace the imports

```python
from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, LINE, LITMUS, Loosened, Origin
```

with

```python
from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.holds_written import NARROWER
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Loosened, Origin
```

Replace `LOOSER`

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "imports.types_only", "imports.also", "uses.apply_never", "testing.skips", "files.pinned", "reserved",
          "known", "translated", "review.never", "review.mask", "evals.placement.lines")
```

with

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "holds", "imports.types_only", "imports.also", "uses.apply_never", "testing.skips", "files.pinned",
          "reserved", "known", "translated", "review.never", "review.mask", "evals.placement.lines")
```

In `_looser`, right after the line

```python
    found += [(LITMUS, name, "") for name in shared if base.parts[pairs[name]].litmus and not custom.parts[name].litmus]
```

add

```python
    found += [("holds", name, kind) for name in shared for kind in _allowed(custom.parts[name])
              if kind not in _allowed(base.parts[pairs[name]])]
```

Add this function between `_looser` and `_known` (two blank lines on each side):

```python
def _allowed(part: Part) -> tuple[str, ...]:
    """The kinds a part's holds allows, in the order of KINDS: every kind when it lists none, else those it lists and,
    when it lists classes, the kinds every class covers too."""
    listed = {held.kind for held in part.holds}
    if not listed:
        return KINDS
    return tuple(kind for kind in KINDS if kind in listed or ("classes" in listed and kind in NARROWER))
```

In `_sentence`, right after

```python
        case "litmus":
            return f"{part} has no litmus, though the profile it is compared with gives it one (parts.{part}.litmus)"
```

add

```python
        case "holds":
            return f"{part} may also define {what} at the top level (parts.{part}.holds)"
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: all PASS.

- [ ] **Step 6: Lint and self-check**

Run: `uv run ruff check && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "A kind of definition a part's holds allows that the part it is compared with does not is one looser line under holds, each kind its own, classes allowing records and exceptions too and no holds allowing every kind, said as the part may also define it at the top level

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: A setting of a held kind dropped or widened is looser

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (imports, a new `HELD` before `LOOSER`, `LOOSER`,
  `_looser` after the `holds` line of Task 1, new `_held_to`, `_settings_looser`, `_added` after `_allowed`,
  `_sentence` after the `holds` case, a new `_held_sentence` before `_shown`)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: `_allowed(part: Part) -> tuple[str, ...]` (Task 1); `Held(kind: str, names: tuple[str, ...] = (),
  immutable: bool = False, built_by: tuple[str, ...] = ())` from `xarch.modules.spec.domain.published`;
  `name_matches(pattern: str, name: str) -> bool` from `xarch.kernel.logic.placement`; `holding(**holds)` (Task 1).
- Produces: `HELD` (the seven settings keys, in order); `_added(key: str, holder: str, before: tuple[str, ...], now:
  tuple[str, ...], pairs: Mapping[str, str]) -> list[Looser]` (used again in Task 4 for a tier's `imports.must`).

- [ ] **Step 1: Write the failing tests**

Append at the end of `tests/modules/spec/application/logic/test_looseness.py`:

```python


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={}),
                 [("holds.classes.names", "", "the classes of service may be named anything "
                                              "(parts.service.holds.classes.names)")],
                 id="names dropped"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": ["*Service", "*"]}),
                 [("holds.classes.names", "*", "the classes of service may also be named * "
                                               "(parts.service.holds.classes.names)")],
                 id="a pattern no pattern of the base covers"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "FooService"}), [],
                 id="a pattern a pattern of the base covers"),
    pytest.param(holding(classes={"names": ["*Service", "*Store"]}), holding(classes={"names": "*Service"}), [],
                 id="a pattern dropped from a list that keeps others is stricter"),
    pytest.param(holding(functions={"names": "is_*"}), holding(functions={}),
                 [("holds.functions.names", "", "the functions of service may be named anything "
                                                "(parts.service.holds.functions.names)")],
                 id="the names of functions dropped"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "*Service"}, records={"immutable": True}),
                 [("holds.records.names", "", "the records of service may be named anything "
                                              "(parts.service.holds.records.names)")],
                 id="records held to the names of classes, now listed with none"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "*Service"}), [],
                 id="records neither lists are not compared"),
    pytest.param(holding(classes={"names": "*Service"}), holding(exceptions={}),
                 [("holds.exceptions.names", "", "the exceptions of service may be named anything "
                                                 "(parts.service.holds.exceptions.names)")],
                 id="exceptions listed alone, held to the names of classes before"),
    pytest.param(holding(classes={"names": "*"}), holding(classes={"names": ["*Service", "Odd"]}), [],
                 id="a pattern of the base of * covers every pattern"),
    pytest.param(holding(records={"immutable": True}), holding(records={}),
                 [("holds.records.immutable", "", "the records of service need no longer be immutable records "
                                                  "(parts.service.holds.records.immutable)")],
                 id="records no longer immutable"),
    pytest.param(holding(classes={"immutable": True}), holding(classes={}),
                 [("holds.classes.immutable", "", "the classes of service need no longer be immutable records "
                                                  "(parts.service.holds.classes.immutable)")],
                 id="classes no longer immutable"),
    pytest.param(holding(classes={"immutable": True}), holding(classes={"immutable": True}, exceptions={"names": "*Error"}),
                 [], id="exceptions are never held to immutable"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={}),
                 [("holds.classes.built_by", "", "the classes of service may be built by any part "
                                                 "(parts.service.holds.classes.built_by)")],
                 id="built_by dropped"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={"built_by": ["api", "store"]}),
                 [("holds.classes.built_by", "store", "the classes of service may also be built by store "
                                                      "(parts.service.holds.classes.built_by)")],
                 id="a part added to built_by"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={"built_by": ["api"]}), [],
                 id="built_by kept"),
    pytest.param(holding(classes={}), holding(classes={"built_by": ["api"]}), [], id="built_by newly written"),
])
def test_a_setting_of_a_kind_held_dropped_or_widened_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened(key, "service", what, sentence) for key, what, sentence in found)
```

(The spec's T4 names `bootstrap` in `built_by`; `layered()` has no such part, so its parts `api` and `store` stand in.)

In `test_each_key_of_a_part_renamed_in_place_is_compared_with_the_part_it_pairs_with`'s table, after the row
`    pytest.param(marked(["store", {"api": "types_only"}]), id="a target naming it marked types_only"),` add:

```python
    pytest.param(given(layered(), "service", holds={"classes": {"built_by": ["api"]}}), id="a built_by naming it"),
```

In `test_a_way_a_copy_renaming_a_part_in_place_is_looser_is_said_under_the_new_name`'s table, after the row ending
`                 "routes", id="a types_only mark dropped from a target naming it"),` add:

```python
    pytest.param(given(layered(), "api", holds={"classes": {"built_by": ["service"]}}),
                 as_routes(given(layered(), "api", holds={"classes": {}})), "holds.classes.built_by", "routes", "",
                 id="a built_by dropped from it"),
    pytest.param(given(layered(), "service", holds={"classes": {"built_by": ["api"]}}),
                 as_routes(given(layered(), "service", holds={"classes": {"built_by": ["api", "store"]}})),
                 "holds.classes.built_by", "service", "store", id="a built_by naming it widened, it read as itself"),
```

In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, add as the last entry of `pairs`, after
the `holding` pair of Task 1:

```python
        (parsed(holding()), parsed(holding(classes={"names": "*Service", "immutable": True, "built_by": ["api"]},
                                           functions={"names": "is_*"}, records={"names": "*Record", "immutable": True},
                                           exceptions={"names": "*Error"}))),
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q -k "setting_of_a_kind or renaming_a_part or renamed_in_place or every_key"`
Expected: FAIL for every row of `test_a_setting_of_a_kind_held_dropped_or_widened_is_looser` that expects a line (9
rows), and for the two new rows of `..._is_said_under_the_new_name` (`assert [] == [('holds.classes.built_by', ...`).
The rows expecting no line, the new `a built_by naming it` row and the every-key test PASS (no settings key in
`LOOSER` yet).

- [ ] **Step 3: Write the implementation**

In `xarch/modules/spec/application/logic/looseness.py`, replace the imports

```python
from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.holds_written import NARROWER
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Loosened, Origin
```

with

```python
from xarch.kernel.logic.names import outside_text
from xarch.kernel.logic.placement import name_matches
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.holds_written import NARROWER
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Held, Loosened, Origin
```

Replace `LOOSER` (as Task 1 left it) with `HELD` and the new `LOOSER`:

```python
HELD = ("holds.classes.names", "holds.classes.immutable", "holds.classes.built_by", "holds.functions.names",
        "holds.records.names", "holds.records.immutable", "holds.exceptions.names")
"""The key of each setting of a kind of holds, a way it is looser listed under, kind by kind in the order of KINDS."""
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "holds", *HELD, "imports.types_only", "imports.also", "uses.apply_never", "testing.skips",
          "files.pinned", "reserved", "known", "translated", "review.never", "review.mask", "evals.placement.lines")
```

(`HELD` goes right after the `Looser` alias and its docstring; the `LOOSER` docstring line stays below `LOOSER`.)

In `_looser`, right after the `holds` lines Task 1 added:

```python
    found += [("holds", name, kind) for name in shared for kind in _allowed(custom.parts[name])
              if kind not in _allowed(base.parts[pairs[name]])]
```

add

```python
    for name in shared:
        found += _settings_looser(custom.parts[name], base.parts[pairs[name]], pairs)
```

After `_allowed` (two blank lines between each), add:

```python
def _held_to(part: Part, kind: str) -> Held:
    """The settings a part holds a kind to: those written under it when the part lists it; else, for a kind every
    class covers, those written under classes when it lists classes (immutable never for an exception); else none."""
    held = {item.kind: item for item in part.holds}
    if kind in held:
        return held[kind]
    if kind in NARROWER and "classes" in held:
        wider = held["classes"]
        return Held(kind, wider.names, wider.immutable and kind != "exceptions")
    return Held(kind)


def _settings_looser(custom: Part, base: Part, pairs: Mapping[str, str]) -> list[Looser]:
    """Each setting of a kind the custom part drops or widens, against the base part it pairs with: compared for each
    kind either lists that both allow, on the settings each holds the kind to."""
    listed = {held.kind for held in (*custom.holds, *base.holds)}
    found: list[Looser] = []
    for kind in KINDS:
        if kind in listed and kind in _allowed(custom) and kind in _allowed(base):
            before, now = _held_to(base, kind), _held_to(custom, kind)
            if before.names and not now.names:
                found.append((f"holds.{kind}.names", custom.name, ""))
            elif before.names:
                found += [(f"holds.{kind}.names", custom.name, pattern) for pattern in now.names
                          if not any(name_matches(wider, pattern) for wider in before.names)]
            if before.immutable and not now.immutable:
                found.append((f"holds.{kind}.immutable", custom.name, ""))
            if before.built_by:
                found += _added(f"holds.{kind}.built_by", custom.name, before.built_by, now.built_by, pairs)
    return found


def _added(key: str, holder: str, before: tuple[str, ...], now: tuple[str, ...], pairs: Mapping[str, str]) -> list[Looser]:
    """A list of parts the base holder names, against the custom holder's: dropped, one entry; else each custom part,
    read through the pairing, the base does not name, said as written."""
    if not now:
        return [(key, holder, "")]
    return [(key, holder, name) for name in now if pairs.get(name, name) not in before]
```

Why it is right: `Held` for `functions` and `exceptions` always has `immutable=False` and `built_by=()` (the parser
leaves settings a kind does not take at their defaults, `holds_written.py:70-73`), and `_held_to` gives a narrower
kind `built_by=()`, so only `holds.classes.built_by`, `holds.classes.immutable` and `holds.records.immutable` can
come out of the two later branches: exactly the keys of `HELD`.

In `_sentence`, right after the `holds` case of Task 1:

```python
        case "holds":
            return f"{part} may also define {what} at the top level (parts.{part}.holds)"
```

add

```python
        case _ if key.startswith("holds."):
            return _held_sentence(key, part, what)
```

Add this function between `_sentence` and `_shown` (two blank lines on each side):

```python
def _held_sentence(key: str, part: str, what: str) -> str:
    """How a setting of a kind of holds dropped or widened is said, at the address of the kind compared."""
    _, kind, setting = key.split(".")
    at = f"(parts.{part}.{key})"
    match setting:
        case "names" if not what:
            return f"the {kind} of {part} may be named anything {at}"
        case "names":
            return f"the {kind} of {part} may also be named {what} {at}"
        case "immutable":
            return f"the {kind} of {part} need no longer be immutable records {at}"
        case "built_by" if not what:
            return f"the {kind} of {part} may be built by any part {at}"
        case "built_by":
            return f"the {kind} of {part} may also be built by {what} {at}"
    raise ValueError(f"no sentence says how a profile is looser under {key!r}")
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: all PASS.

- [ ] **Step 5: Lint and self-check**

Run: `uv run ruff check && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "A setting of a held kind dropped or widened is one looser line under its own key, holds.classes.names to holds.exceptions.names, compared for each kind either part lists and both allow on the settings the part holds the kind to, records and exceptions through classes, a names pattern widened when no base pattern matches it read as a name and a built_by part read through the pairing

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: A part's `shared` dropped or lowered is looser

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (`LOOSER`, `_looser` after the settings loop of Task 2,
  `_sentence` after the `holds.` case)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: `Part.shared: int | None`; `given`, `renamed`, `holding` (test helpers).
- Produces: key `"shared"` in `LOOSER`, right after `*HELD`.

- [ ] **Step 1: Write the failing tests**

Append at the end of `tests/modules/spec/application/logic/test_looseness.py`:

```python


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(given(layered(), "service", shared=3), layered(),
                 [("", "service is no longer held to be shared (parts.service.shared)")], id="dropped"),
    pytest.param(given(layered(), "service", shared=3), given(layered(), "service", shared=2),
                 [("2", "the public names of service need only 2 users, fewer than the profile it is compared with asks "
                        "(parts.service.shared)")], id="lowered"),
    pytest.param(given(layered(), "service", shared=2), given(layered(), "service", shared=3), [], id="raised"),
    pytest.param(given(layered(), "service", shared=3), given(layered(), "service", shared=3), [], id="kept"),
    pytest.param(layered(), given(layered(), "service", shared=2), [], id="newly set"),
])
def test_a_part_held_to_fewer_users_of_its_public_names_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened("shared", "service", what, sentence) for what, sentence in found)


def test_a_part_that_pairs_with_none_is_compared_neither_on_what_it_holds_nor_on_how_widely_it_is_shared():
    custom = renamed(layered(), "api", "routes")
    custom["parts"]["routes"]["path"] = "src/<module>/routes"
    base = given(layered(), "api", shared=3, holds={"classes": {"names": "*Api"}})
    assert loosened(parsed(custom), parsed(base)) == ()
```

In `test_each_key_of_a_part_renamed_in_place_is_compared_with_the_part_it_pairs_with`'s table, after the row
`    pytest.param(given(layered(), "service", holds={"classes": {"built_by": ["api"]}}), id="a built_by naming it"),`
(Task 2), add:

```python
    pytest.param(given(layered(), "api", holds={"classes": {"names": "*Api", "built_by": ["service"]}}, shared=2),
                 id="the kinds the part holds, their settings and how widely it is shared"),
```

In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, add as the last entry of `pairs`:

```python
        (parsed(layered()), parsed(given(layered(), "service", shared=3))),
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q -k "fewer_users or pairs_with_none or renamed_in_place or every_key"`
Expected: FAIL for rows `dropped` and `lowered` (`assert () == (Loosened('shared', ...`); the other rows, the
pairs-with-none test, the new renamed-in-place row and the every-key test PASS.

- [ ] **Step 3: Write the implementation**

In `LOOSER`, add `"shared"` right after `*HELD`:

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "holds", *HELD, "shared", "imports.types_only", "imports.also", "uses.apply_never", "testing.skips",
          "files.pinned", "reserved", "known", "translated", "review.never", "review.mask", "evals.placement.lines")
```

In `_looser`, right after the settings loop of Task 2:

```python
    for name in shared:
        found += _settings_looser(custom.parts[name], base.parts[pairs[name]], pairs)
```

add

```python
    for name in shared:
        before, now = base.parts[pairs[name]].shared, custom.parts[name].shared
        if before is not None and (now is None or now < before):
            found.append(("shared", name, "" if now is None else str(now)))
```

In `_sentence`, right after

```python
        case _ if key.startswith("holds."):
            return _held_sentence(key, part, what)
```

add

```python
        case "shared" if not what:
            return f"{part} is no longer held to be shared (parts.{part}.shared)"
        case "shared":
            return (f"the public names of {part} need only {what} users, fewer than the profile it is compared with asks "
                    f"(parts.{part}.shared)")
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: all PASS.

- [ ] **Step 5: Lint and self-check**

Run: `uv run ruff check && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "A part's shared dropped, or set to fewer users than the part it is compared with asks, is one looser line under shared; a raised, kept or newly set shared is stricter, and a part that pairs with none is compared on neither its holds nor its shared

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: A tier's `imports.must` dropped or widened, and a tier no longer `plain_tables`, are looser

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (`LOOSER`, `_looser` after the `uses.apply_never`
  comprehension, `_sentence` after the `uses.apply_never` case)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: `_added(key, holder, before, now, pairs) -> list[Looser]` (Task 2); `Tier.imports_must: tuple[str, ...]`
  (part names); `Tier.plain_tables: bool`; in `_looser`, the local `tiers: dict[str, Tier]` (base tier name to the
  paired custom tier) and `pairs` (custom part name to base part name), both already there.
- Produces: keys `"tiers.imports.must"` and `"plain_tables"` in `LOOSER`, right after `"uses.apply_never"`; test
  helpers `reaching(*parts: str) -> dict`, `plain() -> dict`, `tight() -> dict`, `tiered(**imports) -> dict`.

- [ ] **Step 1: Write the failing tests**

Add these helpers right after `holding` (Task 1), before `@pytest.mark.parametrize("profile", [`:

```python
def reaching(*parts: str) -> dict:
    """covered(), each test of its integration tier reaching one of the parts given."""
    document = covered()
    document["tiers"]["integration"]["imports"] = {"must": list(parts)}
    return document


def plain() -> dict:
    """covered(), its unit tier plain_tables."""
    document = covered()
    document["tiers"]["unit"]["plain_tables"] = True
    return document


def tight() -> dict:
    """covered(), its unit tier plain_tables and each of its tests reaching service."""
    document = covered()
    document["tiers"]["unit"] |= {"plain_tables": True, "imports": {"must": ["service"]}}
    return document


```

In `test_each_key_of_a_part_renamed_in_place_is_compared_with_the_part_it_pairs_with`'s table, after the row with
id `the kinds the part holds, their settings and how widely it is shared` (Task 3), add:

```python
    pytest.param(reaching("api"), id="a tier's imports.must naming it"),
```

In `test_a_way_a_copy_renaming_a_part_in_place_is_looser_is_said_under_the_new_name`'s table, after the row with id
`a built_by naming it widened, it read as itself` (Task 2), add:

```python
    pytest.param(reaching("api"), as_routes(reaching("api", "store")), "tiers.imports.must", "integration", "store",
                 id="a tier's imports.must naming it widened, it read as itself"),
```

In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, add as the last entry of `pairs`:

```python
        (parsed(covered()), parsed(tight())),
```

Append at the end of the file:

```python


def tiered(**imports) -> dict:
    """BASE, its tier unit given the imports given besides its types_only."""
    return {**BASE, "tiers": {"unit": {**TIER, "imports": {"types_only": ["store"], **imports}}}}


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(tiered(must=["core"]), tiered(),
                 [("", "the unit tests no longer have to reach any part (tiers.unit.imports.must)")], id="dropped"),
    pytest.param(tiered(must=["core"]), tiered(must=["core", "store"]),
                 [("store", "the unit tests may also meet imports.must by reaching store (tiers.unit.imports.must)")],
                 id="a part added"),
    pytest.param(tiered(must=["core"]), tiered(must=["core"]), [], id="kept"),
    pytest.param(tiered(), tiered(must=["core"]), [], id="newly written"),
])
def test_a_tier_whose_tests_may_reach_more_parts_to_meet_imports_must_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened("tiers.imports.must", "unit", what, sentence) for what, sentence in found)


def test_a_tier_no_longer_plain_tables_is_looser_and_one_newly_plain_tables_is_not():
    assert loosened(parsed(covered()), parsed(plain())) == (
        Loosened("plain_tables", "unit", "", "the table tests of the unit tests may now branch (tiers.unit.plain_tables)"),)
    assert loosened(parsed(plain()), parsed(covered())) == ()


def test_a_tier_renamed_in_place_no_longer_plain_tables_is_said_under_its_new_name():
    base = plain()
    custom = covered()
    custom["tiers"] = {"logic" if name == "unit" else name: tier for name, tier in custom["tiers"].items()}
    custom["parts"]["service"]["tests"] = "logic"
    assert loosened(parsed(custom), parsed(base)) == (
        Loosened("plain_tables", "logic", "", "the table tests of the logic tests may now branch (tiers.logic.plain_tables)"),)


def test_the_ways_a_part_holds_and_a_tier_reaches_are_listed_after_the_other_ways_of_each():
    base = tight()
    base["parts"]["api"]["litmus"] = "Does it answer a request?"
    base["parts"]["service"] |= {"holds": {"classes": {"names": "*Service"}}, "shared": 3}
    base["tiers"]["unit"]["uses"] = {"apply_never": True}
    assert [(item.key, item.part, item.what) for item in loosened(parsed(covered()), parsed(base))] == [
        ("litmus", "api", ""), ("holds", "service", "functions"), ("holds.classes.names", "service", ""),
        ("shared", "service", ""), ("uses.apply_never", "unit", ""), ("tiers.imports.must", "unit", ""),
        ("plain_tables", "unit", "")]


@pytest.mark.parametrize("base, custom, key", [
    pytest.param(holding(classes={}), holding(), "holds", id="holds dropped as a whole"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={}), "holds.classes.names",
                 id="a names setting dropped"),
    pytest.param(given(layered(), "service", shared=3), layered(), "shared", id="shared dropped"),
    pytest.param(reaching("api"), covered(), "tiers.imports.must", id="a tier's imports.must dropped"),
    pytest.param(plain(), covered(), "plain_tables", id="a tier's plain_tables dropped"),
])
def test_a_key_of_holds_shared_or_a_tier_one_side_drops_is_comparable_and_listed_looser(base, custom, key):
    origin = compared(parsed(custom), parsed(base))
    assert origin.match == 1.0
    assert [item.key for item in origin.looser] == [key]
```

The tier tests are tier tests of `BASE`'s `unit` (subject `core`, `store`; `tiered` keeps its `types_only: [store]`
so no `imports.types_only` line appears) and `covered()`'s `unit` (subject `service`, which has a `testing.table`, so
`plain_tables` parses). The last test is the spec's T12 (the dodge): the match still counts each item comparable
(5.1, untouched) and `_looser` now reads it.

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: FAIL for `test_a_tier_whose_tests_may_reach_more_parts_to_meet_imports_must_is_looser[dropped]` and
`[a part added]`, both plain_tables tests, the order test (no tier lines), rows `a tier's imports.must dropped` and
`a tier's plain_tables dropped` of the dodge test, and row `a tier's imports.must naming it widened, it read as
itself`; everything else PASS.

- [ ] **Step 3: Write the implementation**

In `LOOSER`, add `"tiers.imports.must", "plain_tables"` right after `"uses.apply_never"`:

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "holds", *HELD, "shared", "imports.types_only", "imports.also", "uses.apply_never",
          "tiers.imports.must", "plain_tables", "testing.skips", "files.pinned", "reserved", "known", "translated",
          "review.never", "review.mask", "evals.placement.lines")
```

In `_looser`, right after

```python
    found += [("uses.apply_never", tiers[tier.name].name, "") for tier in base.tiers
              if tier.apply_never and tier.name in tiers and not tiers[tier.name].apply_never]
```

add

```python
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None and tier.imports_must:
            found += _added("tiers.imports.must", mine.name, tier.imports_must, mine.imports_must, pairs)
    found += [("plain_tables", tiers[tier.name].name, "") for tier in base.tiers
              if tier.plain_tables and tier.name in tiers and not tiers[tier.name].plain_tables]
```

In `_sentence`, right after

```python
        case "uses.apply_never":
            return f"the {part} tests are no longer held to their part's never list (tiers.{part}.uses.apply_never)"
```

add

```python
        case "tiers.imports.must" if not what:
            return f"the {part} tests no longer have to reach any part (tiers.{part}.imports.must)"
        case "tiers.imports.must":
            return f"the {part} tests may also meet imports.must by reaching {what} (tiers.{part}.imports.must)"
        case "plain_tables":
            return f"the table tests of the {part} tests may now branch (tiers.{part}.plain_tables)"
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: all PASS.

- [ ] **Step 5: Lint and self-check**

Run: `uv run ruff check && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`. (If `--strict` names a test of this file with "has an `if` expression in
its body ... (tiers.unit.plain_tables; scenario-coverage)", a table test grew a branch: move the case's documents
into its table.)

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "A tier's imports.must dropped or given a part more, read through the pairing, is one looser line under tiers.imports.must, and a tier no longer plain_tables one under plain_tables, each said under the custom tier's name after uses.apply_never; every key the match counts comparable when one side drops it is now read by the looser list

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: `testing.beside` has its key and its sentence, for 6.10 to reach

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (`LOOSER`, `_sentence` after the `testing.skips` case)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: key `"testing.beside"` in `LOOSER`, right after `"testing.skips"`; its sentence
  `tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)`; test constant
  `LATER = {"testing.beside"}`, which card 6.10 empties when it adds the field, the `_looser` branch and the test.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/application/logic/test_looseness.py`, add right before the line `MARK = "imports.may.types_only"`:

```python
LATER = {"testing.beside"}
"""The keys of LOOSER no pair reaches yet: testing.beside is said here, and its line is found and tested with the key
itself (card 6.10), which empties this set."""
```

In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, replace

```python
    found = [item for custom, base in pairs for item in loosened(custom, base)]
    assert sorted({item.key for item in found}) == sorted(LOOSER)
```

with

```python
    found = [item for custom, base in pairs for item in loosened(custom, base)]
    assert LATER <= set(LOOSER)
    assert sorted({item.key for item in found}) == sorted(key for key in LOOSER if key not in LATER)
```

(The line `assert [item.key for item in found if "is no longer reserved" in item.sentence] == ["reserved"]` stays.)

- [ ] **Step 2: Run the test to see it fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q -k every_key`
Expected: FAIL on `assert LATER <= set(LOOSER)` (`testing.beside` is not a key yet).

- [ ] **Step 3: Write the implementation**

In `LOOSER`, add `"testing.beside"` right after `"testing.skips"` (this is the final `LOOSER`):

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "holds", *HELD, "shared", "imports.types_only", "imports.also", "uses.apply_never",
          "tiers.imports.must", "plain_tables", "testing.skips", "testing.beside", "files.pinned", "reserved", "known",
          "translated", "review.never", "review.mask", "evals.placement.lines")
```

In `_sentence`, right after

```python
        case "testing.skips":
            return f"{what} is no longer counted as a skip (testing.skips)"
```

add

```python
        case "testing.beside":
            return "tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)"
```

Do **not** add a `_looser` branch: there is no `testing.beside` field on `Framework` yet (spec §2.6).

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: all PASS (98 tests).

- [ ] **Step 5: Lint and self-check**

Run: `uv run ruff check && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "testing.beside is a key of the looser list with its sentence, that tests may sit beside the code and the mirrored tests tree is no longer checked, written against the key's address for card 6.10 to reach; the every-key test names it as the one key no pair reaches yet

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: The docstring, README and CHANGELOG say the new ways; golden docs and every gate

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py:30-35` (module docstring)
- Modify: `README.md:458` (the `profile check` enforcement paragraph)
- Modify: `CHANGELOG.md:77` (`[Unreleased]`, `### Changed`)
- Regenerated, expected unchanged: `docs/cli/**`, `docs/web/**`, `docs/xarch/**`

**Interfaces:**
- Consumes: the keys and sentences of Tasks 1-5.
- Produces: nothing code uses.

- [ ] **Step 1: The module docstring**

In `xarch/modules/spec/application/logic/looseness.py`, replace

```
is below the one the bundled profile gives it (written, else LINE: it flags less). Anything stricter, and what is
compared in no way above (the layout, new parts, the guards' other parameters, `fakes`), is not listed.
"""
```

with

```
is below the one the bundled profile gives it (written, else LINE: it flags less); a kind a part's `holds` allows that
the bundled part's does not (no `holds` allows every kind, and `classes` allows `records` and `exceptions` too); a
setting of a kind dropped or widened, compared for each kind either part lists and both allow, on the settings each
holds the kind to (those written under it, else for `records` and `exceptions` those under `classes`, `immutable`
never for an exception): `names` dropped, or a pattern added that no bundled pattern matches read as a name,
`immutable` dropped, `built_by` dropped or a part added to it; a part's `shared` dropped or lowered; a tier's
`imports.must` dropped, or a part added to it; a tier no longer `plain_tables`; `testing.beside` set where the bundled
profile leaves it out. Anything stricter, and what is compared in no way above (the layout, new parts, the guards'
other parameters, `fakes`), is not listed.
"""
```

- [ ] **Step 2: README**

In `README.md`, replace the line (it occurs once)

```
  other's, an entry of `review.never` or `review.mask` the other holds and this one drops.
```

with

```
  other's, an entry of `review.never` or `review.mask` the other holds and this one drops, a kind a part's `holds`
  allows that the other's does not (`classes` allowing `records` and `exceptions` too), a setting of a kind it holds
  dropped or widened (`names`, `immutable`, `built_by`, compared kind by kind on the settings the part holds each kind
  to, for a kind either lists), a part's `shared` dropped or lowered, a tier's `imports.must` dropped or a part added
  to it, a tier no longer `plain_tables`, and `testing.beside` set where the other leaves it out.
```

- [ ] **Step 3: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, `### Changed`, right after the entry that ends

```
  `profile check`'s `compared_with` (`null` when nothing is compared).
```

add (no blank line between entries, as the section writes them):

```
- The looser lines cover every loosening of 0.3.0: `profile check` and `check`'s enforcement section now also list a
  kind a part's `holds` allows that the other's does not (`holds`), a setting of a kind dropped or widened
  (`holds.classes.names`, `holds.classes.immutable`, `holds.classes.built_by`, `holds.functions.names`,
  `holds.records.names`, `holds.records.immutable`, `holds.exceptions.names`), a part's `shared` dropped or lowered
  (`shared`), a tier's `imports.must` dropped or a part added to it (`tiers.imports.must`), a tier no longer
  `plain_tables` (`plain_tables`), and `testing.beside` set where the other leaves it out (`testing.beside`), each by
  a sentence ending in its address, such as
  `the classes of service may also be named * (parts.service.holds.classes.names)`. Each is information, like the
  others: `--strict` still fails only on a missing `litmus`.
```

- [ ] **Step 4: Regenerate the golden docs and see an empty diff**

```bash
uv run python - <<'EOF'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for profile, out in (("cli", "docs/cli"), ("web", "docs/web"), ("architecture.yaml", "docs/xarch")):
    for found in spec.docs(profile).files:
        Path(out, *found.path).write_text(found.template, encoding="utf-8")
EOF
git status --short docs/ && git diff --stat docs/
```

Expected: nothing under `docs/cli`, `docs/web` or `docs/xarch` (this step edits no template and no profile; the
golden testing docs take their list of looser ways from `xarch/architectures/testing.md`, which the spec leaves to
step 25). A changed file there is a behaviour change: restore it with `git checkout -- <file>` and find its cause.

- [ ] **Step 5: The corpora are untouched**

Run: `git diff --stat 3e3d4dc -- tests/bootstrap/corpora tests/bootstrap/test_recorded_corpora.py docs/examples`
Expected: no output.

- [ ] **Step 6: Run every gate**

```bash
uv run ruff check
uv run xarch check >/dev/null; echo "exit $?"
uv run xarch check --strict >/dev/null; echo "exit $?"
uv run xarch profile check architecture.yaml > /tmp/5-2-profile-check-after.txt; echo "exit $?"
diff /tmp/5-2-profile-check-before.txt /tmp/5-2-profile-check-after.txt && echo SAME
```

Expected: `All checks passed!`, `exit 0`, `exit 0`, `exit 0`, `SAME`. The `compared:` list is the same 18 lines as
before this step (xarch's profile writes the same `holds` as `cli`, adds `plain_tables` and tier `imports.must`, which
are stricter, and no lower `shared`). If `diff` prints a line, read it: it must be a true loosening of
`architecture.yaml` against `cli`; name it in the report rather than change a rule.

Then the suite, in the background (about three and a half minutes), and read its tail at the end:

```bash
timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3
```

Expected: `... passed`, no failures.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py README.md CHANGELOG.md
git commit -m "The looseness docstring, the README's enforcement paragraph and the CHANGELOG say the looser lines cover every loosening of 0.3.0: a kind holds newly allows, a setting of a held kind dropped or widened, shared dropped or lowered, a tier's imports.must dropped or widened, a tier no longer plain_tables and testing.beside; the golden docs regenerate unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.**
- §1 table: `holds` (Task 1); the seven `holds.<kind>.<setting>` keys (Task 2); `shared` (Task 3);
  `tiers.imports.must`, `plain_tables` (Task 4); `testing.beside` key and sentence (Task 5).
  `imports.may.types_only` unchanged: its existing tests at `test_looseness.py:196-212` and `:421-422` keep passing
  (every task's Step 4 runs the whole file). `--strict` untouched (Global Constraints).
- §2 order: `LOOSER` and `_looser` append in the table's order: part ways after `LITMUS`, tier ways after
  `uses.apply_never`, `testing.beside` after `testing.skips` (Tasks 1-5); pinned by the order test (Task 4, T11).
- §2.1 allowed kinds, `classes` allowing `records`/`exceptions`, one line per kind in `KINDS` order: `_allowed`,
  T1's five rows (Task 1).
- §2.2 effective settings, compared kinds (either lists, both allow), coverage by `name_matches(q, p)`, `immutable`
  never for exceptions, `built_by` through the pairing, the five sentences, address naming the kind compared:
  `_held_to`, `_settings_looser`, `_added`, `_held_sentence`; T2/T3/T4 rows (Task 2).
- §2.3 dropped/lowered and their sentences; raised/unset: T5 (Task 3).
- §2.4 tier `imports.must` dropped/widened through the pairing, key `tiers.imports.must`: T6 (Task 4), renamed row
  (Task 4).
- §2.5 `plain_tables`: T7, T9 (Task 4).
- §2.6 `testing.beside`: key and sentence only, `LATER` in T10 (Task 5); no `_looser` branch.
- §2.7 stricter cases: rows `a kind dropped is stricter`, `a pattern dropped from a list ...`, `built_by newly
  written`, `raised`, `newly set`, `kept`, plain_tables newly set; unpaired part (Task 3); records/exceptions freed
  from `classes.built_by`: `_held_to` gives a narrower kind `built_by=()` and no key exists for it.
- §2.8 the dodge: T12 (Task 4); the match's counting not touched.
- §3 docs: docstring, README, CHANGELOG, golden docs regenerated unchanged (Task 6); `keys.yaml`, `profile explain`
  and `xarch/architectures/testing.md` unchanged (its stale list is for step 25).
- §4 T1-T12: Tasks 1 (T1, T10 pair), 2 (T2-T4, T8 `built_by` rows, T10 pair), 3 (T5, T8 holds/shared row, T10 pair),
  4 (T6, T7, T8 tier rows, T9, T10 pair, T11, T12), 5 (T10's `LATER`).
- §5 gates: Task 6 Step 6, and each task's Steps 5-6.

**Placeholder scan.** No TBD/TODO; every code step shows its code; no "similar to".

**Type consistency.** `_allowed(part: Part) -> tuple[str, ...]` (Task 1) used by `_settings_looser` (Task 2);
`_added(key, holder, before, now, pairs) -> list[Looser]` (Task 2) used for `tiers.imports.must` (Task 4); test
helpers `holding` (Task 1), `reaching`, `plain`, `tight`, `tiered` (Task 4) are defined before each table that calls
them.

**Review Focus.** Five lines, each with its test in the owning task (Tasks 2 and 3).

**Deviation from the spec, stated.** T4's `bootstrap` part is `api`/`store` here (`layered()` has no `bootstrap`).
README and CHANGELOG name `testing.beside` as the spec's §3 asks, though no profile can write it until 6.10.
<!-- task-pipeline: validated -->
