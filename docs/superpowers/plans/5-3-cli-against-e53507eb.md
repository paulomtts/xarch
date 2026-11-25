# 5.3 `--against` compares a profile with another for one run — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `xarch check` and `xarch profile check` take `--against NAME|FILE`, which for that run compares the
profile in force (custom or bundled) with the profile it names, says so in text and JSON, refuses a value that does
not load (exit 2) and refuses `--strict` with it (exit 2), while violations, exit codes and `--strict`'s findings
stay what they are without it.

**Architecture:** The choice of the profile compared lives in spec: `origin_of` (looseness logic) gains `against`,
which compares with the one profile `others` holds under that name, bundled or custom in force, `chosen_by
"against"`, no `higher`, and carries the profile's own `based_on` on a new `Origin.based_on`; `ArchitectureService
.origin(location, against)` loads that profile and turns a load failure into one `AgainstUnloaded` refusal. The
value travels `CheckProfile.against` (spec and rules contracts), `Profiles.reviewed(..., against)`, and the CLI
calls `spec.origin(chosen, against)` for `check`; `--strict` never reads it (`Profiles.standing` is unchanged), and
`AppCheckService.check` refuses `strict` with `against` before it looks at anything. The CLI reports learn the word
`--against` and compare a bundled profile when it is given.

**Tech Stack:** Python 3.13, typer (CLI), pytest (`uv run pytest`), ruff (`uv run ruff check`), xarch's own
`uv run xarch check` on itself.

**Spec:** `docs/superpowers/specs/5-3-cli-against-e53507eb.md` (inlined below, under "The spec").

## Global Constraints

- No comments in xarch's code (`xarch/**`): say it in a docstring or a name (`no-comments` guard, `tests/architecture/test_self_check.py`).
- Tests are written first, and seen to fail, before the code that makes them pass.
- Examples simple, with absolute `app.` imports.
- Recorded corpora untouched (`tests/bootstrap/corpora`, `tests/bootstrap/test_recorded_corpora.py`, `docs/examples`).
- Python only in the reader adapter and the preset data files.
- `.claude/` stays out of commits; nothing is pushed.
- Never `uv run ruff check --fix`; fix lint by hand.
- README and CHANGELOG lines under `## [Unreleased]`, `### Added`; the 5.1 and 5.2 bullets stay as they are.
- Golden docs `docs/{cli,web,xarch}/**` are regenerated and their diff read, never edited by hand; expected unchanged.
- There is no `[tool.xarch] against` setting; `--against` is never read from `pyproject.toml`.
- `keys.yaml`, `anchor` in the JSON, and the parenthesis of the `--strict` refusal are 5.4's: not touched.
- Without `--against` every line of output, text and JSON, is byte for byte what it is today.
- Commit messages: one long descriptive sentence, no prefix, then a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Exact texts (verbatim from the spec):
  - load refusal: `--against does not load: <every problem of the loader, joined by "; ">`
  - strict refusal: `--against shows a comparison and --strict fails on one: run \`check --strict\` without --against, and it judges the profile against its baseline`
  - the word for `chosen_by == "against"` in text: `--against`
  - `profile check` heading: `(custom; against web, given with --against; based_on: cli)`, `(custom; against web, given with --against)`, `(bundled; against web, given with --against)`
  - `check` profile line: `(custom; compared with web, --against; match 73%)`, `(bundled; compared with web, --against; match 89%)`
  - help: `The profile it is compared with, for this run: the name of a bundled profile, or a path to a profile file (.yaml or .json) read from the working folder. Default: the one the profile's based_on names, else the bundled profile of highest match; a bundled profile is its own. Refused with --strict.`

## Review Focus

1. **An `--against` profile with several loader problems.** A person expects one readable line, every problem
   joined by `"; "`, never a reason broken over lines. Pinned in Task 2
   (`test_against_a_profile_with_several_problems_is_refused_with_all_of_them_on_one_line`).
2. **`profile check` of a target that does not load, given a bad `--against` too.** A person expects the target's own
   problems (exit 1), not an `--against` refusal: the target is loaded first. Pinned in Task 1
   (`test_the_profile_in_force_is_loaded_before_against_is_read`), Task 2
   (`test_against_is_not_read_when_the_profile_checked_does_not_load`) and Task 6
   (`test_a_profile_that_does_not_load_is_reported_as_it_is_and_against_is_not_read`).
3. **`check --against` naming a profile that does not load, without `--strict`.** A person expects exit 2 and the
   load refusal, in text and JSON, not a report. Pinned in Task 6
   (`test_check_against_a_profile_that_does_not_load_is_refused` and the JSON refusal table).
4. **`--strict --against` on a missing app folder.** A person expects the `--strict` refusal, not "not a
   directory": the refusal comes before anything is looked at. Pinned in Task 4 (table rows) and Task 6
   (`test_strict_with_against_is_refused_before_anything_is_checked`).
5. **`--against` naming the profile in force itself, or a relative path.** A person expects 100% and nothing
   looser, and a path read from the working folder like `--profile`'s. Pinned in Task 1
   (`test_against_the_profile_in_force_itself_matches_it_whole_and_finds_nothing_looser`) and Task 6
   (`test_against_a_path_is_read_from_the_working_folder`).

---

## The spec

# 5.3: `--against` compares a profile with another for one run

Card `e53507eb`, subtask of `3c8f968f`, release step 16 of the merged order (`0.3.0-cohesion-review-3.md`, section 3,
row 16, line 279), after 5.1 (`f004b3d1`, pairing and the match) and 5.2 (`aabea037`, the looser lines), both on this
branch. Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-comparison-design.md`, cited below
as "note line L"; the third cohesion review, in the same folder, as "review 3 line L".

This step builds note §1 (the flag, lines 85-141), §5 items 3 (the `against` half only, lines 328-332), 4 (333-334),
5 (passing `against` on and the `--strict` refusal, 335-338), 6 (339-341), 8 (343-345), 10 (the README options and
the `profile check` paragraph only, 356-358), 12 (the `Added --against` bullet only, 362), and the service and CLI
tests of §5 (lines 373-374 for `against`, 378-379).

## 1. What changes for a person

`xarch check` and `xarch profile check` take `--against NAME|FILE`. For that run, the profile in force is compared
with the profile `--against` names instead of the one its `based_on` names or the bundled one of highest match (note
lines 96-98). Everything the comparison prints (the heading words, the `match:` line and its `low:` reason, the
parts and tiers only one side has, the looser lines, the JSON `compared_with`) is about that profile. A bundled
profile in force, which is its own baseline without the flag, is compared too (note line 98).

Nothing else changes: the violations, the exit code of `check` without `--strict`, and everything `--strict` fails on
are what they are without the flag. `--strict` with `--against` is refused (note lines 100-109; dodge line 418).

## 2. Behavior (normative)

### 2.1 What `--against` accepts

What `--profile` accepts (note lines 91-94): a bare name is a bundled profile; a path to a `.yaml` or `.json` file is
a profile file, read from the working folder. It is loaded as any profile is (`ArchitectureService.load`).

A value that does not load refuses the run, exit 2 (note lines 92-94). The reason is exactly

    --against does not load: <every problem of the loader, joined by "; ">

where each problem is the loader's own text, which already starts with the location as given. `InvalidArchitecture.reason`
joins the problems with newlines, so the spec service catches `InvalidArchitecture` for the `--against` load and joins
its `problems` with "; " itself (a plain `DomainError` handler would give the newline form). So:

- `--against nosuch` → `--against does not load: nosuch: no bundled architecture 'nosuch': use one of cli, web, or a
  path to a .yaml or .json file`
- `--against bad.yaml`, a file holding `name: x` → `--against does not load: bad.yaml: missing \`parts\``
- `--against gone.yaml`, no such file → `--against does not load: gone.yaml: cannot read the file: No such file or
  directory`

In text the reason goes to stderr as every refusal does (`error: ...`); with `--format json`, as the JSON error
document every refusal prints. In `profile check`, the profile checked is loaded first: a target that does not load
is reported as today (exit 1, its problems) and `--against` is not read.

There is no `[tool.xarch] against` setting (note line 39, review-2 Q27; card's dodges). `--against` is never read
from `pyproject.toml`.

### 2.2 Which profile is compared, and why

| Profile in force | `--against` | Compared with | `chosen_by` |
|---|---|---|---|
| custom, any `based_on` | given | the `--against` profile | `against` (new constant `AGAINST` beside `BASED_ON`, `CLOSEST`) |
| bundled | given | the `--against` profile | `against` |
| custom | not given | as today (`based_on`, else highest match) | `based_on` / `closest` |
| bundled | not given | itself (its own baseline), as today | `None` |

With `--against`:

- The comparison is computed exactly as 5.1 and 5.2 compute it against `based_on`'s profile: pairing, `match`, `low`
  (below 75%, or no part paired), `counts`, `only_here`, `only_there`, `elsewhere`, `looser`.
- It runs even when no part pairs (note lines 182-184): the match is low and the reason says "no part in common".
- `higher` is `None`: only the `--against` profile is a candidate, so no other bundled profile is said to match
  higher.
- `Origin.bundled` keeps saying whether the profile in force is bundled. `guards_off` is unchanged (the profile's own
  guards off). `baseline_off` is the guards off in both, as for a custom profile (this field feeds only `--strict`,
  which never runs with `--against`).
- `--against` naming the profile in force itself is allowed: it matches at 100% and lists nothing looser.

### 2.3 Text output

The word for `chosen_by == "against"` in text is `--against` (note lines 116, 125).

`profile check` heading, line 1:

- custom with `based_on`: `checking architecture.yaml (custom; against web, given with --against; based_on: cli)`
  (note line 124)
- custom without `based_on`: `checking mine.yaml (custom; against web, given with --against)`
- bundled: `checking cli (bundled; against web, given with --against)`

The `match:` line and what follows it are 5.1's, with `(--against)` as the reason (note lines 125-127). For
`profile check architecture.yaml --against web`, on this branch (computed against the 0.3.0 profiles, 2026-11-23):

    checking architecture.yaml (custom; against web, given with --against; based_on: cli)
      loads: ok
      files: all 23 it points to are present
      examples: ok: they import only what their part may
      match: 73% with web (--against): 11 of 16 parts, 67 of 96 part keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them
        only here: parts cli, main, profile-values, reports; tier wired. only in web: part web; tier rendering
        low: 27% of what check reads under either profile has nothing to compare with in the other, so the list below says little about how check would do under web
      compared: looser than web (...)

(the `compared:` lines are whatever `_looser` finds against web; exit 0, as a valid profile is.)

`check`'s enforcement section, `profile:` line (note lines 129-135):

- custom: `profile:     architecture.yaml (custom; compared with web, --against; match 73%)`, then, when low, the
  `match:` line 5.1 prints today: `match:  73%, low: <the same reason>`
- bundled: `profile:     cli (bundled; compared with web, --against; match 89%)`

Without `--against` every line is byte for byte what it is today.

### 2.4 JSON

`profile check`'s `compared_with` and `check`'s `enforcement.profile.compared_with` hold the same object they hold
today, with `"chosen_by": "against"` and `"higher": null` (note lines 137-141). For a bundled profile with
`--against`, `compared_with` is that object (today it is `null` for a bundled profile), and `bundled` stays `true`.
`anchor` is not added here (it is 5.4's, note lines 307-308).

`check --format json --against X`: `ok`, `violations` and `enforcement.strict_failures` are equal to those of the
same run without `--against`.

### 2.5 `--strict` with `--against`

`xarch check --strict --against X` is refused, exit 2, before any check runs (note lines 100-109, default ruling line
23-24; dodge line 418). The refusal lives in the rules service (`AppCheckService.check`), so it is testable without
the CLI (note line 337-338), and it fires before the app or tests folder is looked at: a `CheckApp` with `strict=True`,
`against="web"` and an app folder that does not exist comes back as `CheckRefused`, not `NotADirectory`. The reason
is exactly

    --against shows a comparison and --strict fails on one: run `check --strict` without --against, and it judges the profile against its baseline

The note's parenthesis naming the baseline (`(based_on: ../team.yaml, resting on cli)`, line 103) names the anchor of
§4.1, which is 5.4's; this step prints the sentence without it, and 5.4 appends it.

`profile check` has no `--strict`, so there is nothing to refuse there.

### 2.6 `--strict` never reads `--against`

What `--strict` fails on rests on the baseline only: `check`'s source check asks for the profile's standing
(`Profiles.standing`, `rules/application/services/source_check.py:133`) without `against`, so `baseline_off` and `unplaced` are those of
`based_on` / closest / the bundled profile itself. This is a deliberate narrowing of note item 5 (line 335-337,
which lists `source_check.py:129` among the places that pass `against` on): passing it there would let `--against`
change `enforcement.strict_failures` (§2.4), the dodge of line 418, and the refusal of §2.5 already keeps it from
mattering to an exit code. Only the comparison `check` prints (`cli/commands/check.py` `_origin`) reads `against`.

### 2.7 Help and docstrings

The `--against` help (one shared `Annotated` in `cli/terminal.py`, beside `ProfileName`; card):

    The profile it is compared with, for this run: the name of a bundled profile, or a path to a profile file (.yaml
    or .json) read from the working folder. Default: the one the profile's based_on names, else the bundled profile of
    highest match; a bundled profile is its own. Refused with --strict.

`check` and `profile check` show it. Every help text and docstring that says "the bundled profile it is based on",
"the bundled one it is based on" or "the compared bundled profile" reads "the profile it is compared with" (note
lines 343-345): `cli/commands/profile.py` (`check` docstring), `cli/commands/check.py` (`--strict` help),
`spec/contract/__init__.py` (`ProfileChecked`), `spec/application/controller.py` (`origin`, `check_profile`),
`cli/reports/profile_report.py`, `rules/application/logic/enforcement.py` (module docstring and the `litmus`
finding's words), and the rules `Profiles` port docstrings. The `--strict` help keeps its list; "(every guard, when
none is compared)" stays.

### 2.8 Interfaces that carry it (named for the planner)

- `SpecController.origin(location, against=None)`; `ArchitectureService.origin(location, against=None)`;
  `origin_of(..., against: str | None = None)` (or an equivalent that lets `others` hold the one `--against` profile
  and compares a bundled profile in force when it is given).
- `CheckProfile` (spec contract and rules contract) and `CheckApp` (rules contract) gain `against: str | None = None`,
  last, so every existing construction stands.
- Spec: `SpecController.check_profile` hands `cmd.against` to `ProfileReviewService.check(app, target, against=None)`
  (`spec/application/services/profile_review.py:33`), which calls `ArchitectureService.origin(location, against)`
  only after the target itself loaded (§2.1).
- Rules: `Profiles.reviewed(app, target, against=None)`; the `spec_profile` adapter's `reviewed` passes it into
  `CheckProfile`; `ProfileCheckService.check(app, target, against=None)` (`examples.py`); the rules controller passes
  `cmd.against` to both services; `AppCheckService.check(..., strict, against=None)`. `Profiles.standing` does not
  change (§2.6).
- Text: `profile_report.py` `_match_lines` and `compared_words` today print nothing for a bundled profile; with
  `chosen_by == "against"` they print the match section and `compared with ..., --against` for a bundled one too, and
  `_origin_words` gives the §2.3 headings for `against`.
- CLI: `check(..., against: AgainstName = None)` passes it into `CheckApp` and `_origin(spec, chosen, against,
  refuse)`; `profile check(..., against: AgainstName = None)` passes it into `CheckProfile`.

## 3. Docs

- README command block: `xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
  [--strict] [--against NAME|FILE]` and `xarch profile check [NAME|FILE] [--against NAME|FILE] [--app PATH] [--format
  text|json]` (`tests/architecture/test_readme.py::test_the_block_of_commands_gives_every_option_of_every_command`
  holds this).
- README `profile check` paragraph (around lines 236-248): the profile is compared with the one `--against` names for
  the run, else `based_on`'s, else the bundled one of highest match; `chosen_by` is `based_on`, `against` or
  `closest`; a bundled profile is compared only with `--against`. The `check` enforcement paragraph (around 442-449)
  says the same in a clause, and that `--strict` with `--against` is refused (exit 2) because `--strict` judges the
  profile against its baseline. The rest of note item 10 (the formula prose of README 405-416, the JSON section
  334-364) is not this card's.
- `CHANGELOG.md`, `## [Unreleased]`, `### Added`: one bullet, `--against NAME|FILE` on `check` and `profile check`,
  what it compares and how it is said (`against web, given with --against`; `compared with web, --against`;
  `chosen_by: "against"`), that a bundled profile is compared too, that a value that does not load refuses the run
  (exit 2), and that `--strict` with `--against` is refused. The 5.1 and 5.2 bullets stay as they are.
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated and their diff read (review 3 line 232, O8); this step
  expects them not to move, since no profile or template changes. Never edited by hand.
- `keys.yaml` (note item 11) is 5.4's; not touched.

## 4. Tests (written first)

Service tier, spec (`tests/modules/spec/application/test_origin.py`; the controller over `FakeArchitectureFiles`,
which already serves bundled `base`, `other` and a custom `mine.yaml`; this is where the choice of profile and its
refusals are decided, without a filesystem):

1. `origin("mine.yaml", against="other")` compares with `other`: `compared == "other"`, `chosen_by == "against"`,
   even though `mine.yaml` writes `based_on: base` (the flag wins over `based_on`).
2. `against` a path: a second custom file served by the fake (e.g. `theirs.yaml`) is compared, `compared ==
   "theirs.yaml"`, `chosen_by == "against"`.
3. `against` a file that does not load is `ProfileRefused("--against does not load: broken.yaml: missing `parts`")`.
4. `against` an unknown bundled name is `ProfileRefused` whose reason starts `--against does not load: nosuch:`.
5. A bundled profile in force with `against` is compared: `origin("base", against="other")` has `bundled is True`,
   `compared == "other"`, `chosen_by == "against"`, `match` set, `looser` as `_looser(base, other)` finds.
6. With `against`, no part paired still compares: `low is True`, `compared` set (contrast with the existing test that
   a profile sharing no part resembles nothing without the flag).
7. With `against`, `higher is None` even where another bundled profile matches higher.
8. Without `against`, `origin` is unchanged (the existing `test_origin` cases stay green unedited).

Service tier, rules (`tests/modules/rules/application/test_check_app.py`, `test_profile_check.py`; fakes in
`tests/fakes/profiles.py`, which gain `against` on `reviewed` and record it):

9. `CheckApp(ROOT, "cli", ROOT.parent, strict=True, against="web")` is `CheckRefused(<the §2.5 sentence>)`.
10. The same with an app folder that does not exist is still that `CheckRefused`, not `NotADirectory` (the refusal
    comes before anything runs).
11. `CheckApp(..., strict=False, against="web")` checks as without `against`: the same `AppChecked`.
12. `check_profile(CheckProfile(app, target, "web"))` hands `"web"` to `Profiles.reviewed` (the fake records it).

Adapter tier (`tests/modules/rules/adapters/test_spec_profile.py`; the adapter over a fake spec controller):

13. `reviewed(app, target, "web")` sends `CheckProfile(app, target, "web")` to spec and carries `chosen_by
    "against"` into `Resemblance`; `standing(location, app)` still calls `spec.origin(location)` with no `against`.

CLI / bootstrap tier (`tests/bootstrap/test_profile_check.py`, `test_check_enforcement.py`, `test_check_json.py`;
the real app through `CliRunner`, since the wording, the exit codes and the bundled profiles are only whole here):

14. `profile check <architecture.yaml> --against web`: exit 0; line 1 `checking <path> (custom; against web, given
    with --against; based_on: cli)`; the match line `match: 73% with web (--against): 11 of 16 parts, 67 of 96 part
    keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them`; a `low:`
    line. JSON: `chosen_by "against"`, `match 0.73`, `low true`, `higher null`.
15. `profile check cli --against web`: line 1 `checking cli (bundled; against web, given with --against)`, a match
    line with web; JSON `bundled true`, `compared_with.profile "web"`.
16. `--against` a path, read from the working folder: `profile check cli --against architecture/mine/mine.yaml`
    (the fixture's `profile new` copy of web) exits 0, its heading reads `checking cli (bundled; against
    architecture/mine/mine.yaml, given with --against)`, and its match line is `with architecture/mine/mine.yaml
    (--against)` at the match `cli` has with web (89%: the copy pairs as web does).
17. `profile check --against bad.yaml` (a file that does not load): exit 2, stderr `error: --against does not load:
    bad.yaml: missing \`parts\``; with `--format json`, the JSON error document with that reason.
18. `check --against web` on an app: enforcement `profile:` line `(custom; compared with web, --against; match N%)`
    or `(bundled; compared with web, --against; match N%)` for a bundled profile in force; the exit code equals the
    run without `--against`.
19. `check --strict --against web`: exit 2, the §2.5 sentence on stderr; with `--format json`, the error document.
20. `check --format json --against web`: `enforcement.profile.compared_with.chosen_by == "against"`, and `ok`,
    `violations`, `enforcement.strict_failures` equal those of the run without `--against`.
21. `check --help` and `profile check --help` show `--against` and "the profile it is compared with".

Architecture tier (existing, must stay green): `tests/architecture/test_readme.py` (README lists `--against` on both
commands), `test_self_check.py` (no comments in xarch code), `tests/bootstrap/test_docs.py` (golden docs unchanged),
`tests/bootstrap/test_recorded_corpora.py` (findings do not move).

## 5. Out of scope

- `based_on` as a path, its chain, cycles, the anchor `--strict` rests on, `anchor` in the JSON, and the parenthesis
  of the `--strict` refusal (5.4, note §4 and §4.1, item 3's second half, item 11, keys.yaml).
- The match formula, pairing and the looser lines (5.1, 5.2): read, not changed.
- README's formula prose and JSON section beyond the words of §3; the other CHANGELOG bullets of item 12.
- `--against` on any other command (`review`, `init`, `where`, `profile explain`, `profile view`, `profile new`;
  note lines 87-89).
- A `[tool.xarch] against` setting (dodge, note line 39).

## 6. Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: in the background, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check
architecture.yaml` (unchanged: `match: 80% with cli (based_on)` and the same `compared:` list; note line 385-387
says 81%, computed on 0.2.0; 80% is this branch's number, pinned by
`test_xarch_s_own_profile_is_compared_with_cli_the_profile_it_is_based_on_and_matches_it_at_80_percent`).

Project rules (card): no comments in xarch's code; tests first; examples simple, absolute `app.` imports; recorded
corpora untouched; Python only in the reader adapter and preset data files; `.claude/` out of commits; nothing pushed.

---

## File structure

| File | Responsibility in this plan | Task |
|---|---|---|
| `xarch/modules/spec/domain/published.py` | `AGAINST` beside `BASED_ON`, `CLOSEST`; `Origin.based_on`; Origin docstring | 1 |
| `xarch/modules/spec/contract/__init__.py` | re-export `AGAINST`; `CheckProfile.against`; `ProfileChecked` docstring | 1, 2, 7 |
| `xarch/modules/spec/domain/errors.py` | `AgainstUnloaded`, the one-line load refusal | 1 |
| `xarch/modules/spec/application/logic/looseness.py` | `origin_of(..., against)`, `_compared`; module docstring | 1 |
| `xarch/modules/spec/application/services/architecture.py` | `origin(location, against)`, `_against` | 1 |
| `xarch/modules/spec/application/controller.py` | `origin(location, against)`, `check_profile` hands `cmd.against` on | 1, 2 |
| `xarch/modules/spec/application/services/profile_review.py` | `check(app, target, against)` | 2 |
| `xarch/modules/rules/contract/__init__.py` | `CheckProfile.against`, `CheckApp.against` | 3, 4 |
| `xarch/modules/rules/domain/published.py` | `Resemblance.based_on`; docstrings | 3, 7 |
| `xarch/modules/rules/application/ports/profile.py` | `Profiles.reviewed(..., against)`; docstrings | 3, 7 |
| `xarch/modules/rules/adapters/spec_profile.py` | `reviewed` passes `against`, carries `based_on` | 3 |
| `xarch/modules/rules/application/services/examples.py` | `ExamplesService.check(app, target, against)` (the spec's "ProfileCheckService") | 3 |
| `xarch/modules/rules/application/controller.py` | passes `cmd.against` to both services | 3, 4 |
| `xarch/modules/rules/domain/errors.py` | `StrictAgainst` | 4 |
| `xarch/modules/rules/application/services/app_check.py` | refuses `strict` with `against` first | 4 |
| `xarch/modules/rules/application/logic/enforcement.py` | docstring wording | 7 |
| `xarch/cli/reports/profile_report.py` | headings, match line, compared lines and JSON for `against`, bundled included | 5 |
| `xarch/cli/terminal.py` | `AgainstName` option | 6 |
| `xarch/cli/commands/check.py` | `--against` on `check`; `--strict` help wording | 6, 7 |
| `xarch/cli/commands/profile.py` | `--against` on `profile check`; docstring | 6 |
| `README.md` | command block (6); `profile check` and enforcement paragraphs (7) | 6, 7 |
| `CHANGELOG.md` | the `--against` bullet | 7 |
| `tests/fakes/profiles.py` | `reviewed(..., against)` recorded in `against` | 3 |
| `tests/modules/spec/application/test_origin.py` | spec origin with `against` | 1 |
| `tests/modules/spec/application/test_check.py` | spec `check_profile` with `against` | 2 |
| `tests/modules/rules/application/test_profile_check.py` | rules hands `against` on | 3 |
| `tests/modules/rules/adapters/test_spec_profile.py` | adapter sends `against`, standing never does | 3 |
| `tests/modules/rules/application/test_check_app.py` | strict refusal, non-strict unchanged | 4 |
| `tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py` | the words | 5 |
| `tests/bootstrap/test_profile_check.py`, `test_check_enforcement.py`, `test_check_json.py` | the whole app | 6, 7 |

---

### Task 1: spec compares the profile in force with the one `--against` names

**Files:**
- Modify: `xarch/modules/spec/domain/published.py` (lines 1-12 module docstring entry for `Origin`; lines 141-180 `BASED_ON, CLOSEST` and `Origin`)
- Modify: `xarch/modules/spec/contract/__init__.py` (import list lines 11-31, `__all__` lines 41-50)
- Modify: `xarch/modules/spec/domain/errors.py` (append a class after `InvalidArchitecture`, line 38)
- Modify: `xarch/modules/spec/application/logic/looseness.py` (module docstring lines 1-5; import line 54; `origin_of` lines 380-410)
- Modify: `xarch/modules/spec/application/services/architecture.py` (`origin`, lines 112-117)
- Modify: `xarch/modules/spec/application/controller.py` (`origin`, lines 92-99)
- Test: `tests/modules/spec/application/test_origin.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `xarch.modules.spec.domain.published.AGAINST = "against"`, re-exported by `xarch.modules.spec.contract` as `AGAINST`.
  - `Origin.based_on: str = ""` (last field): with `--against`, what the profile's `based_on` names; `""` otherwise.
  - `origin_of(location: str, architecture: Architecture, bundled: bool, others: Mapping[str, Architecture], against: str | None = None) -> Origin`
  - `AgainstUnloaded(problems: Iterable[str])` in `xarch/modules/spec/domain/errors.py`, a `DomainError` whose reason is `--against does not load: ` + problems joined by `"; "`.
  - `ArchitectureService.origin(location: str | Path, against: str | None = None) -> Origin` (raises `InvalidArchitecture` for the target, `AgainstUnloaded` for `against`).
  - `SpecController.origin(location: str, against: str | None = None) -> OriginResult`.

- [ ] **Step 0: Record today's `profile check` of xarch's own profile, for the last task's gate**

Run: `uv run xarch profile check architecture.yaml > /tmp/5-3-profile-check-before.txt; echo "exit $?"`
Expected: `exit 0`; line 5 of the file reads `  match: 80% with cli (based_on): 12 of 15 parts, ...`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/test_origin.py`, add `from dataclasses import replace` as the first import
line (above `import pytest`), and append at the end of the file:

```python
THEIRS = {**BASE, "name": "theirs"}
"""A copy of base at a path, for --against to name."""


def against(custom: dict) -> SpecController:
    """The controller over base and other, bundled, and mine.yaml (custom, as given), theirs.yaml (a copy of base) and
    broken.yaml (a profile that does not load), at their paths."""
    return spec_controller(FakeArchitectureFiles({"base": BASE, "other": OTHER},
                                                 {"mine.yaml": custom, "theirs.yaml": THEIRS,
                                                  "broken.yaml": {"name": "broken"}},
                                                 {"guard.py": "check()\n"}))


def test_against_a_bundled_profile_wins_over_the_one_based_on_names_and_keeps_based_on_to_say():
    origin = against({**BASE, "based_on": "base"}).origin("mine.yaml", against="other")
    assert (origin.bundled, origin.compared, origin.chosen_by, origin.based_on) == (False, "other", "against", "base")


def test_against_a_path_compares_with_the_profile_file_there():
    origin = against(BASE).origin("mine.yaml", against="theirs.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low, origin.looser) == (
        "theirs.yaml", "against", 1.0, False, ())


def test_against_the_profile_in_force_itself_matches_it_whole_and_finds_nothing_looser():
    origin = against(BASE).origin("mine.yaml", against="mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low, origin.looser) == (
        "mine.yaml", "against", 1.0, False, ())


@pytest.mark.parametrize("given, reason", [
    pytest.param("broken.yaml", "--against does not load: broken.yaml: missing `parts`",
                 id="a profile file that does not load is refused with the loader's problem"),
    pytest.param("gone.yaml", "--against does not load: gone.yaml: cannot read the file: no such file",
                 id="a path that holds no file is refused"),
    pytest.param("nosuch", "--against does not load: nosuch: no bundled architecture 'nosuch': use one of base, "
                           "other, or a path to a .yaml or .json file",
                 id="a name that is no bundled profile is refused with the ones that are"),
])
def test_against_a_profile_that_does_not_load_is_refused(given, reason):
    assert against(BASE).origin("mine.yaml", against=given) == ProfileRefused(reason)


def test_the_profile_in_force_is_loaded_before_against_is_read():
    assert against({"name": "mine"}).origin("mine.yaml", against="nosuch") == ProfileRefused(
        "mine.yaml: missing `parts`")


def test_a_bundled_profile_with_against_is_compared_as_a_copy_of_it_would_be():
    spec = against(BASE)
    origin = spec.origin("base", against="other")
    assert (origin.bundled, origin.compared, origin.chosen_by, origin.higher) == (True, "other", "against", None)
    assert origin.match is not None
    assert origin == replace(spec.origin("mine.yaml", against="other"), location="base", bundled=True)
    assert spec.origin("base", against="theirs.yaml").match == 1.0


def test_against_a_profile_no_part_pairs_with_is_still_compared_and_its_match_is_low():
    origin = against({"name": "mine", "parts": {"x": {"path": "x", "role": "all"}}}).origin("mine.yaml", against="base")
    assert (origin.compared, origin.chosen_by, origin.low) == ("base", "against", True)
    assert origin.counts[0][:2] == ("parts", 0)


def test_against_names_no_bundled_profile_of_higher_match():
    spec = against(BASE)
    assert spec.origin("mine.yaml").compared == "base"
    origin = spec.origin("mine.yaml", against="other")
    assert (origin.compared, origin.higher) == ("other", None)


def test_without_against_based_on_is_not_carried():
    origin = against({**BASE, "based_on": "base"}).origin("mine.yaml")
    assert (origin.chosen_by, origin.based_on) == ("based_on", "")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/test_origin.py -q`
Expected: the new tests FAIL with `TypeError: SpecController.origin() got an unexpected keyword argument 'against'`
(and `test_without_against_based_on_is_not_carried` with `AttributeError: 'Origin' object has no attribute
'based_on'`); the existing tests pass.

- [ ] **Step 3: Add `AGAINST` and `Origin.based_on`**

In `xarch/modules/spec/domain/published.py`, in the module docstring replace

```
                 BASED_ON and CLOSEST why it is compared with that one
```

with

```
                 BASED_ON, CLOSEST and AGAINST why it is compared with that one
```

Replace

```python
BASED_ON, CLOSEST = "based_on", "closest"
"""Why a custom profile is compared with the bundled one it is (Origin.chosen_by): it says it is based on it, or that
one has the highest match."""
```

with

```python
BASED_ON, CLOSEST, AGAINST = "based_on", "closest", "against"
"""Why a profile is compared with the one it is (Origin.chosen_by): a custom one says it is based on it, or that one
has the highest match; or, for this run, --against names it."""
```

In the `Origin` docstring replace the lines

```
    compared: for a custom file, the bundled profile it is compared with; None when it is bundled or none is
```

with

```
    compared: the profile it is compared with, as its location is given: for a custom file the bundled one, and for
        either the one --against names; None when it is bundled and --against is not given, or none is
```

replace

```
    chosen_by: why that one: BASED_ON or CLOSEST; None when nothing is compared
```

with

```
    chosen_by: why that one: BASED_ON, CLOSEST or AGAINST; None when nothing is compared
```

and replace

```
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    """
```

with

```
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none, and always with --against
    based_on: with --against, the profile its own based_on names, which the command line says beside it; empty
        otherwise
    """
```

and after the field `higher: tuple[str, float] | None = None` of `Origin` add the field

```python
    based_on: str = ""
```

In `xarch/modules/spec/contract/__init__.py`, add `AGAINST,` to the import from `xarch.modules.spec.domain.published`
(alphabetically first, before `CHOICE,`), and in `__all__` replace `"LITMUS", "CLOSEST",` with
`"LITMUS", "CLOSEST", "AGAINST",`.

- [ ] **Step 4: Add the load refusal**

In `xarch/modules/spec/domain/errors.py`, after the class `InvalidArchitecture` (it ends at line 37,
`super().__init__("\n".join(self.problems))`), add:

```python


class AgainstUnloaded(DomainError):
    """The profile --against names does not load: every problem the loader found, each starting with where it is, on
    one line."""

    def __init__(self, problems: Iterable[str]):
        super().__init__(f"--against does not load: {'; '.join(problems)}")
```

(`Iterable` is already imported there.)

- [ ] **Step 5: Compare with the `--against` profile in `origin_of`**

In `xarch/modules/spec/application/logic/looseness.py`, change the first paragraph of the module docstring from

```
"""How a profile compares with the bundled ones: the one it is compared with, how much the two have in common (its
match), the guards it leaves off, and every way it is looser than that one.

A custom profile is compared with the bundled profile its `based_on` names, else with the one of highest match, the
first by name on a tie; one no part pairs with is no candidate, and with none left nothing is compared. The match is
```

to

```
"""How a profile compares with the bundled ones: the one it is compared with, how much the two have in common (its
match), the guards it leaves off, and every way it is looser than that one.

A custom profile is compared with the bundled profile its `based_on` names, else with the one of highest match, the
first by name on a tie; one no part pairs with is no candidate, and with none left nothing is compared. For one run,
`--against` names the profile compared with instead, bundled or a file, and then a bundled profile is compared too,
even with one no part pairs with, and no other is said to match higher. The match is
```

Change the import line

```python
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Held, Loosened, Origin
```

to

```python
from xarch.modules.spec.domain.published import AGAINST, BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Held, Loosened, Origin
```

Replace the whole function `origin_of` (from `def origin_of(` through its `higher=...` line) with:

```python
def origin_of(location: str, architecture: Architecture, bundled: bool,
              others: Mapping[str, Architecture], against: str | None = None) -> Origin:
    """Where the architecture at location comes from: a bundled one is its own baseline; a custom one is compared with
    the one of others, the bundled architectures by name, it says it is based on, else the one of highest match (the
    first by name on a tie, one no part pairs with never), and is looser than it in the ways it says. With against,
    the name others holds the one profile --against names by, either is compared with that one alone, even when no
    part pairs, and no other is said to match higher."""
    if against is not None:
        return _compared(location, architecture, bundled, others[against], against, AGAINST, architecture.based_on)
    off = _guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    shares = {name: _share(_counts(architecture, other)) for name, other in others.items()
              if _paired_parts(architecture, other)}
    best = max(shares.values(), default=Fraction(0))
    highest = min((name for name, share in shares.items() if share == best), default=None)
    if architecture.based_on in others:
        name, chosen_by = architecture.based_on, BASED_ON
    elif highest is not None:
        name, chosen_by = highest, CLOSEST
    else:
        return Origin(location, False, None, off, (), ())
    share = _share(_counts(architecture, others[name]))
    return replace(_compared(location, architecture, False, others[name], name, chosen_by),
                   higher=(highest, round(float(best), 2)) if highest is not None and best > share else None)


def _compared(location: str, architecture: Architecture, bundled: bool, base: Architecture, name: str,
              chosen_by: str, based_on: str = "") -> Origin:
    """The architecture at location compared with base, which is called name: the guards both leave off, how it is
    looser, its match and its counts, and what pairs with nothing on either side."""
    off = _guards_off(architecture)
    counts = _counts(architecture, base)
    share = _share(counts)
    parts = _paired_parts(architecture, base)
    tiers = _paired_tiers(architecture, base, parts)
    looser = tuple(Loosened(key, part, what, _sentence(key, part, what)) for key, part, what in _looser(architecture, base))
    return Origin(location, bundled, name, off, tuple(g for g in off if g in _guards_off(base)), looser,
                  chosen_by=chosen_by, match=round(float(share), 2), low=share < LOW or not parts, counts=counts,
                  only_here=_unpaired(architecture, parts, tiers),
                  only_there=_unpaired(base, parts.values(), tiers.values()),
                  elsewhere=_elsewhere(architecture, base), based_on=based_on)
```

(`replace` and `Fraction` are already imported in this file.)

- [ ] **Step 6: Load the `--against` profile in the service and pass it through the controller**

In `xarch/modules/spec/application/services/architecture.py`, change the import

```python
from xarch.modules.spec.domain.errors import InvalidArchitecture
```

to

```python
from xarch.modules.spec.domain.errors import AgainstUnloaded, InvalidArchitecture
```

and replace the method `origin` with:

```python
    def origin(self, location: str | Path, against: str | None = None) -> Origin:
        """Where the architecture comes from, the guards it leaves off and how it is looser than the profile it is
        compared with: the one against names, bundled or a file, for a bundled architecture too; else, for a custom
        file, the bundled architecture it resembles. Raises InvalidArchitecture when the architecture does not load,
        and, once it does, AgainstUnloaded when the one against names does not."""
        source, architecture = self._load(location)
        if against is not None:
            return origin_of(source.location, architecture, source.bundled, {against: self._against(against)}, against)
        others = {} if source.bundled else {name: self.load(name) for name in self._files.bundled()}
        return origin_of(source.location, architecture, source.bundled, others)

    def _against(self, location: str) -> Architecture:
        """The architecture --against names; raises AgainstUnloaded with every problem when it does not load."""
        try:
            return self.load(location)
        except InvalidArchitecture as e:
            raise AgainstUnloaded(e.problems) from e
```

In `xarch/modules/spec/application/controller.py`, replace the method `origin` with:

```python
    def origin(self, location: str, against: str | None = None) -> OriginResult:
        """Where the profile at a location callers got from select() comes from, and how it is looser than the profile
        it is compared with: the one against names for this run, else the bundled profile it resembles; a profile that
        cannot be loaded, or one against names that does not load, is refused with why."""
        try:
            return self._architectures.origin(location, against)
        except DomainError as e:
            return ProfileRefused(e.reason)
```

- [ ] **Step 7: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/spec -q`
Expected: all pass (the existing `test_origin`, `test_profile_loading` and `test_check` cases unedited).

- [ ] **Step 8: Lint**

Run: `uv run ruff check xarch/modules/spec tests/modules/spec/application/test_origin.py`
Expected: `All checks passed!`

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/spec/domain/published.py xarch/modules/spec/contract/__init__.py xarch/modules/spec/domain/errors.py xarch/modules/spec/application/logic/looseness.py xarch/modules/spec/application/services/architecture.py xarch/modules/spec/application/controller.py tests/modules/spec/application/test_origin.py
git commit -m "The origin of a profile can be asked against a profile named for the run, bundled or a file: the profile in force, bundled or custom, is compared with that one alone as 5.1 and 5.2 compare it with based_on's, chosen_by against, no profile said to match higher and its own based_on carried to be said beside it, and one that does not load is refused with every problem of the loader on one line after --against does not load

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: spec's check of a profile hands `against` on

**Files:**
- Modify: `xarch/modules/spec/contract/__init__.py` (`CheckProfile`, lines 363-367)
- Modify: `xarch/modules/spec/application/services/profile_review.py` (`check`, lines 22-33)
- Modify: `xarch/modules/spec/application/controller.py` (`check_profile`, lines 145-153)
- Test: `tests/modules/spec/application/test_check.py`

**Interfaces:**
- Consumes: `ArchitectureService.origin(location, against)` and `AgainstUnloaded` from Task 1.
- Produces:
  - `xarch.modules.spec.contract.CheckProfile(app: Path, target: str | None = None, against: str | None = None)`.
  - `ProfileReviewService.check(app: Path, target: str | None, against: str | None = None) -> ProfileChecked`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/spec/application/test_check.py`:

```python
THEIRS = {**BASE, "name": "theirs"}
"""A copy of base at a path, for --against to name."""


def test_with_against_the_profile_checked_is_compared_with_the_one_it_names():
    spec, _ = spec_controller(files={"mine.yaml": MINE, "theirs.yaml": THEIRS})
    checked = spec.check_profile(CheckProfile(APP, "mine.yaml", "theirs.yaml"))
    assert isinstance(checked, ProfileChecked) and checked.origin is not None
    assert (checked.problems, checked.origin.compared, checked.origin.chosen_by, checked.origin.based_on) == (
        (), "theirs.yaml", "against", "base")


def test_against_a_profile_with_several_problems_is_refused_with_all_of_them_on_one_line():
    broken = {**MINE, "colour": 1, "parts": {"core": {"path": "core"}}}
    spec, _ = spec_controller(files={"mine.yaml": MINE, "broken.yaml": broken})
    assert spec.check_profile(CheckProfile(APP, "mine.yaml", "broken.yaml")) == ProfileRefused(
        "--against does not load: broken.yaml: unknown key 'colour': use based_on, checks, docs, evals, excluded, "
        "fakes, files, guards, hints, language, layers, name, never, parts, reserved, review, testing, tiers; "
        "broken.yaml: parts.core: missing `role`")


def test_against_is_not_read_when_the_profile_checked_does_not_load():
    spec, _ = spec_controller(files={})
    assert spec.check_profile(CheckProfile(APP, "gone.yaml", "nosuch")) == ProfileChecked(
        "gone.yaml", (Problem("load", "gone.yaml: cannot read the file: no such file"),), 0, None)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/test_check.py -q`
Expected: the three new tests FAIL with `TypeError: CheckProfile.__init__() takes from 2 to 3 positional arguments but 4 were given`.

- [ ] **Step 3: Carry `against`**

In `xarch/modules/spec/contract/__init__.py`, replace

```python
@dataclass(frozen=True)
class CheckProfile:
    """Validate a profile without an app: target as for ViewProfile."""
    app: Path
    target: str | None = None
```

with

```python
@dataclass(frozen=True)
class CheckProfile:
    """Validate a profile without an app: target as for ViewProfile; against, when given, the profile it is compared
    with for this run, a bundled name or a path."""
    app: Path
    target: str | None = None
    against: str | None = None
```

In `xarch/modules/spec/application/services/profile_review.py`, replace the method `check` with:

```python
    def check(self, app: Path, target: str | None, against: str | None = None) -> ProfileChecked:
        """What validating the profile found: every problem the loader found when it does not load, else what its
        examples import that their part may not, with how many files it points to and where it comes from, compared
        with the profile against names when it is given, which is read only once the profile loads; raises NoProfile,
        UnknownProfile or AgainstUnloaded."""
        location = self._selection.location(app, target)
        try:
            self._architectures.load(location)
        except InvalidArchitecture as e:
            return ProfileChecked(location, tuple(Problem(LOAD, text) for text in e.problems), 0, None)
        files = self._architectures.pointed(location)
        problems = tuple(Problem(EXAMPLES, text) for text in self._architectures.check_examples(location))
        return ProfileChecked(location, problems, len(files), self._architectures.origin(location, against))
```

In `xarch/modules/spec/application/controller.py`, replace the method `check_profile` with:

```python
    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        """Validates a profile: its problems, all at once, with how it differs from the profile it is compared with,
        the one cmd.against names when it is given; one that cannot be chosen, or an against that does not load, is
        refused with why."""
        try:
            return self._review.check(cmd.app, cmd.target, cmd.against)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/spec -q`
Expected: all pass.

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch/modules/spec tests/modules/spec/application/test_check.py`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/contract/__init__.py xarch/modules/spec/application/services/profile_review.py xarch/modules/spec/application/controller.py tests/modules/spec/application/test_check.py
git commit -m "Spec's check of a profile takes against, the profile it is compared with for the run, and reads it only once the profile checked loads, so a target that does not load is reported as today and an against that does not load is refused with all its problems on one line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: rules hands `against` to spec for `profile check`

**Files:**
- Modify: `xarch/modules/rules/contract/__init__.py` (`CheckProfile`, lines 583-588)
- Modify: `xarch/modules/rules/domain/published.py` (`Resemblance`, lines 130-158)
- Modify: `xarch/modules/rules/application/ports/profile.py` (`reviewed`, lines 30-34)
- Modify: `xarch/modules/rules/application/services/examples.py` (`check`, lines 27-32)
- Modify: `xarch/modules/rules/application/controller.py` (`check_profile`, lines 47-59)
- Modify: `xarch/modules/rules/adapters/spec_profile.py` (`reviewed`, lines 113-129)
- Modify: `tests/fakes/profiles.py` (`__init__`, `reviewed`)
- Test: `tests/modules/rules/application/test_profile_check.py`, `tests/modules/rules/adapters/test_spec_profile.py`

**Interfaces:**
- Consumes: spec `CheckProfile(app, target, against)` (Task 2); `Origin.based_on`, `AGAINST` (Task 1).
- Produces:
  - `xarch.modules.rules.contract.CheckProfile(app: Path, target: str | None = None, against: str | None = None)`.
  - `Resemblance.based_on: str = ""` (last field).
  - `Profiles.reviewed(app: Path, target: str | None, against: str | None = None) -> Reviewed`.
  - `ExamplesService.check(app: Path, target: str | None, against: str | None = None) -> ProfileHeld`.
  - `FakeProfiles.against: list[str | None]`, every `against` its `reviewed` was asked with, in order.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/rules/application/test_profile_check.py`:

```python
def test_against_is_handed_to_spec_s_check_of_the_profile_and_none_without_it():
    profiles = FakeProfiles({"mine": profile()}, reviewed={"mine": MINE})
    rules = controller(FakeSourceTree(Path("/src/app"), {}, parsed=PARSED), profiles)
    assert rules.check_profile(CheckProfile(APP_FOLDER, "mine", "web")) == ProfileHeld(MINE, ChecksHeld((), 0))
    assert rules.check_profile(CheckProfile(APP_FOLDER, "mine")) == ProfileHeld(MINE, ChecksHeld((), 0))
    assert profiles.against == ["web", None]
```

In `tests/modules/rules/adapters/test_spec_profile.py`, replace the fake's `__init__`, `origin` and `check_profile`:

```python
    def __init__(self, files: tuple[ProjectFile, ...] | None = None, origin: OriginResult = ORIGIN,
                 checked: CheckResult | None = None):
        self._files, self._origin, self._checked = files, origin, checked
        self.asked: list[CheckProfile] = []
        self.origins: list[tuple[str, ...]] = []

    def origin(self, location: str, *against: str) -> OriginResult:
        self.origins.append((location, *against))
        return self._origin
```

and

```python
    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        assert (cmd.app, cmd.target) == (Path("/p/app"), "mine.yaml"), cmd
        self.asked.append(cmd)
        return self._checked
```

and append at the end of that file:

```python
def test_against_is_sent_to_spec_s_check_its_word_and_based_on_are_kept_and_the_standing_never_asks_for_it():
    origin = Origin("mine.yaml", False, "web", chosen_by="against", match=0.73, low=True, based_on="cli")
    spec = Spec(origin=origin, checked=ProfileChecked("mine.yaml", (), 3, origin))
    reviewed = SpecProfiles(spec).reviewed(Path("/p/app"), "mine.yaml", "web")
    assert spec.asked == [CheckProfile(Path("/p/app"), "mine.yaml", "web")]
    assert reviewed.resemblance == Resemblance(False, "web", (), "against", 0.73, True, based_on="cli")
    SpecProfiles(spec).standing("mine.yaml", "app")
    assert spec.origins == [("mine.yaml",)]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/modules/rules/application/test_profile_check.py tests/modules/rules/adapters/test_spec_profile.py -q`
Expected: the two new tests FAIL (`TypeError: CheckProfile.__init__() takes from 2 to 3 positional arguments but 4
were given`, and `TypeError: SpecProfiles.reviewed() takes 3 positional arguments but 4 were given`); every other
test passes.

- [ ] **Step 3: Carry `against` through rules**

In `xarch/modules/rules/contract/__init__.py`, replace

```python
@dataclass(frozen=True)
class CheckProfile:
    """Check a profile without an app: the one target names (a bundled name or a path), else the one configured for
    the project holding the app folder, whose name its own checks' examples are read below."""
    app: Path
    target: str | None = None
```

with

```python
@dataclass(frozen=True)
class CheckProfile:
    """Check a profile without an app: the one target names (a bundled name or a path), else the one configured for
    the project holding the app folder, whose name its own checks' examples are read below; against, when given, the
    profile it is compared with for this run, a bundled name or a path."""
    app: Path
    target: str | None = None
    against: str | None = None
```

In `xarch/modules/rules/domain/published.py`, in the `Resemblance` docstring replace

```
    compared: the bundled profile it is compared with; None when it is bundled or none is
    looser: how it is looser than the profile it is compared with, in the order the spec module finds it
    chosen_by: why that one: "based_on", the profile says it is based on it, or "closest", it has the highest match;
        None when nothing is compared
```

with

```
    compared: the profile it is compared with: for a custom profile the bundled one, and for either the one --against
        names; None when it is bundled and --against is not given, or none is
    looser: how it is looser than the profile it is compared with, in the order the spec module finds it
    chosen_by: why that one: "based_on", the profile says it is based on it, "closest", it has the highest match, or
        "against", --against names it for this run; None when nothing is compared
```

replace

```
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    """
```

with

```
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    based_on: with --against, the profile its own based_on names, said beside it; empty otherwise
    """
```

and after `higher: tuple[str, float] | None = None` of `Resemblance` add

```python
    based_on: str = ""
```

In `xarch/modules/rules/application/ports/profile.py`, replace the method `reviewed` with:

```python
    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        """The profile target names (a bundled name or a path), else the one configured for the project holding the
        app folder, checked but for its own checks, and compared with the profile against names when it is given;
        raises Unloaded with every problem when it does not load, NoProfile when none is given or configured, and
        ProfileUnusable when it cannot be chosen or against does not load."""
        ...
```

In `xarch/modules/rules/application/services/examples.py`, replace the method `check` with:

```python
    def check(self, app: Path, target: str | None, against: str | None = None) -> ProfileHeld:
        """The profile target names, else the one configured for the project holding the app folder, checked and
        compared with the profile against names when it is given, its own checks held to their examples; raises
        Unloaded when it does not load, NoProfile when none is chosen, and DomainError when it cannot be used."""
        reviewed = self._profiles.reviewed(app, target, against)
        return ProfileHeld(reviewed, self._held(reviewed.location, app.name))
```

In `xarch/modules/rules/application/controller.py`, replace the method `check_profile` with:

```python
    def check_profile(self, cmd: CheckProfile) -> ProfileCheckResult:
        """Validates a profile without an app: every problem at once, what spec's check of it finds and what its own
        checks find against their examples and the vocabulary, with how it differs from the profile it is compared
        with, the one cmd.against names when it is given. One that does not load comes back with the loader's
        problems, none chosen with the profiles known, and one that cannot be used, or an against that does not load,
        is refused with why."""
        try:
            return self._examples.check(cmd.app, cmd.target, cmd.against)
        except Unloaded as e:
            return ProfileUnloaded(e.location, e.problems)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return CheckRefused(e.reason)
```

In `xarch/modules/rules/adapters/spec_profile.py`, replace the method `reviewed` with:

```python
    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        """What spec's check of the profile found, compared with the profile against names when it is given, in rules'
        terms: a profile that does not load raises Unloaded with the loader's problems, none chosen NoProfile with the
        profiles known, and one spec refuses ProfileUnusable."""
        match self._spec.check_profile(CheckProfile(app, target, against)):
            case ProfileChecked(location, problems, _, None):
                raise Unloaded(location, tuple(problem.text for problem in problems))
            case ProfileChecked(location, problems, files, Origin() as origin):
                looser = tuple(Loosened(item.key, item.part, item.what, item.sentence) for item in origin.looser)
                return Reviewed(location, tuple(problem.text for problem in problems), files,
                                Resemblance(origin.bundled, origin.compared, looser, origin.chosen_by, origin.match,
                                            origin.low, origin.counts, origin.only_here, origin.only_there,
                                            origin.elsewhere, origin.higher, origin.based_on))
            case NoProfileChosen(known):
                raise NoProfile(known)
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
```

In `tests/fakes/profiles.py`, append to the class docstring, before its closing `"""`, the sentence
` Every against reviewed is asked with is kept in against, in order.`, add as the last line of `__init__`

```python
        self.against: list[str | None] = []
```

and replace the method `reviewed` with:

```python
    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        self.against.append(against)
        found = self._reviewed[target]
        if isinstance(found, DomainError):
            raise found
        return found
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/rules tests/cli -q`
Expected: all pass.

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch/modules/rules tests/fakes/profiles.py tests/modules/rules`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/contract/__init__.py xarch/modules/rules/domain/published.py xarch/modules/rules/application/ports/profile.py xarch/modules/rules/application/services/examples.py xarch/modules/rules/application/controller.py xarch/modules/rules/adapters/spec_profile.py tests/fakes/profiles.py tests/modules/rules/application/test_profile_check.py tests/modules/rules/adapters/test_spec_profile.py
git commit -m "Rules' check of a profile takes against and hands it through the Profiles port to spec's check, carrying back chosen_by against and the profile's own based_on in the Resemblance, while the standing that --strict rests on still asks spec for the origin without it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `check --strict` with `--against` is refused before anything runs

**Files:**
- Modify: `xarch/modules/rules/contract/__init__.py` (`CheckApp`, lines 287-296)
- Modify: `xarch/modules/rules/domain/errors.py` (append a class)
- Modify: `xarch/modules/rules/application/services/app_check.py` (`check`)
- Modify: `xarch/modules/rules/application/controller.py` (`check_app`)
- Test: `tests/modules/rules/application/test_check_app.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `CheckApp(root: Path, profile: str, cwd: Path, tests: Path | None = None, strict: bool = False, against: str | None = None)`.
  - `StrictAgainst()` in `xarch/modules/rules/domain/errors.py`, a `DomainError` with the §2.5 reason.
  - `AppCheckService.check(root: Path, profile: str, tests: Path | None, cwd: Path, strict: bool, against: str | None = None) -> AppChecked`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/test_check_app.py`, after the line `UNUSABLE = "gone: cannot read the file: no such file"` add:

```python
STRICT_AGAINST = ("--against shows a comparison and --strict fails on one: run `check --strict` without --against, "
                  "and it judges the profile against its baseline")
```

and add these rows at the end of the table of `test_check_app` (after the row with id `"a profile spec refuses is
refused with spec's reason"`):

```python
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "cli", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused"),
    pytest.param(dict(files=GOOD), CheckApp(Path("/elsewhere"), "cli", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused before the app folder is looked at"),
    pytest.param(dict(files=GOOD), CheckApp(ROOT, "gone", ROOT.parent, strict=True, against="web"),
                 CheckRefused(STRICT_AGAINST), id="strict with against is refused before the profile is read"),
```

and after `test_without_strict_a_finding_of_the_enforcement_does_not_fail_the_check` add:

```python
def test_against_without_strict_checks_as_without_it():
    files = {**BAD, "stray.py": []}
    assert check(files, CheckApp(ROOT, "cli", ROOT.parent, against="web"), [MISSING]) == check(
        files, CheckApp(ROOT, "cli", ROOT.parent), [MISSING])
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/modules/rules/application/test_check_app.py -q`
Expected: the four new cases FAIL with `TypeError: CheckApp.__init__() got an unexpected keyword argument 'against'`.

- [ ] **Step 3: Add `against` and the refusal**

In `xarch/modules/rules/contract/__init__.py`, replace

```python
@dataclass(frozen=True)
class CheckApp:
    """Check the app below root, its imports and its structure, and the tests below tests (None: no tests), against
    the architecture at profile (a bundled name or a path); strict also fails on the enforcement's findings. cwd is the
    working folder, in full, that a relative root or tests folder is read from."""
    root: Path
    profile: str
    cwd: Path
    tests: Path | None = None
    strict: bool = False
```

with

```python
@dataclass(frozen=True)
class CheckApp:
    """Check the app below root, its imports and its structure, and the tests below tests (None: no tests), against
    the architecture at profile (a bundled name or a path); strict also fails on the enforcement's findings. cwd is the
    working folder, in full, that a relative root or tests folder is read from. against is the profile the command
    line compares the one in force with for this run, which the check itself never reads: with strict it is refused."""
    root: Path
    profile: str
    cwd: Path
    tests: Path | None = None
    strict: bool = False
    against: str | None = None
```

In `xarch/modules/rules/domain/errors.py`, append:

```python


class StrictAgainst(DomainError):
    """`check --strict` asked with --against: strict fails on how the profile stands to its baseline, which --against
    does not change, so the two are never run together."""

    def __init__(self) -> None:
        super().__init__("--against shows a comparison and --strict fails on one: run `check --strict` without "
                         "--against, and it judges the profile against its baseline")
```

In `xarch/modules/rules/application/services/app_check.py`, change the import

```python
from xarch.modules.rules.domain.errors import RootMissing
```

to

```python
from xarch.modules.rules.domain.errors import RootMissing, StrictAgainst
```

and replace the method `check` with:

```python
    def check(self, root: Path, profile: str, tests: Path | None, cwd: Path, strict: bool,
              against: str | None = None) -> AppChecked:
        """The violations of the source and of the structure, in order of file, line and rule, a relative root or
        tests folder read from cwd, the working folder; whether the check passes, under strict too on the findings of
        its enforcement. Raises StrictAgainst, before anything is looked at, when strict is asked with against, and
        RootMissing, with the folder as given, when the app folder or the tests folder is no folder."""
        if strict and against is not None:
            raise StrictAgainst()
        app, tested = cwd / root, (cwd / tests if tests is not None else None)
        absent = self._tree.absent(folder for folder in (app, tested) if folder is not None)
        if absent:
            raise RootMissing(root if absent[0] == app else tests)
        app, tested = self._tree.resolved(cwd, root), (self._tree.resolved(cwd, tests) if tests is not None else None)
        package = app.name
        checked = self._source.check(app, package, profile, tested)
        violations = ordered((*checked.violations, *self._structure.violations(app, package, profile, tested)))
        return AppChecked(violations, self._source.view(checked.enforcement), dict(checked.profile.hints),
                          passed(violations, checked.enforcement.strict, strict))
```

In `xarch/modules/rules/application/controller.py`, in `check_app` replace

```python
            return self._app.check(cmd.root, cmd.profile, cmd.tests, cmd.cwd, cmd.strict)
```

with

```python
            return self._app.check(cmd.root, cmd.profile, cmd.tests, cmd.cwd, cmd.strict, cmd.against)
```

and its docstring

```python
        """The whole check of an app; a root or tests folder that is no folder is refused, and so are a profile whose
        own checks cannot run and one that cannot be used."""
```

with

```python
        """The whole check of an app; strict asked with against is refused first, a root or tests folder that is no
        folder is refused, and so are a profile whose own checks cannot run and one that cannot be used."""
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/rules -q`
Expected: all pass.

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch/modules/rules tests/modules/rules/application/test_check_app.py`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/contract/__init__.py xarch/modules/rules/domain/errors.py xarch/modules/rules/application/services/app_check.py xarch/modules/rules/application/controller.py tests/modules/rules/application/test_check_app.py
git commit -m "The check of an app takes against and refuses it with strict before it looks at the app folder or the profile, since --against shows a comparison and --strict fails on the baseline, while without strict against changes nothing the check finds

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: the reports say `--against`, and compare a bundled profile when it is given

**Files:**
- Modify: `xarch/cli/reports/profile_report.py` (module docstring lines 1-16; imports lines 28-39; `_origin_words`, `compared_words`, `_match_lines`, `compared_document`, `_compared`)
- Test: `tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py`

**Interfaces:**
- Consumes: `AGAINST` from `xarch.modules.spec.contract` (Task 1); `Origin.based_on` (Task 1); `Resemblance.based_on` (Task 3).
- Produces: `compared_words(origin)`, `low_reason(origin)`, `compared_document(origin)` keep their signatures (used by `xarch/cli/reports/report.py`); a new module constant `GIVEN = "--against"`.

- [ ] **Step 1: Write the failing tests**

In `tests/cli/reports/test_profile_report.py`, directly after the function `based_on_cli` add:

```python
AGAINST_WEB = based_on_cli(compared="web", chosen_by="against")
"""A custom profile compared with web because --against names it, matching it at 80% with COUNTS."""
```

add these rows at the end of the table of `test_profile_check_is_headed_with_where_the_profile_comes_from`:

```python
    pytest.param(replace(AGAINST_WEB, based_on="cli"), "custom; against web, given with --against; based_on: cli",
                 id="a custom one compared with the profile against names says so, then what it is based on"),
    pytest.param(AGAINST_WEB, "custom; against web, given with --against",
                 id="a custom one based on nothing compared with the profile against names says so"),
    pytest.param(replace(AGAINST_WEB, bundled=True), "bundled; against web, given with --against",
                 id="a bundled one compared with the profile against names says so"),
```

and append at the end of the file:

```python
def test_a_profile_compared_with_the_one_against_names_says_so_in_its_match_and_a_bundled_one_is_compared_too():
    said = MATCH.replace("with cli (based_on)", "with web (--against)")
    assert matched(AGAINST_WEB) == [said]
    bundled = replace(AGAINST_WEB, bundled=True)
    assert matched(bundled) == [said]
    assert checked(bundled)[-1] == "  compared: no looser than web"
    compared = json.loads(check_document(ProfileHeld(Reviewed("cli", (), 1, bundled), ChecksHeld((), 0))))[
        "compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["higher"]) == ("web", "against", None)
```

In `tests/cli/reports/test_report.py`, directly after the function `closest` add:

```python
def test_a_profile_compared_with_the_one_against_names_says_so_on_its_profile_line_bundled_or_custom():
    bundled = Origin("web", True, "cli", chosen_by="against", match=0.89, counts=COUNTS)
    assert lines(origin=bundled)[2:] == ["  profile:     web (bundled; compared with cli, --against; match 89%)"]
    custom = closest("/src/mine.yaml", chosen_by="against", match=0.73, low=True)
    assert lines(origin=custom)[2:] == [
        "  profile:     mine.yaml (custom; compared with web, --against; match 73%)",
        "    match:       73%, low: 27% of what check reads under either profile has nothing to compare with in the "
        "other, so the list below says little about how check would do under web"]
    profile = json.loads(json_document("web", bundled, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert (profile["bundled"], profile["compared_with"]["profile"], profile["compared_with"]["chosen_by"]) == (
        True, "cli", "against")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/cli/reports -q`
Expected: the five new cases FAIL: the headings read `custom; against: web` and `bundled`, the match line reads
`(against)` or is missing for the bundled one, and the `profile:` line reads `web (bundled)`.

- [ ] **Step 3: Say `--against` and compare a bundled profile when it is given**

In `xarch/cli/reports/profile_report.py`, in the module docstring replace

```
"elsewhere", "higher", "looser"} (null for a bundled profile or one that resembles none), counts {"parts",
```

with

```
"elsewhere", "higher", "looser"} (null when nothing is compared: a bundled profile without --against, or one that
resembles none), chosen_by "based_on", "closest" or "against", counts {"parts",
```

In the import from `xarch.modules.spec.contract`, add `AGAINST,` before `CLOSEST,`.

After the line `"""How the match line says each kind of thing it counts, by the kind."""` (which follows `COUNTED`),
add:

```python
GIVEN = "--against"
"""How the text says why a profile is compared with the one --against names."""
```

Replace `_origin_words` and `compared_words` with:

```python
def _origin_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as `profile check` heads it: bundled, or custom and the profile it is
    compared with and why (with the match, when it is the closest), if any; with --against, either and the profile it
    names, then what the profile's own based_on names."""
    if origin.chosen_by == AGAINST:
        based_on = f"; based_on: {origin.based_on}" if origin.based_on else ""
        return f"{_kind(origin)}; against {origin.compared}, given with {GIVEN}{based_on}"
    if origin.bundled:
        return "bundled"
    if origin.compared is None:
        return "custom; no bundled profile resembles it"
    if origin.chosen_by == CLOSEST:
        return f"custom; closest bundled: {origin.compared}, match {percent(origin.match)}"
    return f"custom; {origin.chosen_by}: {origin.compared}"


def compared_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as the enforcement section of `check` says it: bundled, or custom and the
    profile it is compared with, why, and the match, if any; a bundled one compared with the one --against names says
    that too."""
    if origin.compared is None:
        return _origin_words(origin)
    return f"{_kind(origin)}; compared with {origin.compared}, {_why(origin)}; match {percent(origin.match)}"


def _kind(origin: Origin | Resemblance) -> str:
    return "bundled" if origin.bundled else "custom"


def _why(origin: Origin | Resemblance) -> str:
    """Why the profile is compared with the one it is, as the text says it: --against for the one it names, else the
    word of the JSON."""
    return GIVEN if origin.chosen_by == AGAINST else str(origin.chosen_by)
```

In `_match_lines`, replace

```python
    if resemblance.bundled or resemblance.compared is None:
        return []
    counts = ", ".join(f"{comparable} of {every} {COUNTED[kind]}" for kind, comparable, every in resemblance.counts)
    lines = [f"  match: {percent(resemblance.match)} with {resemblance.compared} ({resemblance.chosen_by}): {counts} "
             "sit where both profiles have them"]
```

with

```python
    if resemblance.compared is None:
        return []
    counts = ", ".join(f"{comparable} of {every} {COUNTED[kind]}" for kind, comparable, every in resemblance.counts)
    lines = [f"  match: {percent(resemblance.match)} with {resemblance.compared} ({_why(resemblance)}): {counts} "
             "sit where both profiles have them"]
```

In `compared_document`, replace

```python
    if origin.bundled or origin.compared is None:
        return None
```

with

```python
    if origin.compared is None:
        return None
```

In `_compared`, replace

```python
    if resemblance.bundled or resemblance.compared is None:
        return []
```

with

```python
    if resemblance.compared is None:
        return []
```

(A bundled profile without `--against` has `compared is None` — `origin_of` returns it so — so every line without
the flag stays as it is.)

- [ ] **Step 4: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/cli -q`
Expected: all pass, the existing heading, match and JSON tests among them.

- [ ] **Step 5: Lint**

Run: `uv run ruff check xarch/cli tests/cli`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/cli/reports/profile_report.py tests/cli/reports/test_profile_report.py tests/cli/reports/test_report.py
git commit -m "The reports say a profile compared with the one --against names as against web, given with --against, then its own based_on, in the heading of profile check, as --against in its match line and on check's profile line, and show the match, the comparison and compared_with for a bundled profile too when --against is given

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: `--against` on `check` and `profile check`

**Files:**
- Modify: `xarch/cli/terminal.py` (module docstring line 1-2; add `AgainstName` after `ProfileName`, line 31)
- Modify: `xarch/cli/commands/check.py` (imports, `check`, `_origin`)
- Modify: `xarch/cli/commands/profile.py` (imports lines 10-22; `check`, lines 167-189)
- Modify: `README.md` (command block lines 37 and 48)
- Test: `tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_enforcement.py`, `tests/bootstrap/test_check_json.py`

**Interfaces:**
- Consumes: `SpecController.origin(location, against)` (Task 1); rules `CheckProfile(app, target, against)` (Task 3); `CheckApp(..., strict, against)` (Task 4); the report words (Task 5).
- Produces: `xarch.cli.terminal.AgainstName`, the shared `--against` option.

- [ ] **Step 1: Write the failing tests**

Append to `tests/bootstrap/test_profile_check.py`:

```python
AGAINST_WEB = ("  match: 73% with web (--against): 11 of 16 parts, 67 of 96 part keys, 21 of 31 tier entries, 11 of 11 "
               "guards, 9 of 9 profile keys sit where both profiles have them")
"""The match of xarch's own profile with web, computed on the 0.3.0 profiles."""


def test_xarch_s_own_profile_against_web_is_compared_with_web_for_the_run_and_its_match_is_low():
    result = runner.invoke(app, ["profile", "check", str(XARCH), "--against", "web"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking {XARCH} (custom; against web, given with --against; based_on: cli)"
    assert lines[4:7] == [
        AGAINST_WEB,
        "    only here: parts cli, main, profile-values, reports; tier wired. only in web: part web; tier rendering",
        "    low: 27% of what check reads under either profile has nothing to compare with in the other, so the list "
        "below says little about how check would do under web"]
    assert lines[7].startswith("  compared: looser than web")
    document = json.loads(runner.invoke(app, ["profile", "check", str(XARCH), "--against", "web", "--format",
                                              "json"]).output)
    assert {key: document["compared_with"][key] for key in ("profile", "chosen_by", "match", "low", "higher")} == {
        "profile": "web", "chosen_by": "against", "match": 0.73, "low": True, "higher": None}


def test_a_bundled_profile_against_another_is_compared_with_it():
    result = runner.invoke(app, ["profile", "check", "cli", "--against", "web"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "checking cli (bundled; against web, given with --against)"
    assert lines[4] == ("  match: 89% with web (--against): 11 of 13 parts, 64 of 74 part keys, 16 of 18 tier entries, "
                        "11 of 11 guards, 6 of 6 profile keys sit where both profiles have them")
    document = json.loads(runner.invoke(app, ["profile", "check", "cli", "--against", "web", "--format", "json"]).output)
    assert (document["compared_with"]["profile"], document["compared_with"]["chosen_by"]) == ("web", "against")


def test_against_a_path_is_read_from_the_working_folder():
    result = runner.invoke(app, ["profile", "check", "cli", "--against", COPY])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking cli (bundled; against {COPY}, given with --against)"
    assert lines[4].startswith(f"  match: 89% with {COPY} (--against): 11 of 13 parts")


def test_against_a_profile_that_does_not_load_refuses_the_run(tmp_path):
    (tmp_path / "bad.yaml").write_text("name: x\n")
    text = runner.invoke(app, ["profile", "check", "--against", "bad.yaml"])
    assert text.exit_code == 2
    assert "error: --against does not load: bad.yaml: missing `parts`" in text.output
    document = json.loads(runner.invoke(app, ["profile", "check", "--against", "bad.yaml", "--format", "json"]).stdout)
    assert document == {"ok": False, "error": "--against does not load: bad.yaml: missing `parts`"}


def test_a_profile_that_does_not_load_is_reported_as_it_is_and_against_is_not_read(tmp_path):
    (tmp_path / "bad.yaml").write_text("name: x\n")
    result = runner.invoke(app, ["profile", "check", "bad.yaml", "--against", "nosuch"])
    assert result.exit_code == 1
    assert "missing `parts`" in result.output and "--against" not in result.output
```

In `tests/bootstrap/test_check_enforcement.py`, append:

```python
STRICT_AGAINST = ("--against shows a comparison and --strict fails on one: run `check --strict` without --against, "
                  "and it judges the profile against its baseline")


def test_against_compares_the_profile_in_force_for_the_run_and_leaves_the_exit_code_as_it_is(tmp_path):
    bundled = check("--against", "cli")
    assert bundled.exit_code == 0
    assert bundled.stdout.splitlines()[2] == "  profile:     web (bundled; compared with cli, --against; match 89%)"
    plant(tmp_path)
    custom = check("--profile", "arch/open.yaml", "--against", "cli")
    assert custom.exit_code == check("--profile", "arch/open.yaml").exit_code == 0
    assert custom.stdout.splitlines()[2] == (
        "  profile:     arch/open.yaml (custom; compared with cli, --against; match 89%)")


def test_against_changes_only_the_comparison_of_the_json_document(tmp_path):
    plant(tmp_path)
    plain = json.loads(check("--profile", "arch/open.yaml", "--format", "json").stdout)
    against = json.loads(check("--profile", "arch/open.yaml", "--against", "cli", "--format", "json").stdout)
    compared = against["enforcement"]["profile"]["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["higher"]) == ("cli", "against", None)
    assert plain["enforcement"]["strict_failures"]
    assert (against["ok"], against["violations"], against["enforcement"]["strict_failures"]) == (
        plain["ok"], plain["violations"], plain["enforcement"]["strict_failures"])


def test_strict_with_against_is_refused_before_anything_is_checked():
    text = check("--strict", "--against", "cli")
    assert text.exit_code == 2 and f"error: {STRICT_AGAINST}" in text.output
    missing = check("--app", "missing", "--strict", "--against", "cli")
    assert missing.exit_code == 2 and f"error: {STRICT_AGAINST}" in missing.output
    document = json.loads(check("--strict", "--against", "cli", "--format", "json").stdout)
    assert document == {"ok": False, "error": STRICT_AGAINST}


def test_check_against_a_profile_that_does_not_load_is_refused():
    result = check("--against", "nosuch")
    assert result.exit_code == 2
    assert ("error: --against does not load: nosuch: no bundled architecture 'nosuch': use one of cli, web, or a "
            "path to a .yaml or .json file") in result.output


@pytest.mark.parametrize("command", ["check", "profile check"])
def test_check_and_profile_check_take_against_the_profile_it_is_compared_with(command):
    found = typer.main.get_command(app)
    for name in command.split():
        found = found.commands[name]
    option = next(param for param in found.params if "--against" in param.opts)
    assert option.help == (
        "The profile it is compared with, for this run: the name of a bundled profile, or a path to a profile file "
        "(.yaml or .json) read from the working folder. Default: the one the profile's based_on names, else the "
        "bundled profile of highest match; a bundled profile is its own. Refused with --strict.")
```

In `tests/bootstrap/test_check_json.py`, add a row to the table of `test_a_refusal_is_a_json_error_with_exit_code_2`:

```python
    (["--against", "nosuch"], "--against does not load: nosuch: no bundled architecture 'nosuch'"),
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `timeout 600 uv run pytest tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_check_json.py -q`
Expected: every new test FAILS: the runs exit 2 with `No such option: --against`, and the help test with
`StopIteration`.

- [ ] **Step 3: Add the shared option**

In `xarch/cli/terminal.py`, replace the module docstring

```
"""What every command shares: the --app, --profile, --tests and --format options, choosing the app folder and the
profile, how its help is wrapped, and how a refusal reaches the terminal, as text or as JSON."""
```

with

```
"""What every command shares: the --app, --profile, --against, --tests and --format options, choosing the app folder
and the profile, how its help is wrapped, and how a refusal reaches the terminal, as text or as JSON."""
```

and after the `ProfileName = Annotated[...]` definition add:

```python
AgainstName = Annotated[str | None, typer.Option(
    "--against", help="The profile it is compared with, for this run: the name of a bundled profile, or a path to a "
                      "profile file (.yaml or .json) read from the working folder. Default: the one the profile's "
                      "based_on names, else the bundled profile of highest match; a bundled profile is its own. "
                      "Refused with --strict.")]
```

- [ ] **Step 4: Take it on `check`**

In `xarch/cli/commands/check.py`, add `AgainstName,` to the import from `xarch.cli.terminal` (first, before
`AppPath,`), and replace the function `check` (inside `register`) and `_origin` with:

```python
    @app.command()
    @rewrapped
    def check(app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
              output: FormatOption = Format.text, strict: StrictOption = False, against: AgainstName = None) -> None:
        """Report every violation of the architecture in the app and its tests."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        match rules.check_app(CheckApp(app_path, chosen, cwd, tests_root, strict, against)):
            case NotADirectory(root):
                raise refuse(not_a_directory(root, cwd))
            case ChecksCannotRun(problems):
                raise refuse(cannot_run(problems))
            case CheckRefused(reason):
                raise refuse(reason)
            case AppChecked() as checked:
                origin = _origin(spec, chosen, against, refuse)
                echo([json_document(chosen, origin, checked, strict)] if output is Format.json
                     else check_lines(origin, checked, strict, cwd))
                if not checked.ok:
                    raise typer.Exit(1)


def _origin(spec: SpecController, chosen: str, against: str | None, refuse) -> Origin:
    """Where the profile in force comes from and the profile it is compared with, the one against names for this run
    when it is given, which spec works out and the enforcement section shows first; what --strict fails on never reads
    it."""
    match spec.origin(chosen, against):
        case Origin() as origin:
            return origin
        case ProfileRefused(reason):
            raise refuse(reason)
```

- [ ] **Step 5: Take it on `profile check`**

In `xarch/cli/commands/profile.py`, add `AgainstName,` to the import from `xarch.cli.terminal` (first, before
`AppPath,`), and replace the head of `check` and its docstring and `match` line, from `def check(target:` through
`match rules.check_profile(CheckProfile(app, target)):`, with:

```python
    def check(target: Annotated[str | None, typer.Argument(
                  help="A bundled profile's name, or a path to a profile file. Default: the profile configured under "
                       "\\[tool.xarch] in pyproject.toml.")] = None,
              against: AgainstName = None, app_path: AppPath = None, output: FormatOption = Format.text) -> None:
        """Validate a profile without an app.

        It loads (every problem at once, which includes every file it points to existing), its examples import only
        what their part may, each check of its own is written in words that apply and finds something in the code its
        examples flag and nothing in their clean code, and how it differs from the profile it is compared with (the
        one --against names, else the one its based_on names, else the bundled profile of highest match) is shown as
        information. Exit 0 when the profile is valid, 1 when it has problems, 2 when no profile can be chosen or
        --against names one that does not load."""
        refuse = refusal(output)
        app = app_for(spec, in_full(Path()), app_path, refuse)
        match rules.check_profile(CheckProfile(app, target, against)):
```

(the `case` arms below it stay as they are.)

- [ ] **Step 6: Run the bootstrap tests to see them pass, and the README test fail**

Run: `timeout 600 uv run pytest tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_check_json.py tests/architecture/test_readme.py -q`
Expected: the bootstrap tests pass; `test_the_block_of_commands_gives_every_option_of_every_command` FAILS, naming
`--against` under `xarch check` and `xarch profile check`.

- [ ] **Step 7: Name `--against` in the README's command block**

In `README.md`, replace the line

```
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict]
```

with

```
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict] [--against NAME|FILE]
```

and the line

```
xarch profile check [NAME|FILE] [--app PATH] [--format text|json]
```

with

```
xarch profile check [NAME|FILE] [--against NAME|FILE] [--app PATH] [--format text|json]
```

- [ ] **Step 8: Run the tests to see them pass**

Run: `timeout 600 uv run pytest tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_check_json.py tests/architecture -q`
Expected: all pass.

- [ ] **Step 9: Lint**

Run: `uv run ruff check xarch/cli tests/bootstrap`
Expected: `All checks passed!`

- [ ] **Step 10: Commit**

```bash
git add xarch/cli/terminal.py xarch/cli/commands/check.py xarch/cli/commands/profile.py README.md tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_check_json.py
git commit -m "check and profile check take --against NAME|FILE, a bundled name or a path read from the working folder, which compares the profile in force, custom or bundled, with that one for the run, refuses a value that does not load with exit 2, and is refused with --strict, the violations, the exit code and what --strict fails on staying as they are without it; the README's command block names it on both

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: the words say "the profile it is compared with"; README, CHANGELOG, golden docs, every gate

**Files:**
- Modify: `xarch/cli/commands/check.py` (`StrictOption` help, line 30)
- Modify: `xarch/modules/spec/contract/__init__.py` (`ProfileChecked` docstring, lines 385-387)
- Modify: `xarch/modules/rules/application/logic/enforcement.py` (module docstring line 20; docstring lines 83-84)
- Modify: `xarch/modules/rules/application/ports/profile.py` (`standing` docstring, lines 17-18)
- Modify: `xarch/modules/rules/domain/published.py` (module docstring lines 15-16; `Loosened` docstring line 121)
- Modify: `README.md` (`profile check` paragraph, lines 234-249; enforcement paragraph, lines 442-448)
- Modify: `CHANGELOG.md` (`## [Unreleased]`, `### Added`)
- Regenerated, expected unchanged: `docs/cli/**`, `docs/web/**`, `docs/xarch/**`
- Test: `tests/bootstrap/test_check_enforcement.py`

**Interfaces:**
- Consumes: everything above. Produces: nothing new.

- [ ] **Step 1: Write the failing test**

In `tests/bootstrap/test_check_enforcement.py`, append:

```python
def test_the_help_of_strict_names_the_profile_it_is_compared_with():
    command = typer.main.get_command(app).commands["check"]
    strict = next(param for param in command.params if "--strict" in param.opts)
    assert "guards left off that the profile it is compared with switches on (every guard, when none is compared)" in (
        strict.help)
    assert "compared bundled profile" not in strict.help
```

- [ ] **Step 2: Run it to see it fail**

Run: `timeout 300 uv run pytest tests/bootstrap/test_check_enforcement.py::test_the_help_of_strict_names_the_profile_it_is_compared_with -q`
Expected: FAIL (the help says `the compared bundled profile switches on`).

- [ ] **Step 3: Change the words**

`xarch/cli/commands/check.py`: replace

```
         "guards left off that the compared bundled profile switches on (every guard, when none is compared), "
```

with

```
         "guards left off that the profile it is compared with switches on (every guard, when none is compared), "
```

`xarch/modules/spec/contract/__init__.py`, `ProfileChecked` docstring: replace

```
    (when it loads), and, when it loads, its origin: how it differs from the bundled profile it is based on, as
    information."""
```

with

```
    (when it loads), and, when it loads, its origin: how it differs from the profile it is compared with, as
    information."""
```

`xarch/modules/rules/application/logic/enforcement.py`: in the module docstring replace

```
redefines without the litmus the bundled profile it is compared with gives it (litmus), which leaves its code no
```

with

```
redefines without the litmus the profile it is compared with gives it (litmus), which leaves its code no
```

and in the docstring at lines 83-84 replace

```
    """Each way a profile is looser that `--strict` fails on, as said: a part redefined without the litmus the bundled
    profile it is compared with gives it, whose key is the key of its section of the enforcement."""
```

with

```
    """Each way a profile is looser that `--strict` fails on, as said: a part redefined without the litmus the profile
    it is compared with gives it, whose key is the key of its section of the enforcement."""
```

`xarch/modules/rules/application/ports/profile.py`, `standing` docstring: replace

```
        """The guards the profile leaves off, and those the bundled profile it is, or is compared with, leaves off too,
        and the files `init` would write now beside an app folder named app, in the profile's order."""
```

with

```
        """The guards the profile leaves off, and those the profile it is compared with leaves off too (a bundled
        profile being its own, and --against never read here), and the files `init` would write now beside an app
        folder named app, in the profile's order."""
```

`xarch/modules/rules/domain/published.py`: in the module docstring replace `Loosened one way a profile is looser
than the bundled one it is compared with` with `Loosened one way a profile is looser than the profile it is compared
with`, and `Resemblance whether a profile is bundled, the bundled one it is compared with` with `Resemblance whether
a profile is bundled, the profile it is compared with` (re-wrap those two entries to the column of their
neighbours if a line grows past 120 characters); in the `Loosened` docstring replace `One way a profile is looser
than the bundled profile it is compared with:` with `One way a profile is looser than the profile it is compared
with:`.

Then run: `grep -rn "bundled profile it is based on\|bundled one it is based on\|compared bundled profile" xarch`
Expected: no output.

- [ ] **Step 4: Run the test to see it pass**

Run: `timeout 300 uv run pytest tests/bootstrap/test_check_enforcement.py tests/modules/rules tests/modules/spec -q`
Expected: all pass.

- [ ] **Step 5: The README paragraphs**

In `README.md`, in the `profile check` paragraph replace

```
to its examples, and shows how it differs from the bundled profile it is compared with, as information (but for a part
left without the litmus the bundled profile gives it, which fails `check --strict`). Before that comparison a `match:`
```

with

```
to its examples, and shows how it differs from the profile it is compared with, as information (but for a part left
without the litmus that profile gives it, which fails `check --strict`). That profile is the one `--against NAME|FILE`
names for the run (a bundled name, or a path to a profile file read from the working folder; one that does not load
refuses the run, exit 2), else the one its `based_on` names, else the bundled one of highest match; a bundled profile
is its own baseline and is compared only with `--against`, which the heading says: `checking cli (bundled; against
web, given with --against)`, and for a custom one `(custom; against web, given with --against; based_on: cli)`, its
match line reading `match: 73% with web (--against): ...`. Before that comparison a `match:`
```

replace

```
the project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen;
```

with

```
the project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen or
`--against` names one that does not load;
```

replace

```
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load. `compared_with` is `null` for a bundled profile or one no bundled profile
resembles, else `{"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there", "elsewhere", "higher",
"looser"}`: `chosen_by` `based_on` or `closest`, `match` the share to two decimals (`0.8`), `counts` `{"parts",
```

with

```
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load. `compared_with` is `null` for a bundled profile checked without `--against`
or one no bundled profile resembles, else `{"profile", "chosen_by", "match", "low", "counts", "only_here",
"only_there", "elsewhere", "higher", "looser"}`: `chosen_by` `based_on`, `against` or `closest`, `match` the share to
two decimals (`0.8`), `counts` `{"parts",
```

In the enforcement paragraph replace

```
- `profile`: the bundled name, or the custom file's path, the bundled profile it is compared with, why (`based_on`,
  the one its `based_on` names, else `closest`, the one of highest match, the first by name on a tie) and the match:
```

with

```
- `profile`: the bundled name, or the custom file's path, the profile it is compared with, why (`--against`, the one
  `--against` names for the run, which compares a bundled profile too: `web (bundled; compared with cli, --against;
  match 89%)`; else `based_on`, the one its `based_on` names, else `closest`, the one of highest match, the first by
  name on a tie) and the match:
```

and replace

```
  holds the same object as `profile check`'s (`null` when nothing is compared). `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
```

with

```
  holds the same object as `profile check`'s (`null` when nothing is compared). `--strict` with `--against` is
  refused (exit 2): `--strict` judges the profile against its baseline, which `--against` leaves as it is, so the
  violations and `strict_failures` are the same with it and without it. `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
```

Run: `timeout 300 uv run pytest tests/architecture -q`
Expected: all pass.

- [ ] **Step 6: The CHANGELOG bullet**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Added`, directly after the first bullet (the one that starts
`- The match of a custom profile with the bundled one it is compared with:` and ends `` `elsewhere` and `higher`. ``),
insert:

```
- `--against NAME|FILE` on `check` and `profile check`: for that run, the profile in force is compared with the one it
  names, a bundled name or a path to a profile file read from the working folder, instead of the one its `based_on`
  names or the bundled one of highest match, and a bundled profile, its own baseline without the flag, is compared
  too. `profile check` heads it `(custom; against web, given with --against; based_on: cli)` and says `match: 73% with
  web (--against): ...`; `check`'s `profile:` line says `(custom; compared with web, --against; match 73%)`; the JSON
  of both says `"chosen_by": "against"` in `compared_with`. A value that does not load refuses the run (exit 2,
  `--against does not load: ...`), and `--strict` with `--against` is refused (exit 2), since `--strict` judges the
  profile against its baseline.
```

- [ ] **Step 7: Regenerate the golden docs and see an empty diff**

```bash
uv run python - <<'EOF'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for profile, out in (("cli", "docs/cli"), ("web", "docs/web"), ("architecture.yaml", "docs/xarch")):
    for found in spec.docs(profile).files:
        Path(out, *found.path).write_text(found.template, encoding="utf-8")
EOF
git status --short docs/ && git diff --stat docs/
```

Expected: nothing under `docs/cli`, `docs/web` or `docs/xarch` (no profile or template changes in this step). A
changed file there is a behaviour change: restore it with `git checkout -- <file>` and find its cause.

- [ ] **Step 8: The corpora are untouched**

Run: `git diff --stat ca15929 -- tests/bootstrap/corpora tests/bootstrap/test_recorded_corpora.py docs/examples`
Expected: no output.

- [ ] **Step 9: Run every gate**

```bash
uv run ruff check
uv run xarch check >/dev/null; echo "exit $?"
uv run xarch check --strict >/dev/null; echo "exit $?"
uv run xarch profile check architecture.yaml > /tmp/5-3-profile-check-after.txt; echo "exit $?"
diff /tmp/5-3-profile-check-before.txt /tmp/5-3-profile-check-after.txt && echo SAME
```

Expected: `All checks passed!`, `exit 0`, `exit 0`, `exit 0`, `SAME` (still `match: 80% with cli (based_on)` and the
same `compared:` list).

Then the whole suite, in the background (over two minutes), and read its tail at the end:

```bash
timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3
```

Expected: `... passed`, no failures.

- [ ] **Step 10: Commit**

```bash
git add xarch/cli/commands/check.py xarch/modules/spec/contract/__init__.py xarch/modules/rules/application/logic/enforcement.py xarch/modules/rules/application/ports/profile.py xarch/modules/rules/domain/published.py README.md CHANGELOG.md tests/bootstrap/test_check_enforcement.py
git commit -m "The help of --strict and the docstrings say the profile it is compared with rather than the bundled one it is based on, the README says that profile check and check compare with the profile --against names for the run, that chosen_by can be against and that --strict with --against is refused, and the CHANGELOG adds --against under Unreleased; the golden docs regenerate unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.**
- §1, §2.2 table (custom/bundled × given/not): Task 1 (`origin_of`, tests 1, 5, 8), Task 6 (whole app).
- §2.1 accepted values, the one-line reason, the three examples, target loaded first: Task 1 (refusal table,
  `test_the_profile_in_force_is_loaded_before_against_is_read`), Task 2 (several problems; target not loading), Task 6
  (`bad.yaml` in text and JSON; `nosuch` on `check`; path read from the working folder). No `[tool.xarch] against`:
  nothing reads settings for it (Global Constraints).
- §2.2 bullets: same comparison (Task 1 `_compared` shared with based_on/closest), no part paired still compares
  (Task 1), `higher` None (Task 1), `Origin.bundled` kept and `baseline_off` both sides' (Task 1, through `_compared`),
  `--against` the profile itself (Task 1).
- §2.3 text: headings and match line (Task 5, Task 6 tests 14-16), `check` profile line and low match line (Task 5,
  Task 6 test 18); unchanged without the flag (existing report and bootstrap tests stay green).
- §2.4 JSON: `chosen_by "against"`, `higher null`, bundled `compared_with` set, `bundled true` (Task 5, Task 6); `ok`,
  `violations`, `strict_failures` equal (Task 6 test 20); no `anchor`.
- §2.5 strict refusal in `AppCheckService`, before the folder: Task 4; at the CLI, text and JSON: Task 6.
- §2.6 `--strict` never reads `against`: `Profiles.standing` untouched; adapter test asserts `spec.origins ==
  [("mine.yaml",)]` (Task 3); only `_origin` in `check.py` reads it (Task 6).
- §2.7 help and docstrings: help text (Task 6, exact-text test), `--strict` help and the listed docstrings (Task 7,
  plus Tasks 1-5 for the docstrings of the code they change).
- §2.8 interfaces: every named signature, with `ProfileCheckService` being `ExamplesService` in `examples.py` (Task 3).
  `based_on` beside `--against` in the heading needs data the spec's interfaces did not name: carried as
  `Origin.based_on` / `Resemblance.based_on`, set only with `--against`, so every existing Origin equality holds.
- §3 docs: README block (Task 6), paragraphs, CHANGELOG, golden docs (Task 7). keys.yaml untouched.
- §4 tests 1-21: Tasks 1 (1-8), 4 (9-11), 3 (12-13), 6 (14-21); architecture tier in Task 7's gate.
- §6 gates: Task 7 Step 9.

**Placeholder scan.** No TBD/TODO; every code step shows its code; each task repeats what it needs.

**Type consistency.** `against: str | None = None` everywhere; `AGAINST = "against"` (spec domain, re-exported);
`Origin.based_on: str = ""` and `Resemblance.based_on: str = ""` both last; `AgainstUnloaded(problems)` and
`StrictAgainst()`; `FakeProfiles.against` list; `GIVEN = "--against"` in `profile_report.py`;
`_origin(spec, chosen, against, refuse)`.

**Review Focus.** Five lines above, each with its test in its owning task.

**Numbers checked on this branch (2026-11-23):** `architecture.yaml` vs web 73% low, counts 11/16, 67/96, 21/31,
11/11, 9/9, only here `cli, main, profile-values, reports; tier wired`, only in web `part web; tier rendering`, no
elsewhere; cli vs web 89%, counts 11/13, 64/74, 16/18, 11/11, 6/6; cli vs the `profile new` copy of web 89%, same
counts; web vs cli 89%; `arch/open.yaml` (web without closed-tree) vs cli 89%.
<!-- task-pipeline: validated -->
