# 3.10 reader: a record decided by the fact `class.record`, and immutable marks as maps

Card `60c2f93a`, subtask of `3c7754c4`, blocked by `46146cb3` (3.9, the fact `public`, done on the branch this one
stacks on, commit `1c2008d`). Release step 8e of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3, line 271:
"`class.record`; immutable marks as maps. | language-neutral 10 | Step 8 (marks as maps). Before 12 (the kind
`records`).").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below **LN**),
section 10 (lines 967-1032: 10.1 at 969, 10.2 at 976, 10.3 at 997, 10.4 at 1007, 10.5 at 1013, 10.6 at 1022). Also
`code-shape-design.md` (below **CS**) 2.1, line 243: the Needs column of the kind `records` is `class`,
`class.record` (amended so by LN 10.3 lines 1002-1003; R3 C8, lines 159-166). That kind belongs to release step 12
(story 4); this step only makes `class.record` the fact step 12 will read.

Release-wide rules this step inherits: R3 O4, O5 (lines 228-229: README and CHANGELOG lines under `[Unreleased]`),
O7 (line 231: `class.record` is the fact of 8e, placed after `public` in `FACTS`; in `python.yaml` `supplies`,
`NEEDS`, `test_needs_agree.py`), O8 (line 232: golden docs regenerated, diff read; none expected, LN 10.5 line 1020),
O18 (line 242: `python.yaml` is edited by 8e, its lines only), O19 (line 243: the test-only files `brace.yaml` and
`percent.yaml` gain this step's keys and cases). Dodges that apply (card; LN lines 1139-1166): computing `record` in
`facts.py` beside `Class.record` (LN line 1161, "One source per fact"); claiming neutrality with one data file (LN
line 1143); a hidden default in the code (LN line 1152); letting the recorded corpora or golden docs change "a
little" (LN line 1165); a test of the language's name in the checking code (LN line 1141).

## 1. Goal

A record is a type the language writes to hold data, with no behaviour of its own (LN 10.1, lines 971-974). Python
writes one as a class with only special methods that a top-level function of its file names as what it returns;
another language writes it otherwise. The reader decides it and says it as a fact, `Class.record`, as it already says
`Class.immutable` from the marks it is handed. The checking code stops computing it: `facts.py` reads `cls.record`,
and the filter `record` needs `class.record` in place of `class.methods` and `function.returns` (LN 10.3).

The marks that make a class an immutable record become maps, one of four forms, as interface marks already are (LN
10.2 lines 982-992; LN 10.3 lines 1004-1005). Python's reader reads the two forms Python's data file writes.

For Python the reader computes `record` with today's rule exactly, and its immutable marks mean what they meant, so
Python's findings, the recorded corpora and the golden docs do not move (LN 10.5 line 1020).

## 2. Observable behavior

### 2.1 The fact (LN 10.2 lines 978-981; R3 O7)

- `FACTS` (`xarch/profile_values/capabilities.py`) gains `class.record`, placed right after `public` (the fact of
  8d, R3 O7), with the text of LN 10.2 line 978: "whether a class is a record, as the language writes one".
- `python.yaml` (`xarch/architectures/presets/language/python.yaml`) `supplies` gains `class.record: exact` (LN 10.2
  line 981), next to the other `class.*` entries. Nothing else in `supplies` moves (R3 O18).
- A language whose data file lists `supplies` without `class.record` gets today's needs refusal, with today's text,
  for every key of 2.4 it sets (LN 10.4 lines 1009-1011). No new refusal text. Nothing is refused at load for Python.

### 2.2 What the reader supplies (LN 10.2; LN 10.6 line 1028)

- `Class` (`xarch/modules/rules/domain/parsed.py`) gains `record: bool`, default `False`, and its docstring says it:
  "record: it is a record, as the language's reader says". The default exists so hand-built values keep building;
  the Python reader sets it on every class itself.
- Python's reader (`xarch/modules/rules/adapters/fs_source_tree.py`) sets `record` by today's rule exactly
  (`facts.py:245-246` at `1c2008d`): a class is a record when the name of every method of its body (`Class.methods`)
  matches the language's special-name pattern in full, and some function of the same file defined at the top level
  (a `Function` of `SourceFile.functions` with no `owner`) has the class's name in its `returns_named`. A class with no
  method is a record when such a function names it. The rule reads the values the reader already produces for the
  same file (its methods, its functions), so it cannot disagree with them.
- The special-name pattern is the data file's `special`, handed to the reader as `private` already is: `read` and
  `parsed` of the port `SourceTree` (`xarch/modules/rules/application/ports/source_tree.py`) and of `FsSourceTree`
  take a keyword-only `special: str` beside `private`, documented in the port's docstrings ("a class is a record when
  every method's name matches `special` in full, a regular expression ("": no name is special), and a top-level
  function of its file names it in its return annotation"). An empty `special` makes no name special: a class with any
  method is no record. No default value: every caller says what it hands (dodge LN line 1152).
- Every caller passes the profile language's `special` where it passes the language's `private` today
  (`services/holding.py`, `services/source_check.py` for the app and the tests, `services/sources.py`,
  `services/examples.py`, `services/asking.py`). `services/source_reading.py`, which hands `private=""` because spec
  has no profile, hands `special=""` likewise; it reads only imports and comments. The test fake
  `tests/fakes/filesystem.py` takes the same signature.
- The module docstring of `fs_source_tree.py` gains a paragraph stating the record rule, beside the paragraphs on
  immutable records and interfaces.

### 2.3 Immutable marks as maps (LN 10.2 lines 982-992; LN 10.3 lines 1004-1005; LN 10.4 line 1009)

- A data file's `immutable` is a list of marks, each a map of one of four forms:
  - `{base: <outside name>}`: a name among the class's bases;
  - `{decorator: <outside name>, keywords: {<name>: <value>, ...}}`: a decorator, called with each keyword given,
    each value as written (a string). `keywords` may be left out: the decorator then marks a class however it is
    written, bare or called;
  - `{fields: <word>}`: a keyword that marks every field (TypeScript-like `readonly`, inferred);
  - `{type: <outside name>}`: a wrapper type (TypeScript-like `Readonly`, inferred).
  `base`, `decorator` and `type` are read with the outside-name parser of section 3 (`outside_name`, the file's
  `name`, `package`, `member` and `namespace`); `fields` as the interface mark's `keyword` is (a name the language
  allows, holding no member); each key of `keywords` a name the language allows, each value a non-empty string.
- Python's data file writes, replacing the string form (LN 10.2 line 986):
  `immutable: [{base: typing.NamedTuple}, {decorator: dataclasses.dataclass, keywords: {frozen: "True"}}]`.
  Its header comment's description of `immutable` says the four forms and that Python writes the first two.
- Any other value is refused, once for the key, with the text of LN 10.4 line 1009 exactly:
  `immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}`. That covers: `immutable` not a list; an
  item that is no map, a string included (the old form is no longer read: a data file is no user's file, so no
  retired-key hint, LN 12, line 1068); a map with no known form, with two forms
  (`{base: a.B, type: a.C}`), with `keywords` beside anything but `decorator`, with an unknown key; an outside name or
  a word the file's patterns refuse; `keywords` that is no map, is empty, or holds a key the language does not allow
  or a value that is no non-empty string. As with `interface`, a refused key yields no marks, and when the keys that
  say how an outside name is written are refused already, no mark is read and no second problem is added.
- `RecordMark` (`xarch/profile_values/language.py`) becomes one of the four forms, as `InterfaceMark` is: fields
  `base` (steps), `decorator` (steps), `keywords` (pairs, only with `decorator`), `fields` (a word), `type` (steps),
  exactly one of `base`, `decorator`, `fields`, `type` given. Its old `path` field goes. Its docstring says the four
  forms.
- Python's reader reads `base` and `decorator` marks (LN 10.2 lines 991-992): a class is an immutable record when a
  `base` mark's path is one of its bases (read as today: a subscripted base by what it subscripts, an alias by the
  path it reaches), or a `decorator` mark's path is that of one of its decorators (read as a call's callee is) and the
  decorator is called with each keyword of the mark, its value as written (`ast.unparse`). A `fields` or `type` mark
  marks no class in Python's reader (the docstring says so, as it says a keyword interface mark marks none). For
  Python's two marks this is today's meaning on every Python source (the corpora gate it). The forms are sharper than
  the string form was only where Python's file does not go: a `base` mark no longer matches a decorator of that name,
  and a keyword-less `decorator` mark no longer matches a base of that name (the string form matched either place).

### 2.4 Needs (LN 10.3 lines 999-1003; LN 10.6 line 1032; R3 O7)

- The kind `class` (`xarch/modules/rules/domain/vocabulary.py`): the field `record` needs `("class.record",)`, in
  place of `("class.methods", "function.returns")`.
- The filter `record` says "the class is a record, as the language's reader decides" (LN 10.3 line 1000).
- `NEEDS` (`xarch/modules/spec/domain/key_table.py`) for `parts.<part>.holds`: what its expanded rules read, which
  `tests/bootstrap/test_needs_agree.py` compares. Expected, from what `_holds` reads (the kinds `class` and
  `function`, the filters `top-level`, `public`, `exception`, `record`): `("class", "class.exception",
  "class.record", "function", "public")`, losing `class.methods` and `function.returns`. The agree test is the
  arbiter: the entry is what it says, and no fact is left in or added to make it pass.
- A check of the user's own whose filter is `record` needs `class.record` (it follows from the field needs).
- A language with `supplies` that lists every fact but `class.record` is refused `parts.<part>.holds` with today's
  needs text naming `class.record` and its `FACTS` text; given `class.record`, it loads.

### 2.5 The engine reads the fact (LN 10.3 line 999; dodge LN line 1161)

- `facts.py` `_class` puts the trait `record` on a class's fact exactly when `cls.record` is true. No expression in
  `facts.py` computes a record: it no longer reads `is_special` or `returns_named` for it, and `_class` takes no
  parameter it no longer uses. The docstring line of `record` (`facts.py:52-53`) says "a class the language's reader
  says is a record".
- `profile.language.is_special` stays for its other readers (`stand_ins.py`, `filters.py`, `profile_checks.py`).

### 2.6 Things that stay as they are

- The filter words `record` and `immutable`, the rule ids `holds` and `immutable`, every message and fix text of
  those rules, and their expansion (`expansion.py` `_holds`, `_immutable`).
- `keys.yaml` texts of `parts.<part>.holds` and `parts.<part>.immutable`, `docs_template.py`'s `holds` and
  `immutable` lines, and the text of the filter `immutable`. They describe Python's marks and records as they still
  are; their rewrite belongs to step 12 (story 4) and the wrap-up.
- Python's findings, every recorded corpus under `tests/bootstrap/corpora/`, and the golden docs
  `docs/{cli,web,xarch}/testing.md` (LN 10.5 line 1020; R3 O8).

## 3. The test-only languages (LN 10.5 lines 1017-1019; dodge LN line 1143; R3 O19)

- `tests/fakes/languages/brace.yaml` gains `immutable: [{fields: readonly}]`, and its header comment says what it is.
  It loads; its marks read as one `fields` mark.
- `tests/fakes/languages/percent.yaml`'s `immutable: ["%SerialObject"]` becomes `[{base: "%SerialObject"}]` (the
  string form is refused now). It loads, read by its own patterns.
- Neither file gains `supplies`: a file with no `supplies` says nothing of its reader and holds no key to it (as
  today). The refusal for a language lacking `class.record` (2.4) is proved with a language value whose `supplies`
  omits it, as 3.9 proved `public` (`test_profile_needs.py`, `UNSAID`).
- The builders' `BRACE` (`tests/modules/rules/builders.py`) carries brace's marks as the loader reads them.

## 4. Tests (written first)

Tiers in this repo: **adapter** (`tests/modules/rules/adapters/`, the real reader on real files), **unit**
(`tests/modules/**/logic`, `domain`, and services with fakes), **bootstrap** (`tests/bootstrap/`, the CLI and the
recorded corpora end to end), **architecture** (`tests/architecture/`, guards over xarch's own source).

### 4.1 The one-off equality on Python source — adapter (LN 10.5 lines 1015-1016)

New file `tests/modules/rules/adapters/test_fs_source_tree_record.py`, built as `test_fs_source_tree_public.py` is.
Adapter tier: it runs the real reader over real files. For every Python file of xarch's own source (the bundled
example project included) and of each recorded archive (`df537ca`, `7cc6111`, `examples`, unpacked into `tmp_path`,
never edited), read with the `special` and `private` of `python.yaml`, every class's `record` equals the old rule
written in the test as its oracle: every method name matches `special` in full, and a function of the file with no
`owner` has the class's name in `returns_named`. A file that does not parse is passed over. The test also asserts
some class is a record and some is not, so it cannot pass on an empty or uniform read.

### 4.2 The reader — adapter, `tests/modules/rules/adapters/test_fs_source_tree.py`

Adapter tier: what the reader says of written source.
- A class with only special methods (`__init__`, `__eq__`) that a top-level function returns (`def make() -> P`) is a
  record; with no method at all, likewise.
- Not a record: a class with one ordinary method returned by a top-level function; a class with only special
  methods no top-level function names; a class only a method of another class returns; a class named only inside a
  parameter annotation.
- A return annotation naming it inside a union or a subscript (`-> P | None`, `-> list[P]`) makes it a record, since
  `returns_named` holds it (today's rule).
- `special=""`: a class with a special-looking method is no record; one with no method returned by a function is.
- Immutable marks as maps (the existing parametrised case, rewritten): `{base: typing.NamedTuple}` marks a base
  `NamedTuple` and `typing.NamedTuple` (through its import); `{decorator: dataclasses.dataclass, keywords: {frozen:
  "True"}}` marks `@dataclass(frozen=True)` and `@dataclasses.dataclass(frozen=True, slots=True)`, not
  `@dataclass`, `@dataclass()` or `@dataclass(frozen=False)`; a `decorator` mark with no keywords marks `@dataclass`
  bare and called; a `base` mark does not mark a decorator of that name; `fields` and `type` marks mark no class.
- With no marks, no class is immutable (kept).

### 4.3 Neutrality with hand-built facts — unit (LN 10.5 lines 1017-1019)

Unit tier: the checking code alone, under the test-only languages, with no reader.
- Under `BRACE`, a hand-built `Class(record=True)` with no method list and no function naming it (a TypeScript type
  alias) gets the trait `record` (`test_facts.py`), and is exempt from `holds: functions` (`test_holds.py`, logic):
  not listed. The same class with `record=False` is listed.
- Under `PERCENT`, a hand-built class with only `%`-special methods that a top-level function returns, but
  `record=False`, is not a record: the engine does not compute it.
- Under `BRACE`, hand-built classes with `immutable=True` pass `parts.<part>.immutable`; one with `immutable=False` is
  listed (`test_immutable` or the logic test that covers `_immutable`).
- The builders: `read_as` (`tests/modules/rules/builders.py`) sets `record` on a hand-built file under `PYTHON` as
  Python's reader would (the rule of 2.2, using `PYTHON.special`), and keeps a class given `record=True` a record;
  under any other language it keeps `record` as given. Its docstring says so. A builders test pins both.

### 4.4 Facts, filters and vocabulary — unit

- `test_facts.py`: the trait `record` follows `Class.record` alone, both ways (a class the old rule calls a record but
  given `record=False` is none, and the reverse).
- `tests/modules/rules/domain/test_vocabulary.py`: the field `record` of `class` needs exactly `("class.record",)`;
  the filter `record`'s text is the text of 2.4.
- `test_filters.py`, `test_expansion.py`, `test_reads.py`, `world.py`, `test_rule.py`, `tests/modules/rules/
  application/test_holds.py`: hand-built classes meant as records carry `record=True` or go through `read_as` under
  `PYTHON`; none relies on the engine computing it.

### 4.5 Spec side — unit

- `tests/modules/spec/application/logic/test_language_file.py`:
  - the four forms read in the order written, each to its `RecordMark` (`{base: pkg.Record}`, `{decorator:
    pkg.record, keywords: {frozen: "yes", slots: "no"}}`, `{decorator: pkg.record}`, `{fields: readonly}`, `{type:
    pkg.Frozen}`); no `immutable`, no marks;
  - each refusal of 2.3 gives the one text of LN 10.4, once for the key (parametrised: not a list, a string item,
    two forms, `keywords` beside `base`, an unknown key, an empty `keywords`, a keyword value that is no string, an
    outside name the patterns refuse, a `fields` word holding the member);
  - the percent lists read by their own patterns (`{base: "%SerialObject"}`, `{decorator: "%Lib.Rec", keywords:
    {frozen: "yes"}}`) and refused under Python-like patterns, with the one text;
  - each test-only file loads; percent's marks are one `base` mark, brace's one `fields` mark.
- `tests/modules/spec/application/test_language.py`: Python's data file loads to `RecordMark(base=("typing",
  "NamedTuple"))` and `RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),))`, and
  supplies `class.record` exact.
- `tests/profile_values/test_language.py`: `RecordMark`'s forms as values, if that file pins them.
- `tests/modules/spec/application/logic/test_profile_needs.py`: `class.record` is the fact right after `public`,
  with the text of 2.1; Python supplies every fact exact (kept, now including it); a language that supplies every
  fact but `class.record` is refused `parts.<part>.holds` with the needs text, and loads once given it.

### 4.6 Guards (architecture) and end to end (bootstrap)

- `tests/architecture/test_language_seam.py`: passes unchanged, or with the least change its own rules call for (it
  looks for the data file's tokens outside the reader; `facts.py` now holds fewer). No entry is loosened.
- `tests/bootstrap/test_needs_agree.py`: passes with the `NEEDS` of 2.4. Bootstrap tier: it expands every key.
- `tests/bootstrap/test_recorded_corpora.py` and the other bootstrap tests pass unchanged: no recorded finding moves.

## 5. Docs (R3 O4, O5, O8)

- README, the language paragraph (lines 155-157 at `1c2008d`): `immutable` says the marks are maps, `{base}`,
  `{decorator, keywords}`, `{fields}` or `{type}`, such as `{decorator: dataclasses.dataclass, keywords: {frozen:
  "True"}}`; and a sentence or clause that the reader decides whether a class is a record, the fact `class.record` a
  reader supplies, which `holds` and the filter `record` read. Nothing else in the README moves.
- CHANGELOG, under `[Unreleased]`: one `### Added` entry for the fact `class.record` (what it is, who needs it, that
  the reader says it as `Class.record`, that Python supplies it computed as before), and one `### Changed` entry for
  immutable marks as maps (the four forms, Python's line, the refusal text, that the string form is no longer read,
  "No finding of a Python app changes"), in the style of the 3.8 and 3.9 entries.
- The language file's parser docstring (`language_file.py:49-50`) and `python.yaml`'s header comment say the four
  forms.
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated with the repo's generator and the diff read; expected
  none. Never edited by hand. Any diff is a defect of this step to fix in the code, not in the docs.

## 6. Out of scope

- The kind `records` of `holds`, `holds` as a map of kinds, and the nested refusal address
  `parts.logic.holds.records` (LN 10.4 lines 1010-1011; CS 2.1) — story 4, release step 12. Here `holds` stays one
  word, and its NEEDS entry is the only `holds` needs that changes.
- `function.top_level` and `callback` neutrality (LN 10.2 lines 993-995) — release step 9 and later.
- Rewriting the `holds` and `immutable` texts of `keys.yaml`, `docs_template.py` and the filter `immutable` — step 12
  and the wrap-up (step 25).
- A loader check that a reader reads every form its data file writes before it supplies `class.immutable` (LN 10.2
  lines 991-992 state it as the reader author's duty; Python's data file writes only forms its reader reads). Not
  built here.
- The outside-name parser itself (section 3, already built), and any retired-key entry for the string form of
  `immutable` (data files get none, LN 12 line 1068).
- Any edit to the recorded corpora, the bundled profiles, `architecture.yaml` or the golden docs.

## 7. Gates

Each passing on this branch alone, the full suite green:

- `uv run pytest -q` (over two minutes: run in the background, read at the end)
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check` (never `--fix`)
- `uv run xarch profile check architecture.yaml`

Project rules: no comments in xarch's code (docstrings are kept and extended); tests written first; examples simple,
with absolute `app.` imports; recorded corpora never edited; Python only in the reader adapter and the data files
under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.

## 8. Review focus (for the planner)

- A class with no method and a top-level function naming it is a record under Python (`all` of nothing is true);
  the reader must keep that, or the corpora move.
- `special` threaded to every reader caller: a caller that forgets it (or a default that hides it) silently makes no
  method special, so every dataclass with `__post_init__` stops being a record. Every caller passes it explicitly.
- A `base` mark must no longer match a decorator, and a `decorator` mark with keywords must not match a bare
  decorator; Python's two marks keep today's meaning, which the corpora gate and 4.2 prove.
- The `holds` NEEDS entry is settled by `test_needs_agree.py`, not by hand: dropping `class.methods` and
  `function.returns` only if nothing else `holds` expands to reads them.
- YAML reads `frozen: True` (unquoted) as a boolean: the loader refuses a keyword value that is no string, so
  Python's data file must quote `"True"`, and the refusal is tested.
