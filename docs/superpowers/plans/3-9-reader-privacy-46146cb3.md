# 3.9 reader: privacy decided by the fact `public`

Card `46146cb3`, subtask of `3c7754c4`, blocked by `0954fb83` (3.8, done on the branch this one stacks on). Release
step 8d of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below
**R3**, section 3, line 270: "The fact `public`; `is_public` goes from the checking code. | language-neutral 9 | Step
7. Before 12 (kinds and `names` read public names).").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below **LN**),
section 9 (lines 908-965: 9.1 at 910, 9.2 at 916, 9.3 at 930, 9.4 at 940, 9.5 at 946, 9.6 at 955). Also
`code-shape-design.md` (below **CS**) 2.1 (lines 237-247): the Needs column of the kinds `classes` and `functions`
holds `public`, amended so by LN 9 (CS line 246; R3 C8, lines 159-166). That table belongs to release step 12; this
step only puts `public` where step 12 will read it.

Release-wide rules this step inherits: R3 O4, O5 (lines 228-229: README and CHANGELOG lines under `[Unreleased]`),
O7 (line 231: `public` is the fact of 8d, placed after `comment.doc` in `FACTS`, `python.yaml` `supplies`, `NEEDS`,
`test_needs_agree.py`), O8 (line 232: golden docs regenerated, diff read; none expected, LN 9.5 line 953), O18 (line
242: `python.yaml` is edited by 8d, its lines only). R3 line 393 (item 17): "The filter now reads the fact; one
meaning." Dodges that apply (card; LN lines 1143-1165): keeping `is_public(name)` in the checking code beside the fact
(LN line 1161, "One source per fact"); a hidden default in the code (LN line 1152); "a step is not done without its
test-only file" (LN line 1143); letting the corpora or golden docs move "a little" (LN line 1165).

## 1. Goal

Whether a name is for other files to use is the language's rule: a prefix in Python, an `export` in TypeScript, a
mark in ObjectScript (LN 9.1, lines 912-914). The reader decides it and says it as a fact, `public`. The checking code
never reads a name's spelling to decide it: `CheckedLanguage.is_public` goes, and every place that asked it reads the
fact (LN 9.3). `private` stays in the data file and is read only by the reader and by the code that writes or names
new files, scaffold and layout (LN 9.2, lines 924-928); the seam test proves no other file reads it. For Python the
reader computes `public` with today's rule exactly, so Python's findings, the recorded corpora and the golden docs do
not move (LN 9.5, line 953).

## 2. Observable behavior

### 2.1 The fact (LN 9.2)

- `FACTS` (`xarch/profile_values/capabilities.py`) gains `public`, placed right after `comment.doc` (R3 O7), with the
  text of LN 9.2 line 918: "whether a name a file defines, or takes by an import, is for other files to use, as the
  language decides it".
- `python.yaml` `supplies` gains `public: exact` right after `comment.doc: exact` (LN 9.2 line 923). `private: _`
  stays. The header comment's description of `private` says the reader decides a public name by it (and scaffold and
  layout refuse or skip a private name by it); nothing else in the file moves (R3 O18).
- A language that does not list `public` under `supplies` gets today's needs refusal for every key of 2.4 that it
  sets (LN 9.4, lines 942-943); no new refusal text. Nothing is refused at load for Python (LN 9.4 line 942).

### 2.2 What the reader supplies (LN 9.2)

- These values carry whether each name is public, set by the reader (LN 9.2 lines 919-921):
  - `Class` (`xarch/modules/rules/domain/parsed.py`): `public: bool`.
  - `Function` (top level and methods alike): `public: bool`.
  - `Constant`: `public: bool`.
  - The names of `module_functions`: each such name is that of a top-level `Function` of the same file, so its
    `public` is that `Function`'s; no second copy is kept (one source per fact). The planner may instead give
    `module_functions` its own flag, but then the two must never disagree and a test must pin that.
  - `Import` (`xarch/kernel/source.py`): for each name an import takes, whether it is public. Suggested shape: a field
    holding the names it takes that are not public (for example `withheld: frozenset[str] = frozenset()`), so that an
    import built with names alone reads every name as public. The field must not be named `private` (the seam test of
    4.6 looks for that attribute). An import of a whole module (`names is None`) takes no name and carries nothing.
- Defaults: each new field defaults to public (`True`; for `Import`, no name withheld), so values built by hand in
  tests keep building. That default is a convenience of the value, never what the Python reader relies on: the reader
  sets every flag itself (dodge LN line 1152 is about the checking code supplying a language rule, and no checking
  code may rely on the default to mean "Python's rule").
- For Python, the reader (`xarch/modules/rules/adapters/fs_source_tree.py`) sets `public` from the data file's
  `private` with today's rule exactly (LN 9.2 lines 922-923): a name is public unless `private` is given and the name
  starts with it, a special name included (`__init__`, `__all__` are not public). For an imported name the rule is
  applied to the name the import takes as written (`from m import _x as y` withholds `_x`; the name as defined is the
  name taken). This equals LN 9.2's "for an import of a name of the app, the value of the definition it reaches"
  because a Python definition's `public` is decided by its own name, which is the name the import takes; for an
  outside name it is the reader's rule (LN 9.2 lines 920-921). The equality test of 4.1 proves it on every file.
- The reader is handed `private`: `SourceTree.read` and `SourceTree.parsed` (the port,
  `xarch/modules/rules/application/ports/source_tree.py`, and `FsSourceTree`) take a keyword-only `private: str`,
  required as `standard` is, so no caller can forget it and silently read every name as public. Every caller that
  passes `profile.language.standard_modules` passes `profile.language.private` beside it
  (`services/source_check.py`, `holding.py`, `sources.py`, `asking.py`, `examples.py`). `source_reading.py`, which
  reads comment spans only and has no profile, passes `""`. An empty `private` makes every name public.

### 2.3 The facts the engine builds and the filter `public` (LN 9.3)

- The facts of the kinds `class`, `function` and `imported-name` (`xarch/modules/rules/application/logic/facts.py`)
  carry a trait `public` when the reader says the name is public (an `imported-name` of a whole module carries none:
  it names no name). The planner chooses how; the `doc` trait of 3.8 (`_DOC`, the `_trait` table in `filters.py`) is
  the precedent.
- The filter `public` (`filters.py` `_public`) reads that trait (as the other trait filters do) and nothing of the
  language. `not public` passes a fact without it. `special` stays as it is (a pattern of the data file,
  `is_special`).
- The vocabulary (`xarch/modules/rules/domain/vocabulary.py`):
  - a field `public` in `FIELDS`: "whether the name is for other files to use, as the language decides it";
  - the kinds `class`, `function`, `imported-name` carry it, each with `field_needs={"public": ("public",)}`, so a
    rule whose words read it needs the fact (that is how `not public` in `private-imports` needs it: through the
    field, not the filter's own `facts`);
  - `Filter("public", ...)` reads `("public",)` (not `("name",)`) and its meaning says "the name the fact carries is
    public: the language's reader says it is for other files to use"; nothing about how a private name starts.
- Consequence, deliberate: `public` now applies only to the kinds that carry the fact. Written in a check of your own
  on another kind (`method-call`, `callback`, `construction`, `import-into-app`, `comment`), `profile check` refuses it
  with today's "does not apply to the kind read" problem. No bundled profile, xarch's own profile or bundled check
  writes it so (checked: every `keep: [public]` in the repository reads `class`, `function` or `imported-name`).
  CHANGELOG says so.
- The checks that are code, not rules, read the fact (LN 9.3 lines 932-934):
  - `shared.py` (`:65`): a name of a shared part is reported only when its definition (class, top-level function,
    constant) is public, read off the `Class`, `Function` or `Constant` the name was gathered from in `_defined`.
  - `twins.py` (`_counted`, `:129`): a class is counted when it has fields, is public (`cls.public`) and is no
    interface.
  - `known.py` (`_declared`, `:62`): the name an entry of `guards.dead-code.known` writes is looked up among the
    file's `class` and `function` facts; it is declared only when the fact found carries `public` (a private class or
    function under that name is "defines no public class or top-level function", as today).
- `CheckedLanguage.is_public` (`xarch/profile_values/language.py:128-130`) is deleted. No file of xarch's code calls
  it (LN 9.3 line 932; the step-25 grep, LN line 1060, finds it only in the 0.2.0 CHANGELOG).
- Docstrings of the rules side that say privacy is a prefix say it is the fact: `twins.py:7` ("it does not start with
  the private prefix"), `shared.py`'s module docstring if it says so, `known.py`, the `facts.py` kind table (the traits
  of `class`, `function`, `imported-name` gain `public`).

### 2.4 Needs (LN 9.3 lines 937-938; R3 O7)

`NEEDS` in `xarch/modules/spec/domain/key_table.py` gains `public` on: `parts.<part>.holds` (a part of classes reads
public top-level functions), `parts.<part>.names`, `parts.<part>.shared`, `guards.private-imports`,
`guards.dead-code.tests_only`, `guards.dead-code.known`, `guards.no-twins`, `guards.no-twins.min_renamed`,
`guards.no-twins.translated`.

LN 9.3 writes "`guards.dead-code`". Read here as the dead-code keys that read public names: the rules of the key
`guards.dead-code` itself (ports, fakes; `expansion.py` `_dead_code`) read `interface` and `named`, never `public`,
and `tests/bootstrap/test_needs_agree.py` requires `NEEDS` to equal the expanded rules' needs for every key the engine
expands. So `guards.dead-code` and `guards.dead-code.untested` do not gain it; `tests_only` (an engine rule) and
`known` (`known.py`) do. For every engine-expanded key the needs-agree test is the arbiter; a key whose rules come to
need `public` through 2.3's field needs gains it in `NEEDS`, and none other.

The `holds` kinds of CS 2.1 do not exist yet (release step 12); this step adds `public` to today's `holds` key only.

### 2.5 Who reads `private` (LN 9.2 lines 924-928; LN 9.6 line 960)

After this step, the attribute `private` of the language (and `is_private_name` of `xarch/kernel/logic/names.py`) is
read only by:

- the reader (`fs_source_tree.py`), and the services that hand it `private` (2.2);
- scaffold (`scaffold/application/logic/names.py:15`, `services/scaffolding.py:47`, `adapters/spec_skeleton.py:42`,
  `domain/values.py`, `domain/errors.py`): a new part or module may not take a private name;
- layout (`layout/application/logic/unmirrored.py:14`, `requirements.py:18`, `adapters/spec_skeleton.py:34`,
  `domain/structure.py`): private folders stay unmirrored;
- spec, which loads the data file and hands `private` to scaffold and layout and prints it:
  `spec/application/logic/language_file.py` (loads it), `spec/application/services/publishing.py:52` (publishes it to
  scaffold and layout), `spec/application/logic/explain.py:36` (the `%private%` word of the format texts, while any
  text still uses it), `spec/application/logic/docs_template.py:514` (the `private-imports` docs line, 2.6), and
  `modules/*/contract/__init__.py` re-exports that carry it;
- `profile_values/language.py`, where the field is defined.

No file of the rules module outside the reader, and no file of `kernel/logic` but the definition of
`is_private_name`, reads it.

### 2.6 Texts (LN 9.3 lines 935-936)

- Docs line of `private-imports` (`docs_template.py:511-514`): when the data file gives `private`, the line is
  byte-identical to today's (``- `private-imports`: no file of the app or its tests imports a name that starts with
  `_` from another file of them.``; golden docs must not move, LN 9.5 line 953). When it gives none, the line prints no
  prefix and says the rule by the fact: "no file of the app or its tests imports a name another file of them keeps
  private." (exact words the planner's, but with "keeps private" and no backticked empty string). This reconciles LN
  9.3 ("prints the prefix only when the data file gives one; the sentence says 'a name another file keeps private'")
  with LN 9.5 (golden docs do not move): the new sentence is the no-prefix form.
- `keys.yaml` (`xarch/architectures/presets/format/keys.yaml`): the texts that define a public name by the prefix
  (`:357` and `:391` "a name that does not start with `%private%`", `:916` and `:918` `guards.private-imports`) say it
  by the fact: a public name is one the language's reader says other files may use; `private-imports` is "no name
  another file keeps private is imported from it" (exact words the planner's; for Python they may add "(for Python,
  one starting with `%private%`)" only if `%private%` is printed solely when the language gives one). These texts show
  in `profile explain` and the key catalogue; the planner confirms none reaches the golden docs, and the regenerated
  golden docs must show no diff.
- `vocabulary.py`: the filter `public`'s meaning (2.3). `profile explain filters.public` shows it, applying to
  `class`, `function`, `imported-name`.

### 2.7 Things that stay as they are

- Python's findings on every profile; the recorded corpora (`tests/bootstrap/corpora/`), not edited; the golden docs
  `docs/{cli,web,xarch}/testing.md`, regenerated with the repo's command and their diff read, expected empty (R3 O8).
- `special`, `is_special`, the `not special` of `private-imports`.
- Scaffold's and layout's refusals and skips by the prefix, and their texts.
- `uv run xarch check`, `--strict`, `xarch profile check architecture.yaml` on xarch itself (xarch's own profile sets
  `private-imports`, `dead-code`, `no-twins`, `holds`, `names`, `shared` where it does; Python supplies `public`, so
  it loads with no new problem).

## 3. The test-only languages (LN 9.5 lines 948-950; dodge LN line 1143)

- `tests/fakes/languages/brace.yaml` and `percent.yaml` give no `private` (they give none today) and their headers say
  why: their names are public or not as their reader says (an `export`, a mark), never by a prefix. No other key
  changes.
- The proof of neutrality is hand-built facts under `BRACE` (and `PERCENT` where cheap) from
  `tests/modules/rules/builders.py`, whose `private` is `""`: whatever a name is spelled, only the flag the values
  carry decides.

## 4. Tests (written first)

Unit = pure logic or a service with fakes, no disk; adapter = the real reader against real source text or files;
architecture = the repository guards; bootstrap = the wired app end to end.

### 4.1 The one-off equality on Python source — adapter (LN 9.5 lines 951-952)

New file beside `tests/modules/rules/adapters/test_fs_source_tree.py` (e.g. `test_fs_source_tree_public.py`).
Adapter tier: it runs the real reader on real files; no other tier reads them.

1. For every `.py` file of xarch's own source (`xarch/**/*.py`, the bundled example project under
   `xarch/architectures/examples` included), read with `FsSourceTree` and `private` from `python.yaml`: every class,
   every function (top level and methods), every constant, and every name every import takes has `public ==
   not name.startswith(prefix)`, `prefix` read from `python.yaml`'s `private` (not a literal). The test also asserts it
   saw at least one public and one non-public value of each of the four, so it cannot pass vacuously.
2. The same over the archived corpora, each unpacked into `tmp_path` (`tests/bootstrap/corpora/df537ca.tar.xz`,
   `7cc6111.tar.xz`, `examples.tar.xz`), with `tarfile` and `filter="data"` as `test_recorded_corpora.py`'s
   `archived` does; the archives are never edited (parametrized by archive, `id` a sentence).
3. A file the reader cannot parse is skipped by the test (it has no definitions), and the test fails if any archive
   yields no parsed file.

### 4.2 The reader — adapter, `tests/modules/rules/adapters/test_fs_source_tree.py`

4. With `private="_"`: `class _A`, `def _f`, `_X = 1`, a method `_m` and a special method `__init__` are not public;
   `class A`, `def f`, `X = 1`, method `m` are. `from m import a, _b` withholds `_b` only; `from m import _b as c`
   withholds `_b`; `import m` withholds nothing.
5. With `private=""` the same source reads every one of them public (an empty prefix makes nothing private).
6. `parsed(text, standard=..., private=...)` gives the same flags as `read` for the same text.
7. `read` and `parsed` called without `private` fail with `TypeError` (required, no hidden default).

### 4.3 Neutrality with hand-built facts — unit (LN 9.5 lines 948-950)

In `tests/modules/rules/application/logic/` (`test_holds.py`, `test_shared.py`, `test_names.py`,
`test_private_imports.py`, `test_dead_code.py`, `test_known.py`, `test_twins.py`), under `BRACE` (no `private`):

8. `holds: classes`: a top-level function `helper` (no prefix) with `public=False` is not listed; one with
   `public=True` is (LN 9.5: "not read by `holds.functions.names`", today's `holds` being the key that reads public
   top-level functions).
9. `shared`: a class `Kept` with `public=False` used by one user is not reported; with `public=True` it is reported
   as used by one user.
10. `names`: a class `helper` (matching no pattern) with `public=False` passes; with `public=True` it is reported.
11. `private-imports`: an import that takes `hidden` from another file of the app, withheld (not public), is reported;
    taken public, it is not. A name spelled with Python's prefix (`_x`) but public is not reported under brace.
12. `dead-code.tests_only`: a class no other file names, `public=False`, is not listed; `public=True` is.
13. `dead-code.known`: an entry naming a class the file defines with `public=False` is "defines no public class or
    top-level function"; with `public=True` it is accepted as today.
14. `no-twins`: two classes with the same fields, one `public=False`, are no twins; both public, they are.
15. The same files built under `PYTHON` with `public` set as the reader would (`_` names `False`) give today's
    findings: the existing tests of these files stay green once their hand-built private definitions say
    `public=False` (2.2: the default is public). The planner updates every hand-built `Class`/`Function`/`Constant`/
    `Import` whose test leans on a `_` name being private; a builder helper may set the flag from `PYTHON.private`, but
    no expected finding changes.

### 4.4 Facts, filters and vocabulary — unit

16. `test_facts.py`: the `class`, `function` and `imported-name` facts carry the trait `public` exactly when the value
    says so; an `imported-name` of a whole module carries none.
17. `test_filters.py:67` (`public` on `imported-name`): picks the facts by the trait, not by spelling; a case where a
    name starting with `_` is public and one where a plain name is withheld proves it.
18. `tests/modules/rules/domain/test_vocabulary.py`: `public` is a field of `class`, `function`, `imported-name`,
    with `field_needs` `("public",)`; the filter `public` applies to those three and to no other kind.
19. `test_rule.py` (or `test_expansion.py`): the `private-imports` rule's `needs` hold `public` (through `not public`);
    `parts.<p>.names` and `holds: classes` and `dead-code.tests_only` rules need it; the `guards.dead-code` port and
    fake rules do not.
20. A written check `{read: method-call, keep: [public]}` is refused with today's "does not apply to the kind read"
    problem (`test_own_checks.py` or the profile-check tests); `{read: class, keep: [public]}` loads.

### 4.5 Spec side — unit

21. `tests/profile_values/test_language.py:19-47`: the `is_public` cases go; a test asserts `CheckedLanguage` has no
    attribute `is_public`.
22. `tests/modules/spec/application/logic/test_profile_needs.py`: a language whose `supplies` lists everything
    `guards.private-imports` needed before but not `public` refuses it with today's needs text naming `public` and its
    `FACTS` text; listing it, it loads. Same for `parts.<p>.shared`.
23. `FACTS` holds `public` right after `comment.doc`; every key's needs stay within `FACTS`; `python.yaml` supplies
    `public` exactly (`test_language_file.py`).
24. `test_docs_template.py`: under a language with `private: "_"` the `private-imports` line is today's, byte for
    byte; under one with no `private` it holds "keeps private" and no empty backticks (` `` `).
25. `test_explain.py` (or the key-catalogue test): the reworded `keys.yaml` texts of 2.6 print no empty `%private%`
    under a language without one.

### 4.6 Guards (architecture) and end to end (bootstrap)

26. `tests/architecture/test_language_seam.py`: a new guard that no file of xarch's code reads `private` of the
    language (`.private` as `language_reads` finds it, and any import or call of `is_private_name`) but those of 2.5,
    listed as an exemption table with why each stays; a stale entry fails, as `EXEMPT` does today. A probe test (the
    file's style) shows the guard finds `profile.language.private` and `is_private_name(...)` written in a rules-logic
    file. The parametrised probe at `:456` drops `language.is_public('x')` from its snippet (the method no longer
    exists; the case still shows `keywords` unsaid). The docstring says privacy is read only by the reader, scaffold
    and layout. `TOKEN_KEYS` keeps `private` (a literal `"_"` is still found).
27. `tests/bootstrap/test_needs_agree.py` green with `public` in `NEEDS` per 2.4;
    `test_python_supplies_every_fact_a_bundled_check_reads` holds.
28. The corpora tests (`tests/bootstrap/test_recorded_corpora.py`) and the golden-doc tests pass with no change.
29. `tests/architecture/test_self_check.py` green.

## 5. Docs (R3 O4, O5, O8)

- `README.md:148` (language paragraph): "how a private name starts" says it is what the Python reader decides a
  public name by, and what scaffold and layout refuse and skip, and that whether a name is public is the fact `public`
  a reader supplies. `README.md:306` (the `private-imports` row): "an import of a name another file of the app or its
  tests keeps private (for Python, one starting with `_`)". `tests/architecture/test_readme.py` stays green.
- `CHANGELOG.md` `[Unreleased]`: under `### Added`, the fact `public` ("whether a name a file defines, or takes by an
  import, is for other files to use, as the language decides it"), which `parts.<part>.holds`, `names`, `shared`,
  `guards.private-imports`, `guards.dead-code.tests_only`, `.known` and `guards.no-twins` need; Python supplies it,
  computed from `private` as before. Under `### Changed`, the filter `public` reads that fact and applies to `class`,
  `function` and `imported-name` only (written on another kind, `profile check` refuses it); no finding of a Python
  app changes.
- Golden docs regenerated with the repo's command, diff read, expected empty; never edited by hand.
- `docs/examples/**` copies of changed files: updated only where a test or the docs generator holds them to the
  code; the planner checks which.

## 6. Out of scope

- Records and immutable marks (LN 10, release step 8e, card 3.10).
- `holds` as a map of kinds and its `names` per kind (CS, release step 12, story 4); this step adds `public` to
  today's keys only.
- A reader for any language but Python, or any reader that decides privacy by anything but the prefix.
- Scaffold's and layout's own reading of `private` (they keep the prefix, LN 9.2 lines 925-927).
- `Method` (`Class.methods`): it carries no `public`; methods are read as `Function` values for privacy.
- Any retired-keys entry or migration hint (no key is renamed).
- Editing the recorded corpora.

## 7. Gates

Each passes on this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background
with `timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`.

Project rules: no comments in xarch's code (docstrings as the code base writes them); tests first; examples simple,
with absolute `app.` imports; recorded corpora edited by hand only, and not at all in this step; Python only in the
reader adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is
pushed.

## 8. Review focus (for the planner)

1. A caller of the reader that forgets `private` (`examples.py`, `asking.py`, `holding.py`'s `parsed` path): every
   name would read public and `private-imports`, `dead-code.tests_only`, `holds` would move in profile examples and
   evals. Required keyword, and a test per service that a `_` name reads non-public.
2. Hand-built tests whose `_` names were private by spelling and now default to public: a silently weakened test
   still passes when it asserts "not reported". The planner greps every hand-built `_`-named `Class`, `Function`,
   `Constant` and `Import` in `tests/` and sets `public=False` where the test leans on it.
3. Special names (`__init__`, `__all__`, `__version__`): not public, as today (`private-imports` exempts them by
   `not special`, `dead-code.tests_only` and `shared` skip them as private). The equality test of 4.1 covers them; the
   reader must not "fix" them to public.
4. `from m import _x as y`: the withheld name is the one taken (`_x`), and `imported-name`'s fact name is `_x`, so
   `private-imports` still reports it.
5. A language with no `private` and no reader-set flags: the docs line, `keys.yaml` texts and `profile explain` never
   print an empty `` `` `` prefix; `profile check` with such a language and `private-imports` set refuses for want of
   `public` unless it is supplied.

---

# 3.9 reader: privacy decided by the fact `public` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Whether a name is for other files to use becomes a fact, `public`, that the language's reader supplies (for
Python from the data file's `private`, with today's rule exactly); every check that asked `CheckedLanguage.is_public`
reads the fact instead, `is_public` is deleted, and no finding, corpus or golden doc of a Python app moves.

**Architecture:** `FACTS` and `python.yaml` gain `public` (Task 1). The rules domain's `Class`, `Function` and
`Constant` gain `public: bool = True` and the kernel's `Import` gains `withheld: frozenset[str] = frozenset()` (the
names it takes that are not public); `FsSourceTree.read`/`parsed` take a required keyword `private: str` and set every
flag with `is_private_name`; every service hands `profile.language.private` (Task 2). The engine's `class`, `function`
and `imported-name` facts carry a trait `public`; the vocabulary declares a field `public` on those three kinds with
`field_needs={"public": ("public",)}`; the filter `public` reads the trait; the test builders read a hand-built file
as Python's reader would; `NEEDS` gains `public` on the engine-expanded keys (Task 3). The code checks `shared`,
`twins` and `known` read the flags, `is_public` goes, and `NEEDS` gains `public` on their keys (Task 4). The docs
line of `private-imports`, the `keys.yaml` texts and a new seam guard on who reads `private` (Task 5). README,
CHANGELOG, golden docs and the gates (Task 6).

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/3-9-reader-privacy-46146cb3.md` (prepended above).

## Global Constraints

- `FACTS["public"]` is exactly `whether a name a file defines, or takes by an import, is for other files to use, as
  the language decides it`, placed right after `comment.doc`.
- `python.yaml`: only `public: exact` right after `comment.doc: exact` under `supplies`, and the header's words for
  `private` (reflowed lines 12-26 as given in Task 1). `private: _` stays. Nothing else in the file moves.
- `FIELDS["public"]` is exactly `whether the name is for other files to use, as the language decides it`; the filter
  `public`'s meaning is exactly `the name the fact carries is public: the language's reader says it is for other files
  to use`, and it reads `("public",)`.
- `NEEDS` gains `public` (appended last) on exactly: `parts.<part>.holds`, `parts.<part>.names`,
  `parts.<part>.shared`, `guards.private-imports`, `guards.dead-code.tests_only`, `guards.dead-code.known`,
  `guards.no-twins`, `guards.no-twins.min_renamed`, `guards.no-twins.translated`. Not `guards.dead-code`, not
  `guards.dead-code.untested`.
- `SourceTree.read` and `SourceTree.parsed` take a keyword-only `private: str` with no default (port, adapter, fake).
  `source_reading.py` passes `private=""`.
- New value fields default to public (`public: bool = True`; `withheld: frozenset[str] = frozenset()`); the field on
  `Import` is never named `private`. The Python reader sets every flag itself.
- `CheckedLanguage.is_public` is deleted; nothing calls it.
- The `private-imports` docs line under a language that gives `private` is byte-identical to today's; with none it is
  exactly ``- `private-imports`: no file of the app or its tests imports a name another file of them keeps private.``
- Python's findings, `tests/bootstrap/corpora/` (never edited) and the golden docs `docs/{cli,web,xarch}/testing.md`
  (regenerated, diff empty) do not move.
- No comments in xarch's code (docstrings as the code base writes them); no docstring of xarch's code names the
  language ("Python") outside the reader adapter; tests first; Python only in the reader adapter and the data files
  under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- Gates (Task 6): `uv run pytest -q` (in the background with `timeout`), `uv run xarch check`,
  `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Design decisions the spec left to the planner

- `module_functions` keeps no flag of its own: `shared` reads the `public` of the top-level `Function` of that name
  (one source per fact).
- The `public` trait is set in `facts.py` (`_class`, `_function`, `_imported`), as `doc` was in 3.8; the filter
  `public` joins the `_trait` table in `filters.py`, and `_public` goes.
- The test builders (`tests/modules/rules/builders.py`): `source()`/`in_tests()` take `language=PYTHON` and pass the
  file through a new `read_as(file, language)`, which makes each class, function and constant whose name starts with
  `language.private` not public (a flag given `False` stays `False`); `imp()` (which already takes `language`)
  withholds the names that start with `language.private`, plus a new keyword `withheld`. So every existing Python test
  keeps its findings with no edit, and a test under `BRACE`/`PERCENT` (no `private`) passes `language=BRACE` and sets
  flags by hand. A `SourceFile` built directly (not through `source`) sets `public=False` itself where it leans on a
  `_` name: `test_kept.py`, `test_elsewhere.py`, `test_asked.py`, `tests/modules/rules/application/test_holds.py`.
- `FakeSourceTree` records each prefix it is handed in `prefixes` (as `handed` records the standard modules), and
  `tests/modules/rules/application/test_private_handed.py` mirrors `test_standard_handed.py`.
- `keys.yaml` drops `%private%` from the three texts that defined a public name by it (no conditional Python clause),
  so nothing can print an empty prefix; `explain.py` keeps the `%private%` word.
- The equality test of spec 4.1 requires "both values seen" per kind over xarch's source and the three archives
  together (xarch's own source imports no private name, so the archive `7cc6111` supplies the non-public imported
  names: `_json_refusal`); each archive alone must yield a parsed file and the rule on every name.
- `known._declared` drops its `profile` parameter, which it no longer reads.
- The new seam guard (`PRIVACY` in `test_language_seam.py`) finds any attribute `.private` and any name, import or
  attribute `is_private_name` in a file of xarch's code (but `architectures/`); its exemption table lists the 15
  files that read it after this step, and a stale entry fails.

## Review Focus

1. A caller of the reader that forgets `private` (every name would read public, and `private-imports`,
   `dead-code.tests_only`, `holds` would move in examples and evals): the keyword is required. Pinned in Task 2
   (`test_the_reader_must_be_handed_the_prefix`, and `test_private_handed.py`, one test per service).
2. Hand-built tests whose `_` names were private by spelling and now default to public, a weakened test still passing
   on "not reported": pinned in Task 3 by the builders (`read_as`, `imp`) and by `public=False` on the four
   `SourceFile`s built directly; `test_kept.py` (`__init__` kept out) and `test_elsewhere.py` (a private function
   breaks no part) would fail without it.
3. Special names (`__init__`, `__all__`) stay not public: pinned in Task 2
   (`test_the_reader_says_a_name_is_public_unless_it_starts_with_the_private_prefix_it_is_handed`) and by the
   equality test over xarch's source and the corpora.
4. `from m import _x as y` withholds `_x`, the name taken: pinned in Task 2 (the same reader test, row `_c`).
5. A language with no `private`: the docs line and the `keys.yaml` texts print no empty `` `` ``, and `profile check`
   refuses `guards.private-imports` and `parts.<part>.shared` for want of `public`. Pinned in Task 5
   (`test_the_private_imports_line_of_a_language_that_gives_no_prefix_...`,
   `test_the_texts_that_say_a_public_name_say_it_by_the_reader_and_never_by_the_prefix`) and Task 3/4
   (`test_the_keys_that_read_whether_a_name_is_public_are_refused_...`).

---

### Task 1: The fact `public`, which Python supplies

**Files:**
- Modify: `xarch/profile_values/capabilities.py` (`FACTS`, after `"comment.doc"`)
- Modify: `xarch/architectures/presets/language/python.yaml` (header lines 12-26; `supplies`, after `comment.doc: exact`)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`
- Test: `tests/modules/spec/application/logic/test_language_file.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `FACTS["public"]` (a key every later task names in needs); `Supply("public", EXACT)` in Python's
  `CheckedLanguage.supplies`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/spec/application/logic/test_profile_needs.py`:

```python
def test_public_is_a_fact_after_comment_doc():
    facts = list(FACTS)
    assert facts[facts.index("comment.doc") + 1] == "public"
    assert FACTS["public"] == ("whether a name a file defines, or takes by an import, is for other files to use, as the "
                               "language decides it")
```

Append to `tests/modules/spec/application/logic/test_language_file.py`:

```python
def test_python_supplies_public_exactly_right_after_comment_doc_and_keeps_its_private_prefix():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    supplies = list(document["supplies"])
    assert supplies[supplies.index("comment.doc") + 1] == "public"
    assert Supply("public", EXACT) in PYTHON_LANGUAGE.checked.supplies
    assert PYTHON_LANGUAGE.checked.private == document["private"] == "_"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py::test_public_is_a_fact_after_comment_doc tests/modules/spec/application/logic/test_language_file.py::test_python_supplies_public_exactly_right_after_comment_doc_and_keeps_its_private_prefix`
Expected: FAIL — `ValueError: 'public' is not in list` / `KeyError: 'public'` (the first), and `IndexError` or
`assert 'use' == 'public'` (the second).

- [ ] **Step 3: Add the fact**

In `xarch/profile_values/capabilities.py`, replace

```python
    "comment.doc": "whether a comment is a doc comment",
```

with

```python
    "comment.doc": "whether a comment is a doc comment",
    "public": "whether a name a file defines, or takes by an import, is for other files to use, as the language "
              "decides it",
```

- [ ] **Step 4: Have Python supply it, and say what `private` decides**

In `xarch/architectures/presets/language/python.yaml`, replace

```yaml
  comment.doc: exact
```

with

```yaml
  comment.doc: exact
  public: exact
```

Then replace header lines 12-26 (from `# package and member are given together); private, ...` through
`# app, {dotted} standing for that file's dotted path and {name} for the name.`) with exactly these 16 lines (the
words of `private` gain what it decides; the rest is the same text reflowed at the file's width):

```yaml
# package and member are given together); private, how a name starts that is private to its file or folder, by which
# the reader decides that a name is not public (the fact public) and scaffold and layout refuse or skip a private
# name; special, the pattern of a name the language reserves for itself (a regular expression the whole name matches);
# call, the special method that calling an instance runs; nothing, the return annotations that say a function gives no
# value, as the reader writes them (a list); unannotated, left out here, would say with its one value, nothing, that a
# function with no return annotation gives none; comments, the forms a comment is written in, each {line: <marker>},
# to the end of its line, {block: [<open>, <close>]}, or {doc: [<open>, <close>]}, a comment that holds documentation
# (its closing may be "" for the end of its line; Python writes line comments only, its documentation being in
# docstrings), the docs printing the first line form's marker; directives, the comments its tools read as
# instructions, each after the marker of a comment of any form (a space in one stands for any spaces); shebang, how
# line 1 names the program that runs the file; encoding, how line 1 or 2 declares the file's encoding (a regular
# expression, after the marker of a comment of any form); branching, the keywords of the statements that branch;
# branching_expressions, the keywords of the expressions that choose between values, as its reader records them;
# immutable, what makes a class an immutable record: a dotted name among its bases or its decorators, a decorator
# called with each keyword written after it, as written; importing, how a file imports a name from another file of the
# app, {dotted} standing for that file's dotted path and {name} for the name.
```

Lines 1-11 and 27-29 (the `supplies:` paragraph) stay as they are.

In `xarch/modules/spec/application/logic/language_file.py`, replace the docstring line

```
    private        what a name private to its file or folder starts with
```

with

```
    private        what a name private to its file or folder starts with: a reader may decide by it whether a name
                   is public (the fact public), and scaffold and layout refuse or skip a private name by it
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec tests/profile_values tests/modules/rules/domain tests/bootstrap/test_needs_agree.py`
Expected: PASS (`test_python_supplies_every_fact_a_bundled_check_reads` included: Python supplies every fact).
`git diff -- xarch/architectures/presets/language/python.yaml` shows only the header lines and `public: exact`.

- [ ] **Step 6: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml \
  xarch/modules/spec/application/logic/language_file.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_language_file.py
git commit -F - <<'MSG'
The fact public, whether a name a file defines or takes by an import is for other files to use as the language decides it, follows comment.doc in FACTS; Python supplies it exactly, and its data file says the reader decides it by private

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 2: The reader says which names are public, handed the language's `private`

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py` (`Class`, `Constant`, `Function`: a field `public`)
- Modify: `xarch/kernel/source.py` (`Import`: a field `withheld`)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring; `read`, `parsed`, `_parsed`,
  `_imports`, `_functions`, `_function`, `_constants`, `_classes`)
- Modify: `xarch/modules/rules/application/ports/source_tree.py` (`read`, `parsed`)
- Modify: `xarch/modules/rules/application/services/source_check.py:75-81`, `holding.py:27,37-38`,
  `sources.py:52`, `asking.py:26`, `examples.py:52-53,60-61`, `source_reading.py`
- Modify: `tests/fakes/filesystem.py` (`FakeSourceTree`)
- Modify: `tests/modules/rules/adapters/test_fs_source_tree.py` (every call of `read`/`parsed`; new tests)
- Create: `tests/modules/rules/adapters/test_fs_source_tree_public.py`
- Create: `tests/modules/rules/application/test_private_handed.py`
- Test: `tests/modules/rules/domain/test_parsed.py`

**Interfaces:**
- Consumes: nothing of Task 1 at run time.
- Produces: `Class.public: bool = True`, `Function.public: bool = True`, `Constant.public: bool = True` (last field of
  each); `Import.withheld: frozenset[str] = frozenset()` (last field); `SourceTree.read(root, paths, table=None,
  immutable=(), interface=(), *, standard: frozenset[str], private: str) -> list[SourceFile]`;
  `SourceTree.parsed(text: str, standard: frozenset[str], *, private: str) -> SourceFile`;
  `FakeSourceTree.prefixes: list[str]`.

- [ ] **Step 1: Write the failing tests of the values**

Replace `tests/modules/rules/domain/test_parsed.py` with:

```python
"""The rules the values of a parsed file keep about themselves: which statements are real, and that a value built by
hand is public, and an import withholds no name, unless it says otherwise."""
from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, Constant, Function


def test_a_function_s_real_statements_are_those_that_are_not_inert():
    assert Function(1, "f", statements=5, inert=2).real_statements == 3


def test_a_value_built_with_a_name_alone_is_public_and_an_import_withholds_nothing():
    assert (Class(1, "_A").public, Function(1, "_f").public, Constant(1, "_X").public) == (True, True, True)
    assert Import(1, ("m",), ("_x",)).withheld == frozenset()
    assert (Class(1, "A", public=False).public, Import(1, ("m",), ("x",), withheld=frozenset({"x"})).withheld) == (
        False, frozenset({"x"}))
```

- [ ] **Step 2: Write the failing tests of the reader**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, add to the imports

```python
from importlib import resources

import yaml
```

(`from importlib import resources` beside `import sys`, `import yaml` beside `import pytest`, as ruff sorts them), and
after the `STANDARD = ...` docstring add

```python
PRIVATE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["private"]
"""How the language the tests' sources are written in starts a private name, as its data file says it."""
```

Then apply these replacements to the whole file (a throwaway script, never committed):

```bash
mkdir -p /tmp/xarch-3-9 && cat > /tmp/xarch-3-9/hand_private.py <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1]) / "tests/modules/rules/adapters/test_fs_source_tree.py"
text = path.read_text(encoding="utf-8")
pairs = [('standard=STANDARD)', 'standard=STANDARD, private=PRIVATE)'),
         ('standard=standard)', 'standard=standard, private=PRIVATE)'),
         ('standard=frozenset({"fs"}))', 'standard=frozenset({"fs"}), private=PRIVATE)'),
         ('.parsed(text, frozenset({"fs"}))', '.parsed(text, frozenset({"fs"}), private=PRIVATE)'),
         ('.parsed(text, STANDARD)', '.parsed(text, STANDARD, private=PRIVATE)'),
         ('os.getcwd()\\n", STANDARD)', 'os.getcwd()\\n", STANDARD, private=PRIVATE)'),
         ('pass\\n", STANDARD)', 'pass\\n", STANDARD, private=PRIVATE)')]
for old, new in pairs:
    assert old in text, old
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
PY
uv run python -I /tmp/xarch-3-9/hand_private.py "$PWD"
grep -c "private=PRIVATE" tests/modules/rules/adapters/test_fs_source_tree.py
```

Expected: `16`. Two lines are then longer than 140; rewrite them. The body of
`test_a_class_is_an_immutable_record_when_a_mark_names_one_of_its_bases_or_its_decorators` becomes:

```python
    (tmp_path / "a.py").write_text(text)
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], immutable=MARKS, standard=STANDARD, private=PRIVATE)[0]
    assert read.classes[0].immutable is immutable
```

and in `test_a_keyword_mark_marks_no_class_of_this_language` the `read = ...` line becomes:

```python
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], interface=(InterfaceMark(keyword=keyword),),
                                           standard=STANDARD, private=PRIVATE)[0]
```

Append the tests of privacy to the same file:

```python
PRIVACY = ("class A: ...\nclass _A: ...\nclass Kept:\n    def __init__(self): ...\n    def m(self): ...\n"
           "    def _m(self): ...\ndef f(): ...\ndef _f(): ...\nX = 1\n_X = 1\n__all__ = ['A']\n"
           "from m import a, _b\nfrom m import _c as c\nimport os\n")
"""A class, a function, a method, a constant and an import of each sort, public and not, special names among them."""


def flags(found: SourceFile) -> tuple:
    """Whether each class, function and constant is public, by its name, and what each import takes and withholds."""
    return ({c.name: c.public for c in found.classes}, {f.name: f.public for f in found.functions},
            {c.name: c.public for c in found.constants}, [(i.names, i.withheld) for i in found.imports])


def test_the_reader_says_a_name_is_public_unless_it_starts_with_the_private_prefix_it_is_handed(tmp_path):
    assert flags(parsed(tmp_path, PRIVACY)) == (
        {"A": True, "_A": False, "Kept": True},
        {"__init__": False, "m": True, "_m": False, "f": True, "_f": False},
        {"X": True, "_X": False, "__all__": False},
        [(("a", "_b"), frozenset({"_b"})), (("_c",), frozenset({"_c"})), (None, frozenset())])


def test_handed_no_prefix_the_reader_makes_every_name_public(tmp_path):
    (tmp_path / "x.py").write_text(PRIVACY)
    classes, functions, constants, imports = flags(
        FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, private="")[0])
    assert {*classes.values(), *functions.values(), *constants.values()} == {True}
    assert [withheld for _, withheld in imports] == [frozenset(), frozenset(), frozenset()]


def test_a_text_in_no_file_is_told_public_as_a_file_is(tmp_path):
    assert flags(FsSourceTree(FileSystem()).parsed(PRIVACY, STANDARD, private=PRIVATE)) == flags(
        parsed(tmp_path, PRIVACY))


def test_the_reader_must_be_handed_the_prefix(tmp_path):
    tree = FsSourceTree(FileSystem())
    with pytest.raises(TypeError):
        tree.read(tmp_path, [], standard=STANDARD)
    with pytest.raises(TypeError):
        tree.parsed("x = 1\n", STANDARD)
```

- [ ] **Step 3: Write the failing equality test over real source**

Create `tests/modules/rules/adapters/test_fs_source_tree_public.py`:

```python
"""FsSourceTree on every Python file of xarch's own source (the bundled example project included) and of the recorded
corpora, each archive unpacked and never edited: each class, function (a method too), constant and name an import
takes is public exactly when its name does not start with the prefix of private names the language's data file
gives, the rule the checks read by spelling before the reader said it. A file that does not parse defines nothing and
is passed over."""
import tarfile
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.platform.filesystem import FileSystem

PRIVATE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["private"]
SOURCE = Path(__file__).resolve().parents[4] / "xarch"
CORPORA = Path(__file__).resolve().parents[3] / "bootstrap" / "corpora"
ARCHIVES = ("df537ca", "7cc6111", "examples")


def read(root: Path) -> list[SourceFile]:
    """Every file below root that parses, read as `check` reads it."""
    tree = FsSourceTree(FileSystem())
    return [file for file in tree.read(root, tree.paths(root, (".py",)), standard=frozenset(), private=PRIVATE)
            if file.error is None]


def unpacked(name: str, into: Path) -> Path:
    with tarfile.open(CORPORA / f"{name}.tar.xz") as archive:
        archive.extractall(into, filter="data")
    return into


def told(files: list[SourceFile]) -> dict[str, list[tuple[str, bool]]]:
    """Each name the files define or take by an import, by what it is, with whether the reader says it is public."""
    return {"class": [(c.name, c.public) for f in files for c in f.classes],
            "function": [(fn.name, fn.public) for f in files for fn in f.functions],
            "constant": [(c.name, c.public) for f in files for c in f.constants],
            "imported name": [(name, name not in i.withheld) for f in files for i in f.imports for name in i.names or ()]}


def broken(found: dict[str, list[tuple[str, bool]]]) -> dict[str, list[str]]:
    """The names, by what they are, whose flag is not the rule of the prefix."""
    return {what: sorted({name for name, public in named if public == name.startswith(PRIVATE)})
            for what, named in found.items()}


def test_every_name_of_xarch_s_own_source_is_public_exactly_when_it_does_not_start_with_the_prefix():
    files = read(SOURCE)
    assert files and broken(told(files)) == {"class": [], "function": [], "constant": [], "imported name": []}


@pytest.mark.parametrize("archive", [
    pytest.param("df537ca", id="the commit df537ca, as recorded"),
    pytest.param("7cc6111", id="the commit 7cc6111, as recorded"),
    pytest.param("examples", id="the bundled examples, as recorded"),
])
def test_every_name_of_a_recorded_corpus_is_public_exactly_when_it_does_not_start_with_the_prefix(tmp_path, archive):
    files = read(unpacked(archive, tmp_path))
    assert files and broken(told(files)) == {"class": [], "function": [], "constant": [], "imported name": []}


def test_the_source_read_holds_public_names_and_others_of_every_kind_so_that_the_rule_is_not_held_vacuously(tmp_path):
    found = told(read(SOURCE))
    for archive in ARCHIVES:
        for what, named in told(read(unpacked(archive, tmp_path / archive))).items():
            found[what] += named
    assert {what: {public for _, public in named} for what, named in found.items()} == {
        "class": {True, False}, "function": {True, False}, "constant": {True, False}, "imported name": {True, False}}
```

- [ ] **Step 4: Write the failing test that every service hands the prefix**

Create `tests/modules/rules/application/test_private_handed.py` (the fake gains `prefixes` in Step 8):

```python
"""Use case: every service that reads the app's code hands the reader how the profile's language starts a private
name, so that a name is public or not as `check` reads it; the reading of a text for spec, which has no profile, hands
none, so that every name of it reads public."""
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

PREFIX = "~"
"""How the profile's language starts a private name: not Python's, so that only the profile can have given it."""
LANGUAGE = replace(PYTHON, private=PREFIX)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"
PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []}, more={TESTS: {"kernel/test_ids.py": []}},
                          parsed=PARSED)


def test_the_check_hands_it_for_the_app_and_for_the_tests():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check_app(CheckApp(ROOT, "mine", ROOT.parent, TESTS))
    assert found.prefixes == [PREFIX, PREFIX]


def test_the_holds_question_hands_it_for_the_files_given_and_for_the_other_files_of_the_app():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.prefixes == [PREFIX, PREFIX]


def test_the_sources_read_for_a_module_that_reads_the_app_s_code_hand_it():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel/ids.py"),), Path("/src"), ROOT, "mine"))
    assert found.prefixes == [PREFIX]


def test_an_eval_s_facts_are_read_with_it():
    found = tree()
    evals = profile(asked={"rule": Asked("file", Scope(APP, "domain"))}, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": evals})).kept(KeepFacts("mine", "app", "rule", ((DOMAIN, "nothing"),)))
    assert found.prefixes == [PREFIX]


def test_the_examples_of_a_profile_s_own_checks_and_evals_are_read_with_it():
    found = tree()
    checks = {"no-managers": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                          (Saying("{name}", "rename it"),), flagged=((DOMAIN, "manager"),),
                                          clean=((DOMAIN, "nothing"),))}
    evals = {"rule": Asked("class", Scope(APP, "domain"), (), ((DOMAIN, "manager"),), ((DOMAIN, "manager"),))}
    reviewed = {"mine": Reviewed("mine", (), 2, Resemblance(False, "cli"))}
    owned = profile(written=checks, asked=evals, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": owned}, reviewed=reviewed)).check_profile(CheckProfile(Path("/p/app"), "mine"))
    assert found.prefixes == [PREFIX, PREFIX, PREFIX, PREFIX]


def test_a_text_read_for_spec_hands_none_since_no_profile_says_it():
    found = tree()
    reader = ReaderController(SourceReadService(found))
    reader.imports("nothing")
    reader.comments("nothing")
    assert found.prefixes == ["", ""]
```

- [ ] **Step 5: Run the new tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters tests/modules/rules/application/test_private_handed.py`
Expected: FAIL — `TypeError: Class.__init__() got an unexpected keyword argument 'public'` / `AttributeError: 'Class'
object has no attribute 'public'`, `TypeError: FsSourceTree.read() got an unexpected keyword argument 'private'`, and
`AttributeError: 'FakeSourceTree' object has no attribute 'prefixes'`.

- [ ] **Step 6: Give the values their flags**

In `xarch/modules/rules/domain/parsed.py`:

`Class`: its docstring's last sentence `...; interface: it is an interface, as the reader was told one is marked (see
InterfaceMark)."""` becomes `...; interface: it is an interface, as the reader was told one is marked (see
InterfaceMark); public: it is for other files to use, as the language's reader says."""`, and after
`    interface: bool = False` add

```python
    public: bool = True
```

`Constant`: its docstring ends `...: its annotation (a string annotation read as the expression it holds) and its
value, but no text of its value; and whether it is for other files to use, as the language's reader says (public)."""`
(replacing `...and its value, but no text of its value."""`), and after `    named: frozenset[str] = frozenset()` add

```python
    public: bool = True
```

`Function`: its docstring's last sentence `...expressions holds each expression of its body that chooses between
values, as (line, the keyword the reader records it by)."""` becomes `...as (line, the keyword the reader records it
by). public: it is for other files to use, as the language's reader says."""`, and after
`    expressions: tuple[tuple[int, str], ...] = ()` add

```python
    public: bool = True
```

`SourceFile`'s docstring: after `(module_functions: a name that one \`def\` binds and nothing else binds, so that what
it names is a function)` add `, each public as that function is` — so it reads `...so that what it names is a function,
each public as that function is). named is ...`.

In `xarch/kernel/source.py`, `Import`'s docstring ends `...unresolved: the import names a place of the code being read
(relative, or by an alias the project maps) that the reader found no file or folder for. withheld: the names it takes
that are not for other files to use, as the language's reader says (none: every name it takes is public)."""`, and
after `    unresolved: bool = False` add

```python
    withheld: frozenset[str] = frozenset()
```

- [ ] **Step 7: Have the reader set them, and require the prefix**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

Add to the module docstring, as a paragraph after the one that begins `A file also lists each name a \`from\` import
takes whose bound name...`:

```
A name is public unless the prefix of private names the reader is handed (the language's data file's `private`) is
given and the name starts with it, a special name included: each class, each function (a method too), each name the
top level binds by an assignment, and each name a `from` import takes as written, its name before any `as`, which the
import withholds when it is not public. An empty prefix makes every name public.
```

Add the import:

```python
from xarch.kernel.logic.names import is_private_name
```

(after `from xarch.kernel.source import Import, Unparsable`; ruff's import order puts `xarch.kernel.logic.names`
before `xarch.kernel.source`).

Replace `read` and `parsed` of `FsSourceTree`:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str) -> list[SourceFile]:
```

(the body unchanged but its last `found.append`, which becomes)

```python
            found.append(_parsed(name, path, text, table, immutable, interface, standard, private,
                                 _Where((root.name, *path[:-1]), root, self._fs)))
```

and

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str) -> SourceFile:
        return _parsed("", (), text, None, (), (), standard, private)
```

Replace `_parsed`'s signature and return:

```python
def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None, marks: tuple[RecordMark, ...],
            interface: tuple[InterfaceMark, ...], standard: frozenset[str], private: str,
            where: _Where | None = None) -> SourceFile:
```

```python
    return SourceFile(name, path, tuple(_imports(tree, standard, private, where)), comments,
                      _functions(tree, form, private, where), tuple(_unions(tree)), calls=tuple(calls.found),
                      classes=tuple(_classes(tree, private, marks, interface, where)),
                      uses=tuple(calls.uses), parameter_calls=tuple(calls.parameter_calls),
                      module_functions=_module_functions(tree), named=_named(tree), callbacks=tuple(calls.callbacks),
                      method_calls=tuple(calls.method_calls), constants=tuple(_constants(tree, private)),
                      unmentioned=_unmentioned(tree), pieces=_pieces(tree))
```

Replace `_imports`:

```python
def _imports(tree: ast.AST, standard: frozenset[str], private: str, where: _Where | None = None) -> list[Import]:
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
                                _last(node), _from(node, where) is None,
                                frozenset(a.name for a in node.names if is_private_name(a.name, private))))
    return found
```

Replace `_functions` and the signature and return of `_function`:

```python
def _functions(tree: ast.Module, form: CaseTable | None, private: str,
               where: _Where | None = None) -> tuple[Function, ...]:
    scope = [_scope(tree, where)]
    lists = _lists(tree)
    found: list[Function] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(_function(node, scope, lists, form, private))
        elif isinstance(node, ast.ClassDef):
            found += [_function(n, scope, lists, form, private, node.name) for n in node.body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return tuple(found)


def _function(node: ast.FunctionDef | ast.AsyncFunctionDef, scope: list[Scope], lists: dict[str, ast.expr],
              form: CaseTable | None, private: str, owner: str = "") -> Function:
```

```python
    return Function(node.lineno, node.name, tables, mentions, blocks, asserts, owner, statements, shape,
                    bool(node.decorator_list), signature, sole_call, returns, inert, forwards, _mentioned(node),
                    choices, public=not is_private_name(node.name, private))
```

Replace `_constants`' signature and its last two statements:

```python
def _constants(tree: ast.Module, private: str) -> list[Constant]:
```

```python
        named = _mentioned(node)
        found += [Constant(node.lineno, name, named, not is_private_name(name, private))
                  for target in targets for name in _bound_names(target)]
    return found
```

Replace `_classes`' signature and the `found.append(...)` of its loop:

```python
def _classes(tree: ast.Module, private: str, marks: tuple[RecordMark, ...] = (),
             interface: tuple[InterfaceMark, ...] = (), where: _Where | None = None) -> list[Class]:
```

```python
            found.append(Class(node.lineno, node.name, bases, methods, _attributes(node), _named(node) - {node.name},
                               exception, tuple(child.target.id for child in declared),
                               tuple(_annotation(child.annotation) or "" for child in declared),
                               _immutable(node, bases, scope, marks), _interface(bases, interface),
                               not is_private_name(node.name, private)))
```

Run `grep -n "_classes(\|_constants(\|_functions(\|_imports(" xarch/modules/rules/adapters/fs_source_tree.py` and
confirm each call passes `private` as above (the only calls are in `_parsed`).

- [ ] **Step 8: The port and the fake take the prefix**

In `xarch/modules/rules/application/ports/source_tree.py`, replace `read` and `parsed`:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so. An absolute import is of the standard library when its first step is one of the modules
        `standard` holds; a relative one never is. A name is public unless it starts with `private`, how the
        language starts a private name ("": every name is public)."""
        ...
```

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str) -> SourceFile:
        """A source text of the app's language that is in no file, parsed as a file of it is, an absolute import of
        the standard library when its first step is one of the modules `standard` holds, a name public unless it
        starts with `private`; one that does not parse holds its error."""
        ...
```

In `tests/fakes/filesystem.py`, `FakeSourceTree`: its docstring's `It records the standard modules each read and each
parse is handed (handed), and the endings each listing is handed (listed), in call order;` becomes `It records the
standard modules each read and each parse is handed (handed), the prefix of private names each is handed (prefixes),
and the endings each listing is handed (listed), in call order;`. In `__init__`, after `self.handed: ... = []` add

```python
        self.prefixes: list[str] = []
```

and replace `read` and `parsed`:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str) -> list[SourceFile]:
        self.handed.append(standard)
        self.prefixes.append(private)
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]
```

```python
    def parsed(self, text: str, standard: frozenset[str], *, private: str) -> SourceFile:
        self.handed.append(standard)
        self.prefixes.append(private)
        return _source("", (), self._parsed[text])
```

- [ ] **Step 9: Every service hands the language's prefix**

`xarch/modules/rules/application/services/source_check.py`, replace

```python
        marks, interface, standard = rules.language.immutable, rules.language.interface, rules.language.standard_modules
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface, standard=standard)
```

with

```python
        marks, interface, standard = rules.language.immutable, rules.language.interface, rules.language.standard_modules
        private = rules.language.private
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks,
                              interface=interface, standard=standard, private=private)
```

and

```python
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), table, marks, interface,
                                     standard=standard) if tests is not None else []
```

with

```python
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), table, marks, interface,
                                     standard=standard, private=private) if tests is not None else []
```

`xarch/modules/rules/application/services/holding.py`, replace

```python
        given = [(path, self._tree.parsed(text, profile.language.standard_modules)) for path, text in cmd.files]
```

with

```python
        given = [(path, self._tree.parsed(text, profile.language.standard_modules, private=profile.language.private))
                 for path, text in cmd.files]
```

and

```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface, standard=profile.language.standard_modules))
```

with

```python
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface, standard=profile.language.standard_modules,
                                     private=profile.language.private))
```

`xarch/modules/rules/application/services/sources.py`, replace

```python
        read = self._tree.read(app, [found.steps], standard=profile.language.standard_modules)[0]
```

with

```python
        read = self._tree.read(app, [found.steps], standard=profile.language.standard_modules,
                               private=profile.language.private)[0]
```

`xarch/modules/rules/application/services/asking.py`, replace

```python
        parsed = [(path, self._tree.parsed(text, profile.language.standard_modules)) for path, text in cmd.files]
```

with

```python
        parsed = [(path, self._tree.parsed(text, profile.language.standard_modules, private=profile.language.private))
                  for path, text in cmd.files]
```

`xarch/modules/rules/application/services/examples.py`, replace

```python
                facts = project([(path, self._tree.parsed(code, profile.language.standard_modules)) for path, code in files],
                                profile, app, (rule,))
```

with

```python
                facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                          private=profile.language.private)) for path, code in files],
                                profile, app, (rule,))
```

and

```python
        facts = project([(path, self._tree.parsed(code, profile.language.standard_modules)) for path, code in files],
                        profile, app, rules)
```

with

```python
        facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                  private=profile.language.private)) for path, code in files],
                        profile, app, rules)
```

`xarch/modules/rules/application/services/source_reading.py`: the class docstring becomes `"""Reads a source text of
the app's language that is in no file, with the reader that reads the app's files, handed no standard module and no
prefix of private names: spec, which asks, has no profile."""`, and both `self._tree.parsed(text, frozenset())`
become

```python
        read = self._tree.parsed(text, frozenset(), private="")
```

Then run `grep -rn "\.parsed(\|_tree\.read(" xarch` and confirm every call passes `private=`.

- [ ] **Step 10: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/fakes tests/kernel`
Expected: PASS. Then `uv run ruff check xarch tests` — no finding.

- [ ] **Step 11: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/kernel/source.py xarch/modules/rules/adapters/fs_source_tree.py \
  xarch/modules/rules/application/ports/source_tree.py xarch/modules/rules/application/services \
  tests/fakes/filesystem.py tests/modules/rules/domain/test_parsed.py tests/modules/rules/adapters \
  tests/modules/rules/application/test_private_handed.py
git commit -F - <<'MSG'
The reader says whether each class, function, constant and imported name is public, from the prefix of private names it is now handed as a required keyword, Python's rule exactly; every service hands it the language's private, and spec's reading of a text hands none

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 3: The facts carry `public`, and the filter `public` reads it

**Files:**
- Modify: `xarch/modules/rules/application/logic/facts.py` (docstring table; `_PUBLIC`; `_class`, `_function`, `_imported`)
- Modify: `xarch/modules/rules/application/logic/filters.py` (`_public` goes; `public` joins the `_trait` table)
- Modify: `xarch/modules/rules/domain/vocabulary.py` (`FIELDS`; kinds `imported-name`, `class`, `function`; `Filter("public", ...)`)
- Modify: `xarch/modules/spec/domain/key_table.py` (`NEEDS` of `parts.<part>.holds`, `parts.<part>.names`,
  `guards.dead-code.tests_only`, `guards.private-imports`)
- Modify: `tests/modules/rules/builders.py` (`imp`, `read_as`, `source`)
- Modify: `tests/modules/rules/application/test_kept.py:21`, `tests/modules/rules/application/test_holds.py:20`,
  `tests/modules/rules/application/logic/test_elsewhere.py:14`, `tests/modules/rules/application/logic/test_asked.py:14`
- Modify: `tests/modules/rules/application/logic/test_facts.py:93-108`, `tests/modules/rules/application/logic/test_reads.py:18-19`
- Modify: `tests/bootstrap/test_profile_explain_words.py:38-40`
- Modify: `tests/modules/spec/application/logic/test_profile_needs.py:15-18`, `tests/modules/spec/application/test_language.py:73-74`,
  `tests/modules/spec/application/test_explain.py:172-180`
- Test: `tests/modules/rules/application/logic/test_facts.py`, `test_filters.py`, `test_expansion.py`,
  `test_holds.py`, `test_names.py`, `test_private_imports.py`, `test_dead_code.py`;
  `tests/modules/rules/domain/test_vocabulary.py`, `tests/modules/rules/domain/test_rule.py`;
  `tests/modules/spec/application/logic/test_profile_needs.py`; `tests/bootstrap/test_needs_agree.py` (unchanged, must pass)

**Interfaces:**
- Consumes: `Class.public`, `Function.public`, `Import.withheld` (Task 2); `FACTS["public"]` (Task 1).
- Produces: the trait `"public"` on `class`, `function` and `imported-name` facts (a whole-module `imported-name`
  never carries it); `FIELDS["public"]`; the kinds' field `public` with `field_needs={"public": ("public",)}`;
  `imp(line, module, *names, up=None, language=PYTHON, withheld: tuple[str, ...] = ()) -> Import`;
  `read_as(file: SourceFile, language: CheckedLanguage) -> SourceFile`;
  `source(path, *imports, root=APP, language=PYTHON, **fields) -> SourceFile` (and `in_tests`, which passes
  `language` through `**fields`).

- [ ] **Step 1: Read hand-built files as Python's reader would**

In `tests/modules/rules/builders.py`, the import `from xarch.kernel.logic.names import outside_steps` becomes

```python
from xarch.kernel.logic.names import is_private_name, outside_steps
```

and replace `imp` and `source`:

```python
def imp(line: int, module: str, *names: str, up: int | None = None, language: CheckedLanguage = PYTHON,
        withheld: tuple[str, ...] = ()) -> Import:
    """`import module` with no names, `from module import names` with some; up, for a relative import, how many
    folders above the importing file's own it climbs. It is marked standard, and written, as the reader marks it when
    handed the standard modules of language (Python unless given): absolute and its first step one of them; the
    module with one dot more than up before it. It withholds, as that reader would, each name that starts as a
    private name of language does, and the names withheld lists besides."""
    steps = dotted(module) if module else ()
    relative = up is not None
    hidden = frozenset(withheld) | frozenset(name for name in names if is_private_name(name, language.private))
    return Import(line, steps, names or None, relative, up or 0,
                  not relative and bool(steps) and steps[0] in language.standard_modules,
                  "." * ((up or 0) + 1) + module if relative else module, withheld=hidden)


def _public(name: str, given: bool, language: CheckedLanguage) -> bool:
    return given and not is_private_name(name, language.private)


def read_as(file: SourceFile, language: CheckedLanguage) -> SourceFile:
    """The file with each class, function and constant whose name starts as a private name of language does made not
    public, as its reader would say; one given as not public stays so."""
    return replace(file, classes=tuple(replace(c, public=_public(c.name, c.public, language)) for c in file.classes),
                   functions=tuple(replace(f, public=_public(f.name, f.public, language)) for f in file.functions),
                   constants=tuple(replace(c, public=_public(c.name, c.public, language)) for c in file.constants))


def source(path: str, *imports: Import, root: str = APP, language: CheckedLanguage = PYTHON, **fields) -> SourceFile:
    """A file at path below root, shown as root/path, with its imports and any other field of a SourceFile, each of its
    definitions public or not as the reader of language would say (Python unless given; see read_as)."""
    return read_as(SourceFile(f"{root}/{path}", steps(path), imports, **fields), language)
```

`in_tests` stays as it is (`language` reaches `source` through `**fields`).

- [ ] **Step 2: Write the failing tests of the facts, the filter, the vocabulary and the rules**

In `tests/modules/rules/application/logic/test_facts.py`, add `from dataclasses import replace` at the top of the
imports and `BRACE` to the builders import (`from tests.modules.rules.builders import BRACE, PROFILE, imp, in_tests,
source`). Replace the bodies of three tests:

```python
def test_a_class_carries_its_name_the_names_it_mentions_and_what_it_is():
    assert DOMAIN.facts["class"] == (
        Fact("class", 1, ("Doc",), "Doc", frozenset({"public"}), names=frozenset({"Repo"})),
        Fact("class", 9, ("Shown",), "Shown", frozenset({"record", "public"})))


def test_a_class_the_reader_says_is_an_immutable_record_carries_it():
    classes = (Class(1, "Frozen", immutable=True), Class(2, "Loose"))
    read = facts_of([source("modules/docs/domain/a.py", classes=classes)], [], PROFILE, "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"immutable", "public"}), frozenset({"public"})]


def test_a_function_says_whether_it_is_at_the_top_level_or_a_method_that_forwards():
    assert DOMAIN.facts["function"] == (
        Fact("function", 4, ("make",), "make", frozenset({"top-level", "public"})),
        Fact("function", 6, ("Doc", "get"), "get", frozenset({"forwards", "public"}), target=("name",),
             text="self.repo.get"))
```

and append:

```python
def test_a_class_a_function_and_a_name_an_import_takes_carry_public_exactly_when_the_reader_says_so():
    file = source("modules/docs/domain/a.ts", imp(1, "app.kernel.ids", "shown", "hidden", withheld=("hidden",),
                                                  language=BRACE), imp(2, "app.kernel.ids", language=BRACE),
                  classes=(Class(3, "Kept", public=False), Class(4, "_Shown")),
                  functions=(Function(5, "kept", public=False), Function(6, "_shown"),
                             Function(7, "m", owner="Kept", public=False)), language=BRACE)
    read = facts_of([file], [], replace(PROFILE, language=BRACE), "app").files[0]
    assert [(f.name, "public" in f.traits) for f in read.facts["class"]] == [("Kept", False), ("_Shown", True)]
    assert [(f.name, "public" in f.traits) for f in read.facts["function"]] == [
        ("kept", False), ("_shown", True), ("m", False)]
    assert [(f.name, "public" in f.traits) for f in read.facts["imported-name"]] == [
        ("shown", True), ("hidden", False), (None, False)]
```

In `tests/modules/rules/application/logic/test_filters.py`, add `from dataclasses import replace` at the top of the
imports, and append:

```python
def test_the_public_filter_holds_of_the_names_the_reader_says_are_public_whatever_they_are_spelled():
    file = source("modules/docs/domain/doc.ts", imp(1, "app.kernel.ids", "_shown", "hidden", withheld=("hidden",),
                                                    language=BRACE), language=BRACE)
    built = facts_of([file], [], replace(PROFILE, language=BRACE), "app", "tests")
    read = built.files[0]
    assert [fact.name for fact in read.facts["imported-name"]
            if question(condition("public"))(Found(RULE, read, fact, None), built, PROFILE)] == ["_shown"]
```

In `tests/modules/rules/application/logic/test_reads.py`, `TRAITS` gains `"public"`:

```python
TRAITS = ("relative", "standard", "on-own-object", "top-level", "forwards", "exception", "record", "interface",
          "immutable", "receiver", "annotated-callable", "no-statements", "exceptions-only", "unreadable", "doc",
          "public")
```

Append to `tests/modules/rules/domain/test_vocabulary.py`:

```python
def test_whether_a_name_is_public_is_a_field_of_the_kinds_whose_names_the_language_decides_and_needs_the_fact():
    public = next(word for word in FILTERS if word.name == "public")
    carrying = [kind for kind in KINDS if kind.carries("public")]
    assert [kind.name for kind in carrying] == ["imported-name", "class", "function"]
    assert [kind.field_needs["public"] for kind in carrying] == [("public",), ("public",), ("public",)]
    assert [kind.name for kind in KINDS if public.applies_to(kind)] == ["imported-name", "class", "function"]
    assert (public.reads, public.meaning, FIELDS["public"]) == (
        ("public",), "the name the fact carries is public: the language's reader says it is for other files to use",
        "whether the name is for other files to use, as the language decides it")
```

Append to `tests/modules/rules/domain/test_rule.py`:

```python
def test_the_public_filter_applies_only_to_the_kinds_whose_reader_says_whether_a_name_is_public():
    with pytest.raises(RuleRefused) as refused:
        made(facts=("method-call",), targets=EXISTING, keep=c("public"), sayings=say("{line}"))
    assert list(refused.value.problems) == [
        "keep: public does not apply to method-call: it reads public, which it does not carry; it applies to "
        "imported-name, class and function"]
    assert made(facts=("class",), targets=EXISTING, keep=c("public"), sayings=say("{name}")).needs == (
        "class", "public")
```

Append to `tests/modules/rules/application/logic/test_expansion.py`:

```python
def test_the_rules_that_read_whether_a_name_is_public_need_the_fact_and_those_of_ports_fakes_and_files_do_not():
    checked = replace(PROFILE, private_imports=True, names={"services": ("*Service",)},
                      holds={"domain": "classes", "logic": "functions"}, dead_code=True, tests_only=True, untested=True)
    book = expansion.book(checked)
    assert {group: ["public" in rule.needs for rule in book[group]]
            for group in ("private-imports", "names", "holds", "tests-only")} == {
        "private-imports": [True], "names": [True], "holds": [True, False], "tests-only": [True, True]}
    assert book["dead-code"] and book["untested"]
    assert not any("public" in rule.needs for rule in (*book["dead-code"], *book["untested"]))
```

- [ ] **Step 3: Write the failing tests that only the reader decides, under a language with no prefix**

`tests/modules/rules/application/logic/test_holds.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, profile, source`; append:

```python
@pytest.mark.parametrize("function, expected", [
    pytest.param(Function(3, "helper", public=False), [], id="a function the reader says is not public"),
    pytest.param(Function(3, "_helper"), ["_helper is a function at the top level, but domain/ of modules/docs holds "
                                          "classes (parts.domain.holds)"],
                 id="one it says is public, whatever its spelling"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_functions_are_public(function, expected):
    braced = profile(holds={"domain": "classes"}, language=BRACE)
    file = source("modules/docs/domain/doc.ts", functions=(function,), language=BRACE)
    assert [w.message for w in weak([file], braced, "app")] == expected
```

`tests/modules/rules/application/logic/test_names.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, profile, source`; append:

```python
BRACED = "modules/docs/application/services/doc.ts"


@pytest.mark.parametrize("cls, expected", [
    pytest.param(Class(3, "helper", public=False), [], id="a class the reader says is not public"),
    pytest.param(Class(3, "helper"), [f"app/{BRACED}:3: helper does not match *Service, as every class of services/ "
                                      "of modules/docs must (parts.services.names)"], id="one it says is public"),
    pytest.param(Class(3, "_Shown"), [f"app/{BRACED}:3: _Shown does not match *Service, as every class of services/ "
                                      "of modules/docs must (parts.services.names)"],
                 id="one it says is public, spelled as a private name of another language"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_classes_are_public(cls, expected):
    braced = profile(names={"services": ("*Service",)}, language=BRACE)
    assert [str(v) for v in violations([source(BRACED, classes=(cls,), language=BRACE)], braced)] == expected
```

`tests/modules/rules/application/logic/test_private_imports.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, PERCENT, imp, in_tests, profile, source`; append:

```python
@pytest.mark.parametrize("language, ending", [
    pytest.param(BRACE, "ts", id="the TypeScript-like language"),
    pytest.param(PERCENT, "cls", id="the ObjectScript-like language"),
])
def test_under_a_language_with_no_private_prefix_the_import_says_which_names_it_withholds(language, ending):
    checked = profile(private_imports=True, language=language)
    file = source(f"kernel/x.{ending}", imp(1, "app.kernel.ids", "hidden", "_shown", withheld=("hidden",),
                                            language=language), language=language)
    assert [str(v) for v in violations([file], [], checked, "app", "tests")] == [
        f"app/kernel/x.{ending}:1: imports the private name hidden from app.kernel.ids (private-imports)"]
```

`tests/modules/rules/application/logic/test_dead_code.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, imp, in_tests, profile, source`; append:

```python
@pytest.mark.parametrize("cls, expected", [
    pytest.param(Class(3, "Rule", public=False), [], id="a class the reader says is not public is not read"),
    pytest.param(Class(3, "_Rule"), ["app/modules/docs/application/logic/rule.ts:3: _Rule"],
                 id="one it says is public is, whatever its spelling"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_names_only_the_tests_use(cls, expected):
    braced = profile(dead_code=True, tests_only=True, language=BRACE)
    file = source("modules/docs/application/logic/rule.ts", classes=(cls,), language=BRACE)
    assert listed_only(file, checked=braced) == expected
```

`tests/modules/spec/application/logic/test_profile_needs.py`: `TOY`'s supplies gain `Supply("public", EXACT)`:

```python
TOY = replace(PYTHON, name="toy", checked=replace(
    PYTHON.checked, title="Toy",
    supplies=(Supply("file", EXACT), Supply("import", EXACT), Supply("import.relative", EXACT),
              Supply("import.standard", EXACT), Supply("class", PARTIAL, "a class defined in a branch is not read"),
              Supply("public", EXACT))))
```

and append:

```python
def test_private_imports_is_refused_under_a_language_whose_reader_does_not_say_which_names_are_public():
    unsaid = replace(TOY, checked=replace(TOY.checked, supplies=tuple(
        supply for supply in TOY.checked.supplies if supply.fact != "public")))
    document = layered(language="toy", guards={"private-imports": {}})
    assert problems(document, languages={"toy": unsaid}) == [refusal("guards.private-imports", "public")]
    assert parsed(document, languages=LANGUAGES).approximate == ()
```

- [ ] **Step 4: Run them to verify they fail**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/modules/spec/application/logic/test_profile_needs.py`
Expected: FAIL — the `test_facts` equalities (no `public` trait yet), the filter test (`_shown` dropped, `hidden`
kept, by spelling), `test_vocabulary`/`test_rule`/`test_expansion` (no field `public`), the BRACE/PERCENT rows that
expect a finding (`is_public` reads every brace name public, so the `public=False` rows report), and the
private-imports refusal (no key needs `public` yet).

- [ ] **Step 5: The facts carry the trait**

In `xarch/modules/rules/application/logic/facts.py`, the docstring's table rows become (only the three rows change):

```
    imported-name       each name an import takes, path the module and the name (the module alone for an import of
                        a whole module), the name it takes (None for a whole module); its traits are the import's,
                        and public when the reader says the name it takes is public
```

```
    class               each class defined at the top level, name its name, names those its bases and body mention;
                        exception, record, interface and immutable when it is one (below); public when the reader
                        says it is public
    function            each function defined at the top level or in a class of the top level, name its name, path
                        its class and its name; top-level when it is in no class; public when the reader says it is
                        public; forwards when it is a method the reader says only forwards, text the callee it
                        forwards to and target the attributes it returns of the call's result
```

After `_DOC = frozenset({"doc"})` add

```python
_PUBLIC = frozenset({"public"})
```

The last statement of `_class` becomes

```python
    return frozenset(n for n, on in (("exception", exception), ("record", record),
                                     ("interface", ports.get(cls.name) is cls), ("immutable", cls.immutable),
                                     ("public", cls.public)) if on)
```

`_function` becomes

```python
def _function(function: Function) -> Fact:
    path = (function.owner, function.name) if function.owner else (function.name,)
    public = _PUBLIC if function.public else frozenset()
    if not function.owner:
        return Fact("function", function.line, path, function.name, _TOP | public)
    if not function.forwards or function.sole_call is None:
        return Fact("function", function.line, path, function.name, public)
    return Fact("function", function.line, path, function.name, _FORWARDS | public, target=function.sole_call.then,
                text=function.forwards)
```

and `_imported` becomes

```python
def _imported(file: SourceFile) -> Iterator[Fact]:
    for i in file.imports:
        traits = _TRAITS[i.relative, i.standard, False]
        if i.names is None:
            yield Fact("imported-name", i.line, i.module, traits=traits, text=i.written)
        else:
            yield from (Fact("imported-name", i.line, (*i.module, name), name,
                             traits if name in i.withheld else traits | _PUBLIC, text=i.written) for name in i.names)
```

- [ ] **Step 6: The filter reads the trait**

In `xarch/modules/rules/application/logic/filters.py`, delete `_public` (the function whose body is
`return found.fact.name is not None and profile.language.is_public(found.fact.name)`), and in `_FACT` replace

```python
    "takes-a-name": _takes_a_name, "on-own-object": _on_own_object, "public": _public, "special": _special, "named": _named,
    **{name: _trait(name) for name in ("top-level", "forwards", "exception", "record", "interface", "immutable",
                                       "receiver", "annotated-callable", "no-statements", "exceptions-only",
                                       "unreadable", "doc")},
```

with

```python
    "takes-a-name": _takes_a_name, "on-own-object": _on_own_object, "special": _special, "named": _named,
    **{name: _trait(name) for name in ("top-level", "forwards", "exception", "record", "interface", "immutable",
                                       "receiver", "annotated-callable", "no-statements", "exceptions-only",
                                       "unreadable", "doc", "public")},
```

- [ ] **Step 7: The vocabulary declares the field, and the needs follow**

In `xarch/modules/rules/domain/vocabulary.py`, after `    "doc": "whether a comment is a doc comment",` in
`FIELDS` add

```python
    "public": "whether the name is for other files to use, as the language decides it",
```

Replace the three kinds:

```python
    Kind("imported-name", "each name an import takes, its path what the import names and the name (that alone for "
                          "an import of the whole)",
         ("line", "path", "written", "relative", "standard", "public"), {"name": "takes-a-name"}, needs=_IMPORT,
         field_needs={"relative": ("import.relative",), "standard": ("import.standard",), "public": ("public",)},
         verb="import"),
```

```python
    Kind("class", "each class defined at the top level of a file", ("line", "name", "mentions", "exception", "record",
                                                                    "interface", "immutable", "public"),
         needs=("class",), field_needs={"mentions": ("class.named",), "exception": _CLASS_EXCEPTION,
                                        "record": ("class.methods", "function.returns"),
                                        "interface": ("class.interface",), "immutable": ("class.immutable",),
                                        "public": ("public",)}),
    Kind("function", "each function defined at the top level, or as a method of a class of the top level",
         ("line", "name", "top-level", "forwards", "public"),
         {"forwarded": "forwards", "returned": "returns-an-attribute"}, needs=("function",),
         field_needs={"forwards": ("function.forwards",), "forwarded": ("function.forwards",),
                      "returned": ("function.forwards",), "public": ("public",)}),
```

and the filter:

```python
    Filter("public", "the name the fact carries is public: the language's reader says it is for other files to use",
           FACT, ("public",)),
```

In `xarch/modules/spec/domain/key_table.py`, in `NEEDS`:

```python
    "parts.<part>.holds": ("class", "class.methods", "class.exception", "function", "function.returns", "public"),
```

```python
    "parts.<part>.names": ("class", "public"),
```

```python
    "guards.dead-code.tests_only": ("class", "class.exception", "function", "named", "public"),
```

```python
    "guards.private-imports": (*_IMPORTS, "public"),
```

- [ ] **Step 8: The files built by hand say what the reader would**

These `SourceFile`s are built directly, not through `source`, and their tests lean on a `_` name being private:

`tests/modules/rules/application/test_kept.py`: `Function(3, "__init__", owner="Publishing")` becomes
`Function(3, "__init__", owner="Publishing", public=False)`.

`tests/modules/rules/application/test_holds.py`: `Function(4, "_helper")` becomes `Function(4, "_helper", public=False)`.

`tests/modules/rules/application/logic/test_elsewhere.py`: `PRIVATE = SourceFile("", (), (), functions=(Function(1,
"_validate"),))` becomes `PRIVATE = SourceFile("", (), (), functions=(Function(1, "_validate", public=False),))`.

`tests/modules/rules/application/logic/test_asked.py`: `Function(5, "_check")` becomes
`Function(5, "_check", public=False)`.

Then the tests that see the new texts and needs:

`tests/bootstrap/test_profile_explain_words.py`, in
`test_a_category_lists_its_words_and_a_word_is_explained_with_an_example_from_a_bundled_profile`, replace

```python
    assert word.output.splitlines()[:4] == [
        "filters.public", "  what: the name the fact carries is public in the language: it does not start as a private "
                          "name", "    does", "  about: the fact"]
```

with

```python
    assert word.output.splitlines()[:3] == [
        "filters.public", "  what: the name the fact carries is public: the language's reader says it is for other "
                          "files to use", "  about: the fact"]
```

`tests/modules/spec/application/test_language.py`: `TOY`'s supplies gain `"public": "exact"`:

```python
TOY = PASCAL | {"supplies": {"file": "exact", "import": "exact", "import.relative": "exact",
                             "class": {"partial": "a class defined in a branch is not read"}, "public": "exact"}}
```

`tests/modules/spec/application/test_explain.py`, in `test_a_fact_the_default_language_does_not_grade_is_said_to_be_absent`,
replace

```python
    assert (found.needs, found.graded) == (
        (Need("class", FACTS["class"], Supply("class", "partial", "nested classes are not read")),), True)
    assert (found.short, found.holder, found.name) == (
        (Shortfall("parts.names", "class", "nested classes are not read"),), "part", "names")
```

with

```python
    assert (found.needs, found.graded) == (
        (Need("class", FACTS["class"], Supply("class", "partial", "nested classes are not read")),
         Need("public", FACTS["public"])), True)
    assert (found.short, found.holder, found.name) == (
        (Shortfall("parts.names", "class", "nested classes are not read"), Shortfall("parts.names", "public", None)),
        "part", "names")
```

- [ ] **Step 9: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/modules/spec tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain_words.py`
Expected: PASS. `test_needs_agree` is the arbiter: if it reports a key, its `NEEDS` row is wrong, not the rule.

- [ ] **Step 10: Commit**

```bash
git add xarch/modules/rules/application/logic/facts.py xarch/modules/rules/application/logic/filters.py \
  xarch/modules/rules/domain/vocabulary.py xarch/modules/spec/domain/key_table.py tests/modules/rules \
  tests/bootstrap/test_profile_explain_words.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/modules/spec/application/test_language.py tests/modules/spec/application/test_explain.py
git commit -F - <<'MSG'
The class, function and imported-name facts carry a trait public when the reader says the name is public, and the filter public reads it, applying to those three kinds only, so that holds, names, private-imports and dead-code.tests_only need the fact public; the test builders read a hand-built file as Python's reader would

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 4: The checks that are code read the flags, and `is_public` goes

**Files:**
- Modify: `xarch/modules/rules/application/logic/shared.py` (module docstring; `violations`; `_defined`)
- Modify: `xarch/modules/rules/application/logic/twins.py` (module docstring lines 6-8; `_counted`)
- Modify: `xarch/modules/rules/application/logic/known.py` (`accepting`'s call of `_declared`; `_declared`)
- Modify: `xarch/profile_values/language.py:128-130` (`is_public` deleted)
- Modify: `xarch/modules/spec/domain/key_table.py` (`NEEDS` of `parts.<part>.shared`, `guards.dead-code.known`,
  `guards.no-twins`, `guards.no-twins.min_renamed`, `guards.no-twins.translated`)
- Modify: `tests/profile_values/test_language.py:1-47`
- Modify: `tests/architecture/test_language_seam.py:456-457`
- Test: `tests/modules/rules/application/logic/test_shared.py`, `test_twins.py`, `test_known.py`;
  `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: `Class.public`, `Function.public`, `Constant.public` (Task 2); the `public` trait of `class` and
  `function` facts (Task 3); `source(..., language=...)`, `in_tests(..., language=...)` (Task 3).
- Produces: `CheckedLanguage` with no `is_public`; `known._declared(read: Read, name: str) -> int | None`.

- [ ] **Step 1: Write the failing tests that only the reader decides**

`tests/modules/rules/application/logic/test_shared.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, imp, profile, source`; append:

```python
@pytest.mark.parametrize("cls, expected", [
    pytest.param(Class(40, "Kept", public=False), [], id="a class the reader says is not public is not read"),
    pytest.param(Class(40, "_Kept"), ["app/kernel/ids.ts:40: the class _Kept is used by modules/rules alone, but "
                                      "kernel/ holds only what at least 2 users share (parts.kernel.shared)"],
                 id="one it says is public is, whatever its spelling"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_names_are_public(cls, expected):
    braced = profile(shared={"kernel": 2}, language=BRACE)
    kernel = source("kernel/ids.ts", classes=(cls,), language=BRACE)
    user = source("modules/rules/domain/values.ts", imp(1, "app.kernel.ids", cls.name, language=BRACE),
                  language=BRACE)
    assert problems(kernel, user, checked=braced) == expected
```

`tests/modules/rules/application/logic/test_twins.py`: the builders import becomes
`from tests.modules.rules.builders import APP, BRACE, imp, profile, source`; append:

```python
@pytest.mark.parametrize("first, reported", [
    pytest.param(Class(5, "A", fields=FIELDS, public=False), False, id="a class the reader says is not public"),
    pytest.param(Class(5, "_A", fields=FIELDS), True, id="one it says is public, whatever its spelling"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_classes_count(first, reported):
    braced = profile(no_twins=3, language=BRACE)
    files = [source("modules/docs/domain/values.ts", classes=(first,), language=BRACE),
             source("modules/docs/application/logic/rule.ts", classes=(Class(9, "B", fields=FIELDS),), language=BRACE)]
    assert bool(problems(*files, checked=braced)) == reported
```

`tests/modules/rules/application/logic/test_known.py`: the builders import becomes
`from tests.modules.rules.builders import BRACE, in_tests, profile, source`; append:

```python
BRACED = "modules/docs/application/logic/rule.ts"


@pytest.mark.parametrize("public, then", [
    pytest.param(False, Accepting((absent(BRACED, "Rule"),), ()),
                 id="an entry naming a class the reader says is not public names none"),
    pytest.param(True, Accepting((), (KnownName(f"app/{BRACED}", 3, "Rule"),)),
                 id="one naming a class it says is public is accepted"),
])
def test_under_a_language_with_no_private_prefix_an_entry_is_held_to_what_the_reader_says_is_public(public, then):
    defined = source(BRACED, classes=(Class(3, "Rule", public=public),), language=BRACE)
    tested = in_tests("modules/docs/application/logic/rule.test.ts",
                      functions=(Function(3, "test_rule", named=frozenset({"Rule"})),), language=BRACE)
    checked = profile(dead_code=True, tests_only=True, tests_only_known=(f"{BRACED}:Rule",), language=BRACE)
    assert accepting([defined], checked, "app", [tested]) == then
```

`tests/modules/spec/application/logic/test_profile_needs.py`, append:

```python
UNSAID = replace(PYTHON, name="unsaid", checked=replace(
    PYTHON.checked, title="Unsaid", supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "public")))
"""A language whose reader supplies every fact but public: it does not say which names are for other files to use."""


def test_a_shared_part_is_refused_under_a_language_whose_reader_does_not_say_which_names_are_public():
    document = layered(language="unsaid")
    document["parts"]["service"] |= {"shared": 2}
    assert problems(document, languages={"unsaid": UNSAID}) == [
        "layered.yaml: parts.service.shared: its check reads public (whether a name a file defines, or takes by an "
        "import, is for other files to use, as the language decides it), which the language unsaid does not supply: "
        "drop parts.service.shared, or check the app with a language whose reader supplies public"]
    said = replace(UNSAID, checked=replace(UNSAID.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"unsaid": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "public" in key.needs) == [
        "guards.dead-code.known", "guards.dead-code.tests_only", "guards.no-twins", "guards.no-twins.min_renamed",
        "guards.no-twins.translated", "guards.private-imports", "parts.<part>.holds", "parts.<part>.names",
        "parts.<part>.shared"]
```

Replace `tests/profile_values/test_language.py` lines 1-47 (the module docstring through
`test_a_language_that_gives_no_tokens_has_every_name_public`) with:

```python
"""The language as a check reads it: which names are special, by the pattern its data file gives. Whether a name is
public is no question of the language's: its reader says it, as the fact public."""
import itertools
from importlib import resources

import pytest
import yaml

from xarch.kernel.placement import Marks
from xarch.profile_values.language import NOTHING, CheckedLanguage

PYTHON_SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                .read_text(encoding="utf-8"))["special"]
TOKENS = CheckedLanguage(private="_", special=PYTHON_SPECIAL)
PERCENT = CheckedLanguage(special=r"%\w+")


@pytest.mark.parametrize("name, special", [
    pytest.param("load", False, id="a plain name is not special"),
    pytest.param("_load", False, id="a name that starts as a private one does is not special"),
    pytest.param("__init__", True, id="a special name is special"),
    pytest.param("__load", False, id="one that only starts as a special name does is not special"),
    pytest.param("load__", False, id="one that only ends as a special name does is not special"),
    pytest.param("__", True, id="the affix alone is special"),
    pytest.param("___", True, id="three underscores are special"),
    pytest.param("_x", False, id="one underscore makes no special name"),
])
def test_a_name_is_told_special_by_the_pattern_of_the_language(name, special):
    assert TOKENS.is_special(name) is special


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


def test_a_language_that_gives_no_tokens_has_no_special_name_and_never_says_whether_a_name_is_public():
    assert CheckedLanguage().is_special("__init__") is False
    assert not hasattr(CheckedLanguage(), "is_public")
```

(Keep the file's tests after line 47 as they are; check by reading lines 1-50 before replacing that the original ends
there with `test_a_language_that_gives_no_tokens_has_every_name_public`.)

In `tests/architecture/test_language_seam.py`, the probe

```python
    pytest.param("def f(language: CheckedLanguage):\n    return language.keywords, language.is_public('x')\n",
                 set(), {"keywords"}, id="a read of a parameter annotated as the language"),
```

becomes

```python
    pytest.param("def f(language: CheckedLanguage):\n    return language.keywords, language.extensions\n",
                 set(), {"keywords"}, id="a read of a parameter annotated as the language"),
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 900 uv run pytest -q tests/modules/rules/application/logic/test_shared.py tests/modules/rules/application/logic/test_twins.py tests/modules/rules/application/logic/test_known.py tests/profile_values/test_language.py tests/modules/spec/application/logic/test_profile_needs.py`
Expected: FAIL — the BRACE rows (the checks still ask `is_public`, which reads every brace name public, so
`public=False` is reported or counted), `hasattr(..., "is_public")`, and the shared refusal and the list of keys
that need `public` (`parts.<part>.shared` and the rest do not need it yet).

- [ ] **Step 3: `shared` reads the flag of the definition**

In `xarch/modules/rules/application/logic/shared.py`, the module docstring's first sentence after the title becomes
`Every public name a file of the part defines at the top level (a class, a function a definition alone binds, a name
an assignment binds), public as the language's reader says it is, is used by at least least users, or it is reported
at its definition.` — i.e. replace

```
many users use. Every public name a file of the part defines at the top level (a class, a function a definition alone
binds, a name an assignment binds) is used by at least least users, or it is reported at its definition.
```

with

```
many users use. Every public name a file of the part defines at the top level (a class, a function a definition alone
binds, a name an assignment binds), public as the language's reader says it is, is used by at least least users, or
it is reported at its definition.
```

In `violations`, replace

```python
    for key, (file, line, kind, part) in defined.items():
        least = profile.shared[part]
        shown = sorted(users[key])
        if not profile.language.is_public(key[1]) or len(shown) >= least:
            continue
```

with

```python
    for key, (file, line, kind, part, public) in defined.items():
        least = profile.shared[part]
        shown = sorted(users[key])
        if not public or len(shown) >= least:
            continue
```

Replace `_defined`:

```python
def _defined(files, where: dict[tuple[str, ...], Place | None],
             profile: Profile) -> dict[Name, tuple[SourceFile, int, str, str, bool]]:
    """Every name a file of a shared part binds at its top level, private ones too: the file, the line, what it is,
    the part, and whether the reader says it is public (a function's name is public as that function is)."""
    found: dict[Name, tuple[SourceFile, int, str, str, bool]] = {}
    for file, steps, _ in files:
        at = where[steps]
        if at is None or at.part not in profile.shared:
            continue
        named = [(c.line, c.name, "class", c.public) for c in file.classes]
        named += [(f.line, f.name, "function", f.public) for f in file.functions
                  if not f.owner and f.name in file.module_functions]
        named += [(c.line, c.name, "constant", c.public) for c in file.constants]
        for line, name, kind, public in sorted(named):
            found.setdefault((steps, name), (file, line, kind, at.part, public))
    return found
```

- [ ] **Step 4: `twins` counts the classes the reader says are public**

In `xarch/modules/rules/application/logic/twins.py`, replace the module docstring's paragraph (lines 5-11)

```
A class's fields are the names its body declares with an annotation, in order (see Class.fields), and each field's
type is its annotation as written (Class.types). A class counts when it is defined at the top level of a file of a
part (a package file included), its name is public in the language (it does not start with the private prefix its
data file gives), and none of its bases is one the language marks as an interface (an interface's fields are a
requirement, not a type). Two classes are compared only when their parts have different names: two parts of one
instance of a repeating folder, of two instances, or outside any. Two classes of the same part, in one instance or in
two, are not this check's business, and the tests are never read.
```

with (the same words, the clause on privacy said by the reader, refilled)

```
A class's fields are the names its body declares with an annotation, in order (see Class.fields), and each field's
type is its annotation as written (Class.types). A class counts when it is defined at the top level of a file of a
part (a package file included), the language's reader says it is public, and none of its bases is one the language
marks as an interface (an interface's fields are a requirement, not a type). Two classes are compared only when their
parts have different names: two parts of one instance of a repeating folder, of two instances, or outside any. Two
classes of the same part, in one instance or in two, are not this check's business, and the tests are never read.
```

and in `_counted` replace

```python
        found += [(file, cls, where) for cls in sorted(file.classes, key=lambda c: c.line)
                  if cls.fields and profile.language.is_public(cls.name)
                  and not cls.interface]
```

with

```python
        found += [(file, cls, where) for cls in sorted(file.classes, key=lambda c: c.line)
                  if cls.fields and cls.public and not cls.interface]
```

- [ ] **Step 5: `known` holds an entry to the facts' `public`**

In `xarch/modules/rules/application/logic/known.py`, in `accepting` replace

```python
        line = _declared(read, name, profile) if read is not None else None
```

with

```python
        line = _declared(read, name) if read is not None else None
```

and replace `_declared`:

```python
def _declared(read: Read, name: str) -> int | None:
    """The line of the class the file defines under name, an exception aside, else of its top-level function, the one
    found being public, as the language's reader says; None when the file defines neither so."""
    function = next((f.line for f in read.facts.get("function", ()) if f.name == name and "top-level" in f.traits
                     and "public" in f.traits), None)
    return next((f.line for f in read.facts.get("class", ()) if f.name == name and "public" in f.traits
                 and "exception" not in f.traits), function)
```

- [ ] **Step 6: `is_public` goes, and the needs follow**

In `xarch/profile_values/language.py`, delete

```python
    def is_public(self, name: str) -> bool:
        """Whether a name is for other files to use: it does not start as a private name does, which a special one may."""
        return not (self.private and name.startswith(self.private))
```

(and the blank line before it, so that `gives_nothing` is the last method).

In `xarch/modules/spec/domain/key_table.py`, in `NEEDS`:

```python
    "parts.<part>.shared": (*_IMPORTS, "import.mentioned", "use", "class", "class.named", "function", "function.named",
                            "module_functions", "constant", "import.resolved", "public"),
```

```python
    "guards.no-twins": ("class", "class.fields", "public"),
    "guards.no-twins.min_renamed": ("class", "class.fields", "class.types", "public"),
    "guards.no-twins.translated": ("class", "class.fields", "call", "function", "function.named", *_IMPORTS,
                                   "import.resolved", "public"),
```

```python
    "guards.dead-code.known": ("class", "class.exception", "function", "function.named", "constant", "named", *_IMPORTS,
                               "public"),
```

Run `grep -rn "is_public" xarch tests` — expected: no line.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/modules/spec tests/profile_values tests/architecture/test_language_seam.py tests/bootstrap/test_needs_agree.py`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/rules/application/logic/shared.py xarch/modules/rules/application/logic/twins.py \
  xarch/modules/rules/application/logic/known.py xarch/profile_values/language.py xarch/modules/spec/domain/key_table.py \
  tests/modules/rules/application/logic/test_shared.py tests/modules/rules/application/logic/test_twins.py \
  tests/modules/rules/application/logic/test_known.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/profile_values/test_language.py tests/architecture/test_language_seam.py
git commit -F - <<'MSG'
shared, no-twins and dead-code.known read whether a name is public off what the reader says of its definition, so that their keys need the fact public; CheckedLanguage.is_public is gone, since no check asks the language how a name is spelled

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 5: The texts say privacy by the fact, and a guard keeps `private` to the reader, scaffold and layout

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:512-514` (`case PrivateImports()`)
- Modify: `xarch/architectures/presets/format/keys.yaml:354-361` (`parts.<part>.holds`), `:389-392`
  (`parts.<part>.names`), `:915-920` (`guards.private-imports`)
- Modify: `xarch/modules/spec/domain/values.py:292` (`PrivateImports`' docstring)
- Modify: `tests/fakes/languages/brace.yaml:1-8`, `tests/fakes/languages/percent.yaml:1-6` (header comments)
- Modify: `tests/modules/spec/application/test_explain.py:96`
- Modify: `tests/architecture/test_language_seam.py` (module docstring; new guard at the end)
- Test: `tests/modules/spec/application/logic/test_docs_template.py`, `tests/modules/spec/application/logic/test_key_catalogue.py`,
  `tests/modules/spec/application/logic/test_language_file.py`

**Interfaces:**
- Consumes: nothing new; the seam guard's exemption table names the files Tasks 2-4 left reading `private`.
- Produces: nothing other tasks use.

- [ ] **Step 1: Write the failing tests of the texts**

Append to `tests/modules/spec/application/logic/test_docs_template.py`:

```python
def test_the_private_imports_line_says_the_prefix_the_language_gives():
    lines = [line for line in filled("{{guards}}", guards={"private-imports": {}}).splitlines()
             if "`private-imports`" in line]
    assert lines == ["- `private-imports`: no file of the app or its tests imports a name that starts with `_` from "
                     "another file of them."]


def test_the_private_imports_line_of_a_language_that_gives_no_prefix_says_the_rule_by_what_a_file_keeps_private():
    view = "src/billing/api/view.tsx"
    architecture = parsed(layered(docs=DOCS | {"example_notes": {}}, language="brace", guards={"private-imports": {}}),
                          folders={"ex": (view,)}, languages={"python": PYTHON, "brace": BRACE})
    filled_in = fill("{{guards}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES)
    lines = [line for line in filled_in.splitlines() if "`private-imports`" in line]
    assert lines == ["- `private-imports`: no file of the app or its tests imports a name another file of them keeps "
                     "private."]
    assert "``" not in lines[0]
```

Append to `tests/modules/spec/application/logic/test_key_catalogue.py`:

```python
@pytest.mark.parametrize("address", [
    pytest.param("parts.<part>.holds", id="holds"),
    pytest.param("parts.<part>.names", id="names"),
    pytest.param("guards.private-imports", id="private-imports"),
])
def test_the_texts_that_say_a_public_name_say_it_by_the_reader_and_never_by_the_prefix(address):
    text = catalogue_of(KEYS_DOCUMENT).texts[address]
    said = f"{text.meaning} {text.accepts}"
    assert "%private%" not in said
    assert "the language's reader says" in said
```

Append to `tests/modules/spec/application/logic/test_language_file.py` (it passes already: it pins the test-only
files, which give no `private`, so that only hand-built flags decide their names):

```python
@pytest.mark.parametrize("path", TEST_LANGUAGES, ids=lambda path: path.stem)
def test_a_test_only_language_gives_no_private_prefix_its_reader_saying_which_names_are_public(path):
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert "private" not in document and language_of(path.stem, document).checked.private == ""
```

In `tests/modules/spec/application/test_explain.py`, the `SHAPE` row

```python
    Shown('guards.private-imports', 1, 'no name starting with `_` is imported from another file', False, True),
```

becomes

```python
    Shown('guards.private-imports', 1, 'no name another file keeps private is imported from it', False, True),
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_docs_template.py tests/modules/spec/application/logic/test_key_catalogue.py tests/modules/spec/application/test_explain.py`
Expected: FAIL — the brace line reads ``a name that starts with `` from`` (an empty prefix), the three catalogue rows
hold `%private%`, and the `SHAPE` row differs. The Python docs line passes already (it pins today's bytes).

- [ ] **Step 3: Say it by the fact**

In `xarch/modules/spec/application/logic/docs_template.py`, replace

```python
        case PrivateImports():
            return ("`private-imports`: no file of the app or its tests imports a name that starts with "
                    f"`{architecture.language.checked.private}` from another file of them.")
```

with

```python
        case PrivateImports():
            private = architecture.language.checked.private
            if private:
                return ("`private-imports`: no file of the app or its tests imports a name that starts with "
                        f"`{private}` from another file of them.")
            return "`private-imports`: no file of the app or its tests imports a name another file of them keeps private."
```

In `xarch/architectures/presets/format/keys.yaml`:

`parts.<part>.holds`' `accepts`, replace

```yaml
      classes or functions. classes: no file of the part defines a public function at the top level (a name that does
      not start with `%private%`). functions: no file of the part defines a class at the top level, whatever its name, but for
```

with

```yaml
      classes or functions. classes: no file of the part defines a public function at the top level (one the
      language's reader says other files may use). functions: no file of the part defines a class at the top level,
      whatever its name, but for
```

`parts.<part>.names`' `accepts`, replace

```yaml
      a pattern, or a list of them, with `*` for any text: every public class (a name that does not start with `%private%`)
      defined at the top level in a file of the part matches one of them
```

with

```yaml
      a pattern, or a list of them, with `*` for any text: every public class (one the language's reader says other
      files may use) defined at the top level in a file of the part matches one of them
```

`guards.private-imports`, replace

```yaml
    meaning: no name starting with `%private%` is imported from another file
    accepts: >-
      {}: no file of the app or its tests imports a name that starts with `%private%` (a dunder name aside) from a file of the
```

with

```yaml
    meaning: no name another file keeps private is imported from it
    accepts: >-
      {}: no file of the app or its tests imports a name another file of them keeps private (one the language's reader
      says is not for other files to use, a dunder name aside) from a file of the
```

(the rest of that `accepts`, `app or its tests, \`from x import _y\`; an import of a whole file, ...`, stays).

In `xarch/modules/spec/domain/values.py`, `PrivateImports`' docstring becomes

```python
    """The guard private-imports: no name another file keeps private is imported from it."""
```

The headers of the test-only languages say why they give no `private`. Replace the 8 header lines of
`tests/fakes/languages/brace.yaml` with:

```yaml
# A test-only language that imitates a TypeScript-like one: no profile names it and no reader is written for it. Its
# packages are named as a package manager names them (a scope, a dash, a dot) or as its runtime's own modules
# (node:fs), and a name in one is joined to it by #. It gives its standard library's top-level modules, its reserved
# words and its builtins as lists, so that spec reads them from here and asks no runtime. Its source files end in .ts,
# .tsx or .mts, and index.ts or index.tsx stands for the folder holding it; index.mts is a module like any other. Its
# comments come in three forms, a line one (//), a block one (/* */) and a doc one (/** */), and its tools read two
# directives after the marker of any of them. It gives no private: its names are public or not as its reader says, by
# an export, never by a prefix. The tests load it to show that the profile and the checks read outside names and
# comments by a language's own patterns; later steps add their keys to it.
```

and the 6 header lines of `tests/fakes/languages/percent.yaml` with:

```yaml
# A test-only language that imitates an ObjectScript-like one: no profile names it and no reader is written for it.
# Its names and packages may start with %, and a name in a package is joined to it by a dot. Its source files end in
# .cls or .mac, and it has no package file: no file stands for the folder holding it. Its comments come in four forms,
# two line ones (// and ;), a block one (/* */) and a doc one (///) that runs to the end of its line; the docs print
# the first line marker. It gives no private: its names are public or not as its reader says, by a mark, never by a
# prefix. The tests load it to show that the profile and the checks read outside names and comments by a language's
# own patterns; later steps add their keys to it.
```

No key of either file changes.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec tests/architecture/test_language_seam.py`
Expected: PASS (the format files' seam tests included: no text names the language).

- [ ] **Step 5: Write the guard on who reads `private`, and its probes**

In `tests/architecture/test_language_seam.py`, add to the module docstring, as a paragraph before the one beginning
`EXEMPT names every file or word that stays`:

```
Privacy: how the language starts a private name (its data file's `private`) is read only by the reader, which decides
by it whether each name is public and says so as the fact public, by the services that hand it to the reader, by
scaffold and layout, which refuse a new private name and leave a private folder unmirrored, and by spec, which hands it
to them and prints it. No other file of xarch's code reads an attribute `private` or names `is_private_name`; PRIVACY
lists those that do, with why, and a stale entry fails.
```

Append to the file:

```python
PRIVACY: dict[str, str] = {
    "modules/rules/adapters/fs_source_tree.py": "the reader: it decides by the prefix whether each name is public",
    "modules/rules/application/services/source_check.py": "hands the reader the prefix for the app and the tests",
    "modules/rules/application/services/holding.py": "hands the reader the prefix for the files given and the app's",
    "modules/rules/application/services/sources.py": "hands the reader the prefix for a file another module reads",
    "modules/rules/application/services/asking.py": "hands the reader the prefix for an eval's files",
    "modules/rules/application/services/examples.py": "hands the reader the prefix for the profile's own examples",
    "modules/scaffold/application/logic/names.py": "scaffold refuses a new part or module of a private name",
    "modules/scaffold/application/services/scaffolding.py": "scaffold says the prefix in that refusal",
    "modules/scaffold/adapters/spec_skeleton.py": "hands scaffold the prefix spec publishes",
    "modules/layout/application/logic/requirements.py": "layout requires no private file or folder",
    "modules/layout/application/logic/unmirrored.py": "layout leaves a private folder unmirrored",
    "modules/layout/adapters/spec_skeleton.py": "hands layout the prefix spec publishes",
    "modules/spec/application/services/publishing.py": "publishes the prefix to scaffold and layout",
    "modules/spec/application/logic/explain.py": "fills %private% in the texts of the format",
    "modules/spec/application/logic/docs_template.py": "prints the prefix in the private-imports line when there is one",
}
"""Every file of xarch's code that reads how the language starts a private name, and why it may."""


def privacy_reads(path: Path) -> bool:
    """Whether the file reads how the language starts a private name: an attribute `private` read off anything, or
    `is_private_name` imported, called or read off its module."""
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Attribute) and node.attr in ("private", "is_private_name"):
            return True
        if (isinstance(node, ast.Name) and node.id == "is_private_name") or (
                isinstance(node, ast.alias) and node.name.split(".")[-1] == "is_private_name"):
            return True
    return False


def privacy_readers(root: Path = SRC) -> set[str]:
    """The files below root, but the bundled profiles' example project, that read it."""
    return {path.relative_to(root).as_posix() for path in root.rglob("*.py")
            if not path.relative_to(root).as_posix().startswith("architectures/") and privacy_reads(path)}


def test_only_the_reader_scaffold_layout_and_what_hands_them_the_prefix_read_how_a_private_name_starts():
    assert sorted(privacy_readers() - set(PRIVACY)) == []


def test_every_file_privacy_exempts_still_reads_it():
    assert sorted(set(PRIVACY) - privacy_readers()) == []


@pytest.mark.parametrize("code", [
    pytest.param("def f(profile):\n    return profile.language.private\n", id="the prefix read off the language"),
    pytest.param("from xarch.kernel.logic.names import is_private_name\n", id="the test of a private name imported"),
    pytest.param("from xarch.kernel.logic import names\n\n\ndef f(x, p):\n    return names.is_private_name(x, p)\n",
                 id="the test called through its module"),
])
def test_the_privacy_guard_finds_the_prefix_read_in_a_file_of_the_rules_logic(tmp_path, code):
    folder = tmp_path / "modules" / "rules" / "application" / "logic"
    folder.mkdir(parents=True)
    (folder / "filters.py").write_text(code)
    assert privacy_readers(tmp_path) == {"modules/rules/application/logic/filters.py"}
```

- [ ] **Step 6: Run the guard**

Run: `timeout 300 uv run pytest -q tests/architecture/test_language_seam.py`
Expected: PASS. If `test_only_the_reader_...` names a file, that file reads `private` outside the reader, scaffold,
layout and spec: stop and report it (do not add it to `PRIVACY` without a reason the spec's 2.5 gives). If
`test_every_file_privacy_exempts_still_reads_it` names one, drop that entry.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/docs_template.py xarch/architectures/presets/format/keys.yaml \
  xarch/modules/spec/domain/values.py tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml \
  tests/modules/spec/application/logic/test_docs_template.py tests/modules/spec/application/logic/test_key_catalogue.py \
  tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/test_explain.py \
  tests/architecture/test_language_seam.py
git commit -F - <<'MSG'
The private-imports docs line prints the prefix only when the language gives one and otherwise says a name another file keeps private; the format's texts say a public name is one the language's reader says other files may use; a seam guard keeps the prefix to the reader, what hands it to the reader, scaffold, layout and spec

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 6: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:146-156` (language paragraph), `README.md:306` (`private-imports` row)
- Modify: `CHANGELOG.md` (`[Unreleased]`: first bullet of `### Added`, first bullet of `### Changed`)
- Throwaway, never committed: `/tmp/xarch-3-9/regenerate_docs.py`

**Interfaces:**
- Consumes: everything above.
- Produces: nothing.

- [ ] **Step 1: The README says what `private` decides, and the row says the rule by the fact**

In `README.md`, replace lines 146-156 (from `and the tokens of its code the checks and the docs need: what a name may
be, ...` through `` `dataclasses.dataclass(frozen=True)`). ``) with exactly:

```markdown
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
(`branching_expressions`), and what makes a class an immutable record (`immutable`: a base, or a decorator called with
its keywords, such as `dataclasses.dataclass(frozen=True)`).
```

(12 lines in place of 11; the line after, `The rest of what a check knows of the language is one adapter, ...`, stays.)

Replace the row

```markdown
| `private-imports` | an import of a name starting with `_` from another file of the app or its tests | `guards.private-imports` |
```

with

```markdown
| `private-imports` | an import of a name another file of the app or its tests keeps private (for Python, one starting with `_`) | `guards.private-imports` |
```

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 2: The CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, insert as the first bullet of `### Added` (before `- The fact
\`comment.doc\`, ...`):

```markdown
- The fact `public`, whether a name a file defines, or takes by an import, is for other files to use, as the language
  decides it, which `parts.<part>.holds`, `parts.<part>.names`, `parts.<part>.shared`, `guards.private-imports`,
  `guards.dead-code.tests_only`, `guards.dead-code.known` and `guards.no-twins` (with `min_renamed` and `translated`)
  need; a language that does not supply it is refused those keys with the needs text. The reader says it of each
  class, function, constant and name an import takes (`Class.public`, `Function.public`, `Constant.public`, and
  `Import.withheld`, the names an import takes that are not public), handed the language's `private` to decide it.
  Python supplies it, computed from `private` as before.
```

and as the first bullet of `### Changed` (before `- A language's data file says how its comments are written ...`):

```markdown
- The filter `public` reads the fact `public`, never how a name is spelled, and applies to `class`, `function` and
  `imported-name` only: written on another kind in a check of your own, `profile check` refuses it (`public does not
  apply to <kind>`). `CheckedLanguage.is_public` is gone. Under a language that gives no `private`, the docs line of
  `private-imports` says "a name another file of them keeps private". No finding of a Python app changes.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-9/regenerate_docs.py` (never committed):

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
mkdir -p /tmp/xarch-3-9
uv run python -I /tmp/xarch-3-9/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
grep -n "private-imports" docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md
```

Expected: three `written` lines, an empty `git diff`, and each `private-imports` line reading
``- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file of them.``
If the diff is not empty, stop and report it with the diff (`git checkout -- docs/cli docs/web docs/xarch` restores
the files). The docs must not move.

- [ ] **Step 4: Run the gates**

Run the suite in the background with a recorded PID, the rest in the foreground, then read the log:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-9/pytest.log 2>&1 & echo $! > /tmp/xarch-3-9/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-3-9/pytest.log`.

Expected: the suite passes (corpora, golden-doc, needs-agree, self-check and seam tests included), both checks
report no violation, ruff reports nothing, the profile check loads. `git status --short` shows no change under
`tests/bootstrap/corpora/` and nothing under `.claude/` staged; `git diff main -- xarch/architectures/presets/language/python.yaml`
shows only the header lines of `private` and `public: exact` (beside the lines 3.8 changed, if `main` predates it);
`grep -rn "is_public" xarch tests` prints nothing.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'MSG'
The README's language paragraph says private is what the Python reader decides the fact public by and what scaffold and layout refuse and skip, its private-imports row says the rule by what another file keeps private, and the CHANGELOG adds the fact public and says the filter public reads it; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

## Self-review against the spec

**Coverage, section by section.**

- 2.1 `FACTS["public"]` after `comment.doc`, `python.yaml` `public: exact` and the header's `private` words: Task 1.
  A language not supplying `public` refused with today's needs text: Task 3 (`guards.private-imports`), Task 4
  (`parts.<part>.shared`, and the list of every key that needs it). Nothing refused for Python: Task 1
  (`test_python_supplies_every_fact_a_bundled_check_reads`), Task 6 (`profile check architecture.yaml`).
- 2.2 `Class`/`Function`/`Constant.public`, `Import.withheld` (not `private`), defaults public: Task 2
  (`test_parsed.py`). `module_functions` keeps no flag; `shared` reads the function's: Task 4. The reader's rule,
  special names and `as` imports: Task 2. `read`/`parsed` take a required keyword `private`; every service hands
  `profile.language.private`; `source_reading.py` hands `""`: Task 2 (`test_private_handed.py`,
  `test_the_reader_must_be_handed_the_prefix`).
- 2.3 The trait on `class`, `function`, `imported-name` (none on a whole-module import), the filter reading it, the
  vocabulary's field, field needs and meaning: Task 3. The refusal on another kind: Task 3 (`test_rule.py`).
  `shared`, `twins`, `known` read the flags; `is_public` deleted; their docstrings and the `facts.py` table: Task 4
  and Task 3.
- 2.4 `NEEDS`: Task 3 (engine keys, held by `test_needs_agree.py`), Task 4 (code checks); `guards.dead-code` and
  `.untested` untouched and pinned (Task 3, `test_expansion.py`; Task 4, the sorted list of keys needing `public`).
- 2.5 Who reads `private`: Task 5 (`PRIVACY`, stale entries fail, probes in a rules-logic file).
- 2.6 Docs line (byte-identical for Python, the no-prefix sentence otherwise), `keys.yaml` texts, `PrivateImports`'
  docstring, the filter's meaning: Task 5 and Task 3; the golden docs never reached: Task 6 Step 3.
- 2.7 Findings, corpora, golden docs, `special`, scaffold and layout untouched: Task 6 gates; the corpora are read
  (unpacked into `tmp_path`) and never written (Task 2).
- 3 Test-only languages give no `private` and say why: Task 5; neutrality under `BRACE` (and `PERCENT` for
  `private-imports`): Tasks 3 and 4.
- 4 Tests 1-29: 1-3 Task 2 (`test_fs_source_tree_public.py`); 4-7 Task 2; 8, 10, 11, 12 Task 3; 9, 13, 14 Task 4;
  15 Task 3 (builders, and the four direct `SourceFile`s); 16-20 Task 3; 21 Task 4; 22 Tasks 3 and 4; 23 Task 1;
  24, 25 Task 5 (25 through the catalogue texts, the source of `profile explain`); 26 Tasks 4 and 5; 27-29 Task 6.
- 5 README, CHANGELOG, golden docs: Task 6. `docs/examples/**`: checked, no copy of a changed file
  (no `is_public`, `standard=` or `private` in them), so none moves.

**Placeholder scan.** No "TBD", no "similar to", no step without its code; the two mechanical rewrites (the adapter
test's calls, Task 2 Step 2) are given as an exact script with its expected count (16) and the two lines it makes too
long rewritten by hand.

**Names across tasks.** `public` (field and trait and fact), `withheld`, `private=` (keyword), `prefixes` (fake),
`read_as`, `imp(..., withheld=...)`, `source(..., language=...)`, `_PUBLIC`, `_declared(read, name)`, `PRIVACY`,
`privacy_reads`, `privacy_readers` are each defined once and used with the same spelling in later tasks.

**Order.** Task 1 needs nothing. Task 2's reader and services stand alone (the checks still ask `is_public`, so no
finding moves). Task 3 makes the facts and the filter read the flags; its `NEEDS` rows land with the rules that need
them, so `test_needs_agree.py` holds at every commit. Task 4 removes the last callers of `is_public` and the method in
one commit. Task 5's guard is written after Task 4, when the set of readers is final.
<!-- task-pipeline: validated -->
