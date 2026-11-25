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
