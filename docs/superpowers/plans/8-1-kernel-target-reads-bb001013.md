# 8.1 kernel: `target()` reads the new reference grammar beside the old

Card: bb001013-7ae0-407b-87d0-5bcc69d34136 (subtask of f1c96689). Release step 24 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3, row 24 at line 287), sub-step 1 of its owning note.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements section 1 with 1.1 to 1.4 (lines 91-152), the section 4 rows that do not need the old forms
refused (lines 293-325), and section 6 sub-step 1 (lines 445-447). From review 3: O4, O5, O8 (lines 228-232).

## Goal

`target()` reads `parts.<part>` and `<word>.<part>`, each optionally followed by `/<path>` and `:<pattern>`. The word
comes from the repeating folders of the profile being read. `target()` still reads every old form (`<part>`,
`<part>@any`, `<part>@own` refused as today, `/<path>`, `:<pattern>`) exactly as it does now. No profile changes. No
writer changes. No old form is refused.

## What is already there (not to be redone)

- `target(value, owner, parts, declared, where, problems, patterns=False, mirrored=False, *, alone)` in
  `xarch/kernel/logic/targets.py:20-77` parses the old grammar with `TARGET` (line 15). It returns
  `Target(part, scope, sub, names)` (`xarch/profile_values/placement.py:21-29`, scope `own`/`any`/`none`). `parts`
  maps each placed part to its path, with the repeating step written as `EACH` (`*`). `_implied` (lines 80-85) words
  the self-import refusal.
- `Repeat(word, root)` (`profile_values/placement.py:13-17`). `root_of` and `repeat_of(repeats, pattern)`
  (`xarch/kernel/logic/placement.py:25-33`) give a path's repeating folder and its word. `targets.py` already imports
  `root_of` from that module.
- The repeats exist where every caller runs: `_Layout.repeats` in `parse_profile`
  (`xarch/modules/spec/application/logic/profile_parsing.py:199`, `built = _layout(...)`, `repeats` built at 287-312),
  and the rules' `Profile.repeats` (`xarch/modules/rules/domain/profile.py:86`, filled by
  `rules/adapters/spec_profile.py:67`).
- Callers of `target()`: `allowed_targets` (`spec/application/logic/targets_written.py:18-42`), itself called by
  `imports_written.may` (lines 56-72), `imports_written.must` (lines 75-95) and `profile_parsing._tier` (lines 669,
  671, `mirrored=True` for `imports.also`); and `own_checks._match` (`rules/application/logic/own_checks.py:113`,
  the check target `place`, `alone="a check that names no part"`).
- `everything` is caught by `allowed_targets` (`WORD`, line 24 and 34) before `target()` runs.

## Inherited constraints

- Grammar (note section 1, lines 94-104): `reference := prefix "." part [ "/" path ] [ ":" pattern ]`,
  `prefix := "parts" | word`. `path` as today, and now no `@`. `pattern` as today, and only where the key takes one.
- The first dot ends the prefix (note, facts, line 66-67: neither a part name nor a word can hold a dot).
- Resolution (note 1.1, lines 124-132): the part must be declared; a declared part that places no file is passed over
  with no problem; `parts.` gives `any` when the part's path holds a word, `none` when not; `<word>.` needs the
  prefix to be a word of the profile, the target part's path to hold that word, and the importer to lie in that
  word's folder; the self-import rule stays.
- In a tier's `imports.also` (`mirrored`), `<word>.<part>` is the instance the test mirrors, through the same
  `Target(part, "own")`; the importer test is skipped there as today (note 3.8, lines 264-271). The 3.8 refusal
  (no part the tier tests lies in the word's folder) is sub-step 5 and out of scope.
- 3.9 (lines 273-276): `module.adapters` in `adapters` is implied and refused; `parts.adapters` in `adapters` stays
  valid; `parts.platform` in `platform` is implied and refused.
- 3.10 (lines 278-282): `@` is not part of the new grammar, in a prefix, a part, a path or a pattern.
- 1.4 (lines 149-152): a part named `everything` becomes nameable as `parts.everything`.
- 3.1 and the default of line 34: a check target `place` whose prefix is no word gets the hint about `path`.
- Message shape (section 4, lines 295-298): the address, the value, what is wrong, what to write. A new form written
  wrong keeps a plain description. Prefer the section 4 wording verbatim.
- Dodges (section 7, lines 461-480): no fourth scope and no `word` field on `Target`; no code path that knows the word
  `module` or the parts of a bundled profile; `<word>.` resolves the same in tests; `<word>.` from an importer outside
  the folder is refused, never accepted to match nothing.
- `target()` gains the repeats (note 5.3, line 390).

## Behavior

### Which grammar a value is read by

A string value is a new reference when its head holds a `.`. The head is the text before the first `/` or `:`, or the
whole value when it has neither. Every other value goes down today's path unchanged, byte for byte, including its
messages: a bare name, `@any`, `@own`, an unknown scope, `/path`, `:pattern`, a non-string, the empty string.

So `kernel/x.py` and `kernel:a.b` are old forms (the dot is after the head). `domain.x` was read before as the part
`domain.x` ("names no part 'domain.x'"). It is now a new reference with the prefix `domain`, and gets the message
below for a prefix that is no word.

### Reading a new reference

`rest` is everything after the first dot. `part` is `rest` up to its first `/` or `:`. `sub` and `names` come from
`rest` as today: `/` starts the path, the first `:` starts the pattern. The checks run in this order, and the first
that fails gives the one problem of the value. Each problem is said at `where`.

1. **Not a reference.** The prefix is empty, `part` is empty, `part` holds a `.`, or `@` appears before the first
   `:`. Examples: `parts.`, `.domain`, `parts..x`, `parts.contract@any`, `module.services/schema@any`.
   Message: `{where}: {value!r} is not a reference: write parts.<part> or <word>.<part>, optionally followed by
   /<path> and :<pattern>`.
2. **Brackets.** The prefix is `<inner>` with `inner` not empty.
   Message: `{where}: {value!r}: write the word without brackets: {inner}.{rest}`. This holds whether or not `inner`
   is a word of the profile.
3. **Prefix is no word.** The prefix is neither `parts` nor the word of any repeat given.
   Message: `{where}: {value!r}: {prefix!r} is neither parts nor a word of this profile ({words}): a profile names no
   instance; write {replacement}`.
   - `{words}` is the words of the repeats in the order given, joined by `, `. With no repeats the parenthesis is
     replaced: `... a word of this profile, which has none: a profile names no instance; ...`.
   - `{replacement}` is `{w}.{rest} or parts.{rest}` when `part` is placed and its path lies in the folder of the
     word `w`. It is `parts.{rest}` when `part` is placed and its path holds no word. Otherwise it is the literal
     `parts.<part> or <word>.<part>`.
   - When the caller says it reads a check target `place`, `; a dotted name of code goes under path` is added at the
     end.
4. **Name pattern.** Today's three checks and texts, in today's order: a pattern where the key takes none (`drop
   ':{names}'`), an empty pattern, a pattern that is not one.
5. **Part.** `part` not declared: `{where}: {value!r} names no part {part!r}` (today's text). Declared and not
   placed: `None`, with no problem.
6. **Path.** Today's check and text (`has an invalid path after the part`).
7. **Scope.**
   - `parts.`: `any` when the part's path holds `EACH`, else `none`.
   - `<word>.`: the target part must lie in that word's folder. The word of a path is
     `repeat_of(repeats, path).word`; a path with no `EACH`, or with an `EACH` whose root no repeat has, has no word.
     - Target path has no word: `{where}: {value!r}: part {part!r} lies in no <{prefix}> folder: write parts.{rest}`.
     - Target path has another word `u`: `{where}: {value!r}: part {part!r} lies in the <{u}> folder, not
       <{prefix}>: write parts.{rest}`.
   - Then, unless `mirrored`, the importer must lie in the same word's folder:
     - No owner: `{where}: {value!r}: {alone} lies in no <{prefix}> folder, so it has no own {prefix}: write
       parts.{rest}`.
     - Owner whose path has no word: `{where}: {value!r}: part {owner!r} lies in no <{prefix}> folder, so it has no
       own {prefix}: write parts.{rest}`.
     - Owner whose path has another word: `{where}: {value!r}: part {owner!r} lies in no <{prefix}> folder: write
       parts.{rest}`.
   - Both hold (or `mirrored`): `own`.
8. **Self-import.** The scope is not `any` and `part` is the owner's name: refused as implied.
   - Owner path holds `EACH`: `{where}: {value!r} is implied: a part may always import itself, its own instance of
     the repeating folder; remove it (parts.{part}, another instance's too, stays allowed)`.
   - Otherwise: today's text, `{where}: {value!r} is implied: a part may always import itself; remove it`.
   - An old form keeps today's parenthesis (`{part}@any, ...`).
9. Otherwise the result is `Target(part, scope, steps, names or "")`.

A word is compared as written. Nothing in the code names a particular word. `parts.parts` (a part named `parts`, note
3.2) and names with `-` (`parts.kernel-logic`, `sub-unit.store`, note 3.5) read as written.

### Interface

- `target()` gains a keyword-only, required `repeats: Collection[Repeat]`. A required argument means no caller can
  leave out the new grammar by mistake. It also gains a keyword-only `place: bool = False`, which is true only for
  the check target `place`. `Target` does not change.
- `allowed_targets` gains a keyword-only, required `repeats` and passes it on. `imports_written.may`, `.must`,
  `profile_parsing._tiers` and `._tier` take the repeats too. `parse_profile` passes `built.repeats`.
- `own_checks._match` passes `profile.repeats` and `place=True`.
- Docstrings (xarch's code has no comments) say the new grammar: the module docstring of `targets.py` (lines 1-4),
  `target()`'s docstring, and `allowed_targets`'s and `targets_written.py`'s module docstring (lines 1-4).

### Docs

- `README.md`: the symbols bullet at line 227 gains one sentence saying that `parts.<part>` (the part in every
  instance) and `<word>.<part>` (the part in the importer's own instance of the `<word>` folder) are read too, with
  `/<path>` and `:<pattern>`. The old forms stay described: they are still the bundled spelling (review 3 O4).
- `CHANGELOG.md`, `## [Unreleased]`, `### Added`: one entry. `imports.may`, `imports.must`, a tier's `imports.may`
  and `imports.also`, and a check's `place` read `parts.<part>` and `<word>.<part>` beside the old forms. Say how each
  resolves and the refusals of a reference written wrong. No old form is refused yet (review 3 O5).
- Golden docs `docs/{cli,web,xarch}/testing.md` (and the rest of `docs/{cli,web,xarch}`) are regenerated the way
  commit ddea9db did, and the diff is read. No diff is expected (note 5.3, line 417-418: the docs phrase prints
  paths). Any diff is a defect to report, not to regenerate past (review 3 O8).

## Tests that prove it (written first, each seen failing)

Tiers are xarch's own (`architecture.yaml`, `tiers`). `unit` is for a pure rule of the kernel or a module. Every test
below is `unit`: `target()` and `allowed_targets` are pure functions, `parse_profile` is a pure function of a mapping,
and `own_checks._targets` is pure logic of rules. No integration or wired test is added: no use case, command or
bundled profile changes, and the gates (`xarch check`, `profile check architecture.yaml`, the full suite) already
read the bundled profiles end to end.

### `tests/kernel/logic/test_targets.py` (unit: the parser is kernel logic)

Fixture, added beside today's:

```
PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"), "kernel": ("kernel",),
         "kernel-logic": ("kernel", "logic"), "store": ("units", "*", "store"), "cli": ("cli",)}
REPEATS = (Repeat("module", ("modules",)), Repeat("unit", ("units",)))
owners: SERVICES, DOMAIN = ("domain", PARTS["domain"]), CLI = ("cli", ("cli",)), KERNEL = ("kernel", ("kernel",)),
        LEDGER = ("ledger", ("units", "*", "ledger"))
```

Every existing test passes `repeats=REPEATS` and keeps its expected value. That proves the old forms still parse.

**T1. Table: a reference is read** (`target(..., patterns=True, alone="a tier's folder", repeats=REPEATS)`, no
problem). One id per line of the section 1 table, plus the combinations:

| id (short) | written | owner | found |
|---|---|---|---|
| parts, part repeats | `parts.domain` | CLI | `Target("domain", "any")` |
| parts, part does not repeat | `parts.kernel` | SERVICES | `Target("kernel", "none")` |
| word, own instance | `module.domain` | SERVICES | `Target("domain", "own")` |
| a path below | `module.services/schema` | DOMAIN | `Target("services", "own", ("schema",))` |
| a name pattern | `parts.domain:*Id` | SERVICES | `Target("domain", "any", (), "*Id")` |
| parts, path and pattern | `parts.domain/values:*Id` | CLI | `Target("domain", "any", ("values",), "*Id")` |
| word, path and pattern | `module.domain/values:*Id` | SERVICES | `Target("domain", "own", ("values",), "*Id")` |
| parts, path | `parts.domain/published` | CLI | `Target("domain", "any", ("published",))` |
| a second word | `unit.store` | LEDGER | `Target("store", "own")` |
| a name with a dash | `parts.kernel-logic` | SERVICES | `Target("kernel-logic", "none")` |
| the part itself in every instance (3.9) | `parts.services` | SERVICES | `Target("services", "any")` |
| a tier's folder, every instance | `parts.domain` | None | `Target("domain", "any")` |

The section 1 row `everything` is the callers' (T5 and the existing "everything names no part" row).

**T2. Table: a reference written wrong is None with its one problem** (`patterns=True` unless the row says not).
One id per section 4 row that does not need the old forms refused, plus the 3.10 rows:

| written | owner | problem (where = `at`) |
|---|---|---|
| `module.kernel` | SERVICES | `at: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel` |
| `module.domain` | CLI | `at: 'module.domain': part 'cli' lies in no <module> folder, so it has no own module: write parts.domain` |
| `module.domain` | None | `at: 'module.domain': a tier's folder lies in no <module> folder, so it has no own module: write parts.domain` |
| `module.store` | SERVICES | `at: 'module.store': part 'store' lies in the <unit> folder, not <module>: write parts.store` |
| `unit.store` | DOMAIN | `at: 'unit.store': part 'domain' lies in no <unit> folder: write parts.store` |
| `orders.services` | DOMAIN | `at: 'orders.services': 'orders' is neither parts nor a word of this profile (module, unit): a profile names no instance; write module.services or parts.services` |
| `<module>.services` | DOMAIN | `at: '<module>.services': write the word without brackets: module.services` |
| `parts.nope` | SERVICES | `at: 'parts.nope' names no part 'nope'` |
| `parts.` | SERVICES | the not-a-reference text |
| `.domain` | SERVICES | the not-a-reference text |
| `parts..x` | SERVICES | the not-a-reference text |
| `parts.domain@any` | SERVICES | the not-a-reference text (3.10) |
| `module.services/schema@any` | DOMAIN | the not-a-reference text (3.10) |
| `module.services` | SERVICES | `at: 'module.services' is implied: a part may always import itself, its own instance of the repeating folder; remove it (parts.services, another instance's too, stays allowed)` |
| `parts.kernel` | KERNEL | `at: 'parts.kernel' is implied: a part may always import itself; remove it` |
| `parts.kernel:*Id`, `patterns=False` | SERVICES | `at: 'parts.kernel:*Id' has a name pattern, which this key does not take: drop ':*Id'` |
| `module.services/../x` | DOMAIN | `at: 'module.services/../x' has an invalid path after the part` |

The not-a-reference text is `at: {value!r} is not a reference: write parts.<part> or <word>.<part>, optionally
followed by /<path> and :<pattern>`.

**T3. Table: a test reads a reference from the instance it mirrors** (`owner=None, mirrored=True`):
`module.domain/values` gives `Target("domain", "own", ("values",))`; `parts.domain` gives `any`; `parts.kernel`
gives `none`; `module.kernel` is refused with the "lies in no <module> folder" text. This proves `<word>.` resolves
the same in tests and only the importer test is skipped.

**T4. The check target `place` hints at `path`** (`place=True`, `alone="a check that names no part"`):
`os.environ` from SERVICES gives `at: 'os.environ': 'os' is neither parts nor a word of this profile (module, unit):
a profile names no instance; write parts.<part> or <word>.<part>; a dotted name of code goes under path`. The same
value without `place` has no hint. `module.domain` with no owner and `place=True` uses the caller's words: `a check
that names no part lies in no <module> folder, so it has no own module: write parts.domain`.

**T5. A part named `everything` is nameable** (note 1.4): with `{"everything": ("everything",)}`,
`parts.everything` gives `Target("everything", "none")`.

**T6. The word comes from the profile's repeats, never from the code**: with parts `{"core": ("packages", "*",
"core"), "api": ("packages", "*", "api")}` and repeats `(Repeat("pkg", ("packages",)),)`, `pkg.core` from `api`
gives `Target("core", "own")`. `module.core` gives `... 'module' is neither parts nor a word of this profile (pkg):
a profile names no instance; write pkg.core or parts.core`.

**T7. A profile with no repeating folder**: with `PARTS` limited to `kernel` and `cli` and `repeats=()`,
`orders.kernel` gives `... 'orders' is neither parts nor a word of this profile, which has none: a profile names no
instance; write parts.kernel`, and `parts.kernel` from `cli` gives `none`.

**T8. A dot after the head is the old grammar**: `kernel/x.py` from SERVICES gives `Target("kernel", "none",
("x.py",))`, as today.

### `tests/modules/spec/application/logic/test_targets_written.py` (unit: spec logic)

**T9.** `allowed_targets(["parts.kernel", "module.domain", "parts.domain/values"], services_part, ...,
repeats=...)` gives the three targets in order. `allowed_targets(["module.domain/values"], None, ...,
mirrored=True, repeats=...)` gives `own`. Existing tests pass the repeats and stay green.

### `tests/modules/spec/application/logic/test_profile_parsing.py` (unit: `parse_profile` is pure)

**T10.** A small inline profile (`modules/<module>/` with `domain` and `services`, and `kernel` outside) writes
`services: imports: {may: [module.domain, parts.kernel, {parts.domain: types_only}], must: [parts.kernel]}` and a
tier with `folder` and `imports: {may: [parts.kernel], also: [module.domain/values]}`. It parses with no problem.
Its `services` rules equal those the same profile gets when written in the old forms (`[domain, kernel,
{domain@any: types_only}]`, `must: [kernel]`), and likewise for the tier's allowance and `also`. This proves the
repeats reach every caller in spec.

**T11.** The same profile with `module.kernel` in `services`' `imports.may` gives the one problem
`parts.services.imports.may: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel`.

### `tests/modules/rules/application/logic/test_own_checks.py` (unit: rules logic)

**T12.** A check of the profile's own whose target `place` is `[parts.kernel]` is read to
`Match("place", places=(Target("kernel"),))`. `[os.environ]` gives the problem of T4 at
`checks.<id>.<slot>.place`. This proves the rules caller passes the repeats and `place=True`.

### Already-existing tests that must stay green unchanged in meaning

`tests/modules/rules/application/logic/test_written.py` (the round trip: what `_place` writes, `target()` reads back)
only gains `repeats=` on its call. The whole suite, including every inline profile that writes old forms.

## Out of scope

- Writers `_place` (`written.py:84`) and `_shown` (`looseness.py`) writing the new form: card 8.2.
- Bundled profiles, `architecture.yaml`, `keys.yaml`, the list-shape messages (`targets_written.py:27`,
  `profile_parsing.py` list texts), the tier keys `imports.must` and `imports.types_only` reading references (today
  `ck.part_names`; this is why section 4's `module.controller` row in those keys is not built here), and the tests'
  and corpora's spelling: card 8.3.
- Refusing the old forms (`@any`, `@own`, bare names), `names a part outside imports`, and the word `parts` refused by
  the tree's reader (3.3): card 8.4. Until then `@own` and the unknown-scope texts stay as they are.
- The 3.8 refusal in `imports.also`: sub-step 5.
- No `profile migrate`, no rewriting on load.

## Gates

Each passes on this branch alone: `uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch check
--strict`, `uv run xarch profile check architecture.yaml`, and `uv run pytest -q` (over two minutes: run it in the
background with `timeout`, read it at the end).

## Project rules

No comments in xarch's code (docstrings only). Tests are written first. Examples are simple, with absolute `app.`
imports. Recorded corpora (`tests/bootstrap/corpora/`) are not touched. Python only in the reader adapter and the data
files under `xarch/architectures/presets/`. `.claude/` stays out of commits. Nothing is pushed.

---

# 8.1 kernel: `target()` reads the new reference grammar beside the old, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `target()` reads `parts.<part>` and `<word>.<part>` (each with optional `/<path>` and `:<pattern>`), the
word taken from the profile's repeating folders, while every old form reads exactly as today.

**Architecture:** `xarch/kernel/logic/targets.py` sends a string whose head (text before the first `/` or `:`) holds a
`.` to a new private `_reference` reader, and everything else down today's path unchanged. `target()` gains a required
keyword `repeats` and a keyword `place`. The repeats are threaded from `parse_profile` (`built.repeats`) through
`_tiers`/`_tier`, `imports_written.may`/`.must` and `allowed_targets`, and from `Profile.repeats` in
`own_checks._match`, which also passes `place=True`.

**Tech Stack:** Python 3.13, pytest, ruff, uv. Run everything with `uv run` from the worktree root.

**Spec:** `docs/superpowers/specs/8-1-kernel-target-reads-bb001013.md` (prepended above).

## Global Constraints

- Grammar: `reference := prefix "." part [ "/" path ] [ ":" pattern ]`, `prefix := "parts" | word`. No `@` in a
  reference before its `:`.
- A string value is a new reference when its head holds a `.`; every other value goes down today's path unchanged,
  byte for byte, including its messages.
- `target()` gains a keyword-only, required `repeats: Collection[Repeat]` and a keyword-only `place: bool = False`.
  `Target` does not change: no fourth scope, no `word` field.
- No code path knows the word `module` or the parts of a bundled profile.
- No comments in xarch's code (docstrings only). Lines at most 140 characters (`ruff.toml`).
- No profile changes, no writer changes (`written.py:_place`, `looseness.py:_shown` untouched), no old form refused.
- Recorded corpora (`tests/bootstrap/corpora/`) are not touched. `.claude/` stays out of commits. Nothing is pushed.
- Never `ruff check --fix`. The full suite takes over two minutes: run it in the background with `timeout`.
- Gates: `uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`,
  `uv run xarch profile check architecture.yaml`, `uv run pytest -q`.

## Review Focus

1. A declared part that places no file, written as a reference (`parts.ghost`): `None` with no problem, as the old
   form does. Test added to Task 1 (`test_a_reference_to_a_part_declared_but_not_placed_is_none_with_no_problem`).
2. A dot inside an old form's pattern (`kernel:a.b`) must stay old grammar: the head is `kernel`. Test added to Task 1
   (T8 table).
3. `@` after the `:` of a reference (`parts.kernel:a@b`) is a bad name pattern, not "not a reference". Test added to
   Task 1 (T2 table, row "an @ inside the pattern").
4. A part named `parts` (`parts.parts`, note 3.2) reads as written. Test added to Task 1
   (`test_a_part_named_parts_is_named_parts_parts`).
5. Non-string and empty values (`3`, `""`) keep today's "is not a target" text. Test added to Task 1 (T8 table).

## File Structure

- Modify `xarch/kernel/logic/targets.py` — the parser: today's path plus `_reference`, `_prefix_problem`,
  `_word_problem`, `_pattern_problem`, `_steps`; `_implied` gains the name of the other instances.
- Modify `xarch/modules/spec/application/logic/targets_written.py` — `allowed_targets` takes and passes `repeats`.
- Modify `xarch/modules/spec/application/logic/imports_written.py` — `may`, `must` take and pass `repeats`.
- Modify `xarch/modules/spec/application/logic/profile_parsing.py` — passes `built.repeats` to `iw.may`, `iw.must`,
  `_tiers`, `_tier`.
- Modify `xarch/modules/rules/application/logic/own_checks.py` — passes `profile.repeats` and `place=True`.
- Tests: `tests/kernel/logic/test_targets.py`, `tests/modules/rules/application/logic/test_written.py`,
  `tests/modules/spec/application/logic/test_targets_written.py`,
  `tests/modules/spec/application/logic/test_profile_parsing.py`,
  `tests/modules/rules/application/logic/test_own_checks.py`.
- Docs: `README.md`, `CHANGELOG.md`; golden docs `docs/{cli,web,xarch}/` checked unchanged.

Task order and why: Task 1 makes `repeats` required in the kernel and has the two spec/rules callers pass `repeats=()`
for one commit (old forms only, behavior identical), so that Tasks 2 and 3 each start from a genuinely failing test
when they thread the real repeats.

---

### Task 1: `target()` reads references beside the old forms

**Files:**
- Modify: `xarch/kernel/logic/targets.py` (whole file, 85 lines today)
- Modify: `xarch/modules/spec/application/logic/targets_written.py:38-39` (the `target(...)` call)
- Modify: `xarch/modules/rules/application/logic/own_checks.py:113-114` (the `target(...)` call)
- Test: `tests/kernel/logic/test_targets.py` (whole file)
- Test: `tests/modules/rules/application/logic/test_written.py:1-30`

**Interfaces:**
- Consumes: `Repeat(word: str, root: tuple[str, ...])` from `xarch.profile_values.placement`;
  `repeat_of(repeats: Iterable[Repeat], pattern: tuple[str, ...]) -> Repeat | None` and `root_of` from
  `xarch.kernel.logic.placement`; `EACH` from `xarch.kernel.placement`.
- Produces: `target(value, owner, parts, declared, where, problems, patterns=False, mirrored=False, *, alone: str,
  repeats: Collection[Repeat], place: bool = False) -> Target | None`. Tasks 2 and 3 call it with `repeats=` and
  (Task 3) `place=True`.

- [ ] **Step 1: Write the failing tests**

Replace the whole of `tests/kernel/logic/test_targets.py` with:

```python
"""How a profile writes a target, read against the parts by their paths, the part that writes it and the profile's
repeating folders: the old forms (a bare name, @any, /<path>, :<pattern>) as before, and the references parts.<part>
and <word>.<part>, each read or refused with its one problem."""
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


READ = [
    pytest.param("domain", SERVICES, Target("domain", "own"), id="a bare name in the importer's repeating folder is its own instance"),
    pytest.param("domain@any/values", SERVICES, Target("domain", "any", ("values",)), id="any instance, and a path below"),
    pytest.param("kernel:*Id", SERVICES, Target("kernel", "none", (), "*Id"), id="a part outside, narrowed by a name pattern"),
    pytest.param("domain@any", None, Target("domain", "any"), id="a scope of no part reaches an instance only by @any"),
]


@pytest.mark.parametrize("written, owner, found", READ)
def test_a_target_is_read_from_its_written_form(written, owner, found):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems, patterns=True, alone="a tier's folder",
                   repeats=REPEATS), problems) == (found, [])


@pytest.mark.parametrize("written, owner, problem", [
    pytest.param("nowhere", SERVICES, "at: 'nowhere' names no part 'nowhere'", id="a part the profile has not"),
    pytest.param("domain", None, "at: 'domain' lies in the repeating folder, which a tier's folder is not in: say "
                                 "domain@any", id="an instance asked for from outside the repeating folder"),
    pytest.param("services", SERVICES, "at: 'services' is implied: a part may always import itself, its own instance "
                                       "of the repeating folder; remove it (services@any, another instance's too, stays "
                                       "allowed)", id="the part itself"),
    pytest.param("kernel:*Id", SERVICES, "at: 'kernel:*Id' has a name pattern, which this key does not take: drop "
                                         "':*Id'", id="a name pattern where none is allowed"),
    pytest.param("everything", SERVICES, "at: 'everything' names no part 'everything'",
                 id="everything is no part: the key that takes it alone says so"),
])
def test_a_target_that_is_not_one_is_none_with_its_problem(written, owner, problem):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems, alone="a tier's folder", repeats=REPEATS),
            problems) == (None, [problem])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("domain/values", Target("domain", "own", ("values",)), [],
                 id="a bare name in the repeating folder is the instance the test mirrors"),
    pytest.param("domain@any", Target("domain", "any"), [], id="any instance stays any"),
    pytest.param("kernel", Target("kernel"), [], id="a part outside the repeating folder is in no instance"),
    pytest.param("domain@own", None, ["at: 'domain@own' says what a bare name already says: write domain"],
                 id="the mirrored instance written out is refused"),
])
def test_a_target_a_test_reads_is_read_from_the_instance_it_mirrors(written, found, problem):
    problems: list[str] = []
    assert (target(written, None, PARTS, PARTS, "at", problems, mirrored=True, alone="a tier's folder", repeats=REPEATS),
            problems) == (found, problem)


@pytest.mark.parametrize("pattern", [
    pytest.param("*Id", id="letters and a star"),
    pytest.param("$*", id="a mark another language starts its names with"),
    pytest.param("%Doc*", id="another such mark"),
    pytest.param("Détail*", id="a letter that is not ascii"),
])
def test_a_name_pattern_is_any_text_but_whitespace_and_the_separators_of_a_target(pattern):
    assert target(f"kernel:{pattern}", SERVICES, PARTS, PARTS, "at", [], patterns=True, alone="a tier's folder",
                  repeats=REPEATS) == Target("kernel", "none", (), pattern)


@pytest.mark.parametrize("written", ["kernel:a b", "kernel:a@b", "kernel:a:b"])
def test_a_name_pattern_with_whitespace_or_a_separator_is_refused(written):
    problems: list[str] = []
    assert (target(written, SERVICES, PARTS, PARTS, "at", problems, patterns=True, alone="a tier's folder",
                   repeats=REPEATS), problems) == (
        None, [f"at: {written!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` "
               "standing for any text"])


def test_what_names_no_part_is_named_in_the_callers_words():
    problems: list[str] = []
    target("domain", None, PARTS, PARTS, "at", problems, alone="a check that names no part", repeats=REPEATS)
    assert problems == ["at: 'domain' lies in the repeating folder, which a check that names no part is not in: say "
                        "domain@any"]


@pytest.mark.parametrize("written, owner, found", [
    pytest.param("parts.domain", CLI, Target("domain", "any"), id="parts, a part that repeats, is every instance"),
    pytest.param("parts.kernel", SERVICES, Target("kernel", "none"), id="parts, a part that does not repeat"),
    pytest.param("module.domain", SERVICES, Target("domain", "own"), id="a word, the importer's own instance"),
    pytest.param("module.services/schema", DOMAIN, Target("services", "own", ("schema",)), id="a path below"),
    pytest.param("parts.domain:*Id", SERVICES, Target("domain", "any", (), "*Id"), id="a name pattern"),
    pytest.param("parts.domain/values:*Id", CLI, Target("domain", "any", ("values",), "*Id"),
                 id="parts, a path and a pattern"),
    pytest.param("module.domain/values:*Id", SERVICES, Target("domain", "own", ("values",), "*Id"),
                 id="a word, a path and a pattern"),
    pytest.param("parts.domain/published", CLI, Target("domain", "any", ("published",)), id="parts, a path"),
    pytest.param("unit.store", LEDGER, Target("store", "own"), id="a second word"),
    pytest.param("parts.kernel-logic", SERVICES, Target("kernel-logic", "none"), id="a name with a dash"),
    pytest.param("parts.services", SERVICES, Target("services", "any"), id="the part itself in every instance"),
    pytest.param("parts.domain", None, Target("domain", "any"), id="a tier's folder, every instance"),
])
def test_a_reference_is_read(written, owner, found):
    assert read(written, owner) == (found, [])


@pytest.mark.parametrize("written, owner, patterns, problem", [
    pytest.param("module.kernel", SERVICES, True,
                 "at: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel",
                 id="a word for a part in no repeating folder"),
    pytest.param("module.domain", CLI, True,
                 "at: 'module.domain': part 'cli' lies in no <module> folder, so it has no own module: write "
                 "parts.domain", id="a word from an importer in no repeating folder"),
    pytest.param("module.domain", None, True,
                 "at: 'module.domain': a tier's folder lies in no <module> folder, so it has no own module: write "
                 "parts.domain", id="a word from what names no part"),
    pytest.param("module.store", SERVICES, True,
                 "at: 'module.store': part 'store' lies in the <unit> folder, not <module>: write parts.store",
                 id="a word for a part in another word's folder"),
    pytest.param("unit.store", DOMAIN, True,
                 "at: 'unit.store': part 'domain' lies in no <unit> folder: write parts.store",
                 id="a word from an importer in another word's folder"),
    pytest.param("orders.services", DOMAIN, True,
                 "at: 'orders.services': 'orders' is neither parts nor a word of this profile (module, unit): a "
                 "profile names no instance; write module.services or parts.services", id="an instance named"),
    pytest.param("<module>.services", DOMAIN, True,
                 "at: '<module>.services': write the word without brackets: module.services", id="the word in brackets"),
    pytest.param("parts.nope", SERVICES, True, "at: 'parts.nope' names no part 'nope'", id="a part the profile has not"),
    pytest.param("parts.", SERVICES, True, f"at: 'parts.' {NOT_A_REFERENCE}", id="no part"),
    pytest.param(".domain", SERVICES, True, f"at: '.domain' {NOT_A_REFERENCE}", id="no prefix"),
    pytest.param("parts..x", SERVICES, True, f"at: 'parts..x' {NOT_A_REFERENCE}", id="a dot in the part"),
    pytest.param("parts.domain@any", SERVICES, True, f"at: 'parts.domain@any' {NOT_A_REFERENCE}", id="an @ scope"),
    pytest.param("module.services/schema@any", DOMAIN, True, f"at: 'module.services/schema@any' {NOT_A_REFERENCE}",
                 id="an @ in the path"),
    pytest.param("module.services", SERVICES, True,
                 "at: 'module.services' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="the own instance of itself"),
    pytest.param("parts.kernel", KERNEL, True, "at: 'parts.kernel' is implied: a part may always import itself; remove it",
                 id="itself, outside a repeating folder"),
    pytest.param("parts.kernel:*Id", SERVICES, False,
                 "at: 'parts.kernel:*Id' has a name pattern, which this key does not take: drop ':*Id'",
                 id="a pattern where the key takes none"),
    pytest.param("module.services/../x", DOMAIN, True, "at: 'module.services/../x' has an invalid path after the part",
                 id="a path that is not one"),
    pytest.param("parts.kernel:a@b", SERVICES, True,
                 "at: 'parts.kernel:a@b' has a name pattern that is not one: write it with no space, `@`, `/` or `:`, "
                 "`*` standing for any text", id="an @ inside the pattern"),
])
def test_a_reference_written_wrong_is_none_with_its_one_problem(written, owner, patterns, problem):
    assert read(written, owner, patterns=patterns) == (None, [problem])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("module.domain/values", Target("domain", "own", ("values",)), [], id="a word is the mirrored instance"),
    pytest.param("parts.domain", Target("domain", "any"), [], id="parts is every instance"),
    pytest.param("parts.kernel", Target("kernel", "none"), [], id="parts outside a repeating folder"),
    pytest.param("module.kernel", None, ["at: 'module.kernel': part 'kernel' lies in no <module> folder: write "
                                         "parts.kernel"], id="a word for a part in no repeating folder"),
])
def test_a_test_reads_a_reference_from_the_instance_it_mirrors(written, found, problem):
    assert read(written, None, mirrored=True) == (found, problem)


def test_a_check_s_place_whose_prefix_is_no_word_is_told_a_dotted_name_goes_under_path():
    no_word = ("at: 'os.environ': 'os' is neither parts nor a word of this profile (module, unit): a profile names no "
               "instance; write parts.<part> or <word>.<part>")
    assert read("os.environ", SERVICES, place=True, alone="a check that names no part") == (
        None, [f"{no_word}; a dotted name of code goes under path"])
    assert read("os.environ", SERVICES) == (None, [no_word])
    assert read("module.domain", None, place=True, alone="a check that names no part") == (
        None, ["at: 'module.domain': a check that names no part lies in no <module> folder, so it has no own module: "
               "write parts.domain"])


def test_a_part_named_everything_is_named_parts_everything():
    assert read("parts.everything", None, parts={"everything": ("everything",)}) == (Target("everything", "none"), [])


def test_the_word_comes_from_the_profile_s_repeats_never_from_the_code():
    parts = {"core": ("packages", "*", "core"), "api": ("packages", "*", "api")}
    repeats = (Repeat("pkg", ("packages",)),)
    api = ("api", parts["api"])
    assert read("pkg.core", api, parts=parts, repeats=repeats) == (Target("core", "own"), [])
    assert read("module.core", api, parts=parts, repeats=repeats) == (
        None, ["at: 'module.core': 'module' is neither parts nor a word of this profile (pkg): a profile names no "
               "instance; write pkg.core or parts.core"])


def test_a_profile_with_no_repeating_folder_has_no_word():
    parts = {"kernel": ("kernel",), "cli": ("cli",)}
    assert read("orders.kernel", ("cli", ("cli",)), parts=parts, repeats=()) == (
        None, ["at: 'orders.kernel': 'orders' is neither parts nor a word of this profile, which has none: a profile "
               "names no instance; write parts.kernel"])
    assert read("parts.kernel", ("cli", ("cli",)), parts=parts, repeats=()) == (Target("kernel", "none"), [])


def test_a_part_named_parts_is_named_parts_parts():
    parts = {"parts": ("parts",), "cli": ("cli",)}
    assert read("parts.parts", ("cli", ("cli",)), parts=parts, repeats=()) == (Target("parts", "none"), [])


def test_a_reference_to_a_part_declared_but_not_placed_is_none_with_no_problem():
    assert read("parts.ghost", SERVICES, declared={*PARTS, "ghost"}) == (None, [])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("kernel/x.py", Target("kernel", "none", ("x.py",)), [], id="a dot in the path"),
    pytest.param("kernel:a.b", Target("kernel", "none", (), "a.b"), [], id="a dot in the pattern"),
    pytest.param(3, None, ["at: 3 is not a target: use <part>, <part>@any, optionally followed by /<path>"],
                 id="no text"),
    pytest.param("", None, ["at: '' is not a target: use <part>, <part>@any, optionally followed by /<path>"],
                 id="empty text"),
])
def test_a_value_whose_head_holds_no_dot_is_read_in_the_old_forms(written, found, problem):
    assert read(written, SERVICES) == (found, problem)
```

In `tests/modules/rules/application/logic/test_written.py`, change the import block and the one `target(...)` call.
Replace:

```python
from xarch.profile_values.placement import Target
```

with:

```python
from xarch.profile_values.placement import Repeat, Target
```

and replace:

```python
    assert (place, target(place, owner, PARTS, PARTS, "at", [], patterns=True, alone="a tier's folder")) == (
        written, found)
```

with:

```python
    assert (place, target(place, owner, PARTS, PARTS, "at", [], patterns=True, alone="a tier's folder",
                          repeats=(Repeat("module", ("modules",)),))) == (written, found)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/kernel/logic/test_targets.py tests/modules/rules/application/logic/test_written.py -q`
Expected: FAIL — every test errors with `TypeError: target() got an unexpected keyword argument 'repeats'`.

- [ ] **Step 3: Write the implementation**

Replace the whole of `xarch/kernel/logic/targets.py` with:

```python
"""How a profile writes a target, a place a part may import or a check names; checked against the parts declared, each
by its path, the part that writes it and the profile's repeating folders, each problem said at its address. Spec reads
a part's `imports` and a tier's with it, and rules the places a check of the profile's own names.

A value whose head (the text before its first `/` or `:`) holds a dot is a reference: `parts.<part>`, the part in every
instance of its repeating folder or, outside one, the part itself; or `<word>.<part>`, the part in the importer's own
instance of the folder the word repeats, a word of the profile's repeating folders; each optionally followed by
`/<path>` and, where the key takes one, `:<pattern>`. Any other value is read in the old forms: `<part>`, `<part>@any`,
`<part>/<path>` and `<part>:<pattern>`."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.logic.placement import repeat_of, root_of
from xarch.kernel.placement import EACH
from xarch.profile_values.placement import Repeat, Target

TARGET = re.compile(r"(?P<part>[^@/:]*)(?:@(?P<scope>[^/:]*))?(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?")
NAME_PATTERN = re.compile(r"[^\s@/:]+")
"""A name pattern: any text but whitespace and the separators of a target, `*` standing for any text."""
_HEAD = re.compile(r"[^/:]*")
_REFERENCE = re.compile(r"(?P<part>[^/:]*)(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?", re.DOTALL)


def target(value: Any, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
           declared: Collection[str], where: str, problems: list[str], patterns: bool = False,
           mirrored: bool = False, *, alone: str, repeats: Collection[Repeat], place: bool = False) -> Target | None:
    """The target a profile writes as value, for the part owner (its name and path; None for what names no part, which
    the caller words as alone, such as "a tier's folder"), each part by its path, repeats the profile's repeating
    folders, whose words a reference names; None, with the problem said at where, when it is not one. A target that
    names a part declared but not placed is None, with no problem of its own. When mirrored, the reader is a test, whose
    own instance of the repeating folder is the one it mirrors: a bare name, or `<word>.<part>`, there is that
    instance. place says the value is a check's `place`, where a prefix that is no word may be a dotted name of code."""
    if isinstance(value, str) and "." in _HEAD.match(value)[0]:
        return _reference(value, owner, parts, declared, where, problems, patterns, mirrored, alone, repeats, place)
    match = TARGET.fullmatch(value) if isinstance(value, str) else None
    if match is None or not match["part"]:
        problems.append(f"{where}: {value!r} is not a target: use <part>, <part>@any, optionally followed by /<path>")
        return None
    name, scope, sub, names = match["part"], match["scope"], match["sub"], match["names"]
    problem = _pattern_problem(value, names, patterns)
    if problem is not None:
        problems.append(f"{where}: {problem}")
        return None
    path = parts.get(name)
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    in_instance = EACH in path
    owned = owner is not None and EACH in owner[1]
    if scope is not None and scope not in ("own", "any"):
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': the only scope is @any, any instance of "
                        "the repeating folder")
        return None
    inside = mirrored or (owner is not None and owned and root_of(owner[1]) == root_of(path))
    if in_instance and scope == "own" and inside:
        problems.append(f"{where}: {value!r} says what a bare name already says: write {name}")
        return None
    if in_instance and not inside and scope != "any":
        if owner is not None and owned:
            problems.append(f"{where}: {value!r} lies in another repeating folder than part '{owner[0]}', which has "
                            f"no own instance of it: write {name}@any")
            return None
        importer = f"{owner[0]} is" if owner is not None else f"{alone} is"
        problems.append(f"{where}: {value!r} lies in the repeating folder, which {importer} not in: say {name}@any")
        return None
    if not in_instance and scope is not None:
        problems.append(f"{where}: {value!r} does not lie in the repeating folder: drop '@{scope}'")
        return None
    steps = _steps(sub)
    if steps is None:
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    chosen = "any" if scope == "any" else ("own" if in_instance else "none")
    if owner is not None and name == owner[0] and chosen != "any":
        problems.append(_implied(where, value, owner, f"{name}@any"))
        return None
    return Target(name, chosen, steps, names or "")


def _reference(value: str, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
               declared: Collection[str], where: str, problems: list[str], patterns: bool, mirrored: bool, alone: str,
               repeats: Collection[Repeat], place: bool) -> Target | None:
    """The target a reference writes (see target); None with its one problem, that of the first of its checks that
    fails: the shape, the prefix, the pattern, the part, the path, the instance, the part itself."""
    prefix, _, rest = value.partition(".")
    match = _REFERENCE.fullmatch(rest)
    if not prefix or match is None or not match["part"] or "." in match["part"] or "@" in value.partition(":")[0]:
        problems.append(f"{where}: {value!r} is not a reference: write parts.<part> or <word>.<part>, optionally followed "
                        "by /<path> and :<pattern>")
        return None
    name, names = match["part"], match["names"]
    path = parts.get(name)
    problem = _prefix_problem(value, prefix, rest, path, repeats, place) or _pattern_problem(value, names, patterns)
    if problem is not None:
        problems.append(f"{where}: {problem}")
        return None
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    steps = _steps(match["sub"])
    if steps is None:
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    if prefix == "parts":
        scope = "any" if EACH in path else "none"
    else:
        problem = _word_problem(value, prefix, rest, (name, path), owner, repeats, mirrored, alone)
        if problem is not None:
            problems.append(f"{where}: {problem}")
            return None
        scope = "own"
    if owner is not None and name == owner[0] and scope != "any":
        problems.append(_implied(where, value, owner, f"parts.{name}"))
        return None
    return Target(name, scope, steps, names or "")


def _prefix_problem(value: str, prefix: str, rest: str, path: tuple[str, ...] | None, repeats: Collection[Repeat],
                    place: bool) -> str | None:
    """What is wrong with the prefix of a reference: a word in brackets, or a prefix that is neither parts nor a word of
    the profile, told the reference to write for the part (its path, None when it places none) and, for a check's
    place, that a dotted name of code goes under path; None when the prefix is one."""
    if len(prefix) > 2 and prefix.startswith("<") and prefix.endswith(">"):
        return f"{value!r}: write the word without brackets: {prefix[1:-1]}.{rest}"
    words = [repeat.word for repeat in repeats]
    if prefix == "parts" or prefix in words:
        return None
    known = f" ({', '.join(words)})" if words else ", which has none"
    held = None if path is None else repeat_of(repeats, path)
    instead = ("parts.<part> or <word>.<part>" if path is None
               else f"parts.{rest}" if held is None else f"{held.word}.{rest} or parts.{rest}")
    hint = "; a dotted name of code goes under path" if place else ""
    return (f"{value!r}: {prefix!r} is neither parts nor a word of this profile{known}: a profile names no instance; "
            f"write {instead}{hint}")


def _word_problem(value: str, prefix: str, rest: str, part: tuple[str, tuple[str, ...]],
                  owner: tuple[str, tuple[str, ...]] | None, repeats: Collection[Repeat], mirrored: bool,
                  alone: str) -> str | None:
    """What is wrong with `<word>.<part>`: the part (its name and path) must lie in the word's folder and, but for the
    instance a test mirrors, so must the importer, owner, or what the caller words as alone; None when both do."""
    instead = f"write parts.{rest}"
    held = repeat_of(repeats, part[1])
    if held is None:
        return f"{value!r}: part {part[0]!r} lies in no <{prefix}> folder: {instead}"
    if held.word != prefix:
        return f"{value!r}: part {part[0]!r} lies in the <{held.word}> folder, not <{prefix}>: {instead}"
    if mirrored:
        return None
    importer = alone if owner is None else f"part {owner[0]!r}"
    mine = None if owner is None else repeat_of(repeats, owner[1])
    if mine is None:
        return f"{value!r}: {importer} lies in no <{prefix}> folder, so it has no own {prefix}: {instead}"
    return None if mine.word == prefix else f"{value!r}: {importer} lies in no <{prefix}> folder: {instead}"


def _pattern_problem(value: str, names: str | None, patterns: bool) -> str | None:
    """What is wrong with the name pattern of a target: one where the key takes none (patterns false), an empty one, or
    one that is not one; None when it writes none or writes one."""
    if names is None:
        return None
    if not patterns:
        return f"{value!r} has a name pattern, which this key does not take: drop ':{names}'"
    if not names:
        return f"{value!r} has an empty name pattern after `:`"
    if not NAME_PATTERN.fullmatch(names):
        return (f"{value!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` standing "
                "for any text")
    return None


def _steps(sub: str | None) -> tuple[str, ...] | None:
    """The path below the part a target writes, step by step, () when it writes none; None when a step is empty, `.`,
    `..` or holds the repeating step."""
    steps = tuple(sub.split("/")) if sub is not None else ()
    return None if any(not step or step in (".", "..") or EACH in step for step in steps) else steps


def _implied(where: str, value: str, part: tuple[str, tuple[str, ...]], again: str) -> str:
    """A part may always import itself, so a target that only says so is refused: the part by its name and path, and
    again, how the target that names it in every instance is written."""
    if EACH not in part[1]:
        return f"{where}: {value!r} is implied: a part may always import itself; remove it"
    return (f"{where}: {value!r} is implied: a part may always import itself, its own instance of the repeating "
            f"folder; remove it ({again}, another instance's too, stays allowed)")
```

In `xarch/modules/spec/application/logic/targets_written.py`, replace:

```python
        written = target(item, None if owner is None else (owner.name, owner.path), paths, declared, where, problems,
                         patterns, mirrored, alone="a tier's folder")
```

with (old forms only until Task 2 threads the profile's repeats):

```python
        written = target(item, None if owner is None else (owner.name, owner.path), paths, declared, where, problems,
                         patterns, mirrored, alone="a tier's folder", repeats=())
```

In `xarch/modules/rules/application/logic/own_checks.py`, replace:

```python
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems,
                                       alone="a check that names no part")) is not None)
```

with (until Task 3):

```python
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems,
                                       alone="a check that names no part", repeats=())) is not None)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/kernel/logic/test_targets.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/logic/test_targets_written.py tests/modules/rules/application/logic/test_own_checks.py -q`
Expected: PASS, all of them. Then `uv run ruff check` — expected: `All checks passed!`. If a line is over 140
characters, wrap it; do not run `--fix`.

- [ ] **Step 5: Commit**

```bash
git add xarch/kernel/logic/targets.py xarch/modules/spec/application/logic/targets_written.py \
  xarch/modules/rules/application/logic/own_checks.py tests/kernel/logic/test_targets.py \
  tests/modules/rules/application/logic/test_written.py
git commit -m "target() reads parts.<part> and <word>.<part>, the word from the profile's repeats, beside the old forms, each reference written wrong refused with its one problem"
```

---

### Task 2: spec passes the profile's repeats to every target it reads

**Files:**
- Modify: `xarch/modules/spec/application/logic/targets_written.py` (module docstring lines 1-4, imports, `allowed_targets` lines 18-42)
- Modify: `xarch/modules/spec/application/logic/imports_written.py:56-95` (`may`, `must`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:203-216` (calls in `parse_profile`), `586-609` (`_tiers`), `641-671` (`_tier`)
- Test: `tests/modules/spec/application/logic/test_targets_written.py`
- Test: `tests/modules/spec/application/logic/test_profile_parsing.py`

**Interfaces:**
- Consumes: `target(..., *, alone, repeats, place=False)` from Task 1.
- Produces: `allowed_targets(value, owner, parts, declared, where, problems, patterns=False, mirrored=False, *,
  repeats: Collection[Repeat]) -> tuple[Target, ...]`; `iw.may(value, owner, parts, declared, where, problems, *,
  repeats: Collection[Repeat])`; `iw.must(written, owner, parts, declared, allowed, problems, *,
  repeats: Collection[Repeat])`; `_tiers(..., language, repeats)`, `_tier(..., language, repeats)` with
  `repeats: tuple[Repeat, ...]`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_targets_written.py`:

Replace the docstring and imports/fixtures at the top (lines 1-18) with:

```python
"""How a profile writes what may be imported, on hand-made parts: a bare part, @any, a path below it, a pattern where
one is allowed, `everything`, the references parts.<part> and <word>.<part>, and each target refused with why."""
import pytest

from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.targets_written import allowed_targets
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target

API = Part("api", ("src", "*", "api"), "handlers")
SERVICE = Part("service", ("src", "*", "service"), "logic")
SHARED = Part("shared", ("shared",), "shared code")
PARTS = {part.name: part for part in (API, SERVICE, SHARED)}
REPEATS = (Repeat("module", ("src",)),)


def written(value, owner=API, patterns=False):
    problems: list[str] = []
    return (allowed_targets(value, owner, PARTS, set(PARTS), "parts.api.imports.may", problems, patterns,
                            repeats=REPEATS), problems)
```

Replace the last test (lines 51-55) with:

```python
def test_a_tier_folder_s_may_import_refuses_a_marked_entry_as_any_entry_that_is_no_target():
    problems: list[str] = []
    assert allowed_targets([{"shared": "types_only"}], None, PARTS, {"shared"}, "tiers.guard.imports.may", problems,
                           repeats=REPEATS) == ()
    assert problems == ["tiers.guard.imports.may: {'shared': 'types_only'} is not a target: use <part>, <part>@any, "
                        "optionally followed by /<path>"]


def test_references_are_read_with_the_profile_s_words_in_the_order_written():
    assert written(["parts.shared", "module.service", "parts.service/rules"]) == (
        (Target("shared"), Target("service", "own"), Target("service", "any", ("rules",))), [])


def test_what_a_tier_s_tests_also_import_reads_a_word_as_the_instance_a_test_mirrors():
    problems: list[str] = []
    assert allowed_targets(["module.service/rules"], None, PARTS, set(PARTS), "tiers.unit.imports.also", problems,
                           mirrored=True, repeats=REPEATS) == (Target("service", "own", ("rules",)),)
    assert problems == []
```

(The spec's T9 names `services_part`, `parts.kernel`, `module.domain`; this file's fixture names the parts `api`,
`service`, `shared` in `src/<module>/`, so the same three cases are written with those names.)

In `tests/modules/spec/application/logic/test_profile_parsing.py`, change the import line

```python
from tests.modules.spec.profiles import layered, parsed, part_of, problems, two_folders
```

to

```python
from copy import deepcopy

from tests.modules.spec.profiles import TESTING, layered, parsed, part_of, problems, two_folders
```

(keep `from copy import deepcopy` in the standard-library import group above `import pytest`, i.e. the file starts
`"""..."""`, then `from copy import deepcopy`, blank line, `import pytest`, blank line, the `tests.` and `xarch.`
imports — the order `ruff check` (rule `I`) asks for), and append at the end of the file:

```python
def referencing(services: dict, guard: dict) -> dict:
    """A profile of modules/<module>/ (domain, services) and kernel/, every part untested, and a tier guard in the
    folder architecture: services writes the imports given, and the guard the keys given beside its folder."""
    return {"name": "refs", "testing": deepcopy(TESTING), "parts": {
        "modules/<module>/": {
            "domain/": {"role": "the rules", "untested": "read through services"},
            "services/": {"role": "the use cases", "untested": "read through the guard", "imports": services}},
        "kernel/": {"role": "shared code", "untested": "too small to test"}},
        "tiers": {"guard": {"folder": "architecture"} | guard}}


def test_references_reach_every_target_spec_reads_and_mean_what_the_old_forms_mean():
    new = parsed(referencing({"may": ["module.domain", "parts.kernel", {"parts.domain": "types_only"}],
                              "must": ["parts.kernel"]},
                             {"imports": {"may": ["parts.kernel"], "also": ["module.domain/values"]}}))
    old = parsed(referencing({"may": ["domain", "kernel", {"domain@any": "types_only"}], "must": ["kernel"]},
                             {"imports": {"may": ["kernel"], "also": ["domain/values"]}}))
    services, (guard,) = new.parts["services"], new.tiers
    assert (new.rules["services"], services.imports_must, services.imports_types_only) == (
        (Target("domain", "own"), Target("kernel"), Target("domain", "any")), (Target("kernel"),),
        (Target("domain", "any"),))
    assert (guard.imports_may, guard.imports_also) == ((Target("kernel"),), (Target("domain", "own", ("values",)),))
    assert (new.rules, services.imports_must, services.imports_types_only, guard.imports_may, guard.imports_also) == (
        old.rules, old.parts["services"].imports_must, old.parts["services"].imports_types_only,
        old.tiers[0].imports_may, old.tiers[0].imports_also)


@pytest.mark.parametrize("services, guard, problem", [
    pytest.param({"may": ["module.kernel"]}, {},
                 "layered.yaml: parts.services.imports.may: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a part's may"),
    pytest.param({"may": ["parts.kernel"], "must": ["module.kernel"]}, {},
                 "layered.yaml: parts.services.imports.must: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a part's must"),
    pytest.param({"may": ["parts.kernel"]}, {"imports": {"also": ["module.kernel"]}},
                 "layered.yaml: tiers.guard.imports.also: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a tier's also"),
    pytest.param({"may": ["parts.kernel"]}, {"imports": {"may": ["module.domain"]}},
                 "layered.yaml: tiers.guard.imports.may: 'module.domain': a tier's folder lies in no <module> folder, "
                 "so it has no own module: write parts.domain", id="a tier's may"),
])
def test_a_reference_written_wrong_is_refused_at_its_address(services, guard, problem):
    assert problems(referencing(services, guard)) == [problem]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_targets_written.py tests/modules/spec/application/logic/test_profile_parsing.py -q`
Expected: FAIL — in `test_targets_written.py` every test errors with
`TypeError: allowed_targets() got an unexpected keyword argument 'repeats'`; in `test_profile_parsing.py` the new
tests fail with problems such as `'module' is neither parts nor a word of this profile, which has none: ...` (the
repeats are not passed yet), while the older tests pass.

- [ ] **Step 3: Write the implementation**

`xarch/modules/spec/application/logic/targets_written.py` — replace lines 1-4 (module docstring) with:

```python
"""What a part, or the tests in a tier's folder, may import, as a profile writes it: a list of targets (see the target
grammar in kernel/logic/targets: the old forms, and the references parts.<part> and <word>.<part>, the word one of the
profile's repeating folders), or `everything`; checked against the parts declared and the part that writes them (None
for a tier's folder), each problem said at its address. What a tier's tests may also import is a list of targets
alone, a bare name in the repeating folder, or <word>.<part>, being the instance a test mirrors."""
```

replace the imports

```python
from typing import Any

from xarch.kernel.logic.targets import target
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Target
```

with

```python
from collections.abc import Collection
from typing import Any

from xarch.kernel.logic.targets import target
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target
```

replace the signature and docstring of `allowed_targets`

```python
def allowed_targets(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
                    problems: list[str], patterns: bool = False, mirrored: bool = False) -> tuple[Target, ...]:
    """What a part, or the tests in a tier's folder (no owner), may import, as targets; a name pattern only where
    patterns allows one; when mirrored, what a tier's tests may also import, read from the instance a test mirrors."""
```

with

```python
def allowed_targets(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
                    problems: list[str], patterns: bool = False, mirrored: bool = False, *,
                    repeats: Collection[Repeat]) -> tuple[Target, ...]:
    """What a part, or the tests in a tier's folder (no owner), may import, as targets, a reference's word one of
    repeats, the profile's repeating folders; a name pattern only where patterns allows one; when mirrored, what a
    tier's tests may also import, read from the instance a test mirrors."""
```

and replace the `repeats=()` call from Task 1

```python
                         patterns, mirrored, alone="a tier's folder", repeats=())
```

with

```python
                         patterns, mirrored, alone="a tier's folder", repeats=repeats)
```

`xarch/modules/spec/application/logic/imports_written.py` — add `Collection` to the import
`from collections.abc import Mapping` (it becomes `from collections.abc import Collection, Mapping`) and
`Repeat` to `from xarch.profile_values.placement import Target` (it becomes
`from xarch.profile_values.placement import Repeat, Target`). Replace `may` (lines 56-72) with:

```python
def may(value: Any, owner: Part, parts: dict[str, Part], declared: set[str], where: str,
        problems: list[str], *, repeats: Collection[Repeat]) -> tuple[tuple[Target, ...], tuple[Target, ...]]:
    """What the part may import, every entry as its target, marked or not, in the order written; and the targets of
    its marked entries, in the same order. An entry refused adds its problem and is in neither. repeats are the
    profile's repeating folders, whose words a reference names."""
    if not isinstance(value, list):
        return allowed_targets(value, owner, parts, declared, where, problems, patterns=True, repeats=repeats), ()
    allowed: list[Target] = []
    marked: list[Target] = []
    for entry in value:
        written = _marked(entry, where, problems) if isinstance(entry, Mapping) else entry
        if written is None:
            continue
        found = allowed_targets([written], owner, parts, declared, where, problems, patterns=True, repeats=repeats)
        allowed += found
        if isinstance(entry, Mapping):
            marked += found
    return tuple(allowed), tuple(marked)
```

and in `must` (lines 75-95) replace the signature

```python
def must(written: Mapping[Any, Any], owner: Part, parts: dict[str, Part], declared: set[str],
         allowed: tuple[Target, ...], problems: list[str]) -> tuple[Target, ...]:
```

with

```python
def must(written: Mapping[Any, Any], owner: Part, parts: dict[str, Part], declared: set[str],
         allowed: tuple[Target, ...], problems: list[str], *, repeats: Collection[Repeat]) -> tuple[Target, ...]:
```

and the line

```python
    found = allowed_targets(value, owner, parts, declared, where, problems) if len(problems) == count else ()
```

with

```python
    found = (allowed_targets(value, owner, parts, declared, where, problems, repeats=repeats) if len(problems) == count
             else ())
```

`xarch/modules/spec/application/logic/profile_parsing.py` — in `parse_profile` replace

```python
    read = {part: iw.may(imports[part].get("may"), item, parts, declared, f"parts.{part}.imports.may", problems)
            for part, item in parts.items()}
```

with

```python
    read = {part: iw.may(imports[part].get("may"), item, parts, declared, f"parts.{part}.imports.may", problems,
                         repeats=built.repeats)
            for part, item in parts.items()}
```

replace

```python
    parts = {part: replace(item, imports_must=iw.must(imports[part], item, parts, declared, rules[part], problems),
                           imports_types_only=read[part][1]) for part, item in parts.items()}
```

with

```python
    parts = {part: replace(item, imports_must=iw.must(imports[part], item, parts, declared, rules[part], problems,
                                                      repeats=built.repeats),
                           imports_types_only=read[part][1]) for part, item in parts.items()}
```

replace

```python
    tiers = _tiers(document, specs, parts, declared, examples, problems, language)
```

with

```python
    tiers = _tiers(document, specs, parts, declared, examples, problems, language, built.repeats)
```

In `_tiers`, replace the signature

```python
def _tiers(document: Mapping[Any, Any], specs: dict[str, Any], parts: dict[str, Part], declared: set[str],
           examples: ex.Examples, problems: list[str], language: Language) -> tuple[Tier, ...]:
```

with

```python
def _tiers(document: Mapping[Any, Any], specs: dict[str, Any], parts: dict[str, Part], declared: set[str],
           examples: ex.Examples, problems: list[str], language: Language, repeats: tuple[Repeat, ...]) -> tuple[Tier, ...]:
```

and its call

```python
        tier = _tier(name, spec, subject, parts, declared, examples, problems, language)
```

with

```python
        tier = _tier(name, spec, subject, parts, declared, examples, problems, language, repeats)
```

In `_tier`, replace the signature

```python
def _tier(name: str, spec: Any, subject: tuple[Subject, ...], parts: dict[str, Part], declared: set[str],
          examples: ex.Examples, problems: list[str], language: Language) -> Tier | None:
```

with

```python
def _tier(name: str, spec: Any, subject: tuple[Subject, ...], parts: dict[str, Part], declared: set[str],
          examples: ex.Examples, problems: list[str], language: Language, repeats: tuple[Repeat, ...]) -> Tier | None:
```

and the two calls

```python
    allowance = (allowed_targets(imports.get("may"), None, parts, declared, f"{where}.imports.may", problems)
                 if "folder" in spec else None)
    also = allowed_targets(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems, mirrored=True)
```

with

```python
    allowance = (allowed_targets(imports.get("may"), None, parts, declared, f"{where}.imports.may", problems,
                                 repeats=repeats) if "folder" in spec else None)
    also = allowed_targets(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems, mirrored=True,
                           repeats=repeats)
```

(`Repeat` is already imported in `profile_parsing.py`; confirm with `grep -n "import.*Repeat" xarch/modules/spec/application/logic/profile_parsing.py`.)

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/spec tests/kernel -q`
Expected: PASS. Then `uv run ruff check` — expected `All checks passed!` (wrap any line over 140 characters by hand).
Then `grep -rn "repeats=()" xarch/modules/spec` — expected: no output.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/targets_written.py xarch/modules/spec/application/logic/imports_written.py \
  xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_targets_written.py \
  tests/modules/spec/application/logic/test_profile_parsing.py
git commit -m "A part's imports.may and imports.must and a tier's imports.may and imports.also read references with the words of the profile's repeating folders"
```

---

### Task 3: a check's `place` reads references with the profile's words and the hint about `path`

**Files:**
- Modify: `xarch/modules/rules/application/logic/own_checks.py:113-114`
- Test: `tests/modules/rules/application/logic/test_own_checks.py` (add after the test ending at line 45)

**Interfaces:**
- Consumes: `target(..., *, alone, repeats, place=False)` from Task 1; `Profile.repeats` (`tests/modules/rules/builders.py`
  `PROFILE` has `repeats=(MODULES,)`, `MODULES = Repeat("module", ("modules",))`, and `services` at
  `("modules", "*", "application", "services")`, `domain` at `("modules", "*", "domain")`, `kernel` at `("kernel",)`).
- Produces: nothing new.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_own_checks.py`, insert after
`test_a_place_is_read_by_the_target_grammar_from_the_part_the_scope_names` (ends at line 45):

```python
def test_a_place_reads_a_reference_with_the_words_of_the_profile_s_repeating_folders():
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("parts.kernel", "module.domain/values")),)),
                          (Saying("m", "f"),))
    (check,) = resolved(profile(written={"placed": placed})).checks
    assert check.rule.targets == (Match("place", places=(Target("kernel"), Target("domain", "own", ("values",)))),)


def test_a_dotted_name_of_code_written_as_a_place_is_told_it_goes_under_path():
    dotted = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("os.environ",)),)), (Saying("m", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(written={"dotted": dotted}))
    assert refused.value.problems == (
        "checks.dotted.may_not.place: 'os.environ': 'os' is neither parts nor a word of this profile (module): a "
        "profile names no instance; write parts.<part> or <word>.<part>; a dotted name of code goes under path",)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/rules/application/logic/test_own_checks.py -q`
Expected: FAIL — the first new test is refused with
`'module' is neither parts nor a word of this profile, which has none: ...`; the second sees `, which has none` in
place of ` (module)` and no `; a dotted name of code goes under path`.

- [ ] **Step 3: Write the implementation**

In `xarch/modules/rules/application/logic/own_checks.py`, replace the Task 1 call

```python
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems,
                                       alone="a check that names no part", repeats=())) is not None)
```

with

```python
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems,
                                       alone="a check that names no part", repeats=profile.repeats,
                                       place=True)) is not None)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/rules -q`
Expected: PASS. Then `uv run ruff check` — expected `All checks passed!`. Then
`grep -rn "repeats=()" xarch` — expected: no output.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules/application/logic/own_checks.py tests/modules/rules/application/logic/test_own_checks.py
git commit -m "A check's place reads references with the words of the profile's repeating folders, a prefix that is no word told a dotted name of code goes under path"
```

---

### Task 4: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:226-230` (the `imports.may` bullet)
- Modify: `CHANGELOG.md:6-8` (`## [Unreleased]`, `### Added`)
- Check unchanged: `docs/cli/`, `docs/web/`, `docs/xarch/`

**Interfaces:**
- Consumes: the behavior of Tasks 1-3.
- Produces: nothing in code.

- [ ] **Step 1: Run the golden-doc tests first (they must already pass: the docs print paths, not targets)**

Run: `uv run pytest tests/bootstrap/test_docs_templates.py -q`
Expected: PASS. A failure here is a defect to report (spec, Docs: "Any diff is a defect to report, not to regenerate
past"): stop and report the failing doc and its diff; do not regenerate.

- [ ] **Step 2: Edit README.md**

In `README.md`, replace the bullet

```markdown
- In `imports.may`, a bare name is that part in the importer's own instance of its repeating folder; `store@any` any
  instance, and the only way to name a part of another repeating folder, which has no own instance; `store/schema`
  only that path below the part; `store:*Id` only the names that match the pattern, imported by name;
  `everything` no limit (also for `imports.libraries`); an entry written `{store: types_only}` is a target the part
  may import only to use as a type. A part may always import itself.
```

with

```markdown
- In `imports.may`, a bare name is that part in the importer's own instance of its repeating folder; `store@any` any
  instance, and the only way to name a part of another repeating folder, which has no own instance; `store/schema`
  only that path below the part; `store:*Id` only the names that match the pattern, imported by name;
  `everything` no limit (also for `imports.libraries`); an entry written `{store: types_only}` is a target the part
  may import only to use as a type. A part may always import itself. A target may also be written as a reference:
  `parts.store` is the part in every instance (or, outside a repeating folder, the part itself), and `<word>.store`,
  such as `module.store`, the part in the importer's own instance of the `<word>` folder, each optionally followed by
  `/<path>` and `:<pattern>`; the forms above stay the bundled spelling.
```

- [ ] **Step 3: Edit CHANGELOG.md**

In `CHANGELOG.md`, directly under `## [Unreleased]` / `### Added` and its blank line, insert as the first entry:

```markdown
- References beside the old forms of a target: a part's `imports.may` and `imports.must`, a tier's `imports.may` and
  `imports.also`, and a check's `place` read `parts.<part>` and `<word>.<part>`, each optionally followed by `/<path>`
  and, where the key takes one, `:<pattern>`. `parts.<part>` is the part in every instance of its repeating folder
  (as `<part>@any`), or the part itself when it lies in none; `<word>.<part>` is the part in the importer's own
  instance of the `<word>` folder, the word one of the profile's repeating folders, and in a tier's `imports.also` the
  instance the test mirrors; `parts.everything` names a part called `everything`. A value is a reference when the
  text before its first `/` or `:` holds a dot. A reference written wrong is refused saying what to write: a word for
  a part in no `<word>` folder or in another word's (`'module.kernel': part 'kernel' lies in no <module> folder: write
  parts.kernel`), a word from an importer outside its folder (`... so it has no own module: write parts.domain`), a
  word in brackets (`write the word without brackets: module.services`), a prefix that is no word of the profile
  (`'orders' is neither parts nor a word of this profile (module): a profile names no instance; write module.services
  or parts.services`, and for a check's `place` the hint that a dotted name of code goes under `path`), `@` anywhere
  before the pattern, and a part's own instance of itself. No old form is refused yet.
```

- [ ] **Step 4: Run every gate**

Run, each from the worktree root:

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
timeout 900 uv run pytest -q > /tmp/pytest-8-1.log 2>&1; echo "exit $?"; tail -5 /tmp/pytest-8-1.log
```

(Run the last one in the background and read the log when it ends.) Expected: ruff `All checks passed!`; both
`xarch check` runs exit 0; `profile check` exits 0; pytest exit 0 with `passed` and no `failed` in the tail. If
`xarch check` reports a duplicate (guard `no-duplicates`, 4 statements) or a dead name in `targets.py`, fix it in
`targets.py` by sharing the helper, rerun Task 1's tests, and note it in the commit message.

Then: `git status --short docs/` — expected: no output (no golden doc changed).

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say imports.may, imports.must, a tier's may and also, and a check's place read parts.<part> and <word>.<part> beside the old forms; the golden docs do not move"
```

---

## Self-review

- **Spec coverage.** Grammar choice by head (Task 1, T8 table and the `domain.x`-style rows `orders.services`,
  `os.environ`). Checks 1-9 in order (Task 1: T1, T2, T3). Brackets (T2). No-word message with words, with none, the
  three replacements and the place hint (T2 `orders.services`, T4, T6, T7; the literal replacement in T4). Pattern
  checks (T2). Undeclared and declared-not-placed parts (T2, Review Focus 1). Path (T2). Scope for `parts.` and
  `<word>.` with each importer case (T1, T2, T3). Self-import with the new parenthesis and today's text (T2). Interface:
  `repeats` required and `place` (Task 1), `allowed_targets`, `may`, `must`, `_tiers`, `_tier`, `parse_profile`
  (Task 2, T9-T11), `own_checks._match` (Task 3, T12). Docstrings (Tasks 1, 2). README, CHANGELOG, golden docs (Task 4).
  3.9 `parts.services` in `services` stays valid (T1). 1.4 `parts.everything` (T5). T6/T7 (Task 1). `test_written.py`
  gains `repeats=` (Task 1).
- **Deviation noted.** T9 is written with `test_targets_written.py`'s own fixture names (`api`, `service`, `shared` in
  `src/<module>/`); T10/T11 use a `referencing` builder with every part `untested` and a guard tier in
  `architecture`, and T11 is widened to one row per caller (part may, part must, tier also, tier may).
- **Placeholders.** None: every code step has its code.
- **Types.** `repeats: Collection[Repeat]` in `target`, `allowed_targets`, `may`, `must`; `tuple[Repeat, ...]` in
  `_tiers`/`_tier` (what `built.repeats` is). `place: bool = False` only on `target`.
<!-- task-pipeline: validated -->
