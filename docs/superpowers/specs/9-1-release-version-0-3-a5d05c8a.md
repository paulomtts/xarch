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
