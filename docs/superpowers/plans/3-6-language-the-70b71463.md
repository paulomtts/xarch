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

---

# 3.6 language: the standard library read from the data file — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A language's data file gives its `standard` as the word `interpreter` or as three lists (`modules`,
`reserved`, `builtins`). Spec fills its three name sets from that one source, and hands the standard modules to the
reader through `CheckedLanguage.standard_modules`. The reader stops reading `sys.stdlib_module_names` itself.

**Architecture:** The loader (`language_file.py`) reads `standard` into `str | StandardLists` (spec's domain). The
spec service `ArchitectureService._named` fills `standard_names`/`reserved_names`/`builtin_names` from the lists, or
from the Runtime port for `interpreter`, and sets `checked.standard_modules` to the same set. That set reaches rules
inside `CheckedLanguage` (`profile.language`). Every rules service hands it to `SourceTree.read(..., standard=...)` /
`SourceTree.parsed(text, standard)`. The Python reader marks `Import.standard` by the handed set.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/3-6-language-the-70b71463.md` (prepended above).

## Global Constraints

- `python.yaml` is not edited at all, header included (R3 O18; LN dodge line 1163).
- `percent.yaml` keeps `standard: interpreter`.
- The recorded corpora (`tests/bootstrap/corpora/`) are not edited. The golden docs `docs/{cli,web,xarch}/testing.md`
  are regenerated, never hand-edited, and the diff must be empty.
- Refusal texts, verbatim:
  - `standard: must be interpreter, or a map of modules, reserved and builtins, each a list of names` (once for the key)
  - `standard.modules: '<item>' is not a package name the language allows` (one per item, `repr` of the item)
  - `standard.reserved: '<item>' is not a name the language allows` / `standard.builtins: '<item>' is not a name the language allows`
- `standard` stays in `REQUIRED`; a missing one still says only ``missing `standard` ``.
- The word `interpreter` is written once in xarch's code: `INTERPRETER` in `xarch/modules/spec/domain/values.py`, read
  by the loader and by `InterpreterRuntime`.
- `SourceTree.read`'s `standard` and `SourceTree.parsed`'s `standard` have no default.
- `tests/architecture/test_agnostic.py` `ALLOWED` stays empty.
- No comments in xarch's code; docstrings as the code base writes them; lines ≤ 140 (ruff), prose wrapped near 120.
- Never `ruff --fix`. Nothing is pushed. `.claude/` stays out of commits.
- Gates, each green on this branch: `uv run pytest -q` (over two minutes: run it in the background and read it at the
  end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
  `uv run xarch profile check architecture.yaml`.

## Spec deviations (decided by the planner, with evidence)

1. **The seam guard bans the word `builtins` outside the reader and the platform.** `tests/architecture/test_language_seam.py`
   reads Python's `namespace: builtins` as a word of the language. It flags it in literals, docstrings and identifiers
   (probed: a literal, a docstring, a field `builtins` and an attribute `.builtins` each gave a leak). The spec fixes
   the key `builtins` and the field `StandardLists.builtins`, so the word is the format's own here and not Python's
   namespace. The guard's own mechanism for this is `EXEMPT` (per file and word, and a stale entry fails). The plan
   adds three entries: `modules/spec/domain/values.py`, `modules/spec/application/logic/language_file.py` and
   `modules/spec/application/services/architecture.py`, each with why. Every other new docstring (ports, wiring,
   `CheckedLanguage`) says "the names it binds without an import" instead.
2. **The agnostic guard bans the string literal `modules`**: it is a layout folder of the bundled profiles (probed:
   `literals_naming` flags `"... a map of modules, ..."`). `ALLOWED` must stay empty (spec 4.7 item 22). So the loader
   takes the map's keys from the fields of `StandardLists`: `STANDARD_LISTS = tuple(f.name for f in
   fields(StandardLists))`. The refusal texts are composed from those keys and come out word for word as the spec
   gives them. Docstrings are not scanned by that guard.
3. **`WORDS_BESIDES` keeps `stdlib_module_names`.** It is a word the guard *bans* outside the seam, not an allowance.
   `platform/interpreter.py` (in the seam) still names it, and no other file may. Only its note changes: the reader
   no longer marks imports with it.
4. **`read`'s `standard` is keyword-only** (`*, standard: frozenset[str]`), because a parameter with no default
   cannot follow the defaulted `table`, `immutable` and `interface`. `_parsed`'s `marks` and `interface` lose their
   defaults for the same reason. Both of its callers already pass them.
5. **Spec test 7's "the old text appears nowhere"** gets no test of its own. The old text was never a literal: it was
   built from `"standard"` and `"must be a name"`, so a search proves nothing. The parametrized refusals of Task 1
   pin the new text instead.
6. **The services' "hands the set" tests (spec 4.6)** go in one new file,
   `tests/modules/rules/application/test_standard_handed.py`, beside the services' other tests, with one test per
   service.

## Review Focus

1. `standard:` left empty in YAML (`None`) → one `standard: must be interpreter, ...` problem, no crash (Task 1, the
   `None` row).
2. A submodule written in `modules` (`os.path` under a Python-like `package` pattern) → refused per item as no
   package name the language allows (Task 1, the `os.path` row).
3. One install with a listed language and an `interpreter` one → the runtime is asked only for the `interpreter` one
   (Task 2, the mixed-languages test).
4. A submodule of a handed module (`import fs.sub`, `from fs.sub import x`) → standard by its first step (Task 3, the
   reader's parametrized test).
5. The holds question with a root reads the other files of the app with the same set as the files given → (Task 3,
   the holds test expects two handed sets).

## File Structure

| File | Change |
| --- | --- |
| `xarch/modules/spec/domain/values.py` | `INTERPRETER`, `StandardLists`, `Language.standard: str \| StandardLists` |
| `xarch/modules/spec/application/logic/language_file.py` | `_standard`, `STANDARD_LISTS`, `STANDARD`; `_WORD` goes; docstring |
| `xarch/modules/spec/adapters/interpreter_runtime.py` | reads `INTERPRETER`; `SOURCE` goes |
| `xarch/profile_values/language.py` | `CheckedLanguage.standard_modules` |
| `xarch/modules/spec/application/services/architecture.py` | `_named`, which fills the three sets and `checked.standard_modules` |
| `xarch/modules/spec/application/ports/runtime.py`, `xarch/bootstrap/wiring.py` | docstrings |
| `xarch/modules/spec/application/ports/example_reader.py` | docstring |
| `xarch/modules/rules/application/ports/source_tree.py` | `read(..., *, standard)`, `parsed(text, standard)` |
| `xarch/modules/rules/adapters/fs_source_tree.py` | handed set; `_standard` and `import sys` go; docstring |
| `xarch/modules/rules/application/services/{source_check,holding,sources,asking,examples,source_reading}.py` | hand the set |
| `tests/fakes/languages/brace.yaml` | `standard` as lists; header |
| `tests/fakes/runtime.py` | records `asked` |
| `tests/fakes/filesystem.py` | `FakeSourceTree` takes and records `handed` |
| `tests/modules/spec/languages.py` | `named`; `PYTHON`, `BRACE` filled as the service fills them |
| `tests/modules/rules/builders.py` | `standard_modules` on `PYTHON`/`BRACE`; `imp(..., language=)` |
| tests | `test_language_file.py`, `test_language.py`, `test_libraries_and_guards.py`, spec `test_never_use.py`, `test_filters.py`, `test_fs_source_tree.py`, new `test_standard_handed.py`, `test_language_seam.py` |
| `README.md`, `CHANGELOG.md` | the two shapes |

---

### Task 1: The data file's `standard` is `interpreter` or three lists

**Files:**
- Modify: `xarch/modules/spec/domain/values.py` (after `LANGUAGES`, line ~29; before `class Language`, line ~302; `Language` lines 303-325)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring lines 1-3 and 14; imports 42-52; constants 61-77; line 104)
- Modify: `xarch/modules/spec/adapters/interpreter_runtime.py` (whole file)
- Modify: `tests/fakes/languages/brace.yaml` (lines 1-9)
- Modify: `tests/architecture/test_language_seam.py` (`EXEMPT`, line 121)
- Test: `tests/modules/spec/application/logic/test_language_file.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces:
  - `xarch.modules.spec.domain.values.INTERPRETER: str == "interpreter"`
  - `xarch.modules.spec.domain.values.StandardLists(modules: tuple[str, ...] = (), reserved: tuple[str, ...] = (), builtins: tuple[str, ...] = ())`, frozen
  - `Language.standard: str | StandardLists` (`"interpreter"`, the lists, or `""`)
  - `language_file.STANDARD_LISTS == ("modules", "reserved", "builtins")`, `language_file.STANDARD` (the refusal text)
  - `tests/fakes/languages/brace.yaml` `standard` as the three lists

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_language_file.py`, change the import at line 10 to:

```python
from xarch.modules.spec.domain.values import Language, StandardLists
```

After the line `INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"` (line 27), add:

```python
STANDARD = "standard: must be interpreter, or a map of modules, reserved and builtins, each a list of names"
LISTS = {"modules": [], "reserved": [], "builtins": []}
"""A standard that lists nothing, to which a test adds the lists it needs."""
```

Append at the end of the file (two blank lines before each test):

```python
def test_a_language_that_lists_its_standard_library_reads_the_three_lists_in_the_order_written():
    standard = {"modules": ["strutils", "sysutils"], "reserved": ["begin", "end"], "builtins": ["writeln"]}
    assert (language_of("pascal", DOCUMENT | {"standard": standard}).standard,
            language_of("pascal", DOCUMENT | {"standard": LISTS}).standard,
            language_of("pascal", DOCUMENT).standard) == (
        StandardLists(("strutils", "sysutils"), ("begin", "end"), ("writeln",)), StandardLists(), "interpreter")


@pytest.mark.parametrize("standard", [
    pytest.param("node", id="another word"),
    pytest.param("", id="an empty string"),
    pytest.param(None, id="left empty"),
    pytest.param(3, id="a number"),
    pytest.param(["fs"], id="a list"),
    pytest.param({"modules": [], "reserved": []}, id="a map missing a list"),
    pytest.param(LISTS | {"keywords": []}, id="a map with a key besides the three"),
    pytest.param(LISTS | {"modules": "fs"}, id="a list that is no list"),
    pytest.param(LISTS | {"modules": [3]}, id="an item that is no text"),
    pytest.param(LISTS | {"reserved": [""]}, id="an empty item"),
])
def test_a_standard_that_is_neither_the_word_nor_the_three_lists_is_refused_once(standard):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"standard": standard})
    assert caught.value.problems == (f"presets/language/odd.yaml: {STANDARD}",)


@pytest.mark.parametrize("lists, problems", [
    pytest.param({"modules": ["x y"]}, ["standard.modules: 'x y' is not a package name the language allows"],
                 id="a module the package pattern refuses"),
    pytest.param({"modules": ["os.path"]}, ["standard.modules: 'os.path' is not a package name the language allows"],
                 id="a module below a top-level one"),
    pytest.param({"reserved": ["x y"]}, ["standard.reserved: 'x y' is not a name the language allows"],
                 id="a reserved word the name pattern refuses"),
    pytest.param({"builtins": ["1a"]}, ["standard.builtins: '1a' is not a name the language allows"],
                 id="a builtin the name pattern refuses"),
    pytest.param({"modules": ["x y", "fs", "2b"]}, ["standard.modules: 'x y' is not a package name the language allows",
                                                    "standard.modules: '2b' is not a package name the language allows"],
                 id="one problem for each item refused"),
])
def test_an_item_of_the_lists_is_checked_with_the_language_s_own_patterns(lists, problems):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"standard": LISTS | lists})
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == problems


def test_with_no_name_package_and_member_any_text_is_an_item_of_the_lists():
    standard = {"modules": ["x y", "os.path"], "reserved": ["1a"], "builtins": ["a b"]}
    assert language_of("pascal", UNJOINED | {"standard": standard}).standard == StandardLists(
        ("x y", "os.path"), ("1a",), ("a b",))


def test_the_items_of_the_lists_are_not_checked_when_the_keys_that_say_how_a_name_is_written_are_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"name": "[a-", "standard": LISTS | {"modules": ["x y"], "reserved": ["1a"]}})
    assert [p.removeprefix("presets/language/odd.yaml: ").split(":")[0] for p in caught.value.problems] == ["name"]


def test_the_brace_test_only_language_lists_its_standard_library_and_the_percent_one_says_interpreter():
    loaded = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8")))
              for path in TEST_LANGUAGES}
    assert (loaded["brace"].standard, loaded["percent"].standard) == (
        StandardLists(("fs", "path", "node:fs", "node:path"), ("class", "const", "function", "interface"),
                      ("globalThis", "fetch")), "interpreter")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py`
Expected: collection error, `ImportError: cannot import name 'StandardLists' from 'xarch.modules.spec.domain.values'`.

- [ ] **Step 3: Add `INTERPRETER` and `StandardLists` to spec's domain**

In `xarch/modules/spec/domain/values.py`, right after the docstring of `LANGUAGES` (the line
`"""Where the data files of the languages are, below the bundled folder: one YAML file each, named for the language."""`),
add:

```python
INTERPRETER = "interpreter"
"""The `standard` of a language's data file that says its standard library, its reserved words and the names it binds
without an import are known from the interpreter running xarch, as its runtime says them."""
```

Right before `@dataclass(frozen=True)` of `class Language:` (line ~302), add:

```python
@dataclass(frozen=True)
class StandardLists:
    """What a language's data file lists as its `standard`, each in the order written: modules, the top-level modules
    of its standard library; reserved, the words no name may be; builtins, the names it binds without an import."""
    modules: tuple[str, ...] = ()
    reserved: tuple[str, ...] = ()
    builtins: tuple[str, ...] = ()


```

In `class Language`, replace the docstring's first sentence and its `standard:` line, and the field:

old:
```python
    """What is true of the language of the app as a whole, read from the data file of its preset (and from the runtime
    for the names only it knows).
```
new:
```python
    """What is true of the language of the app as a whole, read from the data file of its preset (and from the runtime
    for the names only it knows, when the data file says INTERPRETER).
```

old:
```python
    standard: where the names of the standard library are known from
```
new:
```python
    standard: where the names of the standard library are known from: INTERPRETER, the runtime, or the lists the data
        file gives (StandardLists)
```

old:
```python
    standard: str = ""
```
new:
```python
    standard: str | StandardLists = ""
```

- [ ] **Step 4: Read `standard` in the loader**

In `xarch/modules/spec/application/logic/language_file.py`:

Replace the module docstring's first paragraph (lines 1-3):

old:
```python
"""The data file of a language (`presets/language/<name>.yaml`): what is true of the language as a whole and is needed
outside the reader that turns source into facts. Read into a Language, with every problem listed; the names only the
runtime knows are added to it by the service that holds the runtime.
```
new:
```python
"""The data file of a language (`presets/language/<name>.yaml`): what is true of the language as a whole and is needed
outside the reader that turns source into facts. Read into a Language, with every problem listed; the names of its
standard library, its reserved words and the names it binds without an import are added to it by the service that
holds the runtime, from the lists the file gives or from the runtime.
```

Replace the `standard` line of the key table (line 14):

old:
```
    standard       where the names of the standard library are known from
```
new:
```
    standard       where the standard library, the reserved words and the names bound without an import are known
                   from: interpreter, the interpreter running xarch, or a map of three lists, {modules, reserved,
                   builtins}, each item of modules a package by `package` and each of the others a name by `name`
```

Add `from dataclasses import fields` to the standard-library imports, so they read:

```python
import re
from collections.abc import Iterable, Mapping
from dataclasses import fields
from typing import Any
```

Change the values import to:

```python
from xarch.modules.spec.domain.values import INTERPRETER, LANGUAGES, Language, StandardLists
```

Delete the line `_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")` (line 68; its one use goes in this step).

After the docstring of `INTERFACE` (the line
`"""What the loader says of a value of `interface` that is not a list of marks, once for the key."""`), add:

```python
STANDARD_LISTS = tuple(field.name for field in fields(StandardLists))
"""The keys of the map a data file's `standard` may be: the lists of StandardLists, in its order."""
STANDARD = (f"standard: must be {INTERPRETER}, or a map of {', '.join(STANDARD_LISTS[:-1])} and {STANDARD_LISTS[-1]}, "
            "each a list of names")
"""What the loader says of a value of `standard` that is neither the word nor the three lists, once for the key."""
```

In `language_of`, replace line 104:

old:
```python
    standard = _text(document, "standard", "must be a name", problems, _WORD)
```
new:
```python
    standard = _standard(document, problems, joins)
```

Add this function right after `_interface_mark` (before `def _marks`):

```python
def _standard(document: Mapping[Any, Any], problems: list[str],
              joins: tuple[str, str, str] | None) -> str | StandardLists:
    """INTERPRETER, or the three lists, each item checked by the language's patterns (a module as a package, the
    others as names) unless the keys that say how a name is written are refused already (joins None); "" when the
    document gives neither, with one problem for the key."""
    if "standard" not in document:
        return ""
    value = document["standard"]
    if value == INTERPRETER:
        return INTERPRETER
    if not (isinstance(value, Mapping) and set(value) == set(STANDARD_LISTS)
            and all(isinstance(value[key], list) and all(isinstance(item, str) and item for item in value[key])
                    for key in STANDARD_LISTS)):
        problems.append(STANDARD)
        return ""
    lists = StandardLists(*(tuple(value[key]) for key in STANDARD_LISTS))
    if joins is None:
        return lists
    names, package, _ = joins
    first, *rest = STANDARD_LISTS
    problems += [f"standard.{first}: {item!r} is not a package name the language allows" for item in value[first]
                 if not is_name(item, package)]
    problems += [f"standard.{key}: {item!r} is not a name the language allows" for key in rest for item in value[key]
                 if not is_name(item, names)]
    return lists
```

- [ ] **Step 5: The runtime adapter reads the one word**

Replace the whole of `xarch/modules/spec/adapters/interpreter_runtime.py` with:

```python
"""Spec's Runtime port answered by the interpreter running xarch, for a language whose data file gives `standard:
interpreter`."""
from __future__ import annotations

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import INTERPRETER, LANGUAGES
from xarch.platform.interpreter import builtin_names, reserved_words, standard_library


class InterpreterRuntime:
    """Satisfies spec's Runtime port."""

    def standard_library(self, source: str) -> frozenset[str]:
        _read(source)
        return standard_library()

    def reserved_words(self, source: str) -> frozenset[str]:
        _read(source)
        return reserved_words()

    def builtin_names(self, source: str) -> frozenset[str]:
        _read(source)
        return builtin_names()


def _read(source: str) -> None:
    """Refuses a source of names other than the interpreter, the one this runtime reads."""
    if source != INTERPRETER:
        raise InvalidArchitecture(LANGUAGES, [
            f"standard: {source!r} is not a source of names xarch reads: use {INTERPRETER}"])
```

- [ ] **Step 6: The brace test-only language lists its standard library**

In `tests/fakes/languages/brace.yaml`, replace lines 1-9 (the header and up to `standard: interpreter`) with:

```yaml
# A test-only language that imitates a TypeScript-like one: no profile names it and no reader is written for it. Its
# packages are named as a package manager names them (a scope, a dash, a dot) or as its runtime's own modules
# (node:fs), and a name in one is joined to it by #. It gives its standard library's top-level modules, its reserved
# words and its builtins as lists, so that spec reads them from here and asks no runtime. The tests load it to show
# that the profile and the checks read outside names by a language's own patterns; later steps add their keys to it.
title: Brace
extension: .ts
package_file: index.ts
namespace: globalThis
standard: {modules: [fs, path, "node:fs", "node:path"], reserved: [class, const, function, interface],
           builtins: [globalThis, fetch]}
```

The lines after it (`name:`, `package:`, `member:`, `interface:`, `nothing:`, `dynamic:`) stay as they are.

- [ ] **Step 7: Exempt the format's word `builtins` in spec's domain and loader**

In `tests/architecture/test_language_seam.py`, add these two entries as the first entries of the `EXEMPT` dict
(line 121, right after `EXEMPT: dict[tuple[str, str], str] = {`):

```python
    ("modules/spec/domain/values.py", "builtins"): "the key of a data file's `standard` that lists the names a "
                                                   "language binds without an import, a word of the format every "
                                                   "language's file writes and not the namespace of one: a field "
                                                   "of StandardLists",
    ("modules/spec/application/logic/language_file.py", "builtins"): "the same key of the format, named where the "
                                                                     "loader's docstring says the keys of a data "
                                                                     "file",
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/adapters/test_interpreter_runtime.py tests/architecture/test_language_seam.py tests/architecture/test_agnostic.py`
Expected: all pass. Then run the whole spec module, which loads `brace` in many tests:
`timeout 900 uv run pytest -q tests/modules/spec tests/profile_values`
Expected: all pass. The service does not fill `brace`'s lists yet. `tests/modules/spec/languages.py` still builds
`BRACE` with `builtin_names=frozenset({"fetch"})` and empty `standard_names`, so no expectation moves.

- [ ] **Step 9: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!`

- [ ] **Step 10: Commit**

```bash
git add xarch/modules/spec/domain/values.py xarch/modules/spec/application/logic/language_file.py \
        xarch/modules/spec/adapters/interpreter_runtime.py tests/fakes/languages/brace.yaml \
        tests/architecture/test_language_seam.py tests/modules/spec/application/logic/test_language_file.py
git commit -m "A language's standard is interpreter or a map of three lists, modules, reserved and builtins, each item checked with the file's package or name pattern, refused once otherwise; the word interpreter is one constant of spec's domain the loader and the runtime read; brace lists its standard library"
```

---

### Task 2: Spec fills the three sets from one source, and the language carries the standard modules

**Files:**
- Modify: `xarch/profile_values/language.py` (`CheckedLanguage` docstring and fields, lines 31-74)
- Modify: `xarch/modules/spec/application/services/architecture.py` (import line 29; `_language_presets`, lines 153-162)
- Modify: `xarch/modules/spec/application/ports/runtime.py` (class docstring, lines 7-9)
- Modify: `xarch/bootstrap/wiring.py` (`RUNTIME` docstring, lines 73-75)
- Modify: `tests/fakes/runtime.py`
- Modify: `tests/modules/spec/languages.py`
- Modify: `tests/architecture/test_language_seam.py` (`EXEMPT`)
- Test: `tests/modules/spec/application/test_language.py`, `tests/modules/spec/application/logic/test_libraries_and_guards.py`, `tests/modules/spec/application/logic/test_never_use.py`

**Interfaces:**
- Consumes: `INTERPRETER`, `StandardLists`, `Language.standard: str | StandardLists` (Task 1).
- Produces:
  - `CheckedLanguage.standard_modules: frozenset[str] = frozenset()` (the last field)
  - `ArchitectureService._named(language: Language) -> Language`
  - `FakeRuntime.asked: list[str]`, each source it was asked about, in order
  - `tests.modules.spec.languages.named(language, standard, bound, reserved) -> Language`; `BRACE` with `standard_names == {"fs", "path", "node:fs", "node:path"}`, `builtin_names == {"globalThis", "fetch"}`, `reserved_names == {"class", "const", "function", "interface"}` and `checked.standard_modules == standard_names`

- [ ] **Step 1: The fake runtime records what it is asked**

Replace the whole of `tests/fakes/runtime.py` with:

```python
"""In-memory implementation of spec's Runtime port. Not an adapter: a test double only."""
from __future__ import annotations


class FakeRuntime:
    """Satisfies spec's Runtime: the standard library, the builtins and the reserved words as given, whatever the
    source; it records each source it is asked about, in order (asked)."""

    def __init__(self, standard: frozenset[str] = frozenset(), builtins: frozenset[str] = frozenset(),
                 reserved: frozenset[str] = frozenset()):
        self._standard, self._builtins, self._reserved = standard, builtins, reserved
        self.asked: list[str] = []

    def standard_library(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._standard

    def reserved_words(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._reserved

    def builtin_names(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._builtins
```

- [ ] **Step 2: Write the failing tests of the service**

In `tests/modules/spec/application/test_language.py`:

Change the expectation of `test_a_profile_without_a_language_has_the_first_language_by_name_as_the_checks_read_it`
(lines 31-33) to:

```python
    assert view(BASE, {"python": PYTHON, "pascal": PASCAL}) == CheckedLanguage(
        "Pascal", ".pas", "unit.pas", (InterfaceMark(("sys", "Contract")),), (("sys", "load"),), names=r"\w+", package=r"\w+",
        member=".", standard_modules=frozenset({"strutils"}))
```

Change the expectation in `test_a_profile_names_its_language_and_the_skeleton_says_the_file_that_stands_for_a_folder`
(lines 38-40) to:

```python
    assert spec.profile("base").language == CheckedLanguage(
        "Python", ".py", "__init__.py", (InterfaceMark(("typing", "Protocol")),), (), names=r"\w+", package=r"\w+",
        member=".", standard_modules=frozenset({"strutils"}))
```

Change the second param of `test_xarch_with_no_language_to_choose_from_or_one_reads_the_profile_all_the_same`
(lines 55-56) to:

```python
    pytest.param({"python": PYTHON}, CheckedLanguage("Python", ".py", "__init__.py", (InterfaceMark(("typing", "Protocol")),),
                                                     names=r"\w+", package=r"\w+", member=".",
                                                     standard_modules=frozenset({"strutils"})),
                 id="with one, it is that one"),
```

After the definition of `RUNTIME` (line 22), add:

```python
LISTED = PASCAL | {"standard": {"modules": ["fs", "path"], "reserved": ["class"], "builtins": ["fetch"]}}
"""Pascal giving its standard library, its reserved words and its builtins as lists, none of them the runtime's."""
```

Append at the end of the file:

```python
def test_a_language_that_lists_its_standard_library_is_checked_with_its_lists_and_only_another_asks_the_runtime():
    runtime = FakeRuntime(frozenset({"strutils"}), frozenset({"writeln"}), frozenset({"begin"}))
    listing = BASE | {"parts": {"core": {"path": "core", "role": "r", "libraries": ["fs"]}}}
    spec, _ = spec_controller({"base": BASE, "listing": listing}, languages={"listed": LISTED, "pascal": PASCAL},
                              runtime=runtime)
    checked = spec.check_profile(CheckProfile(APP, "listing"))
    assert isinstance(checked, ProfileChecked)
    assert [problem.text for problem in checked.problems] == [
        "listing: parts.core.libraries: 'fs' is in the standard library, which every part may import unless `reserved` "
        "names it"]
    assert (spec.profile("base").language.standard_modules, spec.skeleton("base").reserved) == (
        frozenset({"fs", "path"}), frozenset({"class"}))
    assert runtime.asked and set(runtime.asked) == {"interpreter"}


def test_a_bare_name_a_language_lists_among_its_builtins_is_told_to_be_written_in_its_namespace():
    banned = BASE | {"never": {"ambient": ["fetch"]},
                     "parts": {"core": {"path": "core", "role": "r", "uses": {"never": "ambient"}}}}
    spec, _ = spec_controller({"base": banned}, languages={"listed": LISTED}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert isinstance(checked, ProfileChecked)
    assert "base: never.ambient: 'fetch' is a Pascal builtin, which a bare name does not ban: write system.fetch" in [
        problem.text for problem in checked.problems]


def test_the_standard_modules_the_reader_is_handed_are_the_standard_names_the_profile_is_checked_with():
    runtime = FakeRuntime(frozenset({"strutils"}), frozenset({"writeln"}), frozenset({"begin"}))
    for languages, standard in (({"listed": LISTED}, {"fs", "path"}), ({"pascal": PASCAL}, {"strutils"})):
        spec, _ = spec_controller({"base": BASE}, languages=languages, runtime=runtime)
        assert spec.profile("base").language.standard_modules == frozenset(standard)
```

In `tests/modules/spec/application/logic/test_libraries_and_guards.py`, add after the import of `fill` (line 7):

```python
from tests.modules.spec.languages import BRACE
```

(keep the imports sorted as ruff's isort wants them: `tests.modules.spec.format_files`, `tests.modules.spec.languages`,
`tests.modules.spec.profiles`, then the `xarch` imports; put the new line between the two `tests.modules.spec` lines.)

Append after `test_a_bad_reserved_module_is_refused_saying_what_to_write`:

```python
def test_the_standard_library_a_profile_reserves_from_is_the_one_of_the_language_of_the_app():
    braced = {"brace": BRACE}
    assert parsed(reserving({"fs": "the runtime's"}), languages=braced).reserved == {"fs": "the runtime's"}
    assert problems(reserving({"fs": "the runtime's"})) == [
        "layered.yaml: reserved: 'fs' is not in the Python standard library: an outside package is imported only by the "
        "parts whose `libraries` list it already"]
    assert parsed(reserving({"pickle": "the runtime's"})).reserved == {"pickle": "the runtime's"}
    assert problems(reserving({"pickle": "the runtime's"}), languages=braced) == [
        "layered.yaml: reserved: 'pickle' is not in the Brace standard library: an outside package is imported only by "
        "the parts whose `libraries` list it already"]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/test_language.py tests/modules/spec/application/logic/test_libraries_and_guards.py`
Expected: FAIL. `CheckedLanguage.__init__() got an unexpected keyword argument 'standard_modules'` in
`test_language.py`, and in `test_libraries_and_guards.py` the brace rows fail (`'fs' is not in the Brace standard
library`, since `BRACE` has no standard names yet).

- [ ] **Step 4: `CheckedLanguage` carries the standard modules**

In `xarch/profile_values/language.py`, in the docstring of `CheckedLanguage`, replace its last sentence:

old:
```
    regular expression (empty: its data file gives none); package is the pattern of what an import names from
    outside the app as one step, and member the text that joins a package to a name in it in a profile's lists (both
    empty: its data file does not say, and an outside name is then its whole text)."""
```
new:
```
    regular expression (empty: its data file gives none); package is the pattern of what an import names from
    outside the app as one step, and member the text that joins a package to a name in it in a profile's lists (both
    empty: its data file does not say, and an outside name is then its whole text); standard_modules are the top-level
    modules of its standard library, which the reader is handed to mark an import of one: spec fills them from the
    data file's lists or from the runtime (empty: no module is standard)."""
```

Add the field as the last one, after `unannotated: str = ""`:

```python
    standard_modules: frozenset[str] = frozenset()
```

- [ ] **Step 5: The service fills the three sets and the standard modules from one source**

In `xarch/modules/spec/application/services/architecture.py`, change the import at line 29 to:

```python
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource, FileType, Language, StandardLists
```

Replace `_language_presets` (lines 153-162) with:

```python
    def _language_presets(self) -> dict[str, Language]:
        """The languages xarch ships, read once, each with the names of its standard library, its reserved words and the
        names it binds without an import (see _named)."""
        if self._languages is None:
            self._languages = {name: self._named(language_of(name, document))
                               for name, document in self._files.language_presets().items()}
        return self._languages

    def _named(self, language: Language) -> Language:
        """The language with the names its data file lists, or, for INTERPRETER, the runtime's, the runtime asked then
        and only then; the standard modules the reader is handed are the very set of its standard names."""
        if isinstance(language.standard, StandardLists):
            standard = frozenset(language.standard.modules)
            reserved = frozenset(language.standard.reserved)
            bound = frozenset(language.standard.builtins)
        else:
            standard = self._runtime.standard_library(language.standard)
            reserved = self._runtime.reserved_words(language.standard)
            bound = self._runtime.builtin_names(language.standard)
        return replace(language, checked=replace(language.checked, standard_modules=standard), standard_names=standard,
                       reserved_names=reserved, builtin_names=bound)
```

- [ ] **Step 6: Exempt the read of the format's key in the service**

In `tests/architecture/test_language_seam.py`, add to `EXEMPT`, after the two entries of Task 1:

```python
    ("modules/spec/application/services/architecture.py", "builtins"): "the same key of the format, read from "
                                                                        "StandardLists to fill the names a language "
                                                                        "binds without an import",
```

- [ ] **Step 7: The test languages are filled as the service fills them**

Replace the whole of `tests/modules/spec/languages.py` with:

```python
"""The data file of the language the tests' sources are written in, as the bundled preset says it, and the language it
reads into; and the two test-only languages of tests/fakes/languages/, which no profile names: the builders of every
module's tests share them."""
from __future__ import annotations

import builtins
import keyword
import sys
from dataclasses import replace
from importlib import resources
from pathlib import Path

import yaml

from tests.fakes.runtime import FakeRuntime
from xarch.modules.spec.application.logic.language_file import language_of
from xarch.modules.spec.domain.values import Language


def named(language: Language, standard: frozenset[str], bound: frozenset[str], reserved: frozenset[str]) -> Language:
    """The language with the names of its standard library, the names it binds without an import and its reserved
    words, the standard modules the reader is handed being its standard names, as spec's service fills them."""
    return replace(language, checked=replace(language.checked, standard_modules=standard), standard_names=standard,
                   builtin_names=bound, reserved_names=reserved)


PYTHON_DOCUMENT = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                 .read_text(encoding="utf-8"))
RUNTIME = FakeRuntime(frozenset(sys.stdlib_module_names), frozenset(dir(builtins)), frozenset(keyword.kwlist))
PYTHON = named(language_of("python", PYTHON_DOCUMENT), RUNTIME.standard_library("interpreter"),
               RUNTIME.builtin_names("interpreter"), RUNTIME.reserved_words("interpreter"))

TEST_LANGUAGES = Path(__file__).resolve().parents[2] / "fakes" / "languages"
BRACE_DOCUMENT = yaml.safe_load((TEST_LANGUAGES / "brace.yaml").read_text(encoding="utf-8"))
BRACE = named(language_of("brace", BRACE_DOCUMENT),
              *(frozenset(BRACE_DOCUMENT["standard"][key]) for key in ("modules", "builtins", "reserved")))
"""The TypeScript-like test-only language, the lists its data file gives filled in as spec's service fills them."""
PERCENT = language_of("percent", yaml.safe_load((TEST_LANGUAGES / "percent.yaml").read_text(encoding="utf-8")))
"""The ObjectScript-like test-only language."""
```

- [ ] **Step 8: Drop the replacement the brace file now makes redundant**

In `tests/modules/spec/application/logic/test_never_use.py`, in
`test_the_standard_library_a_list_may_not_be_named_from_is_the_language_s` (line 470), change:

old:
```python
    assert problems(document, languages={"brace": replace(BRACE, standard_names=frozenset({"fs"}))}) == [
```
new:
```python
    assert problems(document, languages={"brace": BRACE}) == [
```

and delete `from dataclasses import replace` (line 4), which nothing else in the file uses. The expectation below
it (`standard('fs', 'Brace')`) does not change. `test_a_bare_builtin_is_told_to_be_written_in_the_namespace_with_the_member_of_the_language`
(line 333) now gets `fetch` from the data file instead of an override, and its expectation does not change either.

- [ ] **Step 9: The runtime's docstrings say when it is asked**

In `xarch/modules/spec/application/ports/runtime.py`, replace the class docstring with:

```python
    """What only the runtime of a language knows: names that no data file could keep current. Each is known from
    source, the word a language's data file gives as its `standard` (interpreter), so that each language gets its own;
    a language whose data file lists its standard library, its reserved words and the names it binds without an
    import is never asked. Each raises InvalidArchitecture for a source it does not read."""
```

In `xarch/bootstrap/wiring.py`, replace the docstring of `RUNTIME` (lines 73-75) with:

```python
"""What that language says of itself (its standard library, reserved words and the names it binds before any code),
as the interpreter running xarch says it, for a language whose data file gives `standard: interpreter`; a language
whose data file lists them is not asked, and needs no runtime of its own."""
```

- [ ] **Step 10: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/profile_values tests/architecture/test_language_seam.py tests/architecture/test_agnostic.py`
Expected: all pass. If a test that loads `brace` fails because `fs`, `path`, `node:fs` or `node:path` is now standard,
or `globalThis` or `fetch` is now a builtin, stop and report it with the failure; do not change its expectation.
(The planner's search, `grep -rn "BRACE\b\|brace" tests`, found no test whose expectation these names move.)

- [ ] **Step 11: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!`

- [ ] **Step 12: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/services/architecture.py \
        xarch/modules/spec/application/ports/runtime.py xarch/bootstrap/wiring.py tests/fakes/runtime.py \
        tests/modules/spec/languages.py tests/architecture/test_language_seam.py \
        tests/modules/spec/application/test_language.py tests/modules/spec/application/logic/test_libraries_and_guards.py \
        tests/modules/spec/application/logic/test_never_use.py
git commit -m "Spec fills the standard names, reserved words and builtins of a listed language from its lists and asks the runtime only for interpreter; the checked language carries the standard modules, the very set the profile is checked with; brace's reserved fs loads and python's is refused, and the other way round for pickle"
```

---

### Task 3: The reader is handed the standard modules

**Files:**
- Modify: `xarch/modules/rules/application/ports/source_tree.py` (`read`, lines 23-28; `parsed`, lines 39-42)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (docstring after line 15; `import sys` line 97; `read` 139-160; `parsed` 167-168; `_parsed` 207-219; `_standard` 271-272; `_imports` 290-300)
- Modify: `xarch/modules/rules/application/services/source_check.py:74-81`, `holding.py:27,37-38`, `sources.py:52`, `asking.py:26`, `examples.py:52,59`, `source_reading.py:16,23`
- Modify: `xarch/modules/spec/application/ports/example_reader.py` (`imports` docstring)
- Modify: `tests/fakes/filesystem.py` (`FakeSourceTree`, lines 17-56)
- Modify: `tests/modules/rules/builders.py` (`PYTHON` lines 37-47, `BRACE` lines 52-55, `imp` lines 149-155)
- Modify: `tests/architecture/test_language_seam.py` (`WORDS_BESIDES`, lines 111-112)
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/modules/rules/application/logic/test_filters.py`
- Create: `tests/modules/rules/application/test_standard_handed.py`

**Interfaces:**
- Consumes: `CheckedLanguage.standard_modules` (Task 2); `tests.modules.rules.builders.PYTHON`, `BRACE_FILE`.
- Produces:
  - `SourceTree.read(root, paths, table=None, immutable=(), interface=(), *, standard: frozenset[str]) -> list[SourceFile]`
  - `SourceTree.parsed(text: str, standard: frozenset[str]) -> SourceFile`
  - `FakeSourceTree.handed: list[frozenset[str]]`, the set each `read` and `parsed` call was handed, in call order
  - `imp(line, module, *names, up=None, language: CheckedLanguage = PYTHON) -> Import`

- [ ] **Step 1: Write the failing tests of the reader**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, keep the module docstring (line 1) and change the imports
after it (lines 2-5) to:

```python
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import xarch
```

keeping every later import line as it is. After the line `PYTEST = CaseTable(...)` (line 30) add:

```python
STANDARD = frozenset(sys.stdlib_module_names)
"""The modules spec hands the reader for the language the tests' sources are written in: the interpreter's standard
library."""
```

Then hand `STANDARD` at every direct call of the reader (11 sites). Each line below is old → new:

- line 35: `return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], table)[0]` → `return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], table, standard=STANDARD)[0]`
- line 89: `return FsSourceTree(FileSystem()).read(tmp_path / root, [tuple(steps)])[0]` → `return FsSourceTree(FileSystem()).read(tmp_path / root, [tuple(steps)], standard=STANDARD)[0]`
- line 181: `found = FsSourceTree(FileSystem()).parsed("from .order import Order\nimport os\n\nOrder()\nos.getcwd()\n")` → `found = FsSourceTree(FileSystem()).parsed("from .order import Order\nimport os\n\nOrder()\nos.getcwd()\n", STANDARD)`
- line 209: `found = FsSourceTree(FileSystem()).read(tmp_path / "app", [("domain", "services.py")])[0]` → `found = FsSourceTree(FileSystem()).read(tmp_path / "app", [("domain", "services.py")], standard=STANDARD)[0]`
- line 246: `.read(tmp_path, [("a.py",)], immutable=MARKS)[0]` → `.read(tmp_path, [("a.py",)], immutable=MARKS, standard=STANDARD)[0]`
- line 272: `.read(tmp_path, [("a.py",)], interface=INTERFACE)[0]` → `.read(tmp_path, [("a.py",)], interface=INTERFACE, standard=STANDARD)[0]`
- line 284: `.read(tmp_path, [("a.py",)], interface=(InterfaceMark(keyword=keyword),))[0]` → `.read(tmp_path, [("a.py",)], interface=(InterfaceMark(keyword=keyword),), standard=STANDARD)[0]`
- line 934: `FsSourceTree(FileSystem()).parsed(text).imports` → `FsSourceTree(FileSystem()).parsed(text, STANDARD).imports`
- line 942: `FsSourceTree(FileSystem()).parsed(text).error` → `FsSourceTree(FileSystem()).parsed(text, STANDARD).error`
- line 996: `FsSourceTree(FileSystem()).parsed("def f():\n    pass\n").pieces` → `FsSourceTree(FileSystem()).parsed("def f():\n    pass\n", STANDARD).pieces`
- line 1011: `FsSourceTree(FileSystem()).parsed(text).comments` → `FsSourceTree(FileSystem()).parsed(text, STANDARD).comments`

Confirm none is left: `grep -n "FsSourceTree(FileSystem())\.\(read\|parsed\)(" tests/modules/rules/adapters/test_fs_source_tree.py | grep -v STANDARD`
must print nothing.

Right after `test_the_imports_are_recorded_in_terms_no_language_owns` (which ends at line ~934), add:

```python
@pytest.mark.parametrize("standard, marked", [
    pytest.param(frozenset({"fs"}), [True, True, True, False],
                 id="an import whose first step is a module the reader is handed is of the standard library"),
    pytest.param(frozenset(), [False, False, False, False], id="handed none, no import is"),
])
def test_an_import_is_of_the_standard_library_by_the_modules_the_reader_is_handed(tmp_path, standard, marked):
    (tmp_path / "x.py").write_text("import fs\nimport fs.sub\nfrom fs.sub import x\nimport os\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=standard)[0]
    assert [i.standard for i in read.imports] == marked


def test_a_relative_import_is_never_of_the_standard_library_whatever_the_reader_is_handed(tmp_path):
    (tmp_path / "fs.py").write_text("")
    (tmp_path / "x.py").write_text("from . import fs\nfrom .fs import x\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=frozenset({"fs"}))[0]
    assert [i.standard for i in read.imports] == [False, False]


def test_a_text_in_no_file_marks_its_imports_as_a_file_does(tmp_path):
    text = "import fs\nfrom fs.sub import x\nimport os\nfrom .fs import y\n"
    (tmp_path / "x.py").write_text(text)
    tree = FsSourceTree(FileSystem())
    read = tree.read(tmp_path, [("x.py",)], standard=frozenset({"fs"}))[0]
    assert [i.standard for i in tree.parsed(text, frozenset({"fs"})).imports] == [i.standard for i in read.imports] == [
        True, True, False, False]


def test_handed_the_interpreter_s_standard_library_every_import_of_xarch_s_own_source_is_marked_by_its_first_step():
    root = Path(xarch.__file__).parent
    tree = FsSourceTree(FileSystem())
    imports = [i for f in tree.read(root, tree.paths(root, ".py"), standard=STANDARD) for i in f.imports
               if not i.relative]
    assert {i.standard for i in imports} == {True, False}
    assert [i for i in imports if i.standard != (i.module[0] in STANDARD)] == []
```

- [ ] **Step 2: Write the failing tests of the services**

Create `tests/modules/rules/application/test_standard_handed.py`:

```python
"""Use case: every service that reads the app's code hands the reader the standard modules of the profile's language,
so that an import is marked of the standard library as `check` marks it; the reading of a text for spec, which has no
profile, hands none."""
from dataclasses import replace
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.application.services.asking import AskingService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.holding import HoldingService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.application.services.sources import SourcesService
from xarch.modules.rules.contract import AskHolds, KeepFacts, ReadSources, Resemblance, Reviewed
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.profile_values.checks import APP, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

STANDARD = frozenset({"fs"})
"""The standard modules of the profile's language: neither none nor the interpreter's, so that only the profile can have
given them."""
LANGUAGE = replace(PYTHON, standard_modules=STANDARD)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"
PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []}, more={TESTS: {"kernel/test_ids.py": []}},
                          parsed=PARSED)


def test_the_check_hands_them_for_the_app_and_for_the_tests():
    found = tree()
    SourceCheckService(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check(ROOT, "app", "mine", TESTS)
    assert found.handed == [STANDARD, STANDARD]


def test_the_holds_question_hands_them_for_the_files_given_and_for_the_other_files_of_the_app():
    found = tree()
    HoldingService(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.handed == [STANDARD, STANDARD]


def test_the_sources_read_for_a_module_that_reads_the_app_s_code_hand_them():
    found = tree()
    SourcesService(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel/ids.py"),), Path("/src"), ROOT, "mine"))
    assert found.handed == [STANDARD]


def test_an_eval_s_facts_are_read_with_them():
    found = tree()
    evals = profile(asked={"rule": Asked("file", Scope(APP, "domain"))}, language=LANGUAGE)
    AskingService(found, FakeProfiles({"mine": evals})).kept(KeepFacts("mine", "app", "rule", ((DOMAIN, "nothing"),)))
    assert found.handed == [STANDARD]


def test_the_examples_of_a_profile_s_own_checks_and_evals_are_read_with_them():
    found = tree()
    checks = {"no-managers": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                          (Saying("{name}", "rename it"),), flagged=((DOMAIN, "manager"),),
                                          clean=((DOMAIN, "nothing"),))}
    evals = {"rule": Asked("class", Scope(APP, "domain"), (), ((DOMAIN, "manager"),), ((DOMAIN, "manager"),))}
    reviewed = {"mine": Reviewed("mine", (), 2, Resemblance(False, "cli"))}
    owned = profile(written=checks, asked=evals, language=LANGUAGE)
    ExamplesService(found, FakeProfiles({"mine": owned}, reviewed=reviewed)).check(Path("/p/app"), "mine")
    assert found.handed == [STANDARD, STANDARD, STANDARD, STANDARD]


def test_a_text_read_for_spec_hands_none_since_no_profile_says_them():
    found = tree()
    reader = SourceReadService(found)
    reader.imports("nothing")
    reader.comments("nothing")
    assert found.handed == [frozenset(), frozenset()]
```

In `tests/modules/rules/application/logic/test_filters.py`, change line 28 to:

```python
from tests.modules.rules.builders import BRACE, imp, source
```

and append at the end of the file:

```python
def test_the_standard_filter_holds_of_the_imports_marked_by_the_standard_modules_of_the_language_read():
    read_as_brace = source("modules/docs/domain/doc.py", imp(1, "fs", "readFile", language=BRACE),
                           imp(2, "lodash", language=BRACE))
    built = facts_of([read_as_brace], [], PROFILE, "app", "tests")
    read = built.files[0]
    assert [fact.line for fact in read.facts["import"]
            if question(condition("standard"))(Found(RULE, read, fact, None), built, PROFILE)] == [1]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/test_standard_handed.py tests/modules/rules/application/logic/test_filters.py`
Expected: FAIL. The reader's tests fail with `TypeError: FsSourceTree.read() got an unexpected keyword argument
'standard'` (and `parsed() takes 2 positional arguments but 3 were given`). The new services file fails with
`AttributeError: 'FakeSourceTree' object has no attribute 'handed'`. `test_filters.py` fails with `TypeError: imp()
got an unexpected keyword argument 'language'`.

- [ ] **Step 4: The port takes the set**

In `xarch/modules/rules/application/ports/source_tree.py`, replace `read` and `parsed` with:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str]) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so. An absolute import is of the standard library when its first step is one of the modules
        `standard` holds; a relative one never is."""
        ...
```

```python
    def parsed(self, text: str, standard: frozenset[str]) -> SourceFile:
        """A source text of the app's language that is in no file, parsed as a file of it is, an absolute import of
        the standard library when its first step is one of the modules `standard` holds; one that does not parse
        holds its error."""
        ...
```

- [ ] **Step 5: The reader marks an import by the handed set**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

After the module docstring's paragraph ending `...since that import names none of them from the top.` (line 15),
insert a blank line and this paragraph:

```
An absolute import is of the standard library when its first step is one of the standard modules the reader is
handed, which spec reads from the language's data file or from the interpreter running xarch; a relative import
never is, nor one that names no module.
```

Delete `import sys` (line 97). Its one use is deleted below.

Replace `read` and `parsed` of `FsSourceTree` with:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str]) -> list[SourceFile]:
        """Each file below root, read as UTF-8 and parsed; one that is not UTF-8, or cannot be read, holds why as its
        error, as one that does not parse does."""
        found: list[SourceFile] = []
        for path in paths:
            name = root.joinpath(*path).relative_to(root.parent).as_posix()
            try:
                text = self._fs.read_text(root.joinpath(*path))
            except UnicodeDecodeError as e:
                found.append(SourceFile(name, path, (), error=Unparsable(
                    0, f"not UTF-8 text (byte {e.object[e.start]:#04x} at offset {e.start} cannot be decoded)",
                    unreadable=True)))
                continue
            except OSError as e:
                found.append(SourceFile(name, path, (), error=Unparsable(
                    0, f"cannot be read ({e.strerror or e})", unreadable=True)))
                continue
            found.append(_parsed(name, path, text, table, immutable, interface, standard,
                                 _Where((root.name, *path[:-1]), root, self._fs)))
        return found
```

```python
    def parsed(self, text: str, standard: frozenset[str]) -> SourceFile:
        return _parsed("", (), text, None, (), (), standard)
```

Replace the signature and the `return` of `_parsed`:

old:
```python
def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None,
            marks: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (),
            where: _Where | None = None) -> SourceFile:
```
new:
```python
def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None, marks: tuple[RecordMark, ...],
            interface: tuple[InterfaceMark, ...], standard: frozenset[str], where: _Where | None = None) -> SourceFile:
```

old:
```python
    return SourceFile(name, path, tuple(_imports(tree, where)), comments, _functions(tree, form, where),
```
new:
```python
    return SourceFile(name, path, tuple(_imports(tree, standard, where)), comments, _functions(tree, form, where),
```

Delete `_standard` (lines 271-272, with the two blank lines after it):

```python
def _standard(name: str) -> bool:
    return name in sys.stdlib_module_names
```

Replace `_imports` with:

```python
def _imports(tree: ast.AST, standard: frozenset[str], where: _Where | None = None) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split(".")), standard=alias.name.split(".")[0] in standard,
                             written=alias.name, last=_last(node)) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, tuple(a.name for a in node.names), node.level > 0,
                                max(node.level - 1, 0), not node.level and bool(module) and module[0] in standard,
                                "." * node.level + (node.module or ""), any(a.name == "*" for a in node.names),
                                _last(node), _from(node, where) is None))
    return found
```

Check: `grep -n "sys" xarch/modules/rules/adapters/fs_source_tree.py` prints nothing.

- [ ] **Step 6: Every service hands the set**

`xarch/modules/rules/application/services/source_check.py`, lines 74-81:

old:
```python
        marks, interface = rules.language.immutable, rules.language.interface
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table, marks, interface) \
            if tests is not None else []
```
new:
```python
        marks, interface, standard = rules.language.immutable, rules.language.interface, rules.language.standard_modules
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface, standard=standard)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table, marks, interface,
                                     standard=standard) if tests is not None else []
```

`xarch/modules/rules/application/services/holding.py`:

old (line 27):
```python
        given = [(path, self._tree.parsed(text)) for path, text in cmd.files]
```
new:
```python
        given = [(path, self._tree.parsed(text, profile.language.standard_modules)) for path, text in cmd.files]
```

old (lines 37-38):
```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface))
```
new:
```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface, standard=profile.language.standard_modules))
```

`xarch/modules/rules/application/services/sources.py`, line 52:

old:
```python
        read = self._tree.read(app, [found.steps])[0]
```
new:
```python
        read = self._tree.read(app, [found.steps], standard=profile.language.standard_modules)[0]
```

`xarch/modules/rules/application/services/asking.py`, line 26:

old:
```python
        parsed = [(path, self._tree.parsed(text)) for path, text in cmd.files]
```
new:
```python
        parsed = [(path, self._tree.parsed(text, profile.language.standard_modules)) for path, text in cmd.files]
```

`xarch/modules/rules/application/services/examples.py`, line 52:

old:
```python
                facts = project([(path, self._tree.parsed(code)) for path, code in files], profile, app, (rule,))
```
new:
```python
                facts = project([(path, self._tree.parsed(code, profile.language.standard_modules)) for path, code in files],
                                profile, app, (rule,))
```

line 59:

old:
```python
        facts = project([(path, self._tree.parsed(code)) for path, code in files], profile, app, rules)
```
new:
```python
        facts = project([(path, self._tree.parsed(code, profile.language.standard_modules)) for path, code in files],
                        profile, app, rules)
```

`xarch/modules/rules/application/services/source_reading.py`, lines 16 and 23, each:

old:
```python
        read = self._tree.parsed(text)
```
new:
```python
        read = self._tree.parsed(text, frozenset())
```

`xarch/modules/spec/application/ports/example_reader.py`, the docstring of `imports`:

old:
```python
        """The imports of an example's text, in order, or where and why it does not parse."""
```
new:
```python
        """The imports of an example's text, in order, or where and why it does not parse; none is marked of the
        standard library, since spec reads no such mark of an example's import."""
```

- [ ] **Step 7: The fake takes and records the set**

In `tests/fakes/filesystem.py`, replace the class docstring, `__init__`, `read` and `parsed` of `FakeSourceTree`:

```python
class FakeSourceTree:
    """Satisfies rules' SourceTree: root folders holding already-parsed source files, each given as its imports or
    as a whole SourceFile (whose name and path are filled in), by its path below the root; the text of any other
    file, by its path; what a text that is in no file parses to, by the text; and the links, each path that is one with
    the path it points to, given in full. It records the standard modules each read and each parse is handed, in call
    order (handed); the imports it returns are those the test built."""

    def __init__(self, root: Path, files: dict[str, list[Import] | SourceFile],
                 more: dict[Path, dict[str, list[Import] | SourceFile]] | None = None,
                 texts: dict[Path, str] | None = None, parsed: dict[str, list[Import] | SourceFile] | None = None,
                 links: dict[Path, Path] | None = None):
        self._trees = {root: files, **(more or {})}
        self._texts, self._parsed, self._links = dict(texts or {}), dict(parsed or {}), dict(links or {})
        self.handed: list[frozenset[str]] = []
```

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str]) -> list[SourceFile]:
        self.handed.append(standard)
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]
```

```python
    def parsed(self, text: str, standard: frozenset[str]) -> SourceFile:
        self.handed.append(standard)
        return _source("", (), self._parsed[text])
```

- [ ] **Step 8: The builders mark an import as the reader does under a language**

In `tests/modules/rules/builders.py`:

In `PYTHON = CheckedLanguage(...)` (lines 37-45), change its last line:

old:
```python
                         member=PYTHON_FILE["member"])
```
new:
```python
                         member=PYTHON_FILE["member"], standard_modules=frozenset(sys.stdlib_module_names))
```

and the docstring right after it:

old:
```python
"""Python as its data file says it, for the checks that read the tokens of its code; the patterns of a name and of a
package, and the member that joins them, read from it."""
```
new:
```python
"""Python as its data file says it, for the checks that read the tokens of its code; the patterns of a name and of a
package, and the member that joins them, read from it; its standard modules the interpreter's, as spec hands them."""
```

In `BRACE = CheckedLanguage(...)` (lines 52-55), change its last line:

old:
```python
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"])
```
new:
```python
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
```

and its docstring:

old:
```python
"""The TypeScript-like test-only language as a check reads it, its patterns, member, interface marks and annotations of
no value read from its data file."""
```
new:
```python
"""The TypeScript-like test-only language as a check reads it, its patterns, member, interface marks, annotations of
no value and standard modules read from its data file."""
```

Replace `imp` (lines 149-155) with:

```python
def imp(line: int, module: str, *names: str, up: int | None = None, language: CheckedLanguage = PYTHON) -> Import:
    """`import module` with no names, `from module import names` with some; up, for a relative import, how many
    folders above the importing file's own it climbs. It is marked standard, and written, as the reader marks it when
    handed the standard modules of language (Python unless given): absolute and its first step one of them; the
    module with one dot more than up before it."""
    steps = dotted(module) if module else ()
    relative = up is not None
    return Import(line, steps, names or None, relative, up or 0,
                  not relative and bool(steps) and steps[0] in language.standard_modules,
                  "." * ((up or 0) + 1) + module if relative else module)
```

- [ ] **Step 9: The seam guard's note on the interpreter's list**

In `tests/architecture/test_language_seam.py`, replace `WORDS_BESIDES` (lines 111-112):

old:
```python
WORDS_BESIDES = {"stdlib_module_names": "the interpreter's list of the standard library, which no data file can hold "
                                        "current: the platform reads it and the reader marks each import with it"}
```
new:
```python
WORDS_BESIDES = {"stdlib_module_names": "the interpreter's list of the standard library, which no data file can hold "
                                        "current: the platform reads it, and spec hands the reader the modules it "
                                        "lists"}
```

The word stays banned outside the reader and the platform. `platform/interpreter.py` still names it, and the tests at
lines 328-346 that prove the scan finds it stay as they are.

- [ ] **Step 10: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/architecture`
Expected: all pass. Then confirm the one reader of the mark is rules' facts, as the spec says:
`grep -rn "\.standard\b" xarch --include=*.py` prints only `xarch/modules/rules/application/logic/facts.py:182` and
`:281`.

- [ ] **Step 11: Run the whole suite, which holds Python's findings and docs to the corpora**

Run, in the background, recording the PID:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-6/pytest.log 2>&1 & echo $! > /tmp/xarch-3-6/pytest.pid
```

Read `/tmp/xarch-3-6/pytest.log` when it ends.
Expected: all pass, the corpora and golden-doc tests of `tests/bootstrap/` included, with no file under
`tests/bootstrap/corpora/` changed (`git status --short tests/bootstrap` prints nothing).

- [ ] **Step 12: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!`

- [ ] **Step 13: Commit**

```bash
git add xarch/modules/rules/application/ports/source_tree.py xarch/modules/rules/adapters/fs_source_tree.py \
        xarch/modules/rules/application/services/source_check.py xarch/modules/rules/application/services/holding.py \
        xarch/modules/rules/application/services/sources.py xarch/modules/rules/application/services/asking.py \
        xarch/modules/rules/application/services/examples.py xarch/modules/rules/application/services/source_reading.py \
        xarch/modules/spec/application/ports/example_reader.py tests/fakes/filesystem.py tests/modules/rules/builders.py \
        tests/architecture/test_language_seam.py tests/modules/rules/adapters/test_fs_source_tree.py \
        tests/modules/rules/application/logic/test_filters.py tests/modules/rules/application/test_standard_handed.py
git commit -m "The reader is handed the standard modules instead of reading the interpreter's list: an absolute import is standard when its first step is one of them; check, the holds question, sources, evals and own checks hand the profile's language's, a text read for spec hands none"
```

---

### Task 4: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:141`
- Modify: `CHANGELOG.md` (`## [Unreleased]`, `### Changed`, line 18)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-3-6/regenerate_docs.py`

**Interfaces:**
- Consumes: the behaviour of Tasks 1-3.
- Produces: nothing later tasks use.

- [ ] **Step 1: README**

In `README.md`, in the paragraph that starts `` `language` names the language of the app`` (line 136), replace:

old:
```
a computed name, the folder of compiled files, and where the standard library's names are known from (`interpreter`);
```
new:
```
a computed name, the folder of compiled files, and where the standard library's top-level modules, the reserved words
and the builtins are known from (`standard`: `interpreter`, the Python running xarch, or three lists, `modules`,
`reserved` and `builtins`, each item checked with the file's `package` or `name`);
```

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: all pass.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, `### Changed` (line 18), insert this entry as the first of the list, with
one blank line after the heading and one blank line after the entry:

```markdown
- A language's data file says its standard library as data, or where it is known from: `standard` is `interpreter`
  (the Python running xarch, as before) or a map of three lists, `{modules: [...], reserved: [...], builtins: [...]}`,
  the top-level modules of its standard library, its reserved words and its builtins, each module checked with the
  file's `package` pattern and each other item with its `name` pattern. The reader is handed the standard modules
  from the language instead of asking the interpreter itself, so the set a profile is checked with and the set an
  import is marked by are one. Refused: `standard: must be interpreter, or a map of modules, reserved and builtins,
  each a list of names`, `standard.modules: '<item>' is not a package name the language allows`, and
  `standard.reserved: '<item>' is not a name the language allows` (`standard.builtins` the same). No finding of a
  Python app changes.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-6/regenerate_docs.py` (never committed):

```python
"""Write docs/{cli,web,xarch}/testing.md from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        if "/".join(file.path) == "testing.md":
            (root / "docs" / folder / "testing.md").write_text(file.template, encoding="utf-8")
            print(f"docs/{folder}/testing.md written")
```

Run:

```bash
uv run python -I /tmp/xarch-3-6/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines, and an empty `git diff`. If the diff is not empty, stop and report it with the diff
(`git checkout -- docs/cli docs/web docs/xarch` restores the files). The docs must not move.

- [ ] **Step 4: Run the gates**

Run each one. Run the first in the background with a recorded PID, and read it at the end:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-6/pytest.log 2>&1 & echo $! > /tmp/xarch-3-6/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

Expected: the suite passes, both checks report no violation, ruff reports nothing, and the profile check loads.
`git status --short` shows no change under `tests/bootstrap/corpora/`, none to
`xarch/architectures/presets/language/python.yaml` or `tests/fakes/languages/percent.yaml`, and nothing under
`.claude/` staged.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "The README's language paragraph and the CHANGELOG say standard's two shapes, interpreter or the lists modules, reserved and builtins checked with the file's package and name, with the three refusal texts; the golden docs regenerate with no diff"
```

---

## Self-review against the spec

**Spec coverage.**
- 2.1 `standard` stays required, two shapes, items checked with `package`/`name`, any text when unjoined, unchecked
  when the joins are refused, the three refusal texts, `interpreter` allowed in any file, `python.yaml` untouched:
  Task 1 (Steps 1, 4), plus Global Constraints and the Task 4 gate check for `python.yaml`/`percent.yaml`.
- 2.2 `StandardLists`, `Language.standard: str | StandardLists`, its docstring: Task 1, Step 3.
  `CheckedLanguage.standard_modules` and its docstring: Task 2, Step 4. One `INTERPRETER` constant read by the loader
  and the adapter: Task 1, Steps 3-5.
- 2.3 the service fills the three sets from the lists or the runtime, `checked.standard_modules` the same set, the
  runtime not asked for a listed language, `_read` unchanged, `profile_checks`/`never_lists` untouched: Task 2,
  Step 5; the consequences for `reserved: {fs}` / `{pickle}` and the builtin hint: Task 2, Step 2 and Step 8.
- 2.4 the port (`read(..., *, standard)`, `parsed(text, standard)`, no default, docstrings), `FsSourceTree` (handed
  set, `_standard` and `import sys` gone, docstring), every caller, `SourceReadService` with `frozenset()`, the
  `ExampleReader` docstring, the grep for `.standard`, the fake recording `handed`, the docstrings of the runtime port,
  the adapter and `wiring.RUNTIME`: Task 3 Steps 4-7 and 10, Task 2 Step 9, Task 1 Step 5. `platform/interpreter.py`
  says nothing contrary ("What only the interpreter running xarch knows ...") and is unchanged.
- 2.5 Python's findings, the corpora, the golden docs, the gates on xarch itself, `keys.yaml` untouched: Task 3
  Step 11, Task 4 Steps 3-4.
- 3 `brace.yaml` lists and its header: Task 1, Step 6. `languages.py` fills `BRACE` and `PYTHON` as the service does,
  and the `fetch` override goes: Task 2, Step 7. `builders.py` `standard_modules` and `imp(..., language=)`: Task 3,
  Step 8. The rerun of every `brace` test and the redundant `replace` dropped: Task 2, Steps 8 and 10.
- 4.1 items 1-6: Task 1, Step 1 (item 7: deviation 5; the refusal-list test at lines 40-58 runs unchanged in Step 8).
  4.2 items 8-10: Task 2, Step 2. 4.3 items 11-12: Task 2, Steps 2 and 8. 4.4 item 13: Task 3, Step 2. 4.5 items
  14-17: Task 3, Step 1. 4.6 items 18-20: Task 3, Step 2 (deviation 6). 4.7 items 21-22: Task 3 Step 9 (deviation 3),
  Task 1 Step 8 and Task 2 Step 10 (`test_agnostic.py` run with `ALLOWED` empty; deviation 2). 4.8 item 23: Task 3
  Step 11, Task 4 Step 4.
- 5 docs: README and CHANGELOG in Task 4; the loader's docstring in Task 1, Step 4; the golden docs in Task 4, Step 3.
- 7 gates: Task 4, Step 4.

**Placeholder scan.** No "TBD" and no "similar to Task N". Every code step shows the code or the exact old → new
lines. The 11 reader call sites in the adapter test are listed one by one, with a grep that proves none is left.

**Type consistency.** `StandardLists(modules, reserved, builtins)` is the same in Task 1 (domain, loader, tests) and
Task 2 (service, `languages.py`). `standard_modules: frozenset[str]` is the same on `CheckedLanguage` (Task 2), at the
callers, in the builders and in the handed tests (Task 3). `read(..., *, standard: frozenset[str])` and
`parsed(text, standard)` are the same on the port, the adapter and the fake, and at every caller (Task 3).
`FakeRuntime.asked` (Task 2, Step 1) is what Task 2's test reads. `FakeSourceTree.handed` (Task 3, Step 7) is what
`test_standard_handed.py` reads.

**Review Focus.** Each of the five lines has its test: 1 and 2 in Task 1, Step 1 (the `None` row and the `os.path`
row); 3 in Task 2, Step 2 (`runtime.asked` with a listed and an `interpreter` language); 4 in Task 3, Step 1
(`import fs.sub`, `from fs.sub import x`); 5 in Task 3, Step 2 (the holds test expects two handed sets).
<!-- task-pipeline: validated -->
