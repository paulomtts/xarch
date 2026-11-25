# 1.1 corpora: the two archived profiles as plain yaml beside their archives

Card `40fa4c21`, subtask of `4e9e503c`. Release step 0 of the 0.3.0 merged order.

## Sources this spec inherits from

- `key-names-design.md` line 28, ruling 8: "The two archived test profiles move out of `7cc6111.tar.xz` and
  `df537ca.tar.xz` into plain yaml beside them. The docstring rule becomes 'never edit the archived code'."
- `0.3.0-cohesion-review-3.md` section 3 (line 248 on), row 0 (line 258): "Baseline gates. The two archived profiles
  out of `7cc6111.tar.xz` and `df537ca.tar.xz` into plain yaml beside them; the docstring says 'never edit the
  archived code'. No output may change." Lines 250-253 give the gates and their order.
- The same file, overlap O9 (line 233): "Step 0 frees the archives; then each step its lines."
- `code-shape-design.md` section 5.5, lines 769-772: the two archived profiles are "edited as plain files: release
  step 0 moves them out of the archives (owner's ruling)".

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`.

## What is there now

- `tests/bootstrap/corpora/7cc6111.tar.xz` and `df537ca.tar.xz` each hold an `architecture.yaml` at the archive root
  (173 lines, SHA-256 `cca3ebb1…24b4`, and 193 lines, SHA-256 `c5105604…fa6`), next to the archived project's
  `xarch/` and `tests/` trees.
- `tests/bootstrap/test_recorded_corpora.py:85-90` unpacks each archive into `tmp_path` and checks it against
  `str(project / "architecture.yaml")`, the profile that came out of the archive.
- The docstring (lines 1-33) says the corpus holds "its Python files and its profile (`corpora/<commit>.tar.xz` …)"
  (lines 3-5) and ends with "Never edit an archived project or its profile, whose findings were recorded from it"
  (lines 32-33).
- Both profiles say `based_on: cli`, which is a bundled name and not a path. Neither profile names a path relative to
  its own folder, so the folder it sits in does not change what it means.
- No recorded finding in `7cc6111.json` or `df537ca.json` names `architecture.yaml`. The check walks the app folder
  (`<project>/xarch`) and the tests folder (`<project>/tests`), and the profile sits at the project root, so the
  profile file is not one of the files checked.
- `tests/bootstrap/corpora/stress.yaml` already sets the pattern of a plain profile beside the archives.

## Required behavior

1. **Two plain profiles.** `tests/bootstrap/corpora/7cc6111.yaml` and `tests/bootstrap/corpora/df537ca.yaml` exist.
   Each is byte for byte the `architecture.yaml` its archive held before this step: same bytes, same line endings,
   same final newline.
2. **The profile moves out of the archive.** After this step neither `7cc6111.tar.xz` nor `df537ca.tar.xz` has an
   `architecture.yaml` member, so there is one copy of each profile and no archived one to edit by mistake. That
   dodge is named on the card. Every other member of each archive keeps its name, its bytes and its type. The
   archived code is not edited.
3. **The test reads the plain file.** The commit test checks the unpacked project against `corpora/<commit>.yaml`
   and never against a file from inside the archive.
4. **No output changes.** Both commits give exactly the findings recorded in `corpora/<commit>.json`, which stay byte
   for byte as they are. `stress-7cc6111.json.xz`, `examples-*.json`, `stress.yaml` and `examples.tar.xz` are
   untouched. The stress test still passes, and it unpacks the same `7cc6111.tar.xz`, now without its profile.
5. **The docstring says so.** The module docstring of `test_recorded_corpora.py` says each commit's corpus is its
   Python files, archived (`corpora/<commit>.tar.xz`, from `git archive <commit>`), with its profile beside the
   archive as plain yaml (`corpora/<commit>.yaml`). The last rule becomes "Never edit the archived code, whose
   findings were recorded from it." It no longer forbids editing the profile, because later steps (O9) edit these
   profiles as plain files under the recording rules the docstring already gives. The table at lines 7-12, the
   recording method and the other rules keep their wording.
6. **The CHANGELOG says it.** Add one line under `## [Unreleased]`, in a `### Changed` heading, written the way the
   0.2.0 entries are. For example: "The two archived corpora's profiles (`7cc6111`, `df537ca`) are plain yaml files
   beside their archives in `tests/bootstrap/corpora/`, so a change of format edits them as files; the recorded
   findings are unchanged." The README needs no line, because it never mentions the corpora.
7. **Golden docs.** Regenerate `docs/{cli,web,xarch}/testing.md` the way the repository does. O8 lists no change for
   step 0, so `git diff -- docs/` must be empty. If it is not empty, stop and report: this step must not move them.

## Error paths

- If a plain profile is missing, the commit test fails with a "file not found" error naming `corpora/<commit>.yaml`.
  It must not fall back to anything inside the archive.
- If someone puts a profile back into an archive, the guard test (T2) fails and names the archive.
- If someone edits a plain profile so that the findings move, the existing commit test fails through
  `first_difference`, with the first finding that differs. Nothing new is needed for that.

## Tests

The first three tests below are written first and fail first. The commit test (T3) changes only in where it reads
the profile.

| # | Test (in `tests/bootstrap/test_recorded_corpora.py`) | Tier | Why this tier |
|---|---|---|---|
| T1 | `test_each_archived_commit_has_its_profile_beside_its_archive_as_plain_yaml`, parametrized on `7cc6111` and `df537ca`: `CORPORA / f"{commit}.yaml"` is a file and parses as yaml with `name: xarch` and `based_on: cli` | wired (bootstrap) | It reads the real corpus files on disk, where the corpora's other tests live. No production code is involved. |
| T2 | `test_no_archived_commit_holds_a_profile_of_its_own`, parametrized on the same: the archive's member names do not include `architecture.yaml` | wired (bootstrap) | It guards the card's named dodge for good: an archived profile cannot come back without failing. |
| T3 | the existing `test_an_earlier_commit_checked_against_its_own_profile_…`, changed to pass `str(CORPORA / f"{commit}.yaml")` | wired (bootstrap), unchanged | It is the proof that no output changed: the findings recorded byte for byte against the old checks. |
| T4 | `test_an_earlier_commit_checked_against_a_tightened_profile_…` and the examples tests, unchanged | wired (bootstrap) | They show that unpacking the repacked `7cc6111.tar.xz` still gives the same project. |

A one-time proof is run during the step and kept out of the suite. Show it in the task report: for each archive, the
old archive (from `git show HEAD:tests/bootstrap/corpora/<commit>.tar.xz`) and the new one list the same members
except `architecture.yaml`, and each of those members has the same bytes (compare the SHA-256 of each member). Also,
`sha256sum` of each new `.yaml` equals the old in-archive `architecture.yaml`. A test inside the suite cannot hold the
old archive, so this proof stays outside it.

## How the archive is repacked (the constraint, not the code)

Rewrite each `.tar.xz` so that it holds every member of the old one in the same order, except `architecture.yaml`.
Keep each member's name, type, mode and bytes. Compress with xz as before. Do not unpack it to disk and re-tar a
folder, because that can change the order, add directory entries or change the modes. Read the old archive's members
and write them out unchanged. A short throwaway script outside the repository is enough, and it is not committed.

## Gates

Each must pass on this branch with the full suite green. Run them in this order (review 3, lines 250-253):

1. `uv run ruff check` (never `--fix`)
2. `uv run xarch check`
3. `uv run xarch check --strict`
4. `uv run xarch profile check architecture.yaml`
5. `uv run pytest -q`, run in the background (it takes over two minutes) and read at the end

Baseline: run all five before any change and record the results, so that a failure the step did not cause is known
from the start.

## Project rules that bind this step

No comments in xarch's code (docstrings only). Never `ruff --fix`. Tests come first. The recorded corpora are edited
by hand only, and only as the note says. Python goes only in the reader adapter and the presets' data files, and the
throwaway repack script is not committed. `.claude/` stays out of commits. Nothing is pushed.

## Out of scope

- Any edit of the two profiles' content (keys, values, comments, whitespace). Later steps 2 onward edit them (O9).
- The archived Python code and tests, and every other corpus file (`stress.yaml`, the findings files,
  `examples.tar.xz`).
- Any rename of a key, rule id or identifier. Those belong to steps 1-5 and their sibling cards.
- `tests/bootstrap/test_written_rules.py`, which reads only `examples.tar.xz`.
- README lines, and any change of xarch's production code.


---

# 1.1 corpora: the two archived profiles as plain yaml Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the `architecture.yaml` out of `tests/bootstrap/corpora/7cc6111.tar.xz` and `df537ca.tar.xz` into
`tests/bootstrap/corpora/7cc6111.yaml` and `df537ca.yaml`, byte for byte, point the commit test at the plain files,
and change no recorded finding.

**Architecture:** Test data and one test module only. The profile bytes are copied out of the archives as they are
at `HEAD`; each archive is rewritten member by member with a throwaway Python script kept in `/tmp` (never in the
repository), dropping only `architecture.yaml`. Two new guard tests pin the new layout; the existing commit test
reads `CORPORA / f"{commit}.yaml"`. The module docstring and the CHANGELOG say so. No production code changes.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `pyyaml` (already a dependency), the standard library's `tarfile`,
`hashlib`, `lzma`.

**Spec:** `docs/superpowers/specs/1-1-corpora-the-two-40fa4c21.md` (prepended above).

## Global Constraints

- Each plain profile is "byte for byte the `architecture.yaml` its archive held before this step: same bytes, same
  line endings, same final newline". SHA-256: `7cc6111` → `cca3ebb1398293dfdf384a4b2f53f2ed905c681ad5e5d2b5ed536a09e0a624b4`,
  `df537ca` → `c5105604cf82b846404696449e7d741687a657f78002c2200817aa253c93cfa6`.
- "Every other member of each archive keeps its name, its bytes and its type. The archived code is not edited."
- "Do not unpack it to disk and re-tar a folder … Read the old archive's members and write them out unchanged."
  Compress with xz. The repack script is not committed.
- `corpora/<commit>.json`, `stress-7cc6111.json.xz`, `examples-*.json`, `stress.yaml`, `examples.tar.xz` stay byte for
  byte as they are.
- `git diff -- docs/` (excluding `docs/superpowers/`) must be empty after regenerating the golden docs; if not, stop
  and report.
- No comments in xarch's code (docstrings only). Never `ruff --fix`. Tests come first. `.claude/` stays out of
  commits. Nothing is pushed. Never `git add docs/superpowers/` (the workflow commits the spec and plan itself).
- Gates, in this order: `uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`,
  `uv run xarch profile check architecture.yaml`, `uv run pytest -q` (in the background, read at the end).
- Never kill processes by name or pattern; stop a stuck test with `timeout`.

## Review Focus

1. **A plain profile is missing.** Someone deletes `corpora/7cc6111.yaml`: the commit test must fail naming
   `7cc6111.yaml` and must not quietly read some profile from the unpacked archive. Pinned by
   `test_a_missing_plain_profile_is_named_and_nothing_from_the_archive_stands_in` (Task 1).
2. **The repack changes a member.** A re-tar from disk would reorder members, add directory entries or change modes.
   The out-of-suite proof (Task 1, Step 8) compares name, type, mode, size and SHA-256 of every member in order.
3. **The copied profile is not byte-identical** (a text-mode copy, a stripped final newline). Pinned by the
   `sha256sum` comparison in Task 1, Step 8, and by the commit test giving the recorded findings.
4. **A profile is put back into an archive.** Pinned by `test_no_archived_commit_holds_a_profile_of_its_own`, whose
   failure message names the archive (Task 1).
5. **The stress test unpacks the repacked `7cc6111.tar.xz`** and must still give its 1735 findings. Pinned by the
   unchanged `test_an_earlier_commit_checked_against_a_tightened_profile_…`, run in Task 1, Step 7.

---

### Task 1: The profiles beside their archives, and the tests that read them

**Files:**
- Create: `tests/bootstrap/corpora/7cc6111.yaml`
- Create: `tests/bootstrap/corpora/df537ca.yaml`
- Modify: `tests/bootstrap/corpora/7cc6111.tar.xz` (repacked without `architecture.yaml`)
- Modify: `tests/bootstrap/corpora/df537ca.tar.xz` (repacked without `architecture.yaml`)
- Modify: `tests/bootstrap/test_recorded_corpora.py:35-45` (imports and a constant), `:85-90` (commit test), plus new
  tests appended after line 90
- Throwaway, never committed: `/tmp/xarch-1-1/repack.py`, `/tmp/xarch-1-1/proof.py`

**Interfaces:**
- Consumes: `archived(name: str, into: Path) -> Path`, `findings(project: Path, profile: str, app: str = "xarch") ->
  list[list]`, `first_difference(found, recorded) -> str`, `CORPORA: Path` — all already in
  `tests/bootstrap/test_recorded_corpora.py`.
- Produces: `ARCHIVED: list[str] = ["7cc6111", "df537ca"]` in the same module; the files
  `tests/bootstrap/corpora/<commit>.yaml`.

- [ ] **Step 1: Record the baseline gates**

Run each in order from the worktree root and write down its result (pass/fail and the last line):

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
mkdir -p /tmp/xarch-1-1
timeout 1200 uv run pytest -q > /tmp/xarch-1-1/baseline-pytest.txt 2>&1 &
echo $! > /tmp/xarch-1-1/baseline-pytest.pid
```

Expected: the first four pass. Read `/tmp/xarch-1-1/baseline-pytest.txt` when the process with the recorded PID has
exited (`tail -5 /tmp/xarch-1-1/baseline-pytest.txt`); expected all green. Any failure here was there before this step:
note it in the task report and do not fix it.

- [ ] **Step 2: Write the failing tests**

In `tests/bootstrap/test_recorded_corpora.py`, change the imports and add the constant. Lines 35-45 become:

```python
import json
import lzma
import tarfile
from pathlib import Path

import pytest
import yaml

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp

CORPORA = Path(__file__).parent / "corpora"
ARCHIVED = ["7cc6111", "df537ca"]
"""The commits archived with their profile beside the archive as plain yaml."""
```

Replace the commit test at lines 85-90 with:

```python
@pytest.mark.parametrize("commit", ARCHIVED)
def test_an_earlier_commit_checked_against_its_own_profile_gives_the_findings_recorded_from_the_old_checks(
        commit, tmp_path):
    project = archived(commit, tmp_path)
    recorded = json.loads((CORPORA / f"{commit}.json").read_text(encoding="utf-8"))["findings"]
    assert first_difference(findings(project, str(CORPORA / f"{commit}.yaml")), recorded) == ""


@pytest.mark.parametrize("commit", ARCHIVED)
def test_each_archived_commit_has_its_profile_beside_its_archive_as_plain_yaml(commit):
    profile = yaml.safe_load((CORPORA / f"{commit}.yaml").read_text(encoding="utf-8"))
    assert (profile["name"], profile["based_on"]) == ("xarch", "cli")


@pytest.mark.parametrize("commit", ARCHIVED)
def test_no_archived_commit_holds_a_profile_of_its_own(commit):
    with tarfile.open(CORPORA / f"{commit}.tar.xz") as archive:
        assert "architecture.yaml" not in archive.getnames(), f"{commit}.tar.xz holds architecture.yaml"


def test_a_missing_plain_profile_is_named_and_nothing_from_the_archive_stands_in(tmp_path):
    project = archived("7cc6111", tmp_path / "project")
    assert not (project / "architecture.yaml").exists()
    with pytest.raises(AssertionError, match=r"7cc6111\.yaml: cannot read the file"):
        findings(project, str(tmp_path / "7cc6111.yaml"))
```

Leave every other line of the module as it is (the docstring changes in Task 2).

- [ ] **Step 3: Run the new tests to verify they fail**

Run:
`timeout 600 uv run pytest -q tests/bootstrap/test_recorded_corpora.py -k "beside_its_archive or holds_a_profile or missing_plain_profile or its_own_profile"`

Expected: 7 FAILED —
- `test_each_archived_commit_has_its_profile_beside_its_archive_as_plain_yaml[7cc6111|df537ca]` with
  `FileNotFoundError: … corpora/7cc6111.yaml` (and `df537ca.yaml`);
- `test_no_archived_commit_holds_a_profile_of_its_own[…]` with `7cc6111.tar.xz holds architecture.yaml` (and
  `df537ca.tar.xz …`);
- `test_an_earlier_commit_checked_against_its_own_profile_…[…]` with
  `CheckRefused(reason='…/corpora/7cc6111.yaml: cannot read the file …')` in the assertion;
- `test_a_missing_plain_profile_is_named_and_nothing_from_the_archive_stands_in` on
  `assert not (project / "architecture.yaml").exists()`.

- [ ] **Step 4: Copy each profile out of its archive, byte for byte**

From the worktree root (binary pipe, no text mode, so the bytes and the final newline stay):

```bash
for c in 7cc6111 df537ca; do
  git show HEAD:tests/bootstrap/corpora/$c.tar.xz > /tmp/xarch-1-1/old-$c.tar.xz
  tar -xOJf /tmp/xarch-1-1/old-$c.tar.xz architecture.yaml > tests/bootstrap/corpora/$c.yaml
done
sha256sum tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
```

Expected:
```
cca3ebb1398293dfdf384a4b2f53f2ed905c681ad5e5d2b5ed536a09e0a624b4  tests/bootstrap/corpora/7cc6111.yaml
c5105604cf82b846404696449e7d741687a657f78002c2200817aa253c93cfa6  tests/bootstrap/corpora/df537ca.yaml
```
`wc -l` gives 173 and 193 lines. If either hash differs, stop: the copy is wrong.

- [ ] **Step 5: Write the throwaway repack script outside the repository**

Create `/tmp/xarch-1-1/repack.py` (never inside the worktree, never committed):

```python
"""Write every member of an old .tar.xz, in order and unchanged, except architecture.yaml, into a new .tar.xz."""
import sys
import tarfile

old_path, new_path = sys.argv[1], sys.argv[2]
with tarfile.open(old_path, "r:xz") as old:
    members = old.getmembers()
    with tarfile.open(new_path, "w:xz", format=old.format, pax_headers=old.pax_headers) as new:
        for member in members:
            if member.name == "architecture.yaml":
                continue
            new.addfile(member, old.extractfile(member) if member.isfile() else None)
print(f"{new_path}: {len(members) - 1} members written")
```

- [ ] **Step 6: Repack both archives**

```bash
for c in 7cc6111 df537ca; do
  python3 -I /tmp/xarch-1-1/repack.py /tmp/xarch-1-1/old-$c.tar.xz tests/bootstrap/corpora/$c.tar.xz
done
```

Expected: `… 7cc6111.tar.xz: 327 members written` and `… df537ca.tar.xz: 400 members written` (the old archives
hold 328 and 401 members, all regular files).

- [ ] **Step 7: Run the module's tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_recorded_corpora.py`
Expected: all PASS (3 `first_difference` cases, 2 commit tests, 2 plain-yaml tests, 2 guard tests, the
missing-profile test, the stress test, 2 examples tests: 13 passed).

- [ ] **Step 8: Run the one-time proof outside the suite and keep its output for the report**

Create `/tmp/xarch-1-1/proof.py` (never committed):

```python
"""For each commit: the old and new archive's members in order, each with type, mode, size and SHA-256, compared."""
import hashlib
import sys
import tarfile
from pathlib import Path


def members(path: Path) -> list[tuple]:
    with tarfile.open(path, "r:xz") as archive:
        return [(m.name, m.type, m.mode, m.size, hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                 if m.isfile() else "") for m in archive.getmembers()]


root = Path(sys.argv[1])
for commit in ("7cc6111", "df537ca"):
    old = members(Path(f"/tmp/xarch-1-1/old-{commit}.tar.xz"))
    new = members(root / "tests" / "bootstrap" / "corpora" / f"{commit}.tar.xz")
    profile = [m for m in old if m[0] == "architecture.yaml"]
    plain = hashlib.sha256((root / "tests" / "bootstrap" / "corpora" / f"{commit}.yaml").read_bytes()).hexdigest()
    print(commit, "old", len(old), "new", len(new),
          "same members in order except architecture.yaml:", [m for m in old if m[0] != "architecture.yaml"] == new,
          "architecture.yaml in new:", any(m[0] == "architecture.yaml" for m in new),
          "plain yaml sha256 equals the old member:", len(profile) == 1 and profile[0][4] == plain, plain)
```

Run: `python3 -I /tmp/xarch-1-1/proof.py "$PWD"`

Expected (two lines):
```
7cc6111 old 328 new 327 same members in order except architecture.yaml: True architecture.yaml in new: False plain yaml sha256 equals the old member: True cca3ebb1398293dfdf384a4b2f53f2ed905c681ad5e5d2b5ed536a09e0a624b4
df537ca old 401 new 400 same members in order except architecture.yaml: True architecture.yaml in new: False plain yaml sha256 equals the old member: True c5105604cf82b846404696449e7d741687a657f78002c2200817aa253c93cfa6
```
Paste this output into the task report. Also confirm the other corpus files are untouched:

Run: `git status --short tests/bootstrap/corpora/`
Expected: exactly `M 7cc6111.tar.xz`, `M df537ca.tar.xz`, `?? 7cc6111.yaml`, `?? df537ca.yaml` (paths prefixed
with `tests/bootstrap/corpora/`); nothing else.

- [ ] **Step 9: Lint**

Run: `uv run ruff check` (never `--fix`)
Expected: `All checks passed!`

- [ ] **Step 10: Commit**

```bash
git add tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml \
        tests/bootstrap/corpora/7cc6111.tar.xz tests/bootstrap/corpora/df537ca.tar.xz \
        tests/bootstrap/test_recorded_corpora.py
git commit -m "$(cat <<'EOF'
The two archived corpora's profiles (7cc6111, df537ca) move out of their archives into plain yaml beside them, byte for byte; each archive keeps every other member in order with its name, type, mode and bytes, the commit test reads corpora/<commit>.yaml, and new tests say each profile is there, no archive holds one, and a missing one is named with nothing from the archive standing in; the recorded findings are unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: The docstring, the CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `tests/bootstrap/test_recorded_corpora.py:1-5` and `:32-33` (module docstring)
- Modify: `CHANGELOG.md:6` (under `## [Unreleased]`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-1-1/regenerate_docs.py`

**Interfaces:**
- Consumes: the files and tests from Task 1; `build_controllers().spec.docs(profile).files`, each with `.path`
  (a sequence of path parts) and `.template` (the generated text), as `tests/bootstrap/test_docs_templates.py` uses.
- Produces: nothing later tasks use.

- [ ] **Step 1: Write the failing docstring test**

Append to `tests/bootstrap/test_recorded_corpora.py`:

```python
def test_the_docstring_says_the_profile_lies_beside_the_archive_and_forbids_editing_only_the_archived_code():
    said = " ".join(__doc__.split())
    assert ("its Python files, archived (`corpora/<commit>.tar.xz`, from `git archive <commit>`), with its profile "
            "beside the archive as plain yaml (`corpora/<commit>.yaml`)") in said
    assert "Never edit the archived code, whose findings were recorded from it." in said
    assert "Never edit an archived project or its profile" not in said
```

- [ ] **Step 2: Run it to verify it fails**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_recorded_corpora.py -k docstring_says`
Expected: FAIL on the first `assert … in said`.

- [ ] **Step 3: Change the docstring**

Lines 1-5 of `tests/bootstrap/test_recorded_corpora.py` become (the rest of the paragraph, the table at lines 7-12,
the recording method and the other rules keep their wording):

```python
"""The check on xarch's own source at earlier commits, where it found many violations, gives exactly the findings the
hand-written checks gave before they became rules as data: each finding's rule, file, line, message and fix, the
violations in order of file, line and rule, then the weak findings in the order found. The source of a commit is
kept beside this test as data, its Python files, archived (`corpora/<commit>.tar.xz`, from `git archive <commit>`),
with its profile beside the archive as plain yaml (`corpora/<commit>.yaml`).
```

Lines 30-33 (the last rule) become:

```python
    - A new check, a new key or a new format of profile, which the oracle cannot know: prove it by unit and wired
      tests; or add a corpus (a new archive and its findings, or a new profile beside stress.yaml) recorded from an
      oracle extended by the same change in its own worktree. Never edit the archived code, whose findings were
      recorded from it.
"""
```

Keep every line at 120 characters or fewer (ruff's limit in `ruff.toml`).

- [ ] **Step 4: Run it to verify it passes**

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_recorded_corpora.py`
Expected: 14 passed.

- [ ] **Step 5: Add the CHANGELOG line**

In `CHANGELOG.md`, line 6 `## [Unreleased]` is followed by a blank line and then `## [0.2.0] - 2026-11-18`. Make
that part read:

```markdown
## [Unreleased]

### Changed

- The two archived corpora's profiles (`7cc6111`, `df537ca`) are plain yaml files beside their archives in
  `tests/bootstrap/corpora/`, so a change of format edits them as files; the recorded findings are unchanged.

## [0.2.0] - 2026-11-18
```

The README gets no line.

- [ ] **Step 6: Regenerate the golden docs and check they did not move**

Create `/tmp/xarch-1-1/regenerate_docs.py` (never committed):

```python
"""Write docs/{cli,web,xarch}/testing.md from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        if "/".join(file.path) == "testing.md":
            (root / "docs" / folder / "testing.md").write_text(file.template, encoding="utf-8")
            print(f"docs/{folder}/testing.md written")
```

Run:
```bash
uv run python -I /tmp/xarch-1-1/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines, and an empty `git diff`. If the diff is not empty, stop and report it with the diff:
this step must not move them (`git checkout -- docs/cli docs/web docs/xarch` restores them).

- [ ] **Step 7: Run the gates in order**

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
timeout 1200 uv run pytest -q > /tmp/xarch-1-1/final-pytest.txt 2>&1 &
echo $! > /tmp/xarch-1-1/final-pytest.pid
```

Expected: the first four pass as in the baseline (Task 1, Step 1). When the recorded PID has exited, read
`tail -5 /tmp/xarch-1-1/final-pytest.txt`: all green, with exactly 6 more passed than the baseline (2
plain-yaml, 2 guard, 1 missing-profile and 1 docstring test; the commit tests count as before). Any failure that was not in the baseline is this step's to fix.

- [ ] **Step 8: Commit**

```bash
git add tests/bootstrap/test_recorded_corpora.py CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
The recorded corpora's docstring says each commit's corpus is its Python files, archived, with its profile beside the archive as plain yaml, and that the archived code is never edited; the CHANGELOG says the two archived profiles are plain yaml beside their archives with the recorded findings unchanged; the golden docs regenerate unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

Expected from `git status --short` before the commit: only `docs/superpowers/` untracked besides the two staged files;
no `.claude/` path staged.
<!-- task-pipeline: validated -->
