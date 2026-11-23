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
