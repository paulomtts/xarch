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
