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
- `xarch review --dry-run`: what an advisory review would ask a decision model of the files chosen (as paths, with
  `--files-from -`, or `--all`), each file's text masked, the files left out and why, and what it would cost. It
  sends nothing, and never changes what `check` finds.

### Not in this release

- An advisory review that sends: `review` runs only with `--dry-run`.
- Languages other than Python.
- A stable check vocabulary: the words a profile's checks are written in may change.

[0.1.0]: https://github.com/paulomtts/xarch/releases/tag/v0.1.0
