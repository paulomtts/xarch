# 9.5 review: the placement record measured again on the integrated branch

Card `673f42f3`, subtask of `d96ff4b1`. Release step 25 of the merged order, the part of it this card owns: the
placement record measured once more on the final branch, after every key rename and move (steps 2 to 24) and the
wrap-up docs (cards 9.1 to 9.4) have landed.

Sources, cited by short name and line (all under `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`, read only,
never edited):

- Note: `profile-form-proposal.md`.
  - Rulings (19-21): the placement order is the tree's reading order (option A), gated by a new measure of the
    placement record; `placement:` (option C) is the fallback, only if the record moves.
  - 2.5 (183-222), and in particular 216-222: the record of xarch's own profile and of the bundled profiles is
    measured again, "two runs, as the last record was". "The record moves" means a part that passed in the last
    record fails in either run.
  - 5.4, Review bullet (666-667): the record is measured again, two runs, before the step is green.
  - 6, Dodges (685-697): "skipping the new measure of the placement record" (694-695).
- R3: `0.3.0-cohesion-review-3.md`.
  - Section 3, row 23 (286): the tree form, gated by the placement record measured again (two runs); the fallback if
    a part that passed fails.
  - Section 3, row 25 (288): the wrap-up, "Everything" before it.
  - Section 3, preamble (250-253): the gates every row passes.
  - O4 (228), O5 (229): a step's README and CHANGELOG lines go under `[Unreleased]`. O8 (232): the golden docs move
    only where a note says.
- The sibling spec that measured the record at step 23: `docs/superpowers/specs/7-2-review-the-f1e50970.md`
  ("7.2"), sections "Who runs this card" and B1. This card repeats B1 of 7.2 on the final branch; it does not repeat
  B3 (the fallback), which is a change of format and out of scope here (card: "Out of scope: any change of format or
  code").

## 1. Who runs this card

**The owner's session runs the measure. An unattended agent does not.** The card says so: "Run by the owner's
session, not guessed and not run by an unattended agent". The measure sends xarch's own source and the bundled
examples to the decision-model provider TypeSafe (`https://api.typesafe.ai`, model `jev-1.14.0`). The owner approved
that for this experiment, on xarch's own repository.

An agent that reaches the measure with no `TYPESAFE_API_KEY` in its environment, or without being told by the owner
that it is the owner's session, stops and escalates. It writes nothing to `.xarch/calibration.json`, and reports no
pass or fail it did not see in a run's output (the card's dodge: "reporting a result not run"). When this spec was
written, the key was not set, the exploration refused the run, and nothing had been sent.

The key comes from the environment only. It is never printed, echoed, logged, written to a file (a spec, a plan, a
result file, a commit message) or passed on a command line. `xarch` reads it from the environment itself.

## 2. What is already true (checked when this spec was written, nothing sent)

- `.xarch/calibration.json` is byte for byte as committed in `3726591` (step 23's measure, card 7.2): top key
  `placement`, `hash` `4f0358d6…`, `model` and `answered_by` `jev-1.14.0`, all 15 parts `passed`. Its commit
  message: "all 15 parts pass (jev-1.14.0, two runs asking every example afresh); the bundled cli and web profiles
  pass 12 of 12 the same way". No record of the bundled profiles is in the repository.
- Since `3726591`, 41 commits have landed. Among them, `architecture.yaml`, `xarch/architectures/cli.yaml`,
  `web.yaml` and `xarch/architectures/presets/format/keys.yaml` changed (the part-reference rewrite of step 24:
  `may: [domain, …]` became `may: [module.domain, parts.kernel, …]`). The golden docs `docs/{cli,web,xarch}` did not
  change, so the placement order (`{{placement}}`) is the tree's reading order of 7.2's table, unchanged.
- Dry runs, sending nothing, each with a fresh `--cache "$(mktemp -d)"` and `TYPESAFE_API_KEY` unset:
  - xarch's own, from the repo root: exit 0; "19 request(s), 174,548 characters, about 43,637 tokens; 0 in the cache
    already". It names the reading alike (`domain + profile-values; logic + kernel-logic`) and the `holds` rule-out.
  - `--profile cli` from an empty scratch folder outside the repo: exit 0, 27 requests, about 48,705 tokens; the
    folder stays empty.
  - `--profile web` the same way: exit 0, 27 requests, about 48,925 tokens; the folder stays empty.

## 3. Goal

Measure the placement record again on the final branch, the way 7.2 measured it, and commit
`.xarch/calibration.json` as measured. Expected: 15 of 15 for xarch's own profile, 12 of 12 for each bundled
profile, in both runs.

- **The record holds.** Every part passes in both runs on all three profiles. Commit `.xarch/calibration.json` as
  run 2 wrote it. The step is green.
- **The record moves.** Any part fails in either run, on any profile. Stop. Report to the owner per run and per
  profile, with the outputs pasted. Do not edit litmus texts, examples, `alike`, `holds` or the profile to make a
  part pass (card: "a part that fails is reported to the owner, not fixed by editing litmus texts"; dodge: "changing
  litmus texts or examples to make a part pass"). Do not write the fallback `placement:`: that is a change of format,
  out of scope here, and the owner decides it. Whether to commit the moved record is the owner's call; by default
  nothing is committed.

## 4. Behavior

### B1. The gates, first

All green on this branch alone before anything is sent: `uv run ruff check` (never `--fix`), `uv run xarch check`,
`uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, and `uv run pytest -q` (over two
minutes: run it in the background, read the result at the end; stop it with `timeout`, never with `pkill`). A red
gate is reported and stops the card; it is not fixed here.

### B2. The dry runs

As section 2, to see what will be sent before anything is sent. Keep the `evals:` cost line of each.

- xarch's own: `uv run xarch review calibrate --eval placement --dry-run --cache "$(mktemp -d)"` from the repo root.
- Bundled: from a fresh empty folder outside the repo,
  `uv run --project <repo> xarch review calibrate --eval placement --profile cli --dry-run --cache "$(mktemp -d)"`,
  and the same with `--profile web`.

Expected: exit 0 each, "Nothing was sent (--dry-run), and nothing was recorded", 0 in the cache already, and no file
written in the scratch folders or under `.xarch/`.

### B3. Run 1 and run 2 (owner's session, key in the environment)

Each run uses a new empty cache folder (`--cache "$(mktemp -d)"`) for each profile, so every example is asked
afresh. A run that reuses another run's cache, or the committed cache `.xarch/cache/review/`, is not one of the two
runs.

- xarch's own: `uv run xarch review calibrate --eval placement --cache "$(mktemp -d)"` from the repo root. It writes
  `.xarch/calibration.json`.
- cli and web: `uv run --project <repo> xarch review calibrate --eval placement --profile <cli|web> --cache
  "$(mktemp -d)"`, each from its own fresh scratch folder outside the repo. The record each writes stays there and is
  not committed.

### B4. Reading a run

For each run and profile, read every part's verdict from the command's output (text, or `--format json`):

- A part passes when its verdict in the record is `passed`. A part whose examples disagree is said and "fails
  nothing"; it counts as a pass only when its verdict is `passed`.
- Exit 0 means every eval passed; exit 1, an eval failed its examples (the record moves). Exit 2 is a refusal and
  exit 3 an example with no answer: neither is a measure. A network failure is not a measure either. Run that
  profile again with a fresh cache; do not count it.
- `answered_by` must be `jev-1.14.0`. A different model is reported to the owner before anything is committed.

Report per run and per profile: parts passed out of the total, the names of any that failed, `answered_by`, the exit
code, and the dry run's cost line. Paste the outputs; do not summarize them from memory.

### B5. The commit (record holds)

- Only `.xarch/calibration.json`, exactly as xarch's run 2 wrote it. Its `model` and `answered_by` are `jev-1.14.0`.
  Its `hash` may stay `4f0358d6…` or change; either is what the run wrote, and it is not edited by hand.
- No other file: no code, no profile, no golden doc, no README or CHANGELOG line (`CHANGELOG.md` and `README.md`
  already say the placement order is the tree's reading order; this card adds nothing under `[Unreleased]`). Nothing
  under `.claude/`. No cache folder from B3 (they live in `mktemp -d`, outside the repo). Nothing pushed.
- The message gives the counts of both runs on all three profiles in the style of `3726591`, says it was measured on
  the integrated 0.3.0 branch, and holds no key. For example: "xarch's own placement record, measured again on the
  integrated branch: all 15 parts pass (jev-1.14.0, two runs asking every example afresh); the bundled cli and web
  profiles pass 12 of 12 the same way".
- After the commit, the gates of B1 pass again.

## 5. Tests that prove it

No code changes, so no new automated test. The proof is the measure itself plus the existing suite.

| # | What it proves | Tier | Why this tier |
|---|---|---|---|
| T1 | The branch is sound before and after the record moves in: `uv run pytest -q`, `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml` | the existing suite (all tiers) and the CLI gates | the card's gates; the record is data the suite reads, so it must stay green with the new record |
| T2 | What would be sent, and that a dry run sends and writes nothing: B2 on all three profiles | manual, owner's session | needs the real CLI against the real profiles; costs nothing and needs no key |
| T3 | The placement record holds on the final branch: B3 and B4, two runs, three profiles, 15/15 and 12/12 | manual, owner's session, live provider | the measure is of a live model's answers to the real litmus texts; a recorded or mocked answer would prove nothing, and the card forbids an unattended agent from running it |
| T4 | The committed file is the measured one: `git diff --stat HEAD~1` shows only `.xarch/calibration.json`, and its parts all read `passed` | manual check of the commit | the card's "Commit `.xarch/calibration.json` as measured" |

## 6. Out of scope

- Any change of format or code (card). In particular the fallback `placement:` of 7.2 B3 and note 5.1 line 517: if
  the record moves, the owner rules on it; this card does not write it.
- Editing litmus texts, examples, `evals.placement.alike` or `holds` to make a part pass.
- Committing records of the bundled profiles. None is in the repository, and this card adds none.
- The sibling cards of release step 25: version 0.3.0 (9.1), the README block (9.2), the CHANGELOG lead (9.3), the
  golden docs regenerated with no diff (9.4), and the re-greps and coupling audit.
- Measuring whether the model's answers move with the order of the options beyond these two runs (note, "Not
  verified", 715).

## 7. For the planner

The plan is one task with no code. Its steps: B1 gates (pytest in the background); B2 dry runs; a hard stop that
checks the owner's session and `TYPESAFE_API_KEY` is present without printing it (for example `test -n
"${TYPESAFE_API_KEY:-}"`), escalating if not; B3 run 1 then run 2; B4 report; B5 commit only on a held record, then
the gates again. There is no failing-test step, because there is no code to drive; the plan says so rather than
inventing a test. Its Review Focus should cover at least: a run that reuses a cache (not afresh); exit 3 or a
network failure counted as a measure; the bundled runs writing into the repo instead of a scratch folder; a
different `answered_by`; and the key reaching a log, a file or a command line.

---

# 9.5 The placement record measured again on the integrated branch, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure xarch's placement record, and the bundled cli and web profiles' records, again on the final 0.3.0 branch (two runs, every example asked afresh) and commit `.xarch/calibration.json` as run 2 wrote it, only if every part passes in both runs on all three profiles.

**Architecture:** One task, no code. The gates first; then dry runs that send nothing; then a hard stop unless this is the owner's session with `TYPESAFE_API_KEY` set; then run 1 and run 2 on three profiles, each with a new empty cache; then a report pasted from the outputs; then, on a held record only, one commit of `.xarch/calibration.json` and the gates again. There is no failing-test step: there is no code to drive, and the spec (section 5) says the proof is the measure itself plus the existing suite. This plan does not invent a test.

**Tech Stack:** Python 3, uv, pytest, ruff, `xarch review calibrate` against TypeSafe (`https://api.typesafe.ai`, model `jev-1.14.0`).

**Spec:** `docs/superpowers/specs/9-5-review-the-673f42f3.md` (prepended above).

## Global Constraints

- **The owner's session runs the measure. An unattended agent does not.** An agent that reaches the measure with no `TYPESAFE_API_KEY` in its environment, or without being told by the owner that it is the owner's session, stops and escalates. It writes nothing to `.xarch/calibration.json`, and reports no pass or fail it did not see in a run's output.
- The key comes from the environment only. It is never printed, echoed, logged, written to a file (a spec, a plan, a result file, a commit message) or passed on a command line. Check it only as `[ -n "${TYPESAFE_API_KEY:+set}" ] && echo set || echo unset`. Never run `env`, `printenv`, `set -x` or `bash -x` in this task.
- Each run uses a new empty cache folder (`--cache "$(mktemp -d)"`) for each profile. A run that reuses another run's cache, or the committed cache `.xarch/cache/review/`, is not one of the two runs.
- Exit 0: every eval passed. Exit 1: an eval failed its examples (the record moves). Exit 2 (refusal), exit 3 (an example with no answer) and a network failure are not a measure: run that profile again with a fresh cache, do not count it.
- A part passes only when its verdict is `passed`. `answered_by` must be `jev-1.14.0`; a different model is reported to the owner before anything is committed.
- The baseline is `3726591`: xarch's 15 parts all `passed`, `hash` `4f0358d6…`; the bundled cli and web 12 of 12 each.
- Out of scope, never done here: any change of format or code; the fallback `placement:`; editing litmus texts, examples, `evals.placement.alike` or `holds`; committing a bundled profile's record; any README or CHANGELOG line.
- The commit holds only `.xarch/calibration.json`, unedited. Nothing under `.claude/`. Nothing pushed.
- Gates, on this branch alone: `uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, `uv run pytest -q` (in the background, read at the end). A red gate is reported and stops the card; it is not fixed here.
- Stop processes only by a PID you recorded or with `timeout`; never `pkill`, `killall` or a pattern kill.

## Review Focus

1. **A run that reuses a cache.** Every calibrate command in Steps 6 and 7 carries its own `--cache "$(mktemp -d)"`, and Step 6 checks the summary's `sent` calls equal the dry run's request count (none answered from a cache), so a run that hit a kept answer is caught and not counted.
2. **Exit 3, exit 2 or a network failure counted as a measure.** The summary helper (Step 5) prints `NOT A MEASURE` for any exit other than 0 or 1, or for no placement verdicts; Steps 6 and 7 say to run that profile again with a fresh cache.
3. **The bundled runs writing into the repo.** Each bundled run is made from its own `mktemp -d` scratch folder with `uv run --project "$REPO"`; Steps 4, 6 and 7 list the scratch folders, and Step 8 checks `git status --short` shows only `.xarch/calibration.json` changed.
4. **A different `answered_by`.** The summary helper prints `answered_by`, and Step 8 checks the record file's `model` and `answered_by` are both `jev-1.14.0`; any other value stops the commit.
5. **The key reaching a log, a file or a command line.** The key is only ever tested with `${TYPESAFE_API_KEY:+set}`; the dry runs run under `env -u TYPESAFE_API_KEY`; Step 8 greps the outputs and the record for the key's value without printing it.

---

### Task 1: The measure, then the commit if the record holds (owner's session only for Steps 5 onward)

**Files:**
- Writes: `.xarch/calibration.json` (by `xarch` itself, run 1 then run 2; nothing else writes it)
- Writes outside the repo only: `/tmp/xarch-9-5/` (outputs and the summary helper), scratch and cache folders from `mktemp -d`
- Commit (record holds only): `.xarch/calibration.json`

**Interfaces:**
- Consumes: `xarch review calibrate --eval placement [--profile cli|web] [--dry-run] --cache <dir> [--format json]`. Its JSON output holds `placement` (`null`, or `{"model", "answered_by", "parts": [{"part", "verdict", ...}]}`), `passed`, `complete`, and `sent` (`{"calls", "cached", ...}`). The record file `.xarch/calibration.json` holds `placement` = `{"hash", "model", "answered_by", "parts": {<name>: {"verdict", ...}}}` (a map keyed by part name).
- Produces: a report to the owner (per run, per profile: passed/total, failed names, `answered_by`, exit code; the dry runs' cost lines), and on a held record one commit.

- [ ] **Step 1: Set up and start the gates (pytest in the background)**

```bash
REPO="$(git rev-parse --show-toplevel)"; mkdir -p /tmp/xarch-9-5
cd "$REPO" && (timeout 900 uv run pytest -q > /tmp/xarch-9-5/pytest.txt 2>&1; echo "exit $?" >> /tmp/xarch-9-5/pytest.txt) &
echo "pytest pid $!"
uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "gates exit $?"
```
Expected: `gates exit 0`. Record the pytest PID. Any non-zero: STOP and report the output; nothing is sent.

- [ ] **Step 2: Read the pytest result**

Once the background job ends (do not `sleep`-poll in a loop; wait for the job): `tail -3 /tmp/xarch-9-5/pytest.txt`
Expected: a `passed` line and `exit 0`. Anything else (failures, or `exit 124` from the timeout): STOP and report the tail; nothing is sent.

- [ ] **Step 3: Confirm the record is the baseline**

```bash
git diff --quiet 3726591 -- .xarch/calibration.json && echo "baseline unchanged" || echo "CHANGED"
python3 -c "import json; p = json.load(open('.xarch/calibration.json'))['placement']; print(p['hash'][:8], p['model'], p['answered_by'], len(p['parts']), sorted({v['verdict'] for v in p['parts'].values()}))"
```
Expected: `baseline unchanged`, then `4f0358d6 jev-1.14.0 jev-1.14.0 15 ['passed']`. Anything else: STOP and report.

- [ ] **Step 4: Dry runs of the three profiles, sending nothing**

The key is removed from these commands' environment so nothing can be sent:
```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
env -u TYPESAFE_API_KEY uv run xarch review calibrate --eval placement --dry-run --cache "$(mktemp -d)" > /tmp/xarch-9-5/dry-xarch.txt 2>&1; echo "xarch exit $?"
grep -n 'evals:\|request(s)\|Nothing was sent' /tmp/xarch-9-5/dry-xarch.txt
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && env -u TYPESAFE_API_KEY uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --dry-run --cache "$(mktemp -d)") > "/tmp/xarch-9-5/dry-$p.txt" 2>&1; echo "$p exit $?"; grep -n 'evals:\|request(s)\|Nothing was sent' "/tmp/xarch-9-5/dry-$p.txt"; echo "scratch $p: [$(ls -A "$S")]"; done
git status --short
```
Expected: `xarch exit 0`, `cli exit 0`, `web exit 0`; each output says "Nothing was sent (--dry-run), and nothing was recorded" and "0 in the cache already"; xarch's own plans 19 requests (about 43,637 tokens), cli 27 (about 48,705), web 27 (about 48,925); each `scratch <p>: []` is empty; `git status --short` shows only the untracked spec and plan docs. Keep the three `evals:` cost lines for the report. A request count far from these, or a file written: STOP and report.

- [ ] **Step 5: Hard stop: the owner's session, with the key set**

Run: `[ -n "${TYPESAFE_API_KEY:+set}" ] && echo set || echo unset`
Expected: `set`, AND the owner told you that you are the owner's session. If it prints `unset`, or you were not told so, STOP here and escalate to the owner with: "9.5 needs the owner's session with TYPESAFE_API_KEY set; the gates and dry runs are green, nothing was sent and nothing written to .xarch/calibration.json". Paste the Step 4 cost lines. Do not continue, and report no pass or fail.

Then write the summary helper (outside the repo; it reads a run's JSON output and its exit code):
```bash
cat > /tmp/xarch-9-5/summary.py <<'EOF'
import json
import sys

code = int(sys.argv[2])
try:
    document = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError) as error:
    print(f"NOT A MEASURE: exit {code}, no JSON ({error})")
    sys.exit(0)
held = document.get("placement")
if code not in (0, 1) or held is None:
    print(f"NOT A MEASURE: exit {code}, placement {'missing' if held is None else 'present'}")
    sys.exit(0)
parts = held["parts"]
failed = [f"{part['part']} ({part['verdict']})" for part in parts if part["verdict"] != "passed"]
sent = document.get("sent") or {}
print(f"{len(parts) - len(failed)} of {len(parts)} passed; failed: {', '.join(failed) or 'none'}; "
      f"answered_by: {held['answered_by']}; exit {code}; sent {sent.get('calls')} cached {sent.get('cached')}")
EOF
```

- [ ] **Step 6: Run 1, three profiles, each with a new empty cache**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-9-5/run1-xarch.json 2> /tmp/xarch-9-5/run1-xarch.err; c=$?
python3 /tmp/xarch-9-5/summary.py /tmp/xarch-9-5/run1-xarch.json "$c"
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-9-5/run1-$p.json" 2> "/tmp/xarch-9-5/run1-$p.err"; c=$?; echo "$p:"; python3 /tmp/xarch-9-5/summary.py "/tmp/xarch-9-5/run1-$p.json" "$c"; echo "scratch $p: [$(ls -A "$S")]"; done
```
Expected: `15 of 15 passed; failed: none; answered_by: jev-1.14.0; exit 0; sent 19 cached 0` for xarch; `12 of 12 passed; failed: none; answered_by: jev-1.14.0; exit 0; sent 27 cached 0` for cli and web; each scratch folder holds only the record that run wrote (it stays there, not committed). A `cached` above 0 means the run was not afresh: it does not count; run that profile again with a fresh `--cache "$(mktemp -d)"`. A `NOT A MEASURE` line (exit 2 or 3, a network failure, no JSON): read the `.err` file, run that profile again with a fresh cache, and do not count the failed attempt. Exit 1 or any part not `passed` counts: the record moved; keep going to Step 7 so both runs are reported, but Step 9 is not done.

- [ ] **Step 7: Run 2, three profiles, each with a new empty cache**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-9-5/run2-xarch.json 2> /tmp/xarch-9-5/run2-xarch.err; c=$?
python3 /tmp/xarch-9-5/summary.py /tmp/xarch-9-5/run2-xarch.json "$c"
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-9-5/run2-$p.json" 2> "/tmp/xarch-9-5/run2-$p.err"; c=$?; echo "$p:"; python3 /tmp/xarch-9-5/summary.py "/tmp/xarch-9-5/run2-$p.json" "$c"; echo "scratch $p: [$(ls -A "$S")]"; done
```
Expected: as Step 6, with the same rules for `cached`, `NOT A MEASURE` and exit 1. Run 2 of xarch's own overwrites `.xarch/calibration.json`; if xarch's run 2 is re-run, the last counted run is the one whose record is committed.

- [ ] **Step 8: Check the record, the tree and the key, then report**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
python3 -c "import json; p = json.load(open('.xarch/calibration.json'))['placement']; print(p['hash'][:8], p['model'], p['answered_by'], len(p['parts']), sorted({v['verdict'] for v in p['parts'].values()}))"
git status --short
python3 - <<'EOF'
import os, pathlib
key = os.environ.get("TYPESAFE_API_KEY", "")
files = list(pathlib.Path("/tmp/xarch-9-5").glob("*")) + [pathlib.Path(".xarch/calibration.json")]
hits = [str(f) for f in files if f.is_file() and key and key in f.read_text(encoding="utf-8", errors="replace")]
print("key found in: " + ", ".join(hits) if hits else "key in no output")
EOF
```
Expected: `<hash8> jev-1.14.0 jev-1.14.0 15 ['passed']` (the hash may be `4f0358d6` or another; it is not edited); `git status --short` shows ` M .xarch/calibration.json` (or nothing, if the run wrote identical bytes) plus the untracked spec and plan docs only; `key in no output`. A model other than `jev-1.14.0`, any other changed file, or `key found in:`: STOP and report; do not commit (if the key was found, delete that file under `/tmp/xarch-9-5/` and tell the owner which one).

Report to the owner, pasting the outputs (not from memory): the three dry-run cost lines from Step 4; for each of run 1 and run 2 and each of xarch, cli, web, the summary line (passed/total, failed names, `answered_by`, exit code); and the Step 8 record line. Then:
- **The record holds** (every summary line in Steps 6 and 7 reads all parts passed, exit 0, `answered_by: jev-1.14.0`, cached 0): go to Step 9.
- **The record moves** (any part not `passed` in either run, on any profile): STOP. Do not commit, do not edit litmus texts, examples, `alike`, `holds` or the profile, and do not write `placement:`. Restore the committed record with `git checkout -- .xarch/calibration.json` only if the owner says so; by default leave it as run 2 wrote it, uncommitted, and the owner decides.

- [ ] **Step 9: Commit the record (record holds only)**

```bash
git add .xarch/calibration.json
git commit -m "xarch's own placement record, measured again on the integrated 0.3.0 branch: all 15 parts pass (jev-1.14.0, two runs asking every example afresh); the bundled cli and web profiles pass 12 of 12 the same way" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
git diff --stat HEAD~1
```
Expected: the commit succeeds; `git diff --stat HEAD~1` lists only `.xarch/calibration.json` (the spec and plan were committed earlier by the workflow's docs commit); any other file listed: report it to the owner. If a count in the reports differs from the message text, the record moved: do not commit. If run 2 wrote bytes identical to the committed record (`git status` showed nothing in Step 8), there is nothing to commit: report "the record holds; .xarch/calibration.json unchanged" instead.

- [ ] **Step 10: The gates again**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
(timeout 900 uv run pytest -q > /tmp/xarch-9-5/pytest-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-9-5/pytest-after.txt) &
echo "pytest pid $!"
uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "gates exit $?"
```
Expected: `gates exit 0`; once the background job ends, `tail -3 /tmp/xarch-9-5/pytest-after.txt` shows `passed` and `exit 0`. A red gate after the commit: report it to the owner with the output; do not fix it here and do not push.
<!-- task-pipeline: validated -->
