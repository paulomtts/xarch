# 6.9 spec: `testing.preset` combines a bundled framework with project settings

Card: ca108f5f-81d9-46fb-b73f-c3f717f89f6b (subtask of 15e55316), release step 21 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3, row 21 at line 284), split with 6.8, 6.10 and 6.11. Blocked by 6.8
(e3450e17), which is on this branch (HEAD eeb3d11).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note").
This card implements ruling R3 (note lines 25-26), the `preset` paragraph of 2.5 (lines 370-374) and the two `preset`
bullets of 2.8 (lines 433-435). From `0.3.0-cohesion-review-3.md` ("review 3"): C3 (lines 110-117), gap G4 (lines
415-417), overlap O22 (line 246), and O4, O5, O8, O9 (lines 228-233) for docs.

## Goal

`testing` may be written as a map that names its preset: `testing: {preset: pytest}`. The framework then comes wholly
from the preset. A framework key written beside `preset` is refused, never merged. `testing: pytest` stays the short
form and means exactly `{preset: pytest}`. A map without `preset` is the whole framework, as today. The map exists so
that 6.10 can add `beside` next to `preset`; this card adds no other setting.

## What is already done (not to be redone)

- `testing` as a preset name or a whole framework map: `_testing` in
  `xarch/modules/spec/application/logic/profile_parsing.py` (around line 529). The str branch looks the name up in
  `presets` and validates the preset's map the same way as one written in the file.
- Today's unknown-preset text: `testing: no preset 'x': use pytest, or write the map {files, declared}` (`_PRESET_MAP`,
  line 143), or `... write the map {files, declared}` when no preset ships.
- `_Testing.preset` and `_framework_named` already name the framework as `` `pytest` `` when a preset was used.
- The needs walker (`profile_needs._configured`) walks a str `testing` as the preset's map, at address `testing.`.
- `Explanation.choices` lists the presets for a key with `choices=CHOICE_PRESETS`, and `explain.py` writes `<preset>`
  for that choice in an example.
- Unknown keys of `testing` are listed by `ck.unknown_keys` from `names_of(TESTING)`, with the retired-keys table
  (`testing.functions`, 6.8).

## Inherited constraints

- R3 (note 25-26, 2.5 lines 372-374): with `preset`, every framework key comes from the preset, and writing one of them
  beside it is refused. Without `preset`, the map is the whole framework. `testing: pytest` is the short form of
  `{preset: pytest}`.
- No override rule (card dodge; review 3 G4, lines 415-417): a framework key beside `preset` never wins over the
  preset and is never merged into it. There is one source for each key. A project with its own `files` pattern writes
  the whole map.
- Refusal text for a framework key beside `preset` (note 2.8 line 433):
  `testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`.
- `testing.preset` naming no preset keeps today's text (note 2.8 line 435): `no preset 'x': use pytest, or write the
  map {files, declared}`.
- The "use ..." list of `testing` is rewritten (review 3 O22, line 246): the unknown-keys list of an inline map gains
  `preset`.
- The bundled profiles (`cli.yaml`, `web.yaml`) and `architecture.yaml` keep writing `testing: pytest` (note line 27-29,
  owner clarification). The recorded corpora (`tests/bootstrap/corpora/`) do not change.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by hand. Expected
  diff: none, because no bundled profile changes (review 3 O8, line 232).
- README and CHANGELOG lines go under `[Unreleased]` (review 3 O4, O5, lines 228-229). The parser docstring
  (`profile_parsing.py:7-58`) is updated for this step's key (O9, line 233).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; Python only in the reader adapter and the data files under `xarch/architectures/presets/`;
  `.claude/` stays out of commits; nothing is pushed.

## Behavior

### B1. The forms of `testing`

| Written | Means |
|---|---|
| `testing: pytest` | the preset `pytest` (unchanged) |
| `testing: {preset: pytest}` | the same: same `Framework`, same mocks, `_Testing.preset == "pytest"` |
| `testing: {files: [...], declared: [...], ...}` | the whole framework, as today, `_Testing.preset == ""` |

A profile written either way loads to an equal `Architecture`. Every message that names the framework (for example
`tiers.<t>.plain_tables: needs a table form: the framework `pytest` ...`) is the same for both forms.

### B2. The key `testing.preset`

- `testing.preset` is a key of the `testing` scope: not required, not enforced on its own, `choices=CHOICE_PRESETS`.
  It feeds the same rules as `testing` (`tiers`, `test-tree`), since it is the whole framework.
- `files` and `declared` stay required when `preset` is absent. When `preset` is present, they are not asked for.
  `profile explain testing.files` still says required. Its `accepts` text names the exception (see B5).
- Inside a preset's own document (`xarch/architectures/presets/testing/*.yaml`, or a test's `presets` map), `preset`
  is refused, so presets do not chain: `testing.preset: the preset old names a preset: a preset writes the whole
  framework`. The "use ..." list of every `testing` (inline map, map with `preset`, preset document) is the same one,
  `names_of(TESTING)`, and so it gains `preset` everywhere. The tests that share one expected text between an inline
  map and a preset stay shared.

### B3. Refusals, in the order they are reported

Each problem is prefixed with the file, as all profile problems are (`layered.yaml: ...`). Problems from one `testing`
are reported in this order: unknown keys (with any retired-keys entry first, as today), then the `preset` problem,
then one problem per framework key beside `preset`, in key-table order (`files, declared, globals, skips, tables,
mocks`).

1. Unknown key in a map that has `preset` or not:
   `testing: unknown key 'colour': use declared, files, globals, mocks, preset, skips, tables`.
   A retired `functions` beside `preset` gets the retired text, whose "use ..." list also gains `preset`.
2. `preset` names no preset:
   `testing.preset: no preset 'rspec': use pytest, or write the map {files, declared}`. With no preset shipped:
   `testing.preset: no preset 'rspec': write the map {files, declared}`. Only the address changes from today's text
   (`testing` becomes `testing.preset`). The rest is today's text.
3. `preset` is not a string (a number, a list, a map, `true`, `null`):
   `testing.preset: must be a preset name: use pytest, or write the map {files, declared}`, with the same no-preset
   variant as 2.
4. A framework key the preset holds, written beside `preset`:
   `testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`.
   The same text for `declared`, `skips`, `tables`, `mocks`, and for `globals` when the preset holds it. The value
   written is never parsed, so a broken value beside `preset` gives this problem and no other.
5. A framework key the preset does not hold, written beside `preset` (pytest has no `globals`):
   `testing.globals: the preset pytest writes no globals: drop it, or drop preset and write the whole map`.
   It is refused anyway, because the map names its framework in one place.
6. When `preset` is refused (2 or 3), keys written beside it are refused with the plain text, without naming a
   preset: `testing.files: written beside preset: drop it, or drop preset and write the whole map`. Problems 2 and 3
   come first.

Any problem in `testing` gives no framework, as today, and the profile is refused with `InvalidArchitecture`.

The non-map, non-string message (`testing: must be a preset name or a mapping {files, declared}: ...`) does not
change. `_PRESET_MAP` stays `{files, declared}` because the unknown-preset text must not change.

### B4. Needs

`profile_needs._configured` walks `testing: {preset: <name>}` as the preset's map at address `testing.`, the same way
as `testing: <name>`. When `<name>` is a known preset, keys written beside `preset` are not walked. They are refused by
B3.4/5 and give no needs refusal of their own. With `preset` naming no preset, or not a string, nothing under
`testing` is walked, as for an unknown str today. A map without `preset` is walked as today.

### B5. Texts, docs, explain

- `xarch/architectures/presets/format/keys.yaml`:
  - `testing.accepts` becomes: a preset name, a map `{preset}` naming one, or a map
    `{files, declared, globals, skips, tables, mocks}`. The rest of the text is kept.
  - A new entry `testing.preset`, meaning "the preset the framework is read from". Its accepts text says: the name of
    a preset xarch ships; every framework key then comes from it, and one written beside it is refused;
    `testing: <preset>` is the short form. Example: `testing: {preset: <preset>}`.
  - `testing.files` and `testing.declared` accepts: required unless `preset` is written.
- `profile explain testing.preset` prints the entry, lists the presets as choices (`pytest`), and its example loads.
  The existing explain coverage tests (every key has a `keys.yaml` entry, every example loads) stay green.
- Parser docstring (`profile_parsing.py:11-13`): `testing: <preset> | {preset} | {files, declared, globals, skips,
  tables, mocks}`.
- README profile block (line 116): `testing:  <preset> | {preset} | {files*, declared*, globals, skips, tables,
  mocks}`. Add one sentence near the `testing.declared` text (around line 181) saying that `testing: {preset: pytest}`
  names a preset as a map, a framework key beside it is refused, and `testing: pytest` is its short form.
- CHANGELOG `[Unreleased]` / `Added`: one line for `testing.preset`, with the refusal text.
- Golden docs: regenerate `docs/{cli,web,xarch}/testing.md` with the repository's usual generator, read the diff, and
  expect it to be empty.

## Out of scope

- `testing.beside`, its refusal, and the R4 tier `folder` rule: card 6.10.
- Whatever 6.11 covers (the rest of release step 21's split).
- Any override or merge of framework keys beside `preset` (G4 dodge).
- New presets (Jest, Vitest, %UnitTest): no preset beyond `pytest` ships.
- Changing `testing: pytest` in the bundled profiles, `architecture.yaml`, `stress.yaml`, or the corpora.
- The non-map message and `_PRESET_MAP` text.

## Tests that prove it (written first)

Tiers as the repository uses them: unit tests of pure logic under `tests/modules/<module>/...`, mirroring the code;
bootstrap tests under `tests/bootstrap/` run the wired app on files in `tmp_path`; architecture tests under
`tests/architecture/` guard the repository itself.

### Unit, spec: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`

Unit tier: `_testing` is pure logic over a document and `presets`, and every other `testing` parsing test is here.

1. `testing: {preset: pytest}` parses to the same `Framework` and mocks as `testing: pytest`, and the parsed
   architectures are equal. Use `PRESETS` and `covered(...)` from the file.
2. The `plain_tables` problem names `` `pytest` `` under `{preset: pytest}`, as under `pytest`. This proves that
   `_Testing.preset` is set.
3. Refusals, one `pytest.param` each, with the exact B3 text:
   - `{preset: rspec}` with `PRESETS`
   - `{preset: rspec}` with `{}`
   - `{preset: 3}`, `{preset: [pytest]}`, `{preset: null}`
   - `{preset: pytest, files: [...]}`
   - `{preset: pytest, declared: [...]}`
   - `{preset: pytest, mocks: {...}}`
   - `{preset: pytest, files: "broken"}`: only the beside problem
   - `{preset: pytest, globals: [x]}`: the "writes no" text
   - `{preset: pytest, files: [...], declared: [...]}`: two problems in key order
   - `{preset: rspec, files: [...]}`: the preset problem, then the plain beside text
   - `{preset: pytest, colour: 1}`: the unknown-key text with `preset` in the list
4. The existing unknown-key params (line 58 and any like it) expect `use declared, files, globals, mocks, preset,
   skips, tables`.
5. A preset document holding `preset` (`"old"` with `{"old": {preset: pytest, files: [...], declared: [...]}}`) gives
   exactly the B2 text and no other problem.
6. `{files, declared}` without `preset` still loads, and still says `missing files` / `missing declared` when one is
   left out (the existing params stay as they are).

### Unit, spec: `tests/modules/spec/application/logic/test_retired_keys.py`

Unit tier: the retired-keys texts are tested here.

7. The `testing` "use ..." lists in this file (lines 404, 476, 488, 494) gain `preset`. This includes the "in a
   preset" params, which keep sharing their text with the inline ones.
8. `testing: {preset: pytest, functions: "test_*"}` gives the retired `functions` text, and no other problem for it.

### Unit, spec: `tests/modules/spec/application/logic/test_profile_needs.py`

Unit tier: needs are pure logic over the key table and a language's supplies.

9. `testing: {preset: pytest}` is walked as the preset: the same `(address, fact)` list as the existing
   `test_a_testing_that_names_a_preset_is_walked_as_the_preset` (line 286).
10. `{preset: pytest, skips: [x]}` with an empty preset `{"pytest": {}}`: the key beside `preset` is not walked, so
    the result is `[]`.
11. `{preset: nosuch}`, `{preset: 3}`: nothing is walked, so the result is `[]`. Add these to the parametrized test at
    line 281.
12. `tests/bootstrap/test_needs_agree.py` stays green unchanged. `preset` has no needs.

### Unit, spec: `tests/modules/spec/domain/test_profile_keys.py` (or the key-table test that exists)

Unit tier: the key table is domain data.

13. The `testing` scope holds `preset`, which is not required and has `choices == CHOICE_PRESETS`. `files` and
    `declared` stay required.

### Bootstrap

Bootstrap tier: these run the wired loader or CLI on a real file, which no unit test reaches.

14. `tests/bootstrap/test_profile_file.py`: the small profile with `testing: pytest` replaced by `testing: {preset:
    pytest}` loads and checks the same as the original.
15. `tests/bootstrap/test_profile_file.py`: with `testing: {preset: pytest, files: [check_*.py]}`, `load_architecture`
    raises with exactly `<file>: testing.files: the preset pytest gives files: drop it, or drop preset and write the
    whole map`. This proves B3.4 end to end against the shipped `pytest.yaml`.
16. `tests/bootstrap/test_profile_file.py`: `testing: {preset: rspec}` gives `<file>: testing.preset: no preset
    'rspec': use pytest, or write the map {files, declared}`. The existing `testing: rspec` test (line 96) keeps
    today's text at `testing:`.
17. `tests/bootstrap/test_profile_explain.py`: `profile explain testing.preset` prints its meaning and lists `pytest`
    as a choice. The existing "every key can be asked for" and example-loads tests cover the new entry.

### Gates

`uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check
architecture.yaml`, then `uv run pytest -q`. The full suite takes over two minutes, so run it in the background and
read it at the end. All must pass on this branch alone. Regenerate the golden docs and read the diff, which should be
empty.

## Notes for the planner

- Add `Key(TESTING, "preset", choices=CHOICE_PRESETS, rules=("tiers", "test-tree"))` to `key_table.py`, placed first
  in the `TESTING` block so that explain lists it first. Check that the key order in the "use ..." list is sorted
  (`unknown_of` sorts), so placement does not change any text.
- `_testing` in `profile_parsing.py` gains the map-with-`preset` branch. Keep the str branch and the whole-map branch
  as they are, and keep `known = names_of(TESTING)` for both. The `preset` branch validates its own keys: first
  unknown keys through `ck.unknown_keys(value, names_of(TESTING), "testing", TESTING)`, then the `preset` value, then
  the beside refusals. Only after that does it hand `presets[name]` to the existing preset path, and that path refuses
  a preset document holding `preset` (B2) before it calls `framework_patterns`. Do not pass the inline map to
  `framework_patterns`, or it will ask for `files` / `declared`.
- `profile_needs._configured`: extend the `scope == PROFILE and key.name == "testing"` case so that a `Mapping`
  holding a str `preset` is replaced by `presets.get(value["preset"])`.
- Existing tests that quote the "use ..." list of `testing` (`test_profile_parsing_tests.py:58`,
  `test_retired_keys.py:404, 476, 488, 494`, `tests/bootstrap/test_profile_file.py:151, 169`) are updated in the same
  task that adds the key. Grep `use declared, files, globals` to find any others.
