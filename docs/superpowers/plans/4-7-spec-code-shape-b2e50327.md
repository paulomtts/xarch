# 4.7 Code-shape internal names follow the 0.3.0 keys — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename xarch's Python identifiers for a part's and a tier's import and shape settings to their 0.3.0 key
addresses (`imports_must`, `imports_may`, `imports_also`, `imports_types_only`, `imports_libraries`, `holds_names`,
`holds_immutable`, `holds_built_by`, and five functions), with nothing a user or a profile sees changing.

**Architecture:** A pure rename in five commits, one per group of values (tier values; part values in spec and its
contract; rules' `Profile`; functions), then a closing task that fixes the last stale docstring, re-greps, diffs every
observable output against a baseline recorded before any edit, regenerates the golden docs (empty diff) and runs the
gates. Every edit is an exact text replacement applied by a small script that refuses to write anything unless each
pattern is seen exactly the expected number of times, so a moved line or a missed site stops the task instead of
slipping through. Tests are edited first (RED: `TypeError`/`AttributeError`/`ImportError`), then the code (GREEN).

**Tech Stack:** Python 3.13, `uv`, `pytest`, `ruff`, xarch's own `xarch check` / `xarch profile check`.

**Spec:** `docs/superpowers/specs/4-7-spec-code-shape-b2e50327.md` (prepended below, verbatim).

## Global Constraints

- Nothing a user or a profile sees changes: every command prints the same bytes for the same input; every refusal,
  finding, sentence, rule id, JSON key and generated doc is the same (spec 1, 2.1).
- Only Python identifiers (dataclass fields, keyword arguments, functions, local names) and the docstrings that name
  them change. Every string literal stays as it is, e.g. `{"built_by": profile.holds_built_by}` keeps `"built_by"`.
- A field keeps its position in its dataclass (several are built positionally, e.g. `checked_tier.py:13-15`,
  `publishing.py:59-61`, `profile_parsing.py:226-229`).
- Kept names (spec 2.3): `where`'s answer fields (`may_import`, `may_import_text`, `libraries`, `types_only` in
  `rules/domain/places.py`, `rules/contract/__init__.py`, `locate.py`, `where_report.py`); identifiers named for a
  rule id (`_must_import`, `_must_import_tiers`, `_no_callbacks`, `_types_only*`, `_names`, `_built_by`, `_libraries`,
  `_immutable`, `_holds`, `_rules` in `expansion.py`; `_must_import_line`, `_tier_must_import_line` in
  `docs_template.py`; the test helpers `must_import`, `must_import_tiers`, `types_only` in
  `tests/modules/rules/application/logic/checks.py`); every guard's snake-case field (`no_callbacks`); `may-import-everything`,
  `mirrored_may_import` and their functions; `Held.names/immutable/built_by`; `Profile.holds`, `Part.holds`;
  `Architecture.rules`, `Profile.rules`; the retired-keys table `xarch/modules/spec/domain/profile_keys.py:194-218`
  and its refusal tests; test function names and `pytest.param` ids; `docs/examples/**`; `tests/bootstrap/corpora/**`.
- No expected value in any test changes; no corpus, no golden doc, no recorded finding is edited by hand (O8).
- No README or CHANGELOG line (O4, O5: nothing user-visible changes).
- No comment is added anywhere. Line length is 140 (`ruff.toml`); `uv run ruff check` is run without `--fix`.
- Commits: one per task, the message saying what was renamed to what and that nothing a user sees changes; never
  stage `.claude/`; never push. Run long commands under `timeout`; never `pkill`/`killall`.
- Scratch files live outside the worktree: scripts in `/tmp/xarch-4-7/`, the baseline in `/tmp/xarch-4-7-base/`,
  the after-run in `/tmp/xarch-4-7-after/`. None is committed.

## Review Focus

1. **A renamed field still read by its old name on a path no test reaches** (e.g. a branch of `looseness.py` or
   `docs_template.py` only a bundled profile exercises) — expected: nothing is left; pinned by Task 6's re-grep
   (every hit classed) and by the byte-for-byte diff of `profile check cli/web/architecture.yaml` and the
   regenerated docs against the Task 1 baseline.
2. **A string literal changed along with an identifier** (a dict key such as `"built_by"` in `filters.py:195`, a
   rule key such as `f"parts.{part}.imports.libraries"`, a refusal text) — expected: unchanged output; pinned by
   Task 6's diff of `check --format json`, `check --strict --format json`, every `profile explain` address and the
   golden docs, and by the rule that the edit scripts only touch the exact patterns they list.
3. **A `where` JSON field renamed with the profile fields** (`may_import`, `may_import_text`, `libraries`,
   `test.types_only`) — expected: `where --format json` identical; pinned by Task 6's diff of the 19 `where`
   outputs (one file of each of the 15 parts, one test of each of the 4 tiers) against the baseline.
4. **A retired key no longer refused, or refused with another text** (`may_import`, `must_import`,
   `may_also_import`, `types_only`, `no_callbacks`, `names`, `immutable`, `built_by` on a part) — expected: same
   problem text and exit code; pinned by the untouched refusal tests and Task 6's diff of `profile explain
   parts.may_import`, `tiers.may_also_import`, `parts.no_callbacks` (exit 2 on the base and after).
5. **A field moved position in a positionally built dataclass** (`CheckedTier`, `PartView`, `Architecture`,
   `Tier`) — expected: same values in the same slots; pinned by the edit scripts, which rename the field line in
   place (never move it), and by the full suite, which builds each positionally.

---

## The spec

# 4.7 spec: code-shape internal names follow the 0.3.0 keys of parts and tiers

Card `b2e50327`, subtask of `c34d7f47`, blocked by `20b1e1ce` (4.6, a tier's `imports` group, done on this branch at
`293ab8c`). Release step 15 of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`,
below **R3**, section 3, line 278: "Code-shape internal names. | code-shape 7 | Step 14.").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Default (CS 65-66): "internal identifiers follow each rename as the note's last step". This step is that last step.
- Rulings 4 and 6 (CS 14-24, 47-49): `holds` is a map of kinds, the settings `names`, `immutable`, `built_by` sit under
  a kind. Ruling 5 (CS 26-28), 12 (CS 52-53), 14 (CS 57): a part's `imports: {may, must, libraries}` with the mark
  `types_only` on an entry of `may`; a tier's `imports: {may, also, must, types_only}`. These are the "two rulings" the
  card's "both rulings" means (CS 817: "for both rulings").
- Ruling 7 and section 4 (CS 645-660, line 651): the guard is `no-callbacks`, its value field `GuardsView.no_callbacks`.
  The snake-case field of the guard is therefore already the 0.3.0 name, as `pass_through` and `package_only` are.
- 3.8 (CS 600-623): rule ids do not change (CS 602-604); `where`'s JSON keeps `may_import`, `may_import_text`,
  `libraries` and `test.types_only` (CS 615-618); the filter keeps its name `may-import-everything` and the variable
  `mirrored_may_import` keeps its name, only their texts moved (CS 619-620, done in 4.5 and 4.6).
- 5.1 item 16 (CS 705-706): not changed: `review`, rule ids, the README id list, `where`'s JSON fields.
- 7 items 7 and 8 (CS 817-822): this step and its re-grep. Gates (CS 828-829).
- Dodges (CS 948-976) the card names: renaming `where`'s JSON fields (CS 970); any behaviour change, and "changing ...
  `review`'s ruled-out parts under cover of the move" (CS 971-972).
- "Not verified" (CS 1008) and "Facts read" (CS 78-79): `libraries`, `holds`, `immutable` and `names` are also English
  words, so the re-grep's `^\s+(names|...):` arm finds unrelated fields; section 4 below lists them.

R3 rules inherited: **O4**, **O5** (R3 228-229): any README or CHANGELOG line of this step goes under `[Unreleased]`
(this step expects none: nothing a user sees changes); **O8** (R3 232): the golden docs `docs/{cli,web,xarch}/testing.md`
are regenerated and their diff read, never edited by hand; for this step the diff must be empty.

## 1. Goal

xarch's own code names each import and shape setting of a part or tier by its 0.3.0 address, so that an agent reading
`part.imports_must` finds `imports.must` in the profile and the key table, and nobody meets `may_import`,
`must_import` or `may_also_import` as the name of a value that a profile no longer writes.

Nothing a user or a profile sees changes: every command prints the same bytes for the same input, every refusal,
finding, sentence, rule id, JSON key and generated doc is the same. Only Python identifiers (dataclass fields, keyword
arguments, functions, local names) and the docstrings that name those identifiers change.

## 2. Behavior

### 2.1 Observable behavior: none changes

For the same working tree content outside `xarch/` and `tests/`, these are byte-identical before (base `293ab8c`) and
after the step:

1. `uv run xarch check --format json` and `uv run xarch check --strict --format json` on xarch itself (exit codes too).
2. `uv run xarch profile check architecture.yaml` (stdout and exit code), and `uv run xarch profile check cli`,
   `... web`.
3. `uv run xarch where --format json <path>` for one file of every part of xarch's own profile and one test file of
   every tier (the JSON keys `may_import`, `may_import_text`, `libraries`, `never_uses`, `test.types_only` among them).
4. `uv run xarch profile explain <address>` for the addresses `parts.imports.may`, `parts.imports.must`,
   `parts.imports.libraries`, `tiers.imports.also`, `tiers.imports.types_only`, `parts.holds.classes.built_by`,
   `guards.no-callbacks`, and the retired `parts.may_import`, `tiers.may_also_import`, `parts.no_callbacks`.
5. Every file `spec.docs(<profile>)` generates for `cli`, `web` and `architecture.yaml`, written over
   `docs/cli`, `docs/web`, `docs/xarch`: `git diff docs/` is empty (this covers the golden `testing.md` copies and
   `docs/xarch/architecture.md`).
6. `tests/bootstrap/corpora/` is not touched: `git diff --stat <base> -- tests/bootstrap/corpora` is empty.
7. `uv run xarch review --offline --all --format json` (`--max-files` is refused with `--all`; a smoke check only: with no
   kept answers in a worktree it reads no file; the report says so).
8. `uv run pytest -q`: the same number of tests collected and passed as on the base, none skipped that was not skipped
   before. A test may be renamed only where its own name is a renamed identifier (none is expected: test names say
   behaviour, and stay).

Error paths: a profile that writes a retired key (`may_import`, `must_import`, `may_also_import`, `types_only` on a part,
`no_callbacks`, `names`, `immutable`, `built_by` on a part) is refused with the same problem text and exit code as on
the base. The retired-keys table `xarch/modules/spec/domain/profile_keys.py:194-218` is not edited.

### 2.2 The renames

The rule: a value that a profile key fills is named by the key's address below its owner, the dots written `_`:
`imports.must` → `imports_must`, `holds.<kind>.names` gathered by part → `holds_names`. A field keeps its position in
its dataclass (several are built positionally, e.g. `spec/application/logic/checked_tier.py:13-15`). Only Python
identifiers change: every string literal stays as it is, including dict keys a check reads by word (e.g.
`{"built_by": profile.built_by}` in `rules/application/logic/filters.py:195` keeps `"built_by"`; it becomes
`{"built_by": profile.holds_built_by}`).

Fields:

| Value (file:line on the base) | Old field | New field |
|---|---|---|
| `Part`, `spec/domain/values.py:94` | `must_import` | `imports_must` |
| `Part`, `spec/domain/values.py:96` | `types_only` | `imports_types_only` |
| `Tier`, `spec/domain/values.py:227` | `types_only` | `imports_types_only` |
| `Tier`, `spec/domain/values.py:230` | `may_import` | `imports_may` |
| `Tier`, `spec/domain/values.py:231` | `must_import` | `imports_must` |
| `Tier`, `spec/domain/values.py:233` | `may_also_import` | `imports_also` |
| `Architecture`, `spec/domain/values.py:404` | `libraries` | `imports_libraries` |
| `CheckedTier`, `profile_values/tiers.py:21,27,28,30` | `types_only`, `may_import`, `must_import`, `may_also_import` | `imports_types_only`, `imports_may`, `imports_must`, `imports_also` |
| `PartView`, `spec/contract/__init__.py:102,108,110` | `may_import`, `must_import`, `types_only` | `imports_may`, `imports_must`, `imports_types_only` |
| `ProfileView`, `spec/contract/__init__.py:158` | `libraries` | `imports_libraries` |
| `Profile`, `rules/domain/profile.py:84` | `libraries` | `imports_libraries` |
| `Profile`, `rules/domain/profile.py:96` | `must_import` | `imports_must` |
| `Profile`, `rules/domain/profile.py:108` | `immutable` | `holds_immutable` |
| `Profile`, `rules/domain/profile.py:109` | `types_only` | `imports_types_only` |
| `Profile`, `rules/domain/profile.py:111` | `names` | `holds_names` |
| `Profile`, `rules/domain/profile.py:112` | `built_by` | `holds_built_by` |

Functions:

| File:line on the base | Old name | New name | Why the new name |
|---|---|---|---|
| `kernel/logic/imports.py:15` | `may_import` | `targets_phrase` | it says any targets as the docs' phrase; it renders `imports.must` too (`docs_template.py:634`) |
| `spec/application/logic/targets_written.py:18` | `may_import` | `allowed_targets` | it reads a part's or tier's `imports.may` and a tier's `imports.also` |
| `spec/application/logic/docs_template.py:193` | `_may_import` | `_imports_may_phrase` | the rules-table cell of a part's `imports.may` |
| `rules/application/logic/tier_of.py:97` | `_may_import` | `_folder_imports` | what the tests in a tier's own folder may import |
| `spec/application/logic/profile_parsing.py:450` | `_libraries` | `_imports_libraries` | it reads `imports.libraries` |

Every caller, import and keyword argument of these follows (the explore list: `looseness.py:81,94-95`,
`publishing.py:61`, `profile_parsing.py:92,196,655-657`, `imports_written.py:23,61,68,88`, `where.py:24,104,105,208`,
`docs_template.py:57,195,441-442,553,634`, `checked_tier.py:14-15`, `spec_profile.py:62-81`, `expansion.py` (every
`profile.<field>` and `tier.<field>` of the table above), `tier_of.py:100-113`, `sentences.py:112,148,167,179`,
`filters.py:106,195`, `locate.py:65` (`tier.types_only`), and any other the type of a renamed field reaches). Local
variables named exactly `may_import`, `must_import`, `may_also_import` in touched code take the new word too.

Docstrings that name a renamed field or function by its identifier are updated in the same edit (`Part` 80-84, `Tier`
204-213, `CheckedTier`, `PartView`, `Profile` 46-75, `Architecture` 366, 379; `published.py`'s `Loosened` docstring already names `imports.*`, so it is checked and not
edited). No comment is added anywhere.

### 2.3 What keeps its name, and why

- `where`'s answer: `rules/domain/places.py:55-56,97` (`may_import_text`, `libraries`), `rules/contract/__init__.py:197-199,
  236-238` (`may_import`, `may_import_text`, `libraries`, `types_only`), `rules/application/services/locate.py:52,65`
  (the fields it fills), `cli/reports/where_report.py`. These are the `where` JSON fields one for one (CS 615-618,
  dodge CS 970); renaming the Python side while keeping the JSON words would add a translation for no reader.
- Identifiers named for a rule id, which does not change (CS 602-604): in `expansion.py` the functions of `book`
  (`_must_import`, `_must_import_tiers`, `_no_callbacks`, `_types_only_*`, `_names`, `_built_by`, `_libraries`,
  `_immutable`, `_holds`, `_rules`); in `docs_template.py` `_must_import_line` and `_tier_must_import_line`, which
  render the docs line headed `` `must-import`: ``.
- The guard `no-callbacks` in snake case, as every guard's field is: `GuardsView.no_callbacks`
  (`spec/contract/__init__.py:137`), `Profile.no_callbacks` (`rules/domain/profile.py:110`), `no_callbacks=` in
  `publishing.py:109` and `spec_profile.py:81` (CS 651).
- The check language's own words, which profiles write: the filter `may-import-everything` and its function
  `_may_import_everything` (`filters.py:72,84`), the variable `mirrored_may_import` and its function
  `_mirrored_may_import` (`sentences.py:88,144`, `vocabulary.py:372`) (CS 619-620).
- `Profile.holds` and `Part.holds`/`PartView.holds` (already the key), `Held.names`, `Held.immutable`, `Held.built_by`
  (`spec/domain/published.py:60-62`: settings nested under a kind, CS 820).
- `Architecture.rules` and `Profile.rules` (the targets of each part's `imports.may`). The re-grep does not name them,
  `rules` is also the module and the docs' rules table, and the rule id `may-import`'s function is `_rules`; renaming
  them is a 180-site change no ruling asks for. Named here so a reviewer does not read it as missed; the owner may ask
  for it as its own step.
- The retired-keys table and its refusal tests (`tests/modules/spec/application/logic/test_retired_keys.py` and the
  other tests that write a retired key to see it refused).
- Test function names and `pytest.param` ids: they describe behaviour in words (e.g.
  `test_the_import_rule_is_may_import_first...`, `id="mirrored_may_import"`).
- `docs/examples/**` (illustrative code quoted by `docs/xarch/architecture.md`): editing it changes a generated doc,
  which is output.

## 3. The re-grep (CS 818-822)

```bash
K="immutable|names|built_by|types_only|libraries"
grep -rnE "no_callbacks|may_import|must_import|may_also_import|^\s+($K):" xarch tests architecture.yaml
```

After the step every hit is in one of these classes, and the plan records the full output once, classed line by line,
in its last task's report (not in a committed file):

1. The retired-keys table, `xarch/modules/spec/domain/profile_keys.py:194-218`, and the tests that write a retired key
   to see it refused.
2. Settings nested under a kind of `holds` (`Held.names/immutable/built_by`; `names:`/`built_by:`/`immutable:` inside a
   `holds:` map in a profile or a test profile).
3. Keys nested under `imports` in a profile or a test profile (`libraries:`, `types_only:` at six or more spaces), and
   `xarch/architectures/presets/format/keys.yaml` (the format's catalogue of keys, whose text names old and new keys).
4. The filter `may-import-everything` and the variable `mirrored_may_import`, with their functions and tests.
5. The `where` JSON fields and the `where` answer values of 2.3.
6. The guard `no-callbacks` in snake case (2.3), and identifiers named for a rule id (2.3).
7. Prose: docstrings, test names, `pytest.param` ids, and strings that quote a retired key.
8. Fields that share an English word and name no key of a part or tier (CS 1008), each one of: `kernel/source.py:22`,
   `layout/domain/structure.py:32`, `scaffold/domain/values.py:38`, `spec/contract/__init__.py:74`,
   `spec/domain/values.py:335` (`Language.names`), `profile_values/placement.py:27` (`Target.names`),
   `profile_values/language.py:92,94`, `review/contract/__init__.py:304`, `rules/domain/rule.py:72,470`,
   `rules/domain/parsed.py:138`, `rules/application/ports/source_tree.py:24`, `rules/adapters/fs_source_tree.py:157,562,
   1003`, `rules/application/logic/twins.py:183`, `spec/application/logic/never_lists.py:30,143`, `tests/fakes/
   filesystem.py:45`, `tests/architecture/test_agnostic.py:53`, `tests/architecture/test_language_seam.py:260,491`,
   and the like in tests (line numbers move; the class is "a local or field of the same word unrelated to profiles").

Any hit outside these classes is a defect of this step, fixed in the commit of the task that owns its file.

## 4. Tests

No test is added: the behaviour is unchanged by definition, and the existing suite pins it. Tests are written first in
the sense the project means for a rename: in each task, the tests that name a renamed identifier (they build a `Part`,
`Tier`, `CheckedTier`, `PartView`, `ProfileView` or `Profile` by keyword, read one of its fields, or call a renamed
function) are edited first, run, and seen failing with `TypeError: ... unexpected keyword argument` or
`AttributeError` / `ImportError`; then the code is renamed and they pass.

The tests that change, each staying in its tier (as `uv run xarch where <file>` reports it; the reason it is there is unchanged):

| File | Tier | What changes |
|---|---|---|
| `tests/modules/spec/application/logic/test_tiers.py`, `test_checked_tier.py`, `test_profile_parsing.py`, `test_profile_parsing_tests.py`, `test_profile_parsing_substance.py`, `test_imports_written.py`, `test_targets_written.py`, `test_docs_template.py`, `test_looseness.py`, `test_profile_view.py`, `test_libraries_and_guards.py`, `test_written_checks.py`, `test_example_imports.py`, `test_hints.py`, `test_profile_needs.py`, `test_profile_parsing_docs.py` | unit (spec's logic, one function under test each) | field and function names |
| `tests/modules/spec/application/test_profile.py`, `test_explain.py`, `test_origin.py` | integration (spec's controller around fakes) | field names |
| `tests/modules/rules/application/logic/test_tier_imports.py`, `test_must_import.py`, `test_no_callbacks.py`, `test_expansion.py`, `test_expandable.py`, `test_where.py`, `test_sentences.py`, `test_libraries.py`, `test_places.py`, `test_ordered.py`, `checks.py` | unit (rules' logic) | `Profile(...)` and `CheckedTier(...)` keywords, field reads |
| `tests/modules/rules/application/test_locate.py`, `test_words.py` | integration (rules' controller around fakes) | the same |
| `tests/modules/rules/adapters/test_spec_profile.py` | unit (an adapter's translation of spec's contract) | `PartView`/`ProfileView` and `Profile` fields |
| `tests/kernel/logic/test_imports.py` | unit (kernel logic) | `may_import` → `targets_phrase` |
| `tests/bootstrap/test_bundled_imports.py`, `test_bundled_guards.py`, `test_where.py`, `test_profile_explain.py`, `test_needs_agree.py`, `test_bundled_architectures.py`, `test_check_enforcement.py`, `test_repeating_folders.py`, `test_profile_file.py`, `test_docs.py`, `test_profile_explain_words.py` | wired (the bundled profiles as they ship, through bootstrap) | field reads only; their expected values do not change |
| `tests/cli/reports/test_where_report.py` | unit (the report's translation) | nothing expected: it reads `where` fields, which keep their names; listed so the reviewer checks it is untouched |

The list is from the explore grep and is an upper bound; a file whose only hit is a kept name (2.3) or a retired key in
a refusal test is not edited. No expected value in any test changes: an edit to an expected string, a recorded
finding, or a corpus is a sign of a behaviour change and is refused.

Proof beyond the suite (gates, not tests, recorded to a scratch folder outside the worktree and diffed, never
committed): the commands of 2.1 items 1-4 and 7, run on the base before any edit and again at the end; items 5 and 6 by
regenerating and `git diff`.

## 5. Gates

Each passes on this branch alone, the full suite green: `uv run pytest -q` (over two minutes: run it in the background
and read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml` (CS 828-829). No typecheck command exists. Plus 2.1 and the re-grep of 3.

## 6. Hand-off to the planner

Follow the writing-plans format. Suggested tasks, each leaving the suite green and committed on its own:

1. Before any edit: record the outputs of 2.1 items 1-4 and 7 and the `pytest -q` summary line to a scratch folder
   outside the worktree (e.g. under `/tmp/xarch-4-7-base/`).
2. Tier values: `Tier` and `CheckedTier` fields, `checked_tier.py`, and every reader (`tier_of.py`, `expansion.py`,
   `sentences.py`, `looseness.py`, `docs_template.py`, `locate.py`, `profile_parsing.py`'s tier reader), tests first.
3. Part values in spec and its contract: `Part`, `PartView`, `Architecture.imports_libraries`,
   `ProfileView.imports_libraries`, `publishing.py`, and the rules adapter that reads them, tests first.
4. `rules`' `Profile`: `imports_libraries`, `imports_must`, `imports_types_only`, `holds_names`, `holds_immutable`,
   `holds_built_by`, `spec_profile.py` and every reader in `rules/application/logic`, tests first.
5. Functions: `targets_phrase`, `allowed_targets`, `_imports_may_phrase`, `_folder_imports`, `_imports_libraries`,
   tests first.
6. The docstrings of 2.2 that still name an old identifier; the re-grep of 3 classed in full; 2.1 rerun and diffed;
   golden docs regenerated (the script of the 4.6 plan, `docs/superpowers/plans/4-6-spec-a-tier-s-20b1e1ce.md:1660-1668`)
   with an empty diff; all gates.

Commits: one per task, the message saying what was renamed to what and that nothing a user sees changes; `.claude/`
never staged; nothing pushed. No README or CHANGELOG line (O4, O5: nothing user-visible); the plan says so in task 6.

## 7. Out of scope

- Anything that changes output (card): finding texts, keys in parentheses, rule ids, refusal texts, JSON keys,
  generated docs, the key catalogue `keys.yaml`, the retired-keys table.
- Renaming `where`'s JSON fields or the Python fields that are those fields one for one (CS 615-618, 970).
- `Architecture.rules` / `Profile.rules` and the function `_rules` (2.3).
- The check language's words `may-import-everything` and `mirrored_may_import` (CS 619-620).
- References inside `imports` (`parts.<part>`, `<word>.<part>`): story 8, release step 24 (CS 41-43, 810-811).
- The new looser lines of the profile comparison: release step 16 (CS 612-614).
- Restructuring `Profile`'s flat per-part maps into a value per kind, or folding a part's import fields into one
  `imports` value: a shape change, not a rename; the flat rename keeps every position and default.
- `docs/examples/**`, `tests/bootstrap/corpora/**`, `review` (CS 705).

---

## File structure

Nothing is created in the repository. The files that change, by task:

| Task | Source | Tests |
|---|---|---|
| 2 tier values | `xarch/modules/spec/domain/values.py` (`Tier`), `xarch/profile_values/tiers.py`, `xarch/modules/spec/application/logic/{checked_tier,looseness,docs_template}.py`, `xarch/modules/rules/application/logic/{tier_of,expansion,sentences}.py`, `xarch/modules/rules/application/services/locate.py` | `tests/modules/rules/builders.py`, `tests/modules/rules/application/test_locate.py`, `tests/modules/rules/application/logic/test_{expansion,expandable,sentences,types_only,where,tier_imports,must_import}.py`, `tests/modules/spec/application/logic/test_{checked_tier,tiers,profile_parsing_tests,profile_parsing_substance}.py` |
| 3 part values | `xarch/modules/spec/domain/values.py` (`Part`, `Architecture`), `xarch/modules/spec/contract/__init__.py`, `xarch/modules/spec/application/services/publishing.py`, `xarch/modules/spec/application/logic/{profile_parsing,looseness,docs_template}.py`, `xarch/modules/rules/adapters/spec_profile.py` (reads) | `tests/bootstrap/test_bundled_guards.py`, `tests/modules/spec/application/logic/test_{imports_written,profile_parsing_substance,profile_parsing,libraries_and_guards,never_use,looseness}.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/spec/application/test_profile.py` |
| 4 rules' `Profile` | `xarch/modules/rules/domain/profile.py`, `xarch/modules/rules/adapters/spec_profile.py` (keywords), `xarch/modules/rules/application/logic/{where,filters,sentences,expansion}.py` | `tests/modules/rules/builders.py`, `tests/modules/rules/application/test_{locate,check_app,words,rule}.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/rules/application/logic/test_{built_by,libraries,holds,names,must_import,types_only,expandable,expansion,where}.py`, `tests/modules/rules/application/logic/world.py` |
| 5 functions | `xarch/kernel/logic/imports.py`, `xarch/modules/spec/application/logic/{targets_written,docs_template,profile_parsing,imports_written}.py`, `xarch/modules/rules/application/logic/{where,tier_of}.py` | `tests/kernel/logic/test_imports.py`, `tests/modules/spec/application/logic/test_targets_written.py` |
| 6 close | `xarch/modules/rules/domain/published.py` (one docstring) | none |

Every test file stays in its tier; none is moved, none added. The spec's test table is an upper bound: files it lists
whose only hits are kept names (e.g. `test_where_report.py`, `tests/bootstrap/test_where.py`, `checks.py`,
`test_retired_keys.py`) are not edited.

---

### Task 1: Record the baseline before any edit

**Files:**
- Create (outside the worktree): `/tmp/xarch-4-7/apply.py`, `/tmp/xarch-4-7/record.sh`, `/tmp/xarch-4-7-base/*`

**Interfaces:**
- Produces: `/tmp/xarch-4-7/apply.py` with `apply(table: dict[str, list[tuple[str, str, int]]]) -> None` (each
  entry `(regex, replacement, expected_count)`, applied in order per file; exits non-zero and writes nothing when any
  count differs); `/tmp/xarch-4-7/record.sh <out-dir>` writing one `<name>.out` per command with its `exit <code>`
  last line; `/tmp/xarch-4-7-base/` holding the baseline and `/tmp/xarch-4-7-base/pytest.txt`.

- [ ] **Step 1: Check the starting point**

Run: `git log -1 --format=%h && git status --short`
Expected: `293ab8c` (or a later docs commit adding the spec and this plan) and no modified tracked file under
`xarch/` or `tests/`.

- [ ] **Step 2: Write the edit helper**

```bash
mkdir -p /tmp/xarch-4-7
cat > /tmp/xarch-4-7/apply.py <<'PYEOF'
"""Apply exact text replacements, each seen exactly the number of times given, or change nothing and fail."""
import re
import sys
from pathlib import Path


def apply(table: dict[str, list[tuple[str, str, int]]]) -> None:
    texts = {}
    for file, edits in table.items():
        text = Path(file).read_text(encoding="utf-8")
        for old, new, count in edits:
            seen = len(re.findall(old, text))
            if seen != count:
                sys.exit(f"{file}: {old!r} seen {seen} times, expected {count}; nothing written")
            text = re.sub(old, new, text)
        texts[file] = text
    for file, text in texts.items():
        Path(file).write_text(text, encoding="utf-8")
    print(f"{len(texts)} files written")
PYEOF
```

- [ ] **Step 3: Write the recorder**

```bash
cat > /tmp/xarch-4-7/record.sh <<'SHEOF'
#!/usr/bin/env bash
# Record what xarch prints for the commands of spec 2.1 items 1-4 and 7, each with its exit code, into the folder $1.
out="$1"; mkdir -p "$out"
run() { local name="$1"; shift; "$@" > "$out/$name.out" 2>&1; echo "exit $?" >> "$out/$name.out"; }
run check uv run xarch check --format json
run check-strict uv run xarch check --strict --format json
run profile-check-own uv run xarch profile check architecture.yaml
run profile-check-cli uv run xarch profile check cli
run profile-check-web uv run xarch profile check web
for f in xarch/modules/spec/domain/values.py xarch/modules/spec/application/logic/checked_tier.py \
         xarch/modules/rules/application/ports/source_tree.py xarch/modules/spec/application/services/publishing.py \
         xarch/modules/spec/application/controller.py xarch/modules/rules/adapters/spec_profile.py \
         xarch/platform/typesafe.py xarch/cli/app.py xarch/cli/reports/where_report.py xarch/__main__.py \
         xarch/bootstrap/wiring.py xarch/modules/spec/contract/__init__.py xarch/profile_values/tiers.py \
         xarch/kernel/logic/imports.py xarch/kernel/violations.py \
         tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/test_profile.py \
         tests/bootstrap/test_where.py tests/architecture/test_agnostic.py; do
    run "where-$(echo "$f" | tr '/' '_')" uv run xarch where --format json "$f"
done
for a in parts.imports.may parts.imports.must parts.imports.libraries tiers.imports.also tiers.imports.types_only \
         parts.holds.classes.built_by guards.no-callbacks parts.may_import tiers.may_also_import parts.no_callbacks; do
    run "explain-$a" uv run xarch profile explain "$a"
done
run review uv run xarch review --offline --all --format json
ls "$out" | wc -l
SHEOF
```

The 19 `where` files are one file of each of the 15 parts of `architecture.yaml` (domain, logic, ports, services,
controller, adapters, platform, cli, reports, main, bootstrap, contract, profile-values, kernel-logic, kernel) and one
test of each of its 4 tiers (unit, integration, wired, guard).

- [ ] **Step 4: Record the baseline**

Run: `rm -rf /tmp/xarch-4-7-base && timeout 600 bash /tmp/xarch-4-7/record.sh /tmp/xarch-4-7-base`
Expected: prints `35`. `grep -l '^exit 2' /tmp/xarch-4-7-base/*` lists exactly `explain-parts.may_import.out`,
`explain-tiers.may_also_import.out`, `explain-parts.no_callbacks.out` (retired keys, refused) and `review.out`
(`--all` refuses more files than one run judges, nothing sent); every other file ends `exit 0`. These exit codes are
the base's; only equality with the after-run matters.

- [ ] **Step 5: Record the suite's count**

Run (in the background; it takes about three minutes): `timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3 > /tmp/xarch-4-7-base/pytest.txt; cat /tmp/xarch-4-7-base/pytest.txt`
Expected: `5709 passed` (the count on `293ab8c`); write down the exact line, it is compared in Task 6.

- [ ] **Step 6: No commit**

Nothing in the repository changed: `git status --short` shows no new change. This task commits nothing.

---

### Task 2: A tier's values take the names of its `imports` group

**Files:**
- Modify: `xarch/modules/spec/domain/values.py` (`Tier`, docstring lines 204-213, fields 227, 230, 231, 233)
- Modify: `xarch/profile_values/tiers.py:21,27,28,30`
- Modify: `xarch/modules/spec/application/logic/checked_tier.py:13-15`
- Modify: `xarch/modules/spec/application/logic/looseness.py:92-95`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:426-427,442,553`
- Modify: `xarch/modules/rules/application/logic/tier_of.py:100-103,113`
- Modify: `xarch/modules/rules/application/logic/expansion.py:141-142,188,352,359`
- Modify: `xarch/modules/rules/application/logic/sentences.py:148`
- Modify: `xarch/modules/rules/application/services/locate.py:65`
- Test: the 13 test files of `t2_tests.py` below

**Interfaces:**
- Consumes: `/tmp/xarch-4-7/apply.py` (Task 1).
- Produces: `Tier.imports_types_only: tuple[str, ...]`, `Tier.imports_may: tuple[Target, ...] | None`,
  `Tier.imports_must: tuple[str, ...]`, `Tier.imports_also: tuple[Target, ...]`, and the same four fields with the
  same types on `CheckedTier` (`xarch.profile_values.tiers`), each in the place of the old field. Old names
  `types_only`, `may_import`, `must_import`, `may_also_import` no longer exist on either class.

- [ ] **Step 1: Write the test edits**

```bash
cat > /tmp/xarch-4-7/t2_tests.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

R = "tests/modules/rules/application/logic/"
S = "tests/modules/spec/application/logic/"
apply({
    "tests/modules/rules/builders.py": [(r'\("web",\), types_only=', '("web",), imports_types_only=', 1)],
    "tests/modules/rules/application/test_locate.py": [(r"\bmay_also_import=", "imports_also=", 1)],
    R + "test_expansion.py": [(r"replace\(t, must_import=", "replace(t, imports_must=", 2),
                              (r"\bmay_also_import=", "imports_also=", 1)],
    R + "test_expandable.py": [(r'\("tier",\), types_only=', '("tier",), imports_types_only=', 1),
                               (r"\bmay_import=", "imports_may=", 1),
                               (r'must_import=\("two",\)', 'imports_must=("two",)', 1),
                               (r"\bmay_also_import=", "imports_also=", 1)],
    R + "test_sentences.py": [(r"\bmay_also_import=", "imports_also=", 1)],
    R + "test_types_only.py": [(r"replace\(GUARD, types_only=", "replace(GUARD, imports_types_only=", 1)],
    R + "test_where.py": [(r"here\.tier\.types_only\b", "here.tier.imports_types_only", 1)],
    R + "test_tier_imports.py": [(r"\bmay_import=", "imports_may=", 3), (r"\bmay_also_import=", "imports_also=", 3)],
    R + "test_must_import.py": [(r"replace\(INTEGRATION, must_import=", "replace(INTEGRATION, imports_must=", 1)],
    S + "test_checked_tier.py": [(r"\)\.may_also_import == \(Target\(\"service\", \"own\"\),\n {81}Target",
                                  ').imports_also == (Target("service", "own"),\n' + " " * 78 + "Target", 1)],
    S + "test_tiers.py": [(r"(?<!imports)\.types_only\b", ".imports_types_only", 4), (r"\.may_import\b", ".imports_may", 6),
                          (r"\.may_also_import\b", ".imports_also", 4), (r"\.must_import\b", ".imports_must", 3)],
    S + "test_profile_parsing_tests.py": [(r"(?<!imports)\.types_only\b", ".imports_types_only", 1),
                                          (r"\.may_import\b", ".imports_may", 3),
                                          (r"\.may_also_import\b", ".imports_also", 1)],
    S + "test_profile_parsing_substance.py": [(r'\]\.must_import\b', "].imports_must", 2)],
})
PYEOF
```

`test_tiers.py:400` (`with_tier(types_only=..., may_import=..., ...)`) writes the retired keys into a profile to see
them refused; its keywords are dict keys of the document, not fields, and are not touched (the patterns match only
`.<field>` reads, and `(?<!imports)` skips the `imports.types_only` addresses inside strings).

- [ ] **Step 2: Apply them and see the tests fail**

Run: `uv run python /tmp/xarch-4-7/t2_tests.py && timeout 600 uv run pytest -q -p no:cacheprovider tests/modules/spec/application/logic/test_tiers.py tests/modules/rules/application/logic/test_tier_imports.py tests/modules/spec/application/logic/test_checked_tier.py 2>&1 | tail -5`
Expected: `13 files written`, then FAIL: a collection error `TypeError: CheckedTier.__init__() got an unexpected
keyword argument 'imports_may'` for `test_tier_imports.py`, and `AttributeError: 'Tier' object has no attribute
'imports_types_only'` (or `imports_may`, `imports_also`) in `test_tiers.py` and `test_checked_tier.py`.

- [ ] **Step 3: Write the code edits**

```bash
cat > /tmp/xarch-4-7/t2_code.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

SPEC = "xarch/modules/spec/"
RULES = "xarch/modules/rules/"
apply({
    SPEC + "domain/values.py": [
        (r"\n    types_only: parts its tests may import", "\n    imports_types_only: parts its tests may import", 1),
        (r"\n    may_import: what the tests in its own folder", "\n    imports_may: what the tests in its own folder", 1),
        (r"\n    must_import: the parts one of which", "\n    imports_must: the parts one of which", 1),
        (r"\n    may_also_import: what each of its tests", "\n    imports_also: what each of its tests", 1),
        (r"\n    types_only: tuple\[str, \.\.\.\] = \(\)\n    apply_never",
         "\n    imports_types_only: tuple[str, ...] = ()\n    apply_never", 1),
        (r"\n    may_import: tuple\[Target, \.\.\.\] \| None = None\n    must_import: tuple\[str, \.\.\.\] = \(\)",
         "\n    imports_may: tuple[Target, ...] | None = None\n    imports_must: tuple[str, ...] = ()", 1),
        (r"\n    may_also_import: tuple\[Target, \.\.\.\] = \(\)\n", "\n    imports_also: tuple[Target, ...] = ()\n", 1)],
    "xarch/profile_values/tiers.py": [
        (r"\n    types_only: tuple\[str, \.\.\.\] = \(\)", "\n    imports_types_only: tuple[str, ...] = ()", 1),
        (r"\n    may_import: tuple", "\n    imports_may: tuple", 1),
        (r"\n    must_import: tuple", "\n    imports_must: tuple", 1),
        (r"\n    may_also_import: tuple", "\n    imports_also: tuple", 1)],
    SPEC + "application/logic/checked_tier.py": [
        (r"\btier\.types_only\b", "tier.imports_types_only", 1), (r"\btier\.may_import\b", "tier.imports_may", 1),
        (r"\btier\.must_import\b", "tier.imports_must", 1), (r"\btier\.may_also_import\b", "tier.imports_also", 1)],
    SPEC + "application/logic/looseness.py": [
        (r"\b(tier|mine)\.types_only\b", r"\1.imports_types_only", 2),
        (r"\b(tier|mine)\.may_also_import\b", r"\1.imports_also", 2)],
    SPEC + "application/logic/docs_template.py": [
        (r"\btier\.types_only\b", "tier.imports_types_only", 2), (r"\btier\.must_import\b", "tier.imports_must", 2)],
    RULES + "application/logic/tier_of.py": [
        (r"\btier\.may_import\b", "tier.imports_may", 2), (r"\btier\.may_also_import\b", "tier.imports_also", 3)],
    RULES + "application/logic/expansion.py": [
        (r"\btier\.types_only\b", "tier.imports_types_only", 2), (r"\btier\.may_also_import\b", "tier.imports_also", 1),
        (r"\btier\.must_import\b", "tier.imports_must", 2)],
    RULES + "application/logic/sentences.py": [(r"\btier\.may_also_import\b", "tier.imports_also", 1)],
    RULES + "application/services/locate.py": [(r"\btier\.types_only if tier\b", "tier.imports_types_only if tier", 1)],
})
PYEOF
```

- [ ] **Step 4: Apply them**

Run: `uv run python /tmp/xarch-4-7/t2_code.py && git diff --stat -- xarch`
Expected: `9 files written`; 9 files under `xarch/`, 34 insertions and 34 deletions.

- [ ] **Step 5: Run the suite and the linter**

Run (in the background): `timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3; uv run ruff check`
Expected: the count of Task 1 Step 5 (`5709 passed`), then `All checks passed!`.

- [ ] **Step 6: Commit**

```bash
git add xarch tests
git commit -m "A tier's values take the names of its imports group: Tier and CheckedTier's types_only, may_import, must_import and may_also_import become imports_types_only, imports_may, imports_must and imports_also, in the same places, and every reader follows; nothing a user sees changes"
```

---

### Task 3: A part's values in spec and its contract take the names of its `imports` group

**Files:**
- Modify: `xarch/modules/spec/domain/values.py` (`Part` docstring 80, 84-85, fields 94, 96; `Architecture`
  docstring 366, 379, field 404)
- Modify: `xarch/modules/spec/contract/__init__.py:102,108,110,158`
- Modify: `xarch/modules/spec/application/services/publishing.py:61,66`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:196-197`
- Modify: `xarch/modules/spec/application/logic/looseness.py:67-75,81`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:407,409,441,566,568,634`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:62,65,70,80` (right-hand reads only; the keywords are Task 4)
- Test: the 9 test files of `t3_tests.py` below

**Interfaces:**
- Consumes: `/tmp/xarch-4-7/apply.py`; Task 2's tier fields (untouched here).
- Produces: `Part.imports_must: tuple[Target, ...]`, `Part.imports_types_only: tuple[Target, ...]`;
  `Architecture.imports_libraries: dict[str, tuple[str, ...]] | None`; `PartView.imports_may: tuple[Target, ...]`
  (third, positional), `PartView.imports_must`, `PartView.imports_types_only`;
  `ProfileView.imports_libraries: dict[str, tuple[str, ...]] | None`. `Architecture` stays built positionally in
  `profile_parsing.py:226` (its local `libraries` keeps its name: only locals named exactly `may_import`,
  `must_import`, `may_also_import` are renamed, and none exists).

- [ ] **Step 1: Write the test edits**

```bash
cat > /tmp/xarch-4-7/t3_tests.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

S = "tests/modules/spec/application/logic/"
apply({
    "tests/bootstrap/test_bundled_guards.py": [(r"\(profile\.libraries or", "(profile.imports_libraries or", 1),
                                               (r"\bp\.must_import\b", "p.imports_must", 2)],
    S + "test_imports_written.py": [(r"\]\.must_import\b", "].imports_must", 2),
                                    (r"\barchitecture\.libraries\[", "architecture.imports_libraries[", 2),
                                    (r"\]\.types_only\b", "].imports_types_only", 4)],
    S + "test_profile_parsing_substance.py": [(r"\bpart\.types_only\b", "part.imports_types_only", 2)],
    S + "test_profile_parsing.py": [(r"\barchitecture\.libraries ==", "architecture.imports_libraries ==", 1),
                                    (r"\)\.libraries\b", ").imports_libraries", 2),
                                    (r"\]\.must_import\b", "].imports_must", 4)],
    S + "test_libraries_and_guards.py": [(r"\)\.libraries ==", ").imports_libraries ==", 1),
                                         (r"\barchitecture\.libraries\[", "architecture.imports_libraries[", 1)],
    S + "test_never_use.py": [(r"\barchitecture\.libraries\[", "architecture.imports_libraries[", 1)],
    S + "test_looseness.py": [(r"replace\(parsed\(layered\(\)\), libraries=None\)",
                               "replace(parsed(layered()), imports_libraries=None)", 1)],
    "tests/modules/rules/adapters/test_spec_profile.py": [
        (r'must_import=\(Target\("core"\),\), types_only=\(Target\("core"\),\),',
         'imports_must=(Target("core"),), imports_types_only=(Target("core"),),', 1),
        (r'\n    libraries=(\{"core": \(\), "api": \("fastapi",\)\}, repeats=)', r"\n    imports_libraries=\1", 1)],
    "tests/modules/spec/application/test_profile.py": [(r'\blibraries=\{"src": \(\)\}', 'imports_libraries={"src": ()}', 1)],
})
PYEOF
```

In `test_spec_profile.py` only the `ProfileView` (`VIEW`, `libraries=... repeats=`) and the `PartView` keywords
change here; the expected `Profile(...)` (`libraries=... fakes=`, `must_import={...}`, ...) is Task 4's.

- [ ] **Step 2: Apply them and see the tests fail**

Run: `uv run python /tmp/xarch-4-7/t3_tests.py && timeout 600 uv run pytest -q -p no:cacheprovider tests/modules/spec/application/logic/test_imports_written.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/spec/application/test_profile.py 2>&1 | tail -5`
Expected: `9 files written`, then FAIL: `TypeError: PartView.__init__() got an unexpected keyword argument
'imports_must'` at collection of `test_spec_profile.py`, `AttributeError: 'Part' object has no attribute
'imports_must'` and `'Architecture' object has no attribute 'imports_libraries'` in `test_imports_written.py`.

- [ ] **Step 3: Write the code edits**

```bash
cat > /tmp/xarch-4-7/t3_code.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

SPEC = "xarch/modules/spec/"
apply({
    SPEC + "domain/values.py": [
        (r"\n    must_import: the targets each of its files", "\n    imports_must: the targets each of its files", 1),
        (r"\n    types_only: the targets of its imports\.may marked types_only, in the order of may: its files may import\n"
         r" {16}what they reach",
         "\n    imports_types_only: the targets of its imports.may marked types_only, in the order of may: its files may import\n"
         + " " * 24 + "what they reach", 1),
        (r"\n    must_import: tuple\[Target, \.\.\.\] = \(\)\n    holds: tuple\[Held, \.\.\.\] = \(\)\n"
         r"    types_only: tuple\[Target, \.\.\.\] = \(\)\n",
         "\n    imports_must: tuple[Target, ...] = ()\n    holds: tuple[Held, ...] = ()\n"
         "    imports_types_only: tuple[Target, ...] = ()\n", 1),
        (r"\n    libraries: the outside packages each part may import", "\n    imports_libraries: the outside packages each part may import", 1),
        (r"only the parts whose `libraries` list them may import", "only the parts whose `imports_libraries` list them may import", 1),
        (r"\n    libraries: dict\[str, tuple\[str, \.\.\.\]\] \| None = None\n",
         "\n    imports_libraries: dict[str, tuple[str, ...]] | None = None\n", 1)],
    SPEC + "contract/__init__.py": [
        (r"\n    may_import: tuple\[Target, \.\.\.\]\n", "\n    imports_may: tuple[Target, ...]\n", 1),
        (r"\n    must_import: tuple\[Target, \.\.\.\] = \(\)\n", "\n    imports_must: tuple[Target, ...] = ()\n", 1),
        (r"\n    types_only: tuple\[Target, \.\.\.\] = \(\)\n", "\n    imports_types_only: tuple[Target, ...] = ()\n", 1),
        (r"\n    libraries: dict\[str, tuple\[str, \.\.\.\]\] \| None = None\n",
         "\n    imports_libraries: dict[str, tuple[str, ...]] | None = None\n", 1)],
    SPEC + "application/services/publishing.py": [
        (r"part\.must_import, part\.holds, part\.types_only, part\.shared",
         "part.imports_must, part.holds, part.imports_types_only, part.shared", 1),
        (r"libraries=None if architecture\.libraries is None else dict\(architecture\.libraries\)",
         "imports_libraries=None if architecture.imports_libraries is None else dict(architecture.imports_libraries)", 1)],
    SPEC + "application/logic/profile_parsing.py": [
        (r"replace\(item, must_import=iw\.must\(imports\[part\], item, parts, declared, rules\[part\], problems\),\n"
         r"                           types_only=read\[part\]\[1\]\)",
         "replace(item, imports_must=iw.must(imports[part], item, parts, declared, rules[part], problems),\n"
         "                           imports_types_only=read[part][1])", 1)],
    SPEC + "application/logic/looseness.py": [
        (r"\.parts\[name\]\.types_only\b", ".parts[name].imports_types_only", 2),
        (r"\.parts\[name\]\.must_import\b", ".parts[name].imports_must", 2),
        (r"\b(base|custom)\.libraries\b", r"\1.imports_libraries", 4)],
    SPEC + "application/logic/docs_template.py": [
        (r"\barchitecture\.libraries\b", "architecture.imports_libraries", 2),
        (r"\bpart\.must_import\b", "part.imports_must", 2), (r"\bpart\.types_only\b", "part.imports_types_only", 2)],
    "xarch/modules/rules/adapters/spec_profile.py": [
        (r"\bp\.may_import\b", "p.imports_may", 1), (r"\bp\.must_import\b", "p.imports_must", 2),
        (r"\bp\.types_only\b", "p.imports_types_only", 2),
        (r"None if view\.libraries is None else dict\(view\.libraries\)",
         "None if view.imports_libraries is None else dict(view.imports_libraries)", 1)],
})
PYEOF
```

The `Part` docstring's continuation line under `imports_types_only:` is re-indented from 16 to 24 spaces so it still
hangs under the text; `Architecture`'s docstring names `` `imports_libraries` `` at `reserved:` (379), as the field
it means.

- [ ] **Step 4: Apply them**

Run: `uv run python /tmp/xarch-4-7/t3_code.py && git diff --stat -- xarch`
Expected: `7 files written`.

- [ ] **Step 5: Run the suite and the linter**

Run (in the background): `timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3; uv run ruff check`
Expected: `5709 passed` (Task 1's count), `All checks passed!`.

- [ ] **Step 6: Commit**

```bash
git add xarch tests
git commit -m "A part's values in spec and its contract take the names of its imports group: Part's must_import and types_only become imports_must and imports_types_only, Architecture's and ProfileView's libraries become imports_libraries, PartView's may_import, must_import and types_only become imports_may, imports_must and imports_types_only, in the same places; publishing, the parser, looseness, the docs template and the rules adapter read the new names; nothing a user sees changes"
```

---

### Task 4: Rules' `Profile` names each import and shape setting by its address

**Files:**
- Modify: `xarch/modules/rules/domain/profile.py` (docstring 47, 53, 64, 65, 67, 68; fields 84, 96, 108, 109, 111, 112)
- Modify: `xarch/modules/rules/adapters/spec_profile.py:65,70,78-79,80,82-83,84` (keywords)
- Modify: `xarch/modules/rules/application/logic/where.py:105`
- Modify: `xarch/modules/rules/application/logic/filters.py:106,195`
- Modify: `xarch/modules/rules/application/logic/sentences.py:112,167,179`
- Modify: `xarch/modules/rules/application/logic/expansion.py:30,46,100,105,151,210,312,344`
- Test: the 16 test files of `t4_tests.py` below

**Interfaces:**
- Consumes: `/tmp/xarch-4-7/apply.py`; `PartView.imports_*` and `ProfileView.imports_libraries` (Task 3).
- Produces: on `xarch.modules.rules.domain.profile.Profile`, in the same places and with the same types and
  defaults: `imports_libraries` (was `libraries`), `imports_must` (was `must_import`), `holds_immutable` (was
  `immutable`), `imports_types_only` (was `types_only`), `holds_names` (was `names`), `holds_built_by` (was
  `built_by`). `holds`, `no_callbacks`, `rules` keep their names.

- [ ] **Step 1: Write the test edits**

```bash
cat > /tmp/xarch-4-7/t4_tests.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

R = "tests/modules/rules/application/logic/"
apply({
    "tests/modules/rules/builders.py": [
        (r'\n    libraries=\{"platform": \("sqlmodel",\), "adapters": \("sqlmodel",\), "web": \("fastapi",\),\n'
         r' {15}"bootstrap"',
         '\n    imports_libraries={"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),\n'
         + " " * 23 + '"bootstrap"', 1)],
    "tests/modules/rules/application/test_locate.py": [(r'\blibraries=\{"kernel"', 'imports_libraries={"kernel"', 1)],
    "tests/modules/rules/application/test_check_app.py": [(r"\blibraries=\{", "imports_libraries={", 2)],
    "tests/modules/rules/application/test_words.py": [(r"\bprofile\(names=", "profile(holds_names=", 1)],
    "tests/modules/rules/application/test_rule.py": [(r"\bprofile\(names=", "profile(holds_names=", 1)],
    "tests/modules/rules/adapters/test_spec_profile.py": [
        (r'\n        libraries=(\{"core": \(\), "api": \("fastapi",\)\}, fakes=)', r"\n        imports_libraries=\1", 1),
        (r'\bmust_import=\{"api"', 'imports_must={"api"', 1), (r'\bimmutable=\{"core"', 'holds_immutable={"core"', 1),
        (r'\btypes_only=\{"api"', 'imports_types_only={"api"', 1), (r'\bnames=\{"api"', 'holds_names={"api"', 1),
        (r'\bbuilt_by=\{"api"', 'holds_built_by={"api"', 1)],
    R + "test_built_by.py": [(r"\bbuilt_by=\{", "holds_built_by={", 2)],
    R + "test_libraries.py": [(r"\bprofile\(libraries=", "profile(imports_libraries=", 3),
                              (r"\bPROFILE\.libraries\b", "PROFILE.imports_libraries", 2)],
    R + "test_holds.py": [(r"\bimmutable=\{", "holds_immutable={", 4)],
    R + "test_names.py": [(r'\bnames=\{"services"', 'holds_names={"services"', 5)],
    R + "test_must_import.py": [(r"\bprofile\(must_import=", "profile(imports_must=", 1)],
    R + "test_types_only.py": [(r'\btypes_only=\{"services"', 'imports_types_only={"services"', 5)],
    R + "test_expandable.py": [
        (r'\blibraries=\{"one"', 'imports_libraries={"one"', 1), (r'\btypes_only=\{"one"', 'imports_types_only={"one"', 1),
        (r'\bnames=\{"one"', 'holds_names={"one"', 1), (r'\bbuilt_by=\{"two"', 'holds_built_by={"two"', 1),
        (r'\bimmutable=\{"one"', 'holds_immutable={"one"', 1), (r'\bmust_import=\{"one"', 'imports_must={"one"', 1)],
    R + "test_expansion.py": [
        (r'\bimmutable=\{"logic"', 'holds_immutable={"logic"', 1), (r'\bbuilt_by=\{"services"', 'holds_built_by={"services"', 1),
        (r'\bnames=\{"services"', 'holds_names={"services"', 1), (r'\bmust_import=\{"adapters"', 'imports_must={"adapters"', 1),
        (r'\btypes_only=\{"services"', 'imports_types_only={"services"', 1),
        (r"replace\(PROFILE, libraries=None,", "replace(PROFILE, imports_libraries=None,", 1)],
    R + "world.py": [(r"replace\(PROFILE, libraries=", "replace(PROFILE, imports_libraries=", 1),
                     (r"replace\(PROFILE, built_by=", "replace(PROFILE, holds_built_by=", 1)],
    R + "test_where.py": [(r'\n    libraries=\{"kernel"', '\n    imports_libraries={"kernel"', 1)],
})
PYEOF
```

The patterns name each `Profile` keyword with the value that follows it, so `Class(..., immutable=True)` in
`test_holds.py`, `Held(..., built_by=...)`, `Target(..., names=...)` and `RecordMark` keywords are not touched.

- [ ] **Step 2: Apply them and see the tests fail**

Run: `uv run python /tmp/xarch-4-7/t4_tests.py && timeout 600 uv run pytest -q -p no:cacheprovider tests/modules/rules/application/logic/test_names.py tests/modules/rules/application/logic/test_built_by.py 2>&1 | tail -5`
Expected: `16 files written`, then FAIL with a collection error: `TypeError: Profile.__init__() got an unexpected
keyword argument 'imports_libraries'` (raised by `tests/modules/rules/builders.py`, which every rules test imports).

- [ ] **Step 3: Write the code edits**

```bash
cat > /tmp/xarch-4-7/t4_code.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

RULES = "xarch/modules/rules/"
LOGIC = RULES + "application/logic/"
apply({
    RULES + "domain/profile.py": [
        (r"hold the tree together\. libraries\n    is None", "hold the tree together. imports_libraries\n    is None", 1),
        (r"no check reads a file below one\. must_import holds, by", "no check reads a file below one. imports_must holds, by", 1),
        (r"kind\); immutable, by part,", "kind); holds_immutable, by part,", 1),
        (r"is an immutable record; types_only, by part,", "is an immutable record; imports_types_only, by part,", 1),
        (r"annotated as callables; names, by part and then by", "annotated as callables; holds_names, by part and then by", 1),
        (r"matches one of; built_by, by part, the parts that", "matches one of; holds_built_by, by part, the parts that", 1),
        (r"\n    libraries: dict", "\n    imports_libraries: dict", 1),
        (r"\n    must_import: dict", "\n    imports_must: dict", 1),
        (r"\n    immutable: dict", "\n    holds_immutable: dict", 1),
        (r"\n    types_only: dict", "\n    imports_types_only: dict", 1),
        (r"\n    names: dict", "\n    holds_names: dict", 1),
        (r"\n    built_by: dict", "\n    holds_built_by: dict", 1)],
    RULES + "adapters/spec_profile.py": [
        (r"\n( +)libraries=None if view", r"\n\1imports_libraries=None if view", 1),
        (r"\n( +)must_import=\{p\.name", r"\n\1imports_must={p.name", 1),
        (r"\n( +)immutable=\{p\.name: tuple\(h\.kind for h in p\.holds if h\.immutable\) for p in parts\n {34}if",
         r"\n\1holds_immutable={p.name: tuple(h.kind for h in p.holds if h.immutable) for p in parts\n" + " " * 40 + "if", 1),
        (r"\n( +)types_only=\{p\.name", r"\n\1imports_types_only={p.name", 1),
        (r"\n( +)names=\{p\.name: \{h\.kind: h\.names for h in p\.holds if h\.names\} for p in parts\n {30}if",
         r"\n\1holds_names={p.name: {h.kind: h.names for h in p.holds if h.names} for p in parts\n" + " " * 36 + "if", 1),
        (r"\n( +)built_by=\{p\.name", r"\n\1holds_built_by={p.name", 1)],
    LOGIC + "where.py": [(r"\bprofile\.libraries\b", "profile.imports_libraries", 2)],
    LOGIC + "filters.py": [(r"\bprofile\.libraries\b", "profile.imports_libraries", 1),
                           (r'\{"built_by": profile\.built_by\}', '{"built_by": profile.holds_built_by}', 1)],
    LOGIC + "sentences.py": [(r"\bprofile\.built_by\b", "profile.holds_built_by", 1),
                             (r"\bprofile\.types_only\b", "profile.imports_types_only", 1),
                             (r"\bprofile\.libraries\b", "profile.imports_libraries", 1)],
    LOGIC + "expansion.py": [(r"\bprofile\.libraries\b", "profile.imports_libraries", 2),
                             (r"\bprofile\.built_by\b", "profile.holds_built_by", 2),
                             (r"\bprofile\.types_only\b", "profile.imports_types_only", 1),
                             (r"\bprofile\.names\b", "profile.holds_names", 1),
                             (r"\bprofile\.immutable\b", "profile.holds_immutable", 1),
                             (r"\bprofile\.must_import\b", "profile.imports_must", 1)],
})
PYEOF
```

In `spec_profile.py` the continuation lines of `holds_immutable=` and `holds_names=` move 6 spaces right, to stay under
the `{`. In `filters.py:195` the dict key `"built_by"` is the word a check writes (`target-allows-under built_by`) and
stays; only the value read changes.

- [ ] **Step 4: Apply them**

Run: `uv run python /tmp/xarch-4-7/t4_code.py && git diff --stat -- xarch`
Expected: `6 files written`.

- [ ] **Step 5: Run the suite and the linter**

Run (in the background): `timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3; uv run ruff check`
Expected: `5709 passed`, `All checks passed!`.

- [ ] **Step 6: Commit**

```bash
git add xarch tests
git commit -m "Rules' Profile names each import and shape setting by its address: libraries, must_import, types_only, immutable, names and built_by become imports_libraries, imports_must, imports_types_only, holds_immutable, holds_names and holds_built_by, in the same places; the spec adapter and every reader in rules' logic follow, the words a check writes stay; nothing a user sees changes"
```

---

### Task 5: The functions named for a retired key take the name of what they do

**Files:**
- Modify: `xarch/kernel/logic/imports.py:15` (`may_import` → `targets_phrase`)
- Modify: `xarch/modules/spec/application/logic/targets_written.py:18-19` (`may_import` → `allowed_targets`)
- Modify: `xarch/modules/spec/application/logic/docs_template.py:57,188,193,195,634` (`_may_import` →
  `_imports_may_phrase`; the kernel function's callers)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:92,194,450-451,474,655,657` (`_libraries` →
  `_imports_libraries`; `allowed_targets` callers)
- Modify: `xarch/modules/spec/application/logic/imports_written.py:23,61,68,88`
- Modify: `xarch/modules/rules/application/logic/where.py:24,104,208`
- Modify: `xarch/modules/rules/application/logic/tier_of.py:97,111` (`_may_import` → `_folder_imports`)
- Test: `tests/kernel/logic/test_imports.py`, `tests/modules/spec/application/logic/test_targets_written.py`

**Interfaces:**
- Consumes: `/tmp/xarch-4-7/apply.py`.
- Produces: `xarch.kernel.logic.imports.targets_phrase(targets: Iterable[Target], folders: Mapping[str, str],
  words: Mapping[str, str]) -> str`; `xarch.modules.spec.application.logic.targets_written.allowed_targets(value: Any,
  owner: Part | None, parts: dict[str, Part], declared: set[str], where: str, problems: list[str], patterns: bool =
  False, mirrored: bool = False) -> tuple[Target, ...]`; private `_imports_may_phrase`, `_folder_imports`,
  `_imports_libraries` with unchanged signatures. `expansion._libraries` (the rule `libraries`) and
  `where_report._libraries` keep their names.

- [ ] **Step 1: Write the test edits**

```bash
cat > /tmp/xarch-4-7/t5_tests.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

apply({
    "tests/kernel/logic/test_imports.py": [
        (r"from xarch\.kernel\.logic\.imports import may_import\n", "from xarch.kernel.logic.imports import targets_phrase\n", 1),
        (r"\bmay_import\(targets, FOLDERS, WORDS\)", "targets_phrase(targets, FOLDERS, WORDS)", 1)],
    "tests/modules/spec/application/logic/test_targets_written.py": [
        (r"targets_written import may_import\n", "targets_written import allowed_targets\n", 1),
        (r"\bmay_import\(", "allowed_targets(", 2)],
})
PYEOF
```

- [ ] **Step 2: Apply them and see the tests fail**

Run: `uv run python /tmp/xarch-4-7/t5_tests.py && timeout 300 uv run pytest -q -p no:cacheprovider tests/kernel/logic/test_imports.py tests/modules/spec/application/logic/test_targets_written.py 2>&1 | tail -5`
Expected: `2 files written`, then FAIL: two collection errors, `ImportError: cannot import name 'targets_phrase' from
'xarch.kernel.logic.imports'` and `ImportError: cannot import name 'allowed_targets' from
'xarch.modules.spec.application.logic.targets_written'`.

- [ ] **Step 3: Write the code edits**

```bash
cat > /tmp/xarch-4-7/t5_code.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

SPEC = "xarch/modules/spec/application/logic/"
apply({
    "xarch/kernel/logic/imports.py": [(r"\ndef may_import\(", "\ndef targets_phrase(", 1)],
    "xarch/modules/rules/application/logic/where.py": [
        (r"from xarch\.kernel\.logic\.imports import may_import, shown_target\n",
         "from xarch.kernel.logic.imports import shown_target, targets_phrase\n", 1),
        (r"\bmay_import\(targets, folders, profile\.words\(\)\)", "targets_phrase(targets, folders, profile.words())", 2)],
    SPEC + "docs_template.py": [
        (r"from xarch\.kernel\.logic\.imports import may_import, shown_target\n",
         "from xarch.kernel.logic.imports import shown_target, targets_phrase\n", 1),
        (r"\b_may_import\(", "_imports_may_phrase(", 2),
        (r"(?<![_.])\bmay_import\(", "targets_phrase(", 2)],
    SPEC + "targets_written.py": [(r"\ndef may_import\((.*)\n {15}problems", r"\ndef allowed_targets(\1\n" + " " * 20 + "problems", 1)],
    SPEC + "profile_parsing.py": [
        (r"targets_written import WORD, may_import\n", "targets_written import WORD, allowed_targets\n", 1),
        (r"(?<![_.])\bmay_import\(", "allowed_targets(", 2),
        (r"\b_libraries\(", "_imports_libraries(", 3),
        (r"(\ndef _imports_libraries\(.*)\n {15}reserved", r"\1\n" + " " * 23 + "reserved", 1)],
    SPEC + "imports_written.py": [
        (r"targets_written import WORD, may_import\n", "targets_written import WORD, allowed_targets\n", 1),
        (r"(?<![_.])\bmay_import\(", "allowed_targets(", 3)],
    "xarch/modules/rules/application/logic/tier_of.py": [(r"\b_may_import\(", "_folder_imports(", 2)],
})
PYEOF
```

The imports are written in the order ruff's isort keeps (`shown_target, targets_phrase`; `WORD, allowed_targets`).
The `(?<![_.])` guard keeps `_mirrored_may_import(` and attribute reads out of the call patterns; the continuation lines
of `allowed_targets`' and `_imports_libraries`' signatures move to stay under the `(`.

- [ ] **Step 4: Apply them**

Run: `uv run python /tmp/xarch-4-7/t5_code.py && git diff --stat -- xarch`
Expected: `7 files written`.

- [ ] **Step 5: Run the suite and the linter**

Run (in the background): `timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3; uv run ruff check`
Expected: `5709 passed`, `All checks passed!`.

- [ ] **Step 6: Commit**

```bash
git add xarch tests
git commit -m "The functions named for a retired key take the name of what they do: kernel's may_import becomes targets_phrase, targets_written's may_import becomes allowed_targets, and the private _may_import of the docs template and of tier_of and profile_parsing's _libraries become _imports_may_phrase, _folder_imports and _imports_libraries; every caller follows; nothing a user sees changes"
```

---

### Task 6: The last docstring, the re-grep, the outputs diffed, the golden docs and the gates

**Files:**
- Modify: `xarch/modules/rules/domain/published.py:122` (the `Loosened` docstring names the keys
  `(may_import, libraries, ...)` that looseness no longer reports; it becomes `(imports.may, imports.libraries, ...)`,
  the keys `looseness.LOOSER` holds)
- Regenerated, expected unchanged: `docs/cli/**`, `docs/web/**`, `docs/xarch/**`

**Interfaces:**
- Consumes: everything above; `/tmp/xarch-4-7/record.sh`; `/tmp/xarch-4-7-base/`.
- Produces: the branch's final commit, and the classed re-grep in this task's report (not committed).

- [ ] **Step 1: Write and apply the docstring edit**

```bash
cat > /tmp/xarch-4-7/t6_code.py <<'PYEOF'
import sys
sys.path.insert(0, "/tmp/xarch-4-7")
from apply import apply

apply({
    "xarch/modules/rules/domain/published.py": [
        (r"that loosened \(may_import, libraries, litmus and the others the spec module names\)",
         "that loosened (imports.may, imports.libraries, litmus and the others the spec module names)", 1)],
})
PYEOF
uv run python /tmp/xarch-4-7/t6_code.py
```

Expected: `1 files written`. `xarch/modules/spec/domain/published.py`'s `Loosened` docstring already names
`imports.*` (lines 110-118): read it, do not edit it.

- [ ] **Step 2: Check no docstring of spec 2.2 still names an old identifier**

Run:
```bash
sed -n 76,90p xarch/modules/spec/domain/values.py; sed -n 196,216p xarch/modules/spec/domain/values.py
sed -n 362,382p xarch/modules/spec/domain/values.py; sed -n 10,18p xarch/profile_values/tiers.py
sed -n 95,101p xarch/modules/spec/contract/__init__.py; sed -n 44,76p xarch/modules/rules/domain/profile.py
```
Expected: `Part` names `imports_must:`, `imports_types_only:`; `Tier` names `imports_types_only:`, `imports_may:`,
`imports_must:`, `imports_also:`; `Architecture` names `imports_libraries:` and `` `imports_libraries` ``;
`CheckedTier`'s and `PartView`'s docstrings name no renamed identifier (they say the values in words); `Profile`
names `imports_libraries`, `imports_must`, `holds_immutable`, `imports_types_only`, `holds_names`, `holds_built_by`.
Any old identifier left in one of these docstrings is fixed with an Edit in this task.

- [ ] **Step 3: Run the re-grep of spec 3 and class every hit**

Run:
```bash
K="immutable|names|built_by|types_only|libraries"
grep -rnE "no_callbacks|may_import|must_import|may_also_import|^\s+($K):" xarch tests architecture.yaml > /tmp/xarch-4-7/regrep.txt
wc -l /tmp/xarch-4-7/regrep.txt
grep -vE "tests/bootstrap/corpora|profile_keys.py|test_retired_keys|presets/format/keys.yaml|mirrored_may_import|may-import-everything|_may_import_everything|may_import_text|no_callbacks|def test_|id=\"" /tmp/xarch-4-7/regrep.txt \
  | grep -vE "^[^:]+:[0-9]+:\s+(names|built_by|immutable|libraries|types_only):" | grep -vE "^tests/[^:]+:[0-9]+:.*[\"']"
```
Expected (the second command; the first prints the total): only these, all in kept classes —
`docs_template.py:441,442,552` (`_must_import_line`, `_tier_must_import_line`: class 6, named for the rule id),
`rules/contract/__init__.py:197,236` (`may_import`: class 5, `where`'s answer), `expansion.py:446,447`
(`_must_import`, `_must_import_tiers`: class 6), `where_report.py:118,133` (class 5),
`tests/modules/rules/application/logic/checks.py:97,101` and `test_must_import.py:8,9` (test helpers named for the
rule id: class 6). Then read every line of `/tmp/xarch-4-7/regrep.txt` and class each one by the classes 1-8 of
spec 3 (the `^\s+(names|...):` lines are class 2, 3 or 8: e.g. `Held.names/immutable/built_by` in
`spec/domain/published.py:60-62` class 2, `rules/domain/places.py:56` and `rules/contract/__init__.py:199,238` class 5,
`Language.names`, `Target.names`, `CheckedLanguage.immutable`, `Class.immutable` and the reader's `immutable=` ports
class 8, YAML lines under `imports:` or `holds:` in test profiles class 2 or 3). Record the classed list in this
task's report. A hit in no class is a defect: fix it in the file that owns it, rerun Task 6 from Step 3, and say so
in the report.

- [ ] **Step 4: Record the after-run and diff it against the baseline**

Run:
```bash
rm -rf /tmp/xarch-4-7-after && timeout 600 bash /tmp/xarch-4-7/record.sh /tmp/xarch-4-7-after
diff -r /tmp/xarch-4-7-base /tmp/xarch-4-7-after --exclude=pytest.txt && echo IDENTICAL
```
Expected: `35`, then `IDENTICAL`. Any difference is a behaviour change: find the rename that caused it and undo
that part of it; never accept a difference.

- [ ] **Step 5: Regenerate the golden docs and see an empty diff**

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
Expected: no output from either command (no file under `docs/` changed or added). A changed file is a behaviour
change of this step: restore it with `git checkout -- <file>` and find its cause.

- [ ] **Step 6: Check the corpora are untouched**

Run: `git diff --stat 293ab8c -- tests/bootstrap/corpora docs/examples xarch/modules/spec/domain/profile_keys.py xarch/architectures/presets/format/keys.yaml`
Expected: no output.

- [ ] **Step 7: Run every gate**

Run (the suite in the background; it takes about three minutes):
```bash
timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3
uv run xarch check; echo "exit $?"
uv run xarch check --strict; echo "exit $?"
uv run ruff check
uv run xarch profile check architecture.yaml; echo "exit $?"
```
Expected: the pytest line equals `/tmp/xarch-4-7-base/pytest.txt` (`5709 passed`, nothing skipped that was not
before); both checks `exit 0` with the same notes as the base (`check --format json` was already diffed in Step 4);
`All checks passed!`; `OK: the profile is valid` and `exit 0`. No typecheck command exists.

- [ ] **Step 8: Confirm no README or CHANGELOG line**

Run: `git diff --stat 293ab8c -- README.md CHANGELOG.md`
Expected: no output. Nothing a user sees changes, so O4 and O5 add no line.

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/rules/domain/published.py
git status --short
git commit -m "Loosened's docstring names the keys looseness reports, imports.may and imports.libraries, in place of may_import and libraries; the re-grep finds only kept names, every output of check, profile check, where, profile explain and review is byte-identical to before the renames and the golden docs regenerate unchanged; nothing a user sees changes"
```

`git status --short` before the commit shows only `published.py` staged and nothing else modified (no `docs/`, no
`.claude/`).

---

## Self-review

1. **Spec coverage.** 2.2 fields: `Part` (Task 3), `Tier` and `CheckedTier` (Task 2), `Architecture.imports_libraries`,
   `PartView`, `ProfileView` (Task 3), rules' `Profile` (Task 4). 2.2 functions: all five (Task 5). Callers listed
   in 2.2: `looseness.py` (Tasks 2, 3), `publishing.py` (3), `profile_parsing.py` (3, 5), `imports_written.py` (5),
   `where.py` (4, 5), `docs_template.py` (2, 3, 5), `checked_tier.py` (2), `spec_profile.py` (3, 4), `expansion.py`
   (2, 4), `tier_of.py` (2, 5), `sentences.py` (2, 4), `filters.py` (4), `locate.py` (2). Docstrings: Tasks 2-4 in
   the same edit, checked in Task 6 Step 2; the stale `rules/domain/published.py` docstring in Task 6 Step 1 (a
   docstring the spec does not list, found by the re-grep: it names `may_import` as a looseness key, which it no
   longer is). 2.3 kept names: Global Constraints and the patterns. 2.1 items 1-4, 7: Task 1 Step 4 and Task 6
   Step 4; item 5: Task 6 Step 5; item 6: Task 6 Step 6; item 8: Task 1 Step 5 and Task 6 Step 7. Section 3: Task 6
   Step 3. Section 5: Task 6 Step 7. O4/O5: Task 6 Step 8. O8: Task 6 Step 5.
2. **Placeholders.** None: every edit is in a script with its patterns and counts; every command has its expected
   output.
3. **Type consistency.** Names used across tasks: `imports_types_only`, `imports_may`, `imports_must`,
   `imports_also` (Tier, CheckedTier, PartView where they exist), `imports_libraries` (Architecture, ProfileView,
   Profile), `holds_immutable`, `holds_names`, `holds_built_by` (Profile), `targets_phrase`, `allowed_targets`,
   `_imports_may_phrase`, `_folder_imports`, `_imports_libraries`. Task 3 reads `p.imports_may`, `p.imports_must`,
   `p.imports_types_only` and `view.imports_libraries` in `spec_profile.py`, which it defines; Task 4 renames that
   file's keywords to `Profile`'s new fields, which it defines.
4. **Review Focus.** Five lines, each pinned by Task 6 Steps 3-6 or by the scripts' exact counts.

The edit scripts were run end to end on a scratch copy of `293ab8c` (outside the worktree) before this plan was
written: each task's tests failed after its test edits and passed after its code edits (5709 passed), and
`ruff check`, `xarch check`, `xarch check --strict` and `xarch profile check architecture.yaml` passed. The golden
docs regenerated unchanged, and `check --format json` matched apart from the checkout's path.
<!-- task-pipeline: validated -->
