# 2.4 Internal identifiers follow the key-names renames

Card `c61068a6`, subtask of `9caa480b`. Release step 5 of the 0.3.0 merged order. Stacked on step 4 (card `ba13344f`,
the rule id `rules` becomes `may-import`, branch tip `c7d6127`). Steps 2.1 to 2.3 changed the format and the output:
the part key `tests`, `uses: {never: <list>}`, the block `never`, `tiers.<t>.uses: {apply_never: true}`, the rule ids
`never-use` and `may-import`, the `where` label `never uses` and JSON field `never_uses`, the `Loosened` keys. This
step renames what is left: the Python identifiers that still say `forbidden`, and the test names that still spell
`may_not_use`. Nothing a user can see changes.

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`. `KN` is `key-names-design.md`, `R3` is
`0.3.0-cohesion-review-3.md`.

- KN line 36, default 11: internal identifiers follow each rename, as the note's last step.
- KN line 43, ruling 15: `review.never` keeps its name beside the top-level `never`.
- KN 1.6, lines 256-264: the identifiers to rename (`Architecture.forbidden`, `Part.forbidden`, `Tier.forbidden`,
  `CheckedTier.forbidden`, `Profile.forbidden`, `InPart.forbidden`, `_forbidden_lists`, `_forbidden_refs`,
  `forbidden_names`, `FORBIDDEN_FIX`, `_forbidden_line`); the field of the named lists cannot be called `never`
  because `Architecture.never` holds `review.never`; the recommended names `never_lists`, `uses_never` (a part's
  field), `apply_never` (a tier's), `never_names`, `NEVER_USE_FIX`, `_never_use_line`; review's fields keep `never`;
  "one word per concept and no field with two meanings"; the Python field `tier` stays everywhere.
- KN 1.6, lines 245-255 ("Stays"): English prose ("anything not listed is forbidden", `cli.md:130`, `web.md:130`,
  `docs/templates/architecture.md:100`), the 0.2.0 CHANGELOG entry, and `docs/examples/` (`profile_values/tiers.py:13`
  writes `apply_forbidden: bool`; `forbidden_imports` in two files): placement examples `review calibrate` reads;
  editing them changes what calibration sends.
- KN 2, lines 280-285: `never` (the block, `uses.never`) against `review.never`, different scopes, kept apart.
- KN 5 item 5, line 388: "Internal identifiers (1.6). Behaviour does not change; the gates prove it." Lines 370-373:
  the gates. Lines 390-395: the re-grep at the end of step 5.
- KN "Dodges", line 411: naming the internal field of the lists `never`, beside `Architecture.never` of review.
- R3 C2, lines 102-109: `Architecture.never`, `ProfileView.never` and the review values hold `review.never`
  (`values.py:366, 401`, `spec/contract/__init__.py:172`, `review/domain/values.py:53`); resolution: the lists' fields
  are `never_lists` and `uses_never`, and review's keep `never`.
- R3 section 2: O4, O5 (lines 228-229: README and CHANGELOG lines under `[Unreleased]`), O8 (line 232: the golden docs
  `docs/{cli,web,xarch}/testing.md` regenerated, diff read; this step expects none).

## What is there now

At `c7d6127`, `grep -rni forbidden xarch` (outside the bundled presets, which hold none) finds these identifiers:

| Where | Identifier | What it holds |
|---|---|---|
| `xarch/modules/spec/domain/values.py:393` (docstring 356) | `Architecture.forbidden` | by part, the names its `uses.never` list bans |
| `xarch/modules/spec/domain/values.py:231` (docstring 208) | `Tier.forbidden` | the tier's `uses.apply_never` switch |
| `xarch/modules/spec/contract/__init__.py:107` | `PartView.forbidden` | a part's banned names |
| `xarch/profile_values/tiers.py:22` (docstring 13: "the forbidden list") | `CheckedTier.forbidden` | the tier switch as the checks read it |
| `xarch/modules/rules/domain/profile.py:90` (docstring 51) | `Profile.forbidden` | by part, the banned names |
| `xarch/modules/rules/domain/places.py:57, 98` | `PartPlace.forbidden`, `SuitePlace.forbidden` | the banned names `where` shows |
| `xarch/modules/rules/contract/__init__.py:188, 227` | `InPart.forbidden`, `InTests.forbidden` | the same, as the contract hands `where_report` |
| `xarch/modules/rules/application/logic/expansion.py:15` | `FORBIDDEN_FIX` | the fix text of rule `never-use` |
| `xarch/modules/rules/application/logic/expansion.py:49` | `_forbidden` | builds the `never-use` rules (book key `"never-use"`, 367) |
| `xarch/modules/spec/domain/key_table.py:192` (used 206, 210) | `_FORBIDDEN` | the reader kinds `uses.never` and `uses.apply_never` need |
| `xarch/modules/spec/application/logic/profile_checks.py:609` (caller `profile_parsing.py:459`) | `forbidden_names` | parses the entries of one list under `never` |
| `xarch/modules/spec/application/logic/profile_parsing.py:447` | `_forbidden_lists` | parses the block `never` |
| `xarch/modules/spec/application/logic/profile_parsing.py:463` | `_forbidden_refs` | resolves each part's `uses.never` |
| `xarch/modules/spec/application/logic/profile_parsing.py:168, 182, 203, 209, 468, 485-486` | locals `lists`, `forbidden` | the parsed block; the resolved map |
| `xarch/modules/spec/application/logic/docs_template.py:450` (called 412-413) | `_forbidden_line` | the generated docs line of `never-use` |

Readers of those fields: `spec_profile.py:85`, `publishing.py:59`, `looseness.py:69-70, 88`, `checked_tier.py:13`,
`where.py:105, 201`, `locate.py:52, 65`, `where_report.py:61-62, 80-81, 120, 134`, `docs_template.py:412, 453, 456`,
`expansion.py:53, 61, 66`.

Already right and not touched: `Architecture.never` (`values.py:401`), `ProfileView.never`
(`spec/contract/__init__.py:172`) and the review values' `never` (`review/domain/values.py:53`), all `review.never`;
the scope names `PART_USES`, `TIER_USES`; the key strings `uses.never`, `uses.apply_never`, the rule id `never-use`,
the JSON field `never_uses`.

`grep -rn 'may_not_use\|may-not-use'` over `xarch tests README.md CHANGELOG.md architecture.yaml docs` without
`docs/superpowers` finds three test function names: `tests/bootstrap/test_forbidden.py:25`,
`tests/modules/spec/application/logic/test_forbidden.py:189`, `tests/modules/rules/application/logic/test_stand_ins.py:223`
(the last is about fakes, not the lists, but spells the pattern).

## Required behaviour

### B1. Behaviour does not change

Every command's output, exit code, JSON, generated docs and finding stays byte for byte what it is at `c7d6127`. No
message, key, rule id, label or JSON field is renamed: they already carry the 0.3.0 names. The proof is the gates
passing with no test's expected value edited (only the identifiers the tests use to reach a value), the golden docs
regenerating with no diff, and the recorded corpora (`tests/bootstrap/corpora/`) needing no edit.

### B2. The renames

Each row renames the identifier everywhere it is defined, read, passed by keyword or named in a docstring, in `xarch/`
and in `tests/`.

| Old | New |
|---|---|
| `Architecture.forbidden` | `Architecture.uses_never` |
| `Tier.forbidden` (spec domain) | `Tier.apply_never` |
| `PartView.forbidden` | `PartView.uses_never` |
| `CheckedTier.forbidden` | `CheckedTier.apply_never` |
| `Profile.forbidden` (rules domain) | `Profile.uses_never` |
| `PartPlace.forbidden`, `SuitePlace.forbidden` | `.uses_never` |
| `InPart.forbidden`, `InTests.forbidden` | `.uses_never` |
| `FORBIDDEN_FIX` | `NEVER_USE_FIX` |
| `_forbidden` (expansion) | `_never_use` |
| `_FORBIDDEN` (key table) | `_NEVER_USE` |
| `forbidden_names` | `never_names` |
| `_forbidden_lists` | `_never_lists` |
| `_forbidden_refs` | `_never_refs` |
| locals and parameters `lists` (the parsed `never` block) in `profile_parsing.py` | `never_lists` |
| local `forbidden` (the resolved map) in `profile_parsing.py` | `uses_never` |
| `_forbidden_line` | `_never_use_line` |

Rules for the rows:

- The field that holds a part's banned names is `uses_never`; the tier switch is `apply_never`; the named-lists block,
  where it is a name in code, is `never_lists`. No new field, local or parameter is named bare `never` for the lists
  (KN dodge, line 411; R3 C2). `Architecture.never`, `ProfileView.never` and review's `never` keep their names and
  meaning.
- Field order in every dataclass stays as it is, so positional construction (`profile_parsing.py:209`,
  `checked_tier.py:13`, the builders of the tests) keeps working unchanged in position.
- A docstring that names the field by its old name names the new one, and one that names the list as "the forbidden
  list" says "the `uses.never` list" (`profile_values/tiers.py:13`; `values.py:208, 356`; `profile.py:51`). No comment
  is added anywhere (project rule).
- The Python field `tier` stays everywhere (KN 1.6, line 264).

### B3. The tests' own names

- The test helper `forbidden` (`tests/modules/rules/application/logic/checks.py:30`) becomes `never_use`, and its
  importer (`test_forbidden.py:5` there) imports it by the new name.
- The three test files `test_forbidden.py` (`tests/bootstrap/`, `tests/modules/rules/application/logic/`,
  `tests/modules/spec/application/logic/`) are renamed `test_never_use.py` with `git mv`, and their module docstrings
  that say "The forbidden check" say "The never-use check". No other line of them changes but the identifiers of B2
  and the names below. Before the move, check that no `test_never_use.py` exists in those folders (none does at
  `c7d6127`).
- The three test functions whose names hold `may_not_use` are renamed, keeping what they say:
  `test_a_pure_part_may_not_use_what_the_bundled_profile_forbids_it` →
  `test_a_pure_part_never_uses_what_the_bundled_profile_lists_for_it`;
  `test_the_guards_section_lists_the_names_each_part_may_not_use_and_says_what_it_does_not...` → the same name with
  `may_not_use` replaced by `never_uses`;
  `test_mocks_in_a_test_that_may_not_use_the_fakes_are_not_checked` →
  `test_mocks_in_a_test_barred_from_the_fakes_are_not_checked`.
- The docstring of `tests/modules/spec/application/logic/test_profile_checks.py:16` ("a part's `forbidden` list")
  names the `never` list.

### B4. What stays

These keep the word `forbidden` (or `apply_forbidden`) on purpose:

- The retired-names table (`xarch/modules/spec/domain/profile_keys.py:160-163`) and every test of a refusal of an old
  key or rule id: `test_profile_keys.py`, `test_retired_keys.py`, `test_explain.py:239-246`,
  `test_profile_explain.py:264-266`, `test_architecture_files.py:236-240`, the yaml-key arguments
  `service_writing(forbidden=...)`, `covered(forbidden=...)`, `{"forbidden": LISTS}`, `hints={"forbidden": ...}` and the
  expected messages in the renamed `test_never_use.py` of spec, `parts.service.uses: unknown key 'forbidden'` (114).
- Test-local variables named `forbidden` are renamed `uses_never` (`test_profile_parsing.py:393-394`), since B7.2 would
  report them.
- The assertions that the old JSON field is gone: `"forbidden" not in document` (`test_where_report.py:37, 44, 49`),
  `"forbidden" not in found` (`tests/bootstrap/test_where.py:117`).
- `test_written_checks.py:113-122`: an own check may take the freed id `forbidden`.
- English prose: `xarch/architectures/cli.md:130`, `web.md:130`, `docs/templates/architecture.md:100` and the
  generated `docs/{cli,web,xarch}/architecture.md` lines from it; `tests/architecture/test_self_check.py:61` ("one
  forbidden import").
- `CHANGELOG.md:23` (the `[Unreleased]` line that records the rename) and `:47` (0.2.0, history).
- `docs/examples/` (`profile_values/tiers.py:13` `apply_forbidden: bool`, `forbidden_imports` in two files) and the
  `docs/xarch/architecture.md` lines that quote them (347, 361, 399, 554).
- `tests/bootstrap/corpora/`: names of archived source files in recorded findings (`7cc6111.json:1400-1401`). No
  corpus is edited by this step.
- The archived code inside the `.tar.xz` files.

### B5. README and CHANGELOG

- CHANGELOG: one line under `[Unreleased]` → `### Changed` (`CHANGELOG.md:6-8`), after the existing lines of this
  release: "Internal names follow the 0.3.0 key names: the fields and functions that read `uses.never` and
  `uses.apply_never` say `uses_never`, `apply_never` and `never_lists` in place of `forbidden`; no output changes." (R3 O5.)
- README: no change. It names no internal identifier (`grep -n forbidden README.md` returns nothing at `c7d6127`).

### B6. Golden docs

`docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md` are regenerated as steps 2.2 and 2.3 did
(`build_controllers().spec.docs(<profile>)` for `cli`, `web` and `architecture.yaml`, written over `docs/cli/`,
`docs/web/`, `docs/xarch/`) and the diff is read: it must be empty. `_never_use_line` renders the same line. They are never
edited by hand (R3 O8).

### B7. Re-grep at the end

Run from the worktree root, after the gates:

1. `grep -rn 'may_not_use\|may-not-use' xarch tests README.md CHANGELOG.md architecture.yaml docs --exclude-dir=superpowers`
   returns nothing. `docs/superpowers/` is the workflow's record of the release's own specs and plans (this one
   included), which quote the pattern as history; it is not product text and is excluded.
2. `grep -rnw forbidden xarch tests docs README.md CHANGELOG.md architecture.yaml --exclude-dir=superpowers` returns only
   the lines B4 lists (KN 5, lines 390-392). Any other hit is an identifier this step missed.
3. `grep -rn 'FORBIDDEN\|\b_forbidden\|forbidden_names' xarch tests` returns nothing (`\b` keeps out the retired key
   `apply_forbidden` and test names such as `test_forbidden`, which B4 keeps).
4. `grep -rnw never xarch/modules/spec/domain/values.py xarch/modules/spec/contract/__init__.py` shows `never` only on
   the `review.never` fields and prose, never on a field holding the lists.

## Error paths

None new. The step adds no input and changes no refusal. If a rename is missed in a reader, Python raises
`AttributeError` or `TypeError` (an unexpected keyword) at the first test that reaches it; the full suite is the net.
A missed docstring or local shows up in B7.

## Tests

No new behaviour, so no new behaviour test. The proof is the existing suite, renamed to reach the new identifiers,
with no expected value edited:

| Test | Tier | Why there |
|---|---|---|
| `tests/modules/spec/application/logic/test_profile_parsing.py:38, 393-399` (`architecture.uses_never`), `test_profile_parsing_tests.py:133` (`t.apply_never`), the renamed spec `test_never_use.py:87, 91, 151, 152, 172` | unit (spec logic) | the parser fills the renamed fields with the same values |
| `tests/modules/spec/application/logic/test_profile_checks.py:8, 18` (`never_names`) | unit (spec logic) | the entry parser under its new name gives the same names and problems |
| `tests/modules/rules/builders.py:70, 89`, `tests/modules/rules/adapters/test_spec_profile.py:45, 115` | unit (rules adapter) | `PartView.uses_never` maps to `Profile.uses_never`; `CheckedTier.apply_never` carries over |
| `tests/modules/rules/application/logic/test_expansion.py:21`, `test_expandable.py:14-15`, the renamed rules `test_never_use.py:5, 17, 19, 97, 111` | unit (rules logic) | the `never-use` rules read `Profile.uses_never` and `CheckedTier.apply_never` and find the same violations |
| `tests/modules/rules/application/logic/test_where.py:40, 100, 171, 229, 275` | unit (rules logic) | `where` places carry `uses_never` with the same names |
| `tests/cli/reports/test_where_report.py:34` (`replace(PART, uses_never=...)`) | unit (cli report) | the JSON field `never_uses` and the text label still come out of the renamed contract field |
| `tests/bootstrap/test_bundled_guards.py:64, 67`, `tests/architecture/test_environment.py:14` | bootstrap / architecture | the bundled and own profiles parse to the same `uses_never` map and `apply_never` tiers |
| the renamed bootstrap `test_never_use.py` and the whole suite, including `tests/bootstrap/test_recorded_corpora.py` and the golden-doc tests | bootstrap | end to end: same findings, same recorded corpora, same generated docs |

Tests first: for each rename, the test lines that reach the identifier are changed first and run to see them fail
(`AttributeError`, `TypeError`, `ImportError`), then the code is renamed and they pass. Test-only renames (B3) are moves
and need no failing run.

Gates, each passing on this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the
background, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`.

## Hand-off to the planner

- Group the plan by concept, one task per concept, each carrying its own test-first cycle and commit: (1) the spec
  side's part and tier fields with their readers (`Architecture.uses_never`, `Tier.apply_never`, `PartView.uses_never`,
  `CheckedTier.apply_never`, `checked_tier.py`, `publishing.py`, `looseness.py`, `docs_template.py` with
  `_never_use_line`, `spec_profile.py`); (2) the rules side (`Profile.uses_never`, places, contract, `where.py`,
  `locate.py`, `where_report.py`, `expansion.py` with `NEVER_USE_FIX`, `_never_use`); (3) the parser
  (`never_names`, `_never_lists`, `_never_refs`, locals) and `_NEVER_USE`; (4) the tests' own names (B3); (5) CHANGELOG,
  golden-doc regeneration, B7 re-grep and the gates. A planner may merge (1) and (2) if the adapter makes them
  inseparable (`spec_profile.py:85` reads one and builds the other): it must stay green after each commit.
- Each task's commit leaves the suite green; `uv run ruff check` after each (long lines from longer names are wrapped
  by hand).
- `.claude/` stays out of commits; nothing is pushed.

## Out of scope

- Any behaviour change: messages, keys, rule ids, labels, JSON fields, generated docs, recorded findings.
- `docs/examples/` and what calibration sends (KN 1.6, lines 252-254).
- `review.never` and its fields (ruling 15, R3 C2).
- code-shape's internal names (`may_import`, `must_import`, `holds`, `immutable` fields and their readers): release
  step 4.7.
- The `tier` → `tests` rename's internal names: the Python field `tier` stays (KN 1.6, line 264); the remaining
  `grep -rn 'tier:'` and `grep -rn '"rules"'` checks of KN 5 belong to the steps that own them and are not re-done
  here beyond reading their result.
- Renaming test files other than the three `test_forbidden.py`.

---

# 2.4 Internal identifiers follow the key-names renames: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename every Python identifier that still says `forbidden` (and the test names that spell `may_not_use`)
to the 0.3.0 names `uses_never`, `apply_never`, `never_lists`, `never_names`, `NEVER_USE_FIX`, `_never_use`,
`_NEVER_USE`, `_never_use_line`, with no change to any output.

**Architecture:** A pure rename in five tasks, one per concept: (1) the spec side's part and tier fields and their
readers, (2) the rules side's profile, places and contract fields and their readers, (3) the parser's functions and
locals and the key table's kinds, (4) the tests' own names, (5) CHANGELOG, golden docs, re-grep and gates. Each task
changes the tests that reach an identifier first, sees them fail, renames the code, sees them pass, and commits with
the whole suite green. A snapshot of the CLI's outputs and of the dataclasses' field order is taken before any edit and
compared at the end, so "no output changes" is shown, not assumed.

**Tech Stack:** Python 3.13, pytest, ruff, typer; everything runs through `uv run`.

**Spec:** `docs/superpowers/specs/2-4-spec-internal-c61068a6.md` (prepended above).

## Global Constraints

- Behaviour does not change: every command's output, exit code, JSON, generated docs and finding stays byte for byte
  what it is at `c7d6127`. No message, key, rule id, label or JSON field is renamed.
- No test's expected value is edited; only the identifiers the tests use to reach a value (and the test names of B3).
- The recorded corpora (`tests/bootstrap/corpora/`) are not edited. `docs/examples/` is not edited. The golden docs are
  regenerated, never hand-edited, and their diff must be empty.
- Field order in every dataclass stays as it is (positional construction at `profile_parsing.py:209`,
  `checked_tier.py:13`, `profile_parsing.py:643` and in the tests keeps working).
- No new field, local or parameter is named bare `never` for the lists. `Architecture.never`, `ProfileView.never` and
  review's `never` keep their names and meaning. The Python field `tier` stays everywhere.
- No comment is added anywhere (project rule). Docstrings that name an old field name the new one.
- `uv run ruff check` after each task (never `--fix`); line length is 140 (`ruff.toml`).
- `.claude/` stays out of commits; nothing is pushed. Every commit message ends with the line
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Gates on this branch alone: `uv run pytest -q` (over two minutes: run it in the background with `timeout`, read the
  tail at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
  `uv run xarch profile check architecture.yaml`.
- Process safety: never `pkill`/`killall`/`kill` by pattern. Stop a stuck run with `timeout` or by a PID you recorded.

## Decisions this plan takes where the spec is silent or self-contradictory

- **B7.3 and the corpora.** `grep -rn 'FORBIDDEN\|\b_forbidden\|forbidden_names' xarch tests` also matches
  `tests/bootstrap/corpora/7cc6111.json:1400-1401` (`forbidden_names` named in recorded findings of an archived
  source), which B4 keeps and B1 forbids editing. The plan runs B7.3 with `--exclude-dir=corpora` and shows separately
  that the corpora's two lines are its only hits without the exclusion.
- **B7.3 and five test function names.** At `c7d6127`, B7.3 also matches five test function names holding
  `forbidden_names`. B7.3 says the grep returns nothing, so Task 4 renames them too, keeping what they say:
  - `tests/bootstrap/test_where.py:39`
    `test_a_file_in_a_part_says_its_part_role_litmus_imports_libraries_forbidden_names_and_test` →
    `test_a_file_in_a_part_says_its_part_role_litmus_imports_libraries_never_uses_and_test`
  - `tests/modules/rules/application/logic/test_where.py:91`
    `test_code_in_a_part_gets_its_role_litmus_imports_libraries_forbidden_names_and_test` →
    `test_code_in_a_part_gets_its_role_litmus_imports_libraries_never_uses_and_test`
  - `tests/modules/rules/application/logic/test_where.py:225`
    `test_a_test_of_a_tier_not_held_to_forbidden_names_none_and_a_tier_s_types_only_parts_are_shown` →
    `test_a_test_of_a_tier_not_held_to_the_lists_never_uses_none_and_a_tier_s_types_only_parts_are_shown`
  - `tests/modules/rules/application/logic/test_where.py:272`
    `test_a_test_of_a_listed_part_in_a_tier_not_held_to_the_list_is_told_no_forbidden_names` →
    `test_a_test_of_a_listed_part_in_a_tier_not_held_to_the_list_is_told_no_never_uses`
  - `tests/modules/spec/application/logic/test_profile_parsing.py:389`
    `test_a_part_refers_to_a_list_of_forbidden_names_by_its_name` →
    `test_a_part_refers_to_a_list_under_never_by_its_name`
- **B7.2 and the new CHANGELOG line.** The B5 CHANGELOG line itself says "in place of `forbidden`", so after Task 5
  `CHANGELOG.md` has three `-w forbidden` hits (23, 47 and the new line), all expected.
- **Task 1 and Task 2 share `spec_profile.py:85`.** Task 1 changes only what it reads (`p.uses_never`), keeping the
  keyword `forbidden=` of `Profile`; Task 2 changes the keyword. Both stay green.

## Review Focus

The five conditions the spec implies that no renamed test pins, most likely first, each with the check that pins it:

1. **`xarch where` on a part file and on a test held to its part's list, text and JSON.** A missed reader in
   `locate.py` or `where_report.py` swaps or drops the `never uses:` line or the `never_uses` field. Pinned by the
   snapshot of Task 1 Step 1 (`where-part.*`, `where-test.*`, `where-guard.*`) compared in Task 5 Step 6: identical.
2. **A dataclass whose field moved position.** A rename that also moves a field silently reassigns every positional
   construction (`profile_parsing.py:209`, `:643`, `checked_tier.py:13`). Pinned by the field-order snapshot
   (`fields.txt`) of Task 1 Step 1, compared in Task 5 Step 6: only the renamed name differs, in the same place.
3. **`xarch check` and `xarch check --strict` on xarch itself.** The renames touch xarch's own source, which its own
   profile checks (a name, a `holds`, a line length). Pinned by `check.json` and `check-strict.json` of the snapshot:
   identical.
4. **`profile explain` for the two keys whose reader kinds `_NEVER_USE` names.** A wrong rename in `key_table.py`
   changes what `profile explain` says a key needs. Pinned by `explain-never.json` and `explain-apply-never.json` of the
   snapshot: identical.
5. **The generated `never-use` docs line.** `_never_use_line` renders the guards line of `testing.md`. Pinned by the
   golden-doc regeneration of Task 5 Step 2: the diff is empty.

---

## File Structure

No file is created in the app. Files modified, by task:

| Task | Files |
|---|---|
| 1 | `xarch/modules/spec/domain/values.py`, `xarch/modules/spec/contract/__init__.py`, `xarch/profile_values/tiers.py`, `xarch/modules/spec/application/logic/checked_tier.py`, `xarch/modules/spec/application/services/publishing.py`, `xarch/modules/spec/application/logic/looseness.py`, `xarch/modules/spec/application/logic/docs_template.py`, `xarch/modules/rules/adapters/spec_profile.py`, `xarch/modules/rules/application/logic/expansion.py` (line 66 only), `xarch/modules/rules/application/logic/where.py` (line 201 only); tests: `tests/modules/spec/application/logic/test_profile_parsing.py`, `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, `tests/modules/spec/application/logic/test_forbidden.py`, `tests/bootstrap/test_bundled_guards.py`, `tests/architecture/test_environment.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/rules/builders.py`, `tests/modules/rules/application/logic/test_expandable.py`, `tests/modules/rules/application/logic/test_forbidden.py` |
| 2 | `xarch/modules/rules/domain/profile.py`, `xarch/modules/rules/domain/places.py`, `xarch/modules/rules/contract/__init__.py`, `xarch/modules/rules/application/logic/where.py`, `xarch/modules/rules/application/services/locate.py`, `xarch/cli/reports/where_report.py`, `xarch/modules/rules/adapters/spec_profile.py`, `xarch/modules/rules/application/logic/expansion.py`; tests: `tests/modules/rules/builders.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/rules/application/logic/test_expandable.py`, `tests/modules/rules/application/logic/test_expansion.py`, `tests/modules/rules/application/logic/test_forbidden.py`, `tests/modules/rules/application/logic/test_where.py`, `tests/cli/reports/test_where_report.py` |
| 3 | `xarch/modules/spec/application/logic/profile_checks.py`, `xarch/modules/spec/application/logic/profile_parsing.py`, `xarch/modules/spec/domain/key_table.py`; test: `tests/modules/spec/application/logic/test_profile_checks.py` |
| 4 | `git mv` of the three `test_forbidden.py` to `test_never_use.py`; `tests/modules/rules/application/logic/checks.py`, `tests/modules/rules/application/logic/test_stand_ins.py`, `tests/bootstrap/test_where.py`, `tests/modules/rules/application/logic/test_where.py`, `tests/modules/spec/application/logic/test_profile_parsing.py` |
| 5 | `CHANGELOG.md`; `docs/{cli,web,xarch}/testing.md` regenerated (expected unchanged) |

Scratch files live in `/tmp/xarch-2-4/` (outside the worktree); nothing there is committed.

---

### Task 1: The spec side's part and tier fields: `uses_never`, `apply_never`

**Files:**
- Modify: `xarch/modules/spec/domain/values.py:208, 231, 356, 393`
- Modify: `xarch/modules/spec/contract/__init__.py:107`
- Modify: `xarch/profile_values/tiers.py:13, 22`
- Modify: `xarch/modules/spec/application/logic/checked_tier.py:13`
- Modify: `xarch/modules/spec/application/services/publishing.py:59`
- Modify: `xarch/modules/spec/application/logic/looseness.py:69-70, 88`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:412-413, 450-456`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:85`
- Modify: `xarch/modules/rules/application/logic/expansion.py:66`
- Modify: `xarch/modules/rules/application/logic/where.py:201`
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py:38, 393-394, 399`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py:133`
- Test: `tests/modules/spec/application/logic/test_forbidden.py:87, 91, 151, 152, 172`
- Test: `tests/bootstrap/test_bundled_guards.py:64, 67`
- Test: `tests/architecture/test_environment.py:14`
- Test: `tests/modules/rules/adapters/test_spec_profile.py:45`
- Test: `tests/modules/rules/builders.py:70`
- Test: `tests/modules/rules/application/logic/test_expandable.py:15`
- Test: `tests/modules/rules/application/logic/test_forbidden.py:17, 97`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces:
  - `Architecture.uses_never: dict[str, tuple[tuple[str, ...], ...]]` (was `forbidden`; same position, between
    `framework` and `excluded`).
  - `Tier.apply_never: bool` (spec domain; was `forbidden`; same position, between `types_only` and `folder`).
  - `PartView.uses_never: tuple[tuple[str, ...], ...]` (was `forbidden`; same position, between `untested` and
    `must_import`).
  - `CheckedTier.apply_never: bool` (was `forbidden`; same position, between `types_only` and `proves`).
  - `docs_template._never_use_line(architecture: Architecture) -> str` (was `_forbidden_line`).
  - Unchanged here and renamed by Task 2: `Profile.forbidden` (rules domain), read by `spec_profile.py:85` as the
    keyword `forbidden=`.

- [ ] **Step 1: Take the snapshot of outputs and field order (before any edit)**

Create `/tmp/xarch-2-4/fields.py`:

```python
"""Print each renamed dataclass's fields in order, one class per line."""
from dataclasses import fields

from xarch.modules.rules.contract import InPart, InTests
from xarch.modules.rules.domain.places import PartPlace, SuitePlace
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.spec.contract import PartView
from xarch.modules.spec.domain.values import Architecture, Tier
from xarch.profile_values.tiers import CheckedTier

for cls in (Architecture, Tier, PartView, CheckedTier, Profile, PartPlace, SuitePlace, InPart, InTests):
    print(cls.__name__, " ".join(f.name for f in fields(cls)))
```

Create `/tmp/xarch-2-4/snapshot.sh`:

```bash
#!/usr/bin/env bash
# usage: snapshot.sh <out-dir>, run from the worktree root
set -u
out="$1"
mkdir -p "$out"
run() { local name="$1"; shift; timeout 300 uv run "$@" > "$out/$name" 2>&1; echo "exit $?" >> "$out/$name"; }
run check.json xarch check --format json
run check-strict.json xarch check --strict --format json
run where-part.txt xarch where xarch/modules/spec/domain/values.py
run where-part.json xarch where xarch/modules/spec/domain/values.py --format json
run where-test.txt xarch where tests/modules/spec/domain/test_profile_keys.py
run where-test.json xarch where tests/modules/spec/domain/test_profile_keys.py --format json
run where-guard.json xarch where tests/architecture/test_self_check.py --format json
run explain-never.json xarch profile explain parts.uses.never --format json
run explain-apply-never.json xarch profile explain tiers.uses.apply_never --format json
run profile-check.txt xarch profile check architecture.yaml
run fields.txt python -I /tmp/xarch-2-4/fields.py
```

Run:
```bash
git status --short
bash /tmp/xarch-2-4/snapshot.sh /tmp/xarch-2-4/before
tail -n 1 /tmp/xarch-2-4/before/*
cat /tmp/xarch-2-4/before/fields.txt | cut -c1-80
```
Expected: `git status` shows only `?? docs/superpowers/...` (the spec and this plan); every file ends `exit 0`;
`fields.txt` has nine lines, starting `Architecture name layout parts rules ...`, `Tier name subject proves ...`, and
so on, each holding the word `forbidden` once. If any file does not end `exit 0`, stop and report: the baseline is not
clean.

- [ ] **Step 2: Change the tests that reach the spec-side fields**

`tests/modules/spec/application/logic/test_profile_parsing.py`, line 38:
```python
            architecture.naming, architecture.fakes, architecture.files, architecture.uses_never,
```
lines 393-394:
```python
    uses_never = parsed(document).uses_never
    assert uses_never == {"service": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",)),
```
(line 395, `"shared": ...`, stays; re-indent it by one column so it still lines up under the `{`:
`                          "shared": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",))}`)
line 399:
```python
    assert parsed(layered(never={"pure": ["socket"]})).uses_never == {}
```

`tests/modules/spec/application/logic/test_profile_parsing_tests.py`, line 133:
```python
    assert [(t.apply_never, t.types_only) for t in tiers] == [(True, ()), (False, ("service", "store"))]
```

`tests/modules/spec/application/logic/test_forbidden.py`, line 87:
```python
    assert parsed(with_list([name])).uses_never == {"service": (tuple(name.split(".")),)}
```
line 91:
```python
    assert parsed(with_list([".absolute()", "pathlib.Path.cwd"])).uses_never == {
```
lines 151-152:
```python
    assert parsed(service_uses({"never": "ambient"})).uses_never == {"service": (("os", "getcwd"),)}
    assert parsed(covered(never=LISTS)).uses_never == {}
```
line 172:
```python
    assert [tier.apply_never for tier in parsed(document).tiers] == [True, False]
```

`tests/bootstrap/test_bundled_guards.py`, lines 64-67:
```python
    assert architecture.uses_never == {"domain": pure, "logic": pure, "ports": pure, "services": ambient,
                                       "controller": ambient, "adapters": ambient, "platform": environment,
                                       name: environment, "contract": published, "kernel": pure, "kernel-logic": pure}
    assert [tier.name for tier in architecture.tiers if tier.apply_never] == ["unit"]
```

`tests/architecture/test_environment.py`, line 14:
```python
    assert {part for part in architecture.parts if not reading <= set(architecture.uses_never.get(part, ()))} == {
```

`tests/modules/rules/adapters/test_spec_profile.py`, line 45:
```python
    parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/", uses_never=(("socket",),),
```
(line 115, `forbidden={"core": (("socket",),)},`, is the rules `Profile`'s keyword: it stays until Task 2.)

`tests/modules/rules/builders.py`, lines 69-70:
```python
UNIT = CheckedTier("unit", (Target("kernel"), *own("domain", "logic", "adapters")), ("modules", "docs", "domain"),
                apply_never=True)
```
(line 89, `forbidden={"domain": ...}`, is the rules `Profile`'s keyword: Task 2.)

`tests/modules/rules/application/logic/test_expandable.py`, line 15:
```python
    tiers=(CheckedTier("tier", (Target("one"),), ("tier",), types_only=("two",), apply_never=True,
```
(line 14, `forbidden={"one": ...}`, is the rules `Profile`'s keyword: Task 2.)

`tests/modules/rules/application/logic/test_forbidden.py` (`Tier` there is `CheckedTier as Tier`), line 17:
```python
                  tiers=(Tier("unit", (Target("domain", "own"),), apply_never=True),
```
line 97:
```python
                         "tiers": (*PROFILE.tiers, Tier("guard", (), ("architecture",), apply_never=True))})
```
(lines 19 and 111, `forbidden={...}` on `Profile`: Task 2.)

- [ ] **Step 3: Run the changed tests to see them fail**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_forbidden.py tests/bootstrap/test_bundled_guards.py tests/architecture/test_environment.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/application/logic/test_expandable.py tests/modules/rules/application/logic/test_forbidden.py 2>&1 | tail -15
```
Expected: FAIL. `AttributeError: 'Architecture' object has no attribute 'uses_never'`, `AttributeError: 'Tier' object
has no attribute 'apply_never'`, and collection errors
`TypeError: CheckedTier.__init__() got an unexpected keyword argument 'apply_never'` and
`TypeError: PartView.__init__() got an unexpected keyword argument 'uses_never'`.

- [ ] **Step 4: Rename the fields and their readers**

`xarch/modules/spec/domain/values.py`, line 208 (Tier docstring):
```python
    apply_never: its tests are held to the `uses.never` list of the part they mirror
```
line 231:
```python
    apply_never: bool = False
```
line 356 (Architecture docstring; line 357 stays):
```python
    uses_never: the dotted names and modules a part may not use, and the methods it may not call on anything, each as
```
line 393:
```python
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
```

`xarch/modules/spec/contract/__init__.py`, line 107:
```python
    uses_never: tuple[tuple[str, ...], ...] = ()
```

`xarch/profile_values/tiers.py`, line 13 (docstring; lines 12 and 14 stay):
```python
    nothing); the parts its tests may use as types only; whether its tests keep to the `uses.never` list of the part they
```
line 22:
```python
    apply_never: bool = False
```

`xarch/modules/spec/application/logic/checked_tier.py`, line 13:
```python
    return CheckedTier(tier.name, subject, tier.folder, tier.types_only, tier.apply_never, tier.proves, tier.may_touch,
```

`xarch/modules/spec/application/services/publishing.py`, line 59:
```python
                               docs_name(architecture, part), part.untested, architecture.uses_never.get(name, ()),
```

`xarch/modules/spec/application/logic/looseness.py`, lines 69-70:
```python
        kept = custom.uses_never.get(name, ())
        found += [("uses.never", name, ".".join(banned)) for banned in base.uses_never.get(name, ())
```
line 88:
```python
              if tier.apply_never and tier.name in tiers and not tiers[tier.name].apply_never]
```

`xarch/modules/spec/application/logic/docs_template.py`, lines 412-413:
```python
    if architecture.uses_never:
        lines.append(_never_use_line(architecture))
```
lines 450, 453 and 456 (the rest of the function stays):
```python
def _never_use_line(architecture: Architecture) -> str:
```
```python
    for name, names in architecture.uses_never.items():
```
```python
    tiers = [tier.name for tier in architecture.tiers if tier.apply_never]
```

`xarch/modules/rules/adapters/spec_profile.py`, line 85 (reads the renamed `PartView` field; the keyword stays
`forbidden=` until Task 2):
```python
                       forbidden={p.name: p.uses_never for p in parts if p.uses_never},
```

`xarch/modules/rules/application/logic/expansion.py`, line 66:
```python
              for tier in profile.tiers if tier.apply_never for part, names in profile.forbidden.items()]
```

`xarch/modules/rules/application/logic/where.py`, line 201:
```python
    names = tuple(".".join(n) for p in where.parts for n in profile.forbidden.get(p, ())) if where.tier.apply_never else ()
```

Then check nothing still reads the old names on these four classes:
```bash
grep -rn 'tier\.forbidden\|architecture\.forbidden\|custom\.forbidden\|base\.forbidden\|p\.forbidden\|_forbidden_line' xarch tests
```
Expected: no output.

- [ ] **Step 5: Run the tests of Step 3 to see them pass**

Same command as Step 3. Expected: PASS, no error.

- [ ] **Step 6: Lint and the whole suite**

```bash
uv run ruff check
timeout 1500 uv run pytest -q > /tmp/xarch-2-4/task1-pytest.txt 2>&1; echo "exit $?"
tail -n 3 /tmp/xarch-2-4/task1-pytest.txt
```
Run the pytest line in the background (`run_in_background`) and read the tail when it ends. Expected: ruff
`All checks passed!`; pytest `exit 0`, last line `N passed` (with any skips the suite had at `c7d6127`), no failure.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/domain/values.py xarch/modules/spec/contract/__init__.py xarch/profile_values/tiers.py \
  xarch/modules/spec/application/logic/checked_tier.py xarch/modules/spec/application/services/publishing.py \
  xarch/modules/spec/application/logic/looseness.py xarch/modules/spec/application/logic/docs_template.py \
  xarch/modules/rules/adapters/spec_profile.py xarch/modules/rules/application/logic/expansion.py \
  xarch/modules/rules/application/logic/where.py \
  tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_forbidden.py tests/bootstrap/test_bundled_guards.py \
  tests/architecture/test_environment.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/builders.py \
  tests/modules/rules/application/logic/test_expandable.py tests/modules/rules/application/logic/test_forbidden.py
git status --short
git commit -m "$(cat <<'EOF'
The spec side names a part's banned names uses_never and a tier's switch apply_never: Architecture.uses_never, Tier.apply_never, PartView.uses_never and CheckedTier.apply_never, each in its old place, with their readers and the docs line builder _never_use_line; no output changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```
Expected: `git status` before the commit shows only those files staged and `?? docs/superpowers/...` untracked.

---

### Task 2: The rules side's fields: `Profile.uses_never`, the places, the contract, `NEVER_USE_FIX`, `_never_use`

**Files:**
- Modify: `xarch/modules/rules/domain/profile.py:51, 90`
- Modify: `xarch/modules/rules/domain/places.py:57, 98`
- Modify: `xarch/modules/rules/contract/__init__.py:188, 227`
- Modify: `xarch/modules/rules/application/logic/where.py:105, 201`
- Modify: `xarch/modules/rules/application/services/locate.py:52, 65`
- Modify: `xarch/cli/reports/where_report.py:61-62, 80-81, 120, 134`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:85`
- Modify: `xarch/modules/rules/application/logic/expansion.py:15, 49-67, 367`
- Test: `tests/modules/rules/builders.py:89`
- Test: `tests/modules/rules/adapters/test_spec_profile.py:115`
- Test: `tests/modules/rules/application/logic/test_expandable.py:14`
- Test: `tests/modules/rules/application/logic/test_expansion.py:21`
- Test: `tests/modules/rules/application/logic/test_forbidden.py:19, 111`
- Test: `tests/modules/rules/application/logic/test_where.py:40, 100, 171, 229, 275`
- Test: `tests/cli/reports/test_where_report.py:34`

**Interfaces:**
- Consumes (Task 1): `PartView.uses_never`, `CheckedTier.apply_never`.
- Produces:
  - `Profile.uses_never: dict[str, tuple[tuple[str, ...], ...]]` (rules domain; was `forbidden`; same position,
    between `framework` and `info`).
  - `PartPlace.uses_never: tuple[str, ...]` (between `libraries` and `tier`), `SuitePlace.uses_never: tuple[str, ...]`
    (between `may_import_text` and `may_use_fakes`).
  - `InPart.uses_never: tuple[str, ...]` (between `libraries` and `tested`), `InTests.uses_never: tuple[str, ...]`
    (between `types_only` and `tier`).
  - `expansion.NEVER_USE_FIX: str` (was `FORBIDDEN_FIX`, same text), `expansion._never_use(profile: Profile) ->
    tuple[Rule, ...]` (was `_forbidden`); the book key stays `"never-use"`.

- [ ] **Step 1: Change the tests that reach the rules-side fields**

`tests/modules/rules/builders.py`, line 89:
```python
    uses_never={"domain": (NOW, ("builtins", "open"), ("socket",))}, language=PYTHON, default_tests="tests")
```

`tests/modules/rules/adapters/test_spec_profile.py`, line 115:
```python
        uses_never={"core": (("socket",),)},
```

`tests/modules/rules/application/logic/test_expandable.py`, line 14:
```python
    libraries={"one": ("outside",)}, uses_never={"one": (("outside",),)},
```

`tests/modules/rules/application/logic/test_expansion.py`, line 21:
```python
OFF = replace(PROFILE, libraries=None, uses_never={}, tiers=(), package_only=(), no_comments=False, dead_code=False)
```

`tests/modules/rules/application/logic/test_forbidden.py`, line 19:
```python
                  uses_never={"domain": (NOW, ("builtins", "open"), ("socket",), ("urllib",))},
```
line 111:
```python
                  uses_never={"services": (("", "absolute()"), ("", "resolve()"), ("pathlib", "Path", "cwd"))})
```

`tests/modules/rules/application/logic/test_where.py`, line 40:
```python
    uses_never={"domain": (NOW, ("builtins", "open"))},
```
line 100:
```python
    assert (here.libraries, here.uses_never) == ((), ("datetime.datetime.now", "builtins.open"))
```
line 171:
```python
    assert (here.may_use_fakes, here.test_code_from, here.uses_never) == (
```
line 229:
```python
    assert (here.tier.name, here.uses_never, here.tier.types_only) == ("rendering", (), ("controller",))
```
line 275:
```python
    assert (here.tier.name, here.uses_never) == ("unit", ())
```

`tests/cli/reports/test_where_report.py`, line 34 (the asserts of 37, 44 and 49, `"forbidden" not in document`, stay:
they pin that the old JSON field is gone):
```python
    held = replace(PART, uses_never=("socket", "builtins.open"))
```

- [ ] **Step 2: Run the changed tests to see them fail**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/rules tests/cli/reports/test_where_report.py 2>&1 | tail -15
```
Expected: FAIL. Collection errors `TypeError: Profile.__init__() got an unexpected keyword argument 'uses_never'`
(from `builders.py`, which most rules tests import), and in `test_where_report.py`
`TypeError: ... unexpected keyword argument 'uses_never'` from `replace`.

- [ ] **Step 3: Rename the fields, their readers and the expansion names**

`xarch/modules/rules/domain/profile.py`, line 51 (docstring; line 52 stays):
```python
    uses_never holds, by part, the dotted names and modules a part may not use, and the methods it may not call on
```
line 90:
```python
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
```

`xarch/modules/rules/domain/places.py`, lines 57 and 98 (each):
```python
    uses_never: tuple[str, ...]
```

`xarch/modules/rules/contract/__init__.py`, lines 188 and 227 (each):
```python
    uses_never: tuple[str, ...]
```

`xarch/modules/rules/application/logic/where.py`, line 105:
```python
        tuple(".".join(n) for n in profile.uses_never.get(part, ())), tier,
```
line 201 (Task 1 already reads `where.tier.apply_never`):
```python
    names = tuple(".".join(n) for p in where.parts for n in profile.uses_never.get(p, ())) if where.tier.apply_never else ()
```

`xarch/modules/rules/application/services/locate.py`, line 52:
```python
                          _reaches(found.reaches), found.may_import_text, found.libraries, found.uses_never,
```
line 65:
```python
                        found.may_import_text, tier.types_only if tier is not None else (), found.uses_never,
```

`xarch/cli/reports/where_report.py`, lines 61-62:
```python
    if where.uses_never:
        lines.append(_line("never uses", ", ".join(where.uses_never)))
```
lines 80-81:
```python
        if where.uses_never:
            lines.append(_line("never uses", ", ".join(where.uses_never)))
```
line 120:
```python
                         "never_uses": list(where.uses_never)}
```
line 134:
```python
                         "may_import_text": where.may_import_text or None, "never_uses": list(where.uses_never),
```

`xarch/modules/rules/adapters/spec_profile.py`, line 85:
```python
                       uses_never={p.name: p.uses_never for p in parts if p.uses_never},
```

`xarch/modules/rules/application/logic/expansion.py`, line 15:
```python
NEVER_USE_FIX = "do what needs {hit} outside {scope_part}/, and hand {scope_part}/ the result"
```
lines 49-67, the whole function:
```python
def _never_use(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part with a `uses.never` list neither imports what it names, nor uses a name it lists, nor calls a
    method it lists on anything but what its object holds; a test of a tier that applies the lists
    (`uses.apply_never`) is held to the list of each part it mirrors. One finding per line and name."""
    if not profile.uses_never:
        return ()
    facts = ("imported-name", "use", "method-call")
    keep, exempt = _all("not relative", "not on-own-object"), _all("reported-at-import")
    fakes = (_of(f"not below {'/'.join(profile.fakes.folder)}"),) if profile.fakes is not None else ()
    found = [Rule("never-use", Scope(APP, part), facts, MAY_NOT, (Match("path", names=names),),
                  (Saying("{where} may not {verb} {hit} ({key})", NEVER_USE_FIX, once=("line", "hit")),),
                  keep=keep, exempt=exempt, key=f"parts.{part}.uses.never")
             for part, names in profile.uses_never.items()]
    found += [Rule("never-use", Scope(TESTS, part, tier.name, fakes), facts, MAY_NOT, (Match("path", names=names),),
                   (Saying("a test of {scope_part}/ ({tier} tier) may not {verb} {hit} ({key})", NEVER_USE_FIX,
                           once=("line", "hit")),),
                   keep=keep, exempt=exempt, key=f"parts.{part}.uses.never; tiers.{tier.name}.uses.apply_never")
              for tier in profile.tiers if tier.apply_never for part, names in profile.uses_never.items()]
    return tuple(found)
```
line 367 (in `book`):
```python
            "never-use": _never_use(profile), "tiers": _tiers(profile), "types-only tiers": _types_only_tiers(profile),
```

Then check nothing still reads the old names:
```bash
grep -rnw 'forbidden\|FORBIDDEN_FIX\|_forbidden' xarch/modules/rules xarch/cli
```
Expected: no output.

- [ ] **Step 4: Run the tests of Step 2 to see them pass**

Same command as Step 2. Expected: PASS, no error.

- [ ] **Step 5: Lint and the whole suite**

```bash
uv run ruff check
timeout 1500 uv run pytest -q > /tmp/xarch-2-4/task2-pytest.txt 2>&1; echo "exit $?"
tail -n 3 /tmp/xarch-2-4/task2-pytest.txt
```
(pytest in the background, read at the end.) Expected: ruff `All checks passed!`; pytest `exit 0`, no failure.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/domain/profile.py xarch/modules/rules/domain/places.py xarch/modules/rules/contract/__init__.py \
  xarch/modules/rules/application/logic/where.py xarch/modules/rules/application/services/locate.py \
  xarch/cli/reports/where_report.py xarch/modules/rules/adapters/spec_profile.py \
  xarch/modules/rules/application/logic/expansion.py \
  tests/modules/rules/builders.py tests/modules/rules/adapters/test_spec_profile.py \
  tests/modules/rules/application/logic/test_expandable.py tests/modules/rules/application/logic/test_expansion.py \
  tests/modules/rules/application/logic/test_forbidden.py tests/modules/rules/application/logic/test_where.py \
  tests/cli/reports/test_where_report.py
git status --short
git commit -m "$(cat <<'EOF'
The rules side names a part's banned names uses_never: Profile.uses_never, the where places PartPlace and SuitePlace, the contract's InPart and InTests that where_report reads, each in its old place; the never-use rules are built by _never_use with the fix text NEVER_USE_FIX; no output changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: The parser and the key table: `never_names`, `_never_lists`, `_never_refs`, `_NEVER_USE`

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:609`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:168, 182, 203, 209, 447-486`
- Modify: `xarch/modules/spec/domain/key_table.py:192, 206, 210`
- Test: `tests/modules/spec/application/logic/test_profile_checks.py:8, 16, 18`

**Interfaces:**
- Consumes (Task 1): `Architecture.uses_never` filled positionally at `profile_parsing.py:209` (position unchanged).
- Produces:
  - `profile_checks.never_names(value: Any, where: str, problems: list[str], language: Language) ->
    tuple[tuple[str, ...], ...] | None` (was `forbidden_names`, same body).
  - `profile_parsing._never_lists(value: Any, problems: list[str], language: Language) ->
    dict[str, tuple[tuple[str, ...], ...] | None] | None` (was `_forbidden_lists`).
  - `profile_parsing._never_refs(specs: dict[str, Any], parts: dict[str, Part], never_lists: dict[str,
    tuple[tuple[str, ...], ...] | None] | None, problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]`
    (was `_forbidden_refs`, parameter `lists`).
  - `key_table._NEVER_USE` (was `_FORBIDDEN`, same value).

- [ ] **Step 1: Change the test that imports the entry parser**

`tests/modules/spec/application/logic/test_profile_checks.py`, line 8:
```python
from xarch.modules.spec.application.logic.profile_checks import dotted_names, is_name, never_names
```
(ruff's import sorting wants `is_name` before `never_names`.) Lines 16 and 18:
```python
    """What a `never` list of the one item comes to: the names it bans, and every problem."""
```
```python
    return never_names([item], "at", problems, PYTHON), problems
```

- [ ] **Step 2: Run it to see it fail**

Run:
```bash
timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_checks.py 2>&1 | tail -5
```
Expected: FAIL at collection, `ImportError: cannot import name 'never_names' from
'xarch.modules.spec.application.logic.profile_checks'`.

- [ ] **Step 3: Rename the entry parser, the block parser, the reference resolver and their locals**

`xarch/modules/spec/application/logic/profile_checks.py`, lines 609-610:
```python
def never_names(value: Any, where: str, problems: list[str],
                language: Language) -> tuple[tuple[str, ...], ...] | None:
```
(the continuation line is re-indented to line up after the new `(`; the body stays.)

`xarch/modules/spec/application/logic/profile_parsing.py`, line 168:
```python
    never_lists = _never_lists(document["never"], problems, language) if "never" in document else {}
```
line 182:
```python
    uses_never = _never_refs(specs, parts, never_lists, problems)
```
line 203:
```python
    problems += unlike(alike, {name: (frozenset(uses_never.get(name, ())), part.holds, part.immutable)
```
line 209 (the positional argument keeps its place, between the framework and `excluded`):
```python
                        libraries, guards, fakes, built.repeats, written, testing.framework if testing else None, uses_never,
```
lines 447-486, both functions whole:
```python
def _never_lists(value: Any, problems: list[str],
                 language: Language) -> dict[str, tuple[tuple[str, ...], ...] | None] | None:
    """The named lists of names a part never uses; a list already reported is None. None: `never` is no mapping."""
    if not isinstance(value, Mapping):
        problems.append("never: must be a mapping of list names to lists of dotted names, such as "
                        "{pure: [datetime.datetime.now, socket]}")
        return None
    never_lists: dict[str, tuple[tuple[str, ...], ...] | None] = {}
    for name, names in value.items():
        if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
            problems.append(f"never: {name!r} is not a list name: use letters, digits, '_' and '-'")
        else:
            never_lists[name] = ck.never_names(names, f"never.{name}", problems, language)
    return never_lists


def _never_refs(specs: dict[str, Any], parts: dict[str, Part],
                never_lists: dict[str, tuple[tuple[str, ...], ...] | None] | None,
                problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    """What each part whose `uses` names a list under `never` never uses; when `never` is no mapping, a part's list
    says nothing more."""
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name in parts:
        spec = specs[name]
        if "uses" not in spec:
            continue
        uses = _group(spec["uses"], PART_USES, "{never: pure}", f"parts.{name}.uses", problems)
        if "never" not in uses or never_lists is None:
            continue
        ref, where = uses["never"], f"parts.{name}.uses.never"
        if isinstance(ref, list):
            problems.append(f"{where}: names one list under never: write the name of a list, such as pure")
        elif not isinstance(ref, str):
            problems.append(f"{where}: must be the name of a list under `never`")
        elif ref not in never_lists:
            use = f"use {', '.join(sorted(never_lists))}, or write it" if never_lists else "write it"
            problems.append(f"{where}: no list named {ref!r}: {use} under `never`")
        elif never_lists[ref] is not None:
            uses_never[name] = never_lists[ref]
    return uses_never
```
(the local `never, mask = sending(...)` at line 197 is `review.never` and stays.)

`xarch/modules/spec/domain/key_table.py`, line 192:
```python
_NEVER_USE = (*_IMPORTS, "use", "method_call")
```
line 206:
```python
    "parts.<part>.uses.never": _NEVER_USE,
```
line 210:
```python
    "tiers.<tier>.uses.apply_never": _NEVER_USE,
```

Then check:
```bash
grep -rn 'forbidden\|FORBIDDEN\|\blists\b' xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/domain/key_table.py xarch/modules/spec/application/logic/profile_checks.py
```
Expected: only prose lines holding the English word "lists" (docstrings and messages such as line 23 "a part that
lists none", 449 "The named lists of names", 451 "lists of dotted names"), no identifier named `lists`, no
`forbidden` and no `FORBIDDEN`.

- [ ] **Step 4: Run the spec logic tests to see them pass**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/spec 2>&1 | tail -5
```
Expected: PASS, no error.

- [ ] **Step 5: Lint and the whole suite**

```bash
uv run ruff check
timeout 1500 uv run pytest -q > /tmp/xarch-2-4/task3-pytest.txt 2>&1; echo "exit $?"
tail -n 3 /tmp/xarch-2-4/task3-pytest.txt
```
(pytest in the background, read at the end.) Expected: ruff `All checks passed!` (if `I001` reports the import of
Step 1, the names are not in sorted order: put them as `dotted_names, is_name, never_names` by hand, never `--fix`);
pytest `exit 0`, no failure.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py \
  xarch/modules/spec/domain/key_table.py tests/modules/spec/application/logic/test_profile_checks.py
git status --short
git commit -m "$(cat <<'EOF'
The parser names what it reads of never and uses.never by the new keys: never_names parses one list, _never_lists the block never into never_lists, _never_refs resolves each part's uses.never into uses_never, and the key table's reader kinds for uses.never and uses.apply_never are _NEVER_USE; no output changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: The tests' own names

**Files:**
- Move: `tests/bootstrap/test_forbidden.py` → `tests/bootstrap/test_never_use.py`
- Move: `tests/modules/rules/application/logic/test_forbidden.py` → `tests/modules/rules/application/logic/test_never_use.py`
- Move: `tests/modules/spec/application/logic/test_forbidden.py` → `tests/modules/spec/application/logic/test_never_use.py`
- Modify: `tests/modules/rules/application/logic/checks.py:30`
- Modify: the moved files (docstring line 1 of two of them, the import at line 5 of the rules one, the test names of
  bootstrap 25 and spec 189)
- Modify: `tests/modules/rules/application/logic/test_stand_ins.py:223`
- Modify: `tests/bootstrap/test_where.py:39`
- Modify: `tests/modules/rules/application/logic/test_where.py:91, 225, 272`
- Modify: `tests/modules/spec/application/logic/test_profile_parsing.py:389`

**Interfaces:**
- Consumes: Tasks 1-2 (the moved files already hold the renamed field names).
- Produces: the test helper `tests.modules.rules.application.logic.checks.never_use(app: Iterable[SourceFile], tests:
  Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]` (was `forbidden`).

These are renames of tests themselves: no failing run is needed (spec, "Tests"). The proof is the same number of tests
passing before and after.

- [ ] **Step 1: Count the tests before**

```bash
timeout 600 uv run pytest -q --collect-only tests/bootstrap/test_forbidden.py tests/modules/rules/application/logic/test_forbidden.py tests/modules/spec/application/logic/test_forbidden.py tests/modules/rules/application/logic/test_stand_ins.py tests/bootstrap/test_where.py tests/modules/rules/application/logic/test_where.py tests/modules/spec/application/logic/test_profile_parsing.py 2>&1 | tail -n 1 | tee /tmp/xarch-2-4/task4-before.txt
```
Expected: one line `N tests collected`. Keep `N`.

- [ ] **Step 2: Move the three files**

```bash
ls tests/bootstrap/test_never_use.py tests/modules/rules/application/logic/test_never_use.py tests/modules/spec/application/logic/test_never_use.py 2>&1
git mv tests/bootstrap/test_forbidden.py tests/bootstrap/test_never_use.py
git mv tests/modules/rules/application/logic/test_forbidden.py tests/modules/rules/application/logic/test_never_use.py
git mv tests/modules/spec/application/logic/test_forbidden.py tests/modules/spec/application/logic/test_never_use.py
```
Expected: the `ls` reports `No such file or directory` for all three (stop if any exists); the moves succeed.

- [ ] **Step 3: Rename the helper and the names inside the moved files**

`tests/modules/rules/application/logic/checks.py`, line 30:
```python
def never_use(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
```

`tests/modules/rules/application/logic/test_never_use.py`, line 1 (line 2 stays):
```python
"""The never-use check on a hand-built profile: a file of a part neither imports a module its list names nor uses a
```
line 5:
```python
from tests.modules.rules.application.logic.checks import never_use as violations
```

`tests/bootstrap/test_never_use.py`, line 1 (line 2 stays):
```python
"""The never-use check on a throwaway web project, as the bundled profile lists it: the pure parts may not read the
```
line 25:
```python
def test_a_pure_part_never_uses_what_the_bundled_profile_lists_for_it(tmp_path, path, body, problem):
```

`tests/modules/spec/application/logic/test_never_use.py`, line 189 (its module docstring does not say "The forbidden
check" and stays):
```python
def test_the_guards_section_lists_the_names_each_part_never_uses_and_says_what_it_does_not_see():
```

- [ ] **Step 4: Rename the other test functions**

`tests/modules/rules/application/logic/test_stand_ins.py`, line 223:
```python
def test_mocks_in_a_test_barred_from_the_fakes_are_not_checked(path):
```

`tests/bootstrap/test_where.py`, line 39:
```python
def test_a_file_in_a_part_says_its_part_role_litmus_imports_libraries_never_uses_and_test():
```

`tests/modules/rules/application/logic/test_where.py`, line 91:
```python
def test_code_in_a_part_gets_its_role_litmus_imports_libraries_never_uses_and_test():
```
line 225:
```python
def test_a_test_of_a_tier_not_held_to_the_lists_never_uses_none_and_a_tier_s_types_only_parts_are_shown():
```
line 272:
```python
def test_a_test_of_a_listed_part_in_a_tier_not_held_to_the_list_is_told_no_never_uses():
```

`tests/modules/spec/application/logic/test_profile_parsing.py`, line 389:
```python
def test_a_part_refers_to_a_list_under_never_by_its_name():
```

- [ ] **Step 5: Run the moved and renamed tests and count them**

```bash
timeout 600 uv run pytest -q tests/bootstrap/test_never_use.py tests/modules/rules/application/logic/test_never_use.py tests/modules/spec/application/logic/test_never_use.py tests/modules/rules/application/logic/test_stand_ins.py tests/bootstrap/test_where.py tests/modules/rules/application/logic/test_where.py tests/modules/spec/application/logic/test_profile_parsing.py 2>&1 | tail -n 2
cat /tmp/xarch-2-4/task4-before.txt
git diff -M --stat HEAD
```
Expected: `N passed` with the `N` of Step 1; the stat shows the three renames (`test_forbidden.py => test_never_use.py`)
with only the lines of Step 3 changed in them.

- [ ] **Step 6: Lint and the whole suite**

```bash
uv run ruff check
timeout 1500 uv run pytest -q > /tmp/xarch-2-4/task4-pytest.txt 2>&1; echo "exit $?"
tail -n 3 /tmp/xarch-2-4/task4-pytest.txt
```
(pytest in the background, read at the end.) Expected: ruff `All checks passed!`; pytest `exit 0`, the same count
as after Task 3, no failure.

- [ ] **Step 7: Commit**

```bash
git add tests/bootstrap/test_never_use.py tests/modules/rules/application/logic/test_never_use.py \
  tests/modules/spec/application/logic/test_never_use.py tests/modules/rules/application/logic/checks.py \
  tests/modules/rules/application/logic/test_stand_ins.py tests/bootstrap/test_where.py \
  tests/modules/rules/application/logic/test_where.py tests/modules/spec/application/logic/test_profile_parsing.py
git status --short
git commit -m "$(cat <<'EOF'
The never-use tests are named for the rule: the three test_forbidden.py files are test_never_use.py, the check helper is never_use, and the test names that said may_not_use or forbidden_names say never_uses, lists for it, barred from the fakes or a list under never; no test's expected value changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```
Expected: `git status` before the commit shows the three renames as `R` and the five modified files, nothing else but
`?? docs/superpowers/...`.

---

### Task 5: CHANGELOG, golden docs, re-grep, snapshot and gates

**Files:**
- Modify: `CHANGELOG.md` (one entry at the end of `[Unreleased]` → `### Changed`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: nothing new.

- [ ] **Step 1: The CHANGELOG line**

Read `CHANGELOG.md` from line 6 to the next `## [` heading and find the last entry of `### Changed` under
`[Unreleased]` (the `may-import` entry that starts "- The rule id `rules` is renamed `may-import`"). After its last
line, leave one blank line and add:

```markdown
- Internal names follow the 0.3.0 key names: the fields and functions that read `uses.never` and `uses.apply_never`
  say `uses_never`, `apply_never` and `never_lists` in place of `forbidden`; no output changes.
```

Check:
```bash
git diff -- CHANGELOG.md
```
Expected: three added lines (the blank line and the two of the entry), nothing removed.

- [ ] **Step 2: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-2-4/regenerate_docs.py`:

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:
```bash
uv run python -I /tmp/xarch-2-4/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
```
Expected: `written`; `git status` shows nothing under `docs/` but `?? docs/superpowers/...`; `git diff --stat` prints
nothing. Any moved line is a bug of this task's earlier renames (most likely `_never_use_line` in
`docs_template.py`): do not hand-edit it; restore with `git checkout -- docs/cli docs/web docs/xarch`, find the rename
that changed it, and report the hunk.

- [ ] **Step 3: Re-grep B7.1 (`may_not_use`)**

```bash
grep -rn 'may_not_use\|may-not-use' xarch tests README.md CHANGELOG.md architecture.yaml docs --exclude-dir=superpowers
```
Expected: no output.

- [ ] **Step 4: Re-grep B7.2 (`forbidden` as a word)**

```bash
grep -rnw forbidden xarch tests docs README.md CHANGELOG.md architecture.yaml --exclude-dir=superpowers | cut -d: -f1 | sort | uniq -c
```
Expected, exactly (the lines B4 keeps, and the new CHANGELOG line):
```
      3 CHANGELOG.md
      1 docs/cli/architecture.md
      1 docs/templates/architecture.md
      1 docs/web/architecture.md
      1 docs/xarch/architecture.md
      3 tests/bootstrap/test_architecture_files.py
      2 tests/bootstrap/test_profile_explain.py
      1 tests/bootstrap/test_where.py
      1 tests/architecture/test_self_check.py
      3 tests/cli/reports/test_where_report.py
     19 tests/modules/spec/application/logic/test_never_use.py
      7 tests/modules/spec/application/logic/test_retired_keys.py
      4 tests/modules/spec/application/logic/test_written_checks.py
      3 tests/modules/spec/application/test_explain.py
      3 tests/modules/spec/domain/test_profile_keys.py
      1 xarch/architectures/cli.md
      1 xarch/architectures/web.md
      3 xarch/modules/spec/domain/profile_keys.py
```
(`sort` may order `tests/architecture` before `tests/bootstrap`; compare the set of files and counts, not the order.)
Then read the lines themselves:
```bash
grep -rnw forbidden xarch tests docs README.md CHANGELOG.md architecture.yaml --exclude-dir=superpowers | cut -c1-160
```
Expected: every line is one of: the retired-names table (`profile_keys.py:160, 162, 163`) and its tests
(`test_profile_keys.py`, `test_retired_keys.py`, `test_explain.py`, `test_profile_explain.py`,
`test_architecture_files.py`); the yaml keys and expected refusal messages in the spec `test_never_use.py`
(`service_writing(forbidden=...)`, `covered(forbidden=...)`, `{"forbidden": ...}`, `hints={"forbidden": ...}`,
`unknown key 'forbidden'`, `hints.forbidden`); the JSON-field-gone asserts (`test_where_report.py:37, 44, 49`,
`tests/bootstrap/test_where.py:117`); `test_written_checks.py:114-122`; English prose (`cli.md:130`, `web.md:130`,
`docs/templates/architecture.md:100`, the generated `docs/{cli,web,xarch}/architecture.md` lines,
`test_self_check.py:61`); `CHANGELOG.md` 23, 47 and the new line. Any other line is an identifier missed: rename it
in the task that owns it, rerun that task's tests, and amend nothing — make a new commit.

- [ ] **Step 5: Re-grep B7.3 and B7.4**

```bash
grep -rn 'FORBIDDEN\|\b_forbidden\|forbidden_names' xarch tests --exclude-dir=corpora
echo ---
grep -rn 'FORBIDDEN\|\b_forbidden\|forbidden_names' tests/bootstrap/corpora | cut -c1-90
echo ---
grep -rnw never xarch/modules/spec/domain/values.py xarch/modules/spec/contract/__init__.py | cut -c1-120
```
Expected: the first grep prints nothing. The second prints exactly the two recorded lines
`tests/bootstrap/corpora/7cc6111.json:1400:` and `:1401:` (archived findings, B4, not edited). The third prints
`never` only on the `review.never` fields and prose:
`xarch/modules/spec/contract/__init__.py:153` (prose, `review.never`), `:172` (`never: tuple[str, ...] = ()`),
`xarch/modules/spec/domain/values.py:79`, `:207`, `:210` (prose "never call", "never decides"), `:208` (the
`apply_never:` docstring line, which matches on `uses.never`), `:366` (prose of `review.never`), `:401`
(`never: tuple[str, ...] = ()`). No line where a field holding the lists is named bare `never`.

- [ ] **Step 6: Compare the snapshot**

```bash
bash /tmp/xarch-2-4/snapshot.sh /tmp/xarch-2-4/after
for f in check.json check-strict.json where-part.txt where-part.json where-test.txt where-test.json where-guard.json explain-never.json explain-apply-never.json profile-check.txt; do
  cmp -s /tmp/xarch-2-4/before/$f /tmp/xarch-2-4/after/$f && echo "same $f" || echo "DIFFERS $f"
done
sed -E '/^(Tier|CheckedTier) /s/ forbidden( |$)/ apply_never\1/; /^(Architecture|PartView|Profile|PartPlace|SuitePlace|InPart|InTests) /s/ forbidden( |$)/ uses_never\1/' /tmp/xarch-2-4/before/fields.txt | diff - /tmp/xarch-2-4/after/fields.txt && echo "fields: only the renames, in place"
```
Expected: `same` for all ten files, and `fields: only the renames, in place`. A `DIFFERS` is a behaviour change: run
`diff /tmp/xarch-2-4/before/<f> /tmp/xarch-2-4/after/<f>`, find the rename that caused it, fix it in a new commit,
and rerun this step.

- [ ] **Step 7: The gates**

```bash
uv run ruff check
timeout 300 uv run xarch check; echo "exit $?"
timeout 300 uv run xarch check --strict; echo "exit $?"
timeout 120 uv run xarch profile check architecture.yaml | tail -n 1
timeout 1500 uv run pytest -q > /tmp/xarch-2-4/task5-pytest.txt 2>&1; echo "exit $?"
tail -n 3 /tmp/xarch-2-4/task5-pytest.txt
```
(pytest in the background, read at the end.) Expected: ruff `All checks passed!`; both `xarch check` runs `exit 0`;
`OK: the profile is valid`; pytest `exit 0`, no failure, the same count as after Task 4. Then confirm no recorded
corpus moved:
```bash
git diff --stat c7d6127 -- tests/bootstrap/corpora docs/examples docs/cli docs/web docs/xarch
```
Expected: no output.

- [ ] **Step 8: Commit**

```bash
git add CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
The CHANGELOG says the internal names follow the 0.3.0 key names: the fields and functions that read uses.never and uses.apply_never say uses_never, apply_never and never_lists in place of forbidden, and no output changes; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
git log --oneline c7d6127..HEAD
```
Expected: `git status` before the commit shows only `M CHANGELOG.md` staged and `?? docs/superpowers/...`; the log
shows five commits (Tasks 1-5) on top of `c7d6127` plus the workflow's docs commit if it has run.
<!-- task-pipeline: validated -->
