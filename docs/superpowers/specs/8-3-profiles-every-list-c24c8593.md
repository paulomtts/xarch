# 8.3 profiles: every list under `imports` written in the new references

Card: c24c8593-14eb-4870-b1c2-a83cc7208cbb (subtask of f1c96689), blocked by 8.2 (e7336bbc, done: branch tip
a4521b7). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3, row 24 at line 287), sub-step
3 of its owning note.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements section 5 (5.1 lines 329-355, 5.2 lines 357-386, both rewritten against today's tree; 5.3 lines
388-433) and section 6 sub-step 3 (lines 450-452). From review 3: O4, O5, O8 (lines 228, 229, 232).

## Goal

After this card, every list of parts under `imports`, in every profile xarch ships, documents, or keeps as a test
fixture, is written in the reference form of the note's section 1 (lines 91-122): `parts.<part>` or `<word>.<part>`,
optionally followed by `/<path>` and `:<pattern>`, or `everything`. The format text (`keys.yaml`, read by
`profile explain`), the README, the CHANGELOG, the docstrings and the "such as" examples of messages describe that
form. Nothing a profile allows changes: `profile check` still says OK, the looser lines hold the same targets, the
rules every bundled profile expands to are the same text. The old forms (bare name, `@any`) still parse: refusing
them is 8.4.

## What is already there (not to be redone)

- `target()` (`xarch/kernel/logic/targets.py`) reads `parts.<part>` and `<word>.<part>` beside the old forms, given
  `repeats=` (8.1). `allowed_targets` and `imports_written` read a part's `imports.may`/`imports.must` and a tier's
  `imports.may`/`imports.also` through it, with the repeats.
- The writers (`_place` in `xarch/modules/rules/application/logic/written.py`, `_shown` in
  `xarch/modules/spec/application/logic/looseness.py`) already write the new form (8.2). The looser lines of
  `uv run xarch profile check architecture.yaml` already print `parts.profile-values`, `parts.reports`,
  `module.domain/values`, and so on.
- `Target` does not change (note section 7, line 472).

## The hidden prerequisite: a tier's `imports.must` and `imports.types_only`

A tier's `imports.must` and `imports.types_only` are read today by `ck.part_names`
(`xarch/modules/spec/application/logic/profile_checks.py:392-404`), called at
`xarch/modules/spec/application/logic/profile_parsing.py:665-666` (types_only) and `:676-677` (must). It accepts only
a declared plain name, so `must: [parts.controller]` is refused today with `no part named 'parts.controller'`. 8.1 and
8.2 did not touch it. The profiles cannot be rewritten until these two keys read `parts.<part>` (note section 2 table,
lines 166-167: "`parts.<part>` only ... a tier's tests lie in no instance"; rulings, lines 20-26; note 5.3, lines
395-396).

`ck.part_names` is also the reader of keys outside `imports` (`holds.classes.built_by`, guards' `parts`, `fakes.for`,
`guards.no-twins.translated`, `profile_parsing.py:734, 920, 948` and others). Those keep plain names (rulings, lines
22-24). So `part_names` itself does not change; the two tier keys get their own reader.

## Inherited constraints

- The grammar and its resolution: note section 1 (lines 91-122) and 1.1 (lines 124-132). `parts.<part>` is the part
  in every instance, or the part itself when it lies in no repeating folder; `<word>.<part>` the part in the
  importer's own instance of the `<word>` folder.
- Which keys take references (rulings, lines 20-26; section 2.1, lines 195-215): every list of parts under `imports`,
  on a part (`imports.may`, with or without the mode `{<reference>: types_only}`, `imports.must`) and on a tier
  (`imports.may`, `imports.also`, `imports.must`, `imports.types_only`). A tier's `must` and `types_only` take
  `parts.<part>` only.
- Every key outside `imports` that names a part keeps a plain name: `holds.classes.built_by`, guards' `parts`,
  `fakes.for`, `docs.entry`, `guards.scenario-coverage.results`, `layers`, `evals.placement.alike` and `.lines`,
  checks' `in.part`, and the rest of note section 2 (lines 154-193). `imports.libraries` is a list of packages, not of
  parts: it stays as written.
- The check target `place` (`may_not`, `may_only`, `must_reach.targets`) keeps references (rulings, lines 39-40); a
  profile that writes one in an old form is respelled with the rest.
- Rewrite rule, per entry (note 5.1/5.2): a part inside a repeating folder, written bare (own instance) becomes
  `<word>.<part>`, the word that of its repeating folder in that profile; `<part>@any` becomes `parts.<part>`; a part
  outside any repeating folder, written bare, becomes `parts.<part>`; `/<path>` and `:<pattern>` follow unchanged
  (`"domain/values:*Id"` becomes `"module.domain/values:*Id"`, still quoted); the mode map keeps its shape
  (`{core: types_only}` becomes `{parts.core: types_only}`); `everything` and `[]` stay.
- The word comes from the profile's own repeating folders. In the bundled profiles it is `module` (`modules/<module>/`
  at `architecture.yaml:8`, `cli.yaml:7`, `web.yaml:7`). In a test's inline profile or a corpus, read the word from
  that profile's own folder keys; never assume `module` (note section 7, lines 468-469).
- `cli.yaml`, `web.yaml` and `architecture.yaml` change in one commit (note section 6, line 450): `architecture.yaml`
  says `based_on: cli`, and `profile check` compares the two (note 5.2, lines 384-386).
- Generated docs `docs/{cli,web,xarch}/*.md` are regenerated, never edited by hand, and their diff read (note section
  7, line 478; review 3 O8, line 232). The note expects no change (5.3, lines 411-412).
- README and CHANGELOG lines go under `[Unreleased]` (review 3 O4, O5, lines 228-229).
- Project rules (card): no comments in xarch's code (docstrings only); never `ruff --fix`; tests written first and
  seen failing; examples simple, with absolute `app.` imports; Python only in the reader adapter and
  `xarch/architectures/presets/` data; recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as
  the note says (5.3, lines 416-419); `.claude/` out of commits; nothing pushed.

## Behavior

### B1. A tier's `imports.must` and `imports.types_only` read `parts.<part>`

Given a profile with a tier (with or without a repeating folder holding the named part):

| Written under `tiers.<t>.imports.must` or `.types_only` | Result |
|---|---|
| `[parts.controller]`, `controller` declared | accepted; the tier's `reach` / `imports_types_only` holds `"controller"` |
| `[parts.domain, parts.platform]`, both declared | accepted, `("domain", "platform")` in written order |
| `[controller]` (plain, declared) | still accepted, same result (old form; refused in 8.4) |
| `[parts.controller, controller]` | refused: `'controller' is listed twice` (same part, either spelling) |
| `[parts.nope]` | refused: `no part named 'nope'` (the part, not the reference, in the message) |
| `[module.controller]`, `controller` in `modules/<module>/` | refused: `'module.controller': a tier's tests lie in no instance: write parts.controller` (note section 4, line 311) |
| `[module.kernel]`, `kernel` in no repeating folder | refused with the same message, `write parts.kernel` |
| `[parts.controller/x]`, `[parts.controller:*Id]` | refused: `'parts.controller/x': names a part only: write parts.controller` |
| `[]`, not a list, or `everything` | as today: `must be a list of part names` / `no part named 'everything'` |

- Every refused entry is one problem, under the address `tiers.<t>.imports.must` or `tiers.<t>.imports.types_only`.
- The parsed values stay plain part names (`Tier.imports_types_only`, the tier's reach), so the rules
  (`expansion.py`), `where`, `locate`, the sentences and the docs read them unchanged.
- The `{must: [<part>]}` hint the tier's `imports` group gives (`profile_parsing.py:664`) becomes
  `{must: [parts.<part>]}`.
- `ck.part_names` and every other key it reads are unchanged: `fakes.for: [parts.core]` is still refused as today
  (`no part named 'parts.core'`).

### B2. The three bundled profiles are written in references

`xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml` and `architecture.yaml` (at the repository root, xarch's own profile) are rewritten by the rule above,
line for line as the note's tables 5.1 and 5.2 say, at today's lines (from the tree, branch tip a4521b7):

- `architecture.yaml`: parts' `may`/`must` at 22, 37, 55, 70, 88, 106-107, 124, 138, 152, 164, 178, 211, 250; tier
  `integration` `also`/`must` at 299-300; tier `wired` `must`/`types_only` at 311-312; tier `guard` `types_only` at
  324. `may: everything` (bootstrap, guard tier at 323) stays.
- `cli.yaml`: 20, 36, 54, 71, 89, 107-108, 126, 141, 154, 196, and `imports: {types_only: [controller]}` at 264
  becomes `[parts.controller]`. 169 `may: everything` and 279 `{may: []}` stay.
- `web.yaml`: 20, 36, 54, 71, 89, 107-108, 126, 141, 154, 198, and 266 as cli's 264; 171 and 281 stay.
- No key outside `imports`, and no `imports.libraries`, changes.

Observable, after the commit:

- `uv run xarch profile check architecture.yaml` prints exactly what it printed before (captured before the edit),
  including `OK: the profile is valid`, the match line `80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21
  of 31 tier entries, ...` and the same looser lines.
- `uv run xarch check` and `uv run xarch check --strict` give the same findings as before.
- `profile check` of `cli.yaml` and `web.yaml` (as custom files) says OK.
- `tests/bootstrap/test_bundled_imports.py` passes unchanged: the `WHERE` text and the digests of the rules each
  profile expands to do not move. A moved digest means the migration changed what a profile allows: stop and
  investigate, do not update the digest.
- The golden docs stay byte for byte (`tests/bootstrap/test_docs_templates.py`).

### B3. The format text, README, CHANGELOG, docstrings and messages say references

- `xarch/architectures/presets/format/keys.yaml`:
  - `symbols` (lines 115-118): `store`, `store@any`, `store/schema`, `store:*Id` become `parts.store` (the part in
    every instance, or the part itself outside a repeating folder), `unit.store` (the part in the importer's own
    instance of its `<unit>` folder), `parts.store/schema`, `parts.store:*Id`. No text says the old forms are refused.
  - `accepts` of `parts.<part>.imports.may` (lines 346-351), `.imports.may.types_only` (358, `[{parts.core:
    types_only}]`), `.imports.must`, `tiers.<tier>.imports.*` (614-617), `tiers.<tier>.imports.types_only` (766-767,
    `[parts.<part>, ...]`) and `.must`, `.also`: written with references, `<part>` replaced by `parts.<part>` /
    `<word>.<part>` where a reference is meant.
  - Examples: fragment `two` (line 22, `may: [parts.core]`), lines 370 (`{parts.core: types_only}`), 381
    (`must: [parts.core]`), 620 and 761 (`must: [parts.documents]`), 741 (`also: [parts.core]`), 774
    (`types_only: [parts.documents]`), 1246 (`imports: {may: [parts.documents]}`), and any other list under
    `imports` in the file. `fakes.for: [core]` (44), `built_by: [core]` (443), guards' `parts: [documents]` and
    every other key outside `imports` stay plain. Every example still loads, as the existing tests require.
  - `profile explain` prints the new text; its tests are updated first.
- `README.md`: the `imports.may` bullet (lines 227-232) describes the references as the way to write a target
  (`parts.store`, `unit.store`, `/<path>`, `:<pattern>`, `{parts.store: types_only}`, `everything`), drops the
  bare-name and `@any` description, and every profile snippet in the README writes its `imports` lists in references.
  It does not say the old forms are refused.
- `CHANGELOG.md`, under `[Unreleased]`, a `Changed` entry: the bundled profiles (`cli`, `web`) and xarch's own write
  every list under `imports` in references; a tier's `imports.must` and `imports.types_only` read `parts.<part>`
  (and refuse `<word>.<part>`, a path or a pattern there); `profile explain`, the README and the messages describe
  references. It does not say the old forms are refused (8.4).
- Docstrings and messages describing the bare name or `@any`:
  - `xarch/modules/spec/application/logic/example_imports.py:7`;
  - `xarch/modules/spec/domain/values.py` (around 214);
  - `xarch/modules/spec/application/logic/targets_written.py:1-5`, and its message at :31 becomes
    `must be a list of targets such as [parts.core, module.store/schema]` (note section 4, lines 324-325), the word
    `module` here being only a written example in text;
  - `xarch/modules/spec/application/logic/imports_written.py:84` becomes
    `must be a list of targets such as [parts.<part>, <word>.<part>]`;
  - `profile_parsing.py:28-29` (the format summary) and the tier imports summary (44-49), `checked_tier.py:1`,
    `kernel/logic/placement.py:8-14` (re-check; it may already be clean).
  - `xarch/kernel/logic/targets.py` messages and docstring that name or suggest the old forms belong to the refusal
    and stay for 8.4, unless a test this card touches pins them.

### B4. Every test and corpus profile writes references

- Every inline profile in `tests/` (28 files hold lists under `imports`; 20 mention `@any`, per the explore grep) has
  each list under `imports` respelled by the rule, with the word of that profile's own repeating folder. Lists
  outside `imports` stay plain.
- Not respelled: a test whose subject is that an old form still parses (the 8.1 rows of
  `tests/kernel/logic/test_targets.py`, and any test asserting the bare name or `@any` reads to a given `Target`);
  a test that asserts a refusal message for a value that is itself an old form. Those keep proving what they prove,
  until 8.4.
- A respelled test proves the same thing: same assertion, same expected findings and messages, but where the
  message prints the spelling of a target the profile now writes.
- Corpora, by hand: `tests/bootstrap/corpora/7cc6111.yaml` (65, 66, 88), `df537ca.yaml` (69, 70, 93, 100),
  `stress.yaml` (77, 78, 110, 119 and every other list under `imports`). Their word is `module` (`modules/<module>/`
  at line 8, 8 and 6), checked, not assumed. The recorded `.json` findings do not change
  (`tests/bootstrap/test_recorded_corpora.py`, `test_written_rules.py`). The `.tar.xz` archives are not touched.

### B5. The golden docs are regenerated and read

`docs/{cli,web,xarch}/*.md` are regenerated through the docs path `tests/bootstrap/test_docs_templates.py` uses (as
commit ddea9db did) and the diff read. Expected: no diff (note 5.3, lines 411-412). If a doc moves, the plan stops and
the diff is reported with the commit, not hand-fixed; a move is accepted only where it prints a respelled target and
nothing else.

## Error paths

- A bundled profile that no longer loads, a looser line that changes target, a moved rule digest, or a changed
  `check` finding: the commit is wrong; fix the yaml, never the test.
- An inline test profile whose respelling makes a test fail for a reason other than a printed spelling: the respelling
  is wrong (wrong word, or a part outside the folder written `<word>.`); fix the profile.
- A refusal under B1 never stops the other entries of the list being read: one problem per bad entry.

## Out of scope

- Refusing the bare name, `@any`, `@own`, or a prefixed name outside `imports`, and the CHANGELOG's refusal entry, the
  messages of note section 4 for old forms, and the tree's refusal of the word `parts` (8.4, note section 6 sub-step
  4, lines 453-456).
- The `imports.also` test of note 3.8 (sub-step 5, line 457).
- Turning any key outside `imports` into references, or `imports.libraries` (card dodge; note section 7, line 476).
- Any change of what a profile allows (card dodge; note section 7, lines 479-480).
- Editing the generated docs by hand (card dodge).
- Step 25's whole-README read, CHANGELOG lead and version bump.

## Tests

| # | Test | Tier | Why this tier |
|---|---|---|---|
| T1 | Each row of the B1 table, as a table test of the tier reader: `parts.<part>` accepted for `must` and `types_only`, plain still accepted, the duplicate across spellings, `parts.nope`, `module.X` with a repeating and a non-repeating part, `/path` and `:pattern`, empty and non-list | unit (`tests/modules/spec/application/logic/test_profile_parsing_tests.py` or `test_tiers.py`, wherever tier imports are tested now) | pure parsing in the spec module's `logic` part |
| T2 | The `{must: [parts.<part>]}` hint of a tier's bad `imports` group | unit (same file) | message of the same parser |
| T3 | `fakes.for: [parts.core]` still refused with today's text (keys outside `imports` untouched by the new reader) | unit (`test_profile_parsing.py`) | guards against widening `part_names` |
| T4 | The bundled profiles: every string entry of every list under a part's `imports.may`/`imports.must` (and the key of each mode map) and a tier's `imports.may`/`also`/`must`/`types_only` in `cli.yaml`, `web.yaml`, `architecture.yaml` is `everything` or holds a `.` before its first `/` or `:`; no entry of `fakes.for`, `built_by`, guards' `parts`, `layers`, `docs.entry`, `alike`, `results`, `imports.libraries` starts with `parts.` | wired (`tests/bootstrap/test_bundled_imports.py`) | reads the profiles the app ships, as the existing bundled-imports test does |
| T5 | Existing `tests/bootstrap/test_bundled_imports.py` (WHERE and digests) passes unchanged across B2 | wired | the proof the migration kept every rule |
| T6 | Existing golden-docs tests (`tests/bootstrap/test_docs_templates.py`) pass, docs regenerated | wired | byte-for-byte docs of the bundled profiles |
| T7 | `profile explain` text tests (`tests/bootstrap/test_profile_explain*.py`, `tests/modules/spec/application/test_explain.py`, `test_select.py`, `tests/modules/spec/adapters/test_yaml_profile_format.py`) updated first to the new `symbols` and `accepts` text, then seen passing | wired / application / adapters, where they are | they pin the text of `keys.yaml` |
| T8 | Message tests of `targets_written.py:31` and `imports_written.py:84` (`test_targets_written.py`, `test_imports_written.py`) updated first to the new "such as" text | unit | pin the messages |
| T9 | Every respelled inline-profile test keeps passing with its assertions unchanged but for printed spellings | its own tier | proves B4 changed no meaning |
| T10 | `test_recorded_corpora.py` and `test_written_rules.py` pass with the respelled corpora, recorded findings unchanged | wired | the corpora's findings are the proof |
| T11 | Manual gate: `uv run xarch profile check architecture.yaml` output captured before B2 and diffed after: identical | gate, not a test file | the looser lines already print the new form, so equality is the check |

Gates on every commit, each passing alone with the full suite green: `uv run ruff check` (never `--fix`),
`uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, then
`uv run pytest -q` (over two minutes: run it in the background with `timeout`, read it at the end).

## Order of commits (for the planner)

1. B1 with T1-T3, test first.
2. B2: the three profiles in one commit, with T4 (test first: it fails on today's profiles), and any test that pins
   the bundled profiles' text. T5, T6, T11 pass unchanged.
3. B3: `keys.yaml`, README, CHANGELOG, docstrings and messages, with T7 and T8 updated first.
4. B4: tests and corpora (one or several commits, grouped by folder), T9, T10.
5. B5: regenerate the golden docs and read the diff; commit only if they move, with the diff described in the message.

## Review focus (for the planner)

- `imports.libraries` and every key outside `imports` left plain, in the profiles, `keys.yaml`, README and tests.
- The flow forms `imports: {types_only: [controller]}` (cli 264, web 266) and the mode maps `{x: types_only}`: the
  reference goes inside, the shape stays.
- A test profile whose repeating word is not `module` (`<unit>`, `<feature>`, ...), or whose importer lies outside the
  folder: `parts.` there, never `<word>.`.
- Quoted patterns keep their quotes; `everything` and `[]` stay.
- A test that proves an old form still parses is left in the old form.
