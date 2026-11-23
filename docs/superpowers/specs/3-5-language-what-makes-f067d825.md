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
