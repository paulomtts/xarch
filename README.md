# xarch

Check and scaffold an architecture described in an architecture file (a profile): its layout, its parts, which part
may import which, its test tiers and the guards it switches on. Two profiles are bundled, `cli` and `web`; a project
may also bring its own file. xarch knows no part by name: every name comes from the profile.

## Install

xarch needs Python 3.13 or later. It is not on PyPI yet: install it from its repository.

```
uv tool install git+https://github.com/paulomtts/xarch               # the `xarch` command, on your PATH
uvx --from git+https://github.com/paulomtts/xarch xarch --version    # or run it once, without installing it
uv add --dev git+https://github.com/paulomtts/xarch                  # in a project: one of its dev dependencies
```

The guard test `init` writes runs `python -m xarch` with the interpreter that runs the project's tests, so xarch must
also be installed in the project's own environment: add it to the project's dev dependencies, as the last line does.

## Quickstart

```
xarch init --profile cli                              # the skeleton, docs and files; the profile goes in pyproject.toml
xarch new module documents                            # one module, with every folder a module holds
xarch where app/modules/documents/domain/values.py    # what code there may do, before it is written
xarch check                                           # every violation, each with its fix
```

## Commands

```
xarch --version                                              # print the installed version and exit
xarch init [--app PATH] [--profile NAME|FILE]                 # create the top-level skeleton, record the profile (and the
                                                             # app folder, if not app/) in pyproject.toml, write the
                                                             # project docs and files; never overwrites
xarch new WORD NAME [--app PATH] [--profile NAME|FILE]       # create one instance of a repeating folder, with its skeleton
xarch check [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict]
                                                             # report every violation in the app and its tests, each
                                                             # with its fix, then the state of the check's own enforcement
xarch where PATH [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # what a path is and what code there may do, before it is written
xarch profile migrate FILE [--out FOLDER] [--dry-run]        # convert a profile of format 1 to format 2, in a new folder
xarch profile explain [KEY] [--profile NAME|FILE | --configured] [--rule] [--app PATH] [--format text|json]
                                                             # the format of a profile, whole or one key; or a profile's
                                                             # folder tree and import table; with --rule, the rules a
                                                             # key expands to
xarch profile new NAME --from BUNDLED [--out FOLDER] [--app PATH]
                                                             # copy a bundled profile into the project, with its files
xarch profile check [NAME|FILE] [--app PATH] [--format text|json]
                                                             # validate a profile without an app
xarch review [PATH ...] [--files-from FILE|-] [--all] [--dry-run | --offline] [--cache DIR] [--max-files N] [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # advisory: a decision model's reading of where each file
                                                             # chosen belongs; sends the masked text when the key is set
```

`WORD` is the word between `<` and `>` in the profile's paths: in both bundled profiles `<module>`, so
`xarch new module documents` creates `modules/documents/` with every folder a module holds. The folder's own name
(`xarch new modules documents`) is refused, and the message says what to type. A profile may have several repeating
folders, each with a word of its own (`xarch new` takes any of them) under a parent of its own; a path holds one.

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

`init` writes the project's other files (`AGENTS.md`, `ruff.toml`, `docs/project/`, `tests/`) beside the app folder,
in the folder that holds it: for `--app src/shop`, in `src/`, wherever the `pyproject.toml` is. With no
`pyproject.toml` above `src/`, it creates `src/pyproject.toml` recording `app = "shop"`, relative to that file, and a
bare `xarch check` then works from `src/`; run from the folder above, it finds no profile. With a `pyproject.toml`
above `src/`, it records `app = "src/shop"` there, and `AGENTS.md`, `ruff.toml`, `docs/project/` and `tests/` still
land in `src/`.

```toml
[tool.xarch]
profile = "web"          # or a path, such as "architecture.yaml"
app = "src/shop"         # optional; the app folder, relative to this file; recorded by `init --app src/shop`
                         # when this file sits above src/
tests = "tests"          # optional; the default is tests/ beside the app folder, when it exists
```

## The profile file

A profile is one YAML file that states each fact once, on the thing it is about. Its parts are listed in the order their
litmus tests run, which is also the order of the generated docs' tree and rules table. The shape (`*` is required;
everything else is optional, and a key left out means off):

```
xarch: 2*  name*  based_on  language  hints  excluded  reserved
testing:  <preset> | {files*, functions*, skips, table, mocks}
parts*:   {<part>: {path*, role*, litmus, may_import, must_import, libraries, forbidden, tier | untested,
                    package_only, folders, holds, immutable, types_only, no_callbacks, names, built_by, shared}}
forbidden: {<list>: [<dotted name> | .<method>(), ...]}       layers: {<chain>: [<part>, ...]}
tiers:    {<tier>: {proves, litmus, apply_forbidden, plain_tables, types_only, folder, may_import, may_also_import,
                    must_import, docs}}
fakes:    {folder*, for*, prefix}
guards:   {scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins, dead-code,
           pass-through, private-imports}
files:    {<path>: <from> | {from*, pinned, fill}}      docs: {entry, pages, naming, examples, example_notes}
checks:   {<id>: {read*, in, keep, may_not | may_only | must_reach | must_be_reached*, except, mode, message*, fix*,
                  once_per, cases, examples*}}
review:   {never, mask}                                 what `xarch review` may send; `check` never reads it
```

`language` names the language of the app: `python`, which is the default and the only one xarch reads today. What is
true of a language as a whole lives in a data file shipped beside the profiles, `xarch/architectures/presets/language/
<name>.yaml`, the way `testing: pytest` resolves to `presets/testing/pytest.yaml`: the ending of a source file, the file
that stands for a folder, what marks an interface, the namespace of the builtins, the callables that import by a
computed name, the folder of compiled files, and where the standard library's names are known from (`interpreter`);
and the tokens of its code the checks and the docs need: what a name may be, how a private name starts, what a special
name starts and ends with, the special method calling an instance runs, the annotation of no value, the comment marker
and the comments its tools read, the shebang, the encoding declaration, the keywords of the statements that branch and
of the expressions that choose between values (`branching_expressions`), and what makes a class
an immutable record (`immutable`: a base, or a decorator called with its keywords, such as
`dataclasses.dataclass(frozen=True)`).
The rest of what a check knows of the language is one adapter, the reader that turns source into facts
(`modules/rules/adapters/fs_source_tree.py`), and the platform; spec reads the docs' examples through that reader too.
`tests/architecture/test_language_seam.py` fails when any other file of xarch names the language or writes one of
its tokens.

The data file also says what its reader supplies, under `supplies`: each fact of the source a check reads (`import`,
`class.fields`, `callback`, ...; `xarch/profile_values/capabilities.py` lists them), graded
`exact` or `{partial: <what it misses>}`. Every key that configures a check needs the facts that check reads, which
`xarch profile explain <key>` shows under `needs:` (a check of your own needs those of its kinds of fact and of the
fields its words read, as `xarch profile explain kinds.<kind>` shows). A profile that sets a key whose facts its language does not
supply is refused when it loads, naming the key, the fact and what to do; a key whose facts are supplied only partly
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly.

The smallest valid profile is a name and one part (it runs `structure`, the import rules, `libraries` and `syntax`):

```yaml
xarch: 2
name: documents-app
parts:
  documents:
    path: documents
    role: the documents
```

The symbols:

- `<unit>` in a `path`: a repeating folder, one instance per name (`xarch new` takes the word). A profile may have
  several, each with a word of its own and one parent; a path holds one, so one cannot sit inside another. A last step with a dot
  (`controller.py`) makes the part a file.
- In `may_import`, a bare name is that part in the importer's own instance of its repeating folder; `store@any` any
  instance, and the only way to name a part of another repeating folder, which has no own instance; `store/schema`
  only that path below the part; `store:*Id` only the names that match the pattern, imported by name;
  `everything` no limit (also for `libraries`). A part may always import itself.

This is the whole format on one screen. The reference for each key (what it means, what it accepts, whether `check`
enforces it and through which rule, an example that loads, the keys it holds) is the command, which reads the same
table the loader does, so it cannot drift from what is accepted:

```
xarch profile explain                      # the whole format, symbols and smallest profile
xarch profile explain parts.may_import     # one key; also: guards.no-duplicates, testing, tiers.folder, ...
xarch profile explain --profile web        # a profile's folder tree and import table, for a human to approve
xarch profile new mine --from web          # copy a bundled profile into architecture/mine/, with its files
xarch profile check [NAME|FILE]            # validate a profile without an app
```

`explain` takes `--format json` (`{"ok", "key", "where", "meaning", "accepts", "required", "enforced", "read_by",
"rules", "example", "choices", "keys", "needs", "language"}` for a key, `read_by` the command other than `check` that
alone reads it (`review` for `review` and its keys, else null; each `shape` entry has it too), `language` the language whose reader `needs` is graded
by; `{"ok", "key", "profile", "rules", "checks", "needs"}` for a key with
`--rule`, `needs` the facts its rules read; `{"ok", "format", "shape", "symbols", "smallest", "deeper"}` for the whole) and
exits 2 for a key the format does not have, naming the nearest (in JSON, `nearest` the format's keys and `words` the
words of a check). The key may be written with or without the placeholder
steps (`parts.may_import` or `parts.<part>.may_import`). `--profile NAME|FILE` (or `--configured`, the project's profile)
prints the folder tree with each folder's role and the table of what each part may import, as the generated docs show
them.

`new NAME --from BUNDLED` writes `architecture/NAME/NAME.yaml` (beside the app folder; `--out FOLDER` to choose) with
`name: NAME` and `based_on: BUNDLED`, plus every file the profile points to (templates, docs pages, init files, example
folders), so the copy loads on its own and passes `profile check` as it is. If any target file exists nothing is written
and the ones that exist are named. `pyproject.toml` is never edited: it prints the `profile = "..."` line to add under
`[tool.xarch]`, because that line changes what `check` enforces and `init` has usually set it already.

`check` loads the profile (every problem at once, which includes every file it points to existing), runs the
example-import check (the examples' imports obey the profile's own rules), holds each check the profile writes itself
to its examples, and shows how it differs from the bundled profile it is based on, as information (but for a part
left without the litmus the bundled profile gives it, which fails `check --strict`). With no argument it checks the
project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen; `--format
json` gives `{"ok", "profile", "problems": [{"check", "message"}], "files", "checks", "compared_with"}`, `files`
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load.

### Checks of your own

Every check xarch runs from a key (all but `cycles`, `structure`, `test-tree`, `stand-ins`, `scenario-coverage`,
`no-duplicates`, `no-twins` and `shared`) is a rule written in a small vocabulary, and a profile may write rules of its own in the
same words under `checks`: each reads the facts of a kind (`read`) in some files (`in`), keeps those its filters pass
(`keep`), and says that a kept fact may not match its targets (`may_not`), may only match them (`may_only`), or that a
file must reach a target (`must_reach`) or a fact be reached from some files (`must_be_reached`); an exception
(`except`) excuses a finding, and `message` and `fix` say it, with `{variable}`s. A check carries `examples`: code it
must find something in and code it must find nothing in, which `xarch profile check` runs.

```yaml
checks:
  no-todo:
    read: comment
    in: {where: [placed]}
    may_not: {text: ["*TODO*"]}
    message: "{file} leaves a note for later at line {line}: {text}"
    fix: "do it now, or write it where the team tracks its work"
    examples:
      flagged: {documents/notes.py: "# TODO: split this file\n"}
      clean: {documents/notes.py: "# split by kind\n"}
```

Its findings carry its id as their `rule`; `hints` may name it. The enforcement section lists each check of your own
with how many facts it read, and one that read nothing (`reads nothing`), which passes for want of anything to check,
fails `--strict`. A check whose words do not exist or do not apply where they are written (a filter it keeps, or that
its links pass, must apply to every kind they read, or it would drop that kind whole), or that needs a fact the
language's reader does not supply, is refused with every problem at once, each at its address (`checks.<id>.keep`).
The whole vocabulary, from the same table the engine reads, is the command:

```
xarch profile explain checks               # how a check is written and read, with a whole one as an example
xarch profile explain filters              # a category of words: kinds, quantifiers, targets, filters, variables
xarch profile explain filters.public       # one word: what it means, what it applies to, an example
xarch profile explain parts.names --rule   # the rules a key of your profile expands to, written as checks
```

### Migrating a profile of format 1

A file that starts `xarch: 1` is refused by every command, which names `xarch profile migrate FILE`. That command
writes the format 2 profile and the files it names into a new folder (`FILE`'s name with `-v2`, or `--out FOLDER`),
never over a file that exists and never changing the old ones; example files go to the paths they illustrate, and
`{{example:<name>}}` in the templates becomes `{{example:<path>}}`. It validates the result before writing (`--dry-run`
stops there), lists under `changed:` what now means something else and under `by hand:` what has no form in format 2.
YAML comments are not carried over.

## What check checks

`check` reads only the files the profile governs: a file in a part, or a package file of a folder of the layout. A file
anywhere else is never read and is listed as `ungoverned` in the enforcement section; extra top-level folders and files
at the app root are ignored unless the profile switches on `closed-tree`. A folder that is not the app's source at all
is declared under `excluded`, and then no check looks at it. Extra files and subfolders inside a known part belong to
that part.

Every violation names its rule id, says what was found and, on a `fix:` line, what to do. The ids, with the profile key
that switches or configures each (`-` for none: the rule is always on):

| Rule id | What it catches | Key |
|---|---|---|
| `syntax` | a file that does not parse, or that cannot be read as UTF-8 text at all (the message says which), so no other check could read it | - |
| `structure` | a folder or file of the layout missing, at any depth, in the app and in every instance of each repeating folder | `parts.path`, `parts.folders` |
| `rules` | an import between parts that the importing part's `may_import` does not allow, or a name its pattern does not match | `parts.may_import` |
| `libraries` | an outside package a part does not list, or a standard-library name `reserved` holds that it does not list; the rest of the standard library is always allowed, tests are not checked | `parts.libraries`, `reserved` |
| `forbidden` | a name or module a part (or, with `apply_forbidden`, its tests) may not use, or a method written `.name()` it may not call on anything but its own object and what that holds | `forbidden`, `parts.forbidden`, `tiers.apply_forbidden` |
| `tiers` | a test importing what its tier does not allow, or another test file, or a test in no tier | `tiers`, `tiers.folder`, `tiers.may_import`, `tiers.may_also_import`, `parts.tier` |
| `test-tree` | a folder below `tests/<repeating folder>/` that mirrors no folder of the app | `tiers`, `testing` |
| `types-only` | a test, or code of a part, calling what it may import only as a type | `tiers.types_only`, `parts.types_only` |
| `cycles` | instances of the repeating folders that import each other, directly or through others (across repeating folders too); each elementary cycle is reported once, at its first import | - (needs a repeating folder) |
| `package-only` | an import of a file of a part from outside it, where the part is imported as a package | `parts.package_only` |
| `must-import` | a file of a part that never reaches any of the targets the part must reach, nor an outside package, or a test that never reaches what its tier must | `parts.must_import`, `tiers.must_import` |
| `scenario-coverage` | a variant of a result union with no row in its use case's test table, or a branch (a statement of `branching`, an expression of `branching_expressions`) in a table test's body; with `plain_tables`, in any table test of that tier | `guards.scenario-coverage`, `tiers.plain_tables` |
| `no-comments` | a `#` comment in the app or its tests | `guards.no-comments` |
| `stand-ins` | a read port without a fake, or a mock without a spec or with a read port's | `guards.stand-ins`, `fakes` |
| `closed-tree` | a Python file of the app that lies in no part | `guards.closed-tree` |
| `no-duplicates` | two functions or methods of the app with the same code | `guards.no-duplicates` |
| `no-twins` | two public classes in parts of different names that declare the same fields in the same order: one type written twice; with `min_renamed`, also a copy that renamed a field, and with `min_subset`, one that kept at least half of the other's fields in its order; with `translated`, a pair is no twin when a file of a listed part builds one of the two through an import, imports the other (from the file defining it, or from one that takes it from there), and holds one function that names both; a class a file builds where it defines it is built through no import, and translates nothing; each pair so accepted is named in the enforcement section | `guards.no-twins` |
| `dead-code` | a port no other file names, a fake no test uses; with `untested`, a file no test of its tier reaches, and with `tests_only`, a public class or top-level function no other file of the app names (only the tests, or nothing, use it), but those `known` accepts, which the enforcement section names instead, each listed as `weak` only; an entry of `known` whose file defines no such name, whose name another file of the app names, or that no test names in its code (a string of a test does not count), is listed as `weak` too | `guards.dead-code`, `fakes` |
| `pass-through` | a method that only forwards its arguments to a collaborator, or returns an attribute of what that call answers; never a violation: listed as `weak`, and fails only `--strict` | `guards.pass-through` |
| `holds` | a public function at the top level of a part that holds classes, or a class (whatever its name) in one that holds functions; listed as `weak`, and fails only `--strict` | `parts.holds` |
| `immutable` | a class of a part that lists `immutable` that is no immutable record as the language's data file says one is made, an exception aside; listed as `weak`, and fails only `--strict` | `parts.immutable` |
| `no-callbacks` | a function of a part that calls one of its own parameters annotated as a callable | `parts.no_callbacks` |
| `names` | a public class of a part whose name matches none of the part's patterns | `parts.names` |
| `built-by` | a call of the constructor of a part's class from a part it does not list | `parts.built_by` |
| `private-imports` | an import of a name starting with `_` from another file of the app or its tests | `guards.private-imports` |
| `shared` | a public name of a part declared shared that fewer users use than it says (a user: an instance of a repeating folder, or a part outside them; tests not read) | `parts.shared` |

A key left out means its check is off. For what a key means, accepts and exactly checks, run
`xarch profile explain <key>` (for example `xarch profile explain guards.no-duplicates`, `parts.must_import`,
`forbidden` or `tiers`); it reads the table the loader reads, so it cannot drift. A violation's `fix:` says what to do
about that finding, and a profile's `hints` add its own advice after it.

## The output of check

### Text

Every violation says what to do about it. A finding is its line, `<file>[:<line>]: <message>`, then an indented line
`fix: <what to do>`, one imperative sentence specific to the finding, and, when the profile has a
hint (`xarch profile explain hints`) for its rule, an indented `hint: <text>` line. The findings come in order of
file, then line (a whole file first), then rule, then a summary, `OK: no violations` or `<n> violation(s) in <m>
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
    "known": [],
    "translated": [],
    "init_files": [],
    "skipped": {"count": 0, "at": []},
    "dynamic": {"count": 0, "at": []},
    "weak": [],
    "approximate": [],
    "strict_failures": []
  }
}
```

A profile that writes checks of its own also has `"checks"` in `enforcement`: each `{"id", "read", "said"}`, `read`
how many facts it read in the project.

- `ok`: no violation, and with `--strict` no enforcement finding either; it agrees with the exit code. `strict`:
  whether `--strict` was given. `profile`: the profile in force, a bundled name or a path, as selected.
- `violations`: sorted by `file`, then `line` (a whole-file or folder violation, `line: null`, first), then `rule`.
  `file` is the path the text output prints; `message` the sentence it prints after the path; `fix` what to do about
  it, always a non-empty string (a violation cannot be made without one); `hint` the profile's own advice for the
  rule, else `null`. `rule` is one of: `rules`, `libraries`, `forbidden`, `tiers` (a test's imports, or a test in no
  tier), `types-only`, `cycles`, `package-only`, `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`,
  `must-import`, `no-duplicates`, `no-twins`, `dead-code`, `pass-through`, `holds`, `immutable` (these three never a
  violation, only a weak item), `no-callbacks`, `names`, `built-by`, `private-imports`, `shared`, `structure`,
  `test-tree`, and `syntax` (a file that does not parse, or cannot be read as UTF-8 text), or the id of a check the
  profile writes itself.
- `enforcement`: every key always present, empty when there is nothing to report. `profile.looser` items are
  `{"key", "part", "what", "sentence"}` with `key` one of `may_import`, `libraries`, `forbidden`, `untested`,
  `types_only`, `may_also_import`, `apply_forbidden`, `testing.skips`, `files.pinned`, `reserved`, `must_import`, `litmus`, `known`,
  `translated` (the `sentence` names the full address, such as `parts.kernel.may_import`); `excluded` items
  `{"folder", "reason"}`; `known` items `{"file", "line", "name"}`, each public name `guards.dead-code.known` accepts
  as only the tests'; `translated` items `{"file", "line", "function", "built", "other"}`, each pair of classes
  `no-twins` accepts as a translation (`guards.no-twins.translated`): the function that names both, where it is, the
  class its file builds and the other; `init_files` items `{"file", "state"}`, `state` `missing` or
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `weak` items `{"rule", "file", "line",
  "message", "fix"}` (`fix` is `null` for a weak check that has none); `approximate` items `{"key", "fact", "note"}`;
  `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `ungoverned`, `init_files`,
  `skipped`, `dynamic`, `weak`, `approximate`, `vacuous` (a check of the profile's own that read nothing), `litmus` (a
  part redefined without the litmus its compared profile gives it). `strict_failures` is filled whether or not `--strict` was given: it
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
  known:       app/bootstrap/wiring.py:12: build_app is public, a test names it and no other file of the app does, which the profile accepts (guards.dead-code.known)
  init files:  tests/architecture/test_rules.py is changed
  skipped:     1 skip (tests/modules/docs/domain/test_x.py:4)
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
  weak:        app/modules/docs/application/services/doc.py:9: DocService.get only passes its arguments on to self.repo.get
      fix: have the caller use self.repo.get, or keep it as a deliberate plain forward: it stays listed and fails only `check --strict`
```

- `profile`: the bundled name, or the custom file's path and the bundled profile it is based on or, failing that,
  most resembles (the first by name on a tie); one sharing no part resembles none, and nothing is compared. `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
  too; one of them, `package-only`, is switched on by a part's `package_only: true` rather than under `guards`, and the
  line names that key. For a custom file, each way it is looser than the one it resembles, compared only where both use the same
  name: a target added to a part's `may_import`, an outside package added to its `libraries` (or `everything`), a
  name of its `forbidden` list no entry covers any more, a part newly `untested`, a part dropped from a tier's
  `types_only`, a target added to a tier's `may_also_import`, a tier no longer `apply_forbidden`, a name dropped from `testing.skips`, a `files` entry no longer
  `pinned`, a target added to a part's `must_import` or the key dropped, a part redefined without the `litmus` the
  other gives it, a public name `guards.dead-code.known` accepts that the other's does not, a part
  `guards.no-twins.translated` lists that the other's does not. A profile that says `based_on: <bundled name>` is compared with that one, else with the one sharing the
  most part names.
  Stricter differences, new parts, the layout and the guards' other parameters are not compared. This comparison is
  information: the profile defines the architecture, so how it differs from another is no finding for `--strict`, but
  for a litmus dropped, which leaves a part's code no question to be placed by.
- `ungoverned`: the app's Python files in no part and no folder of the layout (what `closed-tree` would report),
  which no check reads, counted with their top folders.
- `excluded`: each folder the profile's `excluded` key leaves out, with its reason; no check reads a file below it,
  so the exclusion stays visible here.
- `translated`: each pair of classes `no-twins` accepts as a translation (`guards.no-twins.translated`), naming the
  function that translates and where it is: the check does not report the pair, so the acceptance stays visible here.
- `known`: each public name `guards.dead-code.known` accepts as only the tests', where it is defined: a test names
  it and no other file of the app does, the `tests_only` check lists it no more, so the acceptance stays visible
  here. An entry that no longer holds (its file defines no such name, another file of the app names it, or no test
  names it in its code) is listed as `weak` instead.
- `init files`: each single file of the profile's `files` that is missing beside the app folder, or, when the entry
  says `pinned: true`, that differs from what `init` would write now. The files of a folder entry (a preset) are
  copied once and not watched.
- `skipped`: each use in the tests of a name of `testing.skips`, or one below it, read through imports.
- `dynamic`: each use, in the files read, of a callable the language's data file lists as importing by a computed name
  (for Python, `importlib.import_module`, `importlib.__import__` and the builtin `__import__`), so it needs no entry in
  the profile; the import rules cannot see what it imports.
- `weak`, met to the letter only, never a violation: a fake `<prefix><Port>` that defines in its own body (methods,
  or names its body or `self.` assigns) less than every port of its name declares; and a `Result` variant that no
  row covers, credited only to standalone tests that name it and hold no `assert`; and a method `pass-through` finds.
  A weak check that has a fix shows it on an indented `fix:` line under its own.
- `approximate`: each key the profile sets whose check reads a fact the language's reader supplies only partly, as
  its data file grades it (`supplies`), with what the reader misses: the check runs, and may miss what it looks for.
  A key whose check reads a fact the language does not supply at all is refused when the profile loads, naming the
  key and the fact. Python's reader supplies every fact exactly, so a Python project never sees this line.

Without `--strict` the section never changes the exit code. `--strict` fails (exit 1) on every finding listed in
`strict_failures`: what the profile in force leaves unenforced or unseen: each guard left off that the bundled profile
in force, or the one a custom profile is compared with, does not also leave off (with no profile to compare with,
every guard left off); each ungoverned file; each missing or changed init file; each skip; each dynamic import; each weak finding;
each approximate key; each part redefined without its litmus. The text
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

For a path in the app: its part and the instance of its repeating folder, the part's role and litmus test, what it may
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
- `part`: for `part`, the part the path lies in; for a `test`, the part it mirrors; else null. `instance` is empty when the part is not in a
  repeating folder; `singular` is the word of the folder the part lies in (for a part outside them, the profile's word
  when it has only one).
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

## xarch review: an advisory reading

`review` is a second, advisory command, apart from `check`: it never runs inside `check`, never changes what `check`
finds or its exit code, and never exits 1. For each file chosen it asks a decision model which part of the profile the
file belongs in, with every part's litmus test (its role, for a part with none) as the options, and prints the
model's reading, ranked: a file whose probability on the part it sits in is below that part's line (0.3 for every part
today) reads as **doubtful here**. That is a reason to read the file against its part's litmus, not a finding: in
trials, about 7 to 10% of well-placed files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files was really
misplaced. The text output names no other part; the JSON gives the probability on every part.

**What leaves the machine, and when.** The decision model is TypeSafe's (`https://api.typesafe.ai`), asked as the
model `jev-1.14.0`, pinned. Review sends whenever `TYPESAFE_API_KEY` is set in the environment: **the key alone allows
it**, so a key set for another purpose (a shell profile, a CI secret) starts sending the first time `xarch review` runs
without `--dry-run` or `--offline`. With no key set, a review that would send refuses (exit 2): "no key: set
TYPESAFE_API_KEY, or run --dry-run to see what would be sent, or --offline to use cached answers only". What is sent
is, for each file judged whose answer is not cached, its masked text (below) and the question; the key travels as the
`Authorization` header only, with `User-Agent: xarch`. The key is never printed, logged, cached or written. Nothing
else of the project is sent: no path, no file name, no project name, no git data, no telemetry.

It reads only the files it is given, and refuses (exit 2) when none is: name them as paths (a folder stands for the
source files below it), pipe a list with `--files-from -` (one path per line, such as
`git diff --name-only main | xarch review --files-from -`), or take every file of the app with `--all`
(alone). A path is read as `xarch where` reads one; one outside the project is refused. Of the files found, a source
file of the app in a part, that parses and holds at least 800 characters, is judged; every other is listed as left out,
with why (not there, no source file, a test, outside the app folder, excluded, in no part, held back by
`review.never`, does not parse, too small). A run judges at most `--max-files` files (50); past that it refuses,
naming how many it chose.

The text a file is judged by is its own, masked: the module each import of the app's own code names (an import named
from the importing file's folder, or whose first step is the app's import name) is replaced by `<masked>` on the
import's line, since it would say the part; every e-mail address becomes `person@example.test`; then each text the
profile's `review.mask` hides (below). Nothing else is masked: docstrings, comments and string literals are sent as
written, so a file that must not leave the machine is one not to choose, or one for `review.never`.

`--dry-run` sends nothing and needs no key. It opens with what leaves the machine, to whom, and whether the key is set
now, then prints the question once (it is the same for every file), the masks in force, and each file judged with the
exact text it would send, marked when its answer is in the cache already (it would not be sent). It ends with the
characters in all and about how many tokens they make (one for every four characters).

Answers are kept in `.xarch/cache/review/` in the project's root (the folder holding the app folder), one JSON file
per question, named by a hash of the model asked, the masked text and the question; each holds the model version
that answered, the probability of each part and the tokens spent, and no code, no question and no key. Commit the
folder: agents and CI then share the answers without spending calls, and a model upgrade shows as a diff of answers.
An identical question is never sent twice. `--cache DIR` keeps them elsewhere. `--offline` sends nothing, needs no
key, and reads the cache only.

Exit codes: 0 when the review ran to the end, whatever it read (doubtful files are not failures); 2 when it refused
before sending anything (no selection, `--all` with paths, over `--max-files`, no key, a path outside the project, a
profile that cannot be used); 3 when some file judged has no answer: not cached under `--offline`, or the decision
model failed (unreachable, rate-limited after retries, a request refused), after which nothing more is sent. What was
answered is printed, the rest is listed as unanswered with why and the decision model's words, and the answers already
kept stay kept.

### What review may send: `review.never` and `review.mask`

The profile may narrow what review sends, under a top-level `review` key that `check` never reads (it changes no
finding and no exit code of `check`). Neither key can switch sending on.

```yaml
review:
  never: [modules/documents/adapters/legal_archive.py, "**/secrets"]
  mask: [Northwind, "DOC-*"]
```

- `never`: paths below the app of the files review never sends, each with its steps written with `/`: a step as
  written, `*` for any text inside one step, and a step that is `**` for any number of folders (none included). A path
  matches a file, or a folder and every file below it. A file chosen that one matches is left out of every run,
  `--dry-run` included, as "held back by review.never (<path>)"; its text goes into no request.
- `mask`: texts hidden in each file's text before it is sent, after the built-in masks: each as written (case counts),
  `*` standing for a run of one or more letters, digits, `_`, `-` and `.`; each match is sent as `<masked>`.
  `--dry-run` shows the texts masked and lists the patterns in force.

`profile check` lists, as looser, an entry of either that the profile it is compared with holds and this one does not:
it sends more. `xarch profile explain review.never` (or `review.mask`) says each in full.

### JSON

`--format json` prints one document. A dry run: `{"ok", "advisory", "profile", "dry_run": true, "sent": false,
"selection": {"by", "found", "judged", "left_out": [{"file", "why", "chars", "pattern"}]}, "question": {"ask",
"role_only", "options": [{"name", "description"}]}, "requests": [{"file", "part", "chars", "cached", "text", "body"}],
"characters", "tokens", "mask", "sends": {"name", "at", "model", "key", "keyed"}}`, `body` the request as the
decision model's service would receive it (JSON text, the key left out), `sends.key` the name of the variable the key
is read from (never the key) and `keyed` whether it is set. A review: `{"ok", "advisory", "profile", "dry_run": false,
"complete", "model", "selection", "placement": {"calibration": {"state", "evidence"}, "role_only", "files": [{"file",
"part", "probability", "line", "doubtful", "chars", "model", "distribution"}]}, "sends", "sent": {"calls", "cached",
"input_tokens", "output_tokens"}, "unanswered": [{"file", "why"}], "failure"}`, the files ranked from the lowest
probability, `distribution` the probability on each part by name, `why` of an unanswered file `not-cached` or
`failed`, `failure` the decision model's words when it failed (else null). In both, `why` of a file left out is one of
`missing`, `not-source`, `test`, `outside`, `excluded`, `unplaced`, `never`, `unparsable`, `small`, `pattern` the
`review.never` path that matched (null for any other `why`); a dry run's `mask` is the profile's `review.mask`. A
refusal is `{"ok": false, "error"}`.

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
  tests/architecture/test_rules.py: {from: examples/shared/tests/architecture/test_rules.py, pinned: true}
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

`AGENTS.md` (beside the app folder, about 45 lines) is written for a coding agent that has never seen xarch: what governs
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
