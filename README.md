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
  (`tests/architecture/` is the guard tier's). A test imports only the part its folder mirrors and what that part
  may import under `rules:`, `@own` meaning the instance it mirrors (a test directly in `application/` has the
  file parts there, such as `controller.py`); a test in a folder that mirrors no part (the guard tier's) imports
  its tier's subject parts and what those may import. It imports the fakes only when its tier tests a part
  `fakes:` stands in for, and other test code only from its own folder (`tests/<each root>/<name>/` or
  `tests/<top folder>/`). A test file in no tier is a violation; a helper above every part's folder
  (`tests/conftest.py`, `tests/modules/<name>/builders.py`) and the fakes are not import-checked.
- `types-only` (with a tier's `types_only: [<part>, ...]`): that tier's tests may import those parts and use them
  as types, but never call what they import from them: `def build(controller: DocumentController)` is fine,
  `DocumentController(...)` is not. A call is read through the import that binds its name (`from m import X as Y`,
  `import m as a` then `a.X(...)`, `import m` then `m.X(...)`); a name bound otherwise in its scope (a parameter,
  an assignment) is not followed. Both bundled profiles give the rendering tier `types_only: [controller]`.
- `test tree`: every folder below `tests/<each root>/` mirrors a folder of the app.
- `cycles` (with an `each:` folder): no instance imports from another that imports, directly or through others,
  from it. Each elementary cycle is reported once, at its first import, with its instances in order from the first
  by name and the import that links each to the next.

Switched on by name in `guards:`:

- `package-only: [<part>, ...]`: the parts are imported as a package, never by their files, from outside them.
- `scenario-coverage: {results, tier, suffix, columns: [<state>, <command>, <result>]}`: every union
  `<Name><suffix> = A | B` in a file of the `results` part has a test file `test_<name>.py` (snake_case) among the
  `tier` tests of the same instance, read from its syntax tree and never run. The file holds a test function (name
  starting `test_`) decorated `pytest.mark.parametrize(<names>, <rows>)`, whose names (one comma-separated string,
  or a list or tuple of strings) include the three `columns`; the last is the result column. `<rows>` is a list or
  tuple literal, or the name of one assigned once at module level; any other form (a call, a concatenation, a
  comprehension, a starred element) is a violation, since a table that cannot be read cannot be checked. Every
  row is `pytest.param(..., id="<sentence>")` with a non-empty string literal as its id: a bare tuple, a missing
  id or an id that is not a literal is a violation. The head of each row's result value (the callee of
  `Rejected("why")`, or a bare name) must be a variant of the union, and every variant must head at least one row,
  or be named anywhere in the body of a standalone `test_` function of the same file (one with no table), the
  escape for a case that does not fit a row. The body of a table test holds no `if`, `match`, `try`, `for` or
  `while`. No docstring header is read.
- `no-comments: {}`: no `#` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do
  `# type: ignore`, `# noqa`, `# pragma:`, a shebang on line 1 and an encoding line on line 1 or 2.
- `stand-ins: {}` (needs `fakes: {path, for, prefix}`): a port is a `Protocol` class (`typing`'s or
  `typing_extensions`') in a part `fakes.for` names, and its kind follows from its methods' return annotations:
  every one `-> None` is fire-only, any one returning something else makes it a read port (a repository, written
  and read back), and a method with no return annotation is a violation. Dunder methods other than `__call__` are left out, a
  property counts as a method, inherited methods are not followed, and another class there is not a port. Every read port
  `X` has a class `<prefix>X` in a file below `fakes.path`. In the tests of a tier whose subject holds a part
  `fakes.for` names, every `unittest.mock` `Mock`, `MagicMock`, `AsyncMock`, `NonCallableMock`,
  `NonCallableMagicMock` and `create_autospec` names its spec (first argument, `spec=` or `spec_set=`), and a spec
  that is a read port of the app is a violation that points to its fake. It stays silent where it cannot read the
  code: a call that unpacks `*args`/`**kwargs`, a spec that is a variable, an expression or a string, a port
  re-exported by a package, and mocks made by `patch`.
- `closed-tree: {}`: every Python file of the app lies in a part or is the `__init__.py` of a folder of the layout,
  which only holds the tree together. Off in both bundled profiles, whose tree is a protocol, not a closed world.

```yaml
tiers:
  - name: rendering
    subject: [web]
    types_only: [controller]
fakes: {path: tests/fakes, for: [ports], prefix: Fake}
guards:
  stand-ins: {}
  closed-tree: {}      # optional: report any file outside the parts
```

## A protocol, not a closed world

`check` requires what the profile demands and is not bothered by anything else.

- Required: every top-level folder of the profile, and in every module `contract/`, `domain/`,
  `application/controller.py`, `application/services/`, `application/ports/` and `adapters/`. A missing one is
  reported, e.g. `app: missing web/` or `app/modules/docs: missing application/ports/`.
- Enforced: the section 5 import table between the parts the profile knows.
- Ignored: extra top-level folders, extra files or folders directly inside a module or `application/`
  (e.g. `modules/a/helpers.py`, `modules/a/utils/`, `application/helpers.py`), files at the app root. Files in
  places the profile does not govern are not checked, and imports into such places are not reported. Under
  `cli`, a `web/` folder is just an extra, and the other way round. A profile that wants a closed world switches
  on the `closed-tree` guard, and then every such file is reported.
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
