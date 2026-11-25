# 8.4 spec: the old reference forms are refused with their replacement

Card: 810682ee-28a2-4487-83d3-87a0238dcae6 (subtask of f1c96689), blocked by 8.3 (c24c8593, done: branch tip
72b857c). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3), sub-step 4 of its owning
note.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements section 4 (lines 293-325), 3.3 (lines 233-238) as moved by `profile-form-proposal.md` 5.3 item 2
(lines 627-628: the refusal of the word `parts` sits in the reader of the tree's keys, "same rule, same text"), 3.10
(lines 278-282), 3.11 (lines 284-287) and section 6 sub-step 4 (lines 453-455). Dodges: note section 7 (lines
461-480). From review 3: O4, O5, O8.

## Goal

After this card, a profile that writes a target in an old form (`<part>@any`, `<part>@own`, the bare name of a part,
each with or without `/<path>` and `:<pattern>`) is refused by `profile check` (and by every command that loads the
profile), one problem per value, each naming the exact reference to write instead, computed from the profile. Only
`parts.<part>`, `<word>.<part>` and `everything` remain. Alongside: the reader of the `parts` tree refuses a repeating
folder word `parts`; a key outside `imports` that names a part refuses a prefixed name with the plain name to write;
`<word>.` from an importer outside that folder and a concrete instance name stay refused (already built in 8.1) and are
pinned by tests. The CHANGELOG says so. Nothing any valid profile allows changes: every bundled profile and every
fixture already writes references (8.3).

## What is already there (not to be redone)

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

## Inherited constraints

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

## Definitions used below

- *head*: the value's text before its first `/` or `:`. *tail*: the rest (`/<path>`, `:<pattern>`), carried unchanged
  into the replacement.
- *word of a part*: `repeat_of(repeats, path).word` (`xarch/kernel/logic/placement.py`), or none when the part lies in
  no repeating folder.
- *`<word>.` would be accepted*: the part has a word W, and either the reader is mirrored (a tier's `imports.also`) or
  the importer (`owner`) lies in a W folder; never for a tier's `imports.must` / `.types_only`. These are exactly the
  conditions `_word_problem` checks today; the replacement must be computed by the same rule, not a copy of it.

## Behavior

### B1. `target()` refuses every head without a dot

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

### B2. A tier's `imports.must` and `imports.types_only` refuse a dot-less entry

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

### B3. The tree's reader refuses the repeating word `parts`

In `xarch/modules/spec/application/logic/parts_tree.py`, `_steps()` (lines 147-160), a key whose step is `<parts>`
(at any depth: `units/<parts>/store/`, `<parts>/x.py`) is refused, one problem per key, beside the neighbouring
problems:

`parts: '<key>' has the step `<parts>`: `<parts>` is reserved: `parts.` names a part in every instance; give the
repeating folder another word`

The part below it is not read (as for the other step problems). `<partsx>`, `<sub-parts>`, a plain folder `parts/`
(no brackets) and a part named `parts` stay valid (note 3.2). `xarch/kernel/logic/placement.py` is not changed for
this (proposal 5.3 item 2).

### B4. A key outside `imports` refuses a prefixed name

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

### B5. Already refused, pinned by tests (no code change expected)

- Concrete instance name: `orders.services` is refused with `'orders' is neither parts nor a word of this profile
  (module): a profile names no instance; write module.services or parts.services`, **also** when the profile
  declares a part named `orders` (note 3.11; dodge line 476).
- `<word>.` from an importer outside its folder: `module.contract` in `parts.cli.imports.may` (`cli` outside
  `modules/<module>/`), in a tier's `imports.may` (owner None, `a tier's folder`), and in a check's `place` with no
  `in.part` (`a check that names no part`): refused with `write parts.contract`.

### B6. Bundled profiles rewritten with their old lines are refused line by line

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

### B7. Text

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

## Out of scope

- The `imports.also` refusal of `<word>.` when no part the tier tests lies in the word's folder (note 3.8): card 8.5.
  Mirrored handling is not touched beyond B1.
- Refusing `parts.X` beside `module.X` in one list (rulings line 34, later change).
- `structure` shadowing a part named `structure` (note 3.12).
- Any change to `Target`, the writers (`written_target`, `_place`, `_shown`), the rules, or what a valid profile
  allows.
- Corpora findings: not expected to move; if a recorded finding moves, stop and report rather than edit.

## Tests

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

## Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run
xarch profile check architecture.yaml` (still OK, looser lines unchanged).

## Review focus for the planner

- A value refused twice (removal message plus a pattern, `must`-not-in-`may`, or duplicate problem): one per value.
- The replacement disagreeing with what `_reference` then accepts: a hint that, written, is refused again (other than
  the implied self-import row).
- Mirrored readers (`imports.also`) given `parts.` only for a bare repeating name.
- A B4 helper that claims `os.environ`-like dotted names or undeclared parts.
- `everything` or a part named `everything` broken by the dot-less branch.
