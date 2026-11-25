# 9.3 docs: CHANGELOG leads with 0.3.0, breaking changes first — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `CHANGELOG.md`'s `[Unreleased]` entries become one `## [0.3.0] - <commit date>` section that opens with
`### Breaking changes` (a paragraph, the table of old and new, the breaking entries), then `### Added` and
`### Changed`, held there by a new test file `tests/architecture/test_changelog.py`.

**Architecture:** The test is written first and run red. The CHANGELOG is then rebuilt by a throwaway script, kept
outside the repository, that cuts each of today's 57 entries out of the file by the line it starts on and lays them out
under the three headings, so no entry's text is retyped by hand. The table and its opening paragraph are written
verbatim from this plan, every row already checked against `v0.2.0` and this branch while the plan was written.

**Tech Stack:** Python 3.13, pytest, `uv`, ruff, Markdown (Keep a Changelog 1.1.0).

**Spec:** `docs/superpowers/specs/9-3-docs-changelog-e2b598d4.md` (copied verbatim below the line).

## Global Constraints

- Files changed: `CHANGELOG.md` and the new `tests/architecture/test_changelog.py`; nothing else in the repository.
- The 0.3.0 heading is `## [0.3.0] - YYYY-MM-DD`, the day the change is committed (`date +%F` at that moment), never
  the plan's or the notes' date.
- An empty `## [Unreleased]` heading, with no subsection, stays above `## [0.3.0]`.
- Under `## [0.3.0]`, in this order and no other: `### Breaking changes`, `### Added`, `### Changed`.
- Link line `[0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0` directly above the `[0.2.0]:` line.
  No `[Unreleased]` link.
- The 0.2.0, 0.1.1 and 0.1.0 sections: not a word changes.
- Each entry moved whole, text and wrapping unchanged; the only reworded text is the opening words of the first
  `Added` entry ("References beside the old forms of a target" -> "References as the form of a target").
- No entry dropped, merged, split or added: 57 `- ` bullets in the 0.3.0 section, as under today's `[Unreleased]`.
- No `Family`, `Status`, `ruled`, `default`, `R1`-`R5`, `Q23`, `item 6` or other notes' bookkeeping in the CHANGELOG.
- A `|` inside a table cell is written `\|`.
- No comments in the test file; a module docstring and a one-line docstring per helper, as `test_readme.py` has.
- Never `git commit` anything under `.claude/`; nothing is pushed; no tag is made; README, `pyproject.toml`,
  `uv.lock`, code under `xarch/`, profiles, corpora, `docs/` untouched. Never `ruff check --fix`.
- Long commands run under `timeout`; never `pkill`, `killall`, or `kill` by pattern.

## Review Focus

1. A `|` inside a cell left unescaped, which splits the row into three cells in a rendered table: pinned by
   `test_every_row_of_the_table_of_old_and_new_has_two_cells` (Task 1, Step 1), added for this line.
2. An entry lost, doubled or cut short while moving (a continuation line left behind, a bullet taken twice): the
   restructure script asserts the 57 start lines (Task 1, Step 5), and Task 1, Step 7 compares the sorted lines of the
   old `[Unreleased]` with the new section's, expecting only the paragraph, the table and the one reworded line.
3. The 0.2.0 section or the older link lines touched: Task 1, Step 7 diffs the tail of the file from `## [0.2.0]`
   against today's, expecting only the added `[0.3.0]:` line.
4. The `## [Unreleased]` heading read as the latest release, or the release dated wrong: the release regex needs a
   version and a date, so `[Unreleased]` never matches (test 1), and the date comes from `date +%F` in the same
   step that writes the file (Task 1, Step 5), re-read before the commit (Task 1, Step 11).
5. A table row naming something the code does not have: every row was checked on both sides while this plan was
   written (see "Deviations"), and Task 1, Step 8 re-checks the New-side names by grep.

## Deviations from the spec, and why

- Test 2 takes `<previous>` as the version of the first release heading whose version is not `pyproject.toml`'s,
  not "the second release heading". The spec wants the test red today; with the spec's wording it passes today
  (latest `0.2.0`, previous `0.1.1`, and `[0.2.0]: ...v0.1.1...v0.2.0` exists). After the edit both readings give
  `0.2.0`.
- One test beyond section 4's four: `test_every_row_of_the_table_of_old_and_new_has_two_cells` (Review Focus 1). It
  asserts structure, not prose.
- Table rows written as built, not as R3 writes them (each to be reported in the result note):
  - "order of `parts` as placement order | the tree's reading order (a `placement:` list only as the fallback)": no
    `placement:` list exists (`xarch profile explain placement` finds none); New cell is "the tree's reading order, a
    part before the parts inside it" (CHANGELOG entry 149).
  - "fact field `top-level` on `function`": in `v0.2.0`, `top-level` is a filter worked out in
    `xarch/modules/rules/application/logic/facts.py:83` (`_TOP`), not a fact field; Old cell is "the filter
    `top-level`, worked out by the checks", New "the fact `function.top_level`, which the filter reads".
  - "record computed in `facts.py`" shortened to "a record worked out by the checks".
  - `holds.classes.built_by` "(plain names)" dropped (true, but not a change of 0.3.0's).
  - `writing: {call, keyword, ...}` written in full as built: `{call, keyword, field, specs}` (`language_file.py`
    docstring, `python.yaml` `writing`).
  - The `Loosened` row's New cell gains `tiers.imports.must` (in `looseness.py:74` `LOOSER`, missing from R3).
  - The `compared_with` row's New cell gains `elsewhere` and `higher` (`profile_report.py:14`, and CHANGELOG entry
    25), and names `enforcement.profile.compared_with` in full.
  - The `where` row's New cell keeps the colon, `never uses:`: `where_report.py:62` prints it through `_line`, which
    appends `:`. `JSON` is written before `never_uses` to match the Old cell.
  - The rule id rows say "rule id `never-use`", "rule id `may-import`" on the New side too.
  - Bookkeeping dropped from cells: "(R2)", "ruled", "default", "`anchor` new", "`review.never` R5".
- The stray blank lines between some bullets of today's `[Unreleased]` (64, 241, 304, 309, 314, 321, 326, 329, 344)
  are not carried: each list is written tight, one blank line around each heading. No entry's text changes.
- Entry classing: section 3's classing is kept as written. Re-read against the rule while planning: 265 (`public`
  filter refused on other kinds: `v0.2.0` already refused a filter that does not apply to the kind read,
  `keys.yaml:1280`), 330 (relative imports followed: a correction of what was read), 339 (`unresolved`: an added
  section and key) stay in `Changed`.

The checks behind those, run while writing this plan (the executor need not re-run them; Task 1, Step 8 re-checks the
New side):
`git show v0.2.0:xarch/architectures/presets/language/python.yaml` (`extension`, `package_file`, `interface:
[typing.Protocol, ...]`, `special: __`, `nothing: None`, `comment: "#"`, `immutable: [typing.NamedTuple,
"dataclasses.dataclass(frozen=True)"]`, `standard: interpreter`, `function.tables: exact`);
`git show v0.2.0:xarch/architectures/presets/testing/pytest.yaml` (`functions: "test_*"`, `table: {decorator, row, id,
keywords}`, `spec_keywords`, `spec_position`); `git show v0.2.0:xarch/cli/reports/where_report.py` (`may not use`,
JSON `forbidden`); `git grep '"closest"' v0.2.0` (`report.py:142`); `v0.2.0` `looseness.py:34` `LOOSER`
(`may_import`, `libraries`, `forbidden`, `must_import`, `types_only`, `may_also_import`, `apply_forbidden`);
`git grep "@own" v0.2.0` (`tier_of.py`); `RULES` on this branch (has `never-use`, `may-import`, `holds`, `names`,
`immutable`, `built-by`, `must-import`, `types-only`, `libraries`, `no-callbacks`); `xarch profile explain` of
`based_on`, `testing.beside`, `testing.preset`, `guards.scenario-coverage.tier`, `guards.dead-code.untested`,
`parts.litmus`, `tiers.litmus`, `layers`, `review.never`, `parts.package_only`; `--against` in `xarch check --help`
and `xarch profile check --help`. The draft table was run through test 4's logic against `RETIRED`: no name missing;
the restructured file passed all five tests, and `xarch check`, `xarch check --strict` and `ruff check` passed with
the test file in place.

---

# The spec (verbatim)

# 9.3 docs: CHANGELOG leads with 0.3.0, breaking changes first

Card `e2b598d4`, subtask of `d96ff4b1`. Release step 25 of the merged order, the part of it this card owns: the
`[Unreleased]` entries of every step put under one `0.3.0` heading dated on release, breaking changes first, with the
table of old and new names written against what was built.

Sources, cited by short name and line (all under `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`, read only,
never edited):

- R3: `0.3.0-cohesion-review-3.md`.
  - Section 3, row 25 (288): "CHANGELOG 0.3.0 lead with the table of section 4".
  - Overlap O5 (229): "CHANGELOG | all | Each step writes under `[Unreleased]`; step 25 orders it under one 0.3.0 lead
    with the table of section 4."
  - Overlap O8 (232): the golden docs `docs/{cli,web,xarch}/testing.md` regenerate with no diff in step 25.
  - Section 4 (301-354), "The vocabulary after the release": the table `Old (0.2.0) | New (0.3.0) | Family | Status`,
    45 rows. Its `Family` and `Status` columns are the notes' bookkeeping (`ruled`, `default`, `R2`, `Q23`) and do not
    go into the CHANGELOG.
  - Sections 5 (clashes), 6 (gaps) and 7 (open questions) are not CHANGELOG material.

The truth the CHANGELOG is written against is the code as built, not the notes (card dodge: "listing a change from the
notes that was not built"). The 0.2.0 side is the tag `v0.2.0` (`git show v0.2.0:<path>`); the 0.3.0 side is this
branch:

- `xarch/modules/spec/domain/profile_keys.py` `RETIRED` (188-232): every key, value, guard and rule id retired, with
  its refusal hint;
- `xarch/modules/spec/domain/key_table.py` and `uv run xarch profile explain <key>`: every key a profile has;
- `xarch/architectures/presets/language/python.yaml` and `xarch/modules/spec/application/logic/language_file.py`
  (its docstring 1-70): the language data file's keys;
- `xarch/architectures/presets/testing/pytest.yaml`: the framework data file's keys;
- `xarch/kernel/violations.py` `RULES`: the rule ids;
- `xarch/cli/reports/where_report.py` (62, 81, 114-120) and `xarch/cli/reports/profile_report.py`: the text and JSON
  field names of `where` and of the enforcement section;
- `xarch/architectures/cli.yaml`, `web.yaml`: the bundled profiles.

`pyproject.toml` already says `version = "0.3.0"` (card 9.1, `83356b4`).

## 1. Scope

In scope: `CHANGELOG.md`, and one new test file `tests/architecture/test_changelog.py`.

1. `## [Unreleased]` (CHANGELOG.md:6) becomes `## [0.3.0] - <date>`, the date being the day the change is committed,
   written `YYYY-MM-DD` as 0.2.0's is (`## [0.2.0] - 2026-11-18`, 391). An empty `## [Unreleased]` heading, with no
   subsection under it, stays above it, as Keep a Changelog writes it, so the next step has a place to write.
2. Under `## [0.3.0]` the subsections are, in this order: `### Breaking changes`, `### Added`, `### Changed`. No other
   subsection (no `Removed`: what 0.3.0 removed is a key or value refused with a hint, which is a breaking change).
3. `### Breaking changes` opens with one paragraph and the table of old and new (section 2), then the breaking entries
   (section 3).
4. `### Added` and `### Changed` hold the remaining entries of today's `[Unreleased]`, each in its own subsection as
   today, in today's order.
5. A link reference `[0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0` is added above
   `[0.2.0]: ...` at the end of the file (565). No `[Unreleased]` link is added (the file has none today).
6. A test that holds the CHANGELOG to `pyproject.toml` and to `RETIRED` (section 4), written first.

Out of scope:

- `README.md`: card 9.2 (done, `ea6a003`, `dea3849`). The card says so: "Out of scope: README (9.2)".
- The version: card 9.1 (done, `83356b4`). `pyproject.toml` and `uv.lock` are not touched.
- The golden docs' final regeneration owned by the wrap-up (R3 O8, 232): this card regenerates them once as a gate,
  expects no diff, and edits none by hand. The CHANGELOG feeds none of them.
- The coupling audit (R3 G9): the owner's, outside the repository.
- Any code under `xarch/`, any profile, data file, recorded corpus (`tests/bootstrap/corpora/`), file under
  `docs/superpowers/` or `docs/examples/`.
- The 0.2.0, 0.1.1 and 0.1.0 sections (391-563): not a word changes.
- A tag or a push: nothing is pushed, no tag is made.

## 2. The table of old and new

Placed in `### Breaking changes`, after the opening paragraph. Two columns, `| 0.2.0 | 0.3.0 |`, a header, a `|---|---|`
line, then one row per change, with no blank line inside the table, cells' keys and values in backticks as R3 writes
them. The opening paragraph is one or two sentences: a profile, a data file or a reader of the JSON written for 0.2.0
reads as the table says in 0.3.0; a retired key is refused with a hint saying what to write (`xarch profile check`
lists every one); the entries after the table say each change in full.

The rows are R3 section 4's rows (303-354), the Family and Status columns dropped, each kept only after it is checked
against the code on both sides:

- the Old cell against `v0.2.0` (the file the key lived in at the tag, or `git grep <name> v0.2.0 -- xarch/`);
- the New cell against this branch (section "Sources" above).

Rules for the rows:

- A row whose New side is not built, or is built under another name or form, is written as built, or dropped when
  nothing of it was built. Every such case is reported in the result note, row by row. This spec's own check of the
  New side found each of these built: `never-use` and `may-import` in `RULES`; `never uses` / `never_uses` in
  `where_report.py`; `uses.apply_never`, `plain_tables`, `testing.beside`, `testing: {preset, beside}`, `--against`,
  `compared_with` with `chosen_by`, `low`, `counts`, `only_here`, `only_there`, `anchor`; in `python.yaml` and
  `language_file.py`: `extensions`, `package_files`, `comments`, `standard` (`interpreter` or `{modules, reserved,
  builtins}`), `interface: [{base} | {keyword}]`, `nothing: [None]`, `special` as a pattern, `package`, `member`,
  `unannotated`, `immutable` marks `{base} | {decorator, keywords} | {fields} | {type}`, `writing`; the facts
  `import.resolved`, `class.interface`, `test.function`, `test.call`; `testing.globals`. The executor re-checks each,
  and checks the rest.
- The Old cell `where` text `may not use:` is checked against `v0.2.0`'s `where_report.py`, and the New cell is written
  as the label is printed today (`never uses`, `where_report.py:62`), without a colon if the code prints none.
- The row `none | facts import.resolved, ...` and the other `none | ...` rows are additions, not breaking changes.
  They stay in the table (the table is the vocabulary after the release, R3 301), with `none` in the 0.2.0 cell.
- The last row ("`holds` (name), `untested`, ... | unchanged") stays as the table's last row, saying these names did
  not change.
- The row "privacy from `private: _` in the checking code | the fact `public`, ..." describes where a thing is read,
  not a key a profile writes; it stays, as R3 writes it, only if `public` is a fact today (it is:
  `python.yaml` `supplies: public`).
- A `|` inside a cell (R3 writes `interface: [{base} | {keyword}]`, `{decorator | call | loop, ...}`, `<bundled> | <path ...>`
  in New cells, and may in Old cells) is written `\|`, so the row keeps two cells in a rendered table; the backticks do
  not protect a pipe in a Markdown table.
- A cell's wording may be shortened to fit; no row says anything the code does not do.
- Every 0.3.0 move in `RETIRED` (an entry whose text holds `0.3.0`) has its name in some row's 0.2.0 cell (the test of
  section 4 holds this).

## 3. Which entries are breaking

An entry is breaking when something that worked with 0.2.0 is refused, renamed, or reads differently with 0.3.0: a
profile's key or value, a framework or language data file's key, a fact name a check or eval of one's own reads, a
rule id, a placeholder, a field of `--format json`, or the findings a project on a bundled profile gets. Today's
`[Unreleased]` entries are classed so (by the line their bullet starts on in today's file; the executor re-reads each
against the rule above and may move an entry the other way, saying so in the result note):

Breaking, moved from `### Changed` to `### Breaking changes`, in today's order: 149 (`parts` is the folder tree; `path`
and `folders` retired), 159 (`testing.functions` to `testing.declared`), 162 (`testing.table` to `testing.tables`), 169
(`{name}` refused, `{name:snake}`), 173 (fact `function.tables` split in three), 187 (`enforcement.profile.closest` to
`compared_with`), 198 (a part's `imports` group), 209 (a tier's `imports` group), 218 (`holds` a map of kinds), 229
(findings name the nested keys), 243 (keys held to facts at any depth), 248 (`no_callbacks` to the guard), 255 (an eval
held to its facts), 259 (language file `immutable` marks), 269 (`comment` to `comments`), 276 (`extension`,
`package_file` to lists), 283 (`standard`), 292 (`interface` marks), 305 (retired keys refused with hints), 310 (`tier`
to `tests`), 315 (`forbidden` to `uses.never` / `never`), 322 (rule id `rules` to `may-import`), 354
(`testing.mocks.specs`), 368 (bundled profiles write references; a tier's `must` and `types_only` refuse
`<word>.<part>`), 378 (the old forms of a target refused).

Not breaking, staying in `### Changed`, in today's order: 178, 182, 189, 235, 239, 265, 302, 327, 330, 339, 345, 362.

`### Added` (8-146) stays as it is, with one exception: an entry that describes a state that existed only inside the
0.3.0 cycle, which a reader upgrading from 0.2.0 never saw, is written in its built form. Found by this spec: the first
entry (10), "References beside the old forms of a target", says references were added beside the old forms; as
released, the old forms are refused (378). Its opening words become "References as the form of a target" (or the
like), and the rest of the entry, which says what a reference is and how one written wrong is refused, stays word for
word. No other entry is reworded; one the executor finds of the same kind is fixed the same way and reported.

An entry is moved whole, its text unchanged, its wrapping unchanged. No entry is dropped, merged or split, and none is
added beyond the paragraph and table of section 2.

## 4. Tests

One new file, `tests/architecture/test_changelog.py`, written before the CHANGELOG edit and run red first.

Tier: architecture. Why: `tests/architecture/` is where the repository's documents are held to the code
(`test_readme.py` holds the README to `RULES`, the app and the key table; `test_package_version.py` reads
`pyproject.toml`); these tests read `CHANGELOG.md`, `pyproject.toml` and `RETIRED`, with no app under test, no fixture
project and no command run, so they fit neither the unit tiers under `tests/modules/` nor the scenario tiers under
`tests/bootstrap/`.

The file has a module docstring, as its neighbours do, and no comments. It reads `CHANGELOG.md` and `pyproject.toml`
from `Path(__file__).resolve().parents[2]`, as `test_readme.py:14` and `test_package_version.py:6` do.

1. `test_the_latest_release_is_the_version_pyproject_gives`: the first heading matching `## [<x.y.z>] - <YYYY-MM-DD>`
   (a regex over the file, `^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})$`, multiline) has the version
   `pyproject.toml`'s `[project] version` gives, and its date parses as a date (`datetime.date.fromisoformat`). Red
   today: the first match is `0.2.0`. Why: a release whose CHANGELOG still leads with the last one is the failure this
   card fixes, and the test keeps it fixed for every later release.
2. `test_the_latest_release_has_a_compare_link`: the file holds a line `[<version>]: https://github.com/paulomtts/xarch/compare/v<previous>...v<version>`,
   where `<previous>` is the version of the second release heading. Red today (no `[0.3.0]:` line).
3. `test_the_latest_release_leads_with_its_breaking_changes`: the `###` headings between the latest release heading
   and the next `## ` heading are exactly `["Breaking changes", "Added", "Changed"]`. Red today (there is no 0.3.0
   heading; the test fails on the first test's lookup or finds 0.2.0's `Added, Changed, Removed`). Why the exact list:
   it pins "breaking changes first" and that the entries were sorted, not just headed.
4. `test_every_name_retired_in_this_release_is_in_the_table_of_old_and_new`: the table is the lines starting with `|`
   directly under `### Breaking changes`'s paragraph (the first run of `|` lines in that subsection), header and
   `|---|` line aside; its 0.2.0 cells are each row's first cell (the text between the row's leading `|` and the first `|` not preceded by a
   backslash). For each `Retired` in `RETIRED` whose `text` holds
   `"0.3.0"`, its `name` (and, when `value` is set, its `value`) appears as a whole word (`\b...\b`, with `re.escape`)
   inside a backticked span of some 0.2.0 cell. The assertion compares the sorted list of names found missing against
   `[]`, so a failure names every one at once. Red today (no table). Why: it ties the table to what was built: a move
   the code makes and the table forgets fails, by name. It does not prove a row is built (that is a read, section 2);
   it proves no built move is missing.

The test helpers (a function returning the latest release's section text, one returning the table's first cells) are
plain functions in the test file with a one-line docstring each, as `between` and `options` are in `test_readme.py`.

No test is written for the table's New cells or the entry classing: they are prose checked by the reads of sections 2
and 3, and a test asserting a sentence is present would restate the edit.

## 5. Error paths and edge cases the tests must handle

- The `## [Unreleased]` heading above the release has no date and does not match the release regex; it is skipped,
  not read as the latest release.
- A `###` heading inside a later release section (0.2.0's `Removed`) is not counted: the section ends at the next line
  starting `## `.
- A backticked span in a 0.2.0 cell holding several names (`` `parts.<p>.path`, `parts.<p>.folders` ``, or the
  `Loosened` row's list) counts every name in it; `\b` keeps `tier` from matching inside `tiers` only if the word
  boundary falls there: `tiers.<t>` holds `tier` followed by `s`, so `\btier\b` does not match it, and the row
  `` `parts.<p>.tier: unit` `` is the one that must carry `tier`.
- `RETIRED` names whose text does not hold `0.3.0` (`never` and `apply_never` as part or tier keys, `never` and
  `types_only` under `imports`, the settings refused under a kind) are hints for misplaced keys, not moves of the
  release, and are not required in the table.
- The table's end: the first line after the table not starting with `|`. The entries after it are not read as rows.

## 6. Gates

Each passes on this branch alone, with the full suite green:

- `uv run pytest -q` (over two minutes: run it in the background with `timeout`, read it at the end)
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check` (never `ruff --fix`)
- `uv run xarch profile check architecture.yaml`
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated as `tests/bootstrap/test_docs_templates.py` builds them,
  `git diff docs/` read: empty (R3 O8, 232). Never edited by hand.
- `git diff v0.2.0 -- CHANGELOG.md` read: only lines above `## [0.2.0]` and the one link line change.
- The count of `- ` bullets in the 0.3.0 section equals the count under today's `[Unreleased]` (57, CHANGELOG.md:8-390):
  no entry dropped or added.

## 7. Project rules that bind this card

- No comments in xarch's code, the new test included; docstrings as the file's neighbours have them.
- Tests written first, run red, then the CHANGELOG edit.
- `.claude/` stays out of commits; nothing is pushed; no file outside the repository is edited.
- README untouched (9.2).
- Recorded corpora untouched.

## 8. Dodges

- Listing a change from the notes that was not built: every table row is checked on both sides (section 2); a row not
  built is dropped or written as built and reported.
- Carrying the notes' bookkeeping into the CHANGELOG: no `Family`, `Status`, `ruled`, `default`, `R1`-`R5`, `Q23`,
  `item 6` and the like.
- Rewriting entries while moving them: each is moved whole, except the one found in section 3, reworded at its opening
  words only.
- Dating the release with the notes' or the plan's date: the date is the day of the commit.

---

# Tasks

## File structure

- Create: `tests/architecture/test_changelog.py` — holds `CHANGELOG.md` to `pyproject.toml`'s version and to
  `RETIRED` (`xarch/modules/spec/domain/profile_keys.py:188-232`). Guard tier (`architecture.yaml` tier `guard`,
  `folder: architecture`), beside `test_readme.py` and `test_package_version.py`.
- Modify: `CHANGELOG.md:6-390` (the `[Unreleased]` section) and the link lines at its end (565).
- Scratch, outside the repository, never committed: `/tmp/xarch-9-3/breaking.md` (the opening paragraph and the
  table) and `/tmp/xarch-9-3/restructure.py` (the one-shot rewrite).

One task: the test is red until the CHANGELOG is rewritten, and a reviewer could not approve one without the other.

### Task 1: The CHANGELOG leads with 0.3.0, held by a test

**Files:**
- Create: `tests/architecture/test_changelog.py`
- Modify: `CHANGELOG.md:6-390`, `CHANGELOG.md:565`
- Scratch: `/tmp/xarch-9-3/breaking.md`, `/tmp/xarch-9-3/restructure.py`

**Interfaces:**
- Consumes: `RETIRED: tuple[Retired, ...]` from `xarch.modules.spec.domain.profile_keys`, each `Retired` with
  `scope: str`, `name: str`, `text: str`, `value: str = ""`; `pyproject.toml` `[project] version` (`"0.3.0"`).
- Produces: nothing other tasks read.

- [ ] **Step 1: Write the failing test**

Create `tests/architecture/test_changelog.py` with exactly this content:

```python
"""The CHANGELOG leads with the release pyproject.toml gives: its heading is that version with a date, a link compares
it with the release before, it opens with its breaking changes, and its table of old and new names every key, value
and rule id the release retired."""
import re
import tomllib
from datetime import date
from pathlib import Path

from xarch.modules.spec.domain.profile_keys import RETIRED

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
RELEASE = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})$", re.MULTILINE)
CELL = re.compile(r"(?<!\\)\|")


def latest_release() -> str:
    """The text of the first release headed with a version and a date, up to the next heading of level two."""
    rest = CHANGELOG[RELEASE.search(CHANGELOG).end():]
    following = re.search(r"^## ", rest, re.MULTILINE)
    return rest[:following.start()] if following else rest


def table_rows() -> list[list[str]]:
    """The cells of each row of the first table under the latest release's breaking changes, header and rule aside."""
    breaking = latest_release().partition("### Breaking changes\n")[2].split("\n### ")[0].splitlines()
    first = next((i for i, line in enumerate(breaking) if line.startswith("|")), len(breaking))
    end = next((i for i in range(first, len(breaking)) if not breaking[i].startswith("|")), len(breaking))
    return [CELL.split(row)[1:-1] for row in breaking[first:end][2:]]


def test_the_latest_release_is_the_version_pyproject_gives():
    version, day = RELEASE.search(CHANGELOG).groups()
    assert (version, date.fromisoformat(day).isoformat()) == (VERSION, day)


def test_the_latest_release_has_a_compare_link():
    previous = next(version for version, _ in RELEASE.findall(CHANGELOG) if version != VERSION)
    link = f"[{VERSION}]: https://github.com/paulomtts/xarch/compare/v{previous}...v{VERSION}"
    assert link in CHANGELOG.splitlines()


def test_the_latest_release_leads_with_its_breaking_changes():
    assert re.findall(r"^### (.+)$", latest_release(), re.MULTILINE) == ["Breaking changes", "Added", "Changed"]


def test_every_row_of_the_table_of_old_and_new_has_two_cells():
    rows = table_rows()
    assert rows and [row for row in rows if len(row) != 2] == []


def test_every_name_retired_in_this_release_is_in_the_table_of_old_and_new():
    spans = [span for row in table_rows() for span in re.findall(r"`([^`]+)`", row[0])]
    named = [word for retired in RETIRED if "0.3.0" in retired.text
             for word in (retired.name, retired.value) if word]
    missing = {word for word in named if not any(re.search(rf"\b{re.escape(word)}\b", span) for span in spans)}
    assert sorted(missing) == []
```

- [ ] **Step 2: Run it to see it fail**

Run: `timeout 120 uv run pytest -q tests/architecture/test_changelog.py 2>&1 | tail -8`
Expected: `5 failed`, with these reasons:
- `test_the_latest_release_is_the_version_pyproject_gives`: `assert ('0.2.0', '2026-11-18') == ('0.3.0', '2026-11-18')`
- `test_the_latest_release_has_a_compare_link`: `'[0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0' in [...]`
- `test_the_latest_release_leads_with_its_breaking_changes`: `['Added', 'Changed', 'Removed'] == ['Breaking changes', 'Added', 'Changed']`
- `test_every_row_of_the_table_of_old_and_new_has_two_cells`: `assert []` (no table)
- `test_every_name_retired_in_this_release_is_in_the_table_of_old_and_new`: `assert ['apply_forbidden', ...] == []`

A failure for another reason (an import error, a `StopIteration`) is a bug in the test: fix the test, not the
CHANGELOG.

- [ ] **Step 3: Write the opening paragraph and the table to the scratch file**

```bash
mkdir -p /tmp/xarch-9-3
cat > /tmp/xarch-9-3/breaking.md <<'EOF'
A profile, a data file or a reader of the JSON written for 0.2.0 reads as the table says in 0.3.0. A retired key
or value is refused with a hint saying what to write (`xarch profile check` lists every one); the entries after the
table say each change in full.

| 0.2.0 | 0.3.0 |
|---|---|
| `forbidden` (the top-level block) | `never` |
| `parts.<p>.forbidden: pure` | `parts.<p>.uses: {never: pure}` |
| none | an entry of a `never` list naming another list (`published: [pure, typing.Any]`) |
| `tiers.<t>.apply_forbidden: true` | `tiers.<t>.uses: {apply_never: true}` |
| rule id `forbidden` | rule id `never-use` |
| rule id `rules` | rule id `may-import` |
| `where` text `may not use:`, JSON `forbidden` | `never uses:`, JSON `never_uses` |
| `parts.<p>.tier: unit` | `parts.<p>.tests: unit` |
| `holds: classes` | `holds: {classes: {}}` |
| `holds: functions` | `holds: {functions: {}, records: {}, exceptions: {}}` |
| `parts.<p>.names` | `parts.<p>.holds.<kind>.names` (every kind, `records` included) |
| `parts.<p>.immutable` | `holds.classes.immutable`, `holds.records.immutable` |
| `parts.<p>.built_by` | `holds.classes.built_by` |
| `parts.<p>.no_callbacks: true` | `guards.no-callbacks: {parts: [...]}` |
| `parts.<p>.may_import` | `parts.<p>.imports.may` |
| `parts.<p>.must_import` | `parts.<p>.imports.must` (each entry also in `may`) |
| `parts.<p>.libraries` | `parts.<p>.imports.libraries` |
| `parts.<p>.types_only: [ports]` | a mark on the entry: `imports.may: [{module.ports: types_only}]` |
| `tiers.<t>.may_import` | `tiers.<t>.imports.may` |
| `tiers.<t>.may_also_import` | `tiers.<t>.imports.also` |
| `tiers.<t>.must_import: [controller]` | `tiers.<t>.imports.must: [parts.controller]` |
| `tiers.<t>.types_only: [controller]` | `tiers.<t>.imports.types_only: [parts.controller]` |
| `<part>@any`; the bare name of a part in no repeating folder | `parts.<part>` |
| the bare name of a part in a repeating folder; `<part>@own` | `<word>.<part>`, such as `module.domain` |
| `/path`, `:pattern`, `everything` | unchanged |
| `parts.<p>.path`, `parts.<p>.folders` | the folder tree of `parts`; `parts.<p>.name` where needed |
| the order of `parts` as the placement order | the tree's reading order, a part before the parts inside it |
| the filter `top-level`, worked out by the checks | the fact `function.top_level`, which the filter reads |
| `testing.table: {decorator, row, id, keywords}` | `testing.tables: [{decorator \| call \| loop, columns_from, rows, row, id}]` |
| the fact `function.tables` | `function.tables.decorator`, `function.tables.call`, `function.tables.loop` |
| none | `writing: {call, keyword, field, specs}` in the language file |
| guard `scenario-coverage` `file: test_{name}.py` | `file: test_{name:snake}.py` (also `kebab`, `camel`, `pascal`) |
| `testing.functions: "test_*"` | `testing.declared: [{function: "test_*"}]` |
| none | `testing.globals` |
| `testing.mocks.spec_keywords`, `spec_position` | `testing.mocks.specs: [{keyword} \| {position} \| {type_argument}]` |
| none | `testing.beside: true` |
| `testing: pytest` only as a name, or a whole map | also `testing: {preset: pytest, beside: true}` |
| language file `interface: [names]`, `nothing: None`, `special: __` | `interface: [{base} \| {keyword}]`, `nothing: [None]`, `special: <pattern>`; new `package`, `member`, `unannotated` |
| `standard: interpreter` only | `interpreter`, or `{modules, reserved, builtins}` |
| `extension: .py`, `package_file: __init__.py` (required) | `extensions: [.py]`, `package_files: [__init__.py]` (optional) |
| `comment: "#"` | `comments: [{line} \| {block} \| {doc}]` |
| privacy from `private: _` in the checking code | the fact `public`, set by the reader; `private` read by the reader, scaffold and layout only |
| a record worked out by the checks; `immutable: [names, "call(k=v)"]` | the fact `class.record`; `immutable: [{base} \| {decorator, keywords} \| {fields} \| {type}]` |
| none | facts `import.resolved`, `class.interface`, `file.package`, `comment.doc`, `public`, `class.record`, `test.function`, `test.call`, `call.type_arguments`; enforcement section `unresolved` |
| `Loosened` keys `forbidden`, `apply_forbidden`, `may_import`, `libraries`, `must_import`, `types_only`, `may_also_import` | `uses.never`, `uses.apply_never`, `imports.may`, `imports.libraries`, `imports.must`, `imports.types_only`, `imports.also`; new `holds`, `holds.<kind>.<setting>`, `shared`, `imports.may.types_only`, `tiers.imports.must`, `plain_tables`, `testing.beside` |
| `where` JSON `may_import`, `may_import_text`, `libraries`, `test.types_only` | unchanged |
| `check` JSON `enforcement.profile.closest` | `enforcement.profile.compared_with`, with `chosen_by`, `match`, `low`, `counts`, `only_here`, `only_there`, `elsewhere`, `higher`, `anchor` |
| none | `--against <profile>` on `check` and `profile check`; refused with `--strict` |
| `based_on: <bundled>` | `based_on: <bundled> \| <path from this file's folder>` |
| `holds` (name), `untested`, `tiers`, `guards.scenario-coverage.tier`, `in: {tier}`, `guards.dead-code.untested`, `tests_only`, `package_only`, `shared`, `litmus` (part and tier), `layers`, `review.never`, rule ids `holds`, `names`, `immutable`, `built-by`, `must-import`, `types-only`, `libraries`, `no-callbacks`, filter `may-import-everything` | unchanged |
EOF
```

The heredoc is quoted (`'EOF'`), so backticks, `\|` and `{...}` are written as they stand.

- [ ] **Step 4: Write the restructure script to the scratch file**

```bash
cat > /tmp/xarch-9-3/restructure.py <<'EOF'
import sys
from pathlib import Path

ADDED = [10, 25, 34, 42, 52, 59, 65, 69, 74, 81, 85, 90, 98, 101, 107, 110, 121, 127, 138, 142]
BREAKING = [149, 159, 162, 169, 173, 187, 198, 209, 218, 229, 243, 248, 255, 259, 269, 276, 283, 292, 305, 310, 315,
            322, 354, 368, 378]
CHANGED = [178, 182, 189, 235, 239, 265, 302, 327, 330, 339, 345, 362]
OLD_OPENING = "- References beside the old forms of a target: "
NEW_OPENING = "- References as the form of a target: "

source, table, date = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
lines = source.read_text(encoding="utf-8").splitlines()
assert lines[5] == "## [Unreleased]" and lines[390].startswith("## [0.2.0] - ")
starts = sorted(ADDED + BREAKING + CHANGED)
assert len(starts) == 57 and all(lines[n - 1].startswith("- ") for n in starts)
assert sum(line.startswith("- ") for line in lines[6:390]) == 57


def entry(start: int) -> list[str]:
    taken = [lines[start - 1]]
    for line in lines[start:390]:
        if not line.startswith("  "):
            break
        taken.append(line)
    return taken


def entries(numbers: list[int]) -> list[str]:
    return [line for n in numbers for line in entry(n)]


added = entries(ADDED)
assert added[0].startswith(OLD_OPENING)
added[0] = NEW_OPENING + added[0][len(OLD_OPENING):]
release = ["## [Unreleased]", "", f"## [0.3.0] - {date}", "", "### Breaking changes", "",
           *table.read_text(encoding="utf-8").rstrip("\n").splitlines(), "", *entries(BREAKING), "",
           "### Added", "", *added, "", "### Changed", "", *entries(CHANGED), ""]
link = "[0.2.0]: https://github.com/paulomtts/xarch/compare/v0.1.1...v0.2.0"
rest = lines[390:]
rest.insert(rest.index(link), "[0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0")
source.write_text("\n".join(lines[:5] + release + rest) + "\n", encoding="utf-8")
EOF
```

What it does: it asserts today's layout (`[Unreleased]` at line 6, `## [0.2.0] - ` at line 391, a bullet at each of
the 57 start lines, 57 bullets in all), takes each entry as its bullet line and the two-space continuation lines
after it, rewords the first `Added` entry's opening words only, writes `## [Unreleased]`, `## [0.3.0] - <date>`,
`### Breaking changes` with the scratch paragraph and table then the 25 breaking entries, `### Added` with the 20
added entries, `### Changed` with the 12 others, then lines 391 onward unchanged but for the `[0.3.0]:` link line
inserted above `[0.2.0]:`.

The start lines are section 3's classing: breaking 149, 159, 162, 169, 173, 187, 198, 209, 218, 229, 243, 248, 255,
259, 269, 276, 283, 292, 305, 310, 315, 322, 354, 368, 378; not breaking 178, 182, 189, 235, 239, 265, 302, 327, 330,
339, 345, 362; added 10 through 142.

- [ ] **Step 5: Rewrite the CHANGELOG, dated today**

Run: `uv run python -I /tmp/xarch-9-3/restructure.py CHANGELOG.md /tmp/xarch-9-3/breaking.md "$(date +%F)" && grep -n '^##' CHANGELOG.md | head -6`
Expected: no assertion error, and

```
6:## [Unreleased]
8:## [0.3.0] - <today, YYYY-MM-DD>
10:### Breaking changes
241:### Added
379:### Changed
444:## [0.2.0] - 2026-11-18
```

An `AssertionError` means `CHANGELOG.md` is not the file this plan was written against: stop and report it; do not
adjust the line numbers by guess. To start over: `git checkout -- CHANGELOG.md`.

- [ ] **Step 6: Run the test to see it pass**

Run: `timeout 120 uv run pytest -q tests/architecture/test_changelog.py 2>&1 | tail -2`
Expected: `5 passed`

- [ ] **Step 7: Check that nothing was lost, doubled or touched below 0.3.0**

Run:

```bash
diff <(git show HEAD:CHANGELOG.md | sed -n '391,$p') <(sed -n '444,$p' CHANGELOG.md)
diff <(git show HEAD:CHANGELOG.md | sed -n 7,390p | grep -v '^$' | grep -v '^###' | sort) \
     <(sed -n 9,443p CHANGELOG.md | grep -v '^$' | grep -v '^###' | grep -v '^|' | sort)
awk '/^## \[0\.3\.0\]/{f=1;next} /^## \[0\.2\.0\]/{f=0} f && /^- /' CHANGELOG.md | wc -l
sed -n 6,9p CHANGELOG.md
```

Expected:
- first diff: only `> [0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0`;
- second diff: only the three lines of the opening paragraph added (`> A profile, a data file ...`, `> or value is
  refused ...`, `> table say each change in full.`) and the one changed line
  `< - References beside the old forms of a target: a part's ...` / `> - References as the form of a target: a part's ...`;
- `57`;
- `## [Unreleased]`, a blank line, `## [0.3.0] - <today>`, a blank line (no subsection under `[Unreleased]`).

- [ ] **Step 8: Re-check the table's New side against the code**

Run:

```bash
for t in never-use may-import apply_never plain_tables chosen_by only_here only_there anchor elsewhere higher \
         function.tables.decorator 'name:snake' globals type_argument extensions package_files comments unannotated \
         import.resolved class.interface file.package comment.doc class.record test.function test.call \
         call.type_arguments unresolved compared_with tiers.imports.must; do
  printf '%-26s %s\n' "$t" "$(git grep -l -F -- "$t" -- xarch/ | wc -l)"; done | awk '$2 == 0'
uv run xarch profile explain testing.beside >/dev/null && uv run xarch profile explain testing.preset >/dev/null && echo explain-ok
sed -n 62p xarch/cli/reports/where_report.py
```

Expected: the loop prints nothing (every name is in `xarch/`), `explain-ok`, and line 62 reads
`        lines.append(_line("never uses", ", ".join(where.uses_never)))`. A name printed by the loop is a row not
built: write it as built or drop it, re-run Steps 5-7 from `git checkout -- CHANGELOG.md`, and report it.

- [ ] **Step 9: Read the new section whole**

Run: `sed -n 6,60p CHANGELOG.md` and `sed -n 236,246p CHANGELOG.md` and `sed -n 374,384p CHANGELOG.md`
Expected: the paragraph, a blank line, the table (`awk 'NR>=8 && NR<=443 && /^\|/' CHANGELOG.md | wc -l` prints
`52`: the header, the rule line and 50 rows), a blank line, the
first breaking entry ("- `parts` is the app's folder tree: ..."); one blank line before and after each `###`
heading; no `Family`, `Status`, `ruled`, `default`, `R2`, `Q23` anywhere in lines 8-443
(`sed -n 8,443p CHANGELOG.md | grep -nwE 'ruled|Family|Status|R[1-5]|Q2[0-9]'` prints nothing).

- [ ] **Step 10: The gates**

Run, one at a time, each expected to exit 0:

```bash
timeout 900 uv run pytest -q > /tmp/xarch-9-3/pytest.log 2>&1; echo "pytest exit $?"; tail -3 /tmp/xarch-9-3/pytest.log
uv run xarch check > /dev/null; echo "check exit $?"
uv run xarch check --strict > /dev/null; echo "strict exit $?"
uv run ruff check
uv run xarch profile check architecture.yaml > /dev/null; echo "profile check exit $?"
timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py 2>&1 | tail -1
git status --short
git diff --stat v0.2.0 -- CHANGELOG.md
```

The full suite takes over two minutes; run its line with the Bash tool's background mode and read the log when it
exits. Expected: every exit `0`, `All checks passed!` from ruff, the docs-templates tests `passed` with no failure,
`git status --short` listing only ` M CHANGELOG.md`, `?? tests/architecture/test_changelog.py` and this card's spec
and plan under `docs/superpowers/` (nothing else under `docs/`: the golden docs did not move), and the `v0.2.0` diff
showing changes only above `## [0.2.0]` and the one link line: `diff <(git show v0.2.0:CHANGELOG.md | sed -n
'/^## \[0.2.0\]/,$p') <(sed -n '/^## \[0.2.0\]/,$p' CHANGELOG.md)` prints only
`> [0.3.0]: https://github.com/paulomtts/xarch/compare/v0.2.0...v0.3.0`. A gate that fails is read
and fixed in this task's files; a golden doc is never edited by hand.

- [ ] **Step 11: Commit, dated as the heading is**

Check first that the heading still carries today's date (a commit made after midnight must re-date it):

Run: `grep -n "^## \[0.3.0\] - $(date +%F)$" CHANGELOG.md`
Expected: `8:## [0.3.0] - <today>`. If it prints nothing, run
`sed -i "8s/.*/## [0.3.0] - $(date +%F)/" CHANGELOG.md` and re-run Step 6.

```bash
git add CHANGELOG.md tests/architecture/test_changelog.py
git commit -m "$(cat <<'EOF'
The CHANGELOG leads with 0.3.0, the version pyproject.toml gives: the [Unreleased] entries sit under one dated 0.3.0 heading, breaking changes first with the table of old and new names written against what was built, then Added and Changed; a test holds the latest release to pyproject.toml, its compare link, its three headings and every name RETIRED moves in 0.3.0 to the table

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
EOF
)"
```

Never `git add` the scratch files, anything under `.claude/`, or the spec and plan (the workflow commits those).
<!-- task-pipeline: validated -->
