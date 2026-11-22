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

---

# 3.3 language: one outside-name parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every outside name a language's data file or a profile writes is read by one parser over the language's
`name` and `package` patterns and its `member` joiner, and printed back by one printer, so a TypeScript-like or an
ObjectScript-like test-only language loads and its names read, while every Python text stays byte-for-byte as today.

**Architecture:** Three pure functions in `xarch/kernel/logic/names.py` (`outside_steps`, `outside_name`,
`outside_text`) are the only place that splits or joins an outside name. `CheckedLanguage` gains `package` and
`member`; the loader (`language_file.py`) reads `name`/`package`/`member` first and checks `namespace`, `interface`,
`dynamic` and `immutable` with them; `profile_checks.py` reads `libraries`, `reserved`, `never` lists and the testing
names with them; the rules module splits a check's `path` target and prints every outside name with the profile
language's `member`.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140, import sorting `I`), `uv run`.

**Spec:** `docs/superpowers/specs/3-3-language-one-305c9f45.md` (prepended above; read it whole before Task 1).

## Global Constraints

- Python belongs only in the reader adapter and the data files under `xarch/architectures/presets/`: no new literal,
  docstring word or identifier in `xarch/` may name the language (`tests/architecture/test_language_seam.py` guards
  it: never write `Python`, `builtins`, `typing`, `Protocol`, `importlib`, `__init__`, `.py` in xarch docstrings or
  literals; never quote `` `#...` ``, `` `_x` ``, `` `__x__` `` or `` `None` `` in a docstring of `kernel/logic` or
  `modules/rules/{domain,application}`).
- `python.yaml` gains exactly `package: '(?!\d)\w+'` and `member: "."` after `name:`, plus header-comment words; no
  other line of it changes.
- "`package` and `member` are required when `name` is given. Left out together with `name`, any text is a name, as
  today." No hidden default: `member` never means `.` when left out.
- Python's `name` is not widened; no `never` entry of a Python profile is rewritten; no profile file changes;
  `keys.yaml` does not change; the recorded corpora and the golden docs `docs/{cli,web,xarch}/testing.md` do not move.
- App module paths printed with dots stay as they are.
- No comments in xarch's code; docstrings only. Never `ruff --fix`.
- README and CHANGELOG lines go under `[Unreleased]`; golden docs are regenerated and their diff read, never hand
  edited.
- Run long suites with `timeout` (`timeout 900 uv run pytest -q`), never `pkill`/`killall`.

## Spec deviations (decided by the planner, with evidence)

1. **T20 uses `tests.modules.rules.builders.BRACE`, not `BRACE.checked` from `tests/modules/spec/languages.py`.** No
   test of the rules module imports spec's test helpers (`grep -rln "from tests.modules.spec" tests/modules/rules`
   prints nothing); `builders.py` already builds `PYTHON` as a `CheckedLanguage` read from `python.yaml`, so `BRACE`
   is built the same way from `tests/fakes/languages/brace.yaml`. The value the engine sees is the same.
2. **A refused value prints with `!r`, as today.** Rule 12 writes `'<value>'`; a value that is no string (`row: 3`)
   prints `3 is not an outside name ...`, exactly as today's `3 is not a dotted name ...`
   (`test_testing.py:90`).
3. **`written.py` needs the member threaded in.** `check_of(rule)` and `written(rules)` hold no language today; they
   become `check_of(rule, member, flagged=(), clean=())` and `written(rules, member)`, and
   `xarch/modules/rules/application/services/explaining.py` passes the language's `member` (it already holds the
   `CheckedLanguage` in `_example`, and `self.language((location,))` gives it in `rule`).
4. **Two joins of a table row stay**: `docs_template.py:483` and `scenarios.py:192` print `testing.table.row` with
   `".".join`. Rule 15 does not list them, `scenarios._rows` holds no language, and the table is the business of a
   later step (15a/15b). Under Python they print the same. `profile_parsing.py:537` (`autospec ... is also listed in
   calls`), which has the language at hand, does go through `outside_text`.
5. **`namespace` is read before `interface`** (it is checked with `name` and lets an `interface`/`dynamic`/`immutable`
   head equal it, rule 7), so a document with a bad `namespace` and a bad `interface` lists the namespace problem
   first. No existing test pins that order.

## Review Focus

1. A data file's `immutable` keyword whose name the language's `name` refuses (`"pkg.record(2x=yes)"`): refused with
   rule 5's entry text, as today's `_MARK` refused it. Test: Task 2, Step 1 (`test_language_file.py`).
2. A package written as the namespace (`libraries: [globalThis]` under Brace): rule 11 allows no namespace, so it is
   refused `is not a package name the language Brace allows`. Test: Task 3, Step 1 (`test_never_use.py` brace cases).
3. A `never` entry ending in the member or starting with it (`node:fs#`, `#readFileSync` under Brace): refused with
   rule 13's text, not accepted as a package. Test: Task 3, Step 1.
4. A `never` entry listed twice under a member that is not a dot (`node:fs#readFileSync` twice under Brace): refused
   once, compared on steps. Test: Task 3, Step 1.
5. A check's `path` target under a member that is not a dot (`node:fs#readFileSync`): split at `#`, and a method
   `.run()` still `("", "run()")`. Test: Task 4, Step 1 (`test_own_checks.py`).

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `xarch/kernel/logic/names.py` | `outside_steps`, `outside_name`, `outside_text`: the one parser and printer | 1 |
| `xarch/profile_values/language.py` | `CheckedLanguage.package`, `CheckedLanguage.member` | 1 |
| `tests/kernel/logic/test_names.py` | T1-T6 | 1 |
| `tests/profile_values/test_language.py` | T13 | 1 |
| `xarch/modules/spec/application/logic/language_file.py` | the loader reads `name`/`package`/`member` and checks the lists with them | 2 |
| `xarch/architectures/presets/language/python.yaml` | two keys and their header words | 2 |
| `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml` | the test-only languages | 2 |
| `tests/modules/spec/languages.py` | `BRACE`, `PERCENT` | 2 |
| `tests/modules/spec/application/logic/test_language_file.py` | T7-T12, Review Focus 1 | 2 |
| `tests/modules/spec/application/test_language.py` | T14; its hand-written documents gain the three keys | 2 |
| `tests/architecture/test_language_seam.py` | `language_words` splits with `member`; `TEST_LANGUAGES` (T22) | 2 |
| `xarch/modules/spec/application/logic/profile_checks.py` | rules 11-14 | 3 |
| `xarch/modules/spec/application/logic/profile_parsing.py` | mocks through `outside_names`; `is_name` from the kernel | 3 |
| `tests/modules/spec/application/logic/test_{profile_checks,never_use,libraries_and_guards,profile_parsing,profile_parsing_tests,testing}.py` | T15-T19, Review Focus 2-4 | 3 |
| `xarch/modules/rules/application/logic/{own_checks,sentences,written,where}.py`, `xarch/modules/rules/application/services/explaining.py` | split and print with `profile.language.member` | 4 |
| `xarch/modules/spec/application/logic/{looseness,docs_template,explain}.py` | print with `language.checked.member` | 4 |
| `tests/modules/rules/builders.py`, `tests/modules/rules/application/logic/test_{never_use,own_checks,written}.py`, `tests/modules/spec/application/logic/test_profile_keys.py` | T20, T21, Review Focus 5 | 4 |
| `README.md`, `CHANGELOG.md` | rule 19 | 5 |

---

### Task 1: The parser and printer of outside names, and the language's two new fields

**Files:**
- Modify: `xarch/kernel/logic/names.py` (whole file shown below)
- Modify: `xarch/profile_values/language.py:20-55` (`CheckedLanguage` docstring and fields)
- Test: `tests/kernel/logic/test_names.py`
- Test: `tests/profile_values/test_language.py`

**Interfaces:**
- Consumes: `is_name(text: str, pattern: str) -> bool` (already in `names.py`).
- Produces:
  - `STEP = "."` (module constant of `xarch/kernel/logic/names.py`)
  - `outside_steps(text: str, member: str) -> tuple[str, ...]`
  - `outside_name(text: str, name: str, package: str, member: str, namespace: str = "") -> tuple[str, ...] | None`
  - `outside_text(steps: tuple[str, ...], member: str) -> str`
  - `CheckedLanguage.package: str = ""` and `CheckedLanguage.member: str = ""`, the last two fields, right after
    `names`, in that order (positional construction passes `..., names, package, member`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/kernel/logic/test_names.py` (and change its import line to
`from xarch.kernel.logic.names import is_name, is_private_name, outside_name, outside_steps, outside_text`):

```python
BRACE_NAME = r"[A-Za-z_$][A-Za-z0-9_$]*"
BRACE_PACKAGE = r"(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*|node:[a-z_/]+"
PERCENT = r"%?[A-Za-z][A-Za-z0-9]*"


@pytest.mark.parametrize("text, steps", [
    pytest.param("datetime.datetime.now", ("datetime", "datetime", "now"), id="a package and two names after it"),
    pytest.param("socket", ("socket",), id="a package alone"),
    pytest.param("builtins.open", ("builtins", "open"), id="a package and one name"),
    pytest.param("a..b", None, id="an empty step"),
    pytest.param("datetime.", None, id="a member with nothing after it"),
    pytest.param(".x", None, id="nothing before the member"),
    pytest.param("lodash-es", None, id="a package the pattern refuses"),
    pytest.param("@scope/pkg", None, id="a scoped package the pattern refuses"),
    pytest.param("", None, id="no text"),
])
def test_an_outside_name_is_read_by_the_patterns_of_a_language_joined_by_a_dot(text, steps):
    assert outside_name(text, PATTERN, PATTERN, ".") == steps


@pytest.mark.parametrize("text, steps", [
    pytest.param("node:fs#readFileSync", ("node:fs", "readFileSync"), id="a runtime module and a name in it"),
    pytest.param("globalThis#fetch", ("globalThis", "fetch"), id="the namespace, which the package pattern refuses"),
    pytest.param("lodash.debounce", ("lodash.debounce",), id="a dot is part of a package where the member is not one"),
    pytest.param("lodash.debounce#debounce", ("lodash.debounce", "debounce"), id="a dotted package and a name in it"),
    pytest.param("@scope/pkg", ("@scope/pkg",), id="a scoped package alone"),
    pytest.param("Foo#bar", None, id="a head that is neither a package nor the namespace"),
    pytest.param("node:fs#", None, id="a member with nothing after it"),
    pytest.param("#x", None, id="nothing before the member"),
])
def test_an_outside_name_is_read_by_the_member_of_a_language_that_joins_with_a_hash(text, steps):
    assert outside_name(text, BRACE_NAME, BRACE_PACKAGE, "#", "globalThis") == steps


@pytest.mark.parametrize("text, steps", [
    pytest.param("%Library.RegisteredObject", ("%Library", "RegisteredObject"), id="a percent package and a name"),
    pytest.param("%SerialObject", ("%SerialObject",), id="a percent package alone"),
    pytest.param("9x", None, id="a package that starts with a digit"),
])
def test_an_outside_name_is_read_by_the_patterns_of_a_language_whose_names_start_with_a_percent(text, steps):
    assert outside_name(text, PERCENT, PERCENT, ".", "%SYSTEM") == steps


def test_under_a_language_that_gives_no_member_an_outside_name_is_its_whole_text():
    assert (outside_name("datetime.datetime.now", "", "", ""), outside_name("", "", "", "")) == (
        ("datetime.datetime.now",), None)


@pytest.mark.parametrize("text, member, steps", [
    pytest.param("node:fs#readFileSync", "#", ("node:fs", "readFileSync"), id="split at the member"),
    pytest.param("a.b.c", ".", ("a", "b", "c"), id="split at a dot member, then at each dot"),
    pytest.param(".now()", ".", ("", "now()"), id="a method called on anything"),
    pytest.param("a.b.c", "", ("a.b.c",), id="no member: one step"),
    pytest.param("a.b", "#", ("a.b",), id="no member in the text: one step"),
])
def test_the_steps_of_an_outside_name_are_split_with_no_check(text, member, steps):
    assert outside_steps(text, member) == steps


@pytest.mark.parametrize("steps, member, text", [
    pytest.param(("", "absolute()"), ".", ".absolute()", id="a method, under a dot member"),
    pytest.param(("", "absolute()"), "#", ".absolute()", id="a method, under another member"),
    pytest.param(("node:fs", "readFileSync"), "#", "node:fs#readFileSync", id="a package and a name, with the member"),
    pytest.param(("datetime", "datetime", "now"), ".", "datetime.datetime.now", id="the names after it joined by dots"),
    pytest.param(("socket",), ".", "socket", id="a package alone"),
    pytest.param((), ".", "", id="nothing"),
    pytest.param(("a", "b", "c"), "", "ab.c", id="no member: nothing between the package and its names"),
])
def test_an_outside_name_is_printed_back_with_the_member_of_the_language(steps, member, text):
    assert outside_text(steps, member) == text
```

Append to `tests/profile_values/test_language.py`:

```python
def test_a_language_that_says_nothing_has_no_package_pattern_and_no_member():
    assert (CheckedLanguage().package, CheckedLanguage().member) == ("", "")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/kernel/logic/test_names.py tests/profile_values/test_language.py -q`
Expected: collection ERROR `ImportError: cannot import name 'outside_name'` for `test_names.py`, and
`AttributeError: 'CheckedLanguage' object has no attribute 'package'` for the new language test.

- [ ] **Step 3: Write the implementation**

Replace the whole of `xarch/kernel/logic/names.py` with:

```python
"""Whether a text is a name a language allows, by the pattern its data file gives (a regular expression; any text but
nothing when it gives none), and whether a name is private, by how the language starts one ("" for none); and the
names a profile writes from outside the app, by the language's package pattern and its member: read into their steps,
and printed back from them. Nothing else splits or joins an outside name."""
from __future__ import annotations

import re

STEP = "."
"""What stands between the names after a package in an outside name, and before a method called on anything: a
notation of the profile format, not of a language."""


def is_name(text: str, pattern: str) -> bool:
    """Whether text is a name the pattern allows; any text but nothing when the pattern is empty."""
    return re.fullmatch(pattern or ".+", text) is not None


def is_private_name(text: str, private: str) -> bool:
    """Whether text starts as a private name does; no text does when the language marks none ("")."""
    return bool(private) and text.startswith(private)


def outside_steps(text: str, member: str) -> tuple[str, ...]:
    """The steps of an outside name as written, checked against nothing: the text up to the first member, then the rest
    split at each step mark; the whole text as one step when the language gives no member or the text holds none."""
    if not member:
        return (text,)
    head, found, rest = text.partition(member)
    return (head, *rest.split(STEP)) if found else (head,)


def outside_name(text: str, name: str, package: str, member: str, namespace: str = "") -> tuple[str, ...] | None:
    """The steps of an outside name the language allows: a package (or the namespace, when one is given) alone, or
    followed by the member and names joined by the step mark, each a name the name pattern allows; None when the text
    is none. Under a language that gives no member, any text but nothing is one step."""
    if not text:
        return None
    if not member:
        return (text,)
    head, *steps = outside_steps(text, member)
    if not ((namespace and head == namespace) or (head and is_name(head, package))):
        return None
    return (head, *steps) if all(is_name(step, name) for step in steps) else None


def outside_text(steps: tuple[str, ...], member: str) -> str:
    """An outside name as a profile writes it: a method called on anything, ("", "<name>()"), after the step mark; else
    the package, then the member and the names after it joined by the step mark."""
    if len(steps) == 2 and not steps[0]:
        return f"{STEP}{steps[1]}"
    return steps[0] + member + STEP.join(steps[1:]) if len(steps) > 1 else "".join(steps)
```

In `xarch/profile_values/language.py`, replace the last line of the `CheckedLanguage` docstring

```python
is the pattern of a name the language allows, a regular expression (empty: its data file gives none)."""
```

with

```python
is the pattern of a name the language allows, a regular expression (empty: its data file gives none); package is the
pattern of what an import names from outside the app as one step, and member the text that joins a package to a name
in it in a profile's lists (both empty: its data file does not say, and an outside name is then its whole text)."""
```

and replace the field line `    names: str = ""` with

```python
    names: str = ""
    package: str = ""
    member: str = ""
```

Also change the `RecordMark` docstring's "a dotted name among its bases or its decorators" to "an outside name among
its bases or its decorators" (wording only).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/kernel/logic/test_names.py tests/profile_values/test_language.py tests/architecture/test_language_seam.py -q`
Expected: all PASS (the seam guard reads the new docstrings and literals and finds no word of the language).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check xarch/kernel/logic/names.py xarch/profile_values/language.py tests/kernel/logic/test_names.py tests/profile_values/test_language.py
git add xarch/kernel/logic/names.py xarch/profile_values/language.py tests/kernel/logic/test_names.py tests/profile_values/test_language.py
git commit -m "An outside name is read by one parser over a language's name and package patterns and its member, the text up to the first member being the package or the namespace and each step after it a name, the whole text one step under a language that gives no member; one printer writes it back, a method called on anything after a dot; the language as a check reads it holds package and member, empty when its data file does not say

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The data file reads `name`, `package` and `member` and checks its lists with them; the test-only languages

**Files:**
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring, constants, `language_of`, `_dotted`→`_outside`, `_marks`, new `_joins`, `_mark`)
- Modify: `xarch/architectures/presets/language/python.yaml:8` (header comment) and after line 28 (`name:`)
- Create: `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml`
- Modify: `tests/modules/spec/languages.py`
- Modify: `tests/architecture/test_language_seam.py` (`language_words`, new `TEST_LANGUAGES` and two tests)
- Test: `tests/modules/spec/application/logic/test_language_file.py`
- Test: `tests/modules/spec/application/test_language.py`

**Interfaces:**
- Consumes: `outside_name`, `outside_steps`, `is_name` from `xarch.kernel.logic.names`; `CheckedLanguage(..., names,
  package, member)` from Task 1.
- Produces:
  - `language_file.KEYS` holds `"package"` and `"member"`; `language_file.JOINED = ("name", "package", "member")`.
  - `language_of(name, document) -> Language` whose `checked.package`/`checked.member` are the file's values.
  - `tests.modules.spec.languages.BRACE` (a `Language`, `builtin_names=frozenset({"fetch"})`) and
    `tests.modules.spec.languages.PERCENT` (a `Language`), both with empty `standard_names`/`reserved_names`.
  - `PYTHON.checked.package == r"(?!\d)\w+"`, `PYTHON.checked.member == "."`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Replace the `DOCUMENT` constant and the first test with:

```python
NAME = r"[A-Za-z_]\w*"
JOINS = {"name": NAME, "package": NAME, "member": "."}
DOCUMENT = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
            "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system", "cache": ".objs",
            "standard": "interpreter"} | JOINS
UNJOINED = {key: value for key, value in DOCUMENT.items() if key not in JOINS}
"""DOCUMENT with none of name, package and member."""
PERCENT = {"name": "%?[A-Za-z][A-Za-z0-9]*", "package": "%?[A-Za-z][A-Za-z0-9]*", "member": ".", "namespace": "%SYSTEM",
           "interface": ["%RegisteredObject"], "dynamic": ["%SYSTEM.OBJ.Load"],
           "immutable": ["%SerialObject", "%Lib.Rec(frozen=yes)"]}
"""The lists of a language whose names may start with a percent, under its own patterns."""


def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", ".pas", "unit.pas", (("sys", "Contract"),),
                                  (("sys", "load"), ("sys", "Contract", "load")), names=NAME, package=NAME, member="."),
        "system", "interpreter", ".objs", NAME)
```

Replace the body of `test_every_problem_of_a_document_is_listed_naming_the_preset` with:

```python
    broken = {"title": "", "extension": "pas", "package_file": 3, "interface": "x", "dynamic": ["", "a b"], "cache": "a/b",
              "extra": 1} | JOINS
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        "unknown key 'extra': use branching, branching_expressions, cache, call, comment, directives, dynamic, encoding, extension, "
        "immutable, importing, interface, member, name, namespace, nothing, package, package_file, private, shebang, special, "
        "standard, supplies, title",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        "extension: must be a dot and a name, such as .pas",
        "package_file: must be a file name ending in the extension",
        "interface: must be a list of outside names, such as [<package>.<name>]",
        "dynamic: '' is not an outside name such as <package>.<name>",
        "dynamic: 'a b' is not an outside name such as <package>.<name>",
        "cache: must be a folder name"]
```

In `test_the_tokens_of_the_code_are_read_when_the_document_gives_them`, change `"name": "[a-z]+"` to
`"name": "[A-Za-z]+"` and the expected `"[a-z]+"` to `"[A-Za-z]+"` (the document's `sys.Contract` must stay a name).

In the parametrize list of `test_a_token_that_is_not_what_its_key_takes_is_a_problem`, change the two `immutable`
rows to:

```python
    pytest.param({"immutable": "pkg.Record"}, "immutable: must be a list of outside names",
                 id="marks of an immutable record not a list"),
    pytest.param({"immutable": ["pkg.record(frozen)"]}, "immutable: 'pkg.record(frozen)' is not an outside name",
                 id="a keyword with no value"),
    pytest.param({"immutable": ["pkg.record(2x=yes)"]}, "immutable: 'pkg.record(2x=yes)' is not an outside name",
                 id="a keyword that is no name of the language"),
    pytest.param({"package": "[a-"}, "package: must be a regular expression: ",
                 id="a package that is no regular expression, and no list checked after it"),
    pytest.param({"member": "a b"}, "member: must be a non-empty string with no space", id="a member with a space"),
    pytest.param({"member": ""}, "member: must be a non-empty string with no space", id="an empty member"),
    pytest.param({"member": 3}, "member: must be a non-empty string with no space", id="a member that is no text"),
```

(That test already asserts the document has exactly one problem, so a refused `name`, `package` or `member` adding no
follow-on list problem is pinned by it: T9.)

Rename `test_what_makes_a_class_an_immutable_record_is_read_as_a_dotted_name_and_the_keywords_a_decorator_is_called_with`
to `test_what_makes_a_class_an_immutable_record_is_read_as_an_outside_name_and_the_keywords_a_decorator_is_called_with`
(body unchanged).

Append:

```python
@pytest.mark.parametrize("given", [
    pytest.param(["name"], id="a name alone"),
    pytest.param(["package"], id="a package alone"),
    pytest.param(["member"], id="a member alone"),
    pytest.param(["name", "package"], id="no member"),
    pytest.param(["name", "member"], id="no package"),
    pytest.param(["package", "member"], id="no name"),
])
def test_name_package_and_member_are_given_together(given):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", UNJOINED | {key: JOINS[key] for key in given})
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        f"missing `{key}`: name, package and member are given together" for key in ("name", "package", "member")
        if key not in given]


def test_the_lists_of_a_language_are_read_by_its_own_patterns():
    language = language_of("percent", DOCUMENT | PERCENT)
    assert (language.namespace, language.checked.interface, language.checked.dynamic, language.checked.immutable) == (
        "%SYSTEM", (("%RegisteredObject",),), (("%SYSTEM", "OBJ", "Load"),),
        (RecordMark(("%SerialObject",)), RecordMark(("%Lib", "Rec"), (("frozen", "yes"),))))


def test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them():
    python = {"name": r"(?!\d)\w+", "package": r"(?!\d)\w+", "member": "."}
    lists = {key: PERCENT[key] for key in ("interface", "dynamic", "immutable")}
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | lists | python)
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        "interface: '%RegisteredObject' is not an outside name such as <package>.<name>",
        "dynamic: '%SYSTEM.OBJ.Load' is not an outside name such as <package>.<name>",
        "immutable: '%SerialObject' is not an outside name such as <package>.<name>, or one called with keywords such as "
        "<package>.<name>(<name>=<value>)",
        "immutable: '%Lib.Rec(frozen=yes)' is not an outside name such as <package>.<name>, or one called with keywords "
        "such as <package>.<name>(<name>=<value>)"]


def test_a_document_that_gives_none_of_name_package_and_member_reads_an_outside_name_as_its_whole_text():
    assert language_of("pascal", UNJOINED).checked.interface == (("sys.Contract",),)


def test_a_namespace_is_a_name_the_language_allows():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"namespace": "2sys"})
    assert caught.value.problems == ("presets/language/odd.yaml: namespace: must be a name",)
```

In `tests/modules/spec/application/test_language.py`:

Add `JOINS = {"name": r"\w+", "package": r"\w+", "member": "."}` above `PASCAL`, and end both document literals with
`| JOINS`:

```python
JOINS = {"name": r"\w+", "package": r"\w+", "member": "."}
PASCAL = {"title": "Pascal", "extension": ".pas", "package_file": "unit.pas", "interface": ["sys.Contract"],
          "dynamic": ["sys.load"], "namespace": "system", "standard": "interpreter"} | JOINS
PYTHON = {"title": "Python", "extension": ".py", "package_file": "__init__.py", "interface": ["typing.Protocol"],
          "namespace": "builtins", "cache": "__pycache__", "standard": "interpreter"} | JOINS
```

and give each expected `CheckedLanguage` built from one of them `names=r"\w+", package=r"\w+", member="."`:

```python
    assert view(BASE, {"python": PYTHON, "pascal": PASCAL}) == CheckedLanguage(
        "Pascal", ".pas", "unit.pas", (("sys", "Contract"),), (("sys", "load"),), names=r"\w+", package=r"\w+", member=".")
```

```python
    assert spec.profile("base").language == CheckedLanguage("Python", ".py", "__init__.py", (("typing", "Protocol"),), (),
                                                            names=r"\w+", package=r"\w+", member=".")
```

```python
    pytest.param({"python": PYTHON}, CheckedLanguage("Python", ".py", "__init__.py", (("typing", "Protocol"),),
                                                     names=r"\w+", package=r"\w+", member="."),
                 id="with one, it is that one"),
```

Append to the same file (T14; add `from tests.modules.spec.languages import PYTHON as BUNDLED` and
`from xarch.profile_values.language import CheckedLanguage, RecordMark` to the imports):

```python
def test_the_bundled_language_gives_its_package_pattern_and_its_member_and_reads_its_lists_as_before():
    checked = BUNDLED.checked
    assert (checked.package, checked.member, checked.interface, checked.dynamic, checked.immutable, BUNDLED.namespace) == (
        r"(?!\d)\w+", ".", (("typing", "Protocol"), ("typing_extensions", "Protocol")),
        (("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
        (RecordMark(("typing", "NamedTuple")), RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
        "builtins")
```

In `tests/architecture/test_language_seam.py` add, after the `LANGUAGE` constant:

```python
TEST_LANGUAGES = tuple(sorted((Path(__file__).resolve().parents[1] / "fakes" / "languages").glob("*.yaml")))
"""The test-only languages, which no profile names: each loads, and the guard reads its words; later steps extend
them."""
```

and, after `test_the_words_are_read_from_the_data_file_of_the_language`, append:

```python
def test_the_test_only_languages_are_the_brace_and_the_percent_ones():
    assert [path.stem for path in TEST_LANGUAGES] == ["brace", "percent"]


@pytest.mark.parametrize("language", TEST_LANGUAGES, ids=lambda path: path.stem)
def test_a_test_only_language_loads_and_the_guard_reads_its_words(language):
    loaded = language_of(language.stem, yaml.safe_load(language.read_text(encoding="utf-8")))
    steps = {step for name in (*loaded.checked.interface, *loaded.checked.dynamic) for step in name}
    expected = {loaded.checked.title, loaded.namespace, *steps}
    pattern, _ = language_words(language)
    assert {match[0] for match in pattern.finditer(" ".join(sorted(expected)))} == expected
```

with the import `from xarch.modules.spec.application.logic.language_file import language_of` (sorted after
`from xarch.kernel.logic.names import outside_steps`, which Step 3 adds).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py tests/architecture/test_language_seam.py -q`
Expected: FAIL — the first `test_language_file` test (unknown keys `member`, `package`), the broken-document list,
the together/percent/namespace tests, T14 (`AssertionError` on `''` package), and the seam's
`test_the_test_only_languages_are_the_brace_and_the_percent_ones` (`[] == ['brace', 'percent']`).

- [ ] **Step 3: Write the implementation**

**3a. `xarch/modules/spec/application/logic/language_file.py`.** In the module docstring, replace the lines for
`interface` and `dynamic`:

```
    interface      outside names (see below), any of which among a class's bases marks it as an interface
    dynamic        outside names of what imports by a name worked out when the code runs; optional
    namespace      the namespace of the names the language binds without an import: a name
```

(the old `namespace` line is replaced by the last of these three), replace the `name` line of the tokens list with

```
    name           a regular expression: what a name may be
    package        a regular expression: what an import names from outside the app as one step
    member         the text that joins a package to a name in it in a profile's lists; name, package and member
                   are given together, and an outside name is written <package> or <package><member><name>, more
                   names after the first joined by `.`. Left out together, any text is a name and an outside name is
                   its whole text
```

and the `immutable` lines with

```
    immutable      what makes a class an immutable record: each an outside name among its bases or its decorators,
                   a decorator's written with the keywords it must be called with, `name(key=value, ...)`
```

Replace the imports and constants block (lines 43-64) with:

```python
import re
from collections.abc import Iterable, Mapping
from typing import Any

from xarch.kernel.logic.names import is_name, outside_name
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import LANGUAGES, Language
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
from xarch.profile_values.language import CheckedLanguage, RecordMark

KEYS = ("title", "extension", "package_file", "interface", "dynamic", "namespace", "cache", "standard", "name", "package",
        "member", "private", "special", "call", "nothing", "comment", "directives", "shebang", "encoding", "branching",
        "importing", "supplies", "immutable", "branching_expressions")
REQUIRED = ("title", "extension", "package_file", "namespace", "standard")
JOINED = ("name", "package", "member")
"""The keys that say how an outside name is written: given together or not at all."""
_EXTENSION = re.compile(r"\.[A-Za-z0-9]+")
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PARTIAL = "partial"
"""How the data file grades a fact its reader supplies only partly, with what it misses."""
_FOLDER = re.compile(r"[A-Za-z0-9_.-]+")
_IMPORTING = re.compile(r"(?=[^\n]*\{dotted\})(?=[^\n]*\{name\})[^\n]+")
_MEMBER = re.compile(r"\S+")
_CALLED = re.compile(r"(?P<path>[^()]+)(?:\((?P<keywords>[^()]*)\))?")
_VALUE = re.compile(r"[^,()=]+")
```

(`_DOTTED` and `_MARK` are gone.) Replace `language_of` with:

```python
def language_of(name: str, document: Any) -> Language:
    """The language the document of the preset called name describes; raises InvalidArchitecture."""
    source = f"{LANGUAGES}/{name}.yaml"
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys, such as title, extension and package_file"])
    problems: list[str] = []
    unknown = sorted(str(key) for key in document if key not in KEYS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {', '.join(f'{key!r}' for key in unknown)}: "
                        f"use {', '.join(sorted(KEYS))}")
    problems += [f"missing `{key}`" for key in REQUIRED if key not in document]
    joins = _joins(document, problems)
    names, package, member = joins or ("", "", "")
    title = _text(document, "title", "must be a non-empty string", problems)
    extension = _text(document, "extension", "must be a dot and a name, such as .pas", problems, _EXTENSION)
    package_file = _text(document, "package_file", "must be a file name ending in the extension", problems)
    if package_file and not (extension and package_file.endswith(extension) and package_file != extension):
        problems.append("package_file: must be a file name ending in the extension")
    namespace = _text(document, "namespace", "must be a name", problems)
    if namespace and not is_name(namespace, names):
        problems.append("namespace: must be a name")
        namespace = ""
    interface = _outside(document, "interface", problems, joins, namespace)
    dynamic = _outside(document, "dynamic", problems, joins, namespace)
    standard = _text(document, "standard", "must be a name", problems, _WORD)
    cache = _text(document, "cache", "must be a folder name", problems, _FOLDER)
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "special", "call", "nothing", "comment", "shebang")}
    encoding = _pattern(document, "encoding", problems)
    directives = _words(document, "directives", problems)
    branching = _words(document, "branching", problems)
    expressions = _words(document, "branching_expressions", problems)
    importing = _text(document, "importing", "must be a line holding {dotted} and {name}", problems, _IMPORTING)
    supplies = _supplies(document["supplies"], problems) if "supplies" in document else None
    immutable = _marks(document, problems, joins, namespace)
    if problems:
        raise InvalidArchitecture(source, problems)
    checked = CheckedLanguage(title, extension, package_file, interface, dynamic, tokens["private"], tokens["special"],
                              tokens["call"], tokens["nothing"], tokens["comment"], directives, tokens["shebang"],
                              encoding, branching, supplies, importing, immutable, expressions, names, package, member)
    return Language(name, checked, namespace, standard, cache, names)


def _joins(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, str, str] | None:
    """The pattern of a name, the pattern of a package and the member that joins a name to it: ("", "", "") when the
    document gives none of them, None when it gives one wrong or not all three."""
    count = len(problems)
    names = _pattern(document, "name", problems)
    package = _pattern(document, "package", problems)
    member = _text(document, "member", "must be a non-empty string with no space", problems, _MEMBER)
    if any(key in document for key in JOINED):
        problems += [f"missing `{key}`: name, package and member are given together" for key in JOINED
                     if key not in document]
    return (names, package, member) if len(problems) == count else None
```

Replace `_dotted` with:

```python
def _outside(document: Mapping[Any, Any], key: str, problems: list[str], joins: tuple[str, str, str] | None,
             namespace: str) -> tuple[tuple[str, ...], ...]:
    """The outside names listed at key, each as its steps; none read when the keys that say how one is written are
    refused already (joins None)."""
    if key not in document or joins is None:
        return ()
    names, package, member = joins
    such = f"<package>{member}<name>"
    value = document[key]
    if not isinstance(value, list):
        problems.append(f"{key}: must be a list of outside names, such as [{such}]")
        return ()
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = outside_name(item, names, package, member, namespace) if isinstance(item, str) else None
        if steps is None:
            problems.append(f"{key}: {item!r} is not an outside name such as {such}")
        else:
            found.append(steps)
    return tuple(found)
```

Replace `_marks` with:

```python
def _marks(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
           namespace: str) -> tuple[RecordMark, ...]:
    if "immutable" not in document or joins is None:
        return ()
    such = f"<package>{joins[2]}<name>"
    value = document["immutable"]
    if not isinstance(value, list):
        problems.append(f"immutable: must be a list of outside names, each perhaps called with keywords, such as "
                        f"[{such}, \"{such}(<name>=<value>)\"]")
        return ()
    found: list[RecordMark] = []
    for item in value:
        mark = _mark(item, joins, namespace) if isinstance(item, str) else None
        if mark is None:
            problems.append(f"immutable: {item!r} is not an outside name such as {such}, or one called with keywords "
                            f"such as {such}(<name>=<value>)")
        else:
            found.append(mark)
    return tuple(found)


def _mark(item: str, joins: tuple[str, str, str], namespace: str) -> RecordMark | None:
    """One mark of an immutable record: an outside name, perhaps called with keywords, `name(key=value, ...)`, each key a
    name of the language and each value plain text; None when the text is none."""
    names, package, member = joins
    called = _CALLED.fullmatch(item)
    path = outside_name(called["path"], names, package, member, namespace) if called is not None else None
    if called is None or path is None:
        return None
    if called["keywords"] is None:
        return RecordMark(path)
    pairs = [pair.partition("=") for pair in called["keywords"].split(",")]
    if not all(sep and is_name(key.strip(), names) and _VALUE.fullmatch(value.strip()) for key, sep, value in pairs):
        return None
    return RecordMark(path, tuple((key.strip(), value.strip()) for key, _, value in pairs))
```

**3b. `xarch/architectures/presets/language/python.yaml`.** Replace the comment line

```
# need: name, what a name may be (a regular expression); private, how a name starts that is private to its file or
```

with

```
# need: name, what a name may be (a regular expression); package, what an import names from outside the app as one
# step (a regular expression); member, the text that joins a package to a name in it in a profile's lists (name,
# package and member are given together); private, how a name starts that is private to its file or
```

and right after `name: '(?!\d)\w+'` add

```yaml
package: '(?!\d)\w+'
member: "."
```

No other line of the file changes (`git diff --stat` of it shows 5 insertions, 1 deletion: the comment line becomes three, and two keys are added).

**3c. `tests/fakes/languages/brace.yaml`** (create):

```yaml
# A test-only language that imitates a TypeScript-like one: no profile names it and no reader is written for it. Its
# packages are named as a package manager names them (a scope, a dash, a dot) or as its runtime's own modules
# (node:fs), and a name in one is joined to it by #. The tests load it to show that the profile and the checks read
# outside names by a language's own patterns; later steps add their keys to it.
title: Brace
extension: .ts
package_file: index.ts
namespace: globalThis
standard: interpreter
name: '[A-Za-z_$][A-Za-z0-9_$]*'
package: '(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*|node:[a-z_/]+'
member: "#"
dynamic: ["node:module#createRequire"]
```

**3d. `tests/fakes/languages/percent.yaml`** (create):

```yaml
# A test-only language that imitates an ObjectScript-like one: no profile names it and no reader is written for it.
# Its names and packages may start with %, and a name in a package is joined to it by a dot. The tests load it to show
# that the profile and the checks read outside names by a language's own patterns; later steps add their keys to it.
title: Percent
extension: .cls
package_file: Package.cls
namespace: "%SYSTEM"
standard: interpreter
name: '%?[A-Za-z][A-Za-z0-9]*'
package: '%?[A-Za-z][A-Za-z0-9]*'
member: "."
interface: ["%Library.RegisteredObject"]
dynamic: ["%SYSTEM.OBJ.Load"]
immutable: ["%SerialObject"]
```

**3e. `tests/modules/spec/languages.py`.** Change the module docstring's first sentence to "The data file of the
language the tests' sources are written in, as the bundled preset says it, and the language it reads into; and the two
test-only languages of tests/fakes/languages/, which no profile names: the builders of every module's tests share
them." Add `from pathlib import Path` to the imports and append:

```python
TEST_LANGUAGES = Path(__file__).resolve().parents[2] / "fakes" / "languages"
BRACE = replace(language_of("brace", yaml.safe_load((TEST_LANGUAGES / "brace.yaml").read_text(encoding="utf-8"))),
                builtin_names=frozenset({"fetch"}))
"""The TypeScript-like test-only language; `fetch` is its one builtin, for the hint a bare builtin is given."""
PERCENT = language_of("percent", yaml.safe_load((TEST_LANGUAGES / "percent.yaml").read_text(encoding="utf-8")))
"""The ObjectScript-like test-only language."""
```

**3f. `tests/architecture/test_language_seam.py`.** Add `from xarch.kernel.logic.names import outside_steps` and
`from xarch.modules.spec.application.logic.language_file import language_of` to the imports (after
`import xarch`, sorted). Replace the first three lines of `language_words`' body with:

```python
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    steps = {step for name in (*data.get("interface", ()), *data.get("dynamic", ()))
             for step in outside_steps(name, data.get("member", ""))}
    words = {word for word in (data["namespace"], data.get("cache", ""), data["package_file"].removesuffix(data["extension"]),
                               *steps, *WORDS_BESIDES) if word}
```

(the rest of the function is unchanged; an empty word would make the pattern match everywhere, so it is dropped). In
the module docstring, change "every step of the names that mark an interface and of those that import by a computed
name" to "every step of the names that mark an interface and of those that import by a computed name, split at the
data file's member". `member` is not added to `TOKEN_KEYS`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py tests/architecture/test_language_seam.py tests/kernel -q`
Expected: all PASS.

Then the whole spec module and the bootstrap tier, which load `python.yaml`:
Run: `timeout 900 uv run pytest tests/modules/spec tests/bootstrap -q -x`
Expected: PASS. (Under Python every list reads as before; a failure here is a defect of this task: read it, do not
edit a pin.)

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check xarch/modules/spec/application/logic/language_file.py tests/modules/spec tests/architecture/test_language_seam.py
git add xarch/modules/spec/application/logic/language_file.py xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml tests/modules/spec/languages.py tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py tests/architecture/test_language_seam.py
git commit -m "A language's data file gives package and member with name, all three or none, and its namespace, interface, dynamic and immutable are read by them as outside names, <package><member><name>, refused as not an outside name such as <package><member><name>; python.yaml gains package and member and reads as before; two test-only languages, brace and percent, load, and the seam guard reads their words

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The profile reads its outside names by the language's patterns and member

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (lines 33-47, 361-418, 433, 461, 483-486, 521, 568-636, 655)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (imports; lines 535-538, 690, 830)
- Test: `tests/modules/spec/application/logic/test_profile_checks.py`
- Test: `tests/modules/spec/application/logic/test_never_use.py`
- Test: `tests/modules/spec/application/logic/test_libraries_and_guards.py`
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`
- Test: `tests/modules/spec/application/logic/test_testing.py`

**Interfaces:**
- Consumes: `names.outside_name`, `names.outside_text`, `names.is_name` (Task 1); `Language.checked.package`,
  `Language.checked.member` (Tasks 1-2); `tests.modules.spec.languages.BRACE` (Task 2).
- Produces (in `profile_checks.py`):
  - `outside_name_at(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, ...] | None`
  - `outside_names(value: Any, where: str, problems: list[str], language: Language) -> tuple[tuple[str, ...], ...] | None`
  - `never_names(...)` and `package_names(...)`, `reserved_modules(...)` keep their signatures.
  - Deleted: `is_name`, `_is_dotted`, `_dotted`, `dotted_names`.

- [ ] **Step 1: Write the failing tests**

**1a.** Replace the top of `tests/modules/spec/application/logic/test_profile_checks.py` (docstring, imports,
constants, and every test in the file) with:

```python
"""What a profile may write as a name of the checked language: a name as its data file says one is, an outside name
read by its package pattern and its member, and a method called on anything, on the bundled language, on a hand-made
one whose names may hold a dash, and on a test-only one whose member is not a dot."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import BRACE, PYTHON
from xarch.kernel.logic.names import is_name
from xarch.modules.spec.application.logic.profile_checks import never_names, outside_names

DASHED = replace(PYTHON, names="[a-z][a-z-]*")
NOT_OUTSIDE = "is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()"


def forbidding(item: str) -> tuple[tuple[tuple[str, ...], ...] | None, list[str]]:
    """What a `never` list of the one item comes to: the names it bans, and every problem."""
    problems: list[str] = []
    return never_names([item], "at", problems, PYTHON), problems


@pytest.mark.parametrize("text, language, name", [
    pytest.param("sqlmodel", PYTHON, True, id="a name of the language"),
    pytest.param("2fast", PYTHON, False, id="the language says a name does not start with a digit"),
    pytest.param("web-kit", PYTHON, False, id="nor holds a dash"),
    pytest.param("web-kit", DASHED, True, id="another language may say it does"),
    pytest.param("anything at all", replace(PYTHON, names=""), True, id="a language that says nothing allows any text"),
    pytest.param("", replace(PYTHON, names=""), False, id="but nothing"),
])
def test_a_name_is_what_the_language_says_one_is(text, language, name):
    assert is_name(text, language.names) is name


@pytest.mark.parametrize("text, found", [
    pytest.param("socket", ((("socket",),), []), id="a package alone"),
    pytest.param("datetime.datetime.now", ((("datetime", "datetime", "now"),), []), id="a package and names after it"),
    pytest.param("pytest..param", ((), [f"at: 'pytest..param' {NOT_OUTSIDE}"]), id="an empty step"),
    pytest.param("pkg.2x", ((), [f"at: 'pkg.2x' {NOT_OUTSIDE}"]), id="a step that is no name"),
])
def test_an_outside_name_is_a_package_then_names_of_the_language_after_its_member(text, found):
    assert forbidding(text) == found


def test_one_step_is_not_enough_where_two_are_wanted():
    problems: list[str] = []
    assert (outside_names(["socket"], "at", problems, PYTHON), problems) == (
        (), ["at: 'socket' is not an outside name such as <package>.<name>"])


def test_an_outside_name_of_another_language_is_read_by_its_member():
    problems: list[str] = []
    assert (outside_names(["node:test#skip"], "testing.skips", problems, BRACE), problems) == (
        (("node:test", "skip"),), [])


@pytest.mark.parametrize("item, found", [
    pytest.param(".absolute()", (((("", "absolute()"),), [])), id="a method called on anything"),
    pytest.param(".absolute", ((), ["at: '.absolute' is neither an outside name nor a method: write .absolute() for a "
                                     "method called on anything"]), id="without its parentheses it is none"),
    pytest.param("path.absolute()", ((), [f"at: 'path.absolute()' {NOT_OUTSIDE}"]), id="nor on a name"),
    pytest.param(".a.b()", ((), [f"at: '.a.b()' {NOT_OUTSIDE}"]), id="nor of two steps"),
])
def test_a_method_of_a_forbidden_list_is_named_by_what_lies_between_the_dot_and_the_parentheses(item, found):
    assert forbidding(item) == found
```

**1b.** In `tests/modules/spec/application/logic/test_never_use.py`:

Replace the two constants

```python
DOTTED = "is not a dotted name such as datetime.datetime.now, nor an import name such as socket"
METHOD = f"{DOTTED}, nor a method such as .absolute()"
```

with

```python
METHOD = "is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()"
```

Replace the `.absolute` row of `test_a_bad_method_is_refused_saying_what_to_write` with:

```python
    pytest.param(".absolute", "never.pure: '.absolute' is neither an outside name nor a method: write .absolute() for "
                              "a method called on anything", id="a method without its parentheses"),
```

Change the import line to `from tests.modules.spec.languages import BRACE` plus the existing
`from tests.modules.spec.profiles import covered, layered, parsed, problems`, and append:

```python
BRACED = {"brace": BRACE}


def brace_document(ambient=("node:fs#readFileSync", "globalThis#fetch", ".toISOString()"),
                   libraries=("lodash-es", "@scope/pkg")) -> dict:
    """The layered profile as an app in the brace language writes it: its store's outside packages by the language's
    package names, and a list of outside names under `never`, which its service part never uses."""
    document = layered(never={"ambient": list(ambient)})
    document["parts"]["store"]["libraries"] = list(libraries)
    document["parts"]["service"]["uses"] = {"never": "ambient"}
    return document


def test_outside_names_are_read_by_the_package_pattern_and_the_member_of_the_language():
    architecture = parsed(brace_document(), languages=BRACED)
    assert (architecture.libraries["store"], architecture.uses_never) == (
        ("lodash-es", "@scope/pkg"),
        {"service": (("node:fs", "readFileSync"), ("globalThis", "fetch"), ("", "toISOString()"))})


def test_the_same_outside_names_are_refused_under_a_language_whose_patterns_do_not_allow_them():
    assert problems(brace_document()) == [
        f"layered.yaml: never.ambient: 'node:fs#readFileSync' {METHOD}",
        f"layered.yaml: never.ambient: 'globalThis#fetch' {METHOD}",
        "layered.yaml: parts.store.libraries: 'lodash-es' is not a package name the language Python allows",
        "layered.yaml: parts.store.libraries: '@scope/pkg' is not a package name the language Python allows"]


def test_a_bare_builtin_is_told_to_be_written_in_the_namespace_with_the_member_of_the_language():
    assert problems(brace_document(ambient=["fetch"]), languages=BRACED) == [
        "layered.yaml: never.ambient: 'fetch' is a Brace builtin, which a bare name does not ban: write globalThis#fetch"]


@pytest.mark.parametrize("entry", [
    pytest.param("node:fs#", id="a member with nothing after it"),
    pytest.param("#readFileSync", id="nothing before the member"),
    pytest.param("Fs#readFileSync", id="a head that is neither a package nor the namespace"),
])
def test_an_outside_name_the_language_s_patterns_refuse_is_refused_under_that_language(entry):
    assert problems(brace_document(ambient=[entry]), languages=BRACED) == [
        f"layered.yaml: never.ambient: '{entry}' is not an outside name such as <package>#<name>, nor a package, nor a "
        "method such as .<name>()"]


def test_an_outside_name_listed_twice_is_refused_once_under_a_member_that_is_not_a_dot():
    assert problems(brace_document(ambient=["node:fs#readFileSync", "node:fs#readFileSync"]), languages=BRACED) == [
        "layered.yaml: never.ambient: 'node:fs#readFileSync' is listed twice"]


def test_a_package_is_never_the_namespace_of_the_language():
    assert problems(brace_document(libraries=["globalThis"]), languages=BRACED) == [
        "layered.yaml: parts.store.libraries: 'globalThis' is not a package name the language Brace allows"]


def test_the_guards_section_writes_an_outside_name_with_the_member_of_the_language():
    text = fill("{{guards}}", parsed(brace_document(), languages=BRACED), "layered.md", file_types=FILE_TYPES)
    assert "(`service/`: `node:fs#readFileSync`, `globalThis#fetch`, `.toISOString()`)" in text
```

(The last test turns green only in Task 4, which prints through `outside_text`; today `docs_template` joins with
`.`. Leave it RED at the end of this task and say so in the task report.)

**1c.** In `tests/modules/spec/application/logic/test_libraries_and_guards.py`:

Replace `"layered.yaml: parts.store.libraries: 'sql-model' is not a top-level import name, such as sqlmodel"]` with
`"layered.yaml: parts.store.libraries: 'sql-model' is not a package name the language Python allows"]`, and
`"reserved: 'os.path' is not a top-level import name, such as ast",` with
`"reserved: 'os.path' is not a package name the language Python allows",`. Append:

```python
@pytest.mark.parametrize("library", [
    pytest.param("lodash-es", id="a package name with a dash"),
    pytest.param("@scope/pkg", id="a scoped package name"),
])
def test_a_library_the_package_pattern_of_the_language_refuses_is_refused_naming_the_language(library):
    document = layered()
    document["parts"]["store"]["libraries"] = [library]
    assert problems(document) == [
        f"layered.yaml: parts.store.libraries: '{library}' is not a package name the language Python allows"]
```

**1d.** In `tests/modules/spec/application/logic/test_profile_parsing.py`: replace
`"layered.yaml: parts.store.libraries: 'a.b' is not a top-level import name, such as sqlmodel",` with
`"layered.yaml: parts.store.libraries: 'a.b' is not a package name the language Python allows",`, and

```python
    pytest.param({"pure": []}, "pure", ["layered.yaml: never.pure: must be a non-empty list of dotted names or "
                                        "import names, such as [datetime.datetime.now, socket]"], id="an empty list"),
```

with

```python
    pytest.param({"pure": []}, "pure", ["layered.yaml: never.pure: must be a non-empty list of outside names, packages "
                                        "or methods, such as [<package>.<name>, <package>, .<name>()]"], id="an empty list"),
```

(The `never:` mapping text and the `libraries` shape texts stay as they are.)

**1e.** In `test_profile_parsing_tests.py` and `test_testing.py` (both under
`tests/modules/spec/application/logic/`), replace every occurrence of the two texts:

```bash
sed -i 's/is not a dotted name such as pkg\.sub\.name/is not an outside name such as <package>.<name>/g; s/must be a list of dotted names such as pkg\.sub\.Name/must be a list of outside names such as <package>.<name>/g' tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_testing.py
grep -c "outside name" tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_testing.py
```

Expected counts: `test_profile_parsing_tests.py:3`, `test_testing.py:6`. Listed-twice pins (`never` `[socket, socket]`
in `test_profile_parsing.py`, skips `["a.b", "a.b"]` and mocks `["a.B", "a.B"]` in `test_testing.py`) stay as they
are: they are T19, compared on steps now.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic -q`
Expected: collection ERROR for `test_profile_checks.py` (`ImportError: cannot import name 'outside_names'`) and FAILs
on every repinned text (the code still says `dotted name` / `top-level import name`) and on the brace tests.

- [ ] **Step 3: Write the implementation**

In `xarch/modules/spec/application/logic/profile_checks.py`:

Replace lines 33-47 (`is_name`, `_is_dotted`, `_method_name`) with:

```python
def _outside(text: str, language: Language, namespace: str = "") -> tuple[str, ...] | None:
    """The steps of an outside name as the language writes one (see names.outside_name); None when the text is none."""
    return names.outside_name(text, language.names, language.checked.package, language.checked.member, namespace)


def _such(language: Language) -> str:
    """How a message shows an outside name of the language: <package>, its member, <name>."""
    return f"<package>{language.checked.member}<name>"


def _is_package(text: Any, language: Language) -> bool:
    """Whether text names a package alone, as the language's package pattern says one is; never its namespace."""
    steps = _outside(text, language) if isinstance(text, str) else None
    return steps is not None and len(steps) == 1


def _method_name(item: str, language: Language) -> str | None:
    """The name of the method an item of a `never` list names, `.<name>()`; None when it names none."""
    name = item[1:-len(CALLED)] if item.startswith(".") and item.endswith(CALLED) else ""
    return name if names.is_name(name, language.names) else None
```

Replace each remaining single-name call (rule 14; the texts do not change):

| line | old | new |
|---|---|---|
| 372 | `is_name(value["id"], language)` | `names.is_name(value["id"], language.names)` |
| 376 | `is_name(k, language)` | `names.is_name(k, language.names)` |
| 433 | `not is_name(name, language)` | `not names.is_name(name, language.names)` |
| 461 | `not is_name(item, language)` | `not names.is_name(item, language.names)` |
| 486 | `is_name(functions.replace("*", "x"), language)` | `names.is_name(functions.replace("*", "x"), language.names)` |
| 521 | `if not is_name(name, language):` | `if not names.is_name(name, language.names):` |
| 655 | `not is_name(suffix, language)` | `not names.is_name(suffix, language.names)` |

In `case_table` (lines 370-371) write `outside_name_at` for `_dotted`:

```python
    decorator = outside_name_at(value["decorator"], f"{where}.decorator", problems, language) if "decorator" in value else None
    row = outside_name_at(value["row"], f"{where}.row", problems, language) if "row" in value else None
```

Replace `_dotted` and `dotted_names` (lines 399-418) with:

```python
def outside_name_at(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, ...] | None:
    """An outside name of at least two steps, <package><member><name>: the path an import binds."""
    steps = _outside(value, language) if isinstance(value, str) else None
    if steps is None or len(steps) < 2:
        problems.append(f"{where}: {value!r} is not an outside name such as {_such(language)}")
        return None
    return steps


def outside_names(value: Any, where: str, problems: list[str], language: Language) -> tuple[tuple[str, ...], ...] | None:
    """A non-empty list of outside names of at least two steps, each once."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of outside names such as {_such(language)}")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = outside_name_at(item, where, problems, language)
        if steps is not None and steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        elif steps is not None:
            found.append(steps)
    return tuple(found)
```

In `framework_patterns` (line 483): `skips = outside_names(value["skips"], f"{where}.skips", problems, language) if "skips" in value else ()`.

In `reserved_modules`, replace the first branch

```python
        if not isinstance(name, str) or not is_name(name, language):
            problems.append(f"reserved: {name!r} is not a top-level import name, such as ast")
```

with

```python
        if not _is_package(name, language):
            problems.append(f"reserved: {name!r} is not a package name the language {language.checked.title} allows")
```

In `package_names`, replace

```python
        if not isinstance(package, str) or not is_name(package, language):
            problems.append(f"{where}: {package!r} is not a top-level import name, such as sqlmodel")
```

with

```python
        if not _is_package(package, language):
            problems.append(f"{where}: {package!r} is not a package name the language {language.checked.title} allows")
```

Replace `never_names` with:

```python
def never_names(value: Any, where: str, problems: list[str],
                language: Language) -> tuple[tuple[str, ...], ...] | None:
    """The names a part may not use: outside names, <package><member><name>, or packages alone, read by the language's
    patterns; a builtin is written in the language's namespace for them, <namespace><member><name>. A method called on
    anything is written `.<name>()` and kept as written, split at its dot: ("", "<name>()")."""
    member = language.checked.member
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of outside names, packages or methods, such as "
                        f"[{_such(language)}, <package>, .<name>()]")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        method = _method_name(item, language) if isinstance(item, str) else None
        steps = (("", f"{method}{CALLED}") if method is not None
                 else _outside(item, language, language.namespace) if isinstance(item, str) else None)
        if method is not None and language.checked.is_special(method):
            problems.append(f"{where}: {item!r} is a special method, which no code calls by name")
        elif method is None and isinstance(item, str) and item.startswith(".") and names.is_name(item[1:], language.names):
            problems.append(f"{where}: {item!r} is neither an outside name nor a method: write {item}() for a method "
                            "called on anything")
        elif steps is None:
            problems.append(f"{where}: {item!r} is not an outside name such as {_such(language)}, nor a package, nor a "
                            "method such as .<name>()")
        elif len(steps) == 1 and item in language.builtin_names:
            problems.append(f"{where}: {item!r} is a {language.checked.title} builtin, which a bare name does not ban: "
                            f"write {language.namespace}{member}{item}")
        elif steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(steps)
    return tuple(found)
```

In `xarch/modules/spec/application/logic/profile_parsing.py`:
- add `from xarch.kernel.logic.names import is_name, outside_text` to the imports (between
  `from collections.abc ...`/`typing` block and `from xarch.kernel.logic.placement import root_of`, sorted);
- lines 535-538:

```python
    calls = ck.outside_names(value["calls"], f"{where}.calls", problems, language) if "calls" in value else None
    autospec = ck.outside_names(value["autospec"], f"{where}.autospec", problems, language) if "autospec" in value else ()
    problems += [f"{where}.autospec: {outside_text(name, language.checked.member)!r} is also listed in calls"
                 for name in autospec or () if calls and name in calls]
```

- line 690: `ck.is_name(prefix, language)` → `is_name(prefix, language.names)`;
- line 830: `not ck.is_name(name, language)` → `not is_name(name, language.names)`.

Then check nothing else calls the deleted names:

```bash
grep -rn "ck\.is_name\|ck\.dotted_names\|profile_checks import.*\(is_name\|dotted_names\)\|_is_dotted" xarch tests
```

Expected: no output.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/spec -q`
Expected: all PASS but `test_never_use.py::test_the_guards_section_writes_an_outside_name_with_the_member_of_the_language`
(green in Task 4).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check xarch/modules/spec tests/modules/spec
git add xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_profile_checks.py tests/modules/spec/application/logic/test_never_use.py tests/modules/spec/application/logic/test_libraries_and_guards.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_testing.py
git commit -m "A profile reads its outside names by the language's package pattern and member: libraries and reserved as a package alone, refused as not a package name the language <title> allows; the testing names as outside names of two steps or more, refused as not an outside name such as <package><member><name>; never entries as outside names, packages or .<name>() methods, a bare builtin told to write <namespace><member><name>; each listed twice compared on its steps; under Python every entry reads as before

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Every outside name is split and printed with the language's member

**Files:**
- Modify: `xarch/modules/rules/application/logic/own_checks.py:119-120` (and imports)
- Modify: `xarch/modules/rules/application/logic/sentences.py:57-66, 80-81` (and imports)
- Modify: `xarch/modules/rules/application/logic/written.py:24-27, 51-56, 73-88` (and imports)
- Modify: `xarch/modules/rules/application/services/explaining.py:80, 117`
- Modify: `xarch/modules/rules/application/logic/where.py:105, 201` (and imports)
- Modify: `xarch/modules/spec/application/logic/looseness.py:55-91` (and imports)
- Modify: `xarch/modules/spec/application/logic/docs_template.py:450-455` (and imports)
- Modify: `xarch/modules/spec/application/logic/explain.py:33` (and imports)
- Modify: `tests/modules/rules/builders.py:27-37`
- Test: `tests/modules/rules/application/logic/test_never_use.py`
- Test: `tests/modules/rules/application/logic/test_own_checks.py`
- Test: `tests/modules/rules/application/logic/test_written.py`
- Test: `tests/modules/spec/application/logic/test_profile_keys.py`

**Interfaces:**
- Consumes: `outside_steps`, `outside_text` (Task 1); `CheckedLanguage.member` (rules `Profile.language`),
  `Language.checked.member` (spec `Architecture.language`); `tests.modules.spec.languages.PERCENT` (Task 2).
- Produces:
  - `written.check_of(rule: Rule, member: str, flagged=(), clean=()) -> WrittenCheck`
  - `written.written(rules: Iterable[Rule], member: str) -> dict[str, WrittenCheck]`
  - `tests.modules.rules.builders.BRACE: CheckedLanguage` (title `Brace`, member `#`, read from
    `tests/fakes/languages/brace.yaml`), and `builders.PYTHON` with `package` and `member` read from `python.yaml`.

- [ ] **Step 1: Write the failing tests**

**1a. `tests/modules/rules/builders.py`.** Add `from pathlib import Path` to the imports and replace the `PYTHON`
definition and its docstring (lines 27-37) with:

```python
PYTHON_FILE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                             .read_text(encoding="utf-8"))
PYTHON = CheckedLanguage("Python", ".py", "__init__.py", (("typing", "Protocol"), ("typing_extensions", "Protocol")),
                      (("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
                      "_", "__", "__call__", "None", "#", ("type: ignore", "noqa", "pragma:"), "#!",
                      r"coding[:=][ \t]*[-\w.]+", ("if", "match", "try", "for", "while"),
                      immutable=(RecordMark(("typing", "NamedTuple")),
                                 RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
                      branching_expressions=("if",), names=PYTHON_FILE["name"], package=PYTHON_FILE["package"],
                      member=PYTHON_FILE["member"])
"""Python as its data file says it, for the checks that read the tokens of its code; the patterns of a name and of a
package, and the member that joins them, read from it."""
BRACE_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "brace.yaml")
                            .read_text(encoding="utf-8"))
BRACE = CheckedLanguage(BRACE_FILE["title"], BRACE_FILE["extension"], BRACE_FILE["package_file"], (),
                        (("node:module", "createRequire"),), names=BRACE_FILE["name"], package=BRACE_FILE["package"],
                        member=BRACE_FILE["member"])
"""The TypeScript-like test-only language as a check reads it, its patterns and member read from its data file."""
```

(`sys` stays imported: `builders.py:125` uses it.)

**1b. `tests/modules/rules/application/logic/test_never_use.py`.** Add
`from tests.modules.rules.builders import BRACE, PYTHON` to the imports. Give `PROFILE` and `AMBIENT` the language
(T21; their expected texts do not change): add `language=PYTHON` as the last argument of both `Profile(...)` calls,
e.g.

```python
                  uses_never={"domain": (NOW, ("builtins", "open"), ("socket",), ("urllib",))},
                  framework=Framework(("test_*.py",), "test_*"), language=PYTHON)
```

```python
                  uses_never={"services": (("", "absolute()"), ("", "resolve()"), ("pathlib", "Path", "cwd"))},
                  language=PYTHON)
```

Append (T20):

```python
BRACED = Profile(parts={"adapters": ("modules", "*", "adapters")}, rules={},
                 folders=((), ("modules",), ("modules", "*")),
                 uses_never={"adapters": (("node:fs", "readFileSync"), ("globalThis", "fetch"), ("", "toISOString()"))},
                 language=BRACE)


def test_a_listed_outside_name_of_another_language_is_said_with_its_member():
    file = SourceFile("app/modules/docs/adapters/files.ts", ("modules", "docs", "adapters", "files.ts"), (),
                      uses=(Use(4, ("node:fs", "readFileSync"), 1),))
    (found,) = violations([file], [], BRACED)
    assert (str(found), found.fix) == (
        "app/modules/docs/adapters/files.ts:4: adapters/ of modules/docs may not use node:fs#readFileSync "
        "(parts.adapters.uses.never)",
        "do what needs node:fs#readFileSync outside adapters/, and hand adapters/ the result")
```

**1c. `tests/modules/rules/application/logic/test_own_checks.py`.** Give the toy language a member (T21: it splits a
`path` target today with a hard-coded dot; its expected value does not change):

```python
SUPPLIES = CheckedLanguage("Toy", supplies=(Supply("call", EXACT), Supply("import.resolved", EXACT),
                                            Supply("import", "partial", "no star imports"), Supply("file", EXACT)),
                           member=".")
```

Add `from dataclasses import replace` to the imports (the file does not import it today), and append (Review Focus 5):

```python
def test_a_path_target_is_split_at_the_member_of_the_language_and_a_method_stays_a_method():
    hashed = replace(CHECK, quantified=Quantified(MAY_NOT, (WrittenTarget("path", ("node:fs#readFileSync", ".run()")),
                                                            WrittenTarget("part", ("web",)))))
    (own,) = resolved(profile(language=replace(SUPPLIES, member="#"), written={"no-api": hashed})).checks
    assert own.rule.targets[0].names == (("node:fs", "readFileSync"), ("", "run()"))
```

**1d. `tests/modules/rules/application/logic/test_written.py`.** Pass the member everywhere:
- `check_of(rule).quantified.targets[0].values` → `check_of(rule, ".").quantified.targets[0].values`
- `assert check_of(rule) == check` → `assert check_of(rule, ".") == check`
- in `test_rules_written_as_checks_each_take_an_id_of_their_own`: `written([rule, rule, other])` →
  `written([rule, rule, other], ".")`, `written([rule, other])` → `written([rule, other], ".")`, and every
  `check_of(rule)` / `check_of(other)` there → `check_of(rule, ".")` / `check_of(other, ".")`
- in `test_the_tokens_of_the_language_are_filled_in`: `check_of(rule, (("notes.py", written_out),), ())` →
  `check_of(rule, language.member, (("notes.py", written_out),), ())`

Append:

```python
def test_an_outside_name_is_written_back_with_the_member_of_the_language():
    rule = Rule("x", Scope(), ("use",), MAY_NOT,
                (Match("path", names=(("node:fs", "readFileSync"), ("", "toISOString()"))),), SAID)
    assert check_of(rule, "#").quantified.targets == (WrittenTarget("path", ("node:fs#readFileSync", ".toISOString()")),)
```

**1e. `tests/modules/spec/application/logic/test_profile_keys.py`.** Add `from dataclasses import replace` (not imported
today) and change `from tests.modules.spec.languages import PYTHON` to `... import PERCENT, PYTHON`, and append:

```python
def test_the_path_of_an_interface_is_said_with_the_member_of_the_language():
    hashed = replace(PERCENT, checked=replace(PERCENT.checked, member="#"))
    assert said("`%interface_path%`", hashed) == "`%Library#RegisteredObject`"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/rules/application/logic/test_never_use.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/logic/test_profile_keys.py tests/modules/spec/application/logic/test_never_use.py -q`
Expected: FAIL — T20 (`node:fs.readFileSync` printed), the own-check split (`(("node:fs#readFileSync",), ...)`),
`test_written` (`TypeError` on the extra argument, then `node:fs.readFileSync`), the interface path
(`%Library.RegisteredObject`), and Task 3's guards-section test.

- [ ] **Step 3: Write the implementation**

**`own_checks.py`** — add `from xarch.kernel.logic.names import outside_steps` to the imports (after
`from xarch.kernel.logic.examples import is_test_example`), and in `_match`:

```python
    if form == NAMES:
        return Match(kind, names=tuple(("", value[1:]) if value.startswith(".") else outside_steps(value, profile.language.member)
                                       for value in values))
```

**`sentences.py`** — add `from xarch.kernel.logic.names import outside_text` before
`from xarch.kernel.placement import EVERYTHING`; then

```python
def _targets(found: Found, member: str) -> str:
    return " or ".join(shown for match in found.rule.targets for shown in _shown(match, member))


def _shown(match: Match, member: str) -> list[str]:
    if match.places:
        return list(dict.fromkeys(f"{t.part}/" for t in match.places))
    if match.kind == "part":
        return [f"{p}/" for p in match.words]
    return [*match.words, *(outside_text(n, member) for n in match.names)]
```

and in `_VALUES`:

```python
    "targets": lambda found, facts, profile: _targets(found, profile.language.member),
    "hit": lambda found, facts, profile: outside_text(found.hit or (), profile.language.member),
```

(`grep -n "_targets(\|_shown(" xarch/modules/rules/application/logic/sentences.py` must show no other caller.)

**`written.py`** — add `from xarch.kernel.logic.names import outside_text` before
`from xarch.modules.rules.domain.rule import ...`; then

```python
def written(rules: Iterable[Rule], member: str) -> dict[str, WrittenCheck]:
    """The rules as checks of a profile, each under an id of its own (see _ids), an outside name joined with the
    language's member."""
    rules = list(rules)
    return {name: check_of(rule, member) for rule, name in zip(rules, _ids(rules))}


def written_own(checks: Iterable[OwnCheck], language: CheckedLanguage) -> dict[str, WrittenCheck]:
    """Checks of a profile's own as its `checks` are written, each under its id with its examples, the tokens of the
    language (see _tokens_filled) in their paths and code filled in."""
    return {own.rule.id: check_of(own.rule, language.member, _filled(own.flagged, language), _filled(own.clean, language))
            for own in checks}
```

```python
def check_of(rule: Rule, member: str, flagged: tuple[tuple[str, str], ...] = (),
             clean: tuple[tuple[str, str], ...] = ()) -> WrittenCheck:
    """The rule as the check a profile would write, with the examples given, an outside name joined with member."""
    targets = () if rule.quantifier == MUST_BE_REACHED else tuple(_target(match, member) for match in rule.targets)
    quantified = Quantified(rule.quantifier, targets, rule.links, rule.via, rule.roots, rule.spread, rule.elsewhere)
    return WrittenCheck(rule.facts, rule.scope, quantified, rule.sayings, rule.keep, rule.exempt, rule.mode, flagged,
                        clean)
```

```python
def _target(match: Match, member: str) -> WrittenTarget:
    if match.kind not in _VALUED:
        return WrittenTarget(match.kind)
    return WrittenTarget(match.kind, (*map(_place, match.places), *(outside_text(n, member) for n in match.names),
                                      *match.words))
```

and delete `_dotted` (lines 87-88).

**`explaining.py`** — line 80: `self._form.written({rule.id: check_of(rule, language.member)})`; line 117:
`return RuleShown(address, location, self._form.written(written(rules, self.language((location,)).member)), len(rules),`
(keep the continuation line as it is).

**`where.py`** — add `from xarch.kernel.logic.names import outside_text` after
`from xarch.kernel.logic.imports import may_import, shown_target`; line 105:
`tuple(outside_text(n, profile.language.member) for n in profile.uses_never.get(part, ())), tier,`; line 201:

```python
    names = tuple(outside_text(n, profile.language.member) for p in where.parts for n in profile.uses_never.get(p, ())) \
        if where.tier.apply_never else ()
```

**`looseness.py`** — add `from xarch.kernel.logic.names import outside_text` before
`from xarch.kernel.placement import EVERYTHING`; at the top of `_looser` add `member = custom.language.checked.member`,
and write `outside_text(banned, member)` for `".".join(banned)` (line 70) and `outside_text(name, member)` for
`".".join(name)` (line 91).

**`docs_template.py`** — add `from xarch.kernel.logic.names import outside_text` after
`from xarch.kernel.logic.imports import may_import, shown_target`; in `_never_use_line`:

```python
    member = architecture.language.checked.member
    listed = "; ".join(f"{_and(parts)}: {_ticked(tuple(outside_text(n, member) for n in names))}"
                       for names, parts in groups.items())
```

(line 483's `'.'.join(table.row)` stays: Spec deviation 4.)

**`explain.py`** — add `from xarch.kernel.logic.names import outside_text` after
`from xarch.kernel.logic.capabilities import shortfalls`; line 33:
`"interface_path": outside_text(checked.interface[0], checked.member) if checked.interface else "",`

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest tests/modules tests/cli tests/kernel tests/profile_values -q`
Expected: all PASS. (A probe of this change on a copy of the branch showed that, among the rules tests, only
`test_never_use.py`'s `PROFILE`/`AMBIENT`, `test_own_checks.py`'s `SUPPLIES` and everything built on
`builders.PYTHON` print or split an outside name; if another hand-built `Profile` with a default `CheckedLanguage()`
now prints `datetimedatetime.now`, give it `language=PYTHON` from `tests.modules.rules.builders`, its expected text
unchanged, and name it in the task report.)

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check xarch tests/modules
git add xarch/modules/rules/application/logic/own_checks.py xarch/modules/rules/application/logic/sentences.py xarch/modules/rules/application/logic/written.py xarch/modules/rules/application/services/explaining.py xarch/modules/rules/application/logic/where.py xarch/modules/spec/application/logic/looseness.py xarch/modules/spec/application/logic/docs_template.py xarch/modules/spec/application/logic/explain.py tests/modules/rules/builders.py tests/modules/rules/application/logic/test_never_use.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/logic/test_profile_keys.py
git commit -m "Every outside name is split and printed with the language's member: a check's path target, the name a finding hits and a check's names, a check written back, where's never lists, the looseness items, the docs' never-use line and %interface_path%; under a member that is not a dot a finding says node:fs#readFileSync, and under Python every text is as before

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: README, CHANGELOG, golden docs, the grep check and the gates

**Files:**
- Modify: `README.md:139` (the `language` paragraph's token list)
- Modify: `CHANGELOG.md` (`[Unreleased]` → `### Changed`, after the `unresolved` entry, before `## [0.2.0]`)

**Interfaces:**
- Consumes: everything above.
- Produces: no code.

- [ ] **Step 1: README**

In `README.md`, in the `language` paragraph, replace

```
and the tokens of its code the checks and the docs need: what a name may be, how a private name starts, what a special
```

with

```
and the tokens of its code the checks and the docs need: what a name may be, what an import names from outside the app
as one step (`package`) and the text that joins a package to a name in it in the profile's lists (`member`, `.` for
Python), so that an outside name is written `<package><member><name>`, how a private name starts, what a special
```

(the next README line, starting "name starts and ends with", stays as it is).

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, after the line `  \`"unresolved": []\`.` that ends the `unresolved` entry, leave one blank line (the entries are separated by one) and add:

```
- A language's data file gives `package`, what an import names from outside the app as one step, and `member`, the
  text that joins a package to a name in it (`.` for Python), beside `name`: the three are given together or not at
  all. The outside names a profile writes (`libraries`, `reserved`, the `never` lists, `testing.skips`,
  `testing.mocks.calls` and `autospec`, `testing.table.decorator` and `row`, a check's `path` target) and the data
  file's `interface`, `dynamic` and `immutable` are read by them; no Python profile entry changes. The refusals say
  so: `'<entry>' is not a package name the language Python allows` under `libraries` and `reserved`;
  `'<value>' is not an outside name such as <package>.<name>` under the testing names; and under a `never` list
  `'<entry>' is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()` and
  `'<entry>' is neither an outside name nor a method: write <entry>() for a method called on anything`.
```

- [ ] **Step 3: Run the README guard**

Run: `uv run pytest tests/architecture/test_readme.py -q`
Expected: PASS.

- [ ] **Step 4: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-3-3/regenerate_docs.py` (outside the worktree):

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:

```bash
mkdir -p /tmp/xarch-3-3
uv run python -I /tmp/xarch-3-3/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs/cli docs/web docs/xarch
```

Expected: `written`; `git status` shows nothing under `docs/` besides the spec and plan under `docs/superpowers/`;
`git diff --stat` prints nothing. A moved golden doc is a defect: restore it with
`git checkout -- docs/cli docs/web docs/xarch` and report the hunk; never keep or hand-edit it.

- [ ] **Step 5: The grep check**

```bash
grep -rn "_is_dotted\|dotted_names\|_DOTTED\|_MARK\b" xarch
grep -n "^def is_name" xarch/modules/spec/application/logic/profile_checks.py
```

Expected: both print nothing.

- [ ] **Step 6: Run the gates**

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
timeout 900 uv run pytest -q > /tmp/xarch-3-3/pytest.txt 2>&1; echo "exit $?"; tail -5 /tmp/xarch-3-3/pytest.txt
```

(Run the last line in the background if the tool limits a foreground command; read the file at the end.)
Expected: ruff `All checks passed!`; both `xarch check` runs exit 0; `profile check` exits 0; pytest `exit 0` with
`passed` and no `failed` (the recorded corpora test `tests/bootstrap/test_recorded_corpora.py` and the docs test
`tests/bootstrap/test_docs.py` among them, unchanged).

- [ ] **Step 7: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "The README's language paragraph names package, what an import names from outside the app as one step, and member, the text that joins a package to a name in it, . for Python, an outside name written <package><member><name>; the CHANGELOG says under Unreleased that outside names are read by them with no Python entry changed, and gives the new refusal texts; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review (run by the planner against the spec)

**Spec coverage.**

| Spec | Task |
|---|---|
| 1 `python.yaml` two keys and header | 2 (3b) |
| 2 loader accepts `package`/`member`, texts, sorted unknown-key list | 2 (3a; T7, T9) |
| 3 together or not at all | 2 (`_joins`; T8) |
| 4 `namespace` with `name`, lists as outside names, no follow-on problems | 2 (T9 via the one-problem test, T10, `test_a_namespace_is_a_name_the_language_allows`) |
| 5 loader texts | 2 (T7, T11) |
| 6 Python reads as today | 2 (T14) |
| 7 parser | 1 (T1-T3) |
| 8 no member | 1 (T4, T5), 2 (T12) |
| 9 `own_checks` split | 4 (Review Focus 5; T21 `SUPPLIES`) |
| 10 printer | 1 (T6) |
| 11 `libraries`/`reserved` | 3 (T15, Review Focus 2) |
| 12 testing names | 3 (T18, `outside_names`) |
| 13 `never` entries | 3 (T16, T17, Review Focus 3-4) |
| 14 single names keep `name` | 3 (table of `names.is_name` edits; existing pins) |
| 15 printing places | 4 (T20, written, explain, docs; where/looseness by Python pins) |
| 16 test-only files | 2 (3c, 3d; T22) |
| 17 `BRACE`, `PERCENT` | 2 (3e) |
| 18 neutrality pair | 3 (T17) |
| 19 README, CHANGELOG | 5 |
| 20 golden docs, corpora, no profile, no `keys.yaml` | 5 (Steps 4, 6) |
| Shape: kernel functions, `CheckedLanguage` fields, deletions, seam | 1, 2, 3, 5 (grep) |

**Placeholder scan.** No TBD/TODO; every code step carries its code; the one conditional instruction (Task 4 Step 4,
another hand-built profile) names the exact fix and its import.

**Type consistency.** `outside_name(text, name, package, member, namespace="")`, `outside_steps(text, member)`,
`outside_text(steps, member)` are called with those orders in Tasks 2-4; `check_of(rule, member, flagged, clean)` and
`written(rules, member)` match their callers in `explaining.py` and `test_written.py`; `outside_name_at`/
`outside_names` are the names Task 3 defines and `profile_parsing.py` calls; `CheckedLanguage(..., names, package,
member)` is positional in the loader and keyword in the tests.

**Review Focus.** Five lines, each with its test in the owning task (Tasks 2, 3, 3, 3, 4).
<!-- task-pipeline: validated -->
