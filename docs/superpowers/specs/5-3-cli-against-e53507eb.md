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
