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

---

# 8.3 profiles: every list under `imports` written in the new references, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every list of parts under `imports`, in the bundled profiles (`cli`, `web`), xarch's own `architecture.yaml`, the format text (`keys.yaml`), the README and every test profile and corpus, is written `parts.<part>` or `<word>.<part>` (then `/<path>`, `:<pattern>`), or `everything`, with nothing a profile allows changing.

**Architecture:** One new reader, `tier_parts` in `xarch/modules/spec/application/logic/imports_written.py`, reads a tier's `imports.must` and `imports.types_only` (`parts.<part>` or a plain name, to plain part names), replacing the two calls of `ck.part_names` in `_tier`; `ck.part_names` itself and its other callers do not change. Then the profiles, the format text and the messages are respelled, the tests and corpora after them, each commit proved by the digests of `tests/bootstrap/test_bundled_imports.py`, the recorded corpora and the golden docs, which must not move.

**Tech Stack:** Python 3.13, pytest, typer's `CliRunner`, PyYAML, `uv`, `ruff`, xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/8-3-profiles-every-list-c24c8593.md` (copied in full above this plan).

## Global Constraints

- Rewrite rule, per entry: a part inside a repeating folder, written bare (own instance), becomes `<word>.<part>`, the word that of its repeating folder in that profile; `<part>@any` becomes `parts.<part>`; a part outside any repeating folder, written bare, becomes `parts.<part>`; `/<path>` and `:<pattern>` follow unchanged (`"domain/values:*Id"` becomes `"module.domain/values:*Id"`, still quoted); the mode map keeps its shape (`{core: types_only}` becomes `{parts.core: types_only}`); `everything` and `[]` stay.
- A tier's `imports.must` and `imports.types_only` take `parts.<part>` only (never `<word>.<part>`).
- The word comes from the profile's own repeating folders; never assume `module`.
- Every key outside `imports` that names a part keeps a plain name (`holds.classes.built_by`, guards' `parts`, `fakes.for`, `docs.entry`, `guards.scenario-coverage.results`, `guards.no-twins.translated`, `layers`, `evals.placement.alike` and `.lines`, checks' `in.part`); `imports.libraries` stays as written.
- The old forms (bare name, `@any`) still parse; nothing says they are refused (that is 8.4). A test whose subject is that an old form parses, or that asserts the refusal of a value that is itself an old form, keeps the old form.
- `cli.yaml`, `web.yaml` and `architecture.yaml` change in one commit.
- A moved digest in `tests/bootstrap/test_bundled_imports.py`, a moved golden doc, a changed `check` finding or a changed recorded corpus finding means the migration changed what a profile allows: fix the yaml, never the test or the digest.
- Golden docs `docs/{cli,web,xarch}/*.md` are regenerated, never edited by hand.
- README and CHANGELOG lines go under `[Unreleased]`.
- No comments in xarch's code (docstrings only). Never `ruff --fix`. Tests written first and seen failing. Recorded corpora edited by hand only. `.claude/` out of commits. Nothing pushed.
- Deviation from the spec, B3: the message of `targets_written.py:31` becomes `must be a list of targets such as [parts.core, unit.store/schema]`, not `[parts.core, module.store/schema]`: `tests/architecture/test_agnostic.py` refuses the literal word `module` (a repeating word of the bundled profiles) in any string of xarch's code, and `ALLOWED` stays empty. `unit` is the word `keys.yaml`'s examples already use (`units/<unit>/`).
- Gates on every commit: `uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, then `timeout 900 uv run pytest -q` (over two minutes: run it in the background and read it at the end). Never `pkill`/`killall`; stop a run by `timeout` or by the PID you started.

## Review Focus

1. A tier's `must`/`types_only` written `<word>.<part>` for a part in a repeating folder and for one in none: refused with `a tier's tests lie in no instance: write parts.<part>`, never read as own (Task 1, Step 1, rows `module.store` and `module.shared`).
2. A non-text entry in a tier's `must` (a number, a map such as `{parts.store: types_only}`): refused `no part named ...`, as today, never a crash on an unhashable value (Task 1, Step 1, rows `3` and the map).
3. The flow forms `imports: {types_only: [controller]}` (cli 264, web 266) and the mode map `{contract: types_only}` spliced into web by `tests/bootstrap/test_rule_ids.py`: the reference goes inside the braces, the shape stays (Task 2, Steps 4 and 5).
4. A text outside `imports` that would start with `parts.` in a bundled profile (a guard's `parts`, `fakes.for`): the T4 test counts every text starting `parts.` against the entries under `imports` (Task 2, Step 2).
5. A test profile whose repeating word is not `module` (`<plugin>` in `tests/bootstrap/test_repeating_folders.py`): `plugin.manifest`, and `parts.hooks` for the other folder's part (Task 4, Step 1).

---

### Task 1: A tier's `imports.must` and `imports.types_only` read `parts.<part>`

**Files:**
- Modify: `xarch/modules/spec/application/logic/imports_written.py` (module docstring, imports, new `tier_parts` and `_tier_part` after `_joined`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:664-666` and `:676-677`
- Test: `tests/modules/spec/application/logic/test_tiers.py` (new tests after `test_a_tier_with_no_types_only_has_none`, `NO_MAP` at line 66)
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py` (one new test at the end)

**Interfaces:**
- Consumes: `ck.part_names(value, declared, where, problems) -> list[str]` (unchanged, still used by `fakes.for`, `built_by`, guards).
- Produces: `tier_parts(value: Any, declared: set[str], where: str, problems: list[str]) -> list[str]` in `xarch/modules/spec/application/logic/imports_written.py`: plain part names in written order; each bad entry adds one problem at `where`.

The fixture `covered()` (`tests/modules/spec/profiles.py`) has the repeating folder `src/<module>/` holding `api`, `service`, `store`, and `shared/` outside it; tier `integration` tests `api` and `store` (`with_imports` writes its `imports`).

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_tiers.py`, change line 66:

```python
NO_MAP = "must be a map of may, also, must and types_only, such as {must: [parts.<part>]}"
```

Then add, right after `test_a_tier_with_no_types_only_has_none` (line 98-99):

```python
@pytest.mark.parametrize("key, field", [
    pytest.param("must", "imports_must", id="must"),
    pytest.param("types_only", "imports_types_only", id="types_only"),
])
@pytest.mark.parametrize("written, read", [
    pytest.param(["parts.store"], ("store",), id="a reference to a part of the repeating folder"),
    pytest.param(["parts.shared"], ("shared",), id="a reference to a part in no repeating folder"),
    pytest.param(["parts.store", "parts.api"], ("store", "api"), id="references in the order written"),
    pytest.param(["store"], ("store",), id="a plain name still reads"),
    pytest.param(["parts.store", "api"], ("store", "api"), id="a reference beside a plain name"),
])
def test_a_tier_s_must_and_types_only_read_parts_references_as_the_part_names(key, field, written, read):
    assert getattr(parsed(with_imports({key: written})).tiers[1], field) == read


@pytest.mark.parametrize("key", ["must", "types_only"])
@pytest.mark.parametrize("written, problem", [
    pytest.param(["parts.store", "store"], "'store' is listed twice", id="the same part in both spellings"),
    pytest.param(["parts.store", "parts.store"], "'store' is listed twice", id="the same reference twice"),
    pytest.param(["parts.nope"], "no part named 'nope'", id="a reference to no part"),
    pytest.param(["module.store"], "'module.store': a tier's tests lie in no instance: write parts.store",
                 id="a word for a part of the repeating folder"),
    pytest.param(["module.shared"], "'module.shared': a tier's tests lie in no instance: write parts.shared",
                 id="a word for a part in no repeating folder"),
    pytest.param(["parts.store/sql"], "'parts.store/sql': names a part only: write parts.store", id="a path"),
    pytest.param(["parts.store:*Id"], "'parts.store:*Id': names a part only: write parts.store", id="a pattern"),
    pytest.param(["everything"], "no part named 'everything'", id="everything"),
    pytest.param([3], "no part named 3", id="a number"),
    pytest.param([{"parts.store": "types_only"}], "no part named {'parts.store': 'types_only'}", id="a mode map"),
    pytest.param("parts.store", "must be a list of part names", id="one text"),
    pytest.param([], "must be a list of part names", id="no part at all"),
])
def test_a_tier_s_must_and_types_only_refuse_what_names_no_whole_part(key, written, problem):
    assert problems(with_imports({key: written})) == [f"layered.yaml: tiers.integration.imports.{key}: {problem}"]


def test_each_bad_entry_of_a_tier_s_must_is_its_own_problem():
    assert problems(with_imports({"must": ["module.store", "parts.api", "parts.api/v1", "parts.ghost"]})) == [
        "layered.yaml: tiers.integration.imports.must: 'module.store': a tier's tests lie in no instance: write "
        "parts.store",
        "layered.yaml: tiers.integration.imports.must: 'parts.api/v1': names a part only: write parts.api",
        "layered.yaml: tiers.integration.imports.must: no part named 'ghost'"]
```

In `tests/modules/spec/application/logic/test_profile_parsing.py`, change the import line 8 to add `covered`:

```python
from tests.modules.spec.profiles import TESTING, covered, layered, parsed, part_of, problems, two_folders
```

and add at the end of the file:

```python
def test_a_reference_outside_imports_is_still_no_part_name():
    """Only the lists under `imports` take references: `fakes.for` reads plain part names, as before."""
    assert problems(covered(fakes={"folder": "fakes", "for": ["parts.store"]})) == [
        "layered.yaml: fakes.for: no part named 'parts.store'"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing.py -q`
Expected: FAIL. The `parts.*` rows of `test_a_tier_s_must_and_types_only_read_parts_references_as_the_part_names` fail with `InvalidArchitecture` (`no part named 'parts.store'`); the rows `parts.nope`, `module.store`, `module.shared`, `parts.store/sql`, `parts.store:*Id`, the "both spellings" and "same reference twice" rows of the refusal test and `test_each_bad_entry_of_a_tier_s_must_is_its_own_problem` fail on the message; the four `NO_MAP` rows of `test_the_group_is_refused_when_written_wrong` fail on `{must: [<part>]}`. `test_a_reference_outside_imports_is_still_no_part_name` and the rows `everything`, a number, a mode map, one text, no part at all already pass (they pin today's behaviour).

- [ ] **Step 3: Write the reader**

In `xarch/modules/spec/application/logic/imports_written.py`, replace the last paragraph of the module docstring:

```python
A tier's `imports`, {may, also, must, types_only}, is checked as a group by the same `group`, under its own scope and
with its own example; the tier parser reads its keys (see profile_parsing), its `must` and `types_only` through
tier_parts: whole parts, `parts.<part>`, for a tier's tests lie in no instance.
"""
```

Add `import re` to the imports, so the block reads:

```python
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any
```

and add after `_joined`:

```python
def tier_parts(value: Any, declared: set[str], where: str, problems: list[str]) -> list[str]:
    """The parts a tier's `imports.must` or `imports.types_only` names, by name, in the order written: each entry
    `parts.<part>`, or the plain name of a part declared. An entry that names no whole part declared, or a part
    named twice in either spelling, adds its one problem, and the other entries are still read."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of part names")
        return []
    found: list[str] = []
    for item in value:
        name = _tier_part(item, where, problems)
        if name is None:
            continue
        if name not in declared:
            problems.append(f"{where}: no part named {name!r}")
        elif name in found:
            problems.append(f"{where}: {name!r} is listed twice")
        else:
            found.append(name)
    return found


def _tier_part(item: Any, where: str, problems: list[str]) -> str | None:
    """The part an entry of a tier's `must` or `types_only` names: the entry itself when it is no reference (the text
    before its first `/` or `:` holds no dot), the name after `parts.` when it is one; None, with its problem, for an
    entry that is no text, for `<word>.<part>`, which names an instance, and for a reference that goes on to a path or
    a pattern."""
    if not isinstance(item, str):
        problems.append(f"{where}: no part named {item!r}")
        return None
    if "." not in re.split("[/:]", item, maxsplit=1)[0]:
        return item
    prefix, _, rest = item.partition(".")
    name = re.split("[/:]", rest, maxsplit=1)[0]
    if prefix != "parts":
        problems.append(f"{where}: {item!r}: a tier's tests lie in no instance: write parts.{name}")
        return None
    if name != rest:
        problems.append(f"{where}: {item!r}: names a part only: write parts.{name}")
        return None
    return name
```

In `xarch/modules/spec/application/logic/profile_parsing.py`, in `_tier`, replace lines 664-666:

```python
    imports = iw.group(spec, where, problems, TIER_IMPORTS, "{must: [parts.<part>]}")
    types_only = (iw.tier_parts(imports["types_only"], declared, f"{where}.imports.types_only", problems)
                  if "types_only" in imports else [])
```

and lines 676-677:

```python
    reach = (iw.tier_parts(imports["must"], declared, f"{where}.imports.must", problems)
             if "must" in imports else [])
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing.py -q`
Expected: PASS.

- [ ] **Step 5: Run the gates**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: each passes; `profile check` ends `OK: the profile is valid`. If `ruff` names a line over the length limit (140), wrap it by hand (never `--fix`).
Then run `timeout 900 uv run pytest -q > /tmp/8-3-task1.txt 2>&1` in the background and read the tail of `/tmp/8-3-task1.txt` at the end.
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/imports_written.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing.py
git commit -m "A tier's imports.must and imports.types_only read parts.<part> beside the plain name, and refuse <word>.<part>, a path or a pattern, each entry its one problem

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: The three bundled profiles write every list under `imports` in references

**Files:**
- Modify: `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, `architecture.yaml` (one commit)
- Modify: `tests/bootstrap/test_rule_ids.py:203-204` and `:229-230` (they splice an exact line of `web.yaml`)
- Test: `tests/bootstrap/test_bundled_imports.py` (new T4 test at the end; the existing WHERE and digest tests stay unchanged)

**Interfaces:**
- Consumes: Task 1 (`tier_parts`), so a tier's `must: [parts.controller]` and `types_only: [parts.domain, ...]` load.
- Produces: the bundled profiles in references, which Task 3's `profile explain` examples and Task 4's `test_rule_ids.py` line 171 build on.

Every word here is `module` (`modules/<module>/` at `architecture.yaml:8`, `cli.yaml:7`, `web.yaml:7`). Parts in that folder: `domain`, `logic`, `ports`, `services`, `controller`, `adapters`, `contract`. Parts in no repeating folder: `platform`, `cli` (`web` in web.yaml), `reports` (architecture.yaml only), `main`, `bootstrap`, `profile-values` (architecture.yaml only), `kernel`, `kernel-logic`.

- [ ] **Step 1: Capture today's outputs (the T11 baseline)**

Run, before touching any profile:

```bash
uv run xarch profile check architecture.yaml > /tmp/8-3-profile-check-before.txt
uv run xarch check > /tmp/8-3-check-before.txt
uv run xarch check --strict > /tmp/8-3-check-strict-before.txt; echo "strict exit $?"
```

Expected: the first ends `OK: the profile is valid` and holds `match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, ...`; `strict exit 0`.

- [ ] **Step 2: Write the failing test (T4)**

In `tests/bootstrap/test_bundled_imports.py`, make the imports read:

```python
import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
ROOT = Path(__file__).parents[2]
```

(the `runner = CliRunner()` line exists; `ROOT` is new, right after it), and append at the end of the file:

```python


SHIPPED = {"cli": ROOT / "xarch" / "architectures" / "cli.yaml", "web": ROOT / "xarch" / "architectures" / "web.yaml",
           "architecture.yaml": ROOT / "architecture.yaml"}
"""Each profile the rules above are asked of, by the name they are asked for, as a file."""
LISTS = ("may", "must", "also", "types_only")
"""The lists of parts under an `imports` group, a part's or a tier's, which take references."""


def nodes(node, path=()):
    """Every value of a document, each with the keys and indexes that lead to it."""
    yield path, node
    children = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, value in children:
        yield from nodes(value, (*path, key))


def entries(document) -> list:
    """Every entry of a list of parts under an `imports` group, a marked one by the reference it marks."""
    return [next(iter(entry)) if isinstance(entry, dict) else entry for path, value in nodes(document)
            if path[-2:-1] == ("imports",) and path[-1] in LISTS and isinstance(value, list) for entry in value]


def texts(document) -> list[str]:
    """Every text a document writes, as a value or as a key."""
    return [text for _, value in nodes(document)
            for text in (value if isinstance(value, dict) else [value]) if isinstance(text, str)]


@pytest.mark.parametrize("profile", list(SHIPPED))
def test_every_list_of_parts_under_imports_is_written_in_references_and_no_other_key_is(profile):
    document = yaml.safe_load(SHIPPED[profile].read_text(encoding="utf-8"))
    listed = entries(document)
    assert listed
    assert [entry for entry in listed if entry != "everything" and "." not in re.split("[/:]", entry, maxsplit=1)[0]] == []
    assert sum(entry.startswith("parts.") for entry in listed) == sum(text.startswith("parts.") for text in texts(document))
```

The second assertion is "every entry is a reference or `everything`"; the third is "no text outside those lists (`fakes.for`, `built_by`, guards' `parts`, `layers`, `docs.entry`, `alike`, `results`, `imports.libraries`, ...) starts with `parts.`". Also extend the module docstring's last sentence: replace `for each profile but for the key."""` with `for each profile but for the key; and every list of parts under imports of each is written in references, which no other key is."""`.

- [ ] **Step 3: Run it to verify it fails**

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_imports.py -q -k every_list`
Expected: 3 FAIL, each on the second assertion, `AssertionError: assert ['kernel', 'kernel-logic', ...] == []`.

- [ ] **Step 4: Respell the three profiles**

Edit each line below in place (keep every other line, comment and blank line as it is). Where the new text is two lines, the second continues the flow list, aligned one column after the `[`, as `never.pure` already does in `architecture.yaml`; this keeps every line within 120 columns. `may: everything` (cli 169, web 171, architecture.yaml 192 and 323) and `{may: []}` (cli 279, web 281) stay. No key outside `imports`, and no `imports.libraries`, changes.

**`xarch/architectures/cli.yaml`** (line numbers of today's file, branch tip a4521b7; each old line is replaced by the new line or lines, indentation exactly as shown)

- line 20:

```yaml
        may: [kernel, kernel-logic]
```

  becomes:

```yaml
        may: [parts.kernel, parts.kernel-logic]
```

- line 36:

```yaml
          may: [domain, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic]
```

- line 54:

```yaml
          may: [domain, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic]
```

- line 71:

```yaml
          may: [logic, domain, ports, contract, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.logic, module.domain, module.ports, module.contract, parts.kernel, parts.kernel-logic]
```

- line 89:

```yaml
          may: [services, logic, domain, ports, contract, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.services, module.logic, module.domain, module.ports, module.contract, parts.kernel,
                parts.kernel-logic]
```

- line 107:

```yaml
        may: [ports, domain, kernel, kernel-logic, platform, contract@any]
```

  becomes:

```yaml
        may: [module.ports, module.domain, parts.kernel, parts.kernel-logic, parts.platform, parts.contract]
```

- line 108:

```yaml
        must: [platform, contract@any]
```

  becomes:

```yaml
        must: [parts.platform, parts.contract]
```

- line 126:

```yaml
        may: ["domain/values:*Id", domain/published, kernel, kernel-logic]
```

  becomes:

```yaml
        may: ["module.domain/values:*Id", module.domain/published, parts.kernel, parts.kernel-logic]
```

- line 141:

```yaml
      may: [kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.kernel, parts.kernel-logic]
```

- line 154:

```yaml
      may: [controller@any, contract@any, kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.controller, parts.contract, parts.kernel, parts.kernel-logic]
```

- line 196:

```yaml
        may: [kernel]
```

  becomes:

```yaml
        may: [parts.kernel]
```

- line 264:

```yaml
    imports: {types_only: [controller]}
```

  becomes:

```yaml
    imports: {types_only: [parts.controller]}
```


**`xarch/architectures/web.yaml`** (line numbers of today's file, branch tip a4521b7; each old line is replaced by the new line or lines, indentation exactly as shown)

- line 20:

```yaml
        may: [kernel, kernel-logic]
```

  becomes:

```yaml
        may: [parts.kernel, parts.kernel-logic]
```

- line 36:

```yaml
          may: [domain, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic]
```

- line 54:

```yaml
          may: [domain, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic]
```

- line 71:

```yaml
          may: [logic, domain, ports, contract, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.logic, module.domain, module.ports, module.contract, parts.kernel, parts.kernel-logic]
```

- line 89:

```yaml
          may: [services, logic, domain, ports, contract, kernel, kernel-logic]
```

  becomes:

```yaml
          may: [module.services, module.logic, module.domain, module.ports, module.contract, parts.kernel,
                parts.kernel-logic]
```

- line 107:

```yaml
        may: [ports, domain, kernel, kernel-logic, platform, contract@any]
```

  becomes:

```yaml
        may: [module.ports, module.domain, parts.kernel, parts.kernel-logic, parts.platform, parts.contract]
```

- line 108:

```yaml
        must: [platform, contract@any]
```

  becomes:

```yaml
        must: [parts.platform, parts.contract]
```

- line 126:

```yaml
        may: ["domain/values:*Id", domain/published, kernel, kernel-logic]
```

  becomes:

```yaml
        may: ["module.domain/values:*Id", module.domain/published, parts.kernel, parts.kernel-logic]
```

- line 141:

```yaml
      may: [kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.kernel, parts.kernel-logic]
```

- line 154:

```yaml
      may: [controller@any, contract@any, kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.controller, parts.contract, parts.kernel, parts.kernel-logic]
```

- line 198:

```yaml
        may: [kernel]
```

  becomes:

```yaml
        may: [parts.kernel]
```

- line 266:

```yaml
    imports: {types_only: [controller]}
```

  becomes:

```yaml
    imports: {types_only: [parts.controller]}
```


**`architecture.yaml`** (line numbers of today's file, branch tip a4521b7; each old line is replaced by the new line or lines, indentation exactly as shown)

- line 22:

```yaml
        may: [kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
        may: [parts.kernel, parts.kernel-logic, parts.profile-values]
```

- line 37:

```yaml
          may: [domain, kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic, parts.profile-values]
```

- line 55:

```yaml
          may: [domain, kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
          may: [module.domain, parts.kernel, parts.kernel-logic, parts.profile-values]
```

- line 70:

```yaml
          may: [logic, domain, ports, contract, kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
          may: [module.logic, module.domain, module.ports, module.contract, parts.kernel, parts.kernel-logic,
                parts.profile-values]
```

- line 88:

```yaml
          may: [services, contract, domain/errors, kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
          may: [module.services, module.contract, module.domain/errors, parts.kernel, parts.kernel-logic,
                parts.profile-values]
```

- line 106:

```yaml
        may: [ports, domain, kernel, kernel-logic, profile-values, platform, contract@any]
```

  becomes:

```yaml
        may: [module.ports, module.domain, parts.kernel, parts.kernel-logic, parts.profile-values, parts.platform,
              parts.contract]
```

- line 107:

```yaml
        must: [platform, contract@any]
```

  becomes:

```yaml
        must: [parts.platform, parts.contract]
```

- line 124:

```yaml
        may: ["domain/values:*Id", domain/published, kernel, kernel-logic, profile-values]
```

  becomes:

```yaml
        may: ["module.domain/values:*Id", module.domain/published, parts.kernel, parts.kernel-logic,
              parts.profile-values]
```

- line 138:

```yaml
      may: [kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.kernel, parts.kernel-logic]
```

- line 152:

```yaml
      may: [reports, controller@any, contract@any, kernel, kernel-logic]
```

  becomes:

```yaml
      may: [parts.reports, parts.controller, parts.contract, parts.kernel, parts.kernel-logic]
```

- line 164:

```yaml
        may: [contract@any, kernel, kernel-logic]
```

  becomes:

```yaml
        may: [parts.contract, parts.kernel, parts.kernel-logic]
```

- line 178:

```yaml
      may: [bootstrap]
```

  becomes:

```yaml
      may: [parts.bootstrap]
```

- line 211:

```yaml
      may: [kernel]
```

  becomes:

```yaml
      may: [parts.kernel]
```

- line 250:

```yaml
        may: [kernel, profile-values]
```

  becomes:

```yaml
        may: [parts.kernel, parts.profile-values]
```

- line 299:

```yaml
      also: [domain/values, domain/profile, domain/parsed, domain/outcomes]
```

  becomes:

```yaml
      also: [module.domain/values, module.domain/profile, module.domain/parsed, module.domain/outcomes]
```

- line 300:

```yaml
      must: [controller]
```

  becomes:

```yaml
      must: [parts.controller]
```

- line 311:

```yaml
      must: [bootstrap]
```

  becomes:

```yaml
      must: [parts.bootstrap]
```

- line 312:

```yaml
      types_only: [domain, logic, ports, services, controller, adapters, platform]
```

  becomes:

```yaml
      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters,
                   parts.platform]
```

- line 324:

```yaml
      types_only: [domain, logic, ports, services, controller, adapters, platform]
```

  becomes:

```yaml
      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters,
                   parts.platform]
```

- [ ] **Step 5: Respell the two tests that splice a line of `web.yaml`**

`tests/bootstrap/test_rule_ids.py` finds `web.yaml`'s `services` line by its exact text (`assert text.count(services) == 1`) and marks `contract` types_only in it; after Step 4 that line is written in references, so the two tests must look for the new line and mark `module.contract`:

**`tests/bootstrap/test_rule_ids.py`**

- Replace every one of the 2 occurrences of:

```python
    services = "          may: [logic, domain, ports, contract, kernel, kernel-logic]\n"
```

  with:

```python
    services = "          may: [module.logic, module.domain, module.ports, module.contract, parts.kernel, parts.kernel-logic]\n"
```

- Replace every one of the 2 occurrences of:

```python
    marked = services.replace("ports, contract,", "ports, {contract: types_only},")
```

  with:

```python
    marked = services.replace("module.ports, module.contract,", "module.ports, {module.contract: types_only},")
```

- [ ] **Step 6: Run the bundled-profile tests**

Run: `timeout 600 uv run pytest tests/bootstrap/test_bundled_imports.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_bundled_tiers.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_profile_explain_words.py -q`
Expected: PASS, with `RULES`, `TIER_RULES`, `WHERE` and `TIER_WHERE` of `test_bundled_imports.py` untouched (T5) and the golden docs byte for byte (T6). A moved digest or a changed `where` text means a respelled entry reads to another target: find the entry (a bare name inside `modules/<module>/` must become `module.<part>`, `@any` and a part outside the folder `parts.<part>`), fix the yaml, never the test.

- [ ] **Step 7: Diff the outputs against Step 1 (T11) and run the gates**

```bash
uv run xarch profile check architecture.yaml | diff /tmp/8-3-profile-check-before.txt - && echo profile-check-same
uv run xarch check | diff /tmp/8-3-check-before.txt - && echo check-same
uv run xarch check --strict | diff /tmp/8-3-check-strict-before.txt - && echo strict-same
uv run xarch profile check xarch/architectures/cli.yaml | tail -1
uv run xarch profile check xarch/architectures/web.yaml | tail -1
uv run ruff check
```

Expected: `profile-check-same`, `check-same`, `strict-same`, then `OK: the profile is valid` twice, then `All checks passed!`. Any diff is a defect of Step 4: fix the yaml.
Then run `timeout 900 uv run pytest -q > /tmp/8-3-task2.txt 2>&1` in the background and read its tail at the end. Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml tests/bootstrap/test_bundled_imports.py tests/bootstrap/test_rule_ids.py
git commit -m "The bundled cli and web profiles and xarch's own write every list of parts under imports as parts.<part> or module.<part>; the rules, where, the golden docs and profile check say what they said

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: `profile explain`, the messages, the docstrings, the README and the CHANGELOG say references

**Files:**
- Modify: `xarch/architectures/presets/format/keys.yaml` (`symbols` at 113-118; `fragments.two` at 22; `parts.<part>.imports.may`, `.may.types_only`, `.must` at 343-381; `tiers.<tier>.imports` at 608-620; `.also` at 731-746; `.must` at 748-761; `.types_only` at 763-775; `guards.no-twins.translated`'s example at 1246)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:28-30`, `:46-47` (the format summary of the module docstring)
- Modify: `xarch/modules/spec/application/logic/targets_written.py:1-5` (docstring), `:31` (message)
- Modify: `xarch/modules/spec/application/logic/imports_written.py:4-5` (docstring), `:33` (the part group's example), `:84` (message), `:117` (docstring)
- Modify: `xarch/modules/spec/application/logic/example_imports.py:6-8`, `xarch/modules/spec/domain/values.py:213-214`
- Modify: `xarch/modules/spec/domain/profile_keys.py:218-222`, `:226` (the retired keys' hints)
- Modify: `README.md:227-235`, `CHANGELOG.md` (`## [Unreleased]`, `### Changed`, a new last entry, right before `## [0.2.0]`)
- Test: `tests/bootstrap/test_profile_explain.py:31`, `:42`, `:332`; `tests/modules/spec/application/test_explain.py:22-26`, `:152`; `tests/modules/spec/application/logic/test_tiers.py`, `test_profile_parsing.py`, `test_profile_parsing_tests.py`, `test_imports_written.py`, `test_retired_keys.py`; `tests/modules/spec/domain/test_profile_keys.py`

**Interfaces:**
- Consumes: Task 1 (the `keys.yaml` examples `must: [parts.documents]` and `types_only: [parts.documents]` load only through `tier_parts`), Task 2.
- Produces: the new message texts, which Task 5's tests already expect: `must be a list of targets such as [parts.core, unit.store/schema]` (`targets_written.py`), `must be a list of targets such as [parts.<part>, <word>.<part>]` (a part's `imports.must`), `such as {may: [parts.<part>]}` (a part's `imports` group), `[{parts.ports: types_only}]` and `{types_only: [parts.<part>, ...]}` (retired keys).

Left as they are, on purpose: `xarch/kernel/logic/targets.py`'s messages and docstring (they belong to the refusal of the old forms, 8.4), and `xarch/kernel/logic/placement.py:8-14` and `xarch/modules/spec/application/logic/checked_tier.py:1` (re-read: they speak of scopes, not of how a profile writes them). `profile explain`'s symbol column widens to `parts.store/schema`, so each symbol's text is kept short enough for every line of `xarch profile explain` to stay within 120 columns (`test_with_no_key_the_whole_format_is_one_screen...` holds it).

- [ ] **Step 1: Write the failing tests**

Make these replacements in the tests (each old text is in the file exactly the number of times said):

**`tests/bootstrap/test_profile_explain.py`**

- Replace the one occurrence of:

```python
    assert "symbols" in result.output and "<word>" in result.output and "@any" in result.output
```

  with:

```python
    assert "symbols" in result.output and "<word>" in result.output and "parts.store" in result.output
    assert "unit.store" in result.output and "@any" not in result.output
```

- Replace the one occurrence of:

```python
                     "may: [core]", "parts.imports.may.types_only"):
```

  with:

```python
                     "may: [parts.core]", "parts.imports.may.types_only"):
```

- Replace the one occurrence of:

```python
{types_only: [<part>, ...]}
```

  with:

```python
{types_only: [parts.<part>, ...]}
```


**`tests/modules/spec/application/test_explain.py`**

- Replace the one occurrence of:

```python
    Symbol("<word>/", "under parts, a folder key: a repeating folder, one per name, as in units/<unit>/; there may be several"),
    Symbol("store", "in imports.may, a bare name: that part, in the importer's own instance of its repeating folder"),
    Symbol("store@any", "that part in any instance; the only way to name a part of another repeating folder"),
    Symbol("store/schema", "only what lies below that path of the part"),
    Symbol("store:*Id", "in imports.may, after `:`: only the names that match the pattern, `*` for any text"),
```

  with:

```python
    Symbol("<word>/", "under parts: a repeating folder, one per name, as in units/<unit>/; there may be several"),
    Symbol("parts.store", "in imports: that part in every instance of its repeating folder, or the part itself outside one"),
    Symbol("unit.store", "in imports: that part in the importer's own instance of its repeating folder, units/<unit>/"),
    Symbol("parts.store/schema", "only what lies below that path of the part"),
    Symbol("parts.store:*Id", "in imports.may, after `:`: only the names that match the pattern, `*` for any text"),
```

- Replace the one occurrence of:

```python
    assert "@any" in key.accepts and "may: [core]" in key.example
```

  with:

```python
    assert "parts.<part>" in key.accepts and "<word>.<part>" in key.accepts and "may: [parts.core]" in key.example
    assert "@any" not in key.accepts and "bare name" not in key.accepts
```


**`tests/modules/spec/application/logic/test_tiers.py`**

- Replace every one of the 2 occurrences of:

```python
types_only: [<part>, ...]
```

  with:

```python
types_only: [parts.<part>, ...]
```

- Replace the one occurrence of:

```python
[<part>, shared/text, api@any]
```

  with:

```python
[parts.core, unit.store/schema]
```


**`tests/modules/spec/application/logic/test_profile_parsing_tests.py`**

- Replace the one occurrence of:

```python
[<part>, shared/text, api@any]
```

  with:

```python
[parts.core, unit.store/schema]
```


**`tests/modules/spec/application/logic/test_profile_parsing.py`**

- Replace every one of the 2 occurrences of:

```python
must be a list of targets such as [<part>, "
```

  with:

```python
must be a list of targets such as [parts.core, "
```

- Replace every one of the 2 occurrences of:

```python
"shared/text, api@any], or everything"
```

  with:

```python
"unit.store/schema], or everything"
```

- Replace every one of the 2 occurrences of:

```python
[<part>, <part>@any]
```

  with:

```python
[parts.<part>, <word>.<part>]
```


**`tests/modules/spec/application/logic/test_imports_written.py`**

- Replace every one of the 2 occurrences of:

```python
[<part>, <part>@any]
```

  with:

```python
[parts.<part>, <word>.<part>]
```

- Replace every one of the 5 occurrences of:

```python
such as {may: [<part>]}
```

  with:

```python
such as {may: [parts.<part>]}
```

- Replace every one of the 2 occurrences of:

```python
[{ports: types_only}]
```

  with:

```python
[{parts.ports: types_only}]
```


**`tests/modules/spec/application/logic/test_retired_keys.py`**

- Replace every one of the 3 occurrences of:

```python
[{ports: types_only}]
```

  with:

```python
[{parts.ports: types_only}]
```

- Replace every one of the 2 occurrences of:

```python
{types_only: [<part>, ...]}
```

  with:

```python
{types_only: [parts.<part>, ...]}
```


**`tests/modules/spec/domain/test_profile_keys.py`**

- Replace every one of the 2 occurrences of:

```python
[{ports: types_only}]
```

  with:

```python
[{parts.ports: types_only}]
```

- Replace the one occurrence of:

```python
{types_only: [<part>, ...]}
```

  with:

```python
{types_only: [parts.<part>, ...]}
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 600 uv run pytest tests/bootstrap/test_profile_explain.py tests/modules/spec/application/test_explain.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py -q`
Expected: FAIL: `test_the_whole_format_is_the_keys_of_the_file_their_symbols_and_the_smallest_profile` (`FORMAT.symbols == SAID`), `test_a_key_says_what_it_accepts_...` (`"parts.<part>" in key.accepts`), the two `test_profile_explain.py` tests (`parts.store`, `may: [parts.core]`), the retired-key rows (`[{parts.ports: types_only}]`, `{types_only: [parts.<part>, ...]}`), the `such as` rows; each on its expected text.

- [ ] **Step 3: Rewrite the format text, the docstrings and the messages**

**`xarch/architectures/presets/format/keys.yaml`**

- Replace the one occurrence of:

```yaml
        imports:
          may: [core]
  tiered-part: |
```

  with:

```yaml
        imports:
          may: [parts.core]
  tiered-part: |
```

- Replace the one occurrence of:

```yaml
  "<word>/": "under parts, a folder key: a repeating folder, one per name, as in units/<unit>/; there may be several"
  store: "in imports.may, a bare name: that part, in the importer's own instance of its repeating folder"
  store@any: that part in any instance; the only way to name a part of another repeating folder
  store/schema: only what lies below that path of the part
  store:*Id: "in imports.may, after `:`: only the names that match the pattern, `*` for any text"
```

  with:

```yaml
  "<word>/": "under parts: a repeating folder, one per name, as in units/<unit>/; there may be several"
  parts.store: "in imports: that part in every instance of its repeating folder, or the part itself outside one"
  unit.store: "in imports: that part in the importer's own instance of its repeating folder, units/<unit>/"
  parts.store/schema: only what lies below that path of the part
  parts.store:*Id: "in imports.may, after `:`: only the names that match the pattern, `*` for any text"
```

- Replace the one occurrence of:

```yaml
      [<part>, <part>@any, <part>/<path>, <part>:<pattern>, {<target>: types_only}, ...] or everything: a bare name is
      that part in the importer's own instance (a part of another repeating folder has none: write `@any`), `@any` any
      instance, `/<path>` only what lies below it, `:<pattern>` only the names that match the pattern (`*` for any
      text, such as `core/ids:*Id`): `from <there> import <name>` for each name, never the file as a whole, and a file
      of the tests is not narrowed; an entry written `{<target>: types_only}` is a target the part may import only to
      use as a type (imports.may.types_only); a part may always import itself, so a target that only says so is refused
```

  with:

```yaml
      [parts.<part>, <word>.<part>, ...] or everything, each reference optionally followed by `/<path>` and
      `:<pattern>`, or one marked {<reference>: types_only}: `parts.<part>` is that part in every instance of its
      repeating folder, or the part itself outside one; `<word>.<part>` the part in the importer's own instance of the
      folder the word repeats, which the importer lies in too; `/<path>` only what lies below it, `:<pattern>` only the
      names that match the pattern (`*` for any text, such as `parts.core/ids:*Id`): `from <there> import <name>` for
      each name, never the file as a whole, and a file of the tests is not narrowed; an entry written
      `{<reference>: types_only}` is a target the part may import only to use as a type (imports.may.types_only); a
      part may always import itself, so a target that only says so is refused
```

- Replace the one occurrence of:

```yaml
            may: [{core: types_only}]
```

  with:

```yaml
            may: [{parts.core: types_only}]
```

- Replace the one occurrence of:

```yaml
      [<target>, ...] written as `imports.may` writes them, with no mode,
```

  with:

```yaml
      [<reference>, ...] written as `imports.may` writes them, with no mode,
```

- Replace the one occurrence of:

```yaml
      <<two>>
            must: [core]
```

  with:

```yaml
      <<two>>
            must: [parts.core]
```

- Replace the one occurrence of:

```yaml
      import of the app (only for a tier with a `folder`), `also` what its tests may import besides, `must` the parts
      one of which each of its test files reaches, `types_only` the parts its tests may import only as types. Without
      `imports`, a test imports what the part it mirrors may, and a test of the tier's folder nothing of the app
```

  with:

```yaml
      import of the app (only for a tier with a `folder`), `also` what its tests may import besides, `must` the parts
      (`parts.<part>`) one of which each of its test files reaches, `types_only` the parts (`parts.<part>`) its tests
      may import only as types. Without `imports`, a test imports what the part it mirrors may, and a test of the
      tier's folder nothing of the app
```

- Replace the one occurrence of:

```yaml
          imports:
            must: [documents]
      <<tiered-part>>
  tiers.<tier>.docs:
```

  with:

```yaml
          imports:
            must: [parts.documents]
      <<tiered-part>>
  tiers.<tier>.docs:
```

- Replace the one occurrence of:

```yaml
      targets, as a part's `imports.may`, read from the instance a test mirrors, and added to what each test of the
      tier may import of the app, such as the values a test builds its fakes' answers with; not `everything`. A target
      the bundled profile's tier does not give is listed by `profile check` as looser
```

  with:

```yaml
      references, as a part's `imports.may`, `<word>.<part>` the instance a test mirrors, and added to what each
      test of the tier may import of the app, such as the values a test builds its fakes' answers with; not
      `everything`. A target the bundled profile's tier does not give is listed by `profile check` as looser
```

- Replace the one occurrence of:

```yaml
            also: [core]
```

  with:

```yaml
            also: [parts.core]
```

- Replace the one occurrence of:

```yaml
          imports:
            must: [documents]
      <<tiered-part>>
  tiers.<tier>.imports.types_only:
```

  with:

```yaml
          imports:
            must: [parts.documents]
      <<tiered-part>>
  tiers.<tier>.imports.types_only:
```

- Replace the one occurrence of:

```yaml
      [<part>, ...]: a test may import them to annotate, never to call:
```

  with:

```yaml
      [parts.<part>, ...]: a test may import them to annotate, never to call:
```

- Replace the one occurrence of:

```yaml
            types_only: [documents]
```

  with:

```yaml
            types_only: [parts.documents]
```

- Replace the one occurrence of:

```yaml
          imports: {may: [documents]}
```

  with:

```yaml
          imports: {may: [parts.documents]}
```

- Replace the one occurrence of:

```yaml
      the mode of an entry of `imports.may`, written `{<target>: types_only}`, one target per entry, such as
      `[{core: types_only}]`: a file of the part may import what the entry reaches to annotate, and for `isinstance`
      and exception matching, but never call what it imports from there (`X(...)`, `m.X(...)`, `X.build(...)`) nor
      reference one of its top-level functions at all, read through every import, however written. The rule reads what
      the entry reaches, its part, instance and path; its name pattern narrows only what may be imported. A tier's
      `imports.types_only` is the list form of the same idea, read on a test
```

  with:

```yaml
      the mode of an entry of `imports.may`, written `{<reference>: types_only}`, one reference per entry, such as
      `[{parts.core: types_only}]`: a file of the part may import what the entry reaches to annotate, and for
      `isinstance` and exception matching, but never call what it imports from there (`X(...)`, `m.X(...)`,
      `X.build(...)`) nor reference one of its top-level functions at all, read through every import, however written.
      The rule reads what the entry reaches, its part, instance and path; its name pattern narrows only what may be
      imported. A tier's `imports.types_only` is the list form of the same idea, read on a test
```

- Replace the one occurrence of:

```yaml
      [<part>, ...]: each test file of the tier (a file whose name `testing.files` matches) imports from one of those
      parts, in any instance, or imports test code that is no test file and does, however far the chain goes; a test
      file with no function holding a real statement is exempt, and a file failing is reported once, as a whole. Silent
      on what a test is handed without importing it, such as a fixture
```

  with:

```yaml
      [parts.<part>, ...]: each test file of the tier (a file whose name `testing.files` matches) imports from one of
      those parts, in any instance, or imports test code that is no test file and does, however far the chain goes; a
      test file with no function holding a real statement is exempt, and a file failing is reported once, as a whole.
      A tier's tests lie in no instance, so `<word>.<part>` is refused here. Silent on what a test is handed without
      importing it, such as a fixture
```


**`xarch/modules/spec/application/logic/profile_parsing.py`**

- Replace the one occurrence of:

```python
                               what the part may import besides itself, which it always may: each entry a target
                               (a bare name of a part in the repeating folder is the importer's own instance, `@any`
                               any instance, `/<path>` below it) or one marked {<target>: types_only}, or everything;
```

  with:

```python
                               what the part may import besides itself, which it always may: each entry a reference
                               (`parts.<part>` the part in every instance, `<word>.<part>` the importer's own
                               instance, `/<path>` below it) or one marked {<reference>: types_only}, or everything;
```

- Replace the one occurrence of:

```python
                               `imports.must` the parts one of which each of its test files reaches;
                               `imports.types_only` the parts its tests may import only as types;
```

  with:

```python
                               `imports.must` the parts (`parts.<part>`) one of which each of its test files reaches;
                               `imports.types_only` the parts (`parts.<part>`) its tests may import only as types;
```


**`xarch/modules/spec/application/logic/targets_written.py`**

- Replace the one occurrence of:

```python
"""What a part, or the tests in a tier's folder, may import, as a profile writes it: a list of targets (see the target
grammar in kernel/logic/targets: the old forms, and the references parts.<part> and <word>.<part>, the word one of the
profile's repeating folders), or `everything`; checked against the parts declared and the part that writes them (None
for a tier's folder), each problem said at its address. What a tier's tests may also import is a list of targets
alone, a bare name in the repeating folder, or <word>.<part>, being the instance a test mirrors."""
```

  with:

```python
"""What a part, or the tests in a tier's folder, may import, as a profile writes it: a list of targets, each a reference
(see the target grammar in kernel/logic/targets), parts.<part> or <word>.<part>, the word one of the profile's
repeating folders, or `everything`; checked against the parts declared and the part that writes them (None for a
tier's folder), each problem said at its address. What a tier's tests may also import is a list of targets alone,
<word>.<part> being the instance a test mirrors."""
```

- Replace the one occurrence of:

```python
"{where}: must be a list of targets such as [<part>, shared/text, api@any]"
```

  with:

```python
"{where}: must be a list of targets such as [parts.core, unit.store/schema]"
```


**`xarch/modules/spec/application/logic/imports_written.py`**

- Replace the one occurrence of:

```python
    imports: {may: [<target> | {<target>: types_only}, ...] | everything, must: [<target>, ...],
```

  with:

```python
    imports: {may: [<reference> | {<reference>: types_only}, ...] | everything, must: [<reference>, ...],
```

- Replace the one occurrence of:

```python
          example: str = "{may: [<part>]}") -> Mapping[Any, Any]:
```

  with:

```python
          example: str = "{may: [parts.<part>]}") -> Mapping[Any, Any]:
```

- Replace the one occurrence of:

```python
"{where}: must be a list of targets such as [<part>, <part>@any]"
```

  with:

```python
"{where}: must be a list of targets such as [parts.<part>, <word>.<part>]"
```

- Replace the one occurrence of:

```python
"""A map entry as a profile writes it, in flow style: {ports: types_only}."""
```

  with:

```python
"""A map entry as a profile writes it, in flow style: {parts.ports: types_only}."""
```


**`xarch/modules/spec/application/logic/example_imports.py`**

- Replace the one occurrence of:

```python
or the same part, in the importer's instance (a bare name), in any instance (@any) or outside the repeating folder,
and below its /<path> if it names one.
```

  with:

```python
or the same part, in the importer's instance (`<word>.<part>`), in any instance or outside the repeating folder
(`parts.<part>`), and below its /<path> if it names one.
```


**`xarch/modules/spec/domain/values.py`**

- Replace the one occurrence of:

```python
        folder's allowance), as targets; a bare name of a part in the repeating folder is the instance the test mirrors
```

  with:

```python
        folder's allowance), as targets; `<word>.<part>`, a part in the repeating folder, is the instance the test
        mirrors
```


**`xarch/modules/spec/domain/profile_keys.py`**

- Replace the one occurrence of:

```python
    Retired(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                                "[{ports: types_only}]"),
```

  with:

```python
    Retired(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                                "[{parts.ports: types_only}]"),
```

- Replace the one occurrence of:

```python
    Retired(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                                        "[{ports: types_only}]"),
```

  with:

```python
    Retired(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                                        "[{parts.ports: types_only}]"),
```

- Replace the one occurrence of:

```python
    Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}"),
```

  with:

```python
    Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [parts.<part>, ...]}"),
```

- [ ] **Step 4: README and CHANGELOG**

Before editing, run `grep -nE "(may|must|also|types_only): *\[|@any" README.md`: today it prints only the `imports.may` bullet (line 227), so no other README snippet writes a list under `imports`; if it prints another line, respell it by the rule of the Global Constraints.

**`README.md`**

- Replace the one occurrence of:

```markdown
- In `imports.may`, a bare name is that part in the importer's own instance of its repeating folder; `store@any` any
  instance, and the only way to name a part of another repeating folder, which has no own instance; `store/schema`
  only that path below the part; `store:*Id` only the names that match the pattern, imported by name;
  `everything` no limit (also for `imports.libraries`); an entry written `{store: types_only}` is a target the part
  may import only to use as a type. A part may always import itself. A target may also be written as a reference:
  `parts.store` is the part in every instance (or, outside a repeating folder, the part itself), and `<word>.store`,
  such as `module.store`, the part in the importer's own instance of the `<word>` folder, each optionally followed by
  `/<path>` and `:<pattern>`; the forms above stay the bundled spelling. `profile explain --rule` and the looser lines
  of `profile check` and `check` write a target as a reference, `parts.<part>` or `<word>.<part>`.
```

  with:

```markdown
- Every list of parts under `imports` writes each target as a reference: `parts.store` is that part in every
  instance of its repeating folder (or, outside one, the part itself), and `<word>.store`, such as `unit.store`, the
  part in the importer's own instance of the `<word>` folder, which the importer lies in too (in a tier's
  `imports.also`, the instance the test mirrors); either is optionally followed by `/<path>`, only that path below
  the part (`parts.store/schema`), and, in `imports.may`, `:<pattern>`, only the names that match the pattern,
  imported by name (`parts.store:*Id`). `everything` is no limit (also for `imports.libraries`); an entry written
  `{parts.store: types_only}` is a target the part may import only to use as a type. A tier's `imports.must` and
  `imports.types_only` name whole parts, `parts.<part>`, for a tier's tests lie in no instance. A part may always
  import itself. `profile explain --rule` and the looser lines of `profile check` and `check` write a target the
  same way.
```


**`CHANGELOG.md`**

- Replace the one occurrence of:

```markdown
  also import parts.platform`, `targets: [{place: [parts.platform, parts.contract]}, outside]`). `everything` is
  still written `everything`, and the JSON's shape does not change.
```

  with:

```markdown
  also import parts.platform`, `targets: [{place: [parts.platform, parts.contract]}, outside]`). `everything` is
  still written `everything`, and the JSON's shape does not change.
- The bundled profiles (`cli`, `web`) and xarch's own `architecture.yaml` write every list of parts under `imports`
  as references: a part in the importer's own instance `module.<part>`, one in any instance or in no repeating
  folder `parts.<part>` (`may: [module.domain, parts.kernel, parts.contract]`, `"module.domain/values:*Id"`,
  `types_only: [parts.controller]`); what each allows does not change, and `profile check architecture.yaml` prints
  what it printed. A tier's `imports.must` and `imports.types_only` read `parts.<part>` beside a plain name, and
  refuse `<word>.<part>` (`'module.controller': a tier's tests lie in no instance: write parts.controller`) and a
  path or a pattern (`'parts.controller/x': names a part only: write parts.controller`), each entry its own problem.
  `profile explain` (its symbols and the keys under `imports`), the README and the examples the messages give
  (`must be a list of targets such as [parts.core, unit.store/schema]`, `such as {must: [parts.<part>]}`,
  `[{parts.ports: types_only}]`) say references.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run the command of Step 2. Expected: PASS.
Then: `uv run xarch profile explain | awk 'length($0) > 120'` prints nothing, and `uv run xarch profile explain parts.imports.may` shows the new `accepts:` and the example `may: [parts.core]`.

- [ ] **Step 6: Run the gates**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: each passes. Then `timeout 900 uv run pytest -q > /tmp/8-3-task3.txt 2>&1` in the background, its tail read at the end: all pass (every example of `keys.yaml` is loaded by the existing example tests; one that fails names the key whose example is written wrong: fix the example).

- [ ] **Step 7: Commit**

```bash
git add xarch/architectures/presets/format/keys.yaml xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/application/logic/targets_written.py xarch/modules/spec/application/logic/imports_written.py xarch/modules/spec/application/logic/example_imports.py xarch/modules/spec/domain/values.py xarch/modules/spec/domain/profile_keys.py README.md CHANGELOG.md tests/bootstrap/test_profile_explain.py tests/modules/spec/application/test_explain.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py
git commit -m "profile explain, the messages' examples, the docstrings, the README and the CHANGELOG write a target under imports as parts.<part> or <word>.<part>

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: The bootstrap tests and the recorded corpora write references

**Files:**
- Modify: `tests/bootstrap/test_architecture_files.py`, `test_bundled_tiers.py`, `test_examples.py`, `test_docs_templates.py`, `test_other_framework.py`, `test_loop_tables.py`, `test_no_table_form.py`, `test_app.py`, `test_top_level_file.py`, `test_profile_file.py`, `test_tests_beside.py`, `test_needs_agree.py`, `test_repeating_folders.py`, `test_profile_check.py`, `test_check_enforcement.py`, `test_rule_ids.py` (line 171), all under `tests/bootstrap/`
- Modify: `tests/bootstrap/corpora/7cc6111.yaml`, `df537ca.yaml`, `stress.yaml` (by hand; the `.json` findings and the `.tar.xz` archives are not touched)

**Interfaces:**
- Consumes: Task 1 (a tier's `must`/`types_only` read `parts.<part>`), Task 2 (`web.yaml`'s integration tier spliced by `test_rule_ids.py`).
- Produces: nothing new; the same assertions pass on respelled profiles (T9, T10).

This task changes no behaviour, so there is no RED step: each edit is a respelling, and the proof is that the tests and the recorded findings still pass with their assertions unchanged, but for the two assertions that print a respelled value (`'parts.a' is implied` in `test_architecture_files.py`). The words: `src/<module>/` or `modules/<module>/` give `module` in every file here; `tests/bootstrap/test_repeating_folders.py` has a second folder, `plugins/<plugin>/` (`hooks`, `manifest`), whose word is `plugin`; `test_top_level_file.py`, `test_profile_file.py`, `test_needs_agree.py` have no repeating folder (every entry `parts.<part>`). Kept on purpose: `tests/bootstrap/test_profile_explain_words.py`, `test_where.py`, `test_bundled_holds.py`, `test_review.py` (nothing under `imports` written in an old form); every `fakes.for`, `built_by`, guards' `parts`, `results`, `libraries`, `docs.entry`, `evals` list.

- [ ] **Step 1: Respell the bootstrap tests**

**`tests/bootstrap/test_architecture_files.py`**

- Replace the one occurrence of:

```python
        may: [service]
```

  with:

```python
        may: [module.service]
```

- Replace the one occurrence of:

```python
        may: [store]
```

  with:

```python
        may: [module.store]
```

- Replace the one occurrence of:

```python
"imports": {"may": ["service"]}}
```

  with:

```python
"imports": {"may": ["module.service"]}}
```

- Replace the one occurrence of:

```python
"imports": {"may": ["store"]}}
```

  with:

```python
"imports": {"may": ["module.store"]}}
```

- Replace the one occurrence of:

```python
parts: {a/: {role: r, imports: {may: [a]}}}
```

  with:

```python
parts: {a/: {role: r, imports: {may: [parts.a]}}}
```

- Replace the one occurrence of:

```python
parts.a.imports.may: 'a' is implied
```

  with:

```python
parts.a.imports.may: 'parts.a' is implied
```


**`tests/bootstrap/test_bundled_tiers.py`**

- Replace the one occurrence of:

```python
        may: [store]
```

  with:

```python
        may: [module.store]
```


**`tests/bootstrap/test_examples.py`**

- Replace the one occurrence of:

```python
api/: {role: handlers, imports: {may: [store]}}
```

  with:

```python
api/: {role: handlers, imports: {may: [module.store]}}
```


**`tests/bootstrap/test_docs_templates.py`**

- Replace the one occurrence of:

```python
imports: {may: [store]}}
```

  with:

```python
imports: {may: [module.store]}}
```


**`tests/bootstrap/test_other_framework.py`**

- Replace the one occurrence of:

```python
may: [contract, ports]
```

  with:

```python
may: [module.contract, module.ports]
```


**`tests/bootstrap/test_loop_tables.py`**

- Replace the one occurrence of:

```python
may: [contract, ports]
```

  with:

```python
may: [module.contract, module.ports]
```


**`tests/bootstrap/test_no_table_form.py`**

- Replace the one occurrence of:

```python
        may: [contract]
```

  with:

```python
        may: [module.contract]
```


**`tests/bootstrap/test_app.py`**

- Replace the one occurrence of:

```python
imports: {may: [lib]}
```

  with:

```python
imports: {may: [parts.lib]}
```


**`tests/bootstrap/test_top_level_file.py`**

- Replace the one occurrence of:

```python
      may: [core]
```

  with:

```python
      may: [parts.core]
```


**`tests/bootstrap/test_profile_file.py`**

- Replace the one occurrence of:

```python
      may: [core]
```

  with:

```python
      may: [parts.core]
```


**`tests/bootstrap/test_tests_beside.py`**

- Replace the one occurrence of:

```python
imports: {may: [domain]}
```

  with:

```python
imports: {may: [module.domain]}
```

- Replace the one occurrence of:

```python
imports: {may: [domain, contract]}
```

  with:

```python
imports: {may: [module.domain, module.contract]}
```


**`tests/bootstrap/test_needs_agree.py`**

- Replace the one occurrence of:

```python
      may: [{api: types_only}]
      must: [api]
```

  with:

```python
      may: [{parts.api: types_only}]
      must: [parts.api]
```

- Replace the one occurrence of:

```python
      also: [api]
      must: [core]
      types_only: [api]
```

  with:

```python
      also: [parts.api]
      must: [parts.core]
      types_only: [parts.api]
```

- Replace the one occurrence of:

```python
    imports:
      may: [core]
fakes:
```

  with:

```python
    imports:
      may: [parts.core]
fakes:
```


**`tests/bootstrap/test_repeating_folders.py`**

- Replace every one of the 2 occurrences of:

```python
        may: [kernel]
```

  with:

```python
        may: [parts.kernel]
```

- Replace the one occurrence of:

```python
        may: [domain, kernel]
```

  with:

```python
        may: [module.domain, parts.kernel]
```

- Replace the one occurrence of:

```python
        may: [domain, kernel, contract@any, hooks@any]
```

  with:

```python
        may: [module.domain, parts.kernel, parts.contract, parts.hooks]
```

- Replace the one occurrence of:

```python
        may: [manifest, kernel, contract@any]
        must: [manifest, contract@any]
```

  with:

```python
        may: [plugin.manifest, parts.kernel, parts.contract]
        must: [plugin.manifest, parts.contract]
```


**`tests/bootstrap/test_profile_check.py`**

- Replace the one occurrence of:

```python
imports={"may": ["kernel", "ghost"]}
```

  with:

```python
imports={"may": ["parts.kernel", "parts.ghost"]}
```

- Replace the one occurrence of:

```python
imports={"may": ["kernel", "platform"]}
```

  with:

```python
imports={"may": ["parts.kernel", "parts.platform"]}
```


**`tests/bootstrap/test_check_enforcement.py`**

- Replace every one of the 2 occurrences of:

```python
"  kernel/:\n    imports:\n      may: [platform]\n"
```

  with:

```python
"  kernel/:\n    imports:\n      may: [parts.platform]\n"
```


**`tests/bootstrap/test_rule_ids.py`**

- Replace the one occurrence of:

```python
"  integration:\n    imports: {must: [controller]}\n"
```

  with:

```python
"  integration:\n    imports: {must: [parts.controller]}\n"
```

- [ ] **Step 2: Run them**

Run: `timeout 600 uv run pytest tests/bootstrap/test_architecture_files.py tests/bootstrap/test_bundled_tiers.py tests/bootstrap/test_examples.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_loop_tables.py tests/bootstrap/test_no_table_form.py tests/bootstrap/test_app.py tests/bootstrap/test_top_level_file.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_tests_beside.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_repeating_folders.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_rule_ids.py -q`
Expected: PASS. A failure other than a printed spelling means the respelling is wrong (a wrong word, or a part outside the folder written `<word>.`): fix the profile, not the assertion.

- [ ] **Step 3: Respell the corpora, by hand**

Each row is one line of today's file; replace the whole line, keeping its indentation exactly as shown. A list written as a block (`- logic` under `may:`) keeps its shape; `may: everything` and `libraries: []` stay.

**`tests/bootstrap/corpora/7cc6111.yaml`** (word `module`, from `modules/<module>/` at the top of the file; line numbers of today's file)

| line | today | becomes |
|---|---|---|
| 12 | `        may: [kernel]` | `        may: [parts.kernel]` |
| 22 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 33 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 43 | `            - logic` | `            - module.logic` |
| 44 | `            - domain` | `            - module.domain` |
| 45 | `            - ports` | `            - module.ports` |
| 46 | `            - contract: types_only` | `            - module.contract: types_only` |
| 47 | `            - kernel` | `            - parts.kernel` |
| 56 | `          may: [services, logic, domain, ports, contract, kernel]` | `          may: [module.services, module.logic, module.domain, module.ports, module.contract, parts.kernel]` |
| 65 | `        may: [ports, domain, kernel, platform, contract@any]` | `        may: [module.ports, module.domain, parts.kernel, parts.platform, parts.contract]` |
| 66 | `        must: [platform, contract@any]` | `        must: [parts.platform, parts.contract]` |
| 74 | `        may: ["domain/values:*Id", kernel]` | `        may: ["module.domain/values:*Id", parts.kernel]` |
| 82 | `      may: [kernel]` | `      may: [parts.kernel]` |
| 88 | `      may: [controller@any, contract@any, kernel]` | `      may: [parts.controller, parts.contract, parts.kernel]` |
| 97 | `      may: [bootstrap]` | `      may: [parts.bootstrap]` |
| 132 | `      must: [controller]` | `      must: [parts.controller]` |
| 140 | `      must: [bootstrap]` | `      must: [parts.bootstrap]` |
| 141 | `      types_only: [domain, logic, ports, services, controller, adapters, platform]` | `      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters, parts.platform]` |
| 150 | `      types_only: [domain, logic, ports, services, controller, adapters, platform]` | `      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters, parts.platform]` |

**`tests/bootstrap/corpora/df537ca.yaml`** (word `module`, from `modules/<module>/` at the top of the file; line numbers of today's file)

| line | today | becomes |
|---|---|---|
| 12 | `        may: [kernel]` | `        may: [parts.kernel]` |
| 22 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 33 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 43 | `            - logic` | `            - module.logic` |
| 44 | `            - domain` | `            - module.domain` |
| 45 | `            - ports` | `            - module.ports` |
| 46 | `            - contract: types_only` | `            - module.contract: types_only` |
| 47 | `            - kernel` | `            - parts.kernel` |
| 58 | `          may: [services, logic, domain, ports, contract, kernel]` | `          may: [module.services, module.logic, module.domain, module.ports, module.contract, parts.kernel]` |
| 69 | `        may: [ports, domain, kernel, platform, contract@any]` | `        may: [module.ports, module.domain, parts.kernel, parts.platform, parts.contract]` |
| 70 | `        must: [platform, contract@any]` | `        must: [parts.platform, parts.contract]` |
| 79 | `        may: ["domain/values:*Id", kernel]` | `        may: ["module.domain/values:*Id", parts.kernel]` |
| 87 | `      may: [kernel]` | `      may: [parts.kernel]` |
| 93 | `      may: [reports, controller@any, contract@any, kernel]` | `      may: [parts.reports, parts.controller, parts.contract, parts.kernel]` |
| 100 | `        may: [contract@any, kernel]` | `        may: [parts.contract, parts.kernel]` |
| 113 | `      may: [bootstrap]` | `      may: [parts.bootstrap]` |
| 156 | `      must: [controller]` | `      must: [parts.controller]` |
| 164 | `      must: [bootstrap]` | `      must: [parts.bootstrap]` |
| 165 | `      types_only: [domain, logic, ports, services, controller, adapters, platform]` | `      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters, parts.platform]` |
| 174 | `      types_only: [domain, logic, ports, services, controller, adapters, platform]` | `      types_only: [parts.domain, parts.logic, parts.ports, parts.services, parts.controller, parts.adapters, parts.platform]` |

**`tests/bootstrap/corpora/stress.yaml`** (word `module`, from `modules/<module>/` at the top of the file; line numbers of today's file)

| line | today | becomes |
|---|---|---|
| 10 | `        may: [kernel]` | `        may: [parts.kernel]` |
| 22 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 34 | `          may: [domain, kernel]` | `          may: [module.domain, parts.kernel]` |
| 45 | `            - logic` | `            - module.logic` |
| 46 | `            - domain` | `            - module.domain` |
| 47 | `            - ports` | `            - module.ports` |
| 48 | `            - contract: types_only` | `            - module.contract: types_only` |
| 49 | `            - kernel` | `            - parts.kernel` |
| 50 | `          must: [ports]` | `          must: [module.ports]` |
| 61 | `          may: [services, logic, domain, ports, contract, kernel]` | `          may: [module.services, module.logic, module.domain, module.ports, module.contract, parts.kernel]` |
| 73 | `          - ports` | `          - module.ports` |
| 74 | `          - domain: types_only` | `          - module.domain: types_only` |
| 75 | `          - kernel` | `          - parts.kernel` |
| 76 | `          - platform` | `          - parts.platform` |
| 77 | `          - contract@any` | `          - parts.contract` |
| 78 | `        must: [platform, contract@any]` | `        must: [parts.platform, parts.contract]` |
| 90 | `        may: ["domain/values:*Id", kernel]` | `        may: ["module.domain/values:*Id", parts.kernel]` |
| 98 | `      may: [kernel]` | `      may: [parts.kernel]` |
| 110 | `      may: [reports, controller@any, contract@any, kernel]` | `      may: [parts.reports, parts.controller, parts.contract, parts.kernel]` |
| 119 | `        may: [contract@any, kernel]` | `        may: [parts.contract, parts.kernel]` |
| 133 | `      may: [bootstrap]` | `      may: [parts.bootstrap]` |
| 215 | `      - domain` | `      - parts.domain` |
| 216 | `      - logic` | `      - parts.logic` |
| 217 | `      - kernel` | `      - parts.kernel` |
| 219 | `      - domain` | `      - parts.domain` |
| 225 | `      - controller` | `      - parts.controller` |
| 234 | `      - bootstrap` | `      - parts.bootstrap` |
| 236 | `      - domain` | `      - parts.domain` |
| 237 | `      - logic` | `      - parts.logic` |
| 238 | `      - ports` | `      - parts.ports` |
| 239 | `      - services` | `      - parts.services` |
| 240 | `      - controller` | `      - parts.controller` |
| 241 | `      - adapters` | `      - parts.adapters` |
| 242 | `      - platform` | `      - parts.platform` |
| 252 | `      - domain` | `      - parts.domain` |
| 253 | `      - logic` | `      - parts.logic` |
| 254 | `      - ports` | `      - parts.ports` |
| 255 | `      - services` | `      - parts.services` |
| 256 | `      - controller` | `      - parts.controller` |
| 257 | `      - adapters` | `      - parts.adapters` |
| 258 | `      - platform` | `      - parts.platform` |

Then check nothing under `imports` is left in an old form:

```bash
uv run python - <<'PY'
import re, yaml
from pathlib import Path
def nodes(node, path=()):
    yield path, node
    children = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, value in children:
        yield from nodes(value, (*path, key))
for file in sorted(Path("tests/bootstrap/corpora").glob("*.yaml")):
    document = yaml.safe_load(file.read_text())
    old = [entry for path, value in nodes(document)
           if path[-2:-1] == ("imports",) and path[-1] in ("may", "must", "also", "types_only") and isinstance(value, list)
           for entry in (next(iter(e)) if isinstance(e, dict) else e for e in value)
           if entry != "everything" and "." not in re.split("[/:]", entry, maxsplit=1)[0]]
    print(file.name, old)
PY
```

Expected: `7cc6111.yaml []`, `df537ca.yaml []`, `stress.yaml []`.

- [ ] **Step 4: Run the corpora tests (T10)**

Run: `timeout 600 uv run pytest tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_written_rules.py -q`
Expected: PASS with the recorded `.json` findings unchanged (`git status --short tests/bootstrap/corpora/` lists only the three `.yaml` files).

- [ ] **Step 5: Run the gates**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`, then `timeout 900 uv run pytest -q > /tmp/8-3-task4.txt 2>&1` in the background, its tail read at the end.
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add tests/bootstrap/
git commit -m "The bootstrap tests' profiles and the recorded corpora write every list under imports in references; the corpora's recorded findings do not move

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Before committing, `git status --short` must list only files under `tests/bootstrap/` (no `.claude/`, no `.json`, no `.tar.xz`).

### Task 5: The spec module's parsing tests write references

**Files:**
- Modify: `tests/modules/spec/application/logic/test_profile_parsing.py`, `test_profile_parsing_substance.py`, `test_profile_parsing_tests.py`, `test_tiers.py`, `test_imports_written.py`, `test_targets_written.py`

**Interfaces:**
- Consumes: Task 1 (`tier_parts`: the respelled tier rows `["parts.ghost"]`, `["parts.service", "parts.service"]` give today's `no part named 'ghost'` and `'service' is listed twice`), Task 3 (its message texts, already in these files).
- Produces: nothing new.

No RED step (a respelling). The fixture `layered()`/`covered()`: `src/<module>/` holds `api`, `service`, `store` (word `module`); `shared/` lies in no repeating folder; `two_folders()` adds `ext/<plugin>/` (`hooks`, `manifest`, word `plugin`). Where a respelled value is printed by the message an assertion expects, the expected text is respelled too (listed below with its value). One test, `test_the_subject_of_a_tier_is_its_parts_in_the_order_of_the_parts` (`test_profile_parsing_tests.py:254`), moves `covered()`'s parts out of `src/<module>/` into a flat tree, where the `module.<part>` entries `layered()` now writes name no folder; there a bare name meant the part outside any folder, so the test writes them `parts.<part>` after the move (the first edit of `test_profile_parsing_tests.py` below). Kept in the old forms on purpose, because their subject is that an old form still parses or is refused as one: in `test_profile_parsing.py` the tests at 205-212 (`bare ... with any`), 214-234 (a bare name across folders), 244-265 (`@any`, bare names read to Targets), every row of the table at 276-308, 399, the `must` rows at 417-427 (message rows; Task 3 already changed the `such as` text of two of them), and the old/new comparison at 454-458; in `test_profile_parsing_tests.py` 298 (a bare name the mirrored instance), 349, 351, 363; in `test_imports_written.py` 99, 100, 112; in `test_targets_written.py` 24-26 and 41-46; every `"is not a target: use <part>, <part>@any, ..."` text (the kernel's refusal of an old form, 8.4).

- [ ] **Step 1: Respell**

**`tests/modules/spec/application/logic/test_profile_parsing.py`**

- Replace the one occurrence of:

```python
"cli/": {"role": "commands and output", "imports": {"may": ["core"], "libraries": ["typer"]}}
```

  with:

```python
"cli/": {"role": "commands and output", "imports": {"may": ["parts.core"], "libraries": ["typer"]}}
```

- Replace the one occurrence of:

```python
{"api/": {"role": "HTTP handlers", "imports": {"may": ["service"]}},
```

  with:

```python
{"api/": {"role": "HTTP handlers", "imports": {"may": ["module.service"]}},
```

- Replace the one occurrence of:

```python
                                                                "imports": {"may": ["store", "shared"]}},
```

  with:

```python
                                                                "imports": {"may": ["module.store", "parts.shared"]}},
```

- Replace the one occurrence of:

```python
                                                              "imports": {"may": ["shared"],
```

  with:

```python
                                                              "imports": {"may": ["parts.shared"],
```

- Replace the one occurrence of:

```python
part_of(document, "hooks").setdefault("imports", {})["may"] = ["service@any"]
```

  with:

```python
part_of(document, "hooks").setdefault("imports", {})["may"] = ["parts.service"]
```

- Replace the one occurrence of:

```python
part_of(document, "store").setdefault("imports", {})["must"] = ["shared"]
    part_of(document, "api").setdefault("imports", {})["must"] = ["service"]
```

  with:

```python
part_of(document, "store").setdefault("imports", {})["must"] = ["parts.shared"]
    part_of(document, "api").setdefault("imports", {})["must"] = ["module.service"]
```

- Replace the one occurrence of:

```python
part_of(document, "store").setdefault("imports", {})["must"] = ["api"]
    assert parsed(document).parts["store"].imports_must
```

  with:

```python
part_of(document, "store").setdefault("imports", {})["must"] = ["module.api"]
    assert parsed(document).parts["store"].imports_must
```


**`tests/modules/spec/application/logic/test_profile_parsing_substance.py`**

- Replace the one occurrence of:

```python
imports={"may": [{"store": "types_only"}, "shared"]}
```

  with:

```python
imports={"may": [{"module.store": "types_only"}, "parts.shared"]}
```

- Replace the one occurrence of:

```python
imports={"may": ["store:*Id", "shared/text:Word*"]}
```

  with:

```python
imports={"may": ["module.store:*Id", "parts.shared/text:Word*"]}
```

- Replace the one occurrence of:

```python
pytest.param("store:", "'store:' has an empty
```

  with:

```python
pytest.param("module.store:", "'module.store:' has an empty
```

- Replace the one occurrence of:

```python
pytest.param("store:a b", "'store:a b' has a name pattern that is not one: write it with no space, `@`, `/` or "
                              "`:`
```

  with:

```python
pytest.param("module.store:a b", "'module.store:a b' has a name pattern that is not one: write it with no space, "
                                     "`@`, `/` or `:`
```

- Replace the one occurrence of:

```python
imports={"may": ["store:*Id"], "must": ["store:*Id"]}
```

  with:

```python
imports={"may": ["module.store:*Id"], "must": ["module.store:*Id"]}
```

- Replace the one occurrence of:

```python
parts.service.imports.must: 'store:*Id' has a name pattern
```

  with:

```python
parts.service.imports.must: 'module.store:*Id' has a name pattern
```

- Replace the one occurrence of:

```python
["imports"] = {"must": ["api", "store"]}
```

  with:

```python
["imports"] = {"must": ["parts.api", "parts.store"]}
```

- Replace the one occurrence of:

```python
["imports"] = {"must": ["ghost"]}
```

  with:

```python
["imports"] = {"must": ["parts.ghost"]}
```


**`tests/modules/spec/application/logic/test_profile_parsing_tests.py`**

- Replace the one occurrence of:

```python
    document["parts"] = {f"{name}/": part_of(document, name) for name in ("store", "shared", "service", "api")}
    assert [t.subject for t in parsed(document).tiers]
```

  with:

```python
    document["parts"] = {f"{name}/": part_of(document, name) for name in ("store", "shared", "service", "api")}
    part_of(document, "api")["imports"]["may"] = ["parts.service"]
    part_of(document, "service")["imports"]["may"] = ["parts.store", "parts.shared"]
    part_of(document, "store")["imports"]["may"] = ["parts.shared"]
    assert [t.subject for t in parsed(document).tiers]
```

- Replace the one occurrence of:

```python
{"types_only": ["service", "store"]}
```

  with:

```python
{"types_only": ["parts.service", "parts.store"]}
```

- Replace the one occurrence of:

```python
"imports": {"may": ["shared", "api@any"]}}
```

  with:

```python
"imports": {"may": ["parts.shared", "parts.api"]}}
```

- Replace the one occurrence of:

```python
{"imports": {"types_only": ["repo"]}}
```

  with:

```python
{"imports": {"types_only": ["parts.repo"]}}
```

- Replace the one occurrence of:

```python
{"imports": {"may": ["shared"]}}, "layered.yaml: tiers.unit.imports.may: only
```

  with:

```python
{"imports": {"may": ["parts.shared"]}}, "layered.yaml: tiers.unit.imports.may: only
```

- Replace the one occurrence of:

```python
{"imports": {"also": ["shared", "everything"]}}
```

  with:

```python
{"imports": {"also": ["parts.shared", "everything"]}}
```


**`tests/modules/spec/application/logic/test_tiers.py`**

- Replace the one occurrence of:

```python
pytest.param(["repo", "service"], 
```

  with:

```python
pytest.param(["parts.repo", "parts.service"], 
```

- Replace the one occurrence of:

```python
pytest.param(["service", "service"],
```

  with:

```python
pytest.param(["parts.service", "parts.service"],
```

- Replace the one occurrence of:

```python
with_guard({"may": ["shared", "api@any"]})
```

  with:

```python
with_guard({"may": ["parts.shared", "parts.api"]})
```

- Replace the one occurrence of:

```python
{"also": ["service", "shared"], "must": ["api", "store"],
```

  with:

```python
{"also": ["module.service", "parts.shared"], "must": ["parts.api", "parts.store"],
```

- Replace the one occurrence of:

```python
"types_only": ["service", "store"]}
```

  with:

```python
"types_only": ["parts.service", "parts.store"]}
```

- Replace the one occurrence of:

```python
with_imports({"types_only": ["store", "service"], "must": ["store", "api"]})
```

  with:

```python
with_imports({"types_only": ["parts.store", "parts.service"], "must": ["parts.store", "parts.api"]})
```

- Replace the one occurrence of:

```python
with_imports({"must": ["store", "api"], "types_only": ["store", "service"]})
```

  with:

```python
with_imports({"must": ["parts.store", "parts.api"], "types_only": ["parts.store", "parts.service"]})
```

- Replace the one occurrence of:

```python
with_imports({"must": ["ghost"]})
```

  with:

```python
with_imports({"must": ["parts.ghost"]})
```

- Replace the one occurrence of:

```python
with_imports({"may": ["shared"]})
```

  with:

```python
with_imports({"may": ["parts.shared"]})
```

- Replace the one occurrence of:

```python
with_guard({"may": ["shared"], "also": ["store@any"]})
```

  with:

```python
with_guard({"may": ["parts.shared"], "also": ["parts.store"]})
```

- Replace the one occurrence of:

```python
{"also": ["shared", "everything"]}
```

  with:

```python
{"also": ["parts.shared", "everything"]}
```

- Replace the one occurrence of:

```python
{"also": [{"store": "types_only"}]}, "tiers.integration.imports.also: {'store': 'types_only'} is not "
```

  with:

```python
{"also": [{"parts.store": "types_only"}]}, "tiers.integration.imports.also: {'parts.store': 'types_only'} is not "
```

- Replace the one occurrence of:

```python
{"must": ["nowhere"]}
```

  with:

```python
{"must": ["parts.nowhere"]}
```

- Replace the one occurrence of:

```python
{"must": ["store", "store"]}
```

  with:

```python
{"must": ["parts.store", "parts.store"]}
```

- Replace the one occurrence of:

```python
with_guard({"may": [{"store": "types_only"}]})) == [
        "layered.yaml: tiers.guard.imports.may: {'store': 'types_only'} is not a target
```

  with:

```python
with_guard({"may": [{"parts.store": "types_only"}]})) == [
        "layered.yaml: tiers.guard.imports.may: {'parts.store': 'types_only'} is not a target
```


**`tests/modules/spec/application/logic/test_imports_written.py`**

- Replace the one occurrence of:

```python
{"may": ["shared"], "must": ["shared"], "libraries": ["sqlmodel"]}
```

  with:

```python
{"may": ["parts.shared"], "must": ["parts.shared"], "libraries": ["sqlmodel"]}
```

- Replace the one occurrence of:

```python
{"may": ["store", {"shared": "types_only"}]}
```

  with:

```python
{"may": ["module.store", {"parts.shared": "types_only"}]}
```

- Replace the one occurrence of:

```python
pytest.param({"store": "types_only"}, 
```

  with:

```python
pytest.param({"module.store": "types_only"}, 
```

- Replace the one occurrence of:

```python
pytest.param({"store@any": "types_only"}, 
```

  with:

```python
pytest.param({"parts.store": "types_only"}, 
```

- Replace the one occurrence of:

```python
pytest.param({"store/rules:*Id": "types_only"}, 
```

  with:

```python
pytest.param({"module.store/rules:*Id": "types_only"}, 
```

- Replace the one occurrence of:

```python
[{"store": "types_only"}, "api", {"shared": "types_only"}]
```

  with:

```python
[{"module.store": "types_only"}, "module.api", {"parts.shared": "types_only"}]
```

- Replace the one occurrence of:

```python
["shared", {"shared": "types_only"}]
```

  with:

```python
["parts.shared", {"parts.shared": "types_only"}]
```

- Replace the one occurrence of:

```python
pytest.param({"store": "types"}, "{store: types}: no mode
```

  with:

```python
pytest.param({"module.store": "types"}, "{module.store: types}: no mode
```

- Replace the one occurrence of:

```python
pytest.param({"store": True}, "{store: true}: no mode
```

  with:

```python
pytest.param({"module.store": True}, "{module.store: true}: no mode
```

- Replace the one occurrence of:

```python
{"store": "types_only", "shared": "types_only"},
```

  with:

```python
{"module.store": "types_only", "parts.shared": "types_only"},
```

- Replace the one occurrence of:

```python
"{store: types_only, shared: types_only}: one reference
```

  with:

```python
"{module.store: types_only, parts.shared: types_only}: one reference
```

- Replace the one occurrence of:

```python
pytest.param([{"shared": "types_only"}], "{shared: types_only}: must takes
```

  with:

```python
pytest.param([{"parts.shared": "types_only"}], "{parts.shared: types_only}: must takes
```

- Replace the one occurrence of:

```python
{"may": ["shared"], "must": must}
```

  with:

```python
{"may": ["parts.shared"], "must": must}
```

- Replace the one occurrence of:

```python
{"may": [{"shared": "types_only"}], "must": ["shared"]}
```

  with:

```python
{"may": [{"parts.shared": "types_only"}], "must": ["parts.shared"]}
```

- Replace the one occurrence of:

```python
with_imports("store", {"must": ["shared"]})
```

  with:

```python
with_imports("store", {"must": ["parts.shared"]})
```

- Replace the one occurrence of:

```python
parts.store.imports.must: 'shared' is not in imports.may
```

  with:

```python
parts.store.imports.must: 'parts.shared' is not in imports.may
```

- Replace the one occurrence of:

```python
{"may": ["shared"], "libraries": ["json"]}
```

  with:

```python
{"may": ["parts.shared"], "libraries": ["json"]}
```


**`tests/modules/spec/application/logic/test_targets_written.py`**

- Replace the one occurrence of:

```python
written(["shared:*Id"], patterns=True)
```

  with:

```python
written(["parts.shared:*Id"], patterns=True)
```

- Replace the one occurrence of:

```python
written(["shared:*Id"])[1] == ["parts.api.imports.may: 'shared:*Id' has
```

  with:

```python
written(["parts.shared:*Id"])[1] == ["parts.api.imports.may: 'parts.shared:*Id' has
```

- Replace the one occurrence of:

```python
allowed_targets([{"shared": "types_only"}], 
```

  with:

```python
allowed_targets([{"parts.shared": "types_only"}], 
```

- Replace the one occurrence of:

```python
"tiers.guard.imports.may: {'shared': 'types_only'} is not a target
```

  with:

```python
"tiers.guard.imports.may: {'parts.shared': 'types_only'} is not a target
```

- [ ] **Step 2: Run them (T9)**

Run: `timeout 600 uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_targets_written.py -q`
Expected: PASS.

- [ ] **Step 3: Run the gates**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`, then `timeout 900 uv run pytest -q > /tmp/8-3-task5.txt 2>&1` in the background, its tail read at the end.
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_targets_written.py
git commit -m "The spec module's parsing tests write every list under imports in references, but where an old form is what they prove

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6: The spec module's other tests and builders write references

**Files:**
- Modify: `tests/modules/spec/profiles.py`, `tests/modules/spec/application/builders.py`, `tests/modules/spec/application/origins.py`, `tests/modules/spec/application/test_origin.py`, `tests/modules/spec/application/test_profile_loading.py`
- Modify: `tests/modules/spec/application/logic/test_checked_tier.py`, `test_docs_template.py`, `test_example_imports.py`, `test_looseness.py`, `test_profile_needs.py`, `test_written_checks.py`
- Modify: `tests/modules/spec/adapters/test_yaml_profile_format.py`

**Interfaces:**
- Consumes: Task 1: the looser lines of a tier's `must`/`types_only` print part names (`the unit tests may now call store`, `... by reaching store`), because `tier_parts` reads `parts.store` to `"store"`; those expected texts do not change.
- Produces: nothing new.

No RED step (a respelling). `tests/modules/spec/application/origins.py` and `builders.py` (and the profiles of `test_origin.py`, `test_looseness.py` built on `origins.PARTS`) have no repeating folder: every entry is `parts.<part>`. `profiles.py`, `test_docs_template.py`, `test_example_imports.py`, `test_checked_tier.py`, `test_profile_needs.py` and the `layered()`-based tests of `test_looseness.py` use `src/<module>/` (word `module`) and `ext/<plugin>/` (word `plugin`). Two helpers change with their data: `test_docs_template.py`'s `test_the_instance_is_named_by_the_word_in_the_paths_not_by_xarch` renames the folder word to `<feature>`, so its `service` must say `feature.store` (and it copies `PARTS` with `deepcopy` before writing into it); `test_looseness.py`'s `as_routes`, which renames the part `api` to `routes`, renames `module.api`/`parts.api` too, and `reaching` writes `parts.<part>`. Kept on purpose: `tests/modules/spec/application/test_select.py:30` (it proves the refusal of `api@mine` and `nowhere`), `tests/modules/spec/application/logic/test_explain.py:53` (a template, not a profile), `tests/modules/rules/application/test_rule.py:26,35` (an example text echoed, never parsed), `tests/modules/rules/application/logic/test_own_checks.py:42` (it proves a check's `place` still reads the old forms; 48-53 is its reference twin), `tests/modules/rules/application/logic/test_places.py` and `tests/kernel/logic/test_targets.py` (values and the 8.1 rows, no profile text).

- [ ] **Step 1: Respell**

**`tests/modules/spec/profiles.py`**

- Replace the one occurrence of:

```python
"api/": {"role": "HTTP handlers", "imports": {"may": ["service"]}},
```

  with:

```python
"api/": {"role": "HTTP handlers", "imports": {"may": ["module.service"]}},
```

- Replace the one occurrence of:

```python
"service/": {"role": "business logic", "imports": {"may": ["store", "shared"]}},
```

  with:

```python
"service/": {"role": "business logic", "imports": {"may": ["module.store", "parts.shared"]}},
```

- Replace the one occurrence of:

```python
"store/": {"role": "database access", "imports": {"may": ["shared"], "libraries": ["sqlmodel"]}},
```

  with:

```python
"store/": {"role": "database access", "imports": {"may": ["parts.shared"], "libraries": ["sqlmodel"]}},
```

- Replace the one occurrence of:

```python
"imports": {"may": ["hooks"]}}}
```

  with:

```python
"imports": {"may": ["plugin.hooks"]}}}
```


**`tests/modules/spec/application/builders.py`**

- Replace the one occurrence of:

```python
"api/": {"role": "the handlers", "imports": {"may": ["core"]}}},
```

  with:

```python
"api/": {"role": "the handlers", "imports": {"may": ["parts.core"]}}},
```


**`tests/modules/spec/application/origins.py`**

- Replace the one occurrence of:

```python
"imports": {"types_only": ["store"]}}
```

  with:

```python
"imports": {"types_only": ["parts.store"]}}
```

- Replace the one occurrence of:

```python
"store/": {"role": "storage", "imports": {"may": ["core"], "libraries": ["sqlmodel"]},
```

  with:

```python
"store/": {"role": "storage", "imports": {"may": ["parts.core"], "libraries": ["sqlmodel"]},
```


**`tests/modules/spec/application/test_origin.py`**

- Replace the one occurrence of:

```python
"imports": {"may": ["store"], "libraries": ["yaml"]}}
```

  with:

```python
"imports": {"may": ["parts.store"], "libraries": ["yaml"]}}
```

- Replace the one occurrence of:

```python
"imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
```

  with:

```python
"imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
```

- Replace the one occurrence of:

```python
"imports": {"also": ["edge"]}}}
```

  with:

```python
"imports": {"also": ["parts.edge"]}}}
```

- Replace the one occurrence of:

```python
part("store", imports={"may": ["core"], "libraries": "everything"})
```

  with:

```python
part("store", imports={"may": ["parts.core"], "libraries": "everything"})
```

- Replace every one of the 3 occurrences of:

```python
held(["core", "edge"], ["core"])
```

  with:

```python
held(["parts.core", "parts.edge"], ["parts.core"])
```

- Replace the one occurrence of:

```python
held(["core"])
```

  with:

```python
held(["parts.core"])
```

- Replace the one occurrence of:

```python
held(["core", "edge"], ["core", "edge"])
```

  with:

```python
held(["parts.core", "parts.edge"], ["parts.core", "parts.edge"])
```


**`tests/modules/spec/application/test_profile_loading.py`**

- Replace the one occurrence of:

```python
"imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}},
```

  with:

```python
"imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}},
```


**`tests/modules/spec/application/logic/test_checked_tier.py`**

- Replace the one occurrence of:

```python
{"also": ["service", "shared"]}
```

  with:

```python
{"also": ["module.service", "parts.shared"]}
```


**`tests/modules/spec/application/logic/test_docs_template.py`**

- Replace the one occurrence of:

```python
"imports": {"may": ["shared/text"]}, "sql/": "the queries"},
```

  with:

```python
"imports": {"may": ["parts.shared/text"]}, "sql/": "the queries"},
```

- Replace the one occurrence of:

```python
"imports": {"may": ["store", "api@any", "shared"]}},
```

  with:

```python
"imports": {"may": ["module.store", "parts.api", "parts.shared"]}},
```

- Replace the one occurrence of:

```python
parts(store={"imports": {"may": ["store@any"]}})
```

  with:

```python
parts(store={"imports": {"may": ["parts.store"]}})
```

- Replace the one occurrence of:

```python
parts(service={"imports": {"may": ["store", "api", "shared", "store@any",
                                                                                    "api@any"]}}))
```

  with:

```python
parts(service={"imports": {"may": ["module.store", "module.api", "parts.shared",
                                                                                    "parts.store", "parts.api"]}}))
```

- Replace the one occurrence of:

```python
    feature = {key.replace("<module>", "<feature>"): value for key, value in PARTS.items()}
```

  with:

```python
    feature = {key.replace("<module>", "<feature>"): value for key, value in deepcopy(PARTS).items()}
    feature["src/<feature>/"]["service/"]["imports"]["may"] = ["feature.store", "parts.api", "parts.shared"]
```

- Replace the one occurrence of:

```python
"imports": {"may": ["hooks@any", "shared"]}}},
```

  with:

```python
"imports": {"may": ["parts.hooks", "parts.shared"]}}},
```

- Replace the one occurrence of:

```python
"imports": {"may": ["service@any", "manifest", "shared"], "libraries": ["yaml"]}},
```

  with:

```python
"imports": {"may": ["parts.service", "plugin.manifest", "parts.shared"], "libraries": ["yaml"]}},
```


**`tests/modules/spec/application/logic/test_example_imports.py`**

- Replace the one occurrence of:

```python
"imports": {"may": ["sql", "shared/text"]},
```

  with:

```python
"imports": {"may": ["module.sql", "parts.shared/text"]},
```

- Replace the one occurrence of:

```python
"imports": {"may": ["store", "api@any"]}},
```

  with:

```python
"imports": {"may": ["module.store", "parts.api"]}},
```

- Replace the one occurrence of:

```python
    """Imports outside the app are ignored; api@any reaches another module's api; a module of shared is reached by
    name (shared/text);
```

  with:

```python
    """Imports outside the app are ignored; parts.api reaches another module's api; a module of shared is reached by
    name (parts.shared/text);
```

- Replace the one occurrence of:

```python
    """store@own reaches billing's store, not tax's; shared/text reaches only that path of shared;
```

  with:

```python
    """module.store reaches billing's store, not tax's; parts.shared/text reaches only that path of shared;
```


**`tests/modules/spec/application/logic/test_looseness.py`**

- Replace the one occurrence of:

```python
pytest.param(["service"], "module.service",
```

  with:

```python
pytest.param(["module.service"], "module.service",
```

- Replace the one occurrence of:

```python
pytest.param(["store@any/sql"], "parts.store/sql",
```

  with:

```python
pytest.param(["parts.store/sql"], "parts.store/sql",
```

- Replace the one occurrence of:

```python
pytest.param(["shared/text"], "parts.shared/text",
```

  with:

```python
pytest.param(["parts.shared/text"], "parts.shared/text",
```

- Replace the one occurrence of:

```python
pytest.param(["api@any"], "parts.api",
```

  with:

```python
pytest.param(["parts.api"], "parts.api",
```

- Replace the one occurrence of:

```python
pytest.param(["hooks"], "plugin.hooks",
```

  with:

```python
pytest.param(["plugin.hooks"], "plugin.hooks",
```

- Replace the one occurrence of:

```python
pytest.param(["hooks@any"], "parts.hooks",
```

  with:

```python
pytest.param(["parts.hooks"], "parts.hooks",
```

- Replace the one occurrence of:

```python
pytest.param("shared/text", id="a folder below
```

  with:

```python
pytest.param("parts.shared/text", id="a folder below
```

- Replace the one occurrence of:

```python
pytest.param("shared:*Text", id=
```

  with:

```python
pytest.param("parts.shared:*Text", id=
```

- Replace the one occurrence of:

```python
pytest.param("store/sql:Sql*", id=
```

  with:

```python
pytest.param("module.store/sql:Sql*", id=
```

- Replace the one occurrence of:

```python
{"may": ["store", "shared", target]}
```

  with:

```python
{"may": ["module.store", "parts.shared", target]}
```

- Replace the one occurrence of:

```python
"imports": {"may": ["store"], "libraries": ["yaml"]}}
```

  with:

```python
"imports": {"may": ["parts.store"], "libraries": ["yaml"]}}
```

- Replace the one occurrence of:

```python
"imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
```

  with:

```python
"imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
```

- Replace every one of the 2 occurrences of:

```python
"imports": {"also": ["edge"]}}}
```

  with:

```python
"imports": {"also": ["parts.edge"]}}}
```

- Replace the one occurrence of:

```python
pytest.param([], ["shared/text", "store@any"], (
```

  with:

```python
pytest.param([], ["parts.shared/text", "parts.store"], (
```

- Replace the one occurrence of:

```python
pytest.param(["shared", "store"], ["shared/text", "store"], (),
```

  with:

```python
pytest.param(["parts.shared", "module.store"], ["parts.shared/text", "module.store"], (),
```

- Replace the one occurrence of:

```python
pytest.param(["shared"], [], (), id="a target dropped
```

  with:

```python
pytest.param(["parts.shared"], [], (), id="a target dropped
```

- Replace the one occurrence of:

```python
"imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}},
```

  with:

```python
"imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}},
```

- Replace the one occurrence of:

```python
"core/": {**PARTS["core/"], "imports": {"may": ["store"]}}},
```

  with:

```python
"core/": {**PARTS["core/"], "imports": {"may": ["parts.store"]}}},
```

- Replace the one occurrence of:

```python
        (parsed(BASE), parsed({**BASE, "parts": part("store", imports={"may": ["core"], "must": ["core"], "libraries": ["sqlmodel"]})})),
```

  with:

```python
        (parsed(BASE), parsed({**BASE, "parts": part("store", imports={"may": ["parts.core"], "must": ["parts.core"],
                                                                       "libraries": ["sqlmodel"]})})),
```

- Replace the one occurrence of:

```python
parsed(marked(["store", "shared"])), parsed(marked(["store", {"shared": "types_only"}]))
```

  with:

```python
parsed(marked(["module.store", "parts.shared"])), parsed(marked(["module.store", {"parts.shared": "types_only"}]))
```

- Replace the one occurrence of:

```python
pytest.param(["store", {"shared": "types_only"}], ["store", "shared"],
```

  with:

```python
pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store", "parts.shared"],
```

- Replace the one occurrence of:

```python
pytest.param([{"store": "types_only"}, "shared"], ["store", "shared"],
```

  with:

```python
pytest.param([{"module.store": "types_only"}, "parts.shared"], ["module.store", "parts.shared"],
```

- Replace the one occurrence of:

```python
pytest.param(["store", {"shared": "types_only"}], ["store"], [],
```

  with:

```python
pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store"], [],
```

- Replace the one occurrence of:

```python
    pytest.param(["store", {"shared": "types_only"}], ["store", {"shared": "types_only"}], [], id="the mark kept"),
```

  with:

```python
    pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store", {"parts.shared": "types_only"}], [],
                 id="the mark kept"),
```

- Replace the one occurrence of:

```python
pytest.param(["store", {"shared/x": "types_only"}], ["store", {"shared": "types_only"}], [],
```

  with:

```python
pytest.param(["module.store", {"parts.shared/x": "types_only"}], ["module.store", {"parts.shared": "types_only"}], [],
```

- Replace the one occurrence of:

```python
pytest.param(["store", {"shared": "types_only"}], "everything",
```

  with:

```python
pytest.param(["module.store", {"parts.shared": "types_only"}], "everything",
```

- Replace the one occurrence of:

```python
parsed(marked([{"store": "types_only"}, "shared"]))
```

  with:

```python
parsed(marked([{"module.store": "types_only"}, "parts.shared"]))
```

- Replace the one occurrence of:

```python
                               "imports": {"may": ["shared"]}}
```

  with:

```python
                               "imports": {"may": ["parts.shared"]}}
```

- Replace the one occurrence of:

```python
part_of(custom, "routes")["imports"] = {"may": ["service", "store"]}
```

  with:

```python
part_of(custom, "routes")["imports"] = {"may": ["module.service", "module.store"]}
```

- Replace the one occurrence of:

```python
part_of(base, "service")["imports"] = {"may": ["store", "shared", "api"]}
```

  with:

```python
part_of(base, "service")["imports"] = {"may": ["module.store", "parts.shared", "module.api"]}
```

- Replace the one occurrence of:

```python
part_of(custom, "service")["imports"] = {"may": ["store", "shared", "routes"]}
```

  with:

```python
part_of(custom, "service")["imports"] = {"may": ["module.store", "parts.shared", "module.routes"]}
```

- Replace the one occurrence of:

```python
def as_routes(value):
    """value with every "api" in it, as a key or an entry, read as "routes": the folder api/ named routes in place."""
    if isinstance(value, dict):
        read = {("routes" if key == "api" else key): as_routes(entry) for key, entry in value.items()}
        return read | {"api/": {**read["api/"], "name": "routes"}} if "api/" in read else read
    if isinstance(value, list):
        return [as_routes(entry) for entry in value]
    return "routes" if value == "api" else value
```

  with:

```python
def as_routes(value):
    """value with every "api" in it, as a key or an entry, bare or after a reference's prefix, read as "routes": the
    folder api/ named routes in place."""
    if isinstance(value, dict):
        read = {_routed(key): as_routes(entry) for key, entry in value.items()}
        return read | {"api/": {**read["api/"], "name": "routes"}} if "api/" in read else read
    if isinstance(value, list):
        return [as_routes(entry) for entry in value]
    return _routed(value)


def _routed(value):
    """"api" as "routes", and a reference to api (module.api, parts.api) as one to routes."""
    if not isinstance(value, str):
        return value
    prefix, dot, rest = value.partition(".")
    return "routes" if value == "api" else f"{prefix}.routes" if dot and rest == "api" else value
```

- Replace the one occurrence of:

```python
["imports"] = {"must": list(parts)}
```

  with:

```python
["imports"] = {"must": [f"parts.{name}" for name in parts]}
```

- Replace the one occurrence of:

```python
"imports": {"must": ["service"]}}
```

  with:

```python
"imports": {"must": ["parts.service"]}}
```

- Replace the one occurrence of:

```python
imports={"may": ["service"], "libraries": ["fastapi"]}
```

  with:

```python
imports={"may": ["module.service"], "libraries": ["fastapi"]}
```

- Replace the one occurrence of:

```python
imports={"may": ["store", "shared", "api"], "must": ["api"]}
```

  with:

```python
imports={"may": ["module.store", "parts.shared", "module.api"], "must": ["module.api"]}
```

- Replace every one of the 2 occurrences of:

```python
marked(["store", {"api": "types_only"}])
```

  with:

```python
marked(["module.store", {"module.api": "types_only"}])
```

- Replace the one occurrence of:

```python
as_routes(marked(["store", "api"]))
```

  with:

```python
as_routes(marked(["module.store", "module.api"]))
```

- Replace the one occurrence of:

```python
"imports": {"types_only": ["store"], **imports}
```

  with:

```python
"imports": {"types_only": ["parts.store"], **imports}
```

- Replace the one occurrence of:

```python
tiered(must=["core", "store"])
```

  with:

```python
tiered(must=["parts.core", "parts.store"])
```

- Replace every one of the 5 occurrences of:

```python
tiered(must=["core"])
```

  with:

```python
tiered(must=["parts.core"])
```


**`tests/modules/spec/application/logic/test_profile_needs.py`**

- Replace the one occurrence of:

```python
document["tiers"]["unit"]["imports"] = {"must": ["service"]}
```

  with:

```python
document["tiers"]["unit"]["imports"] = {"must": ["parts.service"]}
```

- Replace the one occurrence of:

```python
    assert parsed(services(imports={"may": ["store", "shared"], "libraries": ["sqlmodel"]}), languages=LANGUAGES).approximate == ()
```

  with:

```python
    assert parsed(services(imports={"may": ["module.store", "parts.shared"], "libraries": ["sqlmodel"]}),
                  languages=LANGUAGES).approximate == ()
```

- Replace the one occurrence of:

```python
tiered(imports={"must": ["service"], "types_only": ["store"]})
```

  with:

```python
tiered(imports={"must": ["parts.service"], "types_only": ["parts.store"]})
```

- Replace the one occurrence of:

```python
pytest.param({"imports": {"may": ["store"], "must": ["store"]}}, 
```

  with:

```python
pytest.param({"imports": {"may": ["module.store"], "must": ["module.store"]}}, 
```

- Replace the one occurrence of:

```python
services(imports={"may": ["store", {"shared": "types_only"}]})
```

  with:

```python
services(imports={"may": ["module.store", {"parts.shared": "types_only"}]})
```

- Replace the one occurrence of:

```python
pytest.param(["store", "shared"], id="no mark"),
```

  with:

```python
pytest.param(["module.store", "parts.shared"], id="no mark"),
```

- Replace the one occurrence of:

```python
pytest.param(["store", {"shared": "types"}], id="a mode refused"),
```

  with:

```python
pytest.param(["module.store", {"parts.shared": "types"}], id="a mode refused"),
```

- Replace the one occurrence of:

```python
part_of(document, "store")["imports"]["must"] = ["shared"]
```

  with:

```python
part_of(document, "store")["imports"]["must"] = ["parts.shared"]
```


**`tests/modules/spec/adapters/test_yaml_profile_format.py`**

- Replace the one occurrence of:

```python
WrittenTarget("place", ("core", "api@any/v1"))
```

  with:

```python
WrittenTarget("place", ("parts.core", "parts.api/v1"))
```

- Replace the one occurrence of:

```python
"  targets: [{place: [core, api@any/v1]}, outside]"
```

  with:

```python
"  targets: [{place: [parts.core, parts.api/v1]}, outside]"
```

- Replace the one occurrence of:

```python
"imports": {"may": ["x"]},
```

  with:

```python
"imports": {"may": ["parts.x"]},
```

- Replace the one occurrence of:

```python
    imports:\n      may: [x]\n
```

  with:

```python
    imports:\n      may: [parts.x]\n
```


**`tests/modules/spec/application/logic/test_written_checks.py`**

- Replace the one occurrence of:

```python
"must_reach": {"targets": [{"place": ["shared"]}, "outside"],
```

  with:

```python
"must_reach": {"targets": [{"place": ["parts.shared"]}, "outside"],
```

- Replace the one occurrence of:

```python
Quantified("must_reach", (WrittenTarget("place", ("shared",)), WrittenTarget("outside")),
```

  with:

```python
Quantified("must_reach", (WrittenTarget("place", ("parts.shared",)), WrittenTarget("outside")),
```

- [ ] **Step 2: Run them (T9)**

Run: `timeout 600 uv run pytest tests/modules/spec -q`
Expected: PASS.

- [ ] **Step 3: Run the gates**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`, then `timeout 900 uv run pytest -q > /tmp/8-3-task6.txt 2>&1` in the background, its tail read at the end.
Expected: all pass. Then confirm no list under `imports` in `tests/` is left in an old form but the kept ones: `grep -rn "@any" tests --include=*.py | grep -v tests/kernel/logic/test_targets.py` prints only lines of `test_select.py:64`, `test_explain.py` (`"@any" not in`), `test_tiers.py`/`test_imports_written.py`/`test_targets_written.py`/`test_profile_parsing*.py` rows listed as kept in Task 5, `tests/modules/rules/application/logic/test_places.py` test ids, and the `"@any" not in` assertions of `tests/bootstrap/`.

- [ ] **Step 4: Commit**

```bash
git add tests/modules/spec/
git commit -m "The spec module's builders and remaining tests write every list under imports in references; as_routes and the feature-word test follow the references

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7: The golden docs are regenerated and read

**Files:**
- Regenerate (never edit by hand): `docs/cli/*.md`, `docs/web/*.md`, `docs/xarch/*.md`

**Interfaces:**
- Consumes: Tasks 2 and 3 (the profiles and the format text the docs are generated from).
- Produces: nothing; expected no diff (note 5.3).

- [ ] **Step 1: Regenerate through the docs path of `tests/bootstrap/test_docs_templates.py`**

```bash
uv run python - <<'PY'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for name, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(Path("architecture.yaml").resolve()))):
    for file in spec.docs(profile).files:
        Path("docs", name, *file.path).write_text(file.template, encoding="utf-8")
PY
git status --short docs/
```

Expected: `git status --short docs/` prints nothing: no golden doc moved.

- [ ] **Step 2: Read the diff, if any**

If a doc moved, run `git diff docs/` and read it. A move is accepted only where a line prints a respelled target and nothing else; then commit it, describing every moved line in the message:

```bash
git add docs/cli docs/web docs/xarch
git commit -m "The golden docs regenerate with <the lines that moved and why>; no golden doc was edited by hand

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Any other move (a rule, a table row, a tree line that says something new) means a profile changed what it allows: stop, run `git checkout docs/`, and report the diff with the commit that caused it. With no diff, there is nothing to commit.

- [ ] **Step 3: Final gates on the branch**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml | diff /tmp/8-3-profile-check-before.txt - && echo same`, then `timeout 900 uv run pytest -q > /tmp/8-3-final.txt 2>&1` in the background, its tail read at the end.
Expected: every gate passes, `same`, and the full suite passes.
<!-- task-pipeline: validated -->
