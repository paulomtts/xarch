# 2.3 The rule id `rules` becomes `may-import`

Card `ba13344f`, subtask of `9caa480b`. Release step 4 of the 0.3.0 merged order. Stacked on step 3 (card `68d678bc`,
`forbidden` becomes `uses: {never: <list>}`, branch tip `c86dddc`), whose table of retired names holds seven entries
(`xarch/modules/spec/domain/profile_keys.py:158-166`), one of them the retired rule id
`Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use")` (163).

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`. `KN` is `key-names-design.md`, `R3` is
`0.3.0-cohesion-review-3.md`.

- KN line 17, ruling 2: the rule id `rules` becomes `may-import`, in the same release.
- KN 1.4, lines 189-195: why (`hints` keys are profile-facing), what it touches (`RULES`, the README id list,
  `expansion.py:106-118`, the book entry, the generated docs line "`rules`: every import between parts ..." which becomes
  "`may-import`: ...", the golden copies, the rule field of every recorded `rules` finding), and that after the rename a
  check of the profile's own may take the ids `rules` and `forbidden`, and may not take `may-import` or `never-use`. The
  filter `may-import-everything` keeps its name.
- KN 1.4, lines 182-187: what a rule id rename touches in general (the README list a test pins, the JSON `rule` field,
  `hints` keys, the ids an own check may not take).
- KN 2, lines 296-299: `may-import` beside the key and the filter is one idea in three spellings; the README already
  states that rule ids are kebab and keys snake (not re-said here).
- KN 3, lines 312-313 (item 4: `expansion.py:106-118`, `docs_template.py:403` and the book entry for `may-import`),
  323 (item 11, README rule table and id list), 325-326 (item 12, CHANGELOG).
- KN 4, line 349: the refusal word for word, `hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import;
  use ...`. Lines 357-363: one table, `rule_hints` reads its rule-id part.
- KN 5 item 4, lines 386-387: the scope of this step, "tests first for `hints.rules` refused". Lines 370-373: the gates.
  Lines 390-395: at the end of release step 5, `grep -rn '"rules"'` returns only the retired rule-id entry and its test
  (step 5's check; this step must leave nothing for it but the internal names 2.4 owns).
- KN "Dodges", lines 413-414 and 421: leaving `rules` in `RULES` beside `may-import`, accepting `hints.rules` as an alias,
  regenerating the golden copies without reading the diff, editing recorded findings by a blind replace.
- R3 section 2: O4, O5 (lines 228-229, README and CHANGELOG under `[Unreleased]`), O8 (232, golden docs regenerated, diff
  read, the `may-import` line named), O10 (234, the recorded findings' rule fields `rules`, reviewed line by line).
  R3 line 261: row 4 of the merged order, "the same files" as step 3.
- `tests/bootstrap/test_recorded_corpora.py:16-32`: how recorded findings may be edited (a change of wording by find and
  replace, diff read line by line; a change of order only by moving the recorded blocks by hand and showing the findings
  are the same; never dumping what the code under test finds).

## What is there now

At `c86dddc`:

- `RULES` (`xarch/kernel/violations.py:10-13`) holds `"rules"` first. `Violation.__post_init__` (32-36) refuses a
  violation whose rule is not in `RULES` (built-in) or is in `RULES` (own).
- Engine: `expansion._rules` (`xarch/modules/rules/application/logic/expansion.py:104-118`) builds `Rule("rules", ...)`
  for each part (114, `key=f"parts.{part}.may_import"`) and one for the structure (117). The book entry `"rules"` (366)
  is read by `source_check.py:88` (`book["rules"]`). `imports.py:3` names "the "rules" rules of expansion.book".
  `ordered.py:11` sorts violations by `(file, line, rule)`.
- Key table (`xarch/modules/spec/domain/key_table.py`): `Key(PROFILE, "parts", True, rules=("structure", "rules"), ...)`
  (54), `Key(PART, "path", True, rules=("structure", "rules"))` (69), `Key(PART, "may_import", rules=("rules",))` (72).
  These feed `profile explain`'s "enforced: yes, by the rule `rules`" and its JSON `rules`.
- `keys.yaml` (`xarch/architectures/presets/format/keys.yaml:239-240`): the `hints` example is
  `hints:\n  rules: Ask the maintainer before adding an import.`
- `rule_hints` (`xarch/modules/spec/application/logic/profile_checks.py:330-343`): the non-mapping problem's example is
  `{rules: see the docs}` (333); an unknown id gets `advice(RULE_ID, ...)` (338), which reads `RETIRED`.
- `written_checks.py:72`: an own check whose id is in `RULES` is refused.
- `docs_template.py:403`: the generated testing doc's line "`rules`: every import between parts is one that the
  `may_import` of the importing part allows (architecture.md, section 5)."
- Golden docs: that line at `docs/cli/testing.md:339`, `docs/web/testing.md:340`, `docs/xarch/testing.md:155`.
- README: rule table row `rules` (269), the rule id list (358, pinned to `RULES` by
  `tests/architecture/test_readme.py:29-31`). README 191-194 name `"rules"` as JSON fields of `profile explain`: not the id.
- CHANGELOG `[Unreleased]`, "Changed": four entries, the last the `uses.never` one.
- Recorded findings (`[kind, rule, file, line, message, fix]`):
  - `tests/bootstrap/corpora/7cc6111.json`: 201 findings, 31 of them `["V", "rules", ...]`. Renaming the rule moves no
    finding in the `(file, line, rule)` order (checked).
  - `tests/bootstrap/corpora/stress-7cc6111.json.xz`: 1735 findings, 31 of them `["V", "rules", ...]`. Renaming moves
    findings: at `xarch/modules/rules/contract/__init__.py:8` and `xarch/modules/spec/contract/__init__.py:7` a block of
    `package-only` findings sits before a block of `rules` findings (for instance indices 1514-1532 `package-only`, then
    1533-1551 `rules` at the spec one); `may-import` sorts before `package-only`, so each `rules` block moves ahead of
    its `package-only` block, each block's inner order kept (31 findings each way, 62 positions).
  - `df537ca.json`, `examples-cli.json`, `examples-web.json`: no finding of rule `rules`.
  - No message or fix of any recorded finding names the rule id (no `(rules)` tag); the word `rules` appears in texts
    and file fields hundreds of times as the name of the module `modules/rules` (967 findings in the stress corpus).
- `key_lookup.retired_at` (42-48): a rule id has no address; `profile explain rules` is not a rule-id lookup
  (`test_retired_keys.py:153-154` pins it).

## Required behavior

1. **`RULES`.** `RULES` holds `"may-import"` in the place `"rules"` held (first), and does not hold `"rules"`. No alias.
2. **Findings.** Every finding of the import rule (a part's `may_import` and the structure's import rule) has rule
   `may-import`: in `--format json`'s `rule`, in `hints` lookup, wherever the rule id is printed. Message and fix texts
   are unchanged, including the key `(parts.<p>.may_import)` in the fix. Findings are ordered by `(file, line, rule)` with
   the new id, so on a line holding a `may-import` and a `package-only` finding the `may-import` one now comes first.
3. **Engine names that are lookups.** The two `Rule(...)` ids are `"may-import"`; the book entry is `"may-import"` and
   `source_check` reads `book["may-import"]` (as step 3 renamed the book entry `forbidden` to `never-use`). The docstring
   of `imports.py` names the `"may-import"` rules of `expansion.book`. `explained`/`--rule` output of
   `profile explain parts.may_import --rule` shows rules with id `may-import`.
4. **Key table.** `rules=("structure", "may-import")` on `parts` and `parts.<part>.path`, `rules=("may-import",)` on
   `parts.<part>.may_import`. `profile explain parts.may_import` prints "enforced: yes, by the rule `may-import`" and its
   JSON `rules` field lists `may-import`. The key `may_import` and the filter `may-import-everything` keep their names.
5. **`hints`.**
   - `hints: {may-import: <text>}` is accepted; its text follows the fix of every `may-import` finding, in text and JSON.
   - `hints: {rules: <text>}` is refused: `hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import; use
     <RULES sorted, then the profile's own ids>`, from a new table entry (6), with the exit code of a profile that does
     not load. The text written under it is not shown.
   - A profile with an own check whose id is `rules` and `hints: {rules: ...}` loads: the hint is that check's.
   - The non-mapping problem reads `hints: must be a mapping of rule ids to one line of text, such as {may-import: see the
     docs}`.
   - The `keys.yaml` example of `hints` reads `may-import: Ask the maintainer before adding an import.` and still loads.
6. **Retired table.** `RETIRED` gains one entry, appended after the seven of step 3:
   `Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import")`. The refusal comes from the table through
   `rule_hints`; no code tests for the name `rules`.
7. **Own checks.** A check of the profile's own may take the id `rules` (and `forbidden`, as since step 3); one named
   `may-import` is refused: `checks.may-import: may-import is the id of a check xarch has: give your check an id of its
   own, such as my-may-import`.
8. **`profile explain`.** Unchanged in what it accepts: a rule id has no address, so `profile explain rules` answers as
   before this step (no new `retired` answer). `profile explain hints` shows the new example.
9. **Generated docs.** The template line reads "`may-import`: every import between parts is one that the `may_import` of
   the importing part allows (architecture.md, section 5)." The golden copies are regenerated (as step 3 did,
   `build_controllers().spec.docs(<profile>)` for `cli`, `web` and `architecture.yaml`, written over `docs/cli/`,
   `docs/web/`, `docs/xarch/`), never edited by hand, and the diff read: exactly three lines move,
   `docs/cli/testing.md:339`, `docs/web/testing.md:340`, `docs/xarch/testing.md:155`. Any other moved line is a bug of
   this step to report, not to hand-edit.
10. **Recorded findings**, by hand, never by running the code under test:
    - `7cc6111.json`: the rule field of each of the 31 `rules` findings becomes `may-import`. Nothing else changes; the
      order stays.
    - `stress-7cc6111.json.xz`: unpacked; the rule field of each of the 31 `rules` findings becomes `may-import`; then,
      at `xarch/modules/rules/contract/__init__.py:8` and `xarch/modules/spec/contract/__init__.py:7`, the block of
      `may-import` findings is moved ahead of the block of `package-only` findings at the same place, each block's
      findings and inner order kept, the file's layout (one value per line) kept; repacked as xz. The size of the
      archive may change.
    - The edit touches only the second element of a finding whose value is exactly `"rules"`; no text, file field or
      other finding moves. Shown for each file: the unpacked diff holds only those rule-field lines and the two block
      moves, and the multiset of findings before (with `rules` read as `may-import`) equals the one after.
    - `df537ca.json`, `examples-*.json`, every `.yaml` corpus and every `.tar.xz` archive: unchanged.
11. **README** (under no heading change): the rule table row reads `may-import`; the rule id list (358) reads
    `may-import` first, in `RULES`' order. The JSON field names `"rules"` of `profile explain` (191-194) stay.
12. **CHANGELOG**, under `[Unreleased]`, "Changed", one entry after the `uses.never` one: the rule id `rules` is
    renamed `may-import`, in findings, in JSON and under `hints`; `hints.rules` is refused with "renamed in 0.3.0: write
    may-import"; a check of the profile's own may now take the id `rules`; on a line with findings of both, `may-import`
    findings now come before `package-only` ones. Finding and fix texts are unchanged.

## Error paths

| Input | Result |
|---|---|
| `hints: {rules: see the docs}` | `<file>: hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import; use <ids>` |
| `hints: {rules: secret text}` | the same problem; `secret text` appears in no output |
| `hints: {rules: x}` with own check `rules` | loads; the hint is for the own check |
| `hints: {may-import: x}` | loads; `hint: x` after each `may-import` fix |
| `hints: []` | `hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}` |
| own check `may-import` | `checks.may-import: may-import is the id of a check xarch has: give your check an id of its own, such as my-may-import` |
| own check `rules` | loads |
| `Violation(..., "rules", ...)` built-in | `ValueError` "a violation names an unknown rule 'rules': ..." |

`<ids>` is `', '.join(sorted(RULES))` plus own ids, so `may-import` sits between `libraries` and `must-import`.

## Tests that prove it

Tiers follow `docs/xarch/testing.md`: `tests/kernel/` and `tests/modules/**/logic/` and `tests/modules/spec/domain/` are
unit (pure values and parsing, no files); `tests/modules/*/application/` drive a service with fakes; `tests/cli/` the
renderers; `tests/bootstrap/` loads real profile files, runs the CLI and the recorded corpora; `tests/architecture/` the
repo's own guards.

Written first, failing on the parent branch:

1. Unit, `tests/modules/spec/application/logic/test_hints.py` (beside the `hints.forbidden` test in `test_forbidden.py:
   275-278`, either home): `hints: {rules: "see the docs"}` gives exactly the one problem of the error table; the value
   written appears in no problem; `hints: {rules: x}` with an own check `rules` loads with that hint. Unit because it
   parses a document in memory.
2. Unit, `tests/modules/spec/domain/test_profile_keys.py`: the shipped table is exactly the eight entries (the seven of
   step 3, then the new one); the generic assertions hold (`rules` is no longer in `RULES`, so the entry names no live
   rule id).
3. Unit, `tests/modules/spec/application/logic/test_retired_keys.py`: `retired(RULE_ID, "rules")` gives "renamed in
   0.3.0: write may-import"; the rule-id "use" list constant follows `RULES`.
4. Unit, `tests/kernel/test_violations.py`: `may-import` is a rule id, `rules` is not; a built-in violation of rule
   `rules` raises.
5. Unit, `tests/modules/spec/application/logic/test_written_checks.py` (beside 114-116): an own check `may-import` is
   refused with the error-table text; one named `rules` loads.
6. Unit, `tests/modules/rules/application/logic/test_expansion.py` and `checks.py`: the book entry is `may-import` and
   its rules have id `may-import`; `test_ordered.py`: a `may-import` and a `package-only` finding at one file and line
   come `may-import` first.
7. Unit, `tests/modules/spec/application/logic/test_docs_template.py`: the guards line begins "`may-import`: every import
   between parts is one that the `may_import` of the importing part allows".
8. Bootstrap, `tests/bootstrap/test_profile_explain.py:36-41`: "enforced: yes, by the rule `may-import`".
9. Bootstrap, `tests/bootstrap/test_check_json.py`: the JSON finding has rule `may-import`; `with_hints` writes
   `may-import:` and the pair reads `("may-import", ...)`; a profile file on disk writing `hints: {rules: ...}` is
   refused with the refusal word for word (proves the wiring through the loader).

Edited in place (no assertion loosened to "unknown rule id" in output):

10. Every test that builds a `Violation` or a `Rule` with id `"rules"`, or asserts the id, reads `"may-import"`: among
    them `tests/cli/reports/test_report.py:25-26, 49`, `tests/bootstrap/test_rule_ids.py`, `test_presets.py`,
    `test_needs_agree.py`, `test_written_rules.py`, `test_bundled_guards.py`, `test_profile_explain_words.py`,
    `tests/modules/rules/application/logic/{test_enforcement,test_imports,test_ordered,test_where,test_verdict}.py`,
    `tests/modules/rules/application/test_check_app.py`, `tests/modules/rules/adapters/test_spec_profile.py`,
    `tests/modules/spec/application/{test_explain,origins,test_profile_loading,test_examples}.py`,
    `tests/modules/spec/application/logic/{test_explain,test_hints}.py`, and the `{rules: see the docs}` example at
    `tests/bootstrap/test_architecture_files.py:165` and `test_hints.py:26-28`. `KNOWN` in `test_hints.py:22` swaps its
    own token. Each hit of `grep -rnE "[\"'\`]rules[\"'\`]" tests` is judged one by one: the module or part named `rules`
    (for instance `test_self_check.py:57`, `test_language_seam.py`, `test_profile_new.py:65`), the JSON field `rules` of
    `profile explain` (`test_vocabulary_report.py`, `test_report.py` fields), and the string in
    `test_violations_say_what_to_do.py:32-34` (a parse of source text, not validated) stay.
11. `test_key_catalogue.py` and `test_needs_agree.py` pass with the key table and `keys.yaml` changed in one commit.
12. Bootstrap: `test_recorded_corpora.py` passes against the hand-edited recordings; `test_docs_templates.py` against the
    regenerated golden docs; `tests/architecture/test_readme.py` against the README id list.

## Out of scope

- Internal identifiers (card 2.4, release step 5): `expansion._rules`, `Architecture.rules`, `Profile.rules`, the
  `rules_table` placeholder, `where.py:9`'s "(its `rules`)", the module and part `modules/rules`, `RulesController`.
- The JSON field `rules` of `profile explain` and `vocabulary_report` (a count or list of rules, not the id).
- The key `may_import` and the `imports` group (release step 13); the filter `may-import-everything` (keeps its name).
- `docs/examples/` and the `Violation(one.place, "rules", ...)` sample it puts into `docs/xarch/architecture.md:405`
  (placement example code, as in step 3); the `.tar.xz` archives; the 0.2.0 CHANGELOG entry; English "rules" in prose.
- A `retired` answer of `profile explain` for a rule id (a rule id has no address).
- Ordering the CHANGELOG under a 0.3.0 lead and reading the README whole (release step 25).

## Gates

On this branch alone, each passing: `uv run pytest -q` (in the background, over two minutes, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

## Project rules for the planner

No comments in xarch's code (docstrings are fine); tests written first; examples simple, with absolute `app.` imports;
recorded corpora edited by hand only, as section 10 says; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; key table rows and `keys.yaml` in one commit; golden docs regenerated, never
hand-edited, diff read; README and CHANGELOG under `[Unreleased]`; `.claude/` stays out of commits; nothing is pushed.

## Review focus (for the planner)

1. A blind replace of `rules` in the recordings, the tests or the code: it would rewrite `modules/rules` in file fields
   and texts (967 stress findings), the JSON field `rules`, or internal names of 2.4.
2. The stress recording edited in the rule field only, leaving the two blocks out of order; or re-dumped from the code
   under test to fix the order.
3. `rules` left in `RULES` beside `may-import`, or `hints.rules` accepted silently or as an alias.
4. The book entry renamed and `source_check` still reading `book["rules"]` (a `KeyError` at check time, not at load).
5. The golden docs regenerated with more than the three lines moved, or the line hand-edited.

---

# 2.3 The rule id `rules` becomes `may-import` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The import rule's id is `may-import` everywhere a rule id is read or printed (findings, JSON, `hints`, the
key table, `profile explain`, the generated docs, the README), `hints.rules` is refused through the table of retired
names, a check of the profile's own may take the id `rules`, and the recorded findings are edited by hand to match.

**Architecture:** One string in `RULES` changes in place (first), and every lookup that names it follows: the two
`Rule(...)` ids of `expansion._rules`, the book entry and `source_check`'s read of it, the key table's `rules=`
tuples, the `keys.yaml` example and the non-mapping `hints` problem. The refusal of `hints.rules` is one new entry of
`RETIRED`, read by `rule_hints` through `advice` as step 3's `forbidden` entry is. The template line of the generated
testing doc changes and the golden docs are regenerated. The recordings are edited by a throwaway script that touches
only the rule line of each `rules` finding and swaps two blocks of the stress recording, proved by a multiset check.
Internal names (`expansion._rules`, `Profile.rules`, the module `modules/rules`, the test helper `checks.rules`) keep
their names: that is step 2.4.

**Tech Stack:** Python 3.13, pytest, typer (CLI), PyYAML; run everything through `uv run`.

**Spec:** `docs/superpowers/specs/2-3-rules-the-rule-id-ba13344f.md` (copied above this line).

## Global Constraints

- `RULES` begins `("may-import", "libraries", "never-use", "tiers", ...`: `"may-import"` stands where `"rules"` stood,
  and `"rules"` is in it nowhere. No alias anywhere.
- `RETIRED` holds exactly the seven entries of step 3, in their order, then
  `Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import")`. No code tests for the name `rules`.
- The texts, word for word:
  - `hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import; use <ids>`, `<ids>` being
    `', '.join(sorted(RULES))` (plus own ids, all sorted together by `advice`).
  - `hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}`
  - `checks.may-import: may-import is the id of a check xarch has: give your check an id of its own, such as my-may-import`
  - the `keys.yaml` example of `hints`: `hints:\n  may-import: Ask the maintainer before adding an import.`
  - the generated docs line: ``- `may-import`: every import between parts is one that the `may_import` of the importing
    part allows (architecture.md, section 5).``
  - `profile explain parts.may_import`: `enforced: yes, by the rule `may-import``; its JSON `rules` is `["may-import"]`.
- The sorted rule ids of the day: `built-by, closed-tree, cycles, dead-code, holds, immutable, libraries, may-import,
  must-import, names, never-use, no-callbacks, no-comments, no-duplicates, no-twins, package-only, pass-through,
  private-imports, scenario-coverage, shared, stand-ins, structure, syntax, test-tree, tiers, types-only`.
- Message and fix texts of findings are unchanged, the key `(parts.<p>.may_import)` in the fix included.
- Stays as it is: the key `may_import`, the filter `may-import-everything`, `expansion._rules`, `Architecture.rules`,
  `Profile.rules`, `where.py:9`, the `rules_table` placeholder, the module and part `modules/rules`, `RulesController`,
  the test helper `checks.rules`, the JSON field `rules` of `profile explain` and `vocabulary_report`, README 191-194,
  `docs/examples/` and `docs/xarch/architecture.md:405`, the `.tar.xz` archives, the 0.2.0 CHANGELOG entry, English
  "rules" in prose, role texts `"role": "rules"`, file and module paths holding `rules`.
- No comments in xarch's code (docstrings are fine). Tests first (RED before GREEN). `ruff check` is never run with
  `--fix`. Lines at most 140 columns (`ruff.toml`); README and CHANGELOG wrap at 120.
- Recorded findings are edited by the throwaway script of Task 1, never by running the code under test; the diff and
  the multiset check are read.
- The key table rows and the `keys.yaml` entry change in one commit (Task 1).
- Golden docs (`docs/cli/`, `docs/web/`, `docs/xarch/`) are regenerated by the script of Task 3, never hand-edited;
  exactly three lines move, any other moved line is reported, not edited.
- README and CHANGELOG lines go under `[Unreleased]`; `.claude/` and `docs/superpowers/` are never added by the
  engineer's commits; nothing is pushed.
- Never `pkill`/`killall`/`kill` by pattern; wrap long runs in `timeout` or stop them by the PID you recorded.
- Every commit message ends with the attribution line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  (if your harness gives you a different attribution line, use that one instead).

## Review Focus

1. A blind replace of `rules` (in tests, code or recordings) that rewrites the module `modules/rules`, a role text, the
   JSON field `rules` or an internal name. Every edit below is addressed by line and string; Task 1 Step 10 greps
   what is left and lists each hit that must stay. The recordings' script touches only a line that is exactly
   `"rules",` in the rule position of a finding, and the multiset check of Task 1 Step 8 proves no text moved.
2. The stress recording edited in the rule field only, leaving the two blocks out of `(file, line, rule)` order. Test:
   `tests/modules/rules/application/logic/test_ordered.py::test_a_may_import_finding_comes_before_a_package_only_finding_at_the_same_line`
   (Task 1), Task 1 Step 8's `blocks.py` and `sorted.py`, and `test_recorded_corpora.py`.
3. `hints: {rules: ...}` accepted (an alias) or refused without the hint, or the text written under it echoed. Tests:
   Task 2, `test_a_hint_for_the_rule_id_rules_is_told_it_is_renamed_may_import`,
   `test_the_text_written_under_hints_rules_is_in_no_problem`, and the loader-wired
   `test_a_profile_with_a_hint_for_the_rule_id_rules_is_refused_with_its_new_name_and_not_its_text`.
4. The book entry renamed but `source_check` still reading `book["rules"]` (a `KeyError` at check time, not at load).
   Test: Task 1, `tests/bootstrap/test_check_json.py` and `tests/bootstrap/test_rule_ids.py` run the real check through
   `source_check` and expect rule `may-import`.
5. A profile whose own check is named `rules` and carries a hint: the own id must win over the retired entry (loads,
   hint kept). Test: Task 1, `test_a_hint_for_a_check_of_its_own_named_rules_is_the_hint_of_that_check`, which Task 2
   must keep green after the entry lands.

---

## File map

- `xarch/kernel/violations.py` — `RULES` (Task 1).
- `xarch/modules/rules/application/logic/expansion.py` — the two `Rule("rules", ...)` ids and the book entry (Task 1).
- `xarch/modules/rules/application/services/source_check.py` — `book["may-import"]` (Task 1).
- `xarch/modules/rules/application/logic/imports.py` — docstring (Task 1).
- `xarch/modules/spec/domain/key_table.py` — three `rules=` tuples (Task 1).
- `xarch/architectures/presets/format/keys.yaml` — the `hints` example (Task 1).
- `xarch/modules/spec/application/logic/profile_checks.py` — the non-mapping `hints` problem (Task 1).
- `xarch/modules/spec/domain/profile_keys.py` — `RETIRED` (Task 2).
- `xarch/modules/spec/application/logic/docs_template.py` — the guards line; golden docs (Task 3).
- Recordings: `tests/bootstrap/corpora/7cc6111.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz` (Task 1).
- `README.md` (Task 1 the id list, Task 4 the rule table row), `CHANGELOG.md` (Task 4).

Throwaway files live in `/tmp/xarch-2-3/` and are never committed.

---

### Task 1: The rule id `may-import`

Everything that names the rule id changes together: once `RULES` changes, every test that builds a `Violation` of
rule `rules`, the README id list, `hints` of `rules` and the recorded corpora break at once, so they move in one commit.
The key table rows and the `keys.yaml` example move in the same commit, as the project requires.

**Files:**
- Modify: `xarch/kernel/violations.py:10`
- Modify: `xarch/modules/rules/application/logic/expansion.py:114, 117, 366`
- Modify: `xarch/modules/rules/application/services/source_check.py:88`
- Modify: `xarch/modules/rules/application/logic/imports.py:3`
- Modify: `xarch/modules/spec/domain/key_table.py:54, 69, 72`
- Modify: `xarch/architectures/presets/format/keys.yaml:240`
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:333`
- Modify: `README.md:358-359`
- Modify (by the script below): `tests/bootstrap/corpora/7cc6111.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz`
- Test: `tests/kernel/test_violations.py`, `tests/modules/rules/application/logic/test_ordered.py`,
  `tests/modules/spec/application/logic/test_written_checks.py`, `tests/modules/spec/application/logic/test_hints.py`,
  `tests/modules/rules/application/logic/test_expansion.py`, `tests/modules/rules/application/logic/checks.py`,
  `tests/modules/rules/application/logic/test_imports.py`, `tests/modules/rules/application/logic/test_enforcement.py`,
  `tests/modules/rules/application/logic/test_verdict.py`, `tests/modules/rules/application/test_check_app.py`,
  `tests/modules/rules/adapters/test_spec_profile.py`, `tests/cli/reports/test_report.py`,
  `tests/modules/spec/application/test_explain.py`, `tests/modules/spec/application/logic/test_explain.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_docs.py`, `tests/bootstrap/test_architecture_files.py`,
  `tests/bootstrap/test_profile_explain.py`, `tests/bootstrap/test_profile_explain_words.py`,
  `tests/bootstrap/test_check_json.py`, `tests/bootstrap/test_rule_ids.py`, `tests/bootstrap/test_presets.py`
- Throwaway: `/tmp/xarch-2-3/recorded.py`, `/tmp/xarch-2-3/same.py`, `/tmp/xarch-2-3/blocks.py`,
  `/tmp/xarch-2-3/sorted.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `RULES[0] == "may-import"`, `"rules" not in RULES`; `expansion.book(profile)["may-import"]` (the group
  renamed from `"rules"`, same place in the dict); key table `rules=("structure", "may-import")` on `parts` and
  `parts.<part>.path`, `rules=("may-import",)` on `parts.<part>.may_import`.

- [ ] **Step 1: Write the new failing tests**

`tests/kernel/test_violations.py`: replace the last test (lines 35-39) by:
```python
def test_the_rule_ids_are_the_stable_ids_of_every_check():
    assert sorted(RULES) == ["built-by", "closed-tree", "cycles", "dead-code", "holds", "immutable", "libraries",
                             "may-import", "must-import", "names", "never-use", "no-callbacks", "no-comments",
                             "no-duplicates", "no-twins", "package-only", "pass-through", "private-imports",
                             "scenario-coverage", "shared", "stand-ins", "structure", "syntax", "test-tree", "tiers",
                             "types-only"]


def test_the_import_rule_is_may_import_first_and_a_built_in_violation_of_rule_rules_cannot_be_made():
    with pytest.raises(ValueError, match="unknown rule") as caught:
        Violation("app/a.py", 3, "a problem", "rules", "do this")
    assert str(caught.value) == "a violation names an unknown rule 'rules': use one of " + ", ".join(sorted(RULES))
    assert (RULES[0], "rules" in RULES) == ("may-import", False)
```

`tests/modules/rules/application/logic/test_ordered.py`, at the end:
```python
def test_a_may_import_finding_comes_before_a_package_only_finding_at_the_same_line():
    package_only = Violation("app/a.py", 3, "imported only as a package", "package-only", "import the package")
    assert ordered([package_only, A]) == (A, package_only)
```

`tests/modules/spec/application/logic/test_written_checks.py`, at the end:
```python
def test_a_check_of_its_own_may_not_take_the_id_may_import_and_may_take_rules_which_xarch_no_longer_has():
    taken, free = read({"may-import": SMALL}), read({"rules": SMALL})
    assert taken == ({}, ["checks.may-import: may-import is the id of a check xarch has: give your check an id of its "
                          "own, such as my-may-import"])
    assert (list(free[0]), free[1]) == (["rules"], [])


def test_a_hint_for_a_check_of_its_own_named_rules_is_the_hint_of_that_check():
    architecture = parsed(layered(checks={"rules": SMALL}, hints={"rules": "see the docs"}))
    assert (list(architecture.checks), architecture.hints) == (["rules"], {"rules": "see the docs"})
```

`tests/bootstrap/test_profile_explain.py`, after `test_a_key_is_explained_with_what_it_accepts_...` (after line 41):
```python
def test_the_example_of_hints_gives_advice_for_the_rule_may_import():
    result = runner.invoke(app, ["profile", "explain", "hints"])
    assert result.exit_code == 0, result.output
    assert "      may-import: Ask the maintainer before adding an import." in result.output.splitlines()
```

`tests/bootstrap/test_profile_explain_words.py`, at the end:
```python
def test_a_part_s_may_import_expands_to_the_rules_may_import():
    listed = explain("parts.may_import", "--rule", "--profile", "web")
    assert listed.exit_code == 0, listed.output
    assert listed.output.splitlines()[0] == "parts.may_import expands to 12 rules in web, written as checks:"
    assert "  may-import-domain:" in listed.output.splitlines() and "  rules-domain:" not in listed.output.splitlines()
```

- [ ] **Step 2: Edit in place the tests that name the rule id**

Each edit is by line and string. Do not run a replace over whole files.

`tests/kernel/test_violations.py` lines 8, 9, 20, 26: the fourth argument `"rules"` becomes `"may-import"`; line 21:
```python
    assert str(caught.value) == "a violation of rule 'may-import' at app/a.py:3 has no fix: say what to do about it"
```
```bash
sed -i -e '8,9s/"a problem", "rules", "do this"/"a problem", "may-import", "do this"/' \
  -e '20s/"a problem", "rules", fix/"a problem", "may-import", fix/' \
  -e "21s/rule 'rules' at/rule 'may-import' at/" \
  -e '26s/"a problem", "rules")/"a problem", "may-import")/' tests/kernel/test_violations.py
```

`tests/modules/rules/application/logic/test_ordered.py` lines 5, 6, 17: `"rules"` becomes `"may-import"`:
```bash
sed -i -e '5,6s/, "rules", /, "may-import", /' -e '17s/, "rules", /, "may-import", /' \
  tests/modules/rules/application/logic/test_ordered.py
```

`tests/cli/reports/test_report.py`:
```bash
sed -i -e '25,26s/, "rules", /, "may-import", /' -e '49s/{"rules": /{"may-import": /' \
  -e '80s/{"rules": /{"may-import": /' -e '83s/{"rule": "rules", /{"rule": "may-import", /' \
  tests/cli/reports/test_report.py
```

`tests/modules/rules/application/logic/test_enforcement.py:172`, `test_verdict.py:8`:
```bash
sed -i '172s/"m", "rules", "f"/"m", "may-import", "f"/' tests/modules/rules/application/logic/test_enforcement.py
sed -i '8s/"a problem", "rules", "do this"/"a problem", "may-import", "do this"/' tests/modules/rules/application/logic/test_verdict.py
```

`tests/modules/rules/application/logic/test_imports.py:79`:
```python
    assert [v.rule for v in found] == ["may-import"]
```

`tests/modules/rules/application/test_check_app.py` lines 40, 60, 63, 69 (`hints={"rules": ...}` and
`{"rules": "ask first"}`) and 43 (the rule of `IMPORT`):
```bash
sed -i -e '40s/hints={"rules": /hints={"may-import": /' -e '43s/(pkg.platform.io)", "rules",/(pkg.platform.io)", "may-import",/' \
  -e '60s/{"rules": "ask first"}/{"may-import": "ask first"}/' -e '63s/{"rules": "ask first"}/{"may-import": "ask first"}/' \
  -e '69s/{"rules": "ask first"}/{"may-import": "ask first"}/' tests/modules/rules/application/test_check_app.py
```

`tests/modules/rules/adapters/test_spec_profile.py` lines 61 and 123: `hints={"rules": "ask first"}` becomes
`hints={"may-import": "ask first"}`:
```bash
sed -i -e '61s/hints={"rules": /hints={"may-import": /' -e '123s/hints={"rules": /hints={"may-import": /' \
  tests/modules/rules/adapters/test_spec_profile.py
```

`tests/modules/rules/application/logic/test_expansion.py:38-39`:
```python
    pytest.param("may-import", [*(f"may-import: app/{p} read import-into-app may_only permitted" for p in PROFILE.parts),
                                "may-import: app/structure read import-into-app may_only permitted"], id="may-import"),
```
and line 78:
```python
    assert {group for group, rules in expansion.book(OFF).items() if rules} == {"syntax", "may-import"}
```

`tests/modules/rules/application/logic/checks.py:49` (the helper keeps its name `rules`, step 2.4):
```python
    return checked(expansion.book(profile)["may-import"], profile, files, root=root)
```

`tests/modules/spec/application/test_explain.py:152`: `"parts.may_import", "parts.<part>", False, True, ("may-import",))`.

`tests/modules/spec/application/logic/test_explain.py:34`:
```python
    assert found is not None and found.rules == ("may-import",) and found.where == "parts.<part>"
```

`tests/modules/spec/application/logic/test_hints.py`: line 13 becomes
```python
    hints = {"stand-ins": "fakes live in tests/fakes", "may-import": "see docs/project/architecture.md"}
```
`KNOWN` (lines 22-24) becomes
```python
KNOWN = ("built-by, closed-tree, cycles, dead-code, holds, immutable, libraries, may-import, must-import, names, "
         "never-use, no-callbacks, no-comments, no-duplicates, no-twins, package-only, pass-through, private-imports, "
         "scenario-coverage, shared, stand-ins, structure, syntax, test-tree, tiers, types-only")
```
the parametrised table (lines 27-37) becomes
```python
@pytest.mark.parametrize("hints, problem", [
    pytest.param([], "hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}",
                 id="a list instead of a mapping"),
    pytest.param("rules", "hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}",
                 id="a string instead of a mapping"),
    pytest.param({"rulez": "x"}, f"hints.rulez: unknown rule id 'rulez': use {KNOWN}", id="an unknown rule id"),
    pytest.param({3: "x"}, f"hints.3: unknown rule id 3: use {KNOWN}", id="a rule id that is no text"),
    pytest.param({"may-import": ""}, "hints.may-import: must be one line of text", id="an empty hint"),
    pytest.param({"may-import": "two\nlines"}, "hints.may-import: must be one line of text", id="a hint of two lines"),
    pytest.param({"may-import": None}, "hints.may-import: must be one line of text", id="a hint that is no text"),
])
```
and the last test (lines 42-45) becomes
```python
def test_every_bad_hint_is_reported_at_once():
    assert problems(layered(hints={"nope": "x", "may-import": "", "cycles": "fine"})) == [
        f"layered.yaml: hints.nope: unknown rule id 'nope': use {KNOWN}",
        "layered.yaml: hints.may-import: must be one line of text"]
```

`tests/modules/spec/application/logic/test_profile_parsing_docs.py:143, 145`:
```bash
sed -i -e '143s/hints={"rules": "see the docs"}/hints={"may-import": "see the docs"}/' \
  -e '145s/{"rules": "see the docs"}/{"may-import": "see the docs"}/' tests/modules/spec/application/logic/test_profile_parsing_docs.py
```

`tests/bootstrap/test_architecture_files.py:165`:
```python
                  'hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}'],
```

`tests/bootstrap/test_profile_explain.py:39` (``"enforced: yes, by the rule `may-import`"``) and line 81
(`key["rules"] == ["may-import"]`, the field name `rules` stays):
```bash
sed -i -e '39s/by the rule `rules`/by the rule `may-import`/' -e '81s/key\["rules"\] == \["rules"\]/key["rules"] == ["may-import"]/' \
  tests/bootstrap/test_profile_explain.py
```

`tests/bootstrap/test_check_json.py`: line 46 `{"rule": "may-import", "file": "app/modules/docs/domain/clock.py", "line": 2,`;
line 85 `    text = (BUNDLED / "web.yaml").read_text() + "\nhints:\n  may-import: the layers are in docs/project/architecture.md\n"`;
line 102 `        ("may-import", "the layers are in docs/project/architecture.md"), ("never-use", None)]`:
```bash
sed -i -e '46s/{"rule": "rules", /{"rule": "may-import", /' -e '85s/\\n  rules: the layers/\\n  may-import: the layers/' \
  -e '102s/("rules", "the layers/("may-import", "the layers/' tests/bootstrap/test_check_json.py
```

`tests/bootstrap/test_rule_ids.py` lines 33-35 become
```python
    pytest.param({"kernel/x.py": "from app.platform import sql\n"}, {}, "may-import",
                 "import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to adapters/, which may import it",
                 id="may-import"),
```
and lines 83-84 become
```python
    pytest.param({"modules/docs/contract/ids.py": "from app.modules.docs.domain.values import Document\n"}, {}, "may-import",
                 id="may-import: a name the pattern does not match"),
```

`tests/bootstrap/test_presets.py:77`:
```python
    pytest.param(b"from shop.kernel import x\n", "may-import", id="an import the part's rules do not allow"),
```

Then check what is left:
```bash
git diff --stat -- tests
grep -rnE "[\"'\`]rules[\"'\`]" tests | grep -v corpora/
```
Expected hits, each one staying (they name the module or part `rules`, a role text, a folder, the JSON field `rules` of
`profile explain`/`vocabulary_report`, an unknown top-level key, a string value given instead of a mapping, a source
text parsed and never validated, or a check of the profile's own named `rules`):
`test_language_seam.py:323-324`, `test_architecture_files.py:242`, `test_self_check.py:57, 64`,
`test_profile_new.py:65`, `test_violations_say_what_to_do.py:32-34`, `test_needs_agree.py:90`,
`test_profile_explain.py:81` (the field `key["rules"]`), `test_profile_explain.py:82, 118`, `test_written_rules.py:85`,
`test_profile_explain_words.py:69`, `test_vocabulary_report.py:83, 95`, `tests/kernel/test_violations.py` (the new test's
`"rules"`), `test_where.py:256`, `test_hints.py:30` (the string `"rules"` given instead of a mapping),
`test_written_checks.py` (the new own-check tests), `test_profile_parsing.py:296, 310`,
`test_profile_parsing_tests.py:237`, `origins.py:5`, `test_tiers.py:251`, `test_examples.py:11`,
`test_profile_loading.py:14`, `test_example_imports.py:89`, and the three generated-docs lines
`test_bundled_guards.py:75`, `test_docs_template.py:256`, `test_libraries_and_guards.py:106` (Task 3). Any other hit is
an edit missed above: read it and decide by the same rule.

- [ ] **Step 3: Run the tests to see them fail**

```bash
timeout 900 uv run pytest -q -x --no-header -p no:randomly tests/kernel tests/cli/reports/test_report.py tests/modules tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_explain_words.py tests/bootstrap/test_check_json.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_presets.py tests/bootstrap/test_architecture_files.py 2>&1 | tail -15
```
(If `-p no:randomly` is refused as an unknown plugin, drop it.) Expected: FAIL — at collection or first test,
`ValueError: a violation names an unknown rule 'may-import': use one of ...` (a module-level `Violation` built with the
new id). Then without `-x`:
```bash
timeout 900 uv run pytest -q tests/kernel tests/cli/reports/test_report.py tests/modules tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_explain_words.py tests/bootstrap/test_check_json.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_presets.py tests/bootstrap/test_architecture_files.py 2>&1 | tail -40
```
Expected: many failures, among them `KeyError: 'may-import'` (the book), `('rules',) != ('may-import',)` (the key
table), the own check `may-import` loading and `rules` refused, the `hints` non-mapping text `{rules: see the docs}`,
`rules-domain:` where `may-import-domain:` is expected, the `hints` example `rules: Ask ...`.

- [ ] **Step 4: The rule id, the engine and the key table**

`xarch/kernel/violations.py:10`:
```python
RULES = ("may-import", "libraries", "never-use", "tiers", "types-only", "cycles", "package-only", "scenario-coverage",
```
(the three following lines unchanged).

`xarch/modules/rules/application/logic/expansion.py:114`:
```python
    found = [Rule("may-import", Scope(APP, part), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
```
line 117:
```python
    return (*found, Rule("may-import", Scope(APP, STRUCTURE), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
```
(line 118, the continuation, stays).
line 366:
```python
    return {"syntax": _syntax(profile), "may-import": _rules(profile), "libraries": _libraries(profile),
```

`xarch/modules/rules/application/services/source_check.py:88`:
```python
        found = run(book["syntax"], facts, rules) + run(book["may-import"], facts, rules) + run(book["libraries"], facts,
```
(line 89, `rules)`, stays).

`xarch/modules/rules/application/logic/imports.py:3`:
```python
rules of what a part may import are rules as data (the "may-import" rules of expansion.book)."""
```

`xarch/modules/spec/domain/key_table.py`:
```bash
sed -i -e '54s/rules=("structure", "rules")/rules=("structure", "may-import")/' \
  -e '69s/rules=("structure", "rules")/rules=("structure", "may-import")/' \
  -e '72s/rules=("rules",)/rules=("may-import",)/' xarch/modules/spec/domain/key_table.py
sed -n '54p;69p;72p' xarch/modules/spec/domain/key_table.py
```
Expected print:
```
    Key(PROFILE, "parts", True, rules=("structure", "may-import"), opens=PART),
    Key(PART, "path", True, rules=("structure", "may-import")),
    Key(PART, "may_import", rules=("may-import",)),
```

`xarch/architectures/presets/format/keys.yaml:240`:
```yaml
        may-import: Ask the maintainer before adding an import.
```

`xarch/modules/spec/application/logic/profile_checks.py:333`:
```python
        problems.append("hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}")
```

`README.md:358-359`, the rule id list the README test pins (re-wrapped so the line stays under 120 columns):
```
  rule, else `null`. `rule` is one of: `may-import`, `libraries`, `never-use`, `tiers` (a test's imports, or a test in
  no tier), `types-only`, `cycles`, `package-only`, `scenario-coverage`, `no-comments`, `stand-ins`, `closed-tree`,
```

Then:
```bash
grep -rnE "[\"'\`]rules[\"'\`]" xarch
```
Expected only: `xarch/cli/reports/vocabulary_report.py:9, 120, 127, 139`, `xarch/cli/reports/profile_report.py:6, 112,
147` (the JSON field and the plural noun), `xarch/modules/rules/application/logic/where.py:9` (step 2.4), and
`xarch/modules/spec/application/logic/docs_template.py:403` (Task 3).

- [ ] **Step 5: Run the tests of Step 3**

Same command as Step 3 without `-x`. Expected: PASS, except `test_recorded_corpora.py` is not in it, and
`test_bundled_guards.py`, `test_docs_template.py`, `test_libraries_and_guards.py` still expect the `rules` line of
the generated docs — they pass, as the template is not changed yet.

- [ ] **Step 6: See the recorded corpora fail**

```bash
timeout 900 uv run pytest -q tests/bootstrap/test_recorded_corpora.py 2>&1 | tail -12
```
Expected: FAIL for `7cc6111` and the stress corpus, the first difference a finding whose rule is `may-import` (found)
against `rules` (recorded). `df537ca` and the examples pass.

- [ ] **Step 7: The script that edits the recordings by text**

Create `/tmp/xarch-2-3/recorded.py`:

```python
"""The findings of rule rules in a recording, by their text: the rule line becomes "may-import", and, where a block of
them sits after a block of package-only findings at the same file and line, the two blocks swap places, each kept
whole and in its order. No other line is touched. Prints how many rule lines it changed and how many blocks it moved."""
import lzma
import sys
from pathlib import Path


def spans(lines: list[str]) -> list[tuple[int, int]]:
    """The first and past-the-last line of each finding: `[`, kind, rule, file, line, message, fix, `]` or `],`."""
    found, start = [], None
    for i, line in enumerate(lines):
        if line == "[" and i > 1:
            start = i
        elif line in ("]", "],") and start is not None:
            found.append((start, i + 1))
            start = None
    return found


def edited(text: str) -> tuple[str, int, int]:
    lines = text.split("\n")
    findings = spans(lines)
    count = 0
    for start, end in findings:
        assert end - start == 8, lines[start:end]
        if lines[start + 2] == '"rules",':
            lines[start + 2] = '"may-import",'
            count += 1
    place = [(lines[s + 1], lines[s + 2], lines[s + 3], lines[s + 4]) for s, _ in findings]
    moved = 0
    i = 0
    while i < len(findings):
        kind, rule, file, line = place[i]
        j = i
        while j < len(findings) and place[j] == (kind, rule, file, line):
            j += 1
        k = j
        while k < len(findings) and place[k] == (kind, '"may-import",', file, line):
            k += 1
        if rule == '"package-only",' and k > j:
            first, middle, last = findings[i][0], findings[j][0], findings[k - 1][1]
            before, after = lines[first:middle], lines[middle:last]
            assert before[-1] == "]," and after[-1] == "],", (before[-1], after[-1])
            lines[first:last] = after + before
            moved += 1
            findings = spans(lines)
            place = [(lines[s + 1], lines[s + 2], lines[s + 3], lines[s + 4]) for s, _ in findings]
            i = k
        else:
            i = j
    return "\n".join(lines), count, moved


path = Path(sys.argv[1])
if path.suffix == ".xz":
    with lzma.open(path, "rt", encoding="utf-8") as file:
        text, count, moved = edited(file.read())
    with lzma.open(path, "wt", encoding="utf-8") as file:
        file.write(text)
else:
    text, count, moved = edited(path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")
print(f"{path.name}: {count} findings renamed, {moved} blocks moved")
```

It reads each finding as the recordings lay it out (`[`, kind, rule, file, line, message, fix, `]`, one value per
line), changes only a rule line that is exactly `"rules",`, and swaps a `package-only` block with the `may-import`
block right after it at the same kind, file and line, whole lines only. A text or file field holding `rules`
(`modules/rules`, 967 findings in the stress recording) is never a rule line and is never touched.

Create `/tmp/xarch-2-3/same.py`:

```python
"""Before and after a recording's edit: the findings are the same (rule rules read as may-import), and the positions
whose finding moved, by place and rule."""
import json
import lzma
import sys
from collections import Counter


def load(path):
    return json.load(lzma.open(path, "rt")) if path.endswith(".xz") else json.load(open(path))


before, after = load(sys.argv[1]), load(sys.argv[2])
assert list(before) == list(after) == ["findings"]
renamed = [[f[0], "may-import" if f[1] == "rules" else f[1], *f[2:]] for f in before["findings"]]
print("same findings:", Counter(map(json.dumps, renamed)) == Counter(map(json.dumps, after["findings"])))
moved = [i for i, (one, other) in enumerate(zip(renamed, after["findings"])) if one != other]
print("positions moved:", len(moved))
print("moved at:", sorted(Counter((after["findings"][i][2], after["findings"][i][3], after["findings"][i][1])
                                  for i in moved).items()))
print("rule fields left 'rules':", sum(f[1] == "rules" for f in after["findings"]))
```

Create `/tmp/xarch-2-3/blocks.py`:

```python
"""Each moved block of the stress recording kept whole and in its order: the may-import block now stands where the
package-only block stood, and the package-only block right after it."""
import json
import lzma
import sys

before = json.load(lzma.open(sys.argv[1], "rt"))["findings"]
after = json.load(lzma.open(sys.argv[2], "rt"))["findings"]
renamed = [[f[0], "may-import" if f[1] == "rules" else f[1], *f[2:]] for f in before]
for package_only, may_import, size in ((1302, 1314, 12), (1514, 1533, 19)):
    print(after[package_only:package_only + size] == renamed[may_import:may_import + size],
          after[package_only + size:may_import + size] == renamed[package_only:may_import])
```

Create `/tmp/xarch-2-3/sorted.py`:

```python
"""Whether the violations of a recording are in order of file, line and rule, rule rules read as may-import."""
import json
import lzma
import sys

for path in sys.argv[1:]:
    data = json.load(lzma.open(path, "rt")) if path.endswith(".xz") else json.load(open(path))
    v = [f for f in data["findings"] if f[0] == "V"]
    key = [(f[2], f[3], "may-import" if f[1] == "rules" else f[1]) for f in v]
    print(path, len(v), "sorted with may-import:", key == sorted(key))
```

- [ ] **Step 8: Run it and read the diff**

```bash
mkdir -p /tmp/xarch-2-3/before
cp tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/stress-7cc6111.json.xz /tmp/xarch-2-3/before/
python3 -I /tmp/xarch-2-3/sorted.py /tmp/xarch-2-3/before/7cc6111.json /tmp/xarch-2-3/before/stress-7cc6111.json.xz
python3 -I /tmp/xarch-2-3/recorded.py tests/bootstrap/corpora/7cc6111.json
python3 -I /tmp/xarch-2-3/recorded.py tests/bootstrap/corpora/stress-7cc6111.json.xz
python3 -I /tmp/xarch-2-3/same.py /tmp/xarch-2-3/before/7cc6111.json tests/bootstrap/corpora/7cc6111.json
python3 -I /tmp/xarch-2-3/same.py /tmp/xarch-2-3/before/stress-7cc6111.json.xz tests/bootstrap/corpora/stress-7cc6111.json.xz
python3 -I /tmp/xarch-2-3/blocks.py /tmp/xarch-2-3/before/stress-7cc6111.json.xz tests/bootstrap/corpora/stress-7cc6111.json.xz
python3 -I /tmp/xarch-2-3/sorted.py tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/stress-7cc6111.json.xz
git diff -- tests/bootstrap/corpora/7cc6111.json | grep '^[-+]"' | sort | uniq -c
xz -dc /tmp/xarch-2-3/before/stress-7cc6111.json.xz > /tmp/xarch-2-3/stress-before.json
xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz > /tmp/xarch-2-3/stress-after.json
diff /tmp/xarch-2-3/stress-before.json /tmp/xarch-2-3/stress-after.json | grep '^[<>]' | wc -l
diff <(sed -n '10418,10611p' /tmp/xarch-2-3/stress-before.json) <(sed -n '10418,10611p' /tmp/xarch-2-3/stress-after.json) | head -40
git status --short -- tests/bootstrap/corpora
```
Expected:
- Before the edit: `7cc6111.json 90 sorted with may-import: True` and `stress-7cc6111.json.xz 1609 sorted with
  may-import: False` (the two blocks out of order).
- `7cc6111.json: 31 findings renamed, 0 blocks moved` and `stress-7cc6111.json.xz: 31 findings renamed, 2 blocks moved`.
- `same.py` on `7cc6111`: `same findings: True`, `positions moved: 0`, `rule fields left 'rules': 0`.
- `same.py` on the stress recording: `same findings: True`, `positions moved: 62`, moved at exactly
  `xarch/modules/rules/contract/__init__.py` 8 (`may-import` 12, `package-only` 12) and
  `xarch/modules/spec/contract/__init__.py` 7 (`may-import` 19, `package-only` 19), `rule fields left 'rules': 0`.
- `blocks.py`: two lines `True True`.
- After the edit both recordings print `sorted with may-import: True`.
- The `7cc6111.json` diff: exactly `31 -"rules",` and `31 +"may-import",`, nothing else.
- The stress line diff counts 372 changed lines (the 31 rule lines and the lines of the two swapped blocks, whose
  findings differ only in their message's dotted name); read the window printed: each hunk is a block's lines in
  their new place, and no line appears that is not in one of the two blocks.
- `git status` lists only the two recordings as modified; `df537ca.json`, `examples-cli.json`, `examples-web.json`,
  every `.yaml` corpus and every `.tar.xz` are unchanged.

If any expectation fails, restore with `git checkout -- tests/bootstrap/corpora` and report; do not adjust the
recording another way.

- [ ] **Step 9: Run the recorded corpora and the README test**

```bash
timeout 1200 uv run pytest -q tests/bootstrap/test_recorded_corpora.py tests/architecture/test_readme.py 2>&1 | tail -3
```
Expected: PASS.

- [ ] **Step 10: The whole suite and the checks**

```bash
mkdir -p /tmp/xarch-2-3
timeout 1500 uv run pytest -q > /tmp/xarch-2-3/task1-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-3/task1-pytest.pid
```
When it has exited (`tail -5 /tmp/xarch-2-3/task1-pytest.txt`): all passed (`test_key_catalogue.py` loads the new
`hints` example, `test_needs_agree.py` and `test_expandable.py` find the key table and the book agree). Then:
```bash
uv run ruff check
uv run xarch check
```
Expected: clean.

- [ ] **Step 11: Commit**

```bash
git add xarch/kernel/violations.py xarch/modules/rules/application/logic/expansion.py \
  xarch/modules/rules/application/services/source_check.py xarch/modules/rules/application/logic/imports.py \
  xarch/modules/spec/domain/key_table.py xarch/architectures/presets/format/keys.yaml \
  xarch/modules/spec/application/logic/profile_checks.py README.md tests \
  tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/stress-7cc6111.json.xz
git status --short
git commit -m "$(cat <<'EOF'
The import rule's id is may-import, in findings, JSON, hints and profile explain (enforced: yes, by the rule may-import), its book entry and the key table; a check of the profile's own may take the id rules and not may-import; the hints example and its non-mapping problem name may-import; the recorded findings of rule rules are edited by hand to may-import, and in the stress recording the two may-import blocks move ahead of the package-only blocks at their line, nothing else moved

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```
`git status --short` before the commit must show only the files named; `.claude/` and `docs/superpowers/` stay out.

---

### Task 2: `hints.rules` is refused with the new name

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py:158-166` (`RETIRED`)
- Test: `tests/modules/spec/domain/test_profile_keys.py`, `tests/modules/spec/application/logic/test_retired_keys.py`,
  `tests/modules/spec/application/logic/test_hints.py`, `tests/bootstrap/test_check_json.py`,
  `tests/bootstrap/test_profile_explain.py`

**Interfaces:**
- Consumes: `RULES` without `rules` (Task 1); `retired(scope, name)`, `advice`, `rule_hints` (step 1, unchanged).
- Produces: `RETIRED` of eight entries, the last `Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import")`.

- [ ] **Step 1: Write the failing tests**

`tests/modules/spec/domain/test_profile_keys.py`: the module docstring's last clause gains the rule id, and the last
test becomes:
```python
"""The table of retired names as xarch ships it: each entry has a scope of the format (or the scope of rule ids), a
name and one line of fixed text, once, and names nothing the format still has; it holds the part key tier, renamed
tests, the old names of never and its keys, those keys written outside uses, and the rule id rules, renamed
may-import."""
```
```python
def test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules():
    assert RETIRED == (
        Retired(PART, "tier", "renamed in 0.3.0: write tests"),
        Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
        Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
        Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
        Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
        Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
        Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"),
        Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import"))
```
(`test_no_entry_names_a_key_its_scope_still_has_nor_a_rule_id_xarch_checks` is unchanged and must stay green: `rules`
is no longer in `RULES`.)

`tests/modules/spec/application/logic/test_retired_keys.py`: after `RULE = "renamed in 0.3.0: write never-use"`
(line 90) add
```python
IMPORT_RULE = "renamed in 0.3.0: write may-import"
```
and in the parametrised table of `test_the_shipped_table_answers_each_name_in_its_scope`, after the
`id="the rule id forbidden"` line, add
```python
    pytest.param(RULE_ID, "rules", IMPORT_RULE, id="the rule id rules"),
    pytest.param(RULE_ID, "may-import", "", id="the rule id may-import, which xarch has"),
```

`tests/modules/spec/application/logic/test_hints.py`, at the end:
```python
def test_a_hint_for_the_rule_id_rules_is_told_it_is_renamed_may_import():
    assert problems(layered(hints={"rules": "see the docs"})) == [
        f"layered.yaml: hints.rules: unknown rule id 'rules': renamed in 0.3.0: write may-import; use {KNOWN}"]


def test_the_text_written_under_hints_rules_is_in_no_problem():
    found = problems(layered(hints={"rules": "secret text"}))
    assert (len(found), "secret text" in "\n".join(found)) == (1, False)
```

`tests/bootstrap/test_check_json.py`: add `from xarch.kernel.violations import RULES` to the imports (after
`from xarch.bootstrap.app import app`), and at the end:
```python
def test_a_profile_with_a_hint_for_the_rule_id_rules_is_refused_with_its_new_name_and_not_its_text(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    (tmp_path / "arch/mine.yaml").write_text((BUNDLED / "web.yaml").read_text() + "\nhints:\n  rules: secret words\n")
    result = runner.invoke(app, ["check", "--profile", "arch/mine.yaml"])
    assert result.exit_code == 2
    assert result.output == ("error: arch/mine.yaml: hints.rules: unknown rule id 'rules': renamed in 0.3.0: write "
                             f"may-import; use {', '.join(sorted(RULES))}\n")
```

`tests/bootstrap/test_profile_explain.py`, after `test_an_address_with_no_entry_is_refused_as_today_with_retired_null_in_json`:
```python
@pytest.mark.parametrize("address", [pytest.param("rules", id="the bare rule id"),
                                     pytest.param("hints.rules", id="the rule id under hints")])
def test_the_rule_id_rules_has_no_address_and_is_refused_as_any_unknown_key(address):
    text = runner.invoke(app, ["profile", "explain", address])
    assert text.exit_code == 2 and f"error: no key `{address}` in the format: the nearest are " in text.output
    assert "may-import" not in text.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] is None
```
This last test passes before and after the step (a rule id has no address, spec item 8): it pins that the new entry
gives `profile explain` no `retired` answer.

- [ ] **Step 2: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_hints.py tests/bootstrap/test_check_json.py tests/bootstrap/test_profile_explain.py 2>&1 | tail -15
```
Expected: FAIL — `RETIRED` has seven entries, `retired(RULE_ID, "rules")` is `""`, and the refusal reads
`hints.rules: unknown rule id 'rules': use built-by, ...` without `renamed in 0.3.0: write may-import; `. The
`profile explain rules` cases pass.

- [ ] **Step 3: The table entry**

`xarch/modules/spec/domain/profile_keys.py`, `RETIRED` (lines 158-166) becomes:
```python
RETIRED: tuple[Retired, ...] = (
    Retired(PART, "tier", "renamed in 0.3.0: write tests"),
    Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
    Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
    Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
    Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
    Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
    Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"),
    Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import"),
)
```
No other code changes: `rule_hints` already sends an unknown id through `advice(RULE_ID, ...)`, and an own check
named `rules` is in `own`, so it is never asked.

- [ ] **Step 4: Run the tests of Step 2, and the own-check hint test**

```bash
timeout 600 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_hints.py tests/bootstrap/test_check_json.py tests/bootstrap/test_profile_explain.py tests/modules/spec/application/logic/test_written_checks.py 2>&1 | tail -3
```
Expected: PASS (`test_a_hint_for_a_check_of_its_own_named_rules_is_the_hint_of_that_check` of Task 1 still passes:
the own id wins over the entry).

- [ ] **Step 5: The whole suite**

```bash
timeout 1500 uv run pytest -q > /tmp/xarch-2-3/task2-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-3/task2-pytest.pid
```
When it has exited: all passed. `uv run ruff check`, `uv run xarch check`: clean.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py tests
git status --short
git commit -m "$(cat <<'EOF'
The table of retired names holds the rule id rules: a profile writing hints.rules is refused with renamed in 0.3.0: write may-import and the ids it may use, never showing the text written under it, and a check of the profile's own named rules keeps its hint; profile explain rules answers as any unknown key, with no retired answer

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: The generated docs

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:403`
- Regenerate: `docs/cli/*.md`, `docs/web/*.md`, `docs/xarch/*.md` (all of them, by the script)
- Test: `tests/modules/spec/application/logic/test_docs_template.py:256`,
  `tests/modules/spec/application/logic/test_libraries_and_guards.py:106`, `tests/bootstrap/test_bundled_guards.py:75`
- Throwaway: `/tmp/xarch-2-3/regenerate_docs.py`

**Interfaces:**
- Consumes: Task 1's `may-import`. Produces: no new name.

- [ ] **Step 1: Write the failing tests**

In each of the three tests the expected line
`"- \`rules\`: every import between parts is one that the \`may_import\` of the importing part allows "` becomes:
```python
        "- `may-import`: every import between parts is one that the `may_import` of the importing part allows "
```
```bash
sed -i '256s/"- `rules`: every import/"- `may-import`: every import/' tests/modules/spec/application/logic/test_docs_template.py
sed -i '106s/"- `rules`: every import/"- `may-import`: every import/' tests/modules/spec/application/logic/test_libraries_and_guards.py
sed -i '75s/"- `rules`: every import/"- `may-import`: every import/' tests/bootstrap/test_bundled_guards.py
git diff --stat -- tests
```
Expected: three files, one line each.

- [ ] **Step 2: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_docs_template.py tests/modules/spec/application/logic/test_libraries_and_guards.py tests/bootstrap/test_bundled_guards.py 2>&1 | tail -8
```
Expected: FAIL, the line reads "- `rules`: every import between parts ...".

- [ ] **Step 3: The template**

`xarch/modules/spec/application/logic/docs_template.py:403`:
```python
             "`may-import`: every import between parts is one that the `may_import` of the importing part allows "
```
(line 404, `"(architecture.md, section 5)."]`, stays).

- [ ] **Step 4: Run the tests of Step 2**

Same command as Step 2. Expected: PASS.

- [ ] **Step 5: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-2-3/regenerate_docs.py`:

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
uv run python -I /tmp/xarch-2-3/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
git diff -U0 -- docs | grep '^[-+@]'
```
Expected: `written`; three files moved, `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`, one
line each, at `docs/cli/testing.md:339`, `docs/web/testing.md:340`, `docs/xarch/testing.md:155`; each hunk is
```
-- `rules`: every import between parts is one that the `may_import` of the importing part allows (architecture.md, section 5).
+- `may-import`: every import between parts is one that the `may_import` of the importing part allows (architecture.md, section 5).
```
Nothing new is untracked. Any other moved line is a bug of this step: do not hand-edit it; restore with
`git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 6: The docs tests, then the suite**

```bash
timeout 900 uv run pytest -q tests/bootstrap/test_docs_templates.py tests/modules/spec/application/logic/test_docs_template.py tests/bootstrap/test_bundled_guards.py 2>&1 | tail -3
timeout 1500 uv run pytest -q > /tmp/xarch-2-3/task3-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-3/task3-pytest.pid
```
Expected: PASS; when the suite has exited, all passed. `uv run ruff check`: clean.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/docs_template.py docs/cli docs/web docs/xarch tests
git status --short
git commit -m "$(cat <<'EOF'
The generated testing doc's rule line reads may-import: every import between parts is one that the may_import of the importing part allows; the golden docs are regenerated and only that line moved, in docs/cli, docs/web and docs/xarch

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: README, CHANGELOG and the gates

**Files:**
- Modify: `README.md:269`
- Modify: `CHANGELOG.md` (`## [Unreleased]` / `### Changed`, after line 28)

**Interfaces:**
- Consumes: everything above. Produces: nothing for code.

- [ ] **Step 1: The README rule table row**

`README.md:269`:
```
| `may-import` | an import between parts that the importing part's `may_import` does not allow, or a name its pattern does not match | `parts.may_import` |
```
Then:
```bash
grep -n '`rules`' README.md
```
Expected: nothing (README 191-194 name `"rules"` as JSON fields, with double quotes, and stay).

- [ ] **Step 2: The CHANGELOG entry**

`CHANGELOG.md`, under `## [Unreleased]` / `### Changed`, after the `uses.never` entry (which ends on line 28,
"Finding and fix texts are otherwise unchanged."), add a blank line and:
```
- The rule id `rules` is renamed `may-import`, in findings, in JSON and under `hints`. A profile writing `hints.rules`
  is refused with "renamed in 0.3.0: write may-import", and a check of the profile's own may now take the id `rules`.
  On a line with findings of both, the `may-import` findings now come before the `package-only` ones. Finding and fix
  texts are unchanged.
```
The blank line before `## [0.2.0] - 2026-11-18` stays.

- [ ] **Step 3: The README test**

```bash
timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | tail -3
```
Expected: PASS.

- [ ] **Step 4: The gates**

```bash
timeout 1500 uv run pytest -q > /tmp/xarch-2-3/gates-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-3/gates-pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```
Expected: each of the four commands clean (exit 0); when the suite has exited (`tail -5
/tmp/xarch-2-3/gates-pytest.txt`), all passed.

Then the leftovers for step 2.4:
```bash
grep -rn '"rules"' xarch
```
Expected only: `xarch/cli/reports/vocabulary_report.py:9, 127, 139` and `xarch/cli/reports/profile_report.py:6, 147`
(the JSON field `rules`), and `vocabulary_report.py:120` / `profile_report.py:112` (the plural noun). No rule-id use of
`"rules"` remains in the code; the retired entry lives in `profile_keys.py` as `"rules"` beside `RULE_ID` (it appears in
the grep too, line 166, and is the one step 5's check allows).

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
README names the rule may-import in its rule table and its rule id list; the CHANGELOG says the rule id rules is renamed may-import in findings, JSON and hints, hints.rules refused with renamed in 0.3.0: write may-import, a check of the profile's own may take the id rules, and may-import findings now come before package-only ones on the same line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-review against the spec

1. **Spec coverage.**
   - Required 1 (`RULES`): Task 1 Step 4, tests `test_the_rule_ids_are_the_stable_ids_of_every_check`,
     `test_the_import_rule_is_may_import_first_and_a_built_in_violation_of_rule_rules_cannot_be_made`.
   - Required 2 (findings, order): Task 1 (`test_check_json`, `test_rule_ids`, `test_report`, `test_ordered`'s new
     test, the recordings).
   - Required 3 (engine lookups, `--rule`): Task 1 Step 4, `test_expansion`, `checks.py`,
     `test_a_part_s_may_import_expands_to_the_rules_may_import`.
   - Required 4 (key table): Task 1, `test_profile_explain.py:39, 81`, both `test_explain.py`.
   - Required 5 (`hints`): accepted (Task 1 `test_check_json` with `may-import:`), refused (Task 2 unit and
     loader-wired), text not shown (Task 2), own check `rules` (Task 1), non-mapping text (Task 1 `test_hints`,
     `test_architecture_files`), `keys.yaml` example (Task 1, `test_the_example_of_hints_gives_advice_for_the_rule_may_import`,
     `test_key_catalogue`).
   - Required 6 (retired table): Task 2.
   - Required 7 (own checks): Task 1 `test_written_checks`.
   - Required 8 (`profile explain`): Task 2's parametrised guard; `profile explain hints` in Task 1.
   - Required 9 (generated docs): Task 3.
   - Required 10 (recordings): Task 1 Steps 7-9.
   - Required 11 (README): Task 1 Step 4 (id list), Task 4 Step 1 (row).
   - Required 12 (CHANGELOG): Task 4 Step 2.
   - Tests 1-12 of the spec: each above; test 1's own-check hint test lives in `test_written_checks.py` beside
     step 3's `forbidden` one (the spec allows either home); test 10's list was judged hit by hit in Task 1 Step 2
     (`test_needs_agree.py`, `test_written_rules.py`, `test_profile_explain_words.py:69`, `origins.py`,
     `test_profile_loading.py`, `test_examples.py` name the JSON field, a role or a module, and stay), and
     `test_profile_parsing_docs.py:143-145`, which the spec's list missed, is edited (its `hints={"rules": ...}` would
     be refused).
2. **Placeholder scan.** No TBD; every code step carries its code or an exact, line-addressed `sed`.
3. **Type consistency.** The book key `"may-import"` is used in `expansion.book`, `source_check`, and
   `tests/modules/rules/application/logic/checks.py`; `RETIRED`'s new entry text is the same in `profile_keys.py`,
   `test_profile_keys.py`, `test_retired_keys.py` (`IMPORT_RULE`), `test_hints.py` and `test_check_json.py`.
4. **Review Focus.** Five lines, each with its test in the owning task.
<!-- task-pipeline: validated -->
