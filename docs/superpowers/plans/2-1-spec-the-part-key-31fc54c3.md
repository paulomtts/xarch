# 2.1 the part key `tier` renamed to `tests`

Card `31fc54c3`, subtask of `9caa480b`. Release step 2 of the 0.3.0 merged order. Stacked on step 1 (card `f77f7f12`,
the table of retired names, shipped empty: `RETIRED = ()` at `xarch/modules/spec/domain/profile_keys.py:154`).

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`.

- `key-names-design.md` line 18, ruling 3: "The part key `tier` becomes `tests`. `untested` stays."
- The same note, line 52: "a key that names a list or a tier keeps a bare name: ... `tests: unit`."
- The same note, section 1.5, lines 197-214: only the key that says "this part is tested by" changes; everything that
  names a tier as a thing keeps `tier`. The table there lists what stays: `tiers`, `untested`,
  `guards.scenario-coverage.tier`, `in: {tier: ...}` in checks and evals, the variable `{tier}`, the filters `tiered`,
  `target-in-own-tier`, `tier_type_only_fix`, the rule id `tiers`, the `where` text "tested by:", the `where` JSON
  `tier`, `tested_in`, `untested`, the docs placeholders `{{tiers}}`, `{{untested}}`, `{{tier_*}}`, and
  `guards.dead-code.untested`, `tests_only` (their explain texts name the difference from the part keys `untested`
  and `tests`). Line 205: `_TIER_INSTEAD` becomes "`tests: <tier>`, or `untested: <reason>`".
- The same note, section 2, lines 270-272: a person may write a path (`tests: tests/units`); the refusal for a value
  that is no tier name "should add 'it names a tier of `tiers`, not a folder' when the value holds a `/`".
- The same note, section 4, line 345: `parts.domain: unknown key 'tier': renamed in 0.3.0: write tests; use holds,
  imports, ...` (the `use` list is the part keys of the day, not those of the example); lines 355-356: one problem per
  retired key, the joined message after them for keys only unknown; line 363: `profile explain` answers the old key
  with "renamed in 0.3.0: write tests" and the exit code of an unknown key.
- The same note, section 5 item 2, lines 378-381: "Key table and `keys.yaml` together, parser and its messages, the
  three profiles, `stress.yaml`, the two archived profiles (plain yaml since release step 0), test fixtures and 'use
  ...' lists, README, CHANGELOG. Tests first for the refusal of `tier` and for the folder-shaped value. No output
  changes besides the messages, so the recorded findings do not move; that is the check that nothing else did."
  Lines 370-373: the gates.
- The same note, line 393: after the release, `grep -rn 'tier:'` in the profiles returns only
  `guards.scenario-coverage.tier`.
- The same note, "Dodges, named in advance", lines 405, 416, 417, 418-419: no alias, silent or warned; no loosening of
  the "use ..." lists to `"unknown key" in output`; no special case per key inside `_keys`; no renaming of
  `guards.scenario-coverage.tier`, `in.tier` or the `tier` variable "for consistency". Line 422: no hint that echoes
  the value written.
- `0.3.0-cohesion-review-3.md` line 259, row 2 of the merged order, depending on step 1. Line 226 (O2): each step edits
  its own tokens of the "use ..." lists and of the part-key list at `test_profile_parsing.py:164`, no loosening. Line
  227 (O3): table row and `keys.yaml` entry in one commit; `tiered-part` is edited by this step. Lines 228-229 (O4,
  O5): README and CHANGELOG lines under `[Unreleased]`. Line 232 (O8): golden docs regenerated and their diff read.
  Line 233 (O9): `stress.yaml`, the two archived profiles, the three bundled profiles and the parser docstring, each
  step its lines.

## What is there now

- The key table row `Key(PART, "tier", rules=("tiers",))` at `xarch/modules/spec/domain/key_table.py:81`. The row
  `Key(SCENARIO_COVERAGE, "tier", ...)` at `:140` and the scope constant `TIER = "tier"` (`profile_keys.py:16`, the
  scope of a tier's own keys) are other things.
- `keys.yaml` (`xarch/architectures/presets/format/keys.yaml`): the entry `parts.<part>.tier` (lines 428-435), the
  fragment `tiered-part` (25-27, `tier: unit`), the `coverage` fragment's parts (55, 59, `tier: integration`), and
  more examples writing a part's `tier:` (65 at least; every one is found by grep). Prose that names the part key: the
  `tiers` entry (196, "every part names its `tier`"), the entry `parts.<part>.tier` itself (430), and the
  `guards.dead-code` texts (861, 975, "a part that has a `tier`"). Line 900 (`guards.scenario-coverage.tier`) and 1271
  (`in` of an eval refuses `files` and `tier`) are other keys.
- The parser (`xarch/modules/spec/application/logic/profile_parsing.py`): the docstring (lines 25-26,
  `tier: <tier> | untested: <reason>`), `_TIER_INSTEAD` (126), and `_coverage` (558-581), which reads `"tier" in spec`
  and `spec["tier"]` and says:
  - `parts.<p>: has a `tier` and is `untested`: drop one`
  - `parts.<p>.tier: the profile has no `tiers`: add them, or drop the key`
  - `parts.<p>.tier: must be the name of a tier: use <tiers in file order>`
  - `parts.<p>.tier: no tier named '<value>': use <tiers in file order>`
  - `parts.<p>: no tier tests it: give it `tier: <tier>`, or `untested: <reason>``
- A part's unknown keys go through `ck.unknown_keys(spec, names_of(PART), where, PART)` (`profile_parsing.py:276`),
  which already gives one problem per retired name with its fixed text, ahead of the joined message for the rest
  (`profile_checks.py:528-548`). `profile explain` already answers an address of the table with the entry's text, exit
  2, `retired` in its JSON (step 1).
- `tests/modules/spec/application/logic/test_retired_keys.py:85-86`, `test_the_shipped_table_gives_nothing`, asserts
  `retired(PART, "tier") == ""` and `retired_at("parts.tier") == ""`.
- Part-level `tier:` lines: `architecture.yaml` 15, `xarch/architectures/cli.yaml` 11, `xarch/architectures/web.yaml`
  11 (each file also holds one `guards.scenario-coverage.tier`, which stays); `tests/bootstrap/corpora/stress.yaml`,
  `7cc6111.yaml`, `df537ca.yaml` (13, 11, 13 `tier:` lines at any depth; the split between parts and the guard is
  found by reading each).
- Tests that write a part's `tier` or assert one of the messages above or a "use ..." list holding `tier` (the explore
  step's counts; a grep per file when editing finds the rest): `tests/bootstrap/test_repeating_folders.py`,
  `test_profile_file.py`, `test_other_framework.py`, `test_written_rules.py`, `test_tier_folder.py`,
  `test_bundled_tiers.py`, `test_architecture_files.py:213`, `tests/modules/spec/application/origins.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (282-297), `test_key_catalogue.py`,
  `test_needs_agree.py`, `test_written_checks.py`, `test_testing.py`, `test_libraries_and_guards.py`,
  `test_checked_tier.py`, `test_profile_parsing.py:164`, `test_explain.py:65` (`Shown("parts.tier", ...)`),
  `tests/modules/rules/application/logic/test_types_only.py`, `test_retired_keys.py` (`PART_USE`), and the profile
  builders in `tests/modules/spec/profiles.py` and `tests/modules/rules/builders.py`.
- README: the key summary line 117 (`tier | untested`), the rule table line 272 (`parts.tier`). Line 528 (the `where`
  JSON field `tier`) and 475-477 (prose, "the tier that tests it") are not the key.
- CHANGELOG `[Unreleased]`, "Changed", lines 13-16: "...; no name is retired yet."

## Required behavior

### 1. The key `tests`

1. A part's key that names the tier whose tests cover it is `tests`. It accepts what `tier` accepted, and nothing
   else: the name of one tier of `tiers`. A profile that wrote `tier: unit` and now writes `tests: unit` loads into
   the same `Architecture`, and every report, finding, `where` answer (text and JSON), generated doc and review reads
   it as before.
2. The internal field (`Part.tier`, `Read.tier`, the `where` JSON field `tier`, the contract fields) keeps its name.
   Every name listed as staying in `key-names-design.md` 1.5 (lines 204-214) stays, `guards.scenario-coverage.tier`
   and `in: {tier: ...}` above all.
3. The rule the key feeds is still `tiers`. `xarch profile explain parts.tests` (also typed `parts.<part>.tests`)
   explains the key: meaning "the tier whose tests cover the part", accepts "the name of a tier; one tier per part;
   with `tiers`, a part names the tier that `tests` it or is `untested`" (the wording may differ; it names `tests`, and
   no text of the format names a part's `tier` as a key), and an example built from the fragment `tiered-part`, which
   writes `tests: unit`.
4. The messages of `_coverage` name the new key, word for word:
   - `parts.<p>: has `tests` and is `untested`: drop one`
   - `parts.<p>.tests: the profile has no `tiers`: add them, or drop the key`
   - `parts.<p>.tests: must be the name of a tier: use <tiers in file order>`
   - `parts.<p>.tests: no tier named '<value>': use <tiers in file order>`
   - `parts.<p>: no tier tests it: give it `tests: <tier>`, or `untested: <reason>``

   `parts.<p>.untested: must be one line of text: why no tier tests the part` is unchanged: it is prose about tiers.

### 2. The value shaped as a folder

1. When the value of `tests` is a string that is no tier name and holds a `/`, the problem is
   `parts.<p>.tests: no tier named '<value>': it names a tier of `tiers`, not a folder: use <tiers in file order>`.
   Example: `tests: tests/units` with tiers `unit, integration` gives
   `parts.api.tests: no tier named 'tests/units': it names a tier of `tiers`, not a folder: use unit, integration`.
2. A value with no `/` that is no tier name (`tests: tests`, `tests: units`) gets the plain message of 1.4. A value
   that is a tier name is accepted, whatever it holds. A value that is not a string gets "must be the name of a tier"
   as before. Only `/` triggers the clause; a `\` does not.
3. One problem per part, never two: the clause is part of the "no tier named" problem, not a problem of its own.

### 3. The old key `tier` is refused

1. `RETIRED` holds exactly one entry: `Retired(PART, "tier", "renamed in 0.3.0: write tests")`. Nothing else is added
   to the table, and no code anywhere tests for the name `tier` of a part (no `if key == "tier"`): the refusal comes
   from the table through the readers step 1 built.
2. A part writing `tier: <anything>` does not load. Its problem is
   `parts.<p>: unknown key 'tier': renamed in 0.3.0: write tests; use <every part key, sorted, `tests` among them>`.
   The value written is never shown. Exit codes are those of any profile that does not load.
3. A part writing `tier` and another unknown key (`tierr`) gives two problems, the retired one first, then the joined
   `parts.<p>: unknown key 'tierr': use ...` unchanged.
4. A part writing `tier` and neither `tests` nor `untested`, in a profile with `tiers`, also gets
   `parts.<p>: no tier tests it: give it `tests: <tier>`, or `untested: <reason>``, as a part with any unknown key does
   today. That is the existing behavior of an unknown key, kept; it is not suppressed for `tier`.
5. A part writing both `tier` and `tests` is refused for `tier` alone; its `tests` is read as written.
6. `tier` is not accepted anywhere as an alias, with or without a warning.
7. `tier` under any other scope is unchanged: `guards.scenario-coverage.tier` is a known key, `in: {tier: ...}` a known
   slot; a key `tier` under a tier (`tiers.unit.tier`) is only unknown, with the plain message, since the entry is
   under `PART` only.
8. `xarch profile explain parts.tier` (and `parts.<part>.tier`) answers with "renamed in 0.3.0: write tests" before
   the nearest keys, exit 2, `retired: "renamed in 0.3.0: write tests"` in its JSON. `profile explain
   guards.scenario-coverage.tier` explains that key as before.

### 4. The profiles and corpora

1. Every part-level `tier:` line in `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`,
   `tests/bootstrap/corpora/stress.yaml`, `7cc6111.yaml` and `df537ca.yaml` reads `tests:` with the same value. The
   `guards.scenario-coverage.tier` line of each stays. Prose in those files that names the part key in backticks names
   `tests`. After the edit, `grep -n 'tier:'` in each file returns only `guards.scenario-coverage.tier` lines.
2. The corpora are edited by hand. The `.tar.xz` archives and the recorded findings (`7cc6111.json`, `df537ca.json`,
   `examples-*.json`, `stress-7cc6111.json.xz`) are not touched, and `test_recorded_corpora.py` passes against them
   unchanged: that is the proof that nothing but the messages moved.
3. `xarch profile check architecture.yaml`, `xarch check` and `xarch check --strict` give the same output as on the
   parent branch.

### 5. Generated docs

The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated from the edited profiles and their diff read. The
expected diff is none: no placeholder renders the key's name. Any line that moves is reported, not hand-edited; a
line that moves for a reason other than this rename is a bug of this step.

### 6. README and CHANGELOG

1. README: the key summary (line 117) reads `tests | untested`; the rule table's `tiers` row (272) names
   `parts.tests`. Nothing else in README changes in this step (`where` JSON `tier` at 528 stays, as does prose about
   "the tier that tests it").
2. CHANGELOG, under `[Unreleased]`, "Changed": a new entry saying the part key `tier` is renamed `tests` (`tests:
   <tier>` or `untested: <reason>`), a profile still writing `tier` on a part is refused with "renamed in 0.3.0: write
   tests", which `xarch profile explain parts.tier` also gives, and a value of `tests` holding a `/` is told it names
   a tier, not a folder; nothing else a profile writes or xarch reports changes. The step-1 entry's closing clause
   "no name is retired yet" is dropped, since one now is (the entry otherwise unchanged).

## Error paths, together

| Input on a part | Problems (in order) |
|---|---|
| `tier: unit` (tiers exist) | `unknown key 'tier': renamed in 0.3.0: write tests; use ...`, then `no tier tests it: give it `tests: <tier>`, or `untested: <reason>`` |
| `tier: unit`, `tests: unit` | the retired one only |
| `tier: unit`, `tierr: 1`, `tests: unit` | the retired one, then `unknown key 'tierr': use ...` |
| `tests: tests/units` | `.tests: no tier named 'tests/units': it names a tier of `tiers`, not a folder: use unit, integration` |
| `tests: units` | `.tests: no tier named 'units': use unit, integration` |
| `tests: 3` | `.tests: must be the name of a tier: use unit, integration` |
| `tests: unit`, `untested: why` | `has `tests` and is `untested`: drop one` |
| `tests: unit`, no `tiers` | `.tests: the profile has no `tiers`: add them, or drop the key` |
| neither, tiers exist | `no tier tests it: give it `tests: <tier>`, or `untested: <reason>`` |

Each line is prefixed with `parts.<p>` as shown in section 1.4.

## Tests that prove it

Tiers follow `docs/xarch/testing.md`: `tests/modules/spec/application/logic/` is the unit tier of the spec module's
logic (pure parsing of a document, no files), `tests/bootstrap/` the tier that loads real profile files and runs the
CLI and the recorded corpora.

Written first, failing on the parent branch:

1. `test_retired_keys.py` (unit: the table and its lookup are pure logic). `test_the_shipped_table_gives_nothing` is
   replaced by a test that the shipped table holds the one entry: `retired(PART, "tier")`, `retired_at("parts.tier")`
   and `retired_at("parts.<part>.tier")` all give "renamed in 0.3.0: write tests"; `retired(TIER, "tier")`,
   `retired(SCENARIO_COVERAGE, "tier")` and `retired(PART, "tests")` give "". `PART_USE` names `tests` in place of
   `tier`, in place.
2. Unit, in `test_profile_parsing_tests.py` (it holds the coverage messages): a part writing `tier: unit` is refused
   with the exact problems of the table's first row; with `tests: unit` beside it, the retired problem alone; with
   `tierr` too, the two problems in order; the value written (`tier: secret-value`) appears in no problem.
3. Unit, same file: the folder-shaped value, parametrized over `tests/units` (clause), `a/b` (clause), `units` (no
   clause), `tests` (no clause), and a tier named `a/b` with `tests: a/b`, which is accepted (a tier name is any one
   line of text, so it may hold `/`; the clause fires only for a value that is no tier name). Each case asserts the
   whole problem list.
4. Unit, same file: each message of section 1.4 names `tests`, by editing the assertions at 282-297 in place.
5. Unit, `tests/modules/spec/application/logic/test_explain.py`: `Shown("parts.tier", ...)` becomes `parts.tests`
   with the new texts; a new case that `parts.tier` is retired with the fixed text.
6. Bootstrap (the CLI's exit code and JSON need a process): `tests/bootstrap/test_profile_explain.py`: `xarch profile
   explain parts.tier` exits 2 and prints "renamed in 0.3.0: write tests"; with `--json`, `retired` holds the text;
   `profile explain parts.tests` exits 0; `profile explain guards.scenario-coverage.tier` exits 0 as before.
7. Bootstrap, `test_profile_file.py` or `test_architecture_files.py` (a real file on disk): a profile file writing
   `tier:` on a part does not load, with the retired problem in the output, word for word.

Edited in place (fixtures and assertions; none loosened to `"unknown key" in output`):

8. Unit: every test fixture and builder that writes a part's `"tier"` / `tier:` writes `tests`; every "use ..." list
   of part keys names `tests` where it named `tier`, at the same position (both sort between `shared` and
   `types_only`); `test_profile_parsing.py:164`'s part-key list; `test_key_catalogue.py` (table and `keys.yaml`
   agree, one commit with them).
9. Bootstrap: `test_architecture_files.py:213` reads `give it `tests: <tier>``; the bundled-profile tests
   (`test_bundled_tiers.py` and the rest) load the edited profiles; `test_recorded_corpora.py` passes with the
   recordings untouched; `test_docs_templates.py` passes against the regenerated golden docs.
10. A test that writes `guards.scenario-coverage.tier`, `in: {tier: ...}`, a tier's `tier` variable or the `where` JSON
    `tier` is not edited.

## Out of scope

- Every other rename of the release: `forbidden` to `uses: {never: ...}`, the block `never`, `apply_forbidden`, the
  rule ids `forbidden` and `rules` (steps 3 and 4); the `imports` groups (steps 13, 14); internal identifiers
  (step 5). The README key summary's `forbidden` and the `tiers` line (120) are left for those steps.
- `untested` on a part and `guards.dead-code.untested`, `tests_only`: unchanged.
- `guards.scenario-coverage.tier`, `in.tier`, the variable `{tier}`, the filters, the rule id `tiers`, the `where`
  label "tested by:" and JSON field `tier`, the internal field `Part.tier`: unchanged (dodge, line 418).
- `docs/examples/`, `xarch/architectures/examples`, the `.tar.xz` archives and every recorded findings file.
- The docstring example of `key_lookup.retired_at` (`key_lookup.py:44`, "parts.tier and parts.<part>.tier"), which
  stays accurate: it is now a real entry's address.
- Ordering the CHANGELOG under a 0.3.0 lead and reading the README block whole (step 25).

## Gates

On this branch alone, each passing: `uv run pytest -q` (in the background, over two minutes, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

## Project rules for the planner

No comments in xarch's code (docstrings are fine); tests written first; examples simple, with absolute `app.` imports;
corpora edited by hand only; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; the key table row and the `keys.yaml` entry in one commit; golden docs regenerated,
never hand-edited; `.claude/` stays out of commits; nothing is pushed.

## Review focus (for the planner)

1. A part-level `tier:` line missed in a profile or corpus, or a `guards.scenario-coverage.tier` line renamed by a
   blind replace: section 4.1's grep after the edit, and the recorded findings test, catch both.
2. A `keys.yaml` example or fragment still writing a part's `tier:` (each example is loaded by the catalogue test,
   which would now refuse it); prose in `keys.yaml` that names a part's `tier` as a key.
3. The folder clause appearing with a value that is a tier name, or as a second problem.
4. An old profile written with `tier` getting its value echoed in a message.
5. A "use ..." list edited by reordering rather than replacing the token, or loosened.

---

# 2.1 The part key `tier` renamed to `tests` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A part names the tier that covers it with `tests: <tier>`; the old part key `tier` is refused through the
table of retired names with "renamed in 0.3.0: write tests"; a folder-shaped value of `tests` is told it names a tier,
not a folder.

**Architecture:** The key table row `Key(PART, "tier", ...)` becomes `Key(PART, "tests", ...)` and its `keys.yaml`
entry moves with it in the same commit; `_coverage` in the parser reads `spec["tests"]` and its messages name `tests`;
every profile, corpus and test fixture that writes a part's `tier:` writes `tests:`. Then the shipped table of retired
names gets its one entry, which the readers step 1 built already turn into the refusal and the `profile explain`
answer. Nothing else in the code names the old key.

**Tech Stack:** Python 3.13, pytest, typer (CLI), PyYAML; run everything through `uv run`.

**Spec:** `docs/superpowers/specs/2-1-spec-the-part-key-31fc54c3.md` (copied above this line).

## Global Constraints

- The retired entry, exactly: `Retired(PART, "tier", "renamed in 0.3.0: write tests")`; nothing else is added to
  `RETIRED`.
- No code tests for the name `tier` of a part (no `if key == "tier"`, no alias, no warning).
- The messages of `_coverage`, word for word:
  - `parts.<p>: has `tests` and is `untested`: drop one`
  - `parts.<p>.tests: the profile has no `tiers`: add them, or drop the key`
  - `parts.<p>.tests: must be the name of a tier: use <tiers in file order>`
  - `parts.<p>.tests: no tier named '<value>': use <tiers in file order>`
  - `parts.<p>.tests: no tier named '<value>': it names a tier of `tiers`, not a folder: use <tiers in file order>`
    (only for a string holding `/` that is no tier name)
  - `parts.<p>: no tier tests it: give it `tests: <tier>`, or `untested: <reason>``
- Stays named `tier`: `guards.scenario-coverage.tier`, `in: {tier: ...}` of checks and evals, the `{tier}` variable,
  the filters `tiered`/`target-in-own-tier`, the rule id `tiers`, the `where` JSON field `tier`, `Part.tier`,
  `Read.tier`, the scope constant `TIER`, `guards.dead-code.untested`/`tests_only`.
- No comments in xarch's code (docstrings are fine). Tests first. `ruff check` is never run with `--fix`.
- Corpora are edited by hand; `.tar.xz` archives and recorded findings (`7cc6111.json`, `df537ca.json`,
  `examples-*.json`, `stress-7cc6111.json.xz`) are not touched.
- The key table row and the `keys.yaml` entry change in one commit.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never hand-edited.
- `.claude/` stays out of commits; nothing is pushed. `docs/superpowers/` (spec and plan) is not added by the
  engineer's commits.
- Never `pkill`/`killall`; stop a test run only by the PID you recorded, or wrap it in `timeout`.
- Every commit message ends with the line `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A part writing `tier` in a profile with no `tiers`: one problem, the retired one, and no coverage problem (there is
   nothing to cover). Test: Task 2, `test_a_part_writing_tier_in_a_profile_with_no_tiers_gets_the_retired_problem_alone`.
2. A value of `tests` that is no string (`null`, a list): "must be the name of a tier", never the folder clause, never
   a crash on `"/" in value`. Test: Task 3, `test_a_value_of_tests_that_is_no_string_must_be_the_name_of_a_tier`.
3. A tier name with a trailing slash (`tests: unit/`) gets the clause; a backslash (`tests\units`) does not. Test:
   Task 3, the `unit/` and backslash cases of `test_a_value_of_tests_that_is_no_tier_name`.
4. The key `tier` under a tier (`tiers.unit.tier`) is only unknown, with the plain message: the entry is under `PART`
   alone. Test: Task 2, `test_tier_under_a_tier_is_only_unknown_with_the_plain_message`.
5. The `guards.scenario-coverage.tier` line of a profile renamed by a blind replace (the profile would then miss
   `tier` for the guard and not load). Test: Task 1 Step 10's grep, the bundled-profile tests and
   `test_recorded_corpora.py`; and Task 2's `profile explain guards.scenario-coverage.tier` bootstrap test.

---

## File map

- `xarch/modules/spec/domain/key_table.py:81` — the part row, `"tier"` to `"tests"`.
- `xarch/architectures/presets/format/keys.yaml` — the entry `parts.<part>.tier` to `parts.<part>.tests`, the
  fragments `tiered-part` and `coverage`, the `may_also_import` example, prose at 196, 430, 861, 975.
- `xarch/modules/spec/application/logic/profile_parsing.py` — docstring 26, `_TIER_INSTEAD` 126, `_coverage` 558-581.
- `xarch/modules/spec/domain/profile_keys.py:154` — `RETIRED` gets its entry (Task 2).
- Profiles/corpora: `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`,
  `tests/bootstrap/corpora/stress.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`.
- Tests and builders (listed per step below).
- `README.md` 117, 272; `CHANGELOG.md` `[Unreleased]`.

---

### Task 1: The part key is `tests`

Everything that writes or reads a part's key changes together: the key table row and its `keys.yaml` entry, the
parser, the six profile files and every test fixture. A partial state does not load the bundled profiles, so this is
one task.

**Files:**
- Modify: `xarch/modules/spec/domain/key_table.py:81`
- Modify: `xarch/architectures/presets/format/keys.yaml` (lines 25-27, 55, 59, 196, 428-430, 557, 561, 861, 975)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (26, 126, 564-575)
- Modify: `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`,
  `tests/bootstrap/corpora/stress.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`
- Test (assertions): `tests/modules/spec/application/logic/test_profile_parsing_tests.py:275-297`,
  `tests/modules/spec/application/logic/test_profile_parsing.py:164-165`,
  `tests/modules/spec/application/logic/test_retired_keys.py:44-45`,
  `tests/modules/spec/application/test_explain.py:65` and a new test at the end,
  `tests/bootstrap/test_architecture_files.py:213`
- Test (fixtures): `tests/modules/spec/profiles.py:59`, `tests/modules/spec/application/origins.py:5,7`,
  `tests/modules/spec/application/logic/test_checked_tier.py:17`,
  `tests/modules/spec/application/logic/test_looseness.py:164`, `tests/modules/spec/application/logic/test_tiers.py:168`,
  `tests/modules/spec/application/logic/test_key_catalogue.py:56,59,78`, `tests/bootstrap/test_bundled_tiers.py:38,42`,
  `tests/bootstrap/test_needs_agree.py:30,36`, `tests/bootstrap/test_repeating_folders.py:17,23,29,36,43,49`,
  `tests/bootstrap/test_profile_file.py:24,30,38,39`, `tests/bootstrap/test_other_framework.py:16,21,22`,
  `tests/bootstrap/test_written_rules.py:109`, `tests/bootstrap/test_tier_folder.py:14`

**Interfaces:**
- Consumes: `key_lookup.names_of(PART)` (sorted known part keys), `ck.unknown_keys` (unchanged).
- Produces: the part key `tests` in `names_of(PART)`, sorting between `shared` and `types_only`; the address
  `parts.tests` / `parts.<part>.tests` in the catalogue; `_coverage` reading `spec["tests"]`. `Part.tier` and every
  internal name stay. After this task the part key `tier` is only unknown (plain message); Task 2 adds the retired
  hint.

- [ ] **Step 1: Record the baselines**

```bash
mkdir -p /tmp/xarch-2-1
uv run xarch check > /tmp/xarch-2-1/check.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/check.txt
uv run xarch check --strict > /tmp/xarch-2-1/strict.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/strict.txt
uv run xarch profile check architecture.yaml > /tmp/xarch-2-1/profile-check.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/profile-check.txt
timeout 1200 uv run pytest -q > /tmp/xarch-2-1/baseline-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-1/baseline-pytest.pid
```

Expected: the three files written. The pytest run takes over two minutes; carry on and read
`tail -5 /tmp/xarch-2-1/baseline-pytest.txt` once the PID in `baseline-pytest.pid` has exited (`kill -0 $(cat
/tmp/xarch-2-1/baseline-pytest.pid)` fails). Expected: all passed. Note the count.

- [ ] **Step 2: Write the failing tests: the coverage messages name `tests`**

In `tests/modules/spec/profiles.py`, `covered()` writes `tests` (line 59):

```python
    for name, tier in (("api", "integration"), ("service", "unit"), ("store", "integration")):
        document["parts"][name]["tests"] = tier
```

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, replace the three tests at lines 275-297 with:

```python
def test_a_part_names_its_tier_or_says_why_it_has_none_when_the_profile_has_tiers():
    document = covered()
    document["parts"]["shared"].pop("untested")
    document["parts"]["store"].pop("tests")
    document["parts"]["api"]["untested"] = "no need"
    document["parts"]["service"]["tests"] = "nope"
    assert problems(document) == [
        "layered.yaml: parts.api: has `tests` and is `untested`: drop one",
        "layered.yaml: parts.service.tests: no tier named 'nope': use unit, integration",
        "layered.yaml: parts.store: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`",
        "layered.yaml: parts.shared: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"]


def test_a_part_naming_a_tier_in_a_profile_with_no_tiers_is_refused():
    document = layered()
    document["parts"]["api"]["tests"] = "unit"
    assert problems(document) == [
        "layered.yaml: parts.api.tests: the profile has no `tiers`: add them, or drop the key"]


def test_a_part_that_is_not_a_text_for_its_tier_is_refused():
    document = covered()
    document["parts"]["api"]["tests"] = 3
    assert problems(document) == ["layered.yaml: parts.api.tests: must be the name of a tier: use unit, integration"]
```

In `tests/modules/spec/application/logic/test_profile_parsing.py`, lines 164-165, the "an unknown key" case's list
replaces the token `tier` by `tests` in place:

```python
                 ["layered.yaml: parts.x: unknown key 'colour': use built_by, folders, forbidden, holds, immutable, libraries, litmus, "
                  "may_import, must_import, names, no_callbacks, package_only, path, role, shared, tests, types_only, untested"],
```

In `tests/modules/spec/application/logic/test_retired_keys.py`, lines 44-45:

```python
PART_USE = ("built_by, folders, forbidden, holds, immutable, libraries, litmus, may_import, must_import, names, "
            "no_callbacks, package_only, path, role, shared, tests, types_only, untested")
```

In `tests/modules/spec/application/test_explain.py`, line 65:

```python
    Shown('parts.tests', 1, 'the tier whose tests cover the part', False, True),
```

and at the end of the file:

```python
def test_the_part_key_of_the_tier_that_covers_it_is_tests_and_its_example_writes_it():
    spec, _ = spec_controller(**BUNDLED)
    found = spec.explain(Explain("parts.<part>.tests"))
    assert isinstance(found, KeyExplained)
    assert (found.key, found.name, found.meaning, found.rules) == (
        "parts.tests", "tests", "the tier whose tests cover the part", ("tiers",))
    assert "`tests`" in found.accepts and "`tier`" not in found.accepts
    assert found.example.endswith("    role: the documents\n    tests: unit\n") and "tier:" not in found.example
```

In `tests/bootstrap/test_architecture_files.py`, line 213:

```python
                 ["parts.a: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`",
```

- [ ] **Step 3: Run the new assertions to see them fail**

Run:
```bash
uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/test_explain.py tests/bootstrap/test_architecture_files.py -x -q 2>&1 | tail -15
```
Expected: FAIL. The first failure is an `unknown key 'tests'` problem (the format has no part key `tests` yet), or
a message that still says `tier`.

- [ ] **Step 4: Rename the key table row and its `keys.yaml` entry**

`xarch/modules/spec/domain/key_table.py:81`:

```python
    Key(PART, "tests", rules=("tiers",)),
```

(Line 140, `Key(SCENARIO_COVERAGE, "tier", ...)`, is not touched.)

`xarch/architectures/presets/format/keys.yaml`:

Lines 25-27, the fragment `tiered-part`:

```yaml
  tiered-part: |
    <<part>>
        tests: unit
```

Lines 51-59, the parts of the fragment `coverage` (line 65, `tier: integration` under `guards: scenario-coverage:` in
the fragment `coverage-guard`, stays as it is):

```yaml
    parts:
      documents:
        path: units/<unit>/documents
        role: the documents
        tests: integration
      results:
        path: units/<unit>/results
        role: the result unions
        tests: integration
```

Line 196, the `tiers` entry's accepts, first line:

```yaml
      a map {<tier>: {...}}; with tiers, every part names the tier that `tests` it or says why it is `untested`; needs `testing`.
```

Lines 428-430, the entry:

```yaml
  parts.<part>.tests:
    meaning: the tier whose tests cover the part
    accepts: the name of a tier; one tier per part; with `tiers`, a part names the tier that `tests` it or is `untested`
```

(its `example:` lines 431-435 stay: they use `<<tiered-part>>`).

Lines 552-561, the parts of the `tiers.<tier>.may_also_import` example:

```yaml
      parts:
        core:
          path: core
          role: the rules of the documents
          tests: unit
        documents:
          path: documents
          role: the documents
          tests: unit
```

Line 861 (in `guards.dead-code`'s accepts), replace `every file of a part that has a `tier`` with
`every file of a part whose `tests` names a tier`, so the lines read:

```yaml
      not count; names are compared by their last step. With `untested: true`, every file of a part whose `tests` names a tier
      that no test of that tier reaches is also listed as `weak`, failing `check --strict` only (see
```

Line 975 (in `guards.dead-code.untested`'s accepts):

```yaml
      true or false: every file of a part whose `tests` names a tier, which no test code of that tier (a file below the tests
```

Check the file:

```bash
grep -nE '^\s+tier: |`tier`|parts\.<part>\.tier' xarch/architectures/presets/format/keys.yaml
```

Expected: exactly two lines (line numbers as today, since no edit adds or drops a line):
`65:        tier: integration` (the guard in the fragment `coverage-guard`) and `1271:` (the `in` of an eval refuses
`files` and `tier`, which is the slot `in.tier`). Both stay. Lines 783 (`tier: <tier>` in the scenario-coverage
accepts) and 900 (`guards.scenario-coverage.tier:`) are other keys too; the pattern does not match them. Before the
edit the same grep prints twelve lines (27, 55, 59, 65, 196, 428, 430, 557, 561, 861, 975, 1271).

- [ ] **Step 5: The parser reads `tests`**

`xarch/modules/spec/application/logic/profile_parsing.py`, docstring lines 26-27:

```python
        tests: <tier> | untested: <reason>
                               one tier covers the part, or the reason none does; with `tiers`, one of the two
```

Line 126:

```python
_TIER_INSTEAD = "`tests: <tier>`, or `untested: <reason>`"
```

`_coverage` (lines 558-581) becomes:

```python
def _coverage(specs: dict[str, Any], parts: dict[str, Part], names: list[str] | None, has_tiers: bool,
              problems: list[str]) -> dict[str, str]:
    """The tier each part names, by part; a part that fits neither way is reported."""
    assigned: dict[str, str] = {}
    for name in parts:
        spec, where = specs[name], f"parts.{name}"
        named, untested = "tests" in spec, "untested" in spec
        if named and untested:
            problems.append(f"{where}: has `tests` and is `untested`: drop one")
        if named and not has_tiers:
            problems.append(f"{where}.tests: the profile has no `tiers`: add them, or drop the key")
        elif named and names is not None:
            tier = spec["tests"]
            use = f"use {', '.join(names)}"
            if not isinstance(tier, str):
                problems.append(f"{where}.tests: must be the name of a tier: {use}")
            elif tier not in names:
                problems.append(f"{where}.tests: no tier named {tier!r}: {use}")
            else:
                assigned[name] = tier
        elif not named and not untested and names is not None:
            problems.append(f"{where}: no tier tests it: give it {_TIER_INSTEAD}")
    return assigned
```

(Lines 739 and 746, `spec["tier"]` of `guards.scenario-coverage`, stay.)

- [ ] **Step 6: Run the Step 2 tests**

Run:
```bash
uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/test_explain.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_keys.py 2>&1 | tail -15
```
Expected: PASS (`test_profile_keys.py` loads every `keys.yaml` example and checks it uses its key).
`tests/bootstrap/test_architecture_files.py` may still fail until Step 9, since the bundled profiles still write
`tier`.

- [ ] **Step 7: The unit-tier fixtures write `tests`**

Each edit replaces the part key `"tier"` / `tier:` by `"tests"` / `tests:` with the same value, nothing else.

`tests/modules/spec/application/origins.py` lines 5-7:

```python
PARTS = {"core": {"path": "core", "role": "rules", "may_import": [], "forbidden": "pure", "tests": "unit"},
         "store": {"path": "store", "role": "storage", "may_import": ["core"], "libraries": ["sqlmodel"],
                   "tests": "unit"},
```

`tests/modules/spec/application/logic/test_checked_tier.py:17`:

```python
    document["parts"]["shared"] = {"path": "shared", "role": "shared code", "tests": "unit"}
```

`tests/modules/spec/application/logic/test_looseness.py:164`:

```python
    store = {key: value for key, value in PARTS["store"].items() if key != "tests"}
```

`tests/modules/spec/application/logic/test_tiers.py:168`:

```python
    document["parts"]["shared"]["tests"] = "integration"
```

`tests/modules/spec/application/logic/test_key_catalogue.py` lines 56 and 59 (a fragment of the test's own, kept in
step with the shipped `tiered-part`):

```python
    fragments = FRAGMENTS | {"tiered": "<<part>>\n    tests: unit\n"}
```
```python
    assert catalogue.texts[ROLE].example == "tiers:\n  unit: {}\n" + FRAGMENTS["part"] + "    tests: unit\n"
```

and line 78, the `"c"` fragment of the cycle case:

```python
    pytest.param(document(fragments={"a": "<<b>>\n", "b": "<<a>>\n", "c": "tests: unit"}),
```

Then search for any part-level `tier` left in the unit tests:

```bash
git grep -nE "\[\"tier\"\]|\"tier\": \"|'tier'" -- tests/modules
```

Expected: only lines that are `guards.scenario-coverage`'s `tier` (`SCENARIOS = {"results": "api", "tier": ...` in
`test_testing.py:13`, `test_libraries_and_guards.py:13`, `test_profile_parsing_tests.py:340`, `466-467`), `in:
{"part": "web", "tier": "unit"}` in `test_written_checks.py:91`, or `test_where.py`'s `here.tier`. None of those is
edited.

- [ ] **Step 8: The bootstrap fixtures write `tests`**

`tests/bootstrap/test_bundled_tiers.py` lines 38 and 42: `    tier: driver` becomes `    tests: driver`, `    tier: unit`
becomes `    tests: unit`.

`tests/bootstrap/test_needs_agree.py` lines 30 and 36: `    tier: unit` becomes `    tests: unit` (both).

`tests/bootstrap/test_repeating_folders.py`:
- line 17: `  kernel: {path: kernel, role: shared primitives, litmus: "Is it a primitive?", tests: unit}`
- lines 23, 36, 49: `    tests: unit`
- lines 29, 43: `    tests: integration`

`tests/bootstrap/test_profile_file.py`:
- lines 24, 30: `    tests: unit`
- lines 38-39:
  ```
    results: {path: modules/<module>/results, role: the results, tests: unit}
    ports: {path: modules/<module>/ports, role: the ports, tests: unit}
  ```
- line 45 (`scenario-coverage: {results: results, tier: unit, ...}`) stays.

`tests/bootstrap/test_other_framework.py`:
- line 16: `  contract:   {path: modules/<module>/contract, role: results, tests: integration}`
- line 21: `    tests: integration`
- line 22: `  ports:      {path: modules/<module>/application/ports, role: ports, tests: integration}`
- line 29 (`    tier: integration` under `guards: scenario-coverage:`) stays. Read lines 14-32 before editing.

`tests/bootstrap/test_written_rules.py:108-109`:

```python
               "tiers": {"unit": {}}, "parts": {"documents": {"path": "documents", "role": "the documents",
                                                              "tests": "unit"}}, "checks": written}
```

`tests/bootstrap/test_tier_folder.py:14`:

```python
  sub: {{path: sub, role: "the only part", tests: unit}}
```

Then search:

```bash
git grep -nE "^\s+tier: |, tier: |\"tier\": \"" -- tests/bootstrap/*.py
```

Expected: only `scenario-coverage` lines (`test_profile_file.py:45`, `test_other_framework.py:29`).

- [ ] **Step 9: The profiles and the corpora write `tests`**

In each file below, every `    tier: ` line before the `guards:` block is a part's and becomes `    tests: `; the one
`tier:` line under `guards: scenario-coverage:` (the line number given) stays. Edit with a line range ending before
that line:

```bash
sed -i '1,322s/^    tier: /    tests: /' architecture.yaml
sed -i '1,289s/^    tier: /    tests: /' xarch/architectures/cli.yaml
sed -i '1,291s/^    tier: /    tests: /' xarch/architectures/web.yaml
sed -i '1,281s/^    tier: /    tests: /' tests/bootstrap/corpora/stress.yaml
sed -i '1,154s/^    tier: /    tests: /' tests/bootstrap/corpora/7cc6111.yaml
sed -i '1,173s/^    tier: /    tests: /' tests/bootstrap/corpora/df537ca.yaml
```

Before running each, confirm the guard line with `sed -n '<n>p' <file>` reads `    tier: integration` and
`sed -n '<n-3>,<n-1>p' <file>` shows `guards:` / `  scenario-coverage:` / `    results: contract` (architecture.yaml
323, cli.yaml 290, web.yaml 292, stress.yaml 282, 7cc6111.yaml 155, df537ca.yaml 174). If a line number has moved,
use the new one.

- [ ] **Step 10: Check the profiles by grep**

```bash
for f in architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml; do echo "== $f"; grep -n 'tier:' "$f"; grep -c '^    tests: ' "$f"; done
git status --short -- tests/bootstrap/corpora
```

Expected, per file, one `tier:` line (the guard's) and a `tests:` count of: architecture.yaml 14, cli.yaml 10,
web.yaml 10, stress.yaml 12, 7cc6111.yaml 10, df537ca.yaml 12. `git status` shows only the three `.yaml` files under
corpora as modified (no `.json`, `.xz` or `.tar.xz`).

- [ ] **Step 11: Run the whole suite**

```bash
timeout 1200 uv run pytest -q > /tmp/xarch-2-1/task1-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-1/task1-pytest.pid
```

When the PID has exited: `tail -20 /tmp/xarch-2-1/task1-pytest.txt`. Expected: all passed, the same count as the
baseline plus the one test added in Step 2. A failure that writes a part's `tier` is a fixture this task missed:
find it with `grep -n "tier" <file>`, change only a part's key, and rerun. `test_recorded_corpora.py` must pass with
the recordings untouched; if it does not, stop and report the diff it prints, since only messages may move.

- [ ] **Step 12: Lint and commit**

```bash
uv run ruff check
git add xarch/modules/spec/domain/key_table.py xarch/architectures/presets/format/keys.yaml \
  xarch/modules/spec/application/logic/profile_parsing.py architecture.yaml xarch/architectures/cli.yaml \
  xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml \
  tests/bootstrap/corpora/df537ca.yaml tests/
git status --short
git commit -m "$(cat <<'EOF'
A part names the tier that covers it with tests: <tier>, in the key table, its keys.yaml entry and examples, the parser's messages, the three profiles, stress.yaml, the two archived profiles and every test fixture; guards.scenario-coverage.tier, in.tier and the internal names stay

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

Expected: ruff passes. `git status --short` before the commit shows nothing unstaged but the untracked
`docs/superpowers/` spec and plan, which are not added.

---

### Task 2: The old key `tier` is refused through the table of retired names

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py:154`
- Test: `tests/modules/spec/domain/test_profile_keys.py` (docstring, last test)
- Test: `tests/modules/spec/application/logic/test_retired_keys.py:85-86`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (new tests after
  `test_a_part_that_is_not_a_text_for_its_tier_is_refused`)
- Test: `tests/modules/spec/application/test_explain.py` (new test at the end)
- Test: `tests/bootstrap/test_profile_explain.py` (new tests at the end)
- Test: `tests/bootstrap/test_architecture_files.py` (new case in the parametrize list of
  `test_a_bad_file_raises_invalid_architecture_naming_every_problem`)

**Interfaces:**
- Consumes: `Retired(scope: str, name: str, text: str)` and `PART` from `xarch.modules.spec.domain.profile_keys`;
  `key_lookup.retired(scope, name) -> str`, `key_lookup.retired_at(address) -> str` (step 1); `ck.unknown_keys` which
  already gives `<where>: unknown key '<name>': <text>; use <sorted known>` for an entry; `UnknownKey(key, nearest,
  retired)` from `profile explain`.
- Produces: `RETIRED == (Retired(PART, "tier", "renamed in 0.3.0: write tests"),)`.

- [ ] **Step 1: Write the failing table tests**

`tests/modules/spec/domain/test_profile_keys.py`: the module docstring's last clause `at this step it has no entry.`
becomes `it holds the part key tier, renamed tests.`, the import line gains `PART` and `Retired`:

```python
from xarch.modules.spec.domain.profile_keys import HELD, PART, RETIRED, RULE_ID, SCOPES, Retired
```

and `test_no_name_is_retired_yet` is replaced by:

```python
def test_the_one_name_retired_is_the_part_key_tier_renamed_tests():
    assert RETIRED == (Retired(PART, "tier", "renamed in 0.3.0: write tests"),)
```

`tests/modules/spec/application/logic/test_retired_keys.py`: replace `test_the_shipped_table_gives_nothing`
(lines 85-86) by:

```python
def test_the_shipped_table_retires_the_part_key_tier_alone():
    renamed = "renamed in 0.3.0: write tests"
    assert (retired(PART, "tier"), retired_at("parts.tier"), retired_at("parts.<part>.tier")) == (renamed,) * 3
    assert (retired(TIER, "tier"), retired(SCENARIO_COVERAGE, "tier"), retired(PART, "tests")) == ("", "", "")
```

- [ ] **Step 2: Write the failing parsing tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, after
`test_a_part_that_is_not_a_text_for_its_tier_is_refused`, add:

```python
PART_KEYS = ("built_by, folders, forbidden, holds, immutable, libraries, litmus, may_import, must_import, names, "
             "no_callbacks, package_only, path, role, shared, tests, types_only, untested")
RETIRED_TIER = f"unknown key 'tier': renamed in 0.3.0: write tests; use {PART_KEYS}"
NO_TIER = "no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"


def test_a_part_still_writing_tier_is_refused_with_the_rename_and_is_tested_by_no_tier():
    document = covered()
    document["parts"]["store"].pop("tests")
    document["parts"]["store"]["tier"] = "integration"
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}", f"layered.yaml: parts.store: {NO_TIER}"]


def test_a_part_writing_tier_beside_tests_is_refused_for_tier_alone():
    document = covered()
    document["parts"]["store"]["tier"] = "integration"
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}"]


def test_a_part_writing_tier_and_a_key_only_unknown_gets_the_retired_problem_first():
    document = covered()
    document["parts"]["store"]["tier"] = "integration"
    document["parts"]["store"]["tierr"] = 1
    assert problems(document) == [f"layered.yaml: parts.store: {RETIRED_TIER}",
                                  f"layered.yaml: parts.store: unknown key 'tierr': use {PART_KEYS}"]


def test_the_value_written_under_tier_is_in_no_problem():
    document = covered()
    document["parts"]["store"].pop("tests")
    document["parts"]["store"]["tier"] = "secret-value"
    found = problems(document)
    assert found == [f"layered.yaml: parts.store: {RETIRED_TIER}", f"layered.yaml: parts.store: {NO_TIER}"]
    assert not any("secret-value" in problem for problem in found)


def test_a_part_writing_tier_in_a_profile_with_no_tiers_gets_the_retired_problem_alone():
    document = layered()
    document["parts"]["api"]["tier"] = "unit"
    assert problems(document) == [f"layered.yaml: parts.api: {RETIRED_TIER}"]


def test_tier_under_a_tier_is_only_unknown_with_the_plain_message():
    document = covered()
    document["tiers"]["unit"]["tier"] = "x"
    assert problems(document) == [
        "layered.yaml: tiers.unit: unknown key 'tier': use apply_forbidden, docs, folder, litmus, may_also_import, "
        "may_import, must_import, plain_tables, proves, types_only"]
```

- [ ] **Step 3: Write the failing explain tests**

At the end of `tests/modules/spec/application/test_explain.py`:

```python
def test_the_part_key_xarch_renamed_is_refused_with_the_fixed_text_however_it_is_typed():
    spec, _ = spec_controller(**BUNDLED)
    for address in ("parts.tier", "parts.<part>.tier"):
        found = spec.explain(Explain(address))
        assert isinstance(found, UnknownKey)
        assert (found.key, found.retired) == ("parts.tier", "renamed in 0.3.0: write tests")


def test_the_tier_of_scenario_coverage_is_still_a_key_of_the_format():
    spec, _ = spec_controller(**BUNDLED)
    found = spec.explain(Explain("guards.scenario-coverage.tier"))
    assert isinstance(found, KeyExplained) and found.key == "guards.scenario-coverage.tier"
```

At the end of `tests/bootstrap/test_profile_explain.py` (no `retiring`: these read the shipped table):

```python
SHIPPED = "renamed in 0.3.0: write tests"


def test_the_part_key_tier_is_refused_with_the_rename_in_text_and_in_json():
    text = runner.invoke(app, ["profile", "explain", "parts.tier"])
    assert text.exit_code == 2
    assert f"error: no key `parts.tier` in the format: {SHIPPED}; the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.<part>.tier", "--format", "json"])
    assert found.exit_code == 2
    document = json.loads(found.output)
    assert (document["ok"], document["key"], document["retired"]) == (False, "parts.tier", SHIPPED)


def test_the_part_key_tests_and_the_tier_of_scenario_coverage_are_explained():
    tests = runner.invoke(app, ["profile", "explain", "parts.tests"])
    assert (tests.exit_code, tests.output.splitlines()[0]) == (0, "parts.tests")
    guard = runner.invoke(app, ["profile", "explain", "guards.scenario-coverage.tier"])
    assert (guard.exit_code, guard.output.splitlines()[0]) == (0, "guards.scenario-coverage.tier")
    assert SHIPPED not in tests.output + guard.output
```

- [ ] **Step 4: Write the failing file-on-disk test**

In `tests/bootstrap/test_architecture_files.py`, add this case to the parametrize list of
`test_a_bad_file_raises_invalid_architecture_naming_every_problem`, just before the `'two keys that are nowhere'`
case:

```python
    pytest.param('name: n\ntesting: pytest\ntiers: {unit: {}}\nparts: {a: {path: a, role: r, tier: secret-value}}\n',
                 ["parts.a: unknown key 'tier': renamed in 0.3.0: write tests; use built_by, folders, forbidden, "
                  "holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, package_only, "
                  "path, role, shared, tests, types_only, untested",
                  "parts.a: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"],
                 id='a part still writing tier'),
```

- [ ] **Step 5: Run the new tests to see them fail**

```bash
uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_architecture_files.py 2>&1 | tail -20
```

Expected: FAIL for the two table tests (`RETIRED == ()`), the five parsing tests that expect
`renamed in 0.3.0: write tests` (they get the plain `unknown key 'tier': use ...`), the explain refusal tests (`retired`
is `""` / `null`) and the `a part still writing tier` case. Three tests PASS already, since they pin what must not
change: `test_tier_under_a_tier_is_only_unknown_with_the_plain_message`,
`test_the_tier_of_scenario_coverage_is_still_a_key_of_the_format` and
`test_the_part_key_tests_and_the_tier_of_scenario_coverage_are_explained`.

- [ ] **Step 6: Add the entry**

`xarch/modules/spec/domain/profile_keys.py:154-155`:

```python
RETIRED: tuple[Retired, ...] = (Retired(PART, "tier", "renamed in 0.3.0: write tests"),)
"""Every key, guard and rule id xarch has retired: a profile writing one is refused with the entry's text."""
```

(`PART` is defined in the same file at line 15; `Retired` is defined just above `RETIRED`.)

- [ ] **Step 7: Run the tests to see them pass**

Same command as Step 5. Expected: PASS.

Then confirm no code names the old key: `git grep -nE "== \"tier\"|\"tier\" ==|key == 'tier'" -- xarch`
Expected: no output.

- [ ] **Step 8: Run the whole suite and lint**

```bash
uv run ruff check
timeout 1200 uv run pytest -q > /tmp/xarch-2-1/task2-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-1/task2-pytest.pid
```

When the PID has exited, `tail -20 /tmp/xarch-2-1/task2-pytest.txt`: all passed. A failure in a test that writes a
part's `tier` (one Task 1 missed) is fixed by writing `tests`, never by loosening an assertion.

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py tests/modules/spec/domain/test_profile_keys.py \
  tests/modules/spec/application/logic/test_retired_keys.py \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py \
  tests/bootstrap/test_architecture_files.py
git commit -m "$(cat <<'EOF'
The table of retired names holds the part key tier, renamed tests: a part still writing it is refused with renamed in 0.3.0: write tests, never showing its value, and profile explain parts.tier answers the same with exit 2; tier under any other scope is unchanged

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: A folder-shaped value of `tests`

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (`_coverage`, the `elif tier not in names:` branch)
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (new tests after Task 2's)

**Interfaces:**
- Consumes: `_coverage` as Task 1 left it; `covered()`, `parsed()`, `problems()` from `tests.modules.spec.profiles`.
- Produces: the "no tier named" message with the clause `: it names a tier of `tiers`, not a folder` before `: use`,
  for a string holding `/` that is no tier name.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

```python
def test_a_path_written_for_tests_is_told_it_names_a_tier_not_a_folder():
    document = covered()
    document["parts"]["api"]["tests"] = "tests/units"
    assert problems(document) == [
        "layered.yaml: parts.api.tests: no tier named 'tests/units': it names a tier of `tiers`, not a folder: "
        "use unit, integration"]


@pytest.mark.parametrize("value, folder", [
    pytest.param("tests/units", True, id="a folder of the tests"),
    pytest.param("a/b", True, id="any text holding a slash"),
    pytest.param("unit/", True, id="a tier name with a trailing slash"),
    pytest.param("units", False, id="no slash: the plain message"),
    pytest.param("tests", False, id="the tests folder's name, with no slash"),
    pytest.param("tests\\units", False, id="a backslash is no slash"),
])
def test_a_value_of_tests_that_is_no_tier_name(value, folder):
    document = covered()
    document["parts"]["api"]["tests"] = value
    clause = ": it names a tier of `tiers`, not a folder" if folder else ""
    assert problems(document) == [
        f"layered.yaml: parts.api.tests: no tier named {value!r}{clause}: use unit, integration"]


def test_a_tier_whose_name_holds_a_slash_is_named_by_tests_with_no_problem():
    document = covered()
    document["tiers"]["a/b"] = {}
    document["parts"]["api"]["tests"] = "a/b"
    architecture = parsed(document)
    assert [subject.part for tier in architecture.tiers if tier.name == "a/b" for subject in tier.subject] == ["api"]


@pytest.mark.parametrize("value", [
    pytest.param(None, id="null"),
    pytest.param(["tests/units"], id="a list holding a path"),
])
def test_a_value_of_tests_that_is_no_string_must_be_the_name_of_a_tier(value):
    document = covered()
    document["parts"]["api"]["tests"] = value
    assert problems(document) == ["layered.yaml: parts.api.tests: must be the name of a tier: use unit, integration"]
```

- [ ] **Step 2: Run them to see the clause cases fail**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py -k "folder or no_tier_name or slash or no_string" 2>&1 | tail -15`
Expected: FAIL for `test_a_path_written_for_tests_is_told_it_names_a_tier_not_a_folder` and the three `True` cases
(the message has no clause); the other cases PASS already.

- [ ] **Step 3: Add the clause**

In `_coverage` of `xarch/modules/spec/application/logic/profile_parsing.py`, the branch

```python
            elif tier not in names:
                problems.append(f"{where}.tests: no tier named {tier!r}: {use}")
```

becomes

```python
            elif tier not in names:
                folder = ": it names a tier of `tiers`, not a folder" if "/" in tier else ""
                problems.append(f"{where}.tests: no tier named {tier!r}{folder}: {use}")
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py 2>&1 | tail -5`
Expected: PASS.

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check
git add xarch/modules/spec/application/logic/profile_parsing.py \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py
git commit -m "$(cat <<'EOF'
A value of a part's tests that holds a slash and is no tier name is told it names a tier of tiers, not a folder, in the one problem it already gets; a tier name holding a slash is accepted

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: README, CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `README.md:117`, `README.md:272`
- Modify: `CHANGELOG.md` (`## [Unreleased]` / `### Changed`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-2-1/regenerate_docs.py`

**Interfaces:**
- Consumes: everything above. Produces: nothing new in code.

- [ ] **Step 1: README**

`README.md:117`, `tier | untested` becomes `tests | untested`:

```
parts*:   {<part>: {path*, role*, litmus, may_import, must_import, libraries, forbidden, tests | untested,
```

`README.md:272`, the last cell of the `tiers` row, `parts.tier` becomes `parts.tests`:

```
| `tiers` | a test importing what its tier does not allow, or another test file, or a test in no tier | `tiers`, `tiers.folder`, `tiers.may_import`, `tiers.may_also_import`, `parts.tests` |
```

Nothing else in README changes (lines 470, 508, 528 are the `where` output's `tier`, which stays).
Check: `grep -n "parts.tier\|tier | untested" README.md` prints nothing.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, the `[Unreleased]` section becomes (the second bullet loses its closing `; no name is retired yet`,
and a third bullet is added):

```markdown
## [Unreleased]

### Changed

- The two archived corpora's profiles (`7cc6111`, `df537ca`) are plain yaml files beside their archives in
  `tests/bootstrap/corpora/`, so a change of format edits them as files; the recorded findings are unchanged.

- A key, a guard or a rule id that xarch has retired is refused with a fixed hint naming what to write instead, one
  problem per retired name ahead of the keys that are only unknown, read from one table that
  `xarch profile explain <old key>` also answers from (the hint in its error, `retired` in its JSON, `null` for an
  address with no entry).

- The part key `tier` is renamed `tests`: a part writes `tests: <tier>` or `untested: <reason>`. A profile still
  writing `tier` on a part is refused with "renamed in 0.3.0: write tests", which `xarch profile explain parts.tier`
  also gives, and a value of `tests` holding a `/` is told it names a tier of `tiers`, not a folder. Nothing else a
  profile writes or xarch reports changes.
```

- [ ] **Step 3: Regenerate the golden docs and check they did not move**

Create `/tmp/xarch-2-1/regenerate_docs.py` (never committed):

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
uv run python -I /tmp/xarch-2-1/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines and an empty `git diff`. If any line moved, do not hand-edit it: read the diff, restore
with `git checkout -- docs/cli docs/web docs/xarch`, and report the diff (a line that moves for any reason is a bug of
this step to report).

- [ ] **Step 4: Compare the gates' output with the baseline**

```bash
uv run xarch check > /tmp/xarch-2-1/check-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/check-after.txt
uv run xarch check --strict > /tmp/xarch-2-1/strict-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/strict-after.txt
uv run xarch profile check architecture.yaml > /tmp/xarch-2-1/profile-check-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-1/profile-check-after.txt
diff /tmp/xarch-2-1/check.txt /tmp/xarch-2-1/check-after.txt
diff /tmp/xarch-2-1/strict.txt /tmp/xarch-2-1/strict-after.txt
diff /tmp/xarch-2-1/profile-check.txt /tmp/xarch-2-1/profile-check-after.txt
```

Expected: the three runs pass (exit 0) and every `diff` is empty. A line that differs is reported with the diff.

- [ ] **Step 5: The full gates**

```bash
uv run ruff check
timeout 1200 uv run pytest -q > /tmp/xarch-2-1/final-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-1/final-pytest.pid
```

When the PID has exited, `tail -5 /tmp/xarch-2-1/final-pytest.txt`: all passed, more than the baseline of Task 1
Step 1 (Tasks 1-3 add tests), none of the baseline failing. `test_recorded_corpora.py` and `test_docs_templates.py`
among the passed.

Last grep of the spec, section 4.1:
```bash
grep -n 'tier:' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
```
Expected: six lines, each the `tier: integration` of `guards.scenario-coverage`.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
README names the part key tests in its key summary and the tiers row, and the CHANGELOG says the part key tier is renamed tests, refused with renamed in 0.3.0: write tests, and a value holding a slash is told it names a tier, not a folder; the golden docs regenerate unchanged

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

`git status --short` before the commit shows only `README.md` and `CHANGELOG.md` staged (and the untracked spec and
plan under `docs/superpowers/`, which are not added).

---

## Self-review against the spec

- 1.1-1.2 (the key `tests`, same `Architecture`, internal names stay): Task 1 Steps 4-5 and 7-11; the recorded
  corpora and the bundled-profile tests prove nothing else moved; Task 4 Step 4 compares the gates' output.
- 1.3 (`profile explain parts.tests`, meaning, accepts naming `tests`, example `tests: unit`, rule `tiers`): Task 1
  Step 4 (keys.yaml), Step 2 (`test_the_part_key_of_the_tier_that_covers_it_is_tests_and_its_example_writes_it`);
  Task 2 Step 3 bootstrap exit 0.
- 1.4 (messages word for word): Task 1 Steps 2 and 5; `untested` message untouched.
- 2.1-2.3 (folder clause, no clause without `/`, backslash, non-string, tier name with `/`, one problem): Task 3.
- 3.1 (one entry, no `if key == "tier"`): Task 2 Steps 1, 6, 7's grep.
- 3.2-3.5 (refusal, value never shown, with `tierr`, with no `tests`, with both): Task 2 Step 2.
- 3.6 (no alias): the refusal tests (the profile does not load).
- 3.7 (other scopes): Task 2 `test_tier_under_a_tier_is_only_unknown_with_the_plain_message`,
  `test_the_tier_of_scenario_coverage_is_still_a_key_of_the_format`, and `in.tier` tests untouched.
- 3.8 (`profile explain parts.tier`, JSON `retired`, `guards.scenario-coverage.tier` as before): Task 2 Step 3.
- 4.1-4.3 (profiles, corpora, grep, recordings untouched, gates' output): Task 1 Steps 9-11, Task 4 Steps 4-5.
- 5 (golden docs): Task 4 Step 3.
- 6 (README, CHANGELOG): Task 4 Steps 1-2.
- Spec tests 1-10: 1 Task 2 Step 1; 2 Task 2 Step 2; 3 Task 3; 4 Task 1 Step 2; 5 Task 1 Step 2 and Task 2 Step 3;
  6 Task 2 Step 3; 7 Task 2 Step 4; 8 Task 1 Steps 2, 7, 8; 9 Task 1 Steps 2, 8, 11 and Task 4 Steps 3, 5; 10 the
  untouched lines named in Task 1 Steps 7-8.
- Deviation from the spec's "What is there now": it names `keys.yaml` line 65 among the examples writing a part's
  `tier:`; line 65 is the `tier` of `guards.scenario-coverage` in the fragment `coverage-guard`, so it stays (Task 1
  Step 4 says so). `tests/modules/rules/builders.py` and `test_types_only.py` build domain values, not profile
  documents, and write no part key: they are not edited.
<!-- task-pipeline: validated -->
