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
