# Instructions for coding agents

This project's architecture is a profile (the `[tool.xarch]` table of `pyproject.toml` names it), enforced by `xarch`.
The code is in `{{app}}/` (pass `--app <folder>` to `xarch` when it is not `app/`). Work from `xarch where <path>`, the
`fix:` line under each violation `xarch check` reports, and `Placement order` (section 7 of
`docs/project/architecture.md`, a short list); that page and `docs/project/testing.md` are reference, not required.

## Before you create or move a file

- Run `xarch where <path>`. It says which part the path belongs to, what the part is for, what it may import, which
  outside packages and names it may or may not use, and where its test goes. It works for a path that does not exist
  yet, and for a test path.
- When you do not know where code belongs, run the litmus tests in the order of `Placement order`: the first one the
  code passes decides where it goes.

## Before you finish any change

- Run `xarch check --strict` and `ruff check`, and fix every violation they report. Every violation says what to do
  in the `fix:` line under it, and shows a `hint:` line when this project adds advice for its rule: follow both. Fix
  the code, not the check.
- `--strict`, which the guard test runs, also fails on each finding under `strict:`, a `weak` one too (a method that
  only forwards, a file no test reaches). A fresh project has none: fix each by its `fix:` line as soon as it shows.
- `xarch check --format json` prints the same as one JSON document, each violation with its `rule`, `file`, `line`,
  `message`, `fix` and `hint` (null when the project has none).

## When the rules themselves must change

- Ask the maintainer first: the profile (`[tool.xarch]` names its file) is theirs to approve. To draft a change, run
  `xarch profile explain` for the whole format on one screen, then `xarch profile explain <key>` (for example
  `parts.imports.may`) for one key, and `xarch profile check` to validate the edited profile before you show it.
- A rule no key says can be written as a check of the profile's own, under `checks`. Every word it is written in is
  explained by the command: `xarch profile explain checks` for how a check reads, `xarch profile explain filters`
  (or `kinds`, `quantifiers`, `targets`, `variables`) for a category, `xarch profile explain filters.public` for one
  word, and `xarch profile explain <key> --rule` for the rules a key already expands to, written as checks to copy.
  Give it `examples` that must and must not produce a finding; `xarch profile check` runs them.

## How tests are written

- A test lives in the folder that mirrors what it tests, and imports only what that part may import. Its tier (unit,
  integration, and so on) follows from where it lives: see the tiers in `docs/project/testing.md`.
- A use case's test is one Given/When/Then table, one row per `Result` variant, each row with an `id`.
- A port the use case reads back is faked (`Fake<Port>` in the fakes folder); a fire-only port is a mock with a spec.
- Test code follows `docs/project/testing.md`; do not copy another shape.

## A second reading, advisory

`xarch review` (experimental) asks a decision model where each file you give it belongs, by the parts' litmus tests. It never
replaces `xarch check`; never edit code or docstrings to raise its numbers. Run it once the check is clean, as
`git diff --name-only <base> | xarch review --files-from - --pieces --format json`. It sends the masked text of
those files to the model's service whenever its key is set, and nothing otherwise; `--dry-run` shows what would
leave the machine. A file it reads as doubtful may hold some content that does not fit its part, or none: for such a
file, or the first piece it ranks in a file, read its part's litmus (`xarch where <path>`), then leave it or move
what does not fit, and say why in one line. With no key set it refuses (exit 2): then
skip it, or run it with `--offline` when the project commits its answer cache; `xarch review calibrate` is the
maintainer's to run, not yours.

## What not to do to get a green check

- Do not move code into a folder that no part covers, to escape a rule.
- Do not switch a guard off, and do not loosen the profile, its `imports.may`, `imports.libraries` or `uses.never` entries.
- Do not edit or delete the guard test (`tests/architecture/test_rules.py`).
- Do not skip a test or mark it as expected to fail.

`xarch check` reports every one of these in its `enforcement` section. If a rule seems wrong for the case at hand,
stop and say so instead of working around it.
