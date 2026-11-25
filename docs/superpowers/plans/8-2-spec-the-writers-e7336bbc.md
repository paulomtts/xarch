# 8.2 the writers emit the new reference form

Card: e7336bbc-02a1-417d-b5ec-175bd3692721 (subtask of f1c96689), blocked by 8.1 (bb001013, done: commits
ae1cab6..d45f1ce). Release step 24 of the merged order (`0.3.0-cohesion-review-3.md`, section 3, row 24 at line 287),
sub-step 2 of its owning note.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/part-references-design.md` ("the note").
This card implements section 6 sub-step 2 (lines 448-449) and the writer lines of section 5.3 (lines 397-401). From
review 3: O12 (line 236, `_shown` is this step's function of `looseness.py`), O4, O5, O8 (lines 228, 229, 232).

## Goal

The two places that write a `Target` back out as profile text write the new reference form:

- `_place` (`xarch/modules/rules/application/logic/written.py:83-87`), which writes the places of a check shown by
  `profile explain <key> --rule` and by the example of `profile explain <word>`.
- `_shown` (`xarch/modules/spec/application/logic/looseness.py:557-562`), which writes the target of a looser line
  of `profile check` and `check` (text and the JSON `what` and `sentence`).

What `_place` writes, `target()` reads back to the same `Target`. Nothing else changes: no profile, no parser, no
`Target` field, no refusal.

## What is already there (not to be redone)

- `target()` (`xarch/kernel/logic/targets.py`) already reads `parts.<part>` and `<word>.<part>` with `/<path>` and
  `:<pattern>`, given `repeats=` (8.1). `parts.<part>` gives scope `any` when the part's path holds a word, `none`
  when it does not; `<word>.<part>` gives `own` (note 1.1, lines 124-132). The old forms still parse.
- `Target(part, scope, sub, names)` (`xarch/profile_values/placement.py`), scope `own`, `any` or `none`. It does not
  change (note section 7, line 472: no fourth scope, no `word` field).
- The part-to-word maps exist on both sides: the rules' `Profile.words()` (`xarch/modules/rules/domain/profile.py:
  124-127`) and the spec's `Architecture.words()` (`xarch/modules/spec/domain/values.py:445-448`). Each gives the word
  of the repeating folder a part lies in, through `repeat_of`, and leaves out a part that lies in none.
- `everything` is written `everything` by `_shown` today and never reaches `_place` (a check's `place` never holds
  it). That stays.

## Inherited constraints

- The spelling (note section 1 table, lines 106-113; rulings lines 8-14):
  - scope `any` and scope `none` are written `parts.<part>`;
  - scope `own` is written `<word>.<part>`, the word that of the repeating folder the part lies in;
  - then `/<step>/<step>...` for `sub`, then `:<names>` when `names` is not empty, as today.
- The word comes from the part's path, through the profile's repeats (`Profile.words()` / `Architecture.words()`).
  Never from the owner, never by splitting the part name, never a literal `module` (card dodge; note section 7,
  lines 468-473).
- `_shown`'s output keeps its place and shape: the `what` of a `Loosened` and the sentence that embeds it; the JSON
  keys do not change (note 5.3, lines 399-401).
- The looser lines of `profile check architecture.yaml` hold the same targets before and after, only respelled (note
  section 7, line 479-480; review 3 O12).
- Project rules (card): no comments in xarch's code (docstrings only); never `ruff --fix`; tests written first and
  seen failing; Python only in the reader adapter and `xarch/architectures/presets/` data; recorded corpora
  (`tests/bootstrap/corpora/`) untouched; `.claude/` out of commits; nothing pushed.

## Behavior

### B1. `_place` writes the new form

`_place` takes the target and the profile's part-to-word map:

| Target | words | written |
|---|---|---|
| `Target("domain", "own")` | `{"domain": "module"}` | `module.domain` |
| `Target("domain", "any", ("values",))` | `{"domain": "module"}` | `parts.domain/values` |
| `Target("kernel", "none", (), "*Id")` | `{}` | `parts.kernel:*Id` |
| `Target("domain", "any")` | `{"domain": "module"}` | `parts.domain` |
| `Target("store", "own", ("sql",), "Sql*")` | `{"store": "unit"}` | `unit.store/sql:Sql*` |
| `Target("api", "any", ("v1",))` | `{}` | `parts.api/v1` |

- A target of scope `own` whose part has no word in the map cannot come out of `target()` (`own` is only read for a
  part inside a repeating folder). `_place` raises `ValueError` naming the part, for example
  `"Target 'kernel' is in its importer's own instance, but part 'kernel' lies in no repeating folder"`. It never
  falls back to `parts.` (that would change the meaning, own to any) nor to the bare name (an old form).
- The word map reaches `_place` through `check_of` and `written`, each gaining a keyword-only, required
  `words: Mapping[str, str]`. `written_own` (used only for the checks written for the explanation, `WORKED`, which
  hold no place) passes an empty map.
- Callers in `xarch/modules/rules/application/services/explaining.py`:
  - `rule()` (line ~117, `profile explain <key> --rule`) passes the words of the profile its rules come from (the
    profile `rules_of` resolves for that location).
  - `_example()` (line ~80, the example of `profile explain <word>`) passes the words of the profile at `location`,
    the one `example()` found the rule in.
  - The fallback to `written_own` (line ~81) is unchanged.

Observable through the CLI (wired):

- `xarch profile explain parts.imports.must --rule --profile web` (and `cli`, and `architecture.yaml`) writes
  `targets: [{place: [parts.platform, parts.contract]}, outside]` where it wrote `[platform, contract@any]`.
- `xarch profile explain targets.place` (in this repository, its example comes from `architecture.yaml`'s
  `parts.adapters.imports.must`) writes the same `[parts.platform, parts.contract]`.
- No other `--rule` output of the bundled profiles or of `architecture.yaml` changes: their `imports.may`, tier
  keys and the rest write no place (checked by running each at this commit: only `parts.imports.must` holds one).

### B2. `_shown` writes the new form

`_shown` writes `everything` for `EVERYTHING`, and every other target as B1 does, the word taken from the custom
profile's `Architecture.words()`. In every call of `_looser` (`looseness.py:245-300`) the shown name is a part of the
custom profile: `imports.may` (line 253), `imports.may.types_only` (line 258, a target of the bundled profile
renamed into the custom names with `_into(t, back)`), `imports.must` (line 275), and a tier's `imports.also`
(line 295).

- The `types_only` line: a target of scope `own` is shown only when a custom allow of scope `own` of the same part
  covers it (`_covers` compares scopes), so its renamed part lies in a repeating folder of the custom profile and has
  a word there. The word is that of the custom profile.
- Scope `own` with no word in the custom map raises the same `ValueError` as B1 (one shared writer, or two that say
  the same; see Design choice below).
- Lines that do not go through `_shown` keep their text: `imports.types_only` of a tier (a plain part name), the
  libraries, `uses.never`, and the rest.

Examples (the test fixtures of `tests/modules/spec/application/logic/test_looseness.py` and `test_origin.py`):

| written in the custom profile | shown before | shown after |
|---|---|---|
| `service` (from `api`, both in `src/<module>/`) | `service` | `module.service` |
| `store@any/sql` | `store@any/sql` | `parts.store/sql` |
| `shared/text` (`shared/` outside the repeating folder) | `shared/text` | `parts.shared/text` |
| `everything` | `everything` | `everything` |
| `api@any` (from `api`) | `api@any` | `parts.api` |
| `store` in a profile with no repeating folder | `store` | `parts.store` |
| `edge` in a tier's `imports.also`, no repeating folder | `edge` | `parts.edge` |

The sentence embeds the new text: `api may also import module.service (parts.api.imports.may)`,
`the unit tests may also import parts.store (tiers.unit.imports.also)`,
`store may also meet imports.must with parts.edge (parts.store.imports.must)`.

Observable through the CLI (wired):

- `xarch profile check <copy of web>` with `domain` given `imports: {may: [kernel, platform]}` says
  `domain may also import parts.platform (parts.domain.imports.may)`; the JSON `looser` entry is
  `{"key": "imports.may", "part": "domain", "what": "parts.platform", "sentence": "domain may also import
  parts.platform (parts.domain.imports.may)"}`.
- `xarch check --profile arch/mine.yaml` (web copy, `kernel` given `may: [platform]`) prints
  `    imports.may: kernel may also import parts.platform (parts.kernel.imports.may)`, the same in the JSON.
- `uv run xarch profile check architecture.yaml` prints its looser lines respelled and nothing else changed:
  `domain may also import parts.profile-values (...)` and the six like it, `cli may also import parts.reports (...)`,
  and `the integration tests may also import module.domain/values` (and `/profile`, `/parsed`, `/outcomes`) under
  `tiers.integration.imports.also`. The libraries, `dead-code` and `no-twins` lines do not move. The count and order
  of lines do not move.

### Design choice for the planner

One writer of the spelling serves both modules. `Target` and `EVERYTHING` live in `xarch/profile_values/placement.py`;
both `written.py` (rules) and `looseness.py` (spec) may import `profile_values` and `kernel` (their `imports.may` in
`architecture.yaml`). The planner may put one function, for example
`written_target(target: Target, words: Mapping[str, str]) -> str`, in `xarch/kernel/logic/targets.py` beside the
reader `target()` (the kernel holds the grammar both ways), and have `_place` and `_shown` call it; or keep two
functions with the same table. Whichever is chosen, `uv run xarch check --strict` must pass (no `no-duplicates`, no
`pass-through` finding: a one-line wrapper that only forwards is a pass-through, so `_place` and `_shown` are either
dropped for the shared function or keep their own work, `_shown` its `everything` branch). The `ValueError` text is
the one of B1 in both.

## Out of scope

- The profiles and the format text: `cli.yaml`, `web.yaml`, `architecture.yaml`, `keys.yaml`, the README symbols
  bullet's description of the bundled spelling, the docstrings that describe the bare name (sub-step 3, card 8.3).
  They keep `@any` and bare names and must keep loading.
- Refusing the old forms, the reserved word `parts`, a prefixed name outside `imports` (sub-step 4).
- The `imports.also` test of note 3.8 (sub-step 5).
- The error texts of `target()` and of `targets_written.py` / `profile_parsing.py` (they are the reader's, 8.1 and
  sub-step 4).
- `tests/modules/spec/adapters/test_yaml_profile_format.py:71-75` (`[core, api@any/v1]`): it hands the YAML adapter
  a `WrittenCheck` built by hand and checks the adapter's text; no writer of this card is in it. Unchanged.
- `tests/modules/rules/application/test_profile_check.py:52` (`Loosened(... "api", "core may also import api")`):
  a `Loosened` built by hand for a fake. Unchanged.
- The `Loosened` values of `test_origin.py` whose `what` does not come from `_shown` (`imports.types_only` of a tier,
  `imports.libraries`, `uses.never`, and the rest). Unchanged.
- The corpora: no recorded finding prints a target's spelling (note 5.3, lines 418-423). Untouched.
- The docs phrase (`may_import` in `kernel/logic/imports.py`, `where`'s `may_import_text`): prints paths, unchanged.

## Tests that prove it (written first, each seen failing)

Tiers are xarch's own (`architecture.yaml`, `tiers`): `unit` for pure logic of the kernel or a module, `integration`
for a use case with fakes, `wired` for the CLI through `bootstrap`.

### `tests/modules/rules/application/logic/test_written.py` (unit: `check_of` and `_place` are pure logic of rules)

Fixture, as today: `PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"),
"kernel": ("kernel",)}`, `SERVICES = ("services", PARTS["services"])`; add
`WORDS = {"domain": "module", "services": "module"}` and `REPEATS = (Repeat("module", ("modules",)),)`.

- **T1. The round trip** (`test_a_place_is_written_as_it_is_read_and_reads_back_as_itself`, kept, rows changed).
  `check_of(rule, ".", words=WORDS)` writes the place, and `target(place, owner, PARTS, PARTS, "at", [],
  patterns=True, alone="a tier's folder", repeats=REPEATS)` reads it back:

  | id | written | owner | found |
  |---|---|---|---|
  | own instance by its word | `module.domain` | `SERVICES` | `Target("domain", "own")` |
  | any instance, and a path below | `parts.domain/values` | `SERVICES` | `Target("domain", "any", ("values",))` |
  | a part outside, narrowed by a name pattern | `parts.kernel:*Id` | `SERVICES` | `Target("kernel", "none", (), "*Id")` |
  | a scope of no part reaches an instance by parts. | `parts.domain` | `None` | `Target("domain", "any")` |
  | own instance, a path and a pattern | `module.domain/values:*Id` | `SERVICES` | `Target("domain", "own", ("values",), "*Id")` |

  The row ids drop the words "bare name" and "@any". The problems list stays empty for every row (assert it).
  The owner's own part with `module.` is not a row: `target()` refuses it as implied (note 3.9).
- **T2. A second word.** With `PARTS` extended by `"store": ("units", "*", "store")`, words
  `{"store": "unit", ...}` and repeats with `Repeat("unit", ("units",))`, `Target("store", "own", ("sql",), "Sql*")`
  is written `unit.store/sql:Sql*` and, owner `("ledger", ("units", "*", "ledger"))` with `"ledger"` in `PARTS`, read
  back to itself. Proves the word comes from the part's folder, not a constant.
- **T3. Own with no word is refused** (`pytest.raises(ValueError, match="lies in no repeating folder")`):
  `check_of(Rule(... Match("place", places=(Target("kernel", "own"),)) ...), ".", words={})`.
- **T4.** `test_a_rule_is_the_check_a_profile_would_write`, first row: the expectation becomes
  `WrittenTarget("place", ("parts.core", "parts.api/v1"))`, `check_of(rule, ".", words={})`; every other row passes
  `words={}` with its expectation unchanged.
- Every other test of the file passes `words=` where it calls `check_of` or `written`, with its expectation
  unchanged.

### `tests/modules/spec/application/logic/test_looseness.py` (unit: `origin_of` is pure logic of the spec)

- **T5.** `test_a_target_added_to_a_rule_is_shown_as_written`: the rows become (written, shown)
  `(["service"], "module.service")`, `(["store@any/sql"], "parts.store/sql")`, `(["shared/text"],
  "parts.shared/text")`, `("everything", "everything")`, `(["api@any"], "parts.api")`; the ids say the new spelling
  ("an own-instance part is shown by its word", "any instance and a sub path", "a part outside the repeating folder is
  shown with parts.", ...). The sentence is built from `shown`, as today.
- **T6.** `test_every_way_a_profile_is_looser_than_another_is_found_in_order`: `Loosened("imports.may", "core",
  "parts.store", "core may also import parts.store (parts.core.imports.may)")` and `Loosened("imports.also", "unit",
  "parts.edge", "the unit tests may also import parts.edge (tiers.unit.imports.also)")`; every other entry unchanged
  (`imports.types_only` keeps `store`).
- **T7.** `test_what_a_tiers_tests_may_also_import_beyond_the_bundled_tier_is_looser`, first row:
  `parts.shared/text` and `parts.store` in `what` and in the sentence.
- **T8. The `types_only` line, tested today, respelled.** `test_a_mark_dropped_while_its_target_stays_allowed_is_looser`
  (lines 205-216, `marked()`): `shared` lies outside the repeating folder, so the two expected sentences become
  `service may now call parts.shared, which it used only as a type (parts.service.imports.may.types_only)`, and the
  `what` filtered is `parts.shared` (the `found` tuples' third item). Add one row for an own-scope target:
  base `[{"store": "types_only"}, "shared"]`, custom `["store", "shared"]`, found
  `(MARK, "service", "module.store", "service may now call module.store, which it used only as a type
  (parts.service.imports.may.types_only)")`. The planner pins the row by running it first on today's code (where the
  `what` is `store`).
- **T8b. A looser line on a part in the repeating folder.**
  `test_a_part_renamed_in_place_pairs_by_its_path_and_is_compared_under_its_own_name` (line ~386): the entry becomes
  `Loosened("imports.may", "routes", "module.store", "routes may also import module.store
  (parts.routes.imports.may)")` (`store` lies in `src/<module>/`).
- **T9. New: the word is the one of the part's own folder.** Profiles from `two_folders()`
  (`tests/modules/spec/profiles.py:52`, folders `src/<module>/` and `ext/<plugin>/`, `manifest` may `["hooks"]`).
  Two rows, each against a base `two_folders()` whose `manifest` may `[]`:
  custom `manifest` may `["hooks"]` gives `Loosened("imports.may", "manifest", "plugin.hooks", "manifest may also
  import plugin.hooks (parts.manifest.imports.may)")`; custom `manifest` may `["hooks@any"]` gives `what ==
  "parts.hooks"`. Proves the word is read from the part's folder in the profile at hand, not the first repeat and not
  `module`.

### `tests/modules/spec/application/test_origin.py` (integration: the origin use case)

- **T10.** Line 112: `Loosened("imports.must", "store", "parts.edge", "store may also meet imports.must with
  parts.edge (parts.store.imports.must)")`. Lines 55, 62 if they come from `_shown` (they do: `imports.may` and
  `imports.also`): `parts.store`, `parts.edge` as in T6. Others unchanged.

### Wired (`tests/bootstrap/`, the CLI through the real wiring)

- **T11.** `tests/bootstrap/test_profile_check.py:107-111`: `domain may also import parts.platform
  (parts.domain.imports.may)`, the JSON `what` `parts.platform` and its sentence.
- **T12.** `tests/bootstrap/test_check_enforcement.py:114, 148, 154`: `kernel may also import parts.platform
  (parts.kernel.imports.may)`, the JSON `what` `parts.platform` and its sentence.
- **T13. New, beside the tests of `tests/bootstrap/test_bundled_imports.py`:** for `cli`, `web` and
  `architecture.yaml`, the text of `profile explain parts.imports.must --rule --profile <p> --format json` holds
  `targets: [{place: [parts.platform, parts.contract]}, outside]` and no `@any`.
- **T14.** `tests/bootstrap/test_bundled_imports.py` `RULES`: the three `must` digests (`3a6fe3a7e4628850` today)
  move, and only they. The engineer captures the checks text of each `(profile, key)` of `RULES` and `TIER_RULES`
  before the change and after it, and confirms the only difference is the one line of T13 (old
  `[platform, contract@any]`, new `[parts.platform, parts.contract]`). The new digests are what the test then
  computes. The `RULES` docstring gains one sentence: in 0.3.0 the places of `must` are written as references
  (`parts.<part>`), which moved only that digest. No other digest moves; one that does is a defect to report.
- **T15. New, `tests/bootstrap/test_profile_explain_words.py`:** `profile explain targets.place` (run in the
  repository, so its example comes from `architecture.yaml`) holds `[parts.platform, parts.contract]` and no `@any`
  in its example.

No other test file is expected to change. Any other failure after the change is read: a test that asserts an old
spelling written by `_place` or `_shown` is updated to the new spelling with its meaning unchanged; anything else is a
defect.

## Docs

- `README.md` (review 3 O4): the symbols bullet (lines 227-233) keeps describing the old forms as the bundled
  spelling (profiles move in 8.3). It gains one sentence: `profile explain --rule` and the looser lines of
  `profile check` and `check` write a target as a reference, `parts.<part>` or `<word>.<part>`. No other README line
  moves.
- `CHANGELOG.md`, `## [Unreleased]`, `### Changed` (create the heading if absent; review 3 O5): one entry.
  `profile explain <key> --rule` and the example of `profile explain <word>` write a check's `place` as a reference,
  and the looser lines of `profile check` and `check` (and their JSON `what` and `sentence`) write a target so:
  `parts.<part>` for a part in every instance or in none, `<word>.<part>` for the importer's own instance, `/<path>`
  and `:<pattern>` as before (for example `domain may also import parts.platform`, `[place: [parts.platform,
  parts.contract]]`). The JSON's shape does not change.
- Golden docs `docs/{cli,web,xarch}/` (review 3 O8): regenerated the way commit ddea9db did (through the docs path
  of `tests/bootstrap/test_docs_templates.py`), and the diff read. No diff is expected (note 5.3, lines 415-418: the
  docs phrase prints paths). Never edited by hand. A diff is a defect to report, not to regenerate past.

## Gates

Each passing on this branch alone: `uv run ruff check` (never `--fix`), `uv run xarch check`,
`uv run xarch check --strict`, `uv run xarch profile check architecture.yaml` (its output read against today's, B2),
then `uv run pytest -q` in the background (over two minutes), read at the end.

## Review focus (for the planner)

1. A profile with two repeating words (`two_folders`): the word must follow the part, never the first repeat or the
   owner's folder (T2, T9).
2. The `types_only` looser line, the one call of `_shown` on a renamed bundled target (T8: its existing rows move to `parts.shared`, one new row proves `module.`).
3. A target with both `/path` and `:pattern` under `<word>.`: order is prefix, part, path, pattern (T1 last row, T2).
4. `everything` in `_shown` stays the word, never `parts.everything` (T5 row).
5. A part whose name holds `-` (`profile-values`, `kernel-logic`): written as `parts.profile-values`, read back by
   `target()` (the `architecture.yaml` looser lines, B2; add a T1 row only if the planner finds `-` untested in the
   round trip).

---

# 8.2 the writers emit the new reference form, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `profile explain <key> --rule`, the example of `profile explain <word>`, and the looser lines of `profile check` and `check` write a `Target` as a reference (`parts.<part>` or `<word>.<part>`, then `/<path>`, then `:<pattern>`), which `target()` reads back to the same `Target`.

**Architecture:** One writer of the spelling, `written_target(target, words)`, goes into `xarch/kernel/logic/targets.py` beside the reader `target()`. The rules module drops its `_place` and calls `written_target` from `_target`; `check_of` and `written` gain a keyword-only, required `words`, passed by `ExplainingService` from the profile at hand. The spec module's `_shown` keeps its `everything` branch and calls `written_target` with `custom.words()`.

**Tech Stack:** Python 3.13, pytest, typer's `CliRunner`, `uv`, `ruff`, xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/8-2-spec-the-writers-e7336bbc.md` (copied in full above this plan).

## Global Constraints

- Scope `any` and scope `none` are written `parts.<part>`; scope `own` is written `<word>.<part>`, the word that of the repeating folder the part lies in; then `/<step>/<step>...` for `sub`, then `:<names>` when `names` is not empty.
- The word comes from the part's path through the profile's repeats (`Profile.words()` / `Architecture.words()`). Never from the owner, never by splitting the part name, never a literal `module`.
- A target of scope `own` whose part has no word raises `ValueError("Target 'kernel' is in its importer's own instance, but part 'kernel' lies in no repeating folder")` (part name with `!r`). No fallback to `parts.` nor to the bare name.
- `everything` is still written `everything` by `_shown`.
- `_shown`'s output keeps its place and shape; the JSON keys do not change.
- No profile, no parser, no `Target` field, no refusal changes. `cli.yaml`, `web.yaml`, `architecture.yaml`, `keys.yaml` untouched.
- No comments in xarch's code (docstrings only). Never `ruff --fix`. Tests written first and seen failing. Recorded corpora (`tests/bootstrap/corpora/`) untouched. `.claude/` out of commits. Nothing pushed.
- `uv run xarch check --strict` must pass: no `no-duplicates`, no `pass-through` finding.
- Golden docs `docs/{cli,web,xarch}/` are never edited by hand.
- Stop a long test run with `timeout`, never `pkill`/`killall`.

## Review Focus

1. A profile with two repeating words: the word follows the part's own folder, never the first repeat, never the owner's folder (`unit.store/...` in Task 1 Step 1, `plugin.hooks` in Task 2 Step 1).
2. The `types_only` looser line, the one call of `_shown` on a bundled target renamed into the custom names: its rows move to `parts.shared`, one new row shows `module.store` (Task 2 Step 1).
3. A target with both `/path` and `:pattern` under `<word>.`: order is prefix, part, path, pattern (`module.domain/values:*Id` and `unit.store/sql:Sql*` in Task 1 Step 1).
4. `everything` in `_shown` stays the word, never `parts.everything` (the `everything` row of T5 in Task 2 Step 1, kept).
5. A part whose name holds `-`: `parts.kernel-logic` round-trips (new T1 row in Task 1 Step 1), and `parts.profile-values` appears in `profile check architecture.yaml` (Task 2 Step 9).

---

## File Structure

- `xarch/kernel/logic/targets.py` — gains `written_target`, the writer of the reference spelling beside the reader `target()`. One grammar, both ways.
- `xarch/modules/rules/application/logic/written.py` — `_place` removed; `_target`, `check_of`, `written`, `written_own` take/pass `words`.
- `xarch/modules/rules/application/services/explaining.py` — passes the profile's words at lines 80 and 117.
- `xarch/modules/spec/application/logic/looseness.py` — `_shown(target, words)`; `_looser` computes `words = custom.words()` once.
- `xarch/modules/spec/domain/published.py` — the `Loosened` docstring's two "(a target as written)" become "(a target as a reference)".
- Tests: `tests/modules/rules/application/logic/test_written.py`, `tests/bootstrap/test_bundled_imports.py`, `tests/bootstrap/test_profile_explain_words.py`, `tests/modules/spec/application/logic/test_looseness.py`, `tests/modules/spec/application/test_origin.py`, `tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_enforcement.py`.
- Docs: `README.md` (one sentence), `CHANGELOG.md` (one entry under `## [Unreleased]` → `### Changed`).

---

### Task 1: The shared writer, and the rules module writes a check's place as a reference

**Files:**
- Modify: `xarch/kernel/logic/targets.py` (module docstring lines 1-9; add `written_target` after `target()`, i.e. after line 81)
- Modify: `xarch/modules/rules/application/logic/written.py:8-16, 25-36, 53-59, 76-87`
- Modify: `xarch/modules/rules/application/services/explaining.py:80, 117`
- Test: `tests/modules/rules/application/logic/test_written.py`
- Test: `tests/bootstrap/test_bundled_imports.py`
- Test: `tests/bootstrap/test_profile_explain_words.py`

**Interfaces:**
- Consumes: `Target(part, scope, sub, names)` from `xarch/profile_values/placement.py`; `Profile.words() -> dict[str, str]` (`xarch/modules/rules/domain/profile.py:124`); `Profiles.profile(location: str) -> Profile` (`xarch/modules/rules/application/ports/profile.py:14`).
- Produces: `written_target(made: Target, words: Mapping[str, str]) -> str` in `xarch.kernel.logic.targets` (Task 2 uses it). `check_of(rule, member, flagged=(), clean=(), *, words: Mapping[str, str]) -> WrittenCheck`; `written(rules, member, *, words: Mapping[str, str]) -> dict[str, WrittenCheck]`; `written_own(checks, language)` unchanged in signature.

- [ ] **Step 0: Capture the checks text of every key `test_bundled_imports.py` digests, before any change**

Create `/tmp/xarch-82-capture.py` (outside the repo; never commit it):

```python
import json
import sys

from typer.testing import CliRunner

from tests.bootstrap.test_bundled_imports import KEYS, RULES, TIER_KEYS, TIER_RULES
from xarch.bootstrap.app import app

runner = CliRunner()
texts = {}
for label, table, keys in (("part", RULES, KEYS), ("tier", TIER_RULES, TIER_KEYS)):
    for profile, key in table:
        found = json.loads(runner.invoke(app, ["profile", "explain", keys[key], "--rule", "--profile", profile,
                                               "--format", "json"]).output)
        texts[f"{label} {profile} {key}"] = found["checks"]
with open(sys.argv[1], "w") as out:
    json.dump(texts, out, indent=1)
```

Run from the worktree root: `timeout 300 uv run python /tmp/xarch-82-capture.py /tmp/xarch-82-before.json`
Expected: the file exists and holds 21 keys (9 part, 12 tier).

- [ ] **Step 1: Write the failing unit tests in `tests/modules/rules/application/logic/test_written.py`**

Replace lines 14-29 (the fixture and the round trip) with:

```python
SAID = (Saying("m", "f"),)
PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"), "kernel": ("kernel",),
         "kernel-logic": ("kernel", "logic")}
SERVICES = ("services", PARTS["services"])
WORDS = {"domain": "module", "services": "module"}
"""The word of the repeating folder each part of PARTS lies in, as Profile.words() gives it."""
REPEATS = (Repeat("module", ("modules",)),)


def placed(made: Target, words=WORDS) -> str:
    """The one place of a rule that names made, as check_of writes it."""
    rule = Rule("x", Scope(), ("import-into-app",), MAY_NOT, (Match("place", places=(made,)),), SAID)
    (place,) = check_of(rule, ".", words=words).quantified.targets[0].values or ()
    return place


@pytest.mark.parametrize("written, owner, found", [
    pytest.param("module.domain", SERVICES, Target("domain", "own"), id="own instance by its word"),
    pytest.param("parts.domain/values", SERVICES, Target("domain", "any", ("values",)), id="any instance, and a path below"),
    pytest.param("parts.kernel:*Id", SERVICES, Target("kernel", "none", (), "*Id"), id="a part outside, narrowed by a name pattern"),
    pytest.param("parts.domain", None, Target("domain", "any"), id="a scope of no part reaches an instance by parts."),
    pytest.param("module.domain/values:*Id", SERVICES, Target("domain", "own", ("values",), "*Id"),
                 id="own instance, a path and a pattern"),
    pytest.param("parts.kernel-logic", SERVICES, Target("kernel-logic", "none"), id="a part whose name holds a dash"),
])
def test_a_place_is_written_as_it_is_read_and_reads_back_as_itself(written, owner, found):
    place = placed(found)
    problems: list[str] = []
    assert (place, target(place, owner, PARTS, PARTS, "at", problems, patterns=True, alone="a tier's folder",
                          repeats=REPEATS), problems) == (written, found, [])


def test_the_word_of_an_own_instance_is_that_of_the_folder_its_part_lies_in():
    parts = {**PARTS, "store": ("units", "*", "store"), "ledger": ("units", "*", "ledger")}
    made = Target("store", "own", ("sql",), "Sql*")
    place = placed(made, {**WORDS, "store": "unit", "ledger": "unit"})
    problems: list[str] = []
    assert (place, target(place, ("ledger", parts["ledger"]), parts, parts, "at", problems, patterns=True,
                          alone="a tier's folder", repeats=(*REPEATS, Repeat("unit", ("units",)))), problems) == (
        "unit.store/sql:Sql*", made, [])


def test_a_place_in_the_own_instance_of_a_part_in_no_repeating_folder_is_refused():
    with pytest.raises(ValueError, match="Target 'kernel' is in its importer's own instance, but part 'kernel' lies in "
                                         "no repeating folder"):
        placed(Target("kernel", "own"), {})
```

In `test_a_rule_is_the_check_a_profile_would_write`, change the first row's expectation (line 37) from `WrittenTarget("place", ("core", "api@any/v1"))` to:

```python
                              Quantified(MUST_REACH, (WrittenTarget("place", ("parts.core", "parts.api/v1")),
```

and its body (line 57) to:

```python
def test_a_rule_is_the_check_a_profile_would_write(rule, check):
    assert check_of(rule, ".", words={}) == check
```

Change `test_rules_written_as_checks_each_take_an_id_of_their_own` (lines 60-65) to:

```python
def test_rules_written_as_checks_each_take_an_id_of_their_own():
    rule = Rule("names", Scope(part="store"), ("class",), MAY_NOT, EXISTING, SAID)
    other = Rule("names", Scope(), ("class",), MAY_NOT, EXISTING, SAID)
    assert written([rule, rule, other], ".", words={}) == {
        "names-store": check_of(rule, ".", words={}), "names-store-2": check_of(rule, ".", words={}),
        "names": check_of(other, ".", words={})}
    assert written([rule, other], ".", words={}) == {"names-store": check_of(rule, ".", words={}),
                                                     "names": check_of(other, ".", words={})}
```

In `test_the_tokens_of_the_language_are_filled_in` (line 95) the expectation becomes:

```python
        "no-todo": check_of(rule, language.member, (("notes.py", written_out),), (), words={})}
```

In `test_an_outside_name_is_written_back_with_the_member_of_the_language` (line 101):

```python
    assert check_of(rule, "#", words={}).quantified.targets == (
        WrittenTarget("path", ("node:fs#readFileSync", ".toISOString()")),)
```

Change the module docstring's first sentence (lines 1-3) to:

```python
"""A rule as the check a profile would write: its slots as the format holds them, its targets as written (places as
references, `parts.<part>` or `<word>.<part>`, which target() reads back; dotted names joined), a rule of reach with how
it reaches; each under an id of its own; and the tokens of the language filled into the examples."""
```

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest tests/modules/rules/application/logic/test_written.py -q`
Expected: FAIL — `TypeError: check_of() got an unexpected keyword argument 'words'` (and `written()` the same) in every test but the three `written_own` ones.

- [ ] **Step 3: Write the failing wired tests**

In `tests/bootstrap/test_bundled_imports.py`, after `test_each_key_of_the_group_expands_to_the_rules_of_before` (line 109), add:

```python
@pytest.mark.parametrize("profile", ["cli", "web", "architecture.yaml"])
def test_the_places_a_part_must_import_are_written_as_references(profile):
    found = json.loads(runner.invoke(app, ["profile", "explain", "parts.imports.must", "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    assert "targets: [{place: [parts.platform, parts.contract]}, outside]" in found["checks"]
    assert "@any" not in found["checks"]
```

In `tests/bootstrap/test_profile_explain_words.py`, the imports (lines 4-9) become:

```python
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app
```

and after `runner = CliRunner()` add:

```python
ROOT = Path(__file__).resolve().parents[2]
"""The repository, whose architecture.yaml is the profile in force when xarch is run there."""
```

and at the end of the file:

```python
def test_the_example_of_targets_place_writes_its_places_as_references(monkeypatch):
    monkeypatch.chdir(ROOT)
    result = explain("targets.place")
    assert result.exit_code == 0, result.output
    example = result.output.partition("  example: ")[2]
    assert "architecture.yaml expands to" in example
    assert "targets: [{place: [parts.platform, parts.contract]}, outside]" in example
    assert "@any" not in example
```

- [ ] **Step 4: Run them to see them fail**

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_imports.py::test_the_places_a_part_must_import_are_written_as_references tests/bootstrap/test_profile_explain_words.py::test_the_example_of_targets_place_writes_its_places_as_references -q`
Expected: 4 FAIL, each on the `targets: [{place: [parts.platform, parts.contract]}, outside]` assertion (today's text is `[platform, contract@any]`).

- [ ] **Step 5: Add `written_target` to `xarch/kernel/logic/targets.py`**

Replace the module docstring's last sentence (line 8-9, "Any other value is read in the old forms: ...") so the docstring ends:

```python
`/<path>` and, where the key takes one, `:<pattern>`. Any other value is read in the old forms: `<part>`, `<part>@any`,
`<part>/<path>` and `<part>:<pattern>`. A target is written back as a reference (see written_target), which reads
back as itself."""
```

After `target()` (after line 81, before `def _reference`), add:

```python
def written_target(made: Target, words: Mapping[str, str]) -> str:
    """The target as a reference, which target() reads back to it: `parts.<part>` for the part in every instance of its
    repeating folder or in none, `<word>.<part>` for the importer's own instance, the word that of the repeating folder
    the part lies in (words, by part); then the path below the part and the name pattern. Raises ValueError for the own
    instance of a part words gives no word, which lies in no repeating folder and has no own instance."""
    if made.scope == "own" and made.part not in words:
        raise ValueError(f"Target {made.part!r} is in its importer's own instance, but part {made.part!r} lies in no "
                         "repeating folder")
    prefix = words[made.part] if made.scope == "own" else "parts"
    return f"{prefix}.{made.part}" + "".join(f"/{step}" for step in made.sub) + (f":{made.names}" if made.names else "")
```

(`Mapping` and `Target` are already imported at lines 13 and 18.)

- [ ] **Step 6: Make `written.py` write with it**

In `xarch/modules/rules/application/logic/written.py`:

Imports (lines 8-16) become:

```python
import re
from collections.abc import Iterable, Mapping

from xarch.kernel.logic.names import outside_text
from xarch.kernel.logic.targets import written_target
from xarch.modules.rules.domain.rule import MUST_BE_REACHED, Match, OwnCheck, Rule
from xarch.modules.rules.domain.vocabulary import TARGETS
from xarch.profile_values.checks import Quantified, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage
```

(the `from xarch.profile_values.placement import Target` line goes: nothing uses it once `_place` is gone).

`written` and `written_own` (lines 25-36) become:

```python
def written(rules: Iterable[Rule], member: str, *, words: Mapping[str, str]) -> dict[str, WrittenCheck]:
    """The rules as checks of a profile, each under an id of its own (see _ids), an outside name joined with the
    language's member, a place written as a reference with words, the word of the repeating folder each part of the
    profile lies in."""
    rules = list(rules)
    return {name: check_of(rule, member, words=words) for rule, name in zip(rules, _ids(rules))}


def written_own(checks: Iterable[OwnCheck], language: CheckedLanguage) -> dict[str, WrittenCheck]:
    """Checks of a profile's own as its `checks` are written, each under its id with its examples, the tokens of the
    language (see _tokens_filled) in their paths and code filled in; checks written for the explanation, which name no
    place, so no word is needed."""
    return {own.rule.id: check_of(own.rule, language.member, _filled(own.flagged, language), _filled(own.clean, language),
                                  words={})
            for own in checks}
```

`check_of` (lines 53-59) becomes:

```python
def check_of(rule: Rule, member: str, flagged: tuple[tuple[str, str], ...] = (),
             clean: tuple[tuple[str, str], ...] = (), *, words: Mapping[str, str]) -> WrittenCheck:
    """The rule as the check a profile would write, with the examples given, an outside name joined with member, a place
    written as a reference with words (see written_target); raises ValueError for a place in the own instance of a part
    words gives no word."""
    targets = () if rule.quantifier == MUST_BE_REACHED else tuple(_target(match, member, words) for match in rule.targets)
    quantified = Quantified(rule.quantifier, targets, rule.links, rule.via, rule.roots, rule.spread, rule.elsewhere)
    return WrittenCheck(rule.facts, rule.scope, quantified, rule.sayings, rule.keep, rule.exempt, rule.mode, flagged,
                        clean)
```

`_target` and `_place` (lines 76-87) become only:

```python
def _target(match: Match, member: str, words: Mapping[str, str]) -> WrittenTarget:
    if match.kind not in _VALUED:
        return WrittenTarget(match.kind)
    return WrittenTarget(match.kind, (*(written_target(place, words) for place in match.places),
                                      *(outside_text(n, member) for n in match.names), *match.words))
```

- [ ] **Step 7: Pass the profile's words in `explaining.py`**

In `xarch/modules/rules/application/services/explaining.py`, line 80 becomes:

```python
            words = self._profiles.profile(location).words()
            return explained.example_key(rule), location, self._form.written({rule.id: check_of(rule, language.member,
                                                                                                 words=words)})
```

and `rule()`'s return (lines 117-118) becomes:

```python
        words = self._profiles.profile(location).words()
        return RuleShown(address, location, self._form.written(written(rules, self.language((location,)).member, words=words)),
                         len(rules), tuple(dict.fromkeys(need for rule in rules for need in rule.needs)))
```

(`example()` found the rule by loading the profile at `location`, and `rules_of` loaded it before line 117, so neither `profile(location)` call meets a profile that cannot be read.)

- [ ] **Step 8: Run the unit and wired tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/rules/application/logic/test_written.py tests/bootstrap/test_profile_explain_words.py tests/bootstrap/test_bundled_imports.py::test_the_places_a_part_must_import_are_written_as_references -q`
Expected: PASS.

- [ ] **Step 9: Capture the checks text after, and read the difference**

Run: `timeout 300 uv run python /tmp/xarch-82-capture.py /tmp/xarch-82-after.json`

Then diff with:

```bash
timeout 60 uv run python -c "
import json, difflib
b, a = json.load(open('/tmp/xarch-82-before.json')), json.load(open('/tmp/xarch-82-after.json'))
for k in b:
    if b[k] != a[k]:
        print('==', k); print(''.join(difflib.unified_diff(b[k].splitlines(True), a[k].splitlines(True), n=0)))
"
```

Expected: exactly three keys differ, `part cli must`, `part web must`, `part architecture.yaml must`, each with one line:
`-      targets: [{place: [platform, contract@any]}, outside]` / `+      targets: [{place: [parts.platform, parts.contract]}, outside]`.
Any other key or line that differs is a defect: stop and report it, do not update a digest past it.

- [ ] **Step 10: Move the three `must` digests in `test_bundled_imports.py`, and say why**

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_imports.py -q`
Expected before the edit: exactly 3 FAIL, `test_each_key_of_the_group_expands_to_the_rules_of_before[cli-must]`, `[web-must]`, `[architecture.yaml-must]`, each `(1, '<new>') != (1, '3a6fe3a7e4628850')`. The new digest, computed while writing this plan from today's text with that one line respelled, is `cb8bbbfa024c046c`; use the value the failure prints, and if it is not `cb8bbbfa024c046c` read Step 9's diff again before going on.

Edit `RULES` (lines 48-55) so the three `must` entries read `(1, "cb8bbbfa024c046c")`:

```python
RULES = {
    ("cli", "may"): (12, "b5fb19f749264287"), ("cli", "must"): (1, "cb8bbbfa024c046c"),
    ("cli", "libraries"): (24, "ae1fba4a77503d1a"),
    ("web", "may"): (12, "f06766b1dbdc51b7"), ("web", "must"): (1, "cb8bbbfa024c046c"),
    ("web", "libraries"): (24, "058402903c045a47"),
    ("architecture.yaml", "may"): (15, "0d94a54e9f44405d"), ("architecture.yaml", "must"): (1, "cb8bbbfa024c046c"),
    ("architecture.yaml", "libraries"): (30, "27ee07b82ce0c6a6"),
}
"""For each profile and key of the group: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change. The rules come in the order of the parts, which became the folder tree's reading
order in 0.3.0 (`contract` after `adapters`, `kernel` before `kernel-logic`): the lines of `may` and `libraries` are the
same as before, and only their order, so only their digests, moved. In 0.3.0 the places of `must` are written as
references (`parts.<part>`), which moved only that digest."""
```

Run: `timeout 300 uv run pytest tests/bootstrap/test_bundled_imports.py -q`
Expected: PASS.

- [ ] **Step 11: Run the rules module and the gates for this task**

Run: `timeout 600 uv run pytest tests/modules/rules tests/kernel -q`
Expected: PASS. A failure that asserts an old spelling written by `check_of`/`written` is updated to the new spelling with its meaning unchanged; any other failure is a defect to report.

Run: `uv run ruff check` (never `--fix`) — Expected: `All checks passed!`
Run: `uv run xarch check --strict` — Expected: exit 0, no finding.

- [ ] **Step 12: Commit**

```bash
git add xarch/kernel/logic/targets.py xarch/modules/rules/application/logic/written.py \
  xarch/modules/rules/application/services/explaining.py tests/modules/rules/application/logic/test_written.py \
  tests/bootstrap/test_bundled_imports.py tests/bootstrap/test_profile_explain_words.py
git commit -m "profile explain --rule and the example of a word write a check's place as parts.<part> or <word>.<part>, the word that of the part's repeating folder, through written_target beside target()

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The looser lines of `profile check` and `check` say a target as a reference

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py:56-66 (imports), 245-300 (_looser), 557-562 (_shown)`
- Modify: `xarch/modules/spec/domain/published.py:110, 122`
- Test: `tests/modules/spec/application/logic/test_looseness.py`
- Test: `tests/modules/spec/application/test_origin.py`
- Test: `tests/bootstrap/test_profile_check.py:107-111`
- Test: `tests/bootstrap/test_check_enforcement.py:114, 148, 154`

**Interfaces:**
- Consumes: `written_target(made: Target, words: Mapping[str, str]) -> str` from `xarch.kernel.logic.targets` (Task 1); `Architecture.words() -> dict[str, str]` (`xarch/modules/spec/domain/values.py:445`).
- Produces: `_shown(target: Target, words: Mapping[str, str]) -> str` (private to `looseness.py`); the `what` and `sentence` of each `Loosened` under `imports.may`, `imports.may.types_only`, `imports.must`, `imports.also`.

- [ ] **Step 0: Capture `profile check architecture.yaml` before the change**

Run: `uv run xarch profile check architecture.yaml > /tmp/xarch-82-pc-before.txt 2>&1; echo $?`
Expected: `0`, and the file ends `OK: the profile is valid`.

- [ ] **Step 1: Write the failing unit tests in `tests/modules/spec/application/logic/test_looseness.py`**

Module docstring, line 2: `a rule's target is shown as the file writes it` becomes `a rule's target is shown as a reference (parts.<part> or <word>.<part>)`, so lines 1-4 read:

```python
"""How a custom profile is looser than a bundled one, on hand-made architectures, as the origin of the custom one says
it: a rule's target is shown as a reference (parts.<part> or <word>.<part>), and each way is said naming the key that
says it. The sentence of each way a profile is looser is asserted here or in tests/modules/spec/application/test_origin.py
(a package added to `imports.libraries`, a part that may import any outside package, an `imports.must` target added or
the key dropped)."""
```

Line 11 import becomes:

```python
from tests.modules.spec.profiles import covered, layered, parsed, part_of, two_folders
```

T5 — replace the table of `test_a_target_added_to_a_rule_is_shown_as_written` (lines 23-29) with:

```python
@pytest.mark.parametrize("written, shown", [
    pytest.param(["service"], "module.service", id="an own-instance part is shown by its word"),
    pytest.param(["store@any/sql"], "parts.store/sql", id="any instance and a sub path"),
    pytest.param(["shared/text"], "parts.shared/text", id="a part outside the repeating folder is shown with parts."),
    pytest.param("everything", "everything", id="everything is shown as the word"),
    pytest.param(["api@any"], "parts.api", id="another instance of the part itself is looser than its own, which is implied"),
])
```

(the body, lines 30-36, is unchanged.)

T6 — in `test_every_way_a_profile_is_looser_than_another_is_found_in_order`, line 65 and line 72 become:

```python
        Loosened("imports.may", "core", "parts.store", "core may also import parts.store (parts.core.imports.may)"),
```

```python
        Loosened("imports.also", "unit", "parts.edge", "the unit tests may also import parts.edge (tiers.unit.imports.also)"),
```

(the `imports.types_only` entry, lines 70-71, keeps `store`.)

T7 — the first row of `test_what_a_tiers_tests_may_also_import_beyond_the_bundled_tier_is_looser` (lines 81-86) becomes:

```python
    pytest.param([], ["shared/text", "store@any"], (
        Loosened("imports.also", "unit", "parts.shared/text",
                 "the unit tests may also import parts.shared/text (tiers.unit.imports.also)"),
        Loosened("imports.also", "unit", "parts.store",
                 "the unit tests may also import parts.store (tiers.unit.imports.also)")),
                 id="each target the bundled tier does not give is looser, shown as a reference"),
```

T8 — the table of `test_a_mark_dropped_while_its_target_stays_allowed_is_looser` (lines 203-217) becomes:

```python
@pytest.mark.parametrize("base, custom, found", [
    pytest.param(["store", {"shared": "types_only"}], ["store", "shared"],
                 [(MARK, "service", "parts.shared", "service may now call parts.shared, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an entry that stays"),
    pytest.param([{"store": "types_only"}, "shared"], ["store", "shared"],
                 [(MARK, "service", "module.store", "service may now call module.store, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an own-instance entry, shown by its word"),
    pytest.param(["store", {"shared": "types_only"}], ["store"], [], id="the entry dropped with its mark"),
    pytest.param(["store", {"shared": "types_only"}], ["store", {"shared": "types_only"}], [], id="the mark kept"),
    pytest.param(["store", {"shared/x": "types_only"}], ["store", {"shared": "types_only"}], [],
                 id="a wider mark covers it"),
    pytest.param(["store", {"shared": "types_only"}], "everything",
                 [(MARK, "service", "parts.shared", "service may now call parts.shared, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="everything over a mark"),
])
```

(The new own-instance row was run on today's code while writing this plan: it finds `(MARK, "service", "store", "service may now call store, which it used only as a type (parts.service.imports.may.types_only)")`, so it fails today only on the spelling.)

T8b — in `test_a_part_renamed_in_place_pairs_by_its_path_and_is_compared_under_its_own_name` (line ~386):

```python
    assert origin.looser == (
        Loosened("imports.may", "routes", "module.store", "routes may also import module.store (parts.routes.imports.may)"),)
```

T9 — add after `test_a_target_added_to_a_rule_is_shown_as_written`:

```python
@pytest.mark.parametrize("may, shown", [
    pytest.param(["hooks"], "plugin.hooks", id="the own instance is named by the word of its part's own folder"),
    pytest.param(["hooks@any"], "parts.hooks", id="any instance of a part of the second folder is named with parts."),
])
def test_the_word_a_target_is_shown_with_is_that_of_its_part_s_own_repeating_folder(may, shown):
    base, custom = two_folders(), two_folders()
    part_of(base, "manifest")["imports"] = {"may": []}
    part_of(custom, "manifest")["imports"] = {"may": may}
    assert loosened(parsed(custom), parsed(base)) == (
        Loosened("imports.may", "manifest", shown, f"manifest may also import {shown} (parts.manifest.imports.may)"),)
```

(`two_folders()` adds `ext/<plugin>/` with `hooks/` and `manifest.py` beside `src/<module>/`; its `words()` is `{'api': 'module', 'service': 'module', 'store': 'module', 'hooks': 'plugin', 'manifest': 'plugin'}`, checked while writing this plan.)

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_looseness.py -q`
Expected: FAIL in the rows changed above, each an assertion error showing the old spelling (`'service'` for `'module.service'`, `'store@any/sql'` for `'parts.store/sql'`, `'hooks'` for `'plugin.hooks'`, ...). The `everything` row of T5, the second to fifth rows of T8 but the new one, and the untouched tests pass.

- [ ] **Step 3: Respell the integration and wired expectations**

`tests/modules/spec/application/test_origin.py` line 55:

```python
        Loosened("imports.may", "core", "parts.store", "core may also import parts.store (parts.core.imports.may)"),
```

line 62:

```python
        Loosened("imports.also", "unit", "parts.edge", "the unit tests may also import parts.edge (tiers.unit.imports.also)"),
```

line 112:

```python
        Loosened("imports.must", "store", "parts.edge", "store may also meet imports.must with parts.edge (parts.store.imports.must)"),)
```

`tests/bootstrap/test_profile_check.py` lines 107-111:

```python
    assert "domain may also import parts.platform (parts.domain.imports.may)" in result.output
    shown = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)
    assert shown["compared_with"]["looser"] == [
        {"key": "imports.may", "part": "domain", "what": "parts.platform",
         "sentence": "domain may also import parts.platform (parts.domain.imports.may)"}]
```

`tests/bootstrap/test_check_enforcement.py` line 114:

```python
        "    imports.may: kernel may also import parts.platform (parts.kernel.imports.may)"]
```

line 148:

```python
    assert "    imports.may: kernel may also import parts.platform (parts.kernel.imports.may)" in strict.stdout.splitlines()
```

lines 153-154:

```python
        {"key": "imports.may", "part": "kernel", "what": "parts.platform",
         "sentence": "kernel may also import parts.platform (parts.kernel.imports.may)"}]
```

- [ ] **Step 4: Run them to see them fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/test_origin.py tests/bootstrap/test_profile_check.py::test_a_looser_copy_is_still_valid_and_the_difference_is_information tests/bootstrap/test_check_enforcement.py::test_a_custom_copy_of_a_bundled_profile_is_compared_with_it tests/bootstrap/test_check_enforcement.py::test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_shown_and_never_fails_strict -q`
Expected: FAIL in `test_every_way_a_custom_profile_is_looser_than_the_bundled_one_it_resembles_is_listed`, `test_a_part_that_no_longer_has_to_import_or_may_meet_it_with_more_is_looser` and the three wired tests, each on the old spelling (`'store'`, `'edge'`, `'platform'`).

- [ ] **Step 5: Make `_shown` write the reference**

In `xarch/modules/spec/application/logic/looseness.py`, add to the imports (after `from xarch.kernel.logic.placement import name_matches`, keeping ruff's order):

```python
from xarch.kernel.logic.targets import written_target
```

In `_looser` (line 245), add after `member = custom.language.checked.member`:

```python
    words = custom.words()
```

and change the four calls:

line 253: `found += [("imports.may", name, _shown(t, words)) for t in custom.rules.get(name, ())`
line 258: `found += [("imports.may.types_only", name, _shown(_into(t, back), words)) for t in base.parts[pairs[name]].imports_types_only`
line 275: `found += [("imports.must", name, _shown(t, words)) for t in now if before and _into(t, pairs) not in before]`
line 295: `found += [("imports.also", mine.name, _shown(t, words)) for t in mine.imports_also`

Replace `_shown` (lines 557-562) with:

```python
def _shown(target: Target, words: Mapping[str, str]) -> str:
    """How a target of the custom profile is said: `everything` as the word, any other as a reference (see
    written_target), the word that of the repeating folder its part lies in in the custom profile (words)."""
    return "everything" if target.part == EVERYTHING else written_target(target, words)
```

(A target of the `types_only` line is renamed into the custom names by `_into(t, back)`, and is shown only when a custom allow of the same part and scope covers it, so an own-scope one lies in a repeating folder of the custom profile and has a word in `words`.)

In `xarch/modules/spec/domain/published.py`, line 110 becomes:

```python
        imports.may     part may also import what (a target as a reference: parts.<part> or <word>.<part>)
```

and line 122 becomes:

```python
        imports.also    the tests of tier part may also import what (a target as a reference: parts.<part> or <word>.<part>)
```

(keep each within 140 characters; check with `uv run ruff check`).

- [ ] **Step 6: Run the tests of Steps 1 and 3 to see them pass**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py -q`
Expected: PASS.

- [ ] **Step 7: Run the spec module**

Run: `timeout 600 uv run pytest tests/modules/spec -q`
Expected: PASS. A failure that asserts an old spelling written by `_shown` is updated to the new spelling with its meaning unchanged; anything else is a defect to report. `tests/modules/spec/adapters/test_yaml_profile_format.py:71-75` and `tests/modules/rules/application/test_profile_check.py:52` build their values by hand and must not change.

- [ ] **Step 8: Gates for this task**

Run: `uv run ruff check` — Expected: `All checks passed!`
Run: `uv run xarch check --strict` — Expected: exit 0, no finding (no `pass-through`: `_shown` keeps its own `everything` branch, and logic is not a pass-through part).

- [ ] **Step 9: Read `profile check architecture.yaml` against Step 0**

Run: `uv run xarch profile check architecture.yaml > /tmp/xarch-82-pc-after.txt 2>&1; echo $?; diff /tmp/xarch-82-pc-before.txt /tmp/xarch-82-pc-after.txt`
Expected: exit `0`, and the diff shows exactly these 13 lines respelled, nothing else, same count and order:

```
<     domain may also import profile-values (parts.domain.imports.may)
>     domain may also import parts.profile-values (parts.domain.imports.may)
(and the same for logic, ports, services, controller, adapters, contract, kernel-logic)
<     cli may also import reports (parts.cli.imports.may)
>     cli may also import parts.reports (parts.cli.imports.may)
<     the integration tests may also import domain/values (tiers.integration.imports.also)
>     the integration tests may also import module.domain/values (tiers.integration.imports.also)
(and the same for domain/profile, domain/parsed, domain/outcomes)
```

The library lines (`ast`, `tokenize`, `yaml`), `guards.dead-code.known` and `guards.no-twins.translated` lines do not move. Any other difference is a defect to report.

- [ ] **Step 10: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py xarch/modules/spec/domain/published.py \
  tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py \
  tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py
git commit -m "The looser lines of profile check and check say a target as parts.<part> or <word>.<part>, the word that of the part's folder in the custom profile; everything stays the word

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: README and CHANGELOG say it, the golden docs do not move, the full gates

**Files:**
- Modify: `README.md:232-233`
- Modify: `CHANGELOG.md` (end of `## [Unreleased]` → `### Changed`, after the `testing.mocks.specs` bullet that ends at line 359, before the blank line and `## [0.2.0] - 2026-11-18` at line 361)
- Test: `tests/architecture/test_readme.py`, `tests/bootstrap/test_docs_templates.py` (run, not edited)

**Interfaces:**
- Consumes: the behavior of Tasks 1 and 2.
- Produces: nothing code depends on.

- [ ] **Step 1: README — one sentence in the symbols bullet**

In `README.md`, the last two lines of the `imports.may` bullet (lines 232-233):

```
  such as `module.store`, the part in the importer's own instance of the `<word>` folder, each optionally followed by
  `/<path>` and `:<pattern>`; the forms above stay the bundled spelling.
```

become:

```
  such as `module.store`, the part in the importer's own instance of the `<word>` folder, each optionally followed by
  `/<path>` and `:<pattern>`; the forms above stay the bundled spelling. `profile explain --rule` and the looser lines
  of `profile check` and `check` write a target as a reference, `parts.<part>` or `<word>.<part>`.
```

No other README line moves.

- [ ] **Step 2: CHANGELOG — one entry under `### Changed`**

Insert, as the last bullet of the `### Changed` section of `## [Unreleased]` (directly after the line `  language's \`writing.specs\` does not write is refused at its index.`):

```
- `profile explain <key> --rule` and the example of `profile explain <word>` write a check's `place` as a reference,
  and the looser lines of `profile check` and `check` (and their JSON `what` and `sentence`) write a target so:
  `parts.<part>` for a part in every instance of its repeating folder or in none, `<word>.<part>` for the importer's
  own instance, the word that of the folder the part lies in, then `/<path>` and `:<pattern>` as before (`domain may
  also import parts.platform`, `targets: [{place: [parts.platform, parts.contract]}, outside]`). `everything` is
  still written `everything`, and the JSON's shape does not change.
```

- [ ] **Step 3: Run the README and golden-docs tests**

Run: `timeout 600 uv run pytest tests/architecture/test_readme.py tests/bootstrap/test_docs_templates.py -q`
Expected: PASS. `test_docs_templates.py` regenerates `docs/{cli,web,xarch}/` from the bundled and xarch's own architecture and compares byte for byte (the docs path commit ddea9db used); a pass means no golden doc moved, as the spec expects (the docs phrase prints paths). A failure there is a defect to report: never regenerate past it, never edit a golden doc by hand. Confirm also: `git status --short docs/` prints nothing.

- [ ] **Step 4: Full gates**

Run each, in order, and read each:
- `uv run ruff check` — Expected: `All checks passed!`
- `uv run xarch check` — Expected: exit 0.
- `uv run xarch check --strict` — Expected: exit 0.
- `uv run xarch profile check architecture.yaml` — Expected: exit 0, its output equal to `/tmp/xarch-82-pc-after.txt` of Task 2 Step 9.
- `timeout 1200 uv run pytest -q > /tmp/xarch-82-pytest.txt 2>&1` run in the background (over two minutes); when it ends, `tail -5 /tmp/xarch-82-pytest.txt` — Expected: all passed, no failure, no error.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say profile explain --rule and the looser lines write a target as parts.<part> or <word>.<part>; the golden docs do not move

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review against the spec

- B1 `_place` writes the new form, every row of its table: Task 1 Step 1 (T1 rows 1-5 for `module.domain`, `parts.domain/values`, `parts.kernel:*Id`, `parts.domain`; T2 for `unit.store/sql:Sql*`; T4 for `parts.api/v1` with `{}`). `ValueError` with the spec's text: T3, implemented in `written_target`. `check_of`/`written` keyword-only required `words`, `written_own` passes `{}`: Task 1 Step 6. Callers `rule()` and `_example()`: Step 7. Wired `--rule` for cli, web, architecture.yaml: T13 (Step 3). `profile explain targets.place`: T15 (Step 3). No other `--rule` output moves: T14 (Steps 0, 9, 10).
- B2 `_shown`: Task 2 Step 5, `everything` kept, word from `custom.words()`; every call of `_looser` (lines 253, 258, 275, 295) passes `words`. Examples table rows: T5, T6, T7 (Step 1), the `imports.must` row via T10 (Step 3). `types_only` line: T8. Renamed-in-place: T8b. Second word: T9. Wired: T11, T12 (Step 3). `profile check architecture.yaml`: Step 9.
- Design choice: one shared writer `written_target` in `xarch/kernel/logic/targets.py`; `_place` dropped (no forwarding wrapper); `_shown` keeps its `everything` branch. Both modules' logic may import `kernel-logic` (architecture.yaml lines 37, 55). `--strict` gate in Tasks 1, 2, 3.
- Docs: README (Task 3 Step 1), CHANGELOG (Step 2), golden docs read through `test_docs_templates.py` (Step 3). The `Loosened` docstring in `published.py` said "a target as written", which this change makes untrue; it is respelled in Task 2 Step 5 (it describes the writer's output, not the profile format, so it is not one of the 8.3 docstrings).
- Out of scope respected: no profile, no parser, no refusal; `test_yaml_profile_format.py:71-75` and `rules/application/test_profile_check.py:52` untouched; corpora untouched.
- Placeholder scan: none. The new digest `cb8bbbfa024c046c` was computed from today's text with the one line respelled; Step 10 says what to do if the run prints another.
- Types: `written_target(made: Target, words: Mapping[str, str]) -> str` is the same name and signature in Task 1 Step 5, Task 1 Step 6, Task 2 Step 5. `check_of(..., *, words=...)` and `written(..., *, words=...)` match every test call.
- Review Focus: each of the five has a test named in its line.
<!-- task-pipeline: validated -->
