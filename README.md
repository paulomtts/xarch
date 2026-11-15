# xarch

Check and scaffold an architecture described in an architecture file (a profile): its layout, its parts, which part
may import which, its test tiers and the guards it switches on. Two profiles are bundled, `cli` and `web`; a project
may also bring its own file. xarch knows no part by name: every name comes from the profile.

## Commands

```
xarch init [--app PATH] [--profile NAME|FILE]                 # create the top-level skeleton, record the profile (and the
                                                             # app folder, if not app/) in pyproject.toml, write the
                                                             # project docs and files; never overwrites
xarch new WORD NAME [--app PATH] [--profile NAME|FILE]       # create one instance of the repeating folder, with its skeleton
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict]
                                                             # report every violation in the app and its tests, each
                                                             # with its fix, then the state of the check's own enforcement
xarch where PATH [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # what a path is and what code there may do, before it is written
xarch profile migrate FILE [--out FOLDER] [--dry-run]        # convert a profile of format 1 to format 2, in a new folder
```

`WORD` is the word between `<` and `>` in the profile's paths: in both bundled profiles `<module>`, so
`xarch new module documents` creates `modules/documents/` with every folder a module holds. The folder's own name
(`xarch new modules documents`) is refused, and the message says what to type. A profile has at most one repeating
folder.

`--app` defaults to the app folder recorded under `[tool.xarch]` (see below), else to `app` (relative to the working
directory); the flag wins over what is recorded. The app's import name is its folder's name. `check`
exits 0 when clean, 1 with violations (or, with `--strict`, with an enforcement finding), and 2 on a usage error (a
missing app or tests folder, no profile or an unknown one, an invalid profile file, an unreadable `pyproject.toml`).
`init` and `new` exit 2 when they refuse (an invalid name, a kind the profile does not declare, a folder that already
exists, no skeleton yet). The output of `check` is described under [The output of check](#the-output-of-check).

## Profiles

| Profile | Top level |
|---|---|
| `cli` | `modules/`, `platform/`, `cli/` (`commands/`), `bootstrap/` (`migrations/`), `kernel/` (`logic/`) |
| `web` | `modules/`, `platform/`, `web/` (`routes/`, `i18n/`, `ui/`), `bootstrap/` (`migrations/`), `kernel/` (`logic/`) |

The profile is a bundled name or a path to a file (`.yaml` or `.json`), chosen in this order:

1. `--profile` on the command (a path is relative to the working directory);
2. `profile` under `[tool.xarch]` in the nearest `pyproject.toml`, looked up from the folder holding the app
   folder upward (the nearest one decides, even when it has no `[tool.xarch]` table); a path is relative to the
   folder holding that `pyproject.toml`.

With neither, the command fails with exit code 2 and lists the profiles found: no profile is assumed. The file is
loaded and validated before anything runs; a bad one is reported with every problem in it, each naming the key by its
address in the file. `init` records the profile it used in that `pyproject.toml` (creating one beside the app folder
if there is none), and, when the app folder is not `app/` beside it, the app folder too, so a bare `xarch check` uses
both. It never changes a value already recorded.

```toml
[tool.xarch]
profile = "web"          # or a path, such as "architecture.yaml"
app = "src/shop"         # optional; the app folder, relative to this file; recorded by `init --app src/shop`
tests = "tests"          # optional; the default is tests/ beside the app folder, when it exists
```

## The profile file

A profile starts with `xarch: 2` and states each fact once, on the thing it is about. Its parts are listed in the
order their litmus tests run, and that order is also the order of the generated docs' tree and rules table.

```yaml
xarch: 2
name: shop
testing: pytest
parts:
  domain:
    path: modules/<module>/domain
    role: entities and values: invariants only
    may_import: [kernel]
    forbidden: pure
    tier: unit
  adapters:
    path: modules/<module>/adapters
    role: driven implementations of the module's ports
    may_import: [domain, kernel, platform, contract@any]
    libraries: [sqlmodel]
    tier: unit
  platform:
    path: platform
    role: clients of outside technology
    may_import: [kernel]
    libraries: [sqlmodel]
    untested: reached through the adapters that use it
  kernel:
    path: kernel
    role: pure primitives
    forbidden: pure
    tier: unit
    folders: {logic: pure functions that modules share}
forbidden:
  pure: [datetime.datetime.now, time.time, builtins.open, builtins.print, socket]
tiers:
  unit: {proves: a rule or a translation, apply_forbidden: true}
```

The smallest valid profile is a name and its parts; it runs `structure`, the import rules, `libraries` and `syntax`:

```yaml
xarch: 2
name: tiny
parts:
  core: {path: core, role: the rules}
  cli:  {path: cli, role: commands and output, may_import: [core], libraries: [typer]}
```

Adding tests is `testing: pytest`, `tiers: {unit: {}}`, and `tier: unit` or `untested: <reason>` on each part.

The symbols:

- `<module>` in a `path`: the repeating folder, one instance per name; the word is what `xarch new` takes and what the
  docs call one instance. A profile has one repeating folder. A last step with a dot (`controller.py`) is a file.
- A bare name in `may_import` (`domain`): that part, in the importer's own instance when it lies in the repeating
  folder. `domain@any`: any instance. `domain/values`: only that path below the part. A part may always import
  itself, so it never lists itself.
- `everything`: for `may_import`, every part; for `libraries`, every outside package, unchecked. A part that writes
  no `libraries` may import none (the standard library is always allowed).
- `forbidden: pure` on a part: the part may not use the names of the top-level list `forbidden.pure`.
- `folders`: folders below a part that the layout shows, each with its note.

`based_on` names the bundled profile a file was copied from, which the enforcement section compares it with. The bundled
`web.yaml` and `cli.yaml` are complete examples; a per-key reference will come from `xarch profile explain`.

### Migrating a profile of format 1

A file that starts `xarch: 1` is refused by every command, which names `xarch profile migrate FILE`. That command
writes the format 2 profile and the files it names into a new folder (`FILE`'s name with `-v2`, or `--out FOLDER`),
never over a file that exists and never changing the old ones; example files go to the paths they illustrate, and
`{{example:<name>}}` in the templates becomes `{{example:<path>}}`. It validates the result before writing (`--dry-run`
stops there), lists under `changed:` what now means something else and under `by hand:` what has no form in format 2.
YAML comments are not carried over.

## What check checks

`check` reads only the files the profile governs: a file in a part, or a package file of a folder of the layout (the
folders the parts' paths and `folders` make). A file anywhere else is never read, and is listed as `ungoverned` in the
enforcement section. A folder that is not the app's source at all (reference code kept as data, such as xarch's own
`architectures/examples/`) is declared with [`excluded`](#excluded-and-hints) instead, and then no check looks at it.

From the profile itself:

- `structure`: every folder and file of the layout exists, at any depth (`kernel/logic/`, `web/routes/`), in the app
  and in every instance of the repeating folder.
- `rules`: every import between parts is one that the importing part's `may_import` allows. A part may always import
  itself (its own instance, for a part in the repeating folder), so a list that only restates it is refused;
  `domain@any` in the list of `domain` says more, another instance's, and stays.
- `libraries`: a part imports only the outside packages in its `libraries`, by top-level import name; the standard
  library (`sys.stdlib_module_names`) is always allowed, and tests are not checked.
- `forbidden`: the names a part may not use, so that what a pure part promises (no clock, no I/O) is checked. An entry
  is a dotted name as an absolute import binds it (`datetime.datetime.now`; a builtin as `builtins.open`, since a
  bare `open` is refused: it would ban nothing) or a whole package or module (`socket`). A file of the part may not
  import a listed module or anything below it, and may not use a listed name, called or not, as the file writes it:
  through the import that binds its first name and its alias, or a builtin by its bare name where no scope shadows
  it. It stays silent on a name reached through a variable or `getattr`, a method of an object, an annotation, and
  what a helper in another file does for the part: a ban list of names, not a proof that the part does no I/O. A
  tier with `apply_forbidden: true` holds its tests to the list of the part they mirror.
- `tiers`: tests mirror the app, `tests/<path>` for the app's `<path>`. A file's tier is that of the part its folder
  mirrors (the one the part names with `tier`); a file directly in the folder of file parts (such as `application/`,
  holding `controller.py`) takes their tier; a folder that mirrors no part belongs to the tier whose `folder` holds
  it (a path below `tests/`: relative, no `..`, no `*`, not a part's folder or the `fakes` folder), and that tier's
  `may_import` says what its tests may import of the app. A test imports only the part its folder mirrors and what
  that part may import, a bare name meaning the instance it mirrors; the fakes only when its tier tests a part
  `fakes.for` names; other test code only from its own folder. A test file in no tier is a violation; helpers above
  every part's folder (`tests/conftest.py`) and the fakes are not import-checked.
- `types-only` (a tier's `types_only: [<part>, ...]`): that tier's tests may import those parts and use them as
  types, but never call what they import from them: `def build(controller: DocumentController)` is fine,
  `DocumentController(...)` is not. A call is read through the import that binds its name; a name that an import
  binds to a module-level function of such a part may not be referenced at all (`map(allowed, xs)` is reported).
  References to classes outside calls stay allowed (`isinstance`, exception matching, enum members).
- `test tree`: every folder below `tests/<root of the repeating folder>/` mirrors a folder of the app.
- `cycles` (with a repeating folder): no instance imports from another that imports, directly or through others,
  from it. Each elementary cycle is reported once, at its first import, with its instances in order from the first
  by name and the import that links each to the next.

Switched on by name in `guards`, each a map (`{}` when it takes nothing):

- `package_only: true` on a part: the part is imported as a package, never by its files, from outside it.
- `scenario-coverage: {results, tier, suffix, columns: [<state>, <command>, <result>], file}`: every union
  `<Name><suffix> = A | B` in a file of the `results` part has a test file named by `file` (`{name}` is `<Name>` in
  snake_case) among the `tier` tests of the same instance, read from its syntax tree and never run. The file holds a
  test function decorated with the `testing.table` decorator whose names include the three `columns` (the last is
  the result column); the rows are a literal list or tuple, each a call of `testing.table.row` with a non-empty
  string literal as its id; the head of each row's result must be a variant of the union, and every variant must
  head a row or be named in a standalone test of the file. A table test holds no `if`, `match`, `try`, `for` or
  `while`. Needs `testing.table`.
- `no-comments: {}`: no `#` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do
  `# type: ignore`, `# noqa`, `# pragma:`, a shebang on line 1 and an encoding line on line 1 or 2.
- `stand-ins: {}` (needs `fakes` with a `prefix`, and `testing.mocks`): a port is a `Protocol` class in a part
  `fakes.for` names; every method `-> None` makes it fire-only, any other return makes it a read port, and a method
  with no return annotation is a violation. Every read port `X` has a class `<prefix>X` in the `fakes` folder. In the
  tests of a tier whose subject holds such a part, every call of one of `testing.mocks.calls` names its spec
  (first argument, or a keyword of `spec_keywords`), `autospec` calls name it as their first argument, and a spec
  that is a read port is a violation that points to its fake; `fixtures` names the parameters (pytest-mock's
  `mocker`) whose methods build mocks. It stays silent where it cannot read the code: `*args`, a spec that is a
  variable, a re-exported port, mocks made by `patch`.
- `closed-tree: {}`: every Python file of the app lies in a part or is the `__init__.py` of a folder of the layout,
  which only holds the tree together (a folder the profile `excluded` is not looked at). Off in both bundled
  profiles, whose tree is a protocol, not a closed world.

### The test framework

xarch holds no test framework: a profile names it with `testing`, required with `tiers` and with `scenario-coverage`
or `stand-ins`, the checks that must tell a test from a helper. `testing: pytest` is a preset shipped with xarch; for
another framework write the map it stands for:

```yaml
testing:
  files: ["test_*.py", "*_test.py"]
  functions: "test_*"
  skips: [pytest.mark.skip, pytest.skip, unittest.skip]
  table: {decorator: pytest.mark.parametrize, row: pytest.param, id: id, keywords: [argnames, argvalues]}
  mocks:
    calls: [unittest.mock.Mock, unittest.mock.MagicMock]
    autospec: [unittest.mock.create_autospec]
    spec_keywords: [spec, spec_set]
    fixtures: {mocker: {calls: [Mock, MagicMock], autospec: [create_autospec]}}
```

`skips` are the dotted names of what skips a test or expects it to fail, which `check` counts in its enforcement
section. Dotted names are what an absolute import binds, so a decorator reached by `from house import cases` is read
as `house.cases.table`; a fixture, which no import binds, is named by `mocks.fixtures`: the parameter and the methods
that build a mock. What stays Python, and so in xarch's code: `typing.Protocol` as the mark of a port, `__init__.py`,
the syntax tree, import resolution and the standard library's names. A framework whose tables or doubles do not have
the shape of a decorator holding rows and a call that names its spec leaves `scenario-coverage` or `stand-ins` out.

### Excluded and hints

Two optional keys of a profile.

`excluded: {<folder>: <reason>}` names folders below the app that are not its source, such as example code shipped as
data. A folder is a path below the app (`architectures/examples`) with no `..`, no leading `/` and no `*`; it may not
be a folder of the layout, nor lie inside or hold another excluded folder; the reason is one line of text and is
required. No check reads a Python file below an excluded folder (so `closed-tree` and the `ungoverned` list leave it
out), and `check` lists each one with its reason in its enforcement section, so the exclusion stays visible. It is not
a finding for `--strict`. `xarch where` on a path inside one says it is excluded and why.

`hints: {<rule id>: <text>}` adds the project's own advice to a rule: one line of text, shown after the built-in `fix`
of every violation of that rule, as a `hint:` line in the text output and as `hint` in the JSON. The rule id is the
`rule` a violation names (`rules`, `libraries`, `forbidden`, `tiers`, `types-only`, `test-tree`, `cycles`,
`structure`, `package-only`, `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`, `syntax`); any other id
is refused when the profile loads, naming the ones there are. The bundled profiles set none.

```yaml
excluded:
  architectures/examples: example projects the bundled profiles ship as data; never imported or run
hints:
  rules: the layers and what each may import are in docs/project/architecture.md
```

## The output of check

### Text

Every violation says what to do about it. A finding is its line, `<file>[:<line>]: <message>`, then an indented line
`fix: <what to do>`, one imperative sentence specific to the finding, and, when the profile has a
[hint](#excluded-and-hints) for its rule, an indented `hint: <text>` line. The findings come in the order the checks
run (the source checks, then the structure), then a summary, `OK: no violations` or `<n> violation(s) in <m>
file(s)`, then the enforcement section (below). Paths are relative to the folder holding the app folder
(`app/kernel/x.py`, `tests/...`).

```
app/kernel/x.py:1: kernel/ may not import platform/ (app.platform)
    fix: import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to adapters/, which may import it
    hint: the layers are in docs/project/architecture.md
1 violation(s) in 1 file(s)
```

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
     "message": "domain/ of modules/docs may not import socket (parts.domain.forbidden)",
     "fix": "do what needs socket outside domain/, and hand domain/ the result",
     "hint": null}
  ],
  "enforcement": {
    "profile": {"location": "web", "bundled": true, "closest": null, "guards_off": ["closed-tree"],
                "baseline_off": ["closed-tree"], "looser": []},
    "ungoverned": {"count": 0, "folders": [], "files": []},
    "excluded": [],
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
  `file` is the path the text output prints; `message` the sentence it prints after the path; `fix` what to do about
  it, always a non-empty string (a violation cannot be made without one); `hint` the profile's own advice for the
  rule, else `null`. `rule` is one of: `rules`, `libraries`, `forbidden`, `tiers`
  (a test's imports, or a test in no tier), `types-only`, `test-tree`, `cycles`, `structure`, `package-only`,
  `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`, and `syntax` (a file that does not parse).
- `enforcement`: every key always present, empty when there is nothing to report. `profile.looser` items are
  `{"key", "part", "what", "sentence"}` with `key` one of `may_import`, `libraries`, `forbidden`, `untested`,
  `types_only`, `apply_forbidden`, `testing.skips`, `files.pinned` (the `sentence` names the full address, such as
  `parts.kernel.may_import`); `excluded` items `{"folder", "reason"}`; `init_files` items `{"file", "state"}`, `state` `missing` or
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `weak` items `{"rule", "file", "line",
  "message"}`; `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `ungoverned`, `init_files`,
  `skipped`, `dynamic`, `weak`. `strict_failures` is filled whether or not `--strict` was given: it
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
    may_import:  kernel may also import platform (parts.kernel.may_import)
  ungoverned:  1 Python file outside every part (app/scripts/)
  excluded:    app/examples/ (example sources the docs show)
  init files:  tests/architecture/test_rules.py is changed
  skipped:     1 skip (tests/modules/docs/domain/test_x.py:4)
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
```

- `profile`: the bundled name, or the custom file's path and the bundled profile it is based on or, failing that,
  most resembles (the first by name on a tie); one sharing no part resembles none, and nothing is compared. `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
  too. For a custom file, each way it is looser than the one it resembles, compared only where both use the same
  name: a target added to a part's `may_import`, an outside package added to its `libraries` (or `everything`), a
  name of its `forbidden` list no entry covers any more, a part newly `untested`, a part dropped from a tier's
  `types_only`, a tier no longer `apply_forbidden`, a name dropped from `testing.skips`, a `files` entry no longer
  `pinned`. A profile that says `based_on: <bundled name>` is compared with that one, else with the one sharing the
  most part names.
  Stricter differences, new parts, the layout and the guards' parameters are not compared. This comparison is
  information: the profile defines the architecture, so how it differs from another is no finding for `--strict`.
- `ungoverned`: the app's Python files in no part and no folder of the layout (what `closed-tree` would report),
  which no check reads, counted with their top folders.
- `excluded`: each folder the profile's `excluded` key leaves out, with its reason; no check reads a file below it,
  so the exclusion stays visible here.
- `init files`: each single file of the profile's `files` that is missing beside the app folder, or, when the entry
  says `pinned: true`, that differs from what `init` would write now. The files of a folder entry (a preset) are
  copied once and not watched.
- `skipped`: each use in the tests of a name of `testing.skips`, or one below it, read through imports.
- `dynamic`: each use, in the files read, of `importlib.import_module`, `importlib.__import__` or the builtin
  `__import__`: Python's own, so they need no entry in the profile; the import rules cannot see what they import.
- `weak`, met to the letter only, never a violation: a fake `<prefix><Port>` that defines in its own body (methods,
  or names its body or `self.` assigns) less than every port of its name declares; and a `Result` variant that no
  row covers, credited only to standalone tests that name it and hold no `assert`.

Without `--strict` the section never changes the exit code. `--strict` fails (exit 1) on every finding listed in
`strict_failures`: what the profile in force leaves unenforced or unseen: each guard left off that the bundled profile
in force, or the one a custom profile is compared with, does not also leave off (with no profile to compare with,
every guard left off); each ungoverned file; each missing or changed init file; each skip; each dynamic import; each weak finding. The text
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
import (its `may_import`, in the words of the docs' rules table), the outside packages it may import (`libraries`: `none`,
a list, or `any outside package`), the names it may not use (`forbidden`), and the tier that tests it with the
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
  its folder below the project root, with `<module>` (the word in the profile's paths) for an instance that is not fixed.
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

- Required: every folder and file the parts and their `folders` make, in the app and in every instance of the repeating
  folder. A missing one is reported, e.g. `app: missing web/` or `app/modules/docs: missing application/ports/`.
- Enforced: the import rules between the parts the profile knows.
- Ignored: extra top-level folders, extra files or folders directly inside an instance or a folder that is no part,
  files at the app root. Files in places the profile does not govern are not checked, and imports into such places are
  not reported. A profile that wants a closed world switches on `closed-tree`, and then every such file is reported.
- Extra files and subfolders inside a known part belong to that part, so their imports are checked as that part's.

## Project docs

`init` also writes the project docs beside the app folder (in the folder holding it). The profile declares them under
`docs.pages`: each key is a path below `docs/project/` and its value the template file it is written from (a bare
string, or `{from, note}`; the file lies next to the profile and its `{{placeholders}}` are filled from the profile).
A key ending in `/` is a folder, which only carries a `note` for the docs tree. The order of the keys is the order of
the docs. A profile without `docs.pages` gets none. The rest of `docs` only feeds the generated pages: `entry` (the part
that is the entry point), `naming` (the naming table) and the examples.

```yaml
docs:
  entry: web
  pages:
    statement.md: {from: docs/statement.md, note: problem statement and use cases}
    architecture.md: {from: web.md, note: this file}
    adrs/: {note: architecture decision records}
    adrs/0000-template.md: docs/adr.md
```

`docs.examples` lists folders next to the profile, each an example project (`examples/shared`, `examples/web`): a file
below one is an example, named by its path in the project (`modules/documents/domain/document.py`), the part it
illustrates is the part that path lies in, and a template quotes it with `{{example:<path>}}`. `docs.example_notes:
{<path>: <note>}` says something after a path. A tier's `docs.example` and `docs.helpers` are paths in an example
project too, so a test example lies where it would live (`tests/modules/documents/application/test_publish.py`). The
bundled profiles' examples are checked: every Python file below the folders imports only what its part may import, and
test code under `tests/` must parse.

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
  AGENTS.md: agents.md
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

- `fill`: whether `{{app}}` in the text is replaced. A file entry is filled by default; a folder entry is not
  (`fill: false`), since a preset is usually foreign content, copied byte for byte so fonts and images survive.
- `pinned` is for single files only: a project edits a preset it copied. The enforcement section's `init files`
  lists a single file that is missing (or pinned and changed), never the files of a folder entry.
- Inside the app, an entry may not replace what the skeleton writes (a package file, a folder or file of the layout).
  A target inside a part is fine and intended. Two entries may not land on the same file, an entry may not lie inside a
  folder entry, and a folder entry may not collide with a doc; all are reported with the other problems of the profile.
- Shipped code is checked code: a Python file that lands in a part is read by `check` like any other.

Both bundled profiles list three files: the guard test, `AGENTS.md` and `ruff.toml`. The last two are not pinned: a
project edits them.

`AGENTS.md` (at the project root, about 40 lines) is written for a coding agent that has never seen xarch: what governs
the project (the profile and `docs/project/`), to run `xarch where <path>` before creating or moving a file and to
take the first litmus test a piece of code passes, to run `xarch check` and `ruff check` before finishing, how tests are
written, and what not to do to get a green check: move code into a folder no part covers, switch a guard off or loosen
the profile, edit the guard test, skip a test. It is static text (it names the app folder with `{{app}}`).

`ruff.toml` holds only the linter rules that are the same for every file: pyflakes and pycodestyle errors, import
sorting, absolute imports only, a return annotation on public functions (which `stand-ins` needs on a port's methods),
the pytest-style rules, no `print`, no naive datetime and no unused `noqa`, for Python 3.13 and a line length of 140.
What differs by part (which imports, names or outside packages a part may use) is the profile's job, via
`may_import`, `libraries` and `forbidden`; `xarch check` does not run the linter.

The guard test, `tests/architecture/test_rules.py`, runs `python -m xarch check --app <project>/<app>` with the
interpreter running the test, and fails with `xarch check`'s output as its message, so every guard runs with the
project's test suite; xarch must be installed in that environment. It does not pass `--strict`; a project that wants
strictness runs `xarch check --strict` in CI or a pre-commit hook (editing the pinned guard test is itself reported as
changed). It is also the guard tier's example in `testing.md`.

## Development

```
uv run pytest tests
uv run ruff check                           # ruff.toml: the bundled linter config, plus what only this repository needs
uv tool install --editable . --reinstall     # refresh the system-wide `xarch`
```

`tests/architecture/test_self_check.py` runs xarch on its own source and tests, against `architecture.yaml` at the
repository root (named in `pyproject.toml`, which also records `app = "xarch"`, so a bare `xarch check` works here): the
`cli` parts and rules, the outside packages xarch really uses, and its tests as they are. `closed-tree` is on, the
example projects under `architectures/examples/` are `excluded`, and the same check in `--strict` mode passes. `tests/architecture/test_agnostic.py` fails if xarch's code names a part of a bundled profile or a name of
its test framework or the linter (xarch's code never runs it). The repository's own `ruff.toml` is the template the
bundled profiles write (`xarch/architectures/lint.toml`, named so that the linter does not read it as a config of
its own) plus an exclusion of the reference snippets under `xarch/architectures/examples/` and of `.claude/`; a test
keeps the two identical otherwise.
