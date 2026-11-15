# xarch

Check and scaffold an architecture described in an architecture file (a profile): its layout, its parts, which part
may import which, its test tiers and the guards it switches on. Two profiles are bundled, `cli` and `web`; a project
may also bring its own file. xarch knows no part by name: every name comes from the profile.

## Commands

```
xarch init [--app PATH] [--profile NAME|FILE]                 # create the top-level skeleton, record the profile in
                                                             # pyproject.toml, write the project docs and files; never overwrites
xarch new KIND NAME [--app PATH] [--profile NAME|FILE]       # create one folder of a kind with its full skeleton
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict]
                                                             # report every violation in the app and its tests,
                                                             # then the state of the check's own enforcement
xarch where PATH [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # what a path is and what code there may do, before it is written
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
exits 0 when clean, 1 with violations (or, with `--strict`, with an enforcement finding), and 2 on a usage error (a
missing app or tests folder, no profile or an unknown one, an invalid architecture file, an unreadable
`pyproject.toml`). Its output is described under [The output of check](#the-output-of-check). `init` and `new` exit 2 when they refuse (an invalid
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
- `forbidden` (with `forbidden:`): the names a part may not use, so that what a pure part promises (no clock, no
  I/O) is checked. An entry is a dotted name as an absolute import binds it (`datetime.datetime.now`; a builtin as
  `builtins.open`) or a whole package or module by its import name (`socket`). A file of the part may not import a
  listed module or anything below it (`import urllib.request` is `urllib`, `from time import time` is `time.time`),
  and may not use a listed name, called or not (`time.time` passed as a key counts), as the file writes it:
  through the import that binds its first name and its alias (`from datetime import datetime as dt; dt.now()`,
  `import datetime; datetime.datetime.now()`), or a builtin by its bare name where no scope shadows it (a
  parameter or an assignment named `open` hides it, and so does a star import). A use bound by an import that was
  itself reported is not reported again. It stays silent on what the file does not write as such a name: a name
  reached through a variable or `getattr`, a method of an object (`Path(p).read_text()`), an annotation, and
  anything a helper in another file does for the part. It is a ban list of names, not a proof that the part does
  no I/O. A tier with `forbidden: true` holds its tests to the list of the part they mirror; both bundled profiles
  give their pure parts (`domain`, `logic`, `kernel`, `ports`, `contract`) one list and set it on the unit tier.

  ```yaml
  forbidden:
    domain: &pure [datetime.datetime.now, datetime.date.today, time.time, builtins.open, builtins.print, socket]
    logic:  *pure
  ```
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
- `scenario-coverage: {results, tier, suffix, columns: [<state>, <command>, <result>], table, file}`: every union
  `<Name><suffix> = A | B` in a file of the `results` part has a test file named by `file` (`{name}` is `<Name>` in
  snake_case: `test_{name}.py`) among the `tier` tests of the same instance, read from its syntax tree and never
  run. The file holds a test function (a name matching `tests.functions`) decorated with the `table.decorator`
  (`pytest.mark.parametrize(<names>, <rows>)` in the bundled profiles), whose names (one comma-separated string,
  or a list or tuple of strings) include the three `columns`; the last is the result column. `<rows>` is a list or
  tuple literal, or the name of one assigned once at module level; any other form (a call, a concatenation, a
  comprehension, a starred element) is a violation, since a table that cannot be read cannot be checked. Every
  row is a call of `table.row` (`pytest.param(..., id="<sentence>")`) with a non-empty string literal as its
  `table.id` keyword: a bare tuple, a missing id or an id that is not a literal is a violation. `table.keywords`,
  optional, are the keywords the decorator's two positional arguments may be given by (`[argnames, argvalues]` for
  pytest); without it only positional arguments are read. The head of each row's result value (the callee of
  `Rejected("why")`, or a bare name) must be a variant of the union, and every variant must head at least one row,
  or be named anywhere in the body of a standalone test function of the same file (one with no table), the
  escape for a case that does not fit a row. The body of a table test holds no `if`, `match`, `try`, `for` or
  `while`. No docstring header is read.
- `no-comments: {}`: no `#` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do
  `# type: ignore`, `# noqa`, `# pragma:`, a shebang on line 1 and an encoding line on line 1 or 2.
- `stand-ins: {mocks, autospec, spec}` (needs `fakes: {path, for, prefix}`): a port is a `Protocol` class (`typing`'s or
  `typing_extensions`') in a part `fakes.for` names, and its kind follows from its methods' return annotations:
  every one `-> None` is fire-only, any one returning something else makes it a read port (a repository, written
  and read back), and a method with no return annotation is a violation. Dunder methods other than `__call__` are left out, a
  property counts as a method, inherited methods are not followed, and another class there is not a port. Every read port
  `X` has a class `<prefix>X` in a file below `fakes.path`. In the tests of a tier whose subject holds a part
  `fakes.for` names, every call of one of the `mocks` (`unittest.mock.Mock`, `MagicMock`, `AsyncMock`,
  `NonCallableMock`, `NonCallableMagicMock`) names its spec (first argument, or a keyword of `spec`: `spec=` or
  `spec_set=`), every call of one of the `autospec` functions (`unittest.mock.create_autospec`, optional) names it
  as its first argument or by the first keyword of `spec`, and a spec that is a read port of the app is a
  violation that points to its fake. All are dotted names an absolute import binds. It stays silent where it cannot read the
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
  stand-ins:
    mocks: [unittest.mock.Mock, unittest.mock.MagicMock]
    spec: [spec, spec_set]
  closed-tree: {}      # optional: report any file outside the parts
```

### The test framework

xarch holds no test framework: a profile names it. The top-level `tests:` key says what a test file and a test
function are called, and is required with `tiers:` and with `scenario-coverage` or `stand-ins`, the checks that must
tell a test from a helper; a profile with neither loads without it.

```yaml
tests:
  files: ["test_*.py", "*_test.py"]     # patterns of a file's name alone, `*` for any text, ending in .py
  functions: "test_*"
  skips: [pytest.mark.skip, pytest.mark.skipif, pytest.mark.xfail, pytest.skip, unittest.skip]   # optional
```

`skips` are the dotted names of what skips a test or expects it to fail, a marker or a call; `check` counts each use
of one in the tests in its enforcement section.

The names a framework gives a table of cases and a mock live in the two guards, as shown for pytest in `web.yaml`
and `cli.yaml`. To use another framework of the same shape, change those names and nothing else: for the `mock` backport, or a
house module of doubles, it is their dotted import paths in `mocks` (`mock.Mock`, `house.doubles.Double`); for a house wrapper around `parametrize`
(`from house import cases`) it is `table: {decorator: house.cases.table, row: house.cases.row, id: name}` with
`file: "{name}_spec.py"` and `tests: {files: ["*_spec.py"], functions: "it_*"}`. Messages and the generated
`testing.md` then speak in those names. Dotted names are what an absolute import binds, so a decorator reached by
`from house import cases` is read as `house.cases.table`; a name bound any other way is not followed. That is why pytest-mock's `mocker` fixture, which no import binds, is
not read.

What stays Python, and so in xarch's code: `typing.Protocol` as the mark of a port, `__init__.py`, the syntax tree,
import resolution and the standard library's names. The limit is the shape of the mechanism: a table is a decorator
holding rows (each a call that may carry an id), and a mock is built by a call that names its spec. A framework whose
cases or doubles have another shape cannot be described by these names, and leaves `scenario-coverage` or
`stand-ins` out of its profile.

## The output of check

### Text

One line per violation, `<file>[:<line>]: <message>`, in the order the checks run (the source checks, then the
structure), then a summary, `OK: no violations` or `<n> violation(s) in <m> file(s)`, then the enforcement section
(below). Paths are relative to the folder holding the app folder (`app/kernel/x.py`, `tests/...`).

### JSON

`xarch check --format json` prints one JSON document on stdout, and nothing else. This shape is a contract: fields
and rule ids may be added, but an existing one keeps its name and meaning.

```json
{
  "ok": false,
  "strict": false,
  "profile": "web",
  "violations": [
    {"rule": "forbidden", "file": "app/modules/docs/domain/clock.py", "line": 1,
     "message": "domain/ of modules/docs may not import socket (forbidden.domain)",
     "fix": "do what needs socket outside domain/, and hand domain/ the result"}
  ],
  "enforcement": {
    "profile": {"location": "web", "bundled": true, "closest": null, "guards_off": ["closed-tree"],
                "baseline_off": ["closed-tree"], "looser": []},
    "ungoverned": {"count": 0, "folders": [], "files": []},
    "init_files": [],
    "skipped": {"count": 0, "at": []},
    "dynamic": {"count": 0, "at": []},
    "weak": [],
    "strict_failures": []
  }
}
```

- `ok`: no violation, and with `--strict` no enforcement finding either; it agrees with the exit code. `strict`:
  whether `--strict` was given. `profile`: the profile in force, a bundled name or a path, as selected.
- `violations`: sorted by `file`, then `line` (a whole-file or folder violation, `line: null`, first), then `rule`.
  `file` is the path the text output prints; `message` the sentence it prints after the path; `fix` a short
  instruction when the check knows one, else `null`. `rule` is one of: `rules`, `libraries`, `forbidden`, `tiers`
  (a test's imports, or a test in no tier), `types-only`, `test-tree`, `cycles`, `structure`, `package-only`,
  `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`, and `syntax` (a file that does not parse).
- `enforcement`: every key always present, empty when there is nothing to report. `profile.looser` items are
  `{"key", "part", "what", "sentence"}` with `key` one of `rules`, `libraries`, `forbidden`, `untested`,
  `types_only`, `tier_forbidden`, `skips`, `pinned`; `init_files` items `{"file", "state"}`, `state` `missing` or
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `weak` items `{"rule", "file", "line",
  "message"}`; `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `looser`, `ungoverned`,
  `init_files`, `skipped`, `dynamic`, `weak`. `strict_failures` is filled whether or not `--strict` was given: it
  is what `--strict` fails on.
- A refusal (exit 2: an unknown or invalid profile, a missing folder) prints `{"ok": false, "error": "<reason>"}` on
  stdout, so a caller always gets JSON. Only an error in the command line itself (an unknown option, a `--format`
  that is neither `text` nor `json`) is typer's usage message on stderr.

### The enforcement section

A check can be made to pass by weakening it: by moving code where no rule applies, switching a guard off, loosening a
rule or deleting the guard test. So after the violations, and also when there are none, `check` reports the state of
its own enforcement. In text, a line with nothing to report is left out:

```
enforcement
  profile:     arch/mine.yaml (custom; closest bundled: web)
    guards off:  no-comments, closed-tree
    rules:       kernel may also import platform
  ungoverned:  1 Python file outside every part (app/scripts/)
  init files:  tests/architecture/test_rules.py is changed
  skipped:     1 skip (tests/modules/docs/domain/test_x.py:4)
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
```

- `profile`: the bundled name, or the custom file's path and the bundled profile it most resembles: the one sharing
  the most part names, the first by name on a tie; one sharing none resembles no bundled profile, and nothing is
  compared. `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
  too. For a custom file, each way it is looser than the one it resembles, compared only where both use the same
  name: a target added to a part's `rules`, an outside package added to its `libraries` (or `libraries` dropped), a
  name of its `forbidden` list no entry covers any more, a part newly `untested`, a part dropped from a tier's
  `types_only`, a tier no longer `forbidden`, a name dropped from `tests.skips`, a `files` entry no longer `pinned`.
  Stricter differences, new parts, the layout and the guards' parameters are not compared.
- `ungoverned`: the app's Python files in no part and no folder of the layout (what `closed-tree` would report),
  which no check reads, counted with their top folders.
- `init files`: each single file of the profile's `files:` that is missing beside the app folder, or, when the entry
  says `pinned: true`, that differs from what `init` would write now. The files of a folder entry (a preset) are
  copied once and not watched.
- `skipped`: each use in the tests of a name of `tests.skips`, or one below it, read through imports.
- `dynamic`: each use, in the files read, of `importlib.import_module`, `importlib.__import__` or the builtin
  `__import__`: Python's own, so they need no entry in the profile; the import rules cannot see what they import.
- `weak`, met to the letter only, never a violation: a fake `<prefix><Port>` that defines in its own body (methods,
  or names its body or `self.` assigns) less than every port of its name declares; and a `Result` variant that no
  row covers, credited only to standalone tests that name it and hold no `assert`.

Without `--strict` the section never changes the exit code. `--strict` fails (exit 1) on every finding listed in
`strict_failures`: each guard left off that the bundled profile in force, or the one a custom profile is compared
with, does not also leave off (with no profile to compare with, every guard left off); each looser item; each
ungoverned file; each missing or changed init file; each skip; each dynamic import; each weak finding. The text
lists them after the section, under `strict:`. The guard test `init` writes runs `check` without `--strict`: a
project opts in by running `xarch check --strict` in CI or a pre-commit hook.

## xarch where: ask before you write

`check` says what went wrong after the fact; `where` answers beforehand, for a person or a coding agent about to create
or move a file: what is this place, and what may code here do? The path may be there or not yet, and may be given from
the working folder, from the folder holding the app folder (the project root), or from the app folder: what exists
wins, else the app folder, then the tests folder, then the project root (a path starting with `..` is the working
folder's alone). It works for the app's paths and for the tests'. Everything it says comes from the profile; xarch
knows no part by name.

```
$ xarch where modules/documents/adapters/db_document_repo.py
path:            app/modules/documents/adapters/db_document_repo.py (new)
part:            adapters/ in module 'documents'
role:            driven only: repos, which translate the platform/ table models; use platform/ clients
litmus:          Does it implement one of this module's ports against a real system, ... (the part's litmus test)
may import:      its own module's `adapters/`, `application/ports/` and `domain/`, `kernel/`, `platform/`, any module's `contract/`
libraries:       sqlmodel
tested by:       unit tier: tests/modules/documents/adapters/test_db_document_repo.py
```

For a path in the app: its part and the instance of the repeating folder, the part's role and litmus test, what it may
import (its `rules`, in the words of the docs' rules table), the outside packages it may import (`libraries`: `none`, or
`not checked` when the profile has none), the names it may not use (`forbidden`), and the tier that tests it with the
file its test would be in (a part that is one file, such as a controller, has its test by use case:
`test_<use case>.py`; a part no tier tests says why). A path in no part is `ungoverned`, with the parts near it (those
below the nearest folder of the layout that holds it) and whether `closed-tree` is on; a folder of the layout that no
part claims is `structure`. A path in the project but outside the app and its tests is ungoverned too.

For a path in the tests: its tier, the part its folder mirrors, what it may import (the per-part rule: that part and what
it may import), whether it may import the fakes, the parts it may use as types only, what the tier proves and may touch,
its litmus test, and the one folder it may import test code from. A test that lies in no tier says so (`note`); a file
below the fakes' folder is a `fake`, any other file that is no test a `support` file.

Exit 0 for every path inside the project, placed or not; 2 for a path outside it or a profile that cannot be used (with
`--format json`, `{"ok": false, "error": "..."}`, as `check` does).

### JSON

`xarch where PATH --format json` prints one JSON document on stdout. Like `check`'s, the shape is a contract: fields may
be added, an existing one keeps its name and meaning. A field that does not apply is `null` (an empty list for a list).

```json
{
  "ok": true,
  "profile": "web",
  "path": "app/modules/documents/domain/document.py",
  "exists": true,
  "kind": "part",
  "part": {"name": "domain", "folder": "domain/", "instance": "documents", "singular": "module",
           "role": "entities, values (incl. ids), errors: invariants only", "litmus": "Is it an invariant of ..."},
  "may_import": [{"part": "domain", "scope": "own", "folder": "domain/", "path": "app/modules/documents/domain/"},
                 {"part": "kernel", "scope": "none", "folder": "kernel/", "path": "app/kernel/"}],
  "may_import_text": "its own module's `domain/`, `kernel/`",
  "libraries": [],
  "forbidden": ["datetime.datetime.now", "builtins.open"],
  "tier": {"name": "unit", "proves": "...", "may_touch": "...", "litmus": "..."},
  "tested_in": {"folder": "tests/modules/documents/domain/", "file": "test_document.py"},
  "untested": null,
  "nearest": [],
  "closed_tree": null,
  "test": null,
  "note": null
}
```

- `kind`: `part`, `structure`, `ungoverned`, `test`, `fake` or `support`. `path` is relative to the folder holding the
  app folder; `exists` says whether it is there now.
- `part`: for `part`, the part the path lies in; for a `test`, the part it mirrors; else null. `instance` and
  `singular` are empty when the part is not in the repeating folder.
- `may_import`: one item per target of the part's rule (for a test: of the part it mirrors and of what that may import):
  `scope` is `own` (the same instance), `any` (any instance) or `none`; `folder` is the part as the docs name it, `path`
  its folder below the project root, with `<module>` (the profile's `singular`) for an instance that is not fixed.
  `may_import_text` says the same in words; `libraries` is the list of outside packages, null when the profile does
  not check them; `forbidden` the dotted names the part may not use.
- `tier`: for a `part`, the tier that tests it (null when none does, and `untested` then says why); for a test, its tier.
  `tested_in`: for a `part`, the test folder and the file (`file` is empty when the path is a folder or no Python file,
  a pattern for a use case's test).
- `nearest`: for `structure` and `ungoverned`, the parts near it: `{"part", "folder", "path"}`. `closed_tree`: for
  `ungoverned`, whether `closed-tree` is on (that is, whether `xarch check` reports the file), else null.
- `test`: for `test`, `fake` and `support`: `{"may_use_fakes", "fakes_path", "types_only", "code_from"}`, whether it
  may import the fakes, where they live, the parts it may use as types and never call, and the folder it may import test
  code from. `note`: one line where the kind alone does not say it.

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

## Project files

`init` can also write files that are not docs, beside the app folder (in the folder holding it, with `docs/` and
`pyproject.toml`), or inside it. The profile declares them under `files:`: each key is a path relative to that folder,
and `from` names the template file it is written from (next to the profile file). A path may not be empty, start with
`/`, hold `..` or an empty step, or clash with a doc (`docs/project/<path>`); a missing template, an unknown key or a
value that is not a mapping is reported with the other problems of the file. The order of the keys is the order they
are written in, a file is never overwritten (what exists is reported `skipped`), and a profile without `files:` writes
none.

A file is its template as it stands, except for one placeholder: `{{app}}` is replaced by the name of the app folder
(`shop` for `--app src/shop`), so a file that must find the app folder can name it. Any other `{{...}}` is written
unchanged. These are not the docs' placeholders: `{{tree}}` and the rest only fill docs.

An entry may say `pinned: true`: the project keeps the file as `init` writes it, and `check` reports it in its
enforcement section when it differs from what `init` would write now (any listed file is reported when it is
missing). A file a project is expected to edit, such as a linter config or an agent instructions file, is left
unpinned. Both bundled profiles pin the guard test.

```yaml
files:
  tests/architecture/test_rules.py: {from: examples/shared/tiers/guard.py, pinned: true}
```

### Presets: a folder of ready-made files

A key ending in `/` is a folder entry: its `from` is a folder next to the profile, and `init` copies every file under
it below the key, keeping the relative paths, never overwriting (each file is reported `created` or `skipped`). The
source folder must hold at least one file. `{{app}}` may start or sit inside a key, and stands for the app folder, whose
name changes with `--app`, so a preset can land inside the app, even inside a part:

```yaml
files:
  "{{app}}/web/ui/design/": {from: presets/design-system/}      # a design system, dropped into a part
  AGENTS.md:                {from: agents.md}                    # a single file, filled
  assets/logo.png:          {from: presets/logo.png, fill: false}
```

- `fill`: whether `{{app}}` in the text is replaced. A file entry is filled by default, as always; a folder entry is
  not (`fill: false`), since a preset is usually foreign content: it is copied byte for byte, so fonts and images
  survive and a text with braces of its own stays as it is. Set `fill: true` on a folder to fill its text; a file that
  is not valid UTF-8 is then refused, naming the file, and so is a filled file entry.
- `pinned` is for single files only: a folder entry cannot be pinned, because a project edits a preset it copied. The
  enforcement section's `init files` therefore lists a single file that is missing (or pinned and changed), and never
  the files of a folder entry.
- Inside the app, an entry may not replace what the skeleton writes: the package file (`__init__.py`) of the app or of
  any folder of the layout, a folder or file of the layout itself, in any instance of a repeating folder. A target
  inside a part is fine and intended. Two entries may not land on the same file, an entry may not lie inside a folder
  entry (nor a folder entry inside another), and a folder entry may not collide with a doc. All of these are reported
  with the other problems of the profile, or by `init` before it writes anything when only the app's name shows them.
- Shipped code is checked code: a Python file that lands in a part is read by `check` like any other, and breaks the
  part's rules or `forbidden` names like any other. xarch ships no preset of its own; this is the mechanism only.

Both bundled profiles list three files: the guard test, `AGENTS.md` and `ruff.toml`. The last two are not pinned: a
project edits them.

`AGENTS.md` (at the project root, about 40 lines) is written for a coding agent that has never seen xarch: what governs
the project (the profile and `docs/project/`), to run `xarch where <path>` before creating or moving a file and to
take the first litmus test a piece of code passes, to run `xarch check` and `ruff check` before finishing, how tests are
written (tiers, the Given/When/Then table, fakes and spec'd mocks), and what not to do to get a green check: move code
into a folder no part covers, switch a guard off or loosen the profile, edit the guard test, skip a test. It is static
text (it names the app folder with `{{app}}`), the same for both profiles.

`ruff.toml` holds only the linter rules that are the same for every file: pyflakes and pycodestyle errors, import sorting,
absolute imports only, a return annotation on public functions (which the `stand-ins` guard needs on a port's
methods), the pytest-style rules (a table's names as one comma-separated string, its rows as a list), no `print`, no
naive datetime and no unused `noqa`, for Python 3.13 and a line length of 140, which fits the docs' code. Anything
that differs by part (which imports, names or outside packages a part may use) is the profile's job, via `rules`,
`libraries` and `forbidden`, checked by `xarch check`; it is not repeated in a generated file that would go stale.
`xarch check` does not run the linter or know about it.

The guard test, `tests/architecture/test_rules.py`, runs `python -m xarch check --app
<project>/<app>` with the interpreter running the test, and fails with `xarch check`'s output, the violations, as its
message, so every guard runs with the project's test suite; xarch must be installed in that environment. It does
not pass `--strict`, so the enforcement section is printed in its message but does not fail it; a project that wants
strictness runs `xarch check --strict` in CI or a pre-commit hook (editing the pinned guard test would itself be
reported as changed). It is also the guard tier's example in `testing.md`, from the same template
with `{{app}}` filled in as `app`.

## Development

```
uv run pytest tests
uv run ruff check                           # ruff.toml: the bundled linter config, plus what only this repository needs
uv tool install --editable . --reinstall     # refresh the system-wide `xarch`
```

`tests/architecture/test_self_check.py` runs xarch on its own source and tests, against `architecture.yaml` at the
repository root (named in `pyproject.toml`): the `cli` layout and rules, the outside packages xarch really uses, and
its tests as they are. `tests/architecture/test_agnostic.py` fails if xarch's code names a part of a bundled profile or a name of
its test framework or the linter (xarch's code never runs it). The repository's own `ruff.toml` is the template the
bundled profiles write (`xarch/architectures/lint.toml`, named so that the linter does not read it as a config of
its own) plus an exclusion of the reference snippets under `xarch/architectures/examples/` and of `.claude/`; a test
keeps the two identical otherwise.
