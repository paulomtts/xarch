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
