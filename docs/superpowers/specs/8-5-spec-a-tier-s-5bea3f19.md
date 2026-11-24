# 8.5 spec: a tier's `imports.also` refuses a word none of its parts lies in

Card: 5bea3f19-c683-414f-bfde-a528aa344f38 (subtask of f1c96689), blocked by 8.4 (810682ee, done: branch tip
86b74a6). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3), sub-step 5 of its owning
note, the last before the wrap-up (story 9).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements 3.8 (lines 264-271), the default ruling that states it (lines 31-32), and section 6 sub-step 5
(line 456), reading 1.1 step 4 (lines 129-130). Dodges: note section 7, chiefly lines 470-471 and 474. From review 3:
O4, O5, O8.

## Goal

After this card, `<word>.<part>` in `tiers.<t>.imports.also` is refused when no part the tier tests lies in a
`<word>` folder: such a tier's tests mirror no instance of that folder, so `own` would reach nothing. Where a part
the tier tests does lie in a `<word>` folder, `<word>.<part>` stays what it is today: the instance the test mirrors,
`Target(part, "own", ...)`, the same value every other key gives (note line 470-471: no separate resolution path for
tests). The old forms in `also` (`<part>@own`, a bare repeating name), already refused by 8.4, name the replacement by
the same rule: `<word>.<part>` only where it would now be accepted, else `parts.<part>`. Nothing a bundled profile
writes changes meaning; `architecture.yaml`'s one `also` list stays accepted.

## What is already there (not to be redone)

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

## Inherited constraints

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

## Definitions

- *the tier's parts*: the parts whose `tests` names the tier (`subject`); `untested` parts and a tier's `folder` are
  not among them.
- *a part lies in a `<W>` folder*: `repeat_of(repeats, path).word == W` (`xarch/kernel/logic/placement.py`), as
  `_word_problem` already reads it for the target part and the importer.
- *mirrored reader*: the reader of `tiers.<t>.imports.also`, and only it.

## Behavior

### B1. A word none of the tier's parts lies in is refused

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

### B2. A word one of the tier's parts lies in is accepted, unchanged

When at least one of the tier's parts lies in a `<W>` folder, `<W>.<part>[/<path>]` reads to
`Target(part, "own", steps)` exactly as today. It is enough that one part does; the others may lie elsewhere (the
unit tier of `architecture.yaml` tests parts in `modules/<module>/` and `kernel`, `platform` outside).

With two words (`<module>` and `<unit>`), each word is judged on its own: a tier testing only `<module>` parts accepts
`module.x` and refuses `unit.y` with B1's message for `<unit>`; a tier testing parts of both accepts both.

### B3. The checks before it keep their messages

A word for a part in no `<W>` folder, or in another word's folder, keeps today's message (`part 'kernel' lies in no
<module> folder: write parts.kernel`; `part 'store' lies in the <unit> folder, not <module>: write parts.store`), even
when B1 would also apply. `parts.<part>` in `also` is never affected by B1.

### B4. The old forms name the replacement by the same rule

In `also`, `<part>@own` and the bare name of a repeating part (already refused by 8.4) name `<W>.<part>` only where
B2 would accept it, else `parts.<part>`:

| Written in `also` | Tier's parts | Problem (after the address) |
|---|---|---|
| `service@own` | `service` (in `<module>`) | `'service@own': @own was removed in 0.3.0: write module.service` (today) |
| `service@own` | `shared` only (outside) | `'service@own': @own was removed in 0.3.0: write parts.service` |
| `service` | `service` | `'service': a bare part name was removed in 0.3.0: write module.service (this module's) or parts.service (any module's)` (today) |
| `service` | `shared` only, or none | `'service': a bare part name was removed in 0.3.0: write parts.service` |

A replacement offered is always one `profile check` then accepts.

### B5. Other readers are untouched

A part's `imports.may` / `imports.must`, a tier's `imports.may`, a check's `place`: no change in what they accept or
say. `everything` in `also` keeps both of today's messages (`must be a list of targets such as [parts.core,
unit.store/schema]: `everything` is not taken, ...` and `` `everything` is not taken, name each target ... ``), also
for a tier with no parts. Check time (`rules`) is not touched: a target accepted here means what it meant before.

### B6. Text

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

## Interface the planner should give it (suggested, not binding)

The kernel must learn the tier's parts without learning about tiers. Suggested: `target()`'s and
`allowed_targets()`'s `mirrored: bool` becomes `mirrored: Collection[tuple[str, ...]] | None = None` (the paths of
the parts the tests mirror; None when the reader is no test), threaded to `_reference` and `_word_problem`; `_tier`
passes `tuple(parts[s.part].path for s in subject)`. Every place that tests `mirrored` for truth must test
`is not None` instead: an empty tuple (a tier with no parts) is still a mirrored reader for the `everything` messages
and must still be refused by B1, not read as an importer-less `a tier's folder`. Keeping `mirrored: bool` and adding a
separate keyword is acceptable if the planner prefers; either way there is one rule, in `_word_problem`, used by both
branches of `target()`.

## Out of scope

- The wrap-up of the release (story 9): version, release notes, the final cohesion pass.
- Refusing `parts.X` beside `module.X` in one list (rulings line 35, a later change).
- Any change to `Target`, the writers (`written_target`, `_place`, `_shown`), the rules module, or check-time
  matching of `own` for a test.
- Readers other than `tiers.<t>.imports.also` (B5).
- A tier's `imports.must` / `.types_only`, which refuse `<word>.` already (8.4).
- Corpora: none writes `also`; if a recorded finding moves, stop and report rather than edit.

## Tests

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

## Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run
xarch profile check architecture.yaml`.

## Review focus for the planner

- `mirrored` tested for truth somewhere after it becomes a collection: an empty tested set then loses B1 or the
  `everything` messages (rows 5, 10, 12).
- The old-form branch computing its replacement by a copy of the rule instead of `_word_problem`: B4 offering
  `module.x` that B1 then refuses.
- B1 judged per target part's folder rather than per word: a tier testing `<module>` parts refusing `module.x` for a
  part in another module-level path, or accepting `unit.y` because some tested part is in any repeating folder.
- Two problems for one value (B3's message and B1's both), or B1 firing before the "part lies in the word's folder"
  check.
- `subject` read before `_coverage` filled it, or a part's `sub` path used instead of the part's own path.
