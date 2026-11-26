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
xarch check [PATH ...] [--files-from FILE|-] [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json] [--strict] [--against NAME|FILE]
                                                             # report every violation in the app and its tests, each
                                                             # with its fix, then the state of the check's own enforcement;
                                                             # with paths, only those of the files at or below them
xarch baseline write [--reset] [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # record the violations found now, which check then holds
                                                             # back; the record may only go down
xarch hook claude [--command TEXT]                           # print Claude Code hooks that run the check after each edit
                                                             # and before the agent stops; writes nothing
xarch where PATH [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # what a path is and what code there may do, before it is written
xarch profile explain [KEY] [--profile NAME|FILE | --configured] [--rule] [--app PATH] [--format text|json]
                                                             # the format of a profile, whole or one key; or a profile's
                                                             # folder tree and import table; with --rule, the rules a
                                                             # key expands to
xarch profile new NAME --from BUNDLED [--out FOLDER] [--app PATH]
                                                             # copy a bundled profile into the project, with its files
xarch profile check [NAME|FILE] [--against NAME|FILE] [--app PATH] [--format text|json]
                                                             # validate a profile without an app
xarch review [PATH ... | calibrate [--eval ID ...] | accept PATH ... (--why TEXT | --remove)] [--files-from FILE|-] [--all] [--pieces] [--context none|imports] [--dry-run | --offline] [--cache DIR] [--max-files N] [--app PATH] [--profile NAME|FILE] [--tests PATH] [--format text|json]
                                                             # experimental, advisory: a decision model's reading of where each file
                                                             # chosen belongs, with --pieces a ranking of its pieces,
                                                             # and the profile's own evals that are calibrated; sends
                                                             # the masked text when the key is set. `review calibrate`
                                                             # holds the profile's own evals to their examples and
                                                             # records the verdicts in .xarch/calibration.json;
                                                             # `review accept` records doubtful files read and found
                                                             # fine in .xarch/accepted.json
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

A profile is one YAML file that states each fact once, on the thing it is about. Its `parts` are the app's folder tree,
and the tree's reading order (top to bottom, a part before the parts inside it) is the order their litmus tests run,
which is also the order of the generated docs' rules table. The shape (`*` is required; everything else is optional,
and a key left out means off):

```
name*  based_on  language  hints  excluded  reserved
testing:  <preset> | {preset, beside, shared} | {files*, declared*, globals, skips, tables, mocks, beside, shared}
parts*:   {<folder>/ | <file>: {<folder>/ | <file>, name, role*, litmus, imports: {may, must, libraries, accepted}, uses: {never},
                              tests | untested, package_only, shared, optional,
                              holds: {classes: {names, immutable, built_by}, functions: {names},
                                      records: {names, immutable}, exceptions: {names}}}}
never:    {<list>: [<dotted name> | .<method>() | <list>, ...]}  layers: {<chain>: [<part>, ...] | {parts*, types_only}}
tiers:    {<tier>: {proves, litmus, uses: {apply_never}, plain_tables, folder, imports: {may, also, must, types_only},
                    accepted: [{file*, import, why*}, ...], docs}}
fakes:    {folder*, for*, prefix | [prefix, ...], tiers}     structure: {accepted: [{path*, why*}, ...]}
guards:   {scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins, dead-code,
           pass-through, no-callbacks, private-imports}
files:    {<path>: <from> | {from*, pinned, fill}}      docs: {entry, pages, naming, examples, example_notes}
checks:   {<id>: {read*, in, keep, may_not | may_only | must_reach | must_not_reach | must_be_reached | at_most |
                  at_least*, except, accepted, mode, message*, fix*, once_per, per_line, cases, examples*}}
review:   {never, mask}                                 what `xarch review` may send; `check` never acts on it
evals:    {placement: {lines, alike, examples}, <id>: {ask*, answer*, yes, no, reads*, in, keep, line, message*,
          fix*, examples*}}                             what `xarch review` asks; `check` never acts on it
```

A tier's `accepted` lists `tiers` findings it accepts one by one, each with a reason: `file` a test of the tier, or
one in no tier (`tests/<path>`), and, if need be, `import`, what it imports, written as `imports.accepted` writes it (a
file or folder below the app, or `tests/<path>` for test code, optionally `:<name>`). With `import`, the findings of
that import in that file are accepted; without it, every `tiers` finding of the file, that it lies in no tier
included, the grain of a backlog of tests not yet in their tier. Such a finding is not reported and the enforcement
section names it under `accepted:`; an entry that accepts nothing is itself a `tiers` finding, so the list can only
shrink.

```yaml
tiers:
  unit:
    accepted:
      - {file: tests/modules/billing/test_rates.py, import: adapters/sql/rates.py, why: "rates read the table until the port lands"}
      - {file: tests/frontend/test_old_page.py, why: "the old page is retired with the old UI"}
```

`structure.accepted` lists findings of the layout the profile accepts one by one, each with a reason: `path` the
folder or file a `structure` finding says is missing, by its path below the app (`modules/billing/domain/errors.py`),
or `tests/<path>`, a folder below the tests that a `test-tree` finding says mirrors nothing (`tests/modules/legacy/`);
a trailing `/` is optional. Such a finding is not reported and the enforcement section names it under `accepted:`;
an entry that accepts nothing (the path is there, or mirrors a folder of the app now) is itself a finding of its
rule, so the list can only shrink. Unlike `parts.<part>.optional`, which frees a part in every instance, an entry
frees one path.

`counterparts` says what lies with what, path by path: each entry, by an id of its own, has `for`, what must have a
counterpart, `has`, where it is, and optionally `when`, the paths that must be there too for it to need one, each a
path below the app or `tests/<path>` below the tests, a folder when it ends in `/` (a folder is there when a file lies
below it). `<word>` binds the text of a step, or part of one (`<port>_repo.py`), to a name that is no private one, and
stands for that text in `has` and `when`; the word of a repeating folder at that folder's place binds only its
instances, never a folder the layout names beside them (`sql/models/` beside `sql/<store>/`); `*` is any text within a
step, and several matches of `has` satisfy it. Each match of `for` with no counterpart is a `counterpart` finding at it,
with `message` and `fix` of the profile's own if it writes them (`{source}`, `{expected}`, `{when}`, `{key}` and each
placeholder). `accepted` lists the matches that need none, each with a reason, as `structure.accepted` writes them; an
entry that no longer accepts anything (its source gone, or now with its counterpart) is itself a finding. A counterpart
whose `for` matches nothing is listed as `reads nothing` in the enforcement section and fails `--strict`. A placeholder
of `has` or `when` that `for` does not bind, or two placeholders side by side in a step, are refused when the profile
loads.

```yaml
counterparts:
  sql-fakes-have-conformance:
    for: adapters/persistence/sql/<store>/
    when: [tests/fakes/<store>/]
    has: tests/conformance/<store>/
  transaction-has-contract:
    for: adapters/persistence/sql/<store>/transaction.py
    has: tests/conformance/<store>/test_*_transaction_contract.py
    accepted:
      - {path: adapters/persistence/sql/filesystem/transaction.py, why: "no memory-vs-sql contract yet"}
```

A key on a part is about its own code and reach; a guard is a pre-built check with a scope, which names the parts it
reads.

A chain of `layers` lists parts from the inside out, and a profile whose `imports.may` lets a part import one after it
is refused when it loads. Layering is strict: an entry marked `types_only` breaks the chain too, unless the chain is
written as a map that says so, `layers: {inward: {parts: [domain, services, controller], types_only: true}}`, where a
part may name one after it as a type only (`types-only` still holds it to that), and any other entry still breaks it.

An entry of a `never` list that is the name of another list includes that list's names in its place, such as
`published: [pure, typing.Any]`; a list may not take the name of a package of the standard library or of a package the
profile names, since an entry of that name would name the list.

What `uses.never` follows is the name as the file binds it, never the value at run time. A use is found when the
name is read: imported however it is written (`import datetime`, `import datetime as dt`, `from datetime import
datetime as D`, a builtin by its bare name such as `open`), and through a plain rebinding in the same file, `x = y`, one
bare name assigned to another at module or function level and nothing else binding `x` in that scope (`clock = D`,
then `clock.now()`; a chain of such rebindings too). Nothing cleverer is followed: not an attribute or an expression
assigned (`now = D.now`, `x = D if a else E`), an unpacking, an annotated assignment, a default of a parameter, a name
passed to a function or returned from one, an attribute stored on an object, or a name bound in another file. A name
worked out when the code runs cannot be followed at all: a call of what imports by a computed name
(`importlib.import_module`, `__import__`) and a `getattr` of a name an import binds (`getattr(t, "time")` after
`import time as t`) are listed under `dynamic` in the enforcement section instead, which `--strict` fails on. So a
green `check` says no file names a forbidden name in a way it follows, not that the code never reaches one.

`language` names the language of the app: `python`, which is the default and the only one xarch reads today. What is
true of a language as a whole lives in a data file shipped beside the profiles, `xarch/architectures/presets/language/
<name>.yaml`, the way `testing: pytest` resolves to `presets/testing/pytest.yaml`: the endings of a source file
(`extensions`, a list; the first is the one messages print), the files that stand for a folder (`package_files`, a
list, optional for a language where no file does), what marks an interface (`interface`, a list of marks, each a base,
`{base: typing.Protocol}`, or a keyword a declaration carries, `{keyword: interface}`), the namespace of the builtins,
the callables that import by a computed name (`dynamic`), those that read a member of an object by one
(`dynamic_attributes`, Python's `getattr`), the folder of compiled files, and where the standard library's top-level modules, the reserved words
and the builtins are known from (`standard`: `interpreter`, the Python running xarch, or three lists, `modules`,
`reserved` and `builtins`, each item checked with the file's `package` or `name`);
and the tokens of its code the checks and the docs need: what a name may be, what an import names from outside the app
as one step (`package`) and the text that joins a package to a name in it in the profile's lists (`member`, `.` for
Python), so that an outside name is written `<package><member><name>`, how a private name starts (`private`, by which
the Python reader decides whether a name is public, the fact `public` a reader supplies, and by which scaffold and
layout refuse and skip a private name), the pattern of a special name (`special`, a regular expression the whole name
matches), the special method calling an instance runs, the annotations of no value (`nothing`, a list: `[None]` for
Python) and, optionally, that a method with no return annotation gives none (`unannotated: nothing`), the forms a
comment is written in (`comments`, a list of `line`, `block` and `doc` forms, `[{line: "#"}]` for Python, a doc
comment being one `no-comments` keeps) and the comments its tools read after the marker of any form, the shebang, the
encoding declaration, the keywords of the statements that branch and of the expressions that choose between values
(`branching_expressions`), and what makes a class an immutable record (`immutable`: marks, each `{base}`,
`{decorator, keywords}`, `{fields}` or `{type}`, such as `{decorator: dataclasses.dataclass, keywords: {frozen:
"True"}}`), and how the code of the checks `profile explain` shows as examples is written (`worked`: one-line
templates, `subclass` a class deriving from a base, `class {name}({base}): ...` for Python; a token whose template
the file leaves out stays as written). Whether a class is a record, a type that only holds data, the reader says: the fact `class.record` a
reader supplies, which `holds`, its kind `records` and the filter `record` read. Whether a function is defined at the
top level of its file, in no class, is the fact `function.top_level` a reader supplies, which the kinds `functions` and
`records` of `holds`, `guards.dead-code.tests_only` and the filter `top-level` read; `holds` itself reads it only when
the language supplies it, so that in a language without it a part that does not list `functions` reads no functions,
which `profile explain parts.holds` and the enforcement section say.
The rest of what a check knows of the language is one adapter, the reader that turns source into facts
(`modules/rules/adapters/fs_source_tree.py`), and the platform; spec reads the docs' examples through that reader too.
`tests/architecture/test_language_seam.py` fails when any other file of xarch names the language or writes one of
its tokens.

The data file also says what its reader supplies, under `supplies`: each fact of the source a check reads (`import`,
`class.fields`, `callback`, ...; `xarch/profile_values/capabilities.py` lists them), graded
`exact` or `{partial: <what it misses>}`. Every key that configures a check needs the facts that check reads, which
`xarch profile explain <key>` shows under `needs:` (a check of your own needs those of its kinds of fact and of the
fields its words read, as `xarch profile explain kinds.<kind>` shows). A key is held to its facts wherever it sits: in
a scope any key opens, however deep, and in each entry of a list, which a problem names by its index from 0
(`<list>.0.<key>`). A profile that sets a key whose facts its language does not
supply is refused when it loads, naming the key, the fact and what to do; a key whose facts are supplied only partly
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call`, `test.call` and `call.type_arguments`, so a framework that
writes a `call` form under Python is refused at that entry (`testing.tables.0.call`, `testing.declared.0.call`), and so
is a mock spec by a type argument (`testing.mocks.specs.0.type_argument`). A framework declares its tests
with `testing.declared`, a list of forms: a `function` form, a function whose name matches a pattern, or a `call` form,
a call whose arguments hold the test's `title` and its `body`; `testing.globals` names what it binds without an import.
A table `call` form's callees must each be listed under a `call` form of `testing.declared`, the call that declares
the test it makes or wraps; one that is not is refused at its entry (`` testing.tables.0.call: `it.each` declares no
test: list it under a `call` form of `testing.declared` ``).
`testing.mocks.specs` lists, in order, the ways a call that builds a mock names its spec, each `{keyword: <name>}`,
`{position: <n>}` or `{type_argument: <n>}`: a call names it by the first entry it gives, the fix of a mock with no
spec writes the first entry by the language's `writing.specs`, and an autospec call reads only the first `keyword`
entry. It replaces `spec_keywords` and `spec_position`, each refused with what to write (`unknown key 'spec_keywords':
moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]`). A `type_argument` entry needs `call.type_arguments`,
which Python's reader does not supply.
`testing: {preset: pytest}` names a preset as a map, and every framework key then comes from it: one written beside
it is refused (`testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`), never
merged, and a project with its own `files` writes the whole map instead; `testing: pytest` is its short form.
`testing: {preset: pytest, beside: true}` keeps every test of a part beside its code: a file of the app whose name
`files` matches is a test of the tier its part names, never code of its part; a tier with a `folder` keeps its tests
below the tests root, and a part may not name such a tier; `test-tree` then reports a test left below the tests root
outside every tier `folder` and the fakes' folder.
`testing: {preset: pytest, shared: [support, helpers.py]}` names test code that a test of any tier may import besides
its own folder's: folders and files below the tests root (default none), each outside every tier `folder` and the
fakes' folder (an entry inside or holding one is refused). A test file there is still a test file, which no test
imports, and the fakes keep their own rule; the `tiers` message of an import from elsewhere names the shared entries,
and `xarch where` lists them for a test.
A fake of the port `X` is named `<prefix>X` (`fakes.prefix`), or, with a list of starts such as `prefix: [InMemory,
Fake]`, by any of them: `stand-ins` and `dead-code` read each, and a fix writes the first.
A test may import the fakes (`fakes.folder`) when its tier's subject holds a part `fakes.for` names; `fakes.tiers:
[<tier>, ...]` (default none) lets the tests of the tiers it lists import them too, a tier with no such part, such as
one placed by its `folder`, and `stand-ins` then holds their mocks as well. A tier the profile does not have is
refused; nothing else opens the fakes to a tier (its `imports.may` never does).
A tier's `folder` holds the tests below it that mirror no part (`tiers: {unit: {folder: unit, imports: {may:
[...]}}}`): they import of the app what its `imports.may` allows, and test code from their own folder, the top folder
below the tests root. A tier's `folder` may lie inside another tier's (`unit` and `unit/meta`), never be the same one:
a test has the tier of the deepest folder holding it, that folder is its own folder, and the outer tier's own folder
leaves it out.
A part's `untested: <reason>` says that no tier covers the part through tests that mirror its folder, the only link
`check` draws between a part and its tests; it does not say that the part has no tests. A suite laid out tier first
(`tests/<tier>/...`, each tier placed by its `folder`, helpers shared through `testing.shared` and the fakes opened
through `fakes.tiers`) therefore gets tier-level checks only: what each tier's tests import, and that every test lies
in a tier, with no coverage per part. Each part keeps an `untested:` reason (such as `its tests lie tier first`), and
`scenario-coverage` and `guards.dead-code.untested`, which read the tests of the tier that covers a part, stay off.
That the table forms and the call form are neutral to a language is proved without a TypeScript reader: a test-only
framework (`tests/fakes/frameworks/stub.yaml`, a function form and a call form of a test, a loop form and a call form of
a table with literal rows) is checked on hand-built facts and worded by the `writing` of the test-only language
`brace.yaml`, beside a framework that writes no form and the loop form read by Python's reader. One fact is never written under
`supplies`: `file.package`, that a file stands for the
folder holding it, follows `package_files`, and the keys whose check reads it (`package_only`, a part's `imports.must`,
`guards.dead-code.untested`) are refused under a language that has none.

The smallest valid profile is a name and one part (it runs `structure`, the import rules, `libraries` and `syntax`):

```yaml
name: documents-app
parts:
  documents/:
    role: the documents
```

The symbols:

- Under `parts`, a key ending in `/` is a folder of one or more steps (`modules/<module>/`), a key holding a dot is a
  file (`controller.py`), and any other key is a key of the part the folder or file is. A folder with a `role` is a
  part; one with no key of a part is only a folder, whose value may be one line of text, its note; a file is always a
  part. A part is named by its folder's last step or its file's name before the first dot, or by `name:`, which two
  parts of one name need. `<unit>/` is a repeating folder, one instance per name (`xarch new` takes the word); a
  profile may have several, each with a word of its own and one parent, and one cannot sit inside another. An
  instance is a folder the layout does not name: a file lying beside the instances (`sql/engine.py` beside
  `sql/<store>/`) belongs to the part of the folder holding them, or is its own part when the layout names it, and a
  folder the layout names beside them (`adapters/web/` beside `adapters/<adapter>/`) is never an instance, for the
  import rules and `where` alike. `cycles` still holds such a folder in one graph with the instances, so a loop
  through it (`adapters/mail` → `adapters/web` → `adapters/factories` → `adapters/mail`) is found; a file lying beside
  them is no node, nor is a part the layout names anywhere else.
- `optional: true` on a part, a folder or a file, says it may be left out: `structure` does not ask for it, in the app
  or in any instance of its repeating folder (a `config.py` only some modules hold, a controller only one module has),
  and `new` and `init` do not make it. Where it is there, its code is checked as any part's, and what the layout puts
  in it is required.
- Every list of parts under `imports` writes each target as a reference: `parts.store` is that part in every
  instance of its repeating folder (or, outside one, the part itself), and `<word>.store`, such as `unit.store`, the
  part in the importer's own instance of the `<word>` folder, which the importer lies in too (in a tier's
  `imports.also`, the instance the test mirrors, so a part the tier tests must lie in that folder); either is
  optionally followed by `/<path>`, only that path below the part (`parts.store/schema`), and, in `imports.may`,
  `:<pattern>`, only the names that match the pattern, imported by name (`parts.store:*Id`). `everything` is no
  limit (also for `imports.libraries`); an entry written `{parts.store: types_only}` is a target the part may
  import only to use as a type. A tier's `imports.must` and `imports.types_only` name whole parts, `parts.<part>`,
  for a tier's tests lie in no instance. A part may always import itself. `profile explain --rule` and the looser
  lines of `profile check` and `check` write a target the same way. The forms before 0.3.0, `store@any`, `store@own`
  and the bare `store`, are refused with the reference to write (`'store@any': @any was removed in 0.3.0: write
  parts.store`). Every other key that names a part, outside `imports`, takes its plain name (`fakes.for: [store]`),
  and a repeating folder cannot be written `<parts>`.

This is the whole format on one screen. The reference for each key (what it means, what it accepts, whether `check`
enforces it and through which rule, an example that loads, the keys it holds) is the command, which reads the same
table the loader does, so it cannot drift from what is accepted:

```
xarch profile explain                      # the whole format, symbols and smallest profile
xarch profile explain parts.imports.may    # one key; also: guards.no-duplicates, testing, tiers.folder, ...
xarch profile explain --profile web        # a profile's folder tree and import table, for a human to approve
xarch profile new mine --from web          # copy a bundled profile into architecture/mine/, with its files
xarch profile check [NAME|FILE]            # validate a profile without an app
```

`explain` takes `--format json` (`{"ok", "key", "where", "meaning", "accepts", "required", "enforced", "read_by",
"rules", "example", "choices", "keys", "needs", "language"}` for a key, `read_by` the command other than `check` that
alone reads it (`review` for `review` and its keys, else null; each `shape` entry has it too), `language` the language whose reader `needs` is graded
by; `{"ok", "key", "profile", "rules", "checks", "needs"}` for a key with
`--rule`, `needs` the facts its rules read; `{"ok", "shape", "symbols", "smallest", "deeper"}` for the whole) and
exits 2 for a key the format does not have, naming the nearest (in JSON, `nearest` the format's keys and `words` the
words of a check). The key may be written with or without the placeholder
steps (`parts.imports.may` or `parts.<part>.imports.may`). `--profile NAME|FILE` (or `--configured`, the project's profile)
prints the folder tree with each folder's role and the table of what each part may import, as the generated docs show
them.

`new NAME --from BUNDLED` writes `architecture/NAME/NAME.yaml` (beside the app folder; `--out FOLDER` to choose) with
`name: NAME` and `based_on: BUNDLED`, plus every file the profile points to (templates, docs pages, init files, example
folders), so the copy loads on its own and passes `profile check` as it is. If any target file exists nothing is written
and the ones that exist are named. `pyproject.toml` is never edited: it prints the `profile = "..."` line to add under
`[tool.xarch]`, because that line changes what `check` enforces and `init` has usually set it already.

`check` loads the profile (every problem at once, which includes every file it points to existing), runs the
example-import check (the examples' imports obey the profile's own rules), holds each check the profile writes itself
to its examples, and shows how it differs from the profile it is compared with, as information (but for a part left
without the litmus that profile gives it, which fails `check --strict`). That profile is the one `--against NAME|FILE`
names for the run (a bundled name, or a path to a profile file read from the working folder; one that does not load
refuses the run, exit 2), else the one its `based_on` names, else the bundled one of highest match. `based_on` is a
bundled name or the path of a profile file (`based_on: ../team.yaml`), read from the folder of the file that writes
it and compared with as written; that file's own `based_on` is followed in turn, and a file of the chain that does not
load, or a chain that comes back to a file of it, refuses the profile (exit 2). A bundled profile
is its own baseline and is compared only with `--against`, which the heading says: `checking cli (bundled; against
web, given with --against)`, and for a custom one `(custom; against web, given with --against; based_on: cli)`, its
match line reading `match: 73% with web (--against): ...`. A profile based on a file is headed `checking
sub/mine.yaml (custom; based_on: ../team.yaml, resting on cli)`, naming the bundled profile `--strict` rests on (`resting
on no bundled profile` when there is none). Before that comparison a `match:`
line says how much the two profiles have in common: `match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part
keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them`, then the parts
and tiers only one of them has, each part the other has by the same name at another path, `low: ...` when the match
is below 75%, and the bundled profile that matches higher than the one `based_on` names. With no argument it checks
the project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen or
`--against` names one that does not load;
`--format json` gives `{"ok", "profile", "problems": [{"check", "message"}], "files", "checks", "compared_with"}`,
`check` being `load`, `examples`, `checks` (a check of the profile's own) or `evals` (an eval of its own), `files`
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load. `compared_with` is `null` for a bundled profile checked without `--against`
or one no bundled profile resembles, else `{"profile", "chosen_by", "match", "low", "counts", "only_here",
"only_there", "elsewhere", "higher", "looser"}`: `chosen_by` `based_on`, `against` or `closest`, `match` the share to
two decimals (`0.8`), `counts` `{"parts",
"part_keys", "tiers", "guards", "profile"}` each `[comparable, all]`, and `higher` `null` or `{"profile", "match"}`.

### Checks of your own

Every check xarch runs from a key (all but `cycles`, `structure`, `test-tree`, `counterpart`, `stand-ins`, `scenario-coverage`,
`no-duplicates`, `no-twins` and `shared`) is a rule written in a small vocabulary, and a profile may write rules of its own in the
same words under `checks`: each reads the facts of a kind (`read`) in some files (`in`), keeps those its filters pass
(`keep`), and says that a kept fact may not match its targets (`may_not`), may only match them (`may_only`), or that a
file must reach a target (`must_reach`) or a fact be reached from some files (`must_be_reached`); an exception
(`except`) excuses a finding, and `message` and `fix` say it, with `{variable}`s (`once_per` says a file's findings
once for each value of its variables; `per_line` says the findings of one line that differ only in its variables as
one, each written as its values joined by `, `). An import made only for the type checker, never when the code
runs, carries the field `type-only` (the fact `import.type_only`; Python's reader sets it on each import in the body of
an `if TYPE_CHECKING:` or `if typing.TYPE_CHECKING:`, not its `else`), so a check that reads `import` or
`imported-name` may keep only those (`keep: [type-only]`) or skip them (`keep: [not type-only]`). A class carries its
`bases` (the fact `class.bases`): each base it names, read through the import that binds it (an alias by the name it
was imported as) or as a class of its own file, then the bases of each class the project defines, in the app or in
the tests, however far; the filter `extends: <pattern>` holds of a class one of those matches by its name, so
`keep: [{named: "*Page"}, {extends: Reactive}]` finds a page that derives from `Reactive` through any number of classes
between, and `except: [{extends: "*Port"}]` excuses a fake that derives from a port. A base taken from a package file
that only re-exports it is followed no further than its name. Two quantifiers count instead of matching targets,
in each file of the scope alone (never across a part or the instances of a repeating folder): `at_most: <n>` makes
each kept fact of a file after the n-th a finding, at its own line (`read: class`, `keep: [{named: "*Port"}]`,
`at_most: 1`: one port per file), and `at_least: <n>` makes a file that keeps fewer a finding, at line 0; `{count}`
says how many the file keeps. The kind `file` carries `lines` (the fact `file.lines`), which the filter
`longer-than: <n>` and the variable `{lines}` read: `read: file`, `keep: [{longer-than: 700}]`, `may_not: exist` finds
each file over 700 lines. `must_not_reach` is the negation of `must_reach`, written the same way (`targets`, `through`,
`through_only`): a file of the scope that reaches a target, by a kept fact of its own or through the files its links
lead to however far, is a finding at the line of its first step, and `{chain}` says the way, each file a link leads
to as a dotted name, then what matched (`app.store -> app.store.sql -> sqlalchemy`), the shortest found. An import of
a name from a package file reaches that package file (`import-into-app` follows a name to its own file only when the
name is a file), and the way then goes on through every file the package file imports, so a name the package only
re-exports is followed, and so is anything else the package file imports. The kind `function` (a method too) carries
its `parameters`, in the order its signature declares them, each with its name, its annotation as written and whether
it has a default, and its `returns`, the return annotation as written (the facts `function.parameters` and
`function.return_annotation`; an annotation is empty where the code writes none, or in a language that writes none,
and then matches no pattern): the filters `has-parameter: <pattern>` (a parameter of that name),
`parameter-has-default: <pattern>` (such a parameter, with a default), `parameter-annotated: <pattern>` (a parameter
whose annotation matches) and `returns-annotated: <pattern>` read them, and `{parameters}` and `{returns}` say them:
`keep: [{parameter-has-default: actor}]` finds each function that gives `actor` a default, `keep:
[{returns-annotated: "*Row*"}]` each that returns a row. The kinds `call`, `method-call` and `construction` carry
their `arguments` (the fact `call.keywords`): each keyword argument they pass, by name, with its value as written when
it is a literal (`3`, `'x'`, `True`; a name or any other expression is no literal); the filter `passes: <pattern>`
holds of a call that passes a keyword the pattern names, and `passes-literal: <pattern>` of one that passes it a
literal, `<pattern>=<text>` matching the value's text too: `read: method-call`, `keep: [{passes-literal:
skip_locked=True}]` finds each `.with_for_update(skip_locked=True)`. Positional arguments are not read. A `call`
carries its `name` too, the last name of its callee, so `named` and the target `name` apply to it (`keep: [{named:
"get_*"}]`). A check carries `examples`: code it
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

A check may accept findings one by one, each with a reason, under `accepted`: a list of `{file, why}`, each naming a
file by its path below the app (`tests/<path>` for one below the tests root) and, if need be, the finding by the value
its check prints for one or more variables (`name: InvoiceClock`). An entry that names no variable accepts every
finding of the check in that file, the grain of an allowlist of files; one may not name a finding by its `line`,
which moves with every edit above it. A finding an entry accepts is not reported, and the enforcement section names it
under `accepted:` instead; an entry that accepts nothing is itself a finding of the check, at its file, so the list,
a ratchet, can only shrink. A finding said once for several facts (`once_per`, `per_line`) is matched on the first.

```yaml
    accepted:
      - {file: tests/billing/test_invoice.py, name: InvoiceClock, why: "the invoice tests freeze two clocks"}
      - {file: tests/legacy/test_export.py, why: "the export suite is retired with the export"}
```

The whole vocabulary, from the same table the engine reads, is the command:

```
xarch profile explain checks               # how a check is written and read, with a whole one as an example
xarch profile explain filters              # a category of words: kinds, quantifiers, targets, filters, variables
xarch profile explain filters.public       # one word: what it means, what it applies to, an example
xarch profile explain parts.holds --rule   # the rules a key of your profile expands to, written as checks
```

## What check checks

`check` reads only the files the profile governs: a file in a part, or a package file of a folder of the layout. A file
anywhere else is never read and is listed as `ungoverned` in the enforcement section; extra top-level folders and files
at the app root are ignored unless the profile switches on `closed-tree`, as both bundled profiles do. A folder that is not the app's source at all
is declared under `excluded`, and then no check looks at it. Extra files and subfolders inside a known part belong to
that part.

Every violation names its rule id, says what was found and, on a `fix:` line, what to do. The ids, with the profile key
that switches or configures each (`-` for none: the rule is always on):

| Rule id | What it catches | Key |
|---|---|---|
| `syntax` | a file that does not parse, or that cannot be read as UTF-8 text at all (the message says which), so no other check could read it | - |
| `structure` | a folder or file of the layout missing, at any depth, in the app and in every instance of each repeating folder; an optional part, and what it holds where it is not there, aside, and a path `structure.accepted` names; an entry of it that names no finding | `parts`, `parts.name`, `parts.optional`, `structure.accepted` |
| `may-import` | an import between parts that the importing part's `imports.may` does not allow, or a name its pattern does not match, but one its `imports.accepted` names, which the enforcement section names instead; the findings of one import line are one, listing what it may not take (the names the pattern does not match, or the places it may not import); an entry of `imports.accepted` that accepts nothing any more (its file gone, the import gone, or `imports.may` now allowing it) | `parts.imports.may`, `parts.imports.accepted` |
| `libraries` | an outside package a part does not list, or a standard-library name `reserved` holds that it does not list; the rest of the standard library is always allowed, tests are not checked | `parts.imports.libraries`, `reserved` |
| `never-use` | a name or module a part (or, with `uses.apply_never`, its tests) may not use, or a method written `.name()` it may not call on anything but its own object and what that holds | `never`, `parts.uses.never`, `tiers.uses.apply_never` |
| `tiers` | a test importing what its tier does not allow, or another test file, or a test in no tier, but what a tier's `accepted` names; an entry of it that names no finding | `tiers`, `tiers.folder`, `tiers.imports.may`, `tiers.imports.also`, `tiers.accepted`, `parts.tests`, `testing.shared`, `fakes.tiers` |
| `test-tree` | a folder below `tests/<repeating folder>/` that mirrors no folder of the app, but one `structure.accepted` names; an entry `tests/<path>` of it that names no finding | `tiers`, `testing`, `structure.accepted` |
| `counterpart` | a match of a counterpart's `for`, where its `when` matches too, with no match of its `has`, but one its `accepted` names; an entry of `accepted` that accepts nothing (its source gone, or now with its counterpart) | `counterparts` |
| `types-only` | a test, or code of a part, calling what it may import only as a type | `tiers.imports.types_only`, `parts.imports.may.types_only` |
| `cycles` | instances of the repeating folders that import each other, directly or through others (across repeating folders too, and through a folder the layout names beside the instances, such as `adapters/web/` beside `adapters/<adapter>/`, which takes part in the graph though it is no instance); each group of instances that all reach each other is one finding, however many cycles run through it: it names the group's instances, how many dependencies run between them, and the dependencies to cut, each with its imports (once per file and line), reported at the first import of the first of them. They are the dependencies that go back in an order of the group chosen so that few imports go back (greedily: an instance nothing left depends on first, one that depends on nothing left last, else the one whose imports out most outweigh its imports in); cutting them all leaves the group with no cycle | - (needs a repeating folder) |
| `package-only` | an import of a file of a part from outside it, where the part is imported as a package | `parts.package_only` |
| `must-import` | a file of a part that never reaches any of the targets the part must reach, nor an outside package, or a test that never reaches what its tier must | `parts.imports.must`, `tiers.imports.must` |
| `scenario-coverage` | a variant of a result union with no row in its use case's test table, or a branch (a statement of `branching`, an expression of `branching_expressions`) in a table test's body; with `plain_tables`, in any table test of that tier; with no table form, a variant named by no test | `guards.scenario-coverage`, `tiers.plain_tables` |
| `no-comments` | a comment of the language in the app or its tests (`#` for Python), but a doc comment and those its tools read | `guards.no-comments` |
| `stand-ins` | a read port without a fake, or a mock without a spec or with a read port's | `guards.stand-ins`, `fakes` |
| `closed-tree` | a Python file of the app that lies in no part | `guards.closed-tree` |
| `no-duplicates` | two functions or methods of the app with the same code | `guards.no-duplicates` |
| `no-twins` | two public classes in parts of different names that declare the same fields in the same order: one type written twice; with `min_renamed`, also a copy that renamed a field, and with `min_subset`, one that kept at least half of the other's fields in its order; with `translated`, a pair is no twin when a file of a listed part builds one of the two through an import, imports the other (from the file defining it, or from one that takes it from there), and holds one function that names both; a class a file builds where it defines it is built through no import, and translates nothing; each pair so accepted is named in the enforcement section | `guards.no-twins` |
| `dead-code` | a port no other file names, a fake no test uses; with `untested`, a file no test of its tier reaches, and with `tests_only`, a public class or top-level function no other file of the app names (only the tests, or nothing, use it), but those `known` accepts, which the enforcement section names instead, each listed as `weak` only; an entry of `known` whose file defines no such name, whose name another file of the app names, or that no test names in its code (a string of a test does not count), is listed as `weak` too | `guards.dead-code`, `fakes` |
| `pass-through` | a method that only forwards its arguments to a collaborator, or returns an attribute of what that call answers; never a violation: listed as `weak`, and fails only `--strict` | `guards.pass-through` |
| `holds` | a public function at the top level of a part whose `holds` does not list `functions`, or a class (whatever its name) of one that does not list `classes`, but an exception or a record when it lists that kind, each said as the narrowest kind it fits; listed as `weak`, and fails only `--strict` | `parts.holds` |
| `immutable` | a class a part holds to `classes`, or a record it holds to `records`, when that kind sets `immutable`, that is no immutable record as the language's data file says one is made, an exception aside; listed as `weak`, and fails only `--strict` | `parts.holds.classes.immutable`, `parts.holds.records.immutable` |
| `no-callbacks` | a function of a part the guard lists that calls one of its own parameters annotated as a callable | `guards.no-callbacks` |
| `names` | a public class, top-level function, record or exception of a part whose name matches none of the patterns of the kind it is held to, a class being held to the narrowest kind listed that it fits | `parts.holds.<kind>.names` |
| `built-by` | a call of the constructor of a class a part holds to `classes` from a part their `built_by` does not list | `parts.holds.classes.built_by` |
| `private-imports` | an import of a name another file of the app or its tests keeps private (for Python, one starting with `_`) | `guards.private-imports` |
| `shared` | a public name of a part declared shared that fewer users use than it says (a user: an instance of a repeating folder, or a part outside them; tests not read) | `parts.shared` |

A key left out means its check is off. For what a key means, accepts and exactly checks, run
`xarch profile explain <key>` (for example `xarch profile explain guards.no-duplicates`, `parts.imports.must`,
`never` or `tiers`); it reads the table the loader reads, so it cannot drift. A violation's `fix:` says what to do
about that finding, and a profile's `hints` add its own advice after it.

## The output of check

### Text

Every violation says what to do about it. A finding is its line, `<file>[:<line>]: <message>`, then an indented line
`fix: <what to do>`, one imperative sentence specific to the finding, and, when the profile has a
hint (`xarch profile explain hints`) for its rule, an indented `hint: <text>` line. The findings come in order of
file, then line (a whole file first), then rule, then a summary, `OK: no violations` or `<n> violation(s) in <m>
file(s)`, then the enforcement section (below). Paths are relative to the folder holding the app folder
(`app/kernel/x.py`, `tests/...`). What the language's parser warns of the code it reads (for Python, a
`SyntaxWarning` such as an invalid escape sequence in a string) is not printed: it is about the code, not xarch's
output, and a linter reports it.

```
app/kernel/x.py:1: kernel/ may not import platform/ (app.platform)
    fix: import only kernel/ in kernel/ (parts.kernel.imports.may), or move this code to adapters/, which may import it
    hint: the layers are in docs/project/architecture.md
1 violation(s) in 1 file(s)
```

### Checking some files: `xarch check PATH ...`

Given paths (files or folders, read from the working folder), or a list of them with `--files-from FILE` (`-` for
stdin, one path per line, blank lines ignored; both may be given), `check` shows only the violations of the files at
or below them, and only those decide the exit code (0, 1 or 2, as for a whole check). It is meant to run after every
edit, by an agent's hook or a pre-commit hook:

```
xarch check app/modules/docs/domain/document.py
git diff --name-only HEAD | xarch check --files-from -
```

Every check still runs on the whole app and its tests, whole-program ones included (`cycles`, `dead-code`,
`no-twins`, `shared`, `stand-ins`, `scenario-coverage`): a partial check skips none, so a violation an edit causes in
the file edited is never missed because its cause lies elsewhere. What it does not show is counted: the summary
names the paths given, `OK: no violations in the 1 path(s) given` or `<n> violation(s) in <m> file(s) of the <k>
path(s) given`, and a `partial:` line follows it, naming the paths, saying that no check was skipped and how many
violations other files have, so its OK never reads as the whole app's:

```
OK: no violations in the 1 path(s) given
partial:     1 path(s) given (app/kernel/clean.py); every check ran on the whole app and its tests, none skipped; 2 violation(s) in other files, not shown: run `xarch check` with no path to see them
```

The enforcement section is the whole app's, as is what `--strict` fails on. In JSON the document gains
`"partial": {"paths": [...], "skipped_checks": [], "elsewhere": <n>}`; a whole check has no `partial` key.

What makes it fast is not reading less but reading once: the reader keeps what it read of each file in a cache, and
a file read again whose text, the way it is read (the profile's language and test framework) and what its relative
imports find on disk are all unchanged, read by the same xarch code, is not parsed again. On xarch's own 310 files a
whole check takes about 11 s with no cache and 1.5 s with it, so a check of one file after an edit takes about as
long as a whole one with a warm cache. The cache is in `xarch/` in the user's cache folder (`$XDG_CACHE_HOME`, else
`~/.cache`); the environment variable `XARCH_CACHE_DIR` names another folder, and set empty switches it off. A cache
that cannot be read is ignored and one that cannot be written is not written; it never changes what `check` finds,
and the folder may be deleted at any time.

### JSON

`xarch check --format json` prints one JSON document on stdout, and nothing else. This shape is a contract: fields
and rule ids may be added, but an existing one keeps its name and meaning.

```json
{
  "ok": false,
  "strict": false,
  "profile": "web",
  "violations": [
    {"rule": "never-use", "file": "app/modules/docs/domain/clock.py", "line": 1,
     "message": "domain/ of modules/docs may not import socket (parts.domain.uses.never)",
     "fix": "do what needs socket outside domain/, and hand domain/ the result",
     "hint": null}
  ],
  "enforcement": {
    "profile": {"location": "web", "bundled": true, "compared_with": null, "guards_off": [], "baseline_off": [],
                "looser": []},
    "ungoverned": {"count": 0, "folders": [], "files": []},
    "excluded": [],
    "known": [],
    "translated": [],
    "init_files": [],
    "skipped": {"count": 0, "at": []},
    "dynamic": {"count": 0, "at": []},
    "unresolved": [],
    "weak": [],
    "approximate": [],
    "strict_failures": []
  }
}
```

A profile that writes checks of its own also has `"checks"` in `enforcement`: each `{"id", "read", "said"}`, `read`
how many facts it read in the project; one that writes counterparts has `"counterparts"`, each the same, `read` how
many matches of its `for` it read. A check of some paths also has `"partial"` (see
[Checking some files](#checking-some-files-xarch-check-path-)): `paths` as given, `skipped_checks` (always `[]`:
every check runs on the whole app) and `elsewhere`, how many violations of other files `violations` leaves out. A
run in which a part's `imports.accepted` accepts an import also has `"accepted"` in `enforcement`: each
`{"file", "line", "part", "import", "why"}`, the import as the entry writes it. A run in which an entry of a
check's `accepted` accepts a finding also has `"accepted_findings"` in `enforcement`: each `{"rule", "file", "line",
"key", "message", "why"}`, the finding as it would be reported, and `key` the entry's list
(`checks.<id>.accepted`, `structure.accepted`, `tiers.<tier>.accepted`).

- `ok`: no violation (of the paths given, for a partial check), and with `--strict` no enforcement finding either; it agrees with the exit code. `strict`:
  whether `--strict` was given. `profile`: the profile in force, a bundled name or a path, as selected.
- `violations`: sorted by `file`, then `line` (a whole-file or folder violation, `line: null`, first), then `rule`.
  `file` is the path the text output prints; `message` the sentence it prints after the path; `fix` what to do about
  it, always a non-empty string (a violation cannot be made without one); `hint` the profile's own advice for the
  rule, else `null`. `rule` is one of: `may-import`, `libraries`, `never-use`, `tiers` (a test's imports, or a test in
  no tier), `types-only`, `cycles`, `package-only`, `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`,
  `must-import`, `no-duplicates`, `no-twins`, `dead-code`, `pass-through`, `holds`, `immutable` (these three never a
  violation, only a weak item), `no-callbacks`, `names`, `built-by`, `private-imports`, `shared`, `structure`,
  `test-tree`, `counterpart`, and `syntax` (a file that does not parse, or cannot be read as UTF-8 text), or the id of a check the
  profile writes itself. An import line that takes several names a part may not import is one `may-import`
  violation, its `message` listing them (or the places it may not import), so the violations count lines, not
  names.
- `enforcement`: every key always present, empty when there is nothing to report. `profile.looser` items are
  `{"key", "part", "what", "sentence"}` with `key` one of `imports.may`, `imports.may.types_only`, `imports.libraries`,
  `uses.never`, `untested`, `optional`, `imports.accepted`, `imports.types_only`, `imports.also`, `uses.apply_never`, `testing.skips`, `testing.shared`,
  `fakes.tiers`, `files.pinned`, `reserved`, `imports.must`, `litmus`, `known`, `checks.accepted`, `structure.accepted`, `tiers.accepted`, `counterparts.accepted`, `translated` (the `sentence` names the full address, such as
  `parts.kernel.imports.may`); `excluded` items
  `{"folder", "reason"}`; `known` items `{"file", "line", "name"}`, each public name `guards.dead-code.known` accepts
  as only the tests'; `translated` items `{"file", "line", "function", "built", "other"}`, each pair of classes
  `no-twins` accepts as a translation (`guards.no-twins.translated`): the function that names both, where it is, the
  class its file builds and the other; `init_files` items `{"file", "state"}`, `state` `missing` or
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `unresolved` items `{"file", "line", "written"}`,
  each import the reader could not follow, at its first line, with the module as the source writes it; `weak` items
  `{"rule", "file", "line", "message", "fix"}` (`fix` is `null` for a weak check that has none); `approximate` items
  `{"key", "fact", "note"}`; `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `ungoverned`,
  `init_files`, `skipped`, `dynamic`, `unresolved`, `weak`, `approximate`, `vacuous` (a check of the profile's own
  that read nothing, or a counterpart whose `for` matches nothing), `litmus` (a part redefined without the litmus its compared profile gives it), `baseline` (a
  baseline that records more than is found). `strict_failures`
  is filled whether or not `--strict` was given: it is what `--strict` fails on.
- A refusal (exit 2: an unknown or invalid profile, a missing folder) prints `{"ok": false, "error": "<reason>"}` on
  stdout, so a caller always gets JSON. Only an error in the command line itself (an unknown option, a `--format`
  that is neither `text` nor `json`) is typer's usage message on stderr.

### The enforcement section

A check can be made to pass by weakening it: by moving code where no rule applies, switching a guard off, loosening a
rule or deleting the guard test. So after the violations, and also when there are none, `check` reports the state of
its own enforcement. In text, a line with nothing to report is left out:

```
enforcement
  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)
    guards off:  no-comments, closed-tree
    imports.may: kernel may also import platform (parts.kernel.imports.may)
  ungoverned:  1 Python file outside every part (app/scripts/)
  excluded:    app/examples/ (example sources the docs show)
  accepted:    app/adapters/mail/send.py:3: imports web/i18n.py, which parts.adapter.imports.accepted accepts: the mail copy is translated by the web ring until its port exists
  known:       app/bootstrap/wiring.py:12: build_app is public, a test names it and no other file of the app does, which the profile accepts (guards.dead-code.known)
  init files:  tests/architecture/test_rules.py is changed
  skipped:     1 skip (tests/modules/docs/domain/test_x.py:4)
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  unresolved:  app/modules/docs/domain/services.py:3: import ".ordr" names no file of the app
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
  weak:        app/modules/docs/application/services/doc.py:9: DocService.get only passes its arguments on to self.repo.get
      fix: have the caller use self.repo.get, or keep it as a deliberate plain forward: it stays listed and fails only `check --strict`
```

- `profile`: the bundled name, or the custom file's path, the profile it is compared with, why (`--against`, the one
  `--against` names for the run, which compares a bundled profile too: `web (bundled; compared with cli, --against;
  match 89%)`; else `based_on`, the one its `based_on` names, else `closest`, the one of highest match, the first by
  name on a tie) and the match:
  the share of what `check` reads under either profile (each part, each key a part, a tier or the profile writes, each
  guard switched on) that has a counterpart in the other. Parts pair by name, then by layout path, and tiers by name,
  then by subject; a part or tier that pairs with none has no counterpart, nor does any key it holds. A match below
  75% is low and says so on a `match:` line under this one, with why; `profile check` shows the counts. One no part
  pairs with is no candidate, and with none left nothing is compared. In JSON, `enforcement.profile.compared_with`
  holds the same object as `profile check`'s (`null` when nothing is compared). `--strict` with `--against` is
  refused (exit 2): `--strict` judges the profile against its baseline, which `--against` leaves as it is, so the
  violations and `strict_failures` are the same with it and without it. When `based_on` is the path of a profile file, `--strict` rests on a bundled profile, its anchor: the bundled profile the chain of files ends on, else the bundled profile closest to its last file, else none. The line says it, `mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on cli)` (`--strict rests on no bundled profile` with none), and `compared_with.anchor` holds it in JSON: a bundled name, or `null` (with `--against`, and for a profile compared with a bundled one it is that one). A guard left off is excused only when the anchor and every file of the chain leave it off too, and a part fails `litmus` when it lacks a litmus that the path file gives the part it pairs with there, or that the anchor gives the part it pairs with in the anchor: a file of one's own can tighten `--strict`, never loosen it. `guards off` lists every guard xarch has that the profile does not switch on, for a bundled profile
  too; one of them, `package-only`, is switched on by a part's `package_only: true` rather than under `guards`, and the
  line names that key. For a custom file, each way it is looser than the one it is compared with, compared only on
  the parts and tiers that pair (a part renamed in place is still compared, under its own name): a target added to a part's `imports.may`, a `types_only` mark dropped from an entry of it, an outside package
  added to its `imports.libraries` (or `everything`), a name of its `uses.never` list no entry covers any more, a part newly `untested`, a part newly `optional`, a part dropped from a tier's
  `imports.types_only`, a target added to a tier's `imports.also`, a tier no longer `uses.apply_never`, a name dropped from `testing.skips`, a `files` entry no longer
  `pinned`, a target added to a part's `imports.must` or the key dropped, a part redefined without the `litmus` the
  other gives it, a public name `guards.dead-code.known` accepts that the other's does not, a part
  `guards.no-twins.translated` lists that the other's does not, a line under `evals.placement.lines` set below the
  other's, an entry of `review.never` or `review.mask` the other holds and this one drops, a kind a part's `holds`
  allows that the other's does not (`classes` allowing `records` and `exceptions` too), a setting of a kind it holds
  dropped or widened (`names`, `immutable`, `built_by`, compared kind by kind on the settings the part holds each kind
  to, for a kind either lists), a part's `shared` dropped or lowered, a tier's `imports.must` dropped or a part added
  to it, a tier no longer `plain_tables`, `testing.beside` set where the other leaves it out, an entry of
  `testing.shared` the other does not share, a tier `fakes.tiers` lists that the other's does not, and an entry of a
  part's `imports.accepted` (a file and what it imports) the other's part does not hold, and an entry of a check's
  `accepted` (a file, and the variables it names) the other's check of the same id does not hold, and an entry of
  `structure.accepted` (a path) the other does not hold, and an entry of a tier's `accepted` (a file, and what it
  imports) the other's tier does not hold.
  Stricter differences, new parts, the layout and the guards' other parameters are not compared. This comparison is
  information: the profile defines the architecture, so how it differs from another is no finding for `--strict`, but
  for a litmus dropped, which leaves a part's code no question to be placed by.
- `ungoverned`: the app's Python files in no part and no folder of the layout (what `closed-tree` would report),
  which no check reads, counted with their top folders.
- `excluded`: each folder the profile's `excluded` key leaves out, with its reason; no check reads a file below it,
  so the exclusion stays visible here.
- `translated`: each pair of classes `no-twins` accepts as a translation (`guards.no-twins.translated`), naming the
  function that translates and where it is: the check does not report the pair, so the acceptance stays visible here.
- `accepted`: each import a part's `imports.accepted` accepts although its `imports.may` does not allow it, where it
  is, with the entry's reason: `may-import` does not report it, so the acceptance stays visible here. An entry that
  accepts nothing any more (its file is gone, the file no longer imports what it names, or `imports.may` now allows
  it) is itself a `may-import` violation, so a list of accepted imports, a ratchet, can only shrink. Each finding
  an entry of a check's `accepted` accepts is listed here too, as the check would report it, with the entry's list and
  its reason; an entry that accepts nothing is a finding of its check. So is each finding of the layout
  `structure.accepted` accepts, and each `tiers` finding a tier's `accepted` accepts.
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
  the profile; the import rules cannot see what it imports. Each call, in the files read, of a callable the data
  file lists as reading a member of an object by a computed name (`dynamic_attributes`: for Python, `getattr`) whose
  first argument is a name an import binds, is listed here too: `uses.never` cannot see which member it reads.
- `unresolved`: each import, in the files read, that names a place of the app (relative, or by an alias the project
  maps) the reader found no file or folder for, at its first line, with the module as written, one line each; the
  import rules cannot see what it names.
- `weak`, met to the letter only, never a violation: a fake `<prefix><Port>` that defines in its own body (methods,
  or names its body or `self.` assigns) less than every port of its name declares; and a `Result` variant that no
  row covers, credited only to standalone tests that name it and hold no `assert`; a method `pass-through` finds; a
  class or function `holds` finds where its part does not hold that kind, and a class `immutable` finds mutable; a
  file `dead-code`'s `untested` finds no test of its tier reaches, a name its `tests_only` finds only the tests use,
  and an entry of `guards.dead-code.known` that no longer holds; and a finding of a check of the profile's own
  whose `mode` is `list`. None of them changes the exit code of a plain `check`; each fails `--strict`, which the
  guard test runs. A weak check that has a fix shows it on an indented `fix:` line under its own.
- `approximate`: each key the profile sets whose check reads a fact the language's reader supplies only partly, as
  its data file grades it (`supplies`), with what the reader misses: the check runs, and may miss what it looks for.
  A key whose check reads a fact the language does not supply at all is refused when the profile loads, naming the
  key and the fact. Python's reader supplies every fact exactly but `function.tables.call`, and none partly, so a
  Python project never sees this line.

Without `--strict` the section never changes the exit code. `--strict` fails (exit 1) on every finding listed in
`strict_failures`: what the profile in force leaves unenforced or unseen: each guard left off that the bundled profile
in force, or the one a custom profile is compared with, does not also leave off (with no profile to compare with,
every guard left off); each ungoverned file; each missing or changed init file; each skip; each dynamic import; each
unresolved import; each weak finding; each approximate key; each part redefined without its litmus. The text lists
them after the section, under `strict:`. The guard test `init` writes runs `check --strict` (see
[Project files](#project-files)): a fresh project of either bundled profile has no such finding.

## Adopting xarch on existing code: `xarch baseline write`

A project that adopts xarch with violations it cannot fix at once records them in a baseline, which `check` then holds
back, so that only what is new is reported, and the record may only go down:

```
xarch baseline write            # record every violation a whole check finds now in .xarch/baseline.json
xarch baseline write --reset    # write it afresh, raising it where it is lower (the diff shows it in review)
```

`.xarch/baseline.json` sits in the folder holding the app, beside the record of accepted files: a version, then each
finding with its `rule`, `file`, `message` and `count`, one entry per key. A finding is keyed by its rule, its file and
its message with every run of digits read as one mark, so that a line moving or a count changing keeps it; findings
of one key are counted, and its count is its ceiling. Commit the file.

- No file: `check` is exactly as it was.
- A violation whose key the record holds, up to its count, is held back: not shown, counted on the `baseline:` line
  of the enforcement section (JSON `enforcement.baseline`). Every other violation is shown and fails the check: a new
  finding never hides behind an old one, since a fix in one place and a new finding in another (or in the same file,
  of another name) is a new key.
- A record above the code (a finding fixed, or moved) passes, and the line says `N below baseline: run \`xarch
  baseline write\` to lower it`; `--strict` fails on it (`strict_failures` key `baseline`), so the guard test keeps the
  record as low as the code. `--strict` does not fail on the findings held back: that is what the record is for.
- `check PATH ...` holds the record against the whole run first (every check runs on the whole app), then shows the
  violations of the paths given; the `baseline:` line counts the whole app's.
- `baseline write` with a record only lowers it: a key no longer found is dropped and a count lowered, never raised,
  and a new finding stays a violation; `--reset` writes every violation found now.
- An entry that accepts a finding (`imports.accepted`, `checks.<id>.accepted`, `structure.accepted`,
  `tiers.<tier>.accepted`) is applied first: an accepted finding is no violation, so it is never recorded, and a stale
  entry is a violation like any other.

In JSON, `enforcement.baseline` is present only when the record is: `{"file", "recorded", "baselined", "below",
"rules": [{"rule", "recorded", "found"}]}`. `xarch baseline write --format json` prints `{"ok", "file", "recorded",
"before", "reset"}`, `before` `null` when there was no record. A record that cannot be read is refused (exit 2).

## Running the check from an agent's hooks: `xarch hook claude`

A coding agent that runs `xarch check` only when it remembers to finds the violations late. `xarch hook claude`
prints the hooks that run it for Claude Code, as the JSON its settings hold; it writes nothing (add its `hooks` key
to `.claude/settings.json`, or `.claude/settings.local.json` for yourself alone, merging it with hooks already
there), reads no app and no profile, and needs `jq`, as Claude Code's own examples do:

- `PostToolUse`, matched on `Edit|Write`: the check of the file just written,
  `jq -r '.tool_input.file_path' | xarch check --files-from -` (see
  [Checking some files](#checking-some-files-xarch-check-path-)); it does not pass `--strict`, so a weak finding
  elsewhere does not interrupt every edit.
- `Stop`: the whole check, `xarch check --strict`, what the guard test runs, skipped when Claude Code is already
  going on because of this hook (`stop_hook_active`), so a check the agent cannot make pass never loops.

Each runs from `$CLAUDE_PROJECT_DIR`, prints the check's output on stderr and exits 2 when the check fails: for
`PostToolUse` Claude Code shows that output to the agent after the edit, and for `Stop` it keeps the agent working,
with the output as the reason. `--command "uv run xarch"` (or any other) says how the hooks run xarch when it is not
on the PATH.

Another agent's hooks are not printed: their formats are their own. The same two hooks carry over to any agent that
can run a command after it edits a file and before it ends its turn: after an edit, pipe the path edited into
`xarch check --files-from -` (or give it as an argument), and before it finishes, run `xarch check --strict`; both
exit 0 when clean, 1 with violations and 2 on a usage error, and print what to fix. An agent with no hooks follows
`AGENTS.md`, which tells it to run `xarch check --strict` before it finishes; the guard test catches what it forgets.

## Running the check before each commit: pre-commit

The repository ships a [pre-commit](https://pre-commit.com) hook, `xarch-check` in `.pre-commit-hooks.yaml`: it runs
`xarch check` with the files staged as its paths, in one run (`require_serial`), so the commit fails on their
violations alone (see [Checking some files](#checking-some-files-xarch-check-path-)); the violations of other files
are counted, not shown, and do not fail it. In the project's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/paulomtts/xarch
    rev: <a tag or commit of xarch>
    hooks:
      - id: xarch-check
```

pre-commit installs xarch in an environment of its own (Python 3.13 or later), which is enough: `check` reads the
source and never imports it. To run the xarch the project already has as a dev dependency instead, write the hook
locally:

```yaml
repos:
  - repo: local
    hooks:
      - id: xarch-check
        name: xarch check
        entry: uv run xarch check
        language: system
        pass_filenames: true
        require_serial: true
```

Neither passes `--strict`, which judges the whole app: add `args: [--strict]` to the first, or `--strict` to the
local `entry`, to fail the commit on it too, as the guard test does.

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
import (its `imports.may`, in the words of the docs' rules table), the outside packages it may import (`imports.libraries`: `none`,
a list, or `any outside package`), the names it never uses (`never uses`, from its `uses.never`), and the tier that
tests it with the file its test would be in (a part that is one file, such as a controller, has its test by use case:
`test_<use case>.py`; a part no tier tests says why). A path in no part is `ungoverned`, with the parts near it (those
below the nearest folder of the layout that holds it) and whether `closed-tree` is on; a folder of the layout that no
part claims is `structure`. A path in the project but outside the app and its tests is ungoverned too.

For a path in the tests: its tier, the part its folder mirrors, what it may import (the per-part rule: that part and what
it may import), whether it may import the fakes, the parts it may use as types only, what the tier proves and may touch,
its litmus test, and the one folder it may import test code from (and the shared test code, under `testing.shared`). A
test that lies in no tier says so (`note`); a file
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
  "never_uses": ["datetime.datetime.now", "builtins.open"],
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
  not check them; `never_uses` the dotted names the part never uses (its `uses.never`).
- `tier`: for a `part`, the tier that tests it (null when none does, and `untested` then says why); for a test, its tier.
  `tested_in`: for a `part`, the test folder and the file (`file` is empty when the path is a folder or no Python file,
  a pattern for a use case's test).
- `nearest`: for `structure` and `ungoverned`, the parts near it: `{"part", "folder", "path"}`. `closed_tree`: for
  `ungoverned`, whether `closed-tree` is on (that is, whether `xarch check` reports the file), else null.
- `test`: for `test`, `fake` and `support`: `{"may_use_fakes", "fakes_path", "types_only", "code_from"}`, whether it
  may import the fakes, where they live, the parts it may use as types and never call, and the folder it may import test
  code from; a profile with `testing.shared` adds `"shared"` to a tiered test's object, the shared folders (ending in
  `/`) and files below the project root. `note`: one line where the kind alone does not say it.

## xarch review: an advisory reading

`review` is experimental: its command line, its output and its JSON may change, and the bundled profiles ship no
calibration record, so a project runs `xarch review calibrate` once and commits the record. In 0.1.0, held to the
bundled profiles' own doc examples by the real model (`jev-1.14.0`, 2026-11-17), placement passed for 3 of the 12 parts
of the `cli` profile and 5 of the 12 of the `web` profile, and a part whose examples disagree is read but never marked
doubtful. Since 0.1.1 the litmus texts of eight parts say more exactly what decides a case, eight short example files
show it in their code, and every comment is cut from what is sent, so no comment can tell the model the answer;
measured again with the same model, placement passes for all 12 parts of both profiles, in each of five runs that asked every
example afresh. Across them the weakest example read 0.43 on its own part and none read above 0.27 on another, against
a line of 0.30. That is a sanity check of the litmus texts against 27 short examples, not a measure of how often a reading of
your code is right.

`review` is a second, advisory command, apart from `check`: it never runs inside `check`, never changes what `check`
finds or its exit code, and a review of files never exits 1 (`review calibrate` exits 1 when an eval fails its
examples). For each file chosen it asks a decision model which part of the profile the
file belongs in, with every part's litmus test (its role, for a part with none) as the options, and prints the
model's reading, ranked: a file whose probability on the part it sits in is below that part's line (0.3, unless the
profile sets the part's own under `evals.placement.lines`) reads as **doubtful here**. That says some of the file's content may not fit its part (all of it, a function of it, or none), and is a reason to read the file against its part's litmus, not a finding: in
trials, about 7 to 10% of well-placed files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files was really
misplaced. The text output names no other part but those its part is read alike with and those ruled out of its
answer (below); the JSON gives the probability on every part.

The order of the options moves a probability only near the line, so a file whose first answer falls within 0.15 of its
part's line is asked again in two other orders (the options rotated by a third and by two thirds; one other order for
a profile of two parts) and read on the mean, which the reading says ("the mean of 3 orders of the options"). Each
order is its own question, kept in the cache on its own; offline, a file whose other orders are not all kept is
unanswered. Whether a file needs them is known from the answers kept before anything is sent.

A file judged under 2,000 characters is marked `small`: small files read lower for being small (in trials a tenth of
the smallest quarter of files read as doubtful, a fiftieth of the largest). Every reading ends with the parts read:
for each part a file of which was read, how many were read and how many read as doubtful, with its line. A part with
fewer than 3 files read is said to be too few to say anything of. A part with at least 3 doubtful files, more than a
quarter of those read, gets a note: that usually means its litmus does not describe its files, so read the litmus
(`xarch where` on one of its files) before the files, and only if both are right set the part's own line (below).

**What leaves the machine, and when.** The decision model is TypeSafe's (`https://api.typesafe.ai`), asked as the
model `jev-1.14.0`, pinned. Review sends whenever `TYPESAFE_API_KEY` is set in the environment: **the key alone allows
it**, so a key set for another purpose (a shell profile, a CI secret) starts sending the first time `xarch review` runs
without `--dry-run` or `--offline`. With no key set, a review that would send refuses (exit 2): "no key: set
TYPESAFE_API_KEY, or run --dry-run to see what would be sent, or --offline to use cached answers only". The key is
read without the whitespace around it, and one of whitespace alone is no key; a key holding a character a request
header cannot carry (a line break inside it, a control character, a letter outside ASCII) refuses a review or a
calibration that would send, before anything is sent (exit 2), in a sentence that holds none of it; it blocks no run
that sends nothing: `--dry-run` says the key is set but cannot be used, and why, and `--offline` runs as usual. What is sent
is, for each file judged whose answer is not cached, its masked text (below) and the question; the key travels as the
`Authorization` header only, with `User-Agent: xarch`; a redirect is never followed, so the key goes to that one
place. The key is never printed, logged, cached or written. Nothing
else of the project is sent: no path, no file name, no project name, no git data, no telemetry.

It reads only the files it is given, and refuses (exit 2) when none is: name them as paths (a folder stands for the
source files below it), pipe a list with `--files-from -` (one path per line, such as
`git diff --name-only main | xarch review --files-from -`), or take every file of the app with `--all`
(alone). A path is read as `xarch where` reads one; one outside the project is refused. Of the files found, a source
file of the app in a part, that parses and holds from 800 to 200,000 characters, is judged; every other is listed as
left out, with why (not there, no source file, a test, outside the app folder, excluded, in no part, held back by
`review.never`, does not parse, too small, too large (over 200,000 characters: never sent, `--dry-run` included), a
link to a file outside the app or to no source file). A file reached
through a link, or through a linked folder, is read only when the file it is lies in the app folder once every link is
followed, and is a source file of the app's language. A run judges at most `--max-files` files (50, or 20 with `--pieces`); past
that it refuses, naming how many it chose.

The text a file is judged by is its own, masked: every comment is cut, since it says what its writer thought of the
code, often where it belongs, which the code itself does not; what a comment is, the language's reader says (a `#`
inside a string is none, and a docstring is no comment), and each is cut from its line with the blanks before it, a
line that held only a comment staying as an empty line, so that no line moves. Then the module each import of the
app's own code names (an import named from the importing file's folder, or whose first step is the app's import name)
is replaced by `<masked>` on the lines the import spans, however the source writes it (blanks around its dots, a line
continued), since it would say the part; every e-mail address becomes `person@example.test`; then each text the
profile's `review.mask` hides (below). Nothing else is masked: docstrings and string literals are sent as written, so
a file that must not leave the machine is one not to choose, or one for `review.never`. The same masks apply to
everything review and `review calibrate` send: a file, a piece and the opening lines sent before it, the text an eval
reads, placement's examples and an eval's own, in a run and its dry run alike.

Sizes are counted twice over. Whether a file is judged at all (800 to 200,000 characters, else left out as too small
or too large, with its size) is counted on the file as it is; being marked `small` (under 2,000), how a file is cut
into pieces (a class over 4,000, a piece under 200) and which pieces are judged (1,000 or more) are counted on the
text sent, masked, which is the number of characters a request shows.

`--dry-run` sends nothing and needs no key. It opens with what leaves the machine, to whom, and whether the key is set
now (and when it is set but cannot be used, why), then prints the question once (it is the same for every file), the masks in force, and each file judged with the
exact text it would send (in text, each character a terminal would not show as itself, such as an escape or a form
feed, written as its code, `\x1b`; the JSON holds the text as it is) and how many characters that text holds, marked when its answer is in the cache already (it would not be sent). It ends with the
characters in all and about how many tokens they make (one for every four characters), and how many more requests a
file near its line may cost (its other orders, which a dry run cannot know it will need).

Answers are kept in `.xarch/cache/review/` in the project's root (the folder holding the app folder), one JSON file
per question, named by a hash of the model asked, the masked text and the question; each holds the model version
that answered, the probability of each part and the tokens spent, and no code, no question and no key. Commit the
folder: agents and CI then share the answers without spending calls, and a model upgrade shows as a diff of answers.
An identical question is never sent twice. `--cache DIR` keeps them elsewhere. `--offline` sends nothing, needs no
key, and reads the cache only. An answer kept that does not answer the question (a probability for other options than
its own, probabilities not summing to 1, a count of tokens below 0) is no answer, and the question is asked again. A
cache folder that is a file or a link is refused (exit 2) before anything is sent; an answer kept through a link is
none, and keeping one replaces the link, never writing through it.

**Pieces.** A whole-file reading does not move when one piece inside a good file is misplaced, so `--pieces` also
ranks the pieces of each file chosen, inside that file only. A piece is a function or a class at the top level, as the
language's reader cuts it; a class over 4,000 characters is cut into its methods instead, each sent with the class's
text before its first method; a piece under 200 characters is joined to the next piece of its class (or of the top
level), the last to the one before. Only pieces of 1,000 characters or more are judged (smaller ones read low for being
small), each asked once with placement's question and one more sentence: "This text is one piece of a larger file."
The text output shows the lowest 3 of a file's pieces, ranked, each with its lines and the probability on the part
its file sits in, and what to do: read the first one against the part's litmus. A piece is never called doubtful, has
no line, and is never compared with a piece of another file: in trials about a third of the pieces of good files read
below 0.3. A file with fewer than 2 pieces judged has nothing to rank, and its pieces are not asked. `--all
--pieces` is refused: a sweep over pieces is noise. By default nothing but the piece is sent; `--context imports`
sends the file's opening lines first (those before its first piece: for most files its docstring and imports),
masked. In trials that cut false alarms and missed more misplaced pieces, and it raises every number, so the two are
never compared; the reading says which was used. `--dry-run --pieces` lists each piece's request after the files',
with its name, kind and lines, and the exact text it would send.

Exit codes: 0 when the review ran to the end, whatever it read (doubtful files are not failures); 2 when it refused
before sending anything (no selection, `--all` with paths, `--all --pieces`, `--dry-run` with `--offline`,
`--context` without `--pieces`, over `--max-files`, an app folder that is not there, no key or one that cannot be used, a path outside the project, a profile that cannot be used, a `--files-from` list that is not UTF-8, a
cache folder that cannot keep answers, a record that cannot be read), or when what it got cannot be written; 3 when some file or piece judged has no answer: not cached under `--offline`; refused by the
decision model as that request's own fault (malformed, too large, a field it cannot accept), after which the rest is
still sent; or the decision model failed otherwise (unreachable, a timeout or rate-limited after retries, a key
refused, the service erroring), after which nothing more is sent. What was answered is printed, the rest is listed as
unanswered with why and the decision model's words (for a request refused alone, under it), and the answers already
kept stay kept. `review calibrate` does the same with its examples. When the reader of the output goes early (`| head`), the rest of the output is dropped quietly and the
exit code is still the run's own, for every command. A path written `./calibrate` (or `calibrate/`) is a path to
review, not the word `calibrate`.

### What review may send: `review.never` and `review.mask`

The profile may narrow what review sends, under a top-level `review` key that `check` never acts on: a value written
wrong makes the profile invalid for every command, `check` included, and no finding and no exit code of `check`
depends on what it says. Neither key can switch sending on.

```yaml
review:
  never: [modules/documents/adapters/legal_archive.py, "**/secrets"]
  mask: [Northwind, "DOC-*"]
```

- `never`: paths below the app of the files review never sends, each with its steps written with `/`: a step as
  written, `*` for any text inside one step, and a step that is `**` for any number of folders (none included). A path
  matches a file, or a folder and every file below it, and is matched against a link's own path and the path of the
file it links to. A file chosen that one matches is left out of every run,
  `--dry-run` included, as "held back by review.never (<path>)"; its text goes into no request. So is each of the
  profile's own examples whose path below the app one matches (a file of `docs.examples` or of
  `evals.placement.examples`, and an example of an eval of its own): `review calibrate`, its dry run included, never
  sends it and lists it as held back by review.never, with the path; placement and each eval are then held to the
  examples that remain (a part left with none is measured elsewhere only; an eval left with fewer than 2 flagged or 2
  clean is not held, sends nothing and fails), and what a record is held as is those examples, so a record made
  before an example was held back, or while it was, does not stand once that changes. `--dry-run` lists
  the paths in force, and says of each that matched no file found in that run that it matched nothing: a path of
  `never` is read below the app, so one copied from review's output with the app folder's name first matches nothing.
- `mask`: texts hidden in each file's text before it is sent, after the built-in masks: each as written (case counts),
  `*` standing for a run of one or more letters, digits, `_`, `-` and `.`; each match is sent as `<masked>`.
  `--dry-run` shows the texts masked and lists the patterns in force.

`profile check` lists, as looser, an entry of either that the profile it is compared with holds and this one does not:
it sends more. `xarch profile explain review.never` (or `review.mask`) says each in full.

### A part's line: `evals.placement.lines`

A part whose files read low across the board, even when well placed, can be given its own line by hand (lines are
never computed from a run: a part that reads low usually means its litmus does not describe its files, which a computed
line would hide). Read the part's litmus first.

```yaml
evals:
  placement:
    lines: {domain: 0.2}
```

Each value is a number above 0 and below 1; a part not written keeps 0.3, the line the trials measured. Every reading
says a line set this way as "set by the profile", since the trials' numbers hold at 0.3 only. `check` never acts on
`evals`: a value written wrong makes the profile invalid for every command, `check` included, and no finding and no
exit code of `check` depends on what it says; its enforcement lists a line set lower as looser, for information only. `profile check` lists a part whose line is below the one the profile it is compared with gives it as looser:
it flags less. `xarch profile explain evals.placement.lines` says it in full.

### Parts one file cannot tell apart: `evals.placement.alike`

Some parts differ in something no single file shows: two parts of pure functions, one a module's own and one shared by
several modules, differ only in how many modules use a function. A profile may name such parts as a group, and a file
of one is then read on the sum of the probabilities on the group's parts, against its own part's line.

```yaml
evals:
  placement:
    alike: [[logic, kernel-logic]]
```

The sum decides everything a run does with the number: doubt, asking again near the line, the order of the readings,
the summary of each part, and the ranking of pieces. Each reading says the parts counted with its own ("summed with
kernel-logic (evals.placement.alike)"; `alike` in the JSON, empty when none), and the JSON's `distribution` keeps the
probability on each part as answered. `review calibrate` holds a group to its lines as one: an example's reading on its
own part is the group's sum, an example of one part reading at or above the line of another part of its group crosses
nothing, and its report says of each part of a group that it was held with the others; changing the groups makes the
record of placement stale. Each name must be a part, a group needs two parts or more, each named once, and a part is in
one group at most; the parts of a group must have the same `uses.never`, and the same kinds with the same `immutable`
under `holds`, since parts `check` tells apart by rule are not alike. A group hides every doubt between its parts:
name only parts one file truly cannot tell apart. `xarch profile explain evals.placement.alike` says it in full.

### Parts a file cannot lie in: ruled out by `holds`

The decision model judges a file by what it is about, and a part's rules say what may lie there: a file of plain
functions that validates profile documents reads as the part holding profile values, though that part holds classes
(`parts.<part>.holds: {classes: {}}`) and the file could not lie there without breaking the rule: a file rules a part
out when it defines at the top level a kind that part does not list. So each part whose `holds` the file would break
were it to lie there is ruled out of its answer: the probability on it is dropped, and what
remains is read as summing to 1 again. Whether the file would break a part's `holds` is decided by the very rule `check`
runs in that part, on the file as `check` reads it with the rest of the app (an exception class and a record a
function of the file returns are allowed in a part that lists them, as there; a package file breaks none). The file's own
part is never ruled out (when the file breaks it, `check` says so); a part the answer puts nothing on is left as it is;
and an answer that would leave nothing (its own part at 0, every other part ruled out) is read as it was answered.

What remains decides everything a run does with the number: doubt, asking again near the line, the sum over a group
read alike (taken after), the order of the readings and the summary of each part. Each reading says what was ruled
out, with what the answer put on each, under it in text (`ruled out by holds: profile-values 0.45, domain 0.31`) and
as `ruled_out` in the JSON; `distribution` stays as answered. Read it: a file of functions that ought to be an
invariant on a value of `domain/` still shows that the model read it as `domain`. `review calibrate` reads placement's
examples the same way, each as a small project of the examples (an example whose class derives from a class of no
example is read without it), so that a run and its calibration agree; a record of placement held before review ruled
parts out is stale. Pieces (`--pieces`) are read as answered: a piece is one class or function on its own, which no
`holds` decides. Only `holds` rules parts out; no other rule does. A dry run says so.

### Accepting a doubtful file: `xarch review accept`

A person who has read a doubtful file against its part's litmus and found it fine can accept it:

```
xarch review accept app/modules/documents/application/logic/checks.py --why "one rule over a document, read against the litmus"
xarch review accept --remove app/modules/documents/application/logic/checks.py
```

`accept` sends nothing, ever: it reads each file as an `--offline` review would, from the answers in the cache (the
same `--cache`, and the same default), and refuses (exit 2), naming each file and what to do, when `--why` is missing
or holds whitespace alone; when a file is one review does not judge (in no part, a test, too small, held back by
`review.never`, ...); when its answer is not in the cache ("run `xarch review <file>` first"); and when it does not
read as doubtful (there is nothing to accept). Nothing is recorded unless every file named can be. `--remove` takes the
files named out of the record (a file no longer there included), and refuses one the record does not name.

The record is `.xarch/accepted.json`, beside `calibration.json`: for each file, by its path as review shows it, the part
it lies in, `reads_as` (the part outside its own part's group that its answer, once parts are ruled out, put most on),
`hash` and `why`, the files in the order of their paths, two spaces to a level, so that a diff of it reads; no code,
no absolute path, no key. Commit it. `hash` is the SHA-256 of the text review sends for the file (masked, every
comment cut), normalised so that an edit of comments alone leaves it as it is: the text is cut at each line feed, each
line loses the whitespace at its end (as Python's `str.rstrip` takes it), a line left empty is dropped, and the rest
are joined with a line feed before the hash of their UTF-8 is taken. Cutting a comment keeps its line, empty, so a
comment added, changed or removed changes nothing; docstrings are code here, and change it, as does any other edit
(the indentation of a line included), and so does a change to what `review.mask` hides.

In a run of `review`, a doubtful file the record names in the part it lies in reads as **accepted** while its code
hashes as it did: it is not doubtful (in the file's reading, in the summary of its part and in the totals), and is
listed under its own heading with what it read as then and why (`accepted: {why, reads_as}` in the JSON, null
otherwise). Once its code changed, it is doubtful again and says so: accepted before, changed since, with the old
reason and what it read as then beside the new reading (`accepted_before` in the JSON). An accepted file is still
asked whenever its text is not in the cache, as any file is: that is how a change is seen, and accepting saves no
request. Every run says how many files the record names. A file of the record is **stale** when it is gone, lies in
another part now (or in none), no longer reads as doubtful, or is not judged now; that is judged only for the files
the run found (every file of the app with `--all`), and each is listed with the command that takes it out. `review`
never edits the record itself, and its exit codes are as they were: accepting is advisory too. A record that cannot be
read is refused, naming it, by every review and by `accept`, and is never rewritten while it cannot be read.

### Evals of the profile's own

A profile may write evals of its own under `evals`, each under an id of its own (lowercase words joined by `-`, never
`placement`), as it writes checks: one short question, its answer form, what it is asked of and where, and examples.

```yaml
evals:
  rule-outside-entity:
    ask: Does this method itself decide whether a document may change state, by testing the document's fields?
    answer: yes-no
    yes: "the method tests a document's fields to decide whether the change is allowed"
    no: "the method calls the Document's own method, which decides"
    reads: function
    in: {part: services}
    keep: [public]
    message: "{name} may decide a rule of a document's state itself ({value})"
    fix: "read it against the litmus of domain/; if the condition is the document's invariant, move it onto the entity"
    examples:
      flagged: {modules/documents/application/services/publishing.py: ..., ...}
      clean: {modules/documents/application/services/publishing.py: ..., ...}
```

- `ask`: one line, at most 400 characters and one question mark: one rule about what the text shows.
- `answer`: `yes-no` (read as the probability of yes; `yes` and `no` say what each means, sent with the question);
  `{score: [<level 0>, ..., <level 4>], flagged_from: <1 to 4>}` (five levels, the worst last, read as the expected
  level over 4); or `{choice: {<option>: <description>, ...}, flagged: [<option>, ...]}` (three options or more, read
  as the probability of those flagged, the mean of two orders of the options; two options are refused: write yes-no).
- `reads`: `file`, `class` (each at the top level) or `function` (a method included), as the check vocabulary's kinds;
  `in`: `{part, where}` as a check's (the app's files only); `keep`: filters of the vocabulary, such as `[public]`.
- `line`: the value from which a reading is listed (above 0, below 1); left out, calibration sets it.
- `message`, `fix`: sentences with `{file}`, `{line}`, `{name}` and `{value}`; start `fix` from reading something.
- `examples`: at least 2 flagged and 2 clean files, each a path below the app with its code.

`profile check` refuses every slot written wrong at its address (`evals.<id>.answer.choice: two options are a yes or
no: ...`), a filter of `keep` the vocabulary does not have, and an example file in which the eval reads nothing.
`xarch profile explain evals.<id>.ask` (or `evals.title-rule.ask`, any id; and each other slot) says each in full. The bundled profiles write none.

An eval runs only once it was held to its examples (calibrated), as it is written now, by the model review asks, and
passed. Otherwise review does not run it and says why and what to run: `uncalibrated` (never held), `failed` (with what
crossed) or `stale` (its question, answer, scope, line or examples changed, or another model is asked), each with
`xarch review calibrate --eval <id>`. An eval that runs asks one question of each file, class or function it reads in
the files review judges (never one placement leaves out), its masked text alone, and lists each reading at or above its
line with its message and fix, the highest first. How often it reads well-written code as flagged is not known, and the
reading says so.

### Holding evals to their examples: `xarch review calibrate`

`xarch review calibrate [--eval ID ...]` asks the decision model of each thing each eval reads in each of its example
files (masked as a file of the app, and sent as review sends: whenever the key is set; `--dry-run` shows each request
and sends nothing, `--offline` reads the cache only). The value of an example file is the highest of what the eval
reads in it. An eval passes when every flagged example reads above every clean one, by 0.4 at least on the mean, and on
the right side of its line: the one it writes, else midway between the lowest flagged and the highest clean value,
never below 0.5 (for a score, never below the first level flagged). One that fails is named with what crossed, and
what to do: make it one short rule about what the text shows; add a clean example of the case it must not catch.

The verdicts go to `.xarch/calibration.json` in the project's root: for each eval, a hash of what it was held as, the
model asked and the version that answered, the verdict, the line and the value of each example by path; no code and
no question. Commit it, as the cache, so that agents and CI read the same verdicts. A record that cannot be read (a
merge left its marks in it, say) is refused, naming it, by every review that reads it and by calibrate, and is never
rewritten while it cannot be read: mend it, or remove it to hold every eval again; nor is a record that is a link read
or written. Exit codes: 0 when every eval passed, 1 when one failed (a defect of the profile), 2 when it refused (no
key, an eval it does not write, a profile that cannot be used, a record that cannot be read or written), 3 when an
example has no answer, and nothing of that eval is recorded.

Placement is held to its examples in the same run (and alone with `--eval placement`): every file of `docs.examples`
lying in a part, read as clean, and the profile's own under `evals.placement.examples: {flagged, clean}` (a flagged
file's path puts it in a part it does not belong in; a path lying in no part is refused at its address). Each is asked placement's question once. A part passes when its
clean examples read at or above its line, a flagged one lying in it below it, and every other part's example below its
line on it (from the same answers); one with no example of its own is measured elsewhere only. A part whose examples
disagree is said with the example that crossed, and review then reads its files but never marks them doubtful, listing
them under their own heading (not read against a line), never as read as placed; it says how many parts disagree. The
examples are short, and short files read lower: this is a sanity check of the litmus texts, not a way to set lines,
and a disagreement does not fail the calibration. Review says, under placement, whether it was held to its examples,
and when it was not, what to run.

### JSON

`--format json` prints one document. A dry run: `{"ok", "advisory", "profile", "dry_run": true, "sent": false,
"selection": {"by", "found", "judged", "left_out": [{"file", "why", "chars", "pattern"}]}, "question": {"ask",
"role_only", "options": [{"name", "description"}]}, "requests": [{"file", "part", "chars", "cached", "text", "body",
"piece", "kind", "first", "last", "eval"}], "pieces", "piece_question", "context", "characters", "tokens", "reorders",
"masked", "mask", "never": [{"path", "matched"}], "alike", "ruled_out_by", "evals", "sends": {"name", "at", "model", "key", "keyed", "unusable"}}`: `body` the request as the decision model's service would receive it
(JSON text, formatted: the same JSON value the service receives, not the same bytes; the key left out); `chars` how
many characters the text sent holds, masked; `piece`, `kind`, `first` and `last` the piece a request is about and the lines it spans
(null for a whole file); `pieces` whether pieces are asked, `piece_question` the question each piece carries (null
without `--pieces`) and `context` `none` or `imports`; `reorders` how many other orders a file near its line is asked
again in; `sends.key` the name of the variable the key is read from (never the key), `keyed` whether it is set, and
`unusable` why the key set cannot be used (null when it can, or none is set).

A review: `{"ok", "advisory", "profile", "dry_run": false, "complete", "model", "answered_by", "selection", "placement":
{"calibration": {"state", "evidence", "examples": {"state", "why", "parts": [{"part", "verdict", "crossed",
"examples"}]}}, "role_only", "files": [{"file", "part", "probability", "line", "line_by_hand", "doubtful", "chars",
"small", "orders", "model", "alike", "distribution", "ruled_out": [{"part", "by", "probability"}], "accepted":
{"why", "reads_as"}, "accepted_before": {"why", "reads_as"}}], "accepted": {"recorded", "stale": [{"file", "part",
"why", "now"}]}, "parts": [{"part", "read", "doubtful", "line", "line_by_hand",
"summed", "litmus_note", "examples"}]}, "pieces": [{"file", "part", "judged", "too_small", "context", "answered", "alike", "lowest":
[{"rank", "kind", "name", "first", "last", "chars", "probability", "distribution"}]}], "evals": [{"id", "state", "why",
"run", "line", "ask", "form", "examples": {"flagged", "clean"}, "model", "asked", "readings": [{"file", "line", "name",
"value", "message", "fix"}]}], "sends", "sent": {"calls", "cached", "input_tokens", "output_tokens"}, "unanswered":
[{"file", "why", "piece", "eval", "said"}], "failure"}`: `answered_by` the model versions that gave the answers read, asked
or kept, each once (the text header names them when they are not the model asked alone); the files
ranked from the lowest probability; `line_by_hand` whether the profile sets the part's line; `small` whether the file
is under 2,000 characters; `orders` how many orders of the options it was asked in (`probability` and `distribution`
are their mean); `alike` the other parts of the group of the file's part, whose probabilities `probability` counts
with its own (empty when its part is in no group; also for a file's pieces), and of a dry run each group;
`distribution` the probability on each part by name, as answered (also for a piece); `ruled_out` each part ruled out
of the file's answer, `by` the rule that rules it out (`holds`) and `probability` what the answer put on it (empty
when none), `probability` being read on what remains; a dry run's `ruled_out_by` the rules that rule parts out;
`accepted` of a file what was said when it was accepted, its code as it was then (null otherwise), `accepted_before`
the same once its code changed since; `accepted` of placement how many files `.xarch/accepted.json` names
(`recorded`, also `accepted` of a dry run) and each stale, `why` `gone`, `moved`, `not-doubtful` or `not-judged`, `now`
the part a moved file lies in now (null for none) or why a file is not judged; `parts` each part read, `summed` whether 3 or more of its files were read and `litmus_note` whether the note
on its litmus applies; `pieces` each file's lowest 3 pieces (empty when fewer than 2 were judged, or when `answered`
is false); `why` of an unanswered file or piece `not-cached`, `failed` or `refused` (that request alone), `piece` its name
(null for a whole file), `said` the decision model's words of a request it refused alone (else null);
`failure` the decision model's words when it failed (else null); `examples` of placement's calibration `calibrated`,
`uncalibrated` or `stale`, each part's `verdict` `passed`, `disagree` or `elsewhere` (also a part's `examples` in
`parts`, null when placement is not calibrated); each eval's `state` `calibrated`, `uncalibrated`, `failed` or
`stale`, `run` the command that holds it to its examples (null when it ran), `form` `yes-no`, `score` or `choice`,
`asked` how many things it was asked of, `readings` those at or above its `line`; `eval` of a request or of an
unanswered question the eval that asks it (null for placement). In both, `why` of a file left out is one of
`missing`, `not-source`, `test`, `outside`, `excluded`, `unplaced`, `never`, `unparsable`, `small`, `large`, `link`,
`pattern` the
`review.never` path that matched (null for any other `why`); a dry run's `masked` is what review always masks
(`own-imports`, `e-mail`, `comments`) and its `mask` the profile's `review.mask`. A
refusal is `{"ok": false, "error"}`.

A calibration: `{"ok", "calibrated": [{"id", "complete", "passed", "line", "line_by_hand", "crossed", "too_few",
"examples": [{"path", "flagged", "value"}]}], "placement": {"model", "answered_by", "parts": [{"part", "verdict",
"crossed", "examples", "alike"}]}, "passed", "complete", "record", "model", "answered_by", "sends", "sent", "unanswered": [{"id",
"file", "kind", "why", "name", "said"}], "held_back": [{"id", "kind", "example", "pattern"}],
"failure"}` (`placement` null when it was not held); its dry run: `{"ok", "dry_run": true, "sent": false, "evals",
"requests": [{"id", "example", "kind", "part", "name", "first", "last", "chars", "cached", "text", "body"}],
"characters", "tokens", "masked", "mask", "alike", "ruled_out_by", "held_back", "too_few": [{"id", "kind"}], "sends"}`, `kind` `flagged` or `clean`;
`alike` of a part the other parts of its group, held with it as one, and of a dry run each group placement would hold;
`ruled_out_by` of a dry run the rules that rule parts out of each answer of placement's examples (empty when placement
is not held);
`held_back` each example `review.never` holds back (`id` its eval, `placement` for placement's, `pattern` the path that
matched); `too_few` each eval left with too few examples of a kind to be held, and `too_few` of a calibrated eval
whether it is one.

An acceptance: `{"ok", "experimental", "accepted": [{"file", "part", "reads_as"}], "why", "record"}`; a removal:
`{"ok", "experimental", "removed", "record"}`; a refusal of either, `{"ok": false, "error"}`.

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

`AGENTS.md` (beside the app folder, about 60 lines) is written for a coding agent that has never seen xarch: what governs
the project (the profile); that it works from `xarch where <path>`, the `fix:` lines of `check` and the Placement
order (section 7 of `docs/project/architecture.md`, about 15 lines), the two project docs (about 20k tokens) being
reference, not required reading; to run `xarch where <path>` before creating or moving a file and to take the first
litmus test a piece of code passes; to run `xarch check --strict` (what the guard test runs, so a weak finding fails
it too) and `ruff check` before finishing; how tests are written; how to run `xarch review` as a second, advisory reading (with no key set it refuses: skip it, or run it with
`--offline` when the project commits its answer cache; `xarch review calibrate` is the maintainer's), and what not to
do to get a green check: move code into a folder no part covers, switch a guard off or loosen the profile, edit the
guard test, skip a test. It is static text (it names the app folder with `{{app}}`).

`ruff.toml` holds only the linter rules that are the same for every file: pyflakes and pycodestyle errors, import
sorting, absolute imports only, a return annotation on public functions (which `stand-ins` needs on a port's methods),
the pytest-style rules, no `print`, no naive datetime and no unused `noqa`, for Python 3.13 and a line length of 140.
What differs by part (which imports, names or outside packages a part may use) is the profile's job, via
`imports.may`, `imports.libraries` and `uses.never`; `xarch check` does not run the linter.

The guard test, `tests/architecture/test_rules.py`, runs `python -m xarch check --strict --app <project>/<app>` with
the interpreter running the test, and fails with `xarch check`'s output as its message, so every guard runs with the
project's test suite; xarch must be installed in that environment. It passes `--strict` because a project `init` and
`new` have just written, of either bundled profile, has no finding `--strict` fails on: a weak finding (a method that
only forwards, a class where the part holds functions, a file no test reaches) therefore fails the build as soon as it
appears, rather than piling up as advice nobody acts on, and `AGENTS.md` tells an agent to run the same command.
Editing the pinned guard test (to drop `--strict`, say) is itself reported as changed. It is also the guard tier's
example in `testing.md`.

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

`architecture.yaml` also has example files of its own, one or two per part, in `docs/examples/` (outside the package,
so not in the wheel, and outside the app folder, so `check` does not read them as xarch's source; they are linted as
the rest of the repository is): short files in xarch's own vocabulary that its `docs.examples` names, so that
`xarch review calibrate` holds the placement eval to xarch's own parts. Its `evals.placement.alike` names two pairs,
`logic` with `kernel-logic` and `domain` with `profile-values`: each pair differs only in how many modules use a file,
which `check` decides (`shared`) and one file does not show. xarch's own
architecture page, generated from it and `docs/templates/`, is `docs/xarch/architecture.md` (and `docs/xarch/testing.md`).
