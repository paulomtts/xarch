# Instructions for coding agents

This project's architecture is a profile (the `[tool.xarch]` table of `pyproject.toml` names it), enforced by `xarch`.
The code is in `{{app}}/`. Read `docs/project/architecture.md` (where code goes, what may import what) and
`docs/project/testing.md` (how it is tested) before you change anything. Pass `--app <folder>` to `xarch` when the app
folder is not `app/`.

## Before you create or move a file

- Run `xarch where <path>`. It says which part the path belongs to, what the part is for, what it may import, which
  outside packages and names it may or may not use, and where its test goes. It works for a path that does not exist
  yet, and for a test path.
- When you do not know where a piece of code belongs, run the litmus tests in the order of `Placement order` in
  `docs/project/architecture.md`: the first one the code passes decides where it goes.

## Before you finish any change

- Run `xarch check` and `ruff check`, and fix every violation they report. Every violation says what to do in the
  `fix:` line under it, and shows a `hint:` line when this project adds advice for its rule: follow both. Fix the
  code, not the check.
- `xarch check --format json` prints the same as one JSON document, each violation with its `rule`, `file`, `line`,
  `message`, `fix` and `hint` (null when the project has none).

## How tests are written

- A test lives in the folder that mirrors what it tests, and imports only what that part may import. Its tier (unit,
  integration, and so on) follows from where it lives: see the tiers in `docs/project/testing.md`.
- A use case's test is one Given/When/Then table, one row per `Result` variant, each row with an `id`.
- A port the use case reads back is faked (`Fake<Port>` in the fakes folder); a fire-only port is a mock with a spec.
- Test code follows `docs/project/testing.md`; do not copy another shape.

## What not to do to get a green check

- Do not move code into a folder that no part covers, to escape a rule.
- Do not switch a guard off, and do not loosen the profile, its rules, libraries or forbidden names.
- Do not edit or delete the guard test (`tests/architecture/test_rules.py`).
- Do not skip a test or mark it as expected to fail.

`xarch check` reports every one of these in its `enforcement` section. If a rule seems wrong for the case at hand,
stop and say so instead of working around it.
