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
