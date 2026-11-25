# 9.4 docs: the generated docs regenerated with no diff

Card `b342f7cb`, subtask of `d96ff4b1`. Release step 25 of the merged order, the part of it this card owns: the
golden docs regenerated once more, the diff expected empty and read, any diff a defect traced to its step.

Sources, cited by short name and line (all under `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`, read only,
never edited):

- R3: `0.3.0-cohesion-review-3.md`.
  - Section 3, row 25 (288): "golden docs regenerated with no diff".
  - Overlap O8 (232): "Golden docs `docs/{cli,web,xarch}/testing.md`, byte for byte | key-names (`never-use`,
    `may-import` lines, the tier docs text), code-shape (`immutable`, `no-callbacks` lines), profile-form
    (`{{placement}}` under A) | Each step regenerates and reads the diff; step 25 regenerates once more and expects
    none."
  - Section 3, preamble (250-252): the gates every row passes, `uv run ruff check` (no `--fix`),
    `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, then
    `uv run pytest -q` in the background, read at the end.
  - Row 23 (286) and Q2 (48): the last step whose ruling moves the golden docs (the order line, under the tree's
    reading order). Row 24 (287) moves only what part references change. No row after 24 moves them.
  - O4 (228), O5 (229): a step's README and CHANGELOG lines go under `[Unreleased]`.

## 1. What "the golden docs" are, and what regenerates them

The golden docs are the files the generator must produce byte for byte; the code is the truth, the files are its
recorded output:

- `docs/cli/**/*.md` and `docs/web/**/*.md`: what `xarch init` writes into `docs/project/` for the bundled `cli`
  and `web` profiles, built from `xarch/architectures/{cli,web}.yaml`, `xarch/architectures/{cli,web}.md` and the
  shared `xarch/architectures/testing.md`.
- `docs/xarch/architecture.md` and `docs/xarch/testing.md`: what xarch's own `architecture.yaml` generates, from
  `docs/templates/architecture.md` and `docs/templates/testing.md`.

The card names the three `testing.md` files (O8); the `architecture.md` files and the other docs under `docs/cli/`
and `docs/web/` are produced by the same call and held by the same tests, so they are regenerated and read with
them. A diff in any of them is the same kind of defect.

The regenerator is `tests/bootstrap/test_docs_templates.py`:

- `generated(profile)` (20-21): `{"/".join(f.path): f.template for f in build_controllers().spec.docs(profile).files}`.
- `test_init_writes_exactly_the_docs_checked_in_for_the_profile` (24-26): the set of generated paths equals the set
  checked in under `docs/<profile>/`.
- `test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte` (29-31): each doc equals
  its golden copy byte for byte.
- `test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch` (62-68): the same, set and
  bytes, for `docs/xarch/` from `architecture.yaml`.

## 2. Required behavior

1. The docs are regenerated from this branch's code by the same call the tests make
   (`build_controllers().spec.docs(<profile or path>).files`), for `cli`, `web` and `architecture.yaml`, written to a
   scratch directory outside the repository, never over the golden copies, and compared with `diff -r` against
   `docs/cli`, `docs/web` and `docs/xarch`.
2. The diff is empty: no file added, none missing, no byte changed. The three tests of section 1 pass.
3. The diff is read: the comparison's output is looked at and its result is recorded in the plan's run log
   ("cli: no diff", "web: no diff", "xarch: no diff"), not inferred from a green suite alone.
4. No file under `docs/cli/`, `docs/web/`, `docs/xarch/` or `docs/templates/` is edited by this card. No file under
   `xarch/` or `tests/` is edited either: the regeneration is a check, not a change.
5. Because nothing user-visible changes, no README line and no CHANGELOG line is written. The empty
   `## [Unreleased]` heading (CHANGELOG.md:6, left by card 9.3) stays empty.
6. All five gates pass on this branch alone (R3 250-252).

Measured when this spec was written (branch at `912267d`): `uv run pytest -q tests/bootstrap/test_docs_templates.py`
gives 34 passed, and the scratch regeneration of item 1 gives "no diff" for all three directories. The card is
therefore expected to end with no repository change beyond this spec and its plan.

## 3. Error path: a diff appears

If the regeneration of item 1 or any of the three tests shows a diff, it is a defect, never accepted and never
fixed in the golden copy (card dodges: "editing the golden copies by hand; accepting a diff without tracing it").

1. Read the diff: which file, which lines, old text and new text.
2. Trace it to its step: `git log --oneline -- <template> <profile yaml> <the code that renders the moved line>` and
   `git log -S '<moved text>'` over the release branch's history, to find the commit that changed the source
   without regenerating, or regenerated before a later commit changed the source. The step rows of R3 section 3 and
   the O8 owners (key-names, code-shape, profile-form) say which step was entitled to move that line.
3. Report and stop: the defect, the commit and step it traces to, and whether the generated text (the code) or the
   checked-in text is the one the step meant. The fix belongs to the owning step's source, not to this card; the
   card escalates with that report instead of editing anything.

## 4. Tests that prove it

No new test is written. The proof is the existing tests, run as they are, plus one read comparison:

| Test | Tier | Why this tier |
|---|---|---|
| `test_init_writes_exactly_the_docs_checked_in_for_the_profile[cli]`, `[web]` | bootstrap (wiring) | Builds the real controllers through `build_controllers()` and reads the bundled data files: the wiring tier is where a file set produced by the assembled application is held. |
| `test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte[<profile>/<doc>]` | bootstrap (wiring) | Same: byte equality of each generated doc against its golden copy through the assembled application. |
| `test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch` | bootstrap (wiring) | Same, for xarch's own profile and templates. |
| Scratch regeneration and `diff -r` (section 2, item 1) | manual check, recorded in the run log | It is the read the card asks for: a test says pass or fail, the diff shows what moved. It writes outside the repository and is not committed. |
| `uv run pytest -q` (full suite), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml` | gates | The card's gates (R3 250-252); they show nothing else on the branch regressed. |

A new test would duplicate the three above: they already hold the file set and every byte.

## 5. Out of scope

- The placement measure: card 9.5 ("Out of scope: the placement measure (9.5)").
- README (card 9.2, done) and CHANGELOG (card 9.3, done): this card writes no line in either.
- The version (card 9.1, done): `pyproject.toml` and `uv.lock` are not touched.
- The rest of row 25 that belongs to no card here: every note's re-grep run together and the coupling audit
  refreshed (R3 288; the audit is the owner's, outside the repository).
- Recorded corpora (`tests/bootstrap/corpora/`) and recorded findings: not read or edited.
- Fixing a diff, if one appears (section 3): the owning step's work, escalated.

## 6. Project rules that apply

No comments in xarch's code; never `ruff --fix`; `.claude/` stays out of commits; nothing is pushed; the full suite
takes over two minutes and runs in the background, read at the end; the scratch regeneration writes only outside the
worktree (for example a `mktemp -d` directory).

## 7. Handoff to the planner

One task, verification only, in the writing-plans format: regenerate to a scratch directory, `diff -r`, record the
read result, run the three tests, run the five gates. Its "implementation" steps are empty by design: if the diff is
empty there is nothing to write, and the task's commit step is skipped (there is nothing to commit); if a diff
appears, the task stops at section 3 and escalates. The plan must not contain any step that writes into
`docs/cli`, `docs/web`, `docs/xarch` or `docs/templates`.
