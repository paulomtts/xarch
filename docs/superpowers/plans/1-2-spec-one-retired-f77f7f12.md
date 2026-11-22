# 1.2 retired keys: one table read by every unknown-key path

Card `f77f7f12`, subtask of `4e9e503c`. Release step 1 of the 0.3.0 merged order. Stacked on step 0 (card
`40fa4c21`, the archived profiles as plain yaml).

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`.

- `key-names-design.md` lines 24-26, ruling 6: "An old key is refused with a hint from one shared retired-keys table:
  by scope and name, read by every unknown-key path, built first in the release, fixed text in one form.
  `profile explain <old key>` points to the new key from the same table."
- The same note, line 35, default 10: "One wording for every refusal. One problem per retired key when a mapping holds
  several."
- The same note, section 4, lines 339-366: the one wording (lines 342-349), the misplaced forms of new keys from the same
  table (lines 351-353), one problem per retired key with the joined message after them for keys only unknown (lines
  355-356), the mechanism (lines 358-363: the table in `spec/domain/profile_keys.py`, by scope and name, each with its
  fixed hint, plus retired rule ids; read by `_keys` and `ck.unknown_keys` by scope; `rule_hints` reads the rule-id
  part; built with no entry; `profile explain <old key>` answers with the refusal's text and the exit code of an
  unknown key), and no compatibility window (lines 365-366).
- The same note, section 5 item 1, lines 376-377: "The table, the hint in `_keys`, `unknown_keys` and `rule_hints`, one
  problem per retired key, `profile explain` reading the table, with its tests, and no entry yet." Lines 370-373 give
  the gates.
- The same note, "Dodges, named in advance", lines 405, 417, 422: no silent acceptance or alias with a warning; no
  special case per key inside `_keys`; no hint that echoes the value written.
- `0.3.0-cohesion-review-3.md` line 225, overlap O1: the table and its readers (`_keys`, `ck.unknown_keys`,
  `rule_hints`, "unknown guard", `profile explain`); step 1 builds it with no entry; each note adds its entries in its
  own step. Line 258, row 1 of the merged order. Lines 228-229 (O4, O5): README and CHANGELOG lines under
  `[Unreleased]`. Line 232 (O8): golden docs regenerated and their diff read. Lines 216-219 (C15): the misplaced form
  `unknown key 'never': a key of uses, beside imports: write uses: {never: <list>}`, so an entry's text may be any
  fixed text, not only "renamed in 0.3.0: ...".

## What is there now

- `xarch/modules/spec/domain/profile_keys.py` holds the scope constants (`PROFILE`, `PART`, `TIER`, ... lines 13-35),
  `SCOPES` (scope to address, lines 37-60) and the `Key`, `KeyText`, `Catalogue` dataclasses. No table of retired keys
  exists anywhere.
- The top-level keys are checked by `_keys` in `xarch/modules/spec/application/logic/profile_parsing.py:210-218`:
  `unknown key(s) 'a', 'b': use <sorted keys>` then one `missing `<key>`` per required key.
- Every other mapping goes through `unknown_keys(spec, known, where)` in
  `xarch/modules/spec/application/logic/profile_checks.py:527-531`: one joined problem
  `<where>: unknown key(s) 'a', 'b': use <sorted known>`. It knows no scope. Its callers and the scope each one's
  `known` comes from:
  - `profile_parsing.py` 276 `PART`, 513 `MOCKS`, 593 `TIER`, 633 `TIER_DOCS`, 665 `FAKES`, 735 `SCENARIO_COVERAGE`,
    777 `DEAD_CODE`, 873 `NO_DUPLICATES`, 884 `NO_TWINS`, 919 `PASS_THROUGH`, 967 `DOCS`;
  - `profile_checks.py` 105 `NAMING`, 144 `PAGE`, 179 `FILE`, 368 `TABLE`, 441 `FIXTURE` (the ad hoc set
    `{calls, "autospec"}`, whose `calls` is the language's word), 479 `framework_patterns` (called once, from
    `profile_parsing.py:496`, with `names_of(TESTING)`);
  - `sending.py:25` `REVIEW`; `evals.py` 100 `PLACEMENT`, 186 `EVAL` (`slots = names_of(EVAL)`), 310 the ad hoc
    `("flagged", "clean")` of an eval's examples, which is no scope.
- Rule ids under `hints` are checked by `rule_hints` (`profile_checks.py:330-345`):
  `hints.<rule>: unknown rule id '<rule>': use <sorted RULES and own ids>`.
- Guard names are checked in `_guards` (`profile_parsing.py:696-697`):
  `guards: unknown guard '<name>': use <sorted guard names>`, one problem per unknown guard.
- `xarch profile explain <key>` (`xarch/cli/commands/profile.py:65-145`) calls `ExplainService.explain`
  (`xarch/modules/spec/application/services/explanation.py:41-66`); for an address with no key (`key_at` returns
  `None`) it returns `UnknownKey(cleaned(address), nearest(...))` (contract
  `xarch/modules/spec/contract/__init__.py:332-336`). The CLI renders it with `unknown_message` / `unknown_document`
  (`xarch/cli/reports/profile_report.py:132-134, 161-163`) through `refuse_with` (`xarch/cli/terminal.py:67-72`), exit
  code 2 in text and in JSON. When the project's profile does not load, the CLI refuses with that reason instead
  (`profile.py` the `UnknownKey() if isinstance(chosen, ProfileRefused)` branch). `rules/adapters/spec_profile.py:105`
  also calls `spec.explain`, for `KeyFacts`.
- `xarch/modules/spec/application/logic/key_lookup.py` holds the lookups of the key table (`plain`, `keys_of`,
  `names_of`, `required_of`).

## Required behavior

### 1. One table

1. `xarch/modules/spec/domain/profile_keys.py` holds one table of retired names: a tuple of frozen entries, each with a
   scope, a name and a fixed text. The scope is one of the keys of `SCOPES` or of `HELD` (`EVAL`, the entry of `evals`, is only in `HELD`), or a new constant for rule ids (the
   scope of a name written as a key of `hints`). Guard names are entries of the scope `GUARD` (the address
   `guards`), since a guard name is a key of `guards`.
2. The same table holds old keys ("renamed in 0.3.0: write tests"), moved keys ("moved in 0.3.0: write uses: {never:
   <list>}"), misplaced new keys ("a key of uses: write uses: {never: <list>}") and retired rule ids ("renamed in 0.3.0:
   write may-import"). An entry's text is the whole hint, fixed, one line; nothing in the code tells the kinds apart.
3. The shipped table has no entry. No code anywhere names a retired key or rule id.
4. One lookup in `key_lookup.py` gives the text of the entry for a scope and a name, or nothing. Every reader in
   section 2 finds a retired name through it and through nothing else, and it reads the shipped table at the time of
   the call, so a test can set a table built for the test in that one place.

### 2. Every unknown-key path reads it

The one wording (note section 4, lines 342-349), with `<known>` the same sorted list today's message gives:

    <where>: unknown key '<name>': <text>; use <known>
    unknown key '<name>': <text>; use <known>                      (the top level, which has no where)
    hints.<rule>: unknown rule id '<rule>': <text>; use <known>
    guards: unknown guard '<name>': <text>; use <known>

5. **Mappings.** For a mapping of a scope, every key that is not known and has an entry under that scope gives one
   problem of its own in the wording above, in sorted order of the key. The keys that are not known and have no entry
   give today's joined message, byte for byte, after them, listing only those keys (singular `key` when one remains).
   When every unknown key has an entry, no joined message is given. When none has, the output is exactly today's.
6. **The top level.** `_keys` does the same under the scope `PROFILE`, in the same order: retired keys, then the joined
   message, then today's `missing` problems.
7. **Each scope its own.** Each call site in "What is there now" reads the table under the scope its known keys come
   from, including `FIXTURE`, `TESTING` (through `framework_patterns`) and `EVAL`. The one call with no scope (an
   eval's `flagged`/`clean` examples) reads no entry. An entry under one scope never changes the message of another:
   an entry `(PART, "tier")` does not touch `tiers.unit.tier` or a top-level `tier`.
8. **Rule ids.** In `hints`, a rule id that is neither a check xarch has nor one of the profile's own, and has an entry
   under the rule-id scope, gives `hints.<rule>: unknown rule id '<rule>': <text>; use <known>`. Others keep today's
   message. A profile's own id that matches an entry is the profile's own and is accepted, as today.
9. **Guards.** In `guards`, a name that is not a guard and has an entry under `GUARD` gives
   `guards: unknown guard '<name>': <text>; use <known>`. Others keep today's message. `package_only` keeps its own
   problem ahead of the table.
10. **A known name wins.** A name that is known in its scope is accepted even if the table has an entry for it; the
    table only words a refusal, it never refuses a name.
11. **Fixed text.** The problem never holds the value written under the retired key: a part writing
    `tier: unit` and a part writing `tier: [1, 2]` give the same problem.
12. **No alias.** A retired key is refused: the profile does not load, with the exit code of any profile that does not
    load. Nothing is read from its value; no warning in place of a refusal.

### 3. `profile explain <old key>`

13. When the typed address has no key of the format and is the address of an entry (its scope's address in `SCOPES`, or `evals.<id>` for `EVAL` (from `HELD`),
    with the name after it, or the bare name for `PROFILE`; placeholders typed or not, as `cleaned` already handles,
    so `parts.tier` and `parts.<part>.tier` are both `parts.tier`), the answer is still `UnknownKey`, carrying the
    entry's text. A new field of `UnknownKey` with an empty default holds it, so other callers (`spec_profile.py:105`)
    see no change.
14. The text output is

        error: no key `parts.tier` in the format: renamed in 0.3.0: write tests; the nearest are <nearest>

    with today's `; of the words of a check, ...` tail when there are such words. The JSON is today's document with one
    more field, `"retired"`: the entry's text, `null` for an address with no entry. The exit code is 2, as for any
    unknown key, in both.
15. A key of the format is explained as today even if the table has an entry at its address (rule 10). An address with
    no entry gives today's output byte for byte (`"retired": null` is the only addition to the JSON). Rule-id entries
    have no address and are not looked up by `explain`. When the project's profile does not load, the refusal is that
    reason, as today.

### 4. Docs

16. CHANGELOG, under `[Unreleased]` / `### Changed`: one line saying that a key, a guard or a rule id that xarch has
    retired is refused with a fixed hint naming what to write instead, one problem per retired key, read from one table
    that `profile explain` also answers from; no name is retired yet.
17. README: no line at this step. It names no retired key and nothing a reader of it sees changes while the table is
    empty; the step that adds the first entry writes it (O4).
18. The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read: none is expected, since no
    message of a loading profile changes. The recorded corpora are not touched and their findings do not move.

## Error paths

- A profile mixing a retired key, an unknown key and a missing required key gets all three kinds of problem, in the
  order of rule 6, in one `InvalidArchitecture`.
- A mapping that is not a mapping keeps today's "must be a mapping" problem; the table is not read.
- A non-string key (`1:` or `true:` in yaml) is looked up and shown as `str(key)`, as today's message shows it.
- `profile explain` with a typed address that is an entry but the profile of the project does not load: refused with
  the profile's reason, exit 2, as today.

## Tests

Tiers as the repository uses them: `tests/modules/...` are unit tests of one module's functions, fast and with no CLI;
`tests/bootstrap/...` drive the real app through `CliRunner`. A table built for the test is set with
`monkeypatch.setattr` on the shipped table's name in the lookup module (rule 4), so the readers run unchanged.

Unit, `tests/modules/spec/application/logic/test_retired_keys.py` (new; the readers are functions of the spec logic,
and a table built for the test exercises them without a CLI):

1. `unknown_keys` with an entry for one of two unknown keys: the retired problem, then the joined message naming only
   the other, singular.
2. Two retired keys in one mapping (`forbidden` and `tier` under `PART`): two problems, sorted, no joined message.
3. A retired key, two only unknown: one retired problem, then today's plural joined message of the two.
4. No entry matches: output equal to today's, byte for byte (the scope given or not).
5. An entry under another scope does not apply (`(TIER, "tier")` and a part writing `tier`).
6. A known key with an entry is accepted (rule 10).
7. The value written is not in the problem: two values, the same problem (rule 11).
8. `rule_hints` with a rule-id entry: the retired wording; an own id equal to the entry's name is accepted; an id with
   no entry keeps today's message.
9. The top level through the loader (`tests/modules/spec/profiles.py` `problems`): a retired top-level key, an unknown
   one and a missing `parts` give the three problems in rule 6's order.
10. A part, a tier, `testing`, `testing.mocks.fixtures.<parameter>` and an eval through the loader, each with an entry
    under its scope: each gives the retired wording at its `where` (rule 7; one parametrized test, one case per scope
    reached through a call site that the old code reached with no scope, plus `PART` and `TIER`).
11. `guards` with a guard-scope entry: `guards: unknown guard '<name>': <text>; use ...`; another unknown guard keeps
    today's message.
12. An eval's `examples` writing `flagged2`, with an entry `(PART, "flagged2")`: today's message (the call with no
    scope reads no entry).

Unit, `tests/modules/spec/domain/test_profile_keys.py` (new; a property of the shipped data):

13. Every entry of the shipped table has a scope in `SCOPES`, `HELD` or the rule-id scope, a name and one line of text; no two
    entries share scope and name; no entry names a key known in its scope, nor a rule id in `RULES`. It passes on the
    empty table and binds every later step's entries.
14. The shipped table has no entry (the deliverable of this step; the step that adds the first entry deletes this test).

Unit, `tests/modules/spec/application/test_explain.py` (the service, beside its existing tests):

15. With a table built for the test, `explain("parts.tier")` and `explain("parts.<part>.tier")` return `UnknownKey`
    carrying the entry's text; an address with no entry carries the empty text; a key of the format with an entry is
    still `KeyExplained`.

Unit, `tests/cli/reports/test_profile_report.py` (the rendering):

16. `unknown_message` with a text: `no key `parts.tier` in the format: <text>; the nearest are ...`; with words, the
    words' tail after it; with no text, today's string. `unknown_document` gives `"retired"`: the text, or `null`.

Bootstrap, `tests/bootstrap/test_profile_explain.py` (exit codes are only seen through the real app):

17. `profile explain parts.tier` with a table built for the test: exit 2, the error line of rule 14; with `--output
    json`, exit 2, `ok: false`, `retired` set.
18. `profile check` on a profile writing a retired part key, with a table built for the test: exit code as for any
    profile that does not load, the retired problem in the output.

Every existing test that says "unknown key" stays green unchanged: the messages with no entry are byte for byte
today's.

## Gates

On this branch alone, with the full suite green: `uv run pytest -q` (over two minutes: run it in the background, read
it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

## Project rules for the planner

- No comments in xarch's code; docstrings say what a function gives. Tests written first.
- Examples simple, with absolute `app.` imports. Python only in the reader adapter and the data files under
  `xarch/architectures/presets/`; this step adds none there.
- Recorded corpora (`tests/bootstrap/corpora/`) are not touched at this step.
- Golden docs are regenerated and their diff read, never edited by hand.
- `.claude/` stays out of commits; nothing is pushed.

## Out of scope

- Every entry of the table: `tier`, `forbidden`, `apply_forbidden`, the top-level `forbidden`, the rule ids
  `forbidden` and `rules`, the misplaced `never`/`apply_never`. Each later step (release steps 2-4, and the notes with
  a retired key, O1) adds its own, with the README line.
- Any rename of a key, a rule id or an internal identifier.
- Entries for names that never shipped (`may_not_use`, a tier's `beside`, `classes:`/`functions:` part maps; O1).
- `profile explain` of a retired rule id: rule ids have no address in the format.
- The `{rules: see the docs}` example in `rule_hints`' "must be a mapping" text (release step 4).
- Problems that are not "unknown" (wrong type, missing key, `package_only` under `guards`).


---

# 1.2 retired keys: one table read by every unknown-key path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One table of retired names (`RETIRED`, empty) in `profile_keys.py`, one lookup of it in `key_lookup.py`,
read by every unknown-key path (`_keys`, `unknown_keys`, `rule_hints`, the unknown-guard branch) and by
`xarch profile explain`, with every message of a profile that names no retired name byte for byte today's.

**Architecture:** The domain gets a frozen `Retired(scope, name, text)`, the table `RETIRED: tuple[Retired, ...] = ()`
and a scope constant `RULE_ID` for rule ids. `key_lookup.py` reads `RETIRED` as a module global at call time through
`retired(scope, name)` and `retired_at(address)`, so a test sets a table of its own with
`monkeypatch.setattr(key_lookup, "RETIRED", ...)`. `profile_checks.unknown_keys` gains a `scope` argument and is built
on a new `unknown_of` (the problems without the address, which `_keys` uses for the top level) and `advice` (the
`<text>; use <known>` tail, which `rule_hints` and `_guards` use too). `UnknownKey` gains `retired: str = ""`, the
service fills it from `retired_at`, and the report puts it in the message and in the JSON as `"retired"`.

**Tech Stack:** Python 3.13, `uv`, `pytest` (with its `monkeypatch` fixture), `typer.testing.CliRunner`, `ruff`.

**Spec:** `docs/superpowers/specs/1-2-spec-one-retired-f77f7f12.md` (prepended above).

## Global Constraints

- The one wording: `<where>: unknown key '<name>': <text>; use <known>`; at the top level
  `unknown key '<name>': <text>; use <known>`; `hints.<rule>: unknown rule id '<rule>': <text>; use <known>`;
  `guards: unknown guard '<name>': <text>; use <known>`. `<known>` is the same sorted list today's message gives.
- Retired keys first, one problem each, in sorted order of the key; then today's joined message of the keys only
  unknown, "byte for byte, after them, listing only those keys (singular `key` when one remains)"; at the top level
  then today's `missing` problems.
- "The shipped table has no entry. No code anywhere names a retired key or rule id."
- "A name that is known in its scope is accepted even if the table has an entry for it; the table only words a
  refusal, it never refuses a name." The problem never holds the value written.
- `profile explain`: `error: no key `parts.tier` in the format: <text>; the nearest are <nearest>` (then today's
  `; of the words of a check, ...` tail), JSON gains `"retired"` (the text, or `null`), exit 2.
- CHANGELOG one line under `[Unreleased]` / `### Changed`; README unchanged; golden docs
  `docs/{cli,web,xarch}/testing.md` regenerated and expected unchanged; `tests/bootstrap/corpora/` not touched.
- No comments in xarch's code (docstrings only). Never `ruff --fix`. Tests first. `.claude/` stays out of commits.
  Nothing is pushed. Never `git add docs/superpowers/` (the workflow commits the spec and the plan itself).
- Gates: `uv run pytest -q` (in the background, read at the end), `uv run xarch check`, `uv run xarch check --strict`,
  `uv run ruff check`, `uv run xarch profile check architecture.yaml`.
- Never kill processes by name or pattern; stop a stuck test with `timeout`.

### Deviations from the spec's Tests section, and why

- **Names in the tests.** The spec's examples (`tier`, `forbidden` under `PART`, `parts.tier`) are keys the format
  has today, so by rule 10 an entry for them changes nothing. The tests use names the format does not have:
  `tested_by`, `banned`, `colour`, `zone` (keys), `old-rule` (a rule id), `no-comment` (a guard), `asks` (an eval
  slot). The texts are the spec's kinds: `renamed in 0.3.0: write tier`, `moved in 0.3.0: write uses: {never:
  <list>}`, `a key of uses: write uses: {never: <list>}`, `renamed in 0.3.0: write may-import`.
- **Test 15 (the explain service) is not in `tests/modules/spec/application/test_explain.py`.** That file is the
  integration tier, and `xarch check` refuses an integration test that imports `application/logic/` or
  `domain/profile_keys` (checked: "a test of controller/ (integration tier) may not import logic/ of modules/spec"),
  which setting a table requires. Its cases are split: the address matching goes to unit tests of `retired_at`
  (Task 1, in `test_retired_keys.py`), and the service's behaviour (an entry's text carried, a key of the format
  still explained, no entry giving today's answer) to the bootstrap tests of Task 3. The existing integration case
  `UnknownKey("parts.may_imports", (...))` keeps passing and pins that an address with no entry carries `""`.
- **The wired tests set the table through a helper with a `SimpleNamespace` entry** (Task 3), since `xarch check`
  refuses a wired test that calls a `domain/` constructor such as `Retired(...)`.
- **Test 18 (`profile check`) goes in `tests/bootstrap/test_profile_check.py`**, which already writes a profile copy
  in its fixture, not in `test_profile_explain.py`.
- **Two existing report tests change.** `tests/cli/reports/test_profile_report.py`'s two unknown-key tests compare the
  whole JSON document; rule 14 adds `"retired"` to it, so each expected dict gains `"retired": None`. Nothing else in
  them changes.
- The JSON flag is `--format json` (the spec writes `--output json`; the CLI's option is `--format`).

## Review Focus

1. **A non-string yaml key** (`1:` or `true:` in a mapping) with an entry for `"1"`: looked up and shown as
   `str(key)`, `unknown key '1': <text>; use ...`. Pinned by
   `test_a_key_yaml_reads_as_no_string_is_looked_up_as_it_is_shown` (Task 2).
2. **A mapping written as something else** (a part written as a list) while the table has an entry: only today's
   "must be a mapping" problem, the table not read. Pinned by
   `test_a_mapping_written_as_a_list_keeps_its_own_problem_and_reads_no_entry` (Task 2).
3. **Only retired keys at the top level** (no other unknown key, nothing missing): the retired problems alone, no
   joined message with an empty list. Pinned by `test_a_file_whose_only_unknown_keys_are_retired_gives_no_joined_problem`
   (Task 2).
4. **`profile explain` typed loosely**: spaces and stray dots around the address, the `<part>` placeholder, `[]`, an
   eval's id or `<id>` step; and `evals.placement.<name>` must not be read as a slot of an eval with the id
   `placement`. Pinned by `test_an_address_of_an_entry_gives_its_text_however_it_is_typed` and
   `test_an_address_that_is_no_entry_gives_nothing` (Task 1).
5. **`profile explain` of an entry's address in a project whose profile does not load**: refused with the profile's
   reason, as today, not with the hint. Pinned by
   `test_an_address_xarch_retired_in_a_project_whose_profile_does_not_load_is_refused_with_why` (Task 3).

---

### Task 1: The table and its lookups

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py` (after `HELD`, lines 61-63; and at the end of the file, after
  `Catalogue`)
- Modify: `xarch/modules/spec/application/logic/key_lookup.py` (imports line 7; two functions at the end)
- Create: `tests/modules/spec/domain/test_profile_keys.py`
- Create: `tests/modules/spec/application/logic/test_retired_keys.py`

**Interfaces:**
- Consumes: `SCOPES`, `HELD`, `PROFILE`, `EVAL`, `EVALS`, `PART`, `TIER`, `NAMING` from `profile_keys.py`;
  `plain`, `names_of` in `key_lookup.py`; `KEYS`, `SLOTS` from `xarch/modules/spec/domain/key_table.py`; `RULES` from
  `xarch/kernel/violations.py`.
- Produces:
  - `profile_keys.RULE_ID: str = "rule-id"`
  - `profile_keys.Retired` (frozen dataclass: `scope: str`, `name: str`, `text: str`)
  - `profile_keys.RETIRED: tuple[Retired, ...] = ()`
  - `key_lookup.retired(scope: str, name: str) -> str` (the entry's text, `""` when none)
  - `key_lookup.retired_at(address: str) -> str` (the text of the entry whose address is the one typed, `""` when
    none; rule-id entries have no address)
  - the test helper `table(monkeypatch, *entries)` in `test_retired_keys.py`, which Task 2 reuses in the same file.

- [ ] **Step 1: Record the baseline**

```bash
mkdir -p /tmp/xarch-1-2
uv run ruff check
uv run xarch check > /tmp/xarch-1-2/baseline-check.txt 2>&1; echo "check exit $?"
uv run xarch check --strict > /tmp/xarch-1-2/baseline-strict.txt 2>&1; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
timeout 1200 uv run pytest -q > /tmp/xarch-1-2/baseline-pytest.txt 2>&1 &
echo $! > /tmp/xarch-1-2/baseline-pytest.pid
```

Expected: ruff "All checks passed!", the three xarch commands exit 0. Go on with Step 2 while pytest runs; before
Task 1's commit, read `tail -3 /tmp/xarch-1-2/baseline-pytest.txt` (all passed) and note the passed count.

- [ ] **Step 2: Write the failing domain test**

Create `tests/modules/spec/domain/test_profile_keys.py`:

```python
"""The table of retired names as xarch ships it: each entry has a scope of the format (or the scope of rule ids), a
name and one line of fixed text, once, and names nothing the format still has; at this step it has no entry."""
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import HELD, RETIRED, RULE_ID, SCOPES


def test_every_entry_has_a_scope_a_name_and_one_line_of_text():
    scopes = {*SCOPES, *HELD, RULE_ID}
    assert [entry for entry in RETIRED if entry.scope not in scopes or not entry.name or not entry.text.strip()
            or "\n" in entry.text] == []


def test_no_two_entries_share_a_scope_and_a_name():
    assert len({(entry.scope, entry.name) for entry in RETIRED}) == len(RETIRED)


def test_no_entry_names_a_key_its_scope_still_has_nor_a_rule_id_xarch_checks():
    known = {(key.scope, key.name) for key in (*KEYS, *SLOTS)} | {(RULE_ID, rule) for rule in RULES}
    assert [entry for entry in RETIRED if (entry.scope, entry.name) in known] == []


def test_no_name_is_retired_yet():
    assert RETIRED == ()
```

- [ ] **Step 3: Write the failing lookup tests**

Create `tests/modules/spec/application/logic/test_retired_keys.py`:

```python
"""The table of retired names, read by every path that refuses an unknown name: the lookup by scope and name, and by
the address `profile explain` is typed with; every unknown key of a mapping, of the file, under `hints` and under
`guards` that has an entry under its scope gives one problem of its own with the entry's fixed text, ahead of today's
message for the others, which is unchanged. A table built for each test is set where the lookup reads it."""
import pytest

from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.application.logic.key_lookup import retired, retired_at
from xarch.modules.spec.domain.profile_keys import EVAL, NAMING, PART, PROFILE, RULE_ID, TIER, Retired

RENAMED = "renamed in 0.3.0: write tier"
MOVED = "moved in 0.3.0: write uses: {never: <list>}"
MISPLACED = "a key of uses: write uses: {never: <list>}"


def table(monkeypatch: pytest.MonkeyPatch, *entries: tuple[str, str, str]) -> None:
    """The table of retired names is the entries given, each (scope, name, text), for this test alone."""
    monkeypatch.setattr(key_lookup, "RETIRED", tuple(Retired(scope, name, text) for scope, name, text in entries))


def test_the_lookup_gives_the_text_of_the_entry_for_a_scope_and_a_name_or_nothing(monkeypatch):
    table(monkeypatch, (PART, "tested_by", RENAMED))
    assert (retired(PART, "tested_by"), retired(TIER, "tested_by"), retired(PART, "banned"), retired("", "tested_by")) \
        == (RENAMED, "", "", "")


def test_the_shipped_table_gives_nothing():
    assert (retired(PART, "tier"), retired_at("parts.tier")) == ("", "")


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "parts.tested_by", id="a key of a part, typed plain"),
    pytest.param((PART, "tested_by", RENAMED), "parts.<part>.tested_by", id="with the placeholder of the part"),
    pytest.param((PART, "tested_by", RENAMED), " parts.tested_by. ", id="with spaces and a stray dot"),
    pytest.param((PROFILE, "banned", MOVED), "banned", id="a key of the file, by its bare name"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming[].level", id="a key of a row of a list, with []"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming.level", id="a key of a row of a list, typed plain"),
    pytest.param((EVAL, "asks", RENAMED), "evals.<id>.asks", id="a slot of an eval, with the placeholder of its id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.title-rule.asks", id="a slot of an eval, under an id"),
])
def test_an_address_of_an_entry_gives_its_text_however_it_is_typed(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == entry[2]


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "tiers.tested_by", id="the name under another scope"),
    pytest.param((PART, "tested_by", RENAMED), "tested_by", id="the name at the top of the file"),
    pytest.param((PROFILE, "banned", MOVED), "parts.banned", id="a key of the file, under a part"),
    pytest.param((EVAL, "asks", RENAMED), "evals.placement.asks", id="placement is a key of evals, not an eval's id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.asks", id="a slot of an eval, typed with no id step"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "hints.old-rule", id="a rule id has no address"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "old-rule", id="nor a bare one"),
])
def test_an_address_that_is_no_entry_gives_nothing(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == ""
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py -q`
Expected: two collection errors, `ImportError: cannot import name 'RETIRED'` (domain test) and
`ImportError: cannot import name 'retired'` (logic test).

- [ ] **Step 5: Add the table to the domain**

In `xarch/modules/spec/domain/profile_keys.py`, after the docstring of `HELD` (the line ending `...listed with the keys
of that map."""`), insert:

```python
RULE_ID = "rule-id"
"""The scope of a rule id written as a key of `hints`: not a key of the format, so it has no address."""
```

At the end of the file, after the class `Catalogue`, append:

```python


@dataclass(frozen=True)
class Retired:
    """A name xarch no longer reads, and what a profile writes instead.

    scope: one of SCOPES or HELD (GUARD for a guard's name), or RULE_ID for a rule id written under `hints`
    name: the name as a profile writes it
    text: the whole hint, fixed and one line, said after the name in the refusal, such as "renamed in 0.3.0: write
        tests"
    """
    scope: str
    name: str
    text: str


RETIRED: tuple[Retired, ...] = ()
"""Every key, guard and rule id xarch has retired: a profile writing one is refused with the entry's text."""
```

- [ ] **Step 6: Add the two lookups**

In `xarch/modules/spec/application/logic/key_lookup.py`, change the import line

```python
from xarch.modules.spec.domain.profile_keys import HELD, Key
```

to

```python
from xarch.modules.spec.domain.profile_keys import HELD, PROFILE, RETIRED, SCOPES, Key, Retired
```

and append at the end of the file:

```python


def retired(scope: str, name: str) -> str:
    """The fixed text of the entry of the table of retired names for the name in the scope; "" when it has none."""
    return next((entry.text for entry in RETIRED if entry.scope == scope and entry.name == name), "")


def retired_at(address: str) -> str:
    """The fixed text of the entry of the table of retired names at an address as a person types it: plain, with or
    without placeholders (parts.tier and parts.<part>.tier), the bare name for a key of the file, and for a slot of an
    entry of a map of ids the id's placeholder or any id in its step; "" when no entry is there. A rule id has no
    address."""
    written = address.strip().strip(".")
    return next((entry.text for entry in RETIRED if _at(entry, plain(written), written)), "")


def _at(entry: Retired, typed: str, written: str) -> bool:
    """Whether the entry's address is the one typed (plain) or written (as typed, placeholders kept)."""
    if entry.scope == PROFILE:
        return typed == entry.name
    if entry.scope in HELD:
        holder, _, name = typed.rpartition(".")
        above, _, entry_id = holder.rpartition(".")
        held = HELD[entry.scope]
        return name == entry.name and (written == f"{entry.scope}.{entry.name}"
                                       or (above == SCOPES[held] and bool(entry_id) and entry_id not in names_of(held)))
    return entry.scope in SCOPES and typed == plain(f"{SCOPES[entry.scope]}.{entry.name}")
```

(`EVAL` is `"evals.<id>"`, the scope's own address, so `f"{entry.scope}.{entry.name}"` is `evals.<id>.asks`.)

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py -q`
Expected: all pass (4 + 17).

- [ ] **Step 8: Lint and self-check**

Run: `uv run ruff check && uv run xarch check`
Expected: ruff passes; `xarch check` exits 0 (in particular no dead-code finding: `retired` and `retired_at` are
still only used by tests at this point; if `xarch check` reports either as dead code, that is expected to clear in
Tasks 2 and 3, so note it and go on, but any other finding is this task's to fix).

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py xarch/modules/spec/application/logic/key_lookup.py \
  tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py
git commit -m "$(cat <<'EOF'
One table of retired names in profile_keys (scope, name, fixed text; RULE_ID for rule ids), shipped with no entry, and its lookups in key_lookup by scope and name and by the address profile explain is typed with; tests say every entry has a scope, a name and one line once and names nothing the format still has, and that no name is retired yet

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Every unknown-key path reads the table

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py` (imports lines 17 and 21; `rule_hints` lines
  330-345; `fixtures` line 441; `framework_patterns` lines 470-479; `unknown_keys` lines 527-531)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (imports lines 85-99; `_keys` lines 210-218; every
  `ck.unknown_keys` call: lines 276, 513, 593, 633, 665, 735, 777, 873, 884, 919, 967; `framework_patterns` call line
  496; `_guards` line 697)
- Modify: `xarch/modules/spec/application/logic/evals.py` (lines 100 and 186; line 310 stays as it is)
- Modify: `xarch/modules/spec/application/logic/sending.py` (line 25)
- Test: `tests/modules/spec/application/logic/test_retired_keys.py` (append)

**Interfaces:**
- Consumes: `key_lookup.retired(scope, name) -> str`, `profile_keys.RULE_ID`, the test helper `table` (Task 1).
- Produces:
  - `profile_checks.unknown_keys(spec: Mapping[Any, Any], known: Collection[str], where: str, scope: str = "") -> list[str]`
  - `profile_checks.unknown_of(spec: Mapping[Any, Any], known: Collection[str], scope: str = "") -> list[str]`
    (the same problems without `<where>: `)
  - `profile_checks.advice(scope: str, name: str, known: Collection[str]) -> str` (`"<text>; use <known>"`, or
    `"use <known>"` with no entry)
  - `profile_checks.framework_patterns(value, problems, where, known, language, scope: str = "")`

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_retired_keys.py`, replace the import block with:

```python
import pytest

from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.application.logic.key_lookup import names_of, retired, retired_at
from xarch.modules.spec.application.logic.profile_checks import rule_hints, unknown_keys
from xarch.modules.spec.domain.profile_keys import (
    DOCS,
    EVAL,
    FIXTURE,
    GUARD,
    HELD,
    NAMING,
    NO_DUPLICATES,
    PART,
    PLACEMENT,
    PROFILE,
    REVIEW,
    RULE_ID,
    SCOPES,
    TESTING,
    TIER,
    Retired,
)
```

and after the constant `MISPLACED` add:

```python
PART_USE = ("built_by, folders, forbidden, holds, immutable, libraries, litmus, may_import, must_import, names, "
            "no_callbacks, package_only, path, role, shared, tier, types_only, untested")
TIER_USE = "apply_forbidden, docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only"
PROFILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, forbidden, guards, hints, language, layers, name, "
               "parts, reserved, review, testing, tiers")
GUARD_USE = ("closed-tree, dead-code, no-comments, no-duplicates, no-twins, pass-through, private-imports, "
             "scenario-coverage, stand-ins")
EVAL_USE = "answer, ask, examples, fix, in, keep, line, message, no, reads, yes"
RULES_USE = ", ".join(sorted(RULES))
CODE = "def run(doc):\n    return doc\n"


def an_eval() -> dict:
    """An eval of the profile's own, `rule`, yes-no, reading functions of store, that loads as it is."""
    return {"rule": {"ask": "Does this function decide a rule of the document itself?", "answer": "yes-no",
                     "reads": "function", "in": {"part": "store"}, "message": "{name} may decide it ({value})",
                     "fix": "read it against the litmus of store",
                     "examples": {"flagged": {"store/a.py": CODE, "store/b.py": CODE},
                                  "clean": {"store/c.py": CODE, "store/d.py": CODE}}}}


def writing(document: dict, *steps: str) -> dict:
    """The document, with `banned: x` written in the mapping found at the steps."""
    held = document
    for step in steps:
        held = held[step]
    held["banned"] = "x"
    return document
```

Then append to the end of the file:

```python
def test_a_retired_key_gets_its_own_problem_ahead_of_the_one_only_unknown(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert unknown_keys({"path": "a", "banned": 1, "colour": 2}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}",
        f"parts.api: unknown key 'colour': use {PART_USE}"]


def test_two_retired_keys_give_two_problems_in_sorted_order_and_no_joined_one(monkeypatch):
    table(monkeypatch, (PART, "tested_by", RENAMED), (PART, "banned", MOVED))
    assert unknown_keys({"tested_by": 1, "banned": 2}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {MOVED}; use {PART_USE}",
        f"parts.api: unknown key 'tested_by': {RENAMED}; use {PART_USE}"]


def test_a_retired_key_beside_two_only_unknown_keeps_their_plural_message(monkeypatch):
    table(monkeypatch, (PART, "banned", MISPLACED))
    assert unknown_keys({"zone": 1, "banned": 2, "colour": 3}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': {MISPLACED}; use {PART_USE}",
        f"parts.api: unknown keys 'colour', 'zone': use {PART_USE}"]


@pytest.mark.parametrize("entry, scope", [
    pytest.param((PART, "other", RENAMED), PART, id="an entry for another name of the scope"),
    pytest.param((PART, "colour", RENAMED), "", id="a mapping read with no scope"),
])
def test_with_no_entry_for_its_keys_a_mapping_gets_todays_message(monkeypatch, entry, scope):
    table(monkeypatch, entry)
    assert unknown_keys({"zone": 1, "colour": 2}, names_of(PART), "parts.api", scope) == [
        f"parts.api: unknown keys 'colour', 'zone': use {PART_USE}"]


def test_the_shipped_table_changes_no_message():
    assert unknown_keys({"colour": 1}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'colour': use {PART_USE}"]


def test_an_entry_under_another_scope_does_not_apply(monkeypatch):
    table(monkeypatch, (TIER, "banned", RENAMED))
    assert unknown_keys({"banned": 1}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key 'banned': use {PART_USE}"]


def test_an_entry_of_a_part_key_leaves_a_tier_and_the_file_alone(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert sorted(problems(writing(covered(banned=1), "tiers", "unit"))) == sorted([
        f"layered.yaml: unknown key 'banned': use {PROFILE_USE}",
        f"layered.yaml: tiers.unit: unknown key 'banned': use {TIER_USE}"])


def test_a_known_key_with_an_entry_is_accepted(monkeypatch):
    table(monkeypatch, (PART, "role", RENAMED))
    assert unknown_keys({"role": "x", "path": "a"}, names_of(PART), "parts.api", PART) == []
    assert parsed(layered()).parts["api"].role == "HTTP handlers"


def test_the_value_written_under_a_retired_key_is_not_in_its_problem(monkeypatch):
    table(monkeypatch, (PART, "banned", RENAMED))
    assert unknown_keys({"banned": "unit"}, names_of(PART), "parts.api", PART) \
        == unknown_keys({"banned": [1, 2]}, names_of(PART), "parts.api", PART) \
        == [f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}"]


def test_a_key_yaml_reads_as_no_string_is_looked_up_as_it_is_shown(monkeypatch):
    table(monkeypatch, (PART, "1", RENAMED))
    assert unknown_keys({1: "x"}, names_of(PART), "parts.api", PART) == [
        f"parts.api: unknown key '1': {RENAMED}; use {PART_USE}"]


def test_a_mapping_written_as_a_list_keeps_its_own_problem_and_reads_no_entry(monkeypatch):
    table(monkeypatch, (PART, "x", RENAMED))
    document = layered()
    document["parts"]["api"] = ["x"]
    assert problems(document) == ["layered.yaml: parts.api: must be a mapping with `path` and `role`"]


def test_a_retired_rule_id_under_hints_is_refused_with_its_text_and_another_keeps_todays(monkeypatch):
    table(monkeypatch, (RULE_ID, "old-rule", "renamed in 0.3.0: write may-import"))
    found: list[str] = []
    assert rule_hints({"old-rule": "see the docs", "odd-rule": "see the docs"}, found) == {}
    assert found == [
        f"hints.old-rule: unknown rule id 'old-rule': renamed in 0.3.0: write may-import; use {RULES_USE}",
        f"hints.odd-rule: unknown rule id 'odd-rule': use {RULES_USE}"]


def test_a_rule_id_of_the_profile_own_that_matches_an_entry_is_its_own(monkeypatch):
    table(monkeypatch, (RULE_ID, "old-rule", "renamed in 0.3.0: write may-import"))
    found: list[str] = []
    assert rule_hints({"old-rule": "see the docs"}, found, ("old-rule",)) == {"old-rule": "see the docs"}
    assert found == []


def test_the_file_gives_its_retired_keys_then_the_only_unknown_then_the_missing(monkeypatch):
    table(monkeypatch, (PROFILE, "banned", MOVED))
    assert problems({"name": "x", "colour": 1, "banned": 1}) == [
        f"layered.yaml: unknown key 'banned': {MOVED}; use {PROFILE_USE}",
        f"layered.yaml: unknown key 'colour': use {PROFILE_USE}",
        "layered.yaml: missing `parts`"]


def test_a_file_whose_only_unknown_keys_are_retired_gives_no_joined_problem(monkeypatch):
    table(monkeypatch, (PROFILE, "banned", MOVED))
    assert problems(layered(banned=1)) == [f"layered.yaml: unknown key 'banned': {MOVED}; use {PROFILE_USE}"]


@pytest.mark.parametrize("scope, document, problem", [
    pytest.param(PART, writing(layered(), "parts", "api"),
                 f"parts.api: unknown key 'banned': {RENAMED}; use {PART_USE}", id="a part"),
    pytest.param(TIER, writing(covered(), "tiers", "unit"),
                 f"tiers.unit: unknown key 'banned': {RENAMED}; use {TIER_USE}", id="a tier"),
    pytest.param(TESTING, writing(covered(), "testing"),
                 f"testing: unknown key 'banned': {RENAMED}; use files, functions, mocks, skips, table",
                 id="testing, through framework_patterns"),
    pytest.param(FIXTURE, writing(covered(), "testing", "mocks", "fixtures", "mocker"),
                 f"testing.mocks.fixtures.mocker: unknown key 'banned': {RENAMED}; use autospec, calls",
                 id="a fixture, whose keys are the language's word and autospec"),
    pytest.param(EVAL, writing(layered(evals=an_eval()), "evals", "rule"),
                 f"evals.rule: unknown key 'banned': {RENAMED}; use {EVAL_USE}", id="an eval of the profile's own"),
    pytest.param(PLACEMENT, writing(layered(evals={"placement": {}}), "evals", "placement"),
                 f"evals.placement: unknown key 'banned': {RENAMED}; use alike, examples, lines", id="evals.placement"),
    pytest.param(REVIEW, writing(layered(review={}), "review"),
                 f"review: unknown key 'banned': {RENAMED}; use mask, never", id="review"),
    pytest.param(DOCS, writing(layered(docs={}), "docs"),
                 f"docs: unknown key 'banned': {RENAMED}; use entry, example_notes, examples, naming, pages", id="docs"),
    pytest.param(NO_DUPLICATES, writing(layered(guards={"no-duplicates": {}}), "guards", "no-duplicates"),
                 f"guards.no-duplicates: unknown key 'banned': {RENAMED}; use min_statements", id="a guard's settings"),
])
def test_each_mapping_reads_the_entries_of_its_own_scope(monkeypatch, scope, document, problem):
    table(monkeypatch, (scope, "banned", RENAMED))
    assert problems(document) == [f"layered.yaml: {problem}"]


def test_a_retired_guard_is_refused_with_its_text_and_another_unknown_guard_keeps_todays(monkeypatch):
    table(monkeypatch, (GUARD, "no-comment", "renamed in 0.3.0: write no-comments"))
    assert problems(layered(guards={"no-comment": {}, "zzz": {}})) == [
        f"layered.yaml: guards: unknown guard 'no-comment': renamed in 0.3.0: write no-comments; use {GUARD_USE}",
        f"layered.yaml: guards: unknown guard 'zzz': use {GUARD_USE}"]


def test_the_examples_of_an_eval_have_no_scope_and_read_no_entry(monkeypatch):
    table(monkeypatch, *((scope, "flagged2", RENAMED) for scope in (*SCOPES, *HELD, RULE_ID)))
    document = an_eval()
    document["rule"]["examples"]["flagged2"] = {}
    assert problems(layered(evals=document)) == [
        "layered.yaml: evals.rule.examples: unknown key 'flagged2': use clean, flagged"]
```

(`retired` and `retired_at` stay imported for Task 1's tests; `NAMING` and `EVAL` too.)

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_retired_keys.py -q`
Expected: Task 1's tests pass; the new ones fail. The `unknown_keys` ones with
`TypeError: unknown_keys() takes 3 positional arguments but 4 were given`; the loader and `rule_hints` ones with an
`AssertionError` showing today's message where the retired one is expected. These pass already, before any code
change, and must stay passing: `test_with_no_entry_for_its_keys_a_mapping_gets_todays_message` (after the TypeError is
gone), `test_an_entry_of_a_part_key_leaves_a_tier_and_the_file_alone`,
`test_a_mapping_written_as_a_list_keeps_its_own_problem_and_reads_no_entry`,
`test_a_rule_id_of_the_profile_own_that_matches_an_entry_is_its_own`,
`test_the_examples_of_an_eval_have_no_scope_and_read_no_entry`.

- [ ] **Step 3: Make `unknown_keys` read the table, and add `unknown_of` and `advice`**

In `xarch/modules/spec/application/logic/profile_checks.py`, change the two imports

```python
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of
```
```python
from xarch.modules.spec.domain.profile_keys import FILE, NAMING, PAGE, TABLE
```

to

```python
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of, retired
```
```python
from xarch.modules.spec.domain.profile_keys import FILE, FIXTURE, NAMING, PAGE, RULE_ID, TABLE
```

Replace the whole function

```python
def unknown_keys(spec: Mapping[Any, Any], known: Collection[str], where: str) -> list[str]:
    unknown = sorted(str(k) for k in spec if k not in known)
    if not unknown:
        return []
    return [f"{where}: unknown key{'s' if len(unknown) > 1 else ''} {quoted(unknown)}: use {', '.join(sorted(known))}"]
```

with

```python
def unknown_keys(spec: Mapping[Any, Any], known: Collection[str], where: str, scope: str = "") -> list[str]:
    """The problems of the keys of the mapping at where that are not known (see unknown_of), each naming where."""
    return [f"{where}: {problem}" for problem in unknown_of(spec, known, scope)]


def unknown_of(spec: Mapping[Any, Any], known: Collection[str], scope: str = "") -> list[str]:
    """The problems of the keys of a mapping that are not known, as the top of the file, which has no address, says
    them: one of its own for each that the table of retired names holds under the scope, in sorted order, then one for
    all the others; a scope of "" reads no entry."""
    unknown = sorted(str(k) for k in spec if k not in known)
    problems = [f"unknown key {quoted([name])}: {advice(scope, name, known)}" for name in unknown if retired(scope, name)]
    rest = [name for name in unknown if not retired(scope, name)]
    if rest:
        problems.append(f"unknown key{'s' if len(rest) > 1 else ''} {quoted(rest)}: use {', '.join(sorted(known))}")
    return problems


def advice(scope: str, name: str, known: Collection[str]) -> str:
    """What a name that is not known is told: the fixed text of its entry in the table of retired names under the
    scope, when it has one, then the names that are, sorted."""
    text = retired(scope, name)
    return f"{text}; use {', '.join(sorted(known))}" if text else f"use {', '.join(sorted(known))}"
```

- [ ] **Step 4: Give `rule_hints`, `fixtures` and `framework_patterns` their scopes**

In `rule_hints`, replace

```python
            problems.append(f"hints.{rule}: unknown rule id {rule!r}: use {', '.join(sorted((*RULES, *own)))}")
```

with

```python
            problems.append(f"hints.{rule}: unknown rule id {rule!r}: {advice(RULE_ID, str(rule), (*RULES, *own))}")
```

In `fixtures`, replace

```python
        problems += unknown_keys(spec, {calls, "autospec"}, at)
```

with

```python
        problems += unknown_keys(spec, {calls, "autospec"}, at, FIXTURE)
```

In `framework_patterns`, change the signature and docstring and the `unknown_keys` call:

```python
def framework_patterns(value: Any, problems: list[str], where: str, known: Collection[str],
                       language: Language, scope: str = "") -> Framework | None:
    """How the test framework names test files and functions, the map written at `where`; `known` are the keys the
    map may hold, which the caller may widen with what it reads itself, and `scope` the scope whose retired names
    the map's unknown keys are looked up in."""
```

and

```python
    problems += unknown_keys(value, known, where, scope)
```

In the same file, give every other `unknown_keys` call its scope:

```python
        problems += unknown_keys(spec, names_of(NAMING), where, NAMING)
```
```python
        problems += unknown_keys(spec, names_of(PAGE), where, PAGE)
```
```python
        problems += unknown_keys(spec, names_of(FILE), where, FILE)
```
```python
    problems += unknown_keys(value, names_of(TABLE), where, TABLE)
```

- [ ] **Step 5: Give the loader's calls their scopes, and read the table at the top level and under `guards`**

In `xarch/modules/spec/application/logic/profile_parsing.py`, change the import block from `profile_keys` to

```python
from xarch.modules.spec.domain.profile_keys import (
    DEAD_CODE,
    DOCS,
    FAKES,
    MOCKS,
    NO_DUPLICATES,
    NO_TWINS,
    PART,
    PASS_THROUGH,
    PROFILE,
    SCENARIO_COVERAGE,
    TESTING,
    TIER,
    TIER_DOCS,
)
from xarch.modules.spec.domain.profile_keys import GUARD as GUARD_SCOPE
```

(`GUARD` is already the name of `xarch.modules.spec.domain.guards.GUARD` in this file. The aliased line goes AFTER the
parenthesised block, which is the order ruff's isort wants — checked: with it before the block, `ruff check` reports
`I001`. If `ruff check` still reports `I001`, run
`uv run ruff check --diff xarch/modules/spec/application/logic/profile_parsing.py`, which prints the order it wants
without writing anything, and make that edit by hand; never `--fix`.)

Replace `_keys`:

```python
def _keys(document: Mapping[Any, Any]) -> list[str]:
    """The keys of the file that are unknown, those xarch retired first, and those it is missing."""
    problems = ck.unknown_of(document, names_of(PROFILE), PROFILE)
    problems += [f"missing `{key}`" for key in required_of(PROFILE) if key not in document]
    return problems
```

In `_guards`, replace

```python
            problems.append(f"guards: unknown guard {name!r}: use {', '.join(sorted(_GUARDS))}")
```

with

```python
            problems.append(f"guards: unknown guard {name!r}: {ck.advice(GUARD_SCOPE, str(name), _GUARDS)}")
```

Change the `framework_patterns` call (line 496) to

```python
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language, TESTING)
```

and each `ck.unknown_keys` call to pass the scope its known keys come from, exactly:

```python
        problems += ck.unknown_keys(spec, names_of(PART), where, PART)
```
```python
    problems += ck.unknown_keys(value, names_of(MOCKS), where, MOCKS)
```
```python
    problems += ck.unknown_keys(spec, names_of(TIER), where, TIER)
```
```python
    problems += ck.unknown_keys(value, names_of(TIER_DOCS), where, TIER_DOCS)
```
```python
    problems += ck.unknown_keys(value, names_of(FAKES), where, FAKES)
```
```python
    problems += ck.unknown_keys(spec, names_of(SCENARIO_COVERAGE), where, SCENARIO_COVERAGE)
```
```python
    problems += ck.unknown_keys(spec, names_of(DEAD_CODE), where, DEAD_CODE)
```
```python
    problems += ck.unknown_keys(spec, names_of(NO_DUPLICATES), where, NO_DUPLICATES)
```
```python
    problems += ck.unknown_keys(spec, names_of(NO_TWINS), where, NO_TWINS)
```
```python
    problems += ck.unknown_keys(spec, names_of(PASS_THROUGH), where, PASS_THROUGH)
```
```python
    problems += ck.unknown_keys(value, names_of(DOCS), "docs", DOCS)
```

Then confirm none is left without a scope:
`grep -n "unknown_keys(" xarch/modules/spec/application/logic/*.py` — every call but the definition and
`evals.py`'s `("flagged", "clean")` one ends with a scope after `where`.

- [ ] **Step 6: Give `evals.py` and `sending.py` their scopes**

In `xarch/modules/spec/application/logic/evals.py`:

```python
    problems += ck.unknown_keys(written, names_of(PLACEMENT), "evals.placement", PLACEMENT)
```
```python
    problems += ck.unknown_keys(body, slots, where, EVAL)
```

Leave `problems += ck.unknown_keys(value, ("flagged", "clean"), where)` as it is: an eval's examples are no scope.

In `xarch/modules/spec/application/logic/sending.py`:

```python
    problems += ck.unknown_keys(value, names_of(REVIEW), "review", REVIEW)
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_retired_keys.py -q`
Expected: all pass.

- [ ] **Step 8: Run every spec module test, which holds today's messages byte for byte**

Run: `timeout 600 uv run pytest tests/modules/spec -q`
Expected: all pass, with no change to any existing test.

- [ ] **Step 9: Lint and self-check**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict`
Expected: ruff and `xarch check` pass. `xarch check --strict` fails with exactly one finding, a `guards.dead-code.tests_only`
"weak" one for `retired_at` (checked: only tests name it until Task 3's service does); that single finding is expected
here and clears in Task 3, Step 8, where `--strict` must pass clean. Any other finding is this task's to fix.

- [ ] **Step 10: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py \
  xarch/modules/spec/application/logic/evals.py xarch/modules/spec/application/logic/sending.py \
  tests/modules/spec/application/logic/test_retired_keys.py
git commit -m "$(cat <<'EOF'
Every unknown-key path reads the table of retired names under its own scope: a mapping, the top of the file, hints and guards give one problem per retired name with its fixed text, in sorted order, ahead of today's message for the names only unknown, which is unchanged byte for byte; a known name is accepted whatever the table holds, the value written is never shown, and an eval's examples read no entry

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: `profile explain <old key>` answers from the table

**Files:**
- Modify: `xarch/modules/spec/contract/__init__.py:332-336` (`UnknownKey`)
- Modify: `xarch/modules/spec/application/services/explanation.py` (imports line 18; line 52)
- Modify: `xarch/cli/reports/profile_report.py:132-134` (`unknown_message`) and `:161-163` (`unknown_document`)
- Test: `tests/cli/reports/test_profile_report.py` (two expected dicts gain `"retired": None`; one test added)
- Modify (test code, no test file): `tests/bootstrap/project.py` (imports lines 3-8; one helper at the end)
- Test: `tests/bootstrap/test_profile_explain.py` (append)
- Test: `tests/bootstrap/test_profile_check.py` (append)

**Interfaces:**
- Consumes: `key_lookup.retired_at(address: str) -> str` and the module global `key_lookup.RETIRED` (Task 1),
  `profile_keys.PART`.
- Produces: `UnknownKey(key: str, nearest: tuple[str, ...], retired: str = "")`; `unknown_message` and
  `unknown_document` reading `found.retired`; the wired-test helper
  `tests.bootstrap.project.retiring(monkeypatch: pytest.MonkeyPatch, scope: str, name: str, text: str) -> None`.

A wired test may use `domain/` only as a type: `xarch check` refuses a call of `Retired(...)` in `tests/bootstrap/`,
in a test file or in its helpers (checked: "a wired test uses domain/ of modules/spec only as a type: it may not call
xarch.modules.spec.domain.profile_keys.Retired (tiers.wired.types_only)"). So the wired tests set the table through
`retiring`, whose entry is a `types.SimpleNamespace` with the three fields the lookup reads.

- [ ] **Step 1: Write the failing report tests**

In `tests/cli/reports/test_profile_report.py`, change the two existing expected documents to add `"retired": None`:

```python
def test_an_unknown_key_is_said_with_the_nearest_ones_in_text_and_in_json():
    found = UnknownKey("tire", ("tier", "tiers"))
    assert unknown_message(found) == "no key `tire` in the format: the nearest are tier, tiers"
    assert json.loads(unknown_document(found)) == {
        "ok": False, "error": unknown_message(found), "key": "tire", "nearest": ["tier", "tiers"], "words": [],
        "retired": None}


def test_an_unknown_key_near_words_of_a_check_keeps_the_keys_and_the_words_apart_in_json():
    found = UnknownKey("public", ("name",))
    assert json.loads(unknown_document(found, ("filters.public",))) == {
        "ok": False, "error": "no key `public` in the format: the nearest are name; of the words of a check, "
                              "filters.public", "key": "public", "nearest": ["name"], "words": ["filters.public"],
        "retired": None}
```

and add after them:

```python
def test_an_address_xarch_retired_is_said_with_its_fixed_text_before_the_nearest_keys_and_in_json():
    found = UnknownKey("parts.tested_by", ("parts.untested",), "renamed in 0.3.0: write tier")
    assert unknown_message(found) == ("no key `parts.tested_by` in the format: renamed in 0.3.0: write tier; the nearest "
                                      "are parts.untested")
    assert unknown_message(found, ("filters.test",)) == (
        "no key `parts.tested_by` in the format: renamed in 0.3.0: write tier; the nearest are parts.untested; of the "
        "words of a check, filters.test")
    assert json.loads(unknown_document(found)) == {
        "ok": False, "error": unknown_message(found), "key": "parts.tested_by", "nearest": ["parts.untested"],
        "words": [], "retired": "renamed in 0.3.0: write tier"}
```

- [ ] **Step 2: Write the failing bootstrap tests**

In `tests/bootstrap/project.py`, make the imports

```python
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp
from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.contract import CheckProfile, Explain, KeyExplained, ProfileChecked
```

and append at the end of the file:

```python


def retiring(monkeypatch: pytest.MonkeyPatch, scope: str, name: str, text: str) -> None:
    """The table of retired names holds one entry, (scope, name, text), for this test alone: a record with the fields
    the lookup reads, since a wired test builds no value of domain/ itself."""
    monkeypatch.setattr(key_lookup, "RETIRED", (SimpleNamespace(scope=scope, name=name, text=text),))
```

In `tests/bootstrap/test_profile_explain.py`, make the project imports

```python
from tests.bootstrap.project import bundled_profiles, retiring
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.spec.domain.profile_keys import PART
```

add after `runner = CliRunner()`:

```python


RENAMED = "renamed in 0.3.0: write tier"
```

and append:

```python
def test_an_address_xarch_retired_is_refused_with_its_fixed_text_in_text_and_in_json(monkeypatch):
    retiring(monkeypatch, PART, "tested_by", RENAMED)
    text = runner.invoke(app, ["profile", "explain", "parts.<part>.tested_by"])
    assert text.exit_code == 2
    assert f"error: no key `parts.tested_by` in the format: {RENAMED}; the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.tested_by", "--format", "json"])
    assert found.exit_code == 2
    document = json.loads(found.output)
    assert (document["ok"], document["key"], document["retired"]) == (False, "parts.tested_by", RENAMED)
    assert document["error"].startswith(f"no key `parts.tested_by` in the format: {RENAMED}; the nearest are ")


def test_a_key_of_the_format_is_explained_even_with_an_entry_at_its_address(monkeypatch):
    retiring(monkeypatch, PART, "may_import", RENAMED)
    result = runner.invoke(app, ["profile", "explain", "parts.may_import"])
    assert (result.exit_code, result.output.splitlines()[0]) == (0, "parts.may_import")
    assert RENAMED not in result.output


def test_an_address_with_no_entry_is_refused_as_today_with_retired_null_in_json():
    text = runner.invoke(app, ["profile", "explain", "parts.colour"])
    assert text.exit_code == 2 and "error: no key `parts.colour` in the format: the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.colour", "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] is None


def test_an_address_xarch_retired_in_a_project_whose_profile_does_not_load_is_refused_with_why(tmp_path, monkeypatch):
    retiring(monkeypatch, PART, "tested_by", RENAMED)
    (tmp_path / "pyproject.toml").write_text("[tool.xarch\n")
    refused = runner.invoke(app, ["profile", "explain", "parts.tested_by"])
    assert refused.exit_code == 2 and "cannot read" in refused.output and "pyproject.toml" in refused.output
    assert RENAMED not in refused.output
```

In `tests/bootstrap/test_profile_check.py`, make the project imports

```python
from tests.bootstrap.project import retiring
from xarch.bootstrap.app import app
from xarch.modules.spec.domain.profile_keys import PART
```

and append:

```python
def test_a_key_xarch_retired_fails_like_any_profile_that_does_not_load_with_its_fixed_text(tmp_path, monkeypatch):
    retiring(monkeypatch, PART, "tested_by", "renamed in 0.3.0: write tier")
    edit(tmp_path, lambda d: d["parts"]["domain"].update(tested_by="unit"))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert "parts.domain: unknown key 'tested_by': renamed in 0.3.0: write tier; use built_by, " in result.output
    assert "examples: not checked" in result.output and "INVALID: 1 problem" in result.output
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/cli/reports/test_profile_report.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_check.py -q`
Expected: FAIL. The report tests with `TypeError: UnknownKey.__init__() takes 3 positional arguments but 4 were given`
and with `AssertionError` (no `"retired"` in the document); `..._refused_with_its_fixed_text_in_text_and_in_json` and
`..._retired_null_in_json` with `AssertionError`/`KeyError: 'retired'`. These already pass and must stay passing:
`test_a_key_of_the_format_is_explained_even_with_an_entry_at_its_address`,
`test_an_address_xarch_retired_in_a_project_whose_profile_does_not_load_is_refused_with_why`, and the
`profile check` test (Task 2 already gives it).

- [ ] **Step 4: Add the field to `UnknownKey`**

In `xarch/modules/spec/contract/__init__.py`, replace

```python
@dataclass(frozen=True)
class UnknownKey:
    """A key the format does not have, with the nearest ones that exist."""
    key: str
    nearest: tuple[str, ...]
```

with

```python
@dataclass(frozen=True)
class UnknownKey:
    """A key the format does not have, with the nearest ones that exist, and the fixed text of the entry of the table
    of retired names at its address ("" when none is there)."""
    key: str
    nearest: tuple[str, ...]
    retired: str = ""
```

- [ ] **Step 5: Fill it in the service**

In `xarch/modules/spec/application/services/explanation.py`, change

```python
from xarch.modules.spec.application.logic.key_lookup import shown
```

to

```python
from xarch.modules.spec.application.logic.key_lookup import retired_at, shown
```

and

```python
            return UnknownKey(cleaned(address), nearest(cleaned(address)))
```

to

```python
            return UnknownKey(cleaned(address), nearest(cleaned(address)), retired_at(address))
```

and replace the docstring of `explain` (two lines) with these three, which keep within ruff's 140 columns:

```python
        """The whole format with no address, else the key at it, or the nearest keys when the format has none there
        and the text of the retired name there, if any; raises InvalidArchitecture when the data file of a language,
        or of the format's texts, does not load."""
```

- [ ] **Step 6: Say it in the report**

In `xarch/cli/reports/profile_report.py`, replace

```python
def unknown_message(found: UnknownKey, words: Sequence[str] = ()) -> str:
    also = f"; of the words of a check, {', '.join(words)}" if words else ""
    return f"no key `{found.key}` in the format: the nearest are {', '.join(found.nearest)}{also}"
```

with

```python
def unknown_message(found: UnknownKey, words: Sequence[str] = ()) -> str:
    also = f"; of the words of a check, {', '.join(words)}" if words else ""
    retired = f"{found.retired}; " if found.retired else ""
    return f"no key `{found.key}` in the format: {retired}the nearest are {', '.join(found.nearest)}{also}"
```

and

```python
def unknown_document(found: UnknownKey, words: Sequence[str] = ()) -> str:
    return document({"ok": False, "error": unknown_message(found, words), "key": found.key,
                  "nearest": list(found.nearest), "words": list(words)})
```

with

```python
def unknown_document(found: UnknownKey, words: Sequence[str] = ()) -> str:
    return document({"ok": False, "error": unknown_message(found, words), "key": found.key,
                  "nearest": list(found.nearest), "words": list(words), "retired": found.retired or None})
```

`xarch/cli/commands/profile.py` does not change: its `UnknownKey() if isinstance(chosen, ProfileRefused)` branch
still refuses with the profile's reason first.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run pytest tests/cli/reports tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_explain_words.py tests/bootstrap/test_profile_check.py tests/modules/spec/application/test_explain.py tests/modules/rules/adapters/test_spec_profile.py -q`
Expected: all pass.

- [ ] **Step 8: Lint and self-check**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict`
Expected: all pass, no dead-code finding left.

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/spec/contract/__init__.py xarch/modules/spec/application/services/explanation.py \
  xarch/cli/reports/profile_report.py tests/cli/reports/test_profile_report.py tests/bootstrap/project.py \
  tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_check.py
git commit -m "$(cat <<'EOF'
profile explain answers an address of the table of retired names with the entry's fixed text before the nearest keys, and with retired in its JSON (null for an address with no entry), exit 2 as for any unknown key; a key of the format is explained as before whatever the table holds, and a project whose profile does not load is refused with why

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: The CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `CHANGELOG.md` (under `## [Unreleased]` / `### Changed`, after the existing bullet)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-1-2/regenerate_docs.py`

**Interfaces:**
- Consumes: everything above. Produces: nothing new in code.

- [ ] **Step 1: Write the CHANGELOG line**

In `CHANGELOG.md`, the `[Unreleased]` section becomes:

```markdown
## [Unreleased]

### Changed

- The two archived corpora's profiles (`7cc6111`, `df537ca`) are plain yaml files beside their archives in
  `tests/bootstrap/corpora/`, so a change of format edits them as files; the recorded findings are unchanged.

- A key, a guard or a rule id that xarch has retired is refused with a fixed hint naming what to write instead, one
  problem per retired name ahead of the keys that are only unknown, read from one table that
  `xarch profile explain <old key>` also answers from (the hint in its error, `retired` in its JSON, `null` for an
  address with no entry); no name is retired yet.
```

The README gets no line.

- [ ] **Step 2: Regenerate the golden docs and check they did not move**

Create `/tmp/xarch-1-2/regenerate_docs.py` (never committed):

```python
"""Write docs/{cli,web,xarch}/testing.md from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        if "/".join(file.path) == "testing.md":
            (root / "docs" / folder / "testing.md").write_text(file.template, encoding="utf-8")
            print(f"docs/{folder}/testing.md written")
```

Run:
```bash
uv run python -I /tmp/xarch-1-2/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
git status --short -- tests/bootstrap/corpora
```

Expected: three `written` lines, an empty `git diff`, and nothing under `tests/bootstrap/corpora`. If the diff is not
empty, read it and stop and report it with the diff: this step must not move them
(`git checkout -- docs/cli docs/web docs/xarch` restores them).

- [ ] **Step 3: Check no code names a retired name**

Run: `git grep -n "Retired(" -- xarch` and `git grep -n "^RETIRED" -- xarch`
Expected: the first prints nothing (no entry is built anywhere in `xarch/`); the second prints only
`xarch/modules/spec/domain/profile_keys.py:...:RETIRED: tuple[Retired, ...] = ()`.

- [ ] **Step 4: Run the gates**

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
timeout 1200 uv run pytest -q > /tmp/xarch-1-2/final-pytest.txt 2>&1 &
echo $! > /tmp/xarch-1-2/final-pytest.pid
```

Expected: the first four pass. When the recorded PID has exited, read `tail -5 /tmp/xarch-1-2/final-pytest.txt`: all
green, more passed than the baseline of Task 1, Step 1, and no test of the baseline failing. Any failure is this
step's to fix.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
The CHANGELOG says a key, a guard or a rule id xarch has retired is refused with a fixed hint naming what to write instead, one problem per retired name, from one table profile explain also answers from, and that no name is retired yet; the golden docs regenerate unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

`git status --short` before the commit must show only `CHANGELOG.md` staged (and the untracked spec and plan under
`docs/superpowers/`, which are not added).

---

## Self-review against the spec

- Rules 1-4 (one table, kinds not told apart, empty, one lookup read at call time): Task 1 (`Retired`, `RETIRED`,
  `RULE_ID`, `retired`, `retired_at`; the domain tests 13 and 14).
- Rule 5 (mappings), rule 6 (top level), rule 7 (each scope its own, the `flagged`/`clean` call with none), rule 8
  (rule ids, own ids), rule 9 (guards, `package_only` first: the `kind is PackageOnly` branch stays ahead), rules
  10-12 (known wins, fixed text, no alias: the profile does not load): Task 2, and Task 3's `profile check` test.
- Rules 13-15 (`profile explain`): Task 3; the address forms in Task 1's `retired_at` tests.
- Rules 16-18 (docs): Task 4.
- Error paths: the three kinds in one `InvalidArchitecture` (Task 2,
  `test_the_file_gives_its_retired_keys_then_the_only_unknown_then_the_missing`); "must be a mapping" (Review Focus
  2); a non-string key (Review Focus 1); explain with a profile that does not load (Review Focus 5).
- Spec tests 1-14 and 16-18 each have a test; 15 is split as the Deviations section says.
<!-- task-pipeline: validated -->
