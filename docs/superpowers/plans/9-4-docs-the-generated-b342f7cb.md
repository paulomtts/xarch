# 9.4 docs: the generated docs regenerated with no diff — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The golden docs (`docs/cli/`, `docs/web/`, `docs/xarch/`) are regenerated from this branch's code into a
scratch directory outside the repository, compared with `diff -r`, the empty diff read and recorded, and the three
golden-doc tests and the five gates run green, with no repository change beyond the spec and this plan.

**Architecture:** Verification only. A throwaway script kept outside the worktree calls the same
`build_controllers().spec.docs(<target>).files` the tests call, for `cli`, `web` and xarch's own
`architecture.yaml`, and writes each file under a `mktemp -d` directory; `diff -r` compares each scratch tree with its
golden directory. There is no implementation step: if every diff is empty there is nothing to write and nothing to
commit; if any diff appears the task stops and escalates (spec section 3), editing nothing.

**Tech Stack:** Python 3.13, `uv`, pytest, ruff, `xarch` CLI, GNU `diff`.

**Spec:** `docs/superpowers/specs/9-4-docs-the-generated-b342f7cb.md` (copied verbatim below, ahead of the tasks).

## Global Constraints

- No file under `docs/cli/`, `docs/web/`, `docs/xarch/` or `docs/templates/` is edited by this card.
- No file under `xarch/` or `tests/` is edited.
- No README line and no CHANGELOG line is written; the empty `## [Unreleased]` heading (CHANGELOG.md:6) stays empty.
- `pyproject.toml` and `uv.lock` are not touched.
- The scratch regeneration writes only outside the worktree (a `mktemp -d` directory); the script itself lives outside
  the worktree too (`/tmp/xarch-9-4/regen.py`).
- Gates: `uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch check --strict`,
  `uv run xarch profile check architecture.yaml`, then `uv run pytest -q` in the background, read at the end.
- `.claude/` stays out of commits; nothing is pushed.
- A diff is never accepted and never fixed in the golden copy: it is traced and escalated (spec section 3).

## Review Focus

1. **A golden directory holds a file the tests do not glob** (anything not `*.md`, which `rglob("*.md")` skips): the
   tests stay green while the tree differs. `diff -r` over the whole directory catches it ("Only in docs/..."); Step 3
   reads that output, and Step 2 lists any non-`.md` file under the three directories.
2. **The scratch output lands inside the repository** (a relative path, or a scratch dir under the worktree): the
   golden copies or `git status` get polluted. Step 1 asserts the scratch directory is outside the worktree, and
   Step 7 asserts `git status --porcelain` shows only the spec and the plan.
3. **xarch's own profile resolved against the wrong directory** (`architecture.yaml` given relative while the script
   runs from elsewhere): it would regenerate a different profile or fail. The script resolves it against the
   worktree root passed as an argument, the same absolute path the test uses (`DOCS.parent / "architecture.yaml"`).
4. **An empty or partial regeneration compares as "no diff" against nothing** (e.g. the script crashes after writing
   `cli`): Step 3 runs under `set -e`, and Step 2 counts the regenerated files per directory against the golden ones
   so a missing tree cannot pass silently.
5. **A green suite taken as the read** (spec 2.3): the run log must carry the three literal lines "cli: no diff",
   "web: no diff", "xarch: no diff" produced from the `diff -r` exit status, not inferred from pytest.

---

# The spec (verbatim)

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

---

# Tasks

### Task 1: Regenerate the golden docs, read the diff, run the tests and gates

**Files:**
- Create (outside the repository, not committed): `/tmp/xarch-9-4/regen.py`
- Read only: `docs/cli/**`, `docs/web/**`, `docs/xarch/**`, `tests/bootstrap/test_docs_templates.py`
- Modify: none
- Test: `tests/bootstrap/test_docs_templates.py` (existing, run as is)

**Interfaces:**
- Consumes: `xarch.bootstrap.wiring.build_controllers()`; its `.spec.docs(target: str)` returns an object whose
  `.files` are items with `.path: tuple[str, ...]` (path segments under `docs/project/`) and `.template: str` (the
  filled text). `target` is a bundled profile name (`"cli"`, `"web"`) or a path to an architecture file.
- Produces: nothing a later task uses; a run log with "cli: no diff", "web: no diff", "xarch: no diff".

All commands run from the worktree root
(`/home/mtts/Code/xarch/.claude/worktrees/v030/task-9-4-docs-the-generated-b342f7cb`).

- [ ] **Step 1: Write the regeneration script outside the worktree and make the scratch directory**

```bash
mkdir -p /tmp/xarch-9-4
cat > /tmp/xarch-9-4/regen.py <<'PY'
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
if out == root or root in out.parents:
    sys.exit(f"scratch directory {out} is inside the worktree {root}")
targets = (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml")))
for name, target in targets:
    files = build_controllers().spec.docs(target).files
    if not files:
        sys.exit(f"{name}: no files generated")
    for f in files:
        dest = out / name / Path(*f.path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f.template, encoding="utf-8")
    print(f"{name}: {len(files)} files")
PY
SCRATCH=$(mktemp -d)
echo "$SCRATCH" > /tmp/xarch-9-4/scratch-path
echo "$SCRATCH"
```

Expected: a path under `/tmp/` (not under the worktree).

- [ ] **Step 2: Regenerate and count**

```bash
set -e
SCRATCH=$(cat /tmp/xarch-9-4/scratch-path)
uv run python /tmp/xarch-9-4/regen.py "$PWD" "$SCRATCH"
for d in cli web xarch; do
  echo "$d: generated $(find "$SCRATCH/$d" -type f | wc -l), golden $(find "docs/$d" -type f | wc -l)"
done
echo "non-.md files in golden dirs:"; find docs/cli docs/web docs/xarch -type f ! -name '*.md'
```

Expected: the script prints `cli: 12 files`, `web: 12 files`, `xarch: 2 files`; for each directory the generated and
golden counts are equal (12, 12, 2); the non-`.md` list is empty. Measured when the plan was written: exactly that. If counts differ or the script exits non-zero, go to Step 9 (escalate).

- [ ] **Step 3: Diff and read the output**

```bash
SCRATCH=$(cat /tmp/xarch-9-4/scratch-path)
for d in cli web xarch; do
  if diff -r "$SCRATCH/$d" "docs/$d"; then echo "$d: no diff"; else echo "$d: DIFF"; fi
done
```

Expected (verified at `912267d` while writing this plan):

```
cli: no diff
web: no diff
xarch: no diff
```

Read the whole output, not just the last lines. Copy the three result lines verbatim into the run log. Any
`$d: DIFF` line, or any `Only in` / `diff -r` hunk above it, means go to Step 9.

- [ ] **Step 4: Run the three golden-doc tests**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py`
Expected: `34 passed` (the count measured when the spec was written), including
`test_init_writes_exactly_the_docs_checked_in_for_the_profile[cli]`, `[web]`,
every `test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte[...]` case and
`test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch`. A failure in any of those three
goes to Step 9.

- [ ] **Step 5: Run the four quick gates**

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```

Expected: each exits 0 (`ruff`: "All checks passed!"). Never add `--fix`. A failure here is not this card's to fix:
record the output and go to Step 9.

- [ ] **Step 6: Run the full suite in the background and read it at the end**

Start it in the background (it takes over two minutes):

```bash
timeout 900 uv run pytest -q > /tmp/xarch-9-4/pytest.log 2>&1; echo "exit $?" >> /tmp/xarch-9-4/pytest.log
```

When it has finished, read it: `tail -n 20 /tmp/xarch-9-4/pytest.log`
Expected: a final summary line with `passed` and no `failed` or `error`, and `exit 0`.

- [ ] **Step 7: Confirm the repository is unchanged**

```bash
git status --porcelain
git diff --stat HEAD -- docs/cli docs/web docs/xarch docs/templates xarch tests README.md CHANGELOG.md pyproject.toml uv.lock
sed -n 6,8p CHANGELOG.md
```

Expected: `git status --porcelain` lists only
`?? docs/superpowers/specs/9-4-docs-the-generated-b342f7cb.md` and
`?? docs/superpowers/plans/9-4-docs-the-generated-b342f7cb.md` (or nothing, if the workflow has already committed
them); the `git diff --stat` prints nothing; CHANGELOG line 6 is `## [Unreleased]` followed by a blank line and then
`## [0.3.0] ...` (no entry under it).

- [ ] **Step 8: Commit — skipped by design**

There is nothing to commit: the regeneration is a check, not a change, and the spec and plan are committed by the
workflow's `docs_commit` step. Do not run `git commit`. Record in the run log:

```
cli: no diff
web: no diff
xarch: no diff
tests/bootstrap/test_docs_templates.py: 34 passed
gates: ruff, xarch check, xarch check --strict, xarch profile check architecture.yaml: pass
full suite: <summary line from /tmp/xarch-9-4/pytest.log>
commit: none (no repository change)
```

Then remove the scratch files: `rm -rf "$(cat /tmp/xarch-9-4/scratch-path)" /tmp/xarch-9-4`.

- [ ] **Step 9: Error path only — a diff or failure appeared: trace and escalate, edit nothing**

Only if Step 2, 3 or 4 showed a difference (or a gate failed). Do not edit any golden copy, template, profile or code.

1. Read the diff: file, lines, old text (golden, right side of `diff -r "$SCRATCH/$d" "docs/$d"`) and new text
   (generated, left side).
2. Trace it, replacing the placeholders with the file and text the diff names:

```bash
git log --oneline -- docs/templates/architecture.md docs/templates/testing.md \
  xarch/architectures/cli.yaml xarch/architectures/web.yaml xarch/architectures/cli.md xarch/architectures/web.md \
  xarch/architectures/testing.md architecture.yaml
git log --oneline -S '<the moved text, copied from the diff>'
git log --oneline -- docs/<dir>/<file from the diff>
```

   The commit that changed the source without regenerating (or regenerated before a later source change) is the one
   whose `-S` hit touches the template, profile or rendering code but not the golden file. R3 section 3 rows and the
   O8 owners (key-names: `never-use`, `may-import` lines, tier docs text; code-shape: `immutable`, `no-callbacks`
   lines; profile-form: `{{placement}}`) say which step was entitled to move that line.
3. Report and stop: the defect, the commit and step it traces to, and whether the generated text or the checked-in
   text is the one that step meant. Escalate with that report; the fix belongs to the owning step's source.

---

## Self-review against the spec

- Spec 2.1 (regenerate by the tests' call, scratch outside the repo, `diff -r` against the three dirs): Steps 1-3.
- Spec 2.2 (diff empty, three tests pass): Steps 3-4.
- Spec 2.3 (the diff read and recorded as "cli/web/xarch: no diff"): Steps 3 and 8.
- Spec 2.4 (no edits under docs/cli, docs/web, docs/xarch, docs/templates, xarch, tests): Global Constraints, Step 7;
  no step writes there.
- Spec 2.5 (no README/CHANGELOG line, `[Unreleased]` stays empty): Step 7.
- Spec 2.6 (five gates): Steps 5-6.
- Spec 3 (error path: read, trace, report and stop): Step 9.
- Spec 4 (no new test): none added; existing tests run in Step 4.
- Spec 6 (no `--fix`, full suite in background, scratch outside the worktree): Steps 1, 5, 6.
- Spec 7 (one task, commit skipped, no step writes into golden dirs): Task 1, Step 8.

<!-- task-pipeline: validated -->
