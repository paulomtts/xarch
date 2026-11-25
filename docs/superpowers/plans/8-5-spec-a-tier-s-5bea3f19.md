# 8.5 spec: a tier's `imports.also` refuses a word none of its parts lies in — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In `tiers.<t>.imports.also`, `<word>.<part>` is refused when no part the tier tests lies in a `<word>`
folder, and the old forms there name `<word>.<part>` only where it would now be accepted; everything else reads as
today.

**Architecture:** The kernel's `target()` (`xarch/kernel/logic/targets.py`) takes `mirrored` as the paths of the parts
the test's tier tests (`Collection[tuple[str, ...]] | None`, None for every reader that is no test) in place of a
bool. The one rule lives in `_word_problem`: for a mirrored reader, the word is accepted when one of those paths lies
in that word's folder, else refused with B1's message; both branches of `target()` (references and old forms) already
call `_word_problem`, so B4 follows with no new code. `allowed_targets` threads the collection and tests it with
`is not None`; `_tier` passes the paths of its `subject`.

**Tech Stack:** Python 3.13, pytest (`pytest.param(..., id=...)` tables), `uv run`, ruff (no `--fix`), YAML data in
`xarch/architectures/presets/format/keys.yaml`.

**Spec:** `docs/superpowers/specs/8-5-spec-a-tier-s-5bea3f19.md` (reproduced in full below this plan's header).

## Global Constraints

- No comments in xarch's code: docstrings only. Never `ruff --fix`.
- Every new test is written first and seen failing before its code (rows that pin unchanged behaviour pass before and
  after; each RED step lists exactly which ids must fail).
- Lines at most 120 columns (ruff allows 140; the project rule is 120).
- Examples simple, absolute `app.` imports. Python only in the reader adapter and `xarch/architectures/presets/` data.
- Recorded corpora (`tests/bootstrap/corpora/`) not edited; if a recorded finding moves, stop and report.
- Generated docs `docs/{cli,web,xarch}/` never edited by hand; expected not to move.
- `.claude/` out of commits; nothing pushed. No test deleted to make the suite pass.
- B1's message, exactly: `<file>: tiers.<t>.imports.also: '<value>': no part the tier tests lies in a <W> folder, so
  its tests mirror no W: write parts.<rest>` (`<rest>` the value after the prefix, `/<path>` and `:<pattern>` kept).
- Old forms keep the one wording `'<value>': <form> was removed in 0.3.0: write <new>`. One problem per value.
- No `word` field on `Target`, no new scope, no special-casing of a profile, its parts or the word `module`.

## Review Focus

1. Two tiers in one profile, one testing `<module>` parts and one not: each tier's `also` must be judged by its own
   `subject`, never by another tier's parts or all parts. Test: Task 1,
   `test_each_tier_s_word_in_what_its_tests_also_import_is_judged_by_the_parts_that_tier_tests`.
2. A tested part lying deeper below the instance (`modules/*/services/logic`) or a file part (`modules/*/main.py`):
   it lies in the `<module>` folder and must count. Test: Task 1, kernel rows `a tested part deeper in the folder`
   and `a tested file part in the folder`.
3. Several `<word>.` values in one `also` list, all judged against the same tested paths (the collection is read
   once per value, so a one-shot iterable would accept the first and refuse the rest). Test: Task 1,
   `test_several_words_in_one_list_are_each_judged_by_the_same_tested_parts`.
4. A tier with a `folder` that also has parts naming it in `tests`: its parts count, so the word is accepted. Test:
   Task 1, `referencing()` makes `services` `tests: guard` and the existing expectations hold.
5. A value that carries a pattern as well as a path: B1's replacement keeps both (`write parts.domain/values:*Id`).
   Test: Task 1, kernel row `the path and pattern kept in the reference to write`.

---

## The spec

Reproduced verbatim from `docs/superpowers/specs/8-5-spec-a-tier-s-5bea3f19.md`; headings demoted one level.

## 8.5 spec: a tier's `imports.also` refuses a word none of its parts lies in

Card: 5bea3f19-c683-414f-bfde-a528aa344f38 (subtask of f1c96689), blocked by 8.4 (810682ee, done: branch tip
86b74a6). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3), sub-step 5 of its owning
note, the last before the wrap-up (story 9).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements 3.8 (lines 264-271), the default ruling that states it (lines 31-32), and section 6 sub-step 5
(line 456), reading 1.1 step 4 (lines 129-130). Dodges: note section 7, chiefly lines 470-471 and 474. From review 3:
O4, O5, O8.

### Goal

After this card, `<word>.<part>` in `tiers.<t>.imports.also` is refused when no part the tier tests lies in a
`<word>` folder: such a tier's tests mirror no instance of that folder, so `own` would reach nothing. Where a part
the tier tests does lie in a `<word>` folder, `<word>.<part>` stays what it is today: the instance the test mirrors,
`Target(part, "own", ...)`, the same value every other key gives (note line 470-471: no separate resolution path for
tests). The old forms in `also` (`<part>@own`, a bare repeating name), already refused by 8.4, name the replacement by
the same rule: `<word>.<part>` only where it would now be accepted, else `parts.<part>`. Nothing a bundled profile
writes changes meaning; `architecture.yaml`'s one `also` list stays accepted.

### What is already there (not to be redone)

- `target()` (`xarch/kernel/logic/targets.py:31-69`) takes `mirrored: bool`. For a reference it calls `_reference`
  (l.109-144), which calls `_word_problem` (l.166-183). `_word_problem` checks that the target part lies in the word's
  folder (l.172-176), then returns None at once when `mirrored` (l.177-178): the importer test is skipped, and nothing
  takes its place. This is the gap this card closes.
- The old-form branch of `target()` (l.55-57) computes whether `<word>.` would be accepted by calling the same
  `_word_problem` with `mirrored`, and words the replacement from that (l.61-68). It must keep using that one rule.
- `allowed_targets` (`xarch/modules/spec/application/logic/targets_written.py:20-45`) passes `mirrored` through; it
  also uses it to word `everything` in `also` (l.28, 32, 39).
- `_tier` (`xarch/modules/spec/application/logic/profile_parsing.py:648-689`) reads `also` at l.678 with
  `mirrored=True`, the only caller that does. `subject` (built at l.611: every part whose `tests` names this tier) is
  in scope there; each part's path is `parts[s.part].path`.
- `architecture.yaml:303`: `tiers.integration.imports.also: [module.domain/values, ...]`; the integration tier tests
  `services`, `controller`, `adapters`, all under `modules/<module>/` (lines 60, 78, 97). The bundled `cli.yaml` and
  `web.yaml` write no `also` (`tests/bootstrap/test_bundled_imports.py:72-74`, 0 rules).

### Inherited constraints

- Ruling (default): "In `tiers.<t>.imports.also`, `<word>.` is refused when no part the tier tests lies in that
  word's folder" (note lines 31-32, 3.8 lines 269-271).
- `<word>.` in `also` resolves through the same `Target(part, "own")` as anywhere else; no separate path, no fourth
  scope, no `word` field on `Target` (note section 7 lines 470-473; table line 107).
- `<word>.` that would match nothing is refused, never accepted silently (section 7 line 474).
- No special-casing of a profile, its parts or the word `module`: the word and the folders come from the profile read
  (section 7 lines 468-469).
- A refusal of a new form keeps a plain description of what is wrong and what to write; an old form keeps the one
  0.3.0 wording `'<value>': <form> was removed in 0.3.0: write <new>` (note section 4 lines 296-298). One problem per
  value (rulings line 37).
- Resolution order of a reference unchanged (`_reference` docstring: shape, prefix, pattern, part, path, instance,
  part itself): the new test is part of "the instance", after "the target part lies in the word's folder".
- Generated docs `docs/{cli,web,xarch}/testing.md` regenerated, never edited by hand, diff read; expected not to move
  (note 5.3 lines 411-412; review 3 O8).
- README and CHANGELOG lines under `[Unreleased]` (review 3 O4, O5).
- Project rules (card): no comments in xarch's code (docstrings only); never `ruff --fix`; tests written first and
  seen failing; examples simple, absolute `app.` imports; recorded corpora (`tests/bootstrap/corpora/`) not edited
  (none writes `also`); Python only in the reader adapter and `xarch/architectures/presets/` data; `.claude/` out of
  commits; nothing pushed; lines at most 120 columns.

### Definitions

- *the tier's parts*: the parts whose `tests` names the tier (`subject`); `untested` parts and a tier's `folder` are
  not among them.
- *a part lies in a `<W>` folder*: `repeat_of(repeats, path).word == W` (`xarch/kernel/logic/placement.py`), as
  `_word_problem` already reads it for the target part and the importer.
- *mirrored reader*: the reader of `tiers.<t>.imports.also`, and only it.

### Behavior

#### B1. A word none of the tier's parts lies in is refused

In `tiers.<t>.imports.also`, a reference `<W>.<part>[/<path>]` whose target part lies in a `<W>` folder (so it passes
every check that precedes this one) is refused when none of the tier's parts lies in a `<W>` folder, including when
the tier has no parts at all (a tier with only a `folder`). Problem, one per value, at the key's address:

```
<file>: tiers.<t>.imports.also: '<value>': no part the tier tests lies in a <W> folder, so its tests mirror no <W>: write parts.<rest>
```

`<rest>` is the value after the prefix, unchanged (`/<path>` kept), as every other `_word_problem` message writes it.
Example (fixture `covered()`, unit tier tests only `service`; give the unit tier instead only `shared`):
`layered.yaml: tiers.unit.imports.also: 'module.store/rules': no part the tier tests lies in a <module> folder, so
its tests mirror no module: write parts.store/rules`.

The value contributes no target; the tier is refused as any tier with a problem is today.

#### B2. A word one of the tier's parts lies in is accepted, unchanged

When at least one of the tier's parts lies in a `<W>` folder, `<W>.<part>[/<path>]` reads to
`Target(part, "own", steps)` exactly as today. It is enough that one part does; the others may lie elsewhere (the
unit tier of `architecture.yaml` tests parts in `modules/<module>/` and `kernel`, `platform` outside).

With two words (`<module>` and `<unit>`), each word is judged on its own: a tier testing only `<module>` parts accepts
`module.x` and refuses `unit.y` with B1's message for `<unit>`; a tier testing parts of both accepts both.

#### B3. The checks before it keep their messages

A word for a part in no `<W>` folder, or in another word's folder, keeps today's message (`part 'kernel' lies in no
<module> folder: write parts.kernel`; `part 'store' lies in the <unit> folder, not <module>: write parts.store`), even
when B1 would also apply. `parts.<part>` in `also` is never affected by B1.

#### B4. The old forms name the replacement by the same rule

In `also`, `<part>@own` and the bare name of a repeating part (already refused by 8.4) name `<W>.<part>` only where
B2 would accept it, else `parts.<part>`:

| Written in `also` | Tier's parts | Problem (after the address) |
|---|---|---|
| `service@own` | `service` (in `<module>`) | `'service@own': @own was removed in 0.3.0: write module.service` (today) |
| `service@own` | `shared` only (outside) | `'service@own': @own was removed in 0.3.0: write parts.service` |
| `service` | `service` | `'service': a bare part name was removed in 0.3.0: write module.service (this module's) or parts.service (any module's)` (today) |
| `service` | `shared` only, or none | `'service': a bare part name was removed in 0.3.0: write parts.service` |

A replacement offered is always one `profile check` then accepts.

#### B5. Other readers are untouched

A part's `imports.may` / `imports.must`, a tier's `imports.may`, a check's `place`: no change in what they accept or
say. `everything` in `also` keeps both of today's messages (`must be a list of targets such as [parts.core,
unit.store/schema]: `everything` is not taken, ...` and `` `everything` is not taken, name each target ... ``), also
for a tier with no parts. Check time (`rules`) is not touched: a target accepted here means what it meant before.

#### B6. Text

- `xarch/architectures/presets/format/keys.yaml`, `tiers.<tier>.imports.also` `accepts:` (l.735-738): after
  "`<word>.<part>` the instance a test mirrors", say it is refused when no part the tier tests lies in a `<word>`
  folder (write `parts.<part>`). `profile explain tiers.imports.also` prints it.
- Docstrings, no comments: `target()` (l.34-42, the "When mirrored" sentence), `_word_problem` (l.169-170, "but for
  the instance a test mirrors"), `allowed_targets` and the module docstring of `targets_written.py` (l.1-5),
  `_reference` if its order sentence changes.
- README (l.229-230, "in a tier's `imports.also`, the instance the test mirrors"): add that a part the tier tests must
  lie in that folder.
- CHANGELOG `[Unreleased]`: in the entry that lists how a reference written wrong is refused (Added, l.10-22, which
  already says `<word>.<part>` is "in a tier's `imports.also` the instance the test mirrors"), add the refusal with its
  message in short (`... no part the tier tests lies in a <module> folder, so its tests mirror no module: write
  parts.store`).
- Golden docs: regenerated as `tests/bootstrap/test_docs_templates.py` builds them, diff read; expected no change.

### Interface the planner should give it (suggested, not binding)

The kernel must learn the tier's parts without learning about tiers. Suggested: `target()`'s and
`allowed_targets()`'s `mirrored: bool` becomes `mirrored: Collection[tuple[str, ...]] | None = None` (the paths of
the parts the tests mirror; None when the reader is no test), threaded to `_reference` and `_word_problem`; `_tier`
passes `tuple(parts[s.part].path for s in subject)`. Every place that tests `mirrored` for truth must test
`is not None` instead: an empty tuple (a tier with no parts) is still a mirrored reader for the `everything` messages
and must still be refused by B1, not read as an importer-less `a tier's folder`. Keeping `mirrored: bool` and adding a
separate keyword is acceptable if the planner prefers; either way there is one rule, in `_word_problem`, used by both
branches of `target()`.

### Out of scope

- The wrap-up of the release (story 9): version, release notes, the final cohesion pass.
- Refusing `parts.X` beside `module.X` in one list (rulings line 35, a later change).
- Any change to `Target`, the writers (`written_target`, `_place`, `_shown`), the rules module, or check-time
  matching of `own` for a test.
- Readers other than `tiers.<t>.imports.also` (B5).
- A tier's `imports.must` / `.types_only`, which refuse `<word>.` already (8.4).
- Corpora: none writes `also`; if a recorded finding moves, stop and report rather than edit.

### Tests

Tiers in xarch: `tests/kernel/logic` and `tests/modules/*/application/logic` are the unit tier (pure functions, table
tests with `pytest.param(..., id=...)`); `tests/bootstrap` is the integration tier (the CLI and shipped files through
real commands). Every new test is written and seen failing before its code.

Unit, `tests/kernel/logic/test_targets.py` (unit: `target()` is a pure function of its arguments; `PARTS` has
`domain`, `services` under `modules/*`, `store` under `units/*`, `kernel`, `kernel-logic`, `cli` outside). The
`read()` helper gains the tier's part paths; `test_a_test_reads_a_reference_from_the_instance_it_mirrors` (l.202-209)
and the mirrored rows at l.~198-200 pass a tested part in `<module>` so they keep asserting what they assert. New rows:

1. `module.domain/values`, tested parts `[services]`: `Target("domain", "own", ("values",))`, no problem (B2).
2. `module.domain`, tested parts `[services, kernel]`: accepted (B2, one part is enough).
3. `module.domain`, tested parts `[kernel, cli]`: None, B1's message for `<module>` (B1).
4. `module.domain`, tested parts `[store]` (in `<unit>` only): None, B1's message (B1, another word's folder).
5. `module.domain`, tested parts `[]`: None, B1's message (B1, a tier with no parts).
6. `unit.store`, tested parts `[services]`: B1 for `<unit>`; tested parts `[services, store]`: accepted (B2, two
   words).
7. `module.kernel`, tested parts `[]`: today's `part 'kernel' lies in no <module> folder` message, only (B3).
8. `domain@own` and bare `domain`, tested parts `[kernel]`: `write parts.domain` (B4); with `[services]`: today's
   text (B4).

Unit, `tests/modules/spec/application/logic/test_targets_written.py` (unit: `allowed_targets` is pure):

9. `test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors` (l.78-82) passes the tested
   parts; a new case refuses `module.service/rules` when only `shared` is tested, one problem.
10. `everything` and `[..., "everything"]` with an empty tested set keep today's two messages (B5, the empty-tuple
    trap).

Unit, `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (unit: parsing an inline profile; fixture
`covered()`: unit tests `service`, integration tests `api` and `store`, `shared` untested):

11. In the refusal table (l.~330-362) rows where the unit tier is made to test only `shared` (move `service` to
    `integration` in the row's setup, or a dedicated parametrized test): `also: [module.store]` gives B1's message;
    `also: [service@own]` gives `write parts.service`; `also: [service]` gives `write parts.service` (B1, B4). Each
    exactly one problem.
12. A tier with only a `folder` (the `guard` setup of l.290-294) and `also: [module.service]`: B1's message (B1, no
    parts).
13. `test_what_the_tests_of_a_tier_may_also_import_are_targets_a_word_naming_the_mirrored_instance` (l.297-301) stays
    green unchanged (B2).

Existing tests whose input B1 now refuses, to be changed so they keep proving what they prove:

- `tests/modules/spec/application/logic/test_profile_parsing.py:441-473` (`referencing()`): its `guard` tier has only
  a `folder` and every part is `untested`, so `also: ["module.domain/values"]` becomes refused and the bare
  `domain/values` row's replacement becomes `parts.domain/values`. Keep the test's point (references reach every
  target spec reads; each old form refused with its one replacement): make one module part (for instance `services`)
  `tests: guard` instead of `untested`, if the profile then parses clean, so the expectations hold as written; else
  rewrite the two expectations to B1/B4's. The `a tier's also` row of l.~482 (`module.kernel`) keeps its text (B3).
- Grep every other inline profile with `also` holding `<word>.` (`tests/bootstrap/test_profile_explain.py`,
  `test_needs_agree.py`, `test_looseness.py:95-110`, `test_tiers.py:404-416`, `test_retired_keys.py`,
  `tests/modules/spec/domain/test_profile_keys.py`) and confirm its tier tests a part in that word's folder;
  `covered()`'s unit tier tests `service`, so `test_looseness.py`'s `module.store` stays accepted. No test is deleted
  to make the suite pass.

Integration (`tests/bootstrap/test_bundled_imports.py`; integration because it runs the shipped files through the
real command): the existing bundled-profile tests stay green, `architecture.yaml`'s `also` rule count and digest
(l.76) unchanged; `uv run xarch profile check architecture.yaml` says OK with the same looser lines.

### Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run
xarch profile check architecture.yaml`.

### Review focus for the planner

- `mirrored` tested for truth somewhere after it becomes a collection: an empty tested set then loses B1 or the
  `everything` messages (rows 5, 10, 12).
- The old-form branch computing its replacement by a copy of the rule instead of `_word_problem`: B4 offering
  `module.x` that B1 then refuses.
- B1 judged per target part's folder rather than per word: a tier testing `<module>` parts refusing `module.x` for a
  part in another module-level path, or accepting `unit.y` because some tested part is in any repeating folder.
- Two problems for one value (B3's message and B1's both), or B1 firing before the "part lies in the word's folder"
  check.
- `subject` read before `_coverage` filled it, or a part's `sub` path used instead of the part's own path.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `xarch/kernel/logic/targets.py` | the target grammar, the one `<word>.` rule (`_word_problem`) | `mirrored` becomes the tested paths; B1 in `_word_problem`; docstrings |
| `xarch/modules/spec/application/logic/targets_written.py` | a list of targets under `imports` | thread the collection, test `is not None`; docstrings |
| `xarch/modules/spec/application/logic/profile_parsing.py` | `_tier` reads a tier | pass the paths of `subject` |
| `tests/kernel/logic/test_targets.py` | unit: `target()` | helper `mirroring`, `read()` default None, new tables |
| `tests/modules/spec/application/logic/test_targets_written.py` | unit: `allowed_targets` | tested paths, `everything` with none |
| `tests/modules/spec/application/logic/test_profile_parsing_tests.py` | unit: parsing tiers | B1/B4 through a whole profile |
| `tests/modules/spec/application/logic/test_profile_parsing.py` | unit: references across keys | `referencing()` gives the guard a part |
| `xarch/architectures/presets/format/keys.yaml`, `README.md`, `CHANGELOG.md` | text | B6 |

Facts checked while writing this plan (a prototype of exactly Task 1's code was run, then reverted):

- With Task 1's code and no test edits, the full suite fails only in `tests/kernel/logic/test_targets.py` (its
  `read()` passes `mirrored=False`, which `is not None`), in
  `test_targets_written.py::test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors`
  (passes `mirrored=True`) and in
  `test_profile_parsing.py::test_references_reach_every_target_spec_reads_and_the_old_forms_are_each_refused_with_one`
  (its `guard` tier tests no part). Every bootstrap test, `xarch check`, `xarch check --strict` and
  `xarch profile check architecture.yaml` (OK) pass; ruff reports only the over-long `target()` signature, which the
  code below wraps.
- `referencing()` with `services` given `"tests": "guard"` in place of `untested` parses clean and keeps every
  expectation of both tests that use it.
- Task 1's test and code blocks, applied verbatim to this branch, gave exactly Step 5's 17 failures and then exactly
  Step 9's one; with Step 10 the unit tier and `test_bundled_imports.py` pass (5291), ruff and `xarch check` pass,
  and no line runs past 120 columns. (Then reverted: the plan is the deliverable.)
- B1's template in the spec writes `mirror no <W>`, its example and CHANGELOG line `mirror no module`: this plan
  follows the example, the word without brackets after `mirror no`.
- No test pins the `accepts:` text of `tiers.<tier>.imports.also`, and the golden docs are built from
  `xarch/architectures/testing.md`, not from `keys.yaml`.

---

### Task 1: The rule — a mirrored reader judges `<word>.` by the parts its tier tests

**Files:**
- Modify: `xarch/kernel/logic/targets.py:31-44` (`target` signature and docstring), `:109-111` (`_reference`
  signature), `:166-183` (`_word_problem`)
- Modify: `xarch/modules/spec/application/logic/targets_written.py:1-5`, `:20-43`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:678-679`
- Test: `tests/kernel/logic/test_targets.py`
- Test: `tests/modules/spec/application/logic/test_targets_written.py:78-82`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (after line 364, the end of
  `test_a_bad_tier_is_refused`)
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py:443-451` (`referencing()`)

**Interfaces:**
- Consumes: `repeat_of(repeats, path) -> Repeat | None` (`xarch/kernel/logic/placement.py:30`), `Repeat.word`.
- Produces:
  - `target(value, owner, parts, declared, where, problems, patterns: bool = False,
    mirrored: Collection[tuple[str, ...]] | None = None, *, alone: str, repeats: Collection[Repeat],
    place: bool = False) -> Target | None`
  - `allowed_targets(value, owner, parts, declared, where, problems, patterns: bool = False,
    mirrored: Collection[tuple[str, ...]] | None = None, *, repeats: Collection[Repeat]) -> tuple[Target, ...]`
  - `mirrored` is None for every reader but a tier's `imports.also`; `()` is a tier that tests no part and is still
    a mirrored reader.

- [ ] **Step 1: Make the kernel test's helpers speak in tested paths**

In `tests/kernel/logic/test_targets.py`, after line 17 (`NOT_A_REFERENCE = ...`), add:

```python


def mirroring(*names):
    """The paths of the parts a tier tests, by name, as the reader of its tests' imports.also is given them."""
    return tuple(PARTS[name] for name in names)
```

Replace `read()` (lines 20-25) with:

```python
def read(written, owner, parts=PARTS, repeats=REPEATS, patterns=True, mirrored=None, place=False,
         alone="a tier's folder", declared=None):
    problems: list[str] = []
    found = target(written, owner, parts, parts if declared is None else declared, "at", problems, patterns, mirrored,
                   alone=alone, repeats=repeats, place=place)
    return found, problems
```

Replace the two rows at lines 56-59 with:

```python
    pytest.param("domain", None, {"mirrored": mirroring("services")}, f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name a test mirrors"),
    pytest.param("domain@own", None, {"mirrored": mirroring("services")},
                 f"at: 'domain@own': @own {REMOVED} module.domain", id="@own a test mirrors"),
```

Replace the last line of `test_a_test_reads_a_reference_from_the_instance_it_mirrors` (line 209) with:

```python
    assert read(written, None, mirrored=mirroring("services")) == (found, problem)
```

- [ ] **Step 2: Write the kernel tests of B1, B2, B3 and B4**

In `tests/kernel/logic/test_targets.py`, directly after `test_a_test_reads_a_reference_from_the_instance_it_mirrors`
(after line 209), add:

```python
NO_MODULE = "no part the tier tests lies in a <module> folder, so its tests mirror no module"


@pytest.mark.parametrize("written, tested, found, problem", [
    pytest.param("module.domain/values", mirroring("services"), Target("domain", "own", ("values",)), [],
                 id="a word a tested part lies in"),
    pytest.param("module.domain", mirroring("services", "kernel"), Target("domain", "own"), [],
                 id="one tested part in the folder is enough"),
    pytest.param("module.domain", (("modules", "*", "services", "logic"),), Target("domain", "own"), [],
                 id="a tested part deeper in the folder"),
    pytest.param("module.domain", (("modules", "*", "main.py"),), Target("domain", "own"), [],
                 id="a tested file part in the folder"),
    pytest.param("module.domain", mirroring("kernel", "cli"), None, [f"at: 'module.domain': {NO_MODULE}: write "
                                                                     "parts.domain"],
                 id="no tested part in the folder"),
    pytest.param("module.domain", mirroring("store"), None, [f"at: 'module.domain': {NO_MODULE}: write parts.domain"],
                 id="the tested parts in another word's folder"),
    pytest.param("module.domain", (), None, [f"at: 'module.domain': {NO_MODULE}: write parts.domain"],
                 id="a tier that tests no part"),
    pytest.param("module.domain/values:*Id", mirroring("kernel"), None,
                 [f"at: 'module.domain/values:*Id': {NO_MODULE}: write parts.domain/values:*Id"],
                 id="the path and pattern kept in the reference to write"),
    pytest.param("unit.store", mirroring("services"), None,
                 ["at: 'unit.store': no part the tier tests lies in a <unit> folder, so its tests mirror no unit: "
                  "write parts.store"], id="each word judged on its own"),
    pytest.param("unit.store", mirroring("services", "store"), Target("store", "own"), [],
                 id="a tier testing parts of both words"),
    pytest.param("module.kernel", (), None,
                 ["at: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel"],
                 id="the target part's folder is checked first"),
    pytest.param("module.store", (), None,
                 ["at: 'module.store': part 'store' lies in the <unit> folder, not <module>: write parts.store"],
                 id="the target part in another word's folder is checked first"),
    pytest.param("parts.domain", (), Target("domain", "any"), [], id="parts is never refused for it"),
])
def test_a_test_reads_a_word_only_where_a_part_its_tier_tests_lies_in_that_word_s_folder(written, tested, found,
                                                                                          problem):
    assert read(written, None, mirrored=tested) == (found, problem)


@pytest.mark.parametrize("written, tested, problem", [
    pytest.param("domain@own", mirroring("services"), f"at: 'domain@own': @own {REMOVED} module.domain",
                 id="@own, a tested part in the folder"),
    pytest.param("domain@own", mirroring("kernel"), f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own, no tested part in the folder"),
    pytest.param("domain@own", (), f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own, a tier that tests no part"),
    pytest.param("domain", mirroring("services"), f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name, a tested part in the folder"),
    pytest.param("domain", mirroring("kernel"), f"at: 'domain': {BARE} parts.domain",
                 id="a bare name, no tested part in the folder"),
    pytest.param("domain", (), f"at: 'domain': {BARE} parts.domain", id="a bare name, a tier that tests no part"),
    pytest.param("store", mirroring("services"), f"at: 'store': {BARE} parts.store",
                 id="a bare name, the tested parts in another word's folder"),
    pytest.param("domain@any", (), f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any told parts as ever"),
])
def test_an_old_form_a_test_reads_names_the_word_only_where_its_tier_could_write_it(written, tested, problem):
    assert read(written, None, mirrored=tested) == (None, [problem])
```

- [ ] **Step 3: Write the `allowed_targets` tests**

In `tests/modules/spec/application/logic/test_targets_written.py`, replace
`test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors` (lines 78-82) with:

```python
NO_MODULE = "no part the tier tests lies in a <module> folder, so its tests mirror no module"


@pytest.mark.parametrize("tested, targets, problems", [
    pytest.param((SERVICE.path,), (Target("service", "own", ("rules",)),), [], id="a tested part in the word's folder"),
    pytest.param((SHARED.path,), (), [f"tiers.unit.imports.also: 'module.service/rules': {NO_MODULE}: write "
                                      "parts.service/rules"], id="the tested parts outside it"),
])
def test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors(tested, targets, problems):
    said: list[str] = []
    assert allowed_targets(["module.service/rules"], None, PARTS, set(PARTS), "tiers.unit.imports.also", said,
                           mirrored=tested, repeats=REPEATS) == targets
    assert said == problems


def test_several_words_in_one_list_are_each_judged_by_the_same_tested_parts():
    said: list[str] = []
    assert allowed_targets(["module.service", "module.api/routes"], None, PARTS, set(PARTS),
                           "tiers.unit.imports.also", said, mirrored=(SERVICE.path,), repeats=REPEATS) == (
        Target("service", "own"), Target("api", "own", ("routes",)))
    assert said == []
    assert allowed_targets(["module.service", "module.api"], None, PARTS, set(PARTS), "tiers.unit.imports.also",
                           said, mirrored=(SHARED.path,), repeats=REPEATS) == ()
    assert said == [f"tiers.unit.imports.also: 'module.service': {NO_MODULE}: write parts.service",
                    f"tiers.unit.imports.also: 'module.api': {NO_MODULE}: write parts.api"]


@pytest.mark.parametrize("value, targets, problem", [
    pytest.param("everything", (), "tiers.guard.imports.also: must be a list of targets such as [parts.core, "
                                   "unit.store/schema]: `everything` is not taken, name each target the tests may also "
                                   "import", id="everything alone"),
    pytest.param(["parts.shared", "everything"], (Target("shared"),),
                 "tiers.guard.imports.also: `everything` is not taken, name each target the tests may also import",
                 id="everything in the list"),
])
def test_a_tier_that_tests_no_part_still_refuses_everything_in_what_its_tests_also_import(value, targets, problem):
    said: list[str] = []
    assert allowed_targets(value, None, PARTS, set(PARTS), "tiers.guard.imports.also", said, mirrored=(),
                           repeats=REPEATS) == targets
    assert said == [problem]
```

- [ ] **Step 4: Write the parsing tests**

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, directly after `test_a_bad_tier_is_refused`
(after line 364), add:

```python
ALSO = "layered.yaml: tiers.unit.imports.also"
NO_MODULE = "no part the tier tests lies in a <module> folder, so its tests mirror no module"


def unit_tier_of_shared(also: list) -> dict:
    """covered(), its unit tier testing only shared, a part outside the repeating folder (service moves to the
    integration tier), its tests also importing also."""
    document = covered()
    part_of(document, "service")["tests"] = "integration"
    shared = part_of(document, "shared")
    del shared["untested"]
    shared["tests"] = "unit"
    document["tiers"]["unit"]["imports"] = {"also": also}
    return document


@pytest.mark.parametrize("also, expected", [
    pytest.param(["module.store"], f"{ALSO}: 'module.store': {NO_MODULE}: write parts.store", id="a word"),
    pytest.param(["service@own"], f"{ALSO}: 'service@own': @own was removed in 0.3.0: write parts.service",
                 id="@own told parts"),
    pytest.param(["service"], f"{ALSO}: 'service': a bare part name was removed in 0.3.0: write parts.service",
                 id="a bare name told parts"),
])
def test_a_tier_whose_parts_lie_in_no_word_s_folder_refuses_that_word_in_what_its_tests_also_import(also, expected):
    assert problems(unit_tier_of_shared(also)) == [expected]


def test_each_tier_s_word_in_what_its_tests_also_import_is_judged_by_the_parts_that_tier_tests():
    document = unit_tier_of_shared(["module.store"])
    document["tiers"]["integration"]["imports"] = {"also": ["module.service"]}
    assert problems(document) == [f"{ALSO}: 'module.store': {NO_MODULE}: write parts.store"]


def test_a_tier_with_only_a_folder_tests_no_part_and_refuses_a_word_in_what_its_tests_also_import():
    document = covered()
    document["tiers"]["guard"] = {"folder": "architecture", "imports": {"also": ["module.service"]}}
    assert problems(document) == [
        f"layered.yaml: tiers.guard.imports.also: 'module.service': {NO_MODULE}: write parts.service"]
```

(`covered`, `part_of`, `problems`, `pytest` are already imported at the top of the file.
`test_what_the_tests_of_a_tier_may_also_import_are_targets_a_word_naming_the_mirrored_instance` at lines 297-301 and
the `service@own` / `service` rows of `test_a_bad_tier_is_refused` stay unchanged: the unit and integration tiers of
`covered()` test `<module>` parts, so they keep today's text.)

- [ ] **Step 5: Run the new tests to verify they fail**

Run:
`timeout 300 uv run pytest -q tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/test_targets_written.py tests/modules/spec/application/logic/test_profile_parsing_tests.py 2>&1 | grep -E "^FAILED|passed|failed"`

Expected FAIL (the current code reads any non-empty `mirrored` as "accept", and `()` as an importer-less tier's
folder), exactly these ids:
- `test_a_test_reads_a_word_only_where_a_part_its_tier_tests_lies_in_that_word_s_folder[no tested part in the folder]`, `[the tested parts in another word's
  folder]`, `[a tier that tests no part]`, `[the path and pattern kept in the reference to write]`, `[each word judged
  on its own]`
- `test_an_old_form_a_test_reads_names_the_word_only_where_its_tier_could_write_it[@own, no tested part in the
  folder]`, `[a bare name, no tested part in the folder]`, `[a bare name, the tested parts in another word's folder]`
- `test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors[the tested parts outside it]`
- `test_several_words_in_one_list_are_each_judged_by_the_same_tested_parts`
- `test_a_tier_that_tests_no_part_still_refuses_everything_in_what_its_tests_also_import[everything alone]`,
  `[everything in the list]`
- `test_a_tier_whose_parts_lie_in_no_word_s_folder_refuses_that_word_in_what_its_tests_also_import[a word]`, `[@own
  told parts]`, `[a bare name told parts]` (the first with `DID NOT RAISE InvalidArchitecture`)
- `test_each_tier_s_word_in_what_its_tests_also_import_is_judged_by_the_parts_that_tier_tests`
- `test_a_tier_with_only_a_folder_tests_no_part_and_refuses_a_word_in_what_its_tests_also_import`

Every other row passes already: it pins behaviour this card keeps (B2, B3, and the `()` old-form rows, which today
fall to "a tier's folder" and so already say `parts.domain`). If any other id fails, stop: Step 1's helper edit is
wrong.

- [ ] **Step 6: Implement the rule in the kernel**

In `xarch/kernel/logic/targets.py`, replace `target`'s signature and docstring (lines 31-42) with:

```python
def target(value: Any, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
           declared: Collection[str], where: str, problems: list[str], patterns: bool = False,
           mirrored: Collection[tuple[str, ...]] | None = None, *, alone: str, repeats: Collection[Repeat],
           place: bool = False) -> Target | None:
    """The target a profile writes as value, for the part owner (its name and path; None for what names no part, which
    the caller words as alone, such as "a tier's folder"), each part by its path, repeats the profile's repeating
    folders, whose words a reference names; None, with the problem said at where, when it is not one. A target that
    names a part declared but not placed is None, with no problem of its own. mirrored, None but for a test, holds the
    paths of the parts the test's tier tests, () for none: `<word>.<part>` there is the instance a test mirrors,
    refused when none of those parts lies in a `<word>` folder. place says the value is a check's `place`, where a
    prefix that is no word may be a dotted name of code. A value in an old form (see old_form) is None, refused with
    the reference to write: `parts.<part>` for `@any`; for `@own` and a bare name, `<word>.<part>` where that
    reference is accepted, else `parts.<part>`; or, when the reference would be the part itself, as implied."""
```

The body of `target` (lines 43-69) is unchanged: it already passes `mirrored` to `_reference` and to
`_word_problem`, so the old-form branch chooses its replacement by the same rule.

Replace `_reference`'s signature (lines 109-111) with:

```python
def _reference(value: str, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
               declared: Collection[str], where: str, problems: list[str], patterns: bool,
               mirrored: Collection[tuple[str, ...]] | None, alone: str, repeats: Collection[Repeat],
               place: bool) -> Target | None:
```

(its docstring and body unchanged: the new test is part of "the instance").

Replace `_word_problem` (lines 166-183) with:

```python
def _word_problem(value: str, prefix: str, rest: str, part: tuple[str, tuple[str, ...]],
                  owner: tuple[str, tuple[str, ...]] | None, repeats: Collection[Repeat],
                  mirrored: Collection[tuple[str, ...]] | None, alone: str) -> str | None:
    """What is wrong with `<word>.<part>`: the part (its name and path) must lie in the word's folder, and so must the
    importer, owner, or what the caller words as alone; for a test, whose tier tests the parts at the paths mirrored,
    one of those parts must instead, the instance a test mirrors; None when both do."""
    instead = f"write parts.{rest}"
    held = repeat_of(repeats, part[1])
    if held is None:
        return f"{value!r}: part {part[0]!r} lies in no <{prefix}> folder: {instead}"
    if held.word != prefix:
        return f"{value!r}: part {part[0]!r} lies in the <{held.word}> folder, not <{prefix}>: {instead}"
    if mirrored is not None:
        words = {each.word for path in mirrored if (each := repeat_of(repeats, path)) is not None}
        return None if prefix in words else (f"{value!r}: no part the tier tests lies in a <{prefix}> folder, so its "
                                             f"tests mirror no {prefix}: {instead}")
    importer = alone if owner is None else f"part {owner[0]!r}"
    mine = None if owner is None else repeat_of(repeats, owner[1])
    if mine is None:
        return f"{value!r}: {importer} lies in no <{prefix}> folder, so it has no own {prefix}: {instead}"
    return None if mine.word == prefix else f"{value!r}: {importer} lies in no <{prefix}> folder: {instead}"
```

- [ ] **Step 7: Thread the tested paths through `allowed_targets`**

In `xarch/modules/spec/application/logic/targets_written.py`, replace the module docstring (lines 1-5) with:

```python
"""What a part, or the tests in a tier's folder, may import, as a profile writes it: a list of targets, each a reference
(see the target grammar in kernel/logic/targets), parts.<part> or <word>.<part>, the word one of the profile's
repeating folders, or `everything`; checked against the parts declared and the part that writes them (None for a
tier's folder), each problem said at its address. What a tier's tests may also import is a list of targets alone,
<word>.<part> being the instance a test mirrors, refused when no part the tier tests lies in a <word> folder."""
```

Replace `allowed_targets` (lines 20-46) with:

```python
def allowed_targets(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
                    problems: list[str], patterns: bool = False, mirrored: Collection[tuple[str, ...]] | None = None,
                    *, repeats: Collection[Repeat]) -> tuple[Target, ...]:
    """What a part, or the tests in a tier's folder (no owner), may import, as targets, a reference's word one of
    repeats, the profile's repeating folders; a name pattern only where patterns allows one; when mirrored is given,
    the paths of the parts a tier tests (() for none), what that tier's tests may also import, read from the instance
    a test mirrors."""
    if value is None:
        return ()
    if value == WORD and mirrored is None:
        return (Target(EVERYTHING),)
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of targets such as [parts.core, unit.store/schema]"
                        + (f": `{WORD}` is not taken, name each target the tests may also import"
                           if mirrored is not None else f", or {WORD}"))
        return ()
    paths = _paths_of(parts)
    found: list[Target] = []
    for item in value:
        if item == WORD:
            problems.append(f"{where}: `{WORD}` is not taken, name each target the tests may also import"
                            if mirrored is not None
                            else f"{where}: {item!r} stands alone: write `{WORD}` in place of the list")
            continue
        written = target(item, None if owner is None else (owner.name, owner.path), paths, declared, where, problems,
                         patterns, mirrored, alone="a tier's folder", repeats=repeats)
        if written is not None:
            found.append(written)
    return tuple(found)
```

(`Collection` is already imported from `collections.abc` at line 8.)

- [ ] **Step 8: Give the tier's reader the paths of the parts it tests**

In `xarch/modules/spec/application/logic/profile_parsing.py`, replace lines 678-679:

```python
    also = allowed_targets(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems, mirrored=True,
                           repeats=repeats)
```

with:

```python
    also = allowed_targets(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems,
                           mirrored=tuple(parts[tested.part].path for tested in subject), repeats=repeats)
```

(`subject` is built in `_tiers` from `_coverage`'s result before `_tier` is called, one `Subject(part)` per part
whose `tests` names this tier; `parts[...].path` is the part's own path, never a `sub`.)

- [ ] **Step 9: Run the tests to verify they pass, and see what else moved**

Run:
`timeout 300 uv run pytest -q tests/kernel/logic/test_targets.py tests/modules/spec/application/logic/ 2>&1 | grep -E "^FAILED|passed|failed"`

Expected: every test of Steps 1-4 PASS. Exactly one other failure:
`test_profile_parsing.py::test_references_reach_every_target_spec_reads_and_the_old_forms_are_each_refused_with_one`,
raising `InvalidArchitecture: layered.yaml: tiers.guard.imports.also: 'module.domain/values': no part the tier tests
lies in a <module> folder, so its tests mirror no module: write parts.domain/values` — its `guard` tier tests no part.

- [ ] **Step 10: Give `referencing()`'s guard a part it tests**

In `tests/modules/spec/application/logic/test_profile_parsing.py`, replace `referencing()` (lines 443-451) with:

```python
def referencing(services: dict, guard: dict) -> dict:
    """A profile of modules/<module>/ (domain, services) and kernel/, services tested by a tier guard in the folder
    architecture and the other parts untested: services writes the imports given, and the guard the keys given beside
    its folder."""
    return {"name": "refs", "testing": deepcopy(TESTING), "parts": {
        "modules/<module>/": {
            "domain/": {"role": "the rules", "untested": "read through services"},
            "services/": {"role": "the use cases", "tests": "guard", "imports": services}},
        "kernel/": {"role": "shared code", "untested": "too small to test"}},
        "tiers": {"guard": {"folder": "architecture"} | guard}}
```

The expectations of `test_references_reach_every_target_spec_reads_and_the_old_forms_are_each_refused_with_one` and
of `test_a_reference_written_wrong_is_refused_at_its_address` stay exactly as written: the guard now tests a
`<module>` part, so `module.domain/values` is the mirrored instance and the bare `domain/values` is still told
`module.domain/values (this module's) or parts.domain/values (any module's)`; the `a tier's also` row
(`module.kernel`) keeps its B3 text and the `a tier's may` row is no mirrored reader.

- [ ] **Step 11: Run the unit tier and the bundled-profile tests**

Run:
`timeout 600 uv run pytest -q tests/kernel tests/modules tests/bootstrap/test_bundled_imports.py 2>&1 | tail -3`
Expected: PASS, no failure. Then `uv run xarch profile check architecture.yaml 2>&1 | tail -1` — Expected:
`OK: the profile is valid`.

- [ ] **Step 12: Check line widths and lint**

Run: `git diff -U0 -- xarch tests | grep '^+' | grep -v '^+++' | awk 'length > 121'`
Expected: no output (121 counts the leading `+`). Wrap any hit by hand. Then `uv run ruff check` — Expected:
`All checks passed!` (never `--fix`).

- [ ] **Step 13: Commit**

```bash
git add xarch/kernel/logic/targets.py xarch/modules/spec/application/logic/targets_written.py \
  xarch/modules/spec/application/logic/profile_parsing.py tests/kernel/logic/test_targets.py \
  tests/modules/spec/application/logic/test_targets_written.py \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_profile_parsing.py
git commit -m "A tier's imports.also refuses <word>.<part> when no part the tier tests lies in a <word> folder (no part the tier tests lies in a <module> folder, so its tests mirror no module: write parts.<part>), a tier with only a folder too; one part in the folder is enough, each word judged on its own, the target part's folder still checked first; <part>@own and a bare name there name <word>.<part> only where it is accepted, else parts.<part>; target() and allowed_targets take the paths of the parts the tier tests in place of a bool, everything in also keeps both its messages for a tier with no part, and the references test's guard tests services so it proves what it proved"
```

---

### Task 2: Text — keys.yaml, README, CHANGELOG; golden docs unmoved

**Files:**
- Modify: `xarch/architectures/presets/format/keys.yaml:735-738`
- Modify: `README.md:229-232`
- Modify: `CHANGELOG.md:21-22`
- Check: `docs/cli/`, `docs/web/`, `docs/xarch/` (generated)

**Interfaces:** none (text only; `profile explain tiers.imports.also` prints `keys.yaml`).

- [ ] **Step 1: The checks that pin this text**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/bootstrap/test_profile_explain.py tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/test_explain.py 2>&1 | tail -2`
Expected: PASS, before and after this task. No test pins the `accepts:` text of `tiers.<tier>.imports.also`
(checked: `grep -rn "instance a test mirrors" tests` finds nothing), so the prose's check is Step 5.

- [ ] **Step 2: keys.yaml**

In `xarch/architectures/presets/format/keys.yaml`, replace the `accepts:` of `tiers.<tier>.imports.also` (lines
735-738):

```yaml
    accepts: >-
      references, as a part's `imports.may`, `<word>.<part>` the instance a test mirrors, and added to what each
      test of the tier may import of the app, such as the values a test builds its fakes' answers with; not
      `everything`. A target the bundled profile's tier does not give is listed by `profile check` as looser
```

with:

```yaml
    accepts: >-
      references, as a part's `imports.may`, `<word>.<part>` the instance a test mirrors, refused when no part the
      tier tests lies in a `<word>` folder (write `parts.<part>`), and added to what each test of the tier may
      import of the app, such as the values a test builds its fakes' answers with; not `everything`. A target the
      bundled profile's tier does not give is listed by `profile check` as looser
```

- [ ] **Step 3: README**

In `README.md`, replace lines 229-232:

```markdown
  part in the importer's own instance of the `<word>` folder, which the importer lies in too (in a tier's
  `imports.also`, the instance the test mirrors); either is optionally followed by `/<path>`, only that path below
  the part (`parts.store/schema`), and, in `imports.may`, `:<pattern>`, only the names that match the pattern,
  imported by name (`parts.store:*Id`). `everything` is no limit (also for `imports.libraries`); an entry written
```

with:

```markdown
  part in the importer's own instance of the `<word>` folder, which the importer lies in too (in a tier's
  `imports.also`, the instance the test mirrors, so a part the tier tests must lie in that folder); either is
  optionally followed by `/<path>`, only that path below the part (`parts.store/schema`), and, in `imports.may`,
  `:<pattern>`, only the names that match the pattern, imported by name (`parts.store:*Id`). `everything` is no
  limit (also for `imports.libraries`); an entry written
```

(The next line, `  `{parts.store: types_only}` is a target ...`, is unchanged; Markdown joins the lines.)

- [ ] **Step 4: CHANGELOG**

In `CHANGELOG.md`, `## [Unreleased]` → `### Added`, the first entry, replace its last two lines (21-22):

```markdown
  or parts.services`, and for a check's `place` the hint that a dotted name of code goes under `path`), `@` anywhere
  before the pattern, and a part's own instance of itself.
```

with:

```markdown
  or parts.services`, and for a check's `place` the hint that a dotted name of code goes under `path`), `@` anywhere
  before the pattern, and a part's own instance of itself. In a tier's `imports.also`, a word none of the parts the
  tier tests lies in is refused too (`'module.store': no part the tier tests lies in a <module> folder, so its tests
  mirror no module: write parts.store`), and `<part>@own` or a bare name there is then told `parts.<part>`.
```

- [ ] **Step 5: Read what `profile explain` prints, regenerate and read the golden docs**

Run: `uv run xarch profile explain tiers.imports.also 2>&1 | sed -n 1,9p`
Expected: the `accepts:` paragraph holds `refused when no part the tier tests lies in a `<word>` folder (write
`parts.<part>`)`.

The golden docs are regenerated by the same code `tests/bootstrap/test_docs_templates.py` compares
(`build_controllers().spec.docs(profile)` for `cli` and `web`, and xarch's own for `docs/xarch`; they come from
`xarch/architectures/testing.md` and the profiles, not from `keys.yaml`). Run:
`timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py 2>&1 | tail -2 && git status --short docs/`
Expected: PASS and no file under `docs/` listed (only `docs/superpowers/` may show as untracked or added). If a
golden doc test fails, read its diff and stop to report: no bundled profile's meaning changes in this card.

Then: `git diff -U0 -- README.md CHANGELOG.md xarch/architectures/presets/format/keys.yaml | grep '^+' | grep -v '^+++' | awk 'length > 121'`
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add xarch/architectures/presets/format/keys.yaml README.md CHANGELOG.md
git commit -m "profile explain tiers.imports.also says <word>.<part> is refused when no part the tier tests lies in a <word> folder, with parts.<part> to write; the README says a part the tier tests must lie in that folder, and the CHANGELOG's [Unreleased] adds the refusal with its message and that @own or a bare name there is then told parts.<part>; the golden docs, regenerated, do not move"
```

---

### Task 3: Every gate green on the branch

**Files:** none modified, unless a gate points at a line this card wrote.

**Interfaces:** none.

- [ ] **Step 1: The full suite, in the background**

Run (over two minutes; background it with `timeout` and read it at the end):
`timeout 900 uv run pytest -q > /tmp/8-5-suite.txt 2>&1; echo exit=$? >> /tmp/8-5-suite.txt`
Then: `tail -3 /tmp/8-5-suite.txt`
Expected: `... passed` with no `failed`, and `exit=0`. If a test under `tests/bootstrap/corpora/` or a recorded
finding moves, stop and report rather than edit the corpus.

- [ ] **Step 2: xarch on itself**

Run: `uv run xarch check > /dev/null; echo check=$?; uv run xarch check --strict > /dev/null; echo strict=$?`
Expected: `check=0` and `strict=0`.

- [ ] **Step 3: Lint and xarch's own profile**

Run: `uv run ruff check && uv run xarch profile check architecture.yaml 2>&1 | tail -1`
Expected: `All checks passed!` and `OK: the profile is valid`.

- [ ] **Step 4: Lines this card wrote**

Run: `git diff main...HEAD -U0 -- xarch tests README.md CHANGELOG.md | grep '^+' | grep -v '^+++' | awk 'length > 121'`
Expected: no output. If a line shows, wrap it by hand, rerun Steps 1-3, and commit:

```bash
git add <the files wrapped>
git commit -m "The lines this step ran past 120 columns are wrapped again; the text read is the same"
```

Otherwise there is nothing to commit in this task.

---

## Self-review (against the spec)

| Spec | Where |
|---|---|
| B1 (refused, incl. a tier with no parts; message; one problem) | Task 1 Steps 2, 3, 4, 6, 8 (kernel rows `no tested part...`, `a tier that tests no part`; parsing `a word`, `only a folder`) |
| B2 (accepted unchanged; one part enough; two words judged apart) | Task 1 Step 2 (`one tested part...`, `each word judged on its own`, `a tier testing parts of both words`); existing test l.297-301 unchanged |
| B3 (earlier checks keep their messages; `parts.` untouched) | Task 1 Step 2 (`...checked first`, `parts is never refused for it`); `referencing` `a tier's also` row |
| B4 (old forms by the same rule) | Task 1 Steps 2, 4 (four table cases each in kernel and parsing); no new code, `target()` already calls `_word_problem` |
| B5 (other readers; `everything`; check time) | Task 1 Step 3 (`everything` with `()`); `mirrored` None for every other caller; rules module untouched; full suite Task 3 |
| B6 (keys.yaml, docstrings, README, CHANGELOG, golden docs) | Task 1 Steps 6-7 (docstrings), Task 2 |
| Existing tests changed to keep proving | Task 1 Steps 1, 3, 10 |
| Gates | Task 3 |
| Review focus of the spec: truthiness, copied rule, per word, two problems / order, `subject` and `sub` | `is not None` everywhere (Step 7); one rule in `_word_problem`; `words` set compared with `prefix`; B1 after the two part checks; `subject` from `_tiers`, `parts[...].path` |
<!-- task-pipeline: validated -->
