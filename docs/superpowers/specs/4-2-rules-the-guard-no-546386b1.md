# 4.2 rules: the guard `no-callbacks` replaces the part key `no_callbacks`

Card `546386b1`, subtask of `c34d7f47`, blocked by `7f5fb57d` (4.1, the fact `function.top_level`, done on this
branch). Release step 10 of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`,
below **R3**, section 3, line 273: "The guard `no-callbacks`. | code-shape 2 | Step 1. Before 12.").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Rulings 3 (CS lines 16-17) and 7 (lines 39-40): `no_callbacks` leaves the part and becomes the guard
  `no-callbacks: {parts: [...]}`, taking a list of parts as `guards.pass-through` does, and it keeps failing `check`.
- Ruling 10 (line 47): an old key is refused with a hint from the one retired-keys table, in fixed text.
- Default (lines 66-70): the `no-callbacks` docs line sits among the guard lines (review-2 Q13).
- No compatibility window (lines 72-73).
- Section 4 (lines 645-660): name `no-callbacks`; settings `{parts: [<part>, ...]}`, `parts` required, one or more
  declared parts, plain names, each once, as `guards.pass-through.parts`, through one shared helper; it reads what the
  part key reads today (kind `callback`, keep `annotated-callable`, exempt `receiver`), fails `check`; `NEEDS` moves to
  `guards.no-callbacks`; `ORDER` gains it after `pass-through`; a value `NoCallbacks(parts)`;
  `GuardsView.no_callbacks`; `Part.no_callbacks` goes; the bundled profiles write
  `no-callbacks: {parts: [domain, logic]}`; the recorded finding's key text changes (lines 655-656); `guards off` lists
  it for a profile that leaves it out (lines 658-659); the docs line keeps its text and moves among the guard lines,
  diff read (lines 659-660).
- Section 2.10 (line 441): the refusal `parts.logic: unknown key 'no_callbacks': moved in 0.3.0: write guards:
  {no-callbacks: {parts: [logic, ...]}}; use ...`, and the one wording (lines 443-445).
- Section 5.1 items 1, 2, 3, 6, 7, 8, 14, 15 (lines 666-704), only their `no-callbacks` parts.
- Section 5.3, last bullet (lines 749-750): the guard's docs line, one line moving in each golden copy.
- Section 5.5 (lines 769-785): `(parts.<p>.no_callbacks)` becomes `(guards.no-callbacks)` in the recorded findings;
  lines naming source files stay (line 785).
- Section 6 (lines 786-793): the retired entry for `no_callbacks` on a part; `profile explain` answers from the table.
- Section 7 (lines 825-826): the gates of each step.
- Section 8, `profile-comparison-design.md` (lines 922-924): "`no_callbacks` leaves the list, since a dropped guard
  already shows under `guards off`."
- Dodges (lines 948-975) that apply: accepting the old flat key as an alias or with a warning; regenerating the golden
  docs without reading the diff; editing recorded findings by a blind replace.

R3 rules inherited: **O4**, **O5** (lines 228-229): README and CHANGELOG lines of this step go under `[Unreleased]`;
**O8** (line 232): golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read, never edited by
hand, and move only where the note says (here: the `no-callbacks` line); **O10** (line 234): recorded findings edited
by find and replace reviewed line by line; every other step changes none.

## 1. Goal

A profile says which parts take no callbacks once, among its guards, as it says which parts' methods are listed when
they only forward: `guards: {no-callbacks: {parts: [domain, logic]}}`. The part key `no_callbacks: true` is retired:
a profile writing it is refused at load with a hint that writes the new form. What the check reads, which code it
flags, the finding's sentence, and its failing `check` do not change; only the key address the finding names does.
Because it is now a guard, a profile that leaves it out shows `no-callbacks` under `guards off`.

## 2. Behaviour

### 2.1 The guard's settings

`guards.no-callbacks` takes a mapping with one key, `parts`, required. `parts` is a non-empty list of names of parts
the profile declares, plain names, each listed once. Its parsing is the same as `guards.pass-through`'s, through one
helper both guards call. The refusals, each at load, each with the exit code of any profile that does not load
(file name prefix as for every profile problem):

| Written | Problem |
|---|---|
| `no-callbacks: []` (or any non-mapping, `{}` aside) | `guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: the parts whose functions call none of their parameters annotated as callables` |
| `no-callbacks: {}` | `guards.no-callbacks: missing `parts`` |
| `no-callbacks: {parts: []}` or `{parts: logic}` | `guards.no-callbacks.parts: must be a list of part names` |
| `no-callbacks: {parts: [ghost]}` | `guards.no-callbacks.parts: no part named 'ghost'` |
| `no-callbacks: {parts: [logic, logic]}` | `guards.no-callbacks.parts: 'logic' is listed twice` |
| `no-callbacks: {parts: [logic], also: 1}` | the unknown-key problem every guard gives (`ck.unknown_keys` over the guard's keys), naming `parts` as the known key |

The pass-through refusals keep their exact text (`... the parts whose methods are listed when they only forward`);
the shared helper takes the guard's own phrase. The no-callbacks phrase above is the spec's wording; the plan may
not change it without changing the tests that pin it.

A guard listed with no problem is read into `NoCallbacks(parts)`, `parts` a tuple of the names, in the order written.

### 2.2 What the check does

For each listed part, exactly as for each part with `no_callbacks: true` today: a function of the part's code that
calls one of its own parameters annotated as a callable is a finding of rule `no-callbacks`, which fails `check`
(not only `--strict`). The sentence is unchanged; the key in parentheses at its end becomes `(guards.no-callbacks)`
for every part:

    before: resolve calls its parameter exists: logic/ of modules/rules takes no callback (parts.logic.no_callbacks)
    after:  resolve calls its parameter exists: logic/ of modules/rules takes no callback (guards.no-callbacks)

A profile with no `no-callbacks` guard produces no such finding.

### 2.3 Needs

The guard needs the fact `callback`, as the part key did: `NEEDS` loses `parts.<part>.no_callbacks` and gains
`guards.no-callbacks: ("callback",)`. A language whose reader does not supply `callback` is refused the guard at load
with the one needs text naming `guards.no-callbacks` (and its `drop guards.no-callbacks` advice), as for every other
guard with needs. No entry for `guards.no-callbacks.parts` is added (as `guards.pass-through.parts` has none).

### 2.4 Order and `guards off`

`ORDER` becomes `package-only, scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins,
dead-code, pass-through, no-callbacks, private-imports`. `guards off` in `check`, `check --strict` and
`profile check` (text and JSON) is computed from `ORDER`, so for a profile that writes every other guard and leaves
`no-callbacks` out it lists `no-callbacks`; any list of guards off that includes it shows it between `pass-through`
and `private-imports`. A guard off is a `--strict` finding, as for every guard. `baseline_off` follows the same order.

### 2.5 The retired key

A part writing `no_callbacks` (any value) is refused at load:

    parts.logic: unknown key 'no_callbacks': moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}; use <known part keys>

The hint is the fixed text of one new entry of `RETIRED`:
`Retired(PART, "no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}")`. CS 2.10
(line 441) illustrates the text with `[logic, ...]`; ruling 10 fixes the hint text, and the table carries no
substitution, so the text says `<part>` (as `forbidden`'s entry says `<list>`). The `use ...` list of known part keys
no longer names `no_callbacks`. `no_callbacks` is not accepted as an alias, nor with a warning. `xarch profile
explain no_callbacks` (and `parts.<part>.no_callbacks`, as other retired keys are looked up) answers from the table.
`profile explain guards.no-callbacks` and `guards.no-callbacks.parts` answer from the key catalogue.

### 2.6 The key catalogue

`xarch/architectures/presets/format/keys.yaml` loses `parts.<part>.no_callbacks` and gains `guards.no-callbacks` and
`guards.no-callbacks.parts`, placed after the `guards.pass-through` entries, with the same fields (meaning, accepts,
example) and fragment conventions as those entries. Its meaning says what the part key's entry said (no function of
the listed parts calls one of its own parameters annotated as a callable) and that it fails `check`. The catalogue
tests (every key has an entry and an example; every `NEEDS` address is a key) stay green.

### 2.7 The bundled profiles

`xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml` and `architecture.yaml` each drop `no_callbacks: true`
from parts `domain` and `logic` and write `no-callbacks: {parts: [domain, logic]}` right after `pass-through:` and
before `private-imports:` in `guards:`. `uv run xarch check` and `uv run xarch check --strict` on xarch give the same
findings as before; `guards off` stays empty for them; `profile check architecture.yaml` passes.

### 2.8 Generated docs

The docs line keeps its text exactly:

    - `no-callbacks`: no function of {parts shown} calls a parameter annotated as a callable: it is handed values, never a way to fetch them.

It is no longer a part line; it is a guard line, emitted in the order the profile writes its guards, so in the three
golden copies (`docs/xarch/testing.md:169`, `docs/cli/testing.md:349`, `docs/web/testing.md:350`) it moves to just
after the `pass-through` line and before the `private-imports` line. Each golden copy is regenerated with the repo's
regeneration command and the diff read: it must show that one line moved and nothing else (R3 O8). A profile without
the guard has no such line.

### 2.9 Views and internal values

- `Part.no_callbacks` (spec domain) and `PartView.no_callbacks` (spec contract) go.
- `GuardsView` gains `no_callbacks: tuple[str, ...] = ()`, the parts of the guard (empty when it is off), beside
  `pass_through`.
- The rules adapter builds `Profile.no_callbacks` from `GuardsView.no_callbacks`. `Profile.no_callbacks` keeps its
  name and type; its docstring no longer implies a part key.
- The rule's key string is the constant address `guards.no-callbacks`; the rules key-address list (`expansion.py`
  `KEYS`) names `guards.no-callbacks` in place of `parts.no_callbacks`.
- `profile_keys.py` gains `NO_CALLBACKS = "guard.no-callbacks"` and its address `guards.no-callbacks`.

Unchanged: the rule id `no-callbacks` (`kernel/violations.py`, README id list), the rule book key, `source_check`.

Where each lands (the code that reads or writes the part key today, all of it moves; no leftover reference to
`no_callbacks` as a part field or key remains in `xarch/`, the rule id, the `Profile` field and the source-file names
aside):

- `spec/domain/values.py`: `NoCallbacks(parts)` beside `PassThrough` and in the `Guard` union after `PassThrough`;
  `Part.no_callbacks` and its docstring line go.
- `spec/domain/guards.py`: `KEY[NoCallbacks] = "no-callbacks"`, `ORDER` as 2.4.
- `spec/domain/key_table.py`: `Key(PART, "no_callbacks", ...)` goes; `_guard("no-callbacks")` after
  `_guard("pass-through")`, `NO_CALLBACKS` in `_GUARD_SCOPES`, and `Key(NO_CALLBACKS, "parts", True,
  rules=("no-callbacks",))` after the pass-through `parts` key; `NEEDS` as 2.3.
- `spec/application/logic/profile_parsing.py`: the part-key read of `no_callbacks` goes; `_guards` gains the
  `NoCallbacks` branch; `_pass_through` and the new reader share one helper taking the guard's phrase (2.1).
- `spec/application/services/publishing.py`: `PartView` is built positionally, so its argument list loses
  `part.no_callbacks`; `_guards_view` fills `GuardsView.no_callbacks`.
- `spec/application/logic/docs_template.py`: the part-line block that builds the `no-callbacks` line goes;
  `_guard_line` gains the `NoCallbacks` case with the same text (2.8).

### 2.10 Recorded corpora

- Profiles, edited by hand: `tests/bootstrap/corpora/7cc6111.yaml` and `df537ca.yaml` drop `no_callbacks: true` from
  `domain` and `logic` and write `no-callbacks: {parts: [domain, logic]}` after their `pass-through:` line;
  `stress.yaml` drops it from `domain`, `logic`, `services` and `controller` and writes
  `no-callbacks: {parts: [domain, logic, services, controller]}` after its `pass-through:` block, before
  `private-imports:`. Each lists exactly the parts that carried the flag, so the checker sees the same rules.
- Findings, edited line by line, anchored on the exact strings `(parts.domain.no_callbacks)` and
  `(parts.logic.no_callbacks)`, each replaced by `(guards.no-callbacks)`: `7cc6111.json` 16 lines; `df537ca.json` 0;
  `stress-7cc6111.json.xz` 16 lines (6 domain, 10 logic), decompressed to scratch, edited, recompressed with `xz`, the
  text diff shown. Total 32. CS 5.5 and its table (line 169) say 34 (16/0/18); a fresh count on this branch gives
  16/0/16. The 14 other stress lines with `no_callbacks` name source files (`test_no_callbacks.py`,
  `xarch.modules.rules.application.logic.no_callbacks`) and stay (CS line 785's rule for source-file names). The
  corpus test passing with no other line changed is the proof.

### 2.11 README and CHANGELOG

- README: the part-key shape (line 118) drops `no_callbacks` and the guards shape names `no-callbacks`; the rule
  table row of `no-callbacks` (line 308) names `guards.no-callbacks` as its key; the id list (382) is unchanged.
- CHANGELOG under `## [Unreleased]`, `### Changed`: `no_callbacks` on a part becomes the guard
  `no-callbacks: {parts: [...]}`; a part writing `no_callbacks` is refused with the new form; findings name
  `(guards.no-callbacks)`; `guards off` lists it for a profile that leaves it out; the docs line sits among the guard
  lines.

## 3. Tests

Tiers: **unit** (`tests/modules/...`, `tests/kernel/...`: one function or module, no files, fast), **bootstrap**
(`tests/bootstrap/...`: the bundled profiles, recorded corpora, the CLI end to end, the catalogue against the code),
**architecture** (`tests/architecture/test_self_check.py`: xarch checked by its own profile). Written first, each
seen failing for the right reason.

New or changed, with tier and why:

1. Unit, `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (guard parsing table beside the
   pass-through cases): `{"no-callbacks": {"parts": ["service", "api"]}}` reads into
   `NoCallbacks(("service", "api"))`; each refusal of 2.1 (no map, missing `parts`, empty list, a part not there,
   a part twice, an unknown key) with its exact text. Unit: parsing is a pure function of the profile mapping.
2. Unit, same file: the pass-through refusals keep their exact text (existing cases stay green, guarding the shared
   helper's parameterised phrase).
3. Unit, same file: the list of known guards in the unknown-guard advice (line ~465) names `no-callbacks` between
   `pass-through` and `private-imports`. Unit: the advice comes from `ORDER`/`KEY`.
4. Unit, `test_retired_keys.py`: a part writing `no_callbacks: true` (and `no_callbacks: false`) is refused with
   exactly the text of 2.5; `profile explain no_callbacks` answers the retired text. Unit: the table is data.
5. Unit, the `PART_USE`/`PART_KEYS` strings in `test_profile_parsing.py:165`, `test_profile_parsing_tests.py:301`,
   `test_never_use.py:62`, `test_retired_keys.py:45`, and `tests/bootstrap/test_architecture_files.py:232,238`: drop
   `no_callbacks` from the known part keys. Each edited by hand (dodge: loosening the lists).
6. Unit, `test_profile_parsing_substance.py`: `no_callbacks` leaves the substance tests (the field and the
   "must be true or false" case go); its docstring drops it.
7. Unit, `test_profile_needs.py` and `test_language.py`: a language that does not supply `callback` is refused
   `guards.no-callbacks` with the needs text and `drop guards.no-callbacks`; a profile without the guard is not
   refused. Unit: needs are computed from the parsed profile and the language.
8. Unit, `tests/modules/spec/application/test_origin.py` and `tests/modules/spec/application/origins.py`: `OFF` (and
   any guards-off list) includes `no-callbacks` after `pass-through`. Unit: `guards off` is `ORDER` minus the present.
9. Unit, `tests/modules/spec/application/test_explain.py`: explain of `guards.no-callbacks` and
   `guards.no-callbacks.parts` answers from the catalogue; the Shown row of the rule names `guards.no-callbacks`.
10. Unit, docs template tests (`docs_template` tests, and `tests/bootstrap/test_bundled_guards.py:108/138` for the
    bundled order): the `no-callbacks` line is emitted among the guard lines, after `pass-through`, with the exact
    text of 2.8, and not among the part lines; no line for a profile without the guard.
11. Unit, `tests/modules/rules/adapters/test_spec_profile.py`: `GuardsView(no_callbacks=("logic",))` gives
    `Profile.no_callbacks == ("logic",)`; `PartView` built without the dropped field. Unit: the adapter is a mapping.
12. Unit, `tests/modules/rules/application/logic/test_no_callbacks.py`: the finding ends `(guards.no-callbacks)`;
    the same code is flagged and the same is kept or exempt as before. `test_expansion.py:17,53` and
    `test_expandable.py:17`: the key address `guards.no-callbacks`.
13. Bootstrap, `tests/bootstrap/test_needs_agree.py`: the `EVERY_KEY` profile writes the guard, not the part key;
    every `NEEDS` address is a catalogue key. Bootstrap: it reads the shipped catalogue and the key table together.
14. Bootstrap, `tests/bootstrap/test_bundled_guards.py`: the bundled profiles parse to a `Profile` whose
    `no_callbacks == ("domain", "logic")` and whose guards include `NoCallbacks(("domain", "logic"))`.
15. Bootstrap, the CLI end to end (`test_check_enforcement.py` or beside it): a copy of a bundled profile with
    `no-callbacks` removed shows `guards off: no-callbacks` under `check --strict` and in the JSON `guards_off`;
    the shipped profile shows none. Bootstrap: it runs the real CLI on real profile files.
16. Bootstrap, `tests/bootstrap/test_recorded_corpora.py` (unchanged test, changed data): the three recordings match
    with only the 32 lines of 2.10 changed.
17. Bootstrap, the golden docs test: the three `testing.md` files match after regeneration, with the one moved line.
18. Architecture, `tests/architecture/test_self_check.py`: `guards_off == []` on xarch's own profile (unchanged
    assertion; it fails if `architecture.yaml` is not given the guard).

## 4. Gates

Each passes on this branch alone with the full suite green: `uv run pytest -q` (over two minutes: run it in the
background, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`. No typecheck command exists in this repo.

## 5. Project rules

No comments in xarch's code (docstrings only); tests first; examples simple, with absolute `app.` imports; recorded
corpora edited by hand only, and only as 2.10 says; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.

## 6. Out of scope

- `holds` as a map of kinds, and `names`, `immutable`, `built_by` moving under it (CS 7 step 4, release step 12, card
  4.4), and the needs walker (release step 11).
- The `imports` group on parts and tiers (release steps 13, 14), internal renames (step 15), the profile comparison's
  `_looser` lists (CS 8, `profile-comparison-design.md`; nothing in `looseness.py` names `no_callbacks` today).
- Renaming the rule id, the rule book key, or `Profile.no_callbacks`.
- Historical docs under `docs/superpowers/plans` and `docs/superpowers/specs` that mention `no_callbacks`.
- Any other golden-docs line, any other recorded finding.
