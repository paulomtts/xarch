# 3.7 language: several source extensions with an optional package file

Card `1d9a0cdb`, subtask of `3c7754c4`. Release step 8b of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3, line 268:
"`extensions`, optional `package_files`, `file.package`, the stem helper. | language-neutral 7 | Step 7. Before 23
(file keys hold an extension).").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below **LN**),
section 7 (lines 782-846). Release-wide rules this step inherits: R3 O4, O5 (lines 228-229: README and CHANGELOG
under `[Unreleased]`), O7 (line 231: `file.package` is the fact of 8b, placed after `import.resolved` and
`class.interface` in `FACTS`, `python.yaml` `supplies`, `NEEDS`, `test_needs_agree.py`), O8 (line 232: golden docs
regenerated, diff read; none expected for 8b), O18 (line 242: `python.yaml` is edited by 8b, its lines only). Dodges
that apply (card): a hidden default (`extensions` meaning `[.py]`, LN line 1150 "Hidden defaults in the code"); letting
the corpora move (LN 7.5, line 830: "findings, corpora and golden docs do not move"); and "a step is not done without
its test-only file" (LN line 1143).

## 1. Goal

A language's source files may end in one of several endings, and a language may have a file that stands for the
folder holding it, several such names, or none (LN 7.1, lines 784-799). The data file says so with two list keys,
`extensions` (required) and `package_files` (optional), replacing the scalars `extension` and `package_file`. A new
fact `file.package` says the language has a package file; a key whose check cannot mean anything without one is
refused under a language that has none (LN 7.2, lines 801-810). The checking code stops assuming one ending and one
package file: one kernel helper gives a source file's stem (LN 7.3, lines 812-820). Python's findings, the recorded
corpora and the golden docs do not move: `[.py]` and `[__init__.py]` read exactly as today's two keys (LN 7.5,
line 830).

## 2. Observable behavior

### 2.1 The data file (LN 7.1, 7.4)

- `extension` and `package_file` are no longer keys. Written, either is an unknown key, refused with today's unknown-key
  text (`unknown key 'extension': use ...`), listing the new key set; no retired-keys entry or hint (LN 7.1, lines
  797-799: "renamed with no retired-keys entry").
- `extensions` is required: missing, the file is refused with ``missing `extensions` `` (the `REQUIRED` tuple gains it
  in the place `extension` held). No default applies anywhere in the code (dodge: hidden default).
- `extensions` must be a non-empty list of strings, each a dot and a name as today's `_EXTENSION` pattern
  (`\.[A-Za-z0-9]+`) fully matches, no item listed twice. Any other value (a string, an empty list, a list holding a
  non-string, an item with no dot, an item listed twice) gives exactly one problem for the key:
  `extensions: must be a non-empty list of endings, each starting with a dot` (LN 7.4, line 823).
- `package_files` is optional. Given, it must be a non-empty list of strings, no item listed twice; otherwise one
  problem: `package_files: must be a list of file names, each ending in one of extensions`. Each item that ends in
  none of the extensions, or is only an extension (`.py`), gives one problem per item:
  `package_files: 'index.js' ends in none of extensions` (the item by `repr`; LN 7.4, line 823-824). When
  `extensions` is itself refused, the items of `package_files` are not checked against it (the file is refused anyway).
- `supplies` may not name `file.package`: written there (with any grade) it is refused with
  `supplies: file.package follows package_files: drop it from supplies` (LN 7.2, line 805-806), one problem, in place
  of the grade check for that entry.
- When the file gives `supplies`, the language's supplies are those listed plus `file.package` graded `exact` exactly
  when `package_files` is given; with no `package_files`, `file.package` is not supplied. When the file gives no
  `supplies` (`None`: no key is held to a reader), it stays `None` whatever `package_files` says.
- The module docstring of `language_file.py` and the header comment of `python.yaml` describe the two keys
  (`extensions`: the endings of a source file's name, the first the one messages print; `package_files`: the names of
  the files that stand for the folder holding them, each ending in one of the extensions; optional) and say that
  `file.package` follows `package_files`.
- The top-level refusal for a document that is no mapping names the new keys: `must be a mapping of keys, such as
  title, extensions and package_files`.

`python.yaml` (R3 O18): exactly the two lines rewritten, `extensions: [.py]` and `package_files: [__init__.py]`, plus
its header words for them; `supplies` does not list `file.package` (it follows `package_files`).

### 2.2 The language value (LN 7.3, line 814-816)

- `xarch/kernel/placement.py` `Marks` becomes `Marks(extensions: tuple[str, ...] = (), package_files: tuple[str, ...]
  = ())`; empty marks still leave a path as written.
- `xarch/profile_values/language.py` `CheckedLanguage` replaces `extension: str` / `package_file: str` with
  `extensions: tuple[str, ...] = ()` / `package_files: tuple[str, ...] = ()`, in the written order; `.marks` builds
  `Marks(self.extensions, self.package_files)`. Docstring updated. A property `extension` (the first, or `""`) may be
  given for messages; the planner decides, but no reader may use the first extension to decide what a source file is.
- `FACTS` (`xarch/profile_values/capabilities.py`) gains `"file.package": "a file stands for the folder that holds it"`
  (LN 7.2, line 804), placed after `class.interface` (R3 O7).

### 2.3 The stem helper (LN 7.3, lines 814-817)

One function in `xarch/kernel/logic/placement.py`, `stem(name: str, marks: Marks) -> str | None`: the name without the
extension it ends in, the longest such extension when several match; `None` when it ends in none of them. Every
reader that removed `.extension` or tested `.endswith(extension)` calls it (or tests `stem(...) is not None`):

- `module_steps(path, marks)`: the last step loses the extension it ends in; a step ending in none is kept as written
  (as `removesuffix` keeps it today); then a path that stands for its folder loses its last step.
- `stands_for_folder(path, marks)`: true when the last step is one of `package_files`, or ends in no extension and
  equals the stem of one of them (the "written without its ending" case, used when patterns are compared). So under
  `brace`, `a/index.ts`, `a/index.tsx` and `a/index` stand for `a/`; `a/index.mts` does not (it is no listed package
  file). Under a language with no package files, no path stands for its folder. Python: `__init__.py` and `__init__`,
  as today.

### 2.4 The readers converted (LN 7.2, 7.3, 7.6; recount with `grep -rnE 'package_file|\.extension\b' xarch`)

What decides whether a file is a source file reads every extension; what a message prints reads the first.

- **Reading files:** the `SourceTree` port's `paths(root, extensions: tuple[str, ...])` gives the path below root of
  every file whose name ends in one of the extensions, each once, sorted as today (`FileSystem.files` sorts per glob;
  the union is sorted the same way). `FsSourceTree.paths` globs each extension. Callers hand
  `profile.language.extensions`: `services/source_check.py:73-80` (app and tests), `services/holding.py:35`,
  `services/sources.py:43` (LN 7.2, line 803). The fake `tests/fakes/filesystem.py` `FakeSourceTree.paths` takes the
  tuple.
- **Deciding a file is source:** `rules/application/logic/sources.py:24,45`, `tier_of.py:66`, `where.py:116-117`,
  `spec/.../example_imports.py:36`, `evals.py:325-327`, `written_checks.py:268`, `profile_parsing.py:832` accept a
  name that ends in any extension (via `stem`).
- **Package-file checks:** `where.py:121` (`steps[-1] == language.package_file`) becomes "the path stands for its
  folder" (`stands_for_folder`), `where.py:123` the stem helper; `rules` `filters.py:64` `package-file` is unchanged in
  code (it reads `read.package`, which `dotted` now works out from the lists).
- **Messages and docs print the first extension:** `written.py:66` (`%extension%`), `explain.py:35` (`extension`),
  `where.py:119` (sample), `evals.py` refusal (`ending in .py`), `written_checks.py:270`, `profile_examples.py:85`,
  `profile_parsing.py:821`, `profile_checks.py:167,393,397,503`, `docs_template.py:264` (a fence of a file whose suffix
  is any of the extensions is named after the language). `%package_file%` (`explain.py:35`) and `docs_template.py:536`
  (`closed-tree`) print the first package file; for Python, `__init__.py` as today.
- **Scaffold and init:** the spec contract `Skeleton.package_file` (`spec/contract/__init__.py:69`), scaffold's
  `Language.package_file` (`scaffold/domain/values.py:36`), `publishing.py:52`, `project_files.py:51` keep one name:
  the first package file, `""` when the language has none. `scaffold/application/logic/plan.py` with `""` writes no
  package file at all (neither at the root nor in folders), instead of a file named `""`. Python: unchanged.
- **Test-file patterns** (`profile_checks.py:56-63`, LN 7.3 lines 818-819, 7.4 line 825): a `testing.files` pattern is
  a file name with no `/`, at least one character before an ending, that ends in one of the extensions (`*` for any
  text); a file name (`_file_name`) is the same with no `*`. The ASCII class is dropped. The refusal texts keep their
  words with the extensions listed: one extension prints as today (`a name ending in .py, with `*` for any text`);
  several as `.ts, .tsx or .mts`; the non-empty-list refusal reads `each a .py name` for one, `each a .ts, .tsx or .mts
  name` for several. Python's texts do not change.

### 2.5 `file.package` and what needs it (LN 7.2, lines 807-810)

- `NEEDS` (`spec/domain/key_table.py:194-238`) gains `file.package` for `parts.<part>.package_only` (LN: "A language
  with no package file then refuses `package_only` with the existing message"), and for every key the engine expands
  to a rule that reads the filter `package-file` *as written* (not negated): `parts.<part>.must_import` (the exemption,
  `expansion.py:270`; LN's "exemption of `imports.must`", `imports.must` being that key's later name) and
  `guards.dead-code.untested` (`expansion.py:320`, the same exemption). `tiers.<tier>.must_import` reads no
  `package-file` and gains nothing.
- Rule side, so that `tests/bootstrap/test_needs_agree.py` stays green: a rule needs `file.package` when one of its
  conditions is `package-file` not negated, or `target-inside-part` (the word of `package-only` that tells "one of the
  part's files" from "the part as a package"; used by no other bundled rule). A negated `not package-file` (the `where`
  of `holds`, `immutable`, `dead-code`, `dead-code.tests_only`, and the bundled eval in `keys.yaml:95`) needs nothing:
  with no package file every file passes it, which is what those checks mean, so a language without package files
  can still set them. How the vocabulary carries this (e.g. a facts-needed field on `Filter` that `Rule.needs` reads
  for non-negated conditions) is the planner's; `profile explain kinds/filters` show it where they show needs today.
- An own check (a `checks.<id>` rule a profile writes) with `package-file` (not negated) in any slot is refused under a
  language that does not supply `file.package`, with today's shortfall text for checks.
- `parts.<part>.package_only` under a language with no `package_files` is refused with today's needs text:
  `<file>: parts.<part>.package_only: its check reads file.package (a file stands for the folder that holds it), which
  the language <name> does not supply: drop parts.<part>.package_only, or check the app with a language whose reader
  supplies file.package` (LN 7.4, line 824-825).
- Python supplies `file.package` (`package_files` given), so `test_python_supplies_every_fact_a_bundled_check_reads`
  keeps holding; nothing Python refuses changes.

### 2.6 Things that stay as they are

- Python's findings on every profile; the recorded corpora (`tests/bootstrap/corpora/`), never edited; the golden docs
  `docs/{cli,web,xarch}/testing.md`, regenerated with the repo's command and their diff read, expected empty (R3 O8).
- `uv run xarch check`, `--strict`, `xarch profile check architecture.yaml` on xarch itself.
- `keys.yaml` text (`%extension%`, `%package_file%` keep their words and print the first item).

## 3. The test-only language files (LN 7.5, lines 827-830; dodge line 1143)

- `tests/fakes/languages/brace.yaml`: `extensions: [.ts, .tsx, .mts]`, `package_files: [index.ts, index.tsx]`
  (LN 7.1 line 792-793); header says it.
- `tests/fakes/languages/percent.yaml`: `extensions: [.cls, .mac]` and no `package_files` (the card: "a test-only
  language with two extensions and no package file"); header says it has none. It gives no `supplies`, so tests that
  need `file.package` refused build a percent language with a `supplies` list (as `test_profile_needs.py` builds Toy).
- `tests/modules/rules/builders.py` (`PYTHON`, `BRACE`, `PERCENT` `CheckedLanguage`s), `tests/modules/spec/languages.py`,
  `tests/fakes/scaffold_skeleton.py`, and every test building `Marks(` or `CheckedLanguage(extension=...)` move to the
  lists. Tests that leaned on `Package.cls` (grep finds none beyond the file) or on brace's `.ts` alone keep their
  expectations.
- `tests/architecture/test_language_seam.py:154-156`: reads `data["package_files"]` (each item's stem) and
  `data["extensions"]` (each, escaped, joined as alternatives) from `python.yaml`; its snippet at ~338-341, ~426 that
  writes `lang.extension` uses the new name. The guard still finds `__init__` anywhere outside the reader and presets.

## 4. Tests (written first)

Unit = pure logic or a service with fakes, no disk; adapter = real adapter against tmp files; architecture = the
repository guards; bootstrap = the wired app end to end.

### 4.1 Loader — `tests/modules/spec/application/logic/test_language_file.py` (unit: `language_of` is pure)

1. `extensions: [.ts, .tsx]`, `package_files: [index.ts]` read into `checked.extensions == (".ts", ".tsx")`,
   `checked.package_files == ("index.ts",)`, in the order written.
2. `package_files` left out reads `()`; the file loads.
3. Each wrong `extensions` gives exactly one `extensions: must be a non-empty list of endings, each starting with a
   dot` (parametrized: `.py` as a string, `[]`, `[3]`, `[py]`, `[.py, .py]`, `[".p y"]`).
4. `extensions` missing gives ``missing `extensions` ``.
5. `package_files: [index.js]` under `[.ts]` gives `package_files: 'index.js' ends in none of extensions`; two bad
   items, two problems; `[.ts]` alone (only the ending) refused the same way.
6. `package_files: index.ts` (no list) and `[]` give the one shape problem.
7. `extension: .py` and `package_file: __init__.py` are unknown keys (one problem naming both), no hint.
8. `supplies: {file.package: exact}` gives `supplies: file.package follows package_files: drop it from supplies`.
9. With `supplies` given: `file.package` is supplied `exact` iff `package_files` is given. With no `supplies`,
   `checked.supplies is None` both ways.
10. Every file of `tests/fakes/languages/` loads (existing test), and `python.yaml` reads `(".py",)`,
    `("__init__.py",)` and supplies `file.package` exactly.

### 4.2 Stem and placement — `tests/kernel/logic/test_placement.py` (unit: kernel is pure)

11. `stem` under brace marks: `b.tsx → b`, `b.ts → b`, `b.mts → b`, `b.js → None`; the longest matching extension
    wins (marks `(".ts", ".d.ts")`: `x.d.ts → x`).
12. `place_of` under brace marks puts `a/b.tsx` and `a/index.ts` in the part of `a/` (LN 7.5 line 827-828), and
    `a/index.tsx` stands for `a/`; `a/index.mts` does not stand for its folder.
13. With no package files (percent marks) nothing stands for its folder: `module_steps(("a", "Package.cls"))` is
    `("a", "Package")`.
14. Python marks: existing `module_steps`/`stands_for_folder` cases unchanged (`__init__.py`, `__init__`).

### 4.3 Reader paths — `tests/modules/rules/adapters/test_fs_source_tree.py` (adapter: real filesystem)

15. In a tmp tree with `a.ts`, `b/c.tsx`, `d.js`, `paths(root, (".ts", ".tsx"))` gives `[("a.ts",), ("b", "c.tsx")]`
    sorted, `d.js` left out; each file once. `(".py",)` gives today's list.

### 4.4 Rules readers (unit: logic over hand-built files and profiles)

16. `tests/modules/rules/application/logic/test_sources.py` (or the file testing `sources.py`): a `.tsx` file is a
    source file under brace; a `.js` one is not.
17. `where.py` (`tests/.../test_where.py`): the mirror test file name of `a/b.tsx` under brace with pattern `*.test.ts`
    is `b.test.ts`; `a/index.tsx` gets no test file name (stands for its folder).
18. `tier_of.py`: a tier pattern ending in `.tsx` counts as a source file under brace.
19. Service tests (`tests/modules/rules/application/`, `FakeSourceTree`): `SourceCheckService`, `HoldingService` and the
    sources service hand `profile.language.extensions` to `paths`.

### 4.5 Spec readers (unit)

20. `test_profile_checks.py` (or where `testing.files` is tested): under brace, `*.test.tsx` and `*.test.mts` load;
    `*.test.js` refused with `... a name ending in .ts, .tsx or .mts, with `*` for any text`; under Python the text is
    today's `.py` one (verbatim existing test kept); a non-ASCII name such as `tést_*.py` loads; `a/test_*.py` refused.
21. `test_written_checks.py`, `test_evals.py`, `test_profile_examples.py`, `test_profile_parsing.py`: under brace, an
    example path ending `.tsx` is accepted; the refusal text prints `.ts` (the first).
22. `test_explain.py`: `words(brace)` gives `extension: .ts`, `package_file: index.ts`; for a language with no package
    files `package_file` is `""`.

### 4.6 `file.package` needs (unit, spec side)

23. `tests/modules/spec/application/logic/test_profile_needs.py`: a percent-like language with `supplies` listed and no `package_files` refuses
    `package_only: true` with the needs text of 2.5 (LN 7.5 line 829), and the same profile without `package_only`
    loads; `holds`, `immutable` and `guards.dead-code` load under it (negated filter needs nothing).
24. `must_import` on a part and `guards.dead-code.untested` are refused under that language naming `file.package`.
25. `test_key_catalogue.py` / NEEDS tests: `FACTS` holds `file.package` after `class.interface`; every key's needs stay
    within `FACTS`.

### 4.7 Rule needs (unit, rules side) — `tests/modules/rules/domain/test_rule.py`

26. A rule with `exempt: package-file` needs `file.package`; with `where: not package-file` it does not; a rule with
    `keep: target-inside-part` needs it.

### 4.8 Scaffold (unit) — `tests/modules/scaffold/application/logic/test_plan.py`

27. `plan(entries, "")` lists only the entries' files, no package file; `plan(entries, "__init__.py")` unchanged.

### 4.9 Guards (architecture) and end to end (bootstrap)

28. `test_language_seam.py` and `test_agnostic.py` green, reading the new keys of `python.yaml`.
29. `tests/bootstrap/test_needs_agree.py` green with `EVERY_KEY` unchanged (it sets `package_only`, `must_import`,
    `dead-code.untested`): spec's table and the expanded rules agree on `file.package`.
30. The corpora tests and the golden-doc tests pass unchanged (`tests/bootstrap/`).

## 5. Docs (R3 O4, O5, O8)

- `README.md` language paragraph (lines 137-153): "the ending of a source file, the file that stands for a folder"
  becomes the endings of a source file (`extensions`, a list; the first is the one messages print) and the files that
  stand for a folder (`package_files`, optional); and, in the `supplies` paragraph (line 159-), that `file.package`
  follows `package_files` and is never written under `supplies`.
- `CHANGELOG.md` `[Unreleased]`: under `### Changed`, `extension`/`package_file` became `extensions` (a list) and
  optional `package_files`, with the three loader refusal texts of 2.1 quoted and no finding of a Python app moving;
  under `### Added`, the fact `file.package` and that `package_only`, a part's `must_import` and
  `guards.dead-code.untested` need it.
- Golden docs regenerated with the repo's command, diff read, expected empty; never edited by hand.
- `docs/examples/**` copies of changed files (`profile_values/language.py`, `ports/source_tree.py`,
  `adapters/fs_source_tree.py`, `services/app_check.py`): regenerated or updated only if a test or the docs generator
  holds them to the code; the planner checks which.

## 6. Out of scope

- The tree's file keys (story 7; R3 step 23, "file keys hold an extension").
- Comment forms, privacy, records (LN sections 8-10; release steps 8c-8e, sibling cards).
- A reader for any language but Python; Python with more than `.py` (e.g. `.pyi`).
- Choosing a package file among several when writing one (init/scaffold write the first; no key picks another).
- Any retired-keys entry or migration hint for `extension`/`package_file`.
- Editing the recorded corpora.

## 7. Gates

Each passes on this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background
with `timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`.

Project rules: no comments in xarch's code (docstrings as the code base writes them); tests first; examples simple,
with absolute `app.` imports; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.

## 8. Review focus (for the planner)

1. A file name matching two extensions (`.ts` and `.d.ts`): the longest wins in `stem`; `paths` lists the file once.
2. A brace `index.mts`: a source file, not a package file; it is placed in its folder's part as a module `index`.
3. Init/scaffold under a language with no package file: no empty-named file is written.
4. Python's `testing.files` refusal texts are byte-identical to today's.
5. `file.package` never appears in `python.yaml`'s `supplies`, yet Python supplies it.

---

# 3.7 language: several source extensions with an optional package file — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A language's data file says its source endings as a list (`extensions`) and its package files as an optional
list (`package_files`); a new fact `file.package` follows `package_files`; every reader decides "is a source file" with
one kernel helper `stem`, and Python reads exactly as today.

**Architecture:** The kernel's `Marks` becomes two tuples and gains `stem(name, marks)`; `module_steps` and
`stands_for_folder` are rewritten over it (Task 1). Spec's loader reads the two list keys into `CheckedLanguage`, which
keeps two read-only properties, `extension` and `package_file` (the first of each, `""` when none), only for what a
message prints, what init writes and `%extension%`/`%package_file%` (Task 2). Rules' readers then list files by every
ending and decide source with `stem` (Task 3); spec's readers do the same and the `testing.files` texts list every
ending (Task 4). The new fact is wired on both sides: spec's `NEEDS` table, and a `facts` field on rules' `Filter` that
`Rule.needs` reads for a condition written as is, never negated (Task 5). Docs and gates last (Task 6).

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/3-7-language-several-1d9a0cdb.md` (prepended above).

## Global Constraints

- `extension` and `package_file` are no longer data-file keys; written, they are unknown keys with today's text, no
  retired-keys entry, no hint.
- `extensions` is required (``missing `extensions` ``); no default `[.py]` anywhere in the code.
- Refusal texts, verbatim: `extensions: must be a non-empty list of endings, each starting with a dot`;
  `package_files: must be a list of file names, each ending in one of extensions`;
  `package_files: 'index.js' ends in none of extensions` (the item by `repr`);
  `supplies: file.package follows package_files: drop it from supplies`;
  `must be a mapping of keys, such as title, extensions and package_files`.
- `FACTS` gains `"file.package": "a file stands for the folder that holds it"`, placed right after `class.interface`.
- `python.yaml`: only `extensions: [.py]`, `package_files: [__init__.py]` and the header words for them change;
  `supplies` never lists `file.package`.
- What decides whether a file is a source file reads every extension (`stem`); only messages, docs, `%extension%`,
  `%package_file%` and init read the first (the `extension`/`package_file` properties).
- Python's findings, `tests/bootstrap/corpora/` (never edited) and the golden docs `docs/{cli,web,xarch}/testing.md`
  (regenerated, diff empty) do not move.
- No comments in xarch's code (docstrings as the code base writes them); tests first; Python only in the reader
  adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- `profile_values/` may import only `kernel` (not `kernel/logic`), so `CheckedLanguage` gets no method that calls
  `stem`; readers call `stem(name, language.marks)` themselves.
- Gates (Task 6): `uv run pytest -q` (run in the background with `timeout`), `uv run xarch check`,
  `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Review Focus

1. A name that two endings match (`.ts` and `.d.ts`): `stem` takes the longest; `paths` lists the file once. Pinned in
   Task 1 (`test_the_longest_ending_a_name_carries_is_the_one_it_loses`) and Task 3
   (`test_the_files_listed_are_those_whose_name_ends_in_one_of_the_endings_given_each_once`).
2. A brace `index.mts`: a source file, no package file, placed in its folder's part as a module `index`, and given a
   mirror test file name. Pinned in Task 1 (`test_under_several_endings_...`) and Task 3
   (`test_a_file_of_any_ending_of_the_language_has_its_test_file_and_a_package_file_has_none`).
3. Init/scaffold under a language with no package file writes no file named `""`. Pinned in Task 4
   (`test_plan_writes_no_package_file_when_the_language_has_none`).
4. Python's `testing.files` refusal texts stay byte-identical. Pinned in Task 4: the existing tests of
   `test_testing.py`, `test_profile_language.py` and `test_profile_parsing_tests.py` are kept verbatim and run.
5. `file.package` never appears in `python.yaml`'s `supplies`, yet Python supplies it `exact`. Pinned in Task 2
   (`test_python_reads_one_ending_and_one_package_file_and_supplies_file_package_though_its_file_does_not_list_it`).

---

### Task 1: Marks as two lists, and the stem helper

**Files:**
- Modify: `xarch/kernel/placement.py:14-19` (`Marks`)
- Modify: `xarch/kernel/logic/placement.py:36-45` (`module_steps`, `stands_for_folder`; new `stem`)
- Modify: `xarch/profile_values/language.py:76-78` (`marks`, interim: still built from the two scalars)
- Test: `tests/kernel/logic/test_placement.py`
- Test (call sites only): `tests/modules/rules/application/logic/test_imports.py:29-31`,
  `tests/modules/rules/application/logic/test_places.py:139,154`,
  `tests/modules/spec/application/logic/test_language_file.py:40-42`

**Interfaces:**
- Consumes: nothing.
- Produces: `Marks(extensions: tuple[str, ...] = (), package_files: tuple[str, ...] = ())`;
  `stem(name: str, marks: Marks) -> str | None` in `xarch.kernel.logic.placement`;
  `module_steps(path, marks)` and `stands_for_folder(path, marks)` unchanged in signature.

- [ ] **Step 1: Write the failing tests**

In `tests/kernel/logic/test_placement.py`:

Change the import line to add `stem`:

```python
from xarch.kernel.logic.placement import module_steps, place_of, reaches, repeat_of, root_of, stands_for_folder, stem, with_itself
```

Replace `MARKS = Marks(".src", "pkg.src")` (line 8) with:

```python
MARKS = Marks((".src",), ("pkg.src",))
```

Replace the body of `test_a_path_is_read_with_the_marks_it_is_given_and_with_none_as_written` (lines 94-98) with:

```python
def test_a_path_is_read_with_the_marks_it_is_given_and_with_none_as_written():
    patterns = {"domain": ("domain",), "main": ("main.src",)}
    assert place_of(patterns, ("domain", "index.mod"), Marks((".mod",), ("index.mod",))) == Place("domain")
    assert place_of(patterns, ("domain", "x.src"), Marks()) == Place("domain", None, ("x.src",))
    assert place_of(patterns, ("main.src",), Marks()) == Place("main")
```

Replace `SRC = Marks(".src", "pkg.src")` (line 101) with:

```python
SRC = Marks((".src",), ("pkg.src",))
```

Append at the end of the file:

```python
BRACE = Marks((".ts", ".tsx", ".mts"), ("index.ts", "index.tsx"))
"""The marks of the TypeScript-like test-only language: three endings, two package files."""
PERCENT = Marks((".cls", ".mac"))
"""The marks of the ObjectScript-like test-only language: two endings and no package file."""


@pytest.mark.parametrize("name, expected", [
    pytest.param("b.tsx", "b", id="the second ending"),
    pytest.param("b.ts", "b", id="the first ending"),
    pytest.param("b.mts", "b", id="the third ending"),
    pytest.param("b.js", None, id="an ending the language does not have"),
    pytest.param("b", None, id="no ending"),
])
def test_a_name_loses_the_ending_it_carries_and_has_no_stem_when_it_carries_none(name, expected):
    assert stem(name, BRACE) == expected


def test_the_longest_ending_a_name_carries_is_the_one_it_loses():
    assert stem("x.d.ts", Marks((".ts", ".d.ts"))) == "x"
    assert stem("x.d.ts", Marks((".d.ts", ".ts"))) == "x"


@pytest.mark.parametrize("path, place", [
    pytest.param(("a", "b.tsx"), Place("a", None, ("b",)), id="a module of any ending"),
    pytest.param(("a", "index.ts"), Place("a"), id="the first package file stands for its folder"),
    pytest.param(("a", "index.tsx"), Place("a"), id="the second one too"),
    pytest.param(("a", "index.mts"), Place("a", None, ("index",)), id="a module named index of an ending no package file has"),
])
def test_under_several_endings_a_path_is_placed_by_the_ending_it_carries(path, place):
    assert place_of({"a": ("a",)}, path, BRACE) == place


@pytest.mark.parametrize("path, folder", [
    pytest.param(("a", "index.ts"), True, id="a package file"),
    pytest.param(("a", "index"), True, id="a package file written without its ending"),
    pytest.param(("a", "index.mts"), False, id="no listed package file"),
    pytest.param(("a", "main.ts"), False, id="a module"),
])
def test_a_path_stands_for_its_folder_when_it_is_one_of_the_package_files(path, folder):
    assert stands_for_folder(path, BRACE) is folder


def test_with_no_package_file_no_path_stands_for_its_folder():
    assert (module_steps(("a", "Package.cls"), PERCENT), stands_for_folder(("a", "Package.cls"), PERCENT)) == (
        ("a", "Package"), False)
    assert stands_for_folder(("a", "Package"), PERCENT) is False
    assert module_steps(("a", "Run.mac"), PERCENT) == ("a", "Run")


def test_a_step_that_carries_no_ending_is_kept_as_written():
    assert module_steps(("a", "notes.txt"), BRACE) == ("a", "notes.txt")


def test_python_s_package_file_stands_for_its_folder_with_its_ending_or_without_it():
    python = Marks((".py",), ("__init__.py",))
    assert [stands_for_folder(path, python) for path in (("a", "__init__.py"), ("a", "__init__"), ("a", "__init__.pyx"))] == [
        True, True, False]
    assert module_steps(("a", "__init__.py"), python) == ("a",)
```

In `tests/modules/rules/application/logic/test_imports.py` replace lines 29-31 with:

```python
    assert dotted(steps("kernel/ids.src"), Marks((".src",), ("index.src",))) == (("kernel", "ids"), False)
    assert dotted(steps("kernel/index.src"), Marks((".src",), ("index.src",))) == (("kernel",), True)
    assert dotted(steps("kernel/__init__.py"), Marks()) == (("kernel", "__init__.py"), False)
```

In `tests/modules/rules/application/logic/test_places.py` replace `MARKS = Marks(".src", "pkg.src")` (line 139) with
`MARKS = Marks((".src",), ("pkg.src",))`. Line 154 (`Marks()`) stays.

In `tests/modules/spec/application/logic/test_language_file.py` replace
`test_the_marks_of_a_language_are_its_extension_and_its_package_file` (lines 40-42) with:

```python
def test_the_marks_of_a_language_are_its_extensions_and_its_package_files():
    assert language_of("pascal", DOCUMENT).checked.marks == Marks((".pas",), ("unit.pas",))
```

and add `from xarch.kernel.placement import Marks` to its imports (after `import yaml`, alphabetically among the
`xarch` imports: first of them).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/kernel/logic/test_placement.py tests/modules/rules/application/logic/test_imports.py tests/modules/rules/application/logic/test_places.py tests/modules/spec/application/logic/test_language_file.py`
Expected: FAIL — `ImportError: cannot import name 'stem'` for test_placement; the others fail where a tuple is given
where a string was (`AttributeError: 'tuple' object has no attribute ...` or a wrong place).

- [ ] **Step 3: Write the implementation**

`xarch/kernel/placement.py`, replace the `Marks` class:

```python
@dataclass(frozen=True)
class Marks:
    """How the language of the app writes a path: the endings a source file's name may carry, and the names of the
    files that stand for the folder holding them, each ending in one of them (none: no file does). Empty marks leave
    a path as written."""
    extensions: tuple[str, ...] = ()
    package_files: tuple[str, ...] = ()
```

`xarch/kernel/logic/placement.py`, replace `module_steps` and `stands_for_folder` (lines 36-45) with:

```python
def stem(name: str, marks: Marks) -> str | None:
    """The name without the ending of the marks it carries, the longest when several match; None when it carries
    none of them."""
    ending = max((extension for extension in marks.extensions if name.endswith(extension)), key=len, default=None)
    return None if ending is None else name.removesuffix(ending)


def module_steps(path: tuple[str, ...], marks: Marks) -> tuple[str, ...]:
    """A path as the language names it: no ending on its file (a step carrying none kept as written), and a file that
    stands for its folder is the folder."""
    if not path:
        return path
    last = stem(path[-1], marks)
    steps = path[:-1] + (path[-1] if last is None else last,)
    return steps[:-1] if stands_for_folder(path, marks) else steps


def stands_for_folder(path: tuple[str, ...], marks: Marks) -> bool:
    """Whether a path is a file that stands for its folder: one of the package files, or, carrying no ending, the stem
    of one (a package file written without its ending)."""
    if not path:
        return False
    name = path[-1]
    return name in marks.package_files or (stem(name, marks) is None
                                           and name in {stem(file, marks) for file in marks.package_files})
```

In the module docstring of `xarch/kernel/logic/placement.py`, replace

```
pattern is the place's sub-path. A path is compared as its language names it (see Marks): no ending on its file, and
the file that stands for a folder is the folder itself.
```

with

```
pattern is the place's sub-path. A path is compared as its language names it (see Marks): no ending on its file (the
longest of the language's endings it carries, see stem), and a file that stands for a folder is the folder itself.
```

`xarch/profile_values/language.py`, interim until Task 2 replaces the fields — replace the `marks` property:

```python
    @property
    def marks(self) -> Marks:
        return Marks((self.extension,) if self.extension else (), (self.package_file,) if self.package_file else ())
```

- [ ] **Step 4: Run the tests to verify they pass, and the suites that read marks**

Run: `timeout 900 uv run pytest -q tests/kernel tests/modules/rules tests/modules/spec tests/profile_values`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add xarch/kernel/placement.py xarch/kernel/logic/placement.py xarch/profile_values/language.py tests/kernel/logic/test_placement.py tests/modules/rules/application/logic/test_imports.py tests/modules/rules/application/logic/test_places.py tests/modules/spec/application/logic/test_language_file.py
git commit -m "Marks hold the endings of a source file and the package files as lists, and one kernel helper, stem, gives a name without the longest ending it carries or None; a path loses that ending and stands for its folder when it is one of the package files or the stem of one"
```

---

### Task 2: The data file's `extensions` and `package_files`, the language value, and `file.package` supplied

**Files:**
- Modify: `xarch/profile_values/language.py:31-78` (`CheckedLanguage` fields, docstring, `marks`, two properties)
- Modify: `xarch/profile_values/capabilities.py:39-40` (`FACTS` gains `file.package`; constant `PACKAGE_FACT`)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring, `KEYS`, `REQUIRED`, `language_of`,
  `_supplies`, two new readers)
- Modify: `xarch/architectures/presets/language/python.yaml` (header lines 2-4, the supplies comment, lines 26-27)
- Modify: `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml`
- Modify (tests that build a language): `tests/modules/rules/builders.py:39,53-54,62-63`,
  `tests/modules/rules/application/logic/test_written.py:70,83`,
  `tests/modules/spec/application/test_language.py:16,18,33-35,40-42,57`,
  `tests/modules/spec/application/test_explain.py:128-129,173`,
  `tests/modules/spec/application/logic/test_profile_language.py:12`,
  `tests/architecture/test_language_seam.py:146-160,426`
- Test: `tests/modules/spec/application/logic/test_language_file.py`, `tests/profile_values/test_language.py`,
  `tests/modules/spec/application/logic/test_profile_keys.py`

**Interfaces:**
- Consumes: `Marks(extensions, package_files)` (Task 1).
- Produces: `CheckedLanguage.extensions: tuple[str, ...] = ()`, `CheckedLanguage.package_files: tuple[str, ...] = ()`
  (in this position: right after `title`); properties `CheckedLanguage.extension -> str` and
  `CheckedLanguage.package_file -> str` (first item or `""`, for messages, docs and init only);
  `PACKAGE_FACT = "file.package"` in `xarch.profile_values.capabilities`; `FACTS["file.package"]`.

- [ ] **Step 1: Write the failing loader tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Add to the imports `from tests.modules.spec.languages import PYTHON as PYTHON_LANGUAGE` (first import block line after
`import yaml`, before the `xarch` imports, a blank line between them as the file's other test modules do).

Replace `DOCUMENT` (lines 16-18) with:

```python
DOCUMENT = {"title": "Pascal", "extensions": [".pas"], "package_files": ["unit.pas"],
            "interface": [{"base": "sys.Contract"}], "dynamic": ["sys.load", "sys.Contract.load"], "namespace": "system",
            "cache": ".objs", "standard": "interpreter"} | JOINS
```

Add after `LISTS = ...` (line 29-30):

```python
KEYS_USED = ("branching, branching_expressions, cache, call, comment, directives, dynamic, encoding, extensions, "
             "immutable, importing, interface, member, name, namespace, nothing, package, package_files, private, "
             "shebang, special, standard, supplies, title, unannotated")
"""The keys of a data file, as the unknown-key text lists them."""
EXTENSIONS = "extensions: must be a non-empty list of endings, each starting with a dot"
PACKAGE_FILES = "package_files: must be a list of file names, each ending in one of extensions"
UNLISTED = {key: value for key, value in DOCUMENT.items() if key != "package_files"}
"""DOCUMENT with no file standing for a folder."""


def refused(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", document)
    return [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems]
```

Replace `test_a_language_is_read_from_the_document_of_its_preset_by_name` (lines 32-37) with:

```python
def test_a_language_is_read_from_the_document_of_its_preset_by_name():
    assert language_of("pascal", DOCUMENT) == Language(
        "pascal", CheckedLanguage("Pascal", (".pas",), ("unit.pas",),
                                  (InterfaceMark(("sys", "Contract")),),
                                  (("sys", "load"), ("sys", "Contract", "load")), names=NAME, package=NAME, member="."),
        "system", "interpreter", ".objs", NAME)
```

In `test_every_problem_of_a_document_is_listed_naming_the_preset` replace the `broken` literal's first two keys and the
expected list's first and fifth/sixth items so the test reads:

```python
def test_every_problem_of_a_document_is_listed_naming_the_preset():
    broken = {"title": "", "extensions": "pas", "package_files": 3, "interface": "x", "dynamic": ["", "a b"],
              "cache": "a/b", "extra": 1} | JOINS
    with pytest.raises(InvalidArchitecture) as caught:
        language_of("odd", broken)
    assert caught.value.source == "presets/language/odd.yaml"
    assert [problem.removeprefix("presets/language/odd.yaml: ") for problem in caught.value.problems] == [
        f"unknown key 'extra': use {KEYS_USED}",
        "missing `namespace`", "missing `standard`",
        "title: must be a non-empty string",
        EXTENSIONS,
        PACKAGE_FILES,
        INTERFACE,
        "dynamic: '' is not an outside name such as <package>.<name>",
        "dynamic: 'a b' is not an outside name such as <package>.<name>",
        "cache: must be a folder name"]
```

Replace the expected text of `test_a_document_that_is_no_mapping_is_refused`:

```python
    assert caught.value.problems == (
        "presets/language/odd.yaml: must be a mapping of keys, such as title, extensions and package_files",)
```

Replace `test_the_facts_its_reader_supplies_are_read_each_with_its_grade` (lines 134-137) with:

```python
def test_the_facts_its_reader_supplies_are_read_each_with_its_grade_and_file_package_follows_package_files():
    supplies = {"supplies": {"import": "exact", "class": {"partial": "nested classes are not read"}}}
    listed = (Supply("import", EXACT), Supply("class", PARTIAL, "nested classes are not read"))
    assert language_of("pascal", DOCUMENT | supplies).checked.supplies == (*listed, Supply("file.package", EXACT))
    assert language_of("pascal", UNLISTED | supplies).checked.supplies == listed


def test_a_document_that_says_nothing_of_its_reader_supplies_no_grade_whatever_package_files_says():
    assert (language_of("pascal", DOCUMENT).checked.supplies, language_of("pascal", UNLISTED).checked.supplies) == (
        None, None)
```

and delete the old `test_a_document_that_says_nothing_of_its_reader_supplies_no_grade` (lines 140-141), which the
second test replaces.

Append at the end of the file:

```python
def test_the_endings_and_the_package_files_are_read_in_the_order_written():
    checked = language_of("pascal", DOCUMENT | {"extensions": [".ts", ".tsx"], "package_files": ["index.ts"]}).checked
    assert (checked.extensions, checked.package_files) == ((".ts", ".tsx"), ("index.ts",))
    assert (checked.extension, checked.package_file) == (".ts", "index.ts")


def test_package_files_left_out_read_none_and_the_file_loads():
    checked = language_of("pascal", UNLISTED).checked
    assert (checked.package_files, checked.package_file, checked.marks) == ((), "", Marks((".pas",)))


@pytest.mark.parametrize("value", [
    pytest.param(".py", id="a string"),
    pytest.param([], id="an empty list"),
    pytest.param([3], id="a list holding a number"),
    pytest.param(["py"], id="an ending with no dot"),
    pytest.param([".py", ".py"], id="an ending listed twice"),
    pytest.param([".p y"], id="an ending with a space"),
])
def test_extensions_that_are_not_a_list_of_endings_are_one_problem(value):
    assert refused(UNLISTED | {"extensions": value}) == [EXTENSIONS]


def test_extensions_are_required():
    assert refused({key: value for key, value in UNLISTED.items() if key != "extensions"}) == ["missing `extensions`"]


@pytest.mark.parametrize("value, problems", [
    pytest.param(["index.js"], ["package_files: 'index.js' ends in none of extensions"], id="another ending"),
    pytest.param(["index.js", "main.rb"], ["package_files: 'index.js' ends in none of extensions",
                                          "package_files: 'main.rb' ends in none of extensions"], id="one problem each"),
    pytest.param([".ts"], ["package_files: '.ts' ends in none of extensions"], id="only the ending"),
    pytest.param("index.ts", [PACKAGE_FILES], id="no list"),
    pytest.param([], [PACKAGE_FILES], id="an empty list"),
    pytest.param(["index.ts", "index.ts"], [PACKAGE_FILES], id="a file listed twice"),
    pytest.param([""], [PACKAGE_FILES], id="an empty name"),
])
def test_package_files_must_each_end_in_one_of_the_extensions(value, problems):
    assert refused(DOCUMENT | {"extensions": [".ts"], "package_files": value}) == problems


def test_package_files_are_not_checked_against_extensions_that_are_refused_already():
    assert refused(DOCUMENT | {"extensions": "ts", "package_files": ["index.js"]}) == [EXTENSIONS]


def test_the_old_keys_of_one_ending_and_one_package_file_are_unknown_keys():
    old = {key: value for key, value in UNLISTED.items() if key != "extensions"} | {"extension": ".pas",
                                                                                    "package_file": "unit.pas"}
    assert refused(old) == [f"unknown keys 'extension', 'package_file': use {KEYS_USED}", "missing `extensions`"]


@pytest.mark.parametrize("grade", [pytest.param("exact", id="exact"), pytest.param({"partial": "some"}, id="partial")])
def test_file_package_is_never_written_under_supplies(grade):
    assert refused(DOCUMENT | {"supplies": {"import": "exact", "file.package": grade}}) == [
        "supplies: file.package follows package_files: drop it from supplies"]


def test_python_reads_one_ending_and_one_package_file_and_supplies_file_package_though_its_file_does_not_list_it():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    checked = PYTHON_LANGUAGE.checked
    assert (checked.extensions, checked.package_files) == ((".py",), ("__init__.py",))
    assert "file.package" not in document["supplies"]
    assert Supply("file.package", EXACT) in checked.supplies


def test_the_test_only_languages_say_several_endings_and_brace_two_package_files_percent_none():
    read = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
            for path in TEST_LANGUAGES}
    assert (read["brace"].extensions, read["brace"].package_files) == ((".ts", ".tsx", ".mts"), ("index.ts", "index.tsx"))
    assert (read["percent"].extensions, read["percent"].package_files) == ((".cls", ".mac"), ())
```

Add `from importlib import resources` to the stdlib imports at the top of the file (after `import re`).

- [ ] **Step 2: Write the failing value and word tests**

In `tests/profile_values/test_language.py` append:

```python
def test_a_message_prints_the_first_ending_and_the_first_package_file_and_nothing_when_there_is_none():
    several = CheckedLanguage(extensions=(".ts", ".tsx"), package_files=("index.ts", "index.tsx"))
    assert (several.extension, several.package_file) == (".ts", "index.ts")
    assert (CheckedLanguage().extension, CheckedLanguage().package_file) == ("", "")


def test_the_marks_of_a_language_are_its_endings_and_its_package_files_in_full():
    several = CheckedLanguage(extensions=(".ts", ".tsx"), package_files=("index.ts", "index.tsx"))
    assert several.marks == Marks((".ts", ".tsx"), ("index.ts", "index.tsx"))
```

and add `from xarch.kernel.placement import Marks` to its imports.

In `tests/modules/spec/application/logic/test_profile_keys.py`, after
`test_a_word_of_the_table_is_what_the_language_says_for_it` (line ~184), add:

```python
def test_the_ending_and_the_package_file_a_text_says_are_the_language_s_first_and_nothing_when_it_has_none():
    assert said("%extension% `%package_file%`", BRACE) == ".ts `index.ts`"
    assert said("%extension% `%package_file%`", PERCENT) == ".cls ``"
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/profile_values/test_language.py tests/modules/spec/application/logic/test_profile_keys.py`
Expected: FAIL — `unknown keys 'extensions', 'package_files'` problems from the loader, `TypeError: ... unexpected
keyword argument 'extensions'` from `CheckedLanguage`, and `missing `extension`` for the test-only files once edited
(Step 5 edits them; before it they read the old keys).

- [ ] **Step 4: Write the implementation — the value and the fact**

`xarch/profile_values/capabilities.py`: insert in `FACTS` right after the `"class.interface": ...` line:

```python
    "file.package": "a file stands for the folder that holds it",
```

and after the `EXACT` constant and its docstring, add:

```python
PACKAGE_FACT = "file.package"
"""The fact a language supplies, exactly, when its data file gives package_files, and only then; never written under
`supplies`."""
```

`xarch/profile_values/language.py`, in `CheckedLanguage`:

Replace the start of its docstring

```
    """The language of the app as a check reads it: how a message names it, the ending of a source file's name, the file
    that stands for the folder holding it, the marks that make a class an interface (interface: an outside name
```

with

```
    """The language of the app as a check reads it: how a message names it, the endings of a source file's name
    (extensions, in the order written; a message prints the first), the files that stand for the folder holding them
    (package_files; none: no file does), the marks that make a class an interface (interface: an outside name
```

Replace the two fields

```python
    extension: str = ""
    package_file: str = ""
```

with

```python
    extensions: tuple[str, ...] = ()
    package_files: tuple[str, ...] = ()
```

Replace the `marks` property (the interim one of Task 1) with:

```python
    @property
    def marks(self) -> Marks:
        return Marks(self.extensions, self.package_files)

    @property
    def extension(self) -> str:
        """The first ending of a source file's name, the one a message prints; "" when the language gives none. Never
        what decides whether a file is a source file: every ending does (see marks)."""
        return self.extensions[0] if self.extensions else ""

    @property
    def package_file(self) -> str:
        """The first file that stands for its folder, the one a message prints and init writes; "" when the language
        has none."""
        return self.package_files[0] if self.package_files else ""
```

- [ ] **Step 5: Write the implementation — the loader and the data files**

`xarch/modules/spec/application/logic/language_file.py`:

Docstring: replace

```
    title          how a message names the language
    extension      the ending of a source file's name: a dot and a name
    package_file   the name of the file that stands for the folder holding it, ending in the extension
```

with

```
    title          how a message names the language
    extensions     the endings of a source file's name, each a dot and a name: a non-empty list, the first the one a
                   message prints
    package_files  the names of the files that stand for the folder holding them, each ending in one of the
                   extensions: a non-empty list; optional, left out when no file does. The fact file.package follows
                   it: supplied exactly when it is given, and never written under supplies
```

and in the `supplies` paragraph of the docstring replace

```
                   Left out, the file does not say what a reader supplies (no reader is written for it yet), and
                   no key is held to it
```

with

```
                   Left out, the file does not say what a reader supplies (no reader is written for it yet), and
                   no key is held to it; given, file.package is added to it when package_files is given
```

Imports: change `from xarch.profile_values.capabilities import EXACT, FACTS, Supply` to

```python
from xarch.profile_values.capabilities import EXACT, FACTS, PACKAGE_FACT, Supply
```

Replace `KEYS` and `REQUIRED`:

```python
KEYS = ("title", "extensions", "package_files", "interface", "dynamic", "namespace", "cache", "standard", "name",
        "package", "member", "private", "special", "call", "nothing", "unannotated", "comment", "directives", "shebang",
        "encoding", "branching", "importing", "supplies", "immutable", "branching_expressions")
REQUIRED = ("title", "extensions", "namespace", "standard")
```

After `_EXTENSION = re.compile(r"\.[A-Za-z0-9]+")` add:

```python
EXTENSIONS = "extensions: must be a non-empty list of endings, each starting with a dot"
"""What the loader says of a value of `extensions` that is not a list of endings, once for the key."""
PACKAGE_FILES = "package_files: must be a list of file names, each ending in one of extensions"
"""What the loader says of a value of `package_files` that is not a list of file names, once for the key."""
```

In `language_of`, replace the mapping refusal text:

```python
        raise InvalidArchitecture(source, ["must be a mapping of keys, such as title, extensions and package_files"])
```

Replace the four lines

```python
    extension = _text(document, "extension", "must be a dot and a name, such as .pas", problems, _EXTENSION)
    package_file = _text(document, "package_file", "must be a file name ending in the extension", problems)
    if package_file and not (extension and package_file.endswith(extension) and package_file != extension):
        problems.append("package_file: must be a file name ending in the extension")
```

with

```python
    extensions = _extensions(document, problems)
    package_files = _package_files(document, extensions, problems)
```

Replace

```python
    supplies = _supplies(document["supplies"], problems) if "supplies" in document else None
```

with

```python
    supplies = _supplies(document["supplies"], problems) if "supplies" in document else None
    if supplies is not None and package_files:
        supplies = (*supplies, Supply(PACKAGE_FACT, EXACT))
```

Replace the start of the `CheckedLanguage(...)` call

```python
    checked = CheckedLanguage(title=title, extension=extension, package_file=package_file, interface=interface,
```

with

```python
    checked = CheckedLanguage(title=title, extensions=extensions or (), package_files=package_files, interface=interface,
```

(keep the call's other lines; re-wrap so no line passes 140 characters).

Add these two functions right after `language_of`:

```python
def _extensions(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, ...] | None:
    """The endings of a source file's name, in the order written; None when the key is missing, or refused with one
    problem for it."""
    if "extensions" not in document:
        return None
    value = document["extensions"]
    if not (isinstance(value, list) and value and all(isinstance(item, str) and _EXTENSION.fullmatch(item) for item in value)
            and len(set(value)) == len(value)):
        problems.append(EXTENSIONS)
        return None
    return tuple(value)


def _package_files(document: Mapping[Any, Any], extensions: tuple[str, ...] | None,
                   problems: list[str]) -> tuple[str, ...]:
    """The files that stand for the folder holding them, in the order written; none when the key is left out. Each
    must end in one of extensions and be more than the ending, unless extensions are missing or refused already
    (None)."""
    if "package_files" not in document:
        return ()
    value = document["package_files"]
    if not (isinstance(value, list) and value and all(isinstance(item, str) and item.strip() for item in value)
            and len(set(value)) == len(value)):
        problems.append(PACKAGE_FILES)
        return ()
    if extensions is not None:
        problems += [f"package_files: {item!r} ends in none of extensions" for item in value
                     if not any(item.endswith(extension) and item != extension for extension in extensions)]
    return tuple(value)
```

In `_supplies`, replace

```python
        if fact not in FACTS:
            problems.append(f"supplies: {fact!r} is not a fact a check reads: use {', '.join(sorted(FACTS))}")
        elif grade == EXACT:
```

with

```python
        if fact not in FACTS:
            problems.append(f"supplies: {fact!r} is not a fact a check reads: use {', '.join(sorted(FACTS))}")
        elif fact == PACKAGE_FACT:
            problems.append(f"supplies: {PACKAGE_FACT} follows package_files: drop it from supplies")
        elif grade == EXACT:
```

`xarch/architectures/presets/language/python.yaml`:

Replace the header's lines 2-4

```
# needed outside the reader that turns source into facts. title is how a message says it; extension the ending of a
# source file's name; package_file the file that stands for the folder holding it; interface the marks of a class that
# is an interface (a port), each {base: <outside name>}, a name among its bases, or {keyword: <word>}, a keyword its
```

with

```
# needed outside the reader that turns source into facts. title is how a message says it; extensions the endings of a
# source file's name, the first the one a message prints; package_files the files that stand for the folder holding
# them, each ending in one of the extensions (optional: a language may have none); interface the marks of a class that
# is an interface (a port), each {base: <outside name>}, a name among its bases, or {keyword: <word>}, a keyword its
```

Replace the supplies comment's last line

```
# needs a fact not listed here is refused, and one that reads a partial fact is listed as approximate.
```

with

```
# needs a fact not listed here is refused, and one that reads a partial fact is listed as approximate. file.package,
# that a file stands for its folder, is never listed here: it follows package_files.
```

Replace

```yaml
extension: .py
package_file: __init__.py
```

with

```yaml
extensions: [.py]
package_files: [__init__.py]
```

`tests/fakes/languages/brace.yaml`: replace the header's last line and the two keys so the file starts:

```yaml
# A test-only language that imitates a TypeScript-like one: no profile names it and no reader is written for it. Its
# packages are named as a package manager names them (a scope, a dash, a dot) or as its runtime's own modules
# (node:fs), and a name in one is joined to it by #. It gives its standard library's top-level modules, its reserved
# words and its builtins as lists, so that spec reads them from here and asks no runtime. Its source files end in .ts,
# .tsx or .mts, and index.ts or index.tsx stands for the folder holding it; index.mts is a module like any other. The
# tests load it to show that the profile and the checks read outside names by a language's own patterns; later steps
# add their keys to it.
title: Brace
extensions: [.ts, .tsx, .mts]
package_files: [index.ts, index.tsx]
```

(the rest of the file, from `namespace: globalThis` on, unchanged).

`tests/fakes/languages/percent.yaml`: make the file start:

```yaml
# A test-only language that imitates an ObjectScript-like one: no profile names it and no reader is written for it.
# Its names and packages may start with %, and a name in a package is joined to it by a dot. Its source files end in
# .cls or .mac, and it has no package file: no file stands for the folder holding it. The tests load it to show that
# the profile and the checks read outside names by a language's own patterns; later steps add their keys to it.
title: Percent
extensions: [.cls, .mac]
```

(the `package_file: Package.cls` line is deleted; the rest, from `namespace: "%SYSTEM"` on, unchanged).

- [ ] **Step 6: Move every test that builds a language to the lists**

`tests/modules/rules/builders.py`:

```python
PYTHON = CheckedLanguage(title="Python", extensions=(".py",), package_files=("__init__.py",),
```

(line 39; the rest of the call unchanged)

```python
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extensions=tuple(BRACE_FILE["extensions"]),
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
```

(lines 53-54)

```python
PERCENT = CheckedLanguage(title=PERCENT_FILE["title"], extensions=tuple(PERCENT_FILE["extensions"]),
                          interface=marks_of(PERCENT_FILE),
```

(lines 62-63; percent gives no `package_files`). Update the docstring under `BRACE` to read `"""The TypeScript-like
test-only language as a check reads it, its endings, package files, patterns, member, interface marks, annotations of
no value and standard modules read from its data file."""` and under `PERCENT` to begin `"""The ObjectScript-like
test-only language as a check reads it: its two endings and no package file, its interface marks, ...` (rest as is).

`tests/modules/rules/application/logic/test_written.py` lines 70 and 83: `CheckedLanguage(extension=".py", ...)` →
`CheckedLanguage(extensions=(".py",), ...)`.

`tests/modules/spec/application/test_language.py`:

```python
PASCAL = {"title": "Pascal", "extensions": [".pas"], "package_files": ["unit.pas"], "interface": [{"base": "sys.Contract"}],
          "dynamic": ["sys.load"], "namespace": "system", "standard": "interpreter"} | JOINS
PYTHON = {"title": "Python", "extensions": [".py"], "package_files": ["__init__.py"],
          "interface": [{"base": "typing.Protocol"}], "namespace": "builtins", "cache": "__pycache__",
          "standard": "interpreter"} | JOINS
```

and in its three expected `CheckedLanguage(...)` values (lines 33-35, 40-42, 57) replace `"Pascal", ".pas", "unit.pas"`
with `"Pascal", (".pas",), ("unit.pas",)` and `"Python", ".py", "__init__.py"` with `"Python", (".py",), ("__init__.py",)`.

`tests/modules/spec/application/test_explain.py` line 128-129: the expected text becomes
`"presets/language/python.yaml: must be a mapping of keys, such as title, " "extensions and package_files"`; line 173:

```python
    toy = {"title": "Toy", "extensions": [".toy"], "package_files": ["pkg.toy"], "namespace": "core",
```

`tests/modules/spec/application/logic/test_profile_language.py` line 12: `CheckedLanguage("Pascal", ".pas", "unit.pas", ...`
→ `CheckedLanguage("Pascal", (".pas",), ("unit.pas",), ...`.

`tests/architecture/test_language_seam.py`, in `language_words` replace

```python
    words = {word for word in (data["namespace"], data.get("cache", ""), data["package_file"].removesuffix(data["extension"]),
                               *steps, *WORDS_BESIDES) if word}
    ending = re.escape(data["extension"])
```

with

```python
    marks = Marks(tuple(data["extensions"]), tuple(data.get("package_files", ())))
    stems = (stem(name, marks) or "" for name in marks.package_files)
    words = {word for word in (data["namespace"], data.get("cache", ""), *stems, *steps, *WORDS_BESIDES) if word}
    ending = "|".join(re.escape(extension) for extension in marks.extensions)
```

and in the `pattern = re.compile(...)` line below it replace `|{ending}(?![A-Za-z0-9_])` with
`|(?:{ending})(?![A-Za-z0-9_])`. Add the imports `from xarch.kernel.logic.placement import stem` and
`from xarch.kernel.placement import Marks` among its `xarch` imports. In the parametrized snippet at line 426 replace
`lang.extension` with `lang.extensions` (its expectation `set(), {"decorators"}` is unchanged).

- [ ] **Step 7: Run the tests to verify they pass**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/modules/rules tests/profile_values tests/kernel tests/architecture/test_language_seam.py tests/architecture/test_agnostic.py tests/modules/scaffold tests/modules/layout`
Expected: PASS. In particular `test_python_supplies_every_fact_a_bundled_check_reads` (test_profile_needs.py) passes:
Python supplies `file.package` exactly through `package_files`.

- [ ] **Step 8: Commit**

```bash
git add xarch/profile_values/language.py xarch/profile_values/capabilities.py xarch/modules/spec/application/logic/language_file.py xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml tests/modules/rules/builders.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/test_language.py tests/modules/spec/application/test_explain.py tests/modules/spec/application/logic/test_profile_language.py tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_keys.py tests/profile_values/test_language.py tests/architecture/test_language_seam.py
git commit -m "A language's data file says extensions, a non-empty list of endings, and optional package_files, each ending in one of them, refused once each otherwise; the old keys are unknown keys; the fact file.package follows package_files and is never written under supplies; brace lists three endings and two package files, percent two endings and none"
```

---

### Task 3: Rules reads every ending

**Files:**
- Modify: `xarch/modules/rules/application/ports/source_tree.py:19-20`
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:1-2,139-140`
- Modify: `tests/fakes/filesystem.py:17-40` (`FakeSourceTree`)
- Modify: `xarch/modules/rules/application/services/source_check.py:73-80`,
  `xarch/modules/rules/application/services/holding.py:35`, `xarch/modules/rules/application/services/sources.py:43`
- Modify: `xarch/modules/rules/application/logic/sources.py:24,45`, `xarch/modules/rules/application/logic/tier_of.py:66`,
  `xarch/modules/rules/application/logic/where.py:112-126`
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/modules/rules/application/test_extensions_handed.py`
  (new), `tests/modules/rules/application/logic/test_sources.py`, `tests/modules/rules/application/logic/test_where.py`,
  `tests/modules/rules/application/logic/test_tier_of.py`

**Interfaces:**
- Consumes: `stem`, `stands_for_folder` (Task 1); `CheckedLanguage.extensions`, `.marks`, `.extension` (Task 2);
  `BRACE` of `tests/modules/rules/builders.py` with extensions `(".ts", ".tsx", ".mts")` and package files
  `("index.ts", "index.tsx")` (Task 2).
- Produces: `SourceTree.paths(root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]`;
  `FakeSourceTree.listed: list[tuple[str, ...]]`, the endings each `paths` call was handed, in call order.

- [ ] **Step 1: Write the failing tests**

`tests/modules/rules/adapters/test_fs_source_tree.py`: in `test_only_files_are_listed_as_source` (line 611) and at line
971 replace `.paths(tmp_path, ".py")` / `tree.paths(root, ".py")` with `.paths(tmp_path, (".py",))` /
`tree.paths(root, (".py",))`. Replace `test_the_files_listed_are_those_whose_name_ends_in_the_extension_given` (lines
629-632) with:

```python
def test_the_files_listed_are_those_whose_name_ends_in_the_extension_given(tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.pas").write_text("")
    assert FsSourceTree(FileSystem()).paths(tmp_path, (".pas",)) == [("b.pas",)]


def test_the_files_listed_are_those_whose_name_ends_in_one_of_the_endings_given_each_once(tmp_path):
    (tmp_path / "b").mkdir()
    for name in ("x.d.ts", "a.ts", "b/c.tsx", "d.js"):
        (tmp_path / name).write_text("")
    assert FsSourceTree(FileSystem()).paths(tmp_path, (".ts", ".tsx", ".d.ts")) == [("a.ts",), ("b", "c.tsx"), ("x.d.ts",)]
```

Create `tests/modules/rules/application/test_extensions_handed.py`:

```python
"""Use case: every service that lists the app's files lists them by every ending of the profile's language, so that a
file of the second ending is read as one of the first is."""
from dataclasses import replace
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.contract import AskHolds, CheckApp, ReadSources

ENDINGS = (".py", ".pyi")
"""The endings of the profile's language: more than one, so that only the language can have given them."""
LANGUAGE = replace(PYTHON, extensions=ENDINGS)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []},
                          more={TESTS: {"kernel/test_ids.py": []}, ROOT / "kernel": {"ids.py": []}},
                          parsed={"nothing": SourceFile("", (), ())})


def test_the_check_lists_the_app_and_the_tests_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check_app(CheckApp(ROOT, "mine", ROOT.parent, TESTS))
    assert found.listed == [ENDINGS, ENDINGS]


def test_the_holds_question_lists_the_other_files_of_the_app_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.listed == [ENDINGS]


def test_the_sources_of_a_folder_are_listed_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel"),), Path("/src"), ROOT, "mine"))
    assert found.listed == [ENDINGS]
```

Add `from xarch.modules.rules.domain.parsed import SourceFile` to that file's imports (after the `contract` import):
the holds question parses the text `"nothing"` it is given through `FakeSourceTree.parsed`, as `test_standard_handed.py`
does with `PARSED`.

`tests/modules/rules/application/logic/test_sources.py`: add `from tests.modules.rules.builders import BRACE` (merge into
the existing `from tests.modules.rules.builders import PYTHON` line: `from tests.modules.rules.builders import BRACE,
PYTHON`) and append:

```python
def test_a_file_of_any_ending_of_the_language_is_a_source_file_and_one_of_another_is_not():
    braced = replace(PROFILE, language=BRACE)
    assert sited(braced, found("app", "kernel/ids.tsx")) == Sited(IN_PART, "kernel")
    assert sited(braced, found("app", "kernel/ids.mts")) == Sited(IN_PART, "kernel")
    assert sited(braced, found("app", "kernel/ids.js")) == Sited(NOT_SOURCE, "")
```

`tests/modules/rules/application/logic/test_where.py`: change `from tests.modules.rules.builders import PYTHON` to
`from tests.modules.rules.builders import BRACE, PYTHON`, add `from dataclasses import replace` to the stdlib imports,
and append:

```python
BRACED = replace(PROFILE, language=BRACE, framework=Framework(("*.test.ts",), "test*"))
"""PROFILE in the TypeScript-like test-only language, its test files named `*.test.ts`."""


def test_a_file_of_any_ending_of_the_language_has_its_test_file_and_a_package_file_has_none():
    assert where("modules", "docs", "domain", "invoice.tsx", profile=BRACED).test_file == "invoice.test.ts"
    assert where("modules", "docs", "domain", "index.mts", profile=BRACED).test_file == "index.test.ts"
    assert where("modules", "docs", "domain", "index.tsx", profile=BRACED).test_file == ""
    assert where("modules", "docs", "domain", "index.ts", profile=BRACED).test_file == ""
```

`tests/modules/rules/application/logic/test_tier_of.py`: change the builders import to add `BRACE`
(`from tests.modules.rules.builders import BRACE, GUARD, INTEGRATION, PARTS, PROFILE, RENDERING, TWO, UNIT, profile,
steps`) and append:

```python
def test_a_file_part_of_any_ending_of_the_language_gives_the_tests_of_its_folder_its_tier():
    braced = profile(parts={**PARTS, "controller": ("modules", "*", "application", "controller.tsx")}, language=BRACE)
    found = tier_of.tested(braced, steps("modules/docs/application/publish.test.ts"))
    assert (found.tier, found.parts) == (INTEGRATION, ("controller",))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/test_extensions_handed.py tests/modules/rules/application/logic/test_sources.py tests/modules/rules/application/logic/test_where.py tests/modules/rules/application/logic/test_tier_of.py`
Expected: FAIL — `paths` globs `*('.ts', ...)` and finds nothing; `FakeSourceTree` has no `listed`; `ids.tsx` is
`NOT_SOURCE`; `invoice.tsx` gets no test file; the `.tsx` file part gives no tier.

- [ ] **Step 3: Write the implementation**

`xarch/modules/rules/application/ports/source_tree.py`:

```python
    def paths(self, root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]:
        """The path below root of every source file, a file whose name ends in one of extensions, each once, sorted."""
        ...
```

`xarch/modules/rules/adapters/fs_source_tree.py`: the module docstring's first sentence becomes

```
"""SourceTree on the local filesystem for Python, the one language xarch reads: lists the files whose name ends in one
of the endings it is given, and parses one as Python with ast and tokenize, never running it.
```

and `paths`:

```python
    def paths(self, root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]:
        return sorted({f.relative_to(root).parts for extension in extensions for f in self._fs.files(root, f"*{extension}")})
```

`tests/fakes/filesystem.py`, `FakeSourceTree`: in the class docstring replace `It records the standard modules each
read and each parse is handed, in call order (handed); the imports it returns are those the test built.` with `It records
the standard modules each read and each parse is handed (handed), and the endings each listing is handed (listed), in
call order; the imports it returns are those the test built.`; in `__init__` add after `self.handed: list[frozenset[str]]
= []`:

```python
        self.listed: list[tuple[str, ...]] = []
```

and replace `paths`:

```python
    def paths(self, root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]:
        self.listed.append(extensions)
        return [tuple(rel.split("/")) for rel in sorted(self._trees[root])]
```

`xarch/modules/rules/application/services/source_check.py` lines 73-74 and 80:

```python
        extensions = rules.language.extensions
        paths = [p for p in self._tree.paths(root, extensions) if not governed.excluded(rules, p)]
```

```python
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), table, marks, interface,
```

`xarch/modules/rules/application/services/holding.py` line 35: `self._tree.paths(root, profile.language.extensions)`.

`xarch/modules/rules/application/services/sources.py` line 43:
`return walked(profile, where, self._tree.paths(where.path, profile.language.extensions))`.

`xarch/modules/rules/application/logic/sources.py`: add `from xarch.kernel.logic.placement import stem` (first `xarch`
import); line 24:

```python
    if stem(found.path.name, profile.language.marks) is None:
```

line 45:

```python
    if not real.is_relative_to(app) or stem(real.name, profile.language.marks) is None:
```

`xarch/modules/rules/application/logic/tier_of.py`: import line 22 becomes
`from xarch.kernel.logic.placement import place_of, stem`; line 66:

```python
                  if pattern and stem(pattern[-1], profile.language.marks) is not None
```

`xarch/modules/rules/application/logic/where.py`: import line becomes
`from xarch.kernel.logic.placement import repeat_of, stands_for_folder, stem`; replace the body of `_mirror` from
`language = profile.language` to its end with:

```python
    language = profile.language
    marks = language.marks
    is_source = bool(steps) and stem(steps[-1], marks) is not None
    whole_file = stem(profile.parts[part][-1], marks) is not None
    folder = steps[:-1] if is_source else steps
    sample = pattern.replace("*", SAMPLE) if pattern else f"{SAMPLE}{language.extension}"
    tier = tested(profile, (*folder, sample)).tier
    if not pattern or not is_source or stands_for_folder(steps, marks):
        return folder, "", tier
    name = stem(steps[-1], marks) or ""
    if whole_file:
        name = f"<{tier.one_file_per}>" if tier is not None and tier.one_file_per else STAND_IN
    return folder, pattern.replace("*", name), tier
```

- [ ] **Step 4: Run the tests to verify they pass, then the rules suites**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/architecture`
Expected: PASS.

Then: `grep -rnE '\.extension\b|\.package_file\b' xarch/modules/rules`
Expected: only `written.py:66` (`%extension%`, a message) and `where.py` (the `sample` of a tier lookup, which prints
nothing but names a file the first ending would name, as today).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules tests/fakes/filesystem.py tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/test_extensions_handed.py tests/modules/rules/application/logic/test_sources.py tests/modules/rules/application/logic/test_where.py tests/modules/rules/application/logic/test_tier_of.py
git commit -m "The source tree lists the files of every ending of the language, each once; check, the holds question and sources hand the profile's language's endings; a file is a source file, a file part, or mirrored by a test file by the ending it carries, and a package file of any listed name gets no test file"
```

---

### Task 4: Spec reads every ending; init writes no nameless package file

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:56-63,501-512`
- Modify: `xarch/modules/spec/application/logic/written_checks.py:268`
- Modify: `xarch/modules/spec/application/logic/evals.py:324-327`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:832`
- Modify: `xarch/modules/spec/application/logic/example_imports.py:33-36`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:264`
- Modify: `xarch/modules/scaffold/application/logic/plan.py`
- Test: `tests/modules/spec/application/logic/test_testing.py`, `tests/modules/spec/application/logic/test_written_checks.py`,
  `tests/modules/spec/application/logic/test_evals.py`, `tests/modules/spec/application/logic/test_profile_parsing_substance.py`,
  `tests/modules/scaffold/application/logic/test_plan.py`

**Interfaces:**
- Consumes: `stem` (Task 1); `CheckedLanguage.extensions`, `.marks`, `.extension`, `.package_file` (Task 2);
  `BRACE`, `PYTHON` of `tests/modules/spec/languages.py` (spec `Language`s; brace's extensions `.ts, .tsx, .mts`).
- Produces: nothing later tasks use. (`profile_examples.py:85`, `profile_checks.py:167,393,397`, `explain.py:35`,
  `docs_template.py:536`, `project_files.py:51`, `publishing.py:52` read the `extension`/`package_file` properties and
  stay as written: they print, or hand init its one name.)

- [ ] **Step 1: Write the failing tests**

`tests/modules/spec/application/logic/test_testing.py`: add `from tests.modules.spec.languages import BRACE, PYTHON`
(after the `format_files` import) and append:

```python
BRACED = {"python": PYTHON, "brace": BRACE}


def braced(files) -> dict:
    return covered(testing={"files": files, "functions": "test*"}, language="brace")


def test_under_several_endings_a_file_pattern_may_end_in_any_of_them():
    assert parsed(braced(["*.test.tsx", "*.test.mts", "*.test.ts"]), languages=BRACED).framework.files == (
        "*.test.tsx", "*.test.mts", "*.test.ts")


@pytest.mark.parametrize("files, expected", [
    pytest.param(["*.test.js"], "layered.yaml: testing.files: '*.test.js' is not a file name pattern: a name ending in "
                                ".ts, .tsx or .mts, with `*` for any text", id="an ending the language does not have"),
    pytest.param("*.test.ts", "layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .ts, "
                              ".tsx or .mts name with `*` for any text", id="no list"),
])
def test_under_several_endings_a_refusal_lists_every_ending(files, expected):
    assert problems(braced(files), languages=BRACED) == [expected]


def test_a_file_pattern_may_hold_any_character_but_a_slash():
    assert parsed(covered(testing={"files": ["tést_*.py"], "functions": "test_*"})).framework.files == ("tést_*.py",)
    assert problems(covered(testing={"files": [".py"], "functions": "test_*"})) == [
        "layered.yaml: testing.files: '.py' is not a file name pattern: a name ending in .py, with `*` for any text"]
```

`tests/modules/spec/application/logic/test_written_checks.py`: change `from tests.modules.spec.languages import PYTHON`
to `from tests.modules.spec.languages import BRACE, PYTHON` and append:

```python
def test_an_example_of_any_ending_of_the_language_is_read_and_a_refusal_prints_the_first():
    problems: list[str] = []
    braced = {"x": {**SMALL, "examples": {"flagged": {"src/billing/api/x.tsx": "a\n"},
                                          "clean": {"src/billing/api/y.js": "b\n"}}}}
    assert checks(braced, set(ARCHITECTURE.parts), ARCHITECTURE.tiers, BRACE, problems) == {}
    assert problems == ["checks.x.examples.clean: 'src/billing/api/y.js' is not a path of a source file below the app "
                        "(or tests/...), ending in .ts"]
```

`tests/modules/spec/application/logic/test_evals.py`: add `from tests.modules.spec.languages import BRACE, PYTHON` and
append:

```python
def test_an_eval_s_example_of_any_ending_of_the_language_is_read_and_a_refusal_prints_the_first():
    braced = {"flagged": {"store/a.tsx": CODE, "store/b.mts": CODE}, "clean": {"store/c.ts": CODE, "store/d.js": CODE}}
    assert problems(layered(evals=own(examples=braced), language="brace"), languages={"python": PYTHON, "brace": BRACE}) == [
        "layered.yaml: evals.rule.examples.clean: 'store/d.js' is not a path of a source file below the app, ending in .ts"]
```

`tests/modules/spec/application/logic/test_profile_parsing_substance.py`: add
`from tests.modules.spec.languages import BRACE, PYTHON` (if `PYTHON` is imported already, add only `BRACE`) and
append:

```python
def test_dead_code_may_accept_a_public_name_of_a_file_of_any_ending_of_the_language():
    known = ["shared/text.tsx:clean", "shared/run.mts:main"]
    document = covered(guards={"dead-code": {"tests_only": True, "known": known}}, fakes=FAKES, language="brace",
                       testing={"files": ["*.test.ts"], "functions": "test*"})
    assert parsed(document, languages={"python": PYTHON, "brace": BRACE}).guards == (
        DeadCode(False, True, ("shared/text.tsx:clean", "shared/run.mts:main")),)
```

`tests/modules/scaffold/application/logic/test_plan.py`: append:

```python
def test_plan_writes_no_package_file_when_the_language_has_none():
    entries = [(("kernel",), True), (("kernel", "logic"), True), (("main.src",), False)]
    assert plan(entries, "") == [("main.src",)]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/logic/test_evals.py tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/scaffold/application/logic/test_plan.py`
Expected: FAIL — `*.test.tsx` refused (`a name ending in .ts`), `tést_*.py` refused by the ASCII class, the `.tsx`
examples and known names refused, and `plan(entries, "")` lists `("",)` and `("kernel", "")`.
- [ ] **Step 3: Write the implementation**

`xarch/modules/spec/application/logic/profile_checks.py`, replace `_file_pattern` and `_file_name` (lines 56-63) with:

```python
def _endings(language: Language) -> str:
    """The endings of a source file of the language, as a refusal lists them: `.py`, or `.ts, .tsx or .mts`."""
    *rest, last = language.checked.extensions or ("",)
    return f"{', '.join(rest)} or {last}" if rest else last


def _ending(language: Language) -> str:
    """A regular expression any one of the language's endings matches."""
    return "|".join(re.escape(extension) for extension in language.checked.extensions)


def _file_pattern(language: Language) -> re.Pattern[str]:
    """What a file name pattern is: no `/`, at least one character, then one of the language's endings; `*` stands
    for any text."""
    return re.compile(rf"[^/]+(?:{_ending(language)})")


def _file_name(language: Language) -> re.Pattern[str]:
    """What a file name is: no `/` and no `*`, at least one character, then one of the language's endings."""
    return re.compile(rf"[^/*]+(?:{_ending(language)})")
```

In `_file_patterns` (lines 501-512) replace the two messages:

```python
        problems.append(f"{where}: must be a non-empty list of file name patterns, each a {_endings(language)} name "
                        "with `*` for any text")
```

```python
            problems.append(f"{where}: {item!r} is not a file name pattern: a name ending in {_endings(language)}, "
                            "with `*` for any text")
```

(For Python `_endings` gives `.py`: both texts are byte-identical to today's.)

`xarch/modules/spec/application/logic/written_checks.py`: add `from xarch.kernel.logic.placement import stem` (after the
`conditions` import); line 268:

```python
            if not steps or any(step in ("", ".", "..") for step in steps) or stem(steps[-1], language.checked.marks) is None:
```

(line 270's message keeps `{language.checked.extension}`; re-wrap line 268 if it passes 140 characters.)

`xarch/modules/spec/application/logic/evals.py`: import line 28 becomes
`from xarch.kernel.logic.placement import place_of, stem`; in `_example` replace

```python
    if not steps or any(step in ("", ".", "..") for step in steps) or not path.endswith(extension):
```

with

```python
    if not steps or any(step in ("", ".", "..") for step in steps) or stem(steps[-1], language.checked.marks) is None:
```

`xarch/modules/spec/application/logic/profile_parsing.py`: import line 73 becomes
`from xarch.kernel.logic.placement import root_of, stem`; line 832:

```python
        if not file or file.startswith("/") or stem(file.rsplit("/", 1)[-1], language.checked.marks) is None \
```

`xarch/modules/spec/application/logic/example_imports.py`: import line 23 becomes
`from xarch.kernel.logic.placement import reaches, stem`; `checked_examples`:

```python
def checked_examples(architecture: Architecture) -> tuple[Example, ...]:
    """The examples the check reads: those whose file is a source file of the app's language, of any of its endings."""
    marks = architecture.language.checked.marks
    return tuple(example for example in architecture.examples.values()
                 if stem(example.file.rsplit("/", 1)[-1], marks) is not None)
```

`xarch/modules/spec/application/logic/docs_template.py` line 264:

```python
    named = language.name if suffix in language.checked.extensions else kind.fence or suffix.lstrip('.')
```

`xarch/modules/scaffold/application/logic/plan.py`, whole file:

```python
"""What a skeleton turns into on disk: the package file of every folder, when the language has one, and every file,
parents first."""
from __future__ import annotations

from collections.abc import Iterable


def plan(entries: Iterable[tuple[tuple[str, ...], bool]], package_file: str) -> list[tuple[str, ...]]:
    """The files to write: package_file at the root and in every folder (none at all when it is "": the language has
    no package file), and every file, in the order given."""
    found = [((), True), *entries]
    return [path + (package_file,) if is_dir else path for path, is_dir in found if package_file or not is_dir]
```

- [ ] **Step 4: Run the tests to verify they pass, then the spec and scaffold suites**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/modules/scaffold tests/modules/layout tests/architecture`
Expected: PASS, with the verbatim Python texts of `test_testing.py` (`PATTERN`, the two `a name ending in .py` rows),
`test_profile_language.py::test_the_extension_of_the_language_is_what_a_test_file_pattern_ends_in` and
`test_profile_parsing_tests.py:51` unchanged and green.

Then: `grep -rnE 'endswith\((language|architecture)[.a-z_]*\.extension\)|\.extension\)' xarch/modules/spec`
Expected: no line (no reader decides "a source file" by the first ending any more).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic xarch/modules/scaffold/application/logic/plan.py tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/logic/test_evals.py tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/scaffold/application/logic/test_plan.py
git commit -m "Spec reads an example, a known name, a docs block and a test file pattern of any ending of the language, the refusal of a pattern listing every ending (Python's texts unchanged) and the others printing the first; a pattern is any name with no slash; init writes no package file under a language that has none"
```

---

### Task 5: `file.package` — what needs it

**Files:**
- Modify: `xarch/modules/spec/domain/key_table.py:197-224` (`NEEDS`)
- Modify: `xarch/modules/rules/domain/vocabulary.py:75-90` (`Filter.facts`), `:245` (`package-file`), `:299-300`
  (`target-inside-part`)
- Modify: `xarch/modules/rules/domain/rule.py:126-135` (`Rule.needs`)
- Modify: `xarch/modules/rules/application/logic/explained.py:116-117` (`facets` of a filter)
- Test: `tests/modules/rules/domain/test_rule.py`, `tests/modules/rules/application/logic/test_explained.py`,
  `tests/modules/rules/application/logic/test_own_checks.py`, `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: `FACTS["file.package"]` (Task 2); `CheckedLanguage.package_files` (Task 2).
- Produces: `Filter.facts: tuple[str, ...] = ()` — the facts a filter needs when written as is (not negated).

- [ ] **Step 1: Write the failing tests**

`tests/modules/rules/domain/test_rule.py`, after `test_a_rule_needs_the_facts_of_its_kinds_and_of_the_fields_its_words_read`:

```python
def test_a_filter_about_the_package_file_needs_the_language_to_have_one_unless_it_is_negated():
    assert made(exempt=c("package-file")).needs == ("import", "file.package")
    assert made(scope=Scope(APP, "store", where=c("not package-file"))).needs == ("import",)
    assert "file.package" in made(facts=("import-into-app",), targets=EXISTING, sayings=say("m"),
                                  keep=c("target-placed", "target-inside-part")).needs
```

`tests/modules/rules/application/logic/test_explained.py`, add a row to the parametrize of
`test_a_word_says_what_its_category_has_besides_its_name_and_meaning`:

```python
    pytest.param(word(FILTERS, "package-file"), WordFacets(about="file", needs=("file.package",)),
                 id="a filter that needs a fact: what it asks about and the fact"),
```

`tests/modules/rules/application/logic/test_own_checks.py`, append:

```python
def test_an_own_check_that_reads_the_package_file_as_written_needs_the_language_to_have_one_and_negated_does_not():
    exempting = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                             exempt=(Condition("package-file"),))
    negated = replace(exempting, exempt=(Condition("package-file", negated=True),))
    rule = Rule("negated", Scope(), ("import",), MAY_NOT, (Match("exist"),), (Saying("m", "f"),),
                exempt=(Condition("package-file", negated=True),), key="checks.negated")
    assert made({"exempting": exempting, "negated": negated}, PROFILE) == MadeChecks(
        (OwnCheck(rule),),
        ("checks.exempting: needs file.package (a file stands for the folder that holds it), which the reader of Toy "
         "does not supply: read another kind of fact, or drop the check",))
```

`tests/modules/spec/application/logic/test_profile_needs.py`: change
`from tests.modules.spec.profiles import covered, layered, parsed, problems` (unchanged) and add after `LANGUAGES = ...`:

```python
FLAT = replace(PYTHON, name="flat", checked=replace(
    PYTHON.checked, title="Flat", package_files=(),
    supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "file.package")))
"""A language whose reader supplies every fact but file.package: it has no package file."""
FLATS = {"flat": FLAT}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}


def flat(**keys) -> dict:
    document = layered(language="flat")
    document["parts"]["service"] |= keys
    return document


def unsupplied(address: str) -> str:
    return (f"layered.yaml: {address}: its check reads file.package (a file stands for the folder that holds it), "
            f"which the language flat does not supply: drop {address}, or check the app with a language whose reader "
            "supplies file.package")


@pytest.mark.parametrize("keys, address", [
    pytest.param({"package_only": True}, "parts.service.package_only", id="package_only"),
    pytest.param({"must_import": ["store"]}, "parts.service.must_import", id="a part's must_import"),
])
def test_a_key_that_reads_the_package_file_as_written_is_refused_under_a_language_with_none(keys, address):
    assert problems(flat(**keys), languages=FLATS) == [unsupplied(address)]


def test_dead_code_untested_is_refused_under_a_language_with_no_package_file():
    document = covered(guards={"dead-code": {"untested": True}}, fakes=FAKES, language="flat")
    assert problems(document, languages=FLATS) == [unsupplied("guards.dead-code.untested")]


def test_the_keys_that_read_the_package_file_negated_load_under_a_language_with_none():
    assert parsed(flat(holds="functions", immutable=True), languages=FLATS).approximate == ()
    assert parsed(covered(guards={"dead-code": {}}, fakes=FAKES, language="flat"), languages=FLATS).approximate == ()
    assert parsed(flat(), languages=FLATS).approximate == ()


def test_file_package_is_a_fact_after_class_interface_and_only_the_keys_that_read_it_as_written_need_it():
    facts = list(FACTS)
    assert facts[facts.index("class.interface") + 1] == "file.package"
    assert FACTS["file.package"] == "a file stands for the folder that holds it"
    needing = sorted(key.address for key in KEYS if "file.package" in key.needs)
    assert needing == ["guards.dead-code.untested", "parts.<part>.must_import", "parts.<part>.package_only"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/modules/rules/domain/test_rule.py tests/modules/rules/application/logic/test_explained.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/logic/test_profile_needs.py`
Expected: FAIL — `needs == ("import",)` where `file.package` is wanted; `Filter` has no `facts`; the own check is made;
the flat profiles load; no key needs `file.package`.

- [ ] **Step 3: Write the implementation**

`xarch/modules/rules/domain/vocabulary.py`, `Filter`: replace its docstring and add the field:

```python
@dataclass(frozen=True)
class Filter:
    """A filter: its name, what is true of what passes it, whether it asks about the file, the fact or what the fact
    reaches, the fields it reads (any one of them carried makes it apply; none: it applies to every kind), the side it
    applies to, what its value is ("" for none), whether it needs a target matched (HIT), and the facts of the source
    (FACTS of capabilities) it needs of the language when written as is: negated, it needs none, since under a
    language without them every fact passes it."""
    name: str
    meaning: str
    about: str
    reads: tuple[str, ...] = ()
    side: str = ""
    value: str = ""
    needs: str = ""
    facts: tuple[str, ...] = ()
```

Line 245:

```python
    Filter("package-file", "the file is the language's package file, which stands for its folder", FILE,
           facts=("file.package",)),
```

Lines 299-300:

```python
    Filter("target-inside-part", "what the fact reaches lies below its part's own folder: one of its files, not the "
                                 "part as a whole", TARGET, ("place",), facts=("file.package",)),
```

`xarch/modules/rules/domain/rule.py`, `Rule.needs`:

```python
    @property
    def needs(self) -> tuple[str, ...]:
        """The facts of the source (FACTS of capabilities) the rule reads: those of its kinds of fact, those of the
        fields its words read, and those a filter written as is (not negated) needs, in order."""
        kinds = [_KINDS[name] for name in (*self.facts, *self.links, *self.spread, *self.said_kinds) if name in _KINDS]
        words = [*(_FILTERS.get(c.name) for c in self.conditions), *(_TARGETS.get(m.kind) for m in self.targets),
                 *(_VARIABLES.get(name) for name in self.variables)]
        found = [need for kind in kinds for need in kind.needs]
        found += [need for kind in kinds for word in words if word is not None for name in word.reads
                  if kind.carries(name) for need in kind.field_needs.get(name, ())]
        found += [need for c in self.conditions if not c.negated and c.name in _FILTERS for need in _FILTERS[c.name].facts]
        return tuple(dict.fromkeys(found))
```

`xarch/modules/rules/application/logic/explained.py` line 117:

```python
            return WordFacets(about=word.about, side=word.side, value=word.value, needs=word.facts)
```

`xarch/modules/spec/domain/key_table.py`, in `NEEDS`:

```python
    "parts.<part>.must_import": (*_IMPORTS, "import.standard", "function.statements", "file", "file.package"),
```

```python
    "parts.<part>.package_only": (*_IMPORTS, "file.package"),
```

```python
    "guards.dead-code.untested": (*_IMPORTS, "function.statements", "class", "class.exception", "function", "file",
                                  "file.package"),
```

(`tiers.<tier>.must_import` reads no `package-file` and is left as is.)

- [ ] **Step 4: Run the tests to verify they pass, and the two sides agree**

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/modules/spec tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain_words.py`
Expected: PASS. `test_needs_agree.py` (its `EVERY_KEY` unchanged) shows spec's table and the expanded rules agree:
`package_only` gains `file.package` from `target-inside-part`, a part's `must_import` and `dead-code.untested` from
`exempt: package-file`, and the negated `not package-file` of `holds`, `immutable`, `dead-code` and
`dead-code.tests_only` adds nothing.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/domain/key_table.py xarch/modules/rules/domain/vocabulary.py xarch/modules/rules/domain/rule.py xarch/modules/rules/application/logic/explained.py tests/modules/rules/domain/test_rule.py tests/modules/rules/application/logic/test_explained.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/logic/test_profile_needs.py
git commit -m "package_only, a part's must_import and dead-code.untested need file.package, and so does a rule whose filter package-file or target-inside-part is written as is, never negated; a language with no package file refuses them with the needs text and still loads holds, immutable and dead-code"
```

---

### Task 6: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:139-140` (language paragraph), `README.md:166` (supplies paragraph's last sentence)
- Modify: `CHANGELOG.md` (`## [Unreleased]`: `### Added` line 8, `### Changed` line 18)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-3-7/regenerate_docs.py`
- Not touched: `docs/examples/**` (illustrations; no test or generator holds them to the code — checked: no test reads
  `docs/examples`).

**Interfaces:**
- Consumes: the behaviour of Tasks 1-5.
- Produces: nothing.

- [ ] **Step 1: README**

In `README.md`, in the paragraph that starts `` `language` names the language of the app``, replace

```
<name>.yaml`, the way `testing: pytest` resolves to `presets/testing/pytest.yaml`: the ending of a source file, the file
that stands for a folder, what marks an interface (`interface`, a list of marks, each a base, `{base: typing.Protocol}`,
```

with

```
<name>.yaml`, the way `testing: pytest` resolves to `presets/testing/pytest.yaml`: the endings of a source file
(`extensions`, a list; the first is the one messages print), the files that stand for a folder (`package_files`, a
list, optional for a language where no file does), what marks an interface (`interface`, a list of marks, each a base,
`{base: typing.Protocol}`,
```

and re-wrap the rest of that sentence's line (`or a keyword a declaration carries, ...`) so it joins the line above
under 120 characters, as the paragraph is wrapped.

In the paragraph that starts `The data file also says what its reader supplies`, replace its last sentence
`Python's reader supplies every fact exactly.` with

```
Python's reader supplies every fact exactly. One fact is never written under `supplies`: `file.package`, that a file
stands for the folder holding it, follows `package_files`, and the keys whose check reads it (`package_only`, a part's
`must_import`, `guards.dead-code.untested`) are refused under a language that has none.
```

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, `### Added`, insert as the first entry (one blank line after the heading, one
after the entry):

```markdown
- The fact `file.package`, that a file stands for the folder holding it, which a language supplies exactly when its
  data file gives `package_files` and which is never written under `supplies` (`supplies: file.package follows
  package_files: drop it from supplies`). `parts.<part>.package_only`, a part's `must_import` and
  `guards.dead-code.untested` need it, and so does a check of your own whose filter `package-file` (or
  `target-inside-part`) is written as is; `not package-file` needs nothing. Python supplies it.
```

Under `### Changed`, insert as the first entry:

```markdown
- A language's data file says the endings of a source file as a list and its package files as an optional list:
  `extension` and `package_file` became `extensions` (`[.py]` for Python, the first the one messages print) and
  `package_files` (`[__init__.py]`), each package file ending in one of the extensions; a language may have none.
  Every check decides what a source file is by all its endings, and `testing.files` takes a pattern of any of them.
  The old keys are unknown keys. Refused: `extensions: must be a non-empty list of endings, each starting with a
  dot`, `package_files: must be a list of file names, each ending in one of extensions`, and
  `package_files: '<item>' ends in none of extensions`. No finding of a Python app changes.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-7/regenerate_docs.py` (never committed):

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
mkdir -p /tmp/xarch-3-7
uv run python -I /tmp/xarch-3-7/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines and an empty `git diff`. If the diff is not empty, stop and report it with the diff
(`git checkout -- docs/cli docs/web docs/xarch` restores the files). The docs must not move.

- [ ] **Step 4: Run the gates**

Run the suite in the background with a recorded PID, the rest in the foreground, then read the log:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-7/pytest.log 2>&1 & echo $! > /tmp/xarch-3-7/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

Expected: the suite passes (corpora and golden-doc tests of `tests/bootstrap/` included), both checks report no
violation, ruff reports nothing, the profile check loads. `git status --short` shows no change under
`tests/bootstrap/corpora/` and nothing under `.claude/` staged; `git diff main -- xarch/architectures/presets/language/python.yaml`
shows only the header lines, the supplies comment and the two keys.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "The README's language paragraph and the CHANGELOG say extensions, a list whose first item messages print, and optional package_files, with the three refusal texts, and the fact file.package that follows package_files and what needs it; the golden docs regenerate with no diff"
```

---

## Self-review against the spec

**Spec coverage.**
- 2.1 keys, refusals, `supplies` rule, docstring/header, mapping text, `python.yaml` lines: Task 2 (Steps 1, 5).
- 2.2 `Marks`, `CheckedLanguage` lists + first-item properties, `FACTS` placement: Task 1 (Marks), Task 2 (value, FACTS).
- 2.3 `stem`, `module_steps`, `stands_for_folder`: Task 1.
- 2.4 reading files (port, adapter, fake, three services): Task 3; deciding source (`sources.py`, `tier_of.py`,
  `where.py`, `example_imports.py`, `evals.py`, `written_checks.py`, `profile_parsing.py`): Tasks 3, 4; package-file
  checks (`where.py`; `filters.py` unchanged): Task 3; messages printing the first: the `extension`/`package_file`
  properties (Task 2), `docs_template.py:264` reads every ending (Task 4); scaffold/init keep one name through the
  `package_file` property and `plan.py` writes none for `""` (Task 4). `project_files.py` needs no change: with `""`
  its skeleton patterns end in an empty step no target path has, so nothing is refused that should not be. Test-file
  patterns and texts: Task 4.
- 2.5 `NEEDS`, `Filter.facts`/`Rule.needs`, own checks, refusal text, Python supplies it: Tasks 2, 5.
- 2.6 unchanged things: Task 6 gates and docs regeneration.
- 3 test-only files, builders, seam guard: Task 2. `tests/fakes/scaffold_skeleton.py` keeps its one `package_file`
  argument: scaffold's `Language` keeps one name (spec 2.4 "Scaffold and init ... keep one name"), so it does not move.
- 4 tests 1-30: 1-10 Task 2 (except the marks test, Task 1); 11-14 Task 1; 15-19 Task 3; 20-21 Task 4; 22 Task 2
  (`said` under brace/percent); 23-26 Task 5; 27 Task 4; 28-30 run in Tasks 2, 5, 6.
- 5 docs: Task 6. `docs/examples/**`: no test or generator reads them; left as they are.

**Placeholder scan.** Every code step shows its code; no TBD, no "similar to". The brace fixtures of Task 4 (evals,
written checks, dead-code known with its own `testing`) were dry-run against today's code with `.ts` paths and load
with only the ending problem expected.

**Type consistency.** `Marks(extensions, package_files)` tuples throughout; `stem(name, marks) -> str | None`;
`SourceTree.paths(root, extensions: tuple[str, ...])`; `FakeSourceTree.listed`; `CheckedLanguage.extensions`,
`.package_files`, properties `.extension`, `.package_file`; `PACKAGE_FACT`; `Filter.facts`. Names match across tasks.

**Review Focus.** Each of the five lines has its test in the task that owns the code (named in the section).
<!-- task-pipeline: validated -->
