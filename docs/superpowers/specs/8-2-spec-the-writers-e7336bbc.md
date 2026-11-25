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
