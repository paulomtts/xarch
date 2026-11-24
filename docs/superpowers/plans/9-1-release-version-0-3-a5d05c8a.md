# 9.1 Release: version 0.3.0 with every note's re-grep clean — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make xarch's version 0.3.0 (`pyproject.toml`, `uv.lock`, `xarch --version`), run the four notes' re-greps
once together over the final branch and class every hit (fixing any leftover), check the twenty coupling-audit rows
on this branch, and post one card comment on `a5d05c8a` with (A) the rows that move to N and (B) the hits reported,
not fixed.

**Architecture:** One code commit (the version bump, proved by the existing packaging test failing before `uv sync`
and passing after). The re-grep and the audit-row check are read-only runs whose output is saved under
`/tmp/xarch-9-1/` (never committed); a leftover, if one is found, is fixed test-first in its own commit in the shape
of the step that owns it. The last task runs the gates and the golden-docs check, then posts the card comment built
from the `/tmp/xarch-9-1/` files.

**Tech Stack:** Python 3.13, `uv` (`uv lock`, `uv sync`, `uv run`), `pytest`, `ruff`, xarch's own `xarch check` /
`xarch profile check`, GNU `grep`, `brd` (the board CLI).

**Spec:** `docs/superpowers/specs/9-1-release-version-0-3-a5d05c8a.md` (prepended below, verbatim).

## Global Constraints

- `pyproject.toml` line 3 reads `version = "0.3.0"`; no other line of it changes (spec 2).
- `uv.lock` is produced by `uv lock` (never `--upgrade`, never by hand); `git diff uv.lock` shows the one `version`
  line of `name = "xarch"` and nothing else, else revert and report (spec 2).
- `uv run xarch --version` prints exactly `xarch 0.3.0` and a newline, exit 0; `uv lock --check` exits 0 (spec 2).
- The CHANGELOG `[0.2.0]` entry and `tests/modules/spec/application/logic/test_parts_tree.py:3` keep `0.2.0` (spec 2).
- No new test pins the string `0.3.0`; no test or guard is added for the re-grep (spec 5).
- A note's allowed list is never widened; a hit outside it is a leftover (fixed) or a reported class (spec 3.2-3.4).
- Never edit `docs/superpowers/**`, `docs/examples/**`, `tests/bootstrap/corpora/**` (except as a note says),
  `python-coupling-audit.md` or any file outside the repository (spec 1, 7, 8).
- Golden docs `docs/{cli,web,xarch}/*.md` only regenerated, never edited by hand; expected not to move (spec 1, 7).
- No CHANGELOG line unless a leftover fix changes behaviour; then under `[Unreleased]` (spec 1, 3.4).
- No comments in xarch's code; never `uv run ruff check --fix`; tests first; lines at most 120 columns in prose files.
- `.claude/` stays out of commits; nothing is pushed, tagged or published (spec 1, 7).
- Never `pkill`/`killall`/pattern kills; stop a stuck run with `timeout` (brief).

## Review Focus

1. **A stale environment.** After `pyproject.toml` says 0.3.0, `uv run` (which syncs) and `uv run --no-sync` behave
   differently; a person running `uv run --no-sync xarch --version` before `uv sync` sees `xarch 0.2.0`. Expected: after
   Task 1, both `uv run xarch --version` and `uv run --no-sync xarch --version` print `xarch 0.3.0`. Pinned in Task 1
   Step 6.
2. **`uv lock` moving more than one line** (a newer resolver, a yanked wheel). Expected: the diff is the one version line;
   anything more is reverted with `git checkout -- uv.lock` and reported, not committed. Pinned in Task 1 Step 4.
3. **Code that moved since `79ea9d4`.** The re-grep must be run on the final branch (after any leftover fix), not
   trusted from the spec's counts. Expected: every line of the final run is classed; an unclassed line fails the run.
   Pinned in Task 2 Step 3 (the classifier prints `UNCLASSED` lines and the step expects none) and rerun in Task 4.
4. **Hits hidden by `--exclude-dir=superpowers`.** Expected: both runs (with and without the exclusion) are saved and
   the class-1 count is the difference between them, reported in (B). Pinned in Task 2 Steps 1-2.
5. **A coupling row listed as N without evidence on this branch, or `testing.functions` listed as a live key.**
   Expected: every N line carries one file:line seen in this branch's tree; a row whose check fails goes under "not
   moved"; `testing.functions` is listed as retired with successor `testing.declared`. Pinned in Task 3 Step 2 (the
   evidence script fails on any row without a confirmed line).

---

# The spec (verbatim)

# 9.1 release: version 0.3.0 with every note's re-grep clean

Card `a5d05c8a`, subtask of `d96ff4b1`. Release step 25 of the merged order, the parts of it this card owns: the
version, the combined re-grep, and the list of coupling-audit rows that move to N.

Sources, cited below by short name and line (all under `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`, read
only, never edited):

- R3: `0.3.0-cohesion-review-3.md`. Section 3, gates 250-253 and row 25 at 288; overlaps O4 (228), O5 (229), O8 (232).
- KN: `key-names-design.md`. Section 5 re-grep, 390-394; 1.6 on `docs/examples/`, 252-254.
- CS: `code-shape-design.md`. Section 7 item 8, 818-821; 3.8 on `where` fields and kept names, 600-620.
- TT: `test-tables-design.md`. Section 8 item 7, 409-411.
- LN: `language-neutral-design.md`. Section 11 re-grep, 1056-1059; section 12 last row (the coupling audit), 1078;
  1.5 on the "absolute import" wording, 192-194.
- Earlier step specs on this branch that ruled on the same hits: `docs/superpowers/specs/2-3-rules-the-rule-id-ba13344f.md`
  (S2.3) 182-189 and 200-205, `2-4-spec-internal-c61068a6.md` (S2.4) 150-160, `3-7-language-several-1d9a0cdb.md`
  (S3.7) 108-110 and 259-261, `4-7-spec-code-shape-b2e50327.md` (S4.7) 121-148 and 150-182.

## 1. Scope

In scope:

1. The version is 0.3.0 in `pyproject.toml`, `uv.lock`, and in what `xarch --version` prints.
2. The four notes' re-greps, run together once over the paths each note names, every hit classed, any real
   leftover fixed in the way the step that owns it would have fixed it, on this branch.
3. One card comment on this card (`brd comment add`), in two parts: (A) the coupling-audit rows that move to N,
   each with its evidence; (B) the re-grep hits that lie outside a note's own allowed list but are not fixed, by
   class, each with the ruling that keeps it, so the owner can accept or order a fix.

Out of scope, by the card:

- README read whole and the sentence of Q28: card 9.2 (R3 O4, 228).
- CHANGELOG 0.3.0 lead and the table of R3 section 4: card 9.3 (R3 O5, 229). This card adds no CHANGELOG line unless a
  leftover fix of section 3.4 below changes behaviour; such a line goes under `[Unreleased]`.
- The final golden-docs regeneration expected with no diff: card 9.4 (R3 O8, 232). This card still regenerates them
  once as a check (section 4) and edits none by hand.
- Refreshing `python-coupling-audit.md`: it is outside the repository (card dodge: editing files outside the
  repository). The card comment hands the owner its rows.
- Deleting, moving or rewriting anything under `docs/superpowers/`, or any file under `docs/examples/` (section 3.3).
- Tagging, pushing, or publishing a release. Nothing is pushed.

## 2. The version

Observable behaviour:

- `pyproject.toml` line 3 reads `version = "0.3.0"`. No other line of it changes.
- `uv.lock`: the `[[package]]` entry `name = "xarch"` (`source = { editable = "." }`, today 195-196) reads
  `version = "0.3.0"`. It is produced by `uv lock`, never typed by hand, and `git diff uv.lock` shows that one line and
  nothing else (no other package moves: `uv lock` is run without `--upgrade`). If more moves, the change is reverted
  and the cause reported, not committed.
- `uv run xarch --version` prints exactly `xarch 0.3.0` and a newline, exit 0.
- `uv lock --check` exits 0 (the lock agrees with `pyproject.toml`).
- No other file holds the string `0.2.0` as the current version. The existing mentions stay: the CHANGELOG's
  `[0.2.0]` entry (history) and the docstring of `tests/modules/spec/application/logic/test_parts_tree.py:3`
  ("parts of 0.2.0", a statement about an old version).

Error path: an installed environment that still holds 0.2.0 metadata fails
`tests/architecture/test_package_version.py` (installed version against `pyproject.toml`), which is the failing test of
this change (section 5, test 1).

## 3. The combined re-grep

### 3.1 The command

Run once from the worktree root, after the version change, and saved in the plan's last task report (not in a
committed file, as S4.7 150-156 did). The four notes' commands verbatim, with the paths each names:

```bash
P="xarch tests docs README.md architecture.yaml"
echo "== KN forbidden";       grep -rnw forbidden $P
echo "== KN may_not_use";     grep -rn 'may_not_use\|may-not-use' $P
echo "== KN tier:";           grep -rn 'tier:' architecture.yaml xarch/architectures tests/bootstrap/corpora
echo "== KN \"rules\"";       grep -rn '"rules"' $P
K="immutable|names|built_by|types_only|libraries"
echo "== CS";                 grep -rnE "no_callbacks|may_import|must_import|may_also_import|^\s+($K):" xarch tests architecture.yaml
echo "== TT";                 grep -rn "testing.table\b\|CaseTable\|_snake_name" $P
echo "== LN";                 grep -rn "testing\.functions\|spec_keywords\|spec_position\|absolute import\|is_public\|package_file:\|extension:" $P
```

`KN tier:` reads "in the profiles" (KN 392): the profile files are `architecture.yaml`, the bundled profiles under
`xarch/architectures/` and the recorded corpora's yaml profiles. CS names its own paths (CS 819), without `docs` and
`README.md`. The other greps run over the five paths of the card. The whole output is run twice: once as above, once
with `--exclude-dir=superpowers` added to each grep, so the hits of section 3.3 class 1 are counted on their own and
not hidden.

### 3.2 What each note allows

Copied from the notes; a hit in one of these is clean:

- KN `forbidden` (KN 390-392): the retired-keys table, the refusal tests, English prose, the 0.2.0 CHANGELOG entry,
  `docs/examples/`, names of archived files in the recorded findings.
- KN `may_not_use|may-not-use` (KN 392): nothing.
- KN `tier:` (KN 392-393): only `guards.scenario-coverage.tier`.
- KN `"rules"` (KN 393-394): only the retired rule-id entry and its test.
- CS (CS 820-821): the retired-keys table, the refusal tests, settings nested under a kind of `holds`, keys nested
  under `imports`, the filter `may-import-everything`, the `where` JSON fields, prose.
- TT (TT 409-411): the retired-keys entry, its refusal test, the 0.2.0 CHANGELOG.
- LN (LN 1057-1059): the retired-keys entries, their refusal tests, the 0.2.0 CHANGELOG, the scaffold's and layout's
  own reading of `private`.

A list is never widened to make a run pass (card dodge). A hit outside its note's list is either a leftover (3.4) or
a reported hit (3.3): never silently accepted.

### 3.3 Hits outside a note's list that are not fixed: reported

These classes were found at spec time (explore run on this branch at `79ea9d4`). Each lies outside its note's literal
list. Each is kept by a ruling already on record, or by a project rule, so editing it would break that ruling. The
spec does not count them as passing: the implementer lists each class, with its file:line hits and its ruling, in part
(B) of the card comment, and the run's verdict is written "clean apart from the classes reported in (B)".

1. **`docs/superpowers/`** (about 600 hits of `forbidden`, the `may_not_use` hits, and hits of the TT and LN patterns,
   in 92 tracked spec and plan files). These are this release's own working documents, added from 2026-11-22, after
   the notes were written (the notes' counts are at `6dda0e7`, 2026-11-18), so no note could have listed them. They
   are records of past steps, as the 0.2.0 CHANGELOG entry is; rewriting them falsifies the record, and deleting them
   is the owner's call. Not edited.
2. **`docs/examples/` and the generated `docs/xarch/architecture.md` lines that quote it**: `Violation(one.place,
   "rules", ...)` (`docs/examples/modules/rules/application/logic/imports.py:31`, `docs/xarch/architecture.md:405`)
   under KN `"rules"`; `extension: str` (`docs/examples/modules/rules/adapters/fs_source_tree.py:15`,
   `.../application/ports/source_tree.py:10`, `docs/examples/profile_values/language.py:9`,
   `docs/xarch/architecture.md:459, 491, 580`) under LN. KN 252-254 rules that these files are placement examples
   `review calibrate` sends, "not the format", and that editing them changes what calibration sends; S2.3 204-205 and
   S4.7 146-147 keep them for that reason; S3.7 259-261 updates them only where a test or the docs generator holds them
   to the code, and none does. Not edited.
3. **`"rules"` that is not the rule id** (KN `"rules"`): the module and part `rules` (e.g.
   `tests/architecture/test_self_check.py:57,64`, `test_language_seam.py`, `test_profile_new.py:65`), and the JSON
   field `rules` of `profile explain` and the vocabulary report (`xarch/cli/reports/profile_report.py`,
   `vocabulary_report.py`, `README.md:254,256` and their tests). These hits already existed at `6dda0e7` (118 hits
   then), so the note's sentence speaks of the rule id; S2.3 182-189 and 202 keep both. Also
   `tests/kernel/test_violations.py:45-47`, which builds `Violation(..., "rules", ...)` to see it refused: a refusal
   test of the retired id, classed with "its test".
4. **CS hits that S4.7 2.3 keeps** (S4.7 121-148, classes 4-8 of S4.7 150-182): the guard `no-callbacks` in snake case
   (`GuardsView.no_callbacks`, `Profile.no_callbacks`, `no_callbacks=` and the functions that read it), identifiers
   named for an unchanged rule id (`_must_import`, `_must_import_tiers`, `_must_import_line`,
   `_tier_must_import_line`, `_libraries`, `_names`, `_built_by`, `_immutable` in `expansion.py`, `docs_template.py`),
   the variable `mirrored_may_import`, and fields of the same English word that name no profile key (`names`,
   `immutable`, `built_by` fields listed in S4.7 class 8). The `where` fields and the filter are on CS's own list.
5. **TT `CaseTable` in recorded findings**: `tests/bootstrap/corpora/7cc6111.json:536`, `df537ca.json:296-297`, the
   text of findings recorded against archived code that names its own class. Recorded corpora are edited by hand
   only as a note says (card), and no note says to edit these. Not edited.
6. **LN `package_file:` in the scaffold**: `scaffold/domain/values.py:36`, `scaffold/application/logic/plan.py:8`,
   `scaffold/application/services/scaffolding.py:74`, `spec/contract/__init__.py:77`, `tests/fakes/scaffold_skeleton.py:18`.
   The one package file init and scaffold write (the first of `package_files`, `""` for none), kept by S3.7 108-110.
   The note's pattern targets the old data-file key `package_file: __init__.py` (LN 791), which no file holds. These
   are the scaffold's own reading of the language, the class LN 1059 allows for `private`; reported because the
   note's words name `private` only.
7. **LN prose and test names**: `absolute import` in `xarch/kernel/source.py:14`,
   `rules/adapters/fs_source_tree.py:16`, `rules/application/ports/source_tree.py:34,50`,
   `rules/application/logic/facts.py:226`, `tests/modules/rules/application/logic/test_tier_imports.py:243`,
   `README.md:1137`; `is_public` in test function names only (`tests/modules/rules/adapters/test_fs_source_tree_public.py:53,63`
   and the others the explore found) and `tests/profile_values/test_language.py:49`, which asserts
   `not hasattr(CheckedLanguage(), "is_public")`, a test that the old method is gone. LN 1.5 (192-194) retires the
   wording "an absolute import of the app" that assumed names resolve only through absolute imports; the remaining
   hits use "absolute" as the opposite of the fact `Import.relative` (the reader adapter's docstring is Python's own
   place) or quote a user's rule ("absolute imports only"). Rewording them to dodge a grep is churn no ruling asks for.
   `is_public` as an identifier is gone from `xarch/`.

### 3.4 Leftovers: fixed

A leftover is a hit that is in no list of 3.2 and in no class of 3.3: a retired key, rule id or identifier that a
step renamed and that still appears as code, data, profile text or a test fixture where the renaming step's spec says
it moves. At spec time none was found. The implementer reruns 3.1 on the final branch (code may have moved since
`79ea9d4`) and classes every line; any line in neither 3.2 nor 3.3 is a leftover. A leftover is fixed:

- in the shape its owning step fixed the others (KN step 4 or 5 for `"rules"`/`forbidden`, S4.7 2.2 for code-shape
  identifiers, TT step 3 for `testing.table`, LN 7/9/15a/15b for the LN patterns);
- test first when it changes behaviour (a refusal, a message, a parsed value): the test is written, seen failing, then
  the fix; a pure identifier rename is proved by the existing tests that name it, edited first (as S4.7 section 4);
- a recorded corpus only as its note says; a golden doc only by regenerating it;
- with a CHANGELOG line under `[Unreleased]` only when behaviour moves (R3 O5).

A leftover that cannot be fixed without breaking a ruling is reported in (B), not fixed.

### 3.5 Clean at spec time

Confirmed clean outside `docs/superpowers/`: `may_not_use|may-not-use` (no hit); `tier:` in the profiles (only
`guards.scenario-coverage.tier: integration` in `architecture.yaml`, `xarch/architectures/cli.yaml`, `web.yaml`, and the
key's own entries in `presets/format/keys.yaml`); `forbidden` (only the classes KN allows); `_snake_name` (no hit);
`testing.table`, `testing.functions`, `spec_keywords`, `spec_position` (only the retired entries, their refusal tests
and `README.md:192`, the refusal prose).

## 4. The card comment

Posted once on card `a5d05c8a-859e-43e9-8958-0fa4c62bec80` with `brd comment add`, after the gates pass. Plain text,
two headed parts.

**(A) Coupling-audit rows that move to N** (LN 1078). The twenty rows, each with its old class: `testing.functions` S,
`testing.mocks` S, `fakes.for` C, `guards.stand-ins` C, `parts.imports.libraries` C, `uses.never` C, `never` C,
`reserved` C, `parts.package_only` C, `guards.no-comments` C, `guards.private-imports` C, `filters.test` C,
`filters.interface` C, `filters.standard` C, `filters.public` C, `filters.record` C, `filters.special` C,
`filters.directive` C, `targets.path` C, `targets.package` C. Each row is listed as moving to N only when the
implementer has checked it on this branch; the line then names the evidence, one file:line, that what made it S or C
now comes from the language's data or a fact the reader supplies (for example the `python.yaml` key it reads, or the
fact in `key_table.py` `NEEDS` with its `supplies` entry). N means "the meaning and shape work for any language; a
new language needs only a reader that supplies the facts" (`python-coupling-audit.md:27`). A row that fails the check
is listed under its own heading "not moved", with what still ties it to Python; it is not dropped silently and not
listed as N. `testing.functions` is retired (the key no longer exists); its line says so and names its successor
`testing.declared`.

**(B) Re-grep hits reported, not fixed**: each class of 3.3 found in the final run, with its hit count, its
file:line hits (a count and the files for class 1), and the ruling that keeps it, plus any leftover of 3.4 that could
not be fixed. Last line: the verdict as 3.3 words it, and the command of 3.1.

## 5. Tests

| # | Test | Tier | Why there |
|---|---|---|---|
| 1 | `tests/architecture/test_package_version.py::test_the_installed_version_is_the_one_pyproject_gives`, existing, unchanged | architecture | It pins the packaging of the repository itself (installed metadata against `pyproject.toml`), not a module's behaviour. It is the failing test of the bump: after `pyproject.toml` says 0.3.0 and before the environment is synced, `uv run --no-sync pytest tests/architecture/test_package_version.py` fails (`'0.2.0' == '0.3.0'`); after `uv lock` and `uv sync` it passes. |
| 2 | `tests/bootstrap/test_app.py::test_version_prints_the_installed_version_and_exits_0`, existing, unchanged | bootstrap | It drives the wired CLI `app` through Typer; with test 1 it proves `xarch --version` prints 0.3.0. |
| 3 | `tests/bootstrap/test_docs_templates.py`, existing, unchanged | bootstrap | It generates every golden doc from the bundled profiles; it passing with no golden doc edited is the check of O8 for this card. |
| 4 | `tests/bootstrap/test_recorded_corpora.py`, existing, unchanged | bootstrap | No recorded finding moves; it proves no corpus needed an edit. |
| 5 | Any test a leftover fix of 3.4 needs, in the tier of the code it fixes (`uv run xarch where <file>` names it) | per fix | Written first; none is expected. |

No new test pins the string `0.3.0`: a test of the literal would fail at every release, and tests 1 and 2 already tie
the printed version to `pyproject.toml`. No test is added for the re-grep: the notes ask for a run, not a guard, and a
grep guard over the tree would be a new check no note rules (R3 row 25, 288).

Manual checks, in the last task's report:

- `uv run xarch --version` prints `xarch 0.3.0`.
- `uv lock --check` exits 0; `git diff --stat` shows `pyproject.toml` and `uv.lock` with one changed line each (plus
  any leftover fix).
- The golden docs regenerated as `tests/bootstrap/test_docs_templates.py` builds them, `git diff docs/` read: empty.
- The full output of 3.1, both runs, classed line by line into 3.2 lists, 3.3 classes, and 3.4 leftovers.

## 6. Gates

Each passing on this branch with the full suite green (card; R3 250-253): `uv run ruff check` (never `--fix`),
`uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, then
`uv run pytest -q` in the background (over two minutes), read at the end. No typecheck command exists.

## 7. Project rules that bind the plan

- No comments in xarch's code; never `ruff --fix`; tests first; examples simple, with absolute `app.` imports.
- Recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as a note says.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`.
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated and their diff read, never edited by hand (R3 O8, 232).
- README and CHANGELOG lines, if any, under `[Unreleased]` (R3 O4, O5).
- `.claude/` stays out of commits; nothing is pushed; no file outside the repository is edited.

## 8. Dodges

- Widening a re-grep's allowed list to make it pass (card). Section 3.3 reports; it does not accept.
- Rewording prose, renaming test functions, or editing `docs/examples/` or `docs/superpowers/` only so a grep comes
  back empty (breaks KN 252-254 and S4.7 2.3, or the record of past steps).
- Editing `uv.lock` by hand, or `uv lock --upgrade`.
- Listing a coupling-audit row as N without checking it on this branch.
- Editing `python-coupling-audit.md` or any note outside the repository.

---

# Implementation

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `pyproject.toml` | Modify line 3 | The project's version: `0.2.0` → `0.3.0`. |
| `uv.lock` | Regenerated by `uv lock` | The `xarch` package entry's `version` line (today line 196). |
| `/tmp/xarch-9-1/regrep.sh` | Create (scratch, never committed) | Section 3.1's command, verbatim, with an optional `--exclude-dir=superpowers`. |
| `/tmp/xarch-9-1/classify.py` | Create (scratch) | Classes every re-grep line into a 3.2 list item or a 3.3 class; prints `UNCLASSED` for the rest. |
| `/tmp/xarch-9-1/hand.tsv` | Create (scratch) | Hand rulings for lines no pattern of `classify.py` classes, each with a label of `classify.py`'s `LABELS`. |
| `/tmp/xarch-9-1/evidence.py` | Create (scratch) | One file:line per coupling-audit row (section 4 A). |
| `/tmp/xarch-9-1/comment.txt` | Create (scratch) | The card comment, parts (A) and (B). |

Nothing under `xarch/` or `tests/` is expected to change: at spec time no leftover exists (spec 3.4, 3.5). If Task 2
finds one, its fix is the only code change, in its own commit.

The scratch scripts were run by the planner on `79ea9d4`: `classify.py` with the `hand.tsv` below classed all 496 lines
of the excluded run (and the 1144 more of `docs/superpowers/` in the full run) with no `UNCLASSED` line, and
`evidence.py` found a line for every row. Line numbers in `hand.tsv` and in the expected outputs below are those of
`79ea9d4`; if the final branch moved a line, the run says so (an `UNCLASSED` line or a `NOT FOUND` row) and the step
says what to do.

---

### Task 1: The version is 0.3.0

**Files:**
- Modify: `pyproject.toml:3`
- Regenerate: `uv.lock` (the `name = "xarch"` entry's `version`, today line 196)
- Test (existing, unchanged): `tests/architecture/test_package_version.py`, `tests/bootstrap/test_app.py`

**Interfaces:**
- Consumes: nothing.
- Produces: an environment whose installed `xarch` metadata says `0.3.0`; Tasks 2-4 run on it.

- [ ] **Step 1: Read the two files and the test**

Run: `sed -n 1,4p pyproject.toml; grep -n -A2 '^name = "xarch"' uv.lock; cat tests/architecture/test_package_version.py`
Expected: `version = "0.2.0"` on line 3 of `pyproject.toml`; in `uv.lock`, `name = "xarch"` followed by
`version = "0.2.0"` and `source = { editable = "." }`; the test compares `metadata.version("xarch")` with
`pyproject.toml`'s `project.version`.

- [ ] **Step 2: Install the environment at 0.2.0, so the failure can be seen**

A fresh worktree's `.venv` may hold no packages at all (no `pytest`: `uv run --no-sync pytest` then fails with a
`mise` "pytest is not provided" error, which is not the failure this task wants). Sync it before changing anything:

Run: `uv sync 2>&1 | tail -2; uv run --no-sync python -c "from importlib import metadata; print(metadata.version('xarch'))"`
Expected: `uv sync` ends with `xarch==0.2.0` installed (or "Audited", already installed), and the version printed is
`0.2.0`.

- [ ] **Step 2b: Change the version in `pyproject.toml` (the change that makes the test fail)**

Edit `pyproject.toml` line 3 only:

```toml
version = "0.3.0"
```

Run: `git diff --stat pyproject.toml && git diff -U0 pyproject.toml | grep '^[-+]v'`
Expected: `1 file changed, 1 insertion(+), 1 deletion(-)` and exactly the two lines `-version = "0.2.0"` and
`+version = "0.3.0"`.

- [ ] **Step 3: Run the packaging test without syncing, to see it fail**

Run: `timeout 300 uv run --no-sync pytest -q tests/architecture/test_package_version.py 2>&1 | tail -5`
Expected: FAIL, `1 failed`, with `AssertionError: assert '0.2.0' == '0.3.0'`. (`--no-sync` keeps the installed
metadata at 0.2.0; a plain `uv run` would reinstall first.) If it passes, something synced the environment after
Step 2b: set line 3 back to `version = "0.2.0"`, repeat Step 2, set it to `0.3.0` again, and repeat this step. Do not
go on until the failure has been seen once.

- [ ] **Step 4: Regenerate the lock with `uv lock` and read its diff**

Run: `uv lock 2>&1 | tail -3 && git diff --stat uv.lock && git diff -U0 uv.lock`
Expected: `uv lock` reports `Updated xarch v0.2.0 -> v0.3.0` (or resolves with no other package named);
`1 file changed, 1 insertion(+), 1 deletion(-)`; the hunk is exactly:

```diff
-version = "0.2.0"
+version = "0.3.0"
```

inside the `name = "xarch"` entry. If any other line moved, run `git checkout -- uv.lock`, do not commit, and stop to
report the `git diff uv.lock` output (spec 2: "If more moves, the change is reverted and the cause reported"). Never
pass `--upgrade`, never edit `uv.lock` by hand.

Then: `uv lock --check; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 5: Sync the environment and run the version tests to see them pass**

Run: `uv sync 2>&1 | tail -3 && timeout 300 uv run --no-sync pytest -q tests/architecture/test_package_version.py tests/bootstrap/test_app.py -k "version" 2>&1 | tail -3`
Expected: `uv sync` names `xarch==0.3.0` (reinstalled); the tests PASS (`4 passed, 38 deselected` at `79ea9d4`: the
packaging test and the three `--version` tests of `test_app.py`; the count may differ if tests moved, but none fails).

- [ ] **Step 6: Check what a person sees, synced and not**

Run: `uv run xarch --version | od -c | head -2; uv run xarch --version; echo "exit=$?"; uv run --no-sync xarch --version`
Expected: `xarch 0.3.0` followed by `\n` in the `od` output (no trailing space, one newline), `exit=0`, and the
`--no-sync` run also prints `xarch 0.3.0` (Review Focus 1).

- [ ] **Step 7: Check no other file holds `0.2.0` as the current version**

Run: `git grep -n '0\.2\.0' -- ':!docs/superpowers' ':!uv.lock'`
Expected: only the CHANGELOG's history lines (the `## [0.2.0]` heading, its compare link if any, and the 0.2.0 entry's
own text) and `tests/modules/spec/application/logic/test_parts_tree.py:3` ("parts of 0.2.0"). Any other hit that
states the current version (a `__version__`, a docs line saying "xarch 0.2.0 is") is changed to `0.3.0` in this
commit; read each hit before deciding, and list them in the task report. `git grep -n '0\.2\.0' uv.lock` must give
no line of the `xarch` entry (other packages' versions that happen to contain `0.2.0` are not ours).

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "xarch's version is 0.3.0: pyproject.toml says it, uv lock regenerated its one line of the lock, and xarch --version prints xarch 0.3.0

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

Run: `git show --stat HEAD | tail -4`
Expected: `pyproject.toml | 2 +-`, `uv.lock | 2 +-`, `2 files changed, 2 insertions(+), 2 deletions(-)`.

---

### Task 2: The combined re-grep, every hit classed

**Files:**
- Create (scratch, never committed): `/tmp/xarch-9-1/regrep.sh`, `/tmp/xarch-9-1/classify.py`,
  `/tmp/xarch-9-1/hand.tsv`, outputs `/tmp/xarch-9-1/{all,ex}.txt`, `/tmp/xarch-9-1/{all,ex}.tsv`
- Modify: none expected. A leftover found in Step 4 is fixed in Step 5 in the files it names.

**Interfaces:**
- Consumes: the branch after Task 1.
- Produces: `/tmp/xarch-9-1/all.tsv` and `/tmp/xarch-9-1/ex.tsv`, one line per hit:
  `<section>\t<path>:<line>\t<label>\t<text>`, where `<label>` is a key of `LABELS` in `classify.py`; and the counts per
  label (stderr of `classify.py`, saved to `/tmp/xarch-9-1/{all,ex}.counts`). Task 4 builds part (B) from these.

- [ ] **Step 1: Write the re-grep script (section 3.1 verbatim)**

```bash
mkdir -p /tmp/xarch-9-1
cat > /tmp/xarch-9-1/regrep.sh <<'EOF'
#!/usr/bin/env bash
# usage: regrep.sh [--exclude-dir=superpowers]
X="$1"
P="xarch tests docs README.md architecture.yaml"
echo "== KN forbidden";       grep -rnw $X forbidden $P
echo "== KN may_not_use";     grep -rn $X 'may_not_use\|may-not-use' $P
echo "== KN tier:";           grep -rn $X 'tier:' architecture.yaml xarch/architectures tests/bootstrap/corpora
echo "== KN \"rules\"";       grep -rn $X '"rules"' $P
K="immutable|names|built_by|types_only|libraries"
echo "== CS";                 grep -rnE $X "no_callbacks|may_import|must_import|may_also_import|^\s+($K):" xarch tests architecture.yaml
echo "== TT";                 grep -rn $X "testing.table\b\|CaseTable\|_snake_name" $P
echo "== LN";                 grep -rn $X "testing\.functions\|spec_keywords\|spec_position\|absolute import\|is_public\|package_file:\|extension:" $P
EOF
chmod +x /tmp/xarch-9-1/regrep.sh
```

The patterns and paths are section 3.1's, letter for letter; the only addition is `$X`, empty for the full run and
`--exclude-dir=superpowers` for the second (spec 3.1, last sentence). Check it against the spec:
`diff <(sed -n '/^P="xarch/,/^echo "== LN"/p' docs/superpowers/specs/9-1-release-version-0-3-a5d05c8a.md | sed 's/  */ /g') <(sed -n '/^P="xarch/,/^echo "== LN"/p' /tmp/xarch-9-1/regrep.sh | sed 's/ \$X//; s/  */ /g')`
Expected: no output (the script is the spec's command once `$X` is taken out).

- [ ] **Step 2: Run it twice, from the worktree root**

Run:
```bash
/tmp/xarch-9-1/regrep.sh > /tmp/xarch-9-1/all.txt 2> /tmp/xarch-9-1/all.err
/tmp/xarch-9-1/regrep.sh --exclude-dir=superpowers > /tmp/xarch-9-1/ex.txt 2> /tmp/xarch-9-1/ex.err
wc -l /tmp/xarch-9-1/all.txt /tmp/xarch-9-1/ex.txt
grep -v '__pycache__/.*\.pyc: binary file matches$' /tmp/xarch-9-1/all.err /tmp/xarch-9-1/ex.err
grep -v '^==' /tmp/xarch-9-1/all.txt | grep -c '^docs/superpowers/'
grep -c 'may_not_use\|may-not-use' /tmp/xarch-9-1/ex.txt
```
Expected at `79ea9d4` plus Task 1: `1640` and `496` lines (each including the 7 `==` headers); `1144` lines under
`docs/superpowers/` (more if this card's own spec and plan add hits: they quote the patterns; the class-1 count is
whatever this run gives); `0` hits of `may_not_use|may-not-use` outside `docs/superpowers/` (spec 3.5). The numbers
may move if code moved; the runs are what is reported, not these numbers. The last command prints nothing: once tests have run, grep
reports the compiled `__pycache__/*.pyc` copies of matching modules as `binary file matches` on stderr; those are not
hits (no tracked file), so they are kept out of the classed output and not reported. Any other stderr line (a missing
path, a bad pattern) stops the task to report it.

- [ ] **Step 3: Write the classifier and the hand rulings, and class both runs**

```bash
cat > /tmp/xarch-9-1/classify.py <<'EOF'
"""Class every line of the 9.1 re-grep: a 3.2 list item, a 3.3 class, or UNCLASSED (a leftover or a hand ruling).

usage: python3 -I classify.py <regrep output> <hand rulings tsv> > classed.tsv
A hand ruling is one line `<section>\t<path>:<line>\t<label>`; the label must be one of LABELS.
Prints `<section>\t<path>:<line>\t<label>\t<text>` per hit, then the counts per label on stderr.
"""
import re
import sys
from collections import Counter
from pathlib import Path

LABELS = {
    "3.2 retired-keys table": "the retired-keys table (xarch/modules/spec/domain/profile_keys.py)",
    "3.2 refusal test": "a test that writes a retired key or id to see it refused, or a test of the retired entry",
    "3.2 prose": "English prose: docstring, doc text, message, test name or pytest id",
    "3.2 0.2.0 CHANGELOG": "the CHANGELOG's [0.2.0] entry",
    "3.2 scenario-coverage tier": "guards.scenario-coverage.tier, its key entry or form text",
    "3.2 holds setting": "a setting nested under a kind of holds",
    "3.2 imports key": "a key nested under imports, or the format catalogue keys.yaml",
    "3.2 may-import-everything": "the filter may-import-everything and its function",
    "3.2 where field": "a where JSON field or answer value (S4.7 2.3)",
    "3.2 scaffold/layout private": "the scaffold's and layout's own reading of private",
    "3.3.1 superpowers": "docs/superpowers/ working documents",
    "3.3.2 docs/examples": "docs/examples/ and the generated docs that quote it",
    "3.3.3 rules not the rule id": "the module or part rules, or the JSON field rules",
    "3.3.4 S4.7 kept name": "no_callbacks, an identifier named for a rule id, mirrored_may_import, a same-word field",
    "3.3.5 CaseTable in recorded findings": "a recorded corpus finding naming CaseTable",
    "3.3.6 package_file in the scaffold": "the scaffold's one package file",
    "3.3.7 LN prose and test names": "absolute import prose, is_public in test names, the is_public absence test",
}

CS_SECTION = "CS"
YAML_KEY = re.compile(r"^(\s*)([A-Za-z_][\w.-]*|\"[^\"]+\"):")
HOLDS_WORDS = ("names", "immutable", "built_by")
IMPORTS_WORDS = ("libraries", "types_only")

RULES = [
    (None, r"^docs/superpowers/", None, "3.3.1 superpowers"),
    (None, r"^docs/examples/", None, "3.3.2 docs/examples"),
    (None, r"^xarch/modules/spec/domain/profile_keys\.py$", r"Retired\(", "3.2 retired-keys table"),
    (None, r"^CHANGELOG\.md$", None, "3.2 0.2.0 CHANGELOG"),
    (None, r"test_retired_keys\.py$|test_profile_keys\.py$", None, "3.2 refusal test"),
    (None, r"^tests/", r"unknown key '|unknown rule id '|moved in 0\.3\.0|renamed in 0\.3\.0", "3.2 refusal test"),
    ("KN forbidden", r"\.md$", r"is forbidden|forbidden import", "3.2 prose"),
    ("KN forbidden", r"^tests/", r'"""|forbidden" not in|forbidden=|\["forbidden"\]|\{"forbidden"|"forbidden":',
     "3.2 refusal test"),
    ("KN tier:", r"presets/format/keys\.yaml$|\.yaml$", r"tier: integration|tier: <tier>|scenario-coverage\.tier",
     "3.2 scenario-coverage tier"),
    ("KN \"rules\"", r"^docs/xarch/architecture\.md$", r'Violation\(one\.place, "rules"', "3.3.2 docs/examples"),
    ("KN \"rules\"", r"^docs/xarch/testing\.md$", r'"rules": frozenset', "3.3.2 docs/examples"),
    ("KN \"rules\"", r"^tests/kernel/test_violations\.py$", None, "3.2 refusal test"),
    ("KN \"rules\"", r"profile_report\.py$|vocabulary_report\.py$|^README\.md$", None, "3.3.3 rules not the rule id"),
    ("KN \"rules\"", r"^tests/", r'"modules" / "rules"|/ "rules" /|\["rules"\]|"rules":|"rules" in|"spec", "rules"'
     r'|\("rules",\)|"core", "rules"|"role": "rules"|"checks", "rules"|frm\("rules"|"rules", "test_x',
     "3.3.3 rules not the rule id"),
    ("KN \"rules\"", r"^tests/", r'hints=\{"rules"|checks=\{"rules"|read\(\{"rules"|\(\["rules"\]|pytest\.param\("rules"',
     "3.2 refusal test"),
    ("TT", r"^tests/bootstrap/corpora/.*\.json$", r"CaseTable", "3.3.5 CaseTable in recorded findings"),
    ("TT", r"^tests/bootstrap/test_profile_explain\.py$", r'"testing\.table"', "3.2 refusal test"),
    ("LN", r"^README\.md$", r"spec_keywords|spec_position", "3.2 prose"),
    ("LN", r"^tests/bootstrap/test_profile_explain\.py$", r'"testing\.functions"', "3.2 refusal test"),
    ("LN", r"^tests/modules/spec/application/logic/test_testing\.py$", r"spec_keywords|spec_position",
     "3.2 refusal test"),
    ("LN", r"scaffold/|spec/contract/__init__\.py$|tests/fakes/scaffold_skeleton\.py$", r"package_file:",
     "3.3.6 package_file in the scaffold"),
    ("LN", r"", r"absolute import", "3.3.7 LN prose and test names"),
    ("LN", r"^tests/", r"def test_\w*public|hasattr\(CheckedLanguage\(\), \"is_public\"\)", "3.3.7 LN prose and test names"),
    ("LN", r"^docs/xarch/architecture\.md$|^docs/examples/", r"extension: str", "3.3.2 docs/examples"),
    (CS_SECTION, r"", r"may_import_text|^\s*libraries: tuple|^\s*types_only: tuple|^\s*may_import: tuple"
     r'|"may_import":|\["may_import"\]|where\.may_import|\.may_import\b', "3.2 where field"),
    (CS_SECTION, r"", r"may-import-everything|_may_import_everything", "3.2 may-import-everything"),
    (CS_SECTION, r"", r"no_callbacks|mirrored_may_import|\b_?must_import(_tiers|_line)?\b|_tier_must_import_line",
     "3.3.4 S4.7 kept name"),
    (CS_SECTION, r"^xarch/architectures/presets/format/keys\.yaml$", None, "3.2 imports key"),
    (CS_SECTION, r"^xarch/modules/spec/domain/published\.py$", r"^\s*(names|immutable|built_by): ", "3.2 holds setting"),
    (CS_SECTION, r"\.py$", r"^\s*(names|immutable|built_by): (tuple|str|bool|list|set|dict|frozenset|Iterable)\b",
     "3.3.4 S4.7 kept name"),
    (CS_SECTION, r"", r"def test_|id=\"|\"\"\"|^\s*#", "3.2 prose"),
]


def ancestors(path: str, number: int) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    found = YAML_KEY.match(lines[number - 1])
    depth = len(found.group(1)) if found else len(lines[number - 1]) - len(lines[number - 1].lstrip())
    keys = []
    for line in reversed(lines[:number - 1]):
        key = YAML_KEY.match(line)
        if key and len(key.group(1)) < depth:
            keys.append(key.group(2))
            depth = len(key.group(1))
    return keys


def yaml_label(path: str, number: int, text: str) -> str | None:
    word = YAML_KEY.match(text)
    if not path.endswith(".yaml") or not word:
        return None
    above = ancestors(path, number)
    if word.group(2) in HOLDS_WORDS and "holds" in above:
        return "3.2 holds setting"
    if word.group(2) in IMPORTS_WORDS and "imports" in above:
        return "3.2 imports key"
    return None


def label_of(section: str, path: str, number: int, text: str, hand: dict[tuple[str, str], str]) -> str:
    if (section, f"{path}:{number}") in hand:
        return hand[(section, f"{path}:{number}")]
    for scope, where, what, label in RULES:
        if scope not in (None, section) or not re.search(where, path):
            continue
        if what is None or re.search(what, text):
            return label
    if section == CS_SECTION:
        return yaml_label(path, number, text) or "UNCLASSED"
    return "UNCLASSED"


def main(output: str, rulings: str) -> None:
    hand = {}
    for row in Path(rulings).read_text(encoding="utf-8").splitlines():
        if row.strip():
            section, place, label = row.split("\t")
            if label not in LABELS:
                raise SystemExit(f"unknown label {label!r} in {rulings}")
            hand[(section, place)] = label
    counts: Counter[str] = Counter()
    section = ""
    for line in Path(output).read_text(encoding="utf-8").splitlines():
        if line.startswith("== "):
            section = line[3:]
            continue
        path, number, text = line.split(":", 2)
        label = label_of(section, path, int(number), text, hand)
        counts[label] += 1
        print(f"{section}\t{path}:{number}\t{label}\t{text.strip()[:160]}")
    for label, count in sorted(counts.items()):
        print(f"{count:6}  {label}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
EOF
cat > /tmp/xarch-9-1/hand.tsv <<'EOF'
KN forbidden	tests/bootstrap/test_architecture_files.py:234	3.2 refusal test
KN forbidden	tests/bootstrap/test_architecture_files.py:237	3.2 refusal test
KN "rules"	tests/bootstrap/test_profile_explain.py:91	3.3.3 rules not the rule id
CS	xarch/modules/spec/application/logic/imports_written.py:5	3.2 imports key
CS	xarch/modules/spec/domain/values.py:327	3.3.4 S4.7 kept name
CS	tests/bootstrap/test_needs_agree.py:22	3.2 imports key
CS	tests/bootstrap/test_needs_agree.py:41	3.2 imports key
CS	tests/bootstrap/test_profile_file.py:31	3.2 imports key
CS	tests/bootstrap/test_profile_explain.py:67	3.2 refusal test
CS	tests/bootstrap/test_profile_explain.py:69	3.2 refusal test
CS	tests/bootstrap/test_profile_explain.py:76	3.2 refusal test
CS	tests/modules/rules/domain/test_rule.py:146	3.2 refusal test
CS	tests/modules/rules/domain/test_rule.py:147	3.2 refusal test
CS	tests/modules/spec/application/logic/test_imports_written.py:150	3.2 refusal test
CS	tests/modules/spec/application/logic/test_looseness.py:254	3.2 refusal test
CS	tests/modules/spec/application/test_explain.py:124	3.2 refusal test
CS	tests/modules/spec/application/test_explain.py:125	3.2 refusal test
EOF
python3 -I /tmp/xarch-9-1/classify.py /tmp/xarch-9-1/ex.txt /tmp/xarch-9-1/hand.tsv > /tmp/xarch-9-1/ex.tsv 2> /tmp/xarch-9-1/ex.counts
python3 -I /tmp/xarch-9-1/classify.py /tmp/xarch-9-1/all.txt /tmp/xarch-9-1/hand.tsv > /tmp/xarch-9-1/all.tsv 2> /tmp/xarch-9-1/all.counts
cat /tmp/xarch-9-1/ex.counts; grep -cP '\tUNCLASSED\t' /tmp/xarch-9-1/all.tsv
```

`hand.tsv` is tab-separated: write it with real tabs (the heredoc above keeps the tabs as pasted; check with
`grep -cP '\t.*\t' /tmp/xarch-9-1/hand.tsv`, expected `17`).

Expected at `79ea9d4`: the counts

```
    44  3.2 holds setting
    36  3.2 imports key
     5  3.2 may-import-everything
    56  3.2 prose
   123  3.2 refusal test
    12  3.2 retired-keys table
     9  3.2 scenario-coverage tier
    37  3.2 where field
    10  3.3.2 docs/examples
    46  3.3.3 rules not the rule id
    86  3.3.4 S4.7 kept name
     3  3.3.5 CaseTable in recorded findings
     5  3.3.6 package_file in the scaffold
    17  3.3.7 LN prose and test names
```

and `0` `UNCLASSED` lines in `all.tsv` (whose counts add `3.3.1 superpowers` with the `docs/superpowers/` lines).
Note: no hit falls in `3.2 0.2.0 CHANGELOG` or `3.2 scaffold/layout private` because none of the greps' paths holds
`CHANGELOG.md` and no pattern greps `private`; the labels stay so a later run can use them.

- [ ] **Step 4: Read every line of `ex.tsv` and confirm its label; rule each `UNCLASSED` line**

The patterns of `classify.py` are a first sort, not a ruling: a broad one (`3.2 prose` on `def test_`, `3.2 refusal
test` on `moved in 0.3.0`) could cover a real leftover. Read `ex.tsv` whole (`less /tmp/xarch-9-1/ex.tsv`), and for
each line open the hit when its text alone does not show its class (`sed -n '<line-3>,<line+3>p' <path>`). A line is
correctly labelled only if it fits the label's text in `LABELS` and the note list or spec 3.3 class that label names.

For a line that is `UNCLASSED` or wrongly labelled:
- If it fits a 3.2 list item or a 3.3 class, add one `hand.tsv` row `<section>\t<path>:<line>\t<label>` (the
  section as `ex.txt`'s header writes it, e.g. `KN "rules"`, `CS`), and re-run Step 3. Never add a label to `LABELS`
  and never widen a pattern to cover a new kind of hit (spec 3.2: a list is never widened).
- Otherwise it is a leftover (spec 3.4): write it to `/tmp/xarch-9-1/leftovers.txt` as `<path>:<line> <text>` with
  the step that owns it (KN step 4 or 5 for `"rules"`/`forbidden`, S4.7 2.2 for code-shape identifiers, TT step 3 for
  `testing.table`, LN 7/9/15a/15b for the LN patterns) and go to Step 5.

The `docs/superpowers/` lines of `all.tsv` are all `3.3.1 superpowers` by their path; read their count only (spec 4 B
asks a count and the files for class 1): `grep -P '\t3\.3\.1 superpowers\t' /tmp/xarch-9-1/all.tsv | cut -f2 | cut -d: -f1 | sort -u > /tmp/xarch-9-1/superpowers-files.txt; wc -l < /tmp/xarch-9-1/superpowers-files.txt`.

Expected: `0` `UNCLASSED` lines after the rulings, and `/tmp/xarch-9-1/leftovers.txt` absent or empty (none at spec
time). Record in the task report: the final `ex.counts`, every `hand.tsv` row added beyond the 17 given, and the
leftovers (or "none").

- [ ] **Step 5: Fix each leftover, test first (only if Step 4 found one)**

Skip this step when `/tmp/xarch-9-1/leftovers.txt` is empty or absent, and say so in the report.

For each leftover, in its own commit:
1. Run `uv run xarch where <path>` to learn the tier its test belongs in (spec 5, row 5).
2. If the fix changes behaviour (a refusal, a message, a parsed value): write the test in that tier that expects the
   renamed key or id (copy the shape of the owning step's test for the others, e.g. a `pytest.param` row in
   `tests/modules/spec/application/logic/test_retired_keys.py` for a retired key, asserting the exact refusal text the
   others there assert), run `timeout 300 uv run pytest -q <that test file> -k <its id>` and see it FAIL on the
   leftover; then change the code; run it again and see it PASS. Add one CHANGELOG line under `[Unreleased]` saying
   what a user now sees (R3 O5).
3. If it is a pure identifier rename: first edit the existing tests that name the identifier to the new name, run them
   and see them FAIL (`AttributeError`/`TypeError`/`ImportError`), then rename in the code, and see them PASS (as S4.7
   section 4).
4. A leftover in a recorded corpus is edited only as its note says; one in a golden doc only by regenerating it.
5. A leftover that cannot be fixed without breaking a ruling is not fixed: move its line to
   `/tmp/xarch-9-1/unfixed.txt` with the ruling it would break, for part (B).
6. `uv run ruff check` (never `--fix`), then commit:

```bash
git add <the files of this fix>
git commit -m "<what was renamed to what, in the shape step <owner> gave the others>, the re-grep's last <pattern> hit

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

Then re-run Steps 2-4 so `all.tsv`/`ex.tsv` describe the final branch.

- [ ] **Step 6: No commit for the classing itself**

The re-grep's output and its classing are reported, not committed (spec 3.1). Run `git status --short` and check that
nothing under the worktree changed in this task apart from a Step 5 fix (and the untracked spec and plan under
`docs/superpowers/`, which the workflow commits).

---

### Task 3: The twenty coupling-audit rows, checked on this branch

**Files:**
- Create (scratch, never committed): `/tmp/xarch-9-1/evidence.py`, `/tmp/xarch-9-1/rows.tsv`,
  `/tmp/xarch-9-1/rows-checked.txt`
- Modify: none. `python-coupling-audit.md` is not edited (spec 1, 8).

**Interfaces:**
- Consumes: the branch after Task 2.
- Produces: `/tmp/xarch-9-1/rows-checked.txt`, one line per row in the order of spec 4 (A):
  `<row> <old class> -> N: <file>:<line> <why>` or `<row> <old class> not moved: <what still ties it to Python>`.
  Task 4 copies it into part (A).

- [ ] **Step 1: Write the evidence script**

```bash
cat > /tmp/xarch-9-1/evidence.py <<'EOF'
"""The one file:line per coupling-audit row that shows its S or C now comes from the language's data or a fact.

usage (from the worktree root): python3 -I evidence.py > rows.tsv
Prints `<row>\t<old class>\t<file>:<line>\t<the line>`; exits 1 naming every row whose line is not found.
"""
import re
import sys
from pathlib import Path

LANG = "xarch/architectures/presets/language/python.yaml"
TABLE = "xarch/modules/spec/domain/key_table.py"
FILTERS = "xarch/modules/rules/application/logic/filters.py"
TARGETS = "xarch/modules/rules/application/logic/targets.py"
RETIRED = "xarch/modules/spec/domain/profile_keys.py"

ROWS = [
    ("testing.functions", "S", RETIRED, r'Retired\(TESTING, "functions", .*declared'),
    ("testing.mocks", "S", TABLE, r'"testing\.mocks\.specs\[\]\.type_argument": \("call\.type_arguments",\)'),
    ("fakes.for", "C", TABLE, r'^\s*"fakes": \("class", "class\.interface"\)'),
    ("guards.stand-ins", "C", TABLE, r'^\s*"guards\.stand-ins": \(.*"class\.interface"'),
    ("parts.imports.libraries", "C", LANG, r"^package: "),
    ("uses.never", "C", TABLE, r'^\s*"parts\.<part>\.uses\.never": _NEVER_USE'),
    ("never", "C", LANG, r"^member: "),
    ("reserved", "C", "xarch/modules/spec/application/logic/language_file.py", r"The keys of the map a data file.s .standard. may be"),
    ("parts.package_only", "C", TABLE, r'^\s*"parts\.<part>\.package_only": \(\*_IMPORTS, "file\.package"\)'),
    ("guards.no-comments", "C", TABLE, r'^\s*"guards\.no-comments": \("comment", "comment\.doc"\)'),
    ("guards.private-imports", "C", TABLE, r'^\s*"guards\.private-imports": \(\*_IMPORTS, "public"\)'),
    ("filters.test", "C", TABLE, r"Key\(TESTING, \"beside\""),
    ("filters.interface", "C", LANG, r"^  class\.interface: exact"),
    ("filters.standard", "C", LANG, r"^standard: "),
    ("filters.public", "C", LANG, r"^  public: exact"),
    ("filters.record", "C", LANG, r"^  class\.record: exact"),
    ("filters.special", "C", LANG, r"^special: "),
    ("filters.directive", "C", LANG, r"^directives: "),
    ("targets.path", "C", LANG, r"^member: "),
    ("targets.package", "C", LANG, r"^package: "),
]


def first(path: str, pattern: str) -> tuple[int, str] | None:
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if re.search(pattern, line):
            return number, line.strip()
    return None


def main() -> int:
    missing = []
    for row, old, path, pattern in ROWS:
        found = first(path, pattern)
        if found is None:
            missing.append(row)
            continue
        print(f"{row}\t{old}\t{path}:{found[0]}\t{found[1]}")
    for row in missing:
        print(f"NOT FOUND: {row}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
EOF
python3 -I /tmp/xarch-9-1/evidence.py > /tmp/xarch-9-1/rows.tsv; echo "exit=$?"; cat /tmp/xarch-9-1/rows.tsv
```

Expected at `79ea9d4`: `exit=0` and twenty lines, in spec 4 (A)'s order:

```
testing.functions	S	xarch/modules/spec/domain/profile_keys.py:228	Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),
testing.mocks	S	xarch/modules/spec/domain/key_table.py:275	"testing.mocks.specs[].type_argument": ("call.type_arguments",),
fakes.for	C	xarch/modules/spec/domain/key_table.py:239	"fakes": ("class", "class.interface"),
guards.stand-ins	C	xarch/modules/spec/domain/key_table.py:279	"guards.stand-ins": ("class", "class.methods", "class.attributes", "class.interface", "call", "parameter_call",
parts.imports.libraries	C	xarch/architectures/presets/language/python.yaml:48	package: '(?!\d)\w+'
uses.never	C	xarch/modules/spec/domain/key_table.py:258	"parts.<part>.uses.never": _NEVER_USE,
never	C	xarch/architectures/presets/language/python.yaml:49	member: "."
reserved	C	xarch/modules/spec/application/logic/language_file.py:129	"""The keys of the map a data file's `standard` may be: the lists of StandardLists, in its order."""
parts.package_only	C	xarch/modules/spec/domain/key_table.py:259	"parts.<part>.package_only": (*_IMPORTS, "file.package"),
guards.no-comments	C	xarch/modules/spec/domain/key_table.py:278	"guards.no-comments": ("comment", "comment.doc"),
guards.private-imports	C	xarch/modules/spec/domain/key_table.py:295	"guards.private-imports": (*_IMPORTS, "public"),
filters.test	C	xarch/modules/spec/domain/key_table.py:140	Key(TESTING, "beside", rules=("tiers", "test-tree")),
filters.interface	C	xarch/architectures/presets/language/python.yaml:92	class.interface: exact
filters.standard	C	xarch/architectures/presets/language/python.yaml:46	standard: interpreter
filters.public	C	xarch/architectures/presets/language/python.yaml:78	public: exact
filters.record	C	xarch/architectures/presets/language/python.yaml:93	class.record: exact
filters.special	C	xarch/architectures/presets/language/python.yaml:51	special: '(?=__)\w*(?<=__)'
filters.directive	C	xarch/architectures/presets/language/python.yaml:55	directives: ["type: ignore", noqa, "pragma:"]
targets.path	C	xarch/architectures/presets/language/python.yaml:49	member: "."
targets.package	C	xarch/architectures/presets/language/python.yaml:48	package: '(?!\d)\w+'
```

A `NOT FOUND: <row>` on stderr (exit 1) means the line moved or went: find where the row's coupling is now decided
(`git grep -n` the key or fact) and correct that row's `(path, pattern)` in `ROWS`; if the coupling now lives nowhere
in data or facts, the row goes under "not moved" in Step 3.

- [ ] **Step 2: Check each row by reading the code behind its line**

The script proves only that the line exists. A row moves to N only when the check below holds on this branch (spec 4 A:
"Each row is listed as moving to N only when the implementer has checked it on this branch"). For each row, read the
cited line and run the check; write the outcome to `/tmp/xarch-9-1/rows-checked.txt`.

| Row | What made it S or C (audit) | Check on this branch (read and run) |
|---|---|---|
| `testing.functions` S | one function-name pattern | `uv run xarch profile explain testing.functions` refuses with `testing.declared` to write; `Key(TESTING, "declared"` exists in `key_table.py`; `test.function`/`test.call` in `NEEDS` (`key_table.py:272-273`). Line: "retired; successor `testing.declared`". |
| `testing.mocks` S | spec by keyword or position only | `testing.mocks.specs` entries `keyword`/`position`/`type_argument` (`uv run xarch profile explain testing.mocks.specs`); `type_argument` needs `call.type_arguments` (`key_table.py:275`), a fact the reader supplies. |
| `fakes.for` C | ports are classes with an interface base | `fakes` needs `class.interface` (`key_table.py:239`); `python.yaml:42` `interface` takes `{base:}` or `{keyword:}` marks. |
| `guards.stand-ins` C | ports by base; one `nothing` token | `key_table.py:279` needs `class.interface`; `python.yaml:53` `nothing: [None]` is a list. |
| `parts.imports.libraries` C | one `name` regex for packages | `python.yaml:48` `package:` is its own pattern; `git grep -n 'language.*package\b\|\.package\b' xarch/modules/spec/application/logic/profile_checks.py` shows libraries checked against it. |
| `uses.never` C | inherits `never` | `key_table.py:258` reads `_NEVER_USE` (facts only); with `never` below. |
| `never` C | dotted names "as an absolute import binds them" | `python.yaml:48-49` `package` and `member` give the entry syntax; `import.resolved` in `_NEVER_USE` (`key_table.py:236`) resolves relative imports too. |
| `reserved` C | standard library only from the running interpreter | `language_file.py:129` `StandardLists`: `standard` may be a map of lists in the data file, `interpreter` one choice (`python.yaml:46`). |
| `parts.package_only` C | needs a package file | `key_table.py:259` needs `file.package`; `python.yaml:41` `package_files` is optional (header comment line 4). |
| `guards.no-comments` C | one line-comment marker | `key_table.py:278` needs `comment.doc`; `python.yaml:54` `comments` is a list of `{line}`/`{block}`/`{doc}` forms. |
| `guards.private-imports` C | privacy by a name prefix | `key_table.py:295` needs the fact `public`; `python.yaml:78` `public: exact` (the reader decides). |
| `filters.test` C | "a file below the tests folder" | `key_table.py:140` `testing.beside`; `filters.py` `_test` returns `read.is_test` (set by the reader's placement, beside or tree). |
| `filters.interface` C | an interface is a base class name | `filters.py` `_trait("interface")` reads the fact's traits; `python.yaml:92` `class.interface: exact`. |
| `filters.standard` C | from the interpreter only | `filters.py` `_standard` reads the trait `standard` (fact `import.standard`); its list from the data file (`reserved` row). |
| `filters.public` C | privacy is a name prefix | `filters.py` `_trait("public")`; `python.yaml:78`. |
| `filters.record` C | a class with only special methods | `filters.py` `_trait("record")`; `python.yaml:93` `class.record: exact`. |
| `filters.special` C | starts and ends with one token | `filters.py` `_special` calls `language.is_special`, a regular expression (`python.yaml:51`, `xarch/profile_values/language.py` `is_special`). |
| `filters.directive` C | one comment marker | `filters.py` `_directive` reads `language.directives` after the marker of any comment form (`python.yaml:54-55`). |
| `targets.path` C | dotted names only | `targets.py` `_path` reads the fact's `path`; entries split by `language.member` (`python.yaml:49`; `own_checks.py` `outside_steps(value, profile.language.member)`). |
| `targets.package` C | top-level package as an identifier | `targets.py` `_package` takes `path[:1]`, the first step as the reader gives it; packages match `python.yaml:48` `package`. |

For each row, run the `git grep`/`profile explain` the check names and read the function it names
(`grep -n "def _test\b\|def _standard\|def _special\|def _trait\|def _directive" xarch/modules/rules/application/logic/filters.py`,
`grep -n "def _path\|def _package" xarch/modules/rules/application/logic/targets.py`). Then write one line per row:

```
<row> <S|C> -> N: <file>:<line> <one clause: what now comes from data or a fact>
```

or, when the check fails (Python still decides it outside the reader and the data file):

```
<row> <S|C> not moved: <file>:<line> <what still ties it to Python>
```

`testing.functions` is written `testing.functions S -> retired: xarch/modules/spec/domain/profile_keys.py:228 the key
no longer exists; its successor testing.declared takes function and call forms (test.function, test.call)`.

Expected: twenty lines in spec 4 (A)'s order. Run `wc -l < /tmp/xarch-9-1/rows-checked.txt` → `20`.

- [ ] **Step 3: No commit**

Run `git status --short` and check nothing tracked changed.

---

### Task 4: Gates, the golden-docs check, and the card comment

**Files:**
- Create (scratch): `/tmp/xarch-9-1/comment.txt`, `/tmp/xarch-9-1/pytest.log`
- Modify: none (the golden docs are regenerated as a check and must not move).

**Interfaces:**
- Consumes: `/tmp/xarch-9-1/{all,ex}.tsv`, `{all,ex}.counts`, `superpowers-files.txt`, `unfixed.txt` (Task 2),
  `rows-checked.txt` (Task 3).
- Produces: one comment on card `a5d05c8a-859e-43e9-8958-0fa4c62bec80`.

- [ ] **Step 1: Re-run the re-grep on the final branch**

Run: `/tmp/xarch-9-1/regrep.sh > /tmp/xarch-9-1/all.txt 2> /tmp/xarch-9-1/all.err; /tmp/xarch-9-1/regrep.sh --exclude-dir=superpowers > /tmp/xarch-9-1/ex.txt 2> /tmp/xarch-9-1/ex.err; python3 -I /tmp/xarch-9-1/classify.py /tmp/xarch-9-1/ex.txt /tmp/xarch-9-1/hand.tsv > /tmp/xarch-9-1/ex.tsv 2> /tmp/xarch-9-1/ex.counts; python3 -I /tmp/xarch-9-1/classify.py /tmp/xarch-9-1/all.txt /tmp/xarch-9-1/hand.tsv > /tmp/xarch-9-1/all.tsv 2> /tmp/xarch-9-1/all.counts; grep -cP '\tUNCLASSED\t' /tmp/xarch-9-1/all.tsv`
Expected: `0` (and `grep -v '__pycache__/.*\.pyc: binary file matches$' /tmp/xarch-9-1/*.err` prints nothing), and
`ex.counts` equal to Task 2's final counts (if a Step 5 fix ran, the counts are those of after it).

- [ ] **Step 2: The golden docs, regenerated as the test builds them**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_recorded_corpora.py 2>&1 | tail -2; git status --short docs/ tests/bootstrap/corpora/`
Expected: PASS (tests 3 and 4 of spec 5) and no file under `docs/` or the corpora listed, apart from this card's
untracked spec and plan under `docs/superpowers/`. If a golden doc test fails, read its diff and stop to report:
nothing in this card changes a profile's meaning, and no golden doc is edited by hand.

- [ ] **Step 3: The lock and the diff of the branch**

Run: `uv lock --check; echo "exit=$?"; git diff --stat 79ea9d4..HEAD`
Expected: `exit=0`; `pyproject.toml | 2 +-` and `uv.lock | 2 +-` (plus the files of any Task 2 Step 5 fix, nothing
else).

- [ ] **Step 4: The gates, the suite in the background**

Run, one at a time, each expected to exit 0:
```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```
Expected: `All checks passed!` from ruff; `xarch check` and `--strict` report no violation; `profile check` says the
profile is valid. Never `ruff check --fix`.

Then start the suite in the background (it takes over two minutes), with the Bash tool's `run_in_background: true`:
`timeout 900 uv run pytest -q > /tmp/xarch-9-1/pytest.log 2>&1; echo "exit=$?" >> /tmp/xarch-9-1/pytest.log`
When it finishes: `tail -3 /tmp/xarch-9-1/pytest.log`
Expected: `N passed` with no `failed` or `error`, and `exit=0`. A failure is read and reported, not retried until it
passes.

- [ ] **Step 5: Write the card comment**

Build `/tmp/xarch-9-1/comment.txt` from the scratch files. Its shape, plain text:

```
9.1 release: version 0.3.0; re-grep and coupling-audit rows

(A) Coupling-audit rows that move to N (language-neutral-design.md 12, last row). N: the meaning and shape work for
any language; a new language needs only a reader that supplies the facts (python-coupling-audit.md:27). Each checked
on this branch at <git rev-parse --short HEAD>.

<the "-> N" and "-> retired" lines of rows-checked.txt, in order>

Not moved
<the "not moved" lines of rows-checked.txt, or "none">

(B) Re-grep hits reported, not fixed (spec 3.3), from the final run

<for each 3.3 class label present in all.counts, in order 3.3.1 to 3.3.7:>
<label> — <count> hits — ruling: <the ruling of spec 3.3 for that class, one sentence, with its citations>
  <for 3.3.1: "in <n> files:" and the list of superpowers-files.txt; for the others: every <path>:<line> of all.tsv
  with that label, from `grep -P '\t<label>\t' /tmp/xarch-9-1/all.tsv | cut -f1,2`>

Leftovers not fixed (3.4)
<the lines of unfixed.txt with the ruling each would break, or "none">

Lines inside the notes' own lists (3.2): <the 3.2 counts from ex.counts, one per label>.

Verdict: clean apart from the classes reported in (B).
Command (spec 3.1), run once as written and once with --exclude-dir=superpowers on each grep:
<the seven grep lines of /tmp/xarch-9-1/regrep.sh, with $X removed>
```

Commands to fill it:
```bash
rev=$(git rev-parse --short HEAD)
grep -P '\t3\.3\.' /tmp/xarch-9-1/all.tsv | cut -f3 | sort | uniq -c
for l in "3.3.2 docs/examples" "3.3.3 rules not the rule id" "3.3.4 S4.7 kept name" "3.3.5 CaseTable in recorded findings" "3.3.6 package_file in the scaffold" "3.3.7 LN prose and test names"; do echo "== $l"; grep -P "\t${l//./\\.}\t" /tmp/xarch-9-1/all.tsv | cut -f1,2; done
cat /tmp/xarch-9-1/superpowers-files.txt
sed -n '/^P=/,$p' /tmp/xarch-9-1/regrep.sh | sed 's/ \$X//'
```

The rulings, one sentence each, copied from spec 3.3 (keep their citations): 3.3.1 records of past steps, added after
the notes, not edited; 3.3.2 placement examples `review calibrate` sends (KN 252-254, S2.3 204-205, S4.7 146-147,
S3.7 259-261); 3.3.3 the module/part `rules` and the JSON field `rules`, present at `6dda0e7`, kept by S2.3 182-189
and 202; 3.3.4 S4.7 2.3 (121-148) and classes 4-8 of S4.7 150-182; 3.3.5 recorded corpora edited only as a note
says; 3.3.6 the scaffold's one package file, kept by S3.7 108-110 (the note's pattern targets the old data-file key,
LN 791); 3.3.7 LN 1.5 (192-194) retires the wording that assumed names resolve only through absolute imports, these
use "absolute" as the opposite of `Import.relative` or quote a user's rule, and `is_public` survives only in test
names and the test that the method is gone.

Check: `grep -c . /tmp/xarch-9-1/comment.txt` (non-empty), `grep -n 'UNCLASSED\|@@' /tmp/xarch-9-1/comment.txt`
(no output), and read it whole once.

- [ ] **Step 6: Post the comment, once**

Run: `brd comment add a5d05c8a-859e-43e9-8958-0fa4c62bec80 - < /tmp/xarch-9-1/comment.txt`
Expected: `brd` prints the new comment's id. Then `brd comment list a5d05c8a-859e-43e9-8958-0fa4c62bec80 2>&1 | tail -20` shows it. Post it once; if it failed, read the error and
post again only after confirming no comment was created.

- [ ] **Step 7: The task report**

The report (in the session's final message, not a committed file) holds: Task 1 Step 6's output; `uv lock --check`'s
exit; `git diff --stat 79ea9d4..HEAD`; Step 2's `git status --short docs/` (empty); the gates' and the suite's last
lines; the full outputs of the re-grep (`/tmp/xarch-9-1/all.txt`, `ex.txt`) and their classing (`all.tsv`, `ex.tsv`)
line by line, or their paths with the counts if the session cannot carry them whole; the `hand.tsv` rows added; the
leftovers (none expected); and the comment's id. No commit in this task.

---

## Self-review (planner)

1. **Spec coverage.** 1.1 version → Task 1 (pyproject Step 2, lock Step 4, `--version` Step 6, `uv lock --check`
   Step 4, other `0.2.0` Step 7). 1.2 re-grep → Task 2 (3.1 Steps 1-2, 3.2/3.3 Steps 3-4, 3.4 Step 5, 3.5 Step 2's
   `may_not_use` count and the classed `tier:`/`_snake_name` lines) and Task 4 Step 1 (final run). 1.3 card comment →
   Task 3 (A) and Task 4 Steps 5-6 (B). Section 4's golden-docs check → Task 4 Step 2. Section 5 tests 1-2 → Task 1
   Steps 3, 5; tests 3-4 → Task 4 Step 2; test 5 → Task 2 Step 5. Manual checks → Task 4 Step 7. Section 6 gates →
   Task 4 Step 4. Out-of-scope items (README read whole, CHANGELOG lead, final regeneration, the audit file, tagging)
   → no task, and the Global Constraints forbid them.
2. **Placeholders.** The scripts are given whole; `<...>` appears only in the commit message of a conditional fix
   (whose content depends on a leftover not known in advance) and in the comment's template, whose fill commands are
   given.
3. **Consistency.** Labels used in Task 4 Step 5 are keys of `LABELS` in Task 2's `classify.py`; file names under
   `/tmp/xarch-9-1/` agree across tasks; row names and order agree between `evidence.py`, Task 3's table and spec 4 A.
4. **Review Focus.** Each line has its check: 1 → Task 1 Step 6; 2 → Task 1 Step 4; 3 → Task 2 Step 4 and Task 4
   Step 1; 4 → Task 2 Steps 2-4 (both runs, class-1 count); 5 → Task 3 Steps 1-2.
<!-- task-pipeline: validated -->
