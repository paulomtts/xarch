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

---

# 3.10 reader: a record decided by the fact `class.record`, and immutable marks as maps — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Whether a class is a record becomes a fact, `class.record`, that the language's reader supplies as
`Class.record` (for Python from the data file's `special`, with today's rule exactly), the engine reads it instead of
computing it, `holds` needs `class.record` in place of `class.methods` and `function.returns`; and the data file's
immutable marks become maps of four forms, as interface marks are. No finding, corpus or golden doc of a Python app
moves.

**Architecture:** The rules domain's `Class` gains `record: bool = False`; `FsSourceTree.read`/`parsed` (port, adapter,
fake) take a required keyword `special: str` beside `private`, every service hands `profile.language.special`
(`source_reading.py` hands `""`), and the reader works out `record` from the methods and top-level functions it has
already read (Task 1). `FACTS` and `python.yaml` gain `class.record` (Task 2). `facts.py` reads `cls.record`, the
vocabulary's `record` field needs `class.record`, the filter `record` says the reader decides it, `NEEDS` for
`parts.<part>.holds` drops `class.methods` and `function.returns` for `class.record`, and the test builders read a
hand-built Python file's records as Python's reader would (Task 3). `RecordMark` becomes one of four forms, the loader
reads maps and refuses anything else with one text, Python's and the test-only data files write maps, and the reader
reads `base` and `decorator` marks (Task 4). README, CHANGELOG, golden docs and the gates (Task 5).

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/3-10-reader-a-record-60c2f93a.md` (prepended above).

## Global Constraints

- `FACTS["class.record"]` is exactly `whether a class is a record, as the language writes one`, placed right after
  `public` (before `function`).
- `python.yaml`: `class.record: exact` right after `class.interface: exact` under `supplies`; `immutable:` becomes
  exactly `immutable: [{base: typing.NamedTuple}, {decorator: dataclasses.dataclass, keywords: {frozen: "True"}}]`;
  the header's words for `immutable` (Task 4). Nothing else in the file moves.
- The class kind's `field_needs["record"]` is exactly `("class.record",)`; the filter `record`'s meaning is exactly
  `the class is a record, as the language's reader decides`.
- `NEEDS["parts.<part>.holds"]` is exactly `("class", "class.exception", "class.record", "function", "public")`; no
  other `NEEDS` entry changes. `tests/bootstrap/test_needs_agree.py` is the arbiter.
- `SourceTree.read` and `SourceTree.parsed` take a keyword-only `special: str` with no default (port, adapter, fake).
  `source_reading.py` passes `special=""`.
- `Class.record: bool = False`; the Python reader sets it on every class itself.
- `RecordMark` fields are exactly `base: tuple[str, ...] = ()`, `decorator: tuple[str, ...] = ()`,
  `keywords: tuple[tuple[str, str], ...] = ()`, `fields: str = ""`, `type: tuple[str, ...] = ()`; `path` is gone.
- The loader's one refusal text is exactly `immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}`,
  once for the key, and no other `immutable:` text remains.
- `facts.py` no longer calls `is_special` nor reads `returns_named`; `_class` takes `(cls, read, defined, ports)`.
  `CheckedLanguage.is_special` stays.
- Unchanged: the filter words `record` and `immutable`, the rule ids and every message and fix text, `expansion.py`,
  `keys.yaml`, `docs_template.py`, the filter `immutable`'s text.
- Python's findings, `tests/bootstrap/corpora/` (never edited) and the golden docs `docs/{cli,web,xarch}/testing.md`
  (regenerated, diff empty) do not move.
- No comments in xarch's code (docstrings as the code base writes them); no docstring of xarch's code names the
  language ("Python") outside the reader adapter; tests first; Python only in the reader adapter and the data files
  under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- Gates (Task 5): `uv run pytest -q` (in the background with `timeout`), `uv run xarch check`,
  `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Design decisions the spec left to the planner

- The reader computes `record` in `_classes`, which is handed the tuple of `Function`s `_functions` already built for
  the file (so the rule reads the same `returns_named` and `owner` the file carries), through a new adapter helper
  `_record(name, methods, functions, special)`. `_parsed` builds `functions` once and passes it to both `SourceFile`
  and `_classes`.
- `FakeSourceTree` records each `special` it is handed in `specials` (as `prefixes` records `private`), and a new
  `tests/modules/rules/application/test_special_handed.py` mirrors `test_private_handed.py`, one test per service.
- In `tests/modules/rules/adapters/test_fs_source_tree.py` a dict `HANDED = {"private": PRIVATE, "special": SPECIAL}`
  replaces every `private=PRIVATE` by `**HANDED`, so no line grows past 140.
- The test builders (`tests/modules/rules/builders.py`): `read_as(file, language)` also sets `record` on each class:
  as given, or, when `language.title == PYTHON.title`, true when every method `language.is_special` and a function of
  the file with no `owner` holds the class's name in `returns_named`. So every Python test built through `source()`
  keeps its findings with no edit; a `SourceFile` built directly that is meant as a record carries `record=True`
  itself (only `tests/modules/rules/application/test_holds.py`'s `"record"` file). A dry run of the engine change
  alone showed exactly these consumers.
- The builders' marks: `records_of(file)` reads a data file's `immutable` maps as the loader does (beside
  `marks_of`); `BRACE` takes `immutable=records_of(BRACE_FILE)`; `PYTHON` writes its two marks in the new form
  literally, as it does today.
- The builder tests and the hand-built neutrality tests live beside what they exercise: `test_facts.py` (the trait,
  the builders), `tests/modules/rules/application/logic/test_holds.py` (`holds` and `immutable` under `BRACE`).
- The new equality test is its own file, `tests/modules/rules/adapters/test_fs_source_tree_record.py`, built as
  `test_fs_source_tree_public.py` is; its oracle is the old rule written in the test with the data file's `special`.

## Review Focus

1. A caller of the reader that forgets `special` (no method would be special, so every dataclass with
   `__post_init__` would stop being a record and `holds` would list it): the keyword is required. Pinned in Task 1
   (`test_the_reader_must_be_handed_the_pattern_of_a_special_name`, and `test_special_handed.py`, one test per
   service, plus `source_reading`'s `""`).
2. A class with no method that a top-level function returns is a record (`all` of nothing): pinned in Task 1 (the
   reader's parametrised row `no method at all`, and the equality test over xarch's source and the corpora).
3. A `base` mark no longer marks a decorator of that name, a keyword-less `decorator` mark marks the decorator bare and
   called and never a base, and Python's two marks keep today's meaning: pinned in Task 4 (three parametrised reader
   tests) and by the recorded corpora in Task 5.
4. YAML reads `frozen: True` unquoted as a boolean: the loader refuses a keyword value that is no string, so Python's
   file quotes `"True"`. Pinned in Task 4 (`a keyword value that is no string, as YAML reads True unquoted`) and by
   `test_language.py` reading the bundled marks.
5. A reader handed `special=""` makes no method special: a class with a method is no record, one with none still is.
   Pinned in Task 1 (`test_handed_no_special_pattern_only_a_class_with_no_method_can_be_a_record`).

---

### Task 1: The reader says which classes are records, handed the language's `special`

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py` (`Class`, its docstring and a field)
- Modify: `xarch/modules/rules/application/ports/source_tree.py` (`read`, `parsed`)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring, imports, `read`, `parsed`, `_parsed`,
  `_classes`, new `_record`)
- Modify: `xarch/modules/rules/application/services/holding.py:27-28,38-40`, `source_check.py:75-82`,
  `sources.py:52-53`, `examples.py:52-53,61-62`, `asking.py:26-27`, `source_reading.py`
- Modify: `tests/fakes/filesystem.py` (`FakeSourceTree`)
- Modify: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/modules/rules/adapters/test_fs_source_tree_public.py`
- Create: `tests/modules/rules/adapters/test_fs_source_tree_record.py`
- Create: `tests/modules/rules/application/test_special_handed.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Class.record: bool = False` (last field of `Class`, after `public`);
  `SourceTree.read(root, paths, table=None, immutable=(), interface=(), *, standard: frozenset[str], private: str,
  special: str) -> list[SourceFile]`; `SourceTree.parsed(text, standard, *, private: str, special: str) -> SourceFile`;
  `FakeSourceTree.specials: list[str]`.

- [ ] **Step 1: Hand the reader tests the pattern of a special name**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, after the `PRIVATE` constant and its docstring (line 39),
add:

```python
SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["special"]
"""The pattern of a special name of the language the tests' sources are written in, as its data file says it."""
HANDED = {"private": PRIVATE, "special": SPECIAL}
"""What the reader is handed of the language's tokens, as `check` hands it."""
```

Then replace every `private=PRIVATE` in the file by `**HANDED`, and the one `private=""` by `private="", special=SPECIAL`:

```bash
sed -i 's/private=PRIVATE/**HANDED/g; s/private="")/private="", special=SPECIAL)/' tests/modules/rules/adapters/test_fs_source_tree.py
grep -n 'private=' tests/modules/rules/adapters/test_fs_source_tree.py
```

Expected: the grep prints one line only, the read in `test_handed_no_prefix_the_reader_makes_every_name_public`
(`private="", special=SPECIAL`); the `HANDED` dict writes `"private": PRIVATE`, which the pattern does not match.

- [ ] **Step 2: Write the failing reader tests**

Append to `tests/modules/rules/adapters/test_fs_source_tree.py`:

```python
@pytest.mark.parametrize("text, record", [
    pytest.param("class P:\n    def __init__(self): ...\n    def __eq__(self, other): ...\n\ndef make() -> P: ...\n", True,
                 id="only special methods, returned by a top-level function"),
    pytest.param("class P:\n    x: int\n\ndef make() -> P: ...\n", True, id="no method at all, returned by a top-level function"),
    pytest.param("class P:\n    async def __aenter__(self): ...\n\nasync def make() -> P: ...\n", True,
                 id="an async special method, returned by an async top-level function"),
    pytest.param("class P:\n    pass\n\ndef find() -> P | None: ...\n", True, id="named inside a union"),
    pytest.param("class P:\n    pass\n\ndef every() -> list[P]: ...\n", True, id="named inside a subscript"),
    pytest.param("class P:\n    pass\n\ndef make() -> 'P': ...\n", True, id="named in a string annotation"),
    pytest.param("class P:\n    def size(self): ...\n\ndef make() -> P: ...\n", False, id="an ordinary method"),
    pytest.param("class P:\n    def __init__(self): ...\n\ndef make(): ...\n", False, id="returned by no function"),
    pytest.param("class P:\n    pass\n\nclass Q:\n    def make(self) -> P: ...\n", False,
                 id="returned by a method of another class only"),
    pytest.param("class P:\n    pass\n\ndef make(p: P) -> None: ...\n", False, id="named only in a parameter's annotation"),
])
def test_a_class_is_a_record_when_its_methods_are_all_special_and_a_top_level_function_returns_it(tmp_path, text, record):
    assert parsed(tmp_path, text).classes[0].record is record


def test_handed_no_special_pattern_only_a_class_with_no_method_can_be_a_record(tmp_path):
    (tmp_path / "x.py").write_text("class P:\n    def __init__(self): ...\n\nclass Q:\n    pass\n\ndef make() -> P | Q: ...\n")
    found = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, private=PRIVATE, special="")[0]
    assert {c.name: c.record for c in found.classes} == {"P": False, "Q": True}


def test_a_text_in_no_file_is_told_its_records_as_a_file_is(tmp_path):
    text = "class P:\n    def __repr__(self): ...\n\nclass Q:\n    def size(self): ...\n\ndef make() -> P | Q: ...\n"
    found = FsSourceTree(FileSystem()).parsed(text, STANDARD, **HANDED)
    assert [c.record for c in found.classes] == [c.record for c in parsed(tmp_path, text).classes] == [True, False]


def test_the_reader_must_be_handed_the_pattern_of_a_special_name(tmp_path):
    tree = FsSourceTree(FileSystem())
    with pytest.raises(TypeError):
        tree.read(tmp_path, [], standard=STANDARD, private=PRIVATE)
    with pytest.raises(TypeError):
        tree.parsed("x = 1\n", STANDARD, private=PRIVATE)
```

- [ ] **Step 3: Write the failing equality test on Python source**

Create `tests/modules/rules/adapters/test_fs_source_tree_record.py`:

```python
"""FsSourceTree on every Python file of xarch's own source (the bundled example project included) and of the recorded
corpora, each archive unpacked and never edited: each class is a record exactly when the rule the checks worked out
before the reader said it holds of it, every method's name matching the language's special pattern in full and a
function of its file's top level naming the class in its return annotation. A file that does not parse defines nothing
and is passed over."""
import re
import tarfile
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.platform.filesystem import FileSystem

PYTHON = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                        .read_text(encoding="utf-8"))
PRIVATE, SPECIAL = PYTHON["private"], PYTHON["special"]
SOURCE = Path(__file__).parents[4] / "xarch"
CORPORA = Path(__file__).parents[3] / "bootstrap" / "corpora"
ARCHIVES = ("df537ca", "7cc6111", "examples")


def read(root: Path) -> list[SourceFile]:
    """Every file below root that parses, read as `check` reads it."""
    tree = FsSourceTree(FileSystem())
    return [file for file in tree.read(root, tree.paths(root, (".py",)), standard=frozenset(), private=PRIVATE,
                                       special=SPECIAL) if file.error is None]


def unpacked(name: str, into: Path) -> Path:
    with tarfile.open(CORPORA / f"{name}.tar.xz") as archive:
        archive.extractall(into, filter="data")
    return into


def old(cls: Class, file: SourceFile) -> bool:
    """The rule the checks worked out before the reader said it: every method special, and a function of the file's
    top level naming the class in its return annotation."""
    return all(re.fullmatch(SPECIAL, method.name) for method in cls.methods) and any(
        cls.name in function.returns_named for function in file.functions if not function.owner)


def told(files: list[SourceFile]) -> list[tuple[str, bool, bool]]:
    """Each class of the files, by its file and its name, with what the reader says and what the old rule says."""
    return [(f"{file.name}:{cls.name}", cls.record, old(cls, file)) for file in files for cls in file.classes]


def broken(found: list[tuple[str, bool, bool]]) -> list[str]:
    """The classes the reader and the old rule disagree on."""
    return sorted(name for name, record, rule in found if record != rule)


def test_every_class_of_xarch_s_own_source_is_a_record_exactly_when_the_old_rule_says_it_is():
    files = read(SOURCE)
    assert files and broken(told(files)) == []


@pytest.mark.parametrize("archive", [
    pytest.param("df537ca", id="the commit df537ca, as recorded"),
    pytest.param("7cc6111", id="the commit 7cc6111, as recorded"),
    pytest.param("examples", id="the bundled examples, as recorded"),
])
def test_every_class_of_a_recorded_corpus_is_a_record_exactly_when_the_old_rule_says_it_is(tmp_path, archive):
    files = read(unpacked(archive, tmp_path))
    assert files and broken(told(files)) == []


def test_the_source_read_holds_records_and_other_classes_so_that_the_rule_is_not_held_vacuously(tmp_path):
    found = told(read(SOURCE))
    for archive in ARCHIVES:
        found += told(read(unpacked(archive, tmp_path / archive)))
    assert {record for _, record, _ in found} == {True, False}
```

In `tests/modules/rules/adapters/test_fs_source_tree_public.py`, after the `PRIVATE` constant (lines 17-18), add:

```python
SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["special"]
```

and replace the body of `read` (lines 25-28) with:

```python
def read(root: Path) -> list[SourceFile]:
    """Every file below root that parses, read as `check` reads it."""
    tree = FsSourceTree(FileSystem())
    return [file for file in tree.read(root, tree.paths(root, (".py",)), standard=frozenset(), private=PRIVATE,
                                       special=SPECIAL) if file.error is None]
```

- [ ] **Step 4: Write the failing test that every service hands `special`**

Create `tests/modules/rules/application/test_special_handed.py`:

```python
"""Use case: every service that reads the app's code hands the reader the pattern of a special name of the profile's
language, so that a class is a record or not as `check` reads it; the reading of a text for spec, which has no profile,
hands none."""
from dataclasses import replace
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.application.controller import ReaderController
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import AskHolds, CheckApp, CheckProfile, KeepFacts, ReadSources, Resemblance, Reviewed
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.profile_values.checks import APP, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

PATTERN = r"~\w+"
"""The pattern of a special name of the profile's language: not Python's, so that only the profile can have given it."""
LANGUAGE = replace(PYTHON, special=PATTERN)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"
PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []}, more={TESTS: {"kernel/test_ids.py": []}},
                          parsed=PARSED)


def test_the_check_hands_it_for_the_app_and_for_the_tests():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check_app(CheckApp(ROOT, "mine", ROOT.parent, TESTS))
    assert found.specials == [PATTERN, PATTERN]


def test_the_holds_question_hands_it_for_the_files_given_and_for_the_other_files_of_the_app():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.specials == [PATTERN, PATTERN]


def test_the_sources_read_for_a_module_that_reads_the_app_s_code_hand_it():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel/ids.py"),), Path("/src"), ROOT, "mine"))
    assert found.specials == [PATTERN]


def test_an_eval_s_facts_are_read_with_it():
    found = tree()
    evals = profile(asked={"rule": Asked("file", Scope(APP, "domain"))}, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": evals})).kept(KeepFacts("mine", "app", "rule", ((DOMAIN, "nothing"),)))
    assert found.specials == [PATTERN]


def test_the_examples_of_a_profile_s_own_checks_and_evals_are_read_with_it():
    found = tree()
    checks = {"no-managers": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                          (Saying("{name}", "rename it"),), flagged=((DOMAIN, "manager"),),
                                          clean=((DOMAIN, "nothing"),))}
    evals = {"rule": Asked("class", Scope(APP, "domain"), (), ((DOMAIN, "manager"),), ((DOMAIN, "manager"),))}
    reviewed = {"mine": Reviewed("mine", (), 2, Resemblance(False, "cli"))}
    owned = profile(written=checks, asked=evals, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": owned}, reviewed=reviewed)).check_profile(CheckProfile(Path("/p/app"), "mine"))
    assert found.specials == [PATTERN, PATTERN, PATTERN, PATTERN]


def test_a_text_read_for_spec_hands_none_since_no_profile_says_it():
    found = tree()
    reader = ReaderController(SourceReadService(found))
    reader.imports("nothing")
    reader.comments("nothing")
    assert found.specials == ["", ""]
```

- [ ] **Step 5: Run the new tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/adapters/test_fs_source_tree_record.py tests/modules/rules/adapters/test_fs_source_tree_public.py tests/modules/rules/application/test_special_handed.py`
Expected: FAIL — the adapter tests with `TypeError: FsSourceTree.read() got an unexpected keyword argument 'special'`
(every test that reads, old ones included), `test_special_handed.py` with `TypeError` from the fake or
`AttributeError: 'FakeSourceTree' object has no attribute 'specials'`.

- [ ] **Step 6: `Class.record`**

In `xarch/modules/rules/domain/parsed.py`, the last line of `Class`'s docstring

```python
    InterfaceMark); public: it is for other files to use, as the language's reader says."""
```

becomes

```python
    InterfaceMark); public: it is for other files to use, as the language's reader says; record: it is a record, as the
    language's reader says."""
```

and after `    public: bool = True` in `Class` (the field after `interface: bool = False`) add:

```python
    record: bool = False
```

- [ ] **Step 7: The port takes `special`**

In `xarch/modules/rules/application/ports/source_tree.py`, replace `read` and `parsed` with:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so. An absolute import is of the standard library when its first step is one of the modules
        `standard` holds; a relative one never is. A name is public unless it starts with `private`, how the
        language starts a private name ("": every name is public). A class is a record when every method's name
        matches `special` in full, a regular expression ("": no name is special), and a top-level function of its
        file names it in its return annotation."""
        ...
```

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str, special: str) -> SourceFile:
        """A source text of the app's language that is in no file, parsed as a file of it is, an absolute import of
        the standard library when its first step is one of the modules `standard` holds, a name public unless it
        starts with `private`, a class a record as `special` says (see read); one that does not parse holds its
        error."""
        ...
```

- [ ] **Step 8: The reader works out `record`**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

1. Imports: between `import io` and `import tokenize` add `import re`.

2. Module docstring: after the paragraph that ends `...; a mark written with keywords names no base.` (line 79) and
   before the paragraph `A class is an interface when ...`, add this paragraph (with a blank line before and after):

```text
A class is a record when the name of every method of its body matches in full the pattern of a special name the
reader is handed (the language's data file's `special`; an empty one makes no name special), and a function of the
file's top level names the class in its return annotation, as that function's returns_named holds it (inside a union,
a subscript or a string annotation too). A class with no method is one when such a function names it.
```

3. `read` and `parsed` of `FsSourceTree`:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str) -> list[SourceFile]:
```

and in its body the call

```python
            found.append(_parsed(name, path, text, table, immutable, interface, standard, private, special,
                                 _Where((root.name, *path[:-1]), root, self._fs)))
```

and

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str, special: str) -> SourceFile:
        return _parsed("", (), text, None, (), (), standard, private, special)
```

4. `_parsed` becomes:

```python
def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None, marks: tuple[RecordMark, ...],
            interface: tuple[InterfaceMark, ...], standard: frozenset[str], private: str, special: str,
            where: _Where | None = None) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=Unparsable(e.lineno or 0, e.msg))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=Unparsable(0, str(e)))
    calls = _Calls(_BUILTINS if not _star_import(tree) else frozenset(), where)
    calls.visit(tree)
    functions = _functions(tree, form, private, where)
    return SourceFile(name, path, tuple(_imports(tree, standard, private, where)), comments, functions,
                      tuple(_unions(tree)), calls=tuple(calls.found),
                      classes=tuple(_classes(tree, private, special, functions, marks, interface, where)),
                      uses=tuple(calls.uses), parameter_calls=tuple(calls.parameter_calls),
                      module_functions=_module_functions(tree), named=_named(tree), callbacks=tuple(calls.callbacks),
                      method_calls=tuple(calls.method_calls), constants=tuple(_constants(tree, private)),
                      unmentioned=_unmentioned(tree), pieces=_pieces(tree))
```

5. `_classes` becomes (its signature and the `Class(...)` call change; the rest is as today):

```python
def _classes(tree: ast.Module, private: str, special: str, functions: tuple[Function, ...],
             marks: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (),
             where: _Where | None = None) -> list[Class]:
    scope = [_scope(tree, where)]
    builtin = frozenset() if _star_import(tree) else _EXCEPTIONS - set(scope[0])
    exceptions: set[str] = set()
    found: list[Class] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = tuple(_ref(b.value if isinstance(b, ast.Subscript) else b, scope) for b in node.bases)
            methods = tuple(Method(n.lineno, n.name, _annotation(n.returns)) for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            exception = any(isinstance(b, ast.Name) and (b.id in builtin or b.id in exceptions) for b in node.bases)
            if exception:
                exceptions.add(node.name)
            declared = _declared(node)
            found.append(Class(node.lineno, node.name, bases, methods, _attributes(node), _named(node) - {node.name},
                               exception, tuple(child.target.id for child in declared),
                               tuple(_annotation(child.annotation) or "" for child in declared),
                               _immutable(node, bases, scope, marks), _interface(bases, interface),
                               not is_private_name(node.name, private),
                               record=_record(node.name, methods, functions, special)))
    return found


def _record(name: str, methods: tuple[Method, ...], functions: tuple[Function, ...], special: str) -> bool:
    """Whether the class of that name is a record: every one of its methods is named as special says, in full ("": no
    name is special), and a function of the file's top level names it in its return annotation."""
    return all(bool(special) and re.fullmatch(special, method.name) is not None for method in methods) and any(
        name in function.returns_named for function in functions if not function.owner)
```

- [ ] **Step 9: The fake takes and records `special`**

In `tests/fakes/filesystem.py`, `FakeSourceTree`: the docstring's lines

```text
    the path it points to, given in full. It records the standard modules each read and each parse is handed
    (handed), the prefix of private names each is handed (prefixes), and the endings each listing is handed (listed), in
    call order; the imports it returns are those the
    test built."""
```

become

```text
    the path it points to, given in full. It records the standard modules each read and each parse is handed
    (handed), the prefix of private names each is handed (prefixes), the pattern of a special name each is handed
    (specials), and the endings each listing is handed (listed), in call order; the imports it returns are those the
    test built."""
```

in `__init__`, after `self.prefixes: list[str] = []`, add `self.specials: list[str] = []`; and `read` and `parsed`
become:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str) -> list[SourceFile]:
        self.handed.append(standard)
        self.prefixes.append(private)
        self.specials.append(special)
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]
```

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str, special: str) -> SourceFile:
        self.handed.append(standard)
        self.prefixes.append(private)
        self.specials.append(special)
        return _source("", (), self._parsed[text])
```

- [ ] **Step 10: Every service hands `special`**

In `xarch/modules/rules/application/services/holding.py`, lines 27-28:

```python
        given = [(path, self._tree.parsed(text, profile.language.standard_modules, private=profile.language.private,
                                          special=profile.language.special))
                 for path, text in cmd.files]
```

and lines 38-40:

```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface, standard=profile.language.standard_modules,
                                     private=profile.language.private, special=profile.language.special))
```

In `source_check.py`, lines 76-82:

```python
        private, special = rules.language.private, rules.language.special
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface, standard=standard, private=private, special=special)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), table, marks, interface,
                                     standard=standard, private=private, special=special) if tests is not None else []
```

In `sources.py`, lines 52-53:

```python
        read = self._tree.read(app, [found.steps], standard=profile.language.standard_modules,
                               private=profile.language.private, special=profile.language.special)[0]
```

In `examples.py`, lines 52-53:

```python
                facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                          private=profile.language.private,
                                                          special=profile.language.special)) for path, code in files],
```

and lines 61-62:

```python
        facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                  private=profile.language.private,
                                                  special=profile.language.special)) for path, code in files],
```

In `asking.py`, lines 26-27:

```python
        parsed = [(path, self._tree.parsed(text, profile.language.standard_modules, private=profile.language.private,
                                           special=profile.language.special))
                  for path, text in cmd.files]
```

In `source_reading.py`, both calls become `self._tree.parsed(text, frozenset(), private="", special="")`, and the
class docstring becomes:

```python
    """Reads a source text of the app's language that is in no file, with the reader that reads the app's files, handed no
    standard module, no prefix of private names and no pattern of a special name: spec, which asks, has no profile."""
```

- [ ] **Step 11: Run the tests to verify they pass**

Run: `timeout 600 uv run pytest -q tests/modules/rules/adapters tests/modules/rules/application tests/architecture/test_language_seam.py`
Expected: PASS (every adapter test, the equality test over xarch's source and the three archives, the six
`test_special_handed.py` tests, the seam guard unchanged).

Run: `uv run ruff check xarch tests`
Expected: no finding.

- [ ] **Step 12: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/modules/rules/application/ports/source_tree.py \
  xarch/modules/rules/adapters/fs_source_tree.py xarch/modules/rules/application/services/holding.py \
  xarch/modules/rules/application/services/source_check.py xarch/modules/rules/application/services/sources.py \
  xarch/modules/rules/application/services/examples.py xarch/modules/rules/application/services/asking.py \
  xarch/modules/rules/application/services/source_reading.py tests/fakes/filesystem.py \
  tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/adapters/test_fs_source_tree_public.py \
  tests/modules/rules/adapters/test_fs_source_tree_record.py tests/modules/rules/application/test_special_handed.py
git commit -F - <<'MSG'
The reader says whether each class is a record, Class.record, from the pattern of a special name it is now handed as a required keyword beside private, Python's rule exactly: every method special and a top-level function of the file naming the class in its return annotation; every service hands it the language's special, and spec's reading of a text hands none

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 2: The fact `class.record`, which Python supplies

**Files:**
- Modify: `xarch/profile_values/capabilities.py` (`FACTS`, after `public`)
- Modify: `xarch/architectures/presets/language/python.yaml` (`supplies`, after `class.interface: exact`)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `FACTS["class.record"]`, the fact Task 3's vocabulary and `NEEDS` name; Python's `supplies` holds
  `Supply("class.record", "exact")`.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/application/logic/test_profile_needs.py`, after `test_public_is_a_fact_after_comment_doc`, add:

```python
def test_class_record_is_a_fact_after_public():
    facts = list(FACTS)
    assert facts[facts.index("public") + 1] == "class.record"
    assert FACTS["class.record"] == "whether a class is a record, as the language writes one"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py -k "class_record or python_supplies"`
Expected: `test_class_record_is_a_fact_after_public` FAILS (`assert 'function' == 'class.record'`);
`test_python_supplies_every_fact_a_bundled_check_reads` passes.

- [ ] **Step 3: Add the fact**

In `xarch/profile_values/capabilities.py`, right after the two lines of the `"public"` entry (`"public": "whether a
name a file defines, ...` / `"decides it",`), add:

```python
    "class.record": "whether a class is a record, as the language writes one",
```

- [ ] **Step 4: Run the tests: the fact passes, Python now falls short**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py -k "class_record or python_supplies"`
Expected: `test_class_record_is_a_fact_after_public` PASSES; `test_python_supplies_every_fact_a_bundled_check_reads`
FAILS (the dict lacks `'class.record': 'exact'`).

- [ ] **Step 5: Python supplies it**

In `xarch/architectures/presets/language/python.yaml`, after the line `  class.interface: exact` add:

```yaml
  class.record: exact
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `timeout 600 uv run pytest -q tests/modules/spec tests/profile_values tests/modules/rules/domain`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml \
  tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'MSG'
The fact class.record, whether a class is a record as the language writes one, follows public in FACTS; Python supplies it exactly

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 3: The engine reads `class.record`, and `holds` needs it

**Files:**
- Modify: `xarch/modules/rules/application/logic/facts.py` (docstring lines 52-53, `case "class"`, `_class`)
- Modify: `xarch/modules/rules/domain/vocabulary.py:235` (`field_needs["record"]`), `:288-289` (filter `record`)
- Modify: `xarch/modules/spec/domain/key_table.py:199` (`NEEDS["parts.<part>.holds"]`)
- Modify: `tests/modules/rules/builders.py` (`read_as`, new `_record`, import `Class`)
- Modify: `tests/modules/rules/application/test_holds.py:23-24` (the `"record"` file)
- Test: `tests/modules/rules/application/logic/test_facts.py`, `tests/modules/rules/application/logic/test_holds.py`,
  `tests/modules/rules/domain/test_vocabulary.py`, `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: `Class.record` (Task 1), `FACTS["class.record"]` (Task 2).
- Produces: the class fact's trait `record` set exactly when `cls.record`; `_class(cls: Class, read: Read,
  defined: Defined, ports: dict[str, Class]) -> frozenset[str]`; builders `read_as(file, language)` setting `record`.

- [ ] **Step 1: Write the failing engine and builder tests**

In `tests/modules/rules/application/logic/test_facts.py`, change the builders import to

```python
from tests.modules.rules.builders import BRACE, PERCENT, PROFILE, imp, in_tests, profile, source
```

and after `test_a_class_the_reader_says_is_an_immutable_record_carries_it` add:

```python
def test_the_trait_record_follows_what_the_reader_says_alone():
    classes = (Class(1, "Said", methods=(Method(2, "size", None),), record=True),
               Class(4, "Unsaid", methods=(Method(5, "__repr__", "str"),)))
    file = SourceFile("app/modules/docs/domain/a.py", ("modules", "docs", "domain", "a.py"), (), classes=classes,
                      functions=(Function(8, "make", returns_named=frozenset({"Unsaid"})),))
    read = facts_of([file], [], PROFILE, "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"record", "public"}), frozenset({"public"})]


def test_under_brace_a_class_the_reader_says_is_a_record_is_one_with_no_method_list_and_no_function_naming_it():
    file = source("modules/docs/domain/point.ts", classes=(Class(1, "Point", record=True), Class(2, "Shape")),
                  language=BRACE)
    read = facts_of([file], [], profile(language=BRACE), "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"record", "public"}), frozenset({"public"})]


def test_under_percent_a_class_of_special_methods_a_top_level_function_returns_is_no_record_unless_the_reader_says():
    file = source("modules/docs/domain/point.cls", classes=(Class(1, "Point", methods=(Method(2, "%OnNew", None),)),),
                  functions=(Function(4, "Make", returns_named=frozenset({"Point"})),), language=PERCENT)
    read = facts_of([file], [], profile(language=PERCENT), "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"public"})]


def test_a_file_built_under_python_has_its_records_read_as_python_s_reader_would_and_one_given_stays_one():
    file = source("modules/docs/domain/a.py", classes=(Class(1, "Shown", methods=(Method(2, "__repr__", "str"),)),
                                                       Class(4, "Loose"),
                                                       Class(5, "Given", methods=(Method(6, "size", None),), record=True)),
                  functions=(Function(8, "make", returns_named=frozenset({"Shown"})),
                             Function(9, "build", owner="Given", returns_named=frozenset({"Loose"}))))
    assert [c.record for c in file.classes] == [True, False, True]


def test_a_file_built_under_another_language_keeps_its_records_as_given():
    file = source("modules/docs/domain/a.ts", classes=(Class(1, "Shown"), Class(2, "Given", record=True)),
                  functions=(Function(8, "make", returns_named=frozenset({"Shown"})),), language=BRACE)
    assert [c.record for c in file.classes] == [False, True]
```

In `tests/modules/rules/application/logic/test_holds.py`, append:

```python
@pytest.mark.parametrize("record, expected", [
    pytest.param(True, [], id="a class the reader says is a record"),
    pytest.param(False, ["Point"], id="the same class, said to be none"),
])
def test_under_brace_the_reader_alone_says_which_classes_are_records(record, expected):
    braced = profile(holds={"logic": "functions"}, language=BRACE)
    file = source("modules/docs/application/logic/point.ts", classes=(Class(3, "Point", record=record),), language=BRACE)
    assert [w.message.split(" ")[0] for w in weak([file], braced, "app")] == expected


@pytest.mark.parametrize("immutable, expected", [
    pytest.param(True, [], id="a class the reader says is an immutable record"),
    pytest.param(False, ["immutable"], id="one it says is not"),
])
def test_under_brace_the_reader_alone_says_which_classes_are_immutable_records(immutable, expected):
    braced = profile(immutable=("logic",), language=BRACE)
    file = source("modules/docs/application/logic/point.ts", classes=(Class(3, "Point", immutable=immutable),),
                  language=BRACE)
    assert [w.rule for w in weak([file], braced, "app")] == expected
```

In `tests/modules/rules/domain/test_vocabulary.py`, after
`test_the_interface_of_a_class_needs_the_reader_to_mark_interfaces_and_says_no_word_of_bases`, add:

```python
def test_whether_a_class_is_a_record_needs_the_reader_to_say_it():
    kind = next(kind for kind in KINDS if kind.name == "class")
    record = next(word for word in FILTERS if word.name == "record")
    assert (kind.field_needs["record"], record.meaning) == (
        ("class.record",), "the class is a record, as the language's reader decides")
```

In `tests/modules/spec/application/logic/test_profile_needs.py`, at the end of the file, add:

```python
UNRECORDED = replace(PYTHON, name="unrecorded", checked=replace(
    PYTHON.checked, title="Unrecorded", supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "class.record")))
"""A language whose reader supplies every fact but class.record: it does not say which classes are records."""


def test_a_part_that_holds_is_refused_under_a_language_whose_reader_does_not_say_which_classes_are_records():
    document = layered(language="unrecorded")
    document["parts"]["service"] |= {"holds": "functions"}
    assert problems(document, languages={"unrecorded": UNRECORDED}) == [
        "layered.yaml: parts.service.holds: its check reads class.record (whether a class is a record, as the language "
        "writes one), which the language unrecorded does not supply: drop parts.service.holds, or check the app with a "
        "language whose reader supplies class.record"]
    said = replace(UNRECORDED, checked=replace(UNRECORDED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"unrecorded": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "class.record" in key.needs) == ["parts.<part>.holds"]
```

(`layered`, `problems`, `parsed`, `KEYS`, `PYTHON`, `Supply`, `EXACT`, `FACTS` and `replace` are already imported
there.)

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_holds.py tests/modules/rules/domain/test_vocabulary.py tests/modules/spec/application/logic/test_profile_needs.py`
Expected: FAIL —
`test_the_trait_record_follows_what_the_reader_says_alone` (traits swapped: the engine computes it),
`test_under_brace_a_class_the_reader_says_is_a_record_...` (`Point` lacks `record`),
`test_under_percent_...` (`Point` carries `record`),
`test_a_file_built_under_python_...` (`[False, False, True]`),
`test_under_brace_the_reader_alone_says_which_classes_are_records[a class the reader says is a record]` (`['Point']`),
`test_whether_a_class_is_a_record_needs_the_reader_to_say_it`,
`test_a_part_that_holds_is_refused_...` (`DID NOT RAISE InvalidArchitecture`).
`test_a_file_built_under_another_language_keeps_its_records_as_given` and the immutable BRACE test pass already.

- [ ] **Step 3: The engine reads the fact**

In `xarch/modules/rules/application/logic/facts.py`:

the docstring lines

```text
    record              a class with no method but the language's special methods (its data file says how they are
                        named) that a top-level function of its file names in its return annotation
```

become

```text
    record              a class the language's reader says is a record
```

in `_facts`, `case "class":` becomes

```python
        case "class":
            ports = {c.name: c for c in file.classes if c.interface}
            return tuple(Fact("class", c.line, (c.name,), c.name, _class(c, read, defined, ports), names=c.named)
                         for c in file.classes)
```

and `_class` becomes

```python
def _class(cls: Class, read: Read, defined: Defined, ports: dict[str, Class]) -> frozenset[str]:
    exception = (read.steps, cls.name) in defined.exceptions and not read.in_tests
    return frozenset(n for n, on in (("exception", exception), ("record", cls.record),
                                     ("interface", ports.get(cls.name) is cls), ("immutable", cls.immutable),
                                     ("public", cls.public)) if on)
```

In `xarch/modules/rules/domain/vocabulary.py`, in the `class` kind's `field_needs`, the line

```python
                                        "record": ("class.methods", "function.returns"),
```

becomes

```python
                                        "record": ("class.record",),
```

and the filter

```python
    Filter("record", "the class is a record: no method but the language's special ones, and a top-level function of "
                     "its file names it in its return annotation", FACT, ("record",)),
```

becomes

```python
    Filter("record", "the class is a record, as the language's reader decides", FACT, ("record",)),
```

In `xarch/modules/spec/domain/key_table.py`, the line

```python
    "parts.<part>.holds": ("class", "class.methods", "class.exception", "function", "function.returns", "public"),
```

becomes

```python
    "parts.<part>.holds": ("class", "class.exception", "class.record", "function", "public"),
```

- [ ] **Step 4: The builders read a hand-built Python file's records as Python's reader would**

In `tests/modules/rules/builders.py`, the import

```python
from xarch.modules.rules.domain.parsed import SourceFile
```

becomes

```python
from xarch.modules.rules.domain.parsed import Class, SourceFile
```

and `read_as` becomes, with a helper before it:

```python
def _record(cls: Class, file: SourceFile, language: CheckedLanguage) -> bool:
    return cls.record or (language.title == PYTHON.title and all(language.is_special(m.name) for m in cls.methods)
                          and any(cls.name in f.returns_named for f in file.functions if not f.owner))


def read_as(file: SourceFile, language: CheckedLanguage) -> SourceFile:
    """The file with each class, function and constant whose name starts as a private name of language does made not
    public, as its reader would say, one given as not public staying so; and, under Python, each class its reader would
    call a record made one (every method special by language's pattern, and a function of the file's top level naming
    it in its return annotation), one given as a record staying so. Under another language a class is a record only as
    given."""
    return replace(file, classes=tuple(replace(c, public=_public(c.name, c.public, language),
                                               record=_record(c, file, language)) for c in file.classes),
                   functions=tuple(replace(f, public=_public(f.name, f.public, language)) for f in file.functions),
                   constants=tuple(replace(c, public=_public(c.name, c.public, language)) for c in file.constants))
```

In `tests/modules/rules/application/test_holds.py`, the `"record"` entry of `PARSED`

```python
    "record": SourceFile("", (), (), classes=(Class(1, "Found"),),
                         functions=(Function(3, "found", returns_named=frozenset({"Found"})),)),
```

becomes

```python
    "record": SourceFile("", (), (), classes=(Class(1, "Found", record=True),),
                         functions=(Function(3, "found", returns_named=frozenset({"Found"})),)),
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules tests/cli tests/architecture tests/bootstrap/test_needs_agree.py`
Expected: PASS — the new tests, every existing hand-built test of `holds`, filters, facts and expansion unchanged,
`test_needs_agree.py` (what `holds` says it needs is what its rules read: `class`, `class.exception`, `class.record`,
`function`, `public`), and `tests/architecture/test_self_check.py` (xarch's own records come from the reader).
If `test_needs_agree.py` names a fact on either side, the `NEEDS` entry is what it says: change the entry, not the test.

Run: `grep -n "is_special\|returns_named" xarch/modules/rules/application/logic/facts.py`
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/application/logic/facts.py xarch/modules/rules/domain/vocabulary.py \
  xarch/modules/spec/domain/key_table.py tests/modules/rules/builders.py tests/modules/rules/application/test_holds.py \
  tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_holds.py \
  tests/modules/rules/domain/test_vocabulary.py tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'MSG'
The class fact carries the trait record when the reader says the class is a record, and no longer works it out from special methods and return annotations, so that the filter record and parts.<part>.holds need class.record in place of class.methods and function.returns; the test builders read a hand-built file's records as Python's reader would

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 4: Immutable marks as maps of four forms

**Files:**
- Modify: `xarch/profile_values/language.py` (`RecordMark`)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring lines 49-50, constants `_CALLED`,
  `_VALUE` removed, new `IMMUTABLE`, `RECORD_FORMS`, `_marks`, `_mark` replaced by `_record_mark`)
- Modify: `xarch/architectures/presets/language/python.yaml` (header lines 25-27, `immutable:` line 52)
- Modify: `tests/fakes/languages/brace.yaml` (header, a key), `tests/fakes/languages/percent.yaml:19`
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring paragraph on immutable records,
  `_immutable`)
- Modify: `tests/modules/rules/builders.py` (`records_of`, `_record_mark`, `PYTHON`, `BRACE`)
- Test: `tests/modules/spec/application/logic/test_language_file.py`, `tests/modules/spec/application/test_language.py`,
  `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/modules/rules/application/logic/test_holds.py`

**Interfaces:**
- Consumes: nothing from Tasks 1-3 but the files they leave.
- Produces: `RecordMark(base=(), decorator=(), keywords=(), fields="", type=())`;
  `language_file.IMMUTABLE: str`; builders `records_of(file: dict) -> tuple[RecordMark, ...]`.

- [ ] **Step 1: Write the failing loader tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

1. `PERCENT`'s `"immutable"` entry (line 27) becomes

```python
           "immutable": [{"base": "%SerialObject"}, {"decorator": "%Lib.Rec", "keywords": {"frozen": "yes"}}]}
```

2. After the `INTERFACE` constant (line 29) add:

```python
IMMUTABLE = "immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}"
```

3. In `test_a_token_that_is_not_what_its_key_takes_is_a_problem`'s table, delete the three rows whose given is an
   `"immutable"` (ids `marks of an immutable record not a list`, `a keyword with no value`, `a keyword that is no name
   of the language`).

4. Replace `test_what_makes_a_class_an_immutable_record_is_read_as_an_outside_name_and_the_keywords_a_decorator_is_called_with`
   with:

```python
def test_what_makes_a_class_an_immutable_record_is_read_as_marks_of_four_forms_in_the_order_written():
    marks = [{"base": "pkg.Record"}, {"decorator": "pkg.record", "keywords": {"frozen": "yes", "slots": "no"}},
             {"decorator": "pkg.record"}, {"fields": "readonly"}, {"type": "pkg.Frozen"}]
    assert language_of("pascal", DOCUMENT | {"immutable": marks}).checked.immutable == (
        RecordMark(base=("pkg", "Record")),
        RecordMark(decorator=("pkg", "record"), keywords=(("frozen", "yes"), ("slots", "no"))),
        RecordMark(decorator=("pkg", "record")), RecordMark(fields="readonly"), RecordMark(type=("pkg", "Frozen")))
    assert language_of("pascal", DOCUMENT).checked.immutable == ()


@pytest.mark.parametrize("immutable", [
    pytest.param({"base": "pkg.Record"}, id="no list"),
    pytest.param(["pkg.Record"], id="the old shape, an outside name as a string"),
    pytest.param(["pkg.record(frozen=yes)"], id="the old shape, a decorator and its keywords as a string"),
    pytest.param([{"base": "pkg.Record", "type": "pkg.Frozen"}], id="two forms"),
    pytest.param([{"base": "pkg.Record", "keywords": {"frozen": "yes"}}], id="keywords beside a base"),
    pytest.param([{"keywords": {"frozen": "yes"}}], id="keywords alone"),
    pytest.param([{"kind": "pkg.Record"}], id="an unknown key"),
    pytest.param([{"decorator": "pkg.record", "frozen": "yes"}], id="an unknown key beside a form"),
    pytest.param([{"decorator": "pkg.record", "keywords": {}}], id="empty keywords"),
    pytest.param([{"decorator": "pkg.record", "keywords": ["frozen"]}], id="keywords that are no map"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"frozen": True}}],
                 id="a keyword value that is no string, as YAML reads True unquoted"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"frozen": ""}}], id="an empty keyword value"),
    pytest.param([{"decorator": "pkg.record", "keywords": {"2x": "yes"}}], id="a keyword that is no name of the language"),
    pytest.param([{"base": "not a name!"}], id="a base that is no outside name"),
    pytest.param([{"type": 3}], id="a type that is no text"),
    pytest.param([{"fields": "pkg.readonly"}], id="a fields word holding the member"),
    pytest.param([{"fields": "two words"}], id="a fields word with a space"),
    pytest.param([{"base": "pkg.Record"}, "pkg.Other", {"kind": "x"}], id="said once however many marks are wrong"),
])
def test_a_mark_of_an_immutable_record_of_no_form_is_refused_once(immutable):
    assert refused(DOCUMENT | {"immutable": immutable}) == [IMMUTABLE]


def test_the_marks_of_an_immutable_record_are_not_read_when_the_keys_that_say_how_a_name_is_written_are_refused():
    assert [p.split(":")[0] for p in refused(DOCUMENT | {"package": "[a-", "immutable": ["pkg.Record"]})] == ["package"]
```

5. In `test_the_lists_of_a_language_are_read_by_its_own_patterns`, the expected marks

```python
        (RecordMark(("%SerialObject",)), RecordMark(("%Lib", "Rec"), (("frozen", "yes"),))))
```

become

```python
        (RecordMark(base=("%SerialObject",)), RecordMark(decorator=("%Lib", "Rec"), keywords=(("frozen", "yes"),))))
```

6. In `test_the_same_lists_are_refused_under_patterns_that_do_not_allow_them`, the expected list becomes:

```python
    assert [p.removeprefix("presets/language/odd.yaml: ") for p in caught.value.problems] == [
        INTERFACE, "dynamic: '%SYSTEM.OBJ.Load' is not an outside name such as <package>.<name>", IMMUTABLE]
```

7. In `test_the_percent_test_only_language_reads_its_lists_by_its_own_patterns`, `(RecordMark(("%SerialObject",)),)`
   becomes `(RecordMark(base=("%SerialObject",)),)`.

8. After `test_the_brace_test_only_language_marks_an_interface_by_its_keyword` add:

```python
def test_the_brace_test_only_language_marks_an_immutable_record_by_a_keyword_on_every_field():
    path = next(path for path in TEST_LANGUAGES if path.stem == "brace")
    checked = language_of("brace", yaml.safe_load(path.read_text(encoding="utf-8"))).checked
    assert checked.immutable == (RecordMark(fields="readonly"),)
```

In `tests/modules/spec/application/test_language.py`, in
`test_the_bundled_language_gives_its_package_pattern_and_its_member_and_reads_its_lists_as_before`, the line

```python
        (RecordMark(("typing", "NamedTuple")), RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
```

becomes

```python
        (RecordMark(base=("typing", "NamedTuple")),
         RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),))),
```

- [ ] **Step 2: Write the failing reader tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, replace `MARKS` and
`test_a_class_is_an_immutable_record_when_a_mark_names_one_of_its_bases_or_its_decorators` (lines 235-256) with:

```python
MARKS = (RecordMark(base=("typing", "NamedTuple")),
         RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),)))
"""The marks of an immutable record the language's data file writes, as its loader reads them."""


def immutable_of(tmp_path: Path, text: str, marks: tuple[RecordMark, ...]) -> bool:
    (tmp_path / "a.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], immutable=marks, standard=STANDARD,
                                           **HANDED)[0].classes[0].immutable


@pytest.mark.parametrize("text, immutable", [
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=True, order=True)\nclass A:\n    x: int\n", True,
                 id="a decorator a mark names, called with its keyword among others"),
    pytest.param("import dataclasses\n@dataclasses.dataclass(frozen=True)\nclass A:\n    x: int\n", True,
                 id="the decorator read through the import that binds it"),
    pytest.param("import dataclasses\n@dataclasses.dataclass(frozen=True, slots=True)\nclass A:\n    x: int\n", True,
                 id="through the module, with another keyword"),
    pytest.param("from dataclasses import dataclass\n@dataclass\nclass A:\n    x: int\n", False,
                 id="the decorator of a mark, bare"),
    pytest.param("from dataclasses import dataclass\n@dataclass()\nclass A:\n    x: int\n", False,
                 id="the decorator of a mark, called without its keyword"),
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=False)\nclass A:\n    x: int\n", False,
                 id="its keyword with another value"),
    pytest.param("from typing import NamedTuple\nclass A(NamedTuple):\n    x: int\n", True, id="a base a mark names"),
    pytest.param("import typing\nclass A(typing.NamedTuple):\n    x: int\n", True, id="the base read through the module"),
    pytest.param("from typing import NamedTuple\n@NamedTuple\nclass A:\n    x: int\n", False,
                 id="a decorator a base mark names"),
    pytest.param("from dataclasses import dataclass\nclass A(dataclass):\n    x: int\n", False,
                 id="a base a decorator mark names"),
    pytest.param("def dataclass(**k): ...\n@dataclass(frozen=True)\nclass A:\n    x: int\n", False,
                 id="a decorator no import binds"),
])
def test_a_class_is_an_immutable_record_when_a_base_mark_names_a_base_or_a_decorator_mark_a_decorator(tmp_path, text,
                                                                                                    immutable):
    assert immutable_of(tmp_path, text, MARKS) is immutable


@pytest.mark.parametrize("text, immutable", [
    pytest.param("from dataclasses import dataclass\n@dataclass\nclass A:\n    x: int\n", True, id="the decorator bare"),
    pytest.param("from dataclasses import dataclass\n@dataclass()\nclass A:\n    x: int\n", True, id="the decorator called"),
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=True)\nclass A:\n    x: int\n", True,
                 id="the decorator called with keywords"),
    pytest.param("from dataclasses import dataclass\nclass A(dataclass):\n    x: int\n", False, id="a base of that name"),
])
def test_a_decorator_mark_with_no_keywords_marks_the_decorator_however_it_is_written_and_no_base(tmp_path, text, immutable):
    assert immutable_of(tmp_path, text, (RecordMark(decorator=("dataclasses", "dataclass")),)) is immutable


@pytest.mark.parametrize("text", [
    pytest.param("from typing import Final\nclass A(Final):\n    readonly: int\n", id="a base named as a type mark"),
    pytest.param("from typing import Final\n@Final\nclass A:\n    readonly: int\n", id="a decorator named as a type mark"),
])
def test_a_fields_or_a_type_mark_marks_no_class_of_this_language(tmp_path, text):
    assert immutable_of(tmp_path, text, (RecordMark(fields="readonly"), RecordMark(type=("typing", "Final")))) is False
```

(`test_no_class_is_an_immutable_record_when_the_reader_is_given_no_mark`, right after, stays.)

In `tests/modules/rules/application/logic/test_holds.py`, at the top of
`test_under_brace_the_reader_alone_says_which_classes_are_immutable_records` (from Task 3), add as its first line:

```python
    assert BRACE.immutable == (RecordMark(fields="readonly"),)
```

and add `from xarch.profile_values.language import RecordMark` to the file's imports (after the `published` import).

- [ ] **Step 3: Run them to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/logic/test_holds.py`
Expected: FAIL — `TypeError: RecordMark.__init__() got an unexpected keyword argument 'base'` (and `'decorator'`,
`'fields'`) wherever the new form is built, at collection of the adapter test file, and the loader tests refusing
the maps with the old texts.

- [ ] **Step 4: `RecordMark` in four forms**

In `xarch/profile_values/language.py`, `RecordMark` becomes:

```python
@dataclass(frozen=True)
class RecordMark:
    """What makes a class an immutable record in the language, in one of four forms, exactly one of base, decorator,
    fields and type given: an outside name among its bases (base, as its steps); a decorator (decorator, as its steps)
    called with each keyword of keywords, each (name, value as written) (none: however it is written, bare or called);
    a keyword that marks every field (fields); or a wrapper type (type, as its steps)."""
    base: tuple[str, ...] = ()
    decorator: tuple[str, ...] = ()
    keywords: tuple[tuple[str, str], ...] = ()
    fields: str = ""
    type: tuple[str, ...] = ()
```

- [ ] **Step 5: The loader reads maps and refuses anything else once**

In `xarch/modules/spec/application/logic/language_file.py`:

1. The module docstring's `immutable` entry

```text
    immutable      what makes a class an immutable record: each an outside name among its bases or its decorators,
                   a decorator's written with the keywords it must be called with, `name(key=value, ...)`
```

becomes

```text
    immutable      the marks of an immutable record, each {base: <outside name>}, an outside name among a class's
                   bases; {decorator: <outside name>, keywords: {<name>: <value>, ...}}, a decorator called with each
                   keyword given, its value as written, a non-empty string (keywords left out: however it is
                   written); {fields: <word>}, a keyword that marks every field, a name; or {type: <outside name>},
                   a wrapper type
```

2. Delete the two lines

```python
_CALLED = re.compile(r"(?P<path>[^()]+)(?:\((?P<keywords>[^()]*)\))?")
_VALUE = re.compile(r"[^,()=]+")
```

and after the `INTERFACE` constant and its docstring add:

```python
IMMUTABLE = "immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}"
"""What the loader says of a value of `immutable` that is not a list of marks, once for the key."""
RECORD_FORMS = ("base", "decorator", "fields", "type")
"""The keys of a mark of an immutable record, exactly one of them in each; `keywords` may stand beside `decorator`."""
```

3. Replace `_marks` and `_mark` with:

```python
def _marks(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
           namespace: str) -> tuple[RecordMark, ...]:
    """The marks of an immutable record, in the order written; one problem for the key when it is no list or any item
    is no mark; none read when the keys that say how an outside name is written are refused already (joins None)."""
    if "immutable" not in document or joins is None:
        return ()
    value = document["immutable"]
    items = value if isinstance(value, list) else None
    found = tuple(mark for mark in (_record_mark(item, joins, namespace) for item in items or ()) if mark is not None)
    if items is None or len(found) != len(items):
        problems.append(IMMUTABLE)
        return ()
    return found


def _record_mark(item: Any, joins: tuple[str, str, str], namespace: str) -> RecordMark | None:
    """One mark: a map of exactly one of RECORD_FORMS, `keywords` beside `decorator` alone; base, decorator and type
    an outside name, fields a name of the language holding no space, each keyword a name of the language with a
    non-empty string; None when the item is none of them."""
    if not isinstance(item, Mapping):
        return None
    forms = [key for key in item if key in RECORD_FORMS]
    if len(forms) != 1 or set(item) - {*forms, *(("keywords",) if forms == ["decorator"] else ())}:
        return None
    (form,) = forms
    value = item[form]
    if not isinstance(value, str):
        return None
    names, package, member = joins
    if form == "fields":
        return RecordMark(fields=value) if _MEMBER.fullmatch(value) and is_name(value, names) else None
    path = outside_name(value, names, package, member, namespace)
    if path is None:
        return None
    if form == "base":
        return RecordMark(base=path)
    if form == "type":
        return RecordMark(type=path)
    if "keywords" not in item:
        return RecordMark(decorator=path)
    keywords = item["keywords"]
    if not (isinstance(keywords, Mapping) and keywords and all(
            isinstance(key, str) and is_name(key, names) and isinstance(word, str) and word.strip()
            for key, word in keywords.items())):
        return None
    return RecordMark(decorator=path, keywords=tuple(keywords.items()))
```

Run: `grep -n "_CALLED\|_VALUE\|_mark(" xarch/modules/spec/application/logic/language_file.py`
Expected: only `_interface_mark(` and `_record_mark(` lines.

- [ ] **Step 6: The data files write maps**

In `xarch/architectures/presets/language/python.yaml`, the header lines

```text
# immutable, what makes a class an immutable record: a dotted name among its bases or its decorators, a decorator
# called with each keyword written after it, as written; importing, how a file imports a name from another file of the
# app, {dotted} standing for that file's dotted path and {name} for the name.
```

become

```text
# immutable, the marks of an immutable record, each in one of four forms: {base: <outside name>}, a name among its
# bases; {decorator: <outside name>, keywords: {<name>: <value>}}, a decorator called with each keyword given, its
# value as written and quoted so that it stays text (keywords left out: however it is written); {fields: <word>}, a
# keyword that marks every field; or {type: <outside name>}, a wrapper type. Python writes the first two. importing,
# how a file imports a name from another file of the app, {dotted} standing for that file's dotted path and {name} for
# the name.
```

and the line

```yaml
immutable: [typing.NamedTuple, "dataclasses.dataclass(frozen=True)"]
```

becomes

```yaml
immutable: [{base: typing.NamedTuple}, {decorator: dataclasses.dataclass, keywords: {frozen: "True"}}]
```

In `tests/fakes/languages/brace.yaml`, the header lines 7-9

```text
# directives after the marker of any of them. It gives no private: its names are public or not as its reader says, by
# an export, never by a prefix. The tests load it to show that the profile and the checks read outside names and
# comments by a language's own patterns; later steps add their keys to it.
```

become

```text
# directives after the marker of any of them. It gives no private: its names are public or not as its reader says, by
# an export, never by a prefix. Its immutable records are marked by a keyword on every field, readonly. The tests load
# it to show that the profile and the checks read outside names and comments by a language's own patterns; later steps
# add their keys to it.
```

and after the line `interface: [{keyword: interface}]` add:

```yaml
immutable: [{fields: readonly}]
```

In `tests/fakes/languages/percent.yaml`, line 19 `immutable: ["%SerialObject"]` becomes:

```yaml
immutable: [{base: "%SerialObject"}]
```

- [ ] **Step 7: The builders carry the marks as the loader reads them**

In `tests/modules/rules/builders.py`, after `forms_of`, add:

```python
def records_of(file: dict) -> tuple[RecordMark, ...]:
    """The marks of an immutable record a language's data file writes, as its loader reads them: a base, a decorator
    or a type split at the file's member, a decorator's keywords in the order written, a fields word whole."""
    return tuple(_record_mark(mark, file["member"]) for mark in file.get("immutable", ()))


def _record_mark(mark: dict, member: str) -> RecordMark:
    if "base" in mark:
        return RecordMark(base=outside_steps(mark["base"], member))
    if "decorator" in mark:
        return RecordMark(decorator=outside_steps(mark["decorator"], member),
                          keywords=tuple(mark.get("keywords", {}).items()))
    if "type" in mark:
        return RecordMark(type=outside_steps(mark["type"], member))
    return RecordMark(fields=mark["fields"])
```

In `PYTHON`, the argument

```python
                         immutable=(RecordMark(("typing", "NamedTuple")),
                                    RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
```

becomes

```python
                         immutable=(RecordMark(base=("typing", "NamedTuple")),
                                    RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),))),
```

In `BRACE`, after `interface=marks_of(BRACE_FILE),` add `immutable=records_of(BRACE_FILE),`, so that the line reads:

```python
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
                        immutable=records_of(BRACE_FILE),
```

and the docstring after `BRACE` becomes:

```python
"""The TypeScript-like test-only language as a check reads it, its endings, package files, patterns, member, interface
marks, marks of an immutable record, annotations of no value, comment forms, directives and standard modules read from
its data file."""
```

- [ ] **Step 8: The reader reads `base` and `decorator` marks**

In `xarch/modules/rules/adapters/fs_source_tree.py`, the module docstring paragraph

```text
A class is an immutable record when a mark it is given (the language's data file's `immutable`) names one of its bases,
or one of its decorators, by the dotted path its name reaches (read as a call's callee is), called with each keyword
the mark is written with, its value as written (`ast.unparse`); a mark written with keywords names no base.
```

becomes

```text
A class is an immutable record when a mark it is given (the language's data file's `immutable`) is a base mark whose
path is one of its bases (a subscripted base by what it subscripts, an alias by the path it reaches), or a decorator
mark whose path is that of one of its decorators (read as a call's callee is), called with each keyword the mark
gives, its value as written (`ast.unparse`); a decorator mark with no keywords marks the decorator bare or called. A
fields or a type mark marks no class: Python marks none by a keyword on its fields or by a wrapper type.
```

and `_immutable` becomes:

```python
def _immutable(node: ast.ClassDef, bases: tuple[Ref, ...], scope: list[Scope], marks: tuple[RecordMark, ...]) -> bool:
    """Whether a base mark names one of the class's bases, or a decorator mark one of its decorators called with each
    keyword of the mark; a fields or a type mark names neither, since Python marks no class so."""
    for decorator in node.decorator_list:
        called = isinstance(decorator, ast.Call)
        path = _ref(decorator.func if called else decorator, scope)
        given = {(k.arg, ast.unparse(k.value)) for k in decorator.keywords if k.arg} if called else set()
        if any(mark.decorator and mark.decorator == path and set(mark.keywords) <= given for mark in marks):
            return True
    return any(mark.base and mark.base in bases for mark in marks)
```

- [ ] **Step 9: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules tests/profile_values tests/architecture tests/cli`
Expected: PASS (the loader's four forms and refusals, the bundled and test-only data files, the reader's mark
tests, the BRACE marks, the seam guard unchanged).

Run: `grep -rn "RecordMark((" xarch tests --include=*.py; grep -rn "mark.path" xarch`
Expected: no output.

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_recorded_app.py`
Expected: PASS — no recorded finding moves with Python's marks as maps.

- [ ] **Step 10: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml \
  xarch/modules/rules/adapters/fs_source_tree.py tests/modules/rules/builders.py \
  tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_language.py \
  tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/logic/test_holds.py
git commit -F - <<'MSG'
A language's data file writes what makes a class an immutable record as marks of four forms, {base}, {decorator, keywords}, {fields} or {type}, as interface marks are, and anything else is refused once for the key; Python writes a base and a decorator called with frozen "True", its reader reads those two forms only where each belongs, and the test-only languages write a fields mark and a base mark

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 5: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md` (the language paragraph's `immutable` clause, lines 156-157 at `1c2008d`)
- Modify: `CHANGELOG.md` (`[Unreleased]`: first bullet of `### Added`, first bullet of `### Changed`)
- Throwaway, never committed: `/tmp/xarch-3-10/regenerate_docs.py`

**Interfaces:**
- Consumes: everything above.
- Produces: nothing.

- [ ] **Step 1: The README says the marks as maps and the record as the reader's**

In `README.md`, replace

```markdown
(`branching_expressions`), and what makes a class an immutable record (`immutable`: a base, or a decorator called with
its keywords, such as `dataclasses.dataclass(frozen=True)`).
```

with exactly

```markdown
(`branching_expressions`), and what makes a class an immutable record (`immutable`: marks, each `{base}`,
`{decorator, keywords}`, `{fields}` or `{type}`, such as `{decorator: dataclasses.dataclass, keywords: {frozen:
"True"}}`). Whether a class is a record, a type that only holds data, the reader says: the fact `class.record` a
reader supplies, which `holds` and the filter `record` read.
```

(the line after, `The rest of what a check knows of the language is one adapter, ...`, stays.)

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 2: The CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, insert as the first bullet of `### Added` (before `- The fact
\`public\`, ...`):

```markdown
- The fact `class.record`, whether a class is a record, as the language writes one, which `parts.<part>.holds` and a
  check of your own whose filter is `record` need, in place of `class.methods` and `function.returns`; a language
  that does not supply it is refused them with the needs text. The reader says it of each class (`Class.record`),
  handed the language's `special`, and the checks no longer work it out. Python supplies it, computed as before: a
  class whose methods are all special that a top-level function of its file names in its return annotation.
```

and as the first bullet of `### Changed` (before `- The filter \`public\` reads the fact \`public\`, ...`):

```markdown
- A language's data file writes what makes a class an immutable record as marks, each a map of one of four forms,
  as interface marks are: `{base: <outside name>}`, `{decorator: <outside name>, keywords: {<name>: <value>}}`
  (keywords left out: the decorator however it is written), `{fields: <word>}` or `{type: <outside name>}`. Python
  writes `[{base: typing.NamedTuple}, {decorator: dataclasses.dataclass, keywords: {frozen: "True"}}]`, and its reader
  reads the first two forms. The string form is no longer read. Refused, once for the key: `immutable: each mark is
  {base}, {decorator, keywords}, {fields} or {type}`. No finding of a Python app changes.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-10/regenerate_docs.py` (never committed):

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
mkdir -p /tmp/xarch-3-10
uv run python -I /tmp/xarch-3-10/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines and an empty `git diff`. If the diff is not empty, stop and report it with the diff
(`git checkout -- docs/cli docs/web docs/xarch` restores the files); the fix belongs in the code, never in the docs.

- [ ] **Step 4: Run the gates**

Run the suite in the background with a recorded PID, the rest in the foreground, then read the log:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-10/pytest.log 2>&1 & echo $! > /tmp/xarch-3-10/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-3-10/pytest.log`.
Expected: the suite passes (corpora, golden-doc, needs-agree, self-check and seam tests included), both checks
report no violation, ruff reports nothing, the profile check loads. `git status --short` shows no change under
`tests/bootstrap/corpora/` and nothing under `.claude/` staged;
`git diff 1c2008d -- xarch/architectures/presets/language/python.yaml` shows only the header lines of `immutable`,
the `immutable:` line and `class.record: exact`; `grep -rn "class.methods\|function.returns" xarch/modules/rules/domain/vocabulary.py`
prints nothing.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'MSG'
The README's language paragraph says immutable marks are maps of four forms and that the reader says whether a class is a record, the fact class.record that holds and the filter record read, and the CHANGELOG adds the fact class.record and says immutable marks are maps; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

## Self-review against the spec

- 2.1 the fact: Task 2 (`FACTS` after `public`, the text; `supplies`); the refusal with today's text: Task 3
  (`test_a_part_that_holds_is_refused_...`).
- 2.2 the reader supplies `record`: Task 1 (`Class.record` default `False` and docstring; the rule with `special`;
  the port's keyword and docstring; every caller, `source_reading` with `""`; the fake; the module docstring
  paragraph).
- 2.3 marks as maps: Task 4 (four forms, Python's line and header, the one refusal for every case listed, no
  marks when the joins are refused, `RecordMark`'s forms and docstring, the reader's `base`/`decorator` reading,
  `fields`/`type` marking none, the sharper meaning pinned).
- 2.4 needs: Task 3 (`field_needs`, the filter's text, `NEEDS`, settled by `test_needs_agree.py`; a check of your own
  whose filter is `record` follows from the field needs, nothing to add).
- 2.5 the engine reads the fact: Task 3 (`_class` reads `cls.record`, drops `file` and `profile`, the docstring
  line; the grep for `is_special`/`returns_named`); `is_special` stays for `stand_ins.py`, `filters.py`,
  `profile_checks.py` (untouched).
- 2.6 stays: no task touches `expansion.py`, `keys.yaml`, `docs_template.py`, the filter `immutable`, corpora or
  golden docs; Task 5 regenerates and diffs them.
- 3 test-only languages: Task 4 (brace's `fields` mark and header, percent's base mark, neither gains `supplies`,
  `BRACE` carries the marks); the lacking-`class.record` refusal uses a language value (`UNRECORDED`, Task 3).
- 4.1 equality: Task 1 Step 3. 4.2 reader: Task 1 Step 2 (records), Task 4 Step 2 (marks). 4.3 neutrality: Task 3
  (BRACE trait and `holds`, PERCENT no record, BRACE immutable, builders both ways). 4.4: Task 3 (`test_facts.py`
  both ways, `test_vocabulary.py`; the other hand-built tests go through `read_as` unchanged, `test_holds.py` of the
  application sets `record=True`). 4.5: Task 4 (`test_language_file.py`, `test_language.py`), Task 2/3
  (`test_profile_needs.py`). 4.6: the seam guard, `test_needs_agree.py`, the corpora in Tasks 1, 3, 4, 5.
- 5 docs: Task 5 (README, CHANGELOG, golden docs); the loader's docstring and `python.yaml`'s header in Task 4.
- 7 gates: Task 5 Step 4.
- Types: `RecordMark(base=, decorator=, keywords=, fields=, type=)` is used the same in Task 4's loader, builders,
  reader and tests; `special: str` keyword-only in port, adapter and fake (Task 1) and used by every service;
  `_class(cls, read, defined, ports)` (Task 3); `Class.record` (Task 1) read in Tasks 3 and 4.
<!-- task-pipeline: validated -->
