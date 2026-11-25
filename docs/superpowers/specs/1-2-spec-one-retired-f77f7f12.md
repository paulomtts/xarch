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
