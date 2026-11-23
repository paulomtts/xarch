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
