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
