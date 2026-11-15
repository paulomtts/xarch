# xarch

Check and scaffold an architecture described in an architecture file (a profile): its layout, its parts, which part
may import which, its test tiers and the guards it switches on. Two profiles are bundled, `cli` and `web`; a project
may also bring its own file. xarch knows no part by name: every name comes from the profile.

## Commands

```
xarch init [--app PATH] [--profile NAME|FILE]                 # create the top-level skeleton, record the profile in
                                                             # pyproject.toml, write the project docs; never overwrites
xarch new KIND NAME [--app PATH] [--profile NAME|FILE]       # create one folder of a kind with its full skeleton
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH]   # report every violation in the app and its tests
```

A kind is a folder of the profile's layout that declares `each:`, named by its path in the layout: in both bundled
profiles that is `modules`, so `xarch new modules documents` creates `modules/documents/`. A profile has at most one
`each:` folder. Beside `each:` the folder declares `singular:`, the name of one instance of it (`module` in both
bundled profiles): the docs show the folder as `<module>/` and write "its own module's" from it.

```yaml
layout:
  modules:
    singular: module
    each:
      domain: {}
```

`--app` defaults to `app` (relative to the working directory); the app's import name is its folder's name. `check`
exits 0 when clean, 1 with violations, and 2 on a usage error (a missing app or tests folder, no profile or an unknown one, an
invalid architecture file, an unreadable `pyproject.toml`). `init` and `new` exit 2 when they refuse (an invalid
name, a kind the profile does not declare, a folder that already exists, no skeleton yet).

## Profiles

These are the two profiles bundled with xarch, shown as examples; they differ in the entry-point folder, the part that drives the rest. xarch itself knows neither.

| Profile | Top level |
|---|---|
| `cli` | `bootstrap/` (`migrations/`), `kernel/`, `modules/`, `platform/`, `cli/` (`commands/`) |
| `web` | `bootstrap/` (`migrations/`), `kernel/`, `modules/`, `platform/`, `web/` (`routes/`, `i18n/`, `ui/`) |

In both bundled profiles the entry point follows the same rule: it may import any module's `controller` and `contract/`,
`kernel/`, and itself. Violations name the real folder, e.g. `web/ may not import platform/`.

The profile is a bundled name or a path to an architecture file (`.yaml` or `.json`), chosen in this order:

1. `--profile` on the command (a path is relative to the working directory);
2. `profile` under `[tool.xarch]` in the nearest `pyproject.toml`, looked up from the folder holding the app
   folder upward (the nearest `pyproject.toml` decides, even when it has no `[tool.xarch]` table); a path is
   relative to the folder holding that `pyproject.toml`;

With neither, the command fails with exit code 2 and lists the profiles found: no profile is assumed.

The file is loaded and validated before anything runs; a bad one is reported with every problem in it. `init`
records the profile it used in that `pyproject.toml` (creating one beside the app folder if there is none, and never
changing a profile already recorded), so a bare `xarch check` uses it.

```toml
[tool.xarch]
profile = "web"          # or a path, such as "architecture.yaml"
tests = "tests"          # optional; the default is tests/ beside the app folder, when it exists
```

## What check checks

`check` reads only the files the profile governs: a file in a part, or a package file of a folder of the layout.
A file anywhere else (such as reference code kept as data, like xarch's own `architectures/examples/`) is never read.

From the architecture itself:

- `structure`: every folder and file of the layout exists, in the app and in every instance of the `each:` folder.
- `rules`: every import between parts is one that `rules:` allows. `@own` means the importer's own instance of
  the `each:` folder, `@any` any instance.
- `libraries` (with `libraries:`): a part imports only the outside packages listed for it, by top-level import
  name; the standard library (`sys.stdlib_module_names`) is always allowed, and tests are not checked.
- `tiers` (with `tiers:`): tests mirror the app, `tests/<path>` for the app's `<path>`. A file's tier is that of
  the part its folder mirrors; a file directly in the folder of file parts (such as `application/`, holding
  `controller.py`) takes their tier; a folder that mirrors no part belongs to the tier whose example test lies in it
  (`tests/architecture/` is the guard tier's). A test imports only its tier's subject parts and what those parts
  may import under `rules:`; the fakes only when its tier tests a part `fakes:` stands in for; and other test code
  only from its own folder (`tests/<each root>/<name>/` or `tests/<top folder>/`). A test file in no tier is a
  violation; a helper above every part's folder (`tests/conftest.py`, `tests/modules/<name>/builders.py`) and the
  fakes are not import-checked.
- `test tree`: every folder below `tests/<each root>/` mirrors a folder of the app.

Switched on by name in `guards:`:

- `package-only: [<part>, ...]`: the parts are imported as a package, never by their files, from outside them.
- `scenario-coverage: {results, tier, suffix}`: every union `<Name><suffix> = A | B` in a file of the `results`
  part has a test file `test_<name>.py` (snake_case) among the `tier` tests of the same instance, whose module
  docstring has a `Scenario: <title>` line per variant, followed by `Then the <suffix> is <Variant>`, and every
  scenario has a test function `test_<title in snake_case>`.
- `no-comments: {}`: no `#` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do
  `# type: ignore`, `# noqa`, `# pragma:`, a shebang on line 1 and an encoding line on line 1 or 2.

## A protocol, not a closed world

`check` requires what the profile demands and is not bothered by anything else.

- Required: every top-level folder of the profile, and in every module `contract/`, `domain/`,
  `application/controller.py`, `application/services/`, `application/ports/` and `adapters/`. A missing one is
  reported, e.g. `app: missing web/` or `app/modules/docs: missing application/ports/`.
- Enforced: the section 5 import table between the parts the profile knows.
- Ignored: extra top-level folders, extra files or folders directly inside a module or `application/`
  (e.g. `modules/a/helpers.py`, `modules/a/utils/`, `application/helpers.py`), files at the app root. Files in
  places the profile does not govern are not checked, and imports into such places are not reported. Under
  `cli`, a `web/` folder is just an extra, and the other way round.
- Extra files and subfolders inside a known part (e.g. `domain/rules/x.py`) are welcome too; they belong to that
  part, so their imports are checked as that part's.

## Project docs

`init` also writes the project docs beside the app folder (in the folder holding it). The profile declares them: under
`docs:`, each key is a path below `docs/project/` and `from` names the template file it is written from (next to the
profile file; its `{{placeholders}}` are filled from the profile). A key ending in `/` is a folder, which only carries
a `note` for the docs tree; a file's optional `note` does the same. The order of the keys is the order of the docs. A
profile without `docs:` gets none.

```yaml
docs:
  statement.md:          {from: docs/statement.md, note: problem statement and use cases}
  architecture.md:       {from: web.md, note: this file}
  adrs/:                 {note: architecture decision records}
  adrs/0000-template.md: {from: docs/adr.md}
```

The two bundled profiles declare statement, domain, design, architecture, testing and requirements documents, and a
template folder for decision records and artifacts, from short templates: a title, the question the document answers,
and fixed section headings. The architecture and testing documents are written as content, since they are filled from
the profile. Existing files are skipped, never overwritten, and extras (e.g. `.obsidian/`) are left alone.

Copy a folder's template to start a new document of that kind. `new` does not touch the docs, and
`check` does not require them: they are not part of the app structure.

## Development

```
uv run pytest tests
uv tool install --editable . --reinstall     # refresh the system-wide `xarch`
```

`tests/architecture/test_self_check.py` runs xarch on its own source and tests, against `architecture.yaml` at the
repository root (named in `pyproject.toml`): the `cli` layout and rules, the outside packages xarch really uses, and
its tests as they are. `tests/architecture/test_agnostic.py` fails if xarch's code names a part of a bundled profile.
