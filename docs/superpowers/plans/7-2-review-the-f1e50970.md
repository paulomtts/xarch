# 7.2 spec: the placement record measured again on the tree's reading order

Card: f1e50970-a1d7-49d1-bcd1-f7ecf89cb10a (subtask of 49165a1c). This is the second gate of release step 23 of the
merged order (`0.3.0-cohesion-review-3.md`, section 3, row 23 at line 286). Card 7.1 (4375f8b4) built the tree form
and the first gate (the golden docs regenerated and their diff read, commit ddea9db).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-form-proposal.md` ("the note"). This
card implements 2.5 (lines 183-222: the two gates, and "the record moves" at 217-222) and the Review bullet of 5.4
(lines 666-667), with the fallback of rule 8 of 5.1 (lines 535-538) and the form line at 517. The ruling is in the
note's "Rulings already given" (lines 19-21). From `0.3.0-cohesion-review-3.md` ("review 3"): C13 (lines 199-205),
O4, O5, O8 (lines 228-232), the gates (lines 251-253) and row 23 (line 286).

## Who runs this card

**The owner's session runs the measure. An unattended agent does not.** The card says so ("Run by the owner's
session, not guessed and not run by an unattended agent"). The measure sends xarch's own source and the bundled
examples to TypeSafe. The owner approved that for this experiment, on xarch's own repository only.

An agent that reaches the measure step with no `TYPESAFE_API_KEY` in its environment, or without being told it is
the owner's session, stops and escalates. It writes nothing to `.xarch/calibration.json`. It writes no pass or fail
it did not see in a run's output. When this spec was written, the key was not set and nothing had been sent.

The key comes from the environment only. It is never printed, echoed, logged, written to a file (including a plan,
a result file or a commit message) or passed on a command line. `xarch` reads it from the environment itself.

## What is already done (not to be redone)

- `parts` is the folder tree. `Architecture.placement` (`xarch/modules/spec/domain/values.py:365`) is built from the
  tree's reading order (commits 6c13712, 75efc88, ddea9db, d2f0fd9 and d3180be on this branch).
- The placement order of each profile, before step 23 and now (the old order taken from the `parts` keys of
  `6c13712^`; the new one from the golden docs):

  | Profile | Before step 23 (6559439) | Now (tree's reading order) |
  |---|---|---|
  | xarch | domain, logic, ports, services, controller, adapters, platform, cli, reports, main, bootstrap, contract, profile-values, kernel-logic, kernel | domain, logic, ports, services, controller, adapters, contract, platform, cli, reports, main, bootstrap, profile-values, kernel, kernel-logic |
  | cli | domain, logic, ports, services, controller, adapters, platform, cli, bootstrap, contract, kernel-logic, kernel | domain, logic, ports, services, controller, adapters, contract, platform, cli, bootstrap, kernel, kernel-logic |
  | web | as cli, with `web` for `cli` | as cli, with `web` for `cli` |

- The golden docs print the new order: `docs/{cli,web,xarch}/architecture.md` (the `{{placement}}` line, at
  248, 250 and 183) and `docs/{cli,web,xarch}/testing.md` (the part lists in reading order). Their diff was read in
  ddea9db.
- The last record is `.xarch/calibration.json` as committed in 6559439. It holds xarch's own profile only. Its top
  key is `placement`, with `hash` `737aa96f…`, `model` and `answered_by` `jev-1.14.0`, and one verdict per part. All
  15 parts passed. The bundled cli and web profiles passed 12 of 12 each in the same two runs (commit message of
  6559439). Their records were not committed, and no file in the repository holds them.
- `xarch review calibrate --eval placement` asks the placement question with one option per part, in the order of
  `Architecture.placement` (`xarch/modules/review/application/logic/questions.py:19-21`). The question and its
  options go into the cache key (`xarch/modules/review/application/logic/answers.py:43-50`). A new order therefore
  misses every cached answer. `--cache <dir>` names the cache folder, and `--dry-run` sends nothing.
  Checked when this spec was written: the dry run on xarch's own profile plans 19 requests and about 43,600 tokens,
  with 0 already in a fresh cache. From an empty scratch folder, `--profile cli --dry-run` exits 0 and writes nothing
  there.

## Goal

Measure the placement record again on the tree's reading order, as 6559439 measured it. Then do one of two things:

- **The record holds.** Every part that passed in 6559439 passes in both runs, on all three profiles. Commit
  `.xarch/calibration.json` as measured. The step is green.
- **The record moves.** Some part that passed in 6559439 fails in either run, on any of the three profiles. Write
  the fallback `placement:` in the order from before step 23. Regenerate the golden docs and read the diff. Measure
  again, and commit `.xarch/calibration.json` as that measure wrote it.

## Behavior

### B1. The measure (always)

The commands, run by the owner's session with `TYPESAFE_API_KEY` in the environment:

1. All gates green on the branch first: `uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`,
   `uv run xarch profile check architecture.yaml`, and `uv run pytest -q`. Pytest takes over two minutes, so run it in
   the background and read its result at the end.
2. A dry run of each profile, to see what will be sent before anything is sent:
   - xarch's own: `uv run xarch review calibrate --eval placement --dry-run --cache "$(mktemp -d)"` from the repo root.
   - Bundled: from a fresh empty folder outside the repo,
     `uv run --project <repo> xarch review calibrate --eval placement --profile cli --dry-run --cache "$(mktemp -d)"`,
     and the same with `--profile web`.
3. **Run 1 and run 2**, each with a new empty cache folder (`--cache "$(mktemp -d)"`), so that each run asks every
   example afresh. A run that reuses the cache of another run is not one of the two runs. For each run:
   - xarch's own, from the repo root (it writes `.xarch/calibration.json`).
   - cli and web, each from its own fresh scratch folder outside the repo. The record they write stays there and is
     not committed.
4. For each run and profile, read the verdict of every part from the command's output (text, or `--format json`).
   Compare each verdict with 6559439: the 15 parts of xarch's profile, and the 12 of each bundled profile.
   - "Failed" means a part whose verdict is not `passed`.
   - A part whose examples disagree is reported and "fails nothing" (the calibrate output says so). That counts as
     a pass only when the record's verdict for the part is `passed`.
   - A run that exits 3 (an example with no answer) or fails on the network is not a measure. Run it again with a
     fresh cache. Do not count it.
5. Report per run and per profile: parts passed out of the total, the names of any that failed, the model as
   `answered_by`, and the exit code. Keep the cost line of each dry run. Paste the outputs; do not summarize them from
   memory.

### B2. The record holds

- Commit `.xarch/calibration.json` exactly as run 2 wrote it. Its `hash` differs from `737aa96f…`, since the question
  changed. `model` and `answered_by` are `jev-1.14.0`.
- The commit message gives the counts of both runs on all three profiles, in the style of 6559439. For example:
  "all 15 parts pass … the bundled cli and web profiles pass 12 of 12 the same way". It also says the order is the
  tree's reading order. It contains no key.
- Nothing else changes: no code, no profile, no golden doc. No README or CHANGELOG line is added. `CHANGELOG.md:140`
  and `README.md:111` already say the placement order is the tree's reading order.

### B3. The record moves: the fallback `placement:` (option C)

Only when B1 shows a moved record. The profile gains one top-level key, `placement`, a list of part names (note 5.1,
line 517 and rule 8; note 2.5 option C).

- `placement: [domain, logic, …]` at the top level of a profile. When it is present, `Architecture.placement` is that
  list, in that order. When it is absent, the order is the tree's reading order, as now.
- The list names every part of `parts` exactly once. Each of these is refused, with one problem per fault, addressed
  `placement`, in the release's one wording, and nothing is built:
  - a part of `parts` missing from the list ("a part missing from the list is refused", note lines 200-201). The message
    names the missing part and says the list names every part once.
  - a name in the list that is not a part. The message names it and lists the known parts, like every unknown name
    in a profile.
  - a name written twice (rule 8, line 538). The message names it.
  - a value that is not a list of names, or an empty list while `parts` has parts.
- `placement` joins the key table (`xarch/modules/spec/domain/key_table.py`) as a top-level key. So
  `xarch profile explain placement` describes it, and its text says it exists only to fix the order of the litmus
  tests. The README profile block (O4) lists it once.
- The profile writer writes `placement` back, after `parts`, when the profile it writes carries one. A profile with
  no `placement` is written without one.
- xarch's own `architecture.yaml` and the bundled `xarch/architectures/cli.yaml` and `web.yaml` gain `placement:`
  written in the "before step 23" order of the table above. Add it to all three even if only one profile moved: the
  three share one order rule. The litmus texts do not change, and they stay in their parts.
- The golden docs are regenerated through the docs path of `tests/bootstrap/test_docs_templates.py`, and their diff
  is read. Compared with the docs before step 23 (`6c13712^`), the lines printed in placement order show no diff
  (review 3 O8; note 5.4 lines 664-665). That is the card's "no diff expected". Compared with this branch, those lines move
  back. No golden doc is edited by hand.
- README and CHANGELOG lines go under `[Unreleased]` (O4, O5). The CHANGELOG says the record moved under the reading
  order, and which parts failed. It says `placement:` keeps the order from before, and the line at `CHANGELOG.md:140`
  is amended to match. The README sentence at `README.md:111` says the reading order is the order unless
  `placement` is given.
- Then B1 runs again in full (two fresh runs, three profiles). `.xarch/calibration.json` is committed as that measure
  wrote it.
- If the record still moves with today's order restored, stop and escalate to the owner. Do not change litmus texts.

## Tests (only under B3)

B1 and B2 add no code, so they add no tests. The measure is the gate. The suite and the four checks stay green.

Under B3, write each test first:

| # | Test | Tier | Why this tier |
|---|---|---|---|
| T1 | A profile with `placement` listing every part builds `Architecture.placement` in the list's order, not the tree's | unit (profile parsing, `tests/` mirror of `xarch/modules/spec/application/logic/profile_parsing.py`) | a pure function from text to a model |
| T2 | A profile with no `placement` keeps the tree's reading order | unit, same file | pins that the fallback is opt-in |
| T3 | A part missing from `placement` is refused, addressed `placement`, naming the part | unit, same file | an error path of the parser |
| T4 | A name in `placement` that is no part is refused with the list of known parts | unit, same file | the same |
| T5 | A name written twice is refused | unit, same file | the same |
| T6 | A `placement` that is not a list of names, or is empty while parts exist, is refused | unit, same file | the same |
| T7 | `placement` is in the key table, and `profile explain placement` describes it | unit (key table) and the existing explain tests | the key table is data the explain command reads |
| T8 | The writer writes `placement` back after `parts` when given, and leaves it out when absent; a round trip keeps the order | unit (writer's mirror) | the writer is pure text out |
| T9 | Xarch's own and the bundled profiles give the order from before step 23 | the existing bundled-profile tests that pin the order (updated, not loosened) | they already hold the profiles' order |
| T10 | The golden docs match after regeneration | the existing `tests/bootstrap/test_docs_templates.py` | it already holds them byte for byte |

## Out of scope

- Part references (story 8).
- Any change to a litmus text, an eval example, the question's wording or the model. Changing a litmus text to make a
  part pass, or moving the litmus texts out of the parts to win back the order, are dodges of the note (lines 696
  and 694-695).
- Option B of 2.5 (a part after the parts inside it), and any other order rule.
- Committing records for the bundled profiles. None is in the repository, and this card adds none.
- The README sentence of Q28 and the order of the CHANGELOG under one 0.3.0 lead (step 25).
- Measuring whether the model's answers depend on the order of the options in general (note 2.5, "not measured").

## Dodges that apply (from the card and note section 6)

- Skipping the measure, or calling one run two.
- Reporting a result not run, or committing a `calibration.json` that no run wrote.
- Changing litmus texts to make a part pass.
- Moving the litmus texts out of the parts to win back the order.
- Reading the docs diff loosely under B3, or editing a golden doc by hand.

## Gates, on this branch alone

`uv run pytest -q` (in the background, read at the end), `uv run xarch check`, `uv run xarch check --strict`,
`uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Project rules

No comments in xarch's code. Tests come first. Examples are simple, with absolute `app.` imports. Recorded corpora
(`tests/bootstrap/corpora/`) are edited by hand only, and only as the note says; this card does not touch them.
Python only in the reader adapter and the data files under `xarch/architectures/presets/`. `.claude/` stays out of
commits. Nothing is pushed.

---

# 7.2 The placement record measured again on the tree's reading order, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure xarch's placement record (and the bundled cli and web profiles') again on the tree's reading order, then either commit the record as measured (B2), or add the fallback top-level `placement:` key, restore the order from before step 23, and measure again (B3).

**Architecture:** Task 1 is the measure, run only by the owner's session with `TYPESAFE_API_KEY` in its environment; its result picks the branch. If the record holds, Task 2 commits `.xarch/calibration.json` and the card is done. If it moves, Tasks 3–7 add `placement` to the key table, the format's texts, the parser (`Architecture.placement` is the list when written, else the tree's reading order) and the writer, write it into the three profiles in the order from before step 23, regenerate the golden docs, update README and CHANGELOG, and measure again.

**Tech Stack:** Python 3, uv, pytest, ruff, YAML profiles, `xarch review calibrate` against TypeSafe.

**Spec:** `docs/superpowers/specs/7-2-review-the-f1e50970.md` (prepended above).

## Global Constraints

- **The owner's session runs the measure. An unattended agent does not.** An agent that reaches a measure step with no `TYPESAFE_API_KEY` in its environment, or without being told it is the owner's session, stops and escalates. It writes nothing to `.xarch/calibration.json`, and writes no pass or fail it did not see in a run's output.
- The key comes from the environment only. It is never printed, echoed, logged, written to a file (including a plan, a result file or a commit message) or passed on a command line. Check it only as `[ -n "${TYPESAFE_API_KEY:+set}" ] && echo set || echo unset`.
- Each of run 1 and run 2 uses a new empty cache folder (`--cache "$(mktemp -d)"`). A run that reuses the cache of another run is not one of the two runs. A run that exits 3 or fails on the network is not a measure: run it again with a fresh cache, do not count it.
- "Failed" means a part whose verdict is not `passed`. A part whose examples disagree counts as a pass only when its verdict is `passed`.
- The baseline is 6559439: xarch's 15 parts all `passed`; the bundled cli and web 12 of 12 each.
- No change to a litmus text, an eval example, the question's wording or the model. Litmus texts stay in their parts.
- No golden doc is edited by hand; they are regenerated (Task 5, Step 6).
- No comments in xarch's code. Tests come first. Recorded corpora (`tests/bootstrap/corpora/`) are not touched. `.claude/` stays out of commits. Nothing is pushed.
- Gates, on this branch alone: `uv run pytest -q` (in the background, read at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.
- Stop processes only by a PID you recorded or with `timeout`; never `pkill`/`killall`/pattern kills.
- The "before step 23" orders (Task 5 writes these, exactly):
  - xarch: `domain, logic, ports, services, controller, adapters, platform, cli, reports, main, bootstrap, contract, profile-values, kernel-logic, kernel`
  - cli: `domain, logic, ports, services, controller, adapters, platform, cli, bootstrap, contract, kernel-logic, kernel`
  - web: as cli, with `web` for `cli`.

## Review Focus

1. A `placement` entry that is not a string (`1`, or a map `{api: 1}`) is refused as "is not a part", never a crash on an unhashable value (Task 3, Step 1: ids `a name that is no string`, `a map as a name`).
2. A `placement` written as one comma-separated string (`placement: "api, service"`) is refused as not a list, never read letter by letter (Task 3, Step 1: id `a string, not a list`).
3. A list with several faults at once says each fault once, in list order then the missing parts in reading order (Task 3, Step 1: id `several faults at once`).
4. A part named by `name:` rather than its folder (`kernel-logic` at `kernel/logic/`) is listed by that name (Task 3, Step 1: `test_placement_lists_every_part_in_its_own_order_in_place_of_the_tree_s_reading_order`).
5. `profile new --from web` copies `placement` with the tree and the copy loads in the before-step-23 order (Task 5, Step 1: `test_profile_new.py` update).

---

## Branch point

Task 1 always runs. Then:

- **The record holds** (every part passed in both runs on all three profiles): do Task 2 and stop. Tasks 3–7 are not done.
- **The record moves** (any part not `passed` in either run, on any profile): skip Task 2; do Tasks 3, 4, 5, 6 and 7 in order.

---

### Task 1: The measure (B1), owner's session only

**Files:**
- Writes: `.xarch/calibration.json` (by `xarch` itself, run 1 then run 2; nothing else writes it)
- Writes outside the repo only: `/tmp/xarch-7-2/` (outputs), scratch folders from `mktemp -d`

**Interfaces:**
- Consumes: `xarch review calibrate --eval placement [--profile cli|web] [--dry-run] --cache <dir> [--format json]`. Its JSON holds `placement.parts[]` with `part` and `verdict`, and `placement.answered_by`.
- Produces: a report for Task 2 or Task 3–7: per run and per profile, passed/total, failed part names with verdicts, `answered_by`, exit code; the dry runs' cost lines.

- [ ] **Step 1: Confirm you may run the measure**

Run: `[ -n "${TYPESAFE_API_KEY:+set}" ] && echo set || echo unset`
Expected: `set`, and you were told you are the owner's session. If it prints `unset`, or you were not told so, STOP: escalate to the owner with "Task 1 needs the owner's session with TYPESAFE_API_KEY set; nothing was sent and nothing written to .xarch/calibration.json". Do not continue.

- [ ] **Step 2: All gates green first**

Run (pytest in the background; record its PID):
```bash
REPO="$(git rev-parse --show-toplevel)"; mkdir -p /tmp/xarch-7-2
cd "$REPO" && (timeout 900 uv run pytest -q > /tmp/xarch-7-2/pytest.txt 2>&1; echo "exit $?" >> /tmp/xarch-7-2/pytest.txt) &
echo "pytest pid $!"
uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "gates exit $?"
```
Expected: `gates exit 0`. Then, once the background job ends: `tail -3 /tmp/xarch-7-2/pytest.txt` shows `passed` and `exit 0`. Any failure: STOP and report it; nothing is sent.

- [ ] **Step 3: Dry run of each profile**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --dry-run --cache "$(mktemp -d)" | tee /tmp/xarch-7-2/dry-xarch.txt; echo "exit ${PIPESTATUS[0]}"
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --dry-run --cache "$(mktemp -d)") | tee "/tmp/xarch-7-2/dry-$p.txt"; echo "exit ${PIPESTATUS[0]}"; ls -A "$S"; done
```
Expected: each `exit 0`; xarch's plans about 19 requests and about 43,600 tokens, 0 cached; `ls -A` of each scratch folder prints nothing. Keep the cost line of each dry run for the report.

- [ ] **Step 4: Write the summary helper (outside the repo)**

```bash
cat > /tmp/xarch-7-2/summary.py <<'EOF'
import json
import sys

document = json.load(open(sys.argv[1], encoding="utf-8"))
held = document["placement"]
if held is None:
    print("no placement verdicts: not a measure")
    sys.exit(0)
parts = held["parts"]
failed = [f"{part['part']} ({part['verdict']})" for part in parts if part["verdict"] != "passed"]
print(f"{len(parts) - len(failed)} of {len(parts)} passed; failed: {', '.join(failed) or 'none'}; "
      f"answered_by: {held['answered_by']}")
EOF
```

- [ ] **Step 5: Run 1, three profiles, each with a new empty cache**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-7-2/run1-xarch.json; echo "exit $?"
python3 /tmp/xarch-7-2/summary.py /tmp/xarch-7-2/run1-xarch.json
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-7-2/run1-$p.json"; echo "$p exit $?"; python3 /tmp/xarch-7-2/summary.py "/tmp/xarch-7-2/run1-$p.json"; done
```
Expected: one summary line per profile, e.g. `15 of 15 passed; failed: none; answered_by: jev-1.14.0`. A run that exits 3, prints "no placement verdicts", or fails on the network is not a measure: run that profile again with a fresh `--cache "$(mktemp -d)"` and do not count the failed attempt.

- [ ] **Step 6: Run 2, three profiles, each with a new empty cache**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-7-2/run2-xarch.json; echo "exit $?"
python3 /tmp/xarch-7-2/summary.py /tmp/xarch-7-2/run2-xarch.json
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-7-2/run2-$p.json"; echo "$p exit $?"; python3 /tmp/xarch-7-2/summary.py "/tmp/xarch-7-2/run2-$p.json"; done
```
Expected: as Step 5. Run 2 of xarch's own overwrites `.xarch/calibration.json`; that file is what Task 2 commits.

- [ ] **Step 7: Check the record file and report**

Run:
```bash
python3 -c "import json; d = json.load(open('.xarch/calibration.json')); p = d['placement']; print(p['hash'][:8], p['model'], p['answered_by'], len(p['parts']))"
git diff --stat
```
Expected: a hash other than `737aa96f` (unless the order is the one from before step 23), `jev-1.14.0` twice, 15 parts; `git diff --stat` shows only `.xarch/calibration.json`.

Report, pasting the outputs (not from memory): the three dry-run cost lines; for each of run 1 and run 2 and each of xarch, cli, web: the summary line and the exit code. Then decide by the Branch point: every part passed in both runs on all three → Task 2. Anything else → Task 3 (and keep this report; Task 6 names the failed parts from it).

---

### Task 2: The record holds (B2): commit the record

Only when Task 1 found every part passed in both runs on all three profiles.

**Files:**
- Commit: `.xarch/calibration.json` (as run 2 wrote it, unedited)

**Interfaces:**
- Consumes: Task 1's report.
- Produces: one commit; the card is done.

- [ ] **Step 1: Confirm nothing else changed**

Run: `git status --short`
Expected: ` M .xarch/calibration.json` and the untracked spec/plan docs only. Anything else: stop and report.

- [ ] **Step 2: Commit**

Fill the counts and the model from Task 1's report (no key, no other text from the environment):
```bash
git add .xarch/calibration.json
git commit -m "xarch's own placement record, measured again on the tree's reading order: all 15 parts pass (jev-1.14.0, two runs asking every example afresh); the bundled cli and web profiles pass 12 of 12 the same way" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
If a count differs from the text above, the record moved: do not use this task; go to Task 3.

---

### Task 3: `placement` in the key table, the format's texts and the parser (B3: T1–T7)

**Files:**
- Modify: `xarch/modules/spec/domain/key_table.py:65` (add the key after `parts`)
- Modify: `xarch/architectures/presets/format/keys.yaml:161-163` (add the text after `parts`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (header docstring lines 17-25; `parse_profile` lines 233-245; new `_placement_order` before `_bare_from` at line 280)
- Modify: `xarch/modules/spec/domain/values.py:365` (the docstring line of `placement`)
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py`
- Test: `tests/bootstrap/test_profile_explain.py`
- Test (the list of profile keys these pin grows by `placement`): `tests/bootstrap/test_architecture_files.py:146` and `:240`, `tests/bootstrap/test_profile_file.py:137`, `tests/modules/spec/application/test_check.py:35` and `:88`, `tests/modules/spec/application/logic/test_never_use.py:64-65`, `tests/modules/spec/application/logic/test_retired_keys.py:55-56`, and `tests/modules/spec/application/logic/test_profile_parsing.py:401` (the second one)

**Interfaces:**
- Consumes: `parse_profile(document, source, files, presets, bundled, languages) -> Architecture`; `Architecture.placement: tuple[str, ...]`.
- Produces: top-level profile key `placement: [<part>, ...]`. `Architecture.placement` is that list when written, else `tuple(parts)` in the tree's reading order. Refusals (each prefixed by the source, e.g. `layered.yaml: `):
  - `placement: must be a list of part names, every part of parts once: write placement: [<part>, ...]`
  - `placement: <name!r> is not a part of this profile: use <known parts, sorted, joined by ", ">`
  - `placement: names <name!r> twice: name each part once`
  - `placement: <name!r> is missing: the list names every part of parts once`

- [ ] **Step 1: Write the failing parser and key-table tests**

In `tests/modules/spec/application/logic/test_profile_parsing.py`, change the expected message of `test_unknown_keys_are_refused_with_the_keys_that_exist_in_the_file` (line 43-46) to include `placement`:
```python
def test_unknown_keys_are_refused_with_the_keys_that_exist_in_the_file():
    assert problems(layered(colour=1, extra=2)) == [
        "layered.yaml: unknown keys 'colour', 'extra': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
        "hints, language, layers, name, never, parts, placement, reserved, review, testing, tiers"]
```
Then add, after `test_the_reading_order_of_the_tree_is_the_placement_order_a_part_before_the_parts_inside_it` (line 112-119, which is T2 and stays as it is):
```python
def test_placement_lists_every_part_in_its_own_order_in_place_of_the_tree_s_reading_order():
    architecture = parsed(layered(parts={
        "src/<module>/": {"contract/": {"role": "c"}, "api/": {"role": "a"}},
        "platform/": {"role": "p"},
        "kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "kl"}}},
        placement=["api", "platform", "contract", "kernel-logic", "kernel"]))
    assert architecture.placement == ("api", "platform", "contract", "kernel-logic", "kernel")
    assert tuple(architecture.parts) == ("contract", "api", "platform", "kernel", "kernel-logic")


NOT_A_LIST = "placement: must be a list of part names, every part of parts once: write placement: [<part>, ...]"
KNOWN_PARTS = "use api, service, shared, store"
EVERY_PART = ["api", "service", "store", "shared"]


@pytest.mark.parametrize("placement, expected", [
    pytest.param(["api", "service", "store"],
                 ["placement: 'shared' is missing: the list names every part of parts once"], id="a part missing"),
    pytest.param([*EVERY_PART, "cache"],
                 [f"placement: 'cache' is not a part of this profile: {KNOWN_PARTS}"], id="a name that is no part"),
    pytest.param(["api", "service", "api", "store", "shared"],
                 ["placement: names 'api' twice: name each part once"], id="a name written twice"),
    pytest.param([*EVERY_PART, 1], [f"placement: 1 is not a part of this profile: {KNOWN_PARTS}"],
                 id="a name that is no string"),
    pytest.param([*EVERY_PART, {"api": 1}], [f"placement: {{'api': 1}} is not a part of this profile: {KNOWN_PARTS}"],
                 id="a map as a name"),
    pytest.param("api, service, store, shared", [NOT_A_LIST], id="a string, not a list"),
    pytest.param({"api": 1}, [NOT_A_LIST], id="a map, not a list"),
    pytest.param([], [NOT_A_LIST], id="an empty list"),
    pytest.param(["api", "api", "cache", "store"],
                 ["placement: names 'api' twice: name each part once",
                  f"placement: 'cache' is not a part of this profile: {KNOWN_PARTS}",
                  "placement: 'service' is missing: the list names every part of parts once",
                  "placement: 'shared' is missing: the list names every part of parts once"],
                 id="several faults at once"),
])
def test_a_placement_written_wrong_is_refused_one_problem_per_fault_addressed_placement(placement, expected):
    assert problems(layered(placement=placement)) == [f"layered.yaml: {line}" for line in expected]


def test_placement_is_a_top_level_key_of_the_table_right_after_parts_neither_required_nor_enforced():
    profile = [key for key in KEYS if key.scope == "profile"]
    names = [key.name for key in profile]
    assert names[names.index("parts") + 1] == "placement"
    found = profile[names.index("placement")]
    assert (found.required, found.enforced, found.opens, found.read_by) == (False, False, "", "")
```

Every other test that pins the sorted list of profile keys in a refusal message must gain `placement` between `parts` and `reserved`, or the full suite fails once the key exists. In each place listed under **Files** above (the lines are the ones holding `parts, reserved, review, testing, tiers`; in `test_never_use.py` the string is split over lines 64-65 as `... never, parts, "` and `"reserved, review, ..."`), write `parts, placement, reserved, review`. Check none is missed: `grep -rn "parts, reserved\|parts, \"$" tests --include=*.py` prints nothing afterwards (keep every line within 140 columns, `ruff.toml`).

- [ ] **Step 2: Write the failing explain test (T7)**

In `tests/bootstrap/test_profile_explain.py`, after `test_the_example_of_hints_gives_advice_for_the_rule_may_import` (line 46-49), add:
```python
def test_placement_is_explained_as_the_order_of_the_litmus_tests_only_and_check_does_not_enforce_it():
    result = runner.invoke(app, ["profile", "explain", "placement"])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "placement"
    said = " ".join(result.output.split())
    for expected in ("accepts:", "required: no", "enforced: no, it is documentary",
                     "exists only to fix the order of the litmus tests", "placement: [documents, core]"):
        assert expected in said, expected
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py tests/bootstrap/test_profile_explain.py -q -k "placement or unknown_keys_are_refused"`
Expected: FAIL. The parser tests fail with `unknown key 'placement'` in the problems; the key-table test with `ValueError: 'placement' is not in list`; the explain test with exit code 2 (no key `placement`).

- [ ] **Step 4: Add the key to the table**

In `xarch/modules/spec/domain/key_table.py`, after line 65 (`Key(PROFILE, "parts", True, rules=("structure", "may-import"), opens=PART),`) add:
```python
    Key(PROFILE, "placement", False, False),
```

- [ ] **Step 5: Add its text to the format's data file**

In `xarch/architectures/presets/format/keys.yaml`, the `parts:` text ends with
```yaml
    example: |
      <<two>>
  never:
```
Insert between `      <<two>>` and `  never:` (so the text order matches the table order, which `test_key_catalogue.py` holds):
```yaml
  placement:
    meaning: the order the parts' litmus tests run in, when it is not the tree's reading order
    accepts: >-
      a list [<part>, ...] naming every part of `parts` once, in the order their litmus tests run and review's
      placement question offers them; left out, that order is the tree's reading order. It exists only to fix the
      order of the litmus tests: a part missing from the list, a name that is no part, a name written twice, and a
      value that is no list of names are refused when the profile loads
    example: |
      <<two>>
      placement: [documents, core]
```

- [ ] **Step 6: Read `placement` in the parser**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

(a) Insert this function immediately before `def _bare_from(value: Any) -> Any:` (line 280):
```python
_NOT_A_LIST = "placement: must be a list of part names, every part of parts once: write placement: [<part>, ...]"


def _placement_order(document: Mapping[Any, Any], parts: Mapping[str, Part], declared: set[str],
                     problems: list[str]) -> tuple[str, ...]:
    """The order the litmus tests run in: `placement` as written, which names every part once, when the profile
    writes it; else the parts in the tree's reading order. Each fault of the list is refused at `placement`."""
    if "placement" not in document:
        return tuple(parts)
    value = document["placement"]
    if not isinstance(value, list) or (not value and declared):
        problems.append(_NOT_A_LIST)
        return tuple(parts)
    known = ", ".join(sorted(declared))
    seen: list[str] = []
    twice: list[str] = []
    for name in value:
        if not isinstance(name, str) or name not in declared:
            problems.append(f"placement: {name!r} is not a part of this profile: use {known}")
        elif name not in seen:
            seen.append(name)
        elif name not in twice:
            twice.append(name)
            problems.append(f"placement: names {name!r} twice: name each part once")
    problems += [f"placement: {name!r} is missing: the list names every part of parts once" for name in parts
                 if name not in seen]
    return tuple(name for name in seen if name in parts)
```

(b) In `parse_profile`, change
```python
    problems += unlike(alike, {name: (frozenset(uses_never.get(name, ())),
                                      tuple((held.kind, held.immutable) for held in part.holds))
                               for name, part in parts.items()})
    if problems:
```
to
```python
    problems += unlike(alike, {name: (frozenset(uses_never.get(name, ())),
                                      tuple((held.kind, held.immutable) for held in part.holds))
                               for name, part in parts.items()})
    order = _placement_order(document, parts, declared, problems)
    if problems:
```
and in the `return Architecture(...)` that follows, replace `layers, tuple(parts), naming, tiers,` with `layers, order, naming, tiers,`.

(c) In the module docstring, change the end of the `parts:` paragraph
```
                               named by its folder's last step or its file's name before the first dot, or by `name`;
                               the reading order, a part before the parts inside it, is the order their litmus tests run
```
to
```
                               named by its folder's last step or its file's name before the first dot, or by `name`;
                               the reading order, a part before the parts inside it, is the order their litmus tests run
                               unless `placement` gives another
```
and after the line `        package_only: true     the part is imported only as a package from outside it` add
```
    placement: [<part>, ...]   optional; every part of parts once: the order their litmus tests run in place of the
                               reading order, kept only to fix that order
```

- [ ] **Step 7: Say it on the Architecture**

In `xarch/modules/spec/domain/values.py:365`, change
```
    placement: every part once: the order the litmus tests run in
```
to
```
    placement: every part once: the order the litmus tests run in, the profile's `placement` when it writes one, else
        the reading order of parts
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py tests/bootstrap/test_profile_explain.py tests/modules/spec/application/logic/test_key_catalogue.py tests/bootstrap/test_architecture_files.py tests/bootstrap/test_profile_file.py tests/modules/spec/application/test_check.py tests/modules/spec/application/logic/test_never_use.py tests/modules/spec/application/logic/test_retired_keys.py -q`
Expected: PASS (all). `test_with_no_key_the_whole_format_is_one_screen...` still passes (the overview grows from 90 to 91 lines, under its 100).

- [ ] **Step 9: Gates and commit**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "exit $?"` → `exit 0`. Then `timeout 900 uv run pytest -q` in the background (record its PID) and read the result: all pass.
```bash
git add xarch/modules/spec/domain/key_table.py xarch/architectures/presets/format/keys.yaml xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/domain/values.py tests/modules/spec/application/logic/test_profile_parsing.py tests/bootstrap/test_profile_explain.py
git commit -m "A profile may write placement, every part once, to fix the order its litmus tests run in place of the tree's reading order; a part missing, a name that is no part, a name twice and a value that is no list of names are refused at placement" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: The writer writes `placement` after `parts` (B3: T8)

**Files:**
- Modify: `xarch/modules/spec/adapters/yaml_profile_format.py:43-46` (`written`) and a new `_after_parts` after `_ordered` (line 124-126)
- Test: `tests/modules/spec/adapters/test_yaml_profile_format.py`

**Interfaces:**
- Consumes: `YamlProfileFormat.written(document: dict[str, Any]) -> bytes`.
- Produces: the same signature; a document carrying `placement` is written with `placement` right after `parts`; one without it is written without it.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/adapters/test_yaml_profile_format.py`, after `test_the_rest_of_the_document_is_written_as_before` (line 151-153), add:
```python
def test_placement_is_written_right_after_parts_when_given_and_a_round_trip_keeps_its_order():
    document = {"name": "x", "placement": ["b", "a"], "parts": {"a/": {"role": "r"}, "b/": {"role": "s"}},
                "layers": {"l": ["a"]}}
    text = FORMAT.written(document).decode()
    assert "\nplacement: [b, a]\n" in text
    read = yaml.safe_load(text)
    assert list(read) == ["name", "parts", "placement", "layers"]
    assert read["placement"] == ["b", "a"]


def test_a_profile_with_no_placement_is_written_without_one():
    assert "placement" not in FORMAT.written({"name": "x", "parts": {"a/": {"role": "r"}}}).decode()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `timeout 300 uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py -q -k placement`
Expected: FAIL on `list(read) == [...]`: got `['name', 'placement', 'parts', 'layers']`. (The "without one" test passes already; it pins that nothing is added.)

- [ ] **Step 3: Implement**

In `xarch/modules/spec/adapters/yaml_profile_format.py`, change `written` to:
```python
    def written(self, document: dict[str, Any]) -> bytes:
        parts = document.get("parts")
        shown = {**document, "parts": _tree(parts)} if isinstance(parts, Mapping) else document
        return self._writer.dump(_after_parts(shown)).encode("utf-8")
```
and add after `_ordered`:
```python
def _after_parts(document: dict[str, Any]) -> dict[str, Any]:
    """The document with its `placement`, when it has one and `parts` too, right after `parts`, the order it fixes
    read beside the tree it orders."""
    if "placement" not in document or "parts" not in document:
        return document
    shown: dict[str, Any] = {}
    for key, value in document.items():
        if key != "placement":
            shown[key] = value
        if key == "parts":
            shown["placement"] = document["placement"]
    return shown
```
Also add to the module docstring's first sentence, after "its `parts` as the folder tree in canonical form (see _tree)", the words ", and its `placement`, when it has one, right after `parts`".

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py -q`
Expected: PASS (all).

- [ ] **Step 5: Gates and commit**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "exit $?"` → `exit 0`.
```bash
git add xarch/modules/spec/adapters/yaml_profile_format.py tests/modules/spec/adapters/test_yaml_profile_format.py
git commit -m "The profile writer writes placement right after parts when the profile carries one, and none when it does not" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The three profiles write the order from before step 23; the golden docs regenerate (B3: T9, T10)

**Files:**
- Modify: `architecture.yaml` (before `never:`, line 261)
- Modify: `xarch/architectures/cli.yaml` (before `never:`, line 206)
- Modify: `xarch/architectures/web.yaml` (before `never:`, line 208)
- Modify (regenerated, never by hand): `docs/cli/architecture.md`, `docs/web/architecture.md`, `docs/xarch/architecture.md` (and any other doc the regeneration changes)
- Test: `tests/bootstrap/test_bundled_architectures.py:94-106`
- Test: `tests/bootstrap/test_profile_new.py:99`

**Interfaces:**
- Consumes: Task 3's `placement` key; `load_architecture(source) -> Architecture`; `build_controllers().spec.docs(profile).files`, each with `path: tuple[str, ...]` and `template: str`.
- Produces: the three profiles' `Architecture.placement` in the before-step-23 order; `Architecture.parts` keeps the tree's reading order.

- [ ] **Step 1: Write the failing tests**

In `tests/bootstrap/test_bundled_architectures.py`, replace lines 94-106 with:
```python
WEB_TREE = ("domain", "logic", "ports", "services", "controller", "adapters", "contract", "platform", "web",
            "bootstrap", "kernel", "kernel-logic")
WEB_ORDER = ("domain", "logic", "ports", "services", "controller", "adapters", "platform", "web", "bootstrap",
             "contract", "kernel-logic", "kernel")
OWN_TREE = ("domain", "logic", "ports", "services", "controller", "adapters", "contract", "platform", "cli", "reports",
            "main", "bootstrap", "profile-values", "kernel", "kernel-logic")
OWN_ORDER = ("domain", "logic", "ports", "services", "controller", "adapters", "platform", "cli", "reports", "main",
             "bootstrap", "contract", "profile-values", "kernel-logic", "kernel")


def _cli(order: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("cli" if part == "web" else part for part in order)


@pytest.mark.parametrize("source, order, tree", [
    pytest.param("web", WEB_ORDER, WEB_TREE, id="web"),
    pytest.param("cli", _cli(WEB_ORDER), _cli(WEB_TREE), id="cli"),
    pytest.param(OWN, OWN_ORDER, OWN_TREE, id="xarch"),
])
def test_the_placement_of_each_profile_is_the_order_from_before_the_tree_and_its_parts_keep_the_reading_order(
        source, order, tree):
    architecture = load_architecture(source)
    assert architecture.placement == order
    assert tuple(architecture.parts) == tree
```
In `tests/bootstrap/test_profile_new.py:99`, change
```python
    assert load_architecture(copy).placement[-2:] == ("kernel", "kernel-logic")
```
to
```python
    assert load_architecture(copy).placement[-3:] == ("contract", "kernel-logic", "kernel")
    assert yaml.safe_load(copy.read_text(encoding="utf-8"))["placement"][-3:] == ["contract", "kernel-logic", "kernel"]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py -q -k "placement or copy_of_web"`
Expected: FAIL: `architecture.placement` is the reading order (`... "adapters", "contract", "platform", ...`), and the copy has no `placement` key (`KeyError: 'placement'`).

- [ ] **Step 3: Write `placement` into the three profiles**

In each file, insert the line(s) below directly before the line `never:`, with one empty line before `never:` as the files already have (so: `      tests: unit\n\nplacement: ...\n\nnever:`).

`xarch/architectures/cli.yaml`:
```yaml
placement: [domain, logic, ports, services, controller, adapters, platform, cli, bootstrap, contract, kernel-logic, kernel]
```
`xarch/architectures/web.yaml`:
```yaml
placement: [domain, logic, ports, services, controller, adapters, platform, web, bootstrap, contract, kernel-logic, kernel]
```
`architecture.yaml`:
```yaml
placement: [domain, logic, ports, services, controller, adapters, platform, cli, reports, main, bootstrap, contract,
  profile-values, kernel-logic, kernel]
```
No litmus text and nothing under `parts` changes.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py tests/modules/spec/adapters/test_yaml_profile_format.py -q`
Expected: PASS.

- [ ] **Step 5: See the golden docs fail as expected**

Run: `timeout 300 uv run pytest tests/bootstrap/test_docs_templates.py -q`
Expected: FAIL only in `test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte[cli/architecture.md]`, `[web/architecture.md]` and `test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch` (the `{{placement}}` line).

- [ ] **Step 6: Regenerate the golden docs through the docs path**

Write the script outside the repo and run it from the repo root:
```bash
cat > /tmp/xarch-7-2/regenerate_docs.py <<'EOF'
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

spec = build_controllers().spec
for profile, folder in (("cli", "docs/cli"), ("web", "docs/web"), (str(Path("architecture.yaml").resolve()), "docs/xarch")):
    for file in spec.docs(profile).files:
        Path(folder, *file.path).write_text(file.template, encoding="utf-8")
EOF
uv run python /tmp/xarch-7-2/regenerate_docs.py && git diff --stat docs/
```
Expected: `docs/cli/architecture.md`, `docs/web/architecture.md`, `docs/xarch/architecture.md`, 1 insertion and 1 deletion each; no other file.

- [ ] **Step 7: Read the diff closely**

Run:
```bash
git diff docs/
for p in cli web xarch; do diff <(git show 6c13712^:docs/$p/architecture.md | grep '^`domain` →') <(grep '^`domain` →' docs/$p/architecture.md) && echo "$p: placement line as before step 23"; done
```
Expected: the only changed line in each doc is the `{{placement}}` line, now reading `` `domain` → `logic` → `ports` → `services` → `controller` → `adapters` → `platform` → ... → `contract` → ... → `kernel-logic` → `kernel` ``, and the three `diff`s print nothing and each echo prints. The rules table and `testing.md` keep the tree's reading order (they follow `parts`, not `placement`), so they do not move. If any other line moved, stop and report it with the diff; do not edit a doc by hand.

- [ ] **Step 8: Run the docs tests and the full suite**

Run: `timeout 300 uv run pytest tests/bootstrap/test_docs_templates.py -q` → PASS. Then the gates: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "exit $?"` → `exit 0`; and `timeout 900 uv run pytest -q` in the background (record its PID), read at the end → all pass. If a test other than those updated in Step 1 fails because it pins the placement order of a bundled profile, stop and report it with its output.

- [ ] **Step 9: Commit**

```bash
git add architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml docs/cli/architecture.md docs/web/architecture.md docs/xarch/architecture.md tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py
git commit -m "xarch's own and the bundled profiles write placement in the order from before the tree, contract after bootstrap and kernel-logic before kernel; the golden docs regenerate with only the placement line moved back" -m "Regenerated through the docs path of tests/bootstrap/test_docs_templates.py and the diff read: the placement line of docs/{cli,web,xarch}/architecture.md matches 6c13712^ again; nothing else moved; no golden doc was edited by hand." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: README and CHANGELOG (B3)

**Files:**
- Modify: `README.md:100-102` (the sentence on the reading order) and `README.md:114-117` (the profile block)
- Modify: `CHANGELOG.md:8` (a new `### Added` entry) and `CHANGELOG.md:140-142` (the placement sentence)

**Interfaces:**
- Consumes: Task 1's report: the names of the parts that failed, per profile.
- Produces: docs only.

- [ ] **Step 1: README sentence**

In `README.md`, replace
```
A profile is one YAML file that states each fact once, on the thing it is about. Its `parts` are the app's folder tree,
and the tree's reading order (top to bottom, a part before the parts inside it) is the order their litmus tests run,
which is also the order of the generated docs' rules table. The shape (`*` is required; everything else is optional,
and a key left out means off):
```
with
```
A profile is one YAML file that states each fact once, on the thing it is about. Its `parts` are the app's folder tree,
and the tree's reading order (top to bottom, a part before the parts inside it) is the order of the generated docs'
rules table and, unless `placement` lists every part in another order, the order their litmus tests run. The shape
(`*` is required; everything else is optional, and a key left out means off):
```

- [ ] **Step 2: README profile block (O4), once**

In the code block, after the `parts*:` entry, which ends with the line
```
                                      records: {names, immutable}, exceptions: {names}}}}
```
insert
```
placement: [<part>, ...]                                every part once: the litmus order, in place of the reading order
```
Run: `grep -c "^placement:" README.md` → `1`.

- [ ] **Step 3: CHANGELOG**

Under `## [Unreleased]` → `### Added` (line 8), add as the first entry, with the parts named from Task 1's report (each as `` `name` `` and the profile it failed in; write the actual names, e.g. "`contract` in xarch's own and `kernel` in cli"):
```
- `placement`, a top-level key of a profile: every part of `parts` once, the order their litmus tests run and review's
  placement question offers them, in place of the tree's reading order. Measured on the reading order, the placement
  record moved (<the failing parts and profiles from Task 1's report>), so xarch's own profile and the bundled `cli`
  and `web` write `placement:` in the order from before the tree; a part missing from the list, a name that is no
  part, a name written twice and a value that is no list of names are refused at `placement`. It exists only to fix
  the order of the litmus tests.
```
Then amend the `### Changed` sentence at lines 140-142, replacing
```
  note as its value. The placement order is the tree's reading order, a part before the parts inside it: in the
  bundled profiles `contract` moves up to follow `adapters`, and `kernel` now comes before `kernel-logic`, so review's
  placement question offers its options in that order. `profile new` copies the tree, and the profile writer writes
  it, single chains of plain folders joined.
```
with
```
  note as its value. The placement order is the tree's reading order, a part before the parts inside it, unless the
  profile writes `placement`; the bundled profiles write it, so review's placement question offers its options in the
  order it had before. `profile new` copies the tree and `placement`, and the profile writer writes the tree, single
  chains of plain folders joined, with `placement` right after it.
```

- [ ] **Step 4: Gates and commit**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "exit $?"` → `exit 0`; `timeout 300 uv run pytest tests/architecture/test_readme.py -q` → PASS.
```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say placement fixes the order of the litmus tests in place of the reading order, which the bundled profiles write since the record moved under the reading order" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: The measure again with the order restored (B3), owner's session only

**Files:**
- Writes: `.xarch/calibration.json` (by `xarch`, run 1 then run 2)
- Commit: `.xarch/calibration.json`

**Interfaces:**
- Consumes: Tasks 3–6 committed.
- Produces: the committed record, or an escalation.

- [ ] **Step 1: Confirm you may run the measure**

Run: `[ -n "${TYPESAFE_API_KEY:+set}" ] && echo set || echo unset`
Expected: `set`, and you are the owner's session. Otherwise STOP and escalate; write nothing to `.xarch/calibration.json`.

- [ ] **Step 2: Gates green**

```bash
REPO="$(git rev-parse --show-toplevel)"; mkdir -p /tmp/xarch-7-2b
cd "$REPO" && (timeout 900 uv run pytest -q > /tmp/xarch-7-2b/pytest.txt 2>&1; echo "exit $?" >> /tmp/xarch-7-2b/pytest.txt) &
echo "pytest pid $!"
uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml; echo "gates exit $?"
```
Expected: `gates exit 0`, and `tail -3 /tmp/xarch-7-2b/pytest.txt` shows `passed` and `exit 0`. Otherwise stop.

- [ ] **Step 3: Dry runs**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --dry-run --cache "$(mktemp -d)" | tee /tmp/xarch-7-2b/dry-xarch.txt; echo "exit ${PIPESTATUS[0]}"
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --dry-run --cache "$(mktemp -d)") | tee "/tmp/xarch-7-2b/dry-$p.txt"; echo "exit ${PIPESTATUS[0]}"; ls -A "$S"; done
```
Expected: each `exit 0`, 0 cached, scratch folders empty. Keep the cost lines.

- [ ] **Step 4: Run 1**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-7-2b/run1-xarch.json; echo "exit $?"
python3 /tmp/xarch-7-2/summary.py /tmp/xarch-7-2b/run1-xarch.json
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-7-2b/run1-$p.json"; echo "$p exit $?"; python3 /tmp/xarch-7-2/summary.py "/tmp/xarch-7-2b/run1-$p.json"; done
```
(`/tmp/xarch-7-2/summary.py` is the helper written in Task 1, Step 4; if it is gone, write it again exactly as there.) An exit 3 or a network failure is not a measure: rerun that profile with a fresh cache.

- [ ] **Step 5: Run 2**

```bash
REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
uv run xarch review calibrate --eval placement --cache "$(mktemp -d)" --format json > /tmp/xarch-7-2b/run2-xarch.json; echo "exit $?"
python3 /tmp/xarch-7-2/summary.py /tmp/xarch-7-2b/run2-xarch.json
for p in cli web; do S="$(mktemp -d)"; (cd "$S" && uv run --project "$REPO" xarch review calibrate --eval placement --profile "$p" --cache "$(mktemp -d)" --format json) > "/tmp/xarch-7-2b/run2-$p.json"; echo "$p exit $?"; python3 /tmp/xarch-7-2/summary.py "/tmp/xarch-7-2b/run2-$p.json"; done
```

- [ ] **Step 6: Decide**

If any part that passed in 6559439 is not `passed` in either run on any profile: STOP and escalate to the owner with the pasted summaries. Do not change litmus texts; do not commit the record.

Otherwise run `python3 -c "import json; p = json.load(open('.xarch/calibration.json'))['placement']; print(p['hash'][:8], p['model'], p['answered_by'], len(p['parts']))"` and `git status --short` (only `.xarch/calibration.json` modified, besides untracked docs), then commit, with the counts from the summaries:
```bash
git add .xarch/calibration.json
git commit -m "xarch's own placement record, measured again with placement in the order from before the tree: all 15 parts pass (jev-1.14.0, two runs asking every example afresh); the bundled cli and web profiles pass 12 of 12 the same way" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Report the pasted summaries, exit codes and dry-run cost lines of both runs on all three profiles.
<!-- task-pipeline: validated -->
