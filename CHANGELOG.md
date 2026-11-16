# Changelog

All notable changes to this project are written here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - Unreleased

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
- `xarch review`, advisory: a decision model's reading of where each file chosen (as paths, with `--files-from -`, or
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
  only. Exit 0 when it ran, 2 when it refused, 3 when a file has no answer. It never changes what `check` finds.
- A profile's `review` key: `review.never`, the paths below the app of files review never sends, and `review.mask`,
  texts it hides before it sends. `check` never reads either; `profile explain` says them, and `profile check` lists
  an entry the base profile has and the profile drops as looser.
- A profile's `evals.placement.lines`: the line of a part, set by hand. `check` never reads it; `profile explain`
  says it, and `profile check` lists a part whose line is below the base profile's as looser.
- The generated `AGENTS.md` says in one paragraph how to use `xarch review` and that it never replaces `xarch check`.

### Not in this release

- Languages other than Python.
- A stable check vocabulary: the words a profile's checks are written in may change.

[0.1.0]: https://github.com/paulomtts/xarch/releases/tag/v0.1.0
