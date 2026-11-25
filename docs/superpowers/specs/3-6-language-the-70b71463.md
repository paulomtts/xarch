# 3.6 language: the standard library read from the data file

Card `70b71463`, subtask of `3c7754c4`. Release step 8a of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3, line 267:
"`standard`: `interpreter` or three lists; the reader handed the standard modules. | language-neutral 6 | Step 7
(lists checked with `package`, `name`).").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below **LN**),
section 6 (lines 713-780). Conflict resolved by it: R3 C9 (lines 168-175, "Two sources of the standard library").
Gap left open: R3 G3 (lines 412-414). Release-wide rules this step inherits: R3 O4, O5, O8 (lines 228-232), O18
(line 242: `python.yaml` is edited by none of 8a), O20 (line 244: 8a changes the source of `standard_names`, not its
value for Python). Dodges: LN lines 1139-1166, of which two apply here (line 1162: "Two sources for the standard
library (the reader's `sys` and spec's runtime) once 8a lands"; line 1163: "Moving Python's own `standard` to a list
'for symmetry'. `interpreter` stays Python's."), and line 1143 ("A step is not done without its test-only file").

## 1. Goal

What a language binds and reserves (its standard library's top-level modules, its reserved words, its builtins)
becomes data of the language's data file (LN 6.1, lines 715-729): `standard` is either the word `interpreter` (the
Python running xarch, as today) or a map of three lists. And the reader stops asking `sys.stdlib_module_names` itself:
it is handed the standard modules from the language value, so spec's checks and the reader's `Import.standard` share
one source (LN 6.2, lines 731-739; R3 C9). Python's findings, the recorded corpora and the golden docs do not move
(LN 6.5, line 766).

## 2. Observable behavior

### 2.1 The data file's `standard` (LN 6.1, 6.2, 6.4)

- `standard` stays a required key (`REQUIRED` in `language_file.py` unchanged; missing still says only
  ``missing `standard` ``).
- It takes exactly one of two shapes:
  - the string `interpreter`;
  - a map with exactly the three keys `modules`, `reserved`, `builtins`, each a list (possibly empty) of strings.
- Each item is checked with the file's own patterns (LN 6.2, line 733-734):
  - an item of `modules` must be a package the language allows: it fully matches the file's `package` pattern (any
    non-empty text when the file gives no `name`/`package`/`member`);
  - an item of `reserved` or `builtins` must be a name the language allows: `is_name(item, names)`
    (`xarch/kernel/logic/names.py`), i.e. the file's `name` pattern, any non-empty text when it gives none.
  - When `name`/`package`/`member` are themselves refused already (`_joins` returned None), the items are not checked
    (as `_outside` and `_interface` do today); the file is refused anyway for those keys.
- Refusals, raised by `language_of` as `InvalidArchitecture("presets/language/<name>.yaml", problems)`, listed with
  every other problem of the file, no retired-keys hint (LN 6.4, lines 751-758):
  - any other value (another word such as `node`, an empty string, a number, a list, a map missing a key or with an
    extra key, a key whose value is no list, a list holding a non-string or an empty string):
    `standard: must be interpreter, or a map of modules, reserved and builtins, each a list of names` — said once.
  - an item of `modules` the `package` pattern refuses: `standard.modules: 'x y' is not a package name the language
    allows` (the item by `repr`), one problem per item.
  - an item of `reserved` or `builtins` the `name` pattern refuses: `standard.reserved: 'x y' is not a name the
    language allows` / `standard.builtins: 'x y' is not a name the language allows`, one problem per item. (LN 6.4
    gives the `modules` text; these two follow it word for word with the pattern each list is checked with.)
  - The old text `standard: must be a name` is gone.
- Nothing refuses `interpreter` in a non-Python data file (LN 6.4, lines 755-757): the loader never compares the
  language's name. `percent.yaml` keeps `standard: interpreter`.
- `python.yaml` is not edited at all: it keeps `standard: interpreter`, and its header is not touched (R3 O18; LN
  dodge line 1163).

### 2.2 The language value (LN 6.3, 6.6)

- `xarch/modules/spec/domain/values.py` gains a frozen value `StandardLists(modules: tuple[str, ...], reserved:
  tuple[str, ...], builtins: tuple[str, ...])`, in the order written; `Language.standard` becomes
  `str | StandardLists` (`"interpreter"` or the lists; default `""`), and its docstring says so (LN 6.6 row 3).
- `xarch/profile_values/language.py` `CheckedLanguage` gains `standard_modules: frozenset[str] = frozenset()`: the
  top-level modules of the language's standard library, which the reader is handed. Its docstring says it (filled by
  spec from the data file or the runtime; empty: no module is standard). This is how the value reaches rules, which
  never sees spec's `Language` (rules reads `profile.language`, a `CheckedLanguage`).
- The word `interpreter` is written once in xarch's code: one constant that the loader (to accept the word) and the
  `InterpreterRuntime` adapter (its `SOURCE`, `interpreter_runtime.py:8`) both read; the planner places it in spec's
  domain (`values.py`, beside `LANGUAGES`) and has the adapter import it, rather than two equal literals.

### 2.3 Spec fills the three sets from one source (LN 6.3, lines 741-749)

`ArchitectureService._language_presets` (`xarch/modules/spec/application/services/architecture.py:155-162`):

- for `standard: interpreter`: `standard_names`, `builtin_names`, `reserved_names` come from the Runtime port, as
  today, asked with the word;
- for the lists: `standard_names = frozenset(modules)`, `reserved_names = frozenset(reserved)`,
  `builtin_names = frozenset(builtins)`; the runtime is not asked at all;
- in both cases `checked.standard_modules` is set to exactly `standard_names` in the same step
  (`replace(language.checked, standard_modules=...)`), so the set spec checks profiles with and the set the reader is
  handed are one value.
- `InterpreterRuntime._read` keeps refusing any source but `interpreter` (unchanged code; it is only ever asked for
  that one now). `profile_checks.py:586, 607, 643` and `never_lists.py:67` are unchanged: their source changes, not
  their code (LN 6.3 line 748-749).

Observable consequences:

- Under a listed language, `reserved: {fs: ...}` loads when `fs` is in `modules`; under Python it is refused with
  today's text (`profile_checks.py:587`); `reserved: {pickle: ...}` the other way round (LN 6.5, lines 762-763).
- A `never` entry naming a listed builtin gets today's builtin hint (`profile_checks.py:643`); a list of `never`
  named like a listed module is refused as today (`never_lists.py:67`).

### 2.4 The reader is handed the standard modules (LN 6.2, line 735-739; R3 C9)

- The `SourceTree` port (`xarch/modules/rules/application/ports/source_tree.py`): `read(...)` gains a keyword
  parameter `standard: frozenset[str]` after `interface`, and `parsed(text)` becomes `parsed(text, standard)`.
  Neither has a default: an unhanded call would mark every import non-standard and silently change Python's findings
  (LN dodge line 1150, "Hidden defaults in the code"). Docstrings: an absolute import is of the standard library when
  its first step is in `standard`.
- `FsSourceTree` (`xarch/modules/rules/adapters/fs_source_tree.py`): `read`, `parsed`, `_parsed` and `_imports` carry
  the set; `Import.standard` is `True` exactly when the import is absolute, names a module, and its first step is in
  the handed set; relative imports are never standard (as today). `_standard` and the `sys.stdlib_module_names`
  read at line 271-272 are removed; `import sys` goes if nothing else in the file uses it. The module docstring says
  the reader is handed the standard modules.
- Every caller hands `profile.language.standard_modules` (`rules.language` where the variable is so named):
  `services/source_check.py:76, 80` (app and tests), `services/holding.py:27, 37`, `services/sources.py:52`,
  `services/asking.py:26`, `services/examples.py:52, 59`. So an eval's facts, an own check's flagged/clean code, the
  holds question and `sources` all mark imports as `check` does.
- `services/source_reading.py:16, 23` (`SourceReadService`, spec's `ExampleReader` through `ReaderController`) has no
  profile. It hands `frozenset()`, and the `ExampleReader` port's docstring
  (`xarch/modules/spec/application/ports/example_reader.py`) says an example's imports are not marked standard:
  spec reads no `standard` of an example's import (`example_imports.py` ignores every import outside the app by its
  module, lines 8-9; no code of spec reads `Import.standard` — `grep -rn "\.standard\b" xarch` finds only
  `rules/application/logic/facts.py:182, 281`). The planner confirms that grep before relying on it.
- The fake `tests/fakes/filesystem.py` `FakeSourceTree.read`/`parsed` take the new parameter and record what they
  were handed (e.g. a list `handed` of the sets, in call order), so service tests can check it; the imports they
  return stay those the test built.
- Docstrings only (LN 6.6 row 4): `spec/application/ports/runtime.py` (the runtime answers a data file's
  `interpreter`; a listed language is not asked), `interpreter_runtime.py`, `platform/interpreter.py` if it says
  otherwise, and `bootstrap/wiring.py:73-75` `RUNTIME` (a listed language needs no runtime, LN 6.3 line 746-747).

### 2.5 Things that stay as they are

- Python's findings on every profile, the recorded corpora (`tests/bootstrap/corpora/`), and the golden docs
  `docs/{cli,web,xarch}/testing.md` (regenerated, diff read, expected empty; R3 O8, LN 6.5 line 766).
- `uv run xarch check`, `--strict` and `xarch profile check architecture.yaml` on xarch itself.
- `keys.yaml` (its `standard` mentions speak of the standard library, not of where it is known from).

## 3. The test-only language file (LN 6.5, line 762; dodge line 1143)

`tests/fakes/languages/brace.yaml` changes `standard: interpreter` to the lists, each item valid under its own
`package` and `name` patterns:

```yaml
standard: {modules: [fs, path, "node:fs", "node:path"], reserved: [class, const, function, interface],
           builtins: [globalThis, fetch]}
```

- Its header comment says it gives its standard library, reserved words and builtins as lists.
- `tests/modules/spec/languages.py` builds `BRACE` with the three sets filled from its lists (and
  `checked.standard_modules`), as the service does; the ad hoc `builtin_names=frozenset({"fetch"})` override goes,
  since `fetch` is now in the file. `PYTHON` there also gets `checked.standard_modules =
  frozenset(sys.stdlib_module_names)` (tests may read `sys`).
- `tests/modules/rules/builders.py`: `PYTHON` gets `standard_modules=frozenset(sys.stdlib_module_names)` and
  `BRACE` `standard_modules` from `BRACE_FILE["standard"]["modules"]`; `imp()` (line 149-155) marks standard by
  `PYTHON.standard_modules` instead of reading `sys` itself, and a language argument lets a test build an `Import`
  as the reader would under `BRACE`.
- Every existing test that loads `brace` (`grep -rn "BRACE\b\|brace" tests`) is rerun; the planner checks that the
  new `standard_names` (`fs`, `path`, `node:fs`, `node:path`) and builtins (`globalThis`, `fetch`) change no expected
  value, and adjusts only replacements now redundant (e.g. `test_never_use.py:470`
  `replace(BRACE, standard_names=frozenset({"fs"}))` may stay or go; its expectation must not change).
- `percent.yaml` keeps `standard: interpreter` (2.1).

## 4. Tests (written first)

Unit = pure logic or a service with fakes, no disk; adapter = real adapter against real or tmp files; architecture =
the repository guards; bootstrap = the wired app end to end.

### 4.1 Loader — `tests/modules/spec/application/logic/test_language_file.py` (unit: `language_of` is pure)

1. A document with `standard: {modules: [...], reserved: [...], builtins: [...]}` reads into
   `Language.standard == StandardLists(...)`, in the order written; `interpreter` still reads into the word.
2. Each wrong shape gives exactly one `standard: must be interpreter, or a map of modules, reserved and builtins,
   each a list of names` (parametrized: `node`, `""`, `3`, `[fs]`, a map missing `builtins`, a map with an extra key,
   `modules: fs`, `modules: [3]`, `modules: [""]`).
3. `modules: ["x y"]` under `JOINS` gives `standard.modules: 'x y' is not a package name the language allows`;
   `reserved: ["x y"]` and `builtins: ["1a"]` give their `is not a name the language allows` lines; two bad items give
   two problems.
4. With no `name`/`package`/`member` (`UNJOINED`), any non-empty text is accepted in all three lists.
5. With `name` refused, the lists' items are not checked (only the `name` problem is listed for the patterns).
6. Every file of `tests/fakes/languages/` still loads (existing `TEST_LANGUAGES` test), and `brace` loads its lists.
7. The existing refusal list test (line 40-58) still holds; the old `standard: must be a name` text appears nowhere.

### 4.2 Spec service — `tests/modules/spec/application/test_language.py` (unit: service with `FakeRuntime`)

8. A listed language's `standard_names`, `reserved_names`, `builtin_names` are its lists, and the runtime is never
   asked (a `FakeRuntime` that records calls, or raises, shows no call for it).
9. An `interpreter` language's three sets are the runtime's, as today (existing line 44 test kept).
10. For both, `checked.standard_modules == standard_names`.

### 4.3 Profile checks under the two languages (unit: `parse_profile` is pure over the language map)

11. `reserved: {fs: <reason>}` loads under `brace` and is refused under `python` with today's "is not a module of
    the standard library" text (whatever `profile_checks.py:587` says verbatim); `reserved: {pickle: <reason>}` loads
    under `python` and is refused under `brace` (LN 6.5 line 762-763). In
    `tests/modules/spec/application/logic/test_profile_checks.py` (or the file that already tests `reserved`).
12. A `never` entry `fetch` under `brace` gets the builtin hint with no `replace` of `builtin_names`
    (`test_never_use.py`, spec side).

### 4.4 Filter `standard` under brace — `tests/modules/rules/application/logic/test_filters.py` (unit)

13. `Import` values built by `imp(..., language=BRACE)` for `fs` and `lodash` are read by the filter `standard`: `fs`
    is standard, `lodash` is not (LN 6.5 line 764).

### 4.5 The reader — `tests/modules/rules/adapters/test_fs_source_tree.py` (adapter: real `FsSourceTree`)

14. Handed `frozenset({"fs"})`, `import fs` and `from fs import x` are standard, `import os` is not; handed
    `frozenset()`, nothing is standard. This proves the reader reads the handed set, not `sys`.
15. A relative import is never standard, whatever is handed.
16. Handed `frozenset(sys.stdlib_module_names)`, every absolute import of every `.py` file under `xarch/` has
    `standard == (module[0] in sys.stdlib_module_names)` (LN 6.5 line 765: "marks every import of xarch's own source
    as today"). Existing parametrized cases (line 918-930) pass the set and keep their expectations.
17. `parsed(text, standard)` marks as `read` does.

### 4.6 The services hand the set (unit: services with `FakeSourceTree` recording what it is handed)

18. `SourceCheckService.check` hands `profile.language.standard_modules` to both reads (app and tests).
19. `HoldingService.holds` (the given files and `_others`), the `sources` service, `asking` (`kept`) and
    `examples` (own checks and evals) each hand it on every `read`/`parsed` call.
20. `SourceReadService` hands `frozenset()`.
    Tests sit beside each service's existing tests under `tests/modules/rules/application/`.

### 4.7 Guards (architecture)

21. `tests/architecture/test_language_seam.py`: `WORDS_BESIDES` keeps `stdlib_module_names` only if a file the guard
    scans still uses it (`platform/interpreter.py` does; the planner reads the guard's scope); the tests at lines
    328-346 that prove the scan detects the word stay. If no scanned file names it any more, the allowance goes.
22. `tests/architecture/test_agnostic.py` stays green with `ALLOWED` empty: the constant `interpreter` is not a
    Python identifier of the reader's kind; if the guard objects, the constant lives where the guard allows data
    (spec's domain), never by adding to `ALLOWED`.

### 4.8 End to end (bootstrap)

23. The corpora tests and the golden-doc tests pass unchanged (`tests/bootstrap/`), proving Python's findings and
    docs do not move with the reader now handed the set through spec.

## 5. Docs (R3 O4, O5, O8)

- `README.md` line 142: "where the standard library's names are known from (`interpreter`)" also says the other
  shape: or three lists, `modules`, `reserved` and `builtins`, checked with the file's `package` and `name`.
- `CHANGELOG.md`, `[Unreleased]` → `### Changed`: one entry: `standard` in a language's data file is `interpreter`
  (the Python running xarch) or `{modules, reserved, builtins}`, three lists checked with the file's `package` and
  `name`; the reader is handed the standard modules from the language instead of asking the interpreter itself; the
  three refusal texts of 2.1 quoted; no finding of a Python app changes.
- Golden docs regenerated with the repo's regeneration command, diff read, expected empty; never edited by hand.
- `language_file.py` module docstring line 14 (`standard`) says the two shapes.

## 6. Out of scope

- A list per Python version (R3 G3, lines 412-414): `interpreter` still reads the Python running xarch.
- Moving `python.yaml`'s `standard` to lists, or editing `python.yaml` at all (LN dodge line 1163; R3 O18).
- The reader's own builtins (`_BUILTINS = vars(builtins)`, `fs_source_tree.py:265-266`), used to resolve bare names
  in calls: the card and LN 6.2 hand the reader the standard modules only. Named here so the reviewer does not read
  it as a missed second source; it is a candidate for a later step.
- Sections 7 to 10 of LN (extensions and package files, comment forms, privacy, records): release steps 8b to 8e,
  sibling cards.
- A reader for any language but Python; changes to `percent.yaml`.
- The recorded corpora: not edited.

## 7. Gates

Each passes on this branch alone, full suite green: `uv run pytest -q` (over two minutes: run in the background,
read at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

Project rules: no comments in xarch's code (docstrings as the code base writes them); tests first; examples simple,
with absolute `app.` imports; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
