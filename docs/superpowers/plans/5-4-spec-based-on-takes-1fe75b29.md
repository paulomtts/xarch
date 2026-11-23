# 5.4: `based_on` takes a path, and `--strict` rests on a bundled anchor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A profile may write `based_on: <path of a profile file>`. The path is read from the folder of the file that writes it, and the chain of such files is followed, a loop or an unloadable file refusing the profile. `profile check` and `check` compare with that file. `--strict` rests on a bundled *anchor*, so a file of one's own can tighten `--strict` but never loosen it.

**Architecture:** The parser (`profile_parsing._based_on`) accepts a path by its form alone. A new pure logic file, `spec/application/logic/profile_chain.py`, says where a `based_on` path is read from and refuses a loop. `ArchitectureService.origin` loads the chain through `ArchitectureService.load` (passing a `Path`), and hands it to `looseness.origin_of(..., chain=...)`, which stays pure. `origin_of` compares with the chain's first file, finds the anchor, works out `baseline_off` from the anchor and the chain, and appends the anchor's litmus entries. `Origin` and rules' `Resemblance` gain `anchor: str | None = None` as their last field. The reports in `cli/reports/` read `anchor` for the new words and the JSON key.

**Tech Stack:** Python 3.13, pytest, typer (CliRunner), PyYAML, `uv run`.

**Spec:** `docs/superpowers/specs/5-4-spec-based-on-takes-1fe75b29.md` (reproduced in full below; the plan argues from it).

---

## The spec (verbatim)

# 5.4: `based_on` takes a path, and `--strict` rests on a bundled anchor

Card `1fe75b29`, subtask of `3c8f968f`, release step 16 of the merged order (`0.3.0-cohesion-review-3.md`, section 3),
after 5.1 (`f004b3d1`, pairing and the match), 5.2 (`aabea037`, the looser lines) and 5.3 (`e53507eb`, `--against`),
all on this branch. Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-comparison-design.md`,
cited below as "note line L"; the third cohesion review in the same folder as "review 3 line L".

This step builds note §4 (lines 248-266), §4.1 (lines 268-317), §5 item 3 (its `based_on` half, lines 330-332), item 5
(its last sentence, `unplaced`, line 338), item 11 (lines 359-361), item 12 (its `based_on` bullet, line 362), and the
service tests of §5 for `based_on` a path (lines 374-377); review 3 C5 (line 131), C6 (line 141) and gap G5 (line 418),
which this spec closes by tracing the chain into `baseline_off` and `unplaced` (§2.5, §2.6).

## 1. What changes for a person

A profile may write `based_on: ../team.yaml`: the path of another profile file, read from the folder of the file that
writes it (note lines 252-255; review 3 C6). `profile check` and `check` then compare the profile with that file, as
written (note lines 262-263). That file may itself be based on a bundled profile or on another file; the chain is
followed, a loop is refused, and a file of the chain that does not load refuses the profile (note lines 256-261).

`--strict` never takes its excuses from a file of one's own (note lines 276-288; dodge lines 423-425). It rests on a
bundled profile, the *anchor*: the bundled profile the chain ends on, else the bundled profile closest to the chain's
last file, else none. A guard left off is excused only when the anchor and every file of the chain leave it off too,
and a part fails `unplaced` when it lacks a litmus the path file gives it or that the anchor gives the part it pairs
with. A path baseline can tighten `--strict`, never loosen it.

With `based_on` a bundled name, nothing a person sees changes but one JSON field, `compared_with.anchor`.

## 2. Behavior (normative)

### 2.1 What `based_on` accepts (the parser)

`_based_on` (`spec/application/logic/profile_parsing.py:249`) checks the form only (note lines 256-258); it reads no
file.

- A string that `ArchitectureSource.names_a_file` (`spec/domain/values.py:474`) treats as a file (it has a folder
  step or a suffix: `../team.yaml`, `team.yaml`, `base/team.json`) is a path. It is accepted as written, without
  checking that it exists: `Architecture.based_on` holds the string as written. No bundled name holds `/` or a dot
  (note line 253).
- Any other string is a bundled name, checked as today: unknown → `based_on: no bundled profile 'mine': use cli, web`
  (unchanged; `test_profile_parsing.py:78` stays).
- A value that is not a string, or the empty string, → `based_on: must be the name of a bundled profile or the path
  of a profile file: use cli, web` (the words "or the path of a profile file" are new; `test_profile_parsing.py:79`
  is edited to it). With no bundled profiles the `: use ...` tail is left off, as today.

`parse_copy` (`profile new`) keeps writing `based_on: <bundled source>` and printing `wrote <folder>/, a copy of cli
named mine, based_on: cli` (note lines 264-265). No bundled profile's `based_on` changes (card: out of scope).

### 2.2 Where a `based_on` path is read from

From the folder of the file that writes it, never the working folder (note lines 254-255; dodge line 425; review 3
C6). The service resolves it as the normalized join of the writing file's folder and the value: for a profile at
`sub/mine.yaml` writing `based_on: ../team.yaml`, the file read is `team.yaml`; for `/abs/p/mine.yaml` writing
`team.yaml`, it is `/abs/p/team.yaml`. Normalization collapses `.` and `..` steps textually (`posixpath.normpath`
semantics, `/` separators); symlinks are not resolved. A path in a file of the chain is resolved from *that* file's
folder. `--profile` and `--against` keep reading from the working folder (`profile_file.py:11`), as a command line does.

The resolved location is loaded with `ArchitectureService.load`, as any profile is (its own pointed files are read from
its own folder by the port, `fs_architecture_files.py:86-92`), passed as a `Path`: normalization can leave a single
step with no suffix (`../team` from `sub/` gives `team`), which `source_of` (`profile_file.py:11`) would take for a
bundled name unless it is a `Path` (`names_a_file` is true of any `Path`). The location said in reasons and compared for
loops is `str` of that `Path`.

### 2.3 The chain, and its refusals

The chain of a profile whose `based_on` is a path is: the file it names, then the file that file's `based_on` names if
that is a path, and so on. It ends at the first file whose `based_on` is a bundled name (that bundled profile is the
chain's *bundled root*) or that writes no `based_on` (then the chain has no bundled root and its *last file* is that
file).

The chain is loaded by `ArchitectureService.origin` (note lines 256-258, item 3 line 330), on every call for a profile
whose `based_on` is a path, with or without `against`. Nothing else loads it: `docs`, `files`, `pointed`, `placed`,
`check_examples` and `load` do not read `based_on` and do not change. Every refusal below is raised from `origin` as
`InvalidArchitecture` (so its reason is `<location>: <text>`), which `SpecController.origin` and `check_profile`
already turn into `ProfileRefused`, and the CLI into exit 2 with `error: <reason>` on stderr, or the JSON error
document with `--format json` (note line 257: "exit 2").

- **A file of the chain that does not load** (missing, unreadable, or with problems) refuses the profile:

      <writer>: based_on: <value as written> does not load: <its first problem>

  followed by ` (and N more)` when the loader found N > 0 further problems. `<writer>` is the location of the file
  that writes that `based_on` (the profile in force for the first link, as it was given; for a deeper link, the
  resolved location of the file of the chain). `<its first problem>` is the first of `InvalidArchitecture.problems`
  as the loader gives it, which already starts with the resolved location. Example, `mine.yaml` writing
  `based_on: ../team.yaml` from folder `sub/`, `team.yaml` holding only `name: team`:
  `sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: missing \`parts\``.
  A missing file gives the port's own "cannot read the file" problem in the same frame.
- **A loop**: a link whose resolved location is one already in the chain, or the profile in force itself, is refused
  (note lines 259-260). Locations compare after the normalization of §2.2. The reason is said from the file the loop
  comes back to:

      <that file's location>: based_on: <its based_on, as written> is based on this profile[, through <B>]

  where `<B>` is the `based_on` of each file between, as written in each, joined with `, `, and the clause is left
  off when there is none. So `mine.yaml` → `a.yaml` → `mine.yaml` gives `mine.yaml: based_on: a.yaml is based on this
  profile`; `mine.yaml` → `../a.yaml` → `../b.yaml` → back to `mine.yaml` gives `mine.yaml: based_on: ../a.yaml is
  based on this profile, through ../b.yaml` (note line 260); `based_on: mine.yaml` in `mine.yaml` itself gives
  `mine.yaml: based_on: mine.yaml is based on this profile`.

A loop is checked before a load: a link that closes a loop is refused as a loop without reading the file again.

### 2.4 What is compared

For a custom profile whose `based_on` is a path (note lines 262-263):

- The profile in force is compared with the first file of the chain, as `based_on` names it: the match, the pairing,
  `guards off`, `only_here`/`only_there`, `elsewhere` and the looser lines are against that file.
- `Origin.compared` is the path **as written** (`../team.yaml`, not `team.yaml`); `chosen_by` is `based_on`.
- `higher` is the bundled profile of highest match with the profile in force (lowest name on a tie, one no part pairs
  with never) when its match is higher than the match with the path file; else `None`. The path file is never a
  candidate for `higher`.
- No part in common: compared as declared, `low` is true, the reason says "no part in common" (note line 266).

With `--against`, the comparison is with the `--against` profile as 5.3 built it; the chain is still loaded and its
refusals still refuse (§2.3), `Origin.based_on` is the path as written, and `anchor` is `None` (§2.5).

### 2.5 The anchor (`Origin.anchor`)

A new field `anchor: str | None = None`, last in `Origin` (`spec/domain/published.py:146`), on the contract's `Origin`
and on rules' `Resemblance` (`rules/domain/published.py`; appended to the positional construction in
`rules/adapters/spec_profile.py:117-121`). It is the bundled profile `--strict` rests on (note lines 278-280):

| Profile in force | `anchor` |
|---|---|
| bundled, without `--against` | `None` (it is its own baseline; nothing is compared) |
| any, with `--against` | `None` (`--strict` is refused with `--against`) |
| custom, `based_on` a bundled name | that name (== `compared`) |
| custom, no `based_on` (or none in `others`), closest found | the closest (== `compared`) |
| custom, nothing compared | `None` |
| custom, `based_on` a path, chain with a bundled root | the bundled root |
| custom, `based_on` a path, no bundled root | the bundled profile of highest match with the chain's **last file**, lowest name on a tie, one no part of that file pairs with never (the rule of note §3, lines 234-246) |
| as above, no bundled profile pairs with the last file | `None` |

### 2.6 `baseline_off` (the guards `--strict` excuses)

`baseline_off` keeps its meaning for every row of §2.5 but the path rows (note line 282-283):

- Bundled in force without `--against`: its own guards off, as today.
- With `--against`: as 5.3 built it (guards off in both), unchanged; `--strict` never reads it there.
- Custom, `based_on` bundled or closest: the guards it leaves off that the compared profile leaves off, as today.
- Custom, `based_on` a path: each guard the profile in force leaves off that the anchor leaves off **and** every file
  of the chain leaves off, in xarch's order. With no anchor: `()`, no guard excused.

So a guard the path file leaves off while the anchor switches it on is not excused, and a guard the path file switches
on while the anchor leaves it off is not excused either (note lines 290-292). `strict_findings`
(`rules/application/logic/enforcement.py:88`) is unchanged: it already fails each guard off not in `baseline_off`.

### 2.7 `unplaced` (the litmus `--strict` demands)

A part of the profile in force fails `unplaced` when it lacks a litmus that the path file gives the part it pairs with
there, or that the anchor gives the part it pairs with in the anchor (note lines 284-285; dodge line 423). Only the
first file of the chain and the anchor are read for this, not the files between.

`--strict` reads `unplaced` from the `Loosened` entries of key `litmus` in `Origin.looser`
(`enforcement.py:82`, `unplaced`). So for a path `based_on`, `Origin.looser` is:

1. every looser line against the path file, as 5.2 builds them, in their order; then
2. for each part of the profile in force, in its order, that has no litmus, pairs with a part of the anchor that has
   one, and has no `litmus` entry from (1): one entry
   `Loosened("litmus", <part>, <anchor>, "<part> has no litmus, though <anchor>, which --strict rests on, gives the part it pairs with one (parts.<part>.litmus)")`.

No other looser line against the anchor is listed. `profile check` shows these entries in its looser list and `check`'s
enforcement shows them as it shows every looser line; `check --strict` fails on them under `litmus`. For every other
row of §2.5, `looser` is unchanged.

### 2.8 Words and JSON

Only when `based_on` is a path and `--against` is not given (note lines 300-308):

- `profile check` heading: `checking sub/mine.yaml (custom; based_on: ../team.yaml, resting on cli)`; with no anchor,
  `(custom; based_on: ../team.yaml, resting on no bundled profile)`.
- `check` enforcement `profile:` line: `mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict
  rests on cli)`; with no anchor, `...; --strict rests on no bundled profile)`.
- The match line reads `match: N% with ../team.yaml (based_on): ...`, the looser heading `looser than ../team.yaml`,
  as 5.1/5.2 already say them for whatever `compared` holds.

Every other heading and line is unchanged, byte for byte (a bundled `based_on`'s anchor is the compared profile, and
saying it again adds nothing). With `--against` and a path `based_on`, the heading stays 5.3's `(custom; against web,
given with --against; based_on: ../team.yaml)`.

JSON: `compared_with` (`profile_report.py:284`, `compared_document`, read by both `profile check` and `check`'s
`enforcement.profile`) gains `"anchor"`: the `Origin.anchor` value, a bundled name or `null`. It is present whenever
`compared_with` is not `null`. `enforcement.profile.baseline_off` is the §2.6 tuple.

### 2.9 Help, README, CHANGELOG, keys

- `keys.yaml` `based_on` (`xarch/architectures/presets/format/keys.yaml:127-130`): `accepts` becomes the note's text (item
  11, lines 359-361) with its trailing "(4.1)" replaced by the anchor rule: `the name of a bundled profile, or the path of a profile file from this file's folder:
  \`profile check\` and \`check\` compare this one with it, unless \`--against\` names another for the run;
  \`--strict\` rests on a bundled profile: the chain's bundled root, else the bundled profile closest to its last
  file`. `meaning` becomes `the profile this one is based on: the bundled
  one it was copied from, or a profile file`, since the old meaning would contradict `accepts`. `example` stays.
  `CHOICE_BUNDLED` stays the list of bundled names (`services/explanation.py:64`); `tests/bootstrap/project.py`
  `bundled_profiles()` keeps reading it.
- README: the `profile check` paragraph (around line 239, "else the one its `based_on` names") says `based_on` is a
  bundled name or a path read from the folder of the file that writes it, compared as written; the `check`
  enforcement paragraph (around line 451) says the `--strict` anchor rule and gives the two lines of §2.8. Line 229
  (`based_on: BUNDLED` of `profile new`) stays.
- `CHANGELOG.md`, `## [Unreleased]`, `### Added`, one bullet (note item 12, line 362; review 3 O4, O5): `based_on`
  takes a path read from the folder of the file that writes it, the chain and its two refusals, `--strict` rests on a
  bundled anchor (the rule of §2.6 and §2.7), the two lines of §2.8 and `compared_with.anchor`. The other bullets stay.
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated and their diff read, never edited by hand (review 3 O8);
  expected unchanged, since no bundled profile and no template changes.

### 2.10 Interfaces (named for the planner)

- `ArchitectureService.origin(location, against=None)` loads the chain, finds the anchor, and hands `origin_of` what
  it needs; the chain's loading and refusals live in the service, the comparison in `looseness.py` (pure).
- `origin_of(location, architecture, bundled, others, against=None, chain=(), anchor=None)` or an equivalent: `others`
  holds the bundled profiles by name plus, for a path `based_on`, the first file of the chain under its path as
  written (so the existing `architecture.based_on in others` branch, `looseness.py:398`, picks it); `chain` is the
  files of the chain as `Architecture`s, in order; `anchor` is `(name, Architecture)` or `None`. `higher` reads the
  bundled entries only.
- `InvalidArchitecture` (`spec/domain/errors.py`) for both refusals; no new error class is needed.
- `compared_document` and `_origin_words`/`compared_words` in `cli/reports/profile_report.py` and `report.py` read
  `anchor`, and know a path `based_on` by `ArchitectureSource.names_a_file(origin.compared)` with `chosen_by ==
  "based_on"`.

## 3. Tests (written first)

Logic tier, `tests/modules/spec/application/logic/test_profile_parsing.py` (the parser alone; the form of a value is
decided there, without files):

1. `based_on: ../team.yaml`, `team.yaml`, `base/team.json` are accepted, `Architecture.based_on` is the value as
   written, and no problem is reported (no file is consulted).
2. `based_on: mine` → `based_on: no bundled profile 'mine': use cli, web` (existing, unchanged).
3. `based_on: 3` and `based_on: ""` → `based_on: must be the name of a bundled profile or the path of a profile file:
   use cli, web` (line 79 edited).

Logic tier, `tests/modules/spec/application/logic/test_looseness.py` (pure comparison over in-memory profiles; the
excuse and the litmus rules are arithmetic on `Architecture`s):

4. With a chain and an anchor, `baseline_off` is the guards off in force ∩ off in the anchor ∩ off in every chain file.
5. With a chain and no anchor, `baseline_off == ()`.
6. A part with no litmus that the anchor's paired part gives one, and the path file's does not, gets one `litmus`
   entry whose `what` is the anchor and whose sentence is the §2.7 sentence; one the path file already flags gets no
   second entry.
7. `higher` never names the path file; it names a bundled profile of higher match than the path file.
8. A bundled `based_on`: `anchor` equals `compared`, `baseline_off` and `looser` as before (existing tests unedited).

Service tier, `tests/modules/spec/application/test_origin.py` (the controller over `FakeArchitectureFiles`; the
folder a path is read from, the chain and its refusals are decided by the service, and the fake serves files by exact
location, so a wrong folder shows as an unread file; note lines 374-377):

9. `sub/mine.yaml` writing `based_on: ../team.yaml`, the fake serving `team.yaml` (based on `base`) and, under the
   literal key `../team.yaml`, a decoy with other guards: `compared == "../team.yaml"`, `chosen_by == "based_on"`,
   and the comparison is with `team.yaml`'s contents, not the decoy's (read from the profile's folder, not the
   working folder; dodge line 425).
10. A chain file that does not load → `ProfileRefused("sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml:
    missing \`parts\`")`; with three problems, the same with ` (and 2 more)`; a missing file → the reason starts
    `sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: cannot read the file`.
11. A deeper broken link names its writer: `mine.yaml` → `a.yaml` → `b.yaml` broken → reason starts `a.yaml: based_on:
    b.yaml does not load:`.
12. Loops: `mine.yaml` → `a.yaml` → `mine.yaml`; three-file loop with the `through` clause; a self-reference; each
    `ProfileRefused` with the §2.3 reason.
13. Anchor: the chain's bundled root (`mine.yaml` → `team.yaml` → `base`: `anchor == "base"`); no bundled root, the
    bundled profile closest to the last file (`anchor` set though the in-force profile matches another higher); none
    pairing → `anchor is None` and `baseline_off == ()`.
14. A guard the path file leaves off and the anchor switches on is not in `baseline_off` (dodge line 423).
15. A guard the path file switches on and the anchor leaves off is not in `baseline_off`.
16. A litmus the path file gives is demanded (a `litmus` entry against the path file); a litmus the anchor gives the
    paired part is demanded even when the path file drops it (the §2.7 entry) (dodge line 423).
17. With `against="other"` and a path `based_on`: `chosen_by == "against"`, `based_on == "../team.yaml"`,
    `anchor is None`; with the chain broken, still refused.
18. A bundled `based_on` and a closest custom profile: `anchor == compared`; bundled in force: `anchor is None`.

`FakeArchitectureFiles` (`tests/fakes/architecture_files.py`) is used as is: it keys custom files by location; if it
needs a change for these tests, the change is in the fake only.

Adapter tier, `tests/modules/rules/adapters/test_spec_profile.py` (the adapter's translation of spec's contract):

19. `reviewed` carries `anchor` into `Resemblance`; `standing` carries the §2.6 `baseline_off` and the §2.7 `litmus`
    entries into `Standing` (the existing `ORIGIN` constructions keep working, the field has a default).

Rules service tier, `tests/modules/rules/application/logic/test_enforcement.py` or the app-check service tests (that
`--strict` fails on what spec hands it, without the CLI):

20. A `Standing` whose `baseline_off` lacks a guard the profile leaves off fails `guards_off`; one whose `looser`
    carries the §2.7 entry fails `litmus` with its sentence. (Confirms `strict_findings` needs no change.)

Report tier, `tests/cli/reports/test_profile_report.py` and `tests/cli/reports/test_report.py` (the words and JSON of
an `Origin`, without loading anything):

21. The two headings of §2.8 with an anchor and with none; the two `profile:` lines; unchanged lines for a bundled
    `based_on`, closest, nothing compared, and `--against` with a path `based_on`.
22. `compared_with.anchor` in both JSON documents: the name, `null`, and present for a bundled `based_on`.

CLI / bootstrap tier (`tests/bootstrap/test_profile_check.py`, `test_check_enforcement.py`; the real filesystem
adapter and `CliRunner`, since reading from the profile's folder against the working folder is only real on disk):

23. In a tmp project, `architecture/mine/mine.yaml` (a `profile new` copy of cli) rewritten with `based_on:
    ../team/team.yaml`, and `architecture/team/team.yaml` a copy of cli: `profile check architecture/mine/mine.yaml`
    run from the project root exits 0 and heads `checking architecture/mine/mine.yaml (custom; based_on:
    ../team/team.yaml, resting on cli)`; its JSON `compared_with.profile == "../team/team.yaml"`, `anchor == "cli"`.
24. The same with the working folder elsewhere (the profile given by an absolute path): same result (C6).
25. `based_on` to a missing file: `profile check` and `check` exit 2, stderr `error: <...>: based_on: ../team/team.yaml
    does not load: ...`.
26. `check --strict` on the app with `team.yaml` switching off a guard cli switches on, and `mine.yaml` leaving it off:
    exit 1, the guard among the strict failures (the dodge: a lax file of one's own excuses nothing).
27. `check` enforcement `profile:` line `(custom; compared with ../team/team.yaml, based_on; match N%; --strict rests on
    cli)`.
28. `profile explain based_on` prints the §2.9 `accepts`, and its JSON `choices` are still the bundled names
    (`tests/bootstrap/test_profile_explain.py:175-176` stays).

Architecture tier (existing, must stay green unedited): `tests/architecture/test_readme.py`, `test_self_check.py` (no
comments in xarch code), `tests/bootstrap/test_docs.py` (golden docs unchanged), `tests/bootstrap/test_recorded_corpora.py`
(findings do not move; corpora not edited).

## 4. Out of scope

- Changing any bundled profile's `based_on`, or `architecture.yaml`'s / `stress.yaml`'s `based_on: cli` (card).
- The parenthesis the note gives the `--strict --against` refusal (`(based_on: ../team.yaml, resting on cli)`, note
  lines 100-109), which 5.3 §2.5 deferred here: the card lists §4, §4.1 and §5 items 3, 5, 11, 12, not §1, and the
  refusal fires before the profile is chosen or loaded (5.3 §2.5), so naming its anchor would move that refusal after
  profile selection. The refusal keeps 5.3's sentence. Flagged for the owner.
- The match formula, pairing, and 5.2's looser lines (read, not changed); `--against` itself (5.3).
- `based_on` read by any command but `profile check` and `check` (`docs`, `init`, `where`, `review` do not load the
  chain).
- A `based_on` URL or a glob; resolving symlinks when detecting a loop.

## 5. Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: in the background, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check
architecture.yaml` (unchanged: `architecture.yaml` writes `based_on: cli`, so its heading, `match: 80% with cli
(based_on)` and its `compared:` list are as on this branch before the step).

Project rules (card): no comments in xarch's code; tests first; examples simple, absolute `app.` imports; recorded
corpora untouched; Python only in the reader adapter and preset data files; `.claude/` out of commits; nothing pushed;
README and CHANGELOG lines under `[Unreleased]`; golden docs regenerated, never hand-edited.

---

## Global Constraints

- No comments in xarch's code (`tests/architecture/test_self_check.py`); docstrings are how code explains itself, as everywhere in `xarch/`.
- Tests first: every task writes its failing test before the code.
- Examples simple, absolute `app.` imports; recorded corpora (`tests/bootstrap/test_recorded_corpora.py` data) untouched.
- Python only in the reader adapter and preset data files: no Python sits anywhere new.
- `.claude/` stays out of commits; nothing is pushed.
- README and CHANGELOG lines go under `## [Unreleased]`.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated by the tests, never hand-edited; expected unchanged.
- No bundled profile's `based_on` changes, nor `architecture.yaml`'s `based_on: cli`.
- `parse_copy` (`profile new`) keeps writing `based_on: <bundled source>`.
- `--profile` and `--against` keep reading from the working folder; only a `based_on` path is read from the writer's folder.
- Normalization is `posixpath.normpath` of `posixpath.join(posixpath.dirname(writer), value)`; symlinks are never resolved (no `.resolve()`, no `os.path.realpath`; the `pure` and `ambient` never-lists of `architecture.yaml` forbid them anyway).
- `cli/reports/` may import only `contract@any`, `kernel` and `kernel-logic` (`architecture.yaml`, part `reports`). It cannot call `ArchitectureSource.names_a_file`. Spec §2.10 says the reports know a path `based_on` "by `ArchitectureSource.names_a_file(origin.compared)` with `chosen_by == "based_on"`". The plan uses an equivalent the reports may import: a path `based_on` is `chosen_by == BASED_ON` and `anchor != compared`. With real data, a bundled `based_on`'s anchor is the compared name (§2.5), and a path is never a bundled name (§2.1: no bundled name holds `/` or a dot). `Origin`'s docstring states this, and `BASED_ON` is re-exported from the contract.
- Gates, on this branch alone: `uv run pytest -q` (over two minutes: run it in the background and read the result at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml` (text output unchanged from before the step).
- Stop a stuck command with `timeout`, e.g. `timeout 600 uv run pytest -q`; never `pkill`/`killall`.

## Review Focus

1. **A `based_on` path spelled with `.` steps or a redundant `x/..`** (`./team.yaml`, `./x/../team.yaml`): it must read the same file and detect the same loops as the plain spelling. Pinned in Task 2 (`resolved` table, `./mine.yaml` loop row).
2. **A `based_on` path with a folder but no suffix that normalizes to one bare step** (`../team` from `sub/` → `team`): it must be read as a file even when a bundled profile has that name. Pinned in Task 4 (`test_a_based_on_path_with_no_suffix_is_read_as_a_file_and_never_as_a_bundled_name`).
3. **A loop that does not pass through the profile in force** (`mine → a → b → a`): it must be refused, said from `a.yaml`, and must not hang. Pinned in Task 2 (loop table) and Task 4 (service loop table).
4. **Commands other than `profile check`/`check` with a broken chain**: `profile`, `docs`, `files`, `init` must keep working, since only `origin` reads the chain. Pinned in Task 4 (`test_only_the_origin_reads_the_chain_...`).
5. **A profile given by an absolute path, run from another working folder**: the chain must be read from the profile's folder, not the working folder. Pinned in Task 2 (`/abs/p/mine.yaml` row) and Task 8 (CLI test from an unrelated working folder).

---

## File Structure

- Modify `xarch/modules/spec/application/logic/profile_parsing.py` (`_based_on`): a path is accepted by its form.
- Modify `xarch/modules/spec/domain/published.py` (`Origin.anchor`, docstrings of `Origin` and `Loosened`).
- Modify `xarch/modules/spec/application/logic/looseness.py`: `origin_of(..., chain=())`, `_closest`, `_resting`, the anchor's litmus sentence, module docstring.
- Create `xarch/modules/spec/application/logic/profile_chain.py`: `Link`, `based_on_a_file`, `resolved`, `refuse_loop`, `unloaded`. Pure; one responsibility: where a `based_on` path is read from and when a chain loops.
- Modify `xarch/modules/spec/application/services/architecture.py`: `origin` loads the chain through a new `_chain`.
- Modify `xarch/modules/spec/contract/__init__.py`: re-export `BASED_ON`.
- Modify `xarch/modules/rules/domain/published.py` (`Resemblance.anchor`) and `xarch/modules/rules/adapters/spec_profile.py` (carry it).
- Modify `xarch/cli/reports/profile_report.py`: `_rests`, `_origin_words`, `compared_words`, `compared_document`, module docstring.
- Modify `xarch/architectures/presets/format/keys.yaml` (`based_on`'s `meaning` and `accepts`).
- Modify `README.md`, `CHANGELOG.md`.
- Tests: `tests/modules/spec/application/logic/test_profile_parsing.py`, `.../logic/test_looseness.py`, new `.../logic/test_profile_chain.py`, `tests/modules/spec/application/test_origin.py`, `.../test_check.py`, `.../test_explain.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/rules/application/logic/test_enforcement.py`, `tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py`, `tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_enforcement.py`, `tests/bootstrap/test_profile_explain.py`.

---

### Task 1: The parser accepts a `based_on` path by its form

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:115-130` (import), `:249-257` (`_based_on`)
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py:73-76`

**Interfaces:**
- Consumes: `ArchitectureSource.names_a_file(location: str | Path) -> bool` (`xarch/modules/spec/domain/values.py:474`).
- Produces: `Architecture.based_on` holds a path exactly as written (e.g. `"../team.yaml"`), or a bundled name, or `""`.

- [ ] **Step 0: Record the baseline the last gate compares with**

Run: `uv run xarch profile check architecture.yaml > /tmp/xarch-profile-check-before.txt; echo $?`
Expected: `0`, and the file's first line is `checking architecture.yaml (custom; based_on: cli)`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_parsing.py`, replace the whole function `test_based_on_names_a_bundled_profile_and_nothing_else` (lines 73-76) with:

```python
def test_based_on_names_a_bundled_profile_and_nothing_else():
    assert parsed(layered(based_on="web")).based_on == "web"
    assert problems(layered(based_on="mine")) == ["layered.yaml: based_on: no bundled profile 'mine': use cli, web"]
    assert problems(layered(based_on=3)) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file: use cli, web"]
    assert problems(layered(based_on="")) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file: use cli, web"]
    assert problems(layered(based_on=3), bundled=()) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file"]


@pytest.mark.parametrize("path", ["../team.yaml", "team.yaml", "base/team.json"])
def test_based_on_a_path_is_kept_as_written_without_reading_any_file(path):
    assert parsed(layered(based_on=path)).based_on == path
```

(`parsed` and `problems` come from `tests/modules/spec/profiles.py`; `bundled` defaults to `("cli", "web")`. Neither reads a file, so a path that names no file is accepted, which is the point.)

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py -k based_on -v`
Expected: FAIL. `test_based_on_names_a_bundled_profile_and_nothing_else` fails on the message without "or the path of a profile file". The three `test_based_on_a_path_is_kept_as_written...` cases fail with `InvalidArchitecture` (`no bundled profile '../team.yaml'`).

- [ ] **Step 3: Implement**

In `xarch/modules/spec/application/logic/profile_parsing.py`, add `ArchitectureSource,` to the import from `xarch.modules.spec.domain.values` (keep it sorted: right after `Architecture,`):

```python
from xarch.modules.spec.domain.values import (
    Architecture,
    ArchitectureSource,
    DeadCode,
```

Replace `_based_on` (lines 249-257) with:

```python
def _based_on(value: Any, bundled: Collection[str], problems: list[str]) -> str:
    """The profile the file says it is based on: a bundled name, or the path of a profile file, which is taken as
    written and read by no one here."""
    use = f": use {', '.join(bundled)}" if bundled else ""
    if not isinstance(value, str) or not value:
        problems.append(f"based_on: must be the name of a bundled profile or the path of a profile file{use}")
    elif ArchitectureSource.names_a_file(value):
        return value
    elif value not in bundled:
        problems.append(f"based_on: no bundled profile {value!r}{use}")
    else:
        return value
    return ""
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py -v`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing.py
git commit -m "based_on accepts the path of a profile file by its form alone, a folder step or a suffix, kept as written and read by no one in the parser; a value that is not a string, or the empty string, is refused as neither a bundled name nor a path"
```

---

### Task 2: Where a `based_on` path is read from, and the loop a chain may close (pure logic)

**Files:**
- Create: `xarch/modules/spec/application/logic/profile_chain.py`
- Test: `tests/modules/spec/application/logic/test_profile_chain.py` (new)

**Interfaces:**
- Consumes: `ArchitectureSource.names_a_file`, `InvalidArchitecture(source: str, problems: Iterable[str])` (`reason` is `"<source>: <problem>"` per line).
- Produces (used by Task 4):
  - `Link = tuple[str, str]`: `(location as said, based_on as written)`
  - `based_on_a_file(based_on: str) -> bool`
  - `resolved(writer: str, based_on: str) -> str`
  - `refuse_loop(links: Sequence[Link], target: str) -> None`: raises `InvalidArchitecture`
  - `unloaded(based_on: str, problems: Sequence[str]) -> str`

- [ ] **Step 1: Write the failing tests**

Create `tests/modules/spec/application/logic/test_profile_chain.py`:

```python
"""Where a based_on path is read from, the folder of the file that writes it, and the loop a chain of profile files
may close, said from the file the loop comes back to."""
import pytest

from xarch.modules.spec.application.logic.profile_chain import based_on_a_file, refuse_loop, resolved, unloaded
from xarch.modules.spec.domain.errors import InvalidArchitecture


@pytest.mark.parametrize("based_on, file", [
    pytest.param("../team.yaml", True, id="a folder step and a suffix"),
    pytest.param("team.yaml", True, id="a suffix"),
    pytest.param("base/team", True, id="a folder step"),
    pytest.param("cli", False, id="a bare name is a bundled profile"),
    pytest.param("", False, id="no based_on names nothing"),
])
def test_a_based_on_names_a_profile_file_when_it_has_a_folder_step_or_a_suffix(based_on, file):
    assert based_on_a_file(based_on) is file


@pytest.mark.parametrize("writer, based_on, found", [
    pytest.param("sub/mine.yaml", "../team.yaml", "team.yaml", id="from the folder of the file that writes it"),
    pytest.param("/abs/p/mine.yaml", "team.yaml", "/abs/p/team.yaml", id="an absolute writer keeps its folder"),
    pytest.param("mine.yaml", "../a.yaml", "../a.yaml", id="a writer in the working folder"),
    pytest.param("sub/mine.yaml", "./x/../team.yaml", "sub/team.yaml", id="dot steps are collapsed as text"),
    pytest.param("sub/mine.yaml", "../team", "team", id="a single step with no suffix is left as it is"),
])
def test_a_based_on_path_is_read_from_the_folder_of_the_file_that_writes_it(writer, based_on, found):
    assert resolved(writer, based_on) == found


@pytest.mark.parametrize("links, target, reason", [
    pytest.param([("mine.yaml", "mine.yaml")], "mine.yaml",
                 "mine.yaml: based_on: mine.yaml is based on this profile", id="a profile based on itself"),
    pytest.param([("mine.yaml", "a.yaml"), ("a.yaml", "mine.yaml")], "mine.yaml",
                 "mine.yaml: based_on: a.yaml is based on this profile", id="two files say no file between"),
    pytest.param([("p/q/mine.yaml", "../a.yaml"), ("p/a.yaml", "../b.yaml"), ("b.yaml", "p/q/mine.yaml")],
                 "p/q/mine.yaml", "p/q/mine.yaml: based_on: ../a.yaml is based on this profile, through ../b.yaml",
                 id="three files name the based_on of the one between"),
    pytest.param([("mine.yaml", "a.yaml"), ("a.yaml", "b.yaml"), ("b.yaml", "a.yaml")], "a.yaml",
                 "a.yaml: based_on: b.yaml is based on this profile",
                 id="a loop the profile in force is not in is said from the file it comes back to"),
    pytest.param([("./mine.yaml", "mine.yaml")], "mine.yaml",
                 "./mine.yaml: based_on: mine.yaml is based on this profile",
                 id="locations are compared once normalized and said as given"),
])
def test_a_link_back_to_a_file_of_the_chain_is_refused(links, target, reason):
    with pytest.raises(InvalidArchitecture) as caught:
        refuse_loop(links, target)
    assert caught.value.reason == reason


def test_a_link_to_a_file_not_yet_in_the_chain_passes():
    assert refuse_loop([("sub/mine.yaml", "../team.yaml")], "team.yaml") is None


def test_a_file_of_the_chain_that_does_not_load_is_said_with_its_first_problem_and_how_many_more():
    assert unloaded("../team.yaml", ("team.yaml: missing `parts`",)) == (
        "based_on: ../team.yaml does not load: team.yaml: missing `parts`")
    assert unloaded("../team.yaml", ("team.yaml: a", "team.yaml: b", "team.yaml: c")) == (
        "based_on: ../team.yaml does not load: team.yaml: a (and 2 more)")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_chain.py -v`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'xarch.modules.spec.application.logic.profile_chain'`.

- [ ] **Step 3: Implement**

Create `xarch/modules/spec/application/logic/profile_chain.py`:

```python
"""The profile files a profile is based on when its based_on is a path: each read from the folder of the file that
writes it, and the loop a chain of them may close, which refuses the profile."""
from __future__ import annotations

import posixpath
from collections.abc import Sequence

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureSource

Link = tuple[str, str]
"""(location, based_on): a profile of a chain, where it is as said, and its based_on as written."""


def based_on_a_file(based_on: str) -> bool:
    """Whether a based_on names a profile file rather than a bundled profile; an empty one names neither."""
    return bool(based_on) and ArchitectureSource.names_a_file(based_on)


def resolved(writer: str, based_on: str) -> str:
    """Where a based_on path is read from: joined to the folder of the file that writes it, its `.` and `..` steps
    collapsed as text, no link followed."""
    return posixpath.normpath(posixpath.join(posixpath.dirname(writer), based_on))


def refuse_loop(links: Sequence[Link], target: str) -> None:
    """Raises InvalidArchitecture when target, where the last link's based_on is read from, is a profile of the chain
    already: said from the profile the loop comes back to, with the based_on of each profile between."""
    places = [posixpath.normpath(location) for location, _ in links]
    if target not in places:
        return
    back = places.index(target)
    location, based_on = links[back]
    between = [written for _, written in links[back + 1:-1]]
    through = f", through {', '.join(between)}" if between else ""
    raise InvalidArchitecture(location, [f"based_on: {based_on} is based on this profile{through}"])


def unloaded(based_on: str, problems: Sequence[str]) -> str:
    """A based_on whose file does not load, as said from the file that writes it: the loader's first problem, which
    starts with where that file is, and how many more it found."""
    more = f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""
    return f"based_on: {based_on} does not load: {problems[0]}{more}"
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_chain.py -v && uv run ruff check xarch/modules/spec/application/logic/profile_chain.py tests/modules/spec/application/logic/test_profile_chain.py`
Expected: PASS (13 tests), `All checks passed!`

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_chain.py tests/modules/spec/application/logic/test_profile_chain.py
git commit -m "A based_on path is read from the folder of the file that writes it, its dot steps collapsed as text; a link back to a profile of the chain is refused, said from the profile the loop comes back to with the based_on of each between, and a file that does not load is said with its first problem and how many more"
```

---

### Task 3: `Origin.anchor`, and the comparison with a chain (pure logic)

**Files:**
- Modify: `xarch/modules/spec/domain/published.py:107-125` (`Loosened` docstring line `litmus`), `:146-184` (`Origin`)
- Modify: `xarch/modules/spec/application/logic/looseness.py` (module docstring, imports at `:47`, `origin_of` at `:382-403`, new `_closest` and `_resting`, `_sentence` at `:425-426`)
- Test: `tests/modules/spec/application/logic/test_looseness.py` (append), `tests/modules/spec/application/test_check.py:23` (`COPY`)

**Interfaces:**
- Consumes: `Architecture.based_on` (Task 1).
- Produces (used by Tasks 4, 5, 6):
  - `Origin.anchor: str | None = None`, the last field of `Origin`.
  - `origin_of(location: str, architecture: Architecture, bundled: bool, others: Mapping[str, Architecture], against: str | None = None, chain: Sequence[Architecture] = ()) -> Origin`. `others` holds **only the bundled profiles** by name (or, with `against`, the one profile `against` names). `chain` holds the files of the chain in order. When `chain` is non-empty, the profile is compared with `chain[0]` under `architecture.based_on` as written.
  - A `Loosened("litmus", <part>, <anchor>, <sentence>)` entry whose `what` is the anchor.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_looseness.py`, add the import `from xarch.modules.spec.domain.guards import ORDER` (sorted among the `xarch.` imports, before `from xarch.modules.spec.domain.published import Loosened, Origin`). Then append at the end of the file:

```python
def test_a_profile_based_on_a_profile_file_excuses_only_the_guards_the_anchor_and_every_file_of_the_chain_leave_off():
    mine = replace(parsed(layered(guards={"no-comments": {}})), based_on="team.yaml")
    team = parsed(layered(based_on="cli", guards={"private-imports": {}}))
    origin = origin_of("mine.yaml", mine, False, {"cli": parsed(layered(guards={"closed-tree": {}}))}, chain=(team,))
    assert (origin.compared, origin.chosen_by, origin.anchor) == ("team.yaml", "based_on", "cli")
    assert origin.baseline_off == tuple(g for g in ORDER if g not in {"no-comments", "closed-tree", "private-imports"})


def test_a_chain_no_bundled_profile_pairs_with_rests_on_none_and_excuses_no_guard():
    mine = replace(parsed(layered()), based_on="team.yaml")
    origin = origin_of("mine.yaml", mine, False, {"cli": bare(web="web")}, chain=(bare(x="x"),))
    assert (origin.compared, origin.chosen_by, origin.anchor, origin.baseline_off) == ("team.yaml", "based_on", None, ())
    assert origin.low is True


def test_a_part_the_anchor_gives_a_litmus_is_listed_once_after_the_ways_it_is_looser_than_the_file():
    anchor = layered()
    anchor["parts"]["api"]["litmus"] = "Does it answer a request?"
    anchor["parts"]["service"]["litmus"] = "Does it decide?"
    team = layered(based_on="cli")
    team["parts"]["api"]["litmus"] = "Does it answer a request?"
    mine = replace(parsed(layered()), based_on="team.yaml")
    origin = origin_of("mine.yaml", mine, False, {"cli": parsed(anchor)}, chain=(parsed(team),))
    assert origin.looser == (
        Loosened("litmus", "api", "",
                 "api has no litmus, though the profile it is compared with gives it one (parts.api.litmus)"),
        Loosened("litmus", "service", "cli",
                 "service has no litmus, though cli, which --strict rests on, gives the part it pairs with one "
                 "(parts.service.litmus)"))


def test_the_profile_file_based_on_names_is_never_said_to_match_higher_and_a_bundled_one_of_higher_match_is():
    mine = replace(bare(a="a", b="b", c="c"), based_on="team.yaml")
    low = origin_of("mine.yaml", mine, False, {"near": bare(a="a", b="b", c="c")}, chain=(bare(a="a"),))
    assert (low.compared, low.higher) == ("team.yaml", ("near", 1.0))
    high = origin_of("mine.yaml", mine, False, {"far": bare(a="a")}, chain=(bare(a="a", b="b", c="c"),))
    assert (high.compared, high.match, high.higher) == ("team.yaml", 1.0, None)


def test_a_profile_compared_with_a_bundled_one_rests_on_it_and_any_other_rests_on_none():
    mine = bare(a="a", b="b", c="c")
    bundled = {"alpha": bare(a="a", b="b", c="c"), "beta": bare(a="a")}
    assert origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled).anchor == "beta"
    assert origin_of("mine.yaml", mine, False, bundled).anchor == "alpha"
    assert origin_of("mine.yaml", mine, False, {"other": bare(web="web")}).anchor is None
    assert origin_of("alpha", mine, True, {}).anchor is None
    assert origin_of("mine.yaml", mine, False, {"alpha": bare(a="a")}, against="alpha").anchor is None
```

(`bare`, `parsed`, `layered`, `replace` and `Loosened` are already in the file. `layered(...)` builds a fresh dict on every call, so changing one does not touch another. A bundled `based_on`'s `baseline_off` and `looser` are pinned by the existing tests, which stay as they are, spec test 8.)

In `tests/modules/spec/application/test_check.py`, line 23, the service now sets `anchor` for a bundled `based_on`. Replace:

```python
COPY = Origin("mine.yaml", False, "base", OFF, OFF, (), "based_on", 1.0, False, SELF)
```

with:

```python
COPY = Origin("mine.yaml", False, "base", OFF, OFF, (), "based_on", 1.0, False, SELF, anchor="base")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_check.py -q`
Expected: FAIL. The new looseness tests fail with `TypeError: origin_of() got an unexpected keyword argument 'chain'`, or `AttributeError: 'Origin' object has no attribute 'anchor'`. `test_check.py` fails at import with `TypeError: Origin.__init__() got an unexpected keyword argument 'anchor'`.

- [ ] **Step 3: Add `anchor` to `Origin`**

In `xarch/modules/spec/domain/published.py`, in the `Origin` docstring, replace:

```
    compared: the profile it is compared with, as its location is given: for a custom file the bundled one, and for
        either the one --against names; None when it is bundled and --against is not given, or none is
    guards_off: the guards xarch has that it leaves off, in xarch's order
    baseline_off: those the profile it is, or is compared with, leaves off too
```

with:

```
    compared: the profile it is compared with, as its location is given: for a custom file the bundled one, or the
        profile file its based_on names, as written there; for either the one --against names; None when it is
        bundled and --against is not given, or none is
    guards_off: the guards xarch has that it leaves off, in xarch's order
    baseline_off: those the profile it is, or is compared with, leaves off too; for one based on a profile file, those
        the anchor and every file of the chain leave off too, none when there is no anchor
```

and replace:

```
    based_on: with --against, the profile its own based_on names, which the command line says beside it; empty
        otherwise
    """
```

with:

```
    based_on: with --against, the profile its own based_on names, which the command line says beside it; empty
        otherwise
    anchor: the bundled profile --strict rests on: the one compared with when that one is bundled (so a profile file
        is compared with exactly when chosen_by is BASED_ON and anchor is not compared); for one based on a profile
        file, the bundled profile the chain of files ends on, else the bundled profile of highest match with its last
        file; None for a bundled profile without --against, with --against, and when there is none
    """
```

and after the last field `    based_on: str = ""` add:

```python
    anchor: str | None = None
```

In the `Loosened` docstring, replace the line:

```
        litmus          part has no litmus, though the bundled profile gives it one (LITMUS)
```

with:

```
        litmus          part has no litmus, though the bundled profile gives it one (LITMUS); with what, though
                        what, the anchor --strict rests on, gives the part it pairs with one
```

(If the line already reads "the profile it is compared with" instead of "the bundled profile", keep that wording in the replacement and only add the "; with what, ..." clause.)

- [ ] **Step 4: Compare with a chain in `looseness.py`**

In `xarch/modules/spec/application/logic/looseness.py`, change the import on line 47 to:

```python
from collections.abc import Collection, Mapping, Sequence
```

Replace the whole `origin_of` function (lines 382-403) with:

```python
def origin_of(location: str, architecture: Architecture, bundled: bool, others: Mapping[str, Architecture],
              against: str | None = None, chain: Sequence[Architecture] = ()) -> Origin:
    """Where the architecture at location comes from: a bundled one is its own baseline; a custom one is compared with
    the one of others, the bundled architectures by name, it says it is based on, else the one of highest match (the
    first by name on a tie, one no part pairs with never), and is looser than it in the ways it says. With chain, the
    profile files its based_on leads through when it is a path, in order, it is compared with the first, called by its
    based_on as written, which is never said to match higher, and --strict rests on the anchor (see _resting). With
    against, the name others holds the one profile --against names by, either is compared with that one alone, even
    when no part pairs, and no other is said to match higher."""
    if against is not None:
        return _compared(location, architecture, bundled, others[against], against, AGAINST, architecture.based_on)
    off = _guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    highest, best = _closest(architecture, others)
    if chain:
        name, chosen_by, base = architecture.based_on, BASED_ON, chain[0]
    elif architecture.based_on in others:
        name, chosen_by, base = architecture.based_on, BASED_ON, others[architecture.based_on]
    elif highest is not None:
        name, chosen_by, base = highest, CLOSEST, others[highest]
    else:
        return Origin(location, False, None, off, (), ())
    share = _share(_counts(architecture, base))
    origin = replace(_compared(location, architecture, False, base, name, chosen_by), anchor=name,
                     higher=(highest, round(float(best), 2)) if highest is not None and best > share else None)
    return _resting(origin, architecture, chain, others) if chain else origin


def _closest(architecture: Architecture, others: Mapping[str, Architecture]) -> tuple[str | None, Fraction]:
    """The one of others of highest match with the architecture, the first by name on a tie, one no part pairs with
    never, and that match; None and no match when none is left."""
    shares = {name: _share(_counts(architecture, other)) for name, other in others.items()
              if _paired_parts(architecture, other)}
    best = max(shares.values(), default=Fraction(0))
    return min((name for name, share in shares.items() if share == best), default=None), best


def _resting(origin: Origin, architecture: Architecture, chain: Sequence[Architecture],
             bundled: Mapping[str, Architecture]) -> Origin:
    """The origin of a profile compared with the profile file its based_on names, as --strict rests on its anchor:
    the bundled profile the last file of the chain says it is based on, else the one of highest match with that file.
    A guard left off is excused only when the anchor and every file of the chain leave it off too, none with no
    anchor; each part with no litmus that pairs with a part the anchor gives one, and that the comparison with the file
    does not list already, is listed after the ways it is looser than the file."""
    last = chain[-1]
    anchor = last.based_on if last.based_on in bundled else _closest(last, bundled)[0]
    if anchor is None:
        return replace(origin, baseline_off=(), anchor=None)
    base = bundled[anchor]
    excused = set(_guards_off(base)).intersection(*(_guards_off(file) for file in chain))
    listed = {item.part for item in origin.looser if item.key == LITMUS}
    pairs = _paired_parts(architecture, base)
    demanded = tuple(Loosened(LITMUS, name, anchor, _sentence(LITMUS, name, anchor))
                     for name, part in architecture.parts.items()
                     if not part.litmus and name in pairs and base.parts[pairs[name]].litmus and name not in listed)
    return replace(origin, baseline_off=tuple(g for g in origin.guards_off if g in excused),
                   looser=origin.looser + demanded, anchor=anchor)
```

In `_sentence`, directly above the existing arm

```python
        case "litmus":
            return f"{part} has no litmus, though the profile it is compared with gives it one (parts.{part}.litmus)"
```

add the arm:

```python
        case "litmus" if what:
            return (f"{part} has no litmus, though {what}, which --strict rests on, gives the part it pairs with one "
                    f"(parts.{part}.litmus)")
```

At the end of the module docstring, directly after the sentence ending `... (the layout, new parts, the guards'\nother parameters, \`fakes\`), is not listed.`, add a new paragraph before the closing `"""`:

```

A custom profile whose `based_on` is the path of a profile file is compared with that file, called by its path as
written, and is handed the files of its chain in order: that one, the one it names in turn, and so on; no file of the
chain is a candidate for the bundled profile of higher match. `--strict` then rests on the anchor: the bundled profile
the last file says it is based on, else the one of highest match with it, else none. A guard left off is excused only
when the anchor and every file of the chain leave it off too, and a part with no litmus that pairs with a part the
anchor gives one is listed under `litmus` too, after the ways it is looser than the file, unless that comparison lists
it already.
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_check.py tests/modules/spec/application/test_origin.py tests/modules/spec/application/test_profile_loading.py -q`
Expected: PASS (all). The existing `origin_of` tests are not edited.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/domain/published.py xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_check.py
git commit -m "Origin names the bundled profile --strict rests on, its anchor: the compared one when that is bundled, and for a profile compared with a chain of profile files the bundled profile the chain ends on, else the one closest to its last file; a guard is excused only when the anchor and every file leave it off, and a part lacking the litmus the anchor gives the part it pairs with is listed under litmus"
```

---

### Task 4: The service loads the chain, and its refusals refuse the profile

**Files:**
- Modify: `xarch/modules/spec/application/services/architecture.py:18-29` (imports), `:114-123` (`origin`), new `_chain` after `_against` (`:125-130`)
- Test: `tests/modules/spec/application/test_origin.py` (append)

**Interfaces:**
- Consumes: `based_on_a_file`, `resolved`, `refuse_loop`, `unloaded`, `Link` (Task 2). `origin_of(..., chain=...)` (Task 3). `ArchitectureService.load(location: str | Path) -> Architecture`.
- Produces: `ArchitectureService.origin(location, against=None)`. It raises `InvalidArchitecture` (which the controller turns into `ProfileRefused`) for a chain file that does not load, or for a loop. The chain is loaded before `against` is read.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/test_origin.py`, change the contract import to:

```python
from xarch.modules.spec.contract import Loosened, Origin, ProfileRefused, ProfileView
```

and append:

```python
TEAM = {**BASE, "name": "team", "based_on": "base", "guards": {"no-comments": {}, "closed-tree": {}}}
"""A profile file based on base that switches closed-tree on too."""
LIT = {**BASE, "name": "lit", "parts": {**PARTS, "core": {**PARTS["core"], "litmus": "Does it decide?"},
                                       "store": {**PARTS["store"], "litmus": "Does it keep?"}}}
"""A bundled profile that gives core and store a litmus."""


def chained(files: dict, bundled: dict | None = None) -> SpecController:
    """The controller over base and other, bundled (or the bundled profiles given), and the profile files given, by
    their exact location: a file read from a wrong folder is a file that cannot be read."""
    return spec_controller(FakeArchitectureFiles({"base": BASE, "other": OTHER} if bundled is None else bundled, files,
                                                 {"guard.py": "check()\n"}))


def test_a_based_on_path_is_read_from_the_folder_of_the_profile_and_compared_with_as_written():
    decoy = {**BASE, "name": "decoy", "guards": {}}
    mine = {**TEAM, "name": "mine", "based_on": "../team.yaml"}
    origin = chained({"sub/mine.yaml": mine, "team.yaml": TEAM, "../team.yaml": decoy}).origin("sub/mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.anchor) == ("../team.yaml", "based_on", "base")
    assert (origin.match, origin.looser) == (1.0, ())


def test_a_based_on_path_with_no_suffix_is_read_as_a_file_and_never_as_a_bundled_name():
    mine = {**TEAM, "name": "mine", "based_on": "../team"}
    origin = chained({"sub/mine.yaml": mine, "team": TEAM}, {"base": BASE, "team": OTHER}).origin("sub/mine.yaml")
    assert (origin.compared, origin.match, origin.anchor) == ("../team", 1.0, "base")


MINE = {**BASE, "name": "mine", "based_on": "../team.yaml"}
"""A copy of base at sub/mine.yaml based on team.yaml, by its path from sub/."""


def test_a_file_of_the_chain_that_does_not_load_refuses_the_profile_with_its_first_problem():
    assert chained({"sub/mine.yaml": MINE, "team.yaml": {"name": "team"}}).origin("sub/mine.yaml") == ProfileRefused(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: missing `parts`")
    many = chained({"sub/mine.yaml": MINE, "team.yaml": {"colour": 1}}).origin("sub/mine.yaml")
    assert many.reason.startswith(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: unknown key 'colour'")
    assert many.reason.endswith(" (and 2 more)")
    assert chained({"sub/mine.yaml": MINE}).origin("sub/mine.yaml") == ProfileRefused(
        "sub/mine.yaml: based_on: ../team.yaml does not load: team.yaml: cannot read the file: no such file")


def test_a_deeper_file_that_does_not_load_is_said_from_the_file_of_the_chain_that_names_it():
    files = {"mine.yaml": {**BASE, "name": "mine", "based_on": "a.yaml"},
             "a.yaml": {**BASE, "name": "a", "based_on": "b.yaml"}, "b.yaml": {"name": "b"}}
    assert chained(files).origin("mine.yaml") == ProfileRefused(
        "a.yaml: based_on: b.yaml does not load: b.yaml: missing `parts`")


@pytest.mark.parametrize("files, location, reason", [
    pytest.param({"mine.yaml": {**BASE, "based_on": "a.yaml"}, "a.yaml": {**BASE, "based_on": "mine.yaml"}},
                 "mine.yaml", "mine.yaml: based_on: a.yaml is based on this profile", id="two files"),
    pytest.param({"p/q/mine.yaml": {**BASE, "based_on": "../a.yaml"}, "p/a.yaml": {**BASE, "based_on": "../b.yaml"},
                  "b.yaml": {**BASE, "based_on": "p/q/mine.yaml"}},
                 "p/q/mine.yaml", "p/q/mine.yaml: based_on: ../a.yaml is based on this profile, through ../b.yaml",
                 id="three files name the one between"),
    pytest.param({"mine.yaml": {**BASE, "based_on": "mine.yaml"}}, "mine.yaml",
                 "mine.yaml: based_on: mine.yaml is based on this profile", id="a profile based on itself"),
    pytest.param({"mine.yaml": {**BASE, "based_on": "a.yaml"}, "a.yaml": {**BASE, "based_on": "b.yaml"},
                  "b.yaml": {**BASE, "based_on": "a.yaml"}},
                 "mine.yaml", "a.yaml: based_on: b.yaml is based on this profile",
                 id="a loop the profile in force is not in"),
])
def test_a_chain_that_comes_back_to_a_file_of_it_refuses_the_profile(files, location, reason):
    assert chained(files).origin(location) == ProfileRefused(reason)


def test_the_anchor_is_the_bundled_profile_the_chain_ends_on_else_the_one_closest_to_its_last_file_else_none():
    ends = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": TEAM})
    assert ends.origin("mine.yaml").anchor == "base"
    closest = chained({"mine.yaml": {**OTHER, "name": "mine", "based_on": "team.yaml"},
                       "team.yaml": {**BASE, "name": "team"}}).origin("mine.yaml")
    assert (closest.anchor, closest.higher[0]) == ("base", "other")
    alone = {"name": "alone", "parts": {"y": {"path": "y", "role": "all"}}}
    none = chained({"mine.yaml": {**alone, "name": "mine", "based_on": "team.yaml"}, "team.yaml": alone}).origin(
        "mine.yaml")
    assert (none.anchor, none.baseline_off) == (None, ())


def test_a_guard_the_profile_file_leaves_off_and_the_anchor_switches_on_is_not_excused():
    lax = {**BASE, "guards": {}}
    origin = chained({"mine.yaml": {**lax, "name": "mine", "based_on": "team.yaml"},
                      "team.yaml": {**lax, "name": "team", "based_on": "base"}}).origin("mine.yaml")
    assert "no-comments" in origin.guards_off and "no-comments" not in origin.baseline_off
    assert origin.baseline_off == OFF


def test_a_guard_the_profile_file_switches_on_and_the_anchor_leaves_off_is_not_excused():
    origin = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"},
                      "team.yaml": TEAM}).origin("mine.yaml")
    assert "closed-tree" in origin.guards_off and "closed-tree" not in origin.baseline_off


def test_a_litmus_the_profile_file_gives_and_one_the_anchor_gives_are_both_demanded():
    team = {**BASE, "name": "team", "based_on": "lit", "parts": part("store", litmus="Does it keep?")}
    origin = chained({"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": team},
                     {"lit": LIT}).origin("mine.yaml")
    assert origin.looser == (
        Loosened("litmus", "store", "",
                 "store has no litmus, though the profile it is compared with gives it one (parts.store.litmus)"),
        Loosened("litmus", "core", "lit",
                 "core has no litmus, though lit, which --strict rests on, gives the part it pairs with one "
                 "(parts.core.litmus)"))


def test_with_against_a_path_based_on_is_said_beside_it_rests_on_nothing_and_its_chain_still_refuses():
    files = {"mine.yaml": {**BASE, "name": "mine", "based_on": "team.yaml"}, "team.yaml": TEAM}
    origin = chained(files).origin("mine.yaml", against="other")
    assert (origin.compared, origin.chosen_by, origin.based_on, origin.anchor) == (
        "other", "against", "team.yaml", None)
    broken = chained({"mine.yaml": files["mine.yaml"]}).origin("mine.yaml", against="other")
    assert broken == ProfileRefused(
        "mine.yaml: based_on: team.yaml does not load: team.yaml: cannot read the file: no such file")


def test_a_bundled_based_on_or_the_closest_is_the_anchor_and_a_bundled_profile_rests_on_none():
    assert against({**BASE, "based_on": "base"}).origin("mine.yaml").anchor == "base"
    assert controller(BASE).origin("mine.yaml").anchor == "base"
    assert controller(BASE).origin("base").anchor is None


def test_only_the_origin_reads_the_chain_so_the_profile_loads_with_its_based_on_file_missing():
    spec = chained({"sub/mine.yaml": MINE})
    assert isinstance(spec.profile("sub/mine.yaml"), ProfileView)
    assert isinstance(spec.origin("sub/mine.yaml"), ProfileRefused)
```

(`BASE`, `OTHER`, `OFF`, `PARTS`, `part` come from `tests/modules/spec/application/origins.py`, already imported. `against` and `controller` are this file's existing helpers. `BASE` switches on only `no-comments`, and `OFF` is every other guard in xarch's order. `FakeArchitectureFiles` serves a custom file only by its exact location, so a file read from the wrong folder raises `cannot read the file: no such file`.)

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/test_origin.py -q`
Expected: FAIL. The new path tests fail: without the chain, `based_on: ../team.yaml` is not in `others`, so the profile is compared with the closest bundled one (`compared == "base"`), or no `ProfileRefused` comes back. `test_only_the_origin_reads_the_chain...` fails on its second assert. `test_a_bundled_based_on_or_the_closest...` passes already (Task 3).

- [ ] **Step 3: Implement**

In `xarch/modules/spec/application/services/architecture.py`, add after the `looseness` import (line 18):

```python
from xarch.modules.spec.application.logic.profile_chain import Link, based_on_a_file, refuse_loop, resolved, unloaded
```

Replace `origin` (lines 114-123) with:

```python
    def origin(self, location: str | Path, against: str | None = None) -> Origin:
        """Where the architecture comes from, the guards it leaves off and how it is looser than the profile it is
        compared with: the one against names, bundled or a file, for a bundled architecture too; else, for a custom
        file, the profile file its based_on names, or the bundled architecture it resembles. Raises
        InvalidArchitecture when the architecture does not load, when a profile file of the chain its based_on starts
        does not, or when the chain comes back to a file of it; and, once those load, AgainstUnloaded when the one
        against names does not."""
        source, architecture = self._load(location)
        chain = self._chain(source.location, architecture)
        if against is not None:
            return origin_of(source.location, architecture, source.bundled, {against: self._against(against)}, against)
        others = {} if source.bundled else {name: self.load(name) for name in self._files.bundled()}
        return origin_of(source.location, architecture, source.bundled, others, chain=chain)
```

After `_against` (ends at line 130), add:

```python
    def _chain(self, location: str, architecture: Architecture) -> tuple[Architecture, ...]:
        """The profile files the architecture at location is based on, one after another while each one's based_on is
        a path, each read from the folder of the file that names it; raises InvalidArchitecture, said from the file
        that names it, when one does not load or is a file of the chain already."""
        links: list[Link] = [(location, architecture.based_on)]
        chain: list[Architecture] = []
        while based_on_a_file(links[-1][1]):
            writer, based_on = links[-1]
            target = resolved(writer, based_on)
            refuse_loop(links, target)
            try:
                found = self.load(Path(target))
            except InvalidArchitecture as e:
                raise InvalidArchitecture(writer, [unloaded(based_on, e.problems)]) from e
            chain.append(found)
            links.append((target, found.based_on))
        return tuple(chain)
```

(`Path(target)`: `source_of` treats any `Path` as a file, so `team` from `../team` is never taken for a bundled name. A loop is refused before the file is read again.)

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec -q`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/services/architecture.py tests/modules/spec/application/test_origin.py
git commit -m "The origin of a profile whose based_on is a path loads the chain of profile files, each from the folder of the file that names it, with or without --against, and refuses the profile when a file of it does not load, said from the file that names it, or when the chain comes back to a file of it; nothing else reads the chain"
```

---

### Task 5: Rules carries `anchor`, and `--strict` fails on what spec hands it

**Files:**
- Modify: `xarch/modules/rules/domain/published.py:131-162` (`Resemblance`)
- Modify: `xarch/modules/rules/adapters/spec_profile.py:125-127` (`reviewed`)
- Test: `tests/modules/rules/adapters/test_spec_profile.py` (append), `tests/modules/rules/application/logic/test_enforcement.py` (append)

**Interfaces:**
- Consumes: `Origin.anchor` (Task 3).
- Produces: `Resemblance.anchor: str | None = None`, the last field (used by Task 6's reports, which take `Origin | Resemblance`).

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/adapters/test_spec_profile.py`, add `from dataclasses import replace` as the first import line (before `from pathlib import Path`). Append:

```python
def test_the_bundled_profile_strict_rests_on_is_kept_and_the_standing_keeps_what_it_excuses_and_demands():
    said = "core has no litmus, though cli, which --strict rests on, gives the part it pairs with one (parts.core.litmus)"
    origin = replace(ORIGIN, compared="../team.yaml", baseline_off=("dead-code",),
                     looser=(Loosened("litmus", "core", "cli", said),), anchor="cli")
    reviewed = SpecProfiles(Spec(checked=ProfileChecked("mine.yaml", (), 3, origin))).reviewed(Path("/p/app"), "mine.yaml")
    assert (reviewed.resemblance.compared, reviewed.resemblance.anchor) == ("../team.yaml", "cli")
    standing = SpecProfiles(Spec(origin=origin)).standing("mine.yaml", "app")
    assert (standing.baseline_off, standing.looser) == (("dead-code",), (published.Loosened("litmus", "core", "cli", said),))
```

(`ProfileChecked` is already imported in this file; if it is not, add it to the `xarch.modules.spec.contract` import list in sorted order.)

In `tests/modules/rules/application/logic/test_enforcement.py`, add `unplaced,` to the import from `xarch.modules.rules.application.logic.enforcement` (sorted, after `unresolved,`) and `Loosened` to `from xarch.modules.rules.domain.published import At, Drift, Unresolved, Weak` (making it `At, Drift, Loosened, Unresolved, Weak`). Append:

```python
def test_strict_fails_on_a_guard_the_anchor_does_not_excuse_and_on_a_litmus_the_anchor_demands():
    said = "core has no litmus, though cli, which --strict rests on, gives the part it pairs with one (parts.core.litmus)"
    demanded = unplaced((Loosened("untested", "api"), Loosened("litmus", "core", "cli", said)))
    assert demanded == (said,)
    assert strict_findings(Enforcement(("no-comments", "dead-code"), ("dead-code",), unplaced=demanded)) == (
        Finding("guards_off", "no-comments"), Finding("litmus", said))
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/application/logic/test_enforcement.py -q`
Expected: the adapter test FAILS with `AttributeError: 'Resemblance' object has no attribute 'anchor'`. The enforcement test PASSES already: it confirms `strict_findings` needs no change (spec test 20). If the enforcement test fails, stop and report it: the spec assumes no change there.

- [ ] **Step 3: Implement**

In `xarch/modules/rules/domain/published.py`, in the `Resemblance` docstring, replace:

```
    based_on: with --against, the profile its own based_on names, said beside it; empty otherwise
    """
```

with:

```
    based_on: with --against, the profile its own based_on names, said beside it; empty otherwise
    anchor: the bundled profile --strict rests on, as the spec module's origin names it: the one compared with when
        that one is bundled, so a profile file is compared with exactly when chosen_by is "based_on" and anchor is not
        compared; None for a bundled profile without --against, with --against, and when there is none
    """
```

and after `    based_on: str = ""` (line 162) add:

```python
    anchor: str | None = None
```

In `xarch/modules/rules/adapters/spec_profile.py`, replace lines 125-127:

```python
                                Resemblance(origin.bundled, origin.compared, looser, origin.chosen_by, origin.match,
                                            origin.low, origin.counts, origin.only_here, origin.only_there,
                                            origin.elsewhere, origin.higher, origin.based_on))
```

with:

```python
                                Resemblance(origin.bundled, origin.compared, looser, origin.chosen_by, origin.match,
                                            origin.low, origin.counts, origin.only_here, origin.only_there,
                                            origin.elsewhere, origin.higher, origin.based_on, origin.anchor))
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/rules -q`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules/domain/published.py xarch/modules/rules/adapters/spec_profile.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/application/logic/test_enforcement.py
git commit -m "Rules' Resemblance carries the anchor spec's origin names, and the standing keeps the guards the anchor excuses and the litmus it demands, which --strict fails on as it fails on every guard off and every litmus entry"
```

---

### Task 6: The words and the JSON of `profile check` and `check`

**Files:**
- Modify: `xarch/modules/spec/contract/__init__.py:11-31` (import), `:43-52` (`__all__`)
- Modify: `xarch/cli/reports/profile_report.py:1-17` (docstring), `:29-41` (import), `:199-221` (`_origin_words`, `compared_words`), `:284-294` (`compared_document`), new `_rests`
- Test: `tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py`, `tests/bootstrap/test_profile_check.py:117-123`

**Interfaces:**
- Consumes: `Origin.anchor`, `Resemblance.anchor` (Tasks 3, 5); `BASED_ON = "based_on"` from `xarch.modules.spec.domain.published`.
- Produces: the contract exports `BASED_ON`. `compared_document(origin)` gains `"anchor"`. The heading `custom; based_on: <path>, resting on <anchor|no bundled profile>`. The profile line suffix `; --strict rests on <anchor|no bundled profile>`.

- [ ] **Step 1: Write the failing tests**

In `tests/cli/reports/test_profile_report.py`:

(a) Replace `based_on_cli` and `AGAINST_WEB` (lines 108-114) with:

```python
def based_on_cli(**changes) -> Resemblance:
    """A custom profile based on cli, which --strict rests on, matching it at 80% with COUNTS and nothing unpaired; the
    fields given replaced."""
    return replace(Resemblance(False, "cli", (), "based_on", 0.8, False, COUNTS, anchor="cli"), **changes)


AGAINST_WEB = based_on_cli(compared="web", chosen_by="against", anchor=None)
"""A custom profile compared with web because --against names it, matching it at 80% with COUNTS."""
PATH_BASED = based_on_cli(compared="../team.yaml")
"""A custom profile based on the profile file ../team.yaml, resting on cli."""
```

(b) In the parametrize table of `test_profile_check_is_headed_with_where_the_profile_comes_from`, add these rows after the `"a bundled one compared with the profile against names says so"` row:

```python
    pytest.param(PATH_BASED, "custom; based_on: ../team.yaml, resting on cli",
                 id="a custom one based on a profile file names it and the bundled profile --strict rests on"),
    pytest.param(replace(PATH_BASED, anchor=None), "custom; based_on: ../team.yaml, resting on no bundled profile",
                 id="a custom one based on a profile file that rests on no bundled profile says so"),
    pytest.param(replace(AGAINST_WEB, based_on="../team.yaml"),
                 "custom; against web, given with --against; based_on: ../team.yaml",
                 id="with --against a based_on path is said beside it as written, and no anchor"),
```

(c) In `test_the_json_of_profile_check_holds_every_field_of_the_profile_compared_with`, change the expected dict's line

```python
        "elsewhere": ["store: src/*/store there"], "higher": {"profile": "web", "match": 0.88},
```

to

```python
        "elsewhere": ["store: src/*/store there"], "higher": {"profile": "web", "match": 0.88}, "anchor": "cli",
```

(d) Append:

```python
def test_a_profile_based_on_a_profile_file_is_matched_and_compared_with_it_as_written():
    assert matched(PATH_BASED) == [MATCH.replace("with cli (based_on)", "with ../team.yaml (based_on)")]
    assert checked(PATH_BASED)[-1] == "  compared: no looser than ../team.yaml"


def test_the_json_of_profile_check_names_the_bundled_profile_strict_rests_on():
    def anchor(resemblance: Resemblance):
        held = ProfileHeld(Reviewed("mine.yaml", (), 1, resemblance), ChecksHeld((), 0))
        return json.loads(check_document(held))["compared_with"]["anchor"]

    assert anchor(PATH_BASED) == "cli"
    assert anchor(replace(PATH_BASED, anchor=None)) is None
    assert anchor(based_on_cli()) == "cli"
    assert anchor(AGAINST_WEB) is None
```

In `tests/cli/reports/test_report.py`:

(e) In `test_a_part_without_the_litmus_its_base_gives_it_is_said_under_the_profile_and_again_under_strict` (line 179), change

```python
    origin = Origin("mine.yaml", False, "cli", looser=(Loosened("litmus", "cli", "", said),), chosen_by="based_on",
                    match=0.8)
```

to

```python
    origin = Origin("mine.yaml", False, "cli", looser=(Loosened("litmus", "cli", "", said),), chosen_by="based_on",
                    match=0.8, anchor="cli")
```

(f) Append:

```python
def test_a_profile_based_on_a_profile_file_says_the_bundled_profile_strict_rests_on_on_its_profile_line():
    based = Origin("/src/mine.yaml", False, "../team.yaml", chosen_by="based_on", match=0.92, counts=COUNTS,
                   anchor="cli")
    assert lines(origin=based)[2:] == [
        "  profile:     mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on cli)"]
    assert lines(origin=replace(based, anchor=None))[2] == (
        "  profile:     mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on no "
        "bundled profile)")
    assert lines(origin=replace(based, compared="cli"))[2] == (
        "  profile:     mine.yaml (custom; compared with cli, based_on; match 92%)")
    assert lines(origin=closest("/src/mine.yaml", anchor="web"))[2] == (
        "  profile:     mine.yaml (custom; compared with web, closest; match 81%)")
    against = replace(based, compared="web", chosen_by="against", anchor=None, based_on="../team.yaml")
    assert lines(origin=against)[2] == "  profile:     mine.yaml (custom; compared with web, --against; match 92%)"
    profile = json.loads(json_document("mine.yaml", based, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert profile["compared_with"]["anchor"] == "cli"
    assert json.loads(json_document("mine.yaml", against, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]["compared_with"]["anchor"] is None
```

(g) Still in `tests/cli/reports/test_report.py`, `test_the_json_document_holds_the_profile_compared_with_under_compared_with_and_no_closest_key` (line 267) compares `compared_with` to a whole dict, which gains `anchor` once Step 4 lands (a `closest` origin has `anchor` `None`). Change

```python
        "only_here": ["part jobs"], "only_there": [], "elsewhere": [], "higher": None, "looser": []}
```

to

```python
        "only_here": ["part jobs"], "only_there": [], "elsewhere": [], "higher": None, "anchor": None, "looser": []}
```

(Without this edit Step 5 fails on that test with a dict mismatch. Every other whole-dict assertion of `compared_with` is already covered: `test_profile_report.py:202` by (c) and `test_profile_check.py:120` below; the rest select keys.)

In `tests/bootstrap/test_profile_check.py`, `test_json_gives_ok_the_problems_by_check_the_files_and_the_difference`, change the expected line

```python
        "only_here": [], "only_there": [], "elsewhere": [], "higher": None, "looser": []}
```

to

```python
        "only_here": [], "only_there": [], "elsewhere": [], "higher": None, "anchor": "web", "looser": []}
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/cli/reports tests/bootstrap/test_profile_check.py -q`
Expected: FAIL. The new heading rows read `custom; based_on: ../team.yaml` without `, resting on ...`. The profile line has no `; --strict rests on ...`. The JSON has no `anchor` key (`KeyError: 'anchor'`, or a dict mismatch).

- [ ] **Step 3: Re-export `BASED_ON` from the contract**

In `xarch/modules/spec/contract/__init__.py`, add `BASED_ON,` to the import from `xarch.modules.spec.domain.published`, right after `AGAINST,`. In `__all__`, change `"Origin", "Loosened", "LITMUS", "CLOSEST", "AGAINST",` to `"Origin", "Loosened", "LITMUS", "BASED_ON", "CLOSEST", "AGAINST",`.

- [ ] **Step 4: Implement the words and the JSON**

In `xarch/cli/reports/profile_report.py`, add `BASED_ON,` to the import from `xarch.modules.spec.contract`, right after `AGAINST,`.

Replace `_origin_words` and `compared_words` (lines 199-221) with:

```python
def _origin_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as `profile check` heads it: bundled, or custom and the profile it is
    compared with and why (with the match, when it is the closest; with the bundled profile --strict rests on, when it
    is a profile file its based_on names), if any; with --against, either and the profile it names, then what the
    profile's own based_on names."""
    if origin.chosen_by == AGAINST:
        based_on = f"; based_on: {origin.based_on}" if origin.based_on else ""
        return f"{_kind(origin)}; against {origin.compared}, given with {GIVEN}{based_on}"
    if origin.bundled:
        return "bundled"
    if origin.compared is None:
        return "custom; no bundled profile resembles it"
    if origin.chosen_by == CLOSEST:
        return f"custom; closest bundled: {origin.compared}, match {percent(origin.match)}"
    rests = _rests(origin)
    if rests is not None:
        return f"custom; based_on: {origin.compared}, resting on {rests}"
    return f"custom; {origin.chosen_by}: {origin.compared}"


def compared_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as the enforcement section of `check` says it: bundled, or custom and the
    profile it is compared with, why, and the match, if any, then the bundled profile --strict rests on when it is
    compared with a profile file its based_on names; a bundled one compared with the one --against names says that
    too."""
    if origin.compared is None:
        return _origin_words(origin)
    rests = _rests(origin)
    resting = "" if rests is None else f"; --strict rests on {rests}"
    return f"{_kind(origin)}; compared with {origin.compared}, {_why(origin)}; match {percent(origin.match)}{resting}"


def _rests(origin: Origin | Resemblance) -> str | None:
    """The bundled profile --strict rests on, in words, when the profile is compared with the profile file its
    based_on names (its anchor is then not the profile compared); None for any other, which says nothing more."""
    if origin.chosen_by != BASED_ON or origin.anchor == origin.compared:
        return None
    return origin.anchor or "no bundled profile"
```

In `compared_document` (line 288 onwards), change

```python
            "higher": None if origin.higher is None else {"profile": origin.higher[0], "match": origin.higher[1]},
```

to

```python
            "higher": None if origin.higher is None else {"profile": origin.higher[0], "match": origin.higher[1]},
            "anchor": origin.anchor,
```

In the module docstring (lines 13-17), change

```
profile's own) and compared_with {"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there",
"elsewhere", "higher", "looser"} (null when nothing is compared: a bundled profile without --against, or one that
resembles none), chosen_by "based_on", "closest" or "against", counts {"parts",
"part_keys", "tiers", "guards", "profile"} each [comparable, all], higher null or {"profile", "match"}, each looser
```

to

```
profile's own) and compared_with {"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there",
"elsewhere", "higher", "anchor", "looser"} (null when nothing is compared: a bundled profile without --against, or one
that resembles none), chosen_by "based_on", "closest" or "against", counts {"parts",
"part_keys", "tiers", "guards", "profile"} each [comparable, all], higher null or {"profile", "match"}, anchor the
bundled profile `--strict` rests on or null, each looser
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `uv run pytest tests/cli/reports tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py -q`
Expected: PASS (all). Every existing heading and line stays byte for byte as before: a bundled `based_on` has `anchor == compared`.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/contract/__init__.py xarch/cli/reports/profile_report.py tests/cli/reports/test_profile_report.py tests/cli/reports/test_report.py tests/bootstrap/test_profile_check.py
git commit -m "profile check heads a profile based on a profile file (custom; based_on: ../team.yaml, resting on cli), check's profile line ends ; --strict rests on cli, either saying no bundled profile when there is none, and compared_with gains anchor in the JSON of both; every other heading and line is unchanged"
```

---

### Task 7: `profile explain based_on` says a path is accepted

**Files:**
- Modify: `xarch/architectures/presets/format/keys.yaml:127-130`
- Test: `tests/modules/spec/application/test_explain.py:42` and `:111-115`, `tests/bootstrap/test_profile_explain.py` (append)

**Interfaces:**
- Consumes: nothing new.
- Produces: `based_on`'s `meaning` = `the profile this one is based on: the bundled one it was copied from, or a profile file`, and its `accepts` = the `ACCEPTS` text below. `example` and `choices` are unchanged.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/test_explain.py`, line 42, change

```python
    Shown('based_on', 0, 'the bundled profile this was copied from', False, False),
```

to

```python
    Shown('based_on', 0, 'the profile this one is based on: the bundled one it was copied from, or a profile file',
          False, False),
```

and in the `Explain("based_on")` row (lines 111-115), change

```python
                 KeyExplained("based_on", "the file", "the bundled profile this was copied from",
                              "the name of a bundled profile: `profile check` reports how this one is looser than it",
                              False, False, (), "based_on: base", ("base", "other"), (), name="based_on"),
```

to

```python
                 KeyExplained("based_on", "the file",
                              "the profile this one is based on: the bundled one it was copied from, or a profile file",
                              "the name of a bundled profile, or the path of a profile file from this file's folder: "
                              "`profile check` and `check` compare this one with it, unless `--against` names another "
                              "for the run; `--strict` rests on a bundled profile: the chain's bundled root, else the "
                              "bundled profile closest to its last file",
                              False, False, (), "based_on: base", ("base", "other"), (), name="based_on"),
```

In `tests/bootstrap/test_profile_explain.py`, append:

```python
ACCEPTS = ("the name of a bundled profile, or the path of a profile file from this file's folder: `profile check` and "
           "`check` compare this one with it, unless `--against` names another for the run; `--strict` rests on a "
           "bundled profile: the chain's bundled root, else the bundled profile closest to its last file")
"""What based_on accepts, as `profile explain based_on` says it."""


def test_based_on_is_explained_as_a_bundled_name_or_a_profile_file_and_its_choices_stay_the_bundled_names():
    explained = json.loads(runner.invoke(app, ["profile", "explain", "based_on", "--format", "json"]).output)
    assert explained["accepts"] == ACCEPTS
    assert explained["meaning"] == "the profile this one is based on: the bundled one it was copied from, or a profile file"
    assert tuple(explained["choices"]) == bundled_profiles()
    text = runner.invoke(app, ["profile", "explain", "based_on"])
    assert text.exit_code == 0 and "the path of a profile file from this file's folder" in " ".join(text.output.split())
```

(`json`, `runner`, `app` and `bundled_profiles` are already imported in `test_profile_explain.py`; it uses them at lines 173-176.)

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py -q`
Expected: FAIL. `meaning` is still `the bundled profile this was copied from`, and `accepts` is the old text.

- [ ] **Step 3: Implement**

In `xarch/architectures/presets/format/keys.yaml`, replace lines 127-130:

```yaml
  based_on:
    meaning: the bundled profile this was copied from
    accepts: "the name of a bundled profile: `profile check` reports how this one is looser than it"
    example: "based_on: <bundled>"
```

with:

```yaml
  based_on:
    meaning: "the profile this one is based on: the bundled one it was copied from, or a profile file"
    accepts: >-
      the name of a bundled profile, or the path of a profile file from this file's folder: `profile check` and
      `check` compare this one with it, unless `--against` names another for the run; `--strict` rests on a bundled
      profile: the chain's bundled root, else the bundled profile closest to its last file
    example: "based_on: <bundled>"
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest tests/modules/spec tests/bootstrap/test_profile_explain.py tests/bootstrap/test_docs.py tests/bootstrap/test_docs_templates.py -q`
Expected: PASS (all). The golden docs do not quote `based_on`'s meaning, so they stay byte-identical.

- [ ] **Step 5: Commit**

```bash
git add xarch/architectures/presets/format/keys.yaml tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py
git commit -m "profile explain based_on says it accepts a bundled name or the path of a profile file from the file's folder, compared with unless --against names another, and that --strict rests on the chain's bundled root, else the bundled profile closest to its last file; its choices stay the bundled names"
```

---

### Task 8: On disk, through the real app

**Files:**
- Test: `tests/bootstrap/test_profile_check.py` (append), `tests/bootstrap/test_check_enforcement.py` (append)

**Interfaces:**
- Consumes: everything above, through `xarch.bootstrap.app.app` and the real filesystem adapter.
- Produces: nothing new. These tests pin spec tests 23-27 on disk, where "read from the profile's folder, not the working folder" is real.

The behaviour already exists once Tasks 1-7 are in, so these tests are expected to pass when first run. If one fails, the failure is a real bug in Tasks 1-7. Debug it there (superpowers:systematic-debugging); do not change the test to match.

- [ ] **Step 1: Write the tests**

In `tests/bootstrap/test_profile_check.py` (its autouse fixture `in_tmp` has made `architecture/mine/mine.yaml`, a `profile new` copy of web, with the working folder at `tmp_path`), append:

```python
TEAM = "architecture/team/team.yaml"
"""A copy of cli beside the copy of web, for the copy of web to be based on by its path."""


def based_on_team(tmp_path):
    """The copy of web based on a copy of cli by the path ../team/team.yaml, from the copy's own folder."""
    assert runner.invoke(app, ["profile", "new", "team", "--from", "cli"]).exit_code == 0
    edit(tmp_path, lambda d: d.update(based_on="../team/team.yaml"))


def test_a_copy_based_on_a_profile_file_is_compared_with_it_and_rests_on_the_bundled_profile_that_file_is_based_on(
        tmp_path):
    based_on_team(tmp_path)
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == f"checking {COPY} (custom; based_on: ../team/team.yaml, resting on cli)"
    assert "with ../team/team.yaml (based_on): " in result.output
    compared = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["anchor"]) == ("../team/team.yaml", "based_on", "cli")


def test_a_based_on_path_is_read_from_the_profile_s_folder_whatever_the_working_folder(tmp_path, monkeypatch):
    based_on_team(tmp_path)
    (tmp_path / "elsewhere").mkdir()
    monkeypatch.chdir(tmp_path / "elsewhere")
    result = runner.invoke(app, ["profile", "check", str(tmp_path / COPY)])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == (
        f"checking {tmp_path / COPY} (custom; based_on: ../team/team.yaml, resting on cli)")


def test_a_based_on_path_that_names_no_file_refuses_the_profile(tmp_path):
    edit(tmp_path, lambda d: d.update(based_on="../team/team.yaml"))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 2
    assert f"error: {COPY}: based_on: ../team/team.yaml does not load: {TEAM}: cannot read the file" in result.output
```

(From `tmp_path` or `tmp_path/elsewhere`, `../team/team.yaml` read from the working folder names no file. Only a read from `architecture/mine/` finds it, so a wrong folder fails these tests.)

In `tests/bootstrap/test_check_enforcement.py` (its autouse fixture `project` runs `init --profile web` and `new module docs` in `tmp_path`), append:

```python
def chained(root: Path) -> None:
    """arch/team.yaml, a copy of web based on web that leaves no-comments off, and arch/mine.yaml, a copy of web based
    on team.yaml, read from its own folder, that leaves it off too, beside the bundled profiles' files."""
    shutil.copytree(BUNDLED, root / "arch")
    lax = (BUNDLED / "web.yaml").read_text().replace("  no-comments: {}\n", "")
    (root / "arch/team.yaml").write_text(lax.replace("\nname: web\n", "\nname: team\nbased_on: web\n", 1))
    (root / "arch/mine.yaml").write_text(lax.replace("\nname: web\n", "\nname: mine\nbased_on: team.yaml\n", 1))


def test_a_profile_based_on_a_file_of_its_own_says_what_strict_rests_on_and_the_file_excuses_no_guard(tmp_path):
    chained(tmp_path)
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:4] == [
        "  profile:     arch/mine.yaml (custom; compared with team.yaml, based_on; match 100%; --strict rests on web)",
        "    guards off:  no-comments"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-comments"]
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert (profile["compared_with"]["anchor"], profile["guards_off"], profile["baseline_off"]) == (
        "web", ["no-comments"], [])


def test_check_refuses_a_profile_whose_based_on_file_does_not_load(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    (tmp_path / "arch/mine.yaml").write_text(
        (BUNDLED / "web.yaml").read_text().replace("\nname: web\n", "\nname: mine\nbased_on: gone.yaml\n", 1))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 2
    assert "arch/mine.yaml: based_on: gone.yaml does not load: " in result.output
    assert "arch/gone.yaml: cannot read the file" in result.output
```

(Before writing `chained`, confirm `grep -c '^name: web$' xarch/architectures/web.yaml` prints `1`. The `"\nname: web\n"` replacement, count 1, then touches only the top-level name. The location in the refusal may be absolute, depending on how `check` selects the profile, so the last test matches the two ends with `in`.)

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py -v`
Expected: PASS (all, the new ones included). A failure here is a bug in Tasks 1-7: report it with its output and fix it there.

- [ ] **Step 3: Commit**

```bash
git add tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py
git commit -m "On disk, a copy based on a profile file by its path is read from its own folder whatever the working folder, headed with the bundled profile --strict rests on, refused with exit 2 when the file does not load, and check --strict fails on a guard the file leaves off but its anchor switches on"
```

---

### Task 9: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:239` (the `profile check` paragraph), `:242`, `:460` (the `check` enforcement paragraph)
- Modify: `CHANGELOG.md:26` (after the `--against` bullet under `## [Unreleased]` / `### Added`)

**Interfaces:** none.

- [ ] **Step 1: README, the `profile check` paragraph**

In `README.md`, replace line 239:

```
refuses the run, exit 2), else the one its `based_on` names, else the bundled one of highest match; a bundled profile
```

with:

```
refuses the run, exit 2), else the one its `based_on` names, else the bundled one of highest match. `based_on` is a
bundled name or the path of a profile file (`based_on: ../team.yaml`), read from the folder of the file that writes
it and compared with as written; that file's own `based_on` is followed in turn, and a file of the chain that does not
load, or a chain that comes back to a file of it, refuses the profile (exit 2). A bundled profile
```

and replace line 242:

```
match line reading `match: 73% with web (--against): ...`. Before that comparison a `match:`
```

with:

```
match line reading `match: 73% with web (--against): ...`. A profile based on a file is headed `checking
sub/mine.yaml (custom; based_on: ../team.yaml, resting on cli)`, naming the bundled profile `--strict` rests on (`resting
on no bundled profile` when there is none). Before that comparison a `match:`
```

(Check the wording reads on from line 240, which starts `is its own baseline and is compared only with \`--against\``: "A bundled profile is its own baseline ...". Line 239's old ending was "a bundled profile", lower case, so its continuation reads right with the new capital.)

- [ ] **Step 2: README, the `check` enforcement paragraph**

In `README.md` line 460, replace the text

```
violations and `strict_failures` are the same with it and without it. `guards off` lists
```

with:

```
violations and `strict_failures` are the same with it and without it. When `based_on` is the path of a profile file, `--strict` rests on a bundled profile, its anchor: the bundled profile the chain of files ends on, else the bundled profile closest to its last file, else none. The line says it, `mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on cli)` (`--strict rests on no bundled profile` with none), and `compared_with.anchor` holds it in JSON: a bundled name, or `null` (with `--against`, and for a profile compared with a bundled one it is that one). A guard left off is excused only when the anchor and every file of the chain leave it off too, and a part fails `litmus` when it lacks a litmus that the path file gives the part it pairs with there, or that the anchor gives the part it pairs with in the anchor: a file of one's own can tighten `--strict`, never loosen it. `guards off` lists
```

(Line 460 is already one long line in the README; keep the insertion on it, as the line already does.)

Run: `uv run pytest tests/architecture/test_readme.py -q`
Expected: PASS.

- [ ] **Step 3: CHANGELOG**

In `CHANGELOG.md`, directly after the line `  profile against its baseline.` (line 26, the end of the `--against` bullet) and before `- The kinds \`records\` and \`exceptions\` of \`holds\`...`, insert:

```
- `based_on` takes the path of a profile file, read from the folder of the file that writes it (`based_on:
  ../team.yaml`): `profile check` and `check` compare the profile with that file, as written, and follow its own
  `based_on` in turn. A file of the chain that does not load refuses the profile (exit 2, `sub/mine.yaml: based_on:
  ../team.yaml does not load: ...`), and so does a chain that comes back to a file of it (`mine.yaml: based_on: a.yaml
  is based on this profile`). `--strict` rests on a bundled profile, the anchor: the bundled profile the chain ends on,
  else the one closest to its last file, else none. A guard left off is excused only when the anchor and every file of
  the chain leave it off too, and a part fails `litmus` when it lacks a litmus the path file or the anchor gives the
  part it pairs with, so a file of one's own never loosens `--strict`. `profile check` heads it `(custom; based_on:
  ../team.yaml, resting on cli)`, `check`'s `profile:` line says `(custom; compared with ../team.yaml, based_on; match
  92%; --strict rests on cli)`, and `compared_with` gains `anchor` in the JSON of both.
```

- [ ] **Step 4: Golden docs regenerate unchanged**

Run: `uv run pytest tests/bootstrap/test_docs.py tests/bootstrap/test_docs_templates.py -q && git status --short docs/cli docs/web docs/xarch`
Expected: PASS, and `git status` lists nothing under `docs/cli`, `docs/web`, `docs/xarch` (no bundled profile and no template changed). If a golden doc differs, read the diff and report it; never edit a golden doc by hand.

- [ ] **Step 5: The gates**

Run each and read its output:

```bash
timeout 900 uv run pytest -q > /tmp/pytest-5-4.txt 2>&1; echo "pytest exit $?"; tail -5 /tmp/pytest-5-4.txt
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run ruff check; echo "ruff exit $?"
uv run xarch profile check architecture.yaml > /tmp/xarch-profile-check-after.txt; echo "profile check exit $?"
diff /tmp/xarch-profile-check-before.txt /tmp/xarch-profile-check-after.txt && echo "profile check unchanged"
```

(Run the pytest line in the background, `run_in_background`, since it takes over two minutes, and read `/tmp/pytest-5-4.txt` when it ends.)
Expected: pytest exit 0, every test passed. `check` exit 0, `strict` exit 0, `ruff` exit 0 (`All checks passed!`). `profile check` exit 0 with the diff empty (`profile check unchanged`): its heading `checking architecture.yaml (custom; based_on: cli)`, `match: 80% with cli (based_on)` and its `compared:` list are as before the step. A failure here is reported with its output, not worked around. `tests/architecture/test_self_check.py` (no comments), `tests/bootstrap/test_recorded_corpora.py` and `tests/architecture/test_readme.py` are part of the suite and stay unedited.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say based_on takes the path of a profile file read from the folder of the file that writes it, the chain and its two refusals, that --strict rests on a bundled anchor which a file of one's own never loosens, the heading and profile line that name it and compared_with.anchor; the golden docs regenerate unchanged"
```

---

## Self-review (done while writing)

**Spec coverage.**
- §2.1 → Task 1.
- §2.2 → Task 2 (`resolved`) and Task 4 (`Path(target)`, the decoy test, the suffix-less test).
- §2.3 → Task 2 (`refuse_loop`, `unloaded`) and Task 4 (tests 10, 11, 12; a loop is checked before a load).
- §2.4 → Task 3 (comparison with `chain[0]` under the path as written; `higher` bundled only; low with no part in common through `_compared`) and Task 4 (`--against` keeps the chain's refusals).
- §2.5 → Task 3 (`anchor` for every row of the table: bundled → `None`, against → `None`, bundled `based_on`/closest → the name, nothing compared → `None`, chain → root, else closest to the last file, else `None`).
- §2.6 → Task 3 `_resting`.
- §2.7 → Task 3 `_resting`, with the `_sentence` arm.
- §2.8 → Task 6.
- §2.9 → Task 7 (keys) and Task 9 (README, CHANGELOG, golden docs).
- §2.10 → Tasks 3-6. Two named deviations: `others` holds only bundled profiles, with the chain passed whole, which §2.10 allows as "or an equivalent"; and the reports detect a path by `anchor != compared` (see Global Constraints).
- §3 tests 1-3 → Task 1; 4-8 → Task 3; 9-18 → Task 4; 19 → Task 5; 20 → Task 5; 21-22 → Task 6; 23-27 → Task 8 (25 for `check` too, 26-27 in `test_check_enforcement.py`); 28 → Task 7. Architecture-tier tests → Task 9 gates.
- §4 out of scope: no bundled profile, `architecture.yaml` or `--strict --against` refusal changes.
- §5 gates → Task 9.

**Placeholder scan.** No "TBD", no "similar to Task N"; every code step shows its code.

**Type consistency.** `origin_of(location, architecture, bundled, others, against=None, chain=())` is the same in Tasks 3 and 4. The names `Link`, `based_on_a_file`, `resolved`, `refuse_loop`, `unloaded` match across Tasks 2 and 4. `anchor: str | None = None` is the last field of both `Origin` and `Resemblance`. `BASED_ON` is exported in Task 6 and used only there.
<!-- task-pipeline: validated -->
