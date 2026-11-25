<!-- The spec this plan implements, prepended verbatim: docs/superpowers/specs/6-12-rules-a-mock-s-57a4ed18.md -->

# 6.12 spec: a mock's spec may be a type argument, via `testing.mocks.specs`

Card: 57a4ed18-bb10-40aa-b024-002d0eeb65bf (subtask of 15e55316), release step 22 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3, row 22 at line 285: "`testing.mocks.specs`, `Call.types`,
`call.type_arguments`, spec forms in `writing`"). Blocked by 630cd9f2 (6.11), which is on this branch (HEAD 7da5794).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note").
This card implements section 4 (lines 545-616: 4.1 to 4.5) and the 15b rows of section 13 (lines 1119-1123). From
`0.3.0-cohesion-review-3.md` ("review 3"): overlap O13 (line 237, "step 22 adds the spec forms" to `writing`), O6
(line 230, the needs walker over `testing.mocks.specs` entries), O7 (line 231, the fact `call.type_arguments`), and
O4, O5, O8 (lines 228-232) for docs. The vocabulary row of review 3 section 4 (line 339) names the change.

## Goal

A framework says, as one ordered list, the ways a call that builds a mock names its spec: by a keyword argument, by a
positional argument, or by a type argument (`mock<Mailer>()`). The stand-ins check walks that list; its fix texts and
the docs line come from the language's `writing` templates, so no syntax of any language is typed into the checking
code. The two old keys are retired with fixed hints. Under pytest every text comes out byte for byte as today.

## What is already done (not to be redone)

- `Writing` (`xarch/profile_values/language.py:51-80`) holds the row templates `call`, `keyword`, `field`, filled by
  `_fill` in one pass; the loader is `language_file.py:129-132` (`WRITING`, `_TEMPLATES`, `_HOLDING`) and `_writing`
  at `:463-483`. `profile.language` reaches the rules (`xarch/modules/rules/domain/profile.py:116`, used so by
  `scenarios.py:218`); `architecture.language` reaches the docs template.
- The needs walker reads list entries for a scope address ending in `[]` and addresses each entry by its index from 0
  (`profile_needs.py:57-68`; NEEDS rows `testing.tables[].call`, `testing.declared[].call`, `key_table.py:267-271`).
  Its refusal text is `profile_needs.refused` (`:96-101`). Reused, no change (note line 1068, O6).
- The retired-keys table (`xarch/modules/spec/domain/profile_keys.py:187-223`), one wording, one problem per key;
  `unknown_keys` puts a retired key first (`profile_parsing.py:244`).
- 6.11 gave `_testing` the addresses the needs refusal already refused, so a check of an entry can be skipped where
  that refusal settles it (6.11 spec, B2).
- The test-only language Brace (`tests/fakes/languages/brace.yaml`, member `#`, `writing: {call, field}`, no
  `supplies`), loaded by `tests/modules/spec/languages.py`.

## Inherited constraints

- The neutral form, entries, and the order rule: note 4.1 (lines 547-584). Each entry has exactly one key, `keyword`
  (a keyword name), `position` (a whole number from 0), or `type_argument` (a whole number from 0). A call names its
  spec by the first entry it gives; the first entry is the form the fix text suggests; an autospec call reads the
  `position` and `type_argument` entries and only the first `keyword` entry (today's rule, `stand_ins.py:192`).
- `pytest.yaml` lines 19-20 become one line, `specs: [{keyword: spec}, {keyword: spec_set}, {position: 0}]` (note 4.1,
  lines 561-573; section 13, line 1119).
- `Call` and `ParameterCall` gain `types: tuple[Ref, ...]`, each a Ref resolved as any name; new fact
  `call.type_arguments`; Python does not list it (note 4.2, lines 586-592).
- NEEDS: `testing.mocks.specs.<n>.type_argument` needs `call.type_arguments` (note 4.2, line 592).
- The fix texts at `stand_ins.py:189, 197-199` and the docs line `docs_template.py:672-685` (the note's 613-616 at
  6dda0e7) are filled from `writing` templates, one per spec form; for pytest byte for byte as today (note 4.3, lines
  594-601; O13).
- Refusals: note 4.4 (lines 603-609), quoted in B4 below.
- Neutrality proof: note 4.5 (lines 611-616).
- Dodges (note lines 1131-1158, card): no hidden default (`specs` meaning `[{keyword: spec}]`); no
  `call.type_arguments` in the Python reader or `python.yaml` `supplies`; no `<T>` or `(... = ...)` syntax typed in
  the checking code or the docs template, nor a branch on the language's name; the step is not done without its
  test-only file (Brace).
- The recorded corpora (`tests/bootstrap/corpora/`) do not change. The golden docs `docs/{cli,web,xarch}/testing.md`
  are regenerated, never edited by hand, and their diff read; expected diff: none (note line 1127; O8).
- README and CHANGELOG lines go under `[Unreleased]` (O4, O5).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; Python only in the reader adapter and the data files under `xarch/architectures/presets/`;
  `.claude/` stays out of commits; nothing is pushed.

## Behavior

### B1. The key `testing.mocks.specs`

- `testing.mocks` accepts `calls`, `autospec`, `fixtures`, `specs`. `specs` is required, as `spec_keywords` was; when
  left out the problem is `<file>: testing.mocks: missing \`specs\``. There is no default.
- `specs` is a non-empty list. Each entry is a mapping of exactly one key among `keyword`, `position`,
  `type_argument`. A `keyword` value is a keyword name (the language's `name` pattern, as `spec_keywords` entries were
  checked); a `position` or `type_argument` value is a whole number, at least 0 (a bool is not a whole number).
- Refusals, each one problem:
  - `specs` not a list, or an empty list: `testing.mocks.specs: must be a list of {keyword}, {position} or
    {type_argument}` followed by `: the ways a call that builds a mock names its spec, in order, such as
    [{keyword: spec}]`. (The first clause is the note's text verbatim; the explanatory tail follows the house style of
    the `_mocks` mapping problem.)
  - An entry that is not a mapping, has no key, two keys, or a key outside the three:
    `testing.mocks.specs.<n>: must be one of {keyword: <name>}, {position: <n>} or {type_argument: <n>}`, addressed
    by its index from 0, every entry counted.
  - A `keyword` value that is not a keyword name: `testing.mocks.specs.<n>.keyword: 'a b' is not a keyword name`.
  - A `position` or `type_argument` value that is not a whole number at least 0:
    `testing.mocks.specs.<n>.<key>: must be a whole number, at least 0, such as 0`.
  - The same entry written twice (same key and value): `testing.mocks.specs.<n>: {keyword: spec} is listed twice`
    (today's "'spec' is listed twice" moves to the entry; the planner pins the exact text in the test first).
- The value is `StandIns.specs`, a tuple of entries in the written order, replacing `StandIns.spec` and
  `StandIns.spec_position`. An entry is a small frozen value with its form (`keyword`, `position`, `type_argument`)
  and its value (a keyword name or a whole number). Every constructor of `StandIns` in `xarch/` and `tests/` is
  updated (`profile_parsing.py:677`, `tests/bootstrap/test_bundled_guards.py:33`, `tests/modules/rules/builders.py:187`,
  `tests/modules/rules/adapters/test_spec_profile.py:58,122`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py:584`). The shared test profile dict
  `tests/modules/spec/profiles.py:28-29` (`TESTING["mocks"]`) writes `spec_keywords` and `spec_position`; it moves to
  `"specs": [{"keyword": "spec"}, {"keyword": "spec_set"}, {"position": 0}]`, as does the inline `spec_keywords: [of]`
  of `tests/bootstrap/test_loop_tables.py:14` and `test_other_framework.py:15`. Data files live at
  `xarch/architectures/presets/testing/pytest.yaml` and `xarch/architectures/presets/language/python.yaml`; the
  `StandIns` dataclass is in `xarch/profile_values/testing.py`; the unwritten check is in
  `xarch/modules/spec/application/logic/profile_checks.py:536`.
- The mapping problem of `testing.mocks` (`profile_parsing.py:655-658`) names `{calls, specs}` and optionally
  `autospec` and `fixtures`, and drops `spec_position`.

### B2. The language writes each spec form

- `writing` gains one sub-map, `specs`, its keys the entry keys of B1, each a one-line template:

  | Template | Must hold | Python writes |
  |---|---|---|
  | `writing.specs.keyword` | `{callee}`, `{keyword}`, `{value}` | `'{callee}({keyword}={value})'` |
  | `writing.specs.position` | `{callee}`, `{before}`, `{value}` | `'{callee}({before}{value})'` |
  | `writing.specs.type_argument` | `{callee}`, `{before}`, `{value}` | not written |

  The sub-map keeps the spec forms apart from the existing row template `writing.keyword`, which is a table row's id
  form (O13: step 19 added the row forms, this step adds the spec forms). The note's inferred TypeScript-like
  `'{callee}<{value}>()'` gains `{before}` so that a `type_argument` entry at a place past 0 is shown at its place, as
  a `position` entry is; Brace writes `type_argument: '{callee}<{before}{value}>()'`.
- `{before}` is filled with `..., ` once per place before the entry's place (0 places: empty), exactly as
  `stand_ins.py:196` does today; `{value}` with the spec shown; `{keyword}` with the entry's keyword. Filled by
  `Writing._fill`, so a value holding a placeholder is not filled again.
- The loader refuses, each one problem, as for the row templates: `writing.specs` not a mapping; an unknown key of it
  (`writing.specs: unknown key 'x': use keyword, position, type_argument`); a template that is not one line holding
  its placeholders (`writing.specs.<key>: must be a line holding {callee}, {before} and {value}`, or `{callee},
  {keyword} and {value}` for `keyword`). `WRITING` and the docstring of the loader name `specs`. Left out, the language
  writes no spec form.
- A profile entry of a form the language does not write is refused at load:
  `testing.mocks.specs.<n>: the language <title> does not write \`writing.specs.<key>\`, how a mock is given its spec
  by <a keyword | a position | a type argument>`, in the style of `_unwritten` (`profile_checks.py:536-550`). It is
  not given for an entry whose needs refusal of `testing.mocks.specs.<n>.type_argument` is given (the 6.11 skip
  mechanism), so Python reports one problem for a `type_argument` entry, the needs refusal (B4).
- Data files: `python.yaml` `writing` gains `specs: {keyword: ..., position: ...}` and its header comment (lines
  30-32) says what `writing.specs` is; `brace.yaml` gains `specs: {type_argument: '{callee}<{before}{value}>()'}` and
  no `supplies` stanza. Brace has none today, and `profile_needs.short` gives no shortfall for a language without one
  (`profile_needs.py:78-79`), so a `type_argument` entry loads under Brace as it is; adding a stanza would bring needs
  refusals for every fact Brace leaves out and move the tests that load Brace today. `percent.yaml` is not changed: %UnitTest has no mocks and the note gives no ObjectScript-shaped case for
  section 4.

### B3. What the stand-ins check reads

- `Call.types` and `ParameterCall.types`: `tuple[Ref, ...] = ()`, the last field of each, the type arguments in the
  order written; the docstrings say so. The default keeps every existing constructor valid; the Python reader
  (`fs_source_tree.py:1007, 1010`) sets nothing. The adapter's docstring that lists what the Python reader does not
  supply names `call.type_arguments`.
- `FACTS` (`xarch/profile_values/capabilities.py`) gains `call.type_arguments`: "the type arguments a call is given".
  NEEDS gains `testing.mocks.specs[].type_argument: ("call.type_arguments",)`; the key table gains the entry scope and
  its three keys (`keyword`, `position`, `type_argument`, rules `stand-ins`), and `Key(MOCKS, "specs", True, ...)`
  opens it; `spec_keywords` and `spec_position` keys go. The existing `testing.mocks` needs are unchanged.
- `_spec` walks the call's entries in order (for an autospec call, the `position` and `type_argument` entries and only
  the first `keyword` entry, in list order) and stops at the first the call gives:
  - `keyword` k: the call has keyword k; the spec is its value.
  - `position` n: the call has more than n positional arguments; the spec is the one at n.
  - `type_argument` n: the call has more than n type arguments; the spec is the one at n.
  No entry given: the call names a spec only if it unpacks its arguments (today's rule).
- Order change under pytest: today a position wins over a keyword when a call gives both; with pytest's list the
  keyword wins (note, Not verified, line 1172). The corpora gate decides; if a recorded finding moves, stop and report
  it rather than reorder pytest's list.
- No spec named: the violation text is unchanged, `{shown}() names nothing it stands in for (stand-ins)`; the hint is
  `give it a spec, such as <suggested>`, where `<suggested>` is the first entry's template filled with
  `{callee}` = the prefix of what is shown, joined, then the last step of the first `calls` entry (today's
  `constructor` + `names.mocks[0][-1]`), `{value}` = `<port>`, `{keyword}` = the entry's keyword, `{before}` from the
  entry's place. Under pytest: `mock.Mock(spec=<port>)` and friends, byte for byte as today.
- A read port named: the violation text is `<written> stands in for <Port>, a read port (stand-ins)`, where
  `<written>` is the template of the entry that named the spec, filled with `{callee}` = what is shown, `{value}` =
  the port's name, that entry's keyword or place. Under pytest a spec named by `spec=` or by position comes out as
  today; a spec named by `spec_set=` now shows `spec_set=` (today it shows the first keyword, `spec=`). No test nor
  corpus pins a read port named by `spec_set=` (grep at HEAD); the planner pins the new text in a test. The hint stays
  `use its fake <prefix><Port>` for every language.
- The module docstring of `stand_ins.py` (lines 20-23) and `_Built`'s say `specs`, not `spec_position` or spec
  keywords.

### B4. Retired keys and needs

- `testing.mocks.spec_keywords` and `testing.mocks.spec_position` are retired-keys entries of scope `testing.mocks`,
  one problem each, in the one wording (note 4.4, lines 605-607):
  `<file>: testing.mocks: unknown key 'spec_keywords': moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}];
  use autospec, calls, fixtures, specs`, and the same with `'spec_position'`.
- An unknown key of `testing.mocks` lists `use autospec, calls, fixtures, specs` (today's message,
  `test_profile_parsing_tests.py:215, 1077`, changes so).
- Under Python, a `type_argument` entry gets the existing needs refusal alone:
  `<file>: testing.mocks.specs.<n>.type_argument: its check reads call.type_arguments (the type arguments a call is
  given), which the language python does not supply: drop testing.mocks.specs.<n>.type_argument, or check the app with
  a language whose reader supplies call.type_arguments`.

### B5. What a profile and the docs say

- `xarch/architectures/presets/format/keys.yaml`: the `mocks` fragment (line 43) writes `specs: [{keyword: spec}]`;
  the `testing.mocks` `accepts` (line 874) names `{calls, autospec, specs, fixtures}`; the entries
  `testing.mocks.spec_keywords` and `testing.mocks.spec_position` (lines 968-983) give way to `testing.mocks.specs` and
  one entry per entry key (`testing.mocks.specs[].keyword`, `.position`, `.type_argument`), each with what the key
  catalogue test requires (meaning, accepts, example). The `type_argument` entry says it needs `call.type_arguments`.
- The docs line (`docs_template.py:496-498, 672-685`): `{mock}({spec}=<Port>)` and `{built}({spec}=<Port>)` are the
  first entry's template filled with `{value}` = `<Port>`. The `StandIns` match pattern reads `specs`. Under pytest the
  golden docs do not change.
- README (the testing / mocks passage, and the facts list around lines 179-183): one sentence that
  `testing.mocks.specs` lists, in order, the ways a mock names its spec (`keyword`, `position`, `type_argument`),
  replacing `spec_keywords` and `spec_position`, and that `type_argument` needs `call.type_arguments`, which Python's
  reader does not supply. CHANGELOG `[Unreleased]`: one line under `### Changed` for the key and its retired
  predecessors with the refusal, one under `### Added` for `call.type_arguments` and the `writing.specs` templates.
  Follow the form of 7da5794 / 19be557.

## Tests

Tests are written first. Tiers follow the repository's layout: unit tests mirror modules under `tests/modules/`;
`tests/bootstrap/` runs bundled profiles end to end.

Unit, profile loader (`tests/modules/spec/application/logic/test_testing.py`, `test_profile_parsing_tests.py`): the
parse is a pure function of a document in memory.

1. `specs: [{keyword: spec}, {keyword: spec_set}, {position: 0}]` parses to three entries in order.
2. `specs` missing gives `testing.mocks: missing \`specs\``; no default is filled in.
3. `specs: []` and `specs: spec` each give the "must be a list of {keyword}, {position} or {type_argument}" problem.
4. An entry with two keys, with no key, with an unknown key, and one that is a string each give the entry problem at
   `testing.mocks.specs.<n>`, with the right index (a bad entry at 1 beside a good one at 0).
5. `{keyword: "a b"}`, `{position: -1}`, `{position: true}`, `{type_argument: 1.5}` each give their value problem.
6. A duplicate entry gives the "listed twice" problem.
7. `spec_keywords` and `spec_position` each give the retired text of B4, one problem each; both written give two.
8. An unknown key `colour` gives `... use autospec, calls, fixtures, specs` (rewrite of the tests at lines 211-217,
   1074-1078).
9. Under Brace with `writing.specs.type_argument`, `specs: [{type_argument: 0}]` loads.
10. Under Brace, `specs: [{keyword: of}]` (Brace writes no `writing.specs.keyword`) is refused with the unwritten-form
    problem of B2.

Unit, needs (`tests/modules/spec/application/logic/test_profile_needs.py`): 11. under Python,
`specs: [{keyword: spec}, {type_argument: 0}]` gives exactly the needs refusal at `testing.mocks.specs.1.type_argument`
and not the unwritten-form problem. 12. The NEEDS / FACTS / supplies agreement test (`test_needs_agree.py` or its
current name) passes with `call.type_arguments`, and Python's `supplies` does not list it.

Unit, language file (`tests/modules/spec/application/logic/test_language_file.py`): 13. `writing.specs` with the
three templates loads into `Writing`; 14. a template missing a placeholder, an unknown key of `writing.specs`, and a
`writing.specs` that is not a mapping each give their problem; 15. the bundled `python.yaml` loads with `keyword` and
`position` spec templates and no `type_argument`.

Unit, `Writing` (`tests/profile_values/` or wherever `Writing` is tested today): 16. each spec template fills its
placeholders once (`{before}` with `..., ` per place, a value holding `{value}` kept as is).

Unit, the stand-ins check (`tests/modules/rules/application/logic/test_stand_ins.py`), hand-built `Call` and
`ParameterCall` values:

17. Every existing case passes with the same texts under pytest's list (the `replace(..., spec_position=position)` at
    line 143 becomes a `specs` with a `position` entry).
18. A call giving both `spec=` and a positional argument names its spec by the keyword (the order rule).
19. An autospec call with `spec_set=` only names nothing (the first-keyword rule, the existing case at line 117).
20. A read port by `spec_set=` fails with `Mock(spec_set=Mailer) stands in for Mailer, a read port (stand-ins)`.
21. Under Brace, `specs: [{type_argument: 0}]`, a `Call` with `types=(<the app's Mailer Ref>,)` of the mock fails with
    `mock<Mailer>() stands in for Mailer, a read port (stand-ins)` and the hint `use its fake FakeMailer` (note 4.5
    names the fix `mock<FakeMailer>`; the hint is kept as today for every language so pytest's text does not move,
    and the template fills the written form).
22. Under Brace, a mock call with no type argument fails with the hint `give it a spec, such as mock<<port>>()`
    (note 4.5).
23. Under Brace, `type_argument: 1` with one type argument names nothing; with two, the second is the spec and the
    written form is `mock<..., Mailer>()`.
24. A fixture call (`ParameterCall`) with `types` set is read the same way.

Unit, docs template (`test_docs_template.py`): 25. the stand-ins line under pytest is unchanged; under a profile whose
first entry is `type_argument` with Brace's template the line shows `` `mock<<Port>>()` ``.

Bootstrap (`tests/bootstrap/test_bundled_guards.py`, `test_other_framework.py:15`, `test_loop_tables.py:14`): the
inline profiles move to `specs: [{keyword: of}]`; the bundled pytest preset loads and its findings and the recorded
corpora do not move. 26. The golden docs regenerate with no diff (`test_docs_files.py`).

Gates, each passing on this branch alone with the full suite green: `uv run pytest -q` (over two minutes: in the
background, read at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
`uv run xarch profile check architecture.yaml`.

## Out of scope

- The tree form of `parts` (story 7, release step 23).
- A TypeScript or ObjectScript reader, and `call.type_arguments` in the Python reader (note, "What this note leaves
  out", and the dodge).
- A Jest or Vitest framework preset; Brace and hand-built calls stand in for it.
- Changing the hint `use its fake <prefix><Port>` per language.
- The wrap-up of README/CHANGELOG and the coupling audit tables (release step 25).
- Plans under `docs/superpowers/plans/` that name the old keys: historical, left as they are.

---

# 6.12 A mock's spec may be a type argument, via `testing.mocks.specs`: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A framework lists, as `testing.mocks.specs`, the ways a call that builds a mock names its spec (by a keyword, a
position or a type argument); the stand-ins check walks that list and writes every fix and the docs line from the
language's `writing.specs` templates, retiring `spec_keywords` and `spec_position`, with pytest's texts unchanged.

**Architecture:** The language value `Writing` (`xarch/profile_values/language.py`) gains a `SpecWriting` of three
one-line templates, read from a data file's `writing.specs`. The testing value `StandIns`
(`xarch/profile_values/testing.py`) holds `specs`, a tuple of `SpecEntry` (exactly one of `keyword`, `position`,
`type_argument`, in the style of `RowId`), which fills its form's template through `SpecEntry.written`. The loader
(`profile_checks.spec_entries`, `profile_checks.unwritten_specs`, `profile_parsing._mocks`) reads and refuses entries;
the key table opens a list scope `testing.mocks.specs[]` whose `type_argument` key needs the new fact
`call.type_arguments`; the rules check (`stand_ins.py`) and the docs line (`docs_template.py`) only ever call
`SpecEntry.written`, so no syntax of any language is typed in checking code.

**Tech Stack:** Python 3.13, pytest, PyYAML data files, `uv run` for every command, ruff.

**Spec:** `docs/superpowers/specs/6-12-rules-a-mock-s-57a4ed18.md` (prepended above).

## Global Constraints

- No comments in xarch's code (docstrings are prose, not comments); never `ruff --fix`; tests written first.
- Python only in the reader adapter (`xarch/modules/rules/adapters/fs_source_tree.py`) and the data files under
  `xarch/architectures/presets/`; no `<T>` or `(... = ...)` syntax typed in the checking code or the docs template, nor
  a branch on the language's name.
- No hidden default: `specs` is required; left out, `testing.mocks: missing \`specs\``.
- No `call.type_arguments` in the Python reader nor in `python.yaml` `supplies`.
- The step is not done without its test-only language: `tests/fakes/languages/brace.yaml` gains
  `writing.specs.type_argument: '{callee}<{before}{value}>()'` and no `supplies` stanza.
- The recorded corpora `tests/bootstrap/corpora/` do not change. If a recorded finding moves (the keyword-first order
  change), stop and report it; do not reorder pytest's list.
- The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never edited by hand; expected diff: none.
- README and CHANGELOG lines go under `[Unreleased]`.
- Examples simple, absolute `app.` imports; `.claude/` stays out of commits; nothing is pushed.
- Process safety: never `pkill`/`killall`/pattern `kill`; stop a stuck run with `timeout`.
- Every command runs from the worktree root with `uv run`. The full suite takes over three minutes: run it in the
  background and read its log at the end.

## Review Focus

1. A `type_argument` entry under Python: exactly the needs refusal, never the unwritten-form problem beside it (the
   6.11 skip through `unread`). Pinned in Task 3 Step 1 (`test_a_type_argument_entry_under_python_gets_the_needs_refusal_alone_at_its_index`, and the same through a preset).
2. A pytest call that gives both `spec=` and a first positional argument: the keyword now wins (pytest's list order).
   Pinned in Task 2 Step 3 (`test_a_call_giving_two_entries_names_its_spec_by_the_first_the_profile_lists`); the
   corpora gate in Task 4 Step 4 decides whether any recorded finding moved.
3. A `type_argument` entry under Python whose place is broken (`-1`): the needs refusal and the place's own problem,
   both, in that order. Pinned in Task 3 Step 1.
4. A profile still writing `spec_keywords`/`spec_position` and no `specs`: one retired problem per key, then
   `missing \`specs\``. Pinned in Task 2 Step 1 (`test_the_retired_keys_written_in_place_of_specs_...`).
5. A test language that writes no spec template and loads a profile whose mocks list entries (e.g. `TOY` in
   `test_testing.py`, or Brace with a `keyword` entry): refused at each entry with the unwritten-form problem, never a
   crash. Pinned in Task 2 Step 1 (Brace) and handled for `TOY` in Task 2 Step 1 (`TOY` keeps Python's spec templates).

---

## File Structure

- `xarch/profile_values/language.py`: `SPEC_FORMS`, new `SpecWriting`, `Writing.specs`, `Writing.writes_spec`,
  `Writing.spec` (Task 1).
- `xarch/modules/spec/application/logic/language_file.py`: `WRITING`, `SPECS`, `_SPEC_TEMPLATES`, `_SPEC_HOLDING`,
  module docstring, `_writing` split into `_writing`, `_spec_templates`, `_templates` (Task 1).
- `xarch/architectures/presets/language/python.yaml`, `tests/fakes/languages/brace.yaml` (Task 1).
- `tests/modules/rules/builders.py`: `writing_of` (Task 1), `PYTEST_SPECS` and `PROFILE.stand_ins` (Task 2).
- `xarch/profile_values/testing.py`: `SpecEntry`, `StandIns.specs` (Task 2).
- `xarch/modules/spec/domain/profile_keys.py`: `MOCK_SPECS`, its scope, two `Retired` rows (Task 2).
- `xarch/modules/spec/domain/key_table.py`: the `specs` key and its scope's three keys (Task 2); the NEEDS row (Task 3).
- `xarch/modules/spec/application/logic/profile_checks.py`: `SPECS`, `_SPEC_SAID`, `spec_entries`, `_spec_entry`,
  `unwritten_specs`; `identifiers` becomes `_identifiers` (Task 2).
- `xarch/modules/spec/application/logic/profile_parsing.py`: `_testing` passes `unread`; `_mocks` rewritten (Task 2).
- `xarch/modules/rules/application/logic/stand_ins.py`: docstrings, `_mock`, `_read`, `_spec` (Task 2; Task 3 reads
  type arguments).
- `xarch/modules/spec/application/logic/docs_template.py`: the `StandIns` case and `_stand_ins_line` (Task 2).
- `xarch/architectures/presets/testing/pytest.yaml`, `xarch/architectures/presets/format/keys.yaml` (Task 2).
- `xarch/modules/rules/domain/parsed.py`: `Call.types`, `ParameterCall.types` (Task 3).
- `xarch/profile_values/capabilities.py`: the fact `call.type_arguments` (Task 3).
- `xarch/modules/rules/adapters/fs_source_tree.py`: one docstring sentence (Task 3).
- `README.md`, `CHANGELOG.md` (Task 4).

A prototype of exactly this change was built outside the worktree while planning and run against the whole suite:
with every edit of this plan, 6407 passed, none failed.
Before its test edits, the change broke 39 tests, every one listed in a step below (tests that pin the old keys'
texts or the `StandIns` constructor, `TOY`'s empty `Writing`, the example of `testing.mocks.specs[].type_argument`
under Python's templates, the unknown-key scan of the key table over the new list scope, the exact `RETIRED` tuple,
the facts Python supplies, and `xarch check --strict`'s `dead-code.tests_only` finding on `profile_checks.identifiers`
once the loader stops calling it). With the edits of this plan, `ruff check`, `xarch check`, `xarch check --strict` and
`xarch profile check architecture.yaml` passed and the golden docs regenerated unchanged.

---

### Task 1: A language writes how a call that builds a mock names its spec (`writing.specs`)

**Files:**
- Modify: `xarch/profile_values/language.py:51-80` (before and in `Writing`)
- Modify: `xarch/modules/spec/application/logic/language_file.py:56-59` (module docstring), `:81-90` (imports),
  `:129-132` (constants), `:463-483` (`_writing`)
- Modify: `xarch/architectures/presets/language/python.yaml:30-32` (header), `:59-61` (`writing`)
- Modify: `tests/fakes/languages/brace.yaml:9-10` (header), `:28` (`writing`)
- Modify: `tests/modules/rules/builders.py:25` (import), before `_record_mark` (new `writing_of`), `:103`, `:116`
- Test: `tests/profile_values/test_language.py` (append)
- Test: `tests/modules/spec/application/logic/test_language_file.py:9-15` (imports), `:555-586`

**Interfaces:**
- Consumes: nothing new.
- Produces (later tasks rely on these exact names):
  - `xarch.profile_values.language.SPEC_FORMS: tuple[str, str, str] = ("keyword", "position", "type_argument")`
  - `class SpecWriting` (frozen dataclass): `keyword: str = ""`, `position: str = ""`, `type_argument: str = ""`
  - `Writing.specs: SpecWriting = SpecWriting()` (new last field)
  - `Writing.writes_spec(self, form: str) -> bool`
  - `Writing.spec(self, form: str, callee: str, value: str, keyword: str = "", place: int = 0) -> str`
  - `tests.modules.rules.builders.writing_of(file: dict) -> Writing`

- [ ] **Step 1: Write the failing tests of the templates and their loader**

Append to `tests/profile_values/test_language.py`, and change its import line
`from xarch.profile_values.language import NOTHING, CheckedLanguage` to
`from xarch.profile_values.language import NOTHING, CheckedLanguage, SpecWriting, Writing`:

```python


SPECS = Writing(specs=SpecWriting(keyword="{callee}({keyword}={value})", position="{callee}({before}{value})",
                                  type_argument="{callee}<{before}{value}>()"))
"""A language writing each way a call names its spec: the keyword and position forms as Python's file writes them, a
type argument as the TypeScript-like test-only language does."""


@pytest.mark.parametrize("form, keyword, place, written", [
    pytest.param("keyword", "spec_set", 0, "Mock(spec_set=Port)", id="a keyword fills the callee, the keyword and the value"),
    pytest.param("position", "", 0, "Mock(Port)", id="a position at 0 has nothing before it"),
    pytest.param("position", "", 2, "Mock(..., ..., Port)", id="each place before the spec is written once"),
    pytest.param("type_argument", "", 0, "Mock<Port>()", id="a type argument at 0"),
    pytest.param("type_argument", "", 1, "Mock<..., Port>()", id="a type argument past 0 is shown at its place"),
])
def test_a_spec_template_fills_each_placeholder_of_its_form(form, keyword, place, written):
    assert SPECS.spec(form, "Mock", "Port", keyword, place) == written


def test_a_value_holding_a_placeholder_is_not_filled_again():
    assert SPECS.spec("keyword", "{value}", "{keyword}", "{before}") == "{value}({before}={keyword})"
    assert SPECS.spec("position", "{before}", "{value}", place=1) == "{before}(..., {value})"


def test_a_language_writes_a_spec_form_only_when_its_file_gives_the_template():
    assert [form for form in ("keyword", "position", "type_argument") if SPECS.writes_spec(form)] == [
        "keyword", "position", "type_argument"]
    assert [form for form in ("keyword", "position", "type_argument") if Writing().writes_spec(form)] == []
```

In `tests/modules/spec/application/logic/test_language_file.py`:

(a) Replace the import line `from tests.modules.spec.languages import PYTHON as PYTHON_LANGUAGE` with:

```python
from tests.modules.spec.languages import BRACE
from tests.modules.spec.languages import PYTHON as PYTHON_LANGUAGE
```

and the import line
`from xarch.profile_values.language import BLOCK, LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, Writing`
with:

```python
from xarch.profile_values.language import (
    BLOCK,
    LINE,
    CheckedLanguage,
    CommentForm,
    InterfaceMark,
    RecordMark,
    SpecWriting,
    Writing,
)
```

(b) Replace the block from `MAPPING = "writing: must be a mapping {call, keyword, field}: ...` (line 555) through the end
of `test_a_bad_writing_is_refused` (line 586) with:

```python
MAPPING = ("writing: must be a mapping {call, keyword, field, specs}: how a row of a table of cases is written, and "
           "how a call that builds a mock names its spec")
CALL = "writing.call: must be a line holding {callee}"
KEYWORD = "writing.keyword: must be a line holding {callee}, {keyword} and {text}"
FIELD = "writing.field: must be a line holding {field} and {text}"
SPECS_MAPPING = ("writing.specs: must be a mapping {keyword, position, type_argument}: how a call that builds a mock "
                 "names its spec")
SPEC_KEYWORD = "writing.specs.keyword: must be a line holding {callee}, {keyword} and {value}"
SPEC_PLACED = "writing.specs.{key}: must be a line holding {{callee}}, {{before}} and {{value}}"


def test_python_writes_how_a_row_call_and_a_row_id_given_by_a_keyword_are_written_and_a_spec_by_keyword_or_position():
    assert PYTHON_LANGUAGE.checked.writing == Writing(
        call="{callee}(...)", keyword='{callee}(..., {keyword}="{text}")',
        specs=SpecWriting(keyword="{callee}({keyword}={value})", position="{callee}({before}{value})"))


def test_the_typescript_like_test_only_language_writes_a_spec_by_a_type_argument_alone():
    assert BRACE.checked.writing.specs == SpecWriting(type_argument="{callee}<{before}{value}>()")


def test_a_language_whose_file_writes_no_templates_loads_with_empty_ones():
    assert language_of("pascal", DOCUMENT).checked.writing == Writing()


def test_the_templates_a_data_file_writes_are_read_braces_and_all():
    field = '{..., {field}: "{text}"}'
    assert language_of("pascal", DOCUMENT | {"writing": {"field": field}}).checked.writing == Writing(field=field)


@pytest.mark.parametrize("writing, expected", [
    pytest.param("{callee}(...)", [MAPPING], id="a text is no mapping"),
    pytest.param({"row": "x"}, ["writing: unknown key 'row': use call, keyword, field, specs"], id="an unknown key"),
    pytest.param({"row": "x", "cell": "y"}, ["writing: unknown keys 'cell', 'row': use call, keyword, field, specs"],
                 id="two unknown keys are said together"),
    pytest.param({"call": "call()"}, [CALL], id="a call template without its callee"),
    pytest.param({"call": "{callee}\n(...)"}, [CALL], id="a call template over two lines"),
    pytest.param({"call": 3}, [CALL], id="a call template that is no text"),
    pytest.param({"keyword": "{callee}(..., {keyword}=x)"}, [KEYWORD], id="a keyword template without its text"),
    pytest.param({"field": "{text}"}, [FIELD], id="a field template without its field"),
    pytest.param({"specs": "{callee}<{value}>()"}, [SPECS_MAPPING], id="specs that are no mapping"),
    pytest.param({"specs": {"generic": "x"}},
                 ["writing.specs: unknown key 'generic': use keyword, position, type_argument"],
                 id="an unknown key of specs"),
    pytest.param({"specs": {"keyword": "{callee}({value})"}}, [SPEC_KEYWORD], id="a keyword template without its keyword"),
    pytest.param({"specs": {"position": "{callee}({value})"}}, [SPEC_PLACED.format(key="position")],
                 id="a position template without the places before it"),
    pytest.param({"specs": {"type_argument": "{callee}<{before}>()"}}, [SPEC_PLACED.format(key="type_argument")],
                 id="a type argument template without its value"),
    pytest.param({"specs": {"type_argument": "{callee}<\n{before}{value}>()"}}, [SPEC_PLACED.format(key="type_argument")],
                 id="a spec template over two lines"),
])
def test_a_bad_writing_is_refused(writing, expected):
    assert refused(DOCUMENT | {"writing": writing}) == expected


def test_the_spec_templates_a_data_file_writes_are_read_each_under_its_form():
    specs = {"keyword": "{callee}({keyword}: {value})", "position": "{callee}({before}{value})",
             "type_argument": "{callee}<{before}{value}>()"}
    assert language_of("pascal", DOCUMENT | {"writing": {"specs": specs}}).checked.writing == Writing(
        specs=SpecWriting(**specs))
```

(The block is replaced whole: `test_a_language_whose_file_writes_no_templates_loads_with_empty_ones` and
`test_the_templates_a_data_file_writes_are_read_braces_and_all` are in it unchanged, so each stays exactly once; the
old `test_python_writes_how_a_row_call_and_a_row_id_given_by_a_keyword_are_written` is renamed, not duplicated.)

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest -q -p no:cacheprovider tests/profile_values/test_language.py tests/modules/spec/application/logic/test_language_file.py`
Expected: collection errors, `ImportError: cannot import name 'SpecWriting' from 'xarch.profile_values.language'`.

- [ ] **Step 3: Add `SPEC_FORMS`, `SpecWriting` and the spec methods of `Writing`**

In `xarch/profile_values/language.py`, replace the whole `Writing` class (from `@dataclass(frozen=True)` above
`class Writing:` at line 51 to the end of `_fill`, line 80) with:

```python
SPEC_FORMS = ("keyword", "position", "type_argument")
"""The ways a call that builds a mock names its spec, in the order a problem lists them: a keyword argument, the
positional argument at a place, the type argument at a place. They are the keys of an entry of a profile's
`testing.mocks.specs` and of the data file's `writing.specs`."""


@dataclass(frozen=True)
class SpecWriting:
    """How the language writes a call that builds a mock and names its spec, one one-line template per way of naming it
    (empty: the file does not write it): keyword, {callee}, {keyword} and {value} standing for what is called, the
    keyword and the spec; position and type_argument, {callee}, {before} and {value} standing for what is called, the
    places before the spec's own and the spec."""
    keyword: str = ""
    position: str = ""
    type_argument: str = ""


@dataclass(frozen=True)
class Writing:
    """How the language writes a row of a table of cases, and a call that builds a mock, as its data file's `writing`
    says it, each template one line (empty: the file does not write it): call, a row that is a call, {callee} standing
    for what it calls; keyword, a row call whose id a keyword gives, {callee}, {keyword} and {text} standing for what
    it calls, the keyword and the id's text; field, a literal row whose id a field gives, {field} and {text} standing
    for the field and the id's text; specs, how a call that builds a mock names its spec (see SpecWriting). A template
    is filled by `row_call`, `keyword_id`, `field_id` and `spec`: each placeholder replaced in one pass, any other
    text, braces included, kept as it is."""
    call: str = ""
    keyword: str = ""
    field: str = ""
    specs: SpecWriting = SpecWriting()

    def row_call(self, callee: str) -> str:
        """The `call` template for a row that calls callee."""
        return self._fill(self.call, callee=callee)

    def keyword_id(self, callee: str, keyword: str, text: str) -> str:
        """The `keyword` template for a row that calls callee, its id given by keyword with the value text."""
        return self._fill(self.keyword, callee=callee, keyword=keyword, text=text)

    def field_id(self, field: str, text: str) -> str:
        """The `field` template for a literal row, its id given by field with the value text."""
        return self._fill(self.field, field=field, text=text)

    def writes_spec(self, form: str) -> bool:
        """Whether the language writes how a call names its spec in form, one of SPEC_FORMS."""
        return bool(getattr(self.specs, form))

    def spec(self, form: str, callee: str, value: str, keyword: str = "", place: int = 0) -> str:
        """The `specs` template of form, one of SPEC_FORMS, for a call of callee whose spec is value: given by keyword
        for a keyword form, else at place, from 0, each place before it written `..., `."""
        held = {"keyword": keyword} if form == SPEC_FORMS[0] else {"before": "..., " * place}
        return self._fill(getattr(self.specs, form), callee=callee, value=value, **held)

    @staticmethod
    def _fill(template: str, **values: str) -> str:
        """The template with each `{<name>}` of the values replaced in one pass, so that a value holding a
        placeholder is not filled again."""
        return re.sub("{(" + "|".join(values) + ")}", lambda found: values[found.group(1)], template)
```

- [ ] **Step 4: Read `writing.specs` in the loader**

In `xarch/modules/spec/application/logic/language_file.py`:

(a) In the import block `from xarch.profile_values.language import (...)` (lines 81-90), add `SpecWriting,` between
`RecordMark,` and `Writing,`.

(b) In the module docstring, replace

```
                   {text}. Left out, the language writes no template, and a profile whose table forms need one is
                   refused
```

with

```
                   {text}; specs, how a call that builds a mock names its spec, a map of one-line templates, each
                   optional: keyword, by a keyword argument, {callee}, {keyword} and {value}; position, by the
                   positional argument at a place, and type_argument, by the type argument at a place, each
                   {callee}, {before} and {value}. Left out, the language writes no template, and a profile whose
                   table forms or mock specs need one is refused
```

(c) Replace lines 129-132 (`WRITING = ...` and its docstring, `_TEMPLATES`, `_HOLDING` and their docstrings) with:

```python
WRITING = ("writing: must be a mapping {call, keyword, field, specs}: how a row of a table of cases is written, and "
           "how a call that builds a mock names its spec")
"""What the loader says of a value of `writing` that is not a mapping, once for the key."""
_TEMPLATES = {"call": ("{callee}",), "keyword": ("{callee}", "{keyword}", "{text}"), "field": ("{field}", "{text}")}
"""The templates of `writing`, in the order a problem lists them, each with the placeholders it must hold."""
_HOLDING = {"call": "{callee}", "keyword": "{callee}, {keyword} and {text}", "field": "{field} and {text}"}
"""What a problem says each template must hold."""
SPECS = ("writing.specs: must be a mapping {keyword, position, type_argument}: how a call that builds a mock names "
         "its spec")
"""What the loader says of a value of `writing.specs` that is not a mapping, once for the key."""
_SPEC_TEMPLATES = {"keyword": ("{callee}", "{keyword}", "{value}"), "position": ("{callee}", "{before}", "{value}"),
                   "type_argument": ("{callee}", "{before}", "{value}")}
"""The templates of `writing.specs`, in the order a problem lists them, each with the placeholders it must hold."""
_SPEC_HOLDING = {"keyword": "{callee}, {keyword} and {value}", "position": "{callee}, {before} and {value}",
                 "type_argument": "{callee}, {before} and {value}"}
"""What a problem says each template of `writing.specs` must hold."""
```

(d) Replace the whole function `_writing` (lines 463-483, the end of the file) with:

```python
def _writing(document: Mapping[Any, Any], problems: list[str]) -> Writing:
    """How a row of a table of cases is written, and how a call that builds a mock names its spec (specs); empty
    templates when the key is left out or refused. Each template is a one-line text holding every placeholder of its
    own."""
    if "writing" not in document:
        return Writing()
    value = document["writing"]
    if not isinstance(value, Mapping):
        problems.append(WRITING)
        return Writing()
    found = _templates(value, "writing", _TEMPLATES, _HOLDING, ("specs",), problems)
    specs = _spec_templates(value["specs"], problems) if "specs" in value else SpecWriting()
    return Writing(**found, specs=specs)


def _spec_templates(value: Any, problems: list[str]) -> SpecWriting:
    """How a call that builds a mock names its spec, each way its own template; empty ones when refused."""
    if not isinstance(value, Mapping):
        problems.append(SPECS)
        return SpecWriting()
    return SpecWriting(**_templates(value, "writing.specs", _SPEC_TEMPLATES, _SPEC_HOLDING, (), problems))


def _templates(value: Mapping[Any, Any], where: str, templates: Mapping[str, tuple[str, ...]],
               holding: Mapping[str, str], more: tuple[str, ...], problems: list[str]) -> dict[str, str]:
    """The templates the mapping at where writes, by key, each a one-line text holding every placeholder of its own;
    a key that is neither a template nor one of more is refused, all such keys in one problem."""
    unknown = sorted(str(key) for key in value if key not in templates and key not in more)
    if unknown:
        problems.append(f"{where}: unknown key{'s' if len(unknown) > 1 else ''} "
                        f"{', '.join(f'{key!r}' for key in unknown)}: use {', '.join((*templates, *more))}")
    found: dict[str, str] = {}
    for key, held in templates.items():
        line = value.get(key)
        if key in value and isinstance(line, str) and line.strip() and "\n" not in line and all(h in line for h in held):
            found[key] = line
        elif key in value:
            problems.append(f"{where}.{key}: must be a line holding {holding[key]}")
    return found
```

- [ ] **Step 5: Write the templates into the two data files**

In `xarch/architectures/presets/language/python.yaml`, replace the header line

```
# text; field, a literal row whose id a field gives, Python does not write.
```

with

```
# text; field, a literal row whose id a field gives, Python does not write; specs, how a call that builds a mock names
# its spec: keyword, by a keyword argument, {keyword} and {value} standing for the keyword and the spec; position, by
# the positional argument at a place, {before} standing for the places before it and {value} for the spec;
# type_argument, by a type argument, Python does not write.
```

and, under `writing:`, after the line `  keyword: '{callee}(..., {keyword}="{text}")'`, add:

```yaml
  specs:
    keyword: "{callee}({keyword}={value})"
    position: "{callee}({before}{value})"
```

In `tests/fakes/languages/brace.yaml`, replace the two header lines

```
# row's id by a field and branches with if, switch, try, for and while. The tests load it to show that the profile and
# the checks read outside names and comments by a language's own patterns; later steps add their keys to it.
```

with

```
# row's id by a field and branches with if, switch, try, for and while. A call that builds a mock names its spec by a
# type argument, written between angle brackets after what it calls. The tests load it to show that the profile and
# the checks read outside names and comments by a language's own patterns; later steps add their keys to it.
```

and replace its last line `writing: {call: "{callee}(...)", field: '{..., {field}: "{text}"}'}` with:

```yaml
writing: {call: "{callee}(...)", field: '{..., {field}: "{text}"}', specs: {type_argument: "{callee}<{before}{value}>()"}}
```

Do not add a `supplies` stanza to Brace.

- [ ] **Step 6: Build the rules tests' languages with the spec templates**

`tests/modules/rules/builders.py` builds `Writing(**PYTHON_FILE["writing"])` and `Writing(**BRACE_FILE["writing"])`,
which would now pass `specs` as a dict. In that file:

(a) Change the import line
`from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, Writing` to
`from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, SpecWriting, Writing`.

(b) Just above `def _record_mark(mark: dict, member: str) -> RecordMark:`, add:

```python
def writing_of(file: dict) -> Writing:
    """How a language's data file writes a row of a table and a call that builds a mock, as its loader reads it: the
    row templates, and those of a mock's spec under specs."""
    written = dict(file.get("writing", {}))
    return Writing(**{key: line for key, line in written.items() if key != "specs"},
                   specs=SpecWriting(**written.get("specs", {})))


```

(c) Replace `writing=Writing(**PYTHON_FILE["writing"])` (line 103) with `writing=writing_of(PYTHON_FILE)` and
`writing=Writing(**BRACE_FILE["writing"])` (line 116) with `writing=writing_of(BRACE_FILE)`.

- [ ] **Step 7: Run the tests to see them pass**

Run: `uv run pytest -q -p no:cacheprovider tests/profile_values tests/modules/spec tests/modules/rules tests/architecture`
Expected: all pass.

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 8: Commit**

```bash
git add xarch/profile_values/language.py xarch/modules/spec/application/logic/language_file.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/modules/rules/builders.py \
  tests/profile_values/test_language.py tests/modules/spec/application/logic/test_language_file.py
git commit -m "A language's data file writes how a call that builds a mock names its spec under writing.specs, one template per way, Python by keyword and position and the test-only Brace by type argument"
```

---

### Task 2: `testing.mocks.specs` replaces `spec_keywords` and `spec_position`, and the check and the docs write a mock by its template

**Files:**
- Modify: `xarch/profile_values/testing.py:7` (import), `:107-119` (`StandIns`, new `SpecEntry` before it)
- Modify: `xarch/modules/spec/domain/profile_keys.py:31` (`MOCK_SPECS`), `:68` (`SCOPES`), `:223` (`RETIRED`)
- Modify: `xarch/modules/spec/domain/key_table.py:21` (import), `:163-164` (keys)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:25-35` (imports), before `_outside_name_at` (line 552:
  new `SPECS`, `_SPEC_SAID`, `spec_entries`, `_spec_entry`, `unwritten_specs`), `:601-625` (`identifiers` private)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:571`, `:652-677` (`_mocks`)
- Modify: `xarch/modules/rules/application/logic/stand_ins.py:20-25` (module docstring), `:30-35` (imports),
  `:157-205` (`_Built` docstring, `_mock`, `_spec`, new `_read`)
- Modify: `xarch/modules/spec/application/logic/docs_template.py:84`, `:497-499`, `:672-685`
- Modify: `xarch/architectures/presets/testing/pytest.yaml:19-20`
- Modify: `xarch/architectures/presets/format/keys.yaml:43`, `:874`, `:968-983`
- Modify (test data): `tests/modules/spec/profiles.py:26-29`, `tests/modules/rules/builders.py:26` and `:185-188`,
  `tests/bootstrap/test_loop_tables.py:14`, `tests/bootstrap/test_other_framework.py:15`
- Test: `tests/modules/spec/application/logic/test_testing.py`, `test_profile_parsing_tests.py`, `test_retired_keys.py`,
  `test_profile_keys.py`; `tests/modules/spec/domain/test_profile_keys.py`;
  `tests/modules/rules/application/logic/test_stand_ins.py`; `tests/modules/rules/adapters/test_spec_profile.py`;
  `tests/bootstrap/test_bundled_guards.py`; `tests/architecture/test_agnostic.py`

**Interfaces:**
- Consumes (Task 1): `SPEC_FORMS`, `SpecWriting`, `Writing.writes_spec(form)`,
  `Writing.spec(form, callee, value, keyword="", place=0)`, `tests.modules.rules.builders.writing_of`.
- Produces:
  - `xarch.profile_values.testing.SpecEntry` (frozen dataclass): `keyword: str = ""`, `position: int | None = None`,
    `type_argument: int | None = None`; properties `form -> str` (one of `SPEC_FORMS`) and `place -> int`; method
    `written(self, writing: Writing, callee: str, value: str) -> str`.
  - `StandIns(mocks, autospec, specs: tuple[SpecEntry, ...], fixtures: tuple[Fixture, ...] = ())` — the fields
    `spec` and `spec_position` are gone.
  - `xarch.modules.spec.domain.profile_keys.MOCK_SPECS = "testing.mocks.specs"`, scope address
    `"testing.mocks.specs[]"`.
  - `profile_checks.spec_entries(value, where, problems, language) -> tuple[SpecEntry, ...] | None` and
    `profile_checks.unwritten_specs(specs, where, unread, language) -> list[str]`.
  - `profile_parsing._mocks(value, problems, language, unread=frozenset())`.
  - `tests.modules.rules.builders.PYTEST_SPECS`.

- [ ] **Step 1: Write the failing loader tests**

(a) `tests/modules/spec/profiles.py`: replace lines 26-29 of `TESTING`

```python
           "mocks": {"calls": ["unittest.mock.Mock", "unittest.mock.MagicMock"],
                     "autospec": ["unittest.mock.create_autospec"], "spec_keywords": ["spec", "spec_set"],
                     "spec_position": 0, "fixtures": {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
```

with

```python
           "mocks": {"calls": ["unittest.mock.Mock", "unittest.mock.MagicMock"],
                     "autospec": ["unittest.mock.create_autospec"],
                     "specs": [{"keyword": "spec"}, {"keyword": "spec_set"}, {"position": 0}],
                     "fixtures": {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
```

(b) `tests/modules/spec/application/logic/test_testing.py`:

- Import lines 12-13 become:

```python
from xarch.profile_values.language import SpecWriting, Writing
from xarch.profile_values.testing import Fixture, Place, RowId, ScenarioCoverage, SpecEntry, StandIns, TableForm
```

- Replace the constants `MOCKS = (...)` and `POSITION = (...)` (lines 26-31) with:

```python
MOCKS = ("layered.yaml: testing.mocks: must be a mapping {calls, specs}, and optionally autospec and fixtures: the "
         "dotted names of the calls that build a mock, the ways a mock is given its spec, in order, and the parameters "
         "of a test function whose methods build one")
SPECS = ("layered.yaml: testing.mocks.specs: must be a list of {keyword}, {position} or {type_argument}: the ways a "
         "call that builds a mock names its spec, in order, such as [{keyword: spec}]")
SPEC_ENTRY = ("layered.yaml: testing.mocks.specs.{index}: must be one of {{keyword: <name>}}, {{position: <n>}} or "
              "{{type_argument: <n>}}")
WHOLE = "layered.yaml: testing.mocks.specs.{index}.{key}: must be a whole number, at least 0, such as 0"
RETIRED = ("layered.yaml: testing.mocks: unknown key '{key}': moved in 0.3.0: write specs: [{{keyword: spec}}, "
           "{{position: 0}}]; use autospec, calls, fixtures, specs")
```

- Replace the parametrized `test_the_mocks_load_the_position_of_the_argument_that_names_the_spec` (lines 80-88) with:

```python
def test_the_mocks_load_the_ways_a_call_names_its_spec_in_the_order_written():
    document = with_mocks(MOCKS_OK) | {"guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].specs == (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"),
                                                SpecEntry(position=0))
    document = with_mocks(MOCKS_OK | {"specs": [{"position": 2}, {"keyword": "spec"}]}) | {
        "guards": {"stand-ins": {}}, "fakes": FAKES}
    assert parsed(document).guards[0].specs == (SpecEntry(position=2), SpecEntry(keyword="spec"))
```

- In the parametrize of `test_a_bad_mocks_entry_is_refused`, replace the two params

```python
    pytest.param({"spec_keywords": ["spec"]}, "layered.yaml: testing.mocks: missing `calls`",
                 id="mocks with no calls are refused"),
    pytest.param({"calls": [MOCKS_OK["calls"][0]]}, "layered.yaml: testing.mocks: missing `spec_keywords`",
                 id="mocks with no spec keywords are refused"),
```

with

```python
    pytest.param({"specs": [{"keyword": "spec"}]}, "layered.yaml: testing.mocks: missing `calls`",
                 id="mocks with no calls are refused"),
    pytest.param({"calls": [MOCKS_OK["calls"][0]]}, "layered.yaml: testing.mocks: missing `specs`",
                 id="mocks with no specs are refused, none being filled in"),
```

  and replace the last five params (from `pytest.param(MOCKS_OK | {"spec_keywords": ["spec", "spec"]},` through
  `id="a spec position that is true is refused"),`) with:

```python
    pytest.param(MOCKS_OK | {"specs": []}, SPECS, id="an empty list of specs is refused"),
    pytest.param(MOCKS_OK | {"specs": "spec"}, SPECS, id="specs that are no list are refused"),
    pytest.param(MOCKS_OK | {"specs": {"keyword": "spec"}}, SPECS, id="one entry written as a map, not a list"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"keyword": "spec", "position": 0}]},
                 SPEC_ENTRY.format(index=1), id="an entry with two keys, at its index"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {}]}, SPEC_ENTRY.format(index=1),
                 id="an entry with no key"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"generic": 0}]}, SPEC_ENTRY.format(index=1),
                 id="an entry whose key is none of the three"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, "spec_set"]}, SPEC_ENTRY.format(index=1),
                 id="an entry that is no mapping"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "a b"}]},
                 "layered.yaml: testing.mocks.specs.0.keyword: 'a b' is not a keyword name",
                 id="a keyword that is no keyword name is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": 3}]},
                 "layered.yaml: testing.mocks.specs.0.keyword: 3 is not a keyword name",
                 id="a keyword that is no text is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": -1}]}, WHOLE.format(index=0, key="position"),
                 id="a position below 0 is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": "0"}]}, WHOLE.format(index=0, key="position"),
                 id="a position that is text is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"position": True}]}, WHOLE.format(index=0, key="position"),
                 id="a position that is true is refused"),
    pytest.param(MOCKS_OK | {"specs": [{"keyword": "spec"}, {"position": 0}, {"keyword": "spec"}]},
                 "layered.yaml: testing.mocks.specs.2: {keyword: spec} is listed twice",
                 id="a keyword entry listed twice is refused at its second index"),
    pytest.param(MOCKS_OK | {"specs": [{"position": 0}, {"position": 0}]},
                 "layered.yaml: testing.mocks.specs.1: {position: 0} is listed twice",
                 id="a position entry listed twice is refused"),
    pytest.param(MOCKS_OK | {"spec_keywords": ["spec"]}, RETIRED.format(key="spec_keywords"),
                 id="spec_keywords is retired with what to write"),
    pytest.param(MOCKS_OK | {"spec_position": 0}, RETIRED.format(key="spec_position"),
                 id="spec_position is retired with what to write"),
    pytest.param(MOCKS_OK | {"colour": 1},
                 "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
                 id="an unknown key is told the keys of mocks"),
```

- Replace `test_mocks_with_neither_calls_nor_spec_keywords_report_each_one_missing` (lines 164-166) with:

```python
def test_a_type_argument_place_that_is_no_whole_number_is_refused():
    assert problems(with_mocks(MOCKS_OK | {"specs": [{"type_argument": 1.5}]}),
                    languages={"python": READS_EVERY_FACT}) == [WHOLE.format(index=0, key="type_argument")]


def test_mocks_with_neither_calls_nor_specs_report_each_one_missing():
    assert problems(with_mocks({"autospec": ["unittest.mock.create_autospec"]})) == [
        "layered.yaml: testing.mocks: missing `calls`", "layered.yaml: testing.mocks: missing `specs`"]


def test_both_retired_keys_written_give_one_problem_each_in_sorted_order():
    assert problems(with_mocks(MOCKS_OK | {"spec_position": 0, "spec_keywords": ["spec"]})) == [
        RETIRED.format(key="spec_keywords"), RETIRED.format(key="spec_position")]


def test_the_retired_keys_written_in_place_of_specs_are_refused_beside_the_missing_specs():
    mocks = {"calls": MOCKS_OK["calls"], "spec_keywords": ["spec", "spec_set"], "spec_position": 0}
    assert problems(with_mocks(mocks)) == [RETIRED.format(key="spec_keywords"), RETIRED.format(key="spec_position"),
                                           "layered.yaml: testing.mocks: missing `specs`"]
```

  (The type-argument place test runs under `READS_EVERY_FACT`, Python's reader read as supplying every fact, so that
  from Task 3 on the needs refusal of `call.type_arguments` does not stand beside the place's problem.)

- Just above `def test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines():` (line 244), add:

```python
def test_the_stand_ins_line_writes_a_mock_by_the_language_s_template_of_the_first_spec_form():
    architecture = parsed(covered(guards={"scenario-coverage": SCENARIOS, "stand-ins": {}}, fakes=FAKES))
    guards = tuple(replace(guard, specs=(SpecEntry(type_argument=0), SpecEntry(keyword="spec")))
                   if isinstance(guard, StandIns) else guard for guard in architecture.guards)
    writing = Writing(specs=SpecWriting(type_argument="{callee}<{before}{value}>()"))
    typed = replace(architecture, guards=guards, language=replace(
        architecture.language, checked=replace(architecture.language.checked, writing=writing)))
    lines = fill("{{guards}}", typed, "layered.md", file_types=FILE_TYPES).splitlines()
    line = next(line for line in lines if line.startswith("- `stand-ins`"))
    assert "names what it stands in for, `Mock<<Port>>()` (or, from a fixture, `mocker.Mock<<Port>>()`)" in line


```

  (This is spec test 25. It lives beside the other stand-ins line tests, which are in this file, not in
  `test_docs_template.py`; the pytest line, byte for byte, stays pinned by the existing
  `test_the_guards_lines_say_the_names_of_the_framework_the_file_declares`.)

- In `test_a_profile_naming_another_framework_gets_its_own_words_in_the_guards_lines`, replace
  `"mocks": {"calls": ["doubles.Double"], "spec_keywords": ["of"]}}` with
  `"mocks": {"calls": ["doubles.Double"], "specs": [{"keyword": "of"}]}}` (its assertion `` `Double(of=<Port>)` ``
  stays).

- Replace the `TOY` definition and docstring (lines 422-423) with:

```python
TOY = replace(READS_EVERY_FACT, checked=replace(READS_EVERY_FACT.checked, title="Toy",
                                                  writing=Writing(specs=READS_EVERY_FACT.checked.writing.specs)))
"""Python, reading every form, as a language whose data file writes no template of a row: it cannot say a row; it
writes a mock's spec as Python does."""
```

(c) `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

- Replace import line 26 (`from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId,
  ScenarioCoverage, StandIns, TableForm`) with:

```python
from xarch.profile_values.testing import (
    Fakes,
    Fixture,
    Framework,
    Place,
    RowId,
    ScenarioCoverage,
    SpecEntry,
    StandIns,
    TableForm,
)
```

- Just above `PRESET_PROBLEM = (` (line 29) add:

```python
SPECS = ("must be a list of {keyword}, {position} or {type_argument}: the ways a call that builds a mock names its spec, "
         "in order, such as [{keyword: spec}]")
"""What the loader says of a `testing.mocks.specs` that is no list of entries."""
```

- Line 110: replace `"mocks": {"calls": ["unittest.mock.Mock"], "spec_keywords": ["spec"]}}` with
  `"mocks": {"calls": ["unittest.mock.Mock"], "specs": [{"keyword": "spec"}]}}`.

- In `test_the_table_of_cases_and_the_mocks_are_checked_with_the_framework_whether_or_not_a_guard_uses_them` (line
  207), replace

```python
    document["testing"]["mocks"] = {"calls": [], "autospec": ["a.b"], "spec_keywords": [], "fixtures": {}, "colour": 1}
```

  with `document["testing"]["mocks"] = {"calls": [], "autospec": ["a.b"], "specs": [], "fixtures": {}, "colour": 1}`,
  and in its expected list replace the two lines

```python
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, spec_keywords, spec_position",
        "layered.yaml: testing.mocks.calls: must be a list of outside names such as <package>.<name>",
        "layered.yaml: testing.mocks.spec_keywords: must be a list of keyword names such as [spec]",
```

  with

```python
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
        "layered.yaml: testing.mocks.calls: must be a list of outside names such as <package>.<name>",
        f"layered.yaml: testing.mocks.specs: {SPECS}",
```

- In `test_the_guards_in_use_are_those_named_with_the_framework_s_words_taken_from_testing` (line 580), replace

```python
                 (("unittest", "mock", "create_autospec"),), ("spec", "spec_set"),
                 (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),), 0),
```

  with

```python
                 (("unittest", "mock", "create_autospec"),),
                 (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"), SpecEntry(position=0)),
                 (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),)),
```

- In `test_a_problem_of_the_mocks_does_not_stop_the_callees_being_checked` (line 1072), replace its body's mocks line
  and its last two expected lines so that it reads:

```python
def test_a_problem_of_the_mocks_does_not_stop_the_callees_being_checked():
    document = tabled([BY_TEST], EACH)
    document["testing"]["mocks"] = {"calls": ["vitest#vi.fn"], "specs": [], "colour": 1}
    assert problems(document, languages=BRACED) == [
        undeclared(0, "vitest#it.each"),
        "layered.yaml: testing.mocks: unknown key 'colour': use autospec, calls, fixtures, specs",
        f"layered.yaml: testing.mocks.specs: {SPECS}"]
```

- Append at the end of the file:

```python


def mocked(*specs: dict) -> dict:
    """declaring() with a function form, its mocks built by vitest#vi.fn and naming their spec by the specs given, and
    the guard stand-ins on."""
    return declaring([BY_TEST], mocks={"calls": ["vitest#vi.fn"], "specs": list(specs)}) | {
        "guards": {"stand-ins": {}}, "fakes": FAKES}


def test_under_brace_a_mock_may_name_its_spec_by_a_type_argument():
    stand_ins = next(guard for guard in parsed(mocked({"type_argument": 0}, {"type_argument": 1}),
                                               languages=BRACED).guards if isinstance(guard, StandIns))
    assert stand_ins.specs == (SpecEntry(type_argument=0), SpecEntry(type_argument=1))


@pytest.mark.parametrize("specs, said", [
    pytest.param([{"keyword": "of"}], ["0: the language Brace does not write `writing.specs.keyword`, how a mock is given "
                                       "its spec by a keyword"], id="a keyword"),
    pytest.param([{"type_argument": 0}, {"position": 0}],
                 ["1: the language Brace does not write `writing.specs.position`, how a mock is given its spec by a "
                  "position"], id="a position, at its index"),
])
def test_under_brace_a_spec_form_it_does_not_write_is_refused_at_its_entry(specs, said):
    assert problems(mocked(*specs), languages=BRACED) == [f"layered.yaml: testing.mocks.specs.{text}" for text in said]


def test_under_python_a_type_argument_is_refused_as_written_by_no_template():
    assert problems(covered(testing=TESTING | {"mocks": TESTING["mocks"] | {"specs": [{"type_argument": 0}]}}),
                    languages={"python": replace(PYTHON, checked=replace(PYTHON.checked, supplies=None))}) == [
        "layered.yaml: testing.mocks.specs.0: the language Python does not write `writing.specs.type_argument`, how a "
        "mock is given its spec by a type argument"]
```

  (`FAKES`, `BY_TEST`, `declaring`, `BRACED`, `TESTING`, `PYTHON`, `covered`, `parsed`, `problems` and `replace` are
  already defined or imported in this file. The last test reads Python as a language whose file says nothing of its
  reader, so no needs refusal is given and the unwritten-form problem shows alone.)

(d) `tests/modules/spec/application/logic/test_retired_keys.py`:

- After the line `FUNCTIONS_MOVED = 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'` (line 100), add
  `SPECS_MOVED = "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"`.
- At the end of the parametrize of `test_the_shipped_table_answers_each_name_in_its_scope`, after
  `pytest.param(TESTING, "table", TABLE_MOVED, id="the testing key table"),`, add:

```python
    pytest.param(MOCKS, "spec_keywords", SPECS_MOVED, id="the mocks key spec_keywords"),
    pytest.param(MOCKS, "spec_position", SPECS_MOVED, id="the mocks key spec_position"),
    pytest.param(MOCKS, "specs", "", id="the mocks key specs"),
```

- At the end of the parametrize of `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`, after
  `pytest.param("testing.functions", FUNCTIONS_MOVED, id="testing.functions"),`, add:

```python
    pytest.param("testing.mocks.spec_keywords", SPECS_MOVED, id="testing.mocks.spec_keywords"),
    pytest.param("testing.mocks.spec_position", SPECS_MOVED, id="testing.mocks.spec_position"),
```

(e) `tests/modules/spec/domain/test_profile_keys.py`:

- In its `from xarch.modules.spec.domain.profile_keys import (...)`, add `MOCK_SPECS,` and `MOCKS,` after `HELD,`.
- In `test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules`,
  replace the last row `        Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'))`
  with:

```python
        Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),
        Retired(MOCKS, "spec_keywords", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
        Retired(MOCKS, "spec_position", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"))
```

- Just above `def test_testing_names_its_preset_by_a_key_that_is_not_required_and_offers_the_presets():`, add:

```python
def test_the_ways_a_mock_names_its_spec_are_a_required_list_scope_of_keyword_position_and_type_argument():
    assert SCOPES[MOCK_SPECS] == "testing.mocks.specs[]"
    assert [key.name for key in KEYS if key.scope == MOCKS] == ["calls", "autospec", "specs", "fixtures"]
    assert [key.name for key in KEYS if key.scope == MOCK_SPECS] == ["keyword", "position", "type_argument"]
    assert [(key.required, key.opens, key.rules) for key in KEYS if (key.scope, key.name) == (MOCKS, "specs")] == [
        (True, MOCK_SPECS, ("stand-ins",))]
    assert {key.name: key.rules for key in KEYS if key.scope == MOCK_SPECS} == dict.fromkeys(
        ("keyword", "position", "type_argument"), ("stand-ins",))


```

(f) `tests/modules/spec/application/logic/test_profile_keys.py` (every key's example loads under Python; the example of
`testing.mocks.specs[].type_argument` needs a language that writes a type argument):

- In its `from xarch.modules.spec.domain.profile_keys import (...)`, add `MOCK_SPECS,` after `GUARD,`.
- Change `from xarch.profile_values.language import InterfaceMark` to
  `from xarch.profile_values.language import InterfaceMark, SpecWriting`.
- Replace the function `load` with:

```python
EVERY_SPEC = replace(READS_EVERY_FACT, checked=replace(READS_EVERY_FACT.checked, writing=replace(
    READS_EVERY_FACT.checked.writing, specs=SpecWriting(**{**vars(READS_EVERY_FACT.checked.writing.specs),
                                                            "type_argument": "{callee}<{before}{value}>()"}))))
"""Python, its reader supplying every fact, and writing a mock's spec by a type argument as well, as the TypeScript-like
test-only language does."""


def load(document: dict):
    """The document parsed under Python, its reader read as supplying every fact and its data file writing every way a
    mock names its spec: an example shows its key loading, whatever Python's own reader reads and its own file
    writes."""
    return parsed(document, bundled=BUNDLED, folders=every_folder(document), languages={"python": EVERY_SPEC})
```

- The unknown-key scan cannot read a `use ...` list from an entry of the new list scope, whose problem names the three
  forms instead (B1); exempt it as `PART_IMPORTS_MAY` is, and pin its own wording. Change
  `@pytest.mark.parametrize("scope", sorted(set(SCOPES) - {PART_IMPORTS_MAY}))` to
  `@pytest.mark.parametrize("scope", sorted(set(SCOPES) - {PART_IMPORTS_MAY, MOCK_SPECS}))`, and append at the end of
  the file:

```python


def test_an_entry_of_the_mock_specs_with_a_key_besides_its_own_is_told_each_key_of_the_scope():
    document = document_of(keys_of(MOCK_SPECS)[0])
    holders(keys_of(MOCK_SPECS)[0], document)[0]["zz_unknown"] = 1
    found = [p for p in problems(document, bundled=BUNDLED, folders=every_folder(document)) if "specs.0:" in p]
    assert found and [key.name for key in keys_of(MOCK_SPECS) if f"{{{key.name}: <" not in found[0]] == []
```

- [ ] **Step 2: Run the loader tests to see them fail**

Run: `uv run pytest -q -p no:cacheprovider tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_profile_keys.py`
Expected: collection errors, `ImportError: cannot import name 'SpecEntry' from 'xarch.profile_values.testing'` (and
`MOCK_SPECS` from `profile_keys`).

- [ ] **Step 3: Write the failing tests of the check**

(a) `tests/modules/rules/builders.py`: replace the one-line import
`from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId, ScenarioCoverage, StandIns, TableForm, TestForm`
with

```python
from xarch.profile_values.testing import (
    Fakes,
    Fixture,
    Framework,
    Place,
    RowId,
    ScenarioCoverage,
    SpecEntry,
    StandIns,
    TableForm,
    TestForm,
)
```

  just above `PROFILE = Profile(` (after the docstring of `PYTEST_FORM`), add:

```python
PYTEST_SPECS = (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"), SpecEntry(position=0))
"""The ways a mock names its spec under pytest, as its preset says them, in order."""
```

  and in `PROFILE` replace

```python
    stand_ins=StandIns((MOCK, ("unittest", "mock", "MagicMock")), (AUTOSPEC,), ("spec", "spec_set"),
                       (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),), 0),
```

  with

```python
    stand_ins=StandIns((MOCK, ("unittest", "mock", "MagicMock")), (AUTOSPEC,), PYTEST_SPECS,
                       (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),)),
```

(b) `tests/modules/rules/application/logic/test_stand_ins.py`:

- Replace the module docstring (lines 1-3) with:

```python
"""The stand-ins guard on hand-made source files: a port is read or fire-only by its return annotations, a read port
has a fake, a mock in a test that may use the fakes names a spec that is not a read port (by the first of the
profile's specs it gives: a keyword, the argument at a place, or the type argument at a place), and a fake that does
not define every method of its port is weak."""
```

- After `from xarch.modules.rules.domain.published import Weak`, add
  `from xarch.profile_values.testing import SpecEntry` (Task 3 widens it).
- Replace `placed` (lines 141-143) with:

```python
KEYWORDS = (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"))
"""The keyword entries of pytest's specs, with no position."""


def placed(position: int | None):
    """PROFILE, its specs the keyword entries and, unless position is None, an entry of the argument at position."""
    assert PROFILE.stand_ins is not None
    specs = KEYWORDS if position is None else (*KEYWORDS, SpecEntry(position=position))
    return replace(PROFILE, stand_ins=replace(PROFILE.stand_ins, specs=specs))
```

  (every case of `test_a_mock_names_its_spec_by_the_argument_at_the_position_the_profile_gives` keeps its text.)

- Just above `NO_SPEC_FIXTURE = (` add:

```python
def specified(*specs: SpecEntry):
    """PROFILE, its specs the entries given, in order."""
    assert PROFILE.stand_ins is not None
    return replace(PROFILE, stand_ins=replace(PROFILE.stand_ins, specs=specs))


@pytest.mark.parametrize("checked, expected", [
    pytest.param(PROFILE, [], id="pytest lists the keywords first: spec= names the fire-only port"),
    pytest.param(specified(SpecEntry(position=0), *KEYWORDS),
                 [f"tests/{INTEGRATION_TEST}:5: Mock(Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a position listed first: the first argument names the read port"),
])
def test_a_call_giving_two_entries_names_its_spec_by_the_first_the_profile_lists(checked, expected):
    call = Call(5, MOCK, (REPO,), keywords=(("spec", NOTIFIER),))
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(call,))], checked) == expected


def test_a_read_port_named_by_a_later_keyword_is_written_with_that_keyword():
    call = Call(5, MOCK, keywords=(("spec_set", REPO),))
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(call,))]) == [
        f"tests/{INTEGRATION_TEST}:5: Mock(spec_set=Repo) stands in for Repo, a read port (stand-ins)"]


def test_an_autospec_reads_the_position_after_the_first_keyword_but_no_later_keyword():
    checked = specified(SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"), SpecEntry(position=1))
    calls = (Call(5, AUTOSPEC, (None, NOTIFIER)), Call(6, AUTOSPEC, keywords=(("spec_set", NOTIFIER),)))
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=calls)], checked) == [
        f"tests/{INTEGRATION_TEST}:6: create_autospec() names nothing it stands in for (stand-ins)"]


```

  (Spec test 19, an autospec with `spec_set=` alone naming nothing, is the existing case `"spec_set is not a keyword
  create_autospec takes its spec by"`, which keeps passing.)

(c) Other tests that build `StandIns` or read its old fields:

- `tests/bootstrap/test_bundled_guards.py`: in the import line add `SpecEntry` between `ScenarioCoverage` and
  `StandIns`; replace

```python
        stand_ins=StandIns(tuple(("unittest", "mock", m) for m in mocks), (("unittest", "mock", "create_autospec"),),
                               ("spec", "spec_set"), (Fixture("mocker", mocks, ("create_autospec",)),), 0),
```

  with

```python
        stand_ins=StandIns(tuple(("unittest", "mock", m) for m in mocks), (("unittest", "mock", "create_autospec"),),
                           (SpecEntry(keyword="spec"), SpecEntry(keyword="spec_set"), SpecEntry(position=0)),
                           (Fixture("mocker", mocks, ("create_autospec",)),)),
```

- `tests/modules/rules/adapters/test_spec_profile.py`: in the import line
  `from xarch.profile_values.testing import Fakes, Fixture, Framework, ScenarioCoverage, StandIns` add `SpecEntry`
  before `StandIns`, and replace both occurrences (lines 58 and 122) of
  `StandIns((("m", "Mock"),), (), ("spec",), (Fixture("mocker", ("Mock",)),))` with
  `StandIns((("m", "Mock"),), (), (SpecEntry(keyword="spec"),), (Fixture("mocker", ("Mock",)),))`.
- `tests/architecture/test_agnostic.py`: in `framework_names`, replace
  `dotted = (*guard.mocks, *guard.autospec, guard.spec)` with
  `dotted = (*guard.mocks, *guard.autospec, tuple(spec.keyword for spec in guard.specs if spec.keyword))`
  (the scan still holds `spec_set`, which `test_the_framework_names_are_those_of_the_bundled_profiles` asserts).
- `tests/bootstrap/test_loop_tables.py:14` and `tests/bootstrap/test_other_framework.py:15`: replace
  `mocks: {calls: [doubles.Double], spec_keywords: [of]}` with `mocks: {calls: [doubles.Double], specs: [{keyword: of}]}`.

- [ ] **Step 4: Run the check tests to see them fail**

Run: `uv run pytest -q -p no:cacheprovider tests/modules/rules/application/logic/test_stand_ins.py`
Expected: collection error, `ImportError: cannot import name 'SpecEntry'`.

- [ ] **Step 5: Add `SpecEntry` and `StandIns.specs`**

In `xarch/profile_values/testing.py`, change line 7 to
`from xarch.profile_values.language import SPEC_FORMS, Writing`, and replace the whole `StandIns` class (lines 107-118)
with:

```python
@dataclass(frozen=True)
class SpecEntry:
    """One way a call that builds a mock names its spec, as an entry of the framework's `testing.mocks.specs` says it,
    exactly one of three: a keyword argument (keyword, its name), the positional argument at a place from 0
    (position), or the type argument at a place from 0 (type_argument)."""
    keyword: str = ""
    position: int | None = None
    type_argument: int | None = None

    @property
    def form(self) -> str:
        """The key the entry is written with, one of SPEC_FORMS."""
        if self.keyword:
            return SPEC_FORMS[0]
        return SPEC_FORMS[1] if self.position is not None else SPEC_FORMS[2]

    @property
    def place(self) -> int:
        """The place, from 0, of the argument that names the spec; 0 for a keyword entry."""
        return self.position if self.position is not None else self.type_argument or 0

    def written(self, writing: Writing, callee: str, value: str) -> str:
        """The call of callee naming the spec value as the language writes it, by writing's `specs` template of the
        entry's form."""
        return writing.spec(self.form, callee, value, self.keyword, self.place)


@dataclass(frozen=True)
class StandIns:
    """The guard stand-ins: the dotted names of the calls that build a mock, of those that build a mock from a spec
    given as an argument (autospec), and the ways a call that builds one names its spec (specs, in the order written:
    a call names it by the first entry it gives, and a fix writes the first entry; an autospec call reads only the
    first keyword entry of them); and the fixtures, whose methods build mocks the same way. The other parameters are
    those of `fakes`."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    specs: tuple[SpecEntry, ...]
    fixtures: tuple[Fixture, ...] = ()
```

- [ ] **Step 6: Open the scope `testing.mocks.specs[]` and retire the two keys**

In `xarch/modules/spec/domain/profile_keys.py`:

- After `MOCKS = "testing.mocks"` (line 31) add `MOCK_SPECS = "testing.mocks.specs"`.
- In `SCOPES`, after `    MOCKS: "testing.mocks",` add `    MOCK_SPECS: "testing.mocks.specs[]",`.
- In `RETIRED`, after the row `    Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),`
  add:

```python
    Retired(MOCKS, "spec_keywords", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
    Retired(MOCKS, "spec_position", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
```

In `xarch/modules/spec/domain/key_table.py`:

- In the import list from `profile_keys`, add `MOCK_SPECS,` immediately before `MOCKS,` (ruff's isort places it there).
- Replace

```python
    Key(MOCKS, "spec_keywords", True, rules=("stand-ins",)),
    Key(MOCKS, "spec_position", rules=("stand-ins",)),
    Key(MOCKS, "fixtures", rules=("stand-ins",), opens=FIXTURE),
```

  with

```python
    Key(MOCKS, "specs", True, rules=("stand-ins",), opens=MOCK_SPECS),
    Key(MOCK_SPECS, "keyword", rules=("stand-ins",)),
    Key(MOCK_SPECS, "position", rules=("stand-ins",)),
    Key(MOCK_SPECS, "type_argument", rules=("stand-ins",)),
    Key(MOCKS, "fixtures", rules=("stand-ins",), opens=FIXTURE),
```

  (The order is the order of `keys.yaml`'s entries, Step 9.)

- [ ] **Step 7: Read and refuse the entries in the loader**

In `xarch/modules/spec/application/logic/profile_checks.py`:

(a) After `from xarch.profile_values.excluded import Excluded` add `from xarch.profile_values.language import SPEC_FORMS`;
in the `from xarch.profile_values.testing import (...)` block add `SpecEntry,` between `RowId,` and `TableForm,`.

(b) Just above `def _outside_name_at(` (line 552), add:

```python
SPECS = ("must be a list of {keyword}, {position} or {type_argument}: the ways a call that builds a mock names its "
         "spec, in order, such as [{keyword: spec}]")
"""What the loader says of a value of `testing.mocks.specs` that is no list of entries, or an empty one."""
_SPEC_SAID = {"keyword": "a keyword", "position": "a position", "type_argument": "a type argument"}
"""How a problem says each way a call names its spec."""


def spec_entries(value: Any, where: str, problems: list[str], language: Language) -> tuple[SpecEntry, ...] | None:
    """The ways a call that builds a mock names its spec, at least one, in the order written, each entry addressed
    `<where>.<i>`, i from 0, every entry counted, and each once; None when the list or any entry has a problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: {SPECS}")
        return None
    count = len(problems)
    found: list[SpecEntry] = []
    for index, entry in enumerate(value):
        read = _spec_entry(entry, f"{where}.{index}", problems, language)
        if read is not None and read in found:
            problems.append(f"{where}.{index}: {{{read.form}: {read.keyword or read.place}}} is listed twice")
        elif read is not None:
            found.append(read)
    return tuple(found) if len(problems) == count else None


def _spec_entry(entry: Any, where: str, problems: list[str], language: Language) -> SpecEntry | None:
    """One way a call names its spec: exactly one of {keyword: <name>}, {position: <n>} and {type_argument: <n>}."""
    form, item = next(iter(entry.items())) if isinstance(entry, Mapping) and len(entry) == 1 else ("", None)
    if form not in SPEC_FORMS:
        problems.append(f"{where}: must be one of {{keyword: <name>}}, {{position: <n>}} or {{type_argument: <n>}}")
        return None
    if form == "keyword" and not (isinstance(item, str) and names.is_name(item, language.names)):
        problems.append(f"{where}.keyword: {item!r} is not a keyword name")
        return None
    if form != "keyword" and not _counted(item):
        problems.append(f"{where}.{form}: must be a whole number, at least 0, such as 0")
        return None
    return SpecEntry(**{form: item})


def unwritten_specs(specs: tuple[SpecEntry, ...], where: str, unread: Collection[str], language: Language) -> list[str]:
    """A problem for each entry of the list at where whose way of naming a spec the language does not write (its data
    file's `writing.specs`), in the order of the list; none for an entry the needs of the profile refuse already
    (unread)."""
    writing, title = language.checked.writing, language.checked.title
    return [f"{where}.{index}: the language {title} does not write `writing.specs.{entry.form}`, how a mock is given its "
            f"spec by {_SPEC_SAID[entry.form]}" for index, entry in enumerate(specs)
            if not writing.writes_spec(entry.form) and f"{where}.{index}.{entry.form}" not in unread]


```

  (`names`, `Collection`, `Mapping`, `Any`, `Language` and `_counted` are already imported or defined in this file.
  `unwritten_specs` enumerates `specs` by the list's own index: `spec_entries` returns a tuple only when every entry
  was read, duplicates included, so the two indices agree.)

(c) `identifiers` (line 611) is only called inside this file once the loader stops reading `spec_keywords`; a public
function no other file names fails `xarch check --strict` (`dead-code.tests_only`). Rename it `_identifiers`: change
its `def` line to `def _identifiers(value: Any, where: str, problems: list[str], noun: str, example: str,` with the
next line indented one more space (`                 language: Language) -> tuple[str, ...] | None:`), its docstring
to `"""A non-empty list of names, each once, each a plain identifier: the methods of an object."""`, and its two calls
in `fixtures` (lines 601-602) from `identifiers(` to `_identifiers(`.

In `xarch/modules/spec/application/logic/profile_parsing.py`:

(d) In `_testing` (line 571), replace
`    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None` with
`    mocks = _mocks(value["mocks"], problems, language, unread) if "mocks" in value else None`.

(e) Replace the whole function `_mocks` (lines 652-677) with:

```python
def _mocks(value: Any, problems: list[str], language: Language,
           unread: Collection[str] = frozenset()) -> StandIns | None:
    """How a mock is built, and the ways a call that builds one names its spec; an entry of specs the language does not
    write is refused, unless the needs of the profile refuse it already (unread)."""
    where = "testing.mocks"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{calls, specs}}, and optionally autospec and fixtures: the dotted "
                        "names of the calls that build a mock, the ways a mock is given its spec, in order, and the "
                        "parameters of a test function whose methods build one")
        return None
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(MOCKS), where, MOCKS)
    problems += [f"{where}: missing `{key}`" for key in required_of(MOCKS) if key not in value]
    calls = ck.outside_names(value["calls"], f"{where}.calls", problems, language) if "calls" in value else None
    autospec = ck.outside_names(value["autospec"], f"{where}.autospec", problems, language) if "autospec" in value else ()
    problems += [f"{where}.autospec: {outside_text(name, language.checked.member)!r} is also listed in calls"
                 for name in autospec or () if calls and name in calls]
    specs = ck.spec_entries(value["specs"], f"{where}.specs", problems, language) if "specs" in value else None
    problems += ck.unwritten_specs(specs, f"{where}.specs", unread, language) if specs is not None else []
    fixtures = (ck.fixtures(value["fixtures"], f"{where}.fixtures", problems, language, "calls")
                if "fixtures" in value else ())
    if len(problems) != count or calls is None or autospec is None or specs is None or fixtures is None:
        return None
    return StandIns(calls, autospec, specs, fixtures)
```

  (`_whole` stays: other keys use it.)

- [ ] **Step 8: Walk the list in the check, and write the mock by its template in the check and the docs**

In `xarch/modules/rules/application/logic/stand_ins.py`:

(a) In the module docstring, replace the paragraph

```
In a test whose tier may import the fakes (see tier_imports), every call of one of the profile's mocks names its
spec, as its argument at the profile's spec_position (when the profile gives one) or by one of the profile's spec
keywords, and every call of one of its autospec functions as that argument or by the first spec keyword; one that
names none is a violation. A spec that is a class
of the app, a name X taken from a module or read as an attribute of a module imported whole, whose module is a port's
file and X a read port there, is a violation that points to its fake.
```

with

```
In a test whose tier may import the fakes (see tier_imports), every call of one of the profile's mocks names its
spec by the first of the profile's specs it gives, in their order: a keyword argument, the positional argument at a
place, or the type argument at a place; every call of one of its autospec functions the same, reading of the keyword
entries only the first. One that names none is a violation, whose fix writes the first entry by the language's
template of its form (its data file's `writing.specs`). A spec that is a class
of the app, a name X taken from a module or read as an attribute of a module imported whole, whose module is a port's
file and X a read port there, is a violation that points to its fake, written as the entry that named it.
```

(b) Replace the imports

```python
from xarch.modules.rules.domain.parsed import Call, Class, ParameterCall, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.testing import StandIns
```

with

```python
from xarch.modules.rules.domain.parsed import Call, Class, ParameterCall, Ref, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.testing import SpecEntry, StandIns
```

(c) In the docstring of `_Built`, replace

```
    how it is shown (the name called, or for a fixture's the parameter and the method joined by a dot), and whether it
    is an autospec, which takes its spec by
    the argument at the profile's position or by the first spec keyword only."""
```

with

```
    how it is shown (the name called, or for a fixture's the parameter and the method joined by a dot), and whether it
    is an autospec, which reads of the profile's specs the keyword entries but the first."""
```

(d) Replace the functions `_mock` and `_spec` (from `def _mock(` to the end of the file) with:

```python
def _mock(file: SourceFile, mock: _Built, ports: dict[tuple[tuple[str, ...], str], _Port], profile: Profile,
          root: str) -> list[Violation]:
    assert profile.fakes is not None and profile.stand_ins is not None
    names, writing = profile.stand_ins, profile.language.writing
    prefix = mock.shown.rpartition(".")[0]
    constructor = f"{prefix}." if prefix else ""
    suggested = names.specs[0].written(writing, f"{constructor}{names.mocks[0][-1]}", "<port>")
    named, spec, entry = _spec(mock, _read(names.specs, mock.autospec))
    if not named:
        return [Violation(file.name, mock.made.line, f"{mock.shown}() names nothing it stands in for {GUARD}", RULE,
                          f"give it a spec, such as {suggested}")]
    if spec is not None and entry is not None and spec[:1] == (root,):
        port = ports.get((spec[1:-1], spec[-1]))
        if port is not None and port.kind == "read":
            written = entry.written(writing, mock.shown, port.name)
            return [Violation(file.name, mock.made.line, f"{written} stands in for {port.name}, a read port {GUARD}", RULE,
                              f"use its fake {profile.fakes.prefix}{port.name}")]
    return []


def _read(specs: tuple[SpecEntry, ...], autospec: bool) -> tuple[SpecEntry, ...]:
    """The entries a call reads, in their order: every one; for an autospec, the keyword entries but the first left
    out."""
    first = next((entry for entry in specs if entry.keyword), None)
    return tuple(entry for entry in specs if not autospec or not entry.keyword or entry == first)


def _spec(call: _Built, specs: tuple[SpecEntry, ...]) -> tuple[bool, Ref, SpecEntry | None]:
    """Whether the call names a spec (or may, when it unpacks arguments), by the first of specs it gives: a keyword it
    is given, or a positional argument it has at the entry's place; the spec (a Ref) and the entry that named it, None
    and None when none did."""
    made = call.made
    keywords = dict(made.keywords)
    for entry in specs:
        if entry.keyword and entry.keyword in keywords:
            return True, keywords[entry.keyword], entry
        given = made.args if entry.position is not None else ()
        if len(given) > entry.place:
            return True, given[entry.place], entry
    return made.unpacked, None, None
```

  (A `type_argument` entry names nothing yet: Task 3 gives the calls their type arguments.)

In `xarch/modules/spec/application/logic/docs_template.py`:

(e) Line 84: `from xarch.profile_values.testing import ScenarioCoverage, StandIns, TableForm` becomes
`from xarch.profile_values.testing import ScenarioCoverage, SpecEntry, StandIns, TableForm`.

(f) Lines 497-499 become:

```python
        case StandIns(mocks, _, specs, fixtures):
            built = f"{fixtures[0].name}.{fixtures[0].mocks[0]}" if fixtures else ""
            return _stand_ins_line(architecture, mocks[0][-1], specs[0], built)
```

(g) Replace the head of `_stand_ins_line` (from its `def` line through the `mocks = (...)` assignment, lines 672-679)

```python
def _stand_ins_line(architecture: Architecture, mock: str, spec: str, built: str = "") -> str:
    fakes = architecture.fakes
    assert fakes is not None
    parts = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in fakes.stand_in_for])
    tiers = _and([t.name for t in architecture.tiers if any(s.part in fakes.stand_in_for for s in t.subject)])
    fixture = f" (or, from a fixture, `{built}({spec}=<Port>)`)" if built else ""
    mocks = (f"; and every mock in the {tiers} tests names what it stands in for, `{mock}({spec}=<Port>)`{fixture}, "
             "never a read port") if tiers else ""
```

with

```python
def _stand_ins_line(architecture: Architecture, mock: str, spec: SpecEntry, built: str = "") -> str:
    """The line of the guard stand-ins; a mock is written as the first of the profile's specs, by the language's
    template of its form."""
    fakes = architecture.fakes
    assert fakes is not None
    writing = architecture.language.checked.writing
    parts = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in fakes.stand_in_for])
    tiers = _and([t.name for t in architecture.tiers if any(s.part in fakes.stand_in_for for s in t.subject)])
    fixture = f" (or, from a fixture, `{spec.written(writing, built, '<Port>')}`)" if built else ""
    mocks = (f"; and every mock in the {tiers} tests names what it stands in for, "
             f"`{spec.written(writing, mock, '<Port>')}`{fixture}, never a read port") if tiers else ""
```

  (the rest of the function is unchanged).

- [ ] **Step 9: Write `specs` into the pytest preset and the format's key texts**

`xarch/architectures/presets/testing/pytest.yaml`: replace

```yaml
  spec_keywords: [spec, spec_set]
  spec_position: 0
```

with

```yaml
  specs: [{keyword: spec}, {keyword: spec_set}, {position: 0}]
```

`xarch/architectures/presets/format/keys.yaml`:

- In the fragment `mocks: |2` (lines 41-43), replace `        spec_keywords: [spec]` with `        specs: [{keyword: spec}]`.
- In `testing.mocks` (line 874), replace `    accepts: a map {calls, autospec, spec_keywords, spec_position, fixtures}` with
  `    accepts: a map {calls, autospec, specs, fixtures}`.
- Replace the two entries `testing.mocks.spec_keywords:` and `testing.mocks.spec_position:` (lines 968-983, up to but
  not including `  testing.mocks.fixtures:`) with:

```yaml
  testing.mocks.specs:
    meaning: the ways a call that builds a mock names its spec, in order
    accepts: >-
      a non-empty list of entries, each one of {keyword: <name>}, {position: <n>} or {type_argument: <n>}: a call names
      its spec by the first entry it gives, a fix writes the first entry, and an autospec call reads only the first
      keyword entry
    example: |
      <<testing>>
        mocks:
      <<mocks>>
  testing.mocks.specs[].keyword:
    meaning: a keyword argument names the spec
    accepts: a keyword name
    example: |
      <<testing>>
        mocks:
      <<mocks>>
  testing.mocks.specs[].position:
    meaning: the positional argument at a place names the spec
    accepts: "a whole number from 0: the place of the argument"
    example: |
      <<testing>>
        mocks:
          calls: [doubles.make]
          specs: [{keyword: spec}, {position: 0}]
  testing.mocks.specs[].type_argument:
    meaning: the type argument at a place names the spec
    accepts: >-
      a whole number from 0: the place of the type argument; needs call.type_arguments, which a language's reader may
      not supply
    example: |
      <<testing>>
        mocks:
          calls: [doubles.make]
          specs: [{type_argument: 0}]
```

  (Indentation: entries at 2 spaces, their keys at 4, the example block's lines at 6, as the neighbouring entries.)

- [ ] **Step 10: Run the tests of this task to see them pass**

Run: `uv run pytest -q -p no:cacheprovider tests/modules/spec tests/modules/rules tests/architecture tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_loop_tables.py tests/bootstrap/test_other_framework.py tests/profile_values`
Expected: all pass. If any other test fails, read it before changing anything: the prototype found no failure beyond
the ones this task edits.

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 11: Commit**

```bash
git add xarch/profile_values/testing.py xarch/modules/spec/domain/profile_keys.py xarch/modules/spec/domain/key_table.py \
  xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py \
  xarch/modules/rules/application/logic/stand_ins.py xarch/modules/spec/application/logic/docs_template.py \
  xarch/architectures/presets/testing/pytest.yaml xarch/architectures/presets/format/keys.yaml \
  tests/modules/spec/profiles.py tests/modules/rules/builders.py tests/bootstrap/test_loop_tables.py \
  tests/bootstrap/test_other_framework.py tests/bootstrap/test_bundled_guards.py tests/architecture/test_agnostic.py \
  tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_keys.py \
  tests/modules/spec/domain/test_profile_keys.py tests/modules/rules/application/logic/test_stand_ins.py \
  tests/modules/rules/adapters/test_spec_profile.py
git commit -m "testing.mocks.specs lists in order the ways a call that builds a mock names its spec, replacing spec_keywords and spec_position, which are refused with what to write; the stand-ins check walks it and the fixes and the docs line write a mock by the language's writing.specs"
```

---

### Task 3: A call's type arguments, the fact `call.type_arguments`, and its needs

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py:48-55` (`Call`), `:59-68` (`ParameterCall`)
- Modify: `xarch/modules/rules/application/logic/stand_ins.py` (`_spec`, as written in Task 2)
- Modify: `xarch/profile_values/capabilities.py:29` (`FACTS`)
- Modify: `xarch/modules/spec/domain/key_table.py:272` (`NEEDS`)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:133-134` (module docstring)
- Test: `tests/modules/rules/application/logic/test_stand_ins.py` (insert one test, append the Brace tests)
- Test: `tests/modules/rules/domain/test_parsed.py`
- Test: `tests/modules/spec/application/logic/test_profile_needs.py:129-131` and append
- Test: `tests/modules/spec/domain/test_profile_keys.py` (one assert added to the Task 2 test)

**Interfaces:**
- Consumes (Task 2): `SpecEntry`, `StandIns.specs`, `stand_ins._spec`, the `MOCK_SPECS` key `type_argument`.
- Produces: `Call.types: tuple[Ref, ...] = ()` and `ParameterCall.types: tuple[Ref, ...] = ()`, each the last field;
  `FACTS["call.type_arguments"] == "the type arguments a call is given"`;
  `NEEDS["testing.mocks.specs[].type_argument"] == ("call.type_arguments",)`.

- [ ] **Step 1: Write the failing tests**

(a) `tests/modules/rules/application/logic/test_stand_ins.py`: change the import
`from xarch.profile_values.testing import SpecEntry` (Task 2) to
`from xarch.profile_values.testing import Fixture, SpecEntry, StandIns`; just above `NO_SPEC_FIXTURE = (` (after the
tests Task 2 added), add:

```python
def test_a_type_argument_entry_reads_nothing_of_a_call_whose_reader_gives_no_type_arguments():
    checked = specified(SpecEntry(type_argument=0))
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(Call(5, MOCK, (REPO,)),))], checked) == [NO_SPEC]


```

  and append at the end of the file:

```python


BRACE_MOCK = ("vitest", "mock")
BRACE_TEST = "modules/docs/application/services/test_publish.ts"
BRACE_PORTS = ported(READ, path=BRACE_PORT)


def braced(*specs: SpecEntry):
    """PROFILE under the TypeScript-like test-only language, its mocks built by vitest#mock and the fixture vi's mock,
    naming their spec by the entries given."""
    return profile(language=BRACE, stand_ins=StandIns((BRACE_MOCK,), (), specs, (Fixture("vi", ("mock",)),)))


def braced_problems(*calls: Call | ParameterCall, specs: tuple[SpecEntry, ...] = (SpecEntry(type_argument=0),)):
    """The violations of the Brace port and its fake, with a test that makes the calls given."""
    made = in_tests(BRACE_TEST, calls=tuple(c for c in calls if isinstance(c, Call)),
                    parameter_calls=tuple(c for c in calls if isinstance(c, ParameterCall)))
    return [(str(v), v.fix) for v in violations([BRACE_PORTS], [FAKE, made], braced(*specs), "app", "tests")]


@pytest.mark.parametrize("calls, specs, expected", [
    pytest.param((Call(5, BRACE_MOCK, types=(REPO,)),), (SpecEntry(type_argument=0),),
                 [(f"tests/{BRACE_TEST}:5: mock<Repo>() stands in for Repo, a read port (stand-ins)", "use its fake FakeRepo")],
                 id="a read port as the first type argument, written by the language's template"),
    pytest.param((Call(5, BRACE_MOCK),), (SpecEntry(type_argument=0),),
                 [(f"tests/{BRACE_TEST}:5: mock() names nothing it stands in for (stand-ins)",
                   "give it a spec, such as mock<<port>>()")],
                 id="no type argument: the fix writes the first entry by the template"),
    pytest.param((Call(5, BRACE_MOCK, types=(REPO,)),), (SpecEntry(type_argument=1),),
                 [(f"tests/{BRACE_TEST}:5: mock() names nothing it stands in for (stand-ins)",
                   "give it a spec, such as mock<..., <port>>()")],
                 id="a type argument before the place names none"),
    pytest.param((Call(5, BRACE_MOCK, types=(None, REPO)),), (SpecEntry(type_argument=1),),
                 [(f"tests/{BRACE_TEST}:5: mock<..., Repo>() stands in for Repo, a read port (stand-ins)",
                   "use its fake FakeRepo")],
                 id="the type argument at the place is the spec, shown at its place"),
    pytest.param((ParameterCall(5, "vi", "mock", types=(REPO,)),), (SpecEntry(type_argument=0),),
                 [(f"tests/{BRACE_TEST}:5: vi.mock<Repo>() stands in for Repo, a read port (stand-ins)",
                   "use its fake FakeRepo")],
                 id="a fixture's mock is read by its type arguments the same"),
    pytest.param((Call(5, BRACE_MOCK, types=(("app", "modules", "docs", "application", "ports", "repo", "Other"),)),),
                 (SpecEntry(type_argument=0),), [], id="a type argument that is no read port passes"),
])
def test_under_a_typescript_like_language_a_mock_names_its_spec_by_a_type_argument(calls, specs, expected):
    assert braced_problems(*calls, specs=specs) == expected
```

  (`BRACE_PORT`, `READ`, `REPO`, `FAKE`, `ported`, `profile`, `in_tests`, `violations`, `BRACE` are already in the
  file. The port is `READ` alone: under Brace, `None` is no annotation of no value, so `FIRE` would be a read port too.
  The test file sits in `services/`, a folder part of the integration tier, which may use the fakes. Spec tests 21-24
  name the port `Mailer`; the file's port is `Repo`, the same case with the fixtures the file already has.)

(b) `tests/modules/rules/domain/test_parsed.py`: change
`from xarch.modules.rules.domain.parsed import Class, Constant, Function, Row, Table` to
`from xarch.modules.rules.domain.parsed import Call, Class, Constant, Function, ParameterCall, Row, Table`; in the
parametrize of `test_what_a_table_and_its_rows_are_is_said_with_no_word_of_python`, after
`pytest.param(FACTS["test.call"], id="the text of the fact test.call"),` add
`pytest.param(FACTS["call.type_arguments"], id="the text of the fact call.type_arguments"),`; and append:

```python


def test_a_call_and_a_parameter_call_end_with_their_type_arguments_none_by_default():
    assert [f.name for f in fields(Call)][-1] == "types" == [f.name for f in fields(ParameterCall)][-1]
    assert Call(1, ("a", "b")).types == () == ParameterCall(1, "p", "m").types
```

(c) `tests/modules/spec/application/logic/test_profile_needs.py`: replace
`test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_of_a_call_and_the_tests_a_call_declares`
(lines 129-131) with:

```python
def test_python_supplies_every_fact_a_bundled_check_reads_but_the_tables_and_the_tests_of_a_call_and_its_type_arguments():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {
        fact: EXACT for fact in FACTS if fact not in ("function.tables.call", "test.call", "call.type_arguments")}
```

  and append at the end of the file:

```python


TYPE_ARGUMENT_REFUSED = (
    "layered.yaml: testing.mocks.specs.{index}.type_argument: its check reads call.type_arguments (the type arguments "
    "a call is given), which the language python does not supply: drop testing.mocks.specs.{index}.type_argument, or "
    "check the app with a language whose reader supplies call.type_arguments")


def test_a_mock_spec_by_a_type_argument_needs_the_type_arguments_of_a_call_and_the_other_entries_need_nothing():
    needs = {key.address: key.needs for key in KEYS}
    assert {address: needs[address] for address in (
        "testing.mocks.specs", "testing.mocks.specs[].keyword", "testing.mocks.specs[].position",
        "testing.mocks.specs[].type_argument")} == {
        "testing.mocks.specs": (), "testing.mocks.specs[].keyword": (), "testing.mocks.specs[].position": (),
        "testing.mocks.specs[].type_argument": ("call.type_arguments",)}
    assert FACTS["call.type_arguments"] == "the type arguments a call is given"


def test_a_type_argument_entry_under_python_gets_the_needs_refusal_alone_at_its_index():
    mocks = {"calls": ["unittest.mock.Mock"], "specs": [{"keyword": "spec"}, {"type_argument": 0}]}
    assert problems(layered(testing=FILES | {"mocks": mocks})) == [TYPE_ARGUMENT_REFUSED.format(index=1)]


def test_a_type_argument_entry_of_a_testing_preset_is_refused_at_the_same_index():
    mocks = {"calls": ["unittest.mock.Mock"], "specs": [{"type_argument": 0}]}
    assert problems(layered(testing="typed"), presets={"typed": FILES | {"mocks": mocks}}) == [
        TYPE_ARGUMENT_REFUSED.format(index=0)]


def test_a_type_argument_entry_under_python_with_a_bad_place_gets_the_needs_refusal_and_the_problem_of_its_place():
    mocks = {"calls": ["unittest.mock.Mock"], "specs": [{"type_argument": -1}]}
    assert problems(layered(testing=FILES | {"mocks": mocks})) == [
        TYPE_ARGUMENT_REFUSED.format(index=0),
        "layered.yaml: testing.mocks.specs.0.type_argument: must be a whole number, at least 0, such as 0"]
```

  (`FILES`, `layered`, `problems`, `KEYS`, `FACTS`, `PYTHON`, `EXACT` are already in this file; `problems` defaults to
  `{"python": PYTHON}` from `tests/modules/spec/profiles.py`.)

(d) `tests/modules/spec/domain/test_profile_keys.py`: at the end of
`test_the_ways_a_mock_names_its_spec_are_a_required_list_scope_of_keyword_position_and_type_argument` (added in Task 2)
add the line `    assert NEEDS["testing.mocks.specs[].type_argument"] == ("call.type_arguments",)` (`NEEDS` is already
imported there).

- [ ] **Step 2: Run the tests to see them fail**

Run: `uv run pytest -q -p no:cacheprovider tests/modules/rules/application/logic/test_stand_ins.py tests/modules/rules/domain/test_parsed.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/domain/test_profile_keys.py`
Expected: FAIL — `TypeError: Call.__init__() got an unexpected keyword argument 'types'` in the Brace cases,
`KeyError: 'call.type_arguments'` in the fact tests, and the needs tests getting the unwritten-form problem
(`... does not write \`writing.specs.type_argument\` ...`) instead of the needs refusal.
(`test_a_type_argument_entry_reads_nothing_...` passes already: it pins that a Python call's positional argument is
never read as a type argument.)

- [ ] **Step 3: Give a call its type arguments**

In `xarch/modules/rules/domain/parsed.py`, replace the class `Call` body

```python
    """A call whose callee is a Ref, and the line it is on: its positional arguments and its keyword arguments as
    (name, value), each value a Ref; unpacked is whether it also passes *args or **kwargs."""
    line: int
    func: tuple[str, ...]
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False
```

with

```python
    """A call whose callee is a Ref, and the line it is on: its positional arguments and its keyword arguments as
    (name, value), each value a Ref; unpacked is whether it also passes *args or **kwargs; types are the type
    arguments it is given, in the order written, each a Ref as any name is."""
    line: int
    func: tuple[str, ...]
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False
    types: tuple[Ref, ...] = ()
```

and the class `ParameterCall` body

```python
    """A call of a method of a function's parameter, `<parameter>.<method>(...)`, and the line it is on: the names of
    the parameter and of the method, and the arguments as a Call holds them. Only a parameter its function's
    signature alone binds is read: one the body rebinds, or that is no function's parameter, is not."""
    line: int
    parameter: str
    method: str
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False
```

with

```python
    """A call of a method of a function's parameter, `<parameter>.<method>(...)`, and the line it is on: the names of
    the parameter and of the method, and the arguments and the type arguments as a Call holds them. Only a parameter
    its function's signature alone binds is read: one the body rebinds, or that is no function's parameter, is not."""
    line: int
    parameter: str
    method: str
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False
    types: tuple[Ref, ...] = ()
```

The Python reader (`fs_source_tree.py:1007, 1010`) builds both positionally and sets nothing: do not change its code.
In its module docstring, replace

```
functions. A call form declares no test this reader reads: Python's reader does not supply `test.call`. A file read
with no form holds no test.
```

with

```
functions. A call form declares no test this reader reads: Python's reader does not supply `test.call`. A file read
with no form holds no test. A call holds no type arguments this reader reads: Python's reader does not supply
`call.type_arguments`, and every call's types are empty.
```

- [ ] **Step 4: Read a type argument entry in the check**

In `xarch/modules/rules/application/logic/stand_ins.py`, in `_spec` (written in Task 2), replace the line

```python
        given = made.args if entry.position is not None else ()
```

with

```python
        given = made.args if entry.position is not None else made.types if entry.type_argument is not None else ()
```

and its docstring's `or a positional argument it has at the entry's place` with
`or a positional or a type argument it has at the entry's place`, so that the docstring reads:

```python
    """Whether the call names a spec (or may, when it unpacks arguments), by the first of specs it gives: a keyword it
    is given, or a positional or a type argument it has at the entry's place; the spec (a Ref) and the entry that
    named it, None and None when none did."""
```

- [ ] **Step 5: Add the fact and the need**

In `xarch/profile_values/capabilities.py`, after the line
`    "call": "each call whose callee an import binds, as that dotted path, with its arguments",` add:

```python
    "call.type_arguments": "the type arguments a call is given",
```

In `xarch/modules/spec/domain/key_table.py`, after the NEEDS row
`    "testing.mocks": ("call", "parameter_call", "import.resolved"),` add:

```python
    "testing.mocks.specs[].type_argument": ("call.type_arguments",),
```

Do not add `call.type_arguments` to `python.yaml`'s `supplies`.

- [ ] **Step 6: Run the tests to see them pass**

Run: `uv run pytest -q -p no:cacheprovider tests/modules/rules tests/modules/spec tests/architecture tests/profile_values`
Expected: all pass (the needs walker already reads list entries under `[]`, so no change is needed in
`profile_needs.py`; the 6.11 skip through `unread` already keeps the unwritten-form problem from standing beside the
needs refusal).

Run: `uv run ruff check xarch tests`
Expected: `All checks passed!`

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/modules/rules/application/logic/stand_ins.py \
  xarch/profile_values/capabilities.py xarch/modules/spec/domain/key_table.py xarch/modules/rules/adapters/fs_source_tree.py \
  tests/modules/rules/application/logic/test_stand_ins.py tests/modules/rules/domain/test_parsed.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/domain/test_profile_keys.py
git commit -m "A call holds its type arguments and a type_argument entry of testing.mocks.specs names the spec by them; the entry needs the new fact call.type_arguments, which Python's reader does not supply, so Python refuses it with the needs refusal alone"
```

---

### Task 4: README, CHANGELOG, golden docs, gates

**Files:**
- Modify: `README.md:178-185`
- Modify: `CHANGELOG.md:126` (end of `### Added`), `:325` (end of `### Changed`, before `## [0.2.0]`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: the refusal texts of Tasks 2 and 3.
- Produces: nothing code reads.

- [ ] **Step 1: README**

In `README.md`, replace

```
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call` and `test.call`, so a framework that writes a `call` form under
Python is refused at that entry (`testing.tables.0.call`, `testing.declared.0.call`). A framework declares its tests
```

with

```
runs, and is listed under `approximate` in the enforcement section, which `--strict` fails on. Python's reader
supplies every fact exactly but `function.tables.call`, `test.call` and `call.type_arguments`, so a framework that
writes a `call` form under Python is refused at that entry (`testing.tables.0.call`, `testing.declared.0.call`), and so
is a mock spec by a type argument (`testing.mocks.specs.0.type_argument`). A framework declares its tests
```

and after the line `` test: list it under a `call` form of `testing.declared` ``). `` (the end of the 6.11 sentence,
line 185), insert:

```
`testing.mocks.specs` lists, in order, the ways a call that builds a mock names its spec, each `{keyword: <name>}`,
`{position: <n>}` or `{type_argument: <n>}`: a call names it by the first entry it gives, the fix of a mock with no
spec writes the first entry by the language's `writing.specs`, and an autospec call reads only the first `keyword`
entry. It replaces `spec_keywords` and `spec_position`, each refused with what to write (`unknown key 'spec_keywords':
moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]`). A `type_argument` entry needs `call.type_arguments`,
which Python's reader does not supply.
```

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, after the `### Added` bullet that ends `` form, which refuses the entry already. `xarch profile explain testing.tables.call` says so. `` and before the blank line and `### Changed`, add:

```
- The fact `call.type_arguments`, the type arguments a call is given, which Python's reader does not supply; and the
  language data file's `writing.specs`, one template per way a call that builds a mock names its spec (`keyword`,
  `position`, `type_argument`), from which the stand-ins fixes and the docs write a mock. Python writes `keyword` and
  `position`, so its texts read as before.
```

and at the end of `[Unreleased]`'s `### Changed`, after the bullet that ends
`` `'<entry>' is neither an outside name nor a method: write <entry>() for a method called on anything`. `` and before
the blank line and `## [0.2.0] - 2026-11-18`, add:

```
- `testing.mocks.specs` replaces `testing.mocks.spec_keywords` and `testing.mocks.spec_position`: a list, in order, of
  the ways a call that builds a mock names its spec, each `{keyword: <name>}`, `{position: <n>}` or
  `{type_argument: <n>}`, an entry's problem naming it by its index (`testing.mocks.specs.1.keyword`). A profile or a
  preset writing either old key is refused with `unknown key 'spec_keywords': moved in 0.3.0: write specs: [{keyword:
  spec}, {position: 0}]`. The bundled `pytest` preset writes `specs: [{keyword: spec}, {keyword: spec_set}, {position:
  0}]`: a call giving both a keyword and a first argument now names its spec by the keyword, and a read port named by
  `spec_set=` is shown with `spec_set=`. A `type_argument` entry needs `call.type_arguments`, and an entry of a form the
  language's `writing.specs` does not write is refused at its index.
```

- [ ] **Step 3: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-6-12/regenerate_docs.py` (outside the worktree):

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:
```bash
mkdir -p /tmp/xarch-6-12
uv run python -I /tmp/xarch-6-12/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
```
Expected: `written`; no file under `docs/cli`, `docs/web` or `docs/xarch` listed (only untracked files under
`docs/superpowers` may show); `git diff --stat -- docs` prints nothing. If a golden doc moved, do not hand-edit it:
restore it with `git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 4: Run every gate**

Run:
```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
git diff --quiet 7da5794 -- tests/bootstrap/corpora && echo "corpora unchanged"
timeout 1200 uv run pytest -q -p no:cacheprovider > /tmp/xarch-6-12/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-6-12/suite.log
tail -5 /tmp/xarch-6-12/suite.log
```
Expected: `All checks passed!`; exit 0 for each `xarch` command; `corpora unchanged`; the suite `N passed` with no
failure and last line `exit 0`. Run the suite in the background and read it at the end. A failure in
`tests/bootstrap/test_recorded_corpora.py` means a recorded stand-ins finding moved with the keyword-first order:
stop and report it, do not reorder pytest's list.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say testing.mocks.specs replaces spec_keywords and spec_position, with the refusal, and name call.type_arguments and writing.specs; the golden docs regenerate unchanged"
```

---

## Self-Review

**Spec coverage:**
- B1 (key required, no default, list and entry shapes, value checks, duplicates, `StandIns.specs`, every constructor,
  the shared dicts, the mapping problem): Task 2 Steps 1, 3(c), 5, 7, 9. Spec tests 1-8: Task 2 Step 1(b).
- B2 (`writing.specs` templates, `{before}`, one-pass fill, loader refusals, `WRITING` and docstring, data files,
  unwritten-form refusal and its skip): Task 1 (spec tests 13-16), Task 2 Step 7(b) and Step 1(c) (spec tests 9-10),
  Task 3 Step 1(c) (the skip, spec test 11).
- B3 (`Call.types`, `ParameterCall.types`, reader docstring, `FACTS`, NEEDS, key table scope and keys, `_spec` order,
  autospec rule, fix and read-port texts, docstrings): Task 2 Steps 6, 8 (spec tests 17-20); Task 3 (spec tests 12,
  21-24).
- B4 (retired keys, unknown-key list, needs refusal under Python): Task 2 Step 1(b), 1(d), 1(e), Step 6; Task 3 Step 1(c).
- B5 (`keys.yaml`, docs line, README, CHANGELOG): Task 2 Steps 8(e-g), 9 and Step 1(b) (spec test 25); Task 4.
- Bootstrap and golden docs (spec test 26), gates: Task 2 Step 3(c), Task 4 Steps 3-4.

**Placeholder scan:** no TBD/TODO; every code step shows its code; every command has its expected output.

**Type consistency:** `SpecEntry(keyword: str = "", position: int | None = None, type_argument: int | None = None)`,
`.form`, `.place`, `.written(writing, callee, value)` are used with those names in Tasks 2-3 (`stand_ins.py`,
`docs_template.py`, `profile_checks.py`, tests). `Writing.spec(form, callee, value, keyword, place)` and
`Writing.writes_spec(form)` from Task 1 are what `SpecEntry.written` and `unwritten_specs` call. `StandIns(mocks,
autospec, specs, fixtures)` is built positionally the same in `profile_parsing._mocks`, `builders.PROFILE`, the
bootstrap and adapter tests. `MOCK_SPECS` is the scope constant everywhere.

**Review Focus:** each of the five lines names the step whose test pins it.
<!-- task-pipeline: validated -->
