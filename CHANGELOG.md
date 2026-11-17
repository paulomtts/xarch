# Changelog

All notable changes to this project are written here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- The bundled `cli` and `web` profiles are stricter, with five rules xarch's own profile already held: `services`,
  `controller` and `adapters` may not read the working folder, the home folder or the environment (the `ambient`
  list, which now also holds `.chdir()`, `os.environ` and `os.getenv`); `platform` and the entry part (`cli` / `web`)
  may not read the environment (`os.environ`, `os.getenv`): settings are read in `bootstrap` and handed in; the
  `closed-tree` guard is on, so a Python file of the app in no part is a violation, and `check` no longer lists it as
  a guard off; `contract` may not use `typing.Any` (its list, `published`, is the `pure` list and `typing.Any`); and
  `ports` and `adapters` hold classes (`holds: classes`), so a public function at their top level is listed as weak
  and fails `check --strict`. A project on a bundled profile may see new findings: move a stray file into the part
  that fits it (`xarch where <file>` names the parts near it), or, with a profile of the project's own (`xarch profile
  new mine --from cli`), list a folder that is not the app's source under `excluded`; read a setting in `bootstrap`
  and hand it to the client or the command that needs it; give a contract field a type of its own; and put a helper
  function of a port or an adapter in a method or in `application/logic/`.

### Removed

- `xarch profile migrate`, which converted a profile of format 1 to format 2, is gone, with everything that existed
  only for it. A file that starts `xarch: 1` is now refused as an unknown format version, like any other, and the keys
  of format 1 that moved (`layout`, `notes`, `rules`, `placement`, `naming`, `tests`, `examples`, `libraries`) are
  refused as unknown keys, with no word of where they went.
- The profile has no format version: the top-level key `xarch` is gone from the format, from the bundled `cli` and
  `web` profiles, from the copy `profile new` writes, and from `profile explain` (its overview no longer says a format
  number, and its JSON no longer has `format`). A profile that still starts with `xarch: 2` is refused as an unknown
  key: delete the line.

## [0.1.1] - 2026-11-17

### Changed

- The bundled `cli` and `web` profiles pass their own placement calibration for all 12 parts (it was 3 and 5 in
  0.1.0), measured with `jev-1.14.0` with every comment cut from what is sent. The litmus texts of `domain`,
  `controller`, `adapters`, `platform`, `cli`/`web`, `bootstrap`, `contract` and `kernel` say more exactly what decides
  a case (where an id and a module's errors are defined, who fetches a controller for a command or a route and who
  starts the program, what is a primitive and what is a shared function, an adapter that wraps another module's
  controller), and eight short example files show it in their code.
- In the bundled example files, and so in the docs `init` writes from them, every comment sits on a line of its
  own, above the code it explains, never at the end of a code line; the words of each are kept.
- `xarch review` and `xarch review calibrate` cut every comment from what they send: a file, a piece and the opening
  lines sent before it, the text an eval reads, placement's examples and an eval's own, in a run and its dry run
  alike. A comment would tell the decision model what its writer thought of the code, often where it belongs. What a
  comment is, the language's reader says (a `#` inside a string is none, a docstring is no comment): it hands each
  comment's place in its line through rules to review. A comment is cut with the blanks before it, and a line that
  held only a comment stays as an empty line, so the lines of a piece do not move. A dry run says so where it lists
  what is masked: in text, "masked in each text: every comment (cut from its line, the line kept), ...", now in
  `review calibrate --dry-run` too; in JSON, `"masked": ["own-imports", "e-mail", "comments"]` beside `mask`.
  `chars` is still the length of the text sent; whether a file is judged at all (800 to 200,000 characters) is counted
  on the file as it is, `small` and the sizes of pieces on the text sent. What a calibration record is held as now
  names what review always masks, so every record of placement or of an eval made before this is stale: run
  `xarch review calibrate` again.

## [0.1.0] - 2026-11-17

The first release.

### Added

- Commands:
  - `xarch init` creates a project's top-level skeleton, records the profile (and the app folder, when it is not
    `app/`) in `pyproject.toml`, and writes the project docs and files; it never overwrites.
  - `xarch new` creates one instance of a profile's repeating folder, such as a module, with its skeleton.
  - `xarch check` reports every violation in the app and its tests, each with its fix, then the state of the check's own
    enforcement. It prints text or JSON, and `--strict` also fails on an enforcement finding.
  - `xarch where` says what a path is and what code there may do before it is written.
  - `xarch profile migrate`, `explain`, `new` and `check` convert a profile of format 1 to format 2, explain the
    format (a key, or a profile's folder tree and import table), copy a bundled profile into the project, and validate a
    profile without an app.
- Two bundled profiles, `cli` and `web`, each describing the top-level layout, the parts, which part may import which,
  the test tiers and the guards that can be switched on. A project may bring a profile file of its own (`.yaml` or
  `.json`).
- Profile format 2: one YAML file that states each fact once, on the thing it is about.
- A profile's own checks, written under `checks`, each held to its words, its facts and its examples.
- Python, read through the interpreter's own syntax tree, with pytest as the testing preset.
- `xarch review`, experimental and advisory: a decision model's reading of where each file chosen (as paths, with `--files-from -`, or
  `--all`) belongs, by the litmus tests of the profile's parts, ranked, a file below its part's line (0.3, or the
  part's own) read as doubtful there, in text and JSON. A file whose answer falls within 0.15 of its part's line is
  asked again in two other orders of the options and read on the mean; a file under 2,000 characters is marked small;
  every reading ends with how the files of each part read, and a part with at least 3 doubtful files, more than a
  quarter of those read, gets a note pointing at its litmus. `--pieces` also ranks the pieces of each file chosen
  (functions and classes of 1,000 characters or more, a large class as its methods), inside that file only, the
  lowest 3 shown, with no line and no doubt; `--context imports` sends the file's opening lines before each piece;
  `--all --pieces` is refused. It sends each file's masked text to the decision model whenever its key is set in
  the environment, and refuses without one; `--dry-run` shows exactly what would be sent and sends nothing;
  answers are kept in the project's `.xarch/cache/review/` (or `--cache`), holding no code, and `--offline` reads them
  only. Exit 0 when it ran, 2 when it refused, 3 when a file has no answer. A request the decision model refuses as
  its own fault (malformed, too large, a field it cannot accept) leaves that file, piece or example unanswered with
  the decision model's words and the rest is still sent; any other failure stops the sending. It never changes what
  `check` finds. A file over 200,000 characters is left out as too large, in a dry run too, and never sent. A
  file reached through a link to a file outside the app, or to no source file, is left out and never read. The key
  is read without the whitespace around it; one a request header cannot carry refuses a run that would send (exit 2)
  before anything is sent, and blocks no run that sends nothing: `--dry-run` says, in text and in JSON
  (`sends.unusable`), that the key is set but cannot be used, and why, and `--offline` runs as usual; the key is in
  no message; a redirect is never followed. An answer kept that does not answer its question
  is asked again; the cache and the record are never read or written through a link; a cache folder that is a file,
  a record that cannot be read, a record or cache that cannot be written, and a `--files-from` list that is not UTF-8
  are refused (exit 2), never a traceback; the header names the model versions that answered when they are not the
  model asked alone.
- A profile's `review` key: `review.never`, the paths below the app of files review never sends (matched against a
  link and the file it links to), the profile's own examples included: `review calibrate`, its dry run too, never
  sends an example of `docs.examples`, `evals.placement.examples` or an eval of its own that one matches, lists it as
  held back with the path (in JSON `held_back`), and holds placement and each eval to (and as) the examples that
  remain, an eval left with fewer than 2 of a kind not held and failed; and `review.mask`,
  texts it hides before it sends. `check` never acts on either (a value written wrong makes the profile invalid for
  every command, `check` included; no finding and no exit code of `check` depends on them); `profile explain` says
  them, `profile check` lists an entry the base profile has and the profile drops as looser, and the dry run lists
  the `never` paths in force, saying of each that matched nothing that it did.
- A profile's `evals.placement.lines`: the line of a part, set by hand. `check` never acts on it (its enforcement
  lists a line set lower as looser, for information only); `profile explain`
  says it, and `profile check` lists a part whose line is below the base profile's as looser.
- A profile's own evals under `evals.<id>`: one short question (`ask`), its answer form (`yes-no` with `yes` and
  `no`, a score of five levels 0 to 4 with `flagged_from`, or a choice of three options or more with `flagged`), what
  it is asked of (`reads`: file, class or function) and where (`in`, `keep`), its `line`, `message` and `fix`, and at
  least 2 flagged and 2 clean examples. `profile check` refuses each slot written wrong at its address, a `keep` filter
  of no word of the vocabulary, and an example in which the eval reads nothing, under its own heading, `evals`;
  `profile explain evals.<id>.<slot>` says each. The bundled profiles write none.
- `xarch review calibrate [--eval ID ...]` holds the evals of the profile's own to their examples (every flagged one
  above every clean one, by 0.4 on the mean, on the right side of the line, which it sets when the profile writes
  none) and records the verdicts in `.xarch/calibration.json`, to commit; exit 1 when an eval fails. Review runs an
  eval only when it is calibrated as written now by the model asked, lists its readings at or above its line with its
  message and fix, and says of any other why it does not run (uncalibrated, failed, stale) and what to run. The same
  run holds placement to the docs' examples and to `evals.placement.examples`, part by part (a sanity check of the
  litmus texts), its examples masked as written for the docs' example app; an example of `evals.placement.examples`
  lying in no part is refused at its address; review never marks doubtful a file of a part whose examples disagree,
  and lists such files under their own heading. A record that cannot be read is refused, never rewritten.
- The generated `AGENTS.md` says in one paragraph how to use `xarch review` and that it never replaces `xarch check`;
  that with no key set it refuses (exit 2), so the agent skips it, or runs it with `--offline` when the project commits
  its answer cache; and that `xarch review calibrate` is the maintainer's to run, not the agent's.

### Not in this release

- Languages other than Python.
- A stable check vocabulary: the words a profile's checks are written in may change.

[0.1.1]: https://github.com/paulomtts/xarch/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/paulomtts/xarch/releases/tag/v0.1.0
