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


---

# 4.2 rules: the guard `no-callbacks` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the part key `no_callbacks: true` with the guard `no-callbacks: {parts: [...]}`, read through one helper shared with `pass-through`, so a profile says once, among its guards, which parts take no callbacks; the old key is refused with the retired-keys hint, findings name `(guards.no-callbacks)`, and `guards off` lists it when left out.

**Architecture:** Spec reads the guard into a new value `NoCallbacks(parts)` (domain `values.py`, `guards.py` `KEY`/`ORDER`), its keys live in the key table (`key_table.py`, new scope `NO_CALLBACKS` in `profile_keys.py`) and the format's catalogue (`keys.yaml`), and the part key becomes one `RETIRED` entry. Spec publishes the parts in `GuardsView.no_callbacks`; rules' adapter fills the unchanged `Profile.no_callbacks` from it, and the rule's key text becomes the constant `guards.no-callbacks`. The docs line moves from `_part_lines` to `_guard_line`.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/4-2-rules-the-guard-no-546386b1.md` (prepended above).

## Global Constraints

- Guard name `no-callbacks`; settings `{parts: [<part>, ...]}`, `parts` required, a non-empty list of declared part names, each once; parsed by one helper shared with `guards.pass-through`.
- Refusal texts (after the `layered.yaml: ` file prefix): `guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: the parts whose functions call none of their parameters annotated as callables`; `guards.no-callbacks: missing `parts``; `guards.no-callbacks.parts: must be a list of part names`; `guards.no-callbacks.parts: no part named 'ghost'`; `guards.no-callbacks.parts: 'logic' is listed twice`; `guards.no-callbacks: unknown key 'also': use parts`.
- The pass-through refusals keep their exact text (`... the parts whose methods are listed when they only forward`).
- Retired entry: `Retired(PART, "no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}")`; no alias, no warning.
- `ORDER = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins", "dead-code", "pass-through", "no-callbacks", "private-imports")`.
- `NEEDS["guards.no-callbacks"] == ("callback",)`; no `NEEDS` entry for `guards.no-callbacks.parts`; `parts.<part>.no_callbacks` leaves `NEEDS`.
- `profile_keys.NO_CALLBACKS = "guard.no-callbacks"`, address `guards.no-callbacks`.
- Finding text: `<function> calls its parameter <name>: <where> takes no callback (guards.no-callbacks)`; rule id `no-callbacks` unchanged; still a violation (fails `check`, not only `--strict`).
- Docs line text unchanged: `` `no-callbacks`: no function of {parts shown} calls a parameter annotated as a callable: it is handed values, never a way to fetch them. ``, emitted as a guard line in the order the profile writes its guards.
- `GuardsView.no_callbacks: tuple[str, ...] = ()`; `Part.no_callbacks` and `PartView.no_callbacks` go; `Profile.no_callbacks` keeps its name and type.
- Bundled profiles and `architecture.yaml` write `  no-callbacks: {parts: [domain, logic]}` right after their `pass-through:` line.
- Recorded findings: exactly 32 lines change (`7cc6111.json` 16, `df537ca.json` 0, `stress-7cc6111.json.xz` 16), anchored on `(parts.domain.no_callbacks)` / `(parts.logic.no_callbacks)`; no other line.
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated, never hand-edited; diff read: one moved line per file, nothing else.
- No comments in xarch's code (docstrings only). `.claude/` stays out of commits; nothing is pushed.
- Commit messages: one long sentence saying what changed, as `git log` shows, then `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Gates: `uv run pytest -q` (in the background, read at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

### Two readings of the spec fixed here

- Spec §3 item 3 says the unknown-guard advice names `no-callbacks` "between `pass-through` and `private-imports`". The advice is `ck.advice`, which **sorts** the known names (`profile_checks.py:566-570`), so the new name lands between `dead-code` and `no-comments`. The tests pin the sorted list; `ORDER` (and so `guards off`) has it after `pass-through`.
- Spec §2.5 says `xarch profile explain no_callbacks` "answers from the table … as other retired keys are looked up". The lookup (`key_lookup.retired_at`) matches a part key only as `parts.no_callbacks` or `parts.<part>.no_callbacks`; a bare part-key name matches nothing (pinned today by `test_an_address_that_is_no_entry_gives_nothing`, id "the name at the top of the file"). The plan keeps that rule: both part addresses give the retired text, and the bare name is an unknown key whose `nearest` names `guards.no-callbacks`.

## Review Focus

- `no-callbacks:` written with no value (YAML null) must be refused with the "must be a mapping" text, not accepted as `{}` the way `no-duplicates:` is. Pinned in Task 1 Step 1 (`test_profile_parsing_tests.py`, id "no-callbacks, no value").
- A profile that writes the new guard but forgot to drop `no_callbacks: true` on a part gets exactly one problem, the retired key's, and nothing else (no needs problem, no duplicate). Pinned in Task 1 Step 2 (`test_retired_keys.py`).
- A person typing the old address into `xarch profile explain` (`parts.no_callbacks`, `parts.<part>.no_callbacks`, bare `no_callbacks`) is pointed at `guards.no-callbacks`. Pinned in Task 1 Step 4 (`test_explain.py`).
- The docs line follows the order the profile writes its guards, not `ORDER`: written before `pass-through`, it comes before it. Pinned in Task 1 Step 5 (`test_docs_template.py`).
- Every listed part's finding names the same key, `(guards.no-callbacks)`, never the part's address. Pinned in Task 2 Step 1 (`test_no_callbacks.py`, two parts listed).

---

## File Structure

- Modify `xarch/modules/spec/domain/values.py`: `NoCallbacks`, `Guard` union; `Part.no_callbacks` goes.
- Modify `xarch/modules/spec/domain/guards.py`: `KEY`, `ORDER`.
- Modify `xarch/modules/spec/domain/profile_keys.py`: `NO_CALLBACKS`, `SCOPES`, `RETIRED`.
- Modify `xarch/modules/spec/domain/key_table.py`: guard keys, part key goes, `NEEDS`.
- Modify `xarch/architectures/presets/format/keys.yaml`: catalogue entries.
- Modify `xarch/modules/spec/application/logic/profile_parsing.py`: shared helper `_listed_parts`, `NoCallbacks` branch, part-key read goes.
- Modify `xarch/modules/spec/contract/__init__.py`: `PartView`, `GuardsView`.
- Modify `xarch/modules/spec/application/services/publishing.py`: `PartView` args, `_guards_view`.
- Modify `xarch/modules/spec/application/logic/docs_template.py`: part line goes, guard line comes.
- Modify `xarch/modules/rules/adapters/spec_profile.py`, `xarch/modules/rules/domain/profile.py` (docstring), `xarch/modules/rules/application/logic/expansion.py` (key text, `KEYS`).
- Modify profiles: `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/{7cc6111,df537ca,stress}.yaml`.
- Modify recorded findings: `tests/bootstrap/corpora/7cc6111.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz`.
- Modify `README.md`, `CHANGELOG.md`; regenerate `docs/{cli,web,xarch}/testing.md`.
- Tests: listed per task.

Why three tasks: the shipped profiles write the part key, and adding `no-callbacks` to `ORDER` changes `guards off` for them, so the spec side, the adapter, the docs line and every profile must move together to keep the suite green (Task 1). The finding's key text and the recorded findings move together (Task 2). README, CHANGELOG and the closing gates (Task 3). The golden docs are compared by tests, so they regenerate in Task 1 with the docs line.

---

### Task 1: Spec reads the guard `no-callbacks` and retires the part key; the profiles, the adapter and the docs line move with it

**Files:**
- Modify: `xarch/modules/spec/domain/values.py:73-108` (`Part`), `:295-302` (`PassThrough`, `Guard`)
- Modify: `xarch/modules/spec/domain/guards.py`
- Modify: `xarch/modules/spec/domain/profile_keys.py:30`, `:57`, `:158-167`
- Modify: `xarch/modules/spec/domain/key_table.py:8-40`, `:42-43`, `:77`, `:131-140`, `:166`, `:200`, `:226`
- Modify: `xarch/architectures/presets/format/keys.yaml:378-388`, `:901-916`, `:1041-1049`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:88-135`, `:706-745`, `:842-877`, `:937-949`
- Modify: `xarch/modules/spec/contract/__init__.py:92-141`
- Modify: `xarch/modules/spec/application/services/publishing.py:22-32`, `:57-61`, `:92-109`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:63-81`, `:531-546`, `:579-582`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:79`, `xarch/modules/rules/domain/profile.py:64-65`
- Regenerate (never hand-edit): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Modify: `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`, `tests/bootstrap/corpora/stress.yaml`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, `tests/modules/spec/domain/test_values.py`, `tests/modules/spec/application/logic/test_libraries_and_guards.py`, `tests/modules/spec/application/logic/test_retired_keys.py`, `tests/modules/spec/application/logic/test_profile_parsing.py`, `tests/modules/spec/application/logic/test_never_use.py`, `tests/bootstrap/test_architecture_files.py`, `tests/modules/spec/application/logic/test_profile_parsing_substance.py`, `tests/modules/spec/application/logic/test_profile_needs.py`, `tests/modules/spec/application/test_language.py`, `tests/modules/spec/application/origins.py`, `tests/modules/spec/application/test_check.py`, `tests/modules/spec/application/test_explain.py`, `tests/modules/spec/application/test_profile.py`, `tests/modules/spec/application/logic/test_docs_template.py`, `tests/modules/rules/adapters/test_spec_profile.py`, `tests/bootstrap/test_bundled_guards.py`, `tests/bootstrap/test_check_enforcement.py`, `tests/bootstrap/test_needs_agree.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces:
  - `xarch.modules.spec.domain.values.NoCallbacks` — `@dataclass(frozen=True)`, one field `parts: tuple[str, ...]`; in the `Guard` union after `PassThrough`.
  - `xarch.modules.spec.domain.guards.KEY[NoCallbacks] == "no-callbacks"`; `ORDER` as in Global Constraints.
  - `xarch.modules.spec.domain.profile_keys.NO_CALLBACKS == "guard.no-callbacks"`; `SCOPES[NO_CALLBACKS] == "guards.no-callbacks"`.
  - `xarch.modules.spec.contract.GuardsView.no_callbacks: tuple[str, ...] = ()`.
  - `Part` and `PartView` no longer have `no_callbacks`.
  - The rule's key text is still `parts.<part>.no_callbacks` at the end of this task (Task 2 changes it), so no recorded finding moves here.

- [ ] **Step 1: Write the failing parsing and guard-order tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

(a) In the import block from `xarch.modules.spec.domain.values`, add `NoCallbacks,` in its alphabetical place: replace

```python
    DeadCode,
    NoComments,
```

with

```python
    DeadCode,
    NoCallbacks,
    NoComments,
```

(b) Replace the unknown-guard case (lines 464-466):

```python
    pytest.param({"colour": {}}, ["layered.yaml: guards: unknown guard 'colour': use closed-tree, dead-code, "
                                  "no-comments, no-duplicates, no-twins, pass-through, private-imports, "
                                  "scenario-coverage, stand-ins"],
```

with

```python
    pytest.param({"colour": {}}, ["layered.yaml: guards: unknown guard 'colour': use closed-tree, dead-code, "
                                  "no-callbacks, no-comments, no-duplicates, no-twins, pass-through, private-imports, "
                                  "scenario-coverage, stand-ins"],
```

(c) Directly after `test_the_new_guards_take_their_parameters_and_dead_code_needs_fakes` (it ends with `NoTwins(translated=("store", "api")),)`), add:

```python
def test_no_callbacks_takes_the_parts_it_reads_in_the_order_written():
    assert parsed(covered(guards={"no-callbacks": {"parts": ["service", "api"]}})).guards == (
        NoCallbacks(("service", "api")),)
    assert parsed(covered(guards={"pass-through": {"parts": ["api"]}, "no-callbacks": {"parts": ["service"]}})).guards \
        == (PassThrough(("api",)), NoCallbacks(("service",)))
```

(d) In the parametrize list of `test_a_bad_new_guard_is_refused`, after the last pass-through case (`id="pass-through, a part that is not there"),`), add:

```python
    pytest.param({"no-callbacks": []}, ["layered.yaml: guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: "
                                        "the parts whose functions call none of their parameters annotated as callables"],
                 id="no-callbacks, no map"),
    pytest.param({"no-callbacks": None}, ["layered.yaml: guards.no-callbacks: must be a mapping {parts: [<part>, ...]}: "
                                          "the parts whose functions call none of their parameters annotated as "
                                          "callables"],
                 id="no-callbacks, no value"),
    pytest.param({"no-callbacks": {}}, ["layered.yaml: guards.no-callbacks: missing `parts`"],
                 id="no-callbacks, no parts"),
    pytest.param({"no-callbacks": {"parts": []}}, ["layered.yaml: guards.no-callbacks.parts: must be a list of part "
                                                   "names"], id="no-callbacks, an empty list"),
    pytest.param({"no-callbacks": {"parts": "service"}}, ["layered.yaml: guards.no-callbacks.parts: must be a list of "
                                                          "part names"], id="no-callbacks, a name and no list"),
    pytest.param({"no-callbacks": {"parts": ["ghost"]}}, ["layered.yaml: guards.no-callbacks.parts: no part named "
                                                          "'ghost'"], id="no-callbacks, a part that is not there"),
    pytest.param({"no-callbacks": {"parts": ["service", "service"]}},
                 ["layered.yaml: guards.no-callbacks.parts: 'service' is listed twice"], id="no-callbacks, a part twice"),
    pytest.param({"no-callbacks": {"parts": ["service"], "also": 1}},
                 ["layered.yaml: guards.no-callbacks: unknown key 'also': use parts"], id="no-callbacks, an unknown key"),
```

In `tests/modules/spec/domain/test_values.py`, add `NoCallbacks,` to the import from `xarch.modules.spec.domain.values` (between `DeadCode,` and `NoComments,`), and replace

```python
    guards = (PackageOnly, ScenarioCoverage, NoComments, StandIns, ClosedTree, NoDuplicates, NoTwins, DeadCode,
              PassThrough, PrivateImports)
```

with

```python
    guards = (PackageOnly, ScenarioCoverage, NoComments, StandIns, ClosedTree, NoDuplicates, NoTwins, DeadCode,
              PassThrough, NoCallbacks, PrivateImports)
```

In `tests/modules/spec/application/logic/test_libraries_and_guards.py`, replace

```python
    assert list(ORDER) == ["package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates",
                             "no-twins", "dead-code", "pass-through", "private-imports"]
```

with

```python
    assert list(ORDER) == ["package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates",
                             "no-twins", "dead-code", "pass-through", "no-callbacks", "private-imports"]
```

- [ ] **Step 2: Write the failing retired-key tests and drop `no_callbacks` from the known part keys**

Drop `no_callbacks` from every list of known part keys (six lines, each the exact text `names, no_callbacks, `):

```bash
sed -i 's/names, no_callbacks, /names, /' \
  tests/modules/spec/application/logic/test_profile_parsing.py \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_never_use.py \
  tests/modules/spec/application/logic/test_retired_keys.py \
  tests/bootstrap/test_architecture_files.py
git diff --numstat -- tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_never_use.py tests/bootstrap/test_architecture_files.py
grep -rn "no_callbacks" tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_never_use.py tests/bootstrap/test_architecture_files.py
```

Expected: `1 1` for the first two files, `2 2` for `test_architecture_files.py`; the `grep` prints nothing. Read the diff: each line lost exactly `no_callbacks, ` and nothing else.

In `tests/modules/spec/application/logic/test_retired_keys.py`:

(a) Add `NO_CALLBACKS,` to the `profile_keys` import, between `NAMING,` and `NO_DUPLICATES,`.

(b) Replace the `GUARD_USE` line:

```python
GUARD_USE = ("closed-tree, dead-code, no-comments, no-duplicates, no-twins, pass-through, private-imports, "
             "scenario-coverage, stand-ins")
```

with

```python
GUARD_USE = ("closed-tree, dead-code, no-callbacks, no-comments, no-duplicates, no-twins, pass-through, "
             "private-imports, scenario-coverage, stand-ins")
```

(c) After `SWITCH_OUTSIDE = "a key of uses: write uses: {apply_never: true}"`, add:

```python
CALLBACKS_MOVED = "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}"
```

(d) In `test_the_shipped_table_answers_each_name_in_its_scope`'s list, after `pytest.param(TIER, "apply_never", SWITCH_OUTSIDE, id="apply_never on a tier"),`, add:

```python
    pytest.param(PART, "no_callbacks", CALLBACKS_MOVED, id="the part key no_callbacks"),
    pytest.param(GUARD, "no-callbacks", "", id="the guard no-callbacks, which xarch has"),
```

(e) In `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`'s list, after `pytest.param("tiers.apply_never", SWITCH_OUTSIDE, id="tiers.apply_never"),`, add:

```python
    pytest.param("parts.no_callbacks", CALLBACKS_MOVED, id="parts.no_callbacks"),
    pytest.param("parts.<part>.no_callbacks", CALLBACKS_MOVED, id="parts.<part>.no_callbacks"),
    pytest.param("guards.no-callbacks", "", id="guards.no-callbacks"),
```

(f) In `test_every_other_mapping_reads_the_entries_of_its_own_scope`'s list, after the `PASS_THROUGH` case (`"guards.pass-through: unknown key 'banned'", id="pass-through"),`), add:

```python
    pytest.param(NO_CALLBACKS, writing(layered(guards={"no-callbacks": {"parts": ["api"]}}), "guards", "no-callbacks"),
                 "guards.no-callbacks: unknown key 'banned'", id="no-callbacks"),
```

(g) After `test_the_shipped_table_changes_no_message`, add:

```python
@pytest.mark.parametrize("value", [True, False], ids=["true", "false"])
def test_a_part_writing_no_callbacks_is_refused_with_the_guard_that_replaces_it(value):
    document = layered()
    document["parts"]["service"]["no_callbacks"] = value
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'no_callbacks': {CALLBACKS_MOVED}; use {PART_USE}"]


def test_a_part_writing_no_callbacks_beside_the_guard_gets_only_the_retired_key_s_problem():
    document = layered(guards={"no-callbacks": {"parts": ["service"]}})
    document["parts"]["service"]["no_callbacks"] = True
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'no_callbacks': {CALLBACKS_MOVED}; use {PART_USE}"]
```

- [ ] **Step 3: Write the failing substance, needs and language tests**

In `tests/modules/spec/application/logic/test_profile_parsing_substance.py`:

(a) In the module docstring, replace `types_only, no_callbacks, names, built_by)` with `types_only, names, built_by)`.

(b) Replace the two tests

```python
def test_a_part_says_what_its_files_hold_and_how_its_classes_are_named_and_built():
    part = parsed(with_part(holds="classes", names="*Service", built_by=["api"], no_callbacks=True,
                            types_only=["store"])).parts["service"]
    assert (part.holds, part.names, part.built_by, part.no_callbacks, part.types_only) == (
        "classes", ("*Service",), ("api",), True, ("store",))


def test_the_keys_are_off_when_left_out():
    part = parsed(layered()).parts["service"]
    assert (part.holds, part.names, part.built_by, part.no_callbacks, part.types_only) == ("", (), (), False, ())
```

with

```python
def test_a_part_says_what_its_files_hold_and_how_its_classes_are_named_and_built():
    part = parsed(with_part(holds="classes", names="*Service", built_by=["api"], types_only=["store"])).parts["service"]
    assert (part.holds, part.names, part.built_by, part.types_only) == ("classes", ("*Service",), ("api",), ("store",))
    assert not hasattr(part, "no_callbacks")


def test_the_keys_are_off_when_left_out():
    part = parsed(layered()).parts["service"]
    assert (part.holds, part.names, part.built_by, part.types_only) == ("", (), (), ())
```

(c) Delete the parametrize case

```python
    pytest.param({"no_callbacks": "yes"}, "parts.service.no_callbacks: must be true or false",
                 id="no_callbacks, no boolean"),
```

In `tests/modules/spec/application/logic/test_profile_needs.py`, replace

```python
def test_a_key_whose_check_reads_a_fact_the_language_does_not_supply_is_refused_naming_key_fact_and_what_to_do():
    assert problems(services(no_callbacks=True), languages=LANGUAGES) == [
        "layered.yaml: parts.service.no_callbacks: its check reads callback (each call of a function's own parameter, "
        "whether it is the receiver and whether it is annotated as a callable), which the language toy does not "
        "supply: drop parts.service.no_callbacks, or check the app with a language whose reader supplies callback"]


def test_a_key_set_to_false_configures_no_check_and_needs_nothing():
    assert parsed(services(no_callbacks=False), languages=LANGUAGES).approximate == ()
```

with

```python
def test_a_key_whose_check_reads_a_fact_the_language_does_not_supply_is_refused_naming_key_fact_and_what_to_do():
    assert problems(layered(language="toy", guards={"no-callbacks": {"parts": ["service"]}}), languages=LANGUAGES) == [
        "layered.yaml: guards.no-callbacks: its check reads callback (each call of a function's own parameter, "
        "whether it is the receiver and whether it is annotated as a callable), which the language toy does not "
        "supply: drop guards.no-callbacks, or check the app with a language whose reader supplies callback"]


def test_a_profile_without_the_guard_no_callbacks_needs_no_callback():
    assert parsed(layered(language="toy"), languages=LANGUAGES).approximate == ()


def test_callback_is_needed_by_the_guard_no_callbacks_alone():
    assert [key.address for key in KEYS if "callback" in key.needs] == ["guards.no-callbacks"]


def test_a_key_set_to_false_configures_no_check_and_needs_nothing():
    assert parsed(services(immutable=False), languages=LANGUAGES).approximate == ()
```

and replace

```python
    assert parsed(services(no_callbacks=True), languages={"toy": silent}).approximate == ()
```

with

```python
    assert parsed(layered(language="toy", guards={"no-callbacks": {"parts": ["service"]}}),
                  languages={"toy": silent}).approximate == ()
```

(`services(immutable=True)` is refused under toy, which does not supply `class.immutable`, so `False` loading is a real test of "set to false needs nothing".)

In `tests/modules/spec/application/test_language.py`, replace

```python
    named = BASE | {"language": "toy", "parts": {"core": {"path": "core", "role": "r", "names": "*Rule",
                                                          "no_callbacks": True}}}
    spec, _ = spec_controller({"base": named}, languages={"toy": TOY}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert [problem.text for problem in checked.problems] == [
        "base: parts.core.no_callbacks: its check reads callback (each call of a function's own parameter, whether it "
        "is the receiver and whether it is annotated as a callable), which the language toy does not supply: drop "
        "parts.core.no_callbacks, or check the app with a language whose reader supplies callback"]
    spec, _ = spec_controller({"base": named | {"parts": {"core": {"path": "core", "role": "r", "names": "*Rule"}}}},
                              languages={"toy": TOY}, runtime=RUNTIME)
```

with

```python
    named = BASE | {"language": "toy", "parts": {"core": {"path": "core", "role": "r", "names": "*Rule"}},
                    "guards": {"no-callbacks": {"parts": ["core"]}}}
    spec, _ = spec_controller({"base": named}, languages={"toy": TOY}, runtime=RUNTIME)
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert [problem.text for problem in checked.problems] == [
        "base: guards.no-callbacks: its check reads callback (each call of a function's own parameter, whether it "
        "is the receiver and whether it is annotated as a callable), which the language toy does not supply: drop "
        "guards.no-callbacks, or check the app with a language whose reader supplies callback"]
    spec, _ = spec_controller({"base": {key: value for key, value in named.items() if key != "guards"}},
                              languages={"toy": TOY}, runtime=RUNTIME)
```

- [ ] **Step 4: Write the failing `guards off`, explain and published-view tests**

In `tests/modules/spec/application/origins.py`, replace

```python
OFF = ("package-only", "scenario-coverage", "stand-ins", "closed-tree", "no-duplicates", "no-twins", "dead-code",
       "pass-through", "private-imports")
```

with

```python
OFF = ("package-only", "scenario-coverage", "stand-ins", "closed-tree", "no-duplicates", "no-twins", "dead-code",
       "pass-through", "no-callbacks", "private-imports")
```

In `tests/modules/spec/application/test_check.py`, replace

```python
OFF = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins",
       "dead-code", "pass-through", "private-imports")
```

with

```python
OFF = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins",
       "dead-code", "pass-through", "no-callbacks", "private-imports")
```

In `tests/modules/spec/application/test_explain.py`:

(a) In `SHAPE`, delete the line

```python
    Shown('parts.no_callbacks', 1, 'its code calls none of its own parameters', False, True),
```

and after `Shown('guards.pass-through', 1, 'a method that only forwards is listed', False, True),` add

```python
    Shown('guards.no-callbacks', 1, 'no function of the parts calls a parameter annotated as a callable', False, True),
```

(b) In `test_a_key_that_configures_a_check_names_the_facts_it_reads_as_the_default_language_supplies_them`, replace `found = explained("parts.no_callbacks")` with `found = explained("guards.no-callbacks")`.

(c) In `test_a_fact_the_default_language_does_not_grade_is_said_to_be_absent`, replace `assert spec.explain(Explain("parts.no_callbacks")).needs == (Need("callback", FACTS["callback"]),)` with `assert spec.explain(Explain("guards.no-callbacks")).needs == (Need("callback", FACTS["callback"]),)`.

(d) After `test_the_part_key_xarch_renamed_is_refused_with_the_fixed_text_however_it_is_typed`, add:

```python
def test_the_guard_no_callbacks_and_its_parts_are_keys_of_the_format_and_the_guard_needs_callback():
    guard, listed = explained("guards.no-callbacks"), explained("guards.no-callbacks.parts")
    assert (guard.key, guard.where, guard.meaning, guard.required, guard.rules) == (
        "guards.no-callbacks", "guards", "no function of the parts calls a parameter annotated as a callable", False,
        ("no-callbacks",))
    assert guard.needs == (Need("callback", FACTS["callback"], Supply("callback", EXACT)),)
    assert [shown.key for shown in guard.keys] == ["guards.no-callbacks.parts"]
    assert "parts: [documents]" in guard.example
    assert (listed.key, listed.where, listed.required, listed.rules, listed.needs) == (
        "guards.no-callbacks.parts", "guards.no-callbacks", True, ("no-callbacks",), ())


def test_the_part_key_no_callbacks_is_refused_with_the_fixed_text_and_points_to_the_guard():
    for address in ("parts.no_callbacks", "parts.<part>.no_callbacks"):
        found = explained(address)
        assert isinstance(found, UnknownKey)
        assert (found.key, found.retired) == (
            "parts.no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}")
        assert "guards.no-callbacks" in found.nearest
    bare = explained("no_callbacks")
    assert isinstance(bare, UnknownKey) and "guards.no-callbacks" in bare.nearest
```

In `tests/modules/spec/application/test_profile.py`, append:

```python
def test_the_parts_the_guard_no_callbacks_lists_reach_the_checks_and_no_part_carries_the_key():
    listed = {**LAYERED, "guards": {"no-callbacks": {"parts": ["src"]}}}
    view = controller(FakeArchitectureFiles({"listed": listed})).profile("listed")
    assert isinstance(view, ProfileView)
    assert view.guards == GuardsView(no_callbacks=("src",))
    assert not hasattr(view.parts[0], "no_callbacks")
```

- [ ] **Step 5: Write the failing docs-template tests**

In `tests/modules/spec/application/logic/test_docs_template.py`, after `test_a_shared_part_is_said_in_the_guards`, add:

```python
CALLBACKS = ("- `no-callbacks`: no function of `store/` and `service/` calls a parameter annotated as a callable: it is "
             "handed values, never a way to fetch them.")
PRIVATE = ("- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file "
           "of them.")


def test_the_no_callbacks_line_is_a_guard_line_after_the_part_lines():
    lines = filled("{{guards}}", parts=parts(service={"holds": "functions"}),
                   guards={"no-callbacks": {"parts": ["store", "service"]}, "private-imports": {}}).splitlines()
    assert lines[-2:] == [CALLBACKS, PRIVATE]
    assert [line for line in lines if "`no-callbacks`" in line] == [CALLBACKS]


def test_the_no_callbacks_line_follows_the_order_the_profile_writes_its_guards_in():
    lines = filled("{{guards}}", guards={"no-callbacks": {"parts": ["store", "service"]},
                                         "pass-through": {"parts": ["service"]}}).splitlines()
    assert [line.split(":")[0] for line in lines[-2:]] == ["- `no-callbacks`", "- `pass-through`"]


def test_a_profile_without_the_guard_has_no_no_callbacks_line():
    assert "`no-callbacks`" not in filled("{{guards}}", guards={"private-imports": {}})
```

(The third test passes before the change too; it guards the "no line without the guard" rule against the move.)

- [ ] **Step 6: Write the failing adapter test**

In `tests/modules/rules/adapters/test_spec_profile.py`, in `VIEW`, replace

```python
                    holds="functions", no_callbacks=True, shared=2, immutable=True),
```

with

```python
                    holds="functions", shared=2, immutable=True),
```

and replace

```python
                      tests_only_known=("api/x.py:run",), pass_through=("api",), private_imports=True),
```

with

```python
                      tests_only_known=("api/x.py:run",), pass_through=("api",), no_callbacks=("core",),
                      private_imports=True),
```

The expected `Profile` in `test_the_profile_view_becomes_the_profile_the_checks_see` keeps `no_callbacks=("core",)` unchanged: the adapter now takes it from the guards.

- [ ] **Step 7: Write the failing bootstrap tests and move the bootstrap profile to the guard**

In `tests/bootstrap/test_bundled_guards.py`:

(a) Add the import `from xarch.modules.spec.domain.values import NoCallbacks` after `from xarch.modules.spec.contract import GuardsView`.

(b) In `test_the_bundled_profiles_use_every_guard_of_their_own`, replace

```python
        pass_through=("services", "controller", "adapters"),
        private_imports=True)
```

with

```python
        pass_through=("services", "controller", "adapters"), no_callbacks=("domain", "logic"),
        private_imports=True)
```

(c) After that test, add (`isinstance` only: the wired tier uses `domain/` as a type):

```python
@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_write_no_callbacks_as_a_guard_of_domain_and_logic(name):
    architecture = load_architecture(name)
    assert [guard.parts for guard in architecture.guards if isinstance(guard, NoCallbacks)] == [("domain", "logic")]
    assert not any(hasattr(part, "no_callbacks") for part in architecture.parts.values())
```

(d) In `test_the_testing_doc_writes_a_line_per_derived_check_and_per_guard`, delete the two lines

```python
        "- `no-callbacks`: no function of `domain/` and `application/logic/` calls a parameter annotated as a "
        "callable: it is handed values, never a way to fetch them.",
```

and insert them directly after the pass-through entry, so that part of the list reads:

```python
        "- `pass-through`: a method of `application/services/`, `application/controller.py` and `adapters/` whose "
        "whole body forwards to one call on a collaborator, or returns an attribute of what that call answers, is "
        "listed in the enforcement section, and fails `check --strict` only.",
        "- `no-callbacks`: no function of `domain/` and `application/logic/` calls a parameter annotated as a "
        "callable: it is handed values, never a way to fetch them.",
        "- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file "
        "of them.",
```

In `tests/bootstrap/test_check_enforcement.py`, after `test_a_custom_copy_of_a_bundled_profile_is_compared_with_it`, add:

```python
def test_a_copy_of_a_bundled_profile_that_leaves_no_callbacks_out_shows_it_off_and_fails_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    assert "  no-callbacks: {parts: [domain, logic]}\n" in text
    (tmp_path / "arch/mine.yaml").write_text(text.replace("  no-callbacks: {parts: [domain, logic]}\n", ""))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:4] == [
        "  profile:     arch/mine.yaml (custom; closest bundled: web)",
        "    guards off:  no-callbacks"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-callbacks"]
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert (profile["guards_off"], profile["baseline_off"]) == (["no-callbacks"], [])
```

In `tests/bootstrap/test_needs_agree.py`'s `EVERY_KEY`, delete the line `    no_callbacks: true` (under part `core`), and replace

```
  pass-through: {parts: [core]}
  private-imports: {}
```

with

```
  pass-through: {parts: [core]}
  no-callbacks: {parts: [core]}
  private-imports: {}
```

- [ ] **Step 8: Run the new tests to see them fail for the right reasons**

Run:

```bash
timeout 900 uv run pytest -q \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/domain/test_values.py \
  tests/modules/spec/application/logic/test_libraries_and_guards.py tests/modules/spec/application/logic/test_retired_keys.py \
  tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_never_use.py \
  tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/modules/spec/application/test_language.py tests/modules/spec/application/test_origin.py \
  tests/modules/spec/application/test_check.py tests/modules/spec/application/test_explain.py \
  tests/modules/spec/application/test_profile.py tests/modules/spec/application/logic/test_docs_template.py \
  tests/modules/rules/adapters/test_spec_profile.py tests/bootstrap/test_bundled_guards.py \
  tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_architecture_files.py 2>&1 | tail -40
```

Expected: collection ERRORS for the files importing `NoCallbacks` / `NO_CALLBACKS` (`ImportError: cannot import name 'NoCallbacks'` / `'NO_CALLBACKS'`), and FAILURES elsewhere for these reasons: `unknown guard 'no-callbacks'` where a test writes the guard; the known-part-keys lists still naming `no_callbacks`; `ORDER`/`OFF` lacking `no-callbacks`; `GuardsView.__init__() got an unexpected keyword argument 'no_callbacks'`; `hasattr(part, "no_callbacks")` true; the bundled `web.yaml` not holding the guard line. `test_a_profile_without_the_guard_has_no_no_callbacks_line` passes. No failure of another kind (a typo'd name, a syntax error) should appear; fix the test if one does.

- [ ] **Step 9: The guard's value, name, order, scope and retired entry**

In `xarch/modules/spec/domain/values.py`:

(a) In `Part`'s docstring, delete the line `    no_callbacks: no function of it calls one of its own parameters`, and delete the field line `    no_callbacks: bool = False`.

(b) Replace

```python
@dataclass(frozen=True)
class PassThrough:
    """The guard pass-through: the parts whose methods that only forward are listed."""
    parts: tuple[str, ...]


Guard = (PackageOnly | ScenarioCoverage | NoComments | StandIns | ClosedTree | NoDuplicates | NoTwins | DeadCode
         | PassThrough | PrivateImports)
```

with

```python
@dataclass(frozen=True)
class PassThrough:
    """The guard pass-through: the parts whose methods that only forward are listed."""
    parts: tuple[str, ...]


@dataclass(frozen=True)
class NoCallbacks:
    """The guard no-callbacks: the parts whose functions call none of their own parameters annotated as callables."""
    parts: tuple[str, ...]


Guard = (PackageOnly | ScenarioCoverage | NoComments | StandIns | ClosedTree | NoDuplicates | NoTwins | DeadCode
         | PassThrough | NoCallbacks | PrivateImports)
```

In `xarch/modules/spec/domain/guards.py`, replace the import block and the two tables:

```python
from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    NoCallbacks,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
)
from xarch.profile_values.testing import ScenarioCoverage, StandIns

KEY: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage", NoComments: "no-comments",
                        StandIns: "stand-ins", ClosedTree: "closed-tree", NoDuplicates: "no-duplicates",
                        NoTwins: "no-twins", DeadCode: "dead-code", PrivateImports: "private-imports",
                        PassThrough: "pass-through", NoCallbacks: "no-callbacks"}
"""The name a profile switches each guard on by, by the kind of value it is read into."""
GUARD = {key: kind for kind, key in KEY.items()}
"""The kind of value each guard is read into, by the name a profile switches it on by."""

ORDER = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins",
         "dead-code", "pass-through", "no-callbacks", "private-imports")
"""The name of every pre-built check a profile may switch on, in the order xarch lists them."""
```

(keep the module docstring and `from __future__ import annotations` above it as they are).

In `xarch/modules/spec/domain/profile_keys.py`:

(a) After `PASS_THROUGH = "guard.pass-through"`, add `NO_CALLBACKS = "guard.no-callbacks"`.

(b) In `SCOPES`, after `    PASS_THROUGH: "guards.pass-through",`, add `    NO_CALLBACKS: "guards.no-callbacks",`.

(c) In `RETIRED`, after `    Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import"),`, add:

```python
    Retired(PART, "no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}"),
```

In `xarch/modules/spec/domain/key_table.py`:

(a) Add `NO_CALLBACKS,` to the `profile_keys` import, between `NAMING,` and `NO_DUPLICATES,`.

(b) Replace

```python
_GUARD_SCOPES = {"scenario-coverage": SCENARIO_COVERAGE, "no-duplicates": NO_DUPLICATES, "no-twins": NO_TWINS,
                 "dead-code": DEAD_CODE, "pass-through": PASS_THROUGH}
```

with

```python
_GUARD_SCOPES = {"scenario-coverage": SCENARIO_COVERAGE, "no-duplicates": NO_DUPLICATES, "no-twins": NO_TWINS,
                 "dead-code": DEAD_CODE, "pass-through": PASS_THROUGH, "no-callbacks": NO_CALLBACKS}
```

(c) Delete the line `    Key(PART, "no_callbacks", rules=("no-callbacks",)),`.

(d) Replace

```python
    _guard("pass-through"),
    _guard("private-imports"),
```

with

```python
    _guard("pass-through"),
    _guard("no-callbacks"),
    _guard("private-imports"),
```

(e) Replace

```python
    Key(PASS_THROUGH, "parts", True, rules=("pass-through",)),
```

with

```python
    Key(PASS_THROUGH, "parts", True, rules=("pass-through",)),

    Key(NO_CALLBACKS, "parts", True, rules=("no-callbacks",)),
```

(f) In `NEEDS`, delete the line `    "parts.<part>.no_callbacks": ("callback",),`, and replace

```python
    "guards.pass-through": ("function", "function.forwards"),
```

with

```python
    "guards.pass-through": ("function", "function.forwards"),
    "guards.no-callbacks": ("callback",),
```

- [ ] **Step 10: The catalogue's texts**

In `xarch/architectures/presets/format/keys.yaml`:

(a) Delete the whole entry (eleven lines, starting at line 378):

```yaml
  parts.<part>.no_callbacks:
    meaning: its code calls none of its own parameters
    accepts: >-
      true: no function, method or nested function of the part calls, by its bare name, a parameter of a function it
      lies in that is annotated as a callable type (alone, subscripted, in a union or as an optional), as in
      `check(path)` for `check: Callable[[str], bool]`. Not read: the first parameter of a method (`self`, `cls`; a
      staticmethod has none), a parameter with no such annotation, one passed on (`sorted(rows, key=key)`), one whose
      method is called (`p.read()`), and one the body rebinds
    example: |
      <<part>>
          no_callbacks: true
```

(b) Directly after the `guards.pass-through:` entry (whose example ends `          parts: [documents]`) and before `  guards.private-imports:`, insert:

```yaml
  guards.no-callbacks:
    meaning: no function of the parts calls a parameter annotated as a callable
    accepts: >-
      {parts: [<part>, ...]}: no function, method or nested function of those parts calls, by its bare name, a
      parameter of a function it lies in that is annotated as a callable type (alone, subscripted, in a union or as an
      optional), as in `check(path)` for `check: Callable[[str], bool]`; each such call is a violation, and fails
      `check`. Not read: the first parameter of a method (`self`, `cls`; a staticmethod has none), a parameter with no
      such annotation, one passed on (`sorted(rows, key=key)`), one whose method is called (`p.read()`), and one the
      body rebinds
    example: |
      <<part>>
      guards:
        no-callbacks:
          parts: [documents]
```

(c) Directly after the `guards.pass-through.parts:` entry (whose example ends `          parts: [documents]`) and before `  docs.entry:`, insert:

```yaml
  guards.no-callbacks.parts:
    meaning: the parts whose functions call no parameter annotated as a callable
    accepts: "[<part>, ...]"
    example: |
      <<part>>
      guards:
        no-callbacks:
          parts: [documents]
```

- [ ] **Step 11: Parse the guard through one helper shared with pass-through; drop the part key's read**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

(a) In the `profile_keys` import (lines 89-105), add `NO_CALLBACKS,` between `MOCKS,` and `NO_DUPLICATES,`. In the `values` import (lines 107-121), add `NoCallbacks,` between `Layout,` and `NoDuplicates,`.

(b) After the line `_NEEDS_TESTING = (KEY[ScenarioCoverage], KEY[StandIns])`, add:

```python
_LISTED = {PassThrough: (PASS_THROUGH, "the parts whose methods are listed when they only forward"),
           NoCallbacks: (NO_CALLBACKS, "the parts whose functions call none of their parameters annotated as callables")}
"""The guards whose one key is the parts they read, each with the scope of its keys and what its parts are."""
```

(c) In `_guards`, replace

```python
        elif kind is PassThrough:
            guard = _pass_through(spec, declared, parts, where, problems)
            if guard is not None:
                guards.append(guard)
```

with

```python
        elif kind in _LISTED:
            listed = _listed_parts(spec, declared, parts, where, *_LISTED[kind], problems)
            if listed is not None:
                guards.append(kind(listed))
```

(d) Replace the whole function `_pass_through` (lines 937-949):

```python
def _pass_through(spec: Any, declared: set[str], parts: dict[str, Part], where: str,
                  problems: list[str]) -> PassThrough | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{parts: [<part>, ...]}}: the parts whose methods are listed "
                        "when they only forward")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(PASS_THROUGH), where, PASS_THROUGH)
    problems += [f"{where}: missing `{key}`" for key in required_of(PASS_THROUGH) if key not in spec]
    names = ck.part_names(spec["parts"], declared, f"{where}.parts", problems) if "parts" in spec else []
    if len(problems) != count:
        return None
    return PassThrough(tuple(n for n in names if n in parts))
```

with

```python
def _listed_parts(spec: Any, declared: set[str], parts: dict[str, Part], where: str, scope: str, said: str,
                  problems: list[str]) -> tuple[str, ...] | None:
    """The parts a guard whose one key is `parts` reads, in the order written; None, with its problems, when the
    guard is written wrong. scope is the scope of the guard's keys; said, what its parts are, as its refusal says it."""
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{parts: [<part>, ...]}}: {said}")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(scope), where, scope)
    problems += [f"{where}: missing `{key}`" for key in required_of(scope) if key not in spec]
    names = ck.part_names(spec["parts"], declared, f"{where}.parts", problems) if "parts" in spec else []
    if len(problems) != count:
        return None
    return tuple(n for n in names if n in parts)
```

(e) In `_substance`, replace the docstring

```python
    """The keys of a part that say what its code holds and how it is used: holds, immutable, types_only, no_callbacks,
    names, built_by and shared."""
```

with

```python
    """The keys of a part that say what its code holds and how it is used: holds, immutable, types_only, names,
    built_by and shared."""
```

delete the four lines

```python
    no_callbacks = spec.get("no_callbacks", False)
    if not isinstance(no_callbacks, bool):
        problems.append(f"{where}.no_callbacks: must be true or false")
        no_callbacks = False
```

and replace

```python
    return replace(part, holds=holds, no_callbacks=no_callbacks, names=names, built_by=built_by, types_only=types_only,
                   shared=shared, immutable=immutable)
```

with

```python
    return replace(part, holds=holds, names=names, built_by=built_by, types_only=types_only, shared=shared,
                   immutable=immutable)
```

Then confirm no reference remains: `grep -n "no_callbacks\|_pass_through" xarch/modules/spec/application/logic/profile_parsing.py` prints nothing.

- [ ] **Step 12: The published view: `GuardsView.no_callbacks`, `PartView` without the key**

In `xarch/modules/spec/contract/__init__.py`:

(a) Replace `PartView`'s docstring

```python
    """One part of a profile as a check reads it: its name; its path as a pattern, `*` standing for the instance of a
    repeating folder; what it may import besides itself; its role, litmus test, how the docs name it (shown) and why no
    tier tests it; the names it may not use; what each of its files must import one of; what its files define
    (holds); the parts it may use as types only; whether it calls none of its own parameters; the patterns its public
    classes match; the parts that alone may build its classes; for a part there to be shared, the fewest users
    each of its public names must have; and whether every class it defines, but an exception, is an immutable
    record."""
```

with

```python
    """One part of a profile as a check reads it: its name; its path as a pattern, `*` standing for the instance of a
    repeating folder; what it may import besides itself; its role, litmus test, how the docs name it (shown) and why no
    tier tests it; the names it may not use; what each of its files must import one of; what its files define
    (holds); the parts it may use as types only; the patterns its public classes match; the parts that alone may
    build its classes; for a part there to be shared, the fewest users each of its public names must have; and
    whether every class it defines, but an exception, is an immutable record."""
```

and delete its field line `    no_callbacks: bool = False`.

(b) In `GuardsView`'s docstring, replace the last two lines

```python
    profile accepts, each `<file below the app>:<name>`), the parts whose forwarding methods are listed, and private
    imports."""
```

with

```python
    profile accepts, each `<file below the app>:<name>`), the parts whose forwarding methods are listed, the parts
    whose functions call none of their parameters annotated as callables, and private imports."""
```

and replace

```python
    pass_through: tuple[str, ...] = ()
    private_imports: bool = False
```

(in `GuardsView`) with

```python
    pass_through: tuple[str, ...] = ()
    no_callbacks: tuple[str, ...] = ()
    private_imports: bool = False
```

In `xarch/modules/spec/application/services/publishing.py`:

(a) Add `NoCallbacks,` to the `values` import between `Guard,` and `NoComments,`.

(b) Replace

```python
                               part.must_import, part.holds, part.types_only, part.no_callbacks, part.names,
                               part.built_by, part.shared, part.immutable)
```

with

```python
                               part.must_import, part.holds, part.types_only, part.names, part.built_by, part.shared,
                               part.immutable)
```

(c) In `_guards_view`, replace

```python
        pass_through=next((g.parts for g in guards if isinstance(g, PassThrough)), ()),
```

with

```python
        pass_through=next((g.parts for g in guards if isinstance(g, PassThrough)), ()),
        no_callbacks=next((g.parts for g in guards if isinstance(g, NoCallbacks)), ()),
```

- [ ] **Step 13: The docs line becomes a guard line**

In `xarch/modules/spec/application/logic/docs_template.py`:

(a) Add `NoCallbacks,` to the `values` import between `Layout,` and `NoDuplicates,`.

(b) In `_part_lines`, delete the four lines

```python
    callbacks = [p.name for p in parts if p.no_callbacks]
    if callbacks:
        lines.append(f"`no-callbacks`: no function of {shown(callbacks)} calls a parameter annotated as a callable: it "
                     "is handed values, never a way to fetch them.")
```

(c) In `_guard_line`, directly after the `case PassThrough(parts):` branch (which ends `"`check --strict` only.")`) and before `case ClosedTree():`, insert:

```python
        case NoCallbacks(parts):
            shown = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in parts])
            return (f"`no-callbacks`: no function of {shown} calls a parameter annotated as a callable: it is handed "
                    "values, never a way to fetch them.")
```

(It must come before `case _:`, which says the no-comments line.)

- [ ] **Step 14: Rules' adapter reads the parts from the guards**

In `xarch/modules/rules/adapters/spec_profile.py`, replace

```python
                       no_callbacks=tuple(p.name for p in parts if p.no_callbacks),
```

with

```python
                       no_callbacks=guards.no_callbacks,
```

In `xarch/modules/rules/domain/profile.py`, in `Profile`'s docstring, replace

```python
    types_only, by part, the parts it may use as types only; no_callbacks the parts whose
    code calls none of its own parameters; names, by part, the patterns its public classes match one of; built_by, by
```

with

```python
    types_only, by part, the parts it may use as types only; no_callbacks the parts the guard no-callbacks lists,
    whose code calls none of its own parameters annotated as callables; names, by part, the patterns its public
    classes match one of; built_by, by
```

- [ ] **Step 15: Every profile writes the guard**

Create `/tmp/xarch-4-2/move_flag.py` (never committed):

```python
"""Drop `no_callbacks: true` from the parts of each profile and write the guard no-callbacks after pass-through."""
import sys
from pathlib import Path

root = Path(sys.argv[1])
FLAG = "    no_callbacks: true\n"
PASS = "  pass-through: {parts: [services, controller, adapters]}\n"


def edit(path: Path, old: str, new: str, count: int) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == count, (path, old, text.count(old))
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"{path.relative_to(root)}: {count} x {old.strip()!r}")


for name in ("xarch/architectures/cli.yaml", "xarch/architectures/web.yaml", "architecture.yaml",
             "tests/bootstrap/corpora/7cc6111.yaml", "tests/bootstrap/corpora/df537ca.yaml"):
    edit(root / name, FLAG, "", 2)
    edit(root / name, PASS, PASS + "  no-callbacks: {parts: [domain, logic]}\n", 1)
stress = root / "tests/bootstrap/corpora/stress.yaml"
edit(stress, FLAG, "", 4)
edit(stress, "    - platform\n  private-imports: {}\n",
     "    - platform\n  no-callbacks: {parts: [domain, logic, services, controller]}\n  private-imports: {}\n", 1)
```

Run:

```bash
mkdir -p /tmp/xarch-4-2
python3 -I /tmp/xarch-4-2/move_flag.py "$PWD"
git diff --numstat -- xarch/architectures architecture.yaml tests/bootstrap/corpora
grep -rn "no_callbacks" xarch/architectures architecture.yaml tests/bootstrap/corpora/*.yaml
```

Expected: twelve printed edits; numstat `1 2` for each of `cli.yaml`, `web.yaml`, `architecture.yaml`, `7cc6111.yaml`, `df537ca.yaml` and `1 4` for `stress.yaml`; no `.json` or `.xz` in the numstat; the `grep` prints nothing. The flags came from `domain` and `logic` in the five (and also `services`, `controller` in `stress.yaml`), so each guard lists exactly the parts that carried the flag. Read `git diff` of the six files.

- [ ] **Step 16: Run the tests of Steps 1-7 and the spec and rules suites**

Run the command of Step 8 again. Expected: all PASS.

Then:

```bash
timeout 900 uv run pytest -q tests/modules tests/kernel tests/cli 2>&1 | tail -5
grep -rn "no_callbacks" xarch --include=*.py
```

Expected: all PASS. The `grep` prints only `xarch/modules/rules/adapters/spec_profile.py` (`no_callbacks=guards.no_callbacks`), `xarch/modules/rules/application/logic/expansion.py` (`_no_callbacks`, its docstring, `key=f"parts.{part}.no_callbacks"`, `profile.no_callbacks`, `"parts.no_callbacks"` in `KEYS`; Task 2 changes those), `xarch/modules/rules/domain/profile.py` (the field and docstring), and `xarch/modules/spec/contract/__init__.py` / `publishing.py` (the `GuardsView` field and `no_callbacks=` in `_guards_view`).

- [ ] **Step 16a: Regenerate the golden docs and read the diff** (they are checked in and compared by tests: `tests/bootstrap/test_docs_templates.py` generates each of the three from its profile and requires equality, so they must move in the commit that moves the docs line)

Create `/tmp/xarch-4-2/regenerate_docs.py` (never committed):

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
uv run python -I /tmp/xarch-4-2/regenerate_docs.py "$PWD"
git diff --numstat -- docs/cli docs/web docs/xarch docs/templates docs/examples
git diff -U0 -- docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md
git diff -U0 -- docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md | grep '^[-+]- ' | sed 's/^[-+]//' | sort | uniq -c
```

Expected: three `written` lines; numstat `1 1` for each of the three `testing.md` files and nothing else; each file's diff has one `-` hunk (the `no-callbacks` line where the part lines were: `docs/xarch/testing.md:169`, `docs/cli/testing.md:349`, `docs/web/testing.md:350`) and one `+` hunk placing the same line directly after its `pass-through` line and before its `private-imports` line; the last command prints one line, `6 - \`no-callbacks\`: no function of \`domain/\` and \`application/logic/\` calls a parameter annotated as a callable: it is handed values, never a way to fetch them.` (the same text removed and added three times). If anything else moves, stop and report it with the diff (`git checkout -- docs/cli docs/web docs/xarch` restores the files); the fix belongs in the code, never in the docs.

- [ ] **Step 17: Run the whole suite and the checks**

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-4-2/pytest-task1.log 2>&1 & echo $! > /tmp/xarch-4-2/pytest-task1.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-4-2/pytest-task1.log`.
Expected: the suite passes, including `tests/bootstrap/test_docs_templates.py` (the three golden docs, regenerated in Step 16a), `tests/bootstrap/test_recorded_corpora.py` (the rule's key text is still `parts.<part>.no_callbacks`, so the recorded findings match unchanged), `tests/bootstrap/test_needs_agree.py`, `tests/bootstrap/test_rule_ids.py` (its `no-callbacks` case runs the bundled `web` profile, now through the guard) and `tests/architecture/test_self_check.py` (`guards_off == []`); both checks report no violation; ruff reports nothing; the profile check loads. If `test_needs_agree.py::test_the_profile_sets_every_key_the_engine_expands` lists `guards.no-callbacks`, stop and report it: it means `--rule` answers `ok` for a key the engine does not yet expand, and the plan's task order needs Task 2's `KEYS` change here.
If `xarch check` flags `tests/bootstrap/test_bundled_guards.py` for importing `NoCallbacks` (the wired tier uses `domain/` as a type only, and `isinstance` is a use as a type, so it should not), report the finding; do not loosen the profile. Drop that one `isinstance` assertion instead and keep the `GuardsView` and `hasattr` assertions, which pin the same thing.

- [ ] **Step 18: Commit**

```bash
git add xarch/modules/spec xarch/modules/rules/adapters/spec_profile.py xarch/modules/rules/domain/profile.py \
  xarch/architectures/presets/format/keys.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml \
  tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml tests/bootstrap/corpora/stress.yaml \
  tests/modules/spec tests/modules/rules/adapters/test_spec_profile.py tests/bootstrap/test_bundled_guards.py \
  tests/bootstrap/test_check_enforcement.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_architecture_files.py \
  docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md
git status --short
git commit -F - <<'MSG'
A profile says which parts take no callbacks once, among its guards, as no-callbacks: {parts: [...]} read through the one helper pass-through shares, and a part writing no_callbacks is refused with the retired-keys hint that writes the new form, so that the guard needs callback, guards off lists it after pass-through, its docs line sits among the guard lines, and the bundled profiles, xarch's own and the corpora profiles write it for domain and logic

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

`git status --short` before the commit must show nothing under `.claude/` staged and no `.json`/`.xz` change.

---

### Task 2: The finding names `(guards.no-callbacks)`

**Files:**
- Modify: `xarch/modules/rules/application/logic/expansion.py:196-203`, `:354-358`
- Modify: `tests/bootstrap/corpora/7cc6111.json` (16 lines), `tests/bootstrap/corpora/stress-7cc6111.json.xz` (16 lines)
- Test: `tests/modules/rules/application/logic/test_no_callbacks.py`, `tests/modules/rules/application/logic/test_expansion.py`, `tests/modules/rules/application/logic/test_expandable.py`

**Interfaces:**
- Consumes: Task 1's `Profile.no_callbacks` filled from `GuardsView.no_callbacks` (unchanged type `tuple[str, ...]`).
- Produces: every rule of the book group `"no-callbacks"` has `key == "guards.no-callbacks"`; `expansion.KEYS` names `"guards.no-callbacks"` where it named `"parts.no_callbacks"`, so `expandable.expands("guards.no-callbacks") is True`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_no_callbacks.py`, replace

```python
         "(parts.logic.no_callbacks)", "no-callbacks",
```

with

```python
         "(guards.no-callbacks)", "no-callbacks",
```

and append:

```python
def test_every_listed_part_s_finding_names_the_guard_and_not_the_part():
    domain = "modules/docs/domain/rule.py"
    found = violations([source(LOGIC, callbacks=(Callback(4, "resolve", "exists", annotated=True),)),
                        source(domain, callbacks=(Callback(7, "check", "has", annotated=True),))],
                       profile(no_callbacks=("logic", "domain")))
    assert sorted(str(v) for v in found) == [
        f"app/{LOGIC}:4: resolve calls its parameter exists: logic/ of modules/docs takes no callback "
        "(guards.no-callbacks)",
        f"app/{domain}:7: check calls its parameter has: domain/ of modules/docs takes no callback (guards.no-callbacks)"]
```

(The builders' `PROFILE` has parts `domain` at `modules/<module>/domain` and `logic` at `modules/<module>/application/logic`; other rules' findings already say `domain/ of modules/docs`, as `test_holds.py` and `test_dead_code.py` show. `sorted` puts `app/modules/docs/application/...` before `app/modules/docs/domain/...`.)

In `tests/modules/rules/application/logic/test_expansion.py`, append:

```python
def test_the_rules_of_no_callbacks_are_keyed_by_the_guard_for_every_part():
    rules = expansion.book(replace(ON, no_callbacks=("domain", "logic")))["no-callbacks"]
    assert [(rule.scope.part, rule.key) for rule in rules] == [("domain", "guards.no-callbacks"),
                                                               ("logic", "guards.no-callbacks")]
```

In `tests/modules/rules/application/logic/test_expandable.py`, in `test_a_key_is_expandable_when_the_engine_expands_it_once_set`'s list, after `pytest.param("guards.no-comments", True, id="a guard the engine runs"),`, add:

```python
    pytest.param("guards.no-callbacks", True, id="the guard no-callbacks"),
    pytest.param("parts.no_callbacks", False, id="the part key no_callbacks, retired"),
```

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_no_callbacks.py tests/modules/rules/application/logic/test_expansion.py tests/modules/rules/application/logic/test_expandable.py`
Expected: FAIL: the findings end `(parts.logic.no_callbacks)` / `(parts.domain.no_callbacks)`; the rules' keys are `parts.domain.no_callbacks`, `parts.logic.no_callbacks`; `expands("guards.no-callbacks")` is `False` and `expands("parts.no_callbacks")` is `True`.

- [ ] **Step 3: Key the rule by the guard**

In `xarch/modules/rules/application/logic/expansion.py`, replace

```python
def _no_callbacks(profile: Profile) -> tuple[Rule, ...]:
    """Code of a part that lists `no_callbacks` calls none of its own parameters annotated as callables; the first
    parameter of a method, the object it is called on, is no callback."""
    return tuple(Rule("no-callbacks", Scope(APP, part), ("callback",), MAY_NOT, EXISTING,
                      (Saying("{function} calls its parameter {name}: {where} takes no callback ({key})",
                              "have the caller call {name} first and pass {function} the answer as a value"),),
                      keep=_all("annotated-callable"), exempt=_all("receiver"), key=f"parts.{part}.no_callbacks")
                 for part in profile.no_callbacks)
```

with

```python
def _no_callbacks(profile: Profile) -> tuple[Rule, ...]:
    """Code of a part the guard no-callbacks lists calls none of its own parameters annotated as callables; the first
    parameter of a method, the object it is called on, is no callback."""
    return tuple(Rule("no-callbacks", Scope(APP, part), ("callback",), MAY_NOT, EXISTING,
                      (Saying("{function} calls its parameter {name}: {where} takes no callback ({key})",
                              "have the caller call {name} first and pass {function} the answer as a value"),),
                      keep=_all("annotated-callable"), exempt=_all("receiver"), key="guards.no-callbacks")
                 for part in profile.no_callbacks)
```

and in `KEYS` replace `"parts.package_only", "parts.types_only", "parts.no_callbacks", "parts.names", "parts.built_by",` with `"parts.package_only", "parts.types_only", "guards.no-callbacks", "parts.names", "parts.built_by",` (same place: `KEYS` follows the book's order, which `test_the_keys_the_engine_expands_are_those_the_rules_of_a_profile_setting_them_all_are_keyed_by` pins).

- [ ] **Step 4: Run the rules suite**

Run: `timeout 600 uv run pytest -q tests/modules/rules tests/bootstrap/test_needs_agree.py`
Expected: all PASS; `test_needs_agree.py` now reads `guards.no-callbacks` among the expanded keys and finds its needs (`callback`) the same on both sides.

- [ ] **Step 5: Edit the recorded findings, line by line**

The 7cc6111 recording (plain JSON):

```bash
grep -c "(parts\.domain\.no_callbacks)\|(parts\.logic\.no_callbacks)" tests/bootstrap/corpora/7cc6111.json
sed -i 's/(parts\.domain\.no_callbacks)/(guards.no-callbacks)/; s/(parts\.logic\.no_callbacks)/(guards.no-callbacks)/' \
  tests/bootstrap/corpora/7cc6111.json
git diff --numstat -- tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/df537ca.json
git diff -U0 -- tests/bootstrap/corpora/7cc6111.json
```

Expected: the count is `16`; numstat `16 16 tests/bootstrap/corpora/7cc6111.json` and nothing for `df537ca.json`. Read every hunk: each `-` line ends `(parts.domain.no_callbacks)",` or `(parts.logic.no_callbacks)",` and its `+` line is the same text with `(guards.no-callbacks)",` in that place. `grep -c "no_callbacks" tests/bootstrap/corpora/df537ca.json` stays `0`.

The stress recording (xz), decompressed to scratch:

```bash
xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz > /tmp/xarch-4-2/stress-before.json
grep -o "(parts\.[a-z]*\.no_callbacks)" /tmp/xarch-4-2/stress-before.json | sort | uniq -c
sed 's/(parts\.domain\.no_callbacks)/(guards.no-callbacks)/; s/(parts\.logic\.no_callbacks)/(guards.no-callbacks)/' \
  /tmp/xarch-4-2/stress-before.json > /tmp/xarch-4-2/stress-after.json
diff -U0 /tmp/xarch-4-2/stress-before.json /tmp/xarch-4-2/stress-after.json
diff /tmp/xarch-4-2/stress-before.json /tmp/xarch-4-2/stress-after.json | grep -c '^>'
grep -c "no_callbacks" /tmp/xarch-4-2/stress-after.json
xz -c -9 /tmp/xarch-4-2/stress-after.json > tests/bootstrap/corpora/stress-7cc6111.json.xz
xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz | cmp - /tmp/xarch-4-2/stress-after.json && echo same
```

Expected: `6 (parts.domain.no_callbacks)` and `10 (parts.logic.no_callbacks)`; the `diff -U0` shows 16 hunks, each changing only that parenthesis (read each); the count of `>` lines is `16`; `14` lines still say `no_callbacks` (the source-file names `test_no_callbacks.py`, `xarch.modules.rules.application.logic.no_callbacks`, `.../no_callbacks.py`, which stay); `same`.

- [ ] **Step 6: Run the recorded corpora and the whole suite**

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-4-2/pytest-task2.log 2>&1 & echo $! > /tmp/xarch-4-2/pytest-task2.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
```

When the background run ends: `tail -5 /tmp/xarch-4-2/pytest-task2.log`.
Expected: the suite passes, `tests/bootstrap/test_recorded_corpora.py` included (its three recordings match with only the 32 lines changed); both checks and ruff report nothing. Then `grep -rn "no_callbacks" xarch --include=*.py` prints only the `Profile` field and docstring (`rules/domain/profile.py`), `_no_callbacks` and `profile.no_callbacks` (`expansion.py`), the adapter's `no_callbacks=guards.no_callbacks`, and the `GuardsView` field and `_guards_view` line.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules/application/logic/expansion.py tests/modules/rules/application/logic/test_no_callbacks.py \
  tests/modules/rules/application/logic/test_expansion.py tests/modules/rules/application/logic/test_expandable.py \
  tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/stress-7cc6111.json.xz
git commit -F - <<'MSG'
A finding of no-callbacks names the key guards.no-callbacks for every part the guard lists, in place of parts.<part>.no_callbacks, and the engine expands guards.no-callbacks; the recorded findings change in the 32 lines that named the part key, 16 of 7cc6111 and 16 of the stress recording, and in no other

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 3: README, CHANGELOG and the gates

**Files:**
- Modify: `README.md:118`, `:123-124`, `:308`
- Modify: `CHANGELOG.md:44-45` (top of `### Changed` under `## [Unreleased]`)

**Interfaces:**
- Consumes: Tasks 1 and 2 (the docs line is a guard line; the finding's key is `guards.no-callbacks`).
- Produces: nothing code reads.

- [ ] **Step 1: README**

In `README.md`, replace

```
                    package_only, folders, holds, immutable, types_only, no_callbacks, names, built_by, shared}}
```

with

```
                    package_only, folders, holds, immutable, types_only, names, built_by, shared}}
```

replace

```
guards:   {scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins, dead-code,
           pass-through, private-imports}
```

with

```
guards:   {scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins, dead-code,
           pass-through, no-callbacks, private-imports}
```

and replace

```
| `no-callbacks` | a function of a part that calls one of its own parameters annotated as a callable | `parts.no_callbacks` |
```

with

```
| `no-callbacks` | a function of a part the guard lists that calls one of its own parameters annotated as a callable | `guards.no-callbacks` |
```

The id list (line 382) does not change. Then `grep -n "no_callbacks" README.md` prints nothing.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]` → `### Changed`, insert as the first item (after the blank line following `### Changed`):

```
- `no_callbacks` on a part is now the guard `no-callbacks: {parts: [<part>, ...]}`, which lists the parts whose
  functions call none of their parameters annotated as callables, as `pass-through` lists its parts; it reads the same
  code and still fails `check`. A part writing `no_callbacks` is refused at load: `parts.<part>: unknown key
  'no_callbacks': moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}`. Its findings name
  `(guards.no-callbacks)` in place of `(parts.<part>.no_callbacks)`, `guards off` lists `no-callbacks` for a profile
  that leaves it out, and its line in the generated docs sits among the guard lines, after `pass-through`'s in the
  bundled profiles, which write `no-callbacks: {parts: [domain, logic]}`.
```

- [ ] **Step 3: Confirm the golden docs are current**

Task 1 Step 16a regenerated them. Run `uv run python -I /tmp/xarch-4-2/regenerate_docs.py "$PWD"` again (recreate the script from Task 1 Step 16a if `/tmp` was cleared) and `git status --short -- docs`: expected no output (nothing to change; nothing hand-edited).

- [ ] **Step 4: Run the gates**

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-4-2/pytest.log 2>&1 & echo $! > /tmp/xarch-4-2/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-4-2/pytest.log`.
Expected: the suite passes (corpora, needs-agree, rule-ids, check-enforcement, self-check, README tests included); both checks report no violation; ruff reports nothing; the profile check loads with no problem. Then confirm:
- `git diff 81d131e --stat -- tests/bootstrap/corpora` lists only `7cc6111.yaml`, `df537ca.yaml`, `stress.yaml`, `7cc6111.json`, `stress-7cc6111.json.xz`;
- `grep -rn "parts.no_callbacks\|parts\.<part>\.no_callbacks" xarch` prints nothing; `grep -rn "no_callbacks" xarch/architectures` prints nothing;
- `uv run xarch profile explain parts.no_callbacks` prints the retired text `moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}`, and `uv run xarch profile explain guards.no-callbacks` explains the guard;
- nothing under `.claude/` is staged.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'MSG'
The README's profile shape writes no-callbacks among the guards and no longer on a part, and its rule table keys no-callbacks by guards.no-callbacks; the CHANGELOG says the part key became the guard, is refused with the new form, and that findings, guards off and the docs line follow

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

## Self-review against the spec

- §2.1 settings and refusals: Task 1 Steps 1 (every row of the table, plus null), 11 (`_listed_parts`, `_LISTED` with the spec's phrase). Pass-through texts unchanged: existing cases in `test_a_bad_new_guard_is_refused` stay green through the shared helper (spec test 2). `NoCallbacks(parts)` in written order: Step 1 (c).
- §2.2 what the check does, finding text: Task 2 Steps 1, 3; no guard → no finding: existing `test_it_is_off_without_a_listed_part`.
- §2.3 needs: Task 1 Steps 3 (refusal text, `drop guards.no-callbacks`, no refusal without the guard, `callback` needed by the guard alone), 9 (f); no `NEEDS` entry for `.parts`: Step 9 (f) adds none; `test_needs_agree.py` agreement: Task 2 Step 4.
- §2.4 `ORDER`, `guards off`, `baseline_off`: Task 1 Steps 1, 4 (`origins.py`, `test_check.py`), 7 (CLI text and JSON, `--strict` failing), 9.
- §2.5 retired key: Task 1 Steps 2 (true and false, beside the guard, the table by scope and by address, known part keys without `no_callbacks`), 4 (explain), 9 (c). Bare-name lookup reading fixed above.
- §2.6 catalogue: Task 1 Step 10; its tests (`test_profile_keys.py` examples load, accepts one line, every `NEEDS` address a key) run in Step 16.
- §2.7 bundled profiles: Task 1 Steps 7, 15; `guards off` empty for them: `test_a_clean_bundled_project_shows_its_profile_and_the_guards_it_ships_off`, `test_the_json_enforcement_always_holds_every_key`, `test_self_check.py`.
- §2.8 docs line: Task 1 Steps 5, 7 (d), 13; golden copies: Task 1 Step 16a, confirmed in Task 3 Step 3.
- §2.9 views and values: Task 1 Steps 4 (spec view), 6 (adapter), 9, 12, 14; `profile_keys.NO_CALLBACKS`: Step 9; rule key constant and `KEYS`: Task 2 Step 3.
- §2.10 corpora: profiles Task 1 Step 15; findings Task 2 Step 5 (16 + 0 + 16 = 32).
- §2.11 README, CHANGELOG: Task 3 Steps 1, 2.
- §3 tests 1-18: 1-3 Task 1 Step 1 (3 as the sorted list); 4-5 Step 2; 6-7 Step 3; 8-9 Step 4; 10 Steps 5, 7; 11 Step 6; 12 Task 2 Step 1; 13 Task 1 Step 7 and Task 2 Step 4; 14-15 Task 1 Step 7; 16 Task 2 Step 6; 17 Task 1 Step 16a (regenerated, diff read; `test_docs_templates.py` compares all three to the generator); 18 Task 1 Step 17.
- §4 gates: Task 1 Step 17, Task 2 Step 6, Task 3 Step 4.
- Placeholders: none. Names used across tasks: `NoCallbacks`, `NO_CALLBACKS`, `GuardsView.no_callbacks`, `_listed_parts`, `_LISTED`, `CALLBACKS_MOVED` (test-only), all defined where first used.
<!-- task-pipeline: validated -->
