# 6.8 spec: `testing.declared` names how a framework declares its tests

Card: e3450e17-8dba-4e7e-8836-0557927d5442 (subtask of 15e55316), release step 21 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3), split with 6.9 to 6.11. Blocked by 6.7 (68122345), which is on this branch
(HEAD bb4cfcb).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note"). This
card implements the note's 2.1 to 2.4 (lines 231-321), 2.6 (396-408), 2.7 items 1, 3 and 4 (412-419), 2.8's bullets
on `testing.functions`, the `call` form and the needs refusal (424-430), 2.9's bullets on hand-built facts, the
%UnitTest-like framework and the `call` refusal under Python (449-454), and row 15a of section 13 (lines 1108-1116,
minus the `beside`, `preset` and `tier_of` rows).

## Goal

A framework names its tests by a list of forms, `testing.declared`, each a `function` form (a name pattern) or a
`call` form (callees with a `title` and a `body` slot), and may list `globals`, the names it binds without an import.
The reader turns the forms into `Test` facts on `SourceFile.tests`; scenario-coverage, `plain_tables` and `weak` read
those and nothing else. `testing.functions` is retired with a fixed hint. Under pytest nothing a user sees moves: the
same functions are tests, every recorded corpus and golden doc stays byte-equal.

## What is already done (not to be redone)

- `Place` (`xarch/profile_values/testing.py`, `Place`) and its parser `_place` (`profile_checks.py`, `_place`) fit the
  `title` and `body` slots as they are.
- The list-of-forms parsing model: `table_forms` / `_table_form` (`profile_checks.py:420-463`), its scope `TABLES`
  (`profile_keys.py`, address `testing.tables[]`) and the needs walker over list entries (`profile_needs._configured`,
  release step 11): problems address `testing.tables.0.call`, NEEDS keys read `testing.tables[].call`. No walker change.
- A language with no `supplies` (the test-only `brace.yaml`) is never refused for a need (`profile_needs.short`,
  `supplies is None`).
- The %UnitTest-like framework through the real Python reader: `tests/bootstrap/test_no_table_form.py` (card 6.6),
  `Test*` methods of a class, `tables: []`.
- The test-only Vitest-like framework `tests/fakes/frameworks/stub.yaml` and its loader test
  (`test_profile_parsing_tests.py:724-745`, card 6.7).

## Inherited constraints

- The key is `testing.declared`, never `testing.tests` (note 2.2, lines 244-247; dodge, line 1157).
- `declared` is required with at least one form; no hidden default meaning `test_*` (note 2.2 line 261; dodge line
  1152-1153).
- One path: `scenarios.py` reads `file.tests` only; no `fnmatchcase` on a framework pattern stays in it (note 2.6 lines
  398-402; dodge line 1154). The `fnmatchcase` import goes from `scenarios.py`.
- A framework's `globals` are not the language's builtins: a global gets the `Ref` of its bare dotted name
  (`("it", "skip")`), never `builtins.it` (note 2.3 lines 295-300; dodge line 1158). The language's `namespace` is
  unchanged.
- Python's `supplies` lists `test.function: exact` and does not list `test.call`; the Python reader gains no `call` form
  (note 2.4 lines 316-317; dodge lines 1159-1160).
- For a `function` form the reader puts the same `Function` in `functions` and in `tests`; a `call` form's test is in
  `tests` only (note 2.4 lines 309-311).
- App files are read with no forms, so they hold no tests (note 2.4 line 315).
- `weak` prints a titled test's name in double quotes, a function's bare; the checking code reads `titled` and writes
  no language syntax (note 2.6 lines 403-405).
- Problems address an entry by its index from 0 (`testing.declared.0.call`), `profile explain` the key without one
  (`testing.declared.call`) (note 2.4 lines 318-321).
- Recorded corpora (`tests/bootstrap/corpora/`) and golden docs `docs/{cli,web,xarch}/testing.md` do not move (note 2.9
  line 454; card O8). Golden docs are regenerated and their diff read, never edited by hand; expected diff empty.
- Project rules (card): no comments in xarch's code (docstrings are the documentation; YAML data files under
  `tests/fakes/` and presets keep their header comment); never `ruff --fix`; tests written first; examples simple,
  with absolute `app.` imports; Python only in `xarch/modules/rules/adapters/fs_source_tree.py` and the data files
  under `xarch/architectures/presets/`; `.claude/` out of commits; nothing pushed; README and CHANGELOG lines under
  `[Unreleased]` (review 3, O4, O5).

## Behavior

### B1. The values

- `xarch/profile_values/testing.py` gains `TestForm`, a frozen dataclass with a docstring:
  `function: str = ""` (a name pattern, `*` for any text), `call: tuple[tuple[str, ...], ...] = ()` (dotted callees),
  `title: Place | None = None`, `body: Place | None = None`. Exactly one of `function` and `call` is set; `title` and
  `body` are set exactly when `call` is.
- `Framework` loses `functions` and becomes
  `Framework(files: tuple[str, ...], declared: tuple[TestForm, ...], skips=(), tables=(), globals: tuple[tuple[str,
  ...], ...] = ())`. Its docstring names the declared forms and the globals in place of "a test function's" pattern.
- `xarch/modules/rules/domain/parsed.py` gains, near `Function`,
  `Test(line: int, name: str, form: int, titled: bool, body: Function)`: `form` the index of its form in `declared`,
  `titled` whether `name` is a title text, `body` the `Function` the checks read (mentions, asserts, blocks,
  expressions, tables). `name` is `""` for a title that is no plain literal; such a test still counts.
- `SourceFile` gains `tests: tuple[Test, ...] = ()`; its docstring says what it holds (a function form's tests are
  also among `functions`, a call form's are not).
- `xarch/profile_values/capabilities.py` `FACTS` gains `"test.function"` (the tests a function declares by a name that
  matches a pattern) and `"test.call"` (the tests a call with a title declares). The second text is fixed by the
  refusal of B3.
- `xarch/architectures/presets/language/python.yaml` `supplies` gains `test.function: exact` and not `test.call`.

### B2. The key, parsed

`testing` (inline map or preset, through `framework_patterns`) reads:

```yaml
declared:
  - function: "test_*"
  - call: [it, test]
    title: {position: 0}
    body: {position: 1}
globals: [it, test, expect]
```

- `declared` is required: a map without it gives `testing: missing \`declared\`` (as `functions` today).
- `declared` not a non-empty list: `testing.declared: must be a non-empty list of test forms, each {function} or
  {call, title, body}`.
- An entry not a mapping, or with none or both of `function` and `call`: `testing.declared.<i>: write one of function,
  call`.
- An entry key outside `function, call, title, body`: the unknown-keys problem of scope `testing.declared[]`, as for
  `testing.tables[]`.
- `function` not a name pattern (the current test: a string that `names.is_name` accepts with `*` read as a letter):
  `testing.declared.<i>.function: must be a function name pattern: a name with \`*\` for any text`.
- A `function` form with `title` or `body`: `testing.declared.<i>.title: a function form takes no slot: drop title`
  (likewise `body`).
- `call` read by the existing `outside_names`, addressed `testing.declared.<i>.call`; an empty list is refused:
  `testing.declared.<i>.call: must list at least one callee`.
- A `call` form with no `title` / no `body`: `testing.declared.<i>: missing \`title\`` / `missing \`body\``.
- `title` and `body` read by `_place`, addressed `testing.declared.<i>.title` / `.body`.
- `globals` optional, read by `outside_names` at `testing.globals`; left out: none.
- Other `testing` texts that name `functions` say `declared`: `_PRESET_MAP` becomes `{files, declared}`; the
  not-a-mapping texts in `framework_patterns` and `_testing` say "the patterns of a test file's name and the forms that
  declare a test"; the missing-`testing` text (`profile_parsing.py:959`) becomes `write testing: <preset>, or testing:
  {files: [<pattern>, ...], declared: [{function: <pattern>}]}`; the module docstring line 11 reads `testing: <preset> |
  {files, declared, globals, skips, tables, mocks}`.
- `xarch/architectures/presets/testing/pytest.yaml` writes `declared:` / `  - function: "test_*"` in place of
  `functions:`; its header comment says "how a test is declared".

### B3. Keys, needs, retirement

- `key_table.py`: `Key(TESTING, "functions", ...)` goes; `Key(TESTING, "declared", True, rules=("scenario-coverage", "stand-ins"),
  opens=DECLARED)` (the rules `functions` has today) and `Key(TESTING, "globals", rules=("scenario-coverage", "stand-ins"))` come in its place, and a
  scope `DECLARED = "testing.declared"` with `SCOPES[DECLARED] = "testing.declared[]"` holds `function`, `call`,
  `title`, `body`, each `rules=("scenario-coverage",)` (none required at the key-table level; B2 enforces the slots).
- `NEEDS` gains `"testing.declared[].function": ("test.function",)` and `"testing.declared[].call": ("test.call",)`.
- Under Python, a `call` form is refused with the needs refusal:
  `testing.declared.0.call: its check reads test.call (the tests a call with a title declares), which the language
  python does not supply: drop testing.declared.0.call, or check the app with a language whose reader supplies
  test.call`. A `function` form gives no needs problem under Python.
- `profile_keys.py` retired table gains `Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function:
  "<pattern>"}]')`. A map, inline or in a preset, writing `functions` gets exactly:
  `testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: "<pattern>"}]; use declared, files,
  globals, mocks, skips, tables` (the note's text plus `globals`, since `advice` lists the scope's known keys, sorted).
  Writing `functions` in place of `declared` also gives the missing-`declared` problem.
- `keys.yaml`: the `testing.functions` entry goes; entries for `testing.declared`, `testing.declared[].function`,
  `testing.declared[].call`, `testing.declared[].title`, `testing.declared[].body` and `testing.globals` come in, each
  with meaning, accepts and example. The `testing` fragment (line 29-32) and the `testing` key's example (line 150-152)
  write `declared:` with `- function: "check_*"`; the `testing` accepts text (line 145) names `{files, declared,
  globals, skips, tables, mocks}`; `tiers.<tier>.plain_tables` (line 591) says "no test of the tier" for "no test
  function of the tier". `xarch profile explain testing.declared.call` prints its entry.

### B4. The reader

- The port `SourceTree.read` (`source_tree.py`) gains keyword-only `declared: tuple[TestForm, ...] = ()` and `globals:
  tuple[tuple[str, ...], ...] = ()`; its docstring says a file holds a test for each function whose name matches a
  `function` form, and that a use or call of a global's name the file does not bind is read as the global's bare dotted
  name. `FsSourceTree.read` and `_parsed` carry them; `parsed()` passes none.
- `services/source_check.py` passes the framework's `declared` and `globals` when reading the tests root, and none for
  the app. `holding.py` and `sources.py` read app files: unchanged.
- Python reader (`fs_source_tree.py`), function forms: each function or method whose name matches a `function` form's
  pattern (`fnmatchcase`, the first matching form) is in `tests` as `Test(f.line, f.name, index, False, f)`, the very
  `Function` that is in `functions`, in the order of `functions`. A `call` form is ignored by this reader (it never
  reaches it under Python: B3 refuses it).
- Python reader, globals: a bare name the file does not bind (no import, no definition, no assignment at the top level)
  whose name is the first step of a global is read as that global, so `it.skip()` gives a call whose callee is
  `("it", "skip")` and a use whose ref is the same; a name the file binds keeps its own binding; with no globals the
  reader reads as today. A global never yields a `builtins.` ref.
- The module docstring (the reader contract) gains a paragraph on tests and globals.

### B5. The checks

`scenarios.py` reads `test.tests` wherever it read the functions matching `framework.functions`:

- `_tests` returns `file.tests`; tables, mentions, asserts, blocks and expressions are read from `Test.body`;
  "standalone" tests are tests whose body holds no table; `_named` reads the bodies' mentions.
- A test is printed by its name, in double quotes when `titled` (`"places an order"`), bare otherwise. `weak` says
  `<Union> variant <V> is credited to "rejects when out of stock" by name only: no assert in their bodies` at the first
  credited test's line; `_branches` (scenario-coverage and `plain`) says `"places an order" has an \`if\` in its
  body`. A function's name prints as today. When several tests are credited, `weak` joins their printed names with `, `, each printed as above.
- `plain` reads each test of the file with a table, as above.
- The module docstring says "a test" (one the framework declares, `testing.declared`) in place of "a test function,
  one whose name matches the profile's pattern".
- `tests/architecture/test_agnostic.py:75` reads the stems of the declared `function` patterns:
  `(*files, *(form.function for form in declared if form.function))`.

### B6. Test-only frameworks

- `tests/fakes/frameworks/stub.yaml` becomes whole (note 2.7 item 3): `declared` with form 0 `function: "test*"`
  (the existing hand-built tests keep their meaning) and form 1 a `call` form, `call: ["vitest#it", "vitest#test",
  "vitest#it.each", "vitest#test.each"]`, `title: {position: 0}`, `body: {position: 1}`; `globals: [expect]`; its
  header comment says so. It loads under `brace` (no `supplies`, so no needs refusal).
- `tests/bootstrap/test_no_table_form.py` (the %UnitTest-like framework, note 2.7 item 4, 2.9) writes `declared:` /
  `- function: "Test*"`, keeping `tables: []`, and its findings stay as they are.
- Inline maps that write `functions:` in tests (`test_loop_tables.py:12`, `test_other_framework.py:12`,
  `test_profile_file.py:147`, others found by grep) write `declared: [{function: ...}]`, their expectations unchanged.

### B7. Docs and re-grep

- README line 116: `testing:  <preset> | {files*, declared*, globals, skips, tables, mocks}`, and one sentence on the
  two forms and that the call form is proved on hand-built facts (no reader supplies `test.call` yet).
- CHANGELOG `[Unreleased]`: `testing.declared` (function and call forms), `testing.globals`, the `Test` fact and
  `SourceFile.tests`, facts `test.function` (Python supplies it) and `test.call` (none supplies it), weak quoting
  titles; under a removal/change heading, `testing.functions` retired with its hint.
- `git grep -n "testing\.functions\|framework\.functions\|functions: \"" -- xarch tests README.md architecture.yaml`
  returns only the retired-keys entry, its refusal tests and the CHANGELOG line.

## Out of scope

- `testing.preset` (6.9), `testing.beside` and placing tests beside the code, `tier_of`, `test-tree` texts (6.10).
- The cross-check that a table form's `call` names a callee some `declared` call form lists (note 2.7 item 2; 6.11).
- A reader for `test.call`; a TypeScript or ObjectScript reader; a Jest or Vitest preset (note "leaves out").
- Spec forms of `writing` (2.7 item 5, release step 22).
- Any `test` kind in the facts vocabulary or `where` filters beyond wording.

## Tests that prove it (written first)

Tiers as the repository uses them: unit tests of pure logic under `tests/modules/<module>/...` mirroring the code;
adapter tests under `tests/modules/rules/adapters/` read real source through the real reader; bootstrap tests under
`tests/bootstrap/` run the wired app on files in `tmp_path`; architecture tests under `tests/architecture/` guard the
repository itself.

### Unit, spec: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`

Profile parsing is pure logic over a document; this file holds every other `testing` parsing test.

1. `declared: [{function: "test_*"}]` parses to `Framework(..., declared=(TestForm(function="test_*"),))`.
2. A call form parses to `TestForm(call=(("it",),), title=Place(position=0), body=Place(position=1))`; `globals: [it,
   expect]` to `(("it",), ("expect",))`.
3. Refusals, one `pytest.param` each with its exact text: missing `declared`; `declared: []`; `declared: "test_*"`;
   an entry with both holders; with none; a bad function pattern; a function form with `title`; a call form missing
   `title`; missing `body`; `call: []`; a bad `title` place; an unknown entry key.
4. The stub loader test (6.7's) expects `declared` with the two forms and `globals=(("expect",),)`.
5. Messages that named `functions` (`PRESET_PROBLEM`, the missing-`testing` texts at :405, :685, :718) say `declared`.

### Unit, spec: `tests/modules/spec/application/logic/test_retired_keys.py`

The retired table's one-wording texts are tested here.

6. `testing: {files: [...], functions: "test_*", declared: [...]}` gives exactly the retired text of B3; the same
   through a preset map.

### Unit, spec: `tests/modules/spec/application/logic/test_profile_needs.py`

Needs are pure logic over the key table and a language's supplies.

7. The NEEDS of `testing.declared[].function` and `.call` (extend the table at :554-559).
8. Under `python`, an inline call form gives the B3 refusal at `testing.declared.0.call`; a function form gives none.
9. `test_needs_agree.py` (wherever it lives) stays green with the two new facts.

### Unit, spec: `tests/modules/spec/domain/test_profile_keys.py`, `tests/bootstrap/test_profile_explain.py`

10. The `testing.declared[]` scope holds `function, call, title, body`; `testing.functions` is no key; every key has a
    `keys.yaml` entry (the existing coverage test). `profile explain testing.declared.call` prints its meaning
    (bootstrap: explain runs through the wired CLI).

### Adapter: `tests/modules/rules/adapters/test_fs_source_tree.py`

The Python reader is only provable on real Python source through the real adapter.

11. With `declared=(TestForm(function="test_*"),)`, a file with `test_a`, `helper` and a class method `test_b` holds
    `tests` for `test_a` and `test_b` (form 0, `titled=False`), each `body is` the `Function` in `functions`; `helper`
    is no test.
12. Two function forms, a name matching both: one test, the first form's index.
13. With no `declared`, `tests == ()`.
14. With `globals=(("it",),)`, `it.skip()` in a file that does not bind `it` gives a call with callee `("it", "skip")`;
    with `from x import it` the import's binding wins; without globals the call is read as today (assert the
    pre-change callee, found by running the reader first).

### Unit, rules: `tests/modules/rules/application/logic/test_scenarios.py`

The checks are pure logic over hand-built facts; the hand-built call-form tests are the note's 2.9 proof.

15. Existing scenario tests built from functions now build `tests` too (a builder helper, below); their findings are
    unchanged.
16. A file whose functions match the old pattern but whose `tests` is empty: no table test is found (proves one path).
17. Under `STUB`/`BRACE`: a `Test(line, "places an order", 1, True, body)` whose body holds a `Table(form=1)` covering
    the union passes; a row problem is worded in Brace's writing as in 6.7.
18. `plain`: a titled call test with an `if` in its body under a `plain_tables` tier says `"places an order" has an
    \`if\` in its body, and a table test of the unit tier holds no branch (...)`.
19. `weak`: a titled standalone test naming a variant with no assert says `credited to "rejects when out of stock" by
    name only`; an untitled one prints bare; a titled test with `name=""` still counts and prints `""`.
20. A call-form test is not among `functions` and still credits a variant (it lives in `tests` only).

### Unit, builders: `tests/modules/rules/builders.py`

21. `STUB` is built from `stub.yaml`'s `declared` and `globals`; a helper builds `Test` values from functions for a
    function form, so scenario tests state their tests in one call. Every `Framework(` in tests (`builders.py:114,
    :177`, `test_spec_profile.py:62, :122`, `test_expandable.py:23`, `test_tier_of.py:84`, `test_enforcement.py:33,
    :112`, `test_where.py:40, :319`, `test_never_use.py:21`, `test_scenarios.py:323`,
    `test_profile_parsing_tests.py:35, :731`, `test_bundled_guards.py:39`) writes `declared`.

### Bootstrap

22. `tests/bootstrap/test_profile_file.py:92` asserts `architecture.framework.declared == (TestForm(function="test_*"),)`.
23. `test_no_table_form.py`, `test_loop_tables.py`, `test_other_framework.py` pass with `declared` maps, findings
    unchanged (end to end through the real reader: proves function forms select what `functions` selected).
24. The corpora tests and the golden-docs tests pass unchanged.

### Architecture

25. `tests/architecture/test_agnostic.py` reads declared function patterns and stays green.

### Gates

`uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check
architecture.yaml`, then `uv run pytest -q` in the background (over two minutes), all green on this branch alone.
Regenerate `docs/{cli,web,xarch}/testing.md` and read the diff: expected empty.

## Notes for the planner

- Change the values (B1) and every `Framework(` caller in one task, or the suite breaks between tasks.
- Probe today's reading of `it.skip()` with no import before writing test 14, and mirror how `_Calls` binds builtins
  (`fs_source_tree.py:259`) for globals, checked after the file's own bindings and before builtins.
- `_branches` takes the printed name (or the `Test`) so call tests are worded by title; keep `Function`-only callers
  out.
- The `use ...` list of the retired text is computed by `advice`; assert the full text, do not build it.

---

# 6.8 spec: `testing.declared` names how a framework declares its tests, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A framework declares its tests by `testing.declared` (function forms and call forms) and may list `globals`; the reader turns the forms into `Test` facts on `SourceFile.tests`, which scenario-coverage, `plain_tables` and `weak` read alone; `testing.functions` is retired; under pytest nothing a user sees moves.

**Architecture:** Values first (`TestForm`, `Test`, `SourceFile.tests`) with the Python reader filling `tests` from function forms and reading globals (additive, Task 1). Then one atomic switch (Task 2): `Framework` loses `functions` and gains `declared`/`globals`, the loader parses the new keys, the key table and `keys.yaml` learn them, `scenarios.py` reads `file.tests`, `source_check` hands the forms to the reader, and every caller in the tests follows. Then the retired hint (Task 3), the needs facts (Task 4), the quoting of titled tests with the hand-built call-form proof (Task 5), and docs and gates (Task 6).

**Tech Stack:** Python 3.13, pytest, ruff, uv, PyYAML; xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/6-8-spec-testing-e3450e17.md` (prepended above).

## Global Constraints

- The key is `testing.declared`, never `testing.tests`.
- `declared` is required with at least one form; no hidden default meaning `test_*`.
- One path: `scenarios.py` reads `file.tests` only; no `fnmatchcase` and no `fnmatch` import stays in it.
- A framework's `globals` get the `Ref` of their bare dotted name (`("it", "skip")`), never `builtins.<name>`; the language's `namespace` is unchanged.
- Python's `supplies` lists `test.function: exact` and does not list `test.call`; the Python reader gains no `call` form.
- A `function` form's test has the very `Function` that is in `functions` as its `body`; a `call` form's test is in `tests` only.
- App files are read with no forms, so they hold no tests.
- `weak` prints a titled test's name in double quotes, a function's bare; the checking code reads `titled` and writes no language syntax.
- Problems address an entry by its index from 0 (`testing.declared.0.call`); `profile explain` takes the key without one (`testing.declared.call`).
- Recorded corpora (`tests/bootstrap/corpora/`) and golden docs `docs/{cli,web,xarch}/testing.md` do not move; golden docs are regenerated by their tests and their diff read, never edited by hand; expected diff empty.
- No comments in xarch's code (docstrings are the documentation; YAML data files under `tests/fakes/` and presets keep their header comment); never `ruff --fix` (fix an import order by hand); tests written first; Python only in `xarch/modules/rules/adapters/fs_source_tree.py` and the data files under `xarch/architectures/presets/`; `.claude/` out of commits; nothing pushed; README and CHANGELOG lines under `[Unreleased]`.
- Test modules import `Test` and `TestForm` under aliases, `Test as DeclaredTest` and `TestForm as DeclaredForm`, each in its own `from ... import ... as ...` statement: pytest collects every class in a test module whose name starts with `Test`, and these dataclasses would raise a collection warning. Helper modules that pytest does not collect (`tests/modules/rules/builders.py`, `tests/fakes/filesystem.py`) import them by their own names.
- No string literal in `xarch/` may hold `test_` or `_test` at the start of a word (`tests/architecture/test_agnostic.py` scans every literal), and none in `scenarios.py` may be `decorator`, `call` or `loop` (`tests/architecture/test_table_forms.py`). No function in `xarch/` is named `test_*` (a test module importing it would collect it): the parser is `declared_forms`.
- Commit messages are one plain sentence, as the log's, ending with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Deviation from the spec, decided here

- B2 says `call` and `globals` are "read by the existing `outside_names`". That function refuses an outside name of fewer than two steps, but the spec's own examples (`call: [it, test]`, `globals: [it, expect]`, test 2's `(("it",),)`) are one step. `outside_names` and `_outside_name_at` gain a keyword `least: int = 2`; `declared[].call` and `globals` read with `least=1`; every other caller keeps two. The refusal text is unchanged.
- Test 2 of the spec (a call form parses) runs under the test-only language Brace: under Python the call form is refused for `test.call` once Task 4 lands, and the parse test would then fail for a reason it does not test. Every call-form refusal of test 3 runs under Brace for the same reason.
- Under a star import the reader reads no global, as it reads no builtin then (the star import might bind the name). The spec is silent; the module docstring says so and Task 1 pins it.

## Review Focus

1. A test that binds a global's name itself (`it = make()` in its body) keeps its own binding: `it.skip()` is then no call of `("it", "skip")`. Pinned in Task 1 (`test_a_name_the_file_binds_keeps_its_own_binding_over_a_global`).
2. A file holding a star import reads no global, as it reads no builtin. Pinned in Task 1 (`test_a_file_with_a_star_import_reads_no_global`).
3. A global whose name is also a builtin (`globals: [print]`) is read as the global, never as `builtins.print`. Pinned in Task 1 (`test_a_global_named_as_a_builtin_is_read_as_the_global`).
4. An entry of `declared` that is no mapping (`declared: [null]`) is refused at its index, not with a crash. Pinned in Task 2 (the `an entry that is no mapping` row of `test_a_bad_declared_is_refused`).
5. A call form written in a preset (not inline) is refused under Python at its index as an inline one is. Pinned in Task 4 (`test_a_call_form_in_a_testing_preset_is_refused_at_its_index`).

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| `xarch/profile_values/testing.py` | `TestForm`; `Framework(files, declared, skips, tables, globals)` | 1, 2 |
| `xarch/modules/rules/domain/parsed.py` | `Test`; `SourceFile.tests` | 1 |
| `xarch/modules/rules/application/ports/source_tree.py` | `read(..., declared=, globals=)` contract | 1 |
| `xarch/modules/rules/adapters/fs_source_tree.py` | tests from function forms; globals read as bare names | 1 |
| `tests/fakes/filesystem.py` | `FakeSourceTree.read` takes and records the new keywords | 1 |
| `xarch/modules/spec/domain/profile_keys.py` | scope `DECLARED`; retired `functions` | 2, 3 |
| `xarch/modules/spec/domain/key_table.py` | keys `declared`, `globals`, the `declared[]` slots; NEEDS | 2, 4 |
| `xarch/modules/spec/application/logic/profile_checks.py` | `declared_forms`, `framework_patterns`, `outside_names(least=)` | 2 |
| `xarch/modules/spec/application/logic/profile_parsing.py` | texts that named `functions` | 2 |
| `xarch/architectures/presets/format/keys.yaml` | texts of the new keys | 2 |
| `xarch/architectures/presets/testing/pytest.yaml` | `declared: [{function: "test_*"}]` | 2 |
| `xarch/modules/rules/application/logic/scenarios.py` | reads `file.tests`; titled names quoted | 2, 5 |
| `xarch/modules/rules/application/services/source_check.py` | hands the forms and globals to the tests read | 2 |
| `xarch/profile_values/capabilities.py`, `xarch/architectures/presets/language/python.yaml` | facts `test.function`, `test.call` | 4 |
| `tests/fakes/frameworks/stub.yaml`, `tests/modules/rules/builders.py` | the whole test-only framework; `tests_of`, `declaring` | 2 |
| README.md, CHANGELOG.md | docs | 6 |

---

### Task 1: The values and the Python reader: tests from function forms, globals read as bare names

**Files:**
- Modify: `xarch/profile_values/testing.py` (module docstring; new `TestForm` after `Place`)
- Modify: `xarch/modules/rules/domain/parsed.py` (new `Test` after `Function`; `SourceFile` docstring and field `tests`)
- Modify: `xarch/modules/rules/application/ports/source_tree.py` (`read`)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring; imports; `FsSourceTree.read`; `_parsed`; new `_tests`; `_ref`; `_reached`; `_Calls.__init__`, `visit_Call`, `_use`)
- Modify: `tests/fakes/filesystem.py` (`FakeSourceTree.__init__`, `read`, docstring; import)
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/modules/rules/domain/test_parsed.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `xarch.profile_values.testing.TestForm(function: str = "", call: tuple[tuple[str, ...], ...] = (), title: Place | None = None, body: Place | None = None)`, frozen.
  - `xarch.modules.rules.domain.parsed.Test(line: int, name: str, form: int, titled: bool, body: Function)`, frozen.
  - `SourceFile.tests: tuple[Test, ...] = ()` (last field).
  - `SourceTree.read(root, paths, tables=(), immutable=(), interface=(), *, standard, private, special, declared: tuple[TestForm, ...] = (), globals: tuple[tuple[str, ...], ...] = ()) -> list[SourceFile]`.
  - `FakeSourceTree.forms: list[tuple[TestForm, ...]]` and `FakeSourceTree.bound: list[tuple[tuple[str, ...], ...]]`, appended on every `read`, in call order.

- [ ] **Step 1: Write the failing adapter tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, below the existing `from xarch.modules.rules.domain.parsed import (...)` block add the statement `from xarch.modules.rules.domain.parsed import Test as DeclaredTest`, and below `from xarch.profile_values.testing import Place, RowId, TableForm` add `from xarch.profile_values.testing import TestForm as DeclaredForm`. Append at the end of the file:

```python
TESTS = """def test_a():
    assert True


def helper():
    pass


class TestB:
    def test_b(self):
        pass
"""
"""A test file of a function, a helper and a method of a class, by the names pytest would take for tests."""
SKIPPED = "def test_a():\n    it.skip()\n"
"""A test calling a method of a name the file does not bind."""


def declared_in(tmp_path: Path, text: str, declared: tuple[DeclaredForm, ...] = (),
                bound: tuple[tuple[str, ...], ...] = ()) -> SourceFile:
    """The text read as a test file is, handed the forms that declare a test and the framework's globals."""
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, declared=declared, globals=bound,
                                           **HANDED)[0]


def test_a_function_or_a_method_whose_name_matches_a_function_form_is_a_test_whose_body_is_that_function(tmp_path):
    found = declared_in(tmp_path, TESTS, (DeclaredForm(function="test_*"),))
    assert [function.name for function in found.functions] == ["test_a", "helper", "test_b"]
    assert found.tests == (DeclaredTest(1, "test_a", 0, False, found.functions[0]),
                           DeclaredTest(10, "test_b", 0, False, found.functions[2]))
    assert found.tests[0].body is found.functions[0] and found.tests[1].body is found.functions[2]


def test_a_function_is_a_test_of_the_first_form_it_matches_once_and_a_call_form_declares_none_this_reader_reads(
        tmp_path):
    call = DeclaredForm(call=(("it",),), title=Place(0), body=Place(1))
    found = declared_in(tmp_path, "def test_a():\n    pass\n\n\ndef testb():\n    pass\n",
                        (call, DeclaredForm(function="test_*"), DeclaredForm(function="test*")))
    assert [(test.name, test.form, test.titled) for test in found.tests] == [("test_a", 1, False), ("testb", 2, False)]


def test_a_file_read_with_no_form_holds_no_test(tmp_path):
    assert declared_in(tmp_path, TESTS).tests == ()


def test_a_name_the_file_does_not_bind_that_a_global_starts_is_read_as_that_global_in_a_call_and_a_use(tmp_path):
    found = declared_in(tmp_path, SKIPPED, bound=(("it",),))
    assert (found.calls, found.method_calls) == ((Call(2, ("it", "skip")),), ())
    assert Use(2, ("it", "skip"), 0) in found.uses


def test_with_no_globals_a_bare_name_the_file_does_not_bind_is_read_as_before(tmp_path):
    found = declared_in(tmp_path, SKIPPED)
    assert (found.calls, found.uses, found.method_calls) == ((), (), (MethodCall(2, "skip", False),))


def test_a_name_the_file_binds_keeps_its_own_binding_over_a_global(tmp_path):
    imported = declared_in(tmp_path, "from x import it\n\n\ndef test_a():\n    it.skip()\n", bound=(("it",),))
    assert imported.calls == (Call(5, ("x", "it", "skip")),)
    local = declared_in(tmp_path, "def test_a():\n    it = make()\n    it.skip()\n", bound=(("it",),))
    assert (local.calls, local.method_calls) == ((), (MethodCall(3, "skip", False),))


def test_a_global_named_as_a_builtin_is_read_as_the_global(tmp_path):
    found = declared_in(tmp_path, "def test_a():\n    print(1)\n", bound=(("print",),))
    assert found.calls == (Call(2, ("print",), (None,)),)
    assert [use.name for use in found.uses] == [("print",)]


def test_a_file_with_a_star_import_reads_no_global(tmp_path):
    found = declared_in(tmp_path, "from x import *\n\n\ndef test_a():\n    it.skip()\n", bound=(("it",),))
    assert (found.calls, found.method_calls) == ((), (MethodCall(5, "skip", False),))
```

`MethodCall` and `Use` and `Call` are already imported at the top of the file.

- [ ] **Step 2: Write the failing value test**

In `tests/modules/rules/domain/test_parsed.py`, add below `from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row, Table` the statement `from xarch.modules.rules.domain.parsed import Test as DeclaredTest`. In the parametrization of `test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python`, add after `pytest.param(Table.__doc__, id="the docstring of a table"),`:

```python
    pytest.param(DeclaredTest.__doc__, id="the docstring of a test"),
```

And append at the end of the file:

```python
def test_a_test_is_its_line_its_name_the_index_of_its_form_whether_it_is_titled_and_its_body():
    body = Function(3, "test_a")
    test = DeclaredTest(3, "test_a", 0, False, body)
    assert (test.line, test.name, test.form, test.titled, test.body) == (3, "test_a", 0, False, body)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/domain/test_parsed.py`
Expected: FAIL at collection with `ImportError: cannot import name 'Test' from 'xarch.modules.rules.domain.parsed'`.

- [ ] **Step 4: Add `TestForm`**

In `xarch/profile_values/testing.py`, replace the module docstring's first sentence by:

```python
"""How a project's tests are named and placed, as the profile says it: the test framework's names, the forms that
declare a test, the table forms it writes, the scenario-coverage and stand-ins guards, and where the fakes live."""
```

and add after the class `Place`:

```python
@dataclass(frozen=True)
class TestForm:
    """One form a test is declared in, as the framework's `testing.declared` says it, exactly one of two: a function
    whose name matches function, a pattern with `*` for any text; or a call of one of call's dotted names, the test's
    title the argument at title and its body the one at body (both set exactly when call is)."""
    function: str = ""
    call: tuple[tuple[str, ...], ...] = ()
    title: Place | None = None
    body: Place | None = None
```

- [ ] **Step 5: Add `Test` and `SourceFile.tests`**

In `xarch/modules/rules/domain/parsed.py`, add after the class `Function` (after its `real_statements` property):

```python
@dataclass(frozen=True)
class Test:
    """A test a test file declares, in one of the forms of the framework's `testing.declared`: its line; its name, a
    title's text when titled (a call form's; "" for a title that is no plain literal, and the test still counts), else
    its function's name; form, the index of its form in that list; and body, the function whose mentions, asserts,
    blocks, expressions and tables the checks read (for a function form, the very function among the file's)."""
    line: int
    name: str
    form: int
    titled: bool
    body: Function
```

In `SourceFile`'s docstring, replace the last sentence `error is how it fails to parse, and then it holds nothing else.` (it wraps across two lines in the file: it starts with `error is how it fails to` at the end of the `pieces` sentence's line) by:

```
tests are the tests it declares, as its reader reads them by the framework's forms
    (see Test): a function form's are also among its functions, a call form's are not; a file read with no form holds
    none. error is how it fails to parse, and then it holds nothing else.
```

keeping the docstring's lines at most 120 characters, and add the last field:

```python
    tests: tuple[Test, ...] = ()
```

- [ ] **Step 6: Extend the port**

In `xarch/modules/rules/application/ports/source_tree.py`, change the import to `from xarch.profile_values.testing import TableForm, TestForm` and replace `read` by:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], tables: tuple[TableForm, ...] = (),
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str, declared: tuple[TestForm, ...] = (),
             globals: tuple[tuple[str, ...], ...] = ()) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in one of the forms `tables` holds, each tagged with the index of its form; with none, no
        table is recognised. A file holds a test for each function whose name matches the pattern of a function form
        `declared` holds, tagged with the index of the first such form; with none, it holds no test. A use or a call
        of a bare name the file does not bind that is the first step of one of `globals` is read as that bare name,
        never as one of the language's builtins. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so. An absolute import is of the standard library when its first step is one of the modules
        `standard` holds; a relative one never is. A name is public unless it starts with `private`, how the
        language starts a private name ("": every name is public). A class is a record when every method's name
        matches `special` in full, a regular expression ("": no name is special), and a top-level function of its
        file names it in its return annotation."""
        ...
```

- [ ] **Step 7: Read tests and globals in the Python reader**

In `xarch/modules/rules/adapters/fs_source_tree.py`:

1. Add `from fnmatch import fnmatchcase` to the standard-library imports (between `from dataclasses import dataclass` and `from pathlib import Path`: ruff's isort puts `fnmatch` after `dataclasses`), add `Test,` to the `from xarch.modules.rules.domain.parsed import (...)` list between `Table,` and `Union,`, and change the last import to `from xarch.profile_values.testing import Place, TableForm, TestForm`.

2. Append to the module docstring, after the paragraph `Any other form reads no table, and the next form of the list is still tried.`:

```
A file read for tests holds a test for each of its functions, a method too, whose name matches the pattern of a
function form of the framework's `testing.declared`, as fnmatch matches a name: it is a test of the first such form,
tagged with that form's index, untitled, its name the function's and its body that very function, in the order of the
functions. A call form declares no test this reader reads: Python's reader does not supply `test.call`. A file read
with no form holds no test.

A bare name no scope binds whose name is the first step of one of the framework's globals (`testing.globals`) is read,
in a call, an argument and a use, as itself, ahead of a builtin: `it.skip()` calls ("it", "skip"), which is also its
use, bound none of its steps; a global is never read as ("builtins", <name>). A name the file binds, by an import, a
definition or an assignment in any scope around the reading, keeps its own binding. A file that holds a star import
reads no global, as it reads no builtin, since the star import might bind the name.
```

3. In `FsSourceTree.read`, add the keywords and pass them:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], tables: tuple[TableForm, ...] = (),
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str, declared: tuple[TestForm, ...] = (),
             globals: tuple[tuple[str, ...], ...] = ()) -> list[SourceFile]:
```

and replace the last `found.append(_parsed(...))` of the loop by:

```python
            found.append(_parsed(name, path, text, tables, immutable, interface, standard, private, special,
                                 _Where((root.name, *path[:-1]), root, self._fs), declared, globals))
```

4. Replace `_parsed` by:

```python
def _parsed(name: str, path: tuple[str, ...], text: str, forms: tuple[TableForm, ...], marks: tuple[RecordMark, ...],
            interface: tuple[InterfaceMark, ...], standard: frozenset[str], private: str, special: str,
            where: _Where | None = None, declared: tuple[TestForm, ...] = (),
            bound: tuple[tuple[str, ...], ...] = ()) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=Unparsable(e.lineno or 0, e.msg))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=Unparsable(0, str(e)))
    star = _star_import(tree)
    calls = _Calls(_BUILTINS if not star else frozenset(), where,
                   frozenset(steps[0] for steps in bound) if not star else frozenset())
    calls.visit(tree)
    functions = _functions(tree, forms, private, where)
    return SourceFile(name, path, tuple(_imports(tree, standard, private, where)), comments, functions,
                      tuple(_unions(tree)), calls=tuple(calls.found),
                      classes=tuple(_classes(tree, private, special, functions, marks, interface, where)),
                      uses=tuple(calls.uses), parameter_calls=tuple(calls.parameter_calls),
                      module_functions=_module_functions(tree), named=_named(tree), callbacks=tuple(calls.callbacks),
                      method_calls=tuple(calls.method_calls), constants=tuple(_constants(tree, private)),
                      unmentioned=_unmentioned(tree), pieces=_pieces(tree), tests=_tests(functions, declared))


def _tests(functions: tuple[Function, ...], declared: tuple[TestForm, ...]) -> tuple[Test, ...]:
    """Each function whose name matches the pattern of a function form, a test of the first such form, untitled, its
    body the function itself, in the order of the functions; a call form declares none this reader reads."""
    found: list[Test] = []
    for function in functions:
        form = next((index for index, held in enumerate(declared)
                     if held.function and fnmatchcase(function.name, held.function)), None)
        if form is not None:
            found.append(Test(function.line, function.name, form, False, function))
    return tuple(found)
```

5. Replace `_ref` and `_reached` by:

```python
def _ref(node: ast.AST, chain: list[Scope], bare: frozenset[str] = frozenset()) -> Ref:
    return _reached(node, chain, frozenset(), bare)[0]


def _reached(node: ast.AST, chain: list[Scope], names: frozenset[str],
             bare: frozenset[str] = frozenset()) -> tuple[Ref, int]:
    """The path a name or a chain of attributes on one reaches, and how many of its steps the import binding it names
    from the top (none for a relative import); a name no scope binds that is in bare is a global of the framework,
    read as its own bare name, and else one that is in names is a builtin."""
    attrs: list[str] = []
    while isinstance(node, ast.Attribute):
        attrs.insert(0, node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None, 0
    scope = next((scope for scope in chain if node.id in scope), None)
    if scope is None and node.id in bare:
        return (node.id, *attrs), 0
    if scope is None:
        return (("builtins", node.id, *attrs), 0) if node.id in names else (None, 0)
    base = scope[node.id]
    if base is None:
        return None, 0
    return (*base, *attrs), 0 if isinstance(base, _Relative) else len(base)
```

6. In `_Calls`: change `__init__`'s signature to `def __init__(self, builtins: frozenset[str] = frozenset(), where: _Where | None = None, bare: frozenset[str] = frozenset()) -> None:` and add `self._bare = bare` after `self._builtins = builtins`. In `visit_Call`, replace the three `_ref` calls:

```python
        func = _ref(node.func, self._chain, self._bare)
```

```python
            args = tuple(_ref(a, self._chain, self._bare) for a in node.args if not isinstance(a, ast.Starred))
            keywords = tuple((k.arg, _ref(k.value, self._chain, self._bare)) for k in node.keywords if k.arg is not None)
```

and in `_use`:

```python
        name, bound = _reached(node, self._chain, self._builtins, self._bare)
```

The docstring of `_Calls` becomes `"""Collects every call whose callee is a Ref, reading each name in the scope it is read in, a framework's global by its bare name."""`.

- [ ] **Step 8: Keep the fake in step with the port**

In `tests/fakes/filesystem.py`: change the import to `from xarch.profile_values.testing import TableForm, TestForm`; in `FakeSourceTree.__init__` add after `self.listed: list[tuple[str, ...]] = []`:

```python
        self.forms: list[tuple[TestForm, ...]] = []
        self.bound: list[tuple[tuple[str, ...], ...]] = []
```

replace `read`'s signature and its first lines by:

```python
    def read(self, root: Path, paths: list[tuple[str, ...]], tables: tuple[TableForm, ...] = (),
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str, declared: tuple[TestForm, ...] = (),
             globals: tuple[tuple[str, ...], ...] = ()) -> list[SourceFile]:
        self.handed.append(standard)
        self.prefixes.append(private)
        self.specials.append(special)
        self.forms.append(declared)
        self.bound.append(globals)
```

and in the class docstring replace `the pattern of a special name each is handed (specials), and the endings each listing is handed (listed)` by `the pattern of a special name each is handed (specials), the forms that declare a test and the globals each read is handed (forms, bound), and the endings each listing is handed (listed)`.

- [ ] **Step 9: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/ tests/modules/rules/domain/test_parsed.py`
Expected: PASS.

- [ ] **Step 10: Run the rules and spec suites and the gates on the touched code**

Run: `timeout 600 uv run pytest -q tests/modules/rules tests/architecture && uv run ruff check && uv run xarch check`
Expected: PASS; ruff `All checks passed!`; `xarch check` exits 0.

- [ ] **Step 11: Commit**

```bash
git add xarch/profile_values/testing.py xarch/modules/rules/domain/parsed.py \
  xarch/modules/rules/application/ports/source_tree.py xarch/modules/rules/adapters/fs_source_tree.py \
  tests/fakes/filesystem.py tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/domain/test_parsed.py
git commit -m "The Python reader turns the function forms it is handed into the tests of a file, and reads a framework's globals by their bare names

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The switch: `Framework.declared` and `globals`, parsed, keyed, read by the checks

This task changes `Framework`'s shape, so the loader, the key table, the data files, `scenarios.py`, `source_check.py` and every test that builds a framework or writes `functions:` change together; the suite is red between Step 2 and Step 14.

**Files:**
- Modify: `xarch/profile_values/testing.py` (`Framework`)
- Modify: `xarch/modules/spec/domain/profile_keys.py` (`DECLARED`, `SCOPES`)
- Modify: `xarch/modules/spec/domain/key_table.py` (imports; `_KEYS` testing block)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (imports; `DECLARING`, `CALL_SLOTS`; `declared_forms` and its helpers; `_outside_name_at`, `outside_names`; `framework_patterns`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (module docstring line 11; `_PRESET_MAP`; `_Testing` docstring; `_testing`; the missing-`testing` text)
- Modify: `xarch/modules/spec/domain/values.py` (docstring of `framework`), `xarch/modules/rules/domain/profile.py` (docstring of `framework`)
- Modify: `xarch/architectures/presets/testing/pytest.yaml`, `xarch/architectures/presets/format/keys.yaml`
- Modify: `xarch/modules/rules/application/logic/scenarios.py`, `xarch/modules/rules/application/services/source_check.py`
- Modify: `tests/fakes/frameworks/stub.yaml`, `tests/modules/rules/builders.py`
- Modify (callers): `tests/bootstrap/test_bundled_guards.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/modules/rules/application/logic/test_enforcement.py`, `test_expandable.py`, `test_never_use.py`, `test_tier_of.py`, `test_where.py`, `tests/modules/spec/profiles.py`, `tests/modules/spec/application/builders.py`, `tests/modules/spec/application/origins.py`, `tests/modules/spec/application/test_profile_loading.py`, `tests/modules/spec/application/logic/test_profile_language.py`, `test_profile_needs.py`, `test_profile_parsing_substance.py`, `test_testing.py`, `test_retired_keys.py`, `tests/bootstrap/test_architecture_files.py`, `test_loop_tables.py`, `test_no_table_form.py`, `test_other_framework.py`, `test_profile_file.py`, `test_written_rules.py`, `tests/architecture/test_agnostic.py`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, `tests/modules/spec/application/test_explain.py`, `tests/modules/spec/domain/test_profile_keys.py`, `tests/bootstrap/test_profile_explain.py`, `tests/modules/rules/application/logic/test_scenarios.py`, `tests/modules/rules/application/test_check_app.py`

**Interfaces:**
- Consumes: `TestForm`, `Test`, `SourceFile.tests`, `SourceTree.read(..., declared=, globals=)`, `FakeSourceTree.forms`/`.bound` (Task 1).
- Produces:
  - `Framework(files: tuple[str, ...], declared: tuple[TestForm, ...], skips=(), tables=(), globals: tuple[tuple[str, ...], ...] = ())`.
  - `profile_keys.DECLARED = "testing.declared"`, `SCOPES[DECLARED] == "testing.declared[]"`.
  - Keys `testing.declared` (required), `testing.globals`, `testing.declared[].function|call|title|body`.
  - `profile_checks.declared_forms(value, where, problems, language) -> tuple[TestForm, ...] | None`; `outside_names(value, where, problems, language, least: int = 2)`.
  - `tests/modules/rules/builders.py`: `declared_of(file: dict, member: str) -> tuple[TestForm, ...]`, `tests_of(functions: tuple[Function, ...], framework: Framework) -> tuple[Test, ...]`, `declaring(path: str, *functions: Function, framework: Framework | None = None, language: CheckedLanguage = PYTHON, tests: tuple[Test, ...] | None = None, **fields) -> SourceFile`; `STUB.declared`, `STUB.globals` read from `stub.yaml`.

- [ ] **Step 1: Write the failing parse tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

1. Add, below `from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId, ScenarioCoverage, StandIns, TableForm`, the statement `from xarch.profile_values.testing import TestForm as DeclaredForm`.

2. Replace lines 28-72 (from `PRESET_PROBLEM = ...` to the last line of `test_a_bad_testing_key_is_refused`, its `assert problems(...) == expected`; line 72 is part of the old test, so a replacement that stops at 71 leaves a stray indented `assert`) by:

```python
PRESET_PROBLEM = ("layered.yaml: testing: must be a preset name or a mapping {files, declared}: the patterns of a "
                  "test file's name and the forms that declare a test")
BY_NAME = [{"function": "test_*"}]
"""The one form that declares a test by its function's name, as an entry of `testing.declared`."""


def test_the_framework_is_a_preset_by_name_or_the_map_written_out():
    named = parsed(covered(testing="pytest"))
    written = parsed(covered())
    assert named.framework == written.framework == Framework(
        ("test_*.py", "*_test.py"), (DeclaredForm(function="test_*"),), (("pytest", "mark", "skip"), ("pytest", "skip")),
        (PYTEST_FORM,))


def test_a_preset_is_the_same_map_validated_like_one_written_in_the_file():
    broken = {"files": ["test_*.py"], "declared": [{"function": 3}]}
    assert problems(covered(testing="odd"), presets={"odd": broken}) == [
        "layered.yaml: testing.declared.0.function: must be a function name pattern: a name with `*` for any text"]


@pytest.mark.parametrize("testing, presets, expected", [
    pytest.param("rspec", PRESETS, ["layered.yaml: testing: no preset 'rspec': use pytest, or write the map "
                                    "{files, declared}"], id="a preset that does not exist"),
    pytest.param("rspec", {}, ["layered.yaml: testing: no preset 'rspec': write the map {files, declared}"],
                 id="no preset at all"),
    pytest.param(3, PRESETS, [PRESET_PROBLEM], id="not a name or a map"),
    pytest.param({"declared": BY_NAME}, PRESETS, ["layered.yaml: testing: missing `files`"], id="no files"),
    pytest.param({"files": ["test_*.py"]}, PRESETS, ["layered.yaml: testing: missing `declared`"], id="no declared"),
    pytest.param({"files": ["test_*.py"], "declared": BY_NAME, "colour": 1}, PRESETS,
                 ["layered.yaml: testing: unknown key 'colour': use declared, files, globals, mocks, skips, tables"],
                 id="an unknown key"),
    pytest.param({"files": ["x"], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: 'x' is not a file name pattern: a name ending in .py, with `*` for any "
                  "text"], id="a file pattern that is no .py name"),
    pytest.param({"files": [], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with "
                  "`*` for any text"], id="no file patterns"),
    pytest.param({"files": ["a.py", "a.py"], "declared": BY_NAME}, PRESETS,
                 ["layered.yaml: testing.files: 'a.py' is listed twice"], id="a pattern twice"),
    pytest.param({"files": ["a.py"], "declared": [{"function": "a b"}]}, PRESETS,
                 ["layered.yaml: testing.declared.0.function: must be a function name pattern: a name with `*` for any "
                  "text"], id="a function pattern with a space"),
    pytest.param({"files": ["a.py"], "declared": [{"function": "t_*"}], "skips": ["skip"]}, PRESETS,
                 ["layered.yaml: testing.skips: 'skip' is not an outside name such as <package>.<name>"], id="a skip that is not dotted"),
])
def test_a_bad_testing_key_is_refused(testing, presets, expected):
    assert problems(covered(testing=testing), presets=presets) == expected


def test_a_test_declared_by_a_function_form_is_its_name_pattern():
    document = covered(testing={"files": ["test_*.py"], "declared": BY_NAME})
    assert parsed(document).framework == Framework(("test_*.py",), (DeclaredForm(function="test_*"),))


BRACED = {"python": PYTHON, "brace": BRACE}
"""Brace beside Python: Brace's data file says nothing of its reader, so no form is refused there for a fact."""
CALL_FORM = {"call": ["it"], "title": {"position": 0}, "body": {"position": 1}}
"""A call form whose one callee is a name the framework binds without an import."""
TS_FILES = {"files": ["*.test.ts"]}
"""The file pattern of a test file of Brace."""


def declaring(declared, **more) -> dict:
    """covered() in Brace, its test files *.test.ts and its tests declared by the forms given."""
    return covered(testing=TS_FILES | {"declared": declared} | more, language="brace")


def test_a_test_declared_by_a_call_form_is_its_callees_title_and_body_and_globals_are_names_bound_without_an_import():
    framework = parsed(declaring([CALL_FORM], globals=["it", "expect"]), languages=BRACED).framework
    assert framework == Framework(("*.test.ts",), (DeclaredForm(call=(("it",),), title=Place(0), body=Place(1)),),
                                  globals=(("it",), ("expect",)))


def test_globals_left_out_are_none():
    assert parsed(declaring([CALL_FORM]), languages=BRACED).framework.globals == ()


DECLARED_AT = "layered.yaml: testing.declared"
NOT_A_LIST = f"{DECLARED_AT}: must be a non-empty list of test forms, each {{function}} or {{call, title, body}}"


@pytest.mark.parametrize("testing, expected", [
    pytest.param(TS_FILES, "layered.yaml: testing: missing `declared`", id="no declared"),
    pytest.param(TS_FILES | {"declared": []}, NOT_A_LIST, id="an empty list"),
    pytest.param(TS_FILES | {"declared": "test*"}, NOT_A_LIST, id="a pattern that is no list"),
    pytest.param(TS_FILES | {"declared": [CALL_FORM | {"function": "test*"}]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry with both holders"),
    pytest.param(TS_FILES | {"declared": [{"title": {"position": 0}}]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry with no holder"),
    pytest.param(TS_FILES | {"declared": [None]}, f"{DECLARED_AT}.0: write one of function, call",
                 id="an entry that is no mapping"),
    pytest.param(TS_FILES | {"declared": [{"function": "a b"}]},
                 f"{DECLARED_AT}.0.function: must be a function name pattern: a name with `*` for any text",
                 id="a bad function pattern"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*", "title": {"position": 0}}]},
                 f"{DECLARED_AT}.0.title: a function form takes no slot: drop title", id="a function form with a title"),
    pytest.param(TS_FILES | {"declared": [{"call": ["it"], "body": {"position": 1}}]}, f"{DECLARED_AT}.0: missing `title`",
                 id="a call form with no title"),
    pytest.param(TS_FILES | {"declared": [{"call": ["it"], "title": {"position": 0}}]}, f"{DECLARED_AT}.0: missing `body`",
                 id="a call form with no body"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*"}, CALL_FORM | {"call": []}]},
                 f"{DECLARED_AT}.1.call: must list at least one callee", id="a call form with no callee, at its index"),
    pytest.param(TS_FILES | {"declared": [CALL_FORM | {"title": {"position": -1}}]},
                 f"{DECLARED_AT}.0.title: must be {{position: <n>, keyword: <name>}}, at least one of them, of the "
                 "holder's arguments", id="a bad title place"),
    pytest.param(TS_FILES | {"declared": [{"function": "test*", "colour": 1}]},
                 f"{DECLARED_AT}.0: unknown key 'colour': use body, call, function, title", id="an unknown key of an entry"),
])
def test_a_bad_declared_is_refused(testing, expected):
    assert problems(covered(testing=testing, language="brace"), languages=BRACED) == [expected]
```

`BRACE` and `PYTHON` are already imported from `tests.modules.spec.languages` at the top of the file.

3. (Sub-steps 3 and 4 give the line numbers of the file before sub-steps 1 and 2 changed it; sub-step 2 adds about 60 lines above them, so find each site by its text, which is given.) Replace the text `"write testing: <preset>, or testing: {files: [<pattern>, ...], functions: <pattern>}"]` in `test_tiers_need_the_framework_to_tell_a_test_from_a_helper` (line 405) by `"write testing: <preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]`; the same in `test_a_guard_that_reads_tests_needs_the_framework_even_without_tiers` (line 685: `"<preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]`) and in `test_a_plain_tier_with_no_framework_is_told_only_what_is_wrong_with_testing` (line 718: `"or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]`).

4. Replace `{files, functions}` by `{files, declared}` at line 627 and line 721; replace `presets = {"pytest": {"files": ["test_*.py"], "functions": "test_*"}}` by `presets = {"pytest": {"files": ["test_*.py"], "declared": BY_NAME}}` at lines 595 and 706.

5. Replace `test_the_test_only_framework_loads_under_brace_into_a_loop_form_and_a_call_form` by:

```python
def test_the_test_only_framework_loads_under_brace_into_two_forms_of_a_test_two_forms_of_a_table_and_a_global():
    framework = parsed(covered(testing="stub", language="brace"), presets={"stub": STUB},
                       languages={"python": PYTHON, "brace": BRACE}).framework
    assert framework == Framework(("*.test.ts",), (
        DeclaredForm(function="test*"),
        DeclaredForm(call=(("vitest", "it"), ("vitest", "test"), ("vitest", "it", "each"), ("vitest", "test", "each")),
                     title=Place(0), body=Place(1)),
    ), tables=(
        TableForm("bound", None, (), RowId(position=0), loop=True),
        TableForm("fields", Place(0), (), RowId(field="name"), call=(("vitest", "it", "each"), ("vitest", "test", "each"))),
    ), globals=(("expect",),))
```

- [ ] **Step 2: Write the failing key-table, explain and checks tests**

1. `tests/modules/spec/domain/test_profile_keys.py`: add `DECLARED,` to the `from xarch.modules.spec.domain.profile_keys import (...)` list (alphabetically, before `HELD,`; `KEYS` and `SCOPES` and `TESTING` are already imported), and append:

```python
def test_the_forms_that_declare_a_test_are_a_list_scope_of_function_call_title_and_body_and_functions_is_no_key():
    assert SCOPES[DECLARED] == "testing.declared[]"
    assert [key.name for key in KEYS if key.scope == DECLARED] == ["function", "call", "title", "body"]
    assert [key.name for key in KEYS if key.scope == TESTING] == ["files", "declared", "globals", "skips", "tables",
                                                                  "mocks"]
    assert [(key.required, key.opens) for key in KEYS if (key.scope, key.name) == (TESTING, "declared")] == [
        (True, DECLARED)]
```

2. `tests/modules/spec/application/test_explain.py`: in `SHAPE`, replace the line `Shown('testing.functions', 1, "the pattern of a test function's name", True, True),` by the two lines

```python
    Shown('testing.declared', 1, 'the forms a test is declared in', True, True),
    Shown('testing.globals', 1, 'the names the framework binds without an import', False, True),
```

and append after `test_the_forms_of_a_table_and_each_slot_of_a_form_are_keys_of_the_format`:

```python
def test_the_forms_that_declare_a_test_and_each_slot_of_a_form_are_keys_of_the_format():
    declared, slot = explained("testing.declared"), explained("testing.declared.call")
    assert (declared.key, declared.meaning, declared.rules) == (
        "testing.declared", "the forms a test is declared in", ("scenario-coverage", "stand-ins"))
    assert [(held.key, held.required) for held in declared.keys] == [
        ("testing.declared.function", False), ("testing.declared.call", False), ("testing.declared.title", False),
        ("testing.declared.body", False)]
    assert (slot.key, slot.where, slot.required, slot.meaning) == (
        "testing.declared.call", "testing.declared[]", False, "the calls that declare a test")
```

3. `tests/bootstrap/test_profile_explain.py`: append after `test_a_key_that_names_something_xarch_ships_says_which`:

```python
def test_a_slot_of_a_form_that_declares_a_test_is_explained_by_the_key_without_an_index():
    result = runner.invoke(app, ["profile", "explain", "testing.declared.call"])
    assert result.exit_code == 0 and "the calls that declare a test" in result.output
```

4. `tests/modules/rules/application/logic/test_scenarios.py`: change the builders import to `from tests.modules.rules.builders import BRACE, PROFILE, PYTEST_FORM, PYTHON, STUB, declaring, in_tests, profile, source`; replace `publish_tests` by

```python
def publish_tests(*functions: Function, path: str = "modules/docs/application/test_publish.py"):
    return declaring(path, *functions)
```

replace `brace_tests` by

```python
def brace_tests(*functions: Function, path: str = "modules/docs/application/publish.test.ts", tests=None):
    return declaring(path, *functions, framework=STUB, language=BRACE, tests=tests)
```

replace, in `test_a_table_test_of_a_tier_whose_tables_are_plain_holds_no_branch_and_one_of_another_tier_may`,

```python
    tests = [in_tests(UNIT_TEST, functions=(BRANCHED, Function(20, "test_other", blocks=((21, "if"),)))),
             in_tests("modules/web/test_page.py", functions=(BRANCHED,))]
```

by

```python
    tests = [declaring(UNIT_TEST, BRANCHED, Function(20, "test_other", blocks=((21, "if"),))),
             declaring("modules/web/test_page.py", BRANCHED)]
```

and in `test_a_table_test_of_a_plain_tier_holds_no_branch_but_the_statement_that_runs_its_rows` replace `plain([in_tests(UNIT_TEST, functions=(ran,))], PLAIN)` by `plain([declaring(UNIT_TEST, ran)], PLAIN)`. Replace `NO_FORM = profile(framework=Framework(("test_*.py",), "test_*"), ...)` by `NO_FORM = profile(framework=Framework(("test_*.py",), (DeclaredForm(function="test_*"),)), scenarios=replace(PROFILE.scenarios, columns=()))`, and add below `from xarch.profile_values.testing import Framework, Place, RowId, TableForm` the statement `from xarch.profile_values.testing import TestForm as DeclaredForm`. Append after `test_the_test_file_follows_the_guards_file_pattern`:

```python
def test_a_file_whose_functions_match_the_pattern_but_that_holds_no_test_has_no_table_test():
    unread = in_tests("modules/docs/application/test_publish.py", functions=(Function(8, "test_publish", (TABLE,)),))
    assert problems(unread) == [f"{FILE}:1: no table test whose parameters are given, when, then (scenario-coverage)"]


def test_the_test_only_framework_declares_a_function_form_and_a_call_form_and_binds_expect():
    assert ([form.function for form in STUB.declared], STUB.declared[1].call[:2], STUB.globals) == (
        ["test*", ""], (("vitest", "it"), ("vitest", "test")), (("expect",),))
```

5. `tests/modules/rules/application/test_check_app.py`: add the imports `from xarch.profile_values.testing import Framework` and, on its own line below it, `from xarch.profile_values.testing import TestForm as DeclaredForm` (both after `from xarch.profile_values.placement import Repeat, Target`), and append:

```python
def test_the_tests_are_read_with_the_framework_s_forms_and_globals_and_the_app_with_none():
    forms = (DeclaredForm(function="test_*"),)
    framed = replace(entered("cli"), framework=Framework(("test_*.py",), forms, globals=(("it",),)))
    tests = Path("/src/tests")
    tree = FakeSourceTree(ROOT, {"kernel/x.py": []}, more={tests: {"kernel/test_x.py": []}})
    controller(tree, FakeProfiles({"cli": framed})).check_app(CheckApp(ROOT, "cli", ROOT.parent, tests))
    assert (tree.forms, tree.bound) == ([(), forms], [(), (("it",),)])
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/domain/test_profile_keys.py tests/modules/rules/application/test_check_app.py`
Expected: FAIL: `test_profile_keys` with `ImportError: cannot import name 'DECLARED'`; the parse tests with `testing: missing \`functions\`` and unknown-key problems; `test_check_app`'s new test with `TypeError` on `Framework(...)` (`globals` is no field).

- [ ] **Step 4: Change `Framework`**

In `xarch/profile_values/testing.py` replace the class `Framework` by:

```python
@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text); the forms a test is declared in (declared, at least one: a function whose name
    matches a pattern, or a call whose arguments hold the test's title and its body), a test being of the first form
    it matches; the dotted names of what skips a test or expects it to fail (a marker or a call; empty: none is
    counted); the table forms it writes (tables; none: it writes none, and no table is read); and the names it binds
    without an import (globals), which are not the language's builtins."""
    files: tuple[str, ...]
    declared: tuple[TestForm, ...]
    skips: tuple[tuple[str, ...], ...] = ()
    tables: tuple[TableForm, ...] = ()
    globals: tuple[tuple[str, ...], ...] = ()
```

- [ ] **Step 5: The scope and the keys**

1. `xarch/modules/spec/domain/profile_keys.py`: add after `TABLES = "testing.tables"` the line `DECLARED = "testing.declared"`, and in `SCOPES` after `TABLES: "testing.tables[]",` the line `DECLARED: "testing.declared[]",`.

2. `xarch/modules/spec/domain/key_table.py`: add `DECLARED,` to the import list (between `DEAD_CODE,` and `DOCS,`), and replace the line `Key(TESTING, "functions", True, rules=("scenario-coverage", "stand-ins")),` by:

```python
    Key(TESTING, "declared", True, rules=("scenario-coverage", "stand-ins"), opens=DECLARED),
    Key(TESTING, "globals", rules=("scenario-coverage", "stand-ins")),
```

and insert before the line `Key(TABLES, "decorator", rules=("scenario-coverage",)),`:

```python
    Key(DECLARED, "function", rules=("scenario-coverage",)),
    Key(DECLARED, "call", rules=("scenario-coverage",)),
    Key(DECLARED, "title", rules=("scenario-coverage",)),
    Key(DECLARED, "body", rules=("scenario-coverage",)),

```

- [ ] **Step 6: Parse `declared` and `globals`**

In `xarch/modules/spec/application/logic/profile_checks.py`:

1. Change the profile_keys import to `from xarch.modules.spec.domain.profile_keys import DECLARED, FILE, FIXTURE, NAMING, PAGE, RULE_ID, TABLES` and add `TestForm,` to the `from xarch.profile_values.testing import (...)` list after `TableForm,`.

2. Add after the constant `HOLDERS` and its docstring:

```python
DECLARING = ("function", "call")
"""The keys of a form that declares a test that say how it declares one, exactly one of them in each."""
CALL_SLOTS = ("title", "body")
"""The slots of a call form: where the test's title and its body are among the call's arguments."""
```

3. Replace `_outside_name_at` and `outside_names` by:

```python
def _outside_name_at(value: Any, where: str, problems: list[str], language: Language,
                     least: int = 2) -> tuple[str, ...] | None:
    """An outside name of at least `least` steps: two by default, <package><member><name>, the path an import binds;
    one, a name the framework binds without an import too."""
    steps = _outside(value, language) if isinstance(value, str) else None
    if steps is None or len(steps) < least:
        problems.append(f"{where}: {value!r} is not an outside name such as {_such(language)}")
        return None
    return steps


def outside_names(value: Any, where: str, problems: list[str], language: Language,
                  least: int = 2) -> tuple[tuple[str, ...], ...] | None:
    """A non-empty list of outside names of at least `least` steps (see _outside_name_at), each once."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of outside names such as {_such(language)}")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = _outside_name_at(item, where, problems, language, least)
        if steps is not None and steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        elif steps is not None:
            found.append(steps)
    return tuple(found)
```

4. Add before `def framework_patterns`:

```python
def declared_forms(value: Any, where: str, problems: list[str], language: Language) -> tuple[TestForm, ...] | None:
    """The forms a test is declared in, at least one, each entry addressed `<where>.<i>`, i from 0; None when any entry
    has a problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of test forms, each {{function}} or {{call, title, body}}")
        return None
    forms = [_declared_form(entry, f"{where}.{index}", problems, language) for index, entry in enumerate(value)]
    found = tuple(form for form in forms if form is not None)
    return found if len(found) == len(forms) else None


def _declared_form(entry: Any, where: str, problems: list[str], language: Language) -> TestForm | None:
    """One form: exactly one of function and call, and only the keys of the scope."""
    if not isinstance(entry, Mapping) or sum(key in entry for key in DECLARING) != 1:
        problems.append(f"{where}: write one of function, call")
        return None
    count = len(problems)
    problems += unknown_keys(entry, names_of(DECLARED), where, DECLARED)
    if "function" in entry:
        return _function_form(entry, where, problems, language, count)
    return _call_form(entry, where, problems, language, count)


def _function_form(entry: Mapping[Any, Any], where: str, problems: list[str], language: Language,
                   count: int) -> TestForm | None:
    """A function form: a name pattern, `*` for any text, and no slot of a call form; count is how many problems
    there were before the entry."""
    problems += [f"{where}.{slot}: a function form takes no slot: drop {slot}" for slot in CALL_SLOTS if slot in entry]
    pattern = entry["function"]
    if not (isinstance(pattern, str) and names.is_name(pattern.replace("*", "x"), language.names)):
        problems.append(f"{where}.function: must be a function name pattern: a name with `*` for any text")
    return TestForm(function=pattern) if len(problems) == count else None


def _call_form(entry: Mapping[Any, Any], where: str, problems: list[str], language: Language,
               count: int) -> TestForm | None:
    """A call form: at least one callee, each a name of one step or more, and the places of the test's title and its
    body among the call's arguments; count is how many problems there were before the entry."""
    problems += [f"{where}: missing `{slot}`" for slot in CALL_SLOTS if slot not in entry]
    if entry["call"] == []:
        problems.append(f"{where}.call: must list at least one callee")
    calls = outside_names(entry["call"], f"{where}.call", problems, language, 1) if entry["call"] != [] else None
    title = _place(entry["title"], f"{where}.title", problems, language) if "title" in entry else None
    body = _place(entry["body"], f"{where}.body", problems, language) if "body" in entry else None
    if len(problems) != count or calls is None or title is None or body is None:
        return None
    return TestForm(call=calls, title=title, body=body)
```

5. Replace `framework_patterns` by:

```python
def framework_patterns(value: Any, problems: list[str], where: str, known: Collection[str],
                       language: Language, scope: str = "") -> Framework | None:
    """How the test framework names test files and declares its tests, the map written at `where`; `known` are the
    keys the map may hold, which the caller may widen with what it reads itself, and `scope` the scope whose retired
    names the map's unknown keys are looked up in."""
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{files, declared}}: the patterns of a test file's name and the "
                        "forms that declare a test")
        return None
    count = len(problems)
    problems += unknown_keys(value, known, where, scope)
    problems += [f"{where}: missing `{key}`" for key in ("files", "declared") if key not in value]
    files = _file_patterns(value["files"], problems, f"{where}.files", language) if "files" in value else None
    skips = outside_names(value["skips"], f"{where}.skips", problems, language) if "skips" in value else ()
    declared = declared_forms(value["declared"], f"{where}.declared", problems, language) if "declared" in value else None
    bound = outside_names(value["globals"], f"{where}.globals", problems, language, 1) if "globals" in value else ()
    if len(problems) != count or files is None or skips is None or declared is None or bound is None:
        return None
    return Framework(files, declared, skips, globals=bound)
```

- [ ] **Step 7: The loader's texts**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

1. Module docstring line 11: `    testing: <preset> | {files, functions, skips, table, mocks}` becomes `    testing: <preset> | {files, declared, globals, skips, tables, mocks}`.
2. `_PRESET_MAP = "{files, functions}"` becomes `_PRESET_MAP = "{files, declared}"`.
3. `_Testing`'s docstring first line: `"""What `testing` says: how test files are named and tests declared and the table forms the framework writes, and,` (the rest unchanged).
4. In `_testing`, the not-a-mapping text becomes:

```python
        problems.append(f"testing: must be a preset name or a mapping {_PRESET_MAP}: the patterns of a test file's name "
                        "and the forms that declare a test")
```

5. The missing-`testing` text (around line 958) becomes:

```python
    return [f"missing `testing`: {ck.join_and(needing)} must recognise a test file by its name: write testing: "
            "<preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]
```

6. `xarch/modules/spec/domain/values.py` line 372: `framework: how the test framework names test files and functions; None when no tier or guard needs them` becomes `framework: how the test framework names test files and declares tests; None when no tier or guard needs them`. `xarch/modules/rules/domain/profile.py` line 49: `framework names the test files and functions; None: no file is a test.` becomes `framework names the test files and declares the tests; None: no file is a test.` (rewrap the docstring line at 120 if it grows past it).

- [ ] **Step 8: The data files**

1. `xarch/architectures/presets/testing/pytest.yaml`: the header and the first keys become

```yaml
# The test framework pytest, as a profile names it with `testing: pytest`: the same map a profile writes out for another
# framework. How a test file is named and how a test is declared, what skips a test or expects it to fail, the table
# forms it writes, and how a mock is built.
files: ["test_*.py", "*_test.py"]
declared:
  - function: "test_*"
```

(the line `functions: "test_*"` goes; `skips:` and everything below are unchanged).

2. `tests/fakes/frameworks/stub.yaml` becomes:

```yaml
# A test-only framework that imitates Vitest-like tests: no profile names it and no reader reads it. It declares a test
# in two forms, a function whose name starts with test (index 0, the form the hand-built tests of the rules use) and a
# call of it or test, each or not, whose first argument is the test's title and whose second its body (index 1); it
# binds expect without an import. It writes two forms of a table, a loop of the test's body over a list literal
# (index 0) and a call that wraps the test (index 1), both with literal rows. The tests load it to show that the checks
# read a test by its form and word a table by its form's slots and the language's writing, never by a framework's own
# syntax.
files: ["*.test.ts"]
declared:
  - function: "test*"
  - call: ["vitest#it", "vitest#test", "vitest#it.each", "vitest#test.each"]
    title: {position: 0}
    body: {position: 1}
globals: [expect]
tables:
  - loop: true
    columns_from: bound
    row: literal
    id: {position: 0}
  - call: ["vitest#it.each", "vitest#test.each"]
    rows: {position: 0}
    columns_from: fields
    row: literal
    id: {field: name}
```

3. `xarch/architectures/presets/format/keys.yaml`:

   a. The fragment `testing` (lines 29-32) becomes

```yaml
  testing: |
    testing:
      files: [check_*%extension%]
      declared:
        - function: "check_*"
```

   b. The key `testing`'s `accepts` (line 145) begins `a preset name, or a map {files, declared, globals, skips, tables, mocks}; needed with ...` (the rest unchanged), and its example becomes

```yaml
    example: |-
      testing:
        files: [check_*%extension%]
        declared:
          - function: "check_*"
```

   c. In `tiers.<tier>.plain_tables`'s `accepts`, `true: no test function of the tier that holds a table of cases` becomes `true: no test of the tier that holds a table of cases` (rewrap the folded text at the file's width).

   d. Replace the entry `testing.functions:` (its four lines) by:

```yaml
  testing.declared:
    meaning: the forms a test is declared in
    accepts: >-
      a non-empty list of forms, each {function: <pattern>}, a function whose name matches the pattern (`*` for any
      text), or {call: [<dotted name>, ...], title, body}, a call whose arguments hold the test's title and its body;
      a test is of the first form it matches, and an entry's problem names it by its index, testing.declared.0.call
    example: |
      <<testing>>
  testing.declared[].function:
    meaning: a function whose name matches is a test
    accepts: a name with `*` for any text; takes neither title nor body
    example: |
      <<testing>>
  testing.declared[].call:
    meaning: the calls that declare a test
    accepts: >-
      a list of dotted names, or of names the framework binds without an import (`globals`), each a call whose
      arguments hold the test's title and its body; needs title and body
    example: |
      testing:
        files: [check_*%extension%]
        declared:
          - call: [checks.test]
            title: {position: 0}
            body: {position: 1}
  testing.declared[].title:
    meaning: where the title of a test a call declares is
    accepts: >-
      {position: <n>, keyword: <name>} of the call's arguments, at least one of them; needed with call, refused with
      function
    example: |
      testing:
        files: [check_*%extension%]
        declared:
          - call: [checks.test]
            title: {position: 0}
            body: {position: 1}
  testing.declared[].body:
    meaning: where the body of a test a call declares is
    accepts: >-
      {position: <n>, keyword: <name>} of the call's arguments, at least one of them; needed with call, refused with
      function
    example: |
      testing:
        files: [check_*%extension%]
        declared:
          - call: [checks.test]
            title: {position: 0}
            body: {position: 1}
  testing.globals:
    meaning: the names the framework binds without an import
    accepts: >-
      a list of names or dotted names: a use or a call of one that the file does not bind is read as that name, never
      as one of the language's builtins; left out: none
    example: |
      <<testing>>
        globals: [expect]
```

The catalogue orders its texts by the key table, so the entries' order in the file does not matter.

- [ ] **Step 9: The checks read the tests**

In `xarch/modules/rules/application/logic/scenarios.py`:

1. Replace the module docstring's sentence `That file must hold a table, read from its syntax tree in one of the forms the framework writes (`testing.tables`; the reader says how each is read), a test function being one whose name matches the profile's pattern:` by `That file must hold a table, read from its syntax tree in one of the forms the framework writes (`testing.tables`; the reader says how each is read), a test being one the framework declares (`testing.declared`), as the reader hands the file's tests over:`; in the rest of the docstring replace `a test function holding a table` by `a test holding a table`, `a standalone test function (one with no table)` by `a standalone test (one with no table)`, `named in the body of a test function of the file, its name matching the profile's pattern;` by `named in the body of a test of the file;`, and `(to any test function of the file that names it, for a framework that writes no table form)` by `(to any test of the file that names it, for a framework that writes no table form)`. Rewrap the paragraphs at 120.

2. Imports: remove `from fnmatch import fnmatchcase`; the parsed import becomes `from xarch.modules.rules.domain.parsed import Row, SourceFile, Table, Test, Union`.

3. In `violations`, `_named(test, union.name, union.members, profile)` becomes `_named(test, union.name, union.members)`.

4. In `plain`, replace

```python
        for function in test.functions:
            if function.tables and fnmatchcase(function.name, profile.framework.functions):
                found += [Violation(test.name, line, f"{problem}, and a table test of the {where.tier.name} tier holds "
                                                     f"no branch ({key}; {RULE})", RULE, fix)
                          for line, problem, fix in _branches(function, profile) if (test.name, line) not in known]
```

by

```python
        for declared in test.tests:
            if declared.body.tables:
                found += [Violation(test.name, line, f"{problem}, and a table test of the {where.tier.name} tier holds "
                                                     f"no branch ({key}; {RULE})", RULE, fix)
                          for line, problem, fix in _branches(declared, profile) if (test.name, line) not in known]
```

5. Delete `_tests`; replace `_named`, `_credited`, `_covered` and `_branches` by:

```python
def _named(test: SourceFile, union: str, variants: tuple[str, ...]) -> list[Violation]:
    """Each variant no test of the file names in its body, for a framework that writes no table form, in the union's
    order, at the top of the file."""
    named = set().union(*(declared.body.mentions for declared in test.tests))
    return [Violation(test.name, 1, f"{union} variant {v} is named by no test ({RULE})", RULE,
                      f"write a test naming {v}") for v in variants if v not in named]


def _credited(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
              profile: Profile) -> list[Weak]:
    assert profile.framework is not None
    covered: set[str] = set()
    standalone = test.tests
    if profile.framework.tables:
        for declared in test.tests:
            for table in declared.body.tables:
                if set(guard.columns) <= set(table.columns):
                    _rows(table, union, variants, guard, profile, covered)
        standalone = tuple(declared for declared in test.tests if not declared.body.tables)
    found: list[Weak] = []
    for variant in variants:
        credit = [declared for declared in standalone if variant in declared.body.mentions]
        if variant not in covered and credit and not any(declared.body.asserts for declared in credit):
            names = ", ".join(declared.name for declared in credit)
            found.append(Weak(RULE, test.name, credit[0].line, f"{union} variant {variant} is credited to {names} by "
                                                               "name only: no assert in their bodies"))
    return found
```

```python
def _covered(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
             profile: Profile) -> list[Violation]:
    columns = guard.columns
    tables = [(declared, table) for declared in test.tests for table in declared.body.tables
              if set(columns) <= set(table.columns)]
    if not tables:
        return [Violation(test.name, 1, f"no table test whose parameters are {', '.join(columns)} ({RULE})", RULE,
                          f"add a table test whose parameters are {', '.join(columns)}")]
    problems: list[Problem] = []
    covered: set[str] = set()
    for declared, table in tables:
        problems += _branches(declared, profile) + _rows(table, union, variants, guard, profile, covered)
    standalone = set().union(*(declared.body.mentions for declared in test.tests if not declared.body.tables))
    line = tables[0][1].line
    if all(table.rows is not None for _, table in tables):
        problems += [(line, f"{union} variant {v} has no row in the table and no standalone test naming it",
                      f"add a row whose {columns[-1]} is {v}, or a standalone test naming it")
                     for v in variants if v not in covered | standalone]
    return [Violation(test.name, line, f"{problem} ({RULE})", RULE, fix) for line, problem, fix in problems]


def _branches(declared: Test, profile: Profile) -> list[Problem]:
    """Each block and each expression of the test's body that branches, in line order, but the loop at the line that
    runs the rows of one of its tables (its runs; 0 is no line)."""
    fix = "arrange from given, act with when, assert == then, and give the odd case its own test"
    language = profile.language
    body = declared.body
    runs = {(table.runs, "for") for table in body.tables if table.runs}
    found = [(line, keyword, "") for line, keyword in body.blocks
             if keyword in language.branching and (line, keyword) not in runs]
    found += [(line, keyword, " expression") for line, keyword in body.expressions
              if keyword in language.branching_expressions]
    return [(line, f"{declared.name} has {'an' if keyword[:1] in 'aeiou' else 'a'} `{keyword}`{what} in its body", fix)
            for line, keyword, what in sorted(found)]
```

- [ ] **Step 10: Hand the forms to the tests read**

In `xarch/modules/rules/application/services/source_check.py` replace

```python
        tables = rules.framework.tables if rules.framework is not None else ()
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), tables, marks, interface,
                                     standard=standard, private=private, special=special) if tests is not None else []
```

by

```python
        framework = rules.framework
        tables = framework.tables if framework is not None else ()
        declared = framework.declared if framework is not None else ()
        bound = framework.globals if framework is not None else ()
        test_files = self._tree.read(tests, self._tree.paths(tests, extensions), tables, marks, interface,
                                     standard=standard, private=private, special=special, declared=declared,
                                     globals=bound) if tests is not None else []
```

and add to `check`'s docstring, after `Every file below tests is read.`, the sentence `The files below tests are read with the framework's forms of a table and of a test and its globals, the app's with none, so an app file holds no test.`

- [ ] **Step 11: The rules builders**

In `tests/modules/rules/builders.py`:

1. Add `from fnmatch import fnmatchcase` after `from dataclasses import replace`; change the parsed import to `from xarch.modules.rules.domain.parsed import Class, Function, SourceFile, Test`; add `TestForm` to the `from xarch.profile_values.testing import ...` line (after `TableForm`).

2. Add after `_table_form`:

```python
def declared_of(file: dict, member: str) -> tuple[TestForm, ...]:
    """The forms a framework's data file declares a test in, as its loader reads them: a function form's pattern, or a
    call form's callees split at the language's member, its title and its body."""
    return tuple(TestForm(function=form["function"]) if "function" in form else
                 TestForm(call=tuple(outside_steps(name, member) for name in form["call"]), title=_place(form["title"]),
                          body=_place(form["body"])) for form in file["declared"])
```

3. Replace the `STUB = ...` line by:

```python
STUB = Framework(tuple(STUB_FILE["files"]), declared_of(STUB_FILE, BRACE_FILE["member"]),
                 tables=tables_of(STUB_FILE, BRACE_FILE["member"]),
                 globals=tuple(outside_steps(name, BRACE_FILE["member"]) for name in STUB_FILE.get("globals", ())))
"""The test-only framework as a check reads it: a function form and a call form of a test, a loop form and a call form
of a table with literal rows, and its one global, read from its data file."""
```

(the old docstring line under `STUB` goes).

4. In `PROFILE`, `framework=Framework(("test_*.py", "*_test.py"), "test_*", tables=(PYTEST_FORM,)),` becomes `framework=Framework(("test_*.py", "*_test.py"), (TestForm(function="test_*"),), tables=(PYTEST_FORM,)),`.

5. Add after `in_tests`:

```python
def tests_of(functions: tuple[Function, ...], framework: Framework) -> tuple[Test, ...]:
    """The tests a reader finds among functions by the function forms of framework, as the Python reader finds them:
    each function whose name matches a form's pattern, a test of the first such form, untitled, its body the function
    itself."""
    found: list[Test] = []
    for function in functions:
        form = next((index for index, held in enumerate(framework.declared)
                     if held.function and fnmatchcase(function.name, held.function)), None)
        if form is not None:
            found.append(Test(function.line, function.name, form, False, function))
    return tuple(found)


def declaring(path: str, *functions: Function, framework: Framework | None = None, language: CheckedLanguage = PYTHON,
              tests: tuple[Test, ...] | None = None, **fields) -> SourceFile:
    """A file at path below the tests root holding functions, its tests those given, else those tests_of finds among
    the functions by framework (PROFILE's unless given), each definition public or not as the reader of language would
    say."""
    held = framework if framework is not None else PROFILE.framework
    assert held is not None
    return source(path, root=TESTS, language=language, functions=functions,
                  tests=tests_of(functions, held) if tests is None else tests, **fields)
```

- [ ] **Step 12: Every other framework and every `functions:` map in the tests**

Make exactly these replacements; each test file that builds `DeclaredForm(...)` gains the statement `from xarch.profile_values.testing import TestForm as DeclaredForm` on its own line, right below its existing `from xarch.profile_values.testing import ...` line (or after its last `xarch.profile_values` import when it has none from `testing`).

| File:line | Old | New |
|---|---|---|
| `tests/bootstrap/test_bundled_guards.py:39` | `Framework(("test_*.py", "*_test.py"), "test_*",` | `Framework(("test_*.py", "*_test.py"), (DeclaredForm(function="test_*"),),` |
| `tests/modules/rules/adapters/test_spec_profile.py:62` and `:122` | `Framework(("test_*.py",), "test_*", (("skip",),))` | `Framework(("test_*.py",), (DeclaredForm(function="test_*"),), (("skip",),))` |
| `tests/modules/rules/application/logic/test_enforcement.py:33` | `Framework(("test_*.py",), "test_*", SKIPS)` | `Framework(("test_*.py",), (DeclaredForm(function="test_*"),), SKIPS)` |
| `tests/modules/rules/application/logic/test_enforcement.py:112` | `Framework(("test_*.py",), "test_*")` | `Framework(("test_*.py",), (DeclaredForm(function="test_*"),))` |
| `tests/modules/rules/application/logic/test_expandable.py:23` | `Framework(("*",), "*")` | `Framework(("*",), (DeclaredForm(function="*"),))` |
| `tests/modules/rules/application/logic/test_never_use.py:21` | `Framework(("test_*.py",), "test_*")` | `Framework(("test_*.py",), (DeclaredForm(function="test_*"),))` |
| `tests/modules/rules/application/logic/test_tier_of.py:84` | `Framework(("check_*.py",), "check_*")` | `Framework(("check_*.py",), (DeclaredForm(function="check_*"),))` |
| `tests/modules/rules/application/logic/test_where.py:40` | `Framework(("test_*.py",), "test_*")` | `Framework(("test_*.py",), (DeclaredForm(function="test_*"),))` |
| `tests/modules/rules/application/logic/test_where.py:319` | `Framework(("*.test.ts",), "test*")` | `Framework(("*.test.ts",), (DeclaredForm(function="test*"),))` |
| `tests/modules/spec/profiles.py:25` | `"functions": "test_*",` | `"declared": [{"function": "test_*"}],` |
| `tests/modules/spec/application/builders.py:15` | `{"files": ["test_*.py"], "functions": "test_*"}` | `{"files": ["test_*.py"], "declared": [{"function": "test_*"}]}` |
| `tests/modules/spec/application/origins.py:3` | `"functions": "test_*",` | `"declared": [{"function": "test_*"}],` |
| `tests/modules/spec/application/test_profile_loading.py:12` | `{"files": ["test_*.py"], "functions": "test_*"}` | `{"files": ["test_*.py"], "declared": [{"function": "test_*"}]}` |
| `tests/modules/spec/application/test_profile_loading.py:43` | `{files, functions}` | `{files, declared}` |
| `tests/modules/spec/application/logic/test_profile_language.py:35` | `"functions": "check_*"` | `"declared": [{"function": "check_*"}]` |
| `tests/modules/spec/application/logic/test_profile_language.py:37` | `"functions": "check_*"` | `"declared": [{"function": "check_*"}]` |
| `tests/modules/spec/application/logic/test_profile_needs.py:61`, `:545`, `:565` | `"functions": "test_*"` | `"declared": [{"function": "test_*"}]` |
| `tests/modules/spec/application/logic/test_profile_parsing_substance.py:240` | `"functions": "test*"` | `"declared": [{"function": "test*"}]` |
| `tests/modules/spec/application/logic/test_testing.py:15` | `"functions": "test_*"` | `"declared": [{"function": "test_*"}]` |
| `tests/modules/spec/application/logic/test_testing.py:22` | `testing.functions: must be` | `testing.declared.0.function: must be` |
| `tests/modules/spec/application/logic/test_testing.py:34` | `functions: <pattern>}` | `declared: [{function: <pattern>}]}` |
| `tests/modules/spec/application/logic/test_testing.py:59` | `FILES \| {"functions": ""}` | `FILES \| {"declared": [{"function": ""}]}` |
| `tests/modules/spec/application/logic/test_testing.py:60` | `FILES \| {"functions": "9_*"}` | `FILES \| {"declared": [{"function": "9_*"}]}` |
| `tests/modules/spec/application/logic/test_testing.py:61` | `FILES \| {"functions": ["test_*"]}` | `FILES \| {"declared": [{"function": ["test_*"]}]}` |
| `tests/modules/spec/application/logic/test_testing.py:192`, `:323`, `:324` | `"functions": "test_*"` | `"declared": [{"function": "test_*"}]` |
| `tests/modules/spec/application/logic/test_testing.py:245`, `:394` | `"functions": "it_*"` | `"declared": [{"function": "it_*"}]` |
| `tests/modules/spec/application/logic/test_testing.py:304` | `"functions": "test*"` | `"declared": [{"function": "test*"}]` |
| `tests/modules/spec/application/logic/test_retired_keys.py:401` | `use files, functions, mocks, skips, tables` | `use declared, files, globals, mocks, skips, tables` |
| `tests/modules/spec/application/logic/test_retired_keys.py:467`, `:468` | `"functions": "test_*"` | `"declared": [{"function": "test_*"}]` |
| `tests/modules/spec/application/logic/test_retired_keys.py:473` | `use files, functions, mocks, skips, tables` | `use declared, files, globals, mocks, skips, tables` |
| `tests/bootstrap/test_architecture_files.py:164`, `:226` | `functions: <pattern>}'` | `declared: [{function: <pattern>}]}'` |
| `tests/bootstrap/test_loop_tables.py:12` | `  functions: "test_*"` | `  declared: [{function: "test_*"}]` |
| `tests/bootstrap/test_no_table_form.py:17` | `  functions: "Test*"` | `  declared:` then a new line `    - function: "Test*"` |
| `tests/bootstrap/test_other_framework.py:12` | `  functions: "it_*"` | `  declared: [{function: "it_*"}]` |
| `tests/bootstrap/test_profile_file.py:92` | `assert architecture.framework.functions == "test_*"` | `assert architecture.framework.declared == (DeclaredForm(function="test_*"),)` |
| `tests/bootstrap/test_profile_file.py:99` | `{{files, functions}}` | `{{files, declared}}` |
| `tests/bootstrap/test_profile_file.py:147` | `  functions: "test_*"\n'` | `  declared: [{function: "test_*"}]\n'` |
| `tests/bootstrap/test_profile_file.py:150` | `use files, functions, mocks, skips, tables` | `use declared, files, globals, mocks, skips, tables` |
| `tests/bootstrap/test_written_rules.py:107` | `"functions": "check_*"` | `"declared": [{"function": "check_*"}]` |

In `tests/architecture/test_agnostic.py:75` replace `patterns = (*architecture.framework.files, architecture.framework.functions)` by `patterns = (*architecture.framework.files, *(form.function for form in architecture.framework.declared if form.function))`, and in its module docstring `the stems of the patterns of the test files and functions (`test_`, `_test`)` by `the stems of the patterns of the test files and of the declared functions (`test_`, `_test`)`.

The line numbers are those of this branch before the task; a row's line may have moved by the lines Step 1 added above it in the same file (only `test_profile_parsing_tests.py`, whose own rows are in Step 1).

- [ ] **Step 13: Find what is left**

Run: `git grep -n '"functions": "\|functions: "\|framework\.functions\|testing\.functions' -- xarch tests ':!tests/bootstrap/corpora'`
Expected: no output. Any line it prints is a map or a text this task missed: change it the way the table above changes its kind, then run the grep again.

- [ ] **Step 14: Run the suites that the switch touches**

Run: `timeout 900 uv run pytest -q tests/modules tests/architecture tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_architecture_files.py tests/bootstrap/test_loop_tables.py tests/bootstrap/test_no_table_form.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_written_rules.py tests/bootstrap/test_bundled_guards.py`
Expected: PASS. A failure whose message still names `functions` is a site Step 12's table missed: change it the same way.

- [ ] **Step 15: Lint and the self-check**

Run: `uv run ruff check && uv run xarch check && uv run xarch profile check architecture.yaml`
Expected: ruff `All checks passed!`; both `xarch` commands exit 0. An `I001` (import order) is fixed by hand, never with `--fix`.

- [ ] **Step 16: Commit**

```bash
git add xarch tests
git commit -m "A framework declares its tests by testing.declared and binds names by testing.globals, and scenario-coverage, plain_tables and weak read the tests the reader hands over

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `testing.functions` retired with its hint

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py` (`RETIRED`)
- Test: `tests/modules/spec/domain/test_profile_keys.py`, `tests/modules/spec/application/logic/test_retired_keys.py`, `tests/bootstrap/test_profile_file.py`, `tests/bootstrap/test_profile_explain.py`

**Interfaces:**
- Consumes: `framework_patterns` and the key table of Task 2 (the scope `testing` knows `declared, files, globals, mocks, skips, tables`).
- Produces: `Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]')`, last entry of `RETIRED`.

- [ ] **Step 1: Write the failing tests**

1. `tests/modules/spec/domain/test_profile_keys.py`, in `test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules`, replace the tuple's last line `Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"))` by:

```python
        Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
        Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'))
```

2. `tests/modules/spec/application/logic/test_retired_keys.py`: add after the definition of `TABLE_MOVED` (and its docstring, if any):

```python
FUNCTIONS_MOVED = 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'
"""The hint of testing.functions, which testing.declared replaced in 0.3.0."""
```

add `pytest.param("testing.functions", FUNCTIONS_MOVED, id="testing.functions"),` after `pytest.param("testing.table", TABLE_MOVED, id="testing.table"),` in the parametrization of `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`, and append at the end of the file:

```python
@pytest.mark.parametrize("testing, presets", [
    pytest.param({"files": ["test_*.py"], "functions": "test_*", "declared": [{"function": "test_*"}]}, PRESETS,
                 id="in an inline map"),
    pytest.param("old", {"old": {"files": ["test_*.py"], "functions": "test_*", "declared": [{"function": "test_*"}]}},
                 id="in a preset"),
])
def test_the_functions_of_testing_are_refused_with_the_forms_that_declare_a_test(testing, presets):
    assert problems(layered(testing=testing), presets=presets) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use declared, files, globals, mocks, skips, tables"]


def test_functions_written_in_place_of_declared_is_refused_with_its_hint_and_declared_is_missing():
    assert problems(layered(testing={"files": ["test_*.py"], "functions": "test_*"})) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use declared, files, globals, mocks, skips, tables",
        "layered.yaml: testing: missing `declared`"]
```

3. `tests/bootstrap/test_profile_file.py`: append after `test_a_profile_writing_the_table_of_testing_is_refused_with_its_hint`:

```python
FUNCTIONS_PROFILE = PRESET_PROFILE.replace("testing: pytest\n", 'testing:\n  files: ["test_*.py"]\n  functions: "test_*"\n')


def test_a_profile_writing_the_functions_of_testing_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, FUNCTIONS_PROFILE)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert checked.exit_code == 1
    assert (f"    {path}: testing: unknown key 'functions': moved in 0.3.0: write declared: [{{function: \"<pattern>\"}}]; "
            "use declared, files, globals, mocks, skips, tables") in checked.output.splitlines()
```

4. `tests/bootstrap/test_profile_explain.py`: append after `test_the_table_of_testing_is_answered_from_the_table_of_retired_names`:

```python
def test_the_functions_of_testing_are_answered_from_the_table_of_retired_names():
    found = runner.invoke(app, ["profile", "explain", "testing.functions", "--format", "json"])
    assert (found.exit_code, json.loads(found.output)["retired"]) == (
        2, 'moved in 0.3.0: write declared: [{function: "<pattern>"}]')
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py`
Expected: FAIL: the refusals say `unknown key 'functions': use declared, files, ...` with no hint; `RETIRED` lacks the entry; `retired_at("testing.functions") == ""`.

- [ ] **Step 3: Add the entry**

In `xarch/modules/spec/domain/profile_keys.py`, replace the last entry of `RETIRED`

```python
    Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
)
```

by

```python
    Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
    Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),
)
```

- [ ] **Step 4: Run them to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py tests/modules/spec/domain/test_profile_keys.py \
  tests/modules/spec/application/logic/test_retired_keys.py tests/bootstrap/test_profile_file.py \
  tests/bootstrap/test_profile_explain.py
git commit -m "testing.functions is refused with the hint that testing.declared replaces it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: The facts `test.function` and `test.call`, and the needs refusal of a call form under Python

**Files:**
- Modify: `xarch/profile_values/capabilities.py` (`FACTS`)
- Modify: `xarch/architectures/presets/language/python.yaml` (`supplies`)
- Modify: `xarch/modules/spec/domain/key_table.py` (`NEEDS`)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`, `tests/modules/rules/domain/test_parsed.py`

**Interfaces:**
- Consumes: the keys `testing.declared[].function` and `testing.declared[].call` (Task 2).
- Produces: `FACTS["test.function"]`, `FACTS["test.call"]`; `NEEDS["testing.declared[].function"] == ("test.function",)`, `NEEDS["testing.declared[].call"] == ("test.call",)`; Python supplies `test.function: exact`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_needs.py`:

1. In `TOY`'s `supplies`, add `Supply("test.function", EXACT),` after `Supply("public", EXACT)` (Toy's profiles declare their tests by a function form, and Toy's tests are not about that fact): the line becomes `Supply("public", EXACT), Supply("test.function", EXACT))))`.

2. In `test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once`, the list `configured` begins with `("testing.declared.0.function", "testing.declared[].function"),` before `("testing.skips", "testing.skips"),`.

3. Replace `test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call` by:

```python
def test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call_and_the_tests_a_call_declares():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {
        fact: EXACT for fact in FACTS if fact not in ("function.tables.call", "test.call")}
```

4. Append at the end of the file:

```python
def test_each_form_that_declares_a_test_needs_its_own_fact_and_declared_globals_and_the_slots_need_none():
    needs = {key.address: key.needs for key in KEYS}
    assert {address: needs[address] for address in (
        "testing.declared", "testing.declared[].function", "testing.declared[].call", "testing.declared[].title",
        "testing.declared[].body", "testing.globals")} == {
        "testing.declared": (), "testing.declared[].function": ("test.function",),
        "testing.declared[].call": ("test.call",), "testing.declared[].title": (), "testing.declared[].body": (),
        "testing.globals": ()}


DECLARED_CALL = {"call": ["it"], "title": {"position": 0}, "body": {"position": 1}}
"""A form that declares a test by a call of it, its title and its body the call's first two arguments."""
CALL_REFUSED = ("layered.yaml: testing.declared.0.call: its check reads test.call (the tests a call with a title "
                "declares), which the language python does not supply: drop testing.declared.0.call, or check the app "
                "with a language whose reader supplies test.call")


def test_a_call_form_that_declares_a_test_under_python_is_refused_at_its_index():
    assert problems(layered(testing={"files": ["test_*.py"], "declared": [DECLARED_CALL]})) == [CALL_REFUSED]


def test_a_call_form_in_a_testing_preset_is_refused_at_its_index():
    presets = {"each": {"files": ["test_*.py"], "declared": [DECLARED_CALL]}}
    assert problems(layered(testing="each"), presets=presets) == [CALL_REFUSED]


def test_a_function_form_that_declares_a_test_under_python_loads():
    assert parsed(layered(testing=FILES)).approximate == ()
```

`FILES` is the module's `{"files": ["test_*.py"], "declared": [{"function": "test_*"}]}` (changed in Task 2).

5. In `tests/modules/rules/domain/test_parsed.py`, in the parametrization of `test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python`, add after the docstring-of-a-test row:

```python
    pytest.param(FACTS["test.function"], id="the text of the fact test.function"),
    pytest.param(FACTS["test.call"], id="the text of the fact test.call"),
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/modules/rules/domain/test_parsed.py`
Expected: FAIL: `KeyError: 'test.function'` at collection of `test_parsed.py`; the call form loads with no problem; `needs["testing.declared[].function"] == ()`.

- [ ] **Step 3: Add the facts, the supply and the needs**

1. `xarch/profile_values/capabilities.py`, in `FACTS` after the entry `"function.tables.loop": ...,`:

```python
    "test.function": "the tests a function declares by a name that matches a pattern",
    "test.call": "the tests a call with a title declares",
```

2. `xarch/architectures/presets/language/python.yaml`, in `supplies` after `  function.tables.loop: exact`:

```yaml
  test.function: exact
```

3. `xarch/modules/spec/domain/key_table.py`, in `NEEDS` after `"testing.tables[].loop": ("function.tables.loop",),`:

```python
    "testing.declared[].function": ("test.function",),
    "testing.declared[].call": ("test.call",),
```

- [ ] **Step 4: Run them to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/modules/rules/domain/test_parsed.py tests/modules/spec/application/logic/test_profile_keys.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain.py`
Expected: PASS. (`test_profile_keys.py`'s examples load under a language that supplies every fact; `test_needs_agree` reads only keys the engine expands.)

- [ ] **Step 5: Run the spec and rules suites**

Run: `timeout 900 uv run pytest -q tests/modules tests/bootstrap/test_profile_file.py tests/bootstrap/test_bundled_guards.py`
Expected: PASS. A test whose exact list of problems or shortfalls gained a `testing.declared.0.function` item runs under a hand-made language that does not supply `test.function`: give that language `Supply("test.function", EXACT)` as TOY got it, since none of those tests is about that fact.

- [ ] **Step 6: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml \
  xarch/modules/spec/domain/key_table.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/modules/rules/domain/test_parsed.py
git commit -m "A function form needs test.function, which Python supplies, and a call form test.call, which no reader supplies, so a call form under Python is refused at its index

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(add to `git add` any test file Step 5 had to change.)

---

### Task 5: A titled test is named in double quotes; the call form proved on hand-built facts

**Files:**
- Modify: `xarch/modules/rules/application/logic/scenarios.py` (module docstring; new `_printed`; `_credited`; `_branches`)
- Test: `tests/modules/rules/application/logic/test_scenarios.py`

**Interfaces:**
- Consumes: `Test`, `declaring`, `tests_of`, `STUB`, `STUB_PROFILE`, `BRACE_PLAIN`, `brace_tests(..., tests=)`, `written`, `row`, `BOTH`, `TS`, `DOC_TS`, `CALL_FIX`, `ARRANGE_FIX`, `RESULTS`, `stubbed`, `said` (Task 2 and the existing module).
- Produces: `scenarios._printed(declared: Test) -> str`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_scenarios.py`, add `tests_of` to the builders import (`from tests.modules.rules.builders import BRACE, PROFILE, PYTEST_FORM, PYTHON, STUB, declaring, in_tests, profile, source, tests_of`), add below `from xarch.modules.rules.domain.parsed import Function, Row, Table, Union` the statement `from xarch.modules.rules.domain.parsed import Test as DeclaredTest`, and append at the end of the file:

```python
def titled(line: int, title: str, body: Function) -> DeclaredTest:
    """A test the call form of the test-only framework declares (index 1), named by its title."""
    return DeclaredTest(line, title, 1, True, body)


def test_a_test_a_call_declares_covers_the_union_by_the_rows_of_its_body_s_table():
    assert stubbed(brace_tests(tests=(titled(8, "places an order", Function(8, "", (written(*BOTH),))),))) == []


def test_a_row_of_a_titled_test_s_table_is_worded_in_the_language_s_words():
    bare = written(row("Published", written=False, id=None), row("Missing", 11))
    assert stubbed(brace_tests(tests=(titled(8, "places an order", Function(8, "", (bare,))),))) == [
        (f"{TS}:10: row is not a literal (scenario-coverage)", CALL_FIX)]


def test_a_branch_of_a_titled_test_is_said_by_its_title_in_double_quotes():
    branched = titled(8, "places an order", Function(8, "", (written(*BOTH),), blocks=((14, "if"),)))
    assert stubbed(brace_tests(tests=(branched,))) == [
        (f'{TS}:14: "places an order" has an `if` in its body (scenario-coverage)', ARRANGE_FIX)]


def test_a_titled_table_test_of_a_plain_tier_is_said_by_its_title_in_double_quotes():
    held = titled(8, "places an order", Function(8, "", (Table(9, ("a", "b"), (row("x"),), 1, 0),), blocks=((14, "if"),)))
    assert said(brace_tests(tests=(held,), path="modules/docs/domain/doc.test.ts")) == [
        f'{DOC_TS}:14: "places an order" has an `if` in its body, and a table test of the unit tier holds no branch '
        "(tiers.unit.plain_tables; scenario-coverage)"]


@pytest.mark.parametrize("name, titled_, printed", [
    pytest.param("rejects when out of stock", True, '"rejects when out of stock"', id="a title in double quotes"),
    pytest.param("testMissing", False, "testMissing", id="a function's name bare"),
    pytest.param("", True, '""', id="a title that is no plain literal still counts"),
])
def test_weak_names_a_titled_test_in_double_quotes_and_a_function_bare(name, titled_, printed):
    table_test = Function(8, "testPublish", (written(row("Published")),))
    standalone = DeclaredTest(20, name, 1 if titled_ else 0, titled_, Function(20, name if not titled_ else "",
                                                                                  mentions=frozenset({"Missing"})))
    found = brace_tests(table_test, tests=(*tests_of((table_test,), STUB), standalone))
    assert weak([RESULTS], [found], STUB_PROFILE) == [
        Weak("scenario-coverage", TS, 20, f"PublishResult variant Missing is credited to {printed} by name only: no "
                                          "assert in their bodies")]


def test_weak_joins_the_names_of_every_test_it_credits_each_named_as_it_is_declared():
    table_test = Function(8, "testPublish", (written(row("Published")),))
    first = titled(20, "rejects when out of stock", Function(20, "", mentions=frozenset({"Missing"})))
    second = DeclaredTest(30, "testMissing", 0, False, Function(30, "testMissing", mentions=frozenset({"Missing"})))
    found = brace_tests(table_test, tests=(*tests_of((table_test,), STUB), first, second))
    assert weak([RESULTS], [found], STUB_PROFILE) == [
        Weak("scenario-coverage", TS, 20, 'PublishResult variant Missing is credited to "rejects when out of stock", '
                                          "testMissing by name only: no assert in their bodies")]


def test_a_test_a_call_declares_is_among_the_tests_alone_and_still_credits_a_variant():
    table_test = Function(8, "testPublish", (written(row("Published")),))
    missing = titled(20, "rejects when missing", Function(20, "", mentions=frozenset({"Missing"}), asserts=True))
    found = brace_tests(table_test, tests=(*tests_of((table_test,), STUB), missing))
    assert [function.name for function in found.functions] == ["testPublish"]
    assert (stubbed(found), weak([RESULTS], [found], STUB_PROFILE)) == ([], [])
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py`
Expected: FAIL in the double-quote tests: the findings say `places an order has an \`if\`` and `credited to rejects when out of stock`, with no quotes. The coverage tests (`covers the union`, `row ... worded`, `among the tests alone`) and the bare-name row already pass: they prove Task 2's one path.

- [ ] **Step 3: Quote a titled test**

In `xarch/modules/rules/application/logic/scenarios.py`:

1. Append to the module docstring, as its last paragraph:

```
A finding names a test as it is declared: by its title in double quotes when the framework declares it by a call's
title (`"places an order" has an `if` in its body`), by its function's name, bare, otherwise.
```

2. Add after `_given_id`:

```python
def _printed(declared: Test) -> str:
    """How a finding names a test: a title in double quotes, a function's name bare."""
    return f'"{declared.name}"' if declared.titled else declared.name
```

3. In `_credited`, `names = ", ".join(declared.name for declared in credit)` becomes `names = ", ".join(_printed(declared) for declared in credit)`.

4. In `_branches`, `f"{declared.name} has {'an' if ...` becomes `f"{_printed(declared)} has {'an' if ...` (the rest of the line unchanged).

- [ ] **Step 4: Run them to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_scenarios.py tests/architecture/test_table_forms.py tests/architecture/test_agnostic.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules/application/logic/scenarios.py tests/modules/rules/application/logic/test_scenarios.py
git commit -m "A test declared by a title is named in double quotes by scenario-coverage, plain_tables and weak, and the call form is proved on hand-built tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: README, CHANGELOG, the re-grep, golden docs, gates

**Files:**
- Modify: `README.md` (line 116; the `supplies` paragraph, lines 177-184)
- Modify: `CHANGELOG.md` (`[Unreleased]`: `### Added`, `### Changed`)

**Interfaces:**
- Consumes: everything above.
- Produces: docs only.

- [ ] **Step 1: README**

1. Line 116 `testing:  <preset> | {files*, functions*, skips, tables, mocks}` becomes `testing:  <preset> | {files*, declared*, globals, skips, tables, mocks}`.

2. In the paragraph on `supplies`, replace from `Python's reader` (line 177) to `the loop form read by Python's reader.` (line 184) by:

```
Python's reader
supplies every fact exactly but `function.tables.call` and `test.call`, so a framework that writes a `call` form under
Python is refused at that entry (`testing.tables.0.call`, `testing.declared.0.call`). A framework declares its tests
with `testing.declared`, a list of forms: a `function` form, a function whose name matches a pattern, or a `call` form,
a call whose arguments hold the test's `title` and its `body`; `testing.globals` names what it binds without an import.
That the table forms and the call form are neutral to a language is proved without a TypeScript reader: a test-only
framework (`tests/fakes/frameworks/stub.yaml`, a function form and a call form of a test, a loop form and a call form of
a table with literal rows) is checked on hand-built facts and worded by the `writing` of the test-only language
`brace.yaml`, beside a framework that writes no form and the loop form read by Python's reader.
```

(keep the lines that follow, `One fact is never written under` ..., unchanged).

- [ ] **Step 2: CHANGELOG**

Under `## [Unreleased]` / `### Added`, after the item that ends `worded from that language's \`writing\`. Behaviour is unchanged.`, add:

```markdown
- A framework declares its tests with `testing.declared`, a list of forms, each a `function` form, a function whose
  name matches a pattern (`declared: [{function: "test_*"}]`), or a `call` form, a call of one of its callees whose
  arguments hold the test's `title` and its `body` (`{call: [it, test], title: {position: 0}, body: {position: 1}}`);
  an entry's problem names it by its index (`testing.declared.0.call`). `testing.globals` lists the names the framework
  binds without an import (`[it, expect]`): a use or a call of one that the file does not bind is read as that name,
  never as a builtin. The reader turns the forms into the tests of a file (`SourceFile.tests`, each a `Test` with its
  line, its name, the index of its form, whether the name is a title, and its body), and scenario-coverage,
  `plain_tables` and `weak` read those alone. Two facts come with it: `test.function`, which Python supplies, and
  `test.call`, which no reader supplies yet, so a call form under Python is refused at its entry; the call form is
  proved on hand-built facts. A test declared by a title is named in double quotes (`"places an order" has an \`if\`
  in its body`), one declared by its function by its bare name, as before.
```

Under `### Changed`, as its first item:

```markdown
- `testing.functions` is replaced by `testing.declared`: a profile or a preset writing it is refused with `unknown key
  'functions': moved in 0.3.0: write declared: [{function: "<pattern>"}]`. The bundled `pytest` preset writes
  `declared: [{function: "test_*"}]`; the same functions are tests as before, and findings and docs read as before.
```

- [ ] **Step 3: The re-grep**

Run: `git grep -n "testing\.functions\|framework\.functions\|functions: \"" -- xarch tests README.md architecture.yaml ':!tests/bootstrap/corpora'`
Expected exactly these hits (line numbers as they fall), and no others:

```
tests/bootstrap/test_profile_explain.py:<n>:    found = runner.invoke(app, ["profile", "explain", "testing.functions", "--format", "json"])
tests/bootstrap/test_profile_file.py:<n>:FUNCTIONS_PROFILE = PRESET_PROFILE.replace("testing: pytest\n", 'testing:\n  files: ["test_*.py"]\n  functions: "test_*"\n')
tests/modules/spec/application/logic/test_retired_keys.py:<n>:    pytest.param("testing.functions", FUNCTIONS_MOVED, id="testing.functions"),
tests/modules/spec/application/logic/test_retired_keys.py:<n>:"""The hint of testing.functions, which testing.declared replaced in 0.3.0."""
```

The retired entry itself (`Retired(TESTING, "functions", ...)`) and the refusal tests' dicts (`"functions": "test_*"`) do not match the pattern; the CHANGELOG line is outside the grep's paths. Any other hit is a site Task 2 missed: fix it as Task 2's table does and commit it with this task.

- [ ] **Step 4: Golden docs regenerate unchanged, and the protected tests stay green**

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_docs.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_loop_tables.py tests/bootstrap/test_no_table_form.py tests/bootstrap/test_recorded_corpora.py tests/architecture/`
Expected: PASS. Then run `git status --short docs/ tests/bootstrap/corpora/` and expect no output but the untracked spec and plan under `docs/superpowers/`.

- [ ] **Step 5: Full gates**

Start in the background: `timeout 1200 uv run pytest -q > /tmp/pytest-6-8.log 2>&1` (it runs over two minutes; record its PID and read the log's last lines when it ends). Meanwhile run:

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```

Expected: pytest ends `N passed` with no failure and no error; ruff `All checks passed!`; each `xarch` command exits 0.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say a framework declares its tests by testing.declared and binds names by testing.globals, and that testing.functions is retired

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-Review

1. **Spec coverage.** B1 values → Task 1 Steps 4-5 (`TestForm`, `Test`, `SourceFile.tests`), Task 2 Step 4 (`Framework`); facts and Python's supply → Task 4 Step 3. B2 → Task 2 Steps 6-8 (every refusal text pinned by `test_a_bad_declared_is_refused` and `test_a_bad_testing_key_is_refused`; texts that named `functions` in Step 7; the preset in Step 8). B3 keys → Task 2 Step 5; NEEDS and the Python refusal → Task 4; the retired entry and its exact text → Task 3; `keys.yaml` entries and the `testing` fragment/example/accepts, `plain_tables` wording → Task 2 Step 8; `profile explain testing.declared.call` → Task 2 Step 2.3. B4 port and adapter → Task 1 Steps 6-7; `source_check` → Task 2 Step 10, pinned by `test_the_tests_are_read_with_the_framework_s_forms_and_globals_and_the_app_with_none`; `holding.py`, `sources.py` untouched. B5 → Task 2 Step 9 (one path, bodies), Task 5 (quoting); `test_agnostic` → Task 2 Step 12. B6 → Task 2 Step 8.2 (stub), Step 12 (no-table-form framework, inline maps). B7 → Task 6. Spec tests: 1-5 → Task 2 Step 1; 6 → Task 3; 7-9 → Task 4 (9 runs in Task 4 Step 4); 10 → Task 2 Step 2.1-2.3; 11-14 → Task 1 Step 1; 15-16, 21 → Task 2 Steps 2.4, 11; 17-20 → Task 5; 22-23 → Task 2 Step 12; 24-25 → Task 6 Step 4.
2. **Placeholders.** None; each code step holds its code; Step 12 gives every old and new text.
3. **Type consistency.** `TestForm(function, call, title, body)`, `Test(line, name, form, titled, body)`, `Framework(files, declared, skips, tables, globals)` are written the same way in every task; `declaring(path, *functions, framework=, language=, tests=)` and `tests_of(functions, framework)` match between builders (Task 2 Step 11) and their callers (Task 2 Step 2.4, Task 5); `FakeSourceTree.forms`/`.bound` (Task 1 Step 8) match Task 2's test; `outside_names(..., least)` is called positionally with `1` in `_call_form` and `framework_patterns`.
4. **Review Focus.** Five lines, each with its test: Task 1 (local binding, star import, builtin-named global), Task 2 (`declared: [null]`), Task 4 (call form in a preset).
<!-- task-pipeline: validated -->
