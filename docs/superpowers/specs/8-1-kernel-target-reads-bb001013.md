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
