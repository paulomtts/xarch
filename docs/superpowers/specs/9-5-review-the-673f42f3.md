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
