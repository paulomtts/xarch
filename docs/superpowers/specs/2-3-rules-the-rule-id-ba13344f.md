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
