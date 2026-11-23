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
