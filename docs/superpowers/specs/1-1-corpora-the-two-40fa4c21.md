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
