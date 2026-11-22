# 3.3 language: one outside-name parser reads names by the language's `package` pattern with its `member` joiner

Card: 305c9f45 (subtask of 3c7754c4). Release step 7 of the merged order (`0.3.0-cohesion-review-3.md`, section 3,
line 264); the note's step 5b. Blocked by c2e8d450 (3.2, the `unresolved` section), which is on this branch.

Owning note: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note"). Review 3:
`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md` ("review 3").

## Inherited constraints

- The note, rulings (lines 17-18): Python belongs only in the reader adapter and the data files under
  `xarch/architectures/presets/`. Rulings, defaults (line 37): outside names have a `package` pattern and a `member`
  joiner, `.` for Python.
- The note, 3.1 (lines 458-485): three keys of the data file, `name`, `package`, `member`. An outside name is
  `<package>` alone or `<package><member><name>[.<name>...]`; the package is checked with `package`, each later step
  with `name`. A builtin is written `<namespace><member><name>`. A method called on anything stays `.<name>()`, a
  notation of the format. `python.yaml` gains exactly `package: '(?!\d)\w+'` and `member: "."`. "`package` and
  `member` are required when `name` is given. Left out together with `name`, any text is a name, as today" (line 485).
- The note, 3.2 (lines 487-503): one parser serves `libraries` and `reserved` (a package alone), `never.<list>`
  entries, `testing.skips`, `testing.mocks.calls`, `testing.mocks.autospec`, the table's `decorator` and `row`, the
  check target `path` (`own_checks.py:119`), and, in `language_file.py`, `interface`, `dynamic` and `immutable`
  checked with the file's own `name`, `package`, `member`. `_DOTTED`, `_WORD` for `namespace` and `_MARK` go; `_WORD`
  stays for `standard`; `_EXTENSION` and `_FOLDER` stay. Messages that print an outside name join with `member`
  (`sentences.py:81` `{hit}`, the builtin hint). App module paths printed with dots stay.
- The note, 3.3 (lines 505-512): the checking code stops assuming a package is an identifier, that every dot splits a
  step, and that the loader's own lists are ASCII.
- The note, 3.4 (lines 514-526): no Python profile line changes. The TypeScript-like and ObjectScript-like entries
  below load under their files.
- The note, 3.5 (lines 528-534): the two refusal texts and the Python pin of `lodash-es`.
- The note, 3.6 (lines 536-543): two test-only language files; `test_language_file.py` cases with `%RegisteredObject`;
  a hand-built `Use` of `("node:fs", "readFileSync")` failing `uses: {never: ambient}` and printing
  `node:fs#readFileSync`.
- The note, 13 rows 5b (lines 1092-1096): the places that change. Row "all" (lines 1112-1114): no profile changes;
  corpora and golden docs: none expected.
- The note, dodges (lines 1143, 1151, 1152, 1166): no neutrality claimed with one data file; Python's `name` is not
  widened; no hidden default (`member` never means `.` when left out); no `never` entry of a Python profile rewritten.
- Review 3, O17, O19 (lines 241, 243): this step builds the parser before every list that uses it; it creates
  `brace.yaml`, `percent.yaml` and the seam test cases that later steps extend. O4, O5, O8 (lines 228-232): README
  and CHANGELOG lines under `[Unreleased]`; golden docs regenerated, diff read, never hand edited.

## Behavior

### The data file

1. `python.yaml` gains two lines after `name:`: `package: '(?!\d)\w+'` and `member: "."`, and its header comment says
   what they are (one clause each, in the file's style). No other line of it changes.
2. The loader (`language_file.py`) accepts the keys `package` (a regular expression, refused as `name` is when it does
   not compile: `package: must be a regular expression: <error>`) and `member` (a non-empty string holding no space:
   else `member: must be a non-empty string with no space`). The unknown-key text lists them in its sorted key list.
3. `name`, `package` and `member` are given together or not at all. For each one missing while another is given:
   `missing \`<key>\`: name, package and member are given together` (in the order name, package, member).
4. With the three given, the loader reads them first and checks with them:
   - `namespace` with `name` (text unchanged: `namespace: must be a name`); `standard` stays an ASCII word;
   - each `interface` and `dynamic` entry as an outside name (rule 7), one step allowed;
   - each `immutable` entry as an outside name, optionally followed by `(<name>=<value>, ...)` as today, its keyword
     names checked with `name`.
   With the three left out, every non-empty string is a name and an outside name is its whole text, one step (rule 8).
   When `name`, `package` or `member` itself is refused, the lists' entries are not checked further (the file is
   refused already; no follow-on problems).
5. Refusal texts of the loader, `<m>` being the file's `member` (empty when not given):
   - list shape of `interface`/`dynamic`: `<key>: must be a list of outside names, such as [<package><m><name>]`;
   - an entry: `<key>: '<entry>' is not an outside name such as <package><m><name>`;
   - list shape of `immutable`: `immutable: must be a list of outside names, each perhaps called with keywords, such
     as [<package><m><name>, "<package><m><name>(<name>=<value>)"]`;
   - an `immutable` entry: `immutable: '<entry>' is not an outside name such as <package><m><name>, or one called with
     keywords such as <package><m><name>(<name>=<value>)`.
   The angle-bracket words are literal text of the message.
6. Python reads exactly as today: `interface == (("typing", "Protocol"), ("typing_extensions", "Protocol"))`, the same
   `dynamic` and `immutable` tuples, the same `namespace`.

### The one parser

7. An outside name under a language with `member` `<m>` (non-empty), `name` pattern `N`, `package` pattern `P` and
   namespace `S`: the text is split at the first `<m>`. The head must be non-empty and either equal `S` (when `S` is
   given) or match `P` in full. With no `<m>` in the text, the name is the head alone, one step. With one, the rest is
   split at `.` (the format's notation between names, as in `.<name>()`), and every step must be non-empty and match
   `N` in full. The result is `(head, *steps)`; anything else is no outside name.
   - Python: `datetime.datetime.now` is `("datetime", "datetime", "now")`, `socket` is `("socket",)`, `a..b` and
     `datetime.` are refused.
   - Brace: `node:fs#readFileSync` is `("node:fs", "readFileSync")`; `lodash.debounce` is `("lodash.debounce",)`;
     `globalThis#fetch` is `("globalThis", "fetch")` because `globalThis` is the namespace, though `P` refuses it;
     `"@scope/pkg"` is `("@scope/pkg",)`.
   - Percent: `%Library.RegisteredObject` is `("%Library", "RegisteredObject")`.
8. Under a language with no `member` (`Language()`, `CheckedLanguage()`, a data file giving none of the three), an
   outside name is its whole non-empty text, one step, never split. There is no fallback to `.`.
9. The split alone (rule 7 without the pattern checks) is what `own_checks.py:119` uses for a check target `path`,
   with the profile's language `member` (`profile.language`, already at hand in `_match`): it refused nothing before and
   refuses nothing now. Under no `member` the text is one step (rule 8), so a profile built with a default
   `CheckedLanguage()` splits no `path` target; the rules tests that need the split carry Python's language (T21). `.<name>()` stays `("", "<name>()")` there, as today.
10. Outside names are printed by one printer: `("", "<name>()")` prints `.<name>()`; `(head,)` prints `head`;
    `(head, *rest)` prints `head + member + ".".join(rest)`. Under Python every print is byte-for-byte today's.
    Under no `member` a multi-step tuple prints `head` + the rest joined by `.` with nothing between head and rest;
    no profile can produce one (rule 8), only a hand-built test.

### What the profile reads with it

11. `parts.<p>.libraries` and `reserved` read each entry as a package alone: one step, the head matching `package`
    (rule 7 with no `member` in the text and no namespace allowed). A refused entry:
    `<where>: '<entry>' is not a package name the language <title> allows` (for `reserved`, `<where>` is `reserved`).
    This text replaces "is not a top-level import name, such as sqlmodel / ast" for every language, Python included:
    the note's 3.5 says the message names no example package (line 531), and "with today's text" (line 534) is read
    as "still refused at the same key, one problem". The shape texts of the two keys (not a list / not a mapping) do
    not change. The standard-library and listed-twice refusals are unchanged.
12. `testing.skips`, `testing.mocks.calls`, `testing.mocks.autospec`, `testing.table.decorator`, `testing.table.row`
    read each value as an outside name of at least two steps (as today's `_dotted`). Refused:
    `<where>: '<value>' is not an outside name such as <package><m><name>` (Python: `<package>.<name>`), and the list
    shape `<where>: must be a list of outside names such as <package><m><name>`. Listed-twice is unchanged, compared
    on the parsed steps.
13. `never.<list>` entries: the method form `.<name>()` is read first, as today (special-method and missing-`()`
    refusals unchanged in logic). Every other entry is an outside name (rule 7), one step allowed. Texts:
    - not an outside name: `<where>: '<entry>' is not an outside name such as <package><m><name>, nor a package, nor a
      method such as .<name>()`;
    - `.name` without `()`: `<where>: '<entry>' is neither an outside name nor a method: write <entry>() for a method
      called on anything`;
    - list shape: `<where>: must be a non-empty list of outside names, packages or methods, such as
      [<package><m><name>, <package>, .<name>()]`;
    - a bare builtin (one step, in the language's builtins): the hint is `write <namespace><m><entry>` (Python:
      `builtins.open`, unchanged);
    - listed twice: compared on the parsed steps, text unchanged.
14. Every single-name check that reads `name` today (`id`, `keywords`, `functions`, `suffix`, `prefix`, a fixture's
    `calls`, and the rest of `profile_checks.py` and `profile_parsing.py` that are not outside names) keeps reading
    `name` with today's texts.
15. Printing with `member` (rule 10): `{hit}` (`sentences.py:81`), a check's names (`sentences.py:66`), the written
    target (`written.py:87`), the `where` report's never lists (`where.py:105`, `:201`), the looseness items
    (`looseness.py:70`, `:91`), the docs' `never-use` line (`docs_template.py:455`) and `%interface_path%`
    (`explain.py:33`). App module paths printed with dots stay as they are.

### The test-only language files

16. `tests/fakes/languages/brace.yaml` (TypeScript-like) and `tests/fakes/languages/percent.yaml` (ObjectScript-like)
    load with `language_of` with no problem. They hold only keys the loader knows today:
    - brace: `title: Brace`, `extension: .ts`, `package_file: index.ts`, `namespace: globalThis`,
      `standard: interpreter`, `name: '[A-Za-z_$][A-Za-z0-9_$]*'`,
      `package: '(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*|node:[a-z_/]+'`, `member: "#"`,
      `dynamic: ["node:module#createRequire"]`;
    - percent: `title: Percent`, `extension: .cls`, `package_file: Package.cls`, `namespace: "%SYSTEM"`,
      `standard: interpreter`, `name: '%?[A-Za-z][A-Za-z0-9]*'`, `package: '%?[A-Za-z][A-Za-z0-9]*'`, `member: "."`,
      `interface: ["%Library.RegisteredObject"]`, `dynamic: ["%SYSTEM.OBJ.Load"]`, `immutable: ["%SerialObject"]`.
    Each carries a short header comment saying it is a test-only language and which kind it imitates. Later steps
    (5c, 8a-8e, 15a, 15b) add their keys to these files.
17. `tests/modules/spec/languages.py` exposes `BRACE` and `PERCENT` beside `PYTHON`, each `language_of` of its file
    (no runtime names: `standard_names`, `builtin_names`, `reserved_names` empty, except that `BRACE` gets
    `builtin_names={"fetch"}` for the hint test).
18. Under `BRACE`, a profile whose part writes `libraries: [lodash-es, "@scope/pkg"]` and whose `never` block holds
    `ambient: ["node:fs#readFileSync", "globalThis#fetch", ".toISOString()"]` with that part writing
    `uses: {never: ambient}` loads; the parsed list is `(("node:fs", "readFileSync"), ("globalThis", "fetch"),
    ("", "toISOString()"))`. Under `PYTHON` the same document is refused with one problem per entry that does not
    parse: `lodash-es` and `@scope/pkg` (rule 11), `node:fs#readFileSync` and `globalThis#fetch` (rule 13);
    `.toISOString()` loads.

### README, CHANGELOG, golden docs

19. README, the `language` paragraph (around line 133): the tokens list gains what an import names from outside the
    app as one step (`package`) and the text that joins a package to a name in it in the profile's lists (`member`,
    `.` for Python), with the form `<package><member><name>`. CHANGELOG `[Unreleased]`, `### Changed`: one entry saying
    a language's data file gives `package` and `member`, outside names in a profile are read by them (no Python entry
    changes), and the refusal texts of rules 11-13.
20. The golden docs `docs/{cli,web,xarch}/testing.md` regenerate with no diff (Python prints as today). The recorded
    corpora do not change. No profile file changes. `keys.yaml` does not change.

## Shape (what the planner needs to know, not how to write it)

- The parser and printer are pure functions over strings in `xarch/kernel/logic/names.py`, beside `is_name`:
  `outside_steps(text, member) -> tuple[str, ...]` (the split of rules 7-9, no checks),
  `outside_name(text, name, package, member, namespace="") -> tuple[str, ...] | None` (rule 7 with checks, rule 8)
  and `outside_text(steps, member) -> str` (rule 10). The note places the parser in `profile_checks.py` (3.2,
  line 489), but `own_checks.py` in the rules module splits a check target too, and rules may not import spec's
  logic; kernel-logic is what both import. `profile_checks.py` and `language_file.py` call it; nothing else splits or
  joins an outside name.
- `CheckedLanguage` (`xarch/profile_values/language.py`) gains `package: str = ""` and `member: str = ""` after
  `names`, defaults meaning "the data file does not say". Its docstring says so. `Language` reads them through
  `checked` and gets no duplicate field (it keeps `names` as today); the loader fills `CheckedLanguage`.
- Deleted: `profile_checks.is_name` (single-name callers call `names.is_name(text, language.names)`), `_is_dotted`,
  `dotted_names` and `_dotted` in `profile_checks.py` (replaced by one helper over the parser for rule 12),
  `_DOTTED`, `_MARK`, `_dotted` in `language_file.py`, and `_WORD` for `namespace`. Every `split(".")` and
  `".".join` of an outside name listed in rules 9, 13 and 15 goes through the kernel functions.
- The seam test (`tests/architecture/test_language_seam.py`): `language_words` splits `interface`/`dynamic` steps with
  the file's `member`; a new `TEST_LANGUAGES` tuple names the two test-only files, and a parametrized case proves each
  loads with `language_of` and that its words are read (later steps extend it). `member` is not added to
  `TOKEN_KEYS`: Python's `.` is also how xarch joins app module paths, which stay, so a literal `"."` is no leak.
- No comments in xarch's code; docstrings only. Never `ruff --fix`.

## Out of scope

- Interface marks as maps, `{base: ...}`, `Class.interface`, `nothing`, `special` (3.5, step 5c).
- List includes: a `never` entry that names another list (step 7a, `list-reuse-design.md`); this parser reads entries
  only.
- `testing.declared[].call` (15a), `testing.mocks.specs` (15b), `standard` as lists (8a), `extensions`,
  `package_files` (8b), `comments` (8c), `public` (8d), immutable marks as maps (8e).
- The reader adapter (`fs_source_tree.py`): it splits Python import text and stays as it is.
- `keys.yaml` texts (`%namespace%.open` and the like) and a `%member%` word; the shape texts of `libraries` and
  `reserved`; the vocabulary's "dotted names" wording of `NAMES`; the `PACKAGES` target form; wording of app module
  paths for other languages. Left for the wrap-up (step 25) or the note's later steps.
- Any profile (`architecture.yaml`, `cli.yaml`, `web.yaml`, stress, archived), the recorded corpora, the golden docs.

## Tests (written first)

Pure logic tier, `tests/kernel/logic/test_names.py` (create or extend; pure string functions, the fastest place to pin
every split rule):

- T1 `outside_name` under Python patterns: `datetime.datetime.now`, `socket`, `builtins.open`; refused `a..b`,
  `datetime.`, `.x`, `lodash-es`, `@scope/pkg`, `""`.
- T2 under brace patterns with namespace `globalThis`: `node:fs#readFileSync`, `globalThis#fetch`, `lodash.debounce`,
  `lodash.debounce#debounce` gives `("lodash.debounce", "debounce")`, `"@scope/pkg"`; refused `Foo#bar` (head not a
  package nor the namespace), `node:fs#`, `#x`.
- T3 under percent patterns: `%Library.RegisteredObject`, `%SerialObject`; refused `9x`.
- T4 with no member: `datetime.datetime.now` gives `("datetime.datetime.now",)`; `""` is refused.
- T5 `outside_steps`: brace `node:fs#readFileSync`, Python `a.b.c`, method `.now()` gives `("", "now()")`.
- T6 `outside_text`: `("", "absolute()")` with `.` and `#` gives `.absolute()`; `("node:fs", "readFileSync")` with `#`
  gives `node:fs#readFileSync`; `("datetime", "datetime", "now")` with `.` gives `datetime.datetime.now`; `("socket",)`
  gives `socket`.

Data-file tier, `tests/modules/spec/application/logic/test_language_file.py` (the loader on inline documents, where
the note's 3.6 puts the `%RegisteredObject` cases):

- T7 `DOCUMENT` gains `name`, `package`, `member` (`'[A-Za-z_]\w*'`, same, `"."`); the first test's expected value
  gains `package` and `member`; the broken-document test's unknown-key list gains `member, package`, its `interface`
  shape text and its `dynamic` entry texts become rule 5's (`'a b' is not an outside name such as <package>.<name>`;
  `''` likewise).
- T8 Each of `name`, `package`, `member` given alone or in pairs lists the missing ones (rule 3).
- T9 `package` that does not compile and `member` `"a b"` are refused (rule 2), with no follow-on list problems.
- T10 A document with `name`/`package` `'%?[A-Za-z][A-Za-z0-9]*'`, `member` `"."`, `namespace: "%SYSTEM"`, `interface:
  ["%RegisteredObject"]`, `dynamic: ["%SYSTEM.OBJ.Load"]`, `immutable: ["%SerialObject", "%Lib.Rec(frozen=yes)"]`
  loads, with the steps of rule 7.
- T11 The same lists under Python's three patterns are refused with rule 5's texts (`'%RegisteredObject' is not an
  outside name such as <package>.<name>`).
- T12 A document with none of the three reads `interface: ["sys.Contract"]` as `(("sys.Contract",),)` (rule 8).

Language values tier, `tests/profile_values/test_language.py`: T13 `CheckedLanguage()` has `package == member == ""`.

Bundled data tier, `tests/modules/spec/application/test_language.py` (or wherever `PYTHON` is pinned): T14 `PYTHON`'s
`checked.package == r"(?!\d)\w+"` and `checked.member == "."`, and its `interface`, `dynamic`, `immutable`,
`namespace` are today's values.

Profile tier, `tests/modules/spec/application/logic/` (`parse_profile` on documents from `tests/modules/spec/profiles.py`,
the tier where refusals carry their addresses):

- T15 `test_libraries_and_guards.py`: under `PYTHON`, `libraries: [lodash-es]` and `["@scope/pkg"]` are refused with
  `parts.store.libraries: 'lodash-es' is not a package name the language Python allows`; `reserved: {os.path: x}` with
  `reserved: 'os.path' is not a package name the language Python allows`. The existing pins at `:28`, `:135` and
  `test_profile_parsing.py:379` change to this text.
- T16 `test_never_use.py`: the `DOTTED`/`METHOD` constants change to rule 13's text; the builtin hint test still says
  `write builtins.open`; a new case under `BRACE` with `builtin_names={"fetch"}` gives `write globalThis#fetch` for a
  bare `fetch`.
- T17 The neutrality pair of rule 18: one document loads under `BRACE` with the parsed tuples, and is refused under
  `PYTHON` with exactly the four problems.
- T18 `test_testing.py`, `test_profile_parsing_tests.py`, `test_profile_checks.py`: the `is not a dotted name such as
  pkg.sub.name` and `must be a list of dotted names such as pkg.sub.Name` pins change to rule 12's texts; a skip
  `node:test#skip` is accepted under `BRACE`.
- T19 Listed-twice is compared on steps: under Python `[socket, socket]` is refused once, as today.

Hand-built facts tier, `tests/modules/rules/application/logic/test_never_use.py` (the note's 3.6 third bullet; the
engine on a hand-built `Profile`):

- T20 A `Profile` with `language=BRACE.checked`, `uses_never={"adapters": (("node:fs", "readFileSync"),
  ("globalThis", "fetch"), ("", "toISOString()"))}` and a file of `adapters/` with `Use(4, ("node:fs", "readFileSync"),
  1)` gives `4: adapters/ of modules/docs may not use node:fs#readFileSync (parts.adapters.uses.never)`, and its fix
  `do what needs node:fs#readFileSync outside adapters/, ...`.
- T21 The file's existing `PROFILE` (a default `CheckedLanguage()` today) gets the `PYTHON` of
  `tests/modules/rules/builders.py` as its language (rule 10: with no `member` a hit would print without a joiner).
  That `PYTHON` is a positional `CheckedLanguage` built by hand, so it gains `package=r"(?!\d)\w+"` and `member="."`
  too (read from `python.yaml` as its `names` is); without them every rules test through `builders.PROFILE` that
  prints an outside name or reads a check's `path` target (rule 9) would print or split without a joiner. Any other
  rules test that prints or splits an outside name under a default `CheckedLanguage()` is given that `PYTHON` the same
  way; its expected text does not change.

Seam tier, `tests/architecture/test_language_seam.py`: T22 the `TEST_LANGUAGES` case of the Shape section; the existing
guards pass unchanged over `python.yaml`.

Docs tier: T23 the golden-docs test (`tests/bootstrap/test_docs.py`) passes with no regenerated diff; the recorded
corpora test passes unchanged; `tests/architecture/test_readme.py` passes with the README edit.

Grep check (planner adds it as a final task step): `grep -rn "_is_dotted\|dotted_names\|_DOTTED\|_MARK\b" xarch` returns
nothing, and `profile_checks.py` defines no `is_name`.

## Gates

On this branch alone, the full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`. Regenerate the golden docs and confirm no diff.
