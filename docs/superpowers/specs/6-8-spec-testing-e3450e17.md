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
