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

---

# 6.9 spec: `testing.preset` combines a bundled framework with project settings, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `testing` may be written as `{preset: <name>}`, which means exactly `testing: <name>`, and every framework key
written beside `preset` is refused, never merged.

**Architecture:** One new key, `Key(TESTING, "preset", ...)`, placed first in the `TESTING` block of the key table, with
its `keys.yaml` text. `_testing` in `profile_parsing.py` gains a branch for a map holding `preset`. That branch checks
the map's own keys (unknown keys, then the `preset` value, then each framework key beside it) and only then hands the
preset's document to the existing preset path, which now refuses a preset document that itself holds `preset`. The
needs walker (`profile_needs._configured`) walks `{preset: <name>}` as the preset's map, the same way it walks
`testing: <name>`.

**Tech Stack:** Python 3, pytest, PyYAML data files, `uv` for every command.

**Spec:** `docs/superpowers/specs/6-9-spec-testing-preset-ca108f5f.md` (copied in full above).

## Global Constraints

- No comments in xarch's code (`xarch/`). Docstrings are fine. Test files follow the same rule.
- Never run `ruff --fix`. Run `uv run ruff check` and fix by hand. `ruff.toml` allows 140 columns; wrap code, docstrings
  and YAML text near 120, as the files around them are.
- Tests are written first, and each one is run and seen to fail before the code that makes it pass.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`. This card touches no reader.
- The bundled profiles (`xarch/architectures/cli.yaml`, `web.yaml`), `architecture.yaml`, `tests/bootstrap/corpora/`
  and `stress.yaml` keep `testing: pytest` and do not change.
- `_PRESET_MAP` stays `"{files, declared}"`. The non-map, non-string text
  (`testing: must be a preset name or a mapping {files, declared}: ...`) does not change.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never edited by hand. Expected diff: none.
- README and CHANGELOG lines go under `[Unreleased]`.
- `.claude/` stays out of commits. Nothing is pushed.
- Exact refusal texts (copy verbatim):
  - `testing.preset: no preset 'rspec': use pytest, or write the map {files, declared}` (with no preset shipped:
    `testing.preset: no preset 'rspec': write the map {files, declared}`)
  - `testing.preset: must be a preset name: use pytest, or write the map {files, declared}` (no-preset variant:
    `testing.preset: must be a preset name: write the map {files, declared}`)
  - `testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`
  - `testing.globals: the preset pytest writes no globals: drop it, or drop preset and write the whole map`
  - `testing.files: written beside preset: drop it, or drop preset and write the whole map`
  - `testing.preset: the preset old names a preset: a preset writes the whole framework`
  - `testing: unknown key 'colour': use declared, files, globals, mocks, preset, skips, tables`

## Review Focus

1. A `preset` value that cannot be looked up in a dict (a list `[pytest]`, a map `{name: pytest}`): it must give the
   "must be a preset name" text, never a `TypeError: unhashable type`. Pinned in Task 1, Step 1 (params `a list`,
   `a map`).
2. `preset: ""` (an empty name): it is a string, so it gets the "no preset ''" text, not "must be a preset name".
   Pinned in Task 1, Step 1 (param `an empty name`).
3. A framework key beside `preset` written as `null` (`skips:` with no value): the key is still written, so it is
   refused like any other key beside `preset`. Pinned in Task 1, Step 1 (param `a key beside it written null`).
4. All three kinds of problem at once (`{files: [...], preset: 3, colour: 1}`): unknown key first, then the `preset`
   problem, then the plain beside text, whatever order the map was written in. Pinned in Task 1, Step 1 (param
   `every problem, in order`), and dict order is reversed against table order in param `two keys beside it, in the
   order of the table`.
5. The guards that read the framework (stand-ins reads `mocks`, scenario-coverage reads the tables) under the map form:
   the profile must load to the same `Architecture` as under `testing: pytest`. Pinned in Task 1, Step 1 (bootstrap
   test `test_the_guards_that_read_tests_read_the_same_under_a_map_naming_the_preset`).

## File Structure

- `xarch/modules/spec/domain/key_table.py`: gains the key `testing.preset`.
- `xarch/architectures/presets/format/keys.yaml`: the text of `testing.preset`, and the `accepts` of `testing`,
  `testing.files`, `testing.declared`.
- `xarch/modules/spec/application/logic/profile_parsing.py`: `_testing` gains the `preset` branch; new helpers
  `_instead`, `_preset_of`, `_beside`; module docstring line for `testing`; `_Testing` docstring.
- `xarch/modules/spec/application/logic/profile_needs.py`: `_configured` walks `{preset}` as the preset; new helper
  `_framework`.
- Tests: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, `.../test_retired_keys.py`,
  `.../test_profile_needs.py`, `tests/modules/spec/application/test_explain.py`,
  `tests/modules/spec/domain/test_profile_keys.py`, `tests/bootstrap/test_profile_file.py`,
  `tests/bootstrap/test_profile_explain.py`.
- Docs: `README.md`, `CHANGELOG.md`; golden docs regenerated (expected unchanged).

Why three tasks: the key and its parsing must land together, because the catalogue test refuses a key with no
`keys.yaml` text, and the "every example loads" test refuses a `testing.preset` example the parser cannot load. The
needs walk is a separate module with its own tests. Docs and gates come last.

---

### Task 1: `testing.preset`, its key text, and its parsing

**Files:**
- Modify: `xarch/modules/spec/domain/key_table.py:139` (the first line of the `TESTING` block)
- Modify: `xarch/architectures/presets/format/keys.yaml:143-152` (`testing`), `:784-796` (`testing.files`,
  `testing.declared`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:11-13` (docstring), `:148-151` (`_Testing`),
  `:529-553` (`_testing`, `_framework_named`)
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`
- Test: `tests/modules/spec/application/logic/test_retired_keys.py`
- Test: `tests/modules/spec/domain/test_profile_keys.py`
- Test: `tests/modules/spec/application/test_explain.py`
- Test: `tests/bootstrap/test_profile_file.py`
- Test: `tests/bootstrap/test_profile_explain.py`

**Interfaces:**
- Consumes: `ck.unknown_keys(spec, known, where, scope) -> list[str]` (`profile_checks.py:733`),
  `keys_of(scope) -> tuple[Key, ...]` and `names_of(scope) -> set[str]` (`key_lookup.py`, both already imported in
  `profile_parsing.py:88`), `CHOICE_PRESETS` (already imported in `key_table.py:11`).
- Produces: `Key(TESTING, "preset", rules=("tiers", "test-tree"), choices=CHOICE_PRESETS)` in `KEYS`, so
  `names_of(TESTING) == {"preset", "files", "declared", "globals", "skips", "tables", "mocks"}`. In
  `profile_parsing.py`: `_instead(presets: Mapping[str, Any]) -> str`,
  `_preset_of(value: Mapping[Any, Any], presets: Mapping[str, Any], problems: list[str]) -> str`,
  `_beside(key: str, preset: str, presets: Mapping[str, Any]) -> str`. Task 2 relies only on the key existing.

- [ ] **Step 1: Write the failing tests**

1a. In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, change the expected text of the param
`an unknown key` (line 58) so the "use" list holds `preset`:

```python
    pytest.param({"files": ["test_*.py"], "declared": BY_NAME, "colour": 1}, PRESETS,
                 ["layered.yaml: testing: unknown key 'colour': use declared, files, globals, mocks, preset, skips, "
                  "tables"],
                 id="an unknown key"),
```

1b. In the same file, directly after `test_a_bad_testing_key_is_refused` (ends at line 70), add:

```python
def test_a_map_that_names_a_preset_is_the_preset_by_name():
    named, mapped = parsed(covered(testing="pytest")), parsed(covered(testing={"preset": "pytest"}))
    assert mapped.framework == named.framework
    assert mapped == named


BESIDE = "drop it, or drop preset and write the whole map"
NO_RSPEC = "layered.yaml: testing.preset: no preset 'rspec': use pytest, or write the map {files, declared}"
NOT_A_NAME = "layered.yaml: testing.preset: must be a preset name: use pytest, or write the map {files, declared}"
UNKNOWN_COLOUR = "layered.yaml: testing: unknown key 'colour': use declared, files, globals, mocks, preset, skips, tables"
CHECK_FILES = ["check_*.py"]


@pytest.mark.parametrize("testing, presets, expected", [
    pytest.param({"preset": "rspec"}, PRESETS, [NO_RSPEC], id="a preset that does not exist"),
    pytest.param({"preset": "rspec"}, {}, ["layered.yaml: testing.preset: no preset 'rspec': write the map "
                                           "{files, declared}"], id="no preset at all"),
    pytest.param({"preset": ""}, PRESETS, ["layered.yaml: testing.preset: no preset '': use pytest, or write the map "
                                           "{files, declared}"], id="an empty name"),
    pytest.param({"preset": 3}, PRESETS, [NOT_A_NAME], id="a number"),
    pytest.param({"preset": ["pytest"]}, PRESETS, [NOT_A_NAME], id="a list"),
    pytest.param({"preset": {"name": "pytest"}}, PRESETS, [NOT_A_NAME], id="a map"),
    pytest.param({"preset": True}, PRESETS, [NOT_A_NAME], id="true"),
    pytest.param({"preset": None}, PRESETS, [NOT_A_NAME], id="null"),
    pytest.param({"preset": 3}, {}, ["layered.yaml: testing.preset: must be a preset name: write the map "
                                     "{files, declared}"], id="no name, and no preset at all"),
    pytest.param({"preset": "pytest", "files": CHECK_FILES}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}"], id="files beside it"),
    pytest.param({"preset": "pytest", "declared": [{"function": "check_*"}]}, PRESETS,
                 [f"layered.yaml: testing.declared: the preset pytest gives declared: {BESIDE}"],
                 id="declared beside it"),
    pytest.param({"preset": "pytest", "mocks": {"calls": ["unittest.mock.Mock"], "spec_keywords": ["spec"]}}, PRESETS,
                 [f"layered.yaml: testing.mocks: the preset pytest gives mocks: {BESIDE}"], id="mocks beside it"),
    pytest.param({"preset": "pytest", "skips": None}, PRESETS,
                 [f"layered.yaml: testing.skips: the preset pytest gives skips: {BESIDE}"],
                 id="a key beside it written null"),
    pytest.param({"preset": "pytest", "files": "broken"}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}"],
                 id="a broken value beside it is not parsed"),
    pytest.param({"preset": "pytest", "globals": ["x"]}, PRESETS,
                 [f"layered.yaml: testing.globals: the preset pytest writes no globals: {BESIDE}"],
                 id="a key the preset does not hold"),
    pytest.param({"preset": "pytest", "declared": BY_NAME, "files": CHECK_FILES}, PRESETS,
                 [f"layered.yaml: testing.files: the preset pytest gives files: {BESIDE}",
                  f"layered.yaml: testing.declared: the preset pytest gives declared: {BESIDE}"],
                 id="two keys beside it, in the order of the table"),
    pytest.param({"preset": "rspec", "files": CHECK_FILES}, PRESETS,
                 [NO_RSPEC, f"layered.yaml: testing.files: written beside preset: {BESIDE}"],
                 id="a key beside a preset that does not exist"),
    pytest.param({"preset": "pytest", "colour": 1}, PRESETS, [UNKNOWN_COLOUR], id="an unknown key beside it"),
    pytest.param({"files": CHECK_FILES, "preset": 3, "colour": 1}, PRESETS,
                 [UNKNOWN_COLOUR, NOT_A_NAME, f"layered.yaml: testing.files: written beside preset: {BESIDE}"],
                 id="every problem, in order"),
])
def test_a_map_that_names_a_preset_holds_nothing_else(testing, presets, expected):
    assert problems(covered(testing=testing), presets=presets) == expected


def test_a_preset_may_not_name_a_preset_whichever_form_names_it():
    presets = {"old": {"preset": "pytest", "files": ["test_*.py"], "declared": BY_NAME}} | PRESETS
    expected = ["layered.yaml: testing.preset: the preset old names a preset: a preset writes the whole framework"]
    assert problems(covered(testing="old"), presets=presets) == expected
    assert problems(covered(testing={"preset": "old"}), presets=presets) == expected
```

1c. In the same file, directly after `test_a_plain_tier_under_a_preset_that_writes_no_table_form_names_the_preset`
(ends at line 775), add:

```python
def test_a_plain_tier_under_a_map_that_names_a_preset_names_the_preset():
    document = covered(testing={"preset": "pytest"})
    document["tiers"]["unit"]["plain_tables"] = True
    presets = {"pytest": {"files": ["test_*.py"], "declared": BY_NAME}}
    assert problems(document, presets=presets) == [
        "layered.yaml: tiers.unit.plain_tables: needs a table form: the framework `pytest` writes none in "
        "`testing.tables`"]
```

1d. In `tests/modules/spec/application/logic/test_retired_keys.py`, change every
`use declared, files, globals, mocks, skips, tables` to `use declared, files, globals, mocks, preset, skips, tables`
(lines 404, 476, 488, 494), wrapping as shown. Line 404 becomes:

```python
    pytest.param(TESTING, writing(covered(), "testing"),
                 f"testing: unknown key 'banned': {RENAMED}; use declared, files, globals, mocks, preset, skips, "
                 "tables", id="testing, through framework_patterns"),
```

Line 476 becomes:

```python
        f"layered.yaml: testing: unknown key 'table': {TABLE_MOVED}; use declared, files, globals, mocks, preset, "
        "skips, tables"]
```

Lines 488 and 494 become `"use declared, files, globals, mocks, preset, skips, tables"]` and
`"use declared, files, globals, mocks, preset, skips, tables",`. Then, at the end of the file (after
`test_functions_written_in_place_of_declared_is_refused_with_its_hint_and_declared_is_missing`), add:

```python
def test_functions_beside_a_preset_is_refused_with_its_hint_alone():
    assert problems(layered(testing={"preset": "pytest", "functions": "test_*"})) == [
        "layered.yaml: testing: unknown key 'functions': moved in 0.3.0: write declared: [{function: \"<pattern>\"}]; "
        "use declared, files, globals, mocks, preset, skips, tables"]
```

1e. In `tests/modules/spec/domain/test_profile_keys.py`, add `CHOICE_PRESETS,` to the import from
`xarch.modules.spec.domain.profile_keys` (alphabetical: first line inside the parentheses, before `DECLARED,`).
Change the assertion at lines 192-193 to:

```python
    assert [key.name for key in KEYS if key.scope == TESTING] == ["preset", "files", "declared", "globals", "skips",
                                                                  "tables", "mocks"]
```

and add after that test (after line 195):

```python
def test_testing_names_its_preset_by_a_key_that_is_not_required_and_offers_the_presets():
    held = {key.name: key for key in KEYS if key.scope == TESTING}
    assert (held["preset"].required, held["preset"].choices, held["preset"].rules) == (
        False, CHOICE_PRESETS, ("tiers", "test-tree"))
    assert (held["files"].required, held["declared"].required) == (True, True)
```

1f. In `tests/modules/spec/application/test_explain.py`, in `SHAPE`, add a line before
`Shown('testing.files', 1, ...)` (line 46):

```python
    Shown('testing.preset', 1, 'the preset the framework is read from', False, True),
```

1g. In `tests/bootstrap/test_profile_file.py`, change `use declared, files, globals, mocks, skips, tables` to
`use declared, files, globals, mocks, preset, skips, tables` at lines 151 and 169. Line 150-151 becomes:

```python
RETIRED_TABLE = ("testing: unknown key 'table': moved in 0.3.0: write tables, a list of forms (xarch profile explain "
                 "testing.tables); use declared, files, globals, mocks, preset, skips, tables")
```

Lines 168-169 become:

```python
    assert (f"    {path}: testing: unknown key 'functions': moved in 0.3.0: write declared: [{{function: \"<pattern>\"}}]; "
            "use declared, files, globals, mocks, preset, skips, tables") in checked.output.splitlines()
```

Then, directly after `test_a_preset_that_does_not_exist_is_refused_listing_the_ones_that_do` (ends at line 100), add:

```python
MAPPED = PROFILE.replace("testing: pytest", "testing: {preset: pytest}")


def test_a_map_naming_the_preset_loads_and_checks_as_the_preset_by_name(tmp_path):
    assert load_architecture(profile_in(tmp_path, MAPPED)) == load_architecture(profile_in(tmp_path))
    assert check(tmp_path, {"core/rules.py": "from app.cli import app\n"}, MAPPED) == [
        "app/core/rules.py:1: core/ may not import cli/ (app.cli.app)"]


def test_the_guards_that_read_tests_read_the_same_under_a_map_naming_the_preset(tmp_path):
    named = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    mapped = PRESET_PROFILE.replace("testing: pytest\n", "testing: {preset: pytest}\n")
    assert load_architecture(profile_in(tmp_path, mapped)) == named


def test_a_key_beside_the_shipped_preset_is_refused_naming_what_the_preset_gives(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, files: [check_*.py]}"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map",)


def test_a_map_naming_a_preset_that_does_not_exist_is_refused_at_its_preset(tmp_path):
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: rspec}")))
    assert caught.value.problems == (
        f"{tmp_path / 'small.yaml'}: testing.preset: no preset 'rspec': use pytest, or write the map {{files, declared}}",)
```

1h. In `tests/bootstrap/test_profile_explain.py`, directly after
`test_the_functions_of_testing_are_answered_from_the_table_of_retired_names` (ends at line 376), add:

```python
def test_the_preset_of_testing_is_explained_and_names_the_presets_xarch_ships():
    result = runner.invoke(app, ["profile", "explain", "testing.preset"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "testing.preset"
    assert "  what: the preset the framework is read from" in lines
    assert "  one of: pytest" in lines
    assert "    testing: {preset: pytest}" in lines
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
timeout 300 uv run pytest -q --no-header tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py \
  tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_file.py \
  tests/bootstrap/test_profile_explain.py 2>&1 | tail -40
```
Expected: FAIL. The "use" lists lack `preset`; `{preset: pytest}` is read as a whole map and gives
`testing: missing `files``; the domain test's `held["preset"]` raises `KeyError`; `SHAPE` lacks `testing.preset`;
`profile explain testing.preset` exits 2 (no such key).

- [ ] **Step 3: Add the key to the table**

In `xarch/modules/spec/domain/key_table.py`, add one line before `Key(TESTING, "files", True, ...)` (line 139):

```python
    Key(TESTING, "preset", rules=("tiers", "test-tree"), choices=CHOICE_PRESETS),
    Key(TESTING, "files", True, rules=("tiers", "test-tree")),
```

- [ ] **Step 4: Add the key's text to `keys.yaml`**

In `xarch/architectures/presets/format/keys.yaml`, replace the `accepts` of `testing` (lines 145-149):

```yaml
    accepts: >-
      a preset name, a map {preset} naming one, or a map {files, declared, globals, skips, tables, mocks}; needed with
      `tiers` and the guards scenario-coverage and stand-ins. Dotted names are what an import binds; what stays
      %language% is `%interface_path%` as the mark of a port, `%package_file%`, the syntax tree, import resolution
      and the standard library's names
```

Replace the `testing.files` entry (lines 784-788) with the new `testing.preset` entry followed by `testing.files`:

```yaml
  testing.preset:
    meaning: the preset the framework is read from
    accepts: >-
      the name of a preset xarch ships: every key of the framework then comes from it, and one written beside it is
      refused; `testing: <preset>` is its short form
    example: "testing: {preset: <preset>}"
  testing.files:
    meaning: patterns of a test file's name
    accepts: a list of %extension% names with `*` for any text; required unless `preset` is written
    example: |
      <<testing>>
```

In `testing.declared`'s `accepts` (lines 791-794), replace its last line so it reads:

```yaml
    accepts: >-
      a non-empty list of forms, each {function: <pattern>}, a function whose name matches the pattern (`*` for any
      text), or {call: [<dotted name>, ...], title, body}, a call whose arguments hold the test's title and its body;
      a test is of the first form it matches, and an entry's problem names it by its index, testing.declared.0.call;
      required unless `preset` is written
```

The catalogue reads the order of `KEYS`, not the file's, but keep `testing.preset` before `testing.files` so the file
reads in table order.

- [ ] **Step 5: Parse the map with `preset`**

In `xarch/modules/spec/application/logic/profile_parsing.py`, replace `_testing` and add three helpers before
`_framework_named` (lines 529-553). The whole block becomes:

```python
def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, named by its name or under
    `preset`, validated the same; a preset's map that names a preset in turn is refused."""
    preset = ""
    if isinstance(value, Mapping) and "preset" in value:
        preset = _preset_of(value, presets, problems)
        if not preset:
            return None
        value = presets[preset]
    elif isinstance(value, str):
        if value not in presets:
            problems.append(f"testing: no preset {value!r}: {_instead(presets)}")
            return None
        preset, value = value, presets[value]
    elif not isinstance(value, Mapping):
        problems.append(f"testing: must be a preset name or a mapping {_PRESET_MAP}: the patterns of a test file's name "
                        "and the forms that declare a test")
        return None
    if preset and isinstance(value, Mapping) and "preset" in value:
        problems.append(f"testing.preset: the preset {preset} names a preset: a preset writes the whole framework")
        return None
    count = len(problems)
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language, TESTING)
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None or tables is None:
        return None
    return _Testing(replace(framework, tables=tables), mocks, preset)


def _instead(presets: Mapping[str, Any]) -> str:
    """What a `testing` that names no preset is told to write: a preset that ships, when one does, or the map."""
    names = f"use {', '.join(sorted(presets))}, or write" if presets else "write"
    return f"{names} the map {_PRESET_MAP}"


def _preset_of(value: Mapping[Any, Any], presets: Mapping[str, Any], problems: list[str]) -> str:
    """The name of the preset a map of `testing` names under `preset`; "" when the map has a problem: a key it does
    not know, a preset that is no name or does not ship, or a key of the framework written beside it, in that order."""
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(TESTING), "testing", TESTING)
    name = value["preset"]
    if not isinstance(name, str):
        problems.append(f"testing.preset: must be a preset name: {_instead(presets)}")
    elif name not in presets:
        problems.append(f"testing.preset: no preset {name!r}: {_instead(presets)}")
    named = name if isinstance(name, str) and name in presets else ""
    problems += [_beside(key.name, named, presets) for key in keys_of(TESTING)
                 if key.name != "preset" and key.name in value]
    return named if len(problems) == count else ""


def _beside(key: str, preset: str, presets: Mapping[str, Any]) -> str:
    """The problem of a key of the framework written beside `preset`, which names the preset given, "" for none."""
    instead = "drop it, or drop preset and write the whole map"
    if not preset:
        return f"testing.{key}: written beside preset: {instead}"
    gives = "gives" if isinstance(presets[preset], Mapping) and key in presets[preset] else "writes no"
    return f"testing.{key}: the preset {preset} {gives} {key}: {instead}"


def _framework_named(testing: _Testing) -> str:
```

(`_framework_named`'s body stays as it is.) The `isinstance(name, str)` test comes before `name in presets`, so a list
or a map as `preset` never reaches a dict lookup.

- [ ] **Step 6: Update the docstrings**

In the module docstring (line 11), change:

```
    testing: <preset> | {files, declared, globals, skips, tables, mocks}
```

to:

```
    testing: <preset> | {preset} | {files, declared, globals, skips, tables, mocks}
```

and in the next two lines, change `a preset is a name, read from data shipped with xarch` to
`a preset is a name, alone or under preset, read from data shipped with xarch`, rewrapping so no line passes 120
columns. The three lines become:

```
    testing: <preset> | {preset} | {files, declared, globals, skips, tables, mocks}
                               how the test framework names things; a preset is a name, alone or under preset, read
                               from data shipped with xarch, and a key of the framework beside it is refused.
                               Required with `tiers` and with the guards scenario-coverage and stand-ins
```

In `_Testing`'s docstring (lines 149-150), change `"" when written as a map` to `"" when the whole framework is written
out`:

```python
    """What `testing` says: how test files are named and tests declared and the table forms the framework writes, and,
    when written, how a mock is built; preset: the name of the preset it names, "" when the whole framework is written
    out."""
```

- [ ] **Step 7: Run the tests to verify they pass**

Run:
```bash
timeout 300 uv run pytest -q --no-header tests/modules/spec tests/bootstrap/test_profile_file.py \
  tests/bootstrap/test_profile_explain.py tests/bootstrap/test_needs_agree.py 2>&1 | tail -5
```
Expected: PASS, no failures. `tests/modules/spec/application/logic/test_profile_keys.py` covers the new entry too:
its example loads (`test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs[testing.preset]`)
and the loader's unknown-key list for `testing` matches the table
(`test_the_keys_the_loader_names_in_its_unknown_key_message_are_the_keys_of_the_table[testing]`, which now builds
its document from `testing.preset`'s example since that key is first in the scope).

Then run `uv run ruff check` and expect `All checks passed!`. Also run
`grep -rn "use declared, files, globals, mocks, skips" tests xarch README.md CHANGELOG.md` and expect no output.

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/spec/domain/key_table.py xarch/architectures/presets/format/keys.yaml \
  xarch/modules/spec/application/logic/profile_parsing.py \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py \
  tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_file.py \
  tests/bootstrap/test_profile_explain.py
git commit -m "testing may name its preset as a map, {preset: pytest}, which means testing: pytest, and a framework key written beside preset is refused, never merged"
```

---

### Task 2: The needs walk reads `{preset}` as the preset

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_needs.py:27-46` (`_configured`), new helper `_framework`
  before `_held`
- Test: `tests/modules/spec/application/logic/test_profile_needs.py:281-290`

**Interfaces:**
- Consumes: the key `testing.preset` from Task 1 (it has no needs, so the walk yields nothing for it).
- Produces: `_framework(testing: Any, presets: Mapping[str, Any]) -> Any` in `profile_needs.py`, private.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_needs.py`, extend the params of
`test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing` (line 281) to:

```python
@pytest.mark.parametrize("testing", [pytest.param("nosuch", id="a name that is no preset"),
                                     pytest.param(3, id="a number"), pytest.param(["pytest"], id="a list"),
                                     pytest.param({"preset": "nosuch"}, id="a map naming no preset"),
                                     pytest.param({"preset": 3}, id="a map whose preset is no name")])
def test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing(testing):
    assert short(layered(language="toy", testing=testing), {"pytest": {"skips": ["x"]}}, TOY) == []
```

After `test_a_testing_that_names_a_preset_is_walked_as_the_preset` (ends at line 290), add:

```python
def test_a_testing_map_that_names_a_preset_is_walked_as_the_preset():
    found = short(layered(language="toy", testing={"preset": "pytest"}), {"pytest": {"skips": ["x"]}}, TOY)
    assert [(item.address, item.fact) for item in found] == [("testing.skips", "use"),
                                                             ("testing.skips", "import.resolved")]


def test_a_key_written_beside_a_preset_is_not_walked():
    assert short(layered(language="toy", testing={"preset": "pytest", "skips": ["x"]}), {"pytest": {}}, TOY) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 120 uv run pytest -q --no-header tests/modules/spec/application/logic/test_profile_needs.py 2>&1 | tail -15`
Expected: FAIL in `test_a_testing_map_that_names_a_preset_is_walked_as_the_preset` (found is `[]`, since the map is
walked as written and `preset` has no needs) and `test_a_key_written_beside_a_preset_is_not_walked` (the `skips`
beside `preset` is walked and gives two shortfalls). The two new params of the "walks nothing" test already pass:
the map is walked as written and holds no key with needs.

- [ ] **Step 3: Walk `{preset}` as the preset**

In `xarch/modules/spec/application/logic/profile_needs.py`, in `_configured`, replace:

```python
        if scope == PROFILE and key.name == "testing" and isinstance(value, str):
            value = presets.get(value)
```

with:

```python
        if scope == PROFILE and key.name == "testing":
            value = _framework(value, presets)
```

Change the last sentence of `_configured`'s docstring from
`The file's testing, written as the name of a preset, is walked as the preset's mapping."""` to
`The file's testing, naming a preset by its name or under preset, is walked as the preset's mapping."""`.

Add before `def _held(`:

```python
def _framework(testing: Any, presets: Mapping[str, Any]) -> Any:
    """The mapping the file's testing stands for: the preset's when it names one, by its name or under `preset`; None
    when what it names is no preset or no name; else the mapping written."""
    if isinstance(testing, Mapping) and "preset" in testing:
        testing = testing["preset"]
        return presets.get(testing) if isinstance(testing, str) else None
    return presets.get(testing) if isinstance(testing, str) else testing
```

A value of `None` (or any non-mapping) makes `_held` yield nothing, so nothing under `testing` is walked.

- [ ] **Step 4: Run the tests to verify they pass**

Run:
```bash
timeout 300 uv run pytest -q --no-header tests/modules/spec/application/logic/test_profile_needs.py \
  tests/bootstrap/test_needs_agree.py 2>&1 | tail -5
uv run ruff check
```
Expected: PASS; `All checks passed!`. `tests/bootstrap/test_needs_agree.py` is unchanged and stays green.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_needs.py tests/modules/spec/application/logic/test_profile_needs.py
git commit -m "The needs of a testing map that names its preset are the preset's, and a key beside preset is not walked"
```

---

### Task 3: README, CHANGELOG, golden docs, gates

**Files:**
- Modify: `README.md:116`, `README.md:182-183` (after the `testing.globals` sentence)
- Modify: `CHANGELOG.md:106` (end of `[Unreleased]` / `### Added`, before `### Changed`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: the texts of Task 1 (refusal text, `testing.preset` entry).
- Produces: nothing code reads.

- [ ] **Step 1: README profile block**

In `README.md`, line 116, change:

```
testing:  <preset> | {files*, declared*, globals, skips, tables, mocks}
```

to:

```
testing:  <preset> | {preset} | {files*, declared*, globals, skips, tables, mocks}
```

- [ ] **Step 2: README sentence on `{preset}`**

In `README.md`, the sentence ending `` `testing.globals` names what it binds without an import. `` (line 183) is followed
by `That the table forms and the call form are neutral ...`. Insert this sentence between them, on its own lines,
wrapped at 120 columns:

```
`testing: {preset: pytest}` names a preset as a map, and every framework key then comes from it: one written beside
it is refused (`testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`), never
merged, and a project with its own `files` writes the whole map instead; `testing: pytest` is its short form.
```

The edited paragraph reads:

```
... a call whose arguments hold the test's `title` and its `body`; `testing.globals` names what it binds without an import.
`testing: {preset: pytest}` names a preset as a map, and every framework key then comes from it: one written beside
it is refused (`testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map`), never
merged, and a project with its own `files` writes the whole map instead; `testing: pytest` is its short form.
That the table forms and the call form are neutral to a language is proved without a TypeScript reader: ...
```

- [ ] **Step 3: CHANGELOG line**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Added`, after the bullet that ends
`` one declared by its function by its bare name, as before. `` (line 106) and before the blank line and
`### Changed`, add:

```
- `testing` may name its preset as a map, `testing: {preset: pytest}`, which means `testing: pytest`: the framework
  comes wholly from the preset. A framework key written beside `preset` is refused, never merged (`testing.files: the
  preset pytest gives files: drop it, or drop preset and write the whole map`, or `the preset pytest writes no
  globals` for a key the preset does not hold); a `preset` that names no preset is refused at `testing.preset`, and a
  preset may not name a preset. `xarch profile explain testing.preset` explains it, and the "use ..." list of
  `testing` gains `preset`.
```

- [ ] **Step 4: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-6-9/regenerate_docs.py` (outside the worktree):

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:
```bash
mkdir -p /tmp/xarch-6-9
uv run python -I /tmp/xarch-6-9/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
```
Expected: `written`; `git status` lists no file under `docs/cli`, `docs/web` or `docs/xarch` (only the untracked
spec/plan under `docs/superpowers` may show); `git diff --stat -- docs` prints nothing. If any golden doc moved, do
not hand-edit it: restore with `git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 5: Run every gate**

Run:
```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
git diff --quiet -- xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml tests/bootstrap/corpora \
  && echo "profiles and corpora unchanged"
```
Expected: `All checks passed!`; exit 0 for each of the three `xarch` commands; `profiles and corpora unchanged`.

Then run the full suite in the background (it takes over two minutes) and read it at the end:
```bash
timeout 900 uv run pytest -q > /tmp/xarch-6-9/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-6-9/suite.log
tail -5 /tmp/xarch-6-9/suite.log
```
Expected: `N passed` with no failure or error, and the last line `exit 0`.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say testing may name its preset as a map, {preset: pytest}, and that a framework key beside preset is refused; the golden docs regenerate unchanged"
```

---

## Self-Review

**Spec coverage:**
- B1 (forms of `testing`): Task 1 Step 1b (`test_a_map_that_names_a_preset_is_the_preset_by_name`), 1c (plain_tables
  names `` `pytest` ``), 1g (bootstrap equality and check). Whole map unchanged: the existing params of
  `test_a_bad_testing_key_is_refused` (spec test 6) stay.
- B2 (key `testing.preset`): Task 1 Step 3 (key), Step 1e (spec test 13), Step 1b
  `test_a_preset_may_not_name_a_preset_whichever_form_names_it` (spec test 5), and the "use ..." list everywhere
  (Steps 1a, 1d, 1g; spec tests 4 and 7, "in a preset" params keep sharing one text).
- B3.1-6 (refusals and order): Task 1 Step 1b params (spec test 3, each bullet), Step 1d
  `test_functions_beside_a_preset_is_refused_with_its_hint_alone` (spec test 8).
- B4 (needs): Task 2 (spec tests 9, 10, 11); spec test 12 is run unchanged in Task 1 Step 7 and Task 2 Step 4.
- B5 (texts, docs, explain): Task 1 Step 4 (`keys.yaml`), Step 6 (parser docstring), Step 1f/1h (explain, spec test
  17), Task 3 Steps 1-4 (README, CHANGELOG, golden docs).
- Bootstrap spec tests 14, 15, 16: Task 1 Step 1g.
- Gates: Task 3 Step 5.
- Out of scope respected: no `beside`, no merge, no new preset, no change to `_PRESET_MAP`, the non-map text, the
  bundled profiles or corpora (checked in Task 3 Step 5).

**Placeholder scan:** none. Every code step shows its code; every run step its command and expected outcome.

**Type consistency:** `_preset_of(...) -> str`, `_beside(key, preset, presets) -> str`, `_instead(presets) -> str`
are used only in Task 1 Step 5 with those signatures. `_framework(testing, presets) -> Any` is used only in Task 2
Step 3. The key's name is `"preset"` throughout; the explain meaning `the preset the framework is read from` is the
same in `keys.yaml` (Step 4), `SHAPE` (Step 1f) and the bootstrap explain test (Step 1h).

**Review Focus:** five lines above, each pinned by a param or test in Task 1 Step 1.

**Checked before writing:** a throwaway prototype of Task 1 and Task 2 was run against every test in this plan. All
passed, `ruff check`, `xarch check`, `xarch check --strict` and `xarch profile check architecture.yaml` were green, the
golden docs regenerated with no diff, and `xarch profile explain` grew from 89 to 90 lines (its test requires fewer
than 100). The prototype was reverted. Not covered: a preset document that is not a mapping (for example
`presets={"odd": 3}`) already crashes `_testing` with `TypeError` at `"tables" in value` under `testing: odd`. That is
an existing bug, outside this card; the new branch neither fixes nor worsens it.
<!-- task-pipeline: validated -->
