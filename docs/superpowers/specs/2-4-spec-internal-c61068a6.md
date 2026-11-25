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
