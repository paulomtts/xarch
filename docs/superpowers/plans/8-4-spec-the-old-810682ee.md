# 8.4 spec: the old reference forms are refused with their replacement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every old form of a target (`<part>@any`, `<part>@own`, a bare part name, each with or without `/<path>` and
`:<pattern>`) is refused, one problem per value, with the reference to write computed from the profile; the tree
refuses the repeating folder `<parts>`; a key outside `imports` refuses a prefixed part name with the plain one.

**Architecture:** `target()` in `xarch/kernel/logic/targets.py` loses its old-form parser: a dot-less head goes
through a small `old_form()` splitter and is refused with one wording (`removed()`), the replacement chosen by the same
`_word_problem` rule `_reference` already uses. A tier's `must`/`types_only` (`_tier_part`) uses the same two helpers.
One more kernel helper, `outside_imports()`, is called by every reader of a key outside `imports` that names a part.
The `parts` tree reader (`_steps`) refuses the step `<parts>`.

**Tech Stack:** Python 3, pytest (`pytest.param(..., id=...)` tables), Typer `CliRunner` for the integration tier,
`uv run`, ruff.

**Spec:** `docs/superpowers/specs/8-4-spec-the-old-810682ee.md` (reproduced in full below this plan's header).

## The spec

Reproduced verbatim from `docs/superpowers/specs/8-4-spec-the-old-810682ee.md`; headings demoted one level.

## 8.4 spec: the old reference forms are refused with their replacement

Card: 810682ee-28a2-4487-83d3-87a0238dcae6 (subtask of f1c96689), blocked by 8.3 (c24c8593, done: branch tip
72b857c). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3), sub-step 4 of its owning
note.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements section 4 (lines 293-325), 3.3 (lines 233-238) as moved by `profile-form-proposal.md` 5.3 item 2
(lines 627-628: the refusal of the word `parts` sits in the reader of the tree's keys, "same rule, same text"), 3.10
(lines 278-282), 3.11 (lines 284-287) and section 6 sub-step 4 (lines 453-455). Dodges: note section 7 (lines
461-480). From review 3: O4, O5, O8.

### Goal

After this card, a profile that writes a target in an old form (`<part>@any`, `<part>@own`, the bare name of a part,
each with or without `/<path>` and `:<pattern>`) is refused by `profile check` (and by every command that loads the
profile), one problem per value, each naming the exact reference to write instead, computed from the profile. Only
`parts.<part>`, `<word>.<part>` and `everything` remain. Alongside: the reader of the `parts` tree refuses a repeating
folder word `parts`; a key outside `imports` that names a part refuses a prefixed name with the plain name to write;
`<word>.` from an importer outside that folder and a concrete instance name stay refused (already built in 8.1) and are
pinned by tests. The CHANGELOG says so. Nothing any valid profile allows changes: every bundled profile and every
fixture already writes references (8.3).

### What is already there (not to be redone)

- `target()` in `xarch/kernel/logic/targets.py` reads references through `_reference()` (lines 97-133) whenever the
  head (text before the first `/` or `:`) holds a dot. That path already refuses: a malformed reference and `@`
  anywhere before the pattern (`is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path>
  and :<pattern>`, line 105; this covers note 3.10: `parts.contract@any`, `module.services/schema@any`); a bracketed
  word (`write the word without brackets: module.services`, line 142); a prefix that is no word, with the instance hint
  and, for `place`, the dotted-name hint (lines 151-152, note 3.11); `<word>.` for a part in no or another word's
  folder, and from an importer outside the folder (lines 155-172); the self-import (`_implied`, lines 197-203).
- Every head **without** a dot still goes through the old-form branch of `target()` (lines 39-82, regex `TARGET` at
  line 21). That branch is what this card replaces.
- A tier's `imports.must` / `imports.types_only` are read by `tier_parts` / `_tier_part`
  (`xarch/modules/spec/application/logic/imports_written.py:58-97`), which still returns a dot-less entry as a plain
  name (line 87-88). That is the second old-form reader.
- Bundled profiles (`xarch/architectures/cli.yaml`, `web.yaml`, root `architecture.yaml`), corpora
  (`tests/bootstrap/corpora/*.yaml`), `keys.yaml`, README and most tests already write references (8.3, commits
  63e6b58..72b857c).

### Inherited constraints

- One wording for every 0.3.0 refusal of a value: `'<value>': <form> was removed in 0.3.0: write <new>` (note section
  4, lines 297-300). Each problem keeps today's shape: address, value, what is wrong, what to write.
- Every old form refused, no warning, no window, no rewrite on load, no `profile migrate` (rulings lines 7-8, 46; note
  section 7 lines 463-467).
- One problem per line of an inline profile with several old forms (rulings line 37).
- No special-casing of a profile, its parts or the word `module`: the word comes from the paths of the profile read
  (note section 7, lines 468-469).
- No concrete instance name accepted, for tests or otherwise (rulings lines 15-16; section 7 line 476).
- `<word>.` from an importer outside the folder refused, never matching nothing (section 7 line 475).
- Keys outside `imports` keep plain names; the check target `place` keeps references (rulings lines 20-24, 39-40;
  section 2 table lines 158-193; section 7 lines 477-478).
- `Target` does not change; no new scope (section 7 line 472).
- Generated docs `docs/{cli,web,xarch}/testing.md` regenerated, never edited by hand, diff read; expected not to move
  (note 5.3 lines 411-412; review 3 O8).
- README and CHANGELOG lines under `[Unreleased]` (review 3 O4, O5).
- Project rules (card): no comments in xarch's code (docstrings only); never `ruff --fix`; tests first and seen
  failing; examples simple with absolute `app.` imports; recorded corpora edited by hand only and only as the note says
  (none expected here); Python only in the reader adapter and `xarch/architectures/presets/` data; `.claude/` out of
  commits; nothing pushed; line length 120.

### Definitions used below

- *head*: the value's text before its first `/` or `:`. *tail*: the rest (`/<path>`, `:<pattern>`), carried unchanged
  into the replacement.
- *word of a part*: `repeat_of(repeats, path).word` (`xarch/kernel/logic/placement.py`), or none when the part lies in
  no repeating folder.
- *`<word>.` would be accepted*: the part has a word W, and either the reader is mirrored (a tier's `imports.also`) or
  the importer (`owner`) lies in a W folder; never for a tier's `imports.must` / `.types_only`. These are exactly the
  conditions `_word_problem` checks today; the replacement must be computed by the same rule, not a copy of it.

### Behavior

#### B1. `target()` refuses every head without a dot

Applies to every reader of `target()`: a part's `imports.may` (with or without the mode map) and `imports.must`, a
tier's `imports.may` and `imports.also`, and a check's `place` (`own_checks._match`, owner its `in.part`). `<where>` is
the key's address as today.

| Written (head has no dot) | Condition | Problem |
|---|---|---|
| `contract@any` | `contract` declared | `<where>: 'contract@any': @any was removed in 0.3.0: write parts.contract` |
| `contract@any/published`, `contract/published@any` | same | `... @any was removed in 0.3.0: write parts.contract/published` |
| `domain@any:*Id` | same, key takes patterns | `... write parts.domain:*Id` |
| `contract@own` | `<word>.` would be accepted | `<where>: 'contract@own': @own was removed in 0.3.0: write module.contract` (`module` = the part's word) |
| `contract@own`, `kernel@own` | `<word>.` would not be accepted | `... @own was removed in 0.3.0: write parts.contract` |
| `domain` (bare) | part has word W, `<word>.` would be accepted | `<where>: 'domain': a bare part name was removed in 0.3.0: write module.domain (this module's) or parts.domain (any module's)` (W in place of `module` throughout) |
| `contract` (bare) | part has a word, `<word>.` would not be accepted | `... a bare part name was removed in 0.3.0: write parts.contract` |
| `kernel` (bare) | part lies in no repeating folder | `... a bare part name was removed in 0.3.0: write parts.kernel` |
| `"domain/values:*Id"` (bare with tail) | as the bare rows | the tail follows each reference: `write module.domain/values:*Id (this module's) or parts.domain/values:*Id (any module's)` |
| `nope`, `nope@any` | `nope` not declared | today's `<where>: 'nope' names no part 'nope'` (value as written) |
| a declared part that places no file | | None with no problem, as today |
| `domain@foo`, `@any`, `""`, `domain@`, non-string (`1`, a list) | | `<where>: <value!r> is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and :<pattern>` (the one text of `_reference`; replaces today's `is not a target: use <part>, <part>@any, ...`) |
| a pattern where the key takes none, a bad pattern | head declared | the removal message (the old form is what is wrong first); the planner must not emit a second problem for the same value |
| own part in own `may` (`adapters` in `adapters`, `adapters@own`, `platform` in `platform`) | the replacement would be implied | today's implied text from `_implied`, with `parts.adapters` as what stays allowed (note section 4 row "module.adapters in adapters"); one problem |
| `adapters@any` in `adapters` (part in a repeating folder) | `parts.adapters` is accepted | `... @any was removed in 0.3.0: write parts.adapters` |
| `platform@any` in `platform` (part in no repeating folder) | `parts.platform` would be refused as implied | the implied text of the row above, one problem; never a hint that is refused again |
| `everything` | | unchanged: accepted where the key takes it |

- Exactly one problem per refused value; the other entries of the list are still read (and still refused or accepted
  on their own).
- The old-form branch, the regex `TARGET`, the unknown-scope text, `says what a bare name already says`, `lies in
  another repeating folder ... write X@any`, `say X@any`, `drop '@...'` are gone (no reachable path prints them). The
  module docstring (lines 5-10) no longer says "any other value is read in the old forms".
- Values whose head holds a dot behave exactly as at 72b857c (every row of 8.1's table stays green).

#### B2. A tier's `imports.must` and `imports.types_only` refuse a dot-less entry

`_tier_part` (`imports_written.py:79-97`), at `tiers.<t>.imports.must` / `.types_only`:

| Written | Problem |
|---|---|
| `controller`, `controller` declared | `<where>: 'controller': a bare part name was removed in 0.3.0: write parts.controller` |
| `controller@any`, `controller@own` | `... '<value>': @any (or @own) was removed in 0.3.0: write parts.controller` |
| `controller/x`, `controller:*Id` (dot-less head declared) | `... a bare part name was removed in 0.3.0: write parts.controller` (the key names whole parts, so no tail) |
| `nope` (not declared) | today's `<where>: no part named 'nope'` |
| `[controller, controller]` | two removal problems, no `listed twice` |
| `parts.controller`, `module.controller`, `parts.controller/x` | unchanged from 8.3 (c28eb9f) |

The docstrings of `tier_parts` (lines 59-61), `_tier_part` and the module docstring no longer mention a plain name.

#### B3. The tree's reader refuses the repeating word `parts`

In `xarch/modules/spec/application/logic/parts_tree.py`, `_steps()` (lines 147-160), a key whose step is `<parts>`
(at any depth: `units/<parts>/store/`, `<parts>/x.py`) is refused, one problem per key, beside the neighbouring
problems:

`parts: '<key>' has the step `<parts>`: `<parts>` is reserved: `parts.` names a part in every instance; give the
repeating folder another word`

The part below it is not read (as for the other step problems). `<partsx>`, `<sub-parts>`, a plain folder `parts/`
(no brackets) and a part named `parts` stay valid (note 3.2). `xarch/kernel/logic/placement.py` is not changed for
this (proposal 5.3 item 2).

#### B4. A key outside `imports` refuses a prefixed name

For every key that names a part by its plain name, a string value whose text before the first `.` is `parts` or a word
of the profile, and whose text after it, up to the first `/` or `:`, is a declared part P, is refused with:

`<where>: 'parts.bootstrap': names a part outside imports: write bootstrap` (P in place of `bootstrap`)

The keys (note section 2, rows lines 170-182) and today's readers:

- `holds.classes.built_by`, `fakes.for`, `guards.no-twins.translated`, guards' `parts` (pass-through, no-callbacks):
  `ck.part_names` (`profile_checks.py:392`).
- `layers.<name>`: `ck.layer_chains` (`profile_checks.py` ~line 130).
- `guards.scenario-coverage.results`: `ck.scenario_places` (~line 908).
- `docs.entry`: `profile_parsing.py:975`.
- `evals.<id>.in.part`, checks' `in.part`, `must_be_reached.from.part`: `written_checks.scope` (line ~177).
- `evals.placement.alike` (`evals.py:128`) and the keys of `evals.placement.lines` (`evals.py:169`).
- the check target `part` (`xarch/modules/rules/application/logic/own_checks.py:117-120`).

Rules:

- One shared helper decides and words it, used by every reader above (spec and rules both reach it, so it lives where
  both may import from, e.g. `xarch/kernel/logic/targets.py`); a reader keeps today's text for anything the helper
  does not claim.
- Not claimed: a dotted value whose prefix is no word (`os.environ`), or whose part is not declared (`parts.nope`):
  today's `no part named ...` text.
- `module.bootstrap/x` claims as `write bootstrap` (tail dropped).
- One problem per value; a list's other entries still read. The check target `place` is not affected (it takes
  references).

#### B5. Already refused, pinned by tests (no code change expected)

- Concrete instance name: `orders.services` is refused with `'orders' is neither parts nor a word of this profile
  (module): a profile names no instance; write module.services or parts.services`, **also** when the profile
  declares a part named `orders` (note 3.11; dodge line 476).
- `<word>.` from an importer outside its folder: `module.contract` in `parts.cli.imports.may` (`cli` outside
  `modules/<module>/`), in a tier's `imports.may` (owner None, `a tier's folder`), and in a check's `place` with no
  `in.part` (`a check that names no part`): refused with `write parts.contract`.

#### B6. Bundled profiles rewritten with their old lines are refused line by line

For each of `cli.yaml`, `web.yaml`, `architecture.yaml`: invert every entry of every list under `imports`
(`may`, `must`, `also`, `types_only`; the same selection as `entries()` in `tests/bootstrap/test_bundled_imports.py`)
to its old form, derived from the document alone:

- `parts.X<tail>` becomes `X@any<tail>` when X's path in that document holds a `<word>` step, else `X<tail>`; in a
  tier's `must` / `types_only` it becomes `X`.
- `<word>.X<tail>` becomes `X<tail>`.
- A mode map `{ref: types_only}` keeps its shape with the key inverted. `everything` and `[]` stay.

Writing that document to a temporary file and running `uv run xarch profile check <file>` (via `CliRunner` on
`xarch.bootstrap.app.app`) exits non-zero and prints exactly one problem per inverted entry, no other problem, and each
problem contains `was removed in 0.3.0: write <the original reference>` (for an inverted `<word>.X`, the first of the
two references in the message). No branch of the test names a profile, a part or the word `module`.

#### B7. Text

- CHANGELOG `## [Unreleased]`: the `### Added` entry's last sentence `No old form is refused yet.` is removed (the
  entry otherwise stays); a `### Changed` entry (the heading exists, line 145) says the old forms are refused, each
  with its replacement: `<part>@any` (write `parts.<part>`), `<part>@own` and the bare name (write `<word>.<part>` or
  `parts.<part>`, computed from the profile), a bare name in a tier's `imports.must` / `.types_only` (`parts.<part>`),
  the repeating folder word `<parts>`, a prefixed name in a key outside `imports` (the plain name), and that
  `<word>.<part>` from outside its folder and a concrete instance name stay refused. No rewrite on load.
- Docstrings that still describe a bare name or `@own` as accepted: `targets.py` module docstring and `target()`'s
  ("a bare name, or `<word>.<part>`, there is that instance"), `xarch/modules/rules/application/logic/tier_of.py:134`,
  `imports_written.py`. `keys.yaml` and README only where they still describe an old form as accepted (grep `@any`,
  `@own`, `bare`); lines ≤ 120 columns. `profile explain` output follows `keys.yaml`.
- Golden docs: regenerated, diff read, expected no change.

### Out of scope

- The `imports.also` refusal of `<word>.` when no part the tier tests lies in the word's folder (note 3.8): card 8.5.
  Mirrored handling is not touched beyond B1.
- Refusing `parts.X` beside `module.X` in one list (rulings line 34, later change).
- `structure` shadowing a part named `structure` (note 3.12).
- Any change to `Target`, the writers (`written_target`, `_place`, `_shown`), the rules, or what a valid profile
  allows.
- Corpora findings: not expected to move; if a recorded finding moves, stop and report rather than edit.

### Tests

Tiers in xarch: `tests/kernel/logic` and `tests/modules/*/application/logic` are the unit tier (pure functions, table
tests with `pytest.param(..., id=...)`); `tests/bootstrap` is the integration tier (the CLI through `CliRunner`, real
files). Every new test is written and seen failing before its code.

Unit (`tests/kernel/logic/test_targets.py`; unit because `target()` is a pure function of its arguments):

1. One row per B1 table row, with a repeating `modules/<module>/` profile, a second word (`units/<unit>/`), a part
   outside any folder, an importer inside and outside, mirrored, owner None (`alone`), and `place=True`: the exact
   problem text and `None`.
2. Rows that today assert an old form parses (`domain@any/values`, `domain@any`, bare names, `domain@own`, the old
   scope texts, `is not a target: use <part>, ...` at lines ~30-229) are rewritten to assert the B1 refusal. The
   module docstring no longer says "the old forms as before".
3. B5 rows: `orders.services` with a part `orders` declared; `module.contract` from outside for part owner, owner None,
   and place.
4. One row per value: a list of three old forms gives three problems (through `allowed_targets`, unit tier in
   `tests/modules/spec/application/logic/test_targets_written.py`).
5. The B4 helper: `parts.x`, `<word>.x`, `module.x/y` claimed; `os.environ`, `parts.nope`, plain `x` not claimed.

Unit (`tests/modules/spec/application/logic/`):

6. `test_imports_written.py` / `test_tiers.py`: each B2 row, through `tier_parts` and through a tier parse.
7. `test_parts_tree.py`: B3 refused keys (nested and top-level `<parts>`), and `<partsx>`, `parts/`, a part named
   `parts` still valid.
8. `test_profile_checks.py`, `test_profile_parsing.py`, `test_written_checks.py`, `test_evals*.py`: one B4 row per key
   listed, exact text; a reader's unclaimed value keeps today's text.
9. `tests/modules/rules/application/logic/` (own checks): the check target `part: [parts.x]` refused per B4;
   `place: [parts.x]` still accepted.

Integration (`tests/bootstrap/test_bundled_imports.py`; integration because it runs the shipped files through the
real `profile check` command):

10. B6, parametrized over `SHIPPED`.
11. An inline profile with several old forms on separate lines gives one problem line each through `profile check`
    (the "one problem per line" ruling, observed at the CLI).

Existing tests that hold old forms as accepted input (`tests/bootstrap/test_profile_explain.py`,
`test_profile_explain_words.py`, `tests/modules/rules/application/logic/test_places.py`, `test_tier_imports.py`,
`tests/modules/spec/application/test_select.py`, `test_explain.py`, `logic/test_profile_parsing.py`,
`test_profile_parsing_tests.py`, `tests/platform/test_yaml_writer.py`, and any fixture still writing a bare name
under `imports`) are rewritten to references, or to refusal assertions where the old form is what they prove. No test
is deleted to make the suite pass.

### Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run
xarch profile check architecture.yaml` (still OK, looser lines unchanged).

### Review focus for the planner

- A value refused twice (removal message plus a pattern, `must`-not-in-`may`, or duplicate problem): one per value.
- The replacement disagreeing with what `_reference` then accepts: a hint that, written, is refused again (other than
  the implied self-import row).
- Mirrored readers (`imports.also`) given `parts.` only for a bare repeating name.
- A B4 helper that claims `os.environ`-like dotted names or undeclared parts.
- `everything` or a part named `everything` broken by the dot-less branch.

---

## State of the branch (read first)

The card was taken over by hand after the first planning run hung: every task below is **already committed** on
`v030/task-8-4-spec-the-old-810682ee`, one commit per task, in this order:

| Task | Commit |
|---|---|
| 1 `target()` and a tier's `must` refuse the old forms | `1875fc1` |
| 2 the tree refuses `<parts>` | `8d057ce` |
| 3 `outside_imports` at every key outside `imports` | `6374d98` |
| 4 bundled profiles in their old forms; one problem per line | `b525ed1` |
| 5 CHANGELOG, README, docstrings, golden docs | `1981113` |
| 6 lines wrapped to 120; gates | `12a67e9` |

The code blocks below are what those commits hold. An executor working this plan: for each task, confirm the tests
named exist and pass and that the implementation matches the block shown (`git show <commit> -- <file>`); where it
does, the RED step is already history (the commit was made test-first) and the commit step is satisfied by the commit
in the table — do not make an empty commit. Where anything differs from this plan or a test fails, fix it under the
task's steps and commit as shown. Task 6's gates must be run fresh regardless.

## Global Constraints

- One wording for every 0.3.0 refusal of a value: `'<value>': <form> was removed in 0.3.0: write <new>`.
- Every old form refused, no warning, no window, no rewrite on load, no `profile migrate`.
- One problem per value; one problem per line of an inline profile with several old forms.
- No special-casing of a profile, its parts or the word `module`: the word comes from the paths of the profile read.
- No concrete instance name accepted, for tests or otherwise.
- `<word>.` from an importer outside the folder refused, never matching nothing.
- Keys outside `imports` keep plain names; the check target `place` keeps references.
- `Target` does not change; no new scope.
- Generated docs `docs/{cli,web,xarch}/testing.md` regenerated, never edited by hand, diff read; expected not to move.
- README and CHANGELOG lines under `[Unreleased]`.
- No comments in xarch's code (docstrings only); never `ruff --fix`; tests first and seen failing; recorded corpora
  not edited; Python only in the reader adapter and `xarch/architectures/presets/` data; `.claude/` out of commits;
  nothing pushed; line length 120.

## Review Focus

1. A value refused twice (removal plus a pattern problem, `must`-not-in-`may`, or `listed twice`): exactly one
   problem per value — pinned in Task 1 (`kernel:*Id` with `patterns=False`, `kernel:a b`, bare `api` in `must`,
   `[store, store]` in a tier's `must`) and Task 4 (a scenario-coverage guard whose tier is refused adds nothing).
2. A hint that, written, is refused again: `@own`/bare get `<word>.X` only where `_word_problem` accepts it, else
   `parts.X`; `platform@any` inside `platform` gets the implied text — pinned in Task 1 (`kernel@any` in `kernel`,
   `domain@own` from `cli`, `store@own` from another word's folder) and end to end in Task 4 (each problem's reference
   is the one the bundled profile held, and that profile loads).
3. Mirrored readers (`imports.also`) given `parts.` for a bare repeating name — pinned in Task 1 (`mirrored=True`
   rows give `module.domain`) and `test_profile_parsing_tests.py` (`also: [service]`).
4. `outside_imports` claiming `os.environ`-like names or undeclared parts — pinned in Task 3 (`os.environ`,
   `orders.domain`, `parts.nope`, plain `kernel`, `3` all unclaimed; `docs.entry: orders.api` and
   `fakes.for: [parts.nope]` keep the reader's text).
5. `everything`, or a part named `everything`, broken by the dot-less branch — pinned in Task 1 (`everything` alone
   unchanged where taken, in a list `stands alone`, and a part named `everything` told `parts.everything`).

---

### Task 1: `target()` and a tier's `must`/`types_only` refuse every old form

**Files:**
- Modify: `xarch/kernel/logic/targets.py` (module docstring lines 5-10; `TARGET` regex removed; `target()` body for a
  dot-less head; new `old_form`, `removed`, `BARE`, `_NOT_A_REFERENCE`; `_reference` uses `_NOT_A_REFERENCE`)
- Modify: `xarch/modules/spec/application/logic/imports_written.py` (module docstring, `tier_parts`, `_tier_part`)
- Test: `tests/kernel/logic/test_targets.py`, `tests/modules/spec/application/logic/test_targets_written.py`,
  `tests/modules/spec/application/logic/test_tiers.py`, `tests/modules/spec/application/logic/test_imports_written.py`,
  `tests/modules/spec/application/logic/test_profile_parsing.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py`,
  `tests/modules/rules/application/logic/test_own_checks.py`, `tests/modules/spec/application/test_select.py`

**Interfaces:**
- Consumes: `_reference`, `_word_problem(value, word, name, (name, path), owner, repeats, mirrored, alone) -> str | None`
  and `_implied(where, value, owner, again) -> str` already in `targets.py`; `repeat_of(repeats, path) -> Repeat | None`
  from `xarch/kernel/logic/placement.py`.
- Produces: `old_form(value: Any) -> tuple[str, str | None, str] | None` (name, scope `"any"`/`"own"`/None, tail);
  `removed(value: Any, form: str, instead: str) -> str`; `BARE = "a bare part name"` — all three imported by
  `imports_written.py`.

- [ ] **Step 1: Write the failing tests (kernel table)**

In `tests/kernel/logic/test_targets.py`, set the module docstring and fixtures, and replace the old `READ` table, the
old `test_a_target_that_is_not_one_is_none_with_its_problem` and `test_a_target_a_test_reads_is_read_from_the_instance_it_mirrors`
with the removal table:

```python
"""How a profile writes a target, read against the parts by their paths, the part that writes it and the profile's
repeating folders: the references parts.<part> and <word>.<part>, each read or refused with its one problem, and the
old forms (a bare name, @any, @own), each refused with the reference to write."""
import pytest

from xarch.kernel.logic.targets import target
from xarch.profile_values.placement import Repeat, Target

PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"), "kernel": ("kernel",),
         "kernel-logic": ("kernel", "logic"), "store": ("units", "*", "store"), "cli": ("cli",)}
REPEATS = (Repeat("module", ("modules",)), Repeat("unit", ("units",)))
SERVICES = ("services", PARTS["services"])
DOMAIN = ("domain", PARTS["domain"])
CLI = ("cli", PARTS["cli"])
KERNEL = ("kernel", PARTS["kernel"])
LEDGER = ("ledger", ("units", "*", "ledger"))
NOT_A_REFERENCE = "is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and :<pattern>"


def read(written, owner, parts=PARTS, repeats=REPEATS, patterns=True, mirrored=False, place=False,
         alone="a tier's folder", declared=None):
    problems: list[str] = []
    found = target(written, owner, parts, parts if declared is None else declared, "at", problems, patterns, mirrored,
                   alone=alone, repeats=repeats, place=place)
    return found, problems


REMOVED = "was removed in 0.3.0: write"
BARE = "a bare part name was removed in 0.3.0: write"
OWN_MODULE = "module.domain (this module's) or parts.domain (any module's)"


@pytest.mark.parametrize("written, owner, options, problem", [
    pytest.param("domain@any", SERVICES, {}, f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any"),
    pytest.param("domain@any/published", CLI, {}, f"at: 'domain@any/published': @any {REMOVED} parts.domain/published",
                 id="@any and a path"),
    pytest.param("domain/published@any", CLI, {}, f"at: 'domain/published@any': @any {REMOVED} parts.domain/published",
                 id="@any after the path"),
    pytest.param("domain@any:*Id", SERVICES, {}, f"at: 'domain@any:*Id': @any {REMOVED} parts.domain:*Id",
                 id="@any and a pattern"),
    pytest.param("domain@any", None, {}, f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any from a tier"),
    pytest.param("domain@own", SERVICES, {}, f"at: 'domain@own': @own {REMOVED} module.domain",
                 id="@own where the word is accepted"),
    pytest.param("store@own", LEDGER, {}, f"at: 'store@own': @own {REMOVED} unit.store", id="@own, a second word"),
    pytest.param("domain@own", CLI, {}, f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own from an importer outside the folder"),
    pytest.param("store@own", SERVICES, {}, f"at: 'store@own': @own {REMOVED} parts.store",
                 id="@own from another word's folder"),
    pytest.param("kernel@own", SERVICES, {}, f"at: 'kernel@own': @own {REMOVED} parts.kernel",
                 id="@own for a part in no repeating folder"),
    pytest.param("domain", SERVICES, {}, f"at: 'domain': {BARE} {OWN_MODULE}", id="a bare name, the word accepted"),
    pytest.param("store", LEDGER, {}, f"at: 'store': {BARE} unit.store (this unit's) or parts.store (any unit's)",
                 id="a bare name, the second word in place of module"),
    pytest.param("domain", CLI, {}, f"at: 'domain': {BARE} parts.domain", id="a bare name from outside the folder"),
    pytest.param("domain", None, {}, f"at: 'domain': {BARE} parts.domain", id="a bare name from a tier's folder"),
    pytest.param("domain", None, {"mirrored": True}, f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name a test mirrors"),
    pytest.param("domain@own", None, {"mirrored": True}, f"at: 'domain@own': @own {REMOVED} module.domain",
                 id="@own a test mirrors"),
    pytest.param("domain", None, {"place": True, "alone": "a check that names no part"},
                 f"at: 'domain': {BARE} parts.domain", id="a bare name in the place of a check that names no part"),
    pytest.param("domain", SERVICES, {"place": True}, f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name in the place of a check in the folder"),
    pytest.param("kernel", SERVICES, {}, f"at: 'kernel': {BARE} parts.kernel", id="a bare name in no repeating folder"),
    pytest.param("domain/values:*Id", SERVICES, {},
                 f"at: 'domain/values:*Id': {BARE} module.domain/values:*Id (this module's) or "
                 "parts.domain/values:*Id (any module's)", id="the tail follows each reference"),
    pytest.param("kernel:*Id", SERVICES, {"patterns": False}, f"at: 'kernel:*Id': {BARE} parts.kernel:*Id",
                 id="a pattern where the key takes none: the old form first"),
    pytest.param("kernel:a b", SERVICES, {}, f"at: 'kernel:a b': {BARE} parts.kernel:a b",
                 id="a bad pattern: the old form first"),
    pytest.param("nope", SERVICES, {}, "at: 'nope' names no part 'nope'", id="a part the profile has not"),
    pytest.param("nope@any", SERVICES, {}, "at: 'nope@any' names no part 'nope'", id="@any of a part it has not"),
    pytest.param("everything", SERVICES, {}, "at: 'everything' names no part 'everything'",
                 id="everything is no part: the key that takes it alone says so"),
    pytest.param("services", SERVICES, {},
                 "at: 'services' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="the part itself"),
    pytest.param("services@own", SERVICES, {},
                 "at: 'services@own' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="its own instance"),
    pytest.param("services@any", SERVICES, {}, f"at: 'services@any': @any {REMOVED} parts.services",
                 id="itself in every instance"),
    pytest.param("kernel", KERNEL, {}, "at: 'kernel' is implied: a part may always import itself; remove it",
                 id="itself, outside a repeating folder"),
    pytest.param("kernel@any", KERNEL, {}, "at: 'kernel@any' is implied: a part may always import itself; remove it",
                 id="@any of itself outside a repeating folder: never a hint refused again"),
    pytest.param("domain@foo", SERVICES, {}, f"at: 'domain@foo' {NOT_A_REFERENCE}", id="an unknown scope"),
    pytest.param("@any", SERVICES, {}, f"at: '@any' {NOT_A_REFERENCE}", id="a scope of no part"),
    pytest.param("domain@", SERVICES, {}, f"at: 'domain@' {NOT_A_REFERENCE}", id="an empty scope"),
    pytest.param("domain@any@own", SERVICES, {}, f"at: 'domain@any@own' {NOT_A_REFERENCE}", id="two scopes"),
    pytest.param("", SERVICES, {}, f"at: '' {NOT_A_REFERENCE}", id="empty text"),
    pytest.param(1, SERVICES, {}, f"at: 1 {NOT_A_REFERENCE}", id="no text"),
    pytest.param(["domain"], SERVICES, {}, f"at: ['domain'] {NOT_A_REFERENCE}", id="a list"),
])
def test_an_old_form_is_refused_with_the_reference_to_write(written, owner, options, problem):
    assert read(written, owner, **options) == (None, [problem])


def test_an_old_form_of_a_part_named_everything_is_told_parts_everything():
    assert read("everything", CLI, parts={"everything": ("everything",), "cli": ("cli",)}) == (
        None, [f"at: 'everything': {BARE} parts.everything"])


def test_an_old_form_of_a_part_declared_but_not_placed_is_none_with_no_problem():
    assert read("ghost@any", SERVICES, declared={*PARTS, "ghost"}) == (None, [])
```

Rewrite the remaining old-form rows of the file to references (same file):

```python
def test_a_name_pattern_is_any_text_but_whitespace_and_the_separators_of_a_target(pattern):
    assert read(f"parts.kernel:{pattern}", SERVICES) == (Target("kernel", "none", (), pattern), [])


@pytest.mark.parametrize("written", ["parts.kernel:a b", "parts.kernel:a@b", "parts.kernel:a:b"])
def test_a_name_pattern_with_whitespace_or_a_separator_is_refused(written):
    assert read(written, SERVICES) == (
        None, [f"at: {written!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` "
               "standing for any text"])


def test_what_names_no_part_is_named_in_the_callers_words():
    assert read("module.domain", None, alone="a check that names no part") == (
        None, ["at: 'module.domain': a check that names no part lies in no <module> folder, so it has no own module: "
               "write parts.domain"])
```

and replace `test_a_value_whose_head_holds_no_dot_is_read_in_the_old_forms` at the end with the B5 pins:

```python
@pytest.mark.parametrize("written, found", [
    pytest.param("parts.kernel/x.py", Target("kernel", "none", ("x.py",)), id="a dot in the path"),
    pytest.param("parts.kernel:a.b", Target("kernel", "none", (), "a.b"), id="a dot in the pattern"),
])
def test_a_dot_after_the_head_is_no_prefix(written, found):
    assert read(written, SERVICES) == (found, [])


def test_a_concrete_instance_name_is_refused_also_when_a_part_bears_that_name():
    parts = {**PARTS, "orders": ("orders",)}
    assert read("orders.services", DOMAIN, parts=parts) == (
        None, ["at: 'orders.services': 'orders' is neither parts nor a word of this profile (module, unit): a profile "
               "names no instance; write module.services or parts.services"])
```

(`module.contract` from `cli`, from a tier's folder and from a check with no `in.part` is already pinned by 8.1's rows
in the same file, which stay; `test_what_names_no_part_is_named_in_the_callers_words` above pins the check case.)

- [ ] **Step 2: Write the failing tests (readers of `target()` and a tier's `must`)**

`tests/modules/spec/application/logic/test_targets_written.py`: docstring, a `NOT_A_REFERENCE` constant, the read table
in references, and the one-problem-per-value list:

```python
"""How a profile writes what may be imported, on hand-made parts: the references parts.<part> and <word>.<part>, a path
below the part, a pattern where one is allowed, `everything`, and each target refused with why, an old form (a bare
part, @any, @own) with the reference to write."""
```

```python
NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                   ":<pattern>")
```

```python
@pytest.mark.parametrize("value, targets", [
    pytest.param(["module.service"], (Target("service", "own"),),
                 id="a part of its own repeating folder by its word is its own instance"),
    pytest.param(["parts.service"], (Target("service", "any"),), id="any instance"),
    pytest.param(["parts.shared/text"], (Target("shared", "none", ("text",)),), id="a path below a part"),
    pytest.param("everything", (Target(EVERYTHING),), id="everything, written alone"),
    pytest.param(None, (), id="nothing written is nothing more"),
])
```

```python
    pytest.param(["shared@any"], "'shared@any': @any was removed in 0.3.0: write parts.shared",
                 id="a scope on a part outside the repeating folder"),
    pytest.param(["module.api"], "'module.api' is implied: a part may always import itself, its own instance of the "
                                 "repeating folder; remove it (parts.api, another instance's too, stays allowed)",
                 id="itself"),
```

```python
    assert problems == ["tiers.guard.imports.may: {'parts.shared': 'types_only'} " + NOT_A_REFERENCE]


def test_each_old_form_of_a_list_is_its_own_problem_and_the_references_beside_them_are_read():
    assert written(["service", "parts.shared", "service@any", "shared/text"]) == ((Target("shared"),), [
        "parts.api.imports.may: 'service': a bare part name was removed in 0.3.0: write module.service (this "
        "module's) or parts.service (any module's)",
        "parts.api.imports.may: 'service@any': @any was removed in 0.3.0: write parts.service",
        "parts.api.imports.may: 'shared/text': a bare part name was removed in 0.3.0: write parts.shared/text"])
```

`tests/modules/spec/application/logic/test_tiers.py`: add `REMOVED = "was removed in 0.3.0: write"` after `TIER_USE`;
drop the two read rows `["store"]` ("a plain name still reads") and `["parts.store", "api"]`; replace the
`"the same part in both spellings"` refusal row with these rows:

```python
    pytest.param(["store"], f"'store': a bare part name {REMOVED} parts.store", id="a bare name"),
    pytest.param(["store@any"], f"'store@any': @any {REMOVED} parts.store", id="@any"),
    pytest.param(["store@own"], f"'store@own': @own {REMOVED} parts.store", id="@own"),
    pytest.param(["store/sql"], f"'store/sql': a bare part name {REMOVED} parts.store", id="a bare name and a path"),
    pytest.param(["store:*Id"], f"'store:*Id': a bare part name {REMOVED} parts.store",
                 id="a bare name and a pattern"),
    pytest.param(["parts.store", "store"], f"'store': a bare part name {REMOVED} parts.store",
                 id="a bare name beside its reference is the removal alone"),
    pytest.param(["nope"], "no part named 'nope'", id="a bare name of no part"),
    pytest.param(["store@foo"], "no part named 'store@foo'", id="an unknown scope"),
```

and add:

```python
def test_a_bare_name_written_twice_in_a_tier_s_must_is_refused_twice_and_not_listed_twice():
    assert problems(with_imports({"must": ["store", "store"]})) == [
        f"layered.yaml: tiers.integration.imports.must: 'store': a bare part name {REMOVED} parts.store"] * 2
```

Change the two `is not a target: use <part>, <part>@any, optionally followed by /<path>` expectations in
`test_tiers.py` (the `also` mark row and `test_a_mark_in_a_folder_tier_s_may_is_refused_as_any_entry_that_is_no_target`)
to `is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and :<pattern>`.

`tests/modules/spec/application/logic/test_imports_written.py`: add the `NOT_A_REFERENCE` constant above, the
`{3: "types_only"}` row becomes `f"3 {NOT_A_REFERENCE}"`, and the `must` row `["api"]` becomes `["module.api"]` with
`"'module.api' is not in imports.may, so no file could import it: add it there, or name a part the part may import"`.

`tests/modules/spec/application/logic/test_profile_parsing.py`: every old form that proved a read becomes a
reference (`["plugin.manifest", "parts.service", "parts.shared"]`, `["module.store", "parts.shared", "parts.hooks"]`,
`["parts.api", "parts.service/rules"]`, the `test_what_a_part_of_the_repeating_folder_may_import` table in
`module.`/`parts.`); every old-form refusal row asserts the removal. Add the constants:

```python
REMOVED = "was removed in 0.3.0: write"
NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                   ":<pattern>")
```

and the rows (in `test_a_part_in_another_repeating_folder_has_no_own_instance_so_an_old_form_is_told_parts`, which
replaces `..._so_a_bare_name_is_refused` and absorbs `test_a_part_in_another_repeating_folder_may_not_be_said_as_own`):

```python
@pytest.mark.parametrize("importer, name, expected", [
    pytest.param("hooks", "service", f"layered.yaml: parts.hooks.imports.may: 'service': a bare part name {REMOVED} "
                                     "parts.service", id="a plugin part names a module part bare"),
    pytest.param("service", "hooks", f"layered.yaml: parts.service.imports.may: 'hooks': a bare part name {REMOVED} "
                                     "parts.hooks", id="a module part names a plugin part bare"),
    pytest.param("hooks", "service@own", f"layered.yaml: parts.hooks.imports.may: 'service@own': @own {REMOVED} "
                                         "parts.service", id="a plugin part names a module part as its own"),
])
def test_a_part_in_another_repeating_folder_has_no_own_instance_so_an_old_form_is_told_parts(importer, name, expected):
    document = two_folders()
    part_of(document, importer).setdefault("imports", {})["may"] = [name]
    assert problems(document) == [expected]


def test_a_must_import_in_an_old_form_is_refused_once_with_its_reference():
    document = two_folders()
    part_of(document, "hooks").setdefault("imports", {})["may"] = ["parts.service"]
    part_of(document, "hooks").setdefault("imports", {})["must"] = ["service"]
    assert problems(document) == [
        f"layered.yaml: parts.hooks.imports.must: 'service': a bare part name {REMOVED} parts.service"]
```

In the `may` refusal table:

```python
    pytest.param("store", [3], f"layered.yaml: parts.store.imports.may: 3 {NOT_A_REFERENCE}", id="not text"),
    pytest.param("store", [""], f"layered.yaml: parts.store.imports.may: '' {NOT_A_REFERENCE}", id="empty"),
    pytest.param("store", ["service@own"], f"layered.yaml: parts.store.imports.may: 'service@own': @own {REMOVED} "
                                           "module.service", id="@own"),
    pytest.param("shared", ["api@own"], f"layered.yaml: parts.shared.imports.may: 'api@own': @own {REMOVED} parts.api",
                 id="@own from outside"),
    pytest.param("store", ["service@all"], f"layered.yaml: parts.store.imports.may: 'service@all' {NOT_A_REFERENCE}",
                 id="an unknown scope"),
    pytest.param("store", ["shared@any"], f"layered.yaml: parts.store.imports.may: 'shared@any': @any {REMOVED} "
                                          "parts.shared", id="@any on a part outside"),
    pytest.param("shared", ["api"], f"layered.yaml: parts.shared.imports.may: 'api': a bare part name {REMOVED} "
                                    "parts.api", id="a bare part inside, from outside"),
    pytest.param("store", ["service"], f"layered.yaml: parts.store.imports.may: 'service': a bare part name {REMOVED} "
                                       "module.service (this module's) or parts.service (any module's)",
                 id="a bare part inside, from inside"),
    pytest.param("store", ["parts.shared/../x"], "layered.yaml: parts.store.imports.may: 'parts.shared/../x' has an "
                                                 "invalid path after the part", id="a climbing path"),
    pytest.param("store", ["parts.shared/"], "layered.yaml: parts.store.imports.may: 'parts.shared/' has an invalid "
                                             "path after the part", id="a trailing slash"),
    pytest.param("store", ["store"], "layered.yaml: parts.store.imports.may: 'store' is implied: a part may always "
                                     "import itself, its own instance of the repeating folder; remove it "
                                     "(parts.store, another instance's too, stays allowed)", id="itself in an instance"),
```

In the `must` refusal table:

```python
    pytest.param(["module.api"], "layered.yaml: parts.store.imports.must: 'module.api' is not in imports.may, so no "
                                 "file could import it: add it there, or name a part the part may import",
                 id="a part it may not import"),
    pytest.param(["module.store"], "layered.yaml: parts.store.imports.must: 'module.store' is implied: a part may "
                                   "always import itself, its own instance of the repeating folder; remove it "
                                   "(parts.store, another instance's too, stays allowed)", id="the part itself"),
    pytest.param(["api"], f"layered.yaml: parts.store.imports.must: 'api': a bare part name {REMOVED} module.api (this "
                          "module's) or parts.api (any module's)", id="an old form, refused once"),
```

And the equivalence test becomes a refusal test:

```python
def test_references_reach_every_target_spec_reads_and_the_old_forms_are_each_refused_with_one():
    new = parsed(referencing({"may": ["module.domain", "parts.kernel", {"parts.domain": "types_only"}],
                              "must": ["parts.kernel"]},
                             {"imports": {"may": ["parts.kernel"], "also": ["module.domain/values"]}}))
    old = (referencing({"may": ["domain", "kernel", {"domain@any": "types_only"}], "must": ["kernel"]},
                       {"imports": {"may": ["kernel"], "also": ["domain/values"]}}))
    services, (guard,) = new.parts["services"], new.tiers
    assert (new.rules["services"], services.imports_must, services.imports_types_only) == (
        (Target("domain", "own"), Target("kernel"), Target("domain", "any")), (Target("kernel"),),
        (Target("domain", "any"),))
    assert (guard.imports_may, guard.imports_also) == ((Target("kernel"),), (Target("domain", "own", ("values",)),))
    own = f"a bare part name {REMOVED} module.domain (this module's) or parts.domain (any module's)"
    assert problems(old) == [
        f"layered.yaml: parts.services.imports.may: 'domain': {own}",
        f"layered.yaml: parts.services.imports.may: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: parts.services.imports.may: 'domain@any': @any {REMOVED} parts.domain",
        f"layered.yaml: parts.services.imports.must: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: tiers.guard.imports.may: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: tiers.guard.imports.also: 'domain/values': a bare part name {REMOVED} module.domain/values "
        "(this module's) or parts.domain/values (any module's)"]
```

`tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

```python
def test_what_the_tests_of_a_tier_may_also_import_are_targets_a_word_naming_the_mirrored_instance():
    document = covered()
    document["tiers"]["integration"]["imports"] = {"also": ["module.service", "parts.shared", "parts.api"]}
    tiers = parsed(document).tiers
    assert [t.imports_also for t in tiers] == [(), (Target("service", "own"), Target("shared"), Target("api", "any"))]
```

```python
    pytest.param({"imports": {"also": ["service@own"]}}, "layered.yaml: tiers.unit.imports.also: 'service@own': @own "
                                                         "was removed in 0.3.0: write module.service",
                 id="also of the mirrored instance written out"),
    pytest.param({"imports": {"also": ["service"]}}, "layered.yaml: tiers.unit.imports.also: 'service': a bare part "
                                                     "name was removed in 0.3.0: write module.service (this module's) "
                                                     "or parts.service (any module's)", id="also of a bare name"),
```

```python
def test_a_tier_folder_follows_the_rules_it_had_and_its_allowance_is_a_part_s_may_import():
    document = covered()
    document["tiers"]["guard"] = {"folder": "src/billing/api",
                                  "imports": {"may": ["api", "service@own", "repo", "parts.shared/"]}}
    assert problems(document) == [
        "layered.yaml: tiers.guard.folder: 'src/billing/api' is the folder of part 'api', which places its tests: give "
        "`folder` only to a folder that mirrors no part",
        "layered.yaml: tiers.guard.imports.may: 'api': a bare part name was removed in 0.3.0: write parts.api",
        "layered.yaml: tiers.guard.imports.may: 'service@own': @own was removed in 0.3.0: write parts.service",
        "layered.yaml: tiers.guard.imports.may: 'repo' names no part 'repo'",
        "layered.yaml: tiers.guard.imports.may: 'parts.shared/' has an invalid path after the part"]
```

`tests/modules/rules/application/logic/test_own_checks.py` (a check's `place`):

```python
def test_a_place_in_an_old_form_is_refused_with_the_reference_the_part_the_scope_names_would_write():
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("domain/values", "kernel@any")),)),
                          (Saying("m", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(written={"placed": placed}))
    assert refused.value.problems == (
        "checks.placed.may_not.place: 'domain/values': a bare part name was removed in 0.3.0: write "
        "module.domain/values (this module's) or parts.domain/values (any module's)",
        "checks.placed.may_not.place: 'kernel@any': @any was removed in 0.3.0: write parts.kernel")
```

`tests/modules/spec/application/test_select.py`, the `BROKEN` expectation:

```python
                 ProfileRefused(
                     f"{FILE}: parts.api.imports.may: 'api@mine' is not a reference: write parts.<part> or "
                     f"<word>.<part>, optionally followed by /<path> and :<pattern>\n{FILE}: parts.api.imports.may: "
                     "'nowhere' names no part 'nowhere'"),
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/test_targets_written.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/test_select.py`
Expected: FAIL — the removal rows get today's old-form reads (`Target(...)`, `says what a bare name already says`,
`is not a target: use <part>, ...`), and `test_tiers.py`'s bare-name rows read `("store",)`.

- [ ] **Step 4: Implement `target()`'s refusal in `xarch/kernel/logic/targets.py`**

Module docstring, second paragraph's end:

```python
`/<path>` and, where the key takes one, `:<pattern>`. The old forms, `<part>@any`, `<part>@own` and the bare name of a
part, were removed in 0.3.0: each is refused with the reference to write, computed from the profile. A target is
written back as a reference (see written_target), which reads back as itself."""
```

Imports and constants (drop `root_of` and `TARGET`):

```python
from xarch.kernel.logic.placement import repeat_of
from xarch.kernel.placement import EACH
from xarch.profile_values.placement import Repeat, Target

NAME_PATTERN = re.compile(r"[^\s@/:]+")
"""A name pattern: any text but whitespace and the separators of a target, `*` standing for any text."""
_HEAD = re.compile(r"[^/:]*")
_REFERENCE = re.compile(r"(?P<part>[^/:]*)(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?", re.DOTALL)
_NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                    ":<pattern>")
BARE = "a bare part name"
"""How a removal names the old form that writes a part by its name alone."""
```

`target()`'s docstring end and body after the reference branch, plus the two new helpers:

```python
    own instance of the repeating folder is the one it mirrors: `<word>.<part>` there is that instance. place says the
    value is a check's `place`, where a prefix that is no word may be a dotted name of code. A value in an old form
    (see old_form) is None, refused with the reference to write: `parts.<part>` for `@any`; for `@own` and a bare name,
    `<word>.<part>` where that reference is accepted, else `parts.<part>`; or, when the reference would be the part
    itself, as implied."""
    if isinstance(value, str) and "." in _HEAD.match(value)[0]:
        return _reference(value, owner, parts, declared, where, problems, patterns, mirrored, alone, repeats, place)
    old = old_form(value)
    if old is None:
        problems.append(f"{where}: {value!r} {_NOT_A_REFERENCE}")
        return None
    name, scope, tail = old
    path = parts.get(name)
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    held = repeat_of(repeats, path)
    own = (scope != "any" and held is not None
           and _word_problem(value, held.word, name, (name, path), owner, repeats, mirrored, alone) is None)
    if owner is not None and name == owner[0] and (own or EACH not in path):
        problems.append(_implied(where, value, owner, f"parts.{name}"))
        return None
    everywhere = f"parts.{name}{tail}"
    if held is None or not own:
        instead = everywhere
    elif scope == "own":
        instead = f"{held.word}.{name}{tail}"
    else:
        instead = f"{held.word}.{name}{tail} (this {held.word}'s) or {everywhere} (any {held.word}'s)"
    problems.append(f"{where}: {removed(value, BARE if scope is None else f'@{scope}', instead)}")
    return None


def old_form(value: Any) -> tuple[str, str | None, str] | None:
    """What a value whose head holds no dot writes in the old forms: the name of the part, the scope (`any`, `own`,
    None for a bare name) and the tail, `/<path>` and `:<pattern>` as written, the scope taken out wherever it stands
    before the pattern; None when it writes none of them."""
    if not isinstance(value, str):
        return None
    before, colon, pattern = value.partition(":")
    body, at, after = before.partition("@")
    scope = None
    if at:
        scope, slash, below = after.partition("/")
        body += slash + below
        if scope not in ("any", "own"):
            return None
    name = body.partition("/")[0]
    if not name or "@" in body:
        return None
    return name, scope, body[len(name):] + colon + pattern


def removed(value: Any, form: str, instead: str) -> str:
    """The one wording of a value refused for a form 0.3.0 removed: the value, the form and what to write instead."""
    return f"{value!r}: {form} was removed in 0.3.0: write {instead}"
```

In `_reference`, the malformed-reference problem uses the shared text:

```python
        problems.append(f"{where}: {value!r} {_NOT_A_REFERENCE}")
```

Keep `_pattern_problem` and `_steps`: `_reference` still calls both.

- [ ] **Step 5: Implement the tier refusal in `xarch/modules/spec/application/logic/imports_written.py`**

```python
from xarch.kernel.logic.targets import BARE, old_form, removed
```

Module docstring line 14: `tier_parts: whole parts, `parts.<part>` alone, for a tier's tests lie in no instance.`

```python
def tier_parts(value: Any, declared: set[str], where: str, problems: list[str]) -> list[str]:
    """The parts a tier's `imports.must` or `imports.types_only` names, by name, in the order written: each entry
    `parts.<part>`, a part declared. An entry that names no whole part declared, one in an old form, or a part named
    twice, adds its one problem, and the other entries are still read."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of part names")
        return []
    found: list[str] = []
    for item in value:
        name = _tier_part(item, declared, where, problems)
```

```python
def _tier_part(item: Any, declared: set[str], where: str, problems: list[str]) -> str | None:
    """The part an entry of a tier's `must` or `types_only` names, the name after `parts.`; None, with its problem, for
    an entry that is no text, for one in an old form (the text before its first `/` or `:` holds no dot), told
    `parts.<part>` when it names a part declared, for `<word>.<part>`, which names an instance, and for a reference
    that goes on to a path or a pattern."""
    if not isinstance(item, str):
        problems.append(f"{where}: no part named {item!r}")
        return None
    if "." not in re.split("[/:]", item, maxsplit=1)[0]:
        old = old_form(item)
        if old is None or old[0] not in declared:
            problems.append(f"{where}: no part named {item!r}")
        else:
            problems.append(f"{where}: {removed(item, BARE if old[1] is None else f'@{old[1]}', f'parts.{old[0]}')}")
        return None
```

(the rest of `_tier_part`, the `parts.` branch from 8.3, is unchanged).

- [ ] **Step 6: Run the tests to verify they pass**

Run the Step 3 command. Expected: PASS. Then `timeout 600 uv run pytest -q -x tests/modules tests/kernel` — expected
PASS; any other test still writing an old form under `imports` as accepted input is rewritten to a reference (or to a
refusal assertion where the old form is what it proves), never deleted.

- [ ] **Step 7: Confirm the old texts are unreachable**

Run: `grep -rn "says what a bare name\|is not a target: use\|unknown scope\|lies in another repeating folder\|drop '@\|say {name}@any\|^TARGET = re" xarch/`
Expected: no output.

- [ ] **Step 8: Commit**

```bash
git add xarch/kernel/logic/targets.py xarch/modules/spec/application/logic/imports_written.py tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/test_targets_written.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_imports_written.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/test_select.py
git commit -m "target() refuses every old form, <part>@any, <part>@own and the bare name of a part, with the reference to write computed from the profile; a tier's imports.must and imports.types_only refuse a dot-less entry with parts.<part>; one problem per value"
```

(Landed as `1875fc1`.)

---

### Task 2: The tree's reader refuses the repeating word `<parts>`

**Files:**
- Modify: `xarch/modules/spec/application/logic/parts_tree.py` (constant after `_REPEATING`; `_steps`)
- Test: `tests/modules/spec/application/logic/test_parts_tree.py`

**Interfaces:**
- Consumes: `walked(value) -> PartsTree` (test helper already in the file), `_steps(key, problems)`.
- Produces: nothing new for other tasks.

- [ ] **Step 1: Write the failing tests**

After the imports of `test_parts_tree.py`:

```python
RESERVED = ("has the step `<parts>`: `<parts>` is reserved: `parts.` names a part in every instance; give the "
            "repeating folder another word")
```

Three rows in `test_each_refusal_of_the_tree_says_where_and_what_to_write`'s table, before the `17` row:

```python
    pytest.param({"units/<parts>/store/": {"role": "r"}}, f"parts: 'units/<parts>/store/' {RESERVED}",
                 id="15 the word parts in a joined key"),
    pytest.param({"units/": {"<parts>/": {"store/": {"role": "r"}}}}, f"parts: '<parts>/' {RESERVED}",
                 id="15 the word parts in a nested key"),
    pytest.param({"<parts>/x.py": {"role": "r"}}, f"parts: '<parts>/x.py' {RESERVED}",
                 id="15 the word parts at the top"),
```

And after that test:

```python
@pytest.mark.parametrize("value, names", [
    pytest.param({"units/<partsx>/store/": {"role": "r"}}, ["store"], id="a word that starts with parts"),
    pytest.param({"units/<sub-parts>/store/": {"role": "r"}}, ["store"], id="a word that ends with parts"),
    pytest.param({"parts/": {"store/": {"role": "r"}}}, ["store"], id="a plain folder named parts"),
    pytest.param({"parts/": {"role": "r"}}, ["parts"], id="a part named parts"),
])
def test_only_the_repeating_word_parts_is_reserved(value, names):
    tree = walked(value)
    assert (tree.problems, [part.name for part in tree.parts]) == ((), names)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 120 uv run pytest -q tests/modules/spec/application/logic/test_parts_tree.py`
Expected: FAIL on the three `15 the word parts` rows (no problem said); the four valid rows PASS already.

- [ ] **Step 3: Implement**

In `parts_tree.py`, after `_REPEATING`:

```python
_RESERVED = "<parts>"
```

and `_steps`:

```python
def _steps(key: str, problems: list[str]) -> tuple[str, ...] | None:
    """The steps a folder or file key writes, `<word>` as written; None, said, when one of them is no step or is the
    repeating folder `<parts>`, whose word a reference keeps for every instance."""
    steps = tuple((key[:-1] if key.endswith("/") else key).split("/"))
    if any(step in ("", ".", "..") or "\\" in step for step in steps):
        problems.append(f"parts: '{key}' has an empty, `.` or `..` step")
```

(the existing branches unchanged) then, before `else: return steps`:

```python
    elif _RESERVED in steps:
        problems.append(f"parts: '{key}' has the step `{_RESERVED}`: `{_RESERVED}` is reserved: `parts.` names a part "
                        "in every instance; give the repeating folder another word")
```

`xarch/kernel/logic/placement.py` is not touched.

- [ ] **Step 4: Run the tests to verify they pass**

Run the Step 2 command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/parts_tree.py tests/modules/spec/application/logic/test_parts_tree.py
git commit -m "The reader of the parts tree refuses a repeating folder written <parts>, at any depth, one problem per key; <partsx>, <sub-parts>, a plain folder parts/ and a part named parts stay valid"
```

(Landed as `8d057ce`.)

---

### Task 3: A key outside `imports` refuses a prefixed part name, through `outside_imports`

**Files:**
- Modify: `xarch/kernel/logic/targets.py` (new `outside_imports`, at the end)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (`layer_chains`, `part_names`, `scenario_places`)
- Modify: `xarch/modules/spec/application/logic/holds_written.py` (`holds`, `_kind`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (`parse_profile`, `_fakes`, `_guards`,
  `_scenario_coverage`, `_substance`, `_no_twins`, `_listed_parts`, `_docs`)
- Modify: `xarch/modules/spec/application/logic/written_checks.py` (`checks`, `_check`, `scope`, `_quantified`)
- Modify: `xarch/modules/spec/application/logic/evals.py` (`evals`, `_placement`, `_alike`, `_lines`, `_own`, `_within`)
- Modify: `xarch/modules/rules/application/logic/own_checks.py` (`_match`, the `PARTS` form)
- Test: `tests/kernel/logic/test_targets.py`, `tests/modules/spec/application/logic/test_profile_parsing.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py`,
  `tests/modules/spec/application/logic/test_written_checks.py`, `tests/modules/spec/application/logic/test_evals.py`,
  `tests/modules/rules/application/logic/test_own_checks.py`

**Interfaces:**
- Consumes: nothing from Task 1 but the module.
- Produces: `outside_imports(value: Any, declared: Collection[str], words: Collection[str]) -> str | None` — the
  problem text without the address (`"'parts.store': names a part outside imports: write store"`), or None when the
  value is not claimed. New keyword-only `words: Collection[str]` on `ck.part_names`, `ck.layer_chains`,
  `ck.scenario_places`, `holds_written.holds`, `written_checks.checks`, `written_checks.scope`, `evals.evals`;
  positional `words` on the private helpers listed above. `parse_profile` computes
  `words = tuple(repeat.word for repeat in built.repeats)`; `own_checks._match` computes
  `words = [repeat.word for repeat in profile.repeats]`.

- [ ] **Step 1: Write the failing helper test**

`tests/kernel/logic/test_targets.py`: import `outside_imports` beside `target`, and at the end:

```python
@pytest.mark.parametrize("written, problem", [
    pytest.param("parts.kernel", "'parts.kernel': names a part outside imports: write kernel", id="parts"),
    pytest.param("module.domain", "'module.domain': names a part outside imports: write domain", id="a word"),
    pytest.param("unit.store", "'unit.store': names a part outside imports: write store", id="a second word"),
    pytest.param("module.domain/values", "'module.domain/values': names a part outside imports: write domain",
                 id="a path dropped"),
    pytest.param("parts.kernel:*Id", "'parts.kernel:*Id': names a part outside imports: write kernel",
                 id="a pattern dropped"),
    pytest.param("os.environ", None, id="a prefix that is no word"),
    pytest.param("orders.domain", None, id="an instance named"),
    pytest.param("parts.nope", None, id="a part not declared"),
    pytest.param("kernel", None, id="a plain name"),
    pytest.param(3, None, id="no text"),
])
def test_a_key_outside_imports_is_told_the_plain_name_of_a_prefixed_part(written, problem):
    assert outside_imports(written, PARTS, ("module", "unit")) == problem
```

- [ ] **Step 2: Write the failing reader tests**

`tests/modules/spec/application/logic/test_profile_parsing.py` — replace
`test_a_reference_outside_imports_is_still_no_part_name` with:

```python
def built_by(names: list) -> dict:
    document = layered()
    part_of(document, "service")["holds"] = {"classes": {"built_by": names}}
    return document


OUTSIDE = "names a part outside imports: write"


@pytest.mark.parametrize("document, problem", [
    pytest.param(built_by(["parts.store"]), f"parts.service.holds.classes.built_by: 'parts.store': {OUTSIDE} store",
                 id="holds.classes.built_by"),
    pytest.param(covered(fakes={"folder": "fakes", "for": ["parts.store"]}),
                 f"fakes.for: 'parts.store': {OUTSIDE} store", id="fakes.for"),
    pytest.param(covered(guards={"no-twins": {"translated": ["module.store"]}}),
                 f"guards.no-twins.translated: 'module.store': {OUTSIDE} store", id="guards.no-twins.translated"),
    pytest.param(covered(guards={"pass-through": {"parts": ["parts.service"]}}),
                 f"guards.pass-through.parts: 'parts.service': {OUTSIDE} service", id="guards.pass-through.parts"),
    pytest.param(covered(guards={"no-callbacks": {"parts": ["module.service/x"]}}),
                 f"guards.no-callbacks.parts: 'module.service/x': {OUTSIDE} service", id="a path dropped"),
    pytest.param(layered(layers={"app": ["parts.store", "api"]}), f"layers.app: 'parts.store': {OUTSIDE} store",
                 id="layers"),
    pytest.param(layered(docs={"entry": "module.api"}), f"docs.entry: 'module.api': {OUTSIDE} api", id="docs.entry"),
    pytest.param(layered(docs={"entry": "orders.api"}), "docs.entry: no part named 'orders.api'",
                 id="a prefix that is no word keeps the reader's text"),
    pytest.param(covered(fakes={"folder": "fakes", "for": ["parts.nope"]}), "fakes.for: no part named 'parts.nope'",
                 id="a part not declared keeps the reader's text"),
])
def test_a_key_outside_imports_refuses_a_prefixed_name_with_the_plain_one(document, problem):
    assert problems(document) == [f"layered.yaml: {problem}"]
```

`tests/modules/spec/application/logic/test_profile_parsing_tests.py`, in the scenario-coverage refusal table after the
`"repo"` row:

```python
    pytest.param({"results": "parts.api"}, [f"{SCENARIOS}.results: 'parts.api': names a part outside imports: "
                                            "write api"], id="a prefixed name"),
```

`tests/modules/spec/application/logic/test_written_checks.py`: `read()` and the `BRACE` test pass
`words=("module",)` to `checks(...)`; add to the refusal table:

```python
    pytest.param({"x": {**SMALL, "in": {"part": "parts.api"}}},
                 ["checks.x.in.part: 'parts.api': names a part outside imports: write api"], id="a part by a reference"),
    pytest.param({"x": {**SMALL, "in": {"part": "orders.api"}}},
                 ["checks.x.in.part: no part named 'orders.api': write one of api, service, shared, store, or "
                  "structure"], id="a prefix that is no word keeps the reader's text"),
    pytest.param({"x": {**{k: v for k, v in SMALL.items() if k != "may_not"}, "read": "class",
                        "must_be_reached": {"from": {"part": "module.api"}, "through": "names-mentioned"}}},
                 ["checks.x.must_be_reached.from.part: 'module.api': names a part outside imports: write api"],
                 id="a part reached from, by a reference"),
```

`tests/modules/spec/application/logic/test_evals.py`, three rows in their tables:

```python
    pytest.param({"placement": {"lines": {"parts.store": 0.2}}}, "evals.placement.lines: 'parts.store': names a part "
                                                                 "outside imports: write store",
                 id="a part named by a reference"),
```

```python
    pytest.param({"in": {"part": "module.store"}}, "evals.rule.in.part: 'module.store': names a part outside imports: "
                                                   "write store", id="a scope naming a part by a reference"),
```

```python
    pytest.param(alike(("parts.store", "shared")), "evals.placement.alike[0]: 'parts.store': names a part outside "
                                                   "imports: write store", id="a part named by a reference"),
```

`tests/modules/rules/application/logic/test_own_checks.py`:

```python
def test_a_part_target_written_as_a_reference_is_told_the_plain_name_and_a_place_still_takes_one():
    named = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                         Quantified(MAY_NOT, (WrittenTarget("part", ("parts.kernel", "module.domain", "ghost")),)),
                         (Saying("m", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(written={"named": named}))
    assert refused.value.problems == (
        "checks.named.may_not.part: 'parts.kernel': names a part outside imports: write kernel",
        "checks.named.may_not.part: 'module.domain': names a part outside imports: write domain",
        "checks.named.may_not.part: no part named 'ghost'")
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("parts.kernel",)),)), (Saying("m", "f"),))
    (check,) = resolved(profile(written={"placed": placed})).checks
    assert check.rule.targets == (Match("place", places=(Target("kernel"),)),)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/logic/test_evals.py tests/modules/rules/application/logic/test_own_checks.py`
Expected: FAIL — `ImportError: cannot import name 'outside_imports'` for the kernel file; `TypeError: ... unexpected
keyword argument 'words'` in `test_written_checks.py`; the readers say `no part named 'parts.store'`.

- [ ] **Step 4: Implement the helper in `xarch/kernel/logic/targets.py`**

At the end of the file:

```python
def outside_imports(value: Any, declared: Collection[str], words: Collection[str]) -> str | None:
    """What is wrong with a value of a key outside `imports` that names a part by its plain name, written as a
    reference: its prefix `parts` or one of words, the profile's, and its part declared, told the plain name to write;
    None for any other value, which the key's reader words."""
    if not isinstance(value, str):
        return None
    prefix, dot, rest = value.partition(".")
    name = re.split("[/:]", rest, maxsplit=1)[0]
    if not dot or (prefix != "parts" and prefix not in words) or name not in declared:
        return None
    return f"{value!r}: names a part outside imports: write {name}"
```

- [ ] **Step 5: Call it from `profile_checks.py`**

`from xarch.kernel.logic.targets import outside_imports`. Then:

```python
def layer_chains(value: Any, parts: dict[str, Part], declared: set[str], rules: dict[str, tuple[Target, ...]],
                 problems: list[str], *, words: Collection[str]) -> dict[str, tuple[str, ...]]:
```

with the per-part check in the chain loop:

```python
        for part in chain:
            if (prefixed := outside_imports(part, declared, words)) is not None:
                problems.append(f"{where}: {prefixed}")
                ok = False
            elif not isinstance(part, str) or part not in declared:
                problems.append(f"{where}: no part named {part!r}")
                ok = False
```

```python
def part_names(value: Any, declared: Collection[str], where: str, problems: list[str], *,
               words: Collection[str]) -> list[str]:
    """The parts a key outside `imports` names, by their plain names, in the order written; a name that is no part
    declared, one written as a reference (its prefix `parts` or one of words), or one listed twice adds its problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of part names")
        return []
    found: list[str] = []
    for name in value:
        if (prefixed := outside_imports(name, declared, words)) is not None:
            problems.append(f"{where}: {prefixed}")
        elif not isinstance(name, str) or name not in declared:
            problems.append(f"{where}: no part named {name!r}")
        elif name in found:
            problems.append(f"{where}: {name!r} is listed twice")
```

```python
def scenario_places(results: Any, tier: Any, suffix: Any, parts: dict[str, Part], declared: set[str],
                    tiers: tuple[Tier, ...], where: str, problems: list[str], language: Language, *,
                    words: Collection[str]) -> None:
    """The part holding the result unions lies in a repeating folder, the tier is declared and tests that part, and the
    suffix is the end of a name."""
    part = parts.get(results) if isinstance(results, str) else None
    if part is None:
        if (prefixed := outside_imports(results, declared, words)) is not None:
            problems.append(f"{where}.results: {prefixed}")
        elif not isinstance(results, str) or results not in declared:
            problems.append(f"{where}.results: no part named {results!r}")
```

- [ ] **Step 6: Thread `words` through `holds_written.py`**

```python
def holds(value: Any, where: str, declared: Collection[str], problems: list[str], *,
          words: Collection[str]) -> tuple[Held, ...]:
    """The kinds the `holds` of the part at where lists, each with its settings, in the order of KINDS; none when it
    is refused, each problem added to problems; words are the profile's, which a part a setting names never takes."""
```

its last line passes `words` to `_kind(kind, value[kind], "classes" in value, f"{at}.{kind}", declared, problems, words)`;
`_kind(..., problems: list[str], words: Collection[str])` calls
`ck.part_names(settings["built_by"], declared, f"{at}.built_by", problems, words=words)`.

- [ ] **Step 7: Thread `words` through `profile_parsing.py`**

`from xarch.kernel.logic.targets import outside_imports`. In `parse_profile`, after `parts = built.parts`:

```python
    words = tuple(repeat.word for repeat in built.repeats)
```

and pass it: `_substance(specs[part], item, declared, problems, words)`;
`ck.layer_chains(document["layers"], parts, declared, rules, problems, words=words)`;
`_fakes(document["fakes"], parts, declared, problems, language, words)`;
`_guards(..., problems, language, words)`; `_docs(document.get("docs", {}), declared, files, problems, words)`;
`own_checks.checks(document["checks"], declared, tiers, language, problems, words=words)`;
`evals(document["evals"], declared, language, problems, words=words)`.

Each private helper takes a trailing positional `words: Collection[str]` and passes it on:
`_fakes` → `ck.part_names(value["for"], declared, f"{where}.for", problems, words=words)`;
`_guards` → `_scenario_coverage(..., language, words)`, `_no_twins(spec, declared, parts, where, problems, words)`,
`_listed_parts(spec, declared, parts, where, *_LISTED[kind], problems, words)`;
`_scenario_coverage` → `ck.scenario_places(..., language, words=words)`;
`_substance` → `held_kinds(spec["holds"], where, declared, problems, words=words)`;
`_no_twins` → `ck.part_names(spec["translated"], declared, f"{where}.translated", problems, words=words)`;
`_listed_parts` → `ck.part_names(spec["parts"], declared, f"{where}.parts", problems, words=words)`.

`_docs`:

```python
def _docs(value: Any, declared: set[str], files: Collection[str], problems: list[str],
          words: Collection[str]) -> tuple[str, tuple, tuple]:
```

```python
    entry = value.get("entry", "")
    prefixed = outside_imports(entry, declared, words) if "entry" in value else None
    if prefixed is not None or ("entry" in value and (not isinstance(entry, str) or entry not in declared)):
        problems.append(f"docs.entry: {prefixed or f'no part named {entry!r}'}")
        entry = ""
```

- [ ] **Step 8: Thread `words` through `written_checks.py`**

`from collections.abc import Collection, Mapping` and `from xarch.kernel.logic.targets import outside_imports`.

```python
def checks(value: Any, declared: set[str], tiers: tuple[Tier, ...], language: Language,
           problems: list[str], *, words: Collection[str]) -> dict[str, WrittenCheck]:
    """Every check of the map, by its id, as it comes back (see the module); one with a problem is left out, and the
    problem said at its address. words are the profile's, which the part a scope names never takes."""
```

`_check(body, where, declared, tiers, language, problems, words)` calls
`scope(body.get("in", {}), f"{where}.in", declared, tiers, problems, words=words)` and
`_quantified(slot, body[slot], f"{where}.{slot}", declared, tiers, problems, words)`; `_quantified` calls
`scope(value.get("from", {}), f"{where}.from", declared, tiers, problems, words=words)`.

```python
def scope(value: Any, where: str, declared: set[str], tiers: set[str], problems: list[str], *,
          words: Collection[str]) -> Scope:
    """The files a check or an eval reads: their kind, the part, the tier and the filters; a part written as a reference
    (its prefix `parts` or one of words) is told its plain name."""
```

with, between the `part in declared` branch and the `no part named` `else`:

```python
        elif (prefixed := outside_imports(part, declared, words)) is not None:
            problems.append(f"{where}.part: {prefixed}")
```

- [ ] **Step 9: Thread `words` through `evals.py`**

`from xarch.kernel.logic.targets import outside_imports`.

```python
def evals(value: Any, declared: Collection[str], language: Language, problems: list[str], *,
          words: Collection[str]) -> tuple[dict[str, float], tuple[Examples, Examples], dict[str, Eval], Groups]:
    """The line of each part the profile writes one for, by part; placement's own flagged and clean examples; every
    eval of the profile's own, by id; and the groups of parts placement reads alike; each in the order of the file, an
    eval or a group with a problem left out. words are the profile's, which a part these name never takes."""
```

`_own(body, f"evals.{name}", declared, language, problems, words)`, `_placement(..., problems, words)`,
`_lines(placement["lines"], declared, problems, words)`, `_alike(placement["alike"], declared, problems, words)`,
`_within(body.get("in", {}), f"{where}.in", declared, problems, words)` and in `_within`
`scope(value, where, set(declared), set(), problems, words=words)`.

`_alike`'s part check:

```python
        problems += [f"{at}: {prefixed}" if (prefixed := outside_imports(name, declared, words)) is not None
                     else f"{at}: {name!r} is not a part of this profile: name a part under parts" for name in group
                     if name not in declared]
```

`_lines`' loop:

```python
    for part, line in value.items():
        if (prefixed := outside_imports(part, declared, words)) is not None:
            problems.append(f"{where}: {prefixed}")
        elif part not in declared:
            problems.append(f"{where}: {part!r} is not a part of this profile: name a part under parts")
```

- [ ] **Step 10: Call it from `own_checks._match`**

`from xarch.kernel.logic.targets import outside_imports, target`, and the `PARTS` form:

```python
    if form == PARTS:
        words = [repeat.word for repeat in profile.repeats]
        prefixed = [said for v in values if (said := outside_imports(v, profile.parts, words)) is not None]
        problems += [f"{where}.part: {said}" for said in prefixed]
        missing = [v for v in values if v not in profile.parts and outside_imports(v, profile.parts, words) is None]
        if missing:
            problems.append(f"{where}.part: no part named {', '.join(map(repr, missing))}")
        if prefixed or missing:
            return None
```

The `place` form is not touched.

- [ ] **Step 11: Run the tests to verify they pass**

Run the Step 3 command, then `timeout 600 uv run pytest -q -x tests/modules tests/kernel`. Expected: PASS. Any other
caller of a function that gained `words=` (`grep -rn "part_names(\|layer_chains(\|scenario_places(\|checks(\|scope(\|evals(\|holds(" xarch tests | grep -v "def "`)
passes it.

- [ ] **Step 12: Commit**

```bash
git add xarch/kernel/logic/targets.py xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/holds_written.py xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/application/logic/written_checks.py xarch/modules/spec/application/logic/evals.py xarch/modules/rules/application/logic/own_checks.py tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/logic/test_evals.py tests/modules/rules/application/logic/test_own_checks.py
git commit -m "A key outside imports that names a part by its plain name refuses a prefixed name with the plain name to write, through one helper, outside_imports; a prefix that is no word or a part not declared keeps the reader's text, and place still takes references"
```

(Landed as `6374d98`.)

---

### Task 4: Bundled profiles in their old forms are refused line by line; one problem per value at the CLI

**Files:**
- Test: `tests/bootstrap/test_bundled_imports.py` (module docstring; helpers and two tests at the end)
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (`scenario_places`: `written=`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (`parse_profile`, `_guards`, `_scenario_coverage`)

**Interfaces:**
- Consumes: from the test file, `SHIPPED` (profile name → `Path`), `nodes(document)` (yields `(path, value)`),
  `LISTS` (the list keys under `imports`), `runner`, `app` — all already there from 8.3; `_tier_names(tiers)` already in
  `profile_parsing.py`.
- Produces: `ck.scenario_places(..., *, words, written: Collection[str])`.

- [ ] **Step 1: Write the failing integration tests**

Module docstring of `tests/bootstrap/test_bundled_imports.py`, last sentence:

```python
"""What a part, or a tier, of a bundled profile or of xarch's own may import, must import and may import from outside
stays what it was before the import keys moved into `imports` groups: `where` says the same of a file of every part of
xarch's own profile and of a test of each of its tiers, and the rules the keys expand to are, as checks, the same text
for each profile but for the key; every list of parts under imports of each is written in references, which no other
key is; and each, written in the old forms, is refused with one problem per entry, naming the reference it held."""
```

At the end of the file:

```python
REPEATING = re.compile(r"<[^>]+>")
"""A step of a folder key that repeats, `<word>`."""


def repeating_parts(node, repeats=False, found=None) -> dict[str, bool]:
    """Each part of a `parts` tree, by its name (its `name`, else its last step before the first dot), and whether its
    path holds a repeating step."""
    found = {} if found is None else found
    for key, value in node.items() if isinstance(node, dict) else ():
        if not isinstance(key, str) or not ("/" in key or "." in key):
            continue
        steps = key.rstrip("/").split("/")
        inside = repeats or any(REPEATING.fullmatch(step) for step in steps)
        if isinstance(value, dict) and any(isinstance(k, str) and "/" not in k and "." not in k for k in value):
            found[value.get("name") or steps[-1].split(".")[0]] = inside
        repeating_parts(value, inside, found)
    return found


def old_form(reference: str, whole: bool, repeats: dict[str, bool]) -> str:
    """The form a reference was written in before 0.3.0: `parts.X` as `X@any` when X repeats, else `X`; `<word>.X` as
    `X`; whole, for a tier's must and types_only, the part's name alone."""
    prefix, _, rest = reference.partition(".")
    name = re.split("[/:]", rest, maxsplit=1)[0]
    if whole:
        return name
    return f"{name}@any{rest[len(name):]}" if prefix == "parts" and repeats[name] else rest


def inverted(document) -> list[str]:
    """Writes every entry of a list of parts under an `imports` group in its old form, in place; the references it
    held, in the order of the document."""
    repeats = repeating_parts(document["parts"])
    found: list[str] = []
    for path, value in list(nodes(document)):
        if path[-2:-1] != ("imports",) or path[-1] not in LISTS or not isinstance(value, list):
            continue
        whole = path[0] == "tiers" and path[-1] in ("must", "types_only")
        for i, entry in enumerate(value):
            marked = isinstance(entry, dict)
            reference = next(iter(entry)) if marked else entry
            if reference == "everything":
                continue
            found.append(reference)
            old = old_form(reference, whole, repeats)
            value[i] = {old: entry[reference]} if marked else old
    return found


def written_instead(problem: str) -> str:
    """The first reference a problem of a removed form says to write; any other problem as it is said."""
    _, removed, instead = problem.partition("was removed in 0.3.0: write ")
    return instead.split(" (")[0] if removed else problem


def beside(source: Path, folder: Path, text: str) -> Path:
    """The file text as if it sat where source does: folder holds a link to every other file next to source."""
    for item in source.parent.iterdir():
        if item.name != source.name:
            (folder / item.name).symlink_to(item)
    written = folder / source.name
    written.write_text(text, encoding="utf-8")
    return written


@pytest.mark.parametrize("profile", list(SHIPPED))
def test_each_profile_written_in_the_old_forms_is_refused_one_problem_per_entry_each_naming_its_reference(profile,
                                                                                                         tmp_path):
    document = yaml.safe_load(SHIPPED[profile].read_text(encoding="utf-8"))
    references = inverted(document)
    written = beside(SHIPPED[profile], tmp_path, yaml.safe_dump(document, sort_keys=False))
    result = runner.invoke(app, ["profile", "check", str(written)])
    said = [line.strip() for line in result.output.splitlines() if line.strip().startswith(f"{written}:")]
    assert result.exit_code != 0
    assert references
    assert sorted(written_instead(problem) for problem in said) == sorted(references)


def test_an_inline_profile_with_several_old_forms_says_one_problem_per_line(tmp_path):
    written = tmp_path / "tiny.yaml"
    written.write_text("name: tiny\nparts:\n  modules/<module>/:\n    domain/: {role: the rules}\n    services/:\n"
                       "      role: the use cases\n      imports:\n        may:\n          - domain\n"
                       "          - kernel@any\n          - domain@own\n  kernel/: {role: shared code}\n",
                       encoding="utf-8")
    result = runner.invoke(app, ["profile", "check", str(written)])
    assert result.exit_code != 0
    assert [line.strip() for line in result.output.splitlines() if line.strip().startswith(f"{written}:")] == [
        f"{written}: parts.services.imports.may: 'domain': a bare part name was removed in 0.3.0: write module.domain "
        "(this module's) or parts.domain (any module's)",
        f"{written}: parts.services.imports.may: 'kernel@any': @any was removed in 0.3.0: write parts.kernel",
        f"{written}: parts.services.imports.may: 'domain@own': @own was removed in 0.3.0: write module.domain"]
```

(Ensure `from pathlib import Path` and `import yaml` are among the file's imports; add them if not.)

The `sorted(...) == sorted(references)` assertion holds the spec's three demands at once: one problem per inverted
entry (lengths equal), no other problem (an extra line would not be a reference), each naming the original reference.

`tests/modules/spec/application/logic/test_profile_parsing_tests.py`, after `test_a_bad_scenario_coverage_is_refused`:

```python
def test_scenario_coverage_of_a_tier_written_but_refused_leaves_the_refusal_to_the_tier():
    document = covered(guards={"scenario-coverage": GUARDS["scenario-coverage"]})
    document["tiers"]["integration"]["imports"] = {"must": ["store"]}
    assert problems(document) == ["layered.yaml: tiers.integration.imports.must: 'store': a bare part name was removed "
                                  "in 0.3.0: write parts.store"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_bundled_imports.py tests/modules/spec/application/logic/test_profile_parsing_tests.py`
Expected: FAIL — for the bundled profile whose `guards.scenario-coverage` names a tier whose `must` is now refused, an
extra `guards.scenario-coverage.tier: no tier named '...'` line breaks the one-problem-per-entry count; the unit test
sees the same second problem.

- [ ] **Step 3: Implement: a refused tier is not said missing again**

`profile_checks.py`:

```python
def scenario_places(results: Any, tier: Any, suffix: Any, parts: dict[str, Part], declared: set[str],
                    tiers: tuple[Tier, ...], where: str, problems: list[str], language: Language, *,
                    words: Collection[str], written: Collection[str]) -> None:
    """The part holding the result unions lies in a repeating folder, the tier is declared and tests that part, and the
    suffix is the end of a name. A tier written (written, the names of the tiers the file writes) but refused has said
    its own problems, so it adds none here."""
```

```python
    found = next((t for t in tiers if t.name == tier), None)
    if found is None:
        if not (isinstance(tier, str) and tier in written):
            problems.append(f"{where}.tier: no tier named {tier!r}")
```

`profile_parsing.py`, in `parse_profile` before the `_guards` call:

```python
    written_tiers = _tier_names(document["tiers"]) if isinstance(document.get("tiers"), Mapping) else []
    guards = _guards(document.get("guards", {}), specs, parts, declared, tiers, fakes, testing, problems, language,
                     words, written_tiers)
```

`_guards(..., language: Language, words: Collection[str], written_tiers: Collection[str])` passes `written_tiers` to
`_scenario_coverage(spec, parts, declared, tiers, testing, where, problems, language, words, written_tiers)`, whose
signature gains `written_tiers: Collection[str]` and whose call becomes
`ck.scenario_places(..., language, words=words, written=written_tiers)`.

- [ ] **Step 4: Run the tests to verify they pass**

Run the Step 2 command. Expected: PASS (three `SHIPPED` params plus the inline test).

- [ ] **Step 5: Commit**

```bash
git add tests/bootstrap/test_bundled_imports.py tests/modules/spec/application/logic/test_profile_parsing_tests.py xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py
git commit -m "Each bundled profile and xarch's own, every list under imports written back in its old forms, is refused by profile check with one problem per entry, each naming the reference it held; a scenario-coverage whose tier is written but refused leaves that refusal to the tier"
```

(Landed as `b525ed1`.)

---

### Task 5: CHANGELOG, README, docstrings; golden docs regenerated

**Files:**
- Modify: `CHANGELOG.md` (`## [Unreleased]`: `### Added` entry's last sentence; a `### Changed` entry)
- Modify: `README.md` (the symbols paragraph about targets, ~line 233)
- Modify: `xarch/modules/rules/application/logic/tier_of.py` (`as_place` docstring, line 134)
- Check: `xarch/architectures/keys.yaml`, `docs/{cli,web,xarch}/`

**Interfaces:** none.

- [ ] **Step 1: The checks that pin this text**

The golden docs are pinned by `tests/bootstrap/test_docs_templates.py`
(`test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte`,
`test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch`). Run:
`timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py` — Expected: PASS before and after this task
(the docs do not move). Prose has no test of its own; its check is Step 5's grep.

- [ ] **Step 2: CHANGELOG**

In `## [Unreleased]` → `### Added`, the entry ending `... before the pattern, and a part's own instance of itself. No
old form is refused yet.` loses its last sentence:

```markdown
  before the pattern, and a part's own instance of itself.
```

In the 8.3 `### Changed` entry, `read `parts.<part>` beside a plain name, and` becomes `read `parts.<part>`, and`.
Append to `### Changed`:

```markdown
- The old forms of a target are refused, each with the reference to write, computed from the profile, one problem
  per value: `<part>@any` (`'contract@any': @any was removed in 0.3.0: write parts.contract`), `<part>@own` (`write
  module.contract` where the importer lies in the part's `<module>` folder, else `write parts.contract`) and the bare
  name of a part (`'domain': a bare part name was removed in 0.3.0: write module.domain (this module's) or
  parts.domain (any module's)`, or `write parts.kernel` for a part `<word>.` cannot name from there), each with its
  `/<path>` and `:<pattern>` carried into the reference. A bare name, `@any` or `@own` in a tier's `imports.must` or
  `imports.types_only` is told `parts.<part>`. A value with `@` and no dot, such as `domain@all`, is not a reference.
  The tree's reader refuses the repeating folder `<parts>` (`parts.` names a part in every instance: give the
  repeating folder another word), and a key outside `imports` that names a part by its plain name refuses a prefixed
  one (`'parts.bootstrap': names a part outside imports: write bootstrap`). `<word>.<part>` from an importer outside
  its folder and a concrete instance name (`orders.services`, also when a part is named `orders`) stay refused. No
  form is rewritten on load: a profile written in the old forms is refused until it is rewritten.
```

- [ ] **Step 3: README and the docstring**

`README.md`, the paragraph ending `... write a target the same way.`:

```markdown
  same way. The forms before 0.3.0, `store@any`, `store@own` and the bare `store`, are refused with the reference to
  write (`'store@any': @any was removed in 0.3.0: write parts.store`). Every other key that names a part, outside
  `imports`, takes its plain name (`fakes.for: [store]`), and a repeating folder cannot be written `<parts>`.
```

`xarch/modules/rules/application/logic/tier_of.py`:

```python
def as_place(instance: str | None) -> Place:
    """The place a test speaks from: its repeating folder's instance, so that `<word>.<part>` reaches that instance's
    parts."""
    return Place(EACH, instance)
```

- [ ] **Step 4: Regenerate and read the golden docs**

Regenerate the docs the way `tests/bootstrap/test_docs_templates.py` builds them (read its helpers at lines 17-90 for
the command it compares against), then run `git status --short docs/ && git diff --stat docs/`.
Expected: no change under `docs/cli`, `docs/web`, `docs/xarch`. If anything moves, read the diff and stop to report:
no valid profile's meaning changes in this card.

- [ ] **Step 5: Grep for text that still describes an old form as accepted**

Run: `grep -rn "@any\|@own\|bare name\|plain name" README.md xarch/architectures/keys.yaml xarch/ --include=*.py --include=*.yaml --include=*.md | grep -v "was removed\|removed in 0.3.0"`
Expected: only lines that describe the forms as removed, or keys outside `imports` that take a plain name. Rewrite any
other hit; `profile explain` follows `keys.yaml`.

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md README.md xarch/modules/rules/application/logic/tier_of.py
git commit -m "The CHANGELOG's [Unreleased] says the old forms of a target are refused, each with its reference, with no rewrite on load; the README says the same in short; the golden docs, regenerated, do not move"
```

(Landed as `1981113`.)

---

### Task 6: Lines within 120 columns; every gate green

**Files:**
- Modify (only where a line runs past 120 columns): `xarch/modules/spec/application/logic/profile_parsing.py`,
  `xarch/modules/spec/application/logic/written_checks.py`, `xarch/modules/spec/application/logic/parts_tree.py`,
  `tests/modules/spec/application/logic/test_profile_parsing.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py`,
  `tests/modules/spec/application/logic/test_tiers.py`,
  `tests/modules/spec/application/logic/test_written_checks.py`, `tests/modules/spec/application/test_select.py`

**Interfaces:** none.

- [ ] **Step 1: Find the long lines this card wrote**

Run: `git diff main...HEAD -U0 -- xarch tests | grep '^+' | grep -v '^+++' | awk 'length > 121'`
Expected before wrapping: the calls in `parse_profile` that gained `words=words`
(`layers = ck.layer_chains(...)`, `own = (own_checks.checks(...)`, `placement, placed, own_evals, alike = (evals(...)`),
`_no_twins`' `names = ck.part_names(...)`, `_quantified`'s `return WrittenCheck(...)`, the `_RESERVED` problem in
`parts_tree._steps`, and test rows above.

- [ ] **Step 2: Wrap them, same text read**

For example in `profile_parsing.py`:

```python
    layers = (ck.layer_chains(document["layers"], parts, declared, rules, problems, words=words) if "layers" in document
              else {})
```

```python
    own = (own_checks.checks(document["checks"], declared, tiers, language, problems, words=words)
           if "checks" in document else {})
```

```python
    placement, placed, own_evals, alike = (evals(document["evals"], declared, language, problems, words=words)
                                           if "evals" in document else ({}, ((), ()), {}, ()))
```

```python
    names = (ck.part_names(spec["translated"], declared, f"{where}.translated", problems, words=words)
             if "translated" in spec else [])
```

and in `parts_tree.py`:

```python
        problems.append(f"parts: '{key}' has the step `{_RESERVED}`: `{_RESERVED}` is reserved: `parts.` names a part "
                        "in every instance; give the repeating folder another word")
```

Wrap test rows by splitting their string literals; never change what a test asserts. Do not run `ruff --fix`.

- [ ] **Step 3: Run the gates**

```bash
timeout 900 uv run pytest -q > /tmp/8-4-pytest.log 2>&1 &   # record the PID; read the log when it exits
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

Expected: pytest all passed (`tail -3 /tmp/8-4-pytest.log`); `xarch check` and `--strict` clean; ruff `All checks
passed!`; `profile check architecture.yaml` OK with the same looser lines as at `72b857c`
(compare by running it in a throwaway worktree: `git worktree add /tmp/8-4-base 72b857c`, run it there, then
`git worktree remove /tmp/8-4-base`). `git status --short tests/bootstrap/corpora` empty: no recorded finding moved.

- [ ] **Step 4: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/application/logic/written_checks.py xarch/modules/spec/application/logic/parts_tree.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_tiers.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/test_select.py
git commit -m "The lines this step ran past 120 columns are wrapped again; the text read is the same"
```

(Landed as `12a67e9`.)

---

## Self-review against the spec

- B1 (every table row): Task 1 Step 1 has a row per B1 row — `@any` with path either side and pattern, `@own`
  accepted/not (outside, other word, no folder), bare with word / without / no folder / tail, `nope`, declared-unplaced,
  not-a-reference shapes (`domain@foo`, `@any`, `""`, `domain@`, `1`, a list), pattern-not-taken and bad pattern (one
  problem), implied rows (`services`, `services@own`, `kernel`, `kernel@any`), `services@any`, `everything`. Old texts
  gone: Task 1 Step 7. Dotted heads unchanged: 8.1's rows stay in the file.
- B2: Task 1 Step 2 (`test_tiers.py` rows and the twice-written test); docstrings Task 1 Step 5.
- B3: Task 2. B4: Task 3 (helper, every listed key, unclaimed values, `place` untouched). B5: Task 1 Step 1
  (`orders.services` with part `orders`; `module.contract`-style rows from 8.1 and the check-with-no-part row).
- B6: Task 4, parametrized over `SHIPPED`, no branch naming a profile, part or `module`. One problem per line: Task 4.
- B7: Task 5 (CHANGELOG both edits, README, docstrings of `targets.py`, `tier_of.py`, `imports_written.py`, keys.yaml
  grep, golden docs). Gates: Task 6.
- Tests 1-11 of the spec map to: 1-3 → Task 1 Step 1; 4 → Task 1 Step 2 (`test_targets_written.py`); 5 → Task 3
  Step 1; 6 → Task 1 Step 2; 7 → Task 2; 8-9 → Task 3 Step 2; 10-11 → Task 4.
- Names consistent across tasks: `old_form`, `removed`, `BARE`, `outside_imports`, `words=`, `written=`.
- No placeholders: every code step shows its code; Task 5 Step 4's regeneration defers only to the test file that
  already defines it.
<!-- task-pipeline: validated -->
