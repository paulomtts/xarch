# 3.5 language: what makes a port (interface marks, fire-only) read from the data file

Card `f067d825`, subtask of `3c7754c4`. Release step 8 of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, section 3, line 266:
"Interface marks, Class.interface, nothing as a list, unannotated, special as a pattern | language-neutral 5c | Step 7.
Before 12.").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below: **LN**),
section 5 (lines 618-712) and section 13 rows 5c (lines 1097-1104). Ordering: LN line 1045 (row 5c, step 8: "Its marks
use 5b's parser") and LN line 1061 ("5a, 5b and 5c must stay in that order"). 5a and 5b are on this branch already
(immutable marks flow reader ← data file as `RecordMark`; outside names parsed by `outside_name`).

## 1. Goal

What makes a class a port, what makes a port fire-only, and what makes a name special stop being Python's shapes
written into the checking code. They become data of the language's data file, read by the loader into
`CheckedLanguage`, and the reader tells the checks whether a class is an interface. Python's findings, the recorded
corpora and the golden docs do not move; two test-only languages (TypeScript-like `brace`, ObjectScript-like
`percent`) prove the checks follow the data.

## 2. Observable behavior

### 2.1 The data file's `interface`: a list of marks (LN 5.1, lines 620-640)

- `interface` is a list of maps, each with exactly one key:
  - `{base: <outside name>}`: marks a declaration that has that name among its bases. The value is parsed by the same
    outside-name parser as `dynamic` and `immutable` (5b), with the language's `name`, `package`, `member` and
    `namespace`.
  - `{keyword: <word>}`: marks a declaration that is declared with, or carries, that keyword. The value is a name of
    the language (by its `name` pattern; any non-empty text with no space when the file gives none).
- Loaded into `CheckedLanguage.interface: tuple[InterfaceMark, ...]`, in the order written. `InterfaceMark` is a new
  frozen dataclass in `xarch/profile_values/language.py`, beside `RecordMark`:
  `InterfaceMark(base: tuple[str, ...] = (), keyword: str = "")` — exactly one of the two is set.
- `python.yaml` writes `interface: [{base: typing.Protocol}, {base: typing_extensions.Protocol}]` (LN lines 633-636).
- Left out or `[]`: the language marks no interface; no class is a port.
- Refusal (LN 5.5, line 698): a value that is not a list, or any item that is not a one-key map whose key is `base`
  or `keyword` and whose value is valid as above, adds the problem
  `interface: each mark is {base: <outside name>} or {keyword: <word>}` — said once for the key however many items
  are wrong. The old shape (`interface: [typing.Protocol]`, a list of strings) is refused with this message. When the
  `name`/`package`/`member` keys are already refused, `interface` is not read (as `_outside` does today).

### 2.2 `Class.interface`, set by the reader (LN 5.1, lines 638-641)

- `xarch/modules/rules/domain/parsed.py` `Class` gains `interface: bool = False` (after `immutable`), and its
  docstring says it: the class is an interface, as the reader was told one is marked (see `InterfaceMark`).
- The `SourceTree` port's `read` (`xarch/modules/rules/application/ports/source_tree.py:23-27`) gains a keyword
  parameter `interface: tuple[InterfaceMark, ...] = ()` after `immutable`, its docstring saying a class is an
  interface when one of the marks `interface` holds marks it so.
- The Python reader (`xarch/modules/rules/adapters/fs_source_tree.py`) sets `Class.interface` for a module-level class
  when a `{base}` mark's path is among the class's bases, the bases resolved to `Ref`s exactly as for `immutable`
  (a subscripted base, `Protocol[T]`, names `Protocol`; an import alias reaches its path). A `{keyword}` mark never
  marks a class in the Python reader: Python declares no class with a keyword. The module docstring says both, beside
  the paragraph on immutable records (around line 61).
- Callers pass the language's marks: `source_check.py:75-79` (the app and the tests reads) and `holding.py:37` pass
  `interface=rules.language.interface` / `profile.language.interface`. `sources.py:52` (one file read without marks
  today) stays as is.
- The test fake `tests/fakes/filesystem.py` `read` accepts the new parameter; it builds classes from what the test
  hands it, so tests that need a port hand-build `Class(..., interface=True)`.

### 2.3 The checking code reads `cls.interface` (LN 5.4, lines 684-686)

The checks never compare bases with marks again:

- `facts.py:172` (the class kind's `interface` trait / ports): `c.interface`.
- `stand_ins.py:115` (the ports of the parts the fakes stand in for): `cls.interface`.
- `twins.py:130` (no-twins leaves ports out): `not cls.interface`. LN does not name this site; it is the same
  comparison and is changed the same way. Its key's needs are not changed (LN names the three keys that need the fact).

A class with a `Protocol` base but `interface=False` is no port; a class with no base and `interface=True` is one.

### 2.4 New fact `class.interface` (LN 5.1, lines 641-642)

- `xarch/profile_values/capabilities.py` `FACTS` gains
  `"class.interface": "whether a class is an interface, by the marks of the language's data file"` (beside
  `class.immutable`, line 41).
- Needed by `guards.stand-ins` (`key_table.py:222`), `fakes` (the key that opens the fakes block, `key_table.py:59`,
  in whatever needs table lists `fakes`/`fakes.for`; add one where its port reading is listed) and the filter
  `interface` (`vocabulary.py` field needs of the class kind, line 225-228: `"interface": ("class.interface",)`).
- `python.yaml` `supplies` lists `class.interface: exact` (after `class.immutable`).
- A data file whose `supplies` lacks `class.interface` makes those keys refused, as for any missing fact; a test-only
  file without `supplies` holds no key to it (unchanged rule).

### 2.5 `nothing` a list; `unannotated` (LN 5.2, lines 649-667)

- `nothing` is a non-empty list of non-empty strings: the return annotations, as the reader writes them, that say a
  method gives no value. Loaded into `CheckedLanguage.nothing: tuple[str, ...]` (default `()`). `python.yaml` writes
  `nothing: [None]`.
- Refusal: not a list, empty, or holding a non-string or empty string: `nothing: must be a list of return annotations`.
  The old shape `nothing: None` is refused with it.
- New optional key `unannotated`, its only value the word `nothing`: a method with no return annotation gives no
  value. Loaded into `CheckedLanguage.unannotated: str = ""` (`"nothing"` when given). Refusal for any other value:
  `unannotated: must be nothing`. Python leaves it out. Added to `KEYS`.
- No hidden default (card dodge): `nothing` left out means no annotation says no value — never `None`.

### 2.6 Fire-only and read (`stand_ins.py:121-134`)

For a port's methods (special ones left out, but the `call` method kept, as today):

- A method gives no value when its annotation is in `nothing`, or it has no annotation and `unannotated` is `nothing`.
- A method with no annotation, when `unannotated` is not given, is reported as today, same text, same fix.
- Fire-only: every method gives no value. Read: some method gives a value (an annotation not in `nothing`). A port
  with a reported bare method, or with no method, has no kind, as today.

### 2.7 `special` a regular expression (LN 5.3, lines 669-680)

- `special` is a regular expression; `CheckedLanguage.is_special(name)` is `bool(special) and re.fullmatch(special,
  name)`. Its docstring says so.
- `python.yaml`: `special: '(?=__)\w*(?<=__)'`. It must give the same answer as the old `startswith("__") and
  endswith("__")` on every name Python allows: `__init__`, `__call__`, `__` and `___` special; `_x`, `x__`, `__x`,
  `x` not.
- Loaded with `_pattern`: a value that is not a string or does not compile is refused with
  `special: must be a regular expression` (a compile error adds `: <error>` as `_pattern` does today). It leaves the
  `tokens` loop.
- The callers (`facts.py:240`, `stand_ins.py:124`, `filters.py:130`, `profile_checks.py:635`) are untouched; they get
  the new behavior through `is_special`. `call: __call__` stays.

### 2.8 Words of the format and the docs (LN 5.1 line 649-650, LN 5.4 lines 687-690)

- `Language.interface_name` (`values.py:326-330`): the last step of the first mark's `base`, or the first mark's
  `keyword` (`Protocol`; `interface`); `""` with no mark.
- `explain.words` (`explain.py:28-37`): `interface_path` is the first mark's base written as an outside name
  (`outside_text`), or its keyword when the first mark is a keyword one, `""` with none; a new word `nothing` is the
  entries of `nothing` each as written, joined with ` or ` (`None` for Python; `void or Promise<void>` for brace). The
  docstring names it.
- `docs_template.py:619-623` prints the entries of `nothing`, each in backticks, joined with ` or `; one entry prints
  exactly as today (`` `None` ``).
- `keys.yaml:831` (the card's `keys.yaml:801`, moved by earlier steps): `every method returns None` becomes
  `every method returns %nothing%`; the header's list of words (line 6) still reads true.
- `vocabulary.py:280` filter `interface`: `"the class is an interface: the language marks it as one"` (no word of
  bases). `vocabulary.py:178` (`"whether a class is an interface"`) stays.

### 2.9 Data files

- `python.yaml`: the `interface`, `special`, `nothing` lines and `class.interface: exact`; the header comment
  (lines 3-4, 11-13) says the new shapes (interface marks as maps, special a regular expression matched against the
  whole name, nothing a list, unannotated).
- `tests/fakes/languages/brace.yaml` gains `interface: [{keyword: interface}]` and `nothing: [void, "Promise<void>"]`
  (LN 5.6, lines 704-706).
- `tests/fakes/languages/percent.yaml`: `interface: [{keyword: Abstract}]` (in place of
  `["%Library.RegisteredObject"]`), `unannotated: nothing`, `special: '%\w+'` (LN 5.6, lines 707-708).
- Both still load through `language_of` with no problem.
- `language_file.py` module docstring describes `interface` (marks), `special` (a pattern), `nothing` (a list) and
  `unannotated`.

### 2.10 Docs

- README (lines 136-148): "what marks an interface" says a mark is a base or a keyword; "what a special name starts and
  ends with" becomes a pattern of a special name; "the annotation of no value" becomes the annotations of no value,
  and the optional `unannotated`.
- CHANGELOG `## [Unreleased]`, `### Changed` (create the heading after `### Added` if absent): the language data file
  writes interface marks as `{base: ...}` or `{keyword: ...}`, `nothing` as a list, `special` as a regular
  expression, and may say `unannotated: nothing`; the reader marks a class an interface, and a profile key that reads
  ports needs the new fact `class.interface`; the four refusal texts. No finding of a Python app changes (review 3,
  O4, O5).
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never hand-edited, and show **no diff** (LN line 650,
  line 712; O8).

## 3. Refusals (exact texts, LN 5.5 lines 694-699)

| Input | Problem (in `InvalidArchitecture("language/<name>.yaml", ...)`) |
|---|---|
| `interface: typing.Protocol`, `interface: [typing.Protocol]`, `[{base: x, keyword: y}]`, `[{kind: x}]`, `[{base: "not a name!"}]` | `interface: each mark is {base: <outside name>} or {keyword: <word>}` |
| `nothing: None`, `nothing: []`, `nothing: [""]`, `nothing: [1]` | `nothing: must be a list of return annotations` |
| `special: 3`, `special: ""` | `special: must be a regular expression` |
| `special: "("` | `special: must be a regular expression: <re.error text>` |
| `unannotated: none`, `unannotated: true` | `unannotated: must be nothing` |

All problems of a file are listed together, as today.

## 4. Tests (written first)

| Test | File | Tier and why |
|---|---|---|
| `{base}` and `{keyword}` marks load into `InterfaceMark`s in order; python's bundled file gives `(InterfaceMark(("typing","Protocol")), InterfaceMark(("typing_extensions","Protocol")))` | `tests/modules/spec/application/logic/test_language_file.py`, `tests/modules/spec/application/test_language.py:88` | unit: the loader is pure logic over a document |
| each refusal of section 3, exact text | `test_language_file.py` | unit: loader |
| `nothing` loads as a tuple; `unannotated: nothing` loads; `special` loads as the pattern text; the inline tokens dict at `:67` updated | `test_language_file.py` | unit |
| the test-only files load: brace's `interface`/`nothing`, percent's `{keyword: Abstract}`, `unannotated`, `special` | `test_language_file.py` (via `language_of` on the yaml of `tests/fakes/languages/`) | unit: proves the test-only files are valid data, not just read by the seam test |
| `is_special`: python's pattern gives True for `__init__`, `__`, `___`; False for `_x`, `x__`, `__x`; percent's `%\w+` True for `%OnNew`, False for `OnNew`; empty special False | `tests/profile_values/test_language.py` | unit: value object |
| reader: `class P(Protocol)`, `class P(typing.Protocol)`, `class P(typing_extensions.Protocol)`, `class P(Protocol[T])` read `interface=True` with python's marks; a plain class and a class with marks not passed read `False`; a `{keyword}` mark marks nothing | `tests/modules/rules/adapters/test_fs_source_tree.py` | adapter (integration with `ast` over real text): the reader is where the fact is made |
| stand-ins under python: hand-built `Class(interface=True)` with `-> None` methods is fire-only, one `-> Order` is read and needs a fake; a class with a Protocol base and `interface=False` is no port; findings and texts as before | `tests/modules/rules/application/logic/test_stand_ins.py` | unit: check logic over hand-built facts |
| stand-ins under brace: `Class(interface=True)` with methods returning `Promise<void>` / `void` fire-only; one returning `Promise<Order>` read, missing fake reported (LN 5.6 lines 704-706) | `test_stand_ins.py` | unit: neutrality proved on hand-built values, no TypeScript reader |
| stand-ins under percent: a port whose methods have no annotation is fire-only and reports no "no return annotation"; `%OnNew` left out of its methods (LN 5.6 lines 707-708) | `test_stand_ins.py` | unit |
| under python, a method with no annotation is still reported, same text | `test_stand_ins.py` (existing) | unit |
| the class kind's `interface` trait and the `interface` filter follow `Class.interface`; no-twins leaves `interface=True` classes out | `tests/modules/rules/application/logic/` facts/filters/twins tests | unit |
| hand-built ports in existing tests (`builders.py`, `world.py`, `test_dead_code.py`, `test_twins.py`, …) set `interface=True`; `builders.py` `PYTHON` built with `InterfaceMark`s, the regex special and `("None",)`; `BRACE` reads its `interface`/`nothing` from `brace.yaml`; a `PERCENT` built the same way from `percent.yaml` | `tests/modules/rules/builders.py` etc. | support code for the unit tier |
| `class.interface` in `FACTS`; `guards.stand-ins`, the fakes key and the `interface` filter need it; python supplies it exact | `tests/modules/spec/application/logic/test_profile_keys.py` (or the capability tests that cover `class.immutable`) | unit: key table |
| `interface_name` is `Protocol` for python, `interface` for brace, `Abstract` for percent; `explain.words` gives `nothing` = `None` for python and `void or Promise<void>` for brace, `interface_path` = `typing.Protocol` / `interface` | `tests/modules/spec/application/test_explain.py`, values tests | unit |
| seam: `language_words`/`language_tokens`/`ticked_pattern` read the map marks, the list `nothing` and the `special` pattern (LN 5.6, line 709-711: lines 134, 145, 189 of the time; now ~136, ~150-196, ~258); still no leak in xarch's code; `` `__init__` `` in a docstring still flagged; `keys.yaml` (and every format data file) writes no entry of python's `nothing` as a word (would have caught line 831) | `tests/architecture/test_language_seam.py` | architecture: guards the seam across the whole package |
| the seam's test-only-language test reads `base` steps and keyword words of brace and percent | `test_language_seam.py:256` | architecture |
| golden docs regenerate with no diff; bootstrap suites (`test_bundled_guards`, `test_source_checks`, `test_docs`, corpora) unchanged | `tests/bootstrap/` | end-to-end through the CLI: Python's findings do not move |

## 5. Gates (each green on this branch alone)

`uv run pytest -q` (over two minutes: run in the background and read at the end), `uv run xarch check`,
`uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## 6. Project rules

No comments in xarch's code (docstrings are the documentation; the yaml data files may comment); never `ruff --fix`;
tests first; examples simple with absolute `app.` imports; recorded corpora under `tests/bootstrap/corpora/` not
edited (LN does not ask it for 5c); Python only in the reader adapter and the data files under
`xarch/architectures/presets/` — no `if python:` and no TypeScript case in the checking code (card dodges); neutrality
claimed only with both test-only files exercising the new keys (card dodge: "claiming neutrality with one data file");
`.claude/` out of commits; nothing pushed.

## 7. Out of scope

- Records and `class.record`, immutable marks as maps: card 3.10 (LN section 10, line 1050).
- Privacy: card 3.9.
- Any reader for TypeScript or ObjectScript, and an `interfaces` kind of `holds` (LN line 646-647; step 12).
- The standard library / reserved words / builtins from the data file: LN section 6, steps 8a-8e.
- Changing the needs of `guards.no-twins` or `guards.dead-code`.
- `sources.py:52`'s mark-less read.

## 8. Risks for the planner

- `CheckedLanguage(` is built positionally in ~21 places (LN line 1104); `language_file.py:113` and
  `tests/modules/rules/builders.py:31` pass `interface`, `special`, `nothing` by position — keep field order and
  update every call, or switch those to keywords.
- Tests that hand-build a port with a `Protocol` base and rely on base matching break silently (no port found) until
  they set `interface=True`; run the stand-ins, dead-code, twins and facts tests after the switch.
- `special: __` is still a valid regular expression, so an old-shape file would load and mean only the name `__`;
  data files are bundled only, so python.yaml must be changed in the same commit as `is_special`.

---

# 3.5 language: what makes a port read from the data file — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** What makes a class a port (`interface`), what makes a port fire-only (`nothing`, `unannotated`) and what makes
a name special (`special`) become data of the language's data file. The loader reads them into `CheckedLanguage`, the
reader marks each class `interface=True/False`, and the checks read that mark. Python's findings, the corpora and the
golden docs do not move. The test-only `brace` and `percent` languages show the checks follow the data.

**Architecture:** `xarch/profile_values/language.py` gains `InterfaceMark` and the constant `NOTHING`.
`CheckedLanguage.interface` becomes a tuple of marks, `nothing` a tuple of annotations, and it gains `unannotated`.
`is_special` becomes a full match of a regular expression, and a new method `gives_nothing(returns)` holds the
fire-only rule. The loader (`language_file.py`) reads and refuses the new shapes. The Python reader
(`fs_source_tree.py`) sets the new `Class.interface` from `{base}` marks, as it already sets `immutable`. The three
checks that compared bases (`stand_ins.py`, `facts.py`, `twins.py`) read `cls.interface`. A new fact `class.interface`
is listed in `FACTS`, supplied by Python and needed by the keys that read ports.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140; the project keeps lines at 120), `uv run`.

**Spec:** `docs/superpowers/specs/3-5-language-what-makes-f067d825.md` (prepended above; read it whole before Task 1).

## Global Constraints

- No comments in xarch's code; docstrings only (the yaml data files may comment). Never `ruff --fix`. Keep every line
  at 120 characters or fewer.
- Tests are written first and run red before the code that makes them pass (a test that only pins today's behaviour
  is marked so in its step).
- Python is named only in the reader adapter (`xarch/modules/rules/adapters/fs_source_tree.py`) and the data files
  under `xarch/architectures/presets/`. No string literal or docstring elsewhere in `xarch/` may write `Python`,
  `builtins`, `typing`, `typing_extensions`, `Protocol`, `importlib`, `__init__`, `__pycache__` or `.py`, nor be
  exactly `_`, `__call__`, `None`, `#` or `#!`. No docstring of the engine may quote `None` or a special name as code
  (`tests/architecture/test_language_seam.py`). No `if python:` and no TypeScript or ObjectScript case in the checking
  code.
- No string literal in `xarch/` may hold, as a whole word, a part or folder name of the bundled profiles
  (`tests/architecture/test_agnostic.py`).
- `CheckedLanguage`'s field order is kept. New fields go at the end. Every call that builds one with many fields passes
  them by keyword.
- `tests/bootstrap/corpora/` is not edited. The golden docs `docs/{cli,web,xarch}/testing.md` regenerate with no diff
  and are never edited by hand.
- `sources.py:52`'s read with no marks stays as it is. The needs of `guards.no-twins` stay as they are.
- README and CHANGELOG lines go under `[Unreleased]`.
- `.claude/` stays out of every commit; nothing is pushed.
- Run long suites with `timeout` (`timeout 1200 uv run pytest -q`), in the background, and read the result at the
  end. Never `pkill`/`killall`; signal only a PID you recorded.

## Spec deviations (decided by the planner, with evidence)

1. **`guards.dead-code` needs `class.interface` too.** Spec 7 says the needs of `guards.dead-code` do not change. But
   spec 2.4 gives the class kind's field `interface` the field need `class.interface`, and the dead-code rule for
   ports is expanded with `keep=_all("interface")` (`expansion.py:299`). So `Rule.needs` (`rule.py:126-135`) derives
   `class.interface` for it. `tests/bootstrap/test_needs_agree.py` requires a key's table needs to equal the derived
   needs of the rules it expands to, and `guards.dead-code` is such a key: the planner ran
   `xarch profile explain guards.dead-code --rule` on that test's profile and got `ok: true`, `needs: ['class',
   'named']`. Adding the field need without adding the fact to `NEEDS["guards.dead-code"]` fails that test. The spec's
   intent (dead-code reads ports through the same mark) is kept. Python supplies the fact `exact`, so no bundled
   profile changes.
2. **`fakes` gets a new `NEEDS` entry `("class", "class.interface")`.** No needs table lists `fakes` or `fakes.for`
   today. The spec says to add one "where its port reading is listed". `fakes` is not a key the engine expands
   (`profile explain fakes --rule` answers `ok: false`), so `test_needs_agree` does not read it.
3. **The tests of `interface_name` and of the `%nothing%` and `%interface_path%` words go in
   `tests/modules/spec/application/logic/test_profile_keys.py`.** That file already holds the `said` tests for these
   words and imports `PERCENT` and `PYTHON`. `test_explain.py` and the values tests hold none.
4. **The fire-only rule is the method `CheckedLanguage.gives_nothing(returns)`.** The spec gives the behaviour only.
   A method of `CheckedLanguage` is something the engine may read (the seam test's `SAID`), and it keeps the literal
   `nothing` out of the checks.
5. **The seam guard's special-name check matches the data file's pattern as a whole word in a quoted span**
   (`(?<!\w)(?:<special>)(?!\w)`), and a literal fully matched by it is a token. The planner ran both over `xarch/`
   with Python's new pattern: no literal and no docstring span of the engine is found, before or after. The old
   `__\w+__` also found the inside of `a__init__`, and the new check does not. That is the only narrowing.
6. **The header comment of `python.yaml` is rewritten once, in Task 6.** Earlier tasks change only its keys.

## Review Focus

1. **A class of the file's own named like a mark** (`class Protocol: ...` then `class P(Protocol): ...`). A person
   expects no port: the base reaches no outside name. Test: Task 2, Step 1.
2. **A mark imported by an alias** (`from typing import Protocol as Port`, `class P(Port)`). A person expects a port,
   since the alias reaches the mark's path. Test: Task 2, Step 1.
3. **One bad mark among good ones** (`interface: [{base: sys.Contract}, sys.Other, {kind: x}]`). A person expects the
   key refused once, with nothing loaded, never one problem per item. Test: Task 3, Step 1.
4. **A language that gives no `nothing` and no `unannotated`**, and a port whose methods are all annotated `None`.
   A person expects every such port to be read, since no hidden `None` is assumed. Test: Task 5, Step 1
   (`gives_nothing` with `CheckedLanguage()`).
5. **A special method of percent annotated with a value** (`%OnNew -> Order`) beside unannotated ones. A person
   expects it left out of the port's methods, so the port stays fire-only. Test: Task 5, Step 2.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `xarch/profile_values/language.py` | `is_special` by pattern; `InterfaceMark`; `interface` marks; `nothing` tuple, `unannotated`, `NOTHING`, `gives_nothing` | 1, 2, 3, 5 |
| `xarch/modules/spec/application/logic/language_file.py` | loads and refuses `special`, `interface`, `nothing`, `unannotated` | 1, 3, 5 |
| `xarch/architectures/presets/language/python.yaml` | the new values, `class.interface: exact`, header | 1, 3, 4, 5, 6 |
| `tests/fakes/languages/brace.yaml`, `percent.yaml` | their interface marks, `nothing`, `unannotated`, `special` | 1, 3, 5 |
| `xarch/modules/rules/domain/parsed.py` | `Class.interface` | 2 |
| `xarch/modules/rules/application/ports/source_tree.py` | `read(..., interface=())` | 2 |
| `xarch/modules/rules/adapters/fs_source_tree.py` | sets `Class.interface` from `{base}` marks | 2 |
| `tests/fakes/filesystem.py` | the fake's `read` takes `interface` | 2 |
| `xarch/modules/rules/application/services/source_check.py`, `holding.py` | pass the language's marks | 3 |
| `xarch/modules/rules/application/logic/stand_ins.py`, `facts.py`, `twins.py` | read `cls.interface`; fire-only by `gives_nothing` | 3, 5 |
| `xarch/modules/spec/domain/values.py` | `interface_name` from a mark | 3 |
| `xarch/modules/spec/application/logic/explain.py` | `interface_path` from a mark; new word `nothing` | 3, 5 |
| `xarch/profile_values/capabilities.py`, `xarch/modules/spec/domain/key_table.py`, `xarch/modules/rules/domain/vocabulary.py` | the fact `class.interface` and who needs it | 4 |
| `xarch/modules/spec/application/logic/docs_template.py` | the stand-ins line prints each entry of `nothing` | 5 |
| `xarch/architectures/presets/format/keys.yaml` | `returns %nothing%` | 5 |
| `tests/modules/rules/builders.py` | `PYTHON` by keyword from its file; `BRACE`, `PERCENT` with their marks | 1, 3, 5 |
| `tests/architecture/test_language_seam.py` | reads the special pattern, the map marks, the list `nothing` | 1, 3, 5 |
| `README.md`, `CHANGELOG.md` | the new shapes | 6 |

---

### Task 1: A special name is the one the language's pattern matches in full

**Files:**
- Modify: `xarch/profile_values/language.py:1-8` (imports), `:21-34` (docstring), `:61-63` (`is_special`)
- Modify: `xarch/modules/spec/application/logic/language_file.py:24` (docstring), `:102-103`, `:113-115`
- Modify: `xarch/architectures/presets/language/python.yaml:34`
- Modify: `tests/fakes/languages/percent.yaml` (add `special`)
- Modify: `tests/modules/rules/builders.py:30-37` (`PYTHON`)
- Modify: `tests/architecture/test_language_seam.py:150-196` and its two parametrized token tests
- Test: `tests/profile_values/test_language.py`, `tests/modules/spec/application/logic/test_language_file.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `CheckedLanguage.is_special(name: str) -> bool` is `bool(special) and re.fullmatch(special, name) is not
  None`. `CheckedLanguage.special` holds a regular expression. The loader refuses a bad one with `special: must be a
  regular expression` or `special: must be a regular expression: <re.error>`. `builders.PYTHON` is built by keyword.

- [ ] **Step 1: Write the failing value tests**

Replace the whole of `tests/profile_values/test_language.py` with:

```python
"""The language as a check reads it: which names are public or special, by the tokens its data file gives."""
import itertools
from importlib import resources

import pytest
import yaml

from xarch.profile_values.language import CheckedLanguage

PYTHON_SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                .read_text(encoding="utf-8"))["special"]
TOKENS = CheckedLanguage(private="_", special=PYTHON_SPECIAL)
PERCENT = CheckedLanguage(special=r"%\w+")


@pytest.mark.parametrize("name, public, special", [
    pytest.param("load", True, False, id="a plain name is public"),
    pytest.param("_load", False, False, id="a name that starts as a private one does is not public"),
    pytest.param("__init__", False, True, id="a special name is special, and starts as a private one does"),
    pytest.param("__load", False, False, id="one that only starts as a special name does is not special"),
    pytest.param("load__", True, False, id="one that only ends as a special name does is not special"),
    pytest.param("__", False, True, id="the affix alone is special"),
    pytest.param("___", False, True, id="three underscores are special"),
    pytest.param("_x", False, False, id="one underscore makes no special name"),
])
def test_a_name_is_told_by_the_tokens_of_the_language(name, public, special):
    assert (TOKENS.is_public(name), TOKENS.is_special(name)) == (public, special)


def test_python_s_pattern_tells_every_short_name_as_its_affix_did():
    names = ["".join(chars) for size in range(1, 7) for chars in itertools.product("_a1", repeat=size)
             if chars[0] != "1"]
    assert [name for name in names if TOKENS.is_special(name) != (name.startswith("__") and name.endswith("__"))] == []


@pytest.mark.parametrize("name, special", [
    pytest.param("%OnNew", True, id="a name the pattern matches in full"),
    pytest.param("OnNew", False, id="a name it does not match"),
    pytest.param("x%OnNew", False, id="a name it matches only in part"),
])
def test_a_special_name_is_one_the_language_s_pattern_matches_in_full(name, special):
    assert PERCENT.is_special(name) is special


def test_a_language_that_gives_no_tokens_has_every_name_public():
    assert (CheckedLanguage().is_public("_load"), CheckedLanguage().is_special("__init__")) == (True, False)


def test_a_language_that_says_nothing_has_no_package_pattern_and_no_member():
    assert (CheckedLanguage().package, CheckedLanguage().member) == ("", "")
```

- [ ] **Step 2: Write the failing loader tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Add `import re` after line 1 (`"""The data file of a language..."""`), so the imports start:

```python
"""The data file of a language: what is true of the language as a whole, read from a preset and validated like a profile."""
import re
from pathlib import Path
```

In `test_the_tokens_of_the_code_are_read_when_the_document_gives_them` (line 67), change `"special": "__"` to
`"special": r"(?=__)\w*(?<=__)"`, and in its expected tuple (line 74) change the second item `"__"` to
`r"(?=__)\w*(?<=__)"`. The expected tuple then reads:

```python
        "[A-Za-z]+", "_", r"(?=__)\w*(?<=__)", "__call__", "None", "//", ("lint: off",), "#!", "utf-8", ("if", "case"),
        ("?",))
```

In the parametrize list of `test_a_token_that_is_not_what_its_key_takes_is_a_problem` (lines 77-97), add these two
rows after the `"an empty comment marker"` row:

```python
    pytest.param({"special": 3}, "special: must be a regular expression", id="a special name that is no text"),
    pytest.param({"special": ""}, "special: must be a regular expression", id="an empty special name"),
```

After that test, add:

```python
def test_a_special_name_that_is_no_regular_expression_says_why():
    with pytest.raises(re.error) as error:
        re.compile("(")
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"special": "("})
    assert caught.value.problems == (f"presets/language/odd.yaml: special: must be a regular expression: {error.value}",)
```

- [ ] **Step 3: Write the seam guard's new cases**

In `tests/architecture/test_language_seam.py`, in the parametrize list of
`test_the_guard_finds_a_token_of_the_language_where_it_is_written` (lines 295-304), add after the
`"the affix of a special name"` row:

```python
    pytest.param('A = "__init__"\nB = "x__"\nC = "__x"\n', ["__init__"],
                 id="a literal the pattern of a special name matches in full"),
```

In the parametrize list of `test_the_guard_finds_the_code_of_the_language_quoted_in_a_docstring` (lines 420-429),
add after the `"a special name, and the private prefix alone"` row (a pin: it passes before and after):

```python
    pytest.param('"""Its `__init__`, a `a__b` and `__`."""\n', ["__init__", "__"],
                 id="a special name by the pattern, as a whole word"),
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/profile_values/test_language.py tests/modules/spec/application/logic/test_language_file.py tests/architecture/test_language_seam.py`
Expected: FAIL. `test_a_special_name_is_one_the_language_s_pattern_matches_in_full[a name the pattern matches in
full]` fails (`is_special` compares an affix). The two `special` rows fail on the text (`special: must be a
non-empty string`). `test_a_special_name_that_is_no_regular_expression_says_why` fails (no problem raised). The seam
row `a literal the pattern of a special name matches in full` fails (found `[]`).

- [ ] **Step 5: `is_special` matches the pattern in full**

In `xarch/profile_values/language.py`, add `import re` after `from __future__ import annotations`, so lines 3-8 read:

```python
from __future__ import annotations

import re
from dataclasses import dataclass

from xarch.kernel.placement import Marks
from xarch.profile_values.capabilities import Supply
```

In the docstring of `CheckedLanguage`, replace `what a private name starts with, what
    a special name starts and ends with,` with `what a private name starts with, the
    pattern of a special name (special: a regular expression the whole name matches),`. Keep the docstring's lines at
120 characters or fewer; re-wrap that paragraph if a line grows past it.

Replace `is_special` (lines 61-63) with:

```python
    def is_special(self, name: str) -> bool:
        """Whether a name is one the language reserves for itself: special, a regular expression, matches the whole
        name; no name is when the language gives none."""
        return bool(self.special) and re.fullmatch(self.special, name) is not None
```

- [ ] **Step 6: The loader reads `special` as a pattern**

In `xarch/modules/spec/application/logic/language_file.py`, line 24 of the docstring, today

```
    special        what a name the language reserves for itself starts and ends with
```

becomes

```
    special        a regular expression: a name the language reserves for itself, matched against the whole name
```

Lines 102-103, today

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "special", "call", "nothing", "comment", "shebang")}
```

become

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "nothing", "comment", "shebang")}
    special = _pattern(document, "special", problems)
```

Lines 113-115 (the `CheckedLanguage(...)` call) become the keyword form:

```python
    checked = CheckedLanguage(title=title, extension=extension, package_file=package_file, interface=interface,
                              dynamic=dynamic, private=tokens["private"], special=special, call=tokens["call"],
                              nothing=tokens["nothing"], comment=tokens["comment"], directives=directives,
                              shebang=tokens["shebang"], encoding=encoding, branching=branching, supplies=supplies,
                              importing=importing, immutable=immutable, branching_expressions=expressions,
                              names=names, package=package, member=member)
```

- [ ] **Step 7: The data files write a pattern**

`xarch/architectures/presets/language/python.yaml`, line 34, today `special: __`, becomes:

```yaml
special: '(?=__)\w*(?<=__)'
```

`tests/fakes/languages/percent.yaml`: add after `member: "."` (line 11):

```yaml
special: '%\w+'
```

- [ ] **Step 8: `builders.PYTHON` by keyword, its special from the file**

In `tests/modules/rules/builders.py`, replace lines 30-37 (the `PYTHON = CheckedLanguage(...)` call, through
`member=PYTHON_FILE["member"])`) with:

```python
PYTHON = CheckedLanguage(title="Python", extension=".py", package_file="__init__.py",
                         interface=(("typing", "Protocol"), ("typing_extensions", "Protocol")),
                         dynamic=(("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
                         private="_", special=PYTHON_FILE["special"], call="__call__", nothing="None", comment="#",
                         directives=("type: ignore", "noqa", "pragma:"), shebang="#!",
                         encoding=r"coding[:=][ \t]*[-\w.]+", branching=("if", "match", "try", "for", "while"),
                         immutable=(RecordMark(("typing", "NamedTuple")),
                                    RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
                         branching_expressions=("if",), names=PYTHON_FILE["name"], package=PYTHON_FILE["package"],
                         member=PYTHON_FILE["member"])
```

The docstring under it (lines 38-39) stays.

- [ ] **Step 9: The seam guard reads the pattern of a special name**

In `tests/architecture/test_language_seam.py`, replace lines 150-161 (`TOKEN_KEYS` through the end of
`language_tokens`) with:

```python
TOKEN_KEYS = ("private", "call", "nothing", "comment", "shebang")
"""The keys of the data file whose value is a token of the language's code; `special` is the pattern of a special name,
which a literal may not match in full."""


def language_tokens(language: Path = LANGUAGE) -> tuple[set[str], re.Pattern[str], re.Pattern[str]]:
    """The tokens a literal may not be, the pattern of a special name a literal may not match in full, and the pattern
    of the directive words and of the branching keywords quoted as code."""
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    tokens = {data[key] for key in TOKEN_KEYS}
    special = re.compile(data.get("special") or "(?!)")
    directives = "|".join(sorted((re.escape(word) for word in data["directives"]), key=len, reverse=True))
    branching = "|".join(re.escape(word) for word in data["branching"])
    return tokens, special, re.compile(rf"(?<![A-Za-z0-9_])(?:{directives})(?![A-Za-z0-9_])|`(?:{branching})`")
```

In `token_leaks` (lines 164-177), the first line of its body, today
`tokens, words = language_tokens(language)`, becomes `tokens, special, words = language_tokens(language)`, and the
line, today

```python
                found += [(relative, node.lineno, node.value)] if node.value in tokens else []
```

becomes

```python
                found += [(relative, node.lineno, node.value)] if node.value in tokens or special.fullmatch(node.value) \
                    else []
```

In `ticked_pattern` (lines 184-196), the two lines, today

```python
    tokens = "|".join(re.escape(data[key]) for key in TOKEN_KEYS)
    special, importing = re.escape(data["special"]), re.escape(data["importing"].split("{")[0].strip())
```

become

```python
    tokens = "|".join(re.escape(data[key]) for key in TOKEN_KEYS)
    special, importing = data.get("special") or "(?!)", re.escape(data["importing"].split("{")[0].strip())
```

and in its `return`, the part `|{special}\w+{special}|` becomes `|(?<!\w)(?:{special})(?!\w)|`, so the return reads:

```python
    return re.compile(rf"^(?:{tokens})$|(?<!\w)(?:{words})(?!\w)|(?<!\w)(?:{special})(?!\w)"
                      rf"|^{re.escape(data['private'])}\w|^{re.escape(data['comment'])}|^{importing}(?= )")
```

Its docstring stays.

- [ ] **Step 10: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/profile_values tests/modules/spec/application/logic/test_language_file.py tests/architecture/test_language_seam.py tests/modules/rules/application/logic/test_stand_ins.py tests/modules/rules/application/logic/test_filters.py tests/modules/spec/application/logic/test_never_use.py`
Expected: all pass.

- [ ] **Step 11: Run the whole suite**

Run (background, read at the end): `timeout 1500 uv run pytest -q`
Expected: all pass. If a test reads `is_special` through a hand-built `CheckedLanguage(special="__")` and fails, give
it `special=r"(?=__)\w*(?<=__)"`. The planner found none.

- [ ] **Step 12: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/percent.yaml tests/modules/rules/builders.py \
  tests/profile_values/test_language.py tests/modules/spec/application/logic/test_language_file.py \
  tests/architecture/test_language_seam.py
git commit -m "The data file's special is a regular expression a special name matches in full, python.yaml writes '(?=__)\w*(?<=__)', which tells every name as the old affix did, and percent '%\w+'; one that is not a string or does not compile is refused; the seam guard reads the pattern"
```

---

### Task 2: The reader marks a class an interface by the `{base}` marks it is given

**Files:**
- Modify: `xarch/profile_values/language.py` (add `InterfaceMark` after `RecordMark`, line 17)
- Modify: `xarch/modules/rules/domain/parsed.py:115-133` (`Class`)
- Modify: `xarch/modules/rules/application/ports/source_tree.py:8`, `:23-28`
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:68-70` (docstring), `:121`, `:135-153`, `:202-219`,
  `:897-926`
- Modify: `tests/fakes/filesystem.py:13`, `:36-37`
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `InterfaceMark(base: tuple[str, ...] = (), keyword: str = "")` in `xarch/profile_values/language.py`, frozen.
  - `Class.interface: bool = False`, the last field of `Class`.
  - `SourceTree.read(root, paths, table=None, immutable=(), interface: tuple[InterfaceMark, ...] = ())`, the same on
    `FsSourceTree` and `FakeSourceTree`.

- [ ] **Step 1: Write the failing reader tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, line 27, today
`from xarch.profile_values.language import RecordMark`, becomes:

```python
from xarch.profile_values.language import InterfaceMark, RecordMark
```

After `test_no_class_is_an_immutable_record_when_the_reader_is_given_no_mark` (ends line 252), add:

```python
INTERFACE = (InterfaceMark(("typing", "Protocol")), InterfaceMark(("typing_extensions", "Protocol")))


@pytest.mark.parametrize("text, interface", [
    pytest.param("from typing import Protocol\nclass P(Protocol): ...\n", True, id="a base a mark names"),
    pytest.param("import typing\nclass P(typing.Protocol): ...\n", True,
                 id="the base read through the import that binds it"),
    pytest.param("import typing_extensions\nclass P(typing_extensions.Protocol): ...\n", True, id="any of the marks"),
    pytest.param("from typing import Protocol, TypeVar\nT = TypeVar('T')\nclass P(Protocol[T]): ...\n", True,
                 id="a subscripted base names what it subscripts"),
    pytest.param("from typing import Protocol as Port\nclass P(Port): ...\n", True, id="an alias reaches the path"),
    pytest.param("class P: ...\n", False, id="a class with no base"),
    pytest.param("from typing import NamedTuple\nclass P(NamedTuple): ...\n", False, id="a base no mark names"),
    pytest.param("class Protocol: ...\nclass P(Protocol): ...\n", False,
                 id="a class of the file's own named like a mark"),
])
def test_a_class_is_an_interface_when_a_base_mark_names_one_of_its_bases(tmp_path, text, interface):
    (tmp_path / "a.py").write_text(text)
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], interface=INTERFACE)[0]
    assert read.classes[-1].interface is interface


def test_no_class_is_an_interface_when_the_reader_is_given_no_mark(tmp_path):
    assert parsed(tmp_path, "from typing import Protocol\nclass P(Protocol): ...\n").classes[0].interface is False


@pytest.mark.parametrize("keyword", [pytest.param("Protocol", id="the name of a base"),
                                     pytest.param("class", id="the keyword of a class")])
def test_a_keyword_mark_marks_no_class_of_this_language(tmp_path, keyword):
    (tmp_path / "a.py").write_text("from typing import Protocol\nclass P(Protocol): ...\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], interface=(InterfaceMark(keyword=keyword),))[0]
    assert read.classes[0].interface is False
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py`
Expected: FAIL at collection with `ImportError: cannot import name 'InterfaceMark'`.

- [ ] **Step 3: `InterfaceMark`**

In `xarch/profile_values/language.py`, after the `RecordMark` class (after line 16, `keywords: ... = ()`), add:

```python


@dataclass(frozen=True)
class InterfaceMark:
    """What makes a class an interface in the language: an outside name among its bases (base, as its steps), or a
    keyword it is declared with or carries (keyword); exactly one of the two is given."""
    base: tuple[str, ...] = ()
    keyword: str = ""
```

(two blank lines before `@dataclass`, as between the other classes).

- [ ] **Step 4: `Class.interface`**

In `xarch/modules/rules/domain/parsed.py`, the end of `Class`'s docstring (lines 122-123), today

```
    as written (a string annotation by its text); immutable: it is an immutable record, as the reader was told one is
    marked (see RecordMark)."""
```

becomes

```
    as written (a string annotation by its text); immutable: it is an immutable record, as the reader was told one is
    marked (see RecordMark); interface: it is an interface, as the reader was told one is marked (see
    InterfaceMark)."""
```

and after `immutable: bool = False` (line 133) add:

```python
    interface: bool = False
```

- [ ] **Step 5: The port takes the marks**

In `xarch/modules/rules/application/ports/source_tree.py`, line 8 becomes
`from xarch.profile_values.language import InterfaceMark, RecordMark`, and `read` (lines 23-28) becomes:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = ()) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so."""
        ...
```

In `tests/fakes/filesystem.py`, line 13 becomes `from xarch.profile_values.language import InterfaceMark, RecordMark`,
and the signature of `read` (lines 36-37) becomes:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = ()) -> list[SourceFile]:
```

Its body stays: the fake builds classes from what the test hands it.

- [ ] **Step 6: The reader sets it**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

Line 121 becomes `from xarch.profile_values.language import InterfaceMark, RecordMark`.

In the module docstring, after the paragraph that ends `a mark written with keywords names no base.` (line 70), add
a blank line and this paragraph:

```
A class is an interface when a mark it is given (the language's data file's `interface`) is a base mark whose path is
one of its bases, read as for an immutable record (a subscripted base, `Protocol[T]`, by what it subscripts; an alias
by the path it reaches). A keyword mark marks no class: Python declares no class with a keyword.
```

`FsSourceTree.read` (lines 135-136) takes the marks and hands them on. Its signature becomes:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = ()) -> list[SourceFile]:
```

and line 153 becomes:

```python
            found.append(_parsed(name, path, text, table, immutable, interface,
                                 _Where((root.name, *path[:-1]), root, self._fs)))
```

`_parsed` (lines 202-203) becomes:

```python
def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None,
            marks: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (),
            where: _Where | None = None) -> SourceFile:
```

and in its `return` the part `classes=tuple(_classes(tree, marks, where))` becomes
`classes=tuple(_classes(tree, marks, interface, where))`. The call `_parsed("", (), text, None)` (line 163) stays.

`_classes` (line 897) becomes:

```python
def _classes(tree: ast.Module, marks: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (),
             where: _Where | None = None) -> list[Class]:
```

and its `Class(...)` call (lines 911-914) ends with the new value:

```python
            found.append(Class(node.lineno, node.name, bases, methods, _attributes(node), _named(node) - {node.name},
                               exception, tuple(child.target.id for child in declared),
                               tuple(_annotation(child.annotation) or "" for child in declared),
                               _immutable(node, bases, scope, marks), _interface(bases, interface)))
```

After `_immutable` (ends line 926), add:

```python


def _interface(bases: tuple[Ref, ...], marks: tuple[InterfaceMark, ...]) -> bool:
    """Whether a base mark names one of the class's bases; a keyword mark names none, since Python declares no class
    with a keyword."""
    return any(mark.base and mark.base in bases for mark in marks)
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `timeout 600 uv run pytest -q tests/modules/rules tests/architecture/test_language_seam.py`
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/rules/domain/parsed.py \
  xarch/modules/rules/application/ports/source_tree.py xarch/modules/rules/adapters/fs_source_tree.py \
  tests/fakes/filesystem.py tests/modules/rules/adapters/test_fs_source_tree.py
git commit -m "A class says whether it is an interface: the reader is handed the language's interface marks and marks a class one when a base mark's path is among its bases, read as for an immutable record; a keyword mark marks no Python class"
```

---

### Task 3: The data file's `interface` is a list of marks, and the checks read the reader's mark

**Files:**
- Modify: `xarch/profile_values/language.py` (`CheckedLanguage.interface` type and docstring)
- Modify: `xarch/modules/spec/application/logic/language_file.py:8` (docstring), `:57`, `:98`, add `_interface`
- Modify: `xarch/architectures/presets/language/python.yaml:25`
- Modify: `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml:12`
- Modify: `xarch/modules/spec/domain/values.py:327-330` (`interface_name`)
- Modify: `xarch/modules/spec/application/logic/explain.py:28-37` (`words`)
- Modify: `xarch/modules/rules/application/services/source_check.py:75-79`, `holding.py:37`
- Modify: `xarch/modules/rules/application/logic/stand_ins.py:4-14` (docstring), `:115`
- Modify: `xarch/modules/rules/application/logic/facts.py:52-53` (docstring), `:172`
- Modify: `xarch/modules/rules/application/logic/twins.py:130`
- Modify: `tests/modules/rules/builders.py` (`PYTHON`'s interface)
- Modify: `tests/architecture/test_language_seam.py:135-147`, `:255-262`
- Test: `tests/modules/spec/application/logic/test_language_file.py`, `tests/modules/spec/application/test_language.py`,
  `tests/modules/spec/application/logic/test_profile_keys.py`, `tests/modules/rules/application/logic/test_stand_ins.py`,
  `test_dead_code.py`, `test_twins.py`, `world.py`, `test_filters.py`

**Interfaces:**
- Consumes: `InterfaceMark`, `Class.interface`, `SourceTree.read(..., interface=...)` (Task 2).
- Produces:
  - `CheckedLanguage.interface: tuple[InterfaceMark, ...] = ()`.
  - The loader's refusal `interface: each mark is {base: <outside name>} or {keyword: <word>}`, said once.
  - `Language.interface_name`: the last step of the first mark's base, else its keyword, `""` with none.
  - `explain.words(language)["interface_path"]`: the first mark's base as an outside name, else its keyword.
  - `builders.marks_of(file: dict) -> tuple[InterfaceMark, ...]`, the marks a data file's yaml writes.

- [ ] **Step 1: Write the failing loader tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Line 11 becomes `from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark`.

In `DOCUMENT` (line 15), `"interface": ["sys.Contract"]` becomes `"interface": [{"base": "sys.Contract"}]`. In
`PERCENT` (line 22), `"interface": ["%RegisteredObject"]` becomes `"interface": [{"base": "%RegisteredObject"}]`.

Add after `"""The lists of a language whose names may start with a percent, under its own patterns."""` (line 24):

```python
INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"
```

In `test_a_language_is_read_from_the_document_of_its_preset_by_name` (line 29), `(("sys", "Contract"),)` becomes
`(InterfaceMark(("sys", "Contract")),)`.

In `test_every_problem_of_a_document_is_listed_naming_the_preset` (line 53), the expected line
`"interface: must be a list of outside names, such as [<package>.<name>]",` becomes `INTERFACE,`.

In `test_the_lists_of_a_language_are_read_by_its_own_patterns` (line 165), `(("%RegisteredObject",),)` becomes
`(InterfaceMark(("%RegisteredObject",)),)`.

In `test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them` (line 175), the expected line
`"interface: '%RegisteredObject' is not an outside name such as <package>.<name>",` becomes `INTERFACE,`.

`test_a_document_that_gives_none_of_name_package_and_member_reads_an_outside_name_as_its_whole_text` (line 184)
becomes:

```python
def test_a_document_that_gives_none_of_name_package_and_member_reads_an_outside_name_as_its_whole_text():
    assert language_of("pascal", UNJOINED).checked.interface == (InterfaceMark(("sys.Contract",)),)
```

`test_the_percent_test_only_language_reads_its_lists_by_its_own_patterns` (lines 199-203) becomes:

```python
def test_the_percent_test_only_language_reads_its_lists_by_its_own_patterns():
    path = next(path for path in TEST_LANGUAGES if path.stem == "percent")
    checked = language_of("percent", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert (checked.interface, checked.dynamic, checked.immutable) == (
        (InterfaceMark(keyword="Abstract"),), (("%SYSTEM", "OBJ", "Load"),), (RecordMark(("%SerialObject",)),))


def test_the_brace_test_only_language_marks_an_interface_by_its_keyword():
    path = next(path for path in TEST_LANGUAGES if path.stem == "brace")
    checked = language_of("brace", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.interface == (InterfaceMark(keyword="interface"),)
```

Append at the end of the file:

```python
def test_what_makes_a_class_an_interface_is_read_as_marks_in_the_order_written():
    marks = [{"keyword": "interface"}, {"base": "sys.Contract"}, {"base": "sys"}]
    assert language_of("pascal", DOCUMENT | {"interface": marks}).checked.interface == (
        InterfaceMark(keyword="interface"), InterfaceMark(("sys", "Contract")), InterfaceMark(("sys",)))


def test_a_language_that_marks_no_interface_has_none():
    left_out = {key: value for key, value in DOCUMENT.items() if key != "interface"}
    assert (language_of("pascal", DOCUMENT | {"interface": []}).checked.interface,
            language_of("pascal", left_out).checked.interface) == ((), ())


@pytest.mark.parametrize("interface", [
    pytest.param("sys.Contract", id="no list"),
    pytest.param(["sys.Contract"], id="the old shape, a list of outside names"),
    pytest.param([{"base": "sys.Contract", "keyword": "interface"}], id="a mark of two keys"),
    pytest.param([{"kind": "sys.Contract"}], id="a key that is neither"),
    pytest.param([{"base": "not a name!"}], id="a base that is no outside name"),
    pytest.param([{"base": 3}], id="a base that is no text"),
    pytest.param([{"keyword": "two words"}], id="a keyword with a space"),
    pytest.param([{"keyword": "2x"}], id="a keyword that is no name of the language"),
    pytest.param([{"keyword": ""}], id="an empty keyword"),
    pytest.param([{"base": "sys.Contract"}, "sys.Other", {"kind": "x"}], id="said once however many marks are wrong"),
])
def test_a_mark_of_an_interface_that_is_neither_a_base_nor_a_keyword_is_refused_once(interface):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"interface": interface})
    assert caught.value.problems == (f"presets/language/odd.yaml: {INTERFACE}",)


def test_the_marks_of_an_interface_are_not_read_when_the_keys_that_say_how_a_name_is_written_are_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | {"package": "[a-", "interface": ["sys.Contract"]})
    assert [p.removeprefix("presets/language/odd.yaml: ").split(":")[0] for p in caught.value.problems] == ["package"]
```

- [ ] **Step 2: Update the controller's language tests**

In `tests/modules/spec/application/test_language.py`:

Line 13 becomes `from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark`.

Line 16, in `PASCAL`, `"interface": ["sys.Contract"]` becomes `"interface": [{"base": "sys.Contract"}]`. Line 18, in
`PYTHON`, `"interface": ["typing.Protocol"]` becomes `"interface": [{"base": "typing.Protocol"}]`.

Line 32: `(("sys", "Contract"),)` becomes `(InterfaceMark(("sys", "Contract")),)`. Lines 37 and 53:
`(("typing", "Protocol"),)` becomes `(InterfaceMark(("typing", "Protocol")),)`. Keep each line at 120 characters or
fewer (wrap the call's arguments onto the next line where needed).

Line 89, `(("typing", "Protocol"), ("typing_extensions", "Protocol")),` becomes:

```python
        r"(?!\d)\w+", ".", (InterfaceMark(("typing", "Protocol")), InterfaceMark(("typing_extensions", "Protocol"))),
```

- [ ] **Step 3: Write the failing word tests**

In `tests/modules/spec/application/logic/test_profile_keys.py`, line 11 becomes
`from tests.modules.spec.languages import BRACE, PERCENT, PYTHON`, and add after the import of `Language` (line 28):

```python
from xarch.profile_values.language import InterfaceMark
```

(keep the imports sorted the way `ruff check` wants; run it in Step 15).

`test_the_path_of_an_interface_is_said_with_the_member_of_the_language` (lines 185-187) becomes:

```python
def test_the_path_of_an_interface_is_said_with_the_member_of_the_language():
    based = (InterfaceMark(("%Library", "RegisteredObject")),)
    hashed = replace(PERCENT, checked=replace(PERCENT.checked, member="#", interface=based))
    assert said("`%interface_path%`", hashed) == "`%Library#RegisteredObject`"


def test_an_interface_is_called_by_the_last_step_of_its_first_base_or_by_its_keyword():
    assert (PYTHON.interface_name, BRACE.interface_name, PERCENT.interface_name, Language().interface_name) == (
        "Protocol", "interface", "Abstract", "")


def test_the_path_of_an_interface_is_its_first_base_or_its_keyword():
    assert [said("`%interface_path%`", language) for language in (PYTHON, BRACE, PERCENT, Language())] == [
        "`typing.Protocol`", "`interface`", "`Abstract`", "``"]
```

- [ ] **Step 4: Hand-built ports set `interface=True`, and the checks' new cases**

In `tests/modules/rules/application/logic/test_stand_ins.py`:

Lines 17-18 become:

```python
READ = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "str | None"), Method(5, "save", "None")), interface=True)
FIRE = Class(8, "Notifier", (PROTOCOL,), (Method(9, "send", "None"),), interface=True)
```

The parametrize list of `test_ports` (lines 32-59) becomes:

```python
@pytest.mark.parametrize("classes, expected", [
    pytest.param([READ, FIRE], [], id="a read port with its fake and a fire-only port pass"),
    pytest.param([Class(3, "Repo", (), (Method(4, "get", "int"),), interface=True)], [],
                 id="a class the reader marks is a port, whatever its bases"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "int"),), interface=True)],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="a read port with no fake is reported at the port"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "None"), Method(5, "put", "None")), interface=True)],
                 [], id="a fire-only port needs no fake"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "int"),), interface=True),
                  Class(6, "Other", (PROTOCOL,), (Method(7, "get", "None"),), interface=True)],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="only the read ports of a file need fakes"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", None), Method(5, "put", "int")), interface=True)],
                 [f"app/{PORT_FILE}:4: Store.get has no return annotation, and whether Store is fire-only or read "
                  "follows from it (stand-ins)"],
                 id="a method with no return annotation is reported, and the port then has no kind"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "__init__", None), Method(5, "send", "None")),
                        interface=True)], [],
                 id="a dunder method is not one of the port's methods"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "__call__", "int"),), interface=True)],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="__call__ is the method a callable port is"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (), interface=True)], [], id="a port with no methods is neither kind"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "int"),))], [],
                 id="a class with a Protocol base the reader does not mark is no port"),
    pytest.param([Class(3, "Store", (("app", "Base"),), (Method(4, "get", "int"),))], [],
                 id="a class that is not a Protocol is not a port"),
    pytest.param([Class(3, "Store", (None,), (Method(4, "get", "int"),))], [],
                 id="a class whose base is not a name an import binds is not a port"),
])
```

Lines 65, 85 and 95 each read `... = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),))`. In each, the call
gains `, interface=True` before its last `)`:

```python
    store = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),), interface=True)
```

```python
    bare = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),), interface=True)
```

(line 85 and line 95 both become the `bare = ...` line above).

Lines 258-259 become:

```python
OTHER_REPO = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "int"), Method(5, "list", "int"),
                                            Method(6, "drop", "None")), interface=True)
```

Line 278 becomes:

```python
    pytest.param([ported(Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),), interface=True))], [FAKE],
```

Then confirm nothing was missed: `grep -n "(PROTOCOL,)" tests/modules/rules/application/logic/test_stand_ins.py`
lists only lines that also hold `interface=True`, and the one row with id
`a class with a Protocol base the reader does not mark is no port`.

In `tests/modules/rules/application/logic/test_dead_code.py`, lines 12-13 become:

```python
REPO = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "int"),), interface=True)
NOTIFIER = Class(8, "Notifier", (PROTOCOL,), (Method(9, "send", "None"),), interface=True)
```

In `tests/modules/rules/application/logic/test_twins.py`, lines 41-42, today

```python
    pytest.param(Class(5, "A", (("typing", "Protocol"),), fields=FIELDS), Class(9, "B", fields=FIELDS), False,
                 id="an interface, whose fields are a requirement"),
```

become

```python
    pytest.param(Class(5, "A", fields=FIELDS, interface=True), Class(9, "B", fields=FIELDS), False,
                 id="an interface, whose fields are a requirement"),
    pytest.param(Class(5, "A", (("typing", "Protocol"),), fields=FIELDS), Class(9, "B", fields=FIELDS), True,
                 id="a class with a Protocol base the reader does not mark is no interface"),
```

In `tests/modules/rules/application/logic/world.py`, line 65 becomes:

```python
           classes=(Class(2, "Repo", bases=(("typing", "Protocol"),), interface=True),)),
```

In `tests/modules/rules/application/logic/test_filters.py`, add to the imports from `world` (lines 6-25) the name
`RULE` (in its sorted place, after `RESERVED`), and add after them:

```python
from tests.modules.rules.builders import source
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.parsed import Class
from xarch.modules.rules.domain.rule import Found
```

(sorted with the file's other imports as `ruff check` wants). Append at the end of the file:

```python
def test_the_interface_filter_holds_of_the_classes_the_reader_marks_whatever_their_bases():
    ports = source("modules/docs/application/ports/store.py",
                   classes=(Class(2, "Store", interface=True), Class(4, "Based", (("typing", "Protocol"),))))
    built = facts_of([ports], [], PROFILE, "app", "tests")
    read = built.files[0]
    assert [fact.line for fact in read.facts["class"]
            if question(condition("interface"))(Found(RULE, read, fact, None), built, PROFILE)] == [2]
```

- [ ] **Step 5: The seam guard's words of a test-only language, written out**

In `tests/architecture/test_language_seam.py`, `test_the_guard_reads_the_words_of_a_test_only_language` (lines
255-262) becomes:

```python
@pytest.mark.parametrize("stem, expected", [
    pytest.param("brace", {"Brace", "globalThis", "node:module", "createRequire", "interface"}, id="brace"),
    pytest.param("percent", {"Percent", "%SYSTEM", "OBJ", "Load", "Abstract"}, id="percent"),
])
def test_the_guard_reads_the_words_of_a_test_only_language(stem, expected):
    pattern, _ = language_words(next(path for path in TEST_LANGUAGES if path.stem == stem))
    assert {match[0] for match in pattern.finditer(" ".join(sorted(expected)))} == expected
```

- [ ] **Step 6: Run the tests to verify they fail**

Run: `timeout 900 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py tests/modules/spec/application/logic/test_profile_keys.py tests/modules/rules/application/logic/test_stand_ins.py tests/modules/rules/application/logic/test_twins.py tests/modules/rules/application/logic/test_filters.py tests/architecture/test_language_seam.py`
Expected: FAIL. The loader refuses `{"base": ...}` (`interface: '{'base': ...}' is not an outside name ...`), so
most loader and controller tests fail. `interface_name` raises on the mark. The stand-ins row
`a class the reader marks is a port, whatever its bases` fails. So do the twins row
`an interface, whose fields are a requirement` and the filter test (found `[4]`). The `percent` seam row fails: no
`Abstract`.

- [ ] **Step 7: `CheckedLanguage.interface` holds marks**

In `xarch/profile_values/language.py`, `CheckedLanguage.interface` (line 38), today
`interface: tuple[tuple[str, ...], ...] = ()`, becomes:

```python
    interface: tuple[InterfaceMark, ...] = ()
```

`InterfaceMark` is already defined above `CheckedLanguage` (Task 2 put it after `RecordMark`). In the docstring of `CheckedLanguage`, replace `the dotted names that mark a class as an interface, and
those of what imports` with `the marks that make a class an interface (interface: an outside name among its bases, or
a keyword it is declared with or carries), the dotted names of what imports`. Re-wrap to 120 characters.

- [ ] **Step 8: The loader reads the marks**

In `xarch/modules/spec/application/logic/language_file.py`:

Line 8 of the docstring, today

```
    interface      outside names (see below), any of which among a class's bases marks it as an interface
```

becomes

```
    interface      the marks of an interface, each {base: <outside name>}, an outside name (see below) among a
                   declaration's bases, or {keyword: <word>}, a keyword it is declared with or carries, a name
```

Line 57 becomes `from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark`.

After `_VALUE = re.compile(r"[^,()=]+")` (line 73), add:

```python
INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"
"""What the loader says of a value of `interface` that is not a list of marks, once for the key."""
```

Line 98, today `interface = _outside(document, "interface", problems, joins, namespace)`, becomes:

```python
    interface = _interface(document, problems, joins, namespace)
```

After `_outside` (ends line 151), add:

```python


def _interface(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
               namespace: str) -> tuple[InterfaceMark, ...]:
    """The marks of an interface, in the order written; one problem for the key when it is no list or any item is
    no mark; none read when the keys that say how an outside name is written are refused already (joins None)."""
    if "interface" not in document or joins is None:
        return ()
    value = document["interface"]
    items = value if isinstance(value, list) else None
    found = tuple(mark for mark in (_interface_mark(item, joins, namespace) for item in items or ()) if mark is not None)
    if items is None or len(found) != len(items):
        problems.append(INTERFACE)
        return ()
    return found


def _interface_mark(item: Any, joins: tuple[str, str, str], namespace: str) -> InterfaceMark | None:
    """One mark: a map of one key, `base` with an outside name or `keyword` with a name of the language holding no
    space; None when the item is neither."""
    if not (isinstance(item, Mapping) and len(item) == 1):
        return None
    ((key, value),) = item.items()
    if not isinstance(value, str):
        return None
    names, package, member = joins
    if key == "base":
        path = outside_name(value, names, package, member, namespace)
        return InterfaceMark(path) if path is not None else None
    if key == "keyword" and _MEMBER.fullmatch(value) and is_name(value, names):
        return InterfaceMark(keyword=value)
    return None
```

`_MEMBER` (`\S+`) is the existing pattern of a non-empty text with no space.

- [ ] **Step 9: The data files write marks**

`xarch/architectures/presets/language/python.yaml`, line 25, today
`interface: [typing.Protocol, typing_extensions.Protocol]`, becomes:

```yaml
interface: [{base: typing.Protocol}, {base: typing_extensions.Protocol}]
```

`tests/fakes/languages/brace.yaml`: add after `member: "#"` (line 12):

```yaml
interface: [{keyword: interface}]
```

`tests/fakes/languages/percent.yaml`, line 12, today `interface: ["%Library.RegisteredObject"]`, becomes:

```yaml
interface: [{keyword: Abstract}]
```

- [ ] **Step 10: The words of an interface read the first mark**

In `xarch/modules/spec/domain/values.py`, `interface_name` (lines 327-330) becomes:

```python
    @property
    def interface_name(self) -> str:
        """What an interface is called in the language: the last step of the first mark's base, or its keyword; ""
        when nothing marks one."""
        if not self.checked.interface:
            return ""
        first = self.checked.interface[0]
        return first.base[-1] if first.base else first.keyword
```

In `xarch/modules/spec/application/logic/explain.py`, `words` (lines 26-37) becomes:

```python
def words(language: Language) -> dict[str, str]:
    """What the language says for each `%word%` a text of the format may write: the title, the extension, the package
    file, the name of an interface and its path (the first mark's base as an outside name, or its keyword), the
    namespace of the names bound without an import, the marker of a line comment and the comments its tools read,
    each quoted after the marker, and the prefix of a private name."""
    checked = language.checked
    first = checked.interface[0] if checked.interface else None
    path = "" if first is None else outside_text(first.base, checked.member) if first.base else first.keyword
    return {"language": checked.title, "extension": checked.extension, "package_file": checked.package_file,
            "private": checked.private, "interface": language.interface_name, "interface_path": path,
            "namespace": language.namespace, "comment": checked.comment,
            "directives": ", ".join(f"`{checked.comment} {word}`" for word in checked.directives)}
```

- [ ] **Step 11: `builders.PYTHON` takes its marks from its file**

In `tests/modules/rules/builders.py`:

Add `from xarch.kernel.logic.names import outside_steps` to the imports (after
`from xarch.kernel.placement import EVERYTHING`), and line 23 becomes
`from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark`.

Before `PYTHON_FILE = ...` (line 28), add:

```python
def marks_of(file: dict) -> tuple[InterfaceMark, ...]:
    """The interface marks a language's data file writes, as its loader reads them: a base split at the file's member,
    a keyword whole."""
    return tuple(InterfaceMark(outside_steps(mark["base"], file["member"])) if "base" in mark
                 else InterfaceMark(keyword=mark["keyword"]) for mark in file.get("interface", ()))


```

In `PYTHON`, the line `interface=(("typing", "Protocol"), ("typing_extensions", "Protocol")),` becomes
`interface=marks_of(PYTHON_FILE),`. `PYTHON_FILE` must be defined above `PYTHON`, as it is.

- [ ] **Step 12: The callers hand the reader the language's marks**

In `xarch/modules/rules/application/services/source_check.py`, lines 75-79, today

```python
        marks = rules.language.immutable
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table, marks) \
            if tests is not None else []
```

become

```python
        marks, interface = rules.language.immutable, rules.language.interface
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table, marks, interface) \
            if tests is not None else []
```

In `xarch/modules/rules/application/services/holding.py`, line 37 becomes:

```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface))
```

- [ ] **Step 13: The checks read the reader's mark**

`xarch/modules/rules/application/logic/stand_ins.py`, line 115, today
`            if any(base in profile.language.interface for base in cls.bases):`, becomes:

```python
            if cls.interface:
```

and in its module docstring, lines 4-5, today

```
A port is a module-level class, in a file of a part the fakes stand in for, with one of the language's interface
names (its data file's `interface`, generic forms too) among its bases; any other class there is not a port. Its
```

become

```
A port is a module-level class, in a file of a part the fakes stand in for, that the reader marks as an interface (by
the marks of its data file's `interface`); any other class there is not a port. Its
```

(re-wrap that paragraph to 120 characters).

`xarch/modules/rules/application/logic/facts.py`, line 172 becomes:

```python
            ports = {c.name: c for c in file.classes if c.interface}
```

and its docstring lines 52-53, today

```
    interface           a class with one of the names the language's data file marks interfaces with among its bases,
                        the last of its name in its file
```

become

```
    interface           a class the reader says is an interface, by the marks of the language's data file, the last
                        of its name in its file
```

`xarch/modules/rules/application/logic/twins.py`, line 130, today
`                  and not any(base in profile.language.interface for base in cls.bases)]`, becomes:

```python
                  and not cls.interface]
```

- [ ] **Step 14: The seam guard reads the map marks**

In `tests/architecture/test_language_seam.py`, `language_words` (lines 135-147): its first two lines after the
docstring, today

```python
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    steps = {step for name in (*data.get("interface", ()), *data.get("dynamic", ()))
             for step in outside_steps(name, data.get("member", ""))}
```

become

```python
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    marks = data.get("interface", ())
    named = (*(mark["base"] for mark in marks if "base" in mark), *data.get("dynamic", ()))
    steps = {step for name in named for step in outside_steps(name, data.get("member", ""))} | {
        mark["keyword"] for mark in marks if "keyword" in mark}
```

Its docstring becomes `"""The pattern of the words the data file gives, as literal text (each step of an interface
mark's base and of a dynamic name, and each keyword of a mark), and the lowercase words of an identifier."""` (wrapped
to 120). In the module docstring (line 16), `every step of the names that mark an interface and of those that import by
a computed name` becomes `every step of the bases and every keyword that mark an interface and of the names that import
by a computed name`. Re-wrap that paragraph to 120 characters.

- [ ] **Step 15: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/modules/rules tests/architecture tests/profile_values`
Expected: all pass. Then `uv run ruff check` gives no problem.

- [ ] **Step 16: Run the whole suite**

Run (background, read at the end): `timeout 1500 uv run pytest -q`
Expected: all pass, the bootstrap tests included. `tests/bootstrap/test_source_checks.py` (`Repo is a read port with
no fake`, `Notifier is a port that nothing else in the app names`) proves the callers hand the marks to the real
reader.

- [ ] **Step 17: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml \
  xarch/modules/spec/domain/values.py xarch/modules/spec/application/logic/explain.py \
  xarch/modules/rules/application/services/source_check.py xarch/modules/rules/application/services/holding.py \
  xarch/modules/rules/application/logic/stand_ins.py xarch/modules/rules/application/logic/facts.py \
  xarch/modules/rules/application/logic/twins.py tests/modules/rules/builders.py \
  tests/architecture/test_language_seam.py tests/modules/spec/application/logic/test_language_file.py \
  tests/modules/spec/application/test_language.py tests/modules/spec/application/logic/test_profile_keys.py \
  tests/modules/rules/application/logic/test_stand_ins.py tests/modules/rules/application/logic/test_dead_code.py \
  tests/modules/rules/application/logic/test_twins.py tests/modules/rules/application/logic/world.py \
  tests/modules/rules/application/logic/test_filters.py
git commit -m "The data file's interface is a list of marks, {base: <outside name>} or {keyword: <word>}, refused once for the key otherwise; python.yaml writes its two Protocol bases as marks, brace {keyword: interface}, percent {keyword: Abstract}; the source check hands the reader the marks, and the stand-ins, the class kind's interface trait and no-twins read the reader's mark instead of comparing bases"
```

---

### Task 4: The fact `class.interface`, and the keys that read ports need it

**Files:**
- Modify: `xarch/profile_values/capabilities.py:41`
- Modify: `xarch/architectures/presets/language/python.yaml:66`
- Modify: `xarch/modules/spec/domain/key_table.py:194-235` (`NEEDS`)
- Modify: `xarch/modules/rules/domain/vocabulary.py:225-228` (class kind's `field_needs`), `:280-281` (filter text)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`, `tests/modules/rules/domain/test_vocabulary.py`

**Interfaces:**
- Consumes: the reader's mark (Tasks 2-3).
- Produces: `FACTS["class.interface"]`. `NEEDS["guards.stand-ins"]`, `NEEDS["guards.dead-code"]` and the new
  `NEEDS["fakes"]` hold it. The class kind's `field_needs["interface"] == ("class.interface",)`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/spec/application/logic/test_profile_needs.py`:

```python
def test_whether_a_class_is_an_interface_is_a_fact_the_marks_of_the_data_file_say():
    assert FACTS["class.interface"] == "whether a class is an interface, by the marks of the language's data file"


@pytest.mark.parametrize("address", ["guards.stand-ins", "guards.dead-code", "fakes"])
def test_a_key_that_reads_ports_needs_the_reader_to_mark_interfaces(address):
    assert "class.interface" in {key.address: key.needs for key in KEYS}[address]


def test_fakes_are_refused_in_a_language_whose_reader_marks_no_interface():
    document = services()
    document["fakes"] = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}
    assert refusal("fakes", "class.interface") in problems(document, languages=LANGUAGES)
```

Append to `tests/modules/rules/domain/test_vocabulary.py`:

```python
def test_the_interface_of_a_class_needs_the_reader_to_mark_interfaces_and_says_no_word_of_bases():
    kind = next(kind for kind in KINDS if kind.name == "class")
    interface = next(word for word in FILTERS if word.name == "interface")
    assert (kind.field_needs["interface"], interface.meaning) == (
        ("class.interface",), "the class is an interface: the language marks it as one")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/modules/rules/domain/test_vocabulary.py`
Expected: FAIL with `KeyError: 'class.interface'` (FACTS, NEEDS check, field_needs), and the refusal is not in the
problems.

- [ ] **Step 3: The fact, its supply, and who needs it**

`xarch/profile_values/capabilities.py`, after line 41 (`"class.immutable": ...`), add:

```python
    "class.interface": "whether a class is an interface, by the marks of the language's data file",
```

`xarch/architectures/presets/language/python.yaml`, after line 66 (`  class.immutable: exact`), add:

```yaml
  class.interface: exact
```

`xarch/modules/spec/domain/key_table.py`, in `NEEDS`:

- before `"parts.<part>.may_import": _IMPORTS,` (the first entry), add `    "fakes": ("class", "class.interface"),`
- `"guards.stand-ins"` (lines 222-223) becomes:

```python
    "guards.stand-ins": ("class", "class.methods", "class.attributes", "class.interface", "call", "parameter_call",
                         "import.resolved"),
```

- `"guards.dead-code": ("class", "named"),` (line 230) becomes `"guards.dead-code": ("class", "class.interface",
  "named"),` (spec deviation 1).

`xarch/modules/rules/domain/vocabulary.py`, the class kind's `field_needs` (lines 226-228), today

```python
         needs=("class",), field_needs={"mentions": ("class.named",), "exception": _CLASS_EXCEPTION,
                                        "record": ("class.methods", "function.returns"),
                                        "immutable": ("class.immutable",)}),
```

becomes

```python
         needs=("class",), field_needs={"mentions": ("class.named",), "exception": _CLASS_EXCEPTION,
                                        "record": ("class.methods", "function.returns"),
                                        "interface": ("class.interface",), "immutable": ("class.immutable",)}),
```

and the filter `interface` (lines 280-281), today

```python
    Filter("interface", "the class is an interface: one of its bases is a name the language marks interfaces with",
           FACT, ("interface",)),
```

becomes

```python
    Filter("interface", "the class is an interface: the language marks it as one", FACT, ("interface",)),
```

`vocabulary.py:178` (`"interface": "whether a class is an interface",`) stays.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/modules/rules/domain tests/bootstrap/test_needs_agree.py tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py`
Expected: all pass. `test_needs_agree` passes because `guards.dead-code` now lists `class.interface`.

- [ ] **Step 5: Run the whole suite**

Run (background, read at the end): `timeout 1500 uv run pytest -q`
Expected: all pass (`test_python_supplies_every_fact_a_bundled_check_reads` included).

- [ ] **Step 6: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml \
  xarch/modules/spec/domain/key_table.py xarch/modules/rules/domain/vocabulary.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/modules/rules/domain/test_vocabulary.py
git commit -m "A new fact class.interface, whether a class is an interface by the marks of the data file, which python supplies exact; fakes, guards.stand-ins and guards.dead-code need it, as the class kind's interface field does, and the interface filter says the language marks it, with no word of bases"
```

---

### Task 5: `nothing` is a list, `unannotated: nothing` is a choice, and a port's kind follows them

**Files:**
- Modify: `xarch/profile_values/language.py` (`nothing` type, new `unannotated`, `NOTHING`, `gives_nothing`, docstring)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring `:26`, `KEYS`, the tokens loop, new
  `_annotations`, `unannotated`, the `CheckedLanguage(...)` call)
- Modify: `xarch/architectures/presets/language/python.yaml:36`
- Modify: `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml`
- Modify: `xarch/modules/rules/application/logic/stand_ins.py:8-14` (docstring), `:122-134` (`_classified`)
- Modify: `xarch/modules/spec/application/logic/docs_template.py:619-625` (`_stand_ins_line`)
- Modify: `xarch/modules/spec/application/logic/explain.py` (`words`: the word `nothing`)
- Modify: `xarch/architectures/presets/format/keys.yaml:831`
- Modify: `tests/modules/rules/builders.py` (`PYTHON`'s nothing, `BRACE`, new `PERCENT`)
- Modify: `tests/architecture/test_language_seam.py` (`TOKEN_KEYS`, `language_tokens`, `ticked_pattern`)
- Test: `tests/profile_values/test_language.py`, `tests/modules/spec/application/logic/test_language_file.py`,
  `tests/modules/rules/application/logic/test_stand_ins.py`, `tests/modules/spec/application/logic/test_testing.py`,
  `tests/modules/spec/application/logic/test_profile_keys.py`,
  `tests/modules/spec/application/logic/test_key_catalogue.py:12-13`, `tests/architecture/test_language_seam.py`

**Interfaces:**
- Consumes: `CheckedLanguage.interface` marks and `Class.interface` (Tasks 2-3).
- Produces:
  - `NOTHING = "nothing"` in `xarch/profile_values/language.py`, the one value of `unannotated`.
  - `CheckedLanguage.nothing: tuple[str, ...] = ()`, and `unannotated: str = ""` as the last field.
  - `CheckedLanguage.gives_nothing(returns: str | None) -> bool`.
  - `explain.words(language)["nothing"]`: `" or ".join(checked.nothing)`.
  - `builders.BRACE` with `interface` and `nothing` from `brace.yaml`; `builders.PERCENT` with `interface`,
    `special` and `unannotated` from `percent.yaml`.

- [ ] **Step 1: Write the failing value and loader tests**

In `tests/profile_values/test_language.py`, the import line becomes
`from xarch.profile_values.language import NOTHING, CheckedLanguage`, and append:

```python
@pytest.mark.parametrize("language, returns, nothing", [
    pytest.param(CheckedLanguage(nothing=("None",)), "None", True, id="an annotation nothing lists"),
    pytest.param(CheckedLanguage(nothing=("void", "Promise<void>")), "Promise<void>", True, id="any one it lists"),
    pytest.param(CheckedLanguage(nothing=("void",)), "Promise<Order>", False, id="another annotation gives a value"),
    pytest.param(CheckedLanguage(nothing=("None",)), None, False, id="no annotation, and unannotated not said"),
    pytest.param(CheckedLanguage(unannotated=NOTHING), None, True, id="no annotation, and unannotated says nothing"),
    pytest.param(CheckedLanguage(unannotated=NOTHING), "Order", False, id="an annotation still gives a value"),
    pytest.param(CheckedLanguage(), "None", False, id="a language that lists nothing has no annotation of no value"),
])
def test_a_method_gives_no_value_by_the_annotations_the_language_lists_or_its_word_on_none(language, returns, nothing):
    assert language.gives_nothing(returns) is nothing
```

In `tests/modules/spec/application/logic/test_language_file.py`:

- in `test_every_problem_of_a_document_is_listed_naming_the_preset`, the expected unknown-key text (lines 46-48)
  becomes:

```python
        "unknown key 'extra': use branching, branching_expressions, cache, call, comment, directives, dynamic, encoding, extension, "
        "immutable, importing, interface, member, name, namespace, nothing, package, package_file, private, shebang, special, "
        "standard, supplies, title, unannotated",
```

- in `test_the_tokens_of_the_code_are_read_when_the_document_gives_them`, `"nothing": "None"` becomes
  `"nothing": ["None"]`, and in the expected tuple the item `"None"` (after `"__call__"`) becomes `("None",)`.
- append:

```python
def test_the_annotations_of_no_value_and_the_word_on_none_are_read_when_the_document_gives_them():
    checked = language_of("pascal", DOCUMENT | {"nothing": ["void", "Promise<void>"], "unannotated": "nothing"}).checked
    left_out = language_of("pascal", DOCUMENT).checked
    assert ((checked.nothing, checked.unannotated), (left_out.nothing, left_out.unannotated)) == (
        (("void", "Promise<void>"), "nothing"), ((), ""))


@pytest.mark.parametrize("given, problem", [
    pytest.param({"nothing": "None"}, "nothing: must be a list of return annotations", id="the old shape, one text"),
    pytest.param({"nothing": []}, "nothing: must be a list of return annotations", id="an empty list"),
    pytest.param({"nothing": [""]}, "nothing: must be a list of return annotations", id="an empty annotation"),
    pytest.param({"nothing": [1]}, "nothing: must be a list of return annotations", id="an annotation that is no text"),
    pytest.param({"unannotated": "none"}, "unannotated: must be nothing", id="another word"),
    pytest.param({"unannotated": True}, "unannotated: must be nothing", id="no text"),
])
def test_annotations_of_no_value_and_a_word_on_none_that_are_not_what_their_key_takes_are_refused(given, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", DOCUMENT | given)
    assert caught.value.problems == (f"presets/language/odd.yaml: {problem}",)


def test_the_test_only_languages_say_their_annotations_of_no_value_or_their_word_on_none():
    loaded = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
              for path in TEST_LANGUAGES}
    assert ((loaded["brace"].nothing, loaded["brace"].unannotated),
            (loaded["percent"].nothing, loaded["percent"].unannotated, loaded["percent"].special)) == (
        (("void", "Promise<void>"), ""), ((), "nothing", r"%\w+"))
```

- [ ] **Step 2: Write the failing stand-ins tests under the test-only languages**

In `tests/modules/rules/application/logic/test_stand_ins.py`, line 8 becomes:

```python
from tests.modules.rules.builders import AUTOSPEC, BRACE, MOCK, PERCENT, PROFILE, in_tests, profile, source
```

Append at the end of the file:

```python
BRACE_PORT = "modules/docs/application/ports/repo.ts"
PERCENT_PORT = "modules/docs/application/ports/Repo.cls"


@pytest.mark.parametrize("methods, expected", [
    pytest.param((Method(4, "send", "Promise<void>"), Method(5, "close", "void")), [],
                 id="every method returns one of the annotations of no value: fire-only"),
    pytest.param((Method(4, "get", "Promise<Order>"), Method(5, "close", "void")),
                 [f"app/{BRACE_PORT}:3: Store is a read port with no fake (stand-ins)"],
                 id="one method returns something else: read, and its fake is missing"),
])
def test_under_a_typescript_like_language_a_port_s_kind_follows_its_annotations_of_no_value(methods, expected):
    store = Class(3, "Store", (), methods, interface=True)
    assert problems([ported(store, path=BRACE_PORT)], checked=profile(language=BRACE)) == expected


@pytest.mark.parametrize("methods, expected", [
    pytest.param((Method(4, "%OnNew", "Order"), Method(5, "Send", None)), [],
                 id="a method with no annotation gives no value, and a special one is left out"),
    pytest.param((Method(4, "Send", None), Method(5, "Get", "Order")),
                 [f"app/{PERCENT_PORT}:3: Store is a read port with no fake (stand-ins)"],
                 id="an annotated method gives a value: read"),
])
def test_under_an_objectscript_like_language_a_method_with_no_annotation_gives_no_value(methods, expected):
    store = Class(3, "Store", (), methods, interface=True)
    assert problems([ported(store, path=PERCENT_PORT)], checked=profile(language=PERCENT)) == expected
```

The Python case of a method with no annotation is already pinned by the `test_ports` row
`a method with no return annotation is reported, and the port then has no kind` and by
`test_without_a_tests_root_ports_are_still_held_to_their_annotations`: they must still pass, same text.

- [ ] **Step 3: Write the failing words and docs tests**

In `tests/modules/spec/application/logic/test_profile_keys.py`, append:

```python
def test_the_annotations_of_no_value_are_said_each_as_written_joined_by_or():
    assert [said("%nothing%", language) for language in (PYTHON, BRACE, PERCENT)] == ["None", "void or Promise<void>", ""]
```

In `tests/modules/spec/application/logic/test_key_catalogue.py`, `WORDS` (lines 12-13) becomes:

```python
WORDS = ("%language%, %extension%, %package_file%, %private%, %interface%, %interface_path%, %namespace%, %comment%, %directives%, "
         "%nothing%, %min_statements%, %min_fields%, %line%, %max_ask%, %fewest_examples%")
```

In `tests/modules/spec/application/logic/test_testing.py`, add `from dataclasses import replace` as the first import
(before `import pytest`, with a blank line between, as `ruff check` wants), and after
`test_the_guards_lines_say_the_names_of_the_framework_the_file_declares` add:

```python
def test_the_stand_ins_line_says_each_annotation_of_no_value_of_the_language():
    architecture = parsed(covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES))
    checked = replace(architecture.language.checked, nothing=("void", "Promise<void>"))
    brace = replace(architecture, language=replace(architecture.language, checked=checked))
    lines = fill("{{guards}}", brace, "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if line.startswith("- `stand-ins`"))
    assert "is fire-only (every method returns `void` or `Promise<void>`) or read" in line
```

In `tests/architecture/test_language_seam.py`, after `test_no_data_file_of_the_format_names_the_language_of_the_data_file`
(ends line 282), add:

```python
@pytest.mark.parametrize("language", LANGUAGES, ids=lambda path: path.stem)
def test_no_data_file_of_the_format_writes_an_annotation_of_no_value_of_the_language_as_a_word(language):
    nothing = yaml.safe_load(language.read_text(encoding="utf-8")).get("nothing", ())
    pattern = re.compile(rf"(?<!\w)(?:{'|'.join(re.escape(entry) for entry in nothing)})(?!\w)")
    found = [(path.name, match[0]) for path in FORMAT for match in pattern.finditer(path.read_text(encoding="utf-8"))]
    assert FORMAT and nothing and found == []
```

- [ ] **Step 4: Run them to verify they fail**

Run: `timeout 900 uv run pytest -q tests/profile_values/test_language.py tests/modules/spec/application/logic/test_language_file.py tests/modules/rules/application/logic/test_stand_ins.py tests/modules/spec/application/logic/test_profile_keys.py tests/modules/spec/application/logic/test_key_catalogue.py tests/modules/spec/application/logic/test_testing.py tests/architecture/test_language_seam.py`
Expected: FAIL. `test_language.py` fails at collection (`cannot import name 'NOTHING'`), and so does
`test_stand_ins.py` (`cannot import name 'PERCENT'`). The loader refuses `nothing: [...]` (`must be a non-empty
string`) and `unannotated` (unknown key). `%nothing%` is left as written. The stand-ins line prints
`` `('void', 'Promise<void>')` ``. The new seam test fails too: `python.yaml` still writes `nothing: None`, one text,
which the test reads letter by letter, so it finds many matches. After Step 7 it reads the list, and until Step 9 it
finds `[('keys.yaml', 'None')]`.

- [ ] **Step 5: The value: `nothing`, `unannotated`, `gives_nothing`**

In `xarch/profile_values/language.py`:

After the imports, before `RecordMark`, add:

```python
NOTHING = "nothing"
"""The one value of the data file's `unannotated`: a method with no return annotation gives no value."""
```

(with two blank lines before `@dataclass`).

In `CheckedLanguage`, `nothing: str = ""` (line 43) becomes `nothing: tuple[str, ...] = ()`, and after
`member: str = ""` (the last field) add `unannotated: str = ""`.

In its docstring, replace `the return annotation of no
    value,` with `the return annotations of no value as its reader writes them (nothing), whether a method with no
    return annotation gives none (unannotated: nothing when it does; empty when the data file does not say),` and
re-wrap to 120 characters.

After `is_special`, add:

```python
    def gives_nothing(self, returns: str | None) -> bool:
        """Whether a method whose return annotation is returns, as the reader writes it (None: it has none), gives no
        value: its annotation is one nothing lists, or it has none and unannotated says so."""
        return returns in self.nothing if returns is not None else self.unannotated == NOTHING
```

- [ ] **Step 6: The loader reads them**

In `xarch/modules/spec/application/logic/language_file.py`:

The docstring line 26, today

```
    nothing        the return annotation of a function that gives no value
```

becomes

```
    nothing        the return annotations, as its reader writes them, that say a function gives no value: a list
    unannotated    `nothing`, its only value: a function with no return annotation gives no value
```

`KEYS` (lines 59-61) becomes:

```python
KEYS = ("title", "extension", "package_file", "interface", "dynamic", "namespace", "cache", "standard", "name", "package",
        "member", "private", "special", "call", "nothing", "unannotated", "comment", "directives", "shebang", "encoding",
        "branching", "importing", "supplies", "immutable", "branching_expressions")
```

Line 57 becomes `from xarch.profile_values.language import NOTHING, CheckedLanguage, InterfaceMark, RecordMark`.

The tokens loop (from Task 1), today

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "nothing", "comment", "shebang")}
    special = _pattern(document, "special", problems)
```

becomes

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "comment", "shebang")}
    special = _pattern(document, "special", problems)
    nothing = _annotations(document, problems)
    unannotated = _text(document, "unannotated", f"must be {NOTHING}", problems, re.compile(re.escape(NOTHING)))
```

In the `CheckedLanguage(...)` call, `nothing=tokens["nothing"]` becomes `nothing=nothing`, and after `member=member`
add `, unannotated=unannotated` (wrap to 120).

After `_words` (ends line 219 today), add:

```python


def _annotations(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, ...]:
    """The return annotations that say a function gives no value, as the reader writes them: a non-empty list of
    non-empty texts; none when the document does not say."""
    if "nothing" not in document:
        return ()
    value = document["nothing"]
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        problems.append("nothing: must be a list of return annotations")
        return ()
    return tuple(value)
```

- [ ] **Step 7: The data files**

`xarch/architectures/presets/language/python.yaml`, line 36, today `nothing: None`, becomes:

```yaml
nothing: [None]
```

`tests/fakes/languages/brace.yaml`: add after `interface: [{keyword: interface}]`:

```yaml
nothing: [void, "Promise<void>"]
```

`tests/fakes/languages/percent.yaml`: add after `special: '%\w+'`:

```yaml
unannotated: nothing
```

- [ ] **Step 8: A port's kind follows `gives_nothing`**

In `xarch/modules/rules/application/logic/stand_ins.py`, `_classified` (lines 122-134), today

```python
    bare = [m for m in methods if m.returns is None]
    ...
    kind = None
    if not bare and methods:
        kind = "read" if any(m.returns != language.nothing for m in methods) else "fire-only"
```

becomes (the `problems = ...` lines between stay as they are):

```python
    bare = [m for m in methods if m.returns is None and not language.gives_nothing(m.returns)]
    ...
    kind = None
    if not bare and methods:
        kind = "fire-only" if all(language.gives_nothing(m.returns) for m in methods) else "read"
```

Its module docstring, lines 8-14, today

```
language marks as a property or as bound to the class counts as the method it is. By its methods' return annotations a
port is:

    read         any method returns something else than no value: the port is written and read back, so it has a fake
    fire-only    every method returns no value, as the data file's `nothing` says it, written as code or as a string
    unannotated  a method has no return annotation: a violation, since the kind follows from it
```

becomes

```
language marks as a property or as bound to the class counts as the method it is. By its methods' return annotations a
port is:

    read         some method gives a value: the port is written and read back, so it has a fake
    fire-only    every method gives no value: its annotation is one the data file's `nothing` lists, or it has none
                 and the data file says `unannotated: nothing`
    unannotated  a method has no return annotation, and the data file does not say `unannotated`: a violation, since
                 the kind follows from it
```

- [ ] **Step 9: The docs line and the word `nothing`**

In `xarch/modules/spec/application/logic/docs_template.py`, `_stand_ins_line` (lines 619-625): after
`    interface = architecture.language.interface_name` add

```python
    nothing = " or ".join(f"`{annotation}`" for annotation in architecture.language.checked.nothing)
```

and in its `return`, the line

```python
            f"`{architecture.language.checked.nothing}`) or read (any method returns a value), each method annotated; every "
```

becomes

```python
            f"{nothing}) or read (any method returns a value), each method annotated; every "
```

In `xarch/modules/spec/application/logic/explain.py`, `words` (from Task 3): in its returned dict, after the
`"directives"` entry add `"nothing": " or ".join(checked.nothing)`, so the last line of the dict reads:

```python
            "directives": ", ".join(f"`{checked.comment} {word}`" for word in checked.directives),
            "nothing": " or ".join(checked.nothing)}
```

and its docstring ends `..., and the prefix of a private name, and the annotations of no value, each as written,
joined by ` or `.` (re-wrap to 120).

In `xarch/architectures/presets/format/keys.yaml`, line 831, `(every method returns None)` becomes
`(every method returns %nothing%)`. The header comment (line 6, `(%extension%, %interface%, ...)`) stays as it is.

- [ ] **Step 10: The builders carry the new values**

In `tests/modules/rules/builders.py`:

- in `PYTHON`, `nothing="None",` becomes `nothing=tuple(PYTHON_FILE["nothing"]),`.
- `BRACE` (lines 42-44, after Task 3's edits still the positional form) becomes:

```python
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extension=BRACE_FILE["extension"],
                        package_file=BRACE_FILE["package_file"], interface=marks_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"])
"""The TypeScript-like test-only language as a check reads it, its patterns, member, interface marks and annotations of
no value read from its data file."""
PERCENT_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "percent.yaml")
                              .read_text(encoding="utf-8"))
PERCENT = CheckedLanguage(title=PERCENT_FILE["title"], extension=PERCENT_FILE["extension"],
                          package_file=PERCENT_FILE["package_file"], interface=marks_of(PERCENT_FILE),
                          special=PERCENT_FILE["special"], unannotated=PERCENT_FILE["unannotated"],
                          names=PERCENT_FILE["name"], package=PERCENT_FILE["package"], member=PERCENT_FILE["member"])
"""The ObjectScript-like test-only language as a check reads it: its interface marks, the pattern of a special name and
its word on a method with no annotation read from its data file."""
```

(the old docstring line 45 of `BRACE` is replaced by the new one above).

- [ ] **Step 11: The seam guard reads the list `nothing`**

In `tests/architecture/test_language_seam.py`:

`TOKEN_KEYS` and its docstring become:

```python
TOKEN_KEYS = ("private", "call", "comment", "shebang")
"""The keys of the data file whose value is a token of the language's code; `nothing` lists several, each a token, and
`special` is the pattern of a special name, which a literal may not match in full."""
```

In `language_tokens`, `tokens = {data[key] for key in TOKEN_KEYS}` becomes:

```python
    tokens = {data[key] for key in TOKEN_KEYS} | set(data.get("nothing", ()))
```

In `ticked_pattern`, the lines

```python
    tokens = "|".join(re.escape(data[key]) for key in TOKEN_KEYS)
```

and

```python
    words = "|".join(re.escape(name) for name in sorted({data["nothing"], *names}, key=len, reverse=True))
```

become

```python
    tokens = "|".join(re.escape(token) for token in (*(data[key] for key in TOKEN_KEYS), *data.get("nothing", ())))
```

and

```python
    words = "|".join(re.escape(name) for name in sorted({*data.get("nothing", ()), *names}, key=len, reverse=True))
```

- [ ] **Step 12: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/profile_values tests/modules/spec tests/modules/rules tests/architecture`
Expected: all pass. Then `uv run ruff check` gives no problem.

- [ ] **Step 13: Run the whole suite**

Run (background, read at the end): `timeout 1500 uv run pytest -q`
Expected: all pass. `tests/bootstrap/test_docs.py` and the golden docs tests show the stand-ins line unchanged
(`` `None` ``).

- [ ] **Step 14: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml \
  xarch/modules/rules/application/logic/stand_ins.py xarch/modules/spec/application/logic/docs_template.py \
  xarch/modules/spec/application/logic/explain.py xarch/architectures/presets/format/keys.yaml \
  tests/modules/rules/builders.py tests/architecture/test_language_seam.py tests/profile_values/test_language.py \
  tests/modules/spec/application/logic/test_language_file.py tests/modules/rules/application/logic/test_stand_ins.py \
  tests/modules/spec/application/logic/test_profile_keys.py tests/modules/spec/application/logic/test_key_catalogue.py \
  tests/modules/spec/application/logic/test_testing.py
git commit -m "The data file's nothing is a list of the return annotations of no value, python [None] and brace [void, Promise<void>], and unannotated: nothing says a method with no annotation gives none, as percent does; a port is fire-only when every method gives no value and is reported unannotated only where the file does not say so; the docs line, the new word %nothing% and keys.yaml say each annotation as written"
```

---

### Task 6: The header of `python.yaml`, README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `xarch/architectures/presets/language/python.yaml:1-21` (header comment)
- Modify: `README.md:136-148`
- Modify: `CHANGELOG.md` (under `## [Unreleased]`, `### Changed`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-3-5/regenerate_docs.py`

**Interfaces:**
- Consumes: the behaviour of Tasks 1-5.
- Produces: nothing later tasks use.

- [ ] **Step 1: The header of `python.yaml`**

Replace lines 1-21 of `xarch/architectures/presets/language/python.yaml` (every comment line before `title: Python`)
with:

```yaml
# The language Python, as a profile names it with `language: python`: what is true of the language as a whole and is
# needed outside the reader that turns source into facts. title is how a message says it; extension the ending of a
# source file's name; package_file the file that stands for the folder holding it; interface the marks of a class that
# is an interface (a port), each {base: <outside name>}, a name among its bases, or {keyword: <word>}, a keyword its
# declaration carries (Python declares none with one); dynamic the callables that import by a name worked out when the
# code runs; namespace the namespace of the names the language binds without an import; cache the folder its tools
# keep what they compile in, whose files neither the checks nor the examples read; standard where the names of the
# standard library are known from (interpreter: the one running xarch). The tokens of its code that the checks and the
# docs need: name, what a name may be (a regular expression); package, what an import names from outside the app as
# one step (a regular expression); member, the text that joins a package to a name in it in a profile's lists (name,
# package and member are given together); private, how a name starts that is private to its file or folder; special,
# the pattern of a name the language reserves for itself (a regular expression the whole name matches); call, the
# special method that calling an instance runs; nothing, the return annotations that say a function gives no value,
# as the reader writes them (a list); unannotated, left out here, would say with its one value, nothing, that a
# function with no return annotation gives none; comment, the marker of a line comment; directives, the comments its
# tools read as instructions, each after the marker (a space in one stands for any spaces); shebang, how line 1 names
# the program that runs the file; encoding, how line 1 or 2 declares the file's encoding (a regular expression, after
# the marker); branching, the keywords of the statements that branch; branching_expressions, the keywords of the
# expressions that choose between values, as its reader records them; immutable, what makes a class an immutable
# record: a dotted name among its bases or its decorators, a decorator called with each keyword written after it, as
# written; importing, how a file imports a name from another file of the app, {dotted} standing for that file's dotted
# path and {name} for the name.
# supplies: the facts its reader turns the source into, each exact or {partial: what it misses}; a key whose check
# needs a fact not listed here is refused, and one that reads a partial fact is listed as approximate.
```

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/test_language.py tests/modules/spec/application/logic/test_language_file.py tests/architecture/test_language_seam.py`
Expected: all pass (the file still loads; comments are not read).

- [ ] **Step 2: README**

In `README.md`, replace the paragraph from `` `language` names the language of the app`` (line 136) through
`` `dataclasses.dataclass(frozen=True)`).`` (line 148) with:

```markdown
`language` names the language of the app: `python`, which is the default and the only one xarch reads today. What is
true of a language as a whole lives in a data file shipped beside the profiles, `xarch/architectures/presets/language/
<name>.yaml`, the way `testing: pytest` resolves to `presets/testing/pytest.yaml`: the ending of a source file, the file
that stands for a folder, what marks an interface (`interface`, a list of marks, each a base, `{base: typing.Protocol}`,
or a keyword a declaration carries, `{keyword: interface}`), the namespace of the builtins, the callables that import by
a computed name, the folder of compiled files, and where the standard library's names are known from (`interpreter`);
and the tokens of its code the checks and the docs need: what a name may be, what an import names from outside the app
as one step (`package`) and the text that joins a package to a name in it in the profile's lists (`member`, `.` for
Python), so that an outside name is written `<package><member><name>`, how a private name starts, the pattern of a
special name (`special`, a regular expression the whole name matches), the special method calling an instance runs,
the annotations of no value (`nothing`, a list: `[None]` for Python) and, optionally, that a method with no return
annotation gives none (`unannotated: nothing`), the comment marker and the comments its tools read, the shebang, the
encoding declaration, the keywords of the statements that branch and of the expressions that choose between values
(`branching_expressions`), and what makes a class an immutable record (`immutable`: a base, or a decorator called with
its keywords, such as `dataclasses.dataclass(frozen=True)`).
```

The line after it (`The rest of what a check knows of the language is one adapter, ...`) stays.

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: all pass.

- [ ] **Step 3: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, `### Changed` (line 18), insert this entry as the first of the list,
with one blank line after the heading and one blank line after the entry:

```markdown
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
```

- [ ] **Step 4: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-5/regenerate_docs.py` (never committed):

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
uv run python -I /tmp/xarch-3-5/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines, and an empty `git diff`. If the diff is not empty, stop and report it with the diff
(`git checkout -- docs/cli docs/web docs/xarch` restores the files). The docs must not move.

- [ ] **Step 5: Run the gates**

Run each, the first in the background with a recorded PID, and read it at the end:

```bash
timeout 1800 uv run pytest -q
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

Expected: the suite passes, both checks report no violation, ruff reports nothing, and the profile check loads.
`git status --short` shows no change under `tests/bootstrap/corpora/` and nothing under `.claude/` staged.

- [ ] **Step 6: Commit**

```bash
git add xarch/architectures/presets/language/python.yaml README.md CHANGELOG.md
git commit -m "The header of python.yaml says the new shapes, interface marks as maps, special a regular expression matched against the whole name, nothing a list and unannotated; the README's language paragraph and the CHANGELOG say the same, with the four refusal texts; the golden docs regenerate with no diff"
```

---

## Self-review against the spec

**Spec coverage.**
- 2.1 `interface` marks, `InterfaceMark`, the Python value, `[]`/left out, the refusal said once, old shape refused,
  not read when the joins are refused: Task 3, Steps 1, 7-9.
- 2.2 `Class.interface`, the port, the reader (subscripted base, alias, keyword marks nothing, docstring), callers
  (`source_check.py`, `holding.py`), `sources.py:52` untouched, the fake: Task 2 and Task 3, Step 12.
- 2.3 the three sites read `cls.interface`, with both new cases (a Protocol base unmarked is no port; marked with no
  base is one): Task 3, Steps 4 and 13.
- 2.4 `class.interface` in `FACTS`, the needs of stand-ins, fakes and the filter, Python supplies it, a missing supply
  refuses `fakes`: Task 4 (plus deviation 1 for dead-code).
- 2.5 `nothing` a list, `unannotated`, refusals, `KEYS`, no hidden default: Task 5, Steps 1, 5-7.
- 2.6 fire-only and read; unannotated reported only where `unannotated` is not given; `call` kept: Task 5, Steps 2 and
  8 (the `__call__` row stays in `test_ports`).
- 2.7 `special` a pattern, `is_special` by `fullmatch`, Python's pattern equal to the old rule on every short name, the
  loader's texts, callers untouched: Task 1.
- 2.8 `interface_name`, `interface_path`, the new word `nothing`, the docs line, `keys.yaml` `%nothing%`, the filter text,
  `vocabulary.py:178` kept: Tasks 3, 4, 5.
- 2.9 data files (`python.yaml`, `brace.yaml`, `percent.yaml`, both load) and the loader's docstring: Tasks 1, 3, 5;
  the `python.yaml` header: Task 6.
- 2.10 README, CHANGELOG, golden docs with no diff: Task 6.
- Section 3 refusals, each with its exact text: Task 1 (special), Task 3 (interface), Task 5 (nothing, unannotated).
- Section 4 tests: each row has a step (the seam rows in Tasks 1, 3, 5; the builders in Tasks 1, 3, 5; the bootstrap
  suites in each task's whole-suite step and Task 6).
- Section 5 gates: Task 6, Step 5.

**Placeholder scan.** No "TBD", no "similar to Task N"; every code step shows the code. Where a docstring phrase is
replaced inside a longer paragraph, the old and new phrases are given exactly, with the instruction to re-wrap to 120.

**Type consistency.** `InterfaceMark(base, keyword)` (Task 2) is what the loader (Task 3, `_interface_mark`), the
builders (`marks_of`), `interface_name` and `words` read. `Class.interface` (Task 2) is what the three checks read
(Task 3). `read(..., interface=...)` has the same name and type on the port, the adapter and the fake (Task 2) and at
the callers (Task 3). `NOTHING`, `nothing: tuple[str, ...]`, `unannotated: str` and `gives_nothing` (Task 5, Step 5)
are what the loader, the stand-ins and the builders use in the same task.

**Review Focus.** Each of the five lines has its test: 1-2 in Task 2, Step 1; 3 in Task 3, Step 1; 4 in Task 5,
Step 1; 5 in Task 5, Step 2.
<!-- task-pipeline: validated -->
