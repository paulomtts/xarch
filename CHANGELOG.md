# Changelog

All notable changes to this project are written here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- The match of a custom profile with the bundled one it is compared with: the share of what `check` reads under
  either profile (each part, each key a part, a tier or the profile writes, each setting of a kind of `holds` on its
  own, each guard switched on, each check of the profile's own of an id both write) that has a counterpart in the
  other. A match below 75% is low and says why. It is printed on every run that compares: `profile check` says
  `match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, ...`, the parts and tiers only one profile has,
  the parts of the same name at another path, and the bundled profile that matches higher than the one `based_on`
  names; `check`'s enforcement section names the match on its `profile:` line, `(custom; compared with cli, based_on;
  match 80%)`, with a `match:` line under it when it is low. `compared_with` in the JSON of both gains `chosen_by`,
  `match`, `low`, `counts`, `only_here`, `only_there`, `elsewhere` and `higher`.
- `--against NAME|FILE` on `check` and `profile check`: for that run, the profile in force is compared with the one it
  names, a bundled name or a path to a profile file read from the working folder, instead of the one its `based_on`
  names or the bundled one of highest match, and a bundled profile, its own baseline without the flag, is compared
  too. `profile check` heads it `(custom; against web, given with --against; based_on: cli)` and says `match: 73% with
  web (--against): ...`; `check`'s `profile:` line says `(custom; compared with web, --against; match 73%)`; the JSON
  of both says `"chosen_by": "against"` in `compared_with`. A value that does not load refuses the run (exit 2,
  `--against does not load: ...`), and `--strict` with `--against` is refused (exit 2), since `--strict` judges the
  profile against its baseline.
- `based_on` takes the path of a profile file, read from the folder of the file that writes it (`based_on:
  ../team.yaml`): `profile check` and `check` compare the profile with that file, as written, and follow its own
  `based_on` in turn. A file of the chain that does not load refuses the profile (exit 2, `sub/mine.yaml: based_on:
  ../team.yaml does not load: ...`), and so does a chain that comes back to a file of it (`mine.yaml: based_on: a.yaml
  is based on this profile`). `--strict` rests on a bundled profile, the anchor: the bundled profile the chain ends on,
  else the one closest to its last file, else none. A guard left off is excused only when the anchor and every file of
  the chain leave it off too, and a part fails `litmus` when it lacks a litmus the path file or the anchor gives the
  part it pairs with, so a file of one's own never loosens `--strict`. `profile check` heads it `(custom; based_on:
  ../team.yaml, resting on cli)`, `check`'s `profile:` line says `(custom; compared with ../team.yaml, based_on; match
  92%; --strict rests on cli)`, and `compared_with` gains `anchor` in the JSON of both.
- The kinds `records` and `exceptions` of `holds`, narrower than `classes`: a record (`class.record`) or an exception
  may be defined at the top level of a part that lists the kind, `records` with the settings `names` and `immutable`,
  `exceptions` with `names`; `functions` takes `names` (`holds.functions.names`), which every public top-level
  function, in no class, matches. A class is held to the settings of the narrowest kind listed that it fits, in the
  order exceptions, records, classes, and to no other's: beside `exceptions: {names: "*Error"}`, an exception is named
  `*Error` and not by `classes.names`, and is not held to `classes.built_by`. `records: {}` or `exceptions: {}` beside
  `classes`, which already allows them, is refused (`says nothing beside classes ...: give it a setting, or drop it`).
- A part's `holds` reads `function.top_level` only when the language supplies it: in a language that does not, a part
  that does not list `functions` reads no functions, which `xarch profile explain parts.holds` and the enforcement
  section of `check` (an `approximate` item at `parts.<part>.holds`) say: `holds reads no top-level functions: the
  language <title> does not supply function.top_level`. A part listing `functions` or `records` there is refused with
  the needs text at `parts.<part>.holds.functions` or `.records`.

- The fact `function.top_level`, whether a function is defined at the top level of its file, in no class, which
  `parts.<part>.holds`, `guards.dead-code.tests_only` and a check of your own or an eval whose filter reads
  `top-level` (negated or not) need; a language that does not supply it is refused them with the needs text. Python
  supplies it exactly.
- The fact `class.record`, whether a class is a record, as the language writes one, which `parts.<part>.holds` and a
  check of your own whose filter is `record` need, in place of `class.methods` and `function.returns`; a language
  that does not supply it is refused them with the needs text. The reader says it of each class (`Class.record`),
  handed the language's `special`, and the checks no longer work it out. Python supplies it, computed as before: a
  class whose methods are all special that a top-level function of its file names in its return annotation.
- The fact `public`, whether a name a file defines, or takes by an import, is for other files to use, as the language
  decides it, which `parts.<part>.holds`, `parts.<part>.names`, `parts.<part>.shared`, `guards.private-imports`,
  `guards.dead-code.tests_only`, `guards.dead-code.known` and `guards.no-twins` (with `min_renamed` and `translated`)
  need; a language that does not supply it is refused those keys with the needs text. The reader says it of each
  class, function, constant and name an import takes (`Class.public`, `Function.public`, `Constant.public`, and
  `Import.withheld`, the names an import takes that are not public), handed the language's `private` to decide it.
  Python supplies it, computed from `private` as before.
- The fact `comment.doc`, whether a comment is a doc comment, which `guards.no-comments` needs beside `comment`. The
  reader says of each comment the marker it opens with and whether it is a doc comment (`Comment.marker` and
  `Comment.doc`), and a check of your own reads the doc ones with the filter `doc`. Python supplies it: no Python
  comment is a doc comment.
- The fact `file.package`, that a file stands for the folder holding it, which a language supplies exactly when its
  data file gives `package_files` and which is never written under `supplies` (`supplies: file.package follows
  package_files: drop it from supplies`). `parts.<part>.package_only`, a part's `imports.must` and
  `guards.dead-code.untested` need it, and so does a check of your own whose filter `package-file` (or
  `target-inside-part`) is written as is; `not package-file` needs nothing. Python supplies it.
- A list of `never` may include another: an entry that is exactly the name of another list of the block puts that
  list's names in its place, in order, however deep, the list written above or below, as in
  `published: [pure, typing.Any]`. The bundled profiles and xarch's own now write `published` that way, with no
  part's names changed. Refused at the list: one that includes itself (`includes itself`, or `includes itself,
  through never.<list>: drop one of the two`), one that reaches a list twice (`includes never.<list> twice`), one
  that reaches a name twice (`'<name>' is listed in never.<list>, which never.<list> includes: drop it here`), and
  one named like a package of the standard library or one the profile names (`a list may not take the name of a
  package ...: rename it`). A part naming a list of lists is told `a list may include others`.
- `profile check` lists a `types_only` mark dropped from an entry of a part's `imports.may`, whose target the part
  still may import and no mark of the part covers, under the key `imports.may.types_only`: `<part> may now call
  <target>, which it used only as a type (parts.<part>.imports.may.types_only)`.
- A test framework that writes no table form (`testing.tables: []`, or `tables` left out) can switch on
  `guards.scenario-coverage`: every variant of a use case's union must then be named by a test of its test file
  (`<Union> variant <V> is named by no test`), and a variant named only by tests that never assert is weak. The
  guard's `columns` is refused for such a framework (`drop \`columns\`: the framework writes no table, so each result
  is its own test`), and `tiers.<tier>.plain_tables` says `needs a table form: the framework <framework> writes none
  in \`testing.tables\``.
- The table forms are proved neutral to a language by tests alone: a test-only framework (a loop form and a call form
  with literal rows) is loaded under a test-only TypeScript-like language and checked on hand-built facts, each finding
  worded from that language's `writing`. Behaviour is unchanged.
- A framework declares its tests with `testing.declared`, a list of forms, each a `function` form, a function whose
  name matches a pattern (`declared: [{function: "test_*"}]`), or a `call` form, a call of one of its callees whose
  arguments hold the test's `title` and its `body` (`{call: [it, test], title: {position: 0}, body: {position: 1}}`);
  an entry's problem names it by its index (`testing.declared.0.call`). `testing.globals` lists the names the framework
  binds without an import (`[it, expect]`): a use or a call of one that the file does not bind is read as that name,
  never as a builtin. The reader turns the forms into the tests of a file (`SourceFile.tests`, each a `Test` with its
  line, its name, the index of its form, whether the name is a title, and its body), and scenario-coverage,
  `plain_tables` and `weak` read those alone. Two facts come with it: `test.function`, which Python supplies, and
  `test.call`, which no reader supplies yet, so a call form under Python is refused at its entry; the call form is
  proved on hand-built facts. A test declared by a title is named in double quotes (`"places an order" has an \`if\`
  in its body`), one declared by its function by its bare name, as before.
- `testing` may name its preset as a map, `testing: {preset: pytest}`, which means `testing: pytest`: the framework
  comes wholly from the preset. A framework key written beside `preset` is refused, never merged (`testing.files: the
  preset pytest gives files: drop it, or drop preset and write the whole map`, or `the preset pytest writes no
  globals` for a key the preset does not hold); a `preset` that names no preset is refused at `testing.preset`, and a
  preset may not name a preset. `xarch profile explain testing.preset` explains it, and the "use ..." list of
  `testing` gains `preset`.
- `testing.beside`: `testing: {preset: pytest, beside: true}` (or `beside: true` in the whole map) keeps every test
  of a part beside the code it tests. A file of the app whose name `testing.files` matches is then a test of the tier
  its part names, read with the framework's forms and never as code of its part; a finding on it names its app path.
  A tier with a `folder` keeps its tests below the tests root, and a part that names such a tier in `tests` is refused
  (`tiers.guard: parts.domain says tests: guard, and guard keeps its tests in tests/architecture: under
  testing.beside a part's tests sit beside its code; give the part a tier with no folder`). `test-tree` reports a test
  file left below the tests root outside every tier `folder` and the fakes' folder (`lies below the tests folder, but
  testing.beside keeps the tests of a part beside its code: move it beside the code it tests`), in place of the
  folder check of the mirrored tree. A test beside the code with no tier says `lies in no tier: its part is untested`
  or `lies in no part`. A preset may not say `beside`; `profile check` lists `testing.beside` as looser; `xarch
  profile explain testing.beside` explains it, and the "use ..." list of `testing` gains `beside`.
- A table `call` form's callees must each be listed under a `call` form of `testing.declared`, for a framework written
  out or named as a preset: one that is not is refused at its entry (`` testing.tables.0.call: `it.each` declares no
  test: list it under a `call` form of `testing.declared` ``), unless the language's reader is known not to read that
  form, which refuses the entry already. `xarch profile explain testing.tables.call` says so.

### Changed

- `testing.functions` is replaced by `testing.declared`: a profile or a preset writing it is refused with `unknown key
  'functions': moved in 0.3.0: write declared: [{function: "<pattern>"}]`. The bundled `pytest` preset writes
  `declared: [{function: "test_*"}]`; the same functions are tests as before, and findings and docs read as before.
- A framework says how a table of cases is written with `testing.tables`, a list of table forms, each with one of
  `decorator`, `call` or `loop` and the slots `columns_from`, `rows`, `row` and `id`; an entry's problem names it by
  its index, `testing.tables.0.id`. `testing.table` is refused with "moved in 0.3.0: write tables, a list of forms
  (xarch profile explain testing.tables)", and the bundled `pytest` preset writes its one form in the new shape. The
  guard `scenario-coverage` keeps no copy of the table: it reads the framework's forms. A language data file says how
  a row is written with `writing: {call, keyword, field}`; Python writes `call` and `keyword`. Findings and docs read
  as before.
- The guard `scenario-coverage`'s `file` writes the case of the use case's name: `{name:snake}`, `{name:kebab}`,
  `{name:camel}` or `{name:pascal}`, so `{name:kebab}.test.ts` looks for `http-check.test.ts`. The words are split as
  before (HTTPCheck is http, check). A bare `{name}` is refused with "write {name:snake} for what {name} meant". The
  bundled profiles write `test_{name:snake}.py`.
- The fact `function.tables` is now three facts, one per form a table is written in: `function.tables.decorator`,
  `function.tables.call` and `function.tables.loop`. Each holder of an entry of `testing.tables` needs its own fact,
  and is refused at its index when the language does not supply it (`testing.tables.0.call: its check reads
  function.tables.call ...`). Python supplies `function.tables.decorator` and `function.tables.loop`, and not
  `call`. A language data file that writes `function.tables` under `supplies` is refused as an unknown fact.
- Python's reader reads a table from the first `for` of a test's own body over a list literal of the file (`for
  given, when, then in CASES:`), its columns the names the loop binds. Its rows are calls of the form's `row` with a
  keyword id, or tuple or list literals with an id at a position. That `for` is not reported as a branch by
  scenario-coverage or `plain_tables`.
- Without `based_on`, a custom profile is compared with the bundled profile of highest match (the first by name on a
  tie, and one no part pairs with never), no longer the one sharing the most part names. Parts pair by name, then by
  layout path, and tiers by name, then by subject, and the ways a profile is looser are compared on the parts and
  tiers that pair, so a part renamed in place is still compared, under its own name. `profile check` heads a profile
  `custom; based_on: cli` or `custom; closest bundled: cli, match 80%`.
- `check --format json`: `enforcement.profile.closest` is now `enforcement.profile.compared_with`, the same object as
  `profile check`'s `compared_with` (`null` when nothing is compared).
- The looser lines cover every loosening of 0.3.0: `profile check` and `check`'s enforcement section now also list a
  kind a part's `holds` allows that the other's does not (`holds`), a setting of a kind dropped or widened
  (`holds.classes.names`, `holds.classes.immutable`, `holds.classes.built_by`, `holds.functions.names`,
  `holds.records.names`, `holds.records.immutable`, `holds.exceptions.names`), a part's `shared` dropped or lowered
  (`shared`), a tier's `imports.must` dropped or a part added to it (`tiers.imports.must`), a tier no longer
  `plain_tables` (`plain_tables`), and `testing.beside` set where the other leaves it out (`testing.beside`), each by
  a sentence ending in its address, such as
  `the classes of service may also be named * (parts.service.holds.classes.names)`. Each is information, like the
  others: `--strict` still fails only on a missing `litmus`.
- A part's `may_import`, `must_import` and `libraries` move into one group, `imports: {may, must, libraries}`, with
  the same meaning: `may` what the part may import besides itself (or `everything`), `must` the targets each of its
  files imports one of, each an entry of `may`, `libraries` its outside packages. A part's `types_only` becomes a mark
  on its entry of `imports.may`, `{<target>: types_only}`, such as `may: [ports, {contract: types_only}]`, read on what
  the entry reaches (its part, instance and path; a name pattern narrows only what may be imported), not on the part
  in any instance. Findings name the new addresses (`parts.<part>.imports.may`,
  `.imports.must`, `.imports.libraries`, `.imports.may.types_only`), and so do `profile explain` and the `Loosened`
  keys of `profile check` (`imports.may`, `imports.libraries`, `imports.must`). The old keys are refused with the form
  that replaces them (`unknown key 'may_import': moved in 0.3.0: write imports: {may: [...]}`, and the same for
  `must_import`, `libraries` and `types_only`); `profile explain parts.may_import` says the same. Rule ids and `where`'s
  JSON fields do not change.
- A tier's `may_import`, `may_also_import`, `must_import` and `types_only` move into one group, `imports: {may, also,
  must, types_only}`, with the same meaning: `may` what the tests in the tier's `folder` may import (only for a tier
  with a `folder`), `also` what its tests may import besides what the part they mirror may, `must` the parts one of
  which each of its test files reaches, `types_only` the parts its tests may import only as types. Findings name the
  new addresses (`tiers.<tier>.imports.types_only`, `tiers.<tier>.imports.must`, and `tiers.<tier>.imports.also` beside
  `tiers`), and so do `profile explain` and the `Loosened` keys of `profile check` (`imports.types_only`,
  `imports.also`). The old keys are refused with the form that replaces them (`unknown key 'may_also_import': moved in
  0.3.0: write imports: {also: [...]}`, and the same for `may_import`, `must_import` and `types_only`); `profile
  explain tiers.may_import` says the same. Rule ids and `where`'s JSON fields do not change.
- `holds` is a map of kinds, `{classes, functions, records, exceptions}`, each `{}` or its settings: a kind listed may
  exist at the top level of a file of the part, one not listed may not, and no `holds` allows every kind. `names`,
  `immutable` and `built_by` leave the part for the kinds: `holds: {classes: {names: "*Service", built_by:
  [bootstrap]}}`, `holds: {functions: {}, records: {immutable: true}, exceptions: {}}`. `holds: classes` is
  `holds: {classes: {}}` and `holds: functions` is `holds: {functions: {}, records: {}, exceptions: {}}`; written as
  one word, `holds` is refused with that map (`parts.<part>.holds: 'functions': holds as one word was removed in
  0.3.0: write holds: {functions: {}, records: {}, exceptions: {}}, which allows what holds: functions allowed`), and
  so are the flat keys on a part (`unknown key 'names': moved in 0.3.0: write it under the kind it names, such as
  holds: {classes: {names: "*Service"}}`, and the like for `immutable` and `built_by`) and a setting under a kind that
  does not take it (`unknown key 'immutable': a setting of classes and records`), which `xarch profile explain
  <old address>` also gives. Every bundled profile, xarch's own and the corpora profiles write the map.
- Findings name the nested keys: `(parts.<part>.holds.classes.names)`, `(parts.<part>.holds.classes.built_by)`,
  `(parts.<part>.holds.records.immutable)` and the like, in place of `(parts.<part>.names)`, `(parts.<part>.built_by)`
  and `(parts.<part>.immutable)`; `xarch profile explain parts.holds.classes.names --rule` gives the rules. A class in
  a part of functions, records and exceptions is said to be where the part `holds functions, records and exceptions`;
  a definition a part does not allow is said as the narrowest kind it fits (`is a function at the top level`, `is a
  class`, `is a record`, `is an exception`).
- In a part of functions, `immutable` (now under `records`) reads its records only, and `names` its records and
  exceptions, so a plain class there, already listed by `holds`, is no longer listed a second time; the generated
  docs' `immutable` line says "every record of" those parts. `review` rules out the same parts for every file of a
  bundled profile as before; a part is named once whichever of its rules a file breaks.
- `evals.placement.alike` compares the kinds `holds` lists and the `immutable` of each, in place of `holds` and
  `immutable` as part keys: the refusal says `write the same uses.never, and list the same kinds with the same
  immutable under holds, for each, or drop the group`.

- A profile's keys are held to the facts their checks read at any depth, in every scope a key opens and in each
  entry of a list (addressed by its index from 0, as `<list>.0.<key>`), by one walk of the key table in place of a
  walk of the file's scopes one by one; a key written with no value configures nothing, as one set to `false` does.
  The refusals of a profile with several keys short of facts are now listed in the order the key table lists the
  keys, each key before those of the scope it opens.
- `no_callbacks` on a part is now the guard `no-callbacks: {parts: [<part>, ...]}`, which lists the parts whose
  functions call none of their parameters annotated as callables, as `pass-through` lists its parts; it reads the same
  code and still fails `check`. A part writing `no_callbacks` is refused at load: `parts.<part>: unknown key
  'no_callbacks': moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}`. Its findings name
  `(guards.no-callbacks)` in place of `(parts.<part>.no_callbacks)`, `guards off` lists `no-callbacks` for a profile
  that leaves it out, and its line in the generated docs sits among the guard lines, after `pass-through`'s in the
  bundled profiles, which write `no-callbacks: {parts: [domain, logic]}`.
- An eval of your own is now held to the facts it reads, as a check of your own is: one that reads a fact the
  language's reader does not supply is refused at its address, `evals.<name>: needs <fact> (<what it is>), which the
  reader of <language> does not supply: read another kind of fact, or drop the eval`, in `xarch profile check` and
  when its facts are kept, and its examples are not read.
- A language's data file writes what makes a class an immutable record as marks, each a map of one of four forms,
  as interface marks are: `{base: <outside name>}`, `{decorator: <outside name>, keywords: {<name>: <value>}}`
  (keywords left out: the decorator however it is written), `{fields: <word>}` or `{type: <outside name>}`. Python
  writes `[{base: typing.NamedTuple}, {decorator: dataclasses.dataclass, keywords: {frozen: "True"}}]`, and its reader
  reads the first two forms. The string form is no longer read. Refused, once for the key: `immutable: each mark is
  {base}, {decorator, keywords}, {fields} or {type}`. No finding of a Python app changes.
- The filter `public` reads the fact `public`, never how a name is spelled, and applies to `class`, `function` and
  `imported-name` only: written on another kind in a check of your own, `profile check` refuses it (`public does not
  apply to <kind>`). `CheckedLanguage.is_public` is gone. Under a language that gives no `private`, the docs line of
  `private-imports` says "a name another file of them keeps private". No finding of a Python app changes.
- A language's data file says how its comments are written as a list of forms: `comment` became `comments`, each
  form `{line: <marker>}`, `{block: [<open>, <close>]}` or `{doc: [<open>, <close>]}` (a doc form's closing may be
  `""`, the end of its line; `[{line: "#"}]` for Python); left out, the language has none. `%comment%` is the first
  line form's marker, else the first block form's opening. A directive and an encoding declaration are matched after
  the marker of the comment, whatever its form, and `no-comments` keeps doc comments. The old key is an unknown key.
  Refused: `comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}` and
  `comments: needs one form at least`. No finding of a Python app changes.
- A language's data file says the endings of a source file as a list and its package files as an optional list:
  `extension` and `package_file` became `extensions` (`[.py]` for Python, the first the one messages print) and
  `package_files` (`[__init__.py]`), each package file ending in one of the extensions; a language may have none.
  Every check decides what a source file is by all its endings, and `testing.files` takes a pattern of any of them.
  The old keys are unknown keys. Refused: `extensions: must be a non-empty list of endings, each starting with a
  dot`, `package_files: must be a list of file names, each ending in one of extensions`, and
  `package_files: '<item>' ends in none of extensions`. No finding of a Python app changes.
- A language's data file says its standard library as data, or where it is known from: `standard` is `interpreter`
  (the Python running xarch, as before) or a map of three lists, `{modules: [...], reserved: [...], builtins: [...]}`,
  the top-level modules of its standard library, its reserved words and its builtins, each module checked with the
  file's `package` pattern and each other item with its `name` pattern. The reader is handed the standard modules
  from the language instead of asking the interpreter itself, so the set a profile is checked with and the set an
  import is marked by are one. Refused: `standard: must be interpreter, or a map of modules, reserved and builtins,
  each a list of names`, `standard.modules: '<item>' is not a package name the language allows`, and
  `standard.reserved: '<item>' is not a name the language allows` (`standard.builtins` the same). No finding of a
  Python app changes.
- The language's data file says as data what makes a class a port: `interface` is a list of marks, each
  `{base: <outside name>}`, a name among a class's bases (`{base: typing.Protocol}`), or `{keyword: <word>}`, a keyword
  a declaration carries; `nothing` is the list of return annotations that give no value (`nothing: [None]`); `special`
  is a regular expression a special name matches in full (`'(?=__)\w*(?<=__)'` for Python); and a file may say
  `unannotated: nothing`, that a method with no return annotation gives no value. The reader marks a class an
  interface, and the stand-ins, the dead-code ports, the `interface` filter and no-twins read that mark instead of
  comparing bases. The keys that read ports (`fakes`, `guards.stand-ins`, `guards.dead-code`) need the new fact
  `class.interface`, which Python supplies `exact`. Refused: `interface: each mark is {base: <outside name>} or
  {keyword: <word>}` (the old list of names among them), `nothing: must be a list of return annotations`,
  `special: must be a regular expression`, and `unannotated: must be nothing`. No finding of a Python app changes.
- The two archived corpora's profiles (`7cc6111`, `df537ca`) are plain yaml files beside their archives in
  `tests/bootstrap/corpora/`, so a change of format edits them as files; the recorded findings are unchanged.

- A key, a guard or a rule id that xarch has retired is refused with a fixed hint naming what to write instead, one
  problem per retired name ahead of the keys that are only unknown, read from one table that
  `xarch profile explain <old key>` also answers from (the hint in its error, `retired` in its JSON, `null` for an
  address with no entry).

- The part key `tier` is renamed `tests`: a part writes `tests: <tier>` or `untested: <reason>`. A profile still
  writing `tier` on a part is refused with "renamed in 0.3.0: write tests", which `xarch profile explain parts.tier`
  also gives, and a value of `tests` holding a `/` is told it names a tier of `tiers`, not a folder. Nothing else a
  profile writes or xarch reports changes.

- The part key `forbidden` is now `uses: {never: <list>}`, the top-level block `forbidden` is `never`, and a tier's
  `apply_forbidden: true` is `uses: {apply_never: true}`. The rule id is `never-use`, in findings, in JSON and under
  `hints`, and a finding's message ends with the new key, such as `(parts.domain.uses.never)`; `where` prints
  `never uses:` and its JSON field is `never_uses`; the `Loosened` keys are `uses.never` and `uses.apply_never`. Each
  old name is refused with its new form, which `xarch profile explain <old address>` also gives, and `never:` on a
  part or `apply_never:` on a tier is told it is a key of `uses`. Finding and fix texts are otherwise unchanged.

- The rule id `rules` is renamed `may-import`, in findings, in JSON and under `hints`. A profile writing `hints.rules`
  is refused with "renamed in 0.3.0: write may-import", and a check of the profile's own may now take the id `rules`.
  On a line with findings of both, the `may-import` findings now come before the `package-only` ones. Finding and fix
  texts are unchanged.

- Internal names follow the 0.3.0 key names: the fields and functions that read `uses.never` and `uses.apply_never`
  say `uses_never`, `apply_never` and `never_lists` in place of `forbidden`; no output changes.

- The Python reader follows relative imports to the place they name: `from .order import Order` in
  `app/domain/services.py` binds `app.domain.order.Order`, as `from app.domain.order import Order` does, so
  `uses.never`, `built_by`, `types_only`, `shared`, the mocks, `stand-ins` and the twins' translation read names
  imported relatively as they read absolute ones; a name of the app that a `uses.never` list names is found at its use,
  since a relative import's line does not name it in full. An import it cannot follow (one that climbs above the root,
  or names no file or folder below it) is marked unresolved and binds nothing. Python has no alias map, so the reader
  reads no config for aliases. The keys that read those names need the new fact `import.resolved`, which Python
  supplies `exact`; a language that does not supply it is refused on them with the existing message. A project with no
  relative import sees no change.
- A new enforcement section, `unresolved`, lists each import the reader could not follow by file and line with the
  module as written, in text (`unresolved:  app/domain/services.py:3: import ".ordr" names no file of the app`) and
  under the JSON key `unresolved` (`{"file", "line", "written"}`), and `--strict` fails on each, as on a dynamic
  import (`strict_failures` key `unresolved`). A project with no such import sees only the empty JSON key
  `"unresolved": []`.

- A language's data file gives `package`, what an import names from outside the app as one step, and `member`, the
  text that joins a package to a name in it (`.` for Python), beside `name`: the three are given together or not at
  all. The outside names a profile writes (`libraries`, `reserved`, the `never` lists, `testing.skips`,
  `testing.mocks.calls` and `autospec`, `testing.table.decorator` and `row`, a check's `path` target) and the data
  file's `interface`, `dynamic` and `immutable` are read by them; no Python profile entry changes. The refusals say
  so: `'<entry>' is not a package name the language Python allows` under `libraries` and `reserved`;
  `'<value>' is not an outside name such as <package>.<name>` under the testing names; and under a `never` list
  `'<entry>' is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()` and
  `'<entry>' is neither an outside name nor a method: write <entry>() for a method called on anything`.

## [0.2.0] - 2026-11-18

### Added

- `evals.placement.alike`: a profile may name groups of parts that one file cannot tell apart, such as
  `[[logic, kernel-logic]]`. `xarch review` reads a file (and a piece) of a part of a group on the sum of the
  probabilities on the group's parts, for doubt, for asking again near the line, for the ranking and for the summary of
  each part, and each reading says which parts it counted with its own, in text and in JSON (`alike`); the
  probability on each part stays in `distribution` as answered. `review calibrate` holds a group as one: an example
  reading at or above the line of another part of its group is no longer a disagreement, and the report says of each
  part of a group that it was held with the others. A dry run of either lists the groups. A record of placement held
  under other groups is stale; one held with none stays as it is. Each name must be a part, a group holds two parts or
  more, each once, a part is in one group at most, and the parts of a group must have the same `forbidden`, `holds`
  and `immutable`. `xarch profile explain evals.placement.alike` says it. The bundled `cli` and `web` profiles name
  `[[logic, kernel-logic]]`, which differ only in how many modules use a function.

- `xarch review` rules out of each file's answer the parts whose `holds` the file would break were it to lie there
  (a file of functions in a part of classes, say), as the rule `check` runs in each part decides it on the file read
  with the rest of the app: the probability on such a part is dropped and what remains is read as summing to 1, for
  doubt, for asking again near the line, for the sum over a group read alike, for the ranking and for the summary of
  each part. The file's own part is never ruled out. Each reading says what was ruled out, with what the answer put on
  each: `ruled out by holds: ...` under it in text, `ruled_out: [{part, by, probability}]` in the JSON, while
  `distribution` stays as answered. `review calibrate` reads placement's examples the same way, so a record of
  placement held before is stale; recalibrate with `xarch review calibrate --eval placement`. Pieces are read as
  answered. Both dry runs say what is ruled out (`ruled_out_by` in their JSON).

- `xarch review accept <file>... --why "<reason>"`: a person who has read a doubtful file and found it fine accepts
  it, and `.xarch/accepted.json` records it, by the path review shows, with its part, the part it read as, a hash of
  its code and the reason. `accept` sends nothing: it needs the file's answer in the cache, and refuses (exit 2),
  naming each file and what to do, with no reason, for a file review does not judge, one with no answer kept, or one
  that does not read as doubtful; `--remove` takes files out of the record. The hash is of what review sends for the
  file, blind to blank lines and whitespace at the end of a line, so an edit of comments alone keeps it and any other
  change brings the file back. A review reads a doubtful file accepted, while its code is as it was, as accepted and
  not doubtful, listed apart with its reason (`accepted` in the JSON); one changed since is doubtful again, with the
  old reason and what it read as then (`accepted_before`); every run says how many files are accepted, and lists as
  stale, with the command that takes them out, the files of the record it found gone, in another part, no longer
  doubtful or not judged. Review never edits the record, and its exit codes are unchanged.

### Changed

- `xarch review` says what a doubtful file is: some of its content may not fit the part it sits in (all of it, a
  function of it, or none). The heading of the doubtful files, what to do about each one, the README and the agents'
  guide say so, and tell the reader to move only what does not fit. The question asked of the model, the lines and the
  JSON are unchanged.
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

[0.2.0]: https://github.com/paulomtts/xarch/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/paulomtts/xarch/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/paulomtts/xarch/releases/tag/v0.1.0
