# 6.10 spec: `testing.beside` places every test of a part beside its code

Card: 06615c54-feb0-454f-8d46-d1093190d493 (subtask of 15e55316), release step 21 of the merged order
(`0.3.0-cohesion-review-3.md` section 3, row 21 at line 284), split with 6.8, 6.9 and 6.11. Blocked by 6.9
(ca108f5f), which is on this branch (HEAD 9db8c30: `testing: {preset: pytest}` exists).

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` ("the note").
This card implements 2.5 (lines 323-386: R4, mirroring, folder tiers), 2.6 (lines 396-410: how the tier rules read such
tests), the `beside` bullets of 2.8 (lines 429-430, 437-441) and the scratch-project bullet of 2.9 (lines 444-448).
From `0.3.0-cohesion-review-3.md` ("review 3"): C4 (lines 119-124), C12 (lines 191-196), gap G2 (line 410), O4, O5,
O8, O9, O22 (lines 228-246). From `profile-comparison-design.md` ("comparison"): section 5 item 9 (line 346), the
`testing.beside` looser line.

## Goal

A project may write `testing: {preset: pytest, beside: true}`, or `beside: true` in a whole framework map. Then every
test of a part sits beside the code it tests:

- a file of the app whose name `testing.files` matches is a test of the tier its part names, and is not code of its
  part;
- a test file left below the tests root, outside every tier `folder` and the fakes folder, is reported by `test-tree`;
- a tier with a `folder` keeps its tests below the tests root;
- a part that names a folder tier in `tests:` is refused.

`beside: false`, or no `beside`, means exactly what the profile means today.

## What is already done (not to be redone)

- `testing: {preset: <name>}` and the refusal of framework keys beside `preset` (6.9): `_testing`, `_preset_of` and
  `_beside` in `xarch/modules/spec/application/logic/profile_parsing.py:531-589`. `_beside` there is a helper for
  "a key written beside preset". Its name has nothing to do with this card's key.
- The looser sentence for `testing.beside` already exists, and so does its `LOOSER` entry
  (`xarch/modules/spec/application/logic/looseness.py:75` and `:516-517`: "tests may sit beside the code: the mirrored
  tests tree is no longer checked (testing.beside)"). `_looser` (`:245-310`) never emits it. The test
  `tests/modules/spec/application/logic/test_looseness.py:193` keeps it in `LATER` until this card.
- The rule id `test-tree` (`xarch/kernel/violations.py:12`). Its only emitter today is the folder check
  `xarch/modules/layout/application/logic/unmirrored.py`.
- G2, answered during exploration: today's parser lets a part name a tier that has a `folder`. `_coverage`
  (`profile_parsing.py:~651-676`) checks only that the name is a tier. `ck.tier_folder` and `ck.folder_clashes`
  (`profile_checks.py:315-340`) never relate a part's `tests:` to a tier's `folder`. No bundled or own profile does it.
  So R4's refusal is a new problem, not a new wording of an old one.
- The Python reader needs no change. pytest test functions beside the code parse as they do below `tests/`, with the
  forms `testing.declared` gives (`xarch/architectures/presets/testing/pytest.yaml`).

## Inherited constraints

- One project setting, never per tier (note 2.5 lines 331-333, review-2 Q16; card dodge "a per-tier `beside`"). A
  `beside` key under `tiers.<t>` is an unknown key with no retired-keys entry (note 2.8 line 440-441; review 3 O1).
- Owner clarification (note 2.5 lines 325-328; card dodge): no `beside` in `xarch/architecture.yaml`,
  `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, the bundled stress profile, or any file under
  `xarch/architectures/presets/`. The proof is a scratch project only (note 2.9 lines 444-448).
- A test beside the code is a test, read with the declared forms, the table forms and the globals. It is not code of
  its part: `holds` and its kinds, placement review, the `where` rules of `check` and the closed tree do not read it
  (note 2.5 lines 337-339). Card dodge: it must not be read as app code that the checks skip. It is a test file, and
  the tier rules hold it.
- Its tier is the tier its part names, found by today's `tier_of._tier` applied to the app path. Its instance is the
  instance of the part it lies in. `Read.in_tests` is true for it. Its own folder is its instance's folder in the app,
  else its top folder (note 2.5 lines 340-349).
- R4 (note 2.5 lines 361-366; review 3 C4): a tier with a `folder` keeps it under `beside`. A tier that has a `folder`
  and is also named by a part's `tests:` is refused.
- R3 (note 2.5 lines 372-374): `beside` may sit beside `preset`. It is a setting, not a framework key, so 6.9's
  refusal of framework keys beside `preset` does not apply to it. `testing: pytest` stays the short form and cannot
  carry `beside`.
- Refusal and report texts, verbatim (note 2.8 and 2.5):
  - `testing.beside: must be true or false: whether every test of a part sits beside the code it tests`
  - `tiers.guard: parts.domain says tests: guard, and guard keeps its tests in tests/architecture: under
    testing.beside a part's tests sit beside its code; give the part a tier with no folder`
  - test-tree: `lies below the tests folder, but testing.beside keeps the tests of a part beside its code: move it
    beside the code it tests`
  - tiers: `lies in no tier: its part is untested` / `lies in no part`, fix `test the part with a tier, or move the
    test`
- Looser line (comparison 5 item 9; review 3 C12): `testing.beside` is set where the compared profile leaves it out.
  The key is profile-wide, so its `LOOSER` item has no tier or part name.
- Fakes stay in `fakes.folder` below the tests root (note 2.5 lines 376-378). Jest `__mocks__` beside the code is out
  of scope (card).
- The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read, never edited by hand. The
  expected diff is empty, because no bundled profile writes `beside` (review 3 O8, line 232). The recorded corpora
  (`tests/bootstrap/corpora/`) do not move (note 2.9 line 452).
- README and CHANGELOG lines go under `[Unreleased]` (review 3 O4, O5). The parser docstring (`profile_parsing.py:7-58`)
  gains `beside` (O9). The "use ..." list of `testing` gains `beside` (O22).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; Python only in the reader adapter (`rules/adapters/fs_source_tree.py`) and the data files
  under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- xarch checks itself (`uv run xarch check`): every new module needs a part, and every new test file sits at the path
  that mirrors its subject. Layout rules hold: layout reads spec only through `spec.contract`, in
  `layout/adapters/spec_skeleton.py`; rules reads spec only in `rules/adapters/spec_profile.py`.

## Behavior

### B1. The key `testing.beside`

| Written | Means |
|---|---|
| `testing: {preset: pytest, beside: true}` | the preset's framework, with tests beside the code |
| `testing: {files: [...], declared: [...], beside: true}` | the whole framework written out, with tests beside the code |
| `testing: {preset: pytest, beside: false}`, `{preset: pytest}`, `testing: pytest` | tests in the mirrored tree, as today; all three load to an equal `Architecture` |
| `testing: {beside: true}` | refused as today's incomplete map: `files` and `declared` are missing (no new text) |

- `testing.beside` is a key of the `testing` scope. It is not required and feeds the rules `tiers` and `test-tree`. It
  is not one of the framework's keys: 6.9's "written beside preset" refusal skips it, the same way it skips `preset`.
  `profile_needs._configured` does not walk it, and it needs no fact.
- The unknown-key text of `testing` gains `beside`, in the existing sorted order:
  `testing: unknown key 'colour': use beside, declared, files, globals, mocks, preset, skips, tables`. The retired
  `functions` text gains it the same way. Every test that pins that list is updated.
- Inside a preset document (`xarch/architectures/presets/testing/*.yaml`, or a test's `presets` map), `beside` is
  refused. A preset describes a framework, not where a project keeps its tests:
  `testing.beside: the preset <name> says beside: a preset writes the framework; write beside in the profile, beside
  preset`. This text is not in the note. It is this spec's decision, in the voice of 6.9's `testing.preset: the preset
  old names a preset` refusal.

### B2. Refusals

Each problem is prefixed with the file, as every profile problem is, and makes the profile raise
`InvalidArchitecture`.

1. A value that is not a bool (`yes`, `1`, `"true"`, `null`, a list):
   `testing.beside: must be true or false: whether every test of a part sits beside the code it tests`.
2. `beside: true` in a profile with no `tiers`:
   `testing.beside: the profile has no `tiers`: add them, or drop the key`. This spec decides it (the note is
   silent). The text mirrors the existing `parts.<p>.tests: the profile has no `tiers`` text. Without tiers, no test
   beside the code has a tier to be placed by.
3. R4. Under `beside: true`, a part names in `tests:` a tier that has a `folder`. One problem per such part:
   `tiers.<tier>: parts.<part> says tests: <tier>, and <tier> keeps its tests in <tests root>/<folder>: under
   testing.beside a part's tests sit beside its code; give the part a tier with no folder`.
   - `<tests root>` is the name of the tests folder as the profile and `check` know it (`tests`). `<folder>` is the
     tier's folder joined with `/`.
   - Without `beside`, or with `beside: false`, the same profile loads, as it does today.
   - The problems come in the order of `parts` in the file.
4. The beside problems (1 to 3) follow the problems the rest of `testing` reports, so a broken `files` and a broken
   `beside` are both reported.

### B3. What `check` reads under `beside: true`

The app's files are found as today: excluded folders are not looked at, and ungoverned files are not read. Of the
governed files, those whose file name matches a pattern of `testing.files` are **tests beside the code**. Each one is:

- **Read as a test file.** It is read with the framework's declared forms, table forms and globals. It joins the test
  files every test-side check reads: the `tiers` rules, `types-only tiers`, `must-import tiers`, scenario-coverage,
  `plain_tables`, `weak`, stand-ins, skipped and dynamic enforcement, and the `syntax` rule.
- **Not code of its part.** No app-side rule reads it: `holds` and its kinds, `immutable`, `names`, `built-by`,
  `may-import`, `libraries`, `never-use` for app files, `must-import` for parts, `types-only parts`, `no-callbacks`,
  `package-only`, `private-imports`, `shared`, `duplicates`, `twins`, cycles, `dead-code` as a holder of dead code,
  `no-comments` as app code, and `closed-tree`. A test beside the code does not count as a file of its part for
  placement either.
- **Placed by its app path.** Its tier is found by the rules of `tier_of` (B4). Its instance is the instance of the
  repeating folder its path lies in. Its own folder (the folder whose helpers it may import) is its instance's folder,
  else the top folder of its path. Its subject parts (`mirrors`) are the parts found in B4, so the filter
  `mirrors-a-part` holds of it, and a tier's `uses.apply_never`, `imports.must` and `imports.types_only` read its tier
  as they read a mirrored test's.
- **Named by its app path.** A finding on it names the file as `<app root>/<path>`, for example
  `app/modules/docs/application/test_publish.py`, never `tests/...`. Messages that print the own folder or the test's
  folder (`{own_folder}`, `{tests_folder}`) print folders below the app root for it.
- **Never a fake.** A test beside the code is never a fake, even when its path starts with the fakes' folder name.

A file beside the code whose name does not match `testing.files` (such as `conftest.py`, or a builder module) is app
code, as today. Anything any test, mirrored or beside, finds of app code (what `dead-code` counts as used, what
`import-into-app` resolves) is the same as for a mirrored test that imports the same names.

Without `beside`, or with `beside: false`, a file of the app whose name looks like a test is app code, held to every
app rule, as today. This is pinned by a test.

### B4. The tier of a test beside the code

The rules are today's `tier_of._tier` (`tier_of.py:62-77`) applied to the app path:

1. The part its path lies in names a tier with `tests:`. That tier is its tier, and the part is its subject.
2. Else, when its folder is the folder of parts that are files, the tier those parts share, if they share one.
3. A tier's `folder` never places a test beside the code. Tier folders are folders below the tests root.

When none applies, the `tiers` rule reports the file (rule `tiers`, scope tests, the existing "not tiered" rule):

- its path lies in a part marked `untested`: `lies in no tier: its part is untested`;
- its path lies in no part (a governed layout folder that no part claims): `lies in no part`;
- the fix of both: `test the part with a tier, or move the test`.

Mirrored tests keep today's `NO_TIER`/`NO_TIER_FIX` text. A profile without `beside` prints exactly what it prints
today.

### B5. `test-tree` under `beside: true`

When `check` has a tests root:

- Every test file below the tests root (a name `testing.files` matches) that lies in no tier's `folder` and not below
  `fakes.folder` is reported. Rule `test-tree`, line 0, the path `tests/<path>`, the message `lies below the tests
  folder, but testing.beside keeps the tests of a part beside its code`, the fix `move it beside the code it tests`.
  The note writes the message and the fix as one sentence joined by ": ". The text form of the report prints that
  sentence. The findings are sorted by path.
- Files in a folder whose name, or a parent's name, is private in the language (such as `__pycache__`) are skipped,
  as `unmirrored` skips them today.
- Files below the tests root that are not test files (helpers, `conftest.py`, package files) are not reported.
- The folder check `unmirrored` (a folder below `tests/<each root>/` that mirrors no app folder) does not run under
  `beside`. No part's tests mirror the app then, so the file report above replaces it. This spec decides it (the note
  says only that the folder rule "has nothing to read").
- Tests in a tier's `folder` (`tests/architecture/...`) and files below the fakes' folder stay where they are, are not
  reported, and are checked as today, by their tier's folder (B4 rule 3 applies to them).

Without `beside`, `test-tree` reports exactly what it reports today.

### B6. Looseness

`profile check` with a compared profile (`based_on`, or the bundled profile it is compared with) lists
`testing.beside` under looser when the profile sets `beside: true` and the compared profile does not (no `testing`,
or `beside` false or absent). The item has no tier or part name and no detail. Its sentence is the one already
written. When both set it, or neither does, there is no item. `profile check architecture.yaml` lists no
`testing.beside`. `LATER` in `test_looseness.py` is removed, and the all-keys test then reaches every key of `LOOSER`.

The docstring list of looser keys (`xarch/modules/spec/domain/published.py:~124`) gains a `testing.beside` line.
`tests/modules/spec/application/test_origin.py:65`, which pins what each key means, gains it.

### B7. Texts, docs, explain

- Key table (`xarch/modules/spec/domain/key_table.py:139`): a `testing.beside` key after `preset`, with rules `tiers`
  and `test-tree`.
- `xarch/architectures/presets/format/keys.yaml`: a `testing.beside` entry beside `testing.preset`. It means "whether
  every test of a part sits beside the code it tests". Its accepts text: `true` or `false` (default false); under
  true, a file of the app whose name `files` matches is a test of the tier its part names, a tier with a `folder`
  keeps its tests below the tests root, and a part may not name such a tier. Its example loads:
  `testing: {preset: <preset>, beside: true}`. The `testing` entry's accepts text names `beside` among the map's
  keys. `profile explain testing.beside` prints the entry, and the existing explain coverage tests (every key has an
  entry, every example loads) stay green.
- Parser docstring (`profile_parsing.py:7-58`): the `testing` line reads `testing: <preset> | {preset, beside} |
  {files, declared, globals, skips, tables, mocks, beside}`.
- README profile block (line ~116): `beside` is added to both map forms of `testing`. One sentence near the
  `testing.preset` sentence: `testing: {preset: pytest, beside: true}` keeps every test of a part beside its code, a
  tier with a `folder` keeps its tests below the tests root, and a part may not name such a tier.
  `tests/architecture/test_readme.py` stays green.
- CHANGELOG `[Unreleased]` / `Added`: one line for `testing.beside`, naming the R4 refusal and the `test-tree` report.
- Golden docs: regenerate `docs/{cli,web,xarch}/testing.md` with the usual generator, read the diff, expect it to be
  empty.

## Tests that prove it

The tiers follow the repository's layout. A test of a module sits at the path that mirrors it. `tests/bootstrap/` holds
the wired, end-to-end tests that write a scratch project to `tmp_path` and check it through the real reader.

### Parsing (unit: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`, the tier of the parser, pure, on hand-written maps)

1. `{preset: pytest, beside: true}` loads: the framework equals the preset's, and `beside` is true.
2. `{files, declared, beside: true}` loads with `beside` true.
3. `{preset: pytest}`, `{preset: pytest, beside: false}` and `testing: pytest` give equal architectures with `beside`
   false.
4. Table test over non-bool values (`"yes"`, `1`, `None`, `[]`, `"true"`): the B2.1 text, one problem each.
5. `beside: true` with no `tiers`: the B2.2 text.
6. R4: `beside: true`, tier `guard` with `folder: architecture`, part `domain` with `tests: guard`: exactly the B2.3
   text. The same profile without `beside` loads (G2 pinned: today's parser allows it).
7. R4 with two parts naming the folder tier: two problems, in `parts` order.
8. `beside` beside `preset` is not refused as a framework key. `files` beside `preset` still is (6.9's text), in the
   same profile as a valid `beside`.
9. An unknown key lists `beside`: `use beside, declared, files, globals, mocks, preset, skips, tables`. The retired
   `functions` text lists it too.
10. A preset document holding `beside`: the B1 preset text.
11. `tiers.unit.beside: true`: unknown key of the tier, with no retired-keys hint.

Profile file loading (bootstrap: `tests/bootstrap/test_profile_file.py`, which reads real YAML files end to end): the
B2.1 and B2.3 texts with the file prefix.

Needs (unit: `tests/modules/spec/application/logic/test_profile_needs.py`): `{preset: pytest, beside: true}` gives the
preset's needs and no problem about `beside`.

Key catalogue and explain (unit: `tests/modules/spec/domain/test_profile_keys.py`, `test_key_catalogue.py`,
`tests/modules/spec/application/test_explain.py`; bootstrap: `tests/bootstrap/test_profile_explain.py`): the key list
holds `testing.beside`, and `profile explain testing.beside` prints the entry and an example that loads. Each of these
is updated where it pins the full key list. 6.9 edited the same set (`git show 594befd --stat`).

### Looseness (unit: `tests/modules/spec/application/logic/test_looseness.py`, pure functions on parsed architectures)

12. A profile with `beside: true` against the same profile without it: exactly one item, key `testing.beside`, with
    the existing sentence.
13. Both with `beside: true`, and a custom with `beside: false` against a base with `beside: true`: no item.
14. The all-keys test: `LATER` is deleted. A pair that sets `beside` is added, and `found` keys equal `LOOSER`.

`tests/modules/spec/application/test_origin.py`: its key-meaning list gains `testing.beside`.

### Placement of a test beside the code (unit: `tests/modules/rules/application/logic/test_tier_of.py`, `test_facts.py`, `test_filters.py`, on hand-built `Profile` and `SourceFile` values)

15. `tier_of` of an app path in part `application` (with `tests: unit`) under beside: tier `unit`, the instance of
    its module, own folder the instance's folder, parts `("application",)`.
16. An app path in an `untested` part: no tier, and the reason is "untested". An app path in no part: no tier, and the
    reason is "no part".
17. An app path whose top folder is named like a tier's `folder`, or like the fakes' folder: no tier from the folder,
    and not a fake.
18. `facts_of`: a test beside the code is a `Read` with `in_tests` true, `is_test` true, its tier and mirrors, and
    `place` None. It is absent from `known` and present in `known_tests`. The other app files are unchanged.
19. `mirrors-a-part` holds of it, and `in_scope` puts it on the tests side, not the app side.

### Rules over it (unit: `tests/modules/rules/application/logic/` beside the module each touches: `test_scenarios.py`, `test_stand_ins.py`, `test_sentences.py`, `test_expansion.py`)

20. scenario-coverage finds a use case's table test beside the code in the table tier and instance, by the guard's
    `file` name. Without the file, it reports the missing test as today.
21. `{own_folder}` and `{tests_folder}` print below the app root for a test beside the code.
22. The `tiers` rule says `lies in no tier: its part is untested` / `lies in no part`, with the fix
    `test the part with a tier, or move the test`. A mirrored test with no tier keeps `NO_TIER`.

### `test-tree` (unit: `tests/modules/layout/application/logic/`, a test file beside the new logic module, on plain tuples; service: `tests/modules/layout/application/test_structure_check.py`, with the layout test builders and a fake disk and skeleton)

23. Under beside: `tests/modules/docs/application/test_publish.py` is reported with the B5 text. A file in
    `tests/architecture/` (a tier folder), a file in `tests/fakes/`, a non-test file (`tests/conftest.py`) and a file
    below `__pycache__` are not.
24. Under beside, `unmirrored` does not run: a folder `tests/modules/ghost/` with no test file in it gives no finding.
25. Without beside, the structure check reports exactly what it reports today (the existing tests stay as they are).

### End to end on a scratch project (bootstrap: new `tests/bootstrap/test_tests_beside.py`, through the real reader `fs_source_tree.py`, the wiring of `tests/bootstrap/project.py`)

The project: `testing: {preset: pytest, beside: true}`; tiers `unit` (no folder), a scenario tier if the guard needs
one, and `guard` with `folder: architecture`; fakes in `tests/fakes`; part `application` with `tests: unit`; the guard
scenario-coverage on. Never xarch's own profile, and never a bundled one.

26. `app/modules/docs/application/test_publish.py` (a `test_*` function importing `app.modules.docs.application...`) is
    a test of tier `unit`. `check` gives no `holds`, `names`, `closed-tree` or `dead-code` finding on it, and a tier
    finding on it names `app/modules/docs/...`.
27. The same file importing something its tier may not import gives the `tiers` finding, named by its app path.
28. A scenario table test beside the code is found by the guard. Removing it gives the guard's missing-test finding.
29. A test left in `tests/modules/docs/application/test_publish.py` gives the `test-tree` finding.
30. `tests/architecture/test_rules.py` gives no finding and is held to the `guard` tier.
31. The same project without `beside` reports `app/modules/docs/application/test_publish.py` as app code (for example
    a `holds` or `names` finding of its part) and does not report `tests/...` by the new `test-tree` text.
32. A test beside the code in an `untested` part gives the `tiers` finding `lies in no tier: its part is untested`.

### Gates

`uv run pytest -q`, `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`,
`uv run xarch profile check architecture.yaml`, each green on this branch alone. The golden docs regenerate with an
empty diff. The recorded corpora are untouched (`git diff --stat tests/bootstrap/corpora` is empty).

## Review Focus inputs (for the planner)

These are the inputs most likely to break that no bullet above pins directly. Each one goes to the task that owns the
code:

- A test beside the code that imports another test beside the code: it is refused as "a test may not import another
  test file", the same as below `tests/`. It must not resolve as an app import or crash the target lookup.
- A test file beside the code with a syntax error: the `syntax` rule reports it once, by its app path. It is not
  counted twice (as an app file and as a test).
- A project with `beside: true` and no tests root given to `check`: tests beside the code are read and placed, and
  `test-tree` does not run.
- `beside: true` with an excluded folder holding `test_*.py`: those files are not read at all, as excluded files are
  today.
- A part of file type (a part that is one file, step 2 of B4) with a test beside it: the tier its file parts share.

## Out of scope

- Jest `__mocks__` fakes beside the code (card).
- `beside` per tier, and `beside` in xarch's own, the bundled cli/web, the stress profile, or any preset (card dodges).
- The `xarch where <file>` and `xarch review` commands' handling of a test beside the code. This card fixes what
  `check` and `profile check` do. A follow-up card should make `where` call such a file a test and keep it out of
  placement review.
- `testing.mocks.specs`, `Call.types` and the spec forms (release step 22). The table `call` cross-check, and the rest
  of step 21 that belongs to 6.11.
- New presets (Jest, Vitest, %UnitTest), and the TypeScript example of note 2.5 (inferred, no reader).
- Any change to `testing: pytest` in the bundled profiles or the corpora.

## Plan handoff notes

- Carrier suggestion, from exploration: `Framework` (`xarch/profile_values/testing.py:11-24`) reaches
  `Architecture.framework`, `ProfileView.framework` and the rules `Profile.framework` with no new wiring. A
  `beside: bool = False` there is the shortest route, and looseness already reads `architecture.framework`. For
  layout, the `Skeleton` contract (`spec/contract/__init__.py:65-77`, built in `publishing.py:46`) must carry `beside`,
  the test file patterns, every tier's `folder` and the fakes' folder. Layout's `Disk` port needs a listing of the
  files below the tests root.
- `source_check.py:60-148`: under beside, the test files beside the code are read in a second `read` call with the
  test forms, taken out of the `app` list, and added to `test_files`. `facts_of` needs to know their root, so that
  their dotted names come from the app package and their findings name the app root.
- Order of tasks the reviewer can gate separately: (1) parsing + key table + keys.yaml + explain; (2) looseness;
  (3) rules placement and reading (tier_of, facts, source_check, sentences, the `tiers` texts); (4) layout `test-tree`;
  (5) the scratch-project bootstrap test; (6) README, CHANGELOG and the golden-docs regeneration.

---

# 6.10 `testing.beside` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A profile may write `testing: {preset: pytest, beside: true}` (or `beside: true` in a whole framework map),
and then every test of a part sits beside the code it tests: `check` reads such a file as a test of the tier its part
names, never as app code, and `test-tree` reports a test file left below the tests root outside every tier `folder`
and the fakes' folder.

**Architecture:** The setting rides on `Framework.beside` (`xarch/profile_values/testing.py`), which already reaches
`Architecture.framework`, `ProfileView.framework` and the rules `Profile.framework`. Spec parses and refuses it (R4),
looseness lists it, and the `Skeleton` contract carries it to layout. Rules marks a test beside the code with
`SourceFile.beside`: `source_check` reads those files a second time with the test forms, takes them out of the app
list and adds them to the test list, and `tier_of`, `facts`, the filters, the sentences, scenario-coverage and
stand-ins read the flag. Layout gains a file-level `test-tree` report that replaces `unmirrored` under beside.

**Tech Stack:** Python 3.13, pytest, uv, ruff, xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/6-10-spec-testing-06615c54.md`. It is reproduced in full above this plan's header;
executors read both.

## Global Constraints

- One project setting, never per tier. A `beside` key under `tiers.<t>` is an unknown key with no retired-keys entry.
- No `beside` in `xarch/architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, the
  bundled stress profile, or any file under `xarch/architectures/presets/` (the format file `keys.yaml` documents the
  key, it does not set it). The proof is a scratch project only.
- Refusal and report texts, verbatim:
  - `testing.beside: must be true or false: whether every test of a part sits beside the code it tests`
  - `testing.beside: the profile has no `tiers`: add them, or drop the key`
  - `tiers.<tier>: parts.<part> says tests: <tier>, and <tier> keeps its tests in tests/<folder>: under
    testing.beside a part's tests sit beside its code; give the part a tier with no folder`
  - `testing.beside: the preset <name> says beside: a preset writes the framework; write beside in the profile,
    beside preset`
  - test-tree message `lies below the tests folder, but testing.beside keeps the tests of a part beside its code`, fix
    `move it beside the code it tests`
  - tiers messages `lies in no tier: its part is untested` and `lies in no part`, fix
    `test the part with a tier, or move the test`
  - unknown keys of `testing`: `use beside, declared, files, globals, mocks, preset, skips, tables`
  - looser sentence (already in `looseness.py`): `tests may sit beside the code: the mirrored tests tree is no longer
    checked (testing.beside)`
- `beside: false`, or no `beside`, means exactly what the profile means today; `{preset: pytest}`,
  `{preset: pytest, beside: false}` and `testing: pytest` load to an equal `Architecture`.
- Fakes stay in `fakes.folder` below the tests root. A test beside the code is never a fake.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and the diff read, never hand-edited; expected diff:
  empty. `tests/bootstrap/corpora/` does not move.
- README and CHANGELOG lines go under `[Unreleased]`.
- No comments in xarch's code (docstrings only); never `ruff --fix`; tests first; examples simple, with absolute
  `app.` imports; Python only in `rules/adapters/fs_source_tree.py` and the data files under
  `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- `uv run xarch check` must stay green: every new module needs a part, every new test file sits at the path that
  mirrors its subject. Layout reads spec only through `spec.contract` in `layout/adapters/spec_skeleton.py`; rules reads
  spec only in `rules/adapters/spec_profile.py`.
- Lines are at most 140 characters (`ruff.toml`).
- Stop a long test run with `timeout`; never `pkill`/`killall`.

## Review Focus

1. **A test beside the code imports another test beside the code** → refused as `a test may not import another test
   file (app.<...>.test_other)`, never resolved as an app import and never a crash. Pinned in Task 3
   (`test_a_test_beside_the_code_importing_another_reads_it_as_test_code`) and Task 6 (bootstrap).
2. **A test beside the code with a syntax error** → the `syntax` rule reports it once, by its app path; it is not
   counted as an app file too. Pinned in Task 6 (`test_a_broken_test_beside_the_code_is_reported_once`).
3. **`beside: true` and no tests root given to `check`** → tests beside the code are still read and placed (a tier
   finding names the app path), and `test-tree` does not run. Pinned in Task 6
   (`test_without_a_tests_folder_the_tests_beside_the_code_are_still_checked`).
4. **An excluded folder holding `test_*.py` under `beside: true`** → those files are not read at all (a broken one
   gives no finding). Pinned in Task 6 (the `vendor/` file of the scratch app is broken on purpose).
5. **A test beside a part that is one file (B4 step 2)** → the tier its file parts share, as a mirrored test in that
   folder has. Pinned in Task 3 (`test_tested_beside`, the row "beside a file part").

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `xarch/profile_values/testing.py` | modify | `Framework.beside: bool = False` |
| `xarch/modules/spec/domain/key_table.py` | modify | key `testing.beside` |
| `xarch/architectures/presets/format/keys.yaml` | modify | its text; `testing` accepts names `beside` |
| `xarch/modules/spec/application/logic/profile_parsing.py` | modify | parse/refuse `beside`, docstring |
| `xarch/modules/spec/application/logic/looseness.py` | modify | emit `testing.beside` |
| `xarch/modules/spec/domain/published.py` | modify | docstring line |
| `xarch/modules/spec/contract/__init__.py` | modify | `Skeleton.beside`, `test_files`, `kept` |
| `xarch/modules/spec/application/services/publishing.py` | modify | fill them |
| `xarch/modules/rules/domain/parsed.py` | modify | `SourceFile.beside` |
| `xarch/modules/rules/domain/rule.py` | modify | `Facts.beside`, docstrings |
| `xarch/modules/rules/domain/vocabulary.py` | modify | filter `beside` |
| `xarch/modules/rules/application/logic/tier_of.py` | modify | `tested(..., beside)`, `is_test_file`, texts |
| `xarch/modules/rules/application/logic/facts.py` | modify | read beside tests, import facts |
| `xarch/modules/rules/application/logic/filters.py` | modify | `beside`, `below` |
| `xarch/modules/rules/application/logic/sentences.py` | modify | `own_folder`, `tests_folder`, `target` |
| `xarch/modules/rules/application/logic/expansion.py` | modify | `tiers` sayings under beside |
| `xarch/modules/rules/application/logic/scenarios.py` | modify | pass `beside` to `tested` |
| `xarch/modules/rules/application/logic/stand_ins.py` | modify | pass `beside`; never a fake |
| `xarch/modules/rules/application/services/source_check.py` | modify | split the app's test files out |
| `xarch/modules/layout/domain/structure.py` | modify | `Beside` value |
| `xarch/modules/layout/application/logic/beside.py` | create | the file report of `test-tree` |
| `xarch/modules/layout/application/ports/skeleton.py`, `ports/disk.py` | modify | `beside`, `files` |
| `xarch/modules/layout/adapters/spec_skeleton.py`, `fs_disk.py` | modify | implement them |
| `xarch/modules/layout/application/services/structure_check.py` | modify | run `stray` or `unmirrored` |
| `tests/fakes/layout_skeleton.py`, `tests/fakes/filesystem.py` | modify | the fakes follow the ports |
| `tests/bootstrap/test_tests_beside.py` | create | end to end on a scratch project |
| `README.md`, `CHANGELOG.md` | modify | docs |

---

### Task 1: Parse `testing.beside`: key, texts, refusals, explain

**Files:**
- Modify: `xarch/profile_values/testing.py:11-24` (`Framework`)
- Modify: `xarch/modules/spec/domain/key_table.py:139` (after `Key(TESTING, "preset", ...)`)
- Modify: `xarch/architectures/presets/format/keys.yaml:143-153` (`testing`) and `:784-789` (after `testing.preset`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (docstring line 11-14; imports; `parse_profile`
  lines 204-233; `_testing` 531-558; `_preset_of` 578-579; new `_tests_beside`)
- Test: `tests/modules/spec/application/logic/test_profile_parsing_tests.py`
- Test: `tests/modules/spec/application/logic/test_retired_keys.py`, `tests/bootstrap/test_profile_file.py` (the "use"
  list)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`
- Test: `tests/modules/spec/domain/test_profile_keys.py:190-203`
- Test: `tests/modules/spec/application/test_explain.py:46`
- Test: `tests/bootstrap/test_profile_explain.py` (after line 386)

**Interfaces:**
- Consumes: nothing new.
- Produces: `Framework.beside: bool = False` (last field of `Framework`); `Architecture.framework.beside` is `True`
  exactly when the profile writes `testing: {..., beside: true}` and loads. Key `Key(TESTING, "beside",
  rules=("tiers", "test-tree"))`. Later tasks read `profile.framework.beside` (rules) and
  `architecture.framework.beside` (spec).

- [ ] **Step 1: Write the failing parsing tests**

Append to `tests/modules/spec/application/logic/test_profile_parsing_tests.py` (it already imports `replace`,
`pytest`, `PRESETS`, `covered`, `layered`, `parsed`, `problems`, and defines `BY_NAME`):

```python
BESIDE_TYPE = ("layered.yaml: testing.beside: must be true or false: whether every test of a part sits beside the code "
               "it tests")
FOLDER_TIER = {"proves": "the architecture", "litmus": "Does it read the source?", "folder": "architecture"}


def beside(**testing) -> dict:
    """covered(), its testing the preset pytest with the keys given beside it."""
    return covered(testing={"preset": "pytest", **testing})


def guarded(testing: dict, *parts: str) -> dict:
    """covered() with testing as given, a tier guard whose tests live in tests/architecture, and the parts given
    tested by guard."""
    document = covered(testing=testing)
    document["tiers"]["guard"] = dict(FOLDER_TIER)
    for name in parts:
        document["parts"][name]["tests"] = "guard"
    return document


def test_beside_beside_a_preset_is_the_preset_s_framework_with_its_tests_beside_the_code():
    framework = parsed(beside(beside=True)).framework
    assert framework == replace(parsed(covered(testing="pytest")).framework, beside=True)
    assert framework.beside is True


def test_beside_in_a_whole_framework_keeps_the_framework_written():
    framework = parsed(covered(testing={"files": ["test_*.py"], "declared": BY_NAME, "beside": True})).framework
    assert (framework.files, framework.beside) == (("test_*.py",), True)


def test_beside_false_and_no_beside_mean_the_same_as_the_short_form():
    short = parsed(covered(testing="pytest"))
    assert parsed(beside()) == short
    assert parsed(beside(beside=False)) == short
    assert short.framework.beside is False


@pytest.mark.parametrize("value", [
    pytest.param("yes", id="a word"), pytest.param(1, id="a number"), pytest.param(None, id="null"),
    pytest.param([], id="a list"), pytest.param("true", id="the word true, quoted"),
])
def test_beside_that_is_no_bool_is_refused(value):
    assert problems(beside(beside=value)) == [BESIDE_TYPE]


def test_beside_with_no_tiers_is_refused():
    assert problems(layered(testing={"preset": "pytest", "beside": True})) == [
        "layered.yaml: testing.beside: the profile has no `tiers`: add them, or drop the key"]


def test_a_part_naming_a_tier_with_a_folder_is_refused_under_beside_and_loads_without_it():
    assert problems(guarded({"preset": "pytest", "beside": True}, "service")) == [
        "layered.yaml: tiers.guard: parts.service says tests: guard, and guard keeps its tests in tests/architecture: "
        "under testing.beside a part's tests sit beside its code; give the part a tier with no folder"]
    loaded = parsed(guarded({"preset": "pytest"}, "service"))
    assert [s.part for t in loaded.tiers if t.name == "guard" for s in t.subject] == ["service"]


def test_each_part_naming_a_tier_with_a_folder_is_refused_in_the_order_of_parts():
    assert problems(guarded({"preset": "pytest", "beside": True}, "service", "api")) == [
        f"layered.yaml: tiers.guard: parts.{name} says tests: guard, and guard keeps its tests in tests/architecture: "
        "under testing.beside a part's tests sit beside its code; give the part a tier with no folder"
        for name in ("api", "service")]


def test_a_tier_with_a_folder_no_part_names_is_kept_under_beside():
    assert parsed(guarded({"preset": "pytest", "beside": True})).framework.beside is True


def test_beside_is_no_key_of_the_framework_written_beside_preset_but_files_still_is():
    assert problems(beside(beside=True, files=["check_*.py"])) == [
        "layered.yaml: testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map"]


def test_a_broken_framework_and_a_broken_beside_are_both_reported_beside_last():
    assert problems(covered(testing={"files": "broken", "declared": BY_NAME, "beside": "yes"})) == [
        "layered.yaml: testing.files: must be a non-empty list of file name patterns, each a .py name with `*` for "
        "any text", BESIDE_TYPE]


def test_an_unknown_key_beside_preset_lists_beside_among_the_keys():
    assert problems(beside(beside=True, colour=1)) == [
        "layered.yaml: testing: unknown key 'colour': use beside, declared, files, globals, mocks, preset, skips, tables"]


def test_a_preset_may_not_say_beside_whichever_form_names_it():
    presets = {"near": {"files": ["test_*.py"], "declared": BY_NAME, "beside": True}} | PRESETS
    expected = ["layered.yaml: testing.beside: the preset near says beside: a preset writes the framework; write "
                "beside in the profile, beside preset"]
    assert problems(covered(testing="near"), presets=presets) == expected
    assert problems(covered(testing={"preset": "near"}), presets=presets) == expected


def test_beside_under_a_tier_is_an_unknown_key_with_no_hint():
    document = covered()
    document["tiers"]["unit"]["beside"] = True
    found = problems(document)
    assert len(found) == 1 and found[0].startswith("layered.yaml: tiers.unit: unknown key 'beside': use ")
    assert "moved" not in found[0]
```

- [ ] **Step 2: Update every test that pins the "use ..." list of `testing`**

The list gains `beside` first. Run:

```bash
sed -i 's/use declared, files, globals, mocks, preset/use beside, declared, files, globals, mocks, preset/' \
  tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_retired_keys.py \
  tests/bootstrap/test_profile_file.py
grep -rn "use declared, files" tests/ ; echo "left: $?"
```
Expected: `left: 1` (grep finds nothing). The lines touched are `test_profile_parsing_tests.py:58,88`,
`test_retired_keys.py:404,477,490,496,503`, `test_profile_file.py:181,199`; each stays under 140 characters. The new
test of Step 1 already writes `use beside, ...`, so `sed` leaves it unchanged.

- [ ] **Step 3: Write the failing tests of the key, its needs, its text and explain**

In `tests/modules/spec/domain/test_profile_keys.py`, replace lines 193-194:

```python
    assert [key.name for key in KEYS if key.scope == TESTING] == ["preset", "files", "declared", "globals", "skips",
                                                                  "tables", "mocks"]
```
with:
```python
    assert [key.name for key in KEYS if key.scope == TESTING] == ["preset", "beside", "files", "declared", "globals",
                                                                  "skips", "tables", "mocks"]
```
and append:
```python
def test_beside_is_a_setting_of_testing_that_is_not_required_offers_nothing_and_needs_no_fact():
    held = {key.name: key for key in KEYS if key.scope == TESTING}
    assert (held["beside"].required, held["beside"].choices, held["beside"].rules, held["beside"].needs,
            held["beside"].opens) == (False, "", ("tiers", "test-tree"), (), "")
```

In `tests/modules/spec/application/test_explain.py`, after line 46
(`Shown('testing.preset', 1, 'the preset the framework is read from', False, True),`) insert:
```python
    Shown('testing.beside', 1, 'whether every test of a part sits beside the code it tests', False, True),
```

Append to `tests/modules/spec/application/logic/test_profile_needs.py`:
```python
def test_beside_written_beside_a_preset_needs_nothing_and_the_preset_is_walked():
    found = short(layered(language="toy", testing={"preset": "pytest", "beside": True}), {"pytest": {"skips": ["x"]}},
                  TOY)
    assert [(item.address, item.fact) for item in found] == [("testing.skips", "use"),
                                                             ("testing.skips", "import.resolved")]
```

In `tests/bootstrap/test_profile_explain.py`, after
`test_the_preset_of_testing_is_explained_and_names_the_presets_xarch_ships` (ends at line 386) insert:
```python
def test_beside_of_testing_is_explained_with_an_example_that_writes_it():
    result = runner.invoke(app, ["profile", "explain", "testing.beside"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "testing.beside"
    assert "  what: whether every test of a part sits beside the code it tests" in lines
    assert "      beside: true" in lines
```

Append to `tests/bootstrap/test_profile_file.py` (it has `PROFILE`, `profile_in`, `load_architecture`, `pytest`,
`InvalidArchitecture`):
```python
def test_beside_that_is_no_bool_is_refused_naming_the_file(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: sometimes}"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: testing.beside: must be true or false: whether every test of a part sits beside the code it tests",)


def test_a_part_naming_a_tier_with_a_folder_is_refused_under_beside_naming_the_file(tmp_path):
    text = (PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: true}")
            .replace("    tests: unit\n  cli:", "    tests: guard\n  cli:")
            .replace("tiers:\n  unit: {}\n", "tiers:\n  unit: {}\n  guard: {folder: architecture}\n"))
    path = profile_in(tmp_path, text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: tiers.guard: parts.core says tests: guard, and guard keeps its tests in tests/architecture: under "
        "testing.beside a part's tests sit beside its code; give the part a tier with no folder",)


def test_beside_true_loads_with_the_preset_s_framework(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: true}"))
    loaded = load_architecture(path)
    assert loaded.framework.beside is True
    assert loaded.framework.files == load_architecture(profile_in(tmp_path, PROFILE)).framework.files
```

(`PROFILE` of that file writes `core` first with `tests: unit`, then `  cli:`; the replace targets `core`'s line. The
non-bool value is `sometimes`, never `yes`/`no`/`on`/`off`: PyYAML reads those as booleans, so the file would load.)

- [ ] **Step 4: Run the tests to see them fail**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_tests.py \
  tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/domain/test_profile_keys.py \
  tests/modules/spec/application/test_explain.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_file.py 2>&1 | tail -15
```
Expected: FAIL — `unknown key 'beside'` problems, `Framework.__init__() got an unexpected keyword argument` /
`replace() got an unexpected field 'beside'`, the key list without `beside`, explain `no key testing.beside`.

- [ ] **Step 5: Add `Framework.beside`**

In `xarch/profile_values/testing.py`, replace the `Framework` docstring's last sentence and add the field:

```python
@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text); the forms a test is declared in (declared, at least one: a function whose name
    matches a pattern, or a call whose arguments hold the test's title and its body), a test being of the first form
    it matches; the dotted names of what skips a test or expects it to fail (a marker or a call; empty: none is
    counted); the table forms it writes (tables; none: it writes none, and no table is read); the names it binds
    without an import (globals), which are not the language's predefined names; and whether every test of a part sits
    beside the code it tests rather than in the mirrored tests tree (beside, the project's `testing.beside`)."""
    files: tuple[str, ...]
    declared: tuple[TestForm, ...]
    skips: tuple[tuple[str, ...], ...] = ()
    tables: tuple[TableForm, ...] = ()
    globals: tuple[tuple[str, ...], ...] = ()
    beside: bool = False
```

- [ ] **Step 6: Add the key and its text**

In `xarch/modules/spec/domain/key_table.py`, after line 139
(`Key(TESTING, "preset", rules=("tiers", "test-tree"), choices=CHOICE_PRESETS),`) insert:
```python
    Key(TESTING, "beside", rules=("tiers", "test-tree")),
```

In `xarch/architectures/presets/format/keys.yaml`, replace the `testing` entry's `accepts` (lines 145-149):
```yaml
    accepts: >-
      a preset name, a map {preset, beside} naming one, or a map {files, declared, globals, skips, tables, mocks,
      beside}; needed with `tiers` and the guards scenario-coverage and stand-ins. Dotted names are what an import
      binds; what stays %language% is `%interface_path%` as the mark of a port, `%package_file%`, the syntax tree,
      import resolution and the standard library's names
```
and after the `testing.preset` entry (its last line is `    example: "testing: {preset: <preset>}"`) insert:
```yaml
  testing.beside:
    meaning: whether every test of a part sits beside the code it tests
    accepts: >-
      `true` or `false` (default false); under true, a file of the app whose name `files` matches is a test of the
      tier its part names, a tier with a `folder` keeps its tests below the tests root, and a part may not name such a
      tier; it is written beside `preset`, or in the whole map, never in a preset
    example: |
      <<testing>>
        beside: true
      tiers:
        unit:
          proves: a rule
      <<tiered-part>>
```
(The spec's example `testing: {preset: <preset>, beside: true}` cannot be used as written: `explain` fills
`<preset>` only for a key whose `choices` are the presets, and `beside` offers no choice. The fragment `<<testing>>`
is the whole map, so the example loads in the smallest profile, which has no `tiers`, once a tier is added.)

- [ ] **Step 7: Parse `beside`**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

7a. Docstring, lines 11-14, replace the `testing:` line and its text with:
```
    testing: <preset> | {preset, beside} | {files, declared, globals, skips, tables, mocks, beside}
                               how the test framework names things; a preset is a name, alone or under preset, read
                               from data shipped with xarch, and a key of the framework beside it is refused; beside,
                               whether every test of a part sits beside the code it tests (a tier with a `folder`
                               keeps its tests below the tests folder, and no part may name it then).
                               Required with `tiers` and with the guards scenario-coverage and stand-ins
```

7b. Import the tests folder's name. Add to the imports (beside the other `xarch.modules.spec.domain` imports):
```python
from xarch.modules.spec.domain.published import DEFAULT_TESTS
```

7c. In `parse_profile`, after line 205 (`tiers = _tiers(document, specs, parts, declared, examples, problems, language)`)
insert:
```python
    beside = _tests_beside(document, specs, tiers, problems)
```
and in the `return Architecture(...)` call replace `testing.framework if testing else None` with
`replace(testing.framework, beside=beside) if testing else None`.

7d. In `_testing`, after the block
```python
    if preset and isinstance(value, Mapping) and "preset" in value:
        problems.append(f"testing.preset: the preset {preset} names a preset: a preset writes the whole framework")
        return None
```
insert:
```python
    if preset and isinstance(value, Mapping) and "beside" in value:
        problems.append(f"testing.beside: the preset {preset} says beside: a preset writes the framework; write beside "
                        "in the profile, beside preset")
        return None
```
and extend its docstring's last clause: `... a preset's map that names a preset in turn, or says beside, is refused.`

7e. In `_preset_of`, replace
```python
    problems += [_beside(key.name, named, presets) for key in keys_of(TESTING)
                 if key.name != "preset" and key.name in value]
```
with
```python
    problems += [_beside(key.name, named, presets) for key in keys_of(TESTING)
                 if key.name not in _SETTINGS and key.name in value]
```
and after `_TIER_INSTEAD = ...` (line 145) add:
```python
_SETTINGS = ("preset", "beside")
"""The keys of `testing` that are the project's settings, not the framework's: written beside preset, never refused."""
```

7f. After `_framework_named` add:
```python
def _tests_beside(document: Mapping[Any, Any], specs: dict[str, Any], tiers: tuple[Tier, ...],
                  problems: list[str]) -> bool:
    """Whether every test of a part sits beside the code it tests, as the map `testing` writes it (`beside`); false
    when it does not say. A value that is no bool, beside with no `tiers`, and each part, in the order of the file,
    that names in `tests` a tier with a `folder` are refused."""
    written = document.get("testing")
    if not isinstance(written, Mapping) or "beside" not in written:
        return False
    beside = written["beside"]
    if not isinstance(beside, bool):
        problems.append("testing.beside: must be true or false: whether every test of a part sits beside the code it "
                        "tests")
        return False
    if not beside:
        return False
    if "tiers" not in document:
        problems.append("testing.beside: the profile has no `tiers`: add them, or drop the key")
        return False
    folders = {tier.name: tier.folder for tier in tiers if tier.folder is not None}
    for name, spec in specs.items():
        tier = spec.get("tests") if isinstance(spec, Mapping) else None
        if isinstance(tier, str) and tier in folders:
            problems.append(f"tiers.{tier}: parts.{name} says tests: {tier}, and {tier} keeps its tests in "
                            f"{'/'.join((DEFAULT_TESTS, *folders[tier]))}: under testing.beside a part's tests sit "
                            "beside its code; give the part a tier with no folder")
    return True
```
(`Tier` is already imported from `xarch.modules.spec.domain.values`; `Mapping`, `Any` from the top of the file.)

- [ ] **Step 8: Run the tests to see them pass**

Run the command of Step 4. Expected: PASS. Then run the spec module and the explain/keys coverage:
```bash
timeout 900 uv run pytest -q tests/modules/spec tests/bootstrap/test_profile_explain.py \
  tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_check.py 2>&1 | tail -5
```
Expected: all pass (`test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs[testing.beside]`
and `test_the_shipped_file_gives_a_text_for_every_key_of_the_table_and_no_other` among them). If a test elsewhere pins
the full list of `testing`'s keys or the `testing` accepts text, update it to the new value and say so in the commit.

- [ ] **Step 9: Lint and self-check**

```bash
uv run ruff check xarch tests && uv run xarch check; echo "exit $?"
```
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 10: Commit**

```bash
git add xarch/profile_values/testing.py xarch/modules/spec/domain/key_table.py \
  xarch/architectures/presets/format/keys.yaml xarch/modules/spec/application/logic/profile_parsing.py \
  tests/modules/spec tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_file.py
git commit -m "testing may say beside: true beside its preset or in the whole map, and a part naming a tier with a folder is refused then"
```

---

### Task 2: Looseness lists `testing.beside`

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py:296-298` (after the `testing.skips` lines in `_looser`)
- Modify: `xarch/modules/spec/domain/published.py:~124` (docstring list of looser keys)
- Test: `tests/modules/spec/application/logic/test_looseness.py:157-195`
- Test: `tests/modules/spec/application/test_origin.py:39-66`

**Interfaces:**
- Consumes: `Architecture.framework.beside` (Task 1).
- Produces: a `Loosened("testing.beside", "", "", "tests may sit beside the code: the mirrored tests tree is no longer
  checked (testing.beside)")` item when the custom profile sets beside and the compared one does not.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_looseness.py`:

1a. Append:
```python
BESIDE = Loosened("testing.beside", "", "",
                  "tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)")


def near(beside: bool | None) -> Architecture:
    """covered(), its testing saying beside as given (None: not at all)."""
    document = covered()
    if beside is not None:
        document["testing"]["beside"] = beside
    return parsed(document)


def test_a_profile_whose_tests_sit_beside_the_code_is_looser_than_one_whose_tests_mirror_it():
    assert loosened(near(True), near(None)) == (BESIDE,)
    assert loosened(near(True), near(False)) == (BESIDE,)


@pytest.mark.parametrize("custom, base", [
    pytest.param(True, True, id="both beside"),
    pytest.param(False, True, id="beside dropped"),
    pytest.param(None, None, id="neither"),
])
def test_beside_is_looser_only_where_the_compared_profile_leaves_it_out(custom, base):
    assert loosened(near(custom), near(base)) == ()


def test_a_profile_with_no_testing_compared_with_one_beside_is_not_looser_by_beside():
    assert "testing.beside" not in [item.key for item in loosened(parsed(layered()), near(True))]
```

1b. In `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`, add as the last entry of `pairs`
(after `(parsed(covered()), parsed(tight())),`):
```python
        (near(True), near(None)),
```
and replace its two assertions
```python
    assert LATER <= set(LOOSER)
    assert sorted({item.key for item in found}) == sorted(key for key in LOOSER if key not in LATER)
```
with
```python
    assert sorted({item.key for item in found}) == sorted(LOOSER)
```
1c. Delete the `LATER = {"testing.beside"}` assignment and its docstring (lines 193-195). `near` is defined at the
bottom of the module; Python resolves it at call time, so its place does not matter.

In `tests/modules/spec/application/test_origin.py`, in
`test_every_way_a_custom_profile_is_looser_than_the_bundled_one_it_resembles_is_listed`, replace
`"testing": {**TESTING, "skips": ["pytest.mark.skip"]},` with
`"testing": {**TESTING, "skips": ["pytest.mark.skip"], "beside": True},`, and in its expected tuple, after the line
`Loosened("testing.skips", "", "pytest.mark.xfail", "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),`
insert:
```python
        Loosened("testing.beside", "", "",
                 "tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)"),
```
(BASE's tier `unit` has no folder, so `beside: true` loads there.)

- [ ] **Step 2: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py \
  tests/modules/spec/application/test_origin.py 2>&1 | tail -10
```
Expected: FAIL — `loosened(near(True), near(None)) == ()`, and the all-keys test misses `testing.beside`.

- [ ] **Step 3: Emit the item**

In `xarch/modules/spec/application/logic/looseness.py`, `_looser`, right after
```python
    if base.framework is not None:
        found += [("testing.skips", "", outside_text(name, member)) for name in base.framework.skips if name not in skips]
```
insert:
```python
    if custom.framework is not None and custom.framework.beside and not (base.framework is not None
                                                                         and base.framework.beside):
        found.append(("testing.beside", "", ""))
```

In `xarch/modules/spec/domain/published.py`, in the docstring list (after the line
`        testing.skips   what is no longer counted as a skip`) insert:
```
        testing.beside  the tests of a part may sit beside its code, which the compared profile does not allow
```

- [ ] **Step 4: Run them to see them pass**

Run the command of Step 2. Expected: PASS. Then:
```bash
timeout 600 uv run pytest -q tests/modules/spec 2>&1 | tail -3
uv run xarch profile check architecture.yaml 2>&1 | grep -c "testing.beside"
```
Expected: all pass; `0` (xarch's own profile lists no `testing.beside`).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py xarch/modules/spec/domain/published.py \
  tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py
git commit -m "A profile whose tests sit beside the code is looser by testing.beside than one whose tests mirror it"
```

---

### Task 3: Rules place and read a test beside the code

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py:261-294` (`SourceFile`: docstring, last field)
- Modify: `xarch/modules/rules/domain/rule.py:474-507` (`Read` docstring, `Facts.beside`)
- Modify: `xarch/modules/rules/application/logic/tier_of.py` (whole module: docstring, texts, `is_test_file`,
  `tested`, `_tier`)
- Modify: `xarch/modules/rules/application/logic/facts.py:92-133, 207-216`
- Modify: `xarch/modules/rules/application/logic/filters.py:77-85`
- Modify: `xarch/modules/rules/domain/vocabulary.py:259-260` (after the `below` filter)
- Modify: `xarch/modules/rules/application/logic/sentences.py:48-50, 89-90`
- Test: `tests/modules/rules/application/logic/test_tier_of.py`
- Test: `tests/modules/rules/application/logic/test_facts.py`
- Test: `tests/modules/rules/application/logic/test_filters.py`
- Test: `tests/modules/rules/application/logic/test_sentences.py`
- Test: `tests/modules/rules/domain/test_rule.py:191-192` (the list of filter names)

**Interfaces:**
- Consumes: `Framework.beside` (Task 1) — not read in this task; the flag on the file is what is read.
- Produces:
  - `SourceFile.beside: bool = False` (last field).
  - `Facts.beside: frozenset[tuple[str, ...]] = frozenset()` (last field): the steps below the app root of the tests
    beside the code.
  - `tier_of.is_test_file(profile: Profile, path: tuple[str, ...]) -> bool` (was `_is_test`).
  - `tier_of.tested(profile: Profile, path: tuple[str, ...], beside: bool = False) -> Tested`.
  - `tier_of.BESIDE_UNTESTED = "lies in no tier: its part is untested"`, `BESIDE_NO_PART = "lies in no part"`,
    `BESIDE_FIX = "test the part with a tier, or move the test"`.
  - The file filter `beside` (true of a `Read` whose file is beside the code).

- [ ] **Step 1: Write the failing `tier_of` tests**

Append to `tests/modules/rules/application/logic/test_tier_of.py` (it imports `GUARD`, `INTEGRATION`, `PROFILE`,
`UNIT`, `profile`, `steps`, `tier_of`, `Tier`; `SPLIT` and `SHARED` are defined in it):

```python
@pytest.mark.parametrize("checked, path, expected", [
    pytest.param(PROFILE, "modules/docs/application/services/test_publish.py",
                 tier_of.Tested(INTEGRATION, "docs", ("modules", "docs"), True, False, ("services",)),
                 id="beside a part's code: its part's tier, its instance, its instance's folder and its part"),
    pytest.param(PROFILE, "modules/docs/domain/test_doc.py",
                 tier_of.Tested(UNIT, "docs", ("modules", "docs"), True, False, ("domain",)),
                 id="beside another part's code: that part's tier"),
    pytest.param(PROFILE, "modules/docs/application/test_publish.py",
                 tier_of.Tested(INTEGRATION, "docs", ("modules", "docs"), True, False, ("controller",)),
                 id="beside a file part: the tier of the file parts of its folder"),
    pytest.param(SHARED, "modules/docs/application/test_publish.py",
                 tier_of.Tested(SHARED.tiers[1], "docs", ("modules", "docs"), True, False, ("controller", "main")),
                 id="beside file parts sharing one tier: that tier, and it mirrors them all"),
    pytest.param(SPLIT, "modules/docs/application/test_publish.py",
                 tier_of.Tested(None, "docs", ("modules", "docs"), True, False, ()),
                 id="beside file parts of different tiers: no tier, since no tier's folder places it"),
    pytest.param(PROFILE, "platform/test_sql.py", tier_of.Tested(None, None, ("platform",), True, False, ("platform",)),
                 id="in a part no tier tests: no tier, and it lies in its part"),
    pytest.param(PROFILE, "scripts/test_seed.py", tier_of.Tested(None, None, ("scripts",), True, False, ()),
                 id="in no part: no tier and no part"),
    pytest.param(PROFILE, "architecture/test_rules.py", tier_of.Tested(None, None, ("architecture",), True, False, ()),
                 id="in a folder named like a tier's folder: that folder places no test beside the code"),
    pytest.param(PROFILE, "fakes/test_repo.py", tier_of.Tested(None, None, ("fakes",), True, False, ()),
                 id="in a folder named like the fakes': never a fake"),
])
def test_tested_beside(checked, path, expected):
    assert tier_of.tested(checked, steps(path), beside=True) == expected


def test_a_test_file_is_named_by_the_profile_s_patterns():
    assert tier_of.is_test_file(PROFILE, ("modules", "test_doc.py")) is True
    assert tier_of.is_test_file(PROFILE, ("modules", "conftest.py")) is False
```

- [ ] **Step 2: Write the failing `facts`, `filters` and `sentences` tests**

Append to `tests/modules/rules/application/logic/test_facts.py` (add any of these imports it lacks at the top:
`from dataclasses import replace`, `from tests.modules.rules.builders import PROFILE, imp, source`,
`from xarch.modules.rules.application.logic.facts import facts_of`,
`from xarch.modules.rules.domain.parsed import Function`):

```python
def near(path: str, *imports, **fields):
    """A test beside the code, at path below the app root, shown as app/<path>."""
    return replace(source(path, *imports, **fields), beside=True)


DOC_FILE = source("modules/docs/domain/doc.py")


def test_a_test_beside_the_code_is_a_placed_test_and_no_file_of_the_app():
    beside = near("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
                  functions=(Function(3, "test_doc"),))
    built = facts_of([DOC_FILE], [beside], PROFILE, "app", "tests")
    read = next(r for r in built.files if r.file is beside)
    assert (read.in_tests, read.is_test, read.is_fake, read.tier, read.mirrors, read.place, read.instance, read.own) == (
        True, True, False, "unit", ("domain",), None, "docs", ("modules", "docs"))
    steps = ("modules", "docs", "domain", "test_doc")
    assert steps not in built.known and steps in built.known_tests and steps in built.beside
    assert steps in built.test_files and steps not in built.tested_by
    assert [f.target for f in read.facts["import-into-app"]] == [("modules", "docs", "domain", "doc")]
    assert [r.file for r in built.files if not r.in_tests] == [DOC_FILE]


def test_a_test_beside_the_code_importing_another_reads_it_as_test_code():
    other = near("modules/docs/domain/test_other.py", functions=(Function(1, "test_other"),))
    first = near("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain.test_other", "test_other"),
                 imp(2, "app.modules.docs.domain", "doc"))
    built = facts_of([DOC_FILE], [first, other], PROFILE, "app", "tests")
    read = next(r for r in built.files if r.file is first)
    assert [f.target for f in read.facts["import-into-tests"]] == [("modules", "docs", "domain", "test_other")]
    assert [f.target for f in read.facts["import-into-app"]] == [("modules", "docs", "domain", "doc")]


def test_a_test_below_the_tests_root_importing_a_test_beside_the_code_reads_it_as_test_code():
    other = near("modules/docs/domain/test_other.py", functions=(Function(1, "test_other"),))
    mirrored = source("architecture/test_rules.py", imp(1, "app.modules.docs.domain", "test_other"), root="tests")
    built = facts_of([DOC_FILE], [mirrored, other], PROFILE, "app", "tests")
    read = next(r for r in built.files if r.file is mirrored)
    assert [f.target for f in read.facts["import-into-tests"]] == [("modules", "docs", "domain", "test_other")]
    assert read.facts["import-into-app"] == ()
```

Also append to `test_facts.py` (a test beside the code reads the fakes below the tests root as test code, so that the
tier rule on fakes holds it):
```python
def test_a_test_beside_the_code_importing_the_fakes_below_the_tests_root_reads_them_as_test_code():
    beside = near("modules/docs/domain/test_doc.py", imp(1, "tests.fakes.repo", "FakeRepo"),
                  imp(2, "app.modules.docs.domain", "doc"))
    built = facts_of([DOC_FILE], [beside], PROFILE, "app", "tests")
    read = next(r for r in built.files if r.file is beside)
    assert [f.target for f in read.facts["import-into-tests"]] == [("fakes", "repo")]
    assert [f.target for f in read.facts["import-into-app"]] == [("modules", "docs", "domain", "doc")]
```

In `tests/modules/rules/application/logic/test_filters.py`:
- in the parametrize list of `test_a_filter_holds_of_the_facts_it_says`, after the two `below fakes` rows add:
```python
    pytest.param("beside", TEST, "file", [], PROFILE, None, id="beside: a test below the tests root is not"),
```
- append (add `from xarch.modules.rules.application.logic.filters import in_scope` and
  `from xarch.profile_values.checks import APP, TESTS, Scope` and `from tests.modules.rules.builders import source`
  to the imports if missing):
```python
def test_beside_holds_of_a_test_beside_the_code_which_is_on_the_tests_side_and_below_no_folder_of_it():
    beside = replace(source("fakes/test_repo.py"), beside=True)
    built = facts_of([], [beside], PROFILE, "app", "tests")
    read = built.files[0]
    asked = [Found(RULE, read, fact, None) for fact in read.facts["file"]]
    assert [question(condition("beside"))(f, built, PROFILE) for f in asked] == [True]
    assert [question(condition("below fakes"))(f, built, PROFILE) for f in asked] == [False]
    assert (in_scope(Scope(TESTS), read, built, PROFILE), in_scope(Scope(APP), read, built, PROFILE)) == (True, False)


def test_a_test_beside_a_part_s_code_mirrors_the_part():
    read = facts_of([], [replace(source("modules/docs/domain/test_doc.py"), beside=True)], PROFILE, "app",
                    "tests").files[0]
    assert read.mirrors == ("domain",)
    assert in_scope(Scope(TESTS, "domain"), read, facts_of([], [read.file], PROFILE, "app", "tests"), PROFILE)
```

In `tests/modules/rules/domain/test_rule.py`, line 192, replace `"may-import-everything, below, relative, standard, reserved, "`
with `"may-import-everything, below, beside, relative, standard, reserved, "`.

Append to `tests/modules/rules/application/logic/test_sentences.py` (it imports `value`, `PROFILE`, `RULE`; add
`from dataclasses import replace` if missing, and `from tests.modules.rules.builders import imp, source`,
`from xarch.modules.rules.application.logic.facts import facts_of`, `from xarch.modules.rules.domain.rule import
Found`):
```python
def test_the_folders_of_a_test_beside_the_code_are_shown_below_the_app_root():
    other = replace(source("modules/docs/domain/test_other.py"), beside=True)
    beside = replace(source("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain.test_other", "x")),
                     beside=True)
    built = facts_of([], [beside, other], PROFILE, "app", "tests")
    read = built.files[0]
    found = Found(RULE, read, read.facts["import-into-tests"][0], None)
    assert value("own_folder", found, built, PROFILE) == "app/modules/docs"
    assert value("tests_folder", found, built, PROFILE) == "app/modules/docs/domain"
    assert value("target", found, built, PROFILE) == "app.modules.docs.domain.test_other"
```

- [ ] **Step 3: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/rules/application/logic/test_tier_of.py \
  tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_filters.py \
  tests/modules/rules/application/logic/test_sentences.py tests/modules/rules/domain/test_rule.py 2>&1 | tail -15
```
Expected: FAIL — `unexpected keyword argument 'beside'`, `replace() got an unexpected field 'beside'`, `no filter is
named 'beside'`, `module ... has no attribute 'is_test_file'`.

- [ ] **Step 4: Add `SourceFile.beside` and `Facts.beside`**

In `xarch/modules/rules/domain/parsed.py`, `SourceFile`: add as the last field, after `tests: tuple[Test, ...] = ()`:
```python
    beside: bool = False
```
and end its docstring with: `beside: the file is a test that sits beside the code it tests, below the app root
(testing.beside); its path is below the app root, and it is no file of the app's code.`

In `xarch/modules/rules/domain/rule.py`, `Facts`: add as the last field, after
`tested_by: dict[tuple[str, ...], str] = field(default_factory=dict)`:
```python
    beside: frozenset[tuple[str, ...]] = frozenset()
```
and end its docstring with: `; and the steps below the app's root of the tests beside the code (beside), which are
among the test files and are read in the app's namespace.` In `Read`'s docstring replace `in_tests, whether it lies
below the tests root rather than the app's;` with `in_tests, whether it is a test file (below the tests root, or a
test beside the code below the app's) rather than a file of the app;`.

- [ ] **Step 5: Place a test beside the code**

Replace `xarch/modules/rules/application/logic/tier_of.py` lines 1-77 (docstring through `_tier`) so the module
reads, up to `_tests`:

```python
"""Where a test file sits: tests mirror the app, so a file's tier follows from the app part its folder mirrors.

A file at tests/<path> mirrors the app's <path>. Its tier is, in order:
1. the first tier whose subject holds the part that claims <path> (below the subject's sub-path, if it names one);
2. else, when its folder is the folder of parts that are files (such as an application controller), the tier of those parts,
   if they share one;
3. else, the first tier whose `folder` holds it: the file lies in that folder or below it.
A file under the fakes' folder is a fake, which no tier holds. A file in none of these has no tier.

A test beside the code (testing.beside) lies at <path> below the app root and is placed by 1. and 2. alone: a tier's
`folder` is a folder below the tests root and never places it, and it is never a fake.

Its subject is the part its folder mirrors (1.), or the file parts of its folder (2.); a file placed by its tier's
folder (3.) mirrors no part and has none.

Its own folder is the instance of the repeating folder it mirrors (tests/<its root>/<name>/), else the top folder below
the tests root: the folder whose helpers it may import; for a test beside the code, the same folders below the app
root.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fnmatch import fnmatchcase

from xarch.kernel.logic.placement import place_of, stem
from xarch.kernel.placement import EACH, Place
from xarch.modules.rules.application.logic.places import instance_root, matches, targets_of
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.placement import Target
from xarch.profile_values.tiers import CheckedTier

NO_TIER = "lies in no tier: no part's folder and no tier's `folder` is mirrored here"
NO_TIER_FIX = "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`"
BESIDE_UNTESTED = "lies in no tier: its part is untested"
BESIDE_NO_PART = "lies in no part"
BESIDE_FIX = "test the part with a tier, or move the test"


@dataclass(frozen=True)
class Tested:
    """A test file or a file below the tests root: its tier (None if none), the instance of the repeating folder it is
    in, its own folder, whether it is a test (a name the profile's test files match) or a fake, and the parts it
    mirrors (its subject; empty when its tier was found by its tier's folder)."""
    tier: CheckedTier | None
    instance: str | None
    own: tuple[str, ...]
    is_test: bool
    is_fake: bool
    parts: tuple[str, ...] = ()


def is_test_file(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether the file name matches one of the profile's test file patterns; no file is a test when it names none."""
    return bool(path) and profile.framework is not None and any(fnmatchcase(path[-1], pattern)
                                                                for pattern in profile.framework.files)


def tested(profile: Profile, path: tuple[str, ...], beside: bool = False) -> Tested:
    """Where the file at path sits: below the tests root, or, beside, a test beside the code at path below the app
    root."""
    fake = not beside and profile.fakes is not None and path[:len(profile.fakes.folder)] == profile.fakes.folder
    tier, instance, parts = (None, None, ()) if fake else _tier(profile, path, beside)
    return Tested(tier, instance or _instance(profile, path), _own(profile, path), is_test_file(profile, path), fake,
                  parts)


def _tier(profile: Profile, path: tuple[str, ...],
          beside: bool) -> tuple[CheckedTier | None, str | None, tuple[str, ...]]:
    where = place_of(profile.parts, path, profile.language.marks)
    if where.part is not None:
        tier = _first(profile, lambda t: any(s.part == where.part and where.sub[:len(s.sub)] == s.sub
                                             for s in t.subject))
        return tier, where.instance, (where.part,)
    folder = path[:-1]
    file_parts = [name for name, pattern in profile.parts.items()
                  if pattern and stem(pattern[-1], profile.language.marks) is not None
                  and matches(pattern[:-1], folder, profile.language.marks)]
    tiers = {id(t): t for name in file_parts for t in [_first(profile, lambda t, n=name: _tests(t, n))] if t}
    if len(tiers) == 1:
        instance = place_of({"": profile.parts[file_parts[0]][:-1]}, folder, profile.language.marks).instance
        return next(iter(tiers.values())), instance, tuple(file_parts)
    if beside:
        return None, None, ()
    return _first(profile, lambda t: bool(t.folder) and folder[:len(t.folder)] == t.folder), None, ()
```
Keep the rest of the module (`_tests`, `_first`, `_instance`, `_own`, `_folder_imports`, `allowance`,
`may_use_fakes`, `as_place`) as it is. `grep -rn "_is_test\b" xarch tests` must find nothing afterwards.

- [ ] **Step 6: Read a test beside the code in the facts**

In `xarch/modules/rules/application/logic/facts.py`:

6a. In `facts_of`, after `known_tests = frozenset(steps for f, steps, _ in tests if f.error is None)` add:
```python
    near = frozenset(steps for f, steps, _ in tests if f.beside and f.error is None)
```
and replace the `bare = Facts(...)` statement with:
```python
    bare = Facts((), root, tests_root, known, known_tests,
                 frozenset(r.steps for r in placed if r.in_tests and r.is_test and r.file.error is None),
                 {r.steps: r.tier for r in placed if not r.in_tests and r.tier and r.file.error is None}, near)
```
Extend its docstring: `... then of the test files, below the package tests_root, a test beside the code below root:
...`.

6b. `_tested` passes the flag:
```python
def _tested(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile) -> Read:
    where = tested(profile, file.path, file.beside)
    return Read(file, steps, package, True, None, where.tier.name if where.tier is not None else "", where.instance,
                where.own, where.parts, where.is_test, where.is_fake)
```

6c. In `_facts`, replace the `import-into-app` case for tests and the `import-into-tests` case:
```python
        case "import-into-app" if read.in_tests:
            return tuple(Fact("import-into-app", line, target=target, at=_placed(profile, cache, target))
                         for line, target in targets((i for i in file.imports if not i.relative), (),
                                                     facts.known | facts.beside, root) if target not in facts.beside)
```
(The known files include the tests beside the code here so that `from app.<folder> import test_other` resolves to
that test, which is then left to `import-into-tests`, rather than to its folder.)
```python
        case "import-into-tests":
            return tuple(Fact("import-into-tests", line, target=target)
                         for line, target in _into_tests(read, package, facts)) if read.in_tests else ()
```

6d. Add after `_references`:
```python
def _into_tests(read: Read, package: tuple[str, ...], facts: Facts) -> list[tuple[int, tuple[str, ...]]]:
    """What a test's imports reach of the test code: for a test below the tests root, what they reach below it, its
    relative imports read from its own package; for a test beside the code, what its absolute imports reach below the
    tests root (the fakes, which its tier may import only when it tests a part they stand in for, and any other test
    code, which it may not import from outside its own folder); then, for any test, the tests beside the code they
    reach, read below the app's root, a relative import read from its own package only for a test beside the code."""
    imports = read.file.imports
    beside = read.file.beside
    own = list(targets(tuple(i for i in imports if not i.relative) if beside else imports, () if beside else package,
                       facts.known_tests, facts.tests_root))
    near = imports if beside else tuple(i for i in imports if not i.relative)
    return [*own, *((line, target) for line, target in targets(near, package, facts.beside, facts.root)
                    if target in facts.beside)]
```
(`Read` and `Facts` are already imported from `xarch.modules.rules.domain.rule`.)

- [ ] **Step 7: The `beside` filter and `below`**

In `xarch/modules/rules/application/logic/filters.py`, replace `_below` and `_FILE`:
```python
def _below(read: Read, profile: Profile, value: str) -> bool:
    folder = _folder(value)
    return not read.file.beside and read.file.path[:len(folder)] == folder


def _beside(read: Read, profile: Profile, value: str) -> bool:
    return read.file.beside


_FILE: dict[str, Callable[[Read, Profile, str], bool]] = {
    "test": _test, "tiered": _tiered, "placed": _placed_file, "package-file": _package_file,
    "mirrors-a-part": _mirrors_a_part, "may-import-everything": _may_import_everything, "below": _below,
    "beside": _beside}
```

In `xarch/modules/rules/domain/vocabulary.py`, after the `Filter("below", ...)` entry insert:
```python
    Filter("beside", "the test sits beside the code it tests, below the app folder (testing.beside), and lies below "
                     "no folder of the tests", FILE, side=TESTS_SIDE),
```

- [ ] **Step 8: Show a test beside the code's folders below the app root**

In `xarch/modules/rules/application/logic/sentences.py` replace `_target`:
```python
def _target(found: Found, facts: Facts) -> str:
    test_code = found.fact.kind == "import-into-tests" and found.fact.target not in facts.beside
    return ".".join((facts.tests_root if test_code else facts.root, *found.fact.target))


def _side(found: Found, facts: Facts) -> str:
    """The root a test's own folders are shown below: the app's for a test beside the code, else the tests'."""
    return facts.root if found.read.file.beside else facts.tests_root
```
and the two entries of `_VALUES`:
```python
    "own_folder": lambda found, facts, profile: "/".join((_side(found, facts), *found.read.own)),
    "tests_folder": lambda found, facts, profile: "/".join((_side(found, facts), *found.read.file.path[:-1])),
```

- [ ] **Step 9: Run the tests to see them pass**

Run the command of Step 3. Expected: PASS. Then the whole rules module and the architecture tests:
```bash
timeout 900 uv run pytest -q tests/modules/rules tests/architecture tests/cli 2>&1 | tail -5
```
Expected: all pass. If a test pins every filter of the vocabulary in a rendering (for example
`profile explain checks` output), add `beside` there in the vocabulary's order (after `below`).

- [ ] **Step 10: Lint, self-check, commit**

```bash
uv run ruff check xarch tests && uv run xarch check; echo "exit $?"
git add xarch/modules/rules tests/modules/rules
git commit -m "A test beside the code is a test of the tier its part names, read in the app's namespace, never a fake and never placed by a tier's folder"
```
Expected before the commit: `All checks passed!`, `exit 0`.

---

### Task 4: The tiers rule, scenario-coverage and stand-ins over a test beside the code

**Files:**
- Modify: `xarch/modules/rules/application/logic/expansion.py:12, 162-195` (`_tiers`)
- Modify: `xarch/modules/rules/application/logic/scenarios.py:84, 174`
- Modify: `xarch/modules/rules/application/logic/stand_ins.py:92-93, 143, 155`
- Test: `tests/modules/rules/application/logic/test_tier_imports.py`
- Test: `tests/modules/rules/application/logic/test_scenarios.py`
- Test: `tests/modules/rules/application/logic/test_stand_ins.py`
- Test: `tests/modules/rules/application/logic/test_expansion.py` (a row for the tiers rule under beside)

**Interfaces:**
- Consumes: `SourceFile.beside`, `tested(profile, path, beside)`, `BESIDE_UNTESTED`, `BESIDE_NO_PART`, `BESIDE_FIX`,
  the filter `beside` (Task 3); `profile.framework.beside` (Task 1).
- Produces: nothing new for later tasks; Task 6 relies on these rules end to end.

- [ ] **Step 1: Write the failing tests**

Append to `tests/modules/rules/application/logic/test_tier_imports.py` (it imports `replace`, `violations` (the
`tiers` check helper), `PROFILE`, `imp`, `source`, `in_tests`; `APP` and `HELPERS` are defined in it):
```python
NEAR = replace(PROFILE, framework=replace(PROFILE.framework, beside=True))
"""PROFILE, its tests beside the code."""


def beside_problems(path: str, *imports, checked=NEAR) -> list[str]:
    beside = replace(source(path, *imports), beside=True)
    return [f"{v}; fix: {v.fix}" for v in violations([beside, *HELPERS], APP, checked, "app", "tests")]


@pytest.mark.parametrize("path, expected", [
    pytest.param("platform/test_sql.py",
                 ["app/platform/test_sql.py: lies in no tier: its part is untested; fix: test the part with a tier, or "
                  "move the test"], id="in a part no tier tests"),
    pytest.param("scripts/test_seed.py",
                 ["app/scripts/test_seed.py: lies in no part; fix: test the part with a tier, or move the test"],
                 id="in no part"),
    pytest.param("modules/docs/domain/test_doc.py", [], id="in a tested part"),
])
def test_a_test_beside_the_code_with_no_tier_says_why(path, expected):
    assert beside_problems(path) == expected


def test_a_test_beside_the_code_imports_what_its_part_may_and_is_named_by_its_app_path():
    assert beside_problems("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
                           imp(3, "app.platform.sql")) == [
        "app/modules/docs/domain/test_doc.py:3: a test of domain/ (unit tier) may not import platform/ "
        "(app.platform.sql): it imports only what domain/ may (parts.domain.imports.may); fix: import here only what "
        "domain/ may; test platform/ from the folder that mirrors it"]


def test_a_mirrored_test_with_no_tier_keeps_its_text_under_beside():
    found = [str(v) for v in violations([in_tests("scripts/test_x.py"), *HELPERS], APP, NEAR, "app", "tests")]
    assert found == [f"tests/scripts/test_x.py: {NO_TIER}"]
```

In `tests/modules/rules/application/logic/test_expansion.py`, append:
```python
def test_the_tiers_rule_under_beside_says_why_a_test_beside_the_code_has_no_tier_before_the_mirrored_text():
    near = replace(PROFILE, framework=replace(PROFILE.framework, beside=True))
    first = expansion.book(near)["tiers"][0]
    assert [(s.message, s.fix, [written(c) for c in s.when]) for s in first.sayings] == [
        ("lies in no tier: its part is untested", "test the part with a tier, or move the test",
         ["beside", "mirrors-a-part"]),
        ("lies in no part", "test the part with a tier, or move the test", ["beside"]),
        ("lies in no tier: no part's folder and no tier's `folder` is mirrored here",
         "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`", [])]
    assert [s.message for s in expansion.book(PROFILE)["tiers"][0].sayings] == [
        "lies in no tier: no part's folder and no tier's `folder` is mirrored here"]
```
(If `Saying`'s condition field is not named `when`, read `xarch/profile_values/checks.py` `class Saying` and use its
name; the engine reads it as `saying.when` in `engine.py:181`.)

Append to `tests/modules/rules/application/logic/test_scenarios.py` (it imports `replace`, `Function`, `declaring`,
`problems`, `TABLE`, `table`, `row`):
```python
def beside_test(path: str, *functions: Function):
    """A test file beside the code at path below the app root, holding functions."""
    return replace(declaring(path, *functions), name=f"app/{path}", beside=True)


def test_a_use_case_s_table_test_beside_the_code_covers_its_union():
    assert problems(beside_test("modules/docs/application/test_publish.py", Function(8, "test_publish", (TABLE,)))) == []


def test_a_table_test_beside_the_code_is_reported_by_its_app_path():
    assert problems(beside_test("modules/docs/application/test_publish.py",
                                Function(8, "test_publish", (table(row("Published")),)))) == [
        "app/modules/docs/application/test_publish.py:9: PublishResult variant Missing has no row in the table and no "
        "standalone test naming it (scenario-coverage)"]


def test_a_table_test_beside_another_part_s_code_is_of_that_part_s_tier_and_does_not_cover_the_union():
    assert problems(beside_test("modules/docs/domain/test_publish.py", Function(8, "test_publish", (TABLE,)))) == [
        "app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among the integration "
        "tests of docs (scenario-coverage)"]
```
(The third test pins that a test beside the code of `domain` is of `domain`'s tier, `unit`, so it does not stand
for the `integration` test the guard asks for.)

Append to `tests/modules/rules/application/logic/test_stand_ins.py` (it imports `Class`, `Method`, `source`,
`PORTS`, `PORT_FILE`, `problems`, `weak`, `replace`, `PROFILE`):
```python
def test_a_class_beside_the_code_in_a_folder_named_like_the_fakes_is_no_fake():
    beside = replace(source("fakes/test_repo.py", classes=(Class(1, "FakeRepo", (), (Method(2, "get", None),
                                                                                   Method(3, "save", None))),)),
                     beside=True)
    assert problems([PORTS], [beside]) == [f"app/{PORT_FILE}:3: Repo is a read port with no fake (stand-ins)"]
    assert weak([PORTS], [beside], PROFILE) == []
```

- [ ] **Step 2: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/rules/application/logic/test_tier_imports.py \
  tests/modules/rules/application/logic/test_expansion.py tests/modules/rules/application/logic/test_scenarios.py \
  tests/modules/rules/application/logic/test_stand_ins.py 2>&1 | tail -15
```
Expected: FAIL — the beside tiers texts are absent (NO_TIER printed), the expansion row lists one saying, and the
stand-ins test finds no missing fake (the class below `fakes/` counts as a fake). The scenario tests may already
pass, since a path beside the code places as a mirrored one does; they pin it.

- [ ] **Step 3: The tiers rule's sayings under beside**

In `xarch/modules/rules/application/logic/expansion.py`, replace line 12 with
```python
from xarch.modules.rules.application.logic.tier_of import BESIDE_FIX, BESIDE_NO_PART, BESIDE_UNTESTED, NO_TIER, NO_TIER_FIX
```
In `_tiers`, after `also = "".join(...)` add:
```python
    near = ((Saying(BESIDE_UNTESTED, BESIDE_FIX, _all("beside", "mirrors-a-part")),
             Saying(BESIDE_NO_PART, BESIDE_FIX, _all("beside")))
            if profile.framework is not None and profile.framework.beside else ())
```
and in the first `Rule("tiers", ...)` of its return, replace `(Saying(NO_TIER, NO_TIER_FIX),)` with
`(*near, Saying(NO_TIER, NO_TIER_FIX))`. Add to the docstring of `_tiers`: `Under testing.beside a test beside the code
that lies in no tier is told that its part is untested, or that it lies in no part.`

- [ ] **Step 4: Scenario-coverage and stand-ins read the flag**

In `xarch/modules/rules/application/logic/scenarios.py`, replace both `where = tested(profile, test.path)` (line 84 in
`plain`, and line 174 in `_in`) with `where = tested(profile, test.path, test.beside)`.

In `xarch/modules/rules/application/logic/stand_ins.py`:
- `weak`: replace `if test.path[:len(folder)] != folder:` with `if test.beside or test.path[:len(folder)] != folder:`.
- `_missing_fakes`: replace `fakes = {cls.name for t in tests if t.path[:len(folder)] == folder for cls in t.classes}`
  with `fakes = {cls.name for t in tests if not t.beside and t.path[:len(folder)] == folder for cls in t.classes}`.
- `_mocks`: replace `tier = tested(profile, file.path).tier` with `tier = tested(profile, file.path, file.beside).tier`.

- [ ] **Step 5: Run them to see them pass**

Run the command of Step 2, then `timeout 900 uv run pytest -q tests/modules/rules 2>&1 | tail -3`. Expected: PASS.

- [ ] **Step 6: Lint, self-check, commit**

```bash
uv run ruff check xarch tests && uv run xarch check; echo "exit $?"
git add xarch/modules/rules tests/modules/rules
git commit -m "Under testing.beside a test beside the code with no tier says its part is untested or that it lies in no part, and scenario-coverage and stand-ins place it by its app path"
```

---

### Task 5: `test-tree` reports a test left below the tests root

**Files:**
- Modify: `xarch/modules/spec/contract/__init__.py:65-77` (`Skeleton`)
- Modify: `xarch/modules/spec/application/services/publishing.py:46-54` (`skeleton`)
- Modify: `xarch/modules/layout/domain/structure.py` (add `Beside` after `Naming`)
- Create: `xarch/modules/layout/application/logic/beside.py`
- Modify: `xarch/modules/layout/application/ports/skeleton.py`, `xarch/modules/layout/application/ports/disk.py`
- Modify: `xarch/modules/layout/adapters/spec_skeleton.py`, `xarch/modules/layout/adapters/fs_disk.py`
- Modify: `xarch/modules/layout/application/services/structure_check.py`
- Modify: `tests/fakes/layout_skeleton.py`, `tests/fakes/filesystem.py:86-102` (`FakeDisk`)
- Create: `tests/modules/layout/application/logic/test_beside.py`
- Test: `tests/modules/layout/application/test_structure_check.py`, `tests/modules/layout/adapters/test_spec_skeleton.py`,
  `tests/modules/layout/adapters/test_fs_disk.py`, `tests/modules/spec/application/test_skeleton.py`

**Interfaces:**
- Consumes: `Architecture.framework.beside`, `.files`, `Architecture.tiers[*].folder`, `Architecture.fakes.folder`.
- Produces:
  - contract `Skeleton.beside: bool = False`, `Skeleton.test_files: tuple[str, ...] = ()`,
    `Skeleton.kept: tuple[tuple[str, ...], ...] = ()` (last fields).
  - layout domain `Beside(files: tuple[str, ...], kept: tuple[tuple[str, ...], ...])`.
  - `beside.stray(tests: str, files: Iterable[tuple[str, ...]], beside: Beside, naming: Naming) -> list[Violation]`;
    `beside.STRAY`, `beside.STRAY_FIX`.
  - Skeleton port `beside(profile: str) -> Beside | None`; Disk port `files(root: Path) -> list[tuple[str, ...]]`.

- [ ] **Step 1: Write the failing logic test**

Create `tests/modules/layout/application/logic/test_beside.py`:
```python
"""The test-tree rule under testing.beside, on plain values: which test files below the tests root lie outside every
folder whose tests stay there."""
from tests.modules.layout.builders import PYTHON_NAMING
from xarch.modules.layout.application.logic.beside import stray
from xarch.modules.layout.domain.structure import Beside

BESIDE = Beside(("test_*.py", "*_test.py"), (("architecture",), ("fakes",)))
MESSAGE = "lies below the tests folder, but testing.beside keeps the tests of a part beside its code"
FIX = "move it beside the code it tests"


def reported(*paths: str) -> list[tuple[str, int, str, str, str]]:
    return [(f"tests/{path}", 0, MESSAGE, "test-tree", FIX) for path in paths]


def found(*paths: str) -> list[tuple[str, int, str, str, str]]:
    files = [tuple(path.split("/")) for path in paths]
    return [(v.file, v.line, v.message, v.rule, v.fix) for v in stray("tests", files, BESIDE, PYTHON_NAMING)]


def test_a_test_left_in_the_mirrored_tree_is_reported():
    assert found("modules/docs/application/test_publish.py") == reported("modules/docs/application/test_publish.py")


def test_tests_in_a_tier_s_folder_or_below_the_fakes_stay_where_they_are():
    assert found("architecture/test_rules.py", "architecture/rules/test_layers.py", "fakes/test_repo.py") == []


def test_a_file_that_is_no_test_is_not_reported():
    assert found("conftest.py", "modules/docs/builders.py", "modules/__init__.py") == []


def test_a_file_in_a_folder_private_in_the_language_is_never_read():
    assert found("modules/docs/__pycache__/test_publish.py", "_private/x/test_y.py") == []


def test_the_findings_are_sorted_by_path_and_every_pattern_names_a_test():
    assert found("web/test_docs.py", "kernel/ids_test.py", "test_top.py") == reported(
        "kernel/ids_test.py", "test_top.py", "web/test_docs.py")


def test_the_text_form_is_one_sentence():
    [violation] = stray("tests", [("modules", "test_x.py")], BESIDE, PYTHON_NAMING)
    assert f"{violation}: {violation.fix}" == f"tests/modules/test_x.py: {MESSAGE}: {FIX}"
```

- [ ] **Step 2: Write the failing service, adapter and spec tests**

Append to `tests/modules/layout/application/test_structure_check.py` (it defines `ROOT`, `TOP`, `MODULE`,
`CONTROLLER`, `SKELETON`, `TESTS`, imports `FakeDisk`, `FakeSkeleton`, `LayoutController`, `StructureCheckService`,
`CheckStructure`, `PYTHON_NAMING`; add `from xarch.modules.layout.domain.structure import Beside`):
```python
NEAR = FakeSkeleton([("bootstrap",), ("kernel",), ("kernel", "logic"), ("modules",), ("platform",), ("cli",),
                     ("cli", "commands")],
                    {("modules",): [(("contract",), True), (("domain",), True),
                                    (("application", "controller.py"), False), (("application", "services"), True),
                                    (("application", "logic"), True), (("application", "ports"), True),
                                    (("adapters",), True)]}, naming=PYTHON_NAMING,
                    beside=Beside(("test_*.py",), (("architecture",), ("fakes",))))


def run_beside(disk: FakeDisk) -> list[str]:
    controller = LayoutController(StructureCheckService(disk, NEAR))
    return [f"{v}: {v.fix}" for v in controller.check(CheckStructure(ROOT, "app", "cli", TESTS)).violations]


def test_under_beside_a_test_below_the_tests_root_outside_its_kept_folders_is_reported():
    tests = {TESTS / p for p in ["", "modules", "modules/docs", "modules/docs/application", "architecture", "fakes",
                                 "modules/docs/__pycache__"]}
    files = {TESTS / p for p in ["modules/docs/application/test_publish.py", "architecture/test_rules.py",
                                 "fakes/repo.py", "fakes/test_fake.py", "conftest.py",
                                 "modules/docs/__pycache__/test_publish.py"]}
    assert run_beside(FakeDisk(TOP | MODULE | tests, {CONTROLLER} | files)) == [
        "tests/modules/docs/application/test_publish.py: lies below the tests folder, but testing.beside keeps the "
        "tests of a part beside its code: move it beside the code it tests"]


def test_under_beside_a_folder_that_mirrors_nothing_is_not_reported():
    tests = {TESTS / p for p in ["", "modules", "modules/ghost"]}
    assert run_beside(FakeDisk(TOP | MODULE | tests, {CONTROLLER})) == []


def test_under_beside_without_a_tests_root_nothing_below_it_is_read():
    found = LayoutController(StructureCheckService(FakeDisk(TOP | MODULE, {CONTROLLER}), NEAR)).check(
        CheckStructure(ROOT, "app", "cli")).violations
    assert found == ()
```

Append to `tests/modules/layout/adapters/test_spec_skeleton.py`:
```python
def test_without_beside_there_is_no_beside_and_with_it_the_test_files_and_the_kept_folders():
    from dataclasses import replace

    from xarch.modules.layout.domain.structure import Beside

    assert SpecSkeleton(Spec()).beside("cli") is None
    near = replace(SKELETON, beside=True, test_files=("test_*.py",), kept=(("architecture",), ("fakes",)))

    class Near:
        def skeleton(self, profile: str) -> Skeleton:
            return near

    assert SpecSkeleton(Near()).beside("cli") == Beside(("test_*.py",), (("architecture",), ("fakes",)))
```
(Move the two imports to the top of the file when writing it; they are shown inline here only to list them. The file
must not hold a local import in the end.)

Append to `tests/modules/layout/adapters/test_fs_disk.py`:
```python
def test_the_disk_lists_every_file_below_a_root_but_those_it_hides(tmp_path):
    (tmp_path / "modules" / "docs").mkdir(parents=True)
    (tmp_path / "modules" / "docs" / "test_a.py").write_text("")
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache" / "test_b.py").write_text("")
    (tmp_path / "conftest.py").write_text("")
    disk = FsDisk(FileSystem())
    assert disk.files(tmp_path) == [("conftest.py",), ("modules", "docs", "test_a.py")]
    assert disk.files(tmp_path / "gone") == []
```

Append to `tests/modules/spec/application/test_skeleton.py`:
```python
NEAR = {"name": "near", "testing": {"files": ["test_*.py"], "declared": [{"function": "test_*"}], "beside": True},
        "parts": {"src": {"path": "src", "role": "code", "tests": "unit"}},
        "tiers": {"unit": {}, "guard": {"folder": "architecture"}}, "fakes": {"folder": "fakes", "for": ["src"]}}


def test_the_skeleton_says_beside_the_test_files_and_the_folders_whose_tests_stay_below_the_tests_root():
    found = controller(FakeArchitectureFiles({"cli": NEAR})).skeleton("cli")
    assert (found.beside, found.test_files, found.kept) == (True, ("test_*.py",), (("architecture",), ("fakes",)))


def test_without_beside_the_skeleton_says_no_beside():
    found = SPEC.skeleton("cli")
    assert (found.beside, found.kept) == (False, ())
```

- [ ] **Step 3: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/modules/layout tests/modules/spec/application/test_skeleton.py 2>&1 | tail -15
```
Expected: FAIL — `No module named 'xarch.modules.layout.application.logic.beside'`, `cannot import name 'Beside'`,
`unexpected keyword argument 'beside'`, `'FsDisk' object has no attribute 'files'`, `Skeleton has no attribute
'beside'`.

- [ ] **Step 4: Carry beside through the contract**

In `xarch/modules/spec/contract/__init__.py`, `Skeleton`: add after `names: str = ""`:
```python
    beside: bool = False
    test_files: tuple[str, ...] = ()
    kept: tuple[tuple[str, ...], ...] = ()
```
and end its docstring with: `; and whether every test of a part sits beside the code it tests (beside,
testing.beside), the patterns of a test file's name (test_files), and the folders below the tests root whose tests
stay there under beside (kept: each tier's folder, then the fakes' folder).`

In `xarch/modules/spec/application/services/publishing.py`, replace the `return Skeleton(...)` of `skeleton` with:
```python
        framework = architecture.framework
        kept = (*(tier.folder for tier in architecture.tiers if tier.folder),
                *((architecture.fakes.folder,) if architecture.fakes is not None else ()))
        return Skeleton(top_level=tuple(walk(architecture.top_level_tree())), repeating=repeating,
                        title=checked.title, package_file=checked.package_file, private=checked.private,
                        reserved=language.reserved_names, names=language.names,
                        beside=framework is not None and framework.beside,
                        test_files=framework.files if framework is not None else (), kept=kept)
```

- [ ] **Step 5: The layout value, the logic and the ports**

In `xarch/modules/layout/domain/structure.py`, after `class Naming` add:
```python
@dataclass(frozen=True)
class Beside:
    """Where the tests sit when every test of a part sits beside the code it tests (testing.beside): the patterns of a
    test file's name, matched against the file name alone with `*` for any text, and the folders below the tests root
    whose tests stay there (each tier's `folder`, and the fakes' folder)."""
    files: tuple[str, ...]
    kept: tuple[tuple[str, ...], ...]
```
(The module already imports `dataclass`; check its imports and add it if not.)

Create `xarch/modules/layout/application/logic/beside.py`:
```python
"""The test-tree rule under testing.beside: every test file below the tests root lies in a folder whose tests stay
there, a tier's `folder` or the fakes' folder; any other belongs beside the code it tests."""
from __future__ import annotations

from collections.abc import Iterable
from fnmatch import fnmatchcase

from xarch.kernel.logic.names import is_private_name
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.structure import Beside, Naming

STRAY = "lies below the tests folder, but testing.beside keeps the tests of a part beside its code"
STRAY_FIX = "move it beside the code it tests"


def stray(tests: str, files: Iterable[tuple[str, ...]], beside: Beside, naming: Naming) -> list[Violation]:
    """Every test file below the tests root, each given by its path below it, that lies in no folder beside keeps,
    sorted by path: a file whose name no pattern of beside matches is no test, and one in a folder whose name, or the
    name of a folder above it, is private in the language is never read; tests names the tests root in violations."""
    found: list[Violation] = []
    for path in sorted(files):
        if not path or any(is_private_name(step, naming.private) for step in path[:-1]):
            continue
        if not any(fnmatchcase(path[-1], pattern) for pattern in beside.files):
            continue
        if any(path[:len(folder)] == folder for folder in beside.kept):
            continue
        found.append(Violation("/".join((tests, *path)), 0, STRAY, "test-tree", STRAY_FIX))
    return found
```

In `xarch/modules/layout/application/ports/skeleton.py`, import `Beside` beside `Naming`
(`from xarch.modules.layout.domain.structure import Beside, Naming`) and add to the Protocol:
```python
    def beside(self, profile: str) -> Beside | None:
        """Where the tests sit when every test of a part sits beside the code it tests; None when the profile keeps
        them in the mirrored tests tree."""
        ...
```
In `xarch/modules/layout/application/ports/disk.py` add to the Protocol:
```python
    def files(self, root: Path) -> list[tuple[str, ...]]:
        """Every file below root, at any depth, that the disk shows (none it hides, nor any in a folder it hides), as
        its path below it, sorted; [] if root is no folder."""
        ...
```

- [ ] **Step 6: The adapters and the fakes**

In `xarch/modules/layout/adapters/spec_skeleton.py`, import `Beside` (`from xarch.modules.layout.domain.structure
import Beside, Naming`) and add to `SpecSkeleton`, before `_skeleton`:
```python
    def beside(self, profile: str) -> Beside | None:
        skeleton = self._skeleton(profile)
        return Beside(skeleton.test_files, skeleton.kept) if skeleton.beside else None
```
In `xarch/modules/layout/adapters/fs_disk.py`, change the import to
`from xarch.platform.filesystem import HIDDEN, FileSystem` and add:
```python
    def files(self, root: Path) -> list[tuple[str, ...]]:
        below = (tuple(path.split("/")) for path in self._fs.files_below(root))
        return [steps for steps in below if not any(step.startswith(HIDDEN) for step in steps)]
```
In `tests/fakes/layout_skeleton.py`, import `Beside` (`from xarch.modules.layout.domain.structure import Beside,
Naming`), add the parameter `beside: Beside | None = None` after `refused` in `__init__` (store it as
`self._beside = beside`), say in the class docstring `; and where the tests sit under testing.beside (None: they
mirror the app)`, and add:
```python
    def beside(self, profile: str) -> Beside | None:
        return self._beside
```
In `tests/fakes/filesystem.py`, `FakeDisk`, add:
```python
    def files(self, root: Path) -> list[tuple[str, ...]]:
        return sorted(f.relative_to(root).parts for f in self._files if f.is_relative_to(root))
```

- [ ] **Step 7: Run `stray` in place of `unmirrored` under beside**

Replace the body of `StructureCheckService.check` in
`xarch/modules/layout/application/services/structure_check.py` from `found = missing(...)` to the end with:
```python
        found = missing(required, self._disk.present(root, required))
        if tests is None:
            return StructureChecked(tuple(found))
        beside = self._skeleton.beside(profile)
        if beside is not None:
            found += stray(tests.name, self._disk.files(tests), beside, naming)
        else:
            for each in roots:
                found += unmirrored(tests.name, package, each, self._disk.below(tests, each),
                                    set(self._disk.below(root, each)), naming)
        return StructureChecked(tuple(found))
```
add the import `from xarch.modules.layout.application.logic.beside import stray`, and extend the docstring:
`... then every folder below the tests of each repeating folder that mirrors no folder of the app; under
testing.beside, every test file below the tests that lies in no folder whose tests stay there instead.`

- [ ] **Step 8: Run the tests to see them pass**

Run the command of Step 3; then
`timeout 900 uv run pytest -q tests/modules/layout tests/modules/spec tests/modules/scaffold 2>&1 | tail -3`.
Expected: PASS; the existing `test_structure_check.py` tests (without beside) are unchanged and pass.

- [ ] **Step 9: Lint, self-check, commit**

```bash
uv run ruff check xarch tests && uv run xarch check; echo "exit $?"
git add xarch/modules/spec/contract/__init__.py xarch/modules/spec/application/services/publishing.py \
  xarch/modules/layout tests/fakes/layout_skeleton.py tests/fakes/filesystem.py tests/modules/layout \
  tests/modules/spec/application/test_skeleton.py
git commit -m "Under testing.beside, test-tree reports a test file left below the tests root outside every tier folder and the fakes' folder, and no longer reads the mirrored folders"
```
Expected before the commit: `All checks passed!`, `exit 0` (the new module `layout/application/logic/beside.py` lies
in layout's `logic` part, and its test mirrors it).

---

### Task 6: `check` reads the app's tests beside the code, end to end

**Files:**
- Modify: `xarch/modules/rules/application/services/source_check.py:3-20, 74-87` and the `check` docstring
- Create: `tests/bootstrap/test_tests_beside.py`

**Interfaces:**
- Consumes: `tier_of.is_test_file` and `SourceFile.beside` (Task 3), the rules of Task 4, the layout of Task 5,
  the parser of Task 1.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write the failing end-to-end tests**

Create `tests/bootstrap/test_tests_beside.py`:
```python
"""Tests beside the code, wired: a scratch project whose profile says testing: {preset: pytest, beside: true} is
checked through the real reader. A test of a part sits beside its code, read as a test of the tier its part names and
never as code of its part; a test left below the tests folder is reported by test-tree; a tier's folder keeps its
tests below the tests folder. The same project without beside reads that file as app code."""
from pathlib import Path

from tests.bootstrap.project import app_check, write

PROFILE = """\
name: near
testing: TESTING
parts:
  domain:
    path: modules/<module>/domain
    role: the rules of a module
    tests: unit
  contract:
    path: modules/<module>/contract
    role: the results of the use cases
    imports: {may: [domain]}
    tests: unit
  application:
    path: modules/<module>/application
    role: the use cases
    imports: {may: [domain, contract]}
    holds: {classes: {names: "*Controller"}, functions: {names: "build_*"}}
    tests: unit
  scripts:
    path: scripts
    role: one-off scripts
    untested: run by hand
tiers:
  unit:
    proves: a rule
    litmus: Does it decide?
  guard:
    proves: the architecture
    litmus: Does it read the source?
    folder: architecture
fakes: {folder: fakes, for: [domain]}
excluded: {vendor: copied code}
guards:
  scenario-coverage: {results: contract, tier: unit, suffix: Result, columns: [given, when, then], file: "test_{name:snake}.py"}
  closed-tree: {}
"""
BESIDE = "{preset: pytest, beside: true}"
PUBLISH = '''"""Publish a document."""
from app.modules.docs.contract.results import Missing, Published, PublishResult


class PublishController:
    """Publishes a document when it exists."""

    def publish(self, found: bool) -> PublishResult:
        return Published() if found else Missing()
'''
TABLE = '''"""Use case: publish a document."""
import pytest

from app.modules.docs.application.publish import PublishController
from app.modules.docs.contract.results import Missing, Published


@pytest.mark.parametrize("given, when, then", [
    pytest.param(True, "publish", Published, id="a document that exists is published"),
    pytest.param(False, "publish", Missing, id="a document that does not exist is missing"),
])
def test_publish(given, when, then):
    assert isinstance(PublishController().publish(given), then)
'''
NEAR = "app/modules/docs/application/test_publish.py"
APP = {
    "__init__.py": "",
    "modules/__init__.py": "",
    "modules/docs/__init__.py": "",
    "modules/docs/domain/__init__.py": "",
    "modules/docs/domain/document.py": '"""A document."""\n\n\nclass Document:\n    """A document."""\n',
    "modules/docs/contract/__init__.py": "",
    "modules/docs/contract/results.py":
        '"""The results."""\n\n\nclass Published:\n    """Published."""\n\n\nclass Missing:\n    """Missing."""\n\n\n'
        "PublishResult = Published | Missing\n",
    "modules/docs/application/__init__.py": "",
    "modules/docs/application/publish.py": PUBLISH,
    "modules/docs/application/test_publish.py": TABLE,
    "scripts/__init__.py": "",
    "scripts/seed.py": '"""Seed the store."""\n\n\ndef run():\n    return 1\n',
    "vendor/test_copied.py": "def test_copied(:\n",
}
TESTS = {
    "conftest.py": "",
    "fakes/document.py": '"""A fake."""\n\n\nclass FakeDocument:\n    """A fake document."""\n',
    "architecture/test_rules.py": "from pathlib import Path\n\n\ndef test_rules():\n    assert Path\n",
}
STRAY = ("lies below the tests folder, but testing.beside keeps the tests of a part beside its code",
         "move it beside the code it tests")


def check(tmp_path: Path, testing: str = BESIDE, app: dict[str, str | None] | None = None,
          tests: dict[str, str | None] | None = None, with_tests: bool = True):
    """The violations of `xarch check` on the scratch project, its app and tests as given over APP and TESTS (None
    removes a file), its profile's testing as given, and its tests folder given to check unless with_tests is false."""
    app_files = {k: v for k, v in {**APP, **(app or {})}.items() if v is not None}
    test_files = {k: v for k, v in {**TESTS, **(tests or {})}.items() if v is not None}
    root = write(tmp_path / "app", app_files)
    folder = write(tmp_path / "tests", test_files)
    (tmp_path / "near.yaml").write_text(PROFILE.replace("TESTING", testing))
    return app_check(root, str(tmp_path / "near.yaml"), folder if with_tests else None).violations


def of(violations, file: str) -> list[tuple[str, str, str]]:
    return [(v.rule, v.message, v.fix) for v in violations if v.file == file]


def test_a_test_beside_the_code_is_a_test_and_no_code_of_its_part(tmp_path):
    found = check(tmp_path)
    assert of(found, NEAR) == []
    assert [v for v in found if v.rule == "scenario-coverage"] == []
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_beside_the_code_imports_only_what_its_part_may_and_is_named_by_its_app_path(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": "from app.scripts.seed import run\n" + TABLE})
    assert [(rule, message.split(":")[0]) for rule, message, _ in of(found, NEAR)] == [
        ("tiers", "a test of application/ (unit tier) may not import scripts/ (app.scripts.seed)")]


def test_the_guard_finds_the_table_test_beside_the_code_and_misses_it_when_it_is_gone(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": None})
    assert [(v.file, v.message) for v in found if v.rule == "scenario-coverage"] == [
        ("app/modules/docs/contract/results.py",
         "PublishResult has no test file test_publish.py among the unit tests of docs (scenario-coverage)")]


def test_a_test_left_below_the_tests_folder_is_reported_by_test_tree(tmp_path):
    found = check(tmp_path, tests={"modules/docs/application/test_publish.py": TABLE})
    assert [(v.file, v.line, v.message, v.fix) for v in found if v.rule == "test-tree"] == [
        ("tests/modules/docs/application/test_publish.py", 0, *STRAY)]


def test_a_test_in_a_tier_s_folder_stays_there_and_is_held_to_its_tier(tmp_path):
    assert of(check(tmp_path), "tests/architecture/test_rules.py") == []
    found = check(tmp_path, tests={"architecture/test_rules.py": "from app.modules.docs.domain.document import Document\n"})
    assert [(rule, message.startswith("a guard test may not import domain/"))
            for rule, message, _ in of(found, "tests/architecture/test_rules.py")] == [("tiers", True)]


def test_without_beside_the_same_file_is_code_of_its_part_and_the_mirrored_tree_is_not_reported(tmp_path):
    found = check(tmp_path, "pytest", tests={"modules/docs/application/test_publish.py": TABLE})
    assert "names" in [rule for rule, _, _ in of(found, NEAR)]
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_beside_the_code_of_an_untested_part_says_its_part_is_untested(tmp_path):
    found = check(tmp_path, app={"scripts/test_seed.py": "def test_seed():\n    assert True\n"})
    assert of(found, "app/scripts/test_seed.py") == [
        ("tiers", "lies in no tier: its part is untested", "test the part with a tier, or move the test")]


def test_a_test_beside_the_code_may_not_import_another(tmp_path):
    found = check(tmp_path, app={
        "modules/docs/application/test_other.py": "def test_other():\n    assert True\n",
        "modules/docs/application/test_publish.py":
            "from app.modules.docs.application.test_other import test_other\n" + TABLE})
    assert [message.split(":")[0] for rule, message, _ in of(found, NEAR) if rule == "tiers"] == [
        "a test may not import another test file (app.modules.docs.application.test_other)"]


def test_a_broken_test_beside_the_code_is_reported_once(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_broken.py": "def test_broken(:\n"})
    assert [rule for rule, _, _ in of(found, "app/modules/docs/application/test_broken.py")] == ["syntax"]


def test_without_a_tests_folder_the_tests_beside_the_code_are_still_checked(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": "from app.scripts.seed import run\n" + TABLE},
                  with_tests=False)
    assert [rule for rule, _, _ in of(found, NEAR)] == ["tiers"]
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_in_an_excluded_folder_is_not_read(tmp_path):
    assert [v for v in check(tmp_path) if v.file.startswith("app/vendor")] == []
```

- [ ] **Step 2: Run them to see them fail**

```bash
timeout 600 uv run pytest -q tests/bootstrap/test_tests_beside.py 2>&1 | tail -20
```
Expected: FAIL — `of(found, NEAR)` holds `names` (and maybe `closed-tree`) findings: the file is still read as app
code. The `test-tree` and excluded tests may already pass (Task 5); that is expected.

- [ ] **Step 3: Split the app's test files out in `source_check`**

In `xarch/modules/rules/application/services/source_check.py`, add to the imports
`from xarch.modules.rules.application.logic.tier_of import is_test_file`, and replace lines 78-86 (from
`app = self._tree.read(root, ...)` through the `test_files = ...` statement) with:

```python
        framework = rules.framework
        tables = framework.tables if framework is not None else ()
        declared = framework.declared if framework is not None else ()
        bound = framework.globals if framework is not None else ()
        code = [p for p in paths if governed.governed(rules, p)]
        near = {p for p in code if framework is not None and framework.beside and is_test_file(rules, p)}
        app = self._tree.read(root, [p for p in code if p not in near], immutable=marks,
                              interface=interface, standard=standard, private=private, special=special)
        beside = [replace(f, beside=True) for f in self._tree.read(root, [p for p in code if p in near], tables, marks,
                                                                   interface, standard=standard, private=private,
                                                                   special=special, declared=declared, globals=bound)]
        test_files = [*beside, *(self._tree.read(tests, self._tree.paths(tests, extensions), tables, marks, interface,
                                                 standard=standard, private=private, special=special,
                                                 declared=declared, globals=bound) if tests is not None else [])]
```
(`replace` is already imported from `dataclasses`.) In the `check` docstring replace `... the app's with none, so an
app file holds no test.` with `... the app's with none, so an app file holds no test; under testing.beside, a
governed file of the app whose name the test files match is a test beside the code, read as a test with its path
below the app root, and no file of the app.`

- [ ] **Step 4: Run them to see them pass**

Run the command of Step 2. Expected: PASS. If a finding's text differs from an assertion only in the wording of a
sentence that existed before this card (for example the `tiers` import sentence), read the real sentence from the
output, confirm it is today's sentence for a mirrored test of the same import, and adjust the assertion to it; never
change the spec's new texts (`lies in no tier: its part is untested`, the test-tree sentence).

- [ ] **Step 5: Run the rules and bootstrap suites**

```bash
timeout 900 uv run pytest -q tests/modules/rules tests/bootstrap 2>&1 | tail -5
```
Expected: all pass (the bundled profiles and the corpora write no `beside`, so every recorded run is unchanged).

- [ ] **Step 6: Lint, self-check, commit**

```bash
uv run ruff check xarch tests && uv run xarch check; echo "exit $?"
git add xarch/modules/rules/application/services/source_check.py tests/bootstrap/test_tests_beside.py
git commit -m "check reads a test beside the code as a test of its part's tier and no code of the part, proved on a scratch project"
```

---

### Task 7: README, CHANGELOG, golden docs, gates

**Files:**
- Modify: `README.md:116` (profile block) and `:184-186` (after the `testing.preset` sentence)
- Modify: `CHANGELOG.md` (`[Unreleased]` / `### Added`, after the `testing` may name its preset entry)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: everything above.
- Produces: docs only.

- [ ] **Step 1: README**

Replace line 116
```
testing:  <preset> | {preset} | {files*, declared*, globals, skips, tables, mocks}
```
with
```
testing:  <preset> | {preset, beside} | {files*, declared*, globals, skips, tables, mocks, beside}
```
After the sentence ending `... and a project with its own `files` writes the whole map instead; `testing: pytest` is
its short form.` (line 186) insert:
```
`testing: {preset: pytest, beside: true}` keeps every test of a part beside its code: a file of the app whose name
`files` matches is a test of the tier its part names, never code of its part; a tier with a `folder` keeps its tests
below the tests root, and a part may not name such a tier; `test-tree` then reports a test left below the tests root
outside every tier `folder` and the fakes' folder.
```

- [ ] **Step 2: CHANGELOG**

Under `## [Unreleased]` / `### Added`, after the entry that starts `` - `testing` may name its preset as a map ``, add:
```
- `testing.beside`: `testing: {preset: pytest, beside: true}` (or `beside: true` in the whole map) keeps every test
  of a part beside the code it tests. A file of the app whose name `testing.files` matches is then a test of the tier
  its part names, read with the framework's forms and never as code of its part; a finding on it names its app path.
  A tier with a `folder` keeps its tests below the tests root, and a part that names such a tier in `tests` is refused
  (`tiers.guard: parts.domain says tests: guard, and guard keeps its tests in tests/architecture: under
  testing.beside a part's tests sit beside its code; give the part a tier with no folder`). `test-tree` reports a test
  file left below the tests root outside every tier `folder` and the fakes' folder (`lies below the tests folder, but
  testing.beside keeps the tests of a part beside its code: move it beside the code it tests`), in place of the
  folder check of the mirrored tree. A test beside the code with no tier says `lies in no tier: its part is untested`
  or `lies in no part`. A preset may not say `beside`; `profile check` lists `testing.beside` as looser; `xarch
  profile explain testing.beside` explains it, and the "use ..." list of `testing` gains `beside`.
```

- [ ] **Step 3: Run the README test**

```bash
timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | tail -3
```
Expected: PASS.

- [ ] **Step 4: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-6-10/regenerate_docs.py` (outside the worktree):
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
mkdir -p /tmp/xarch-6-10
uv run python -I /tmp/xarch-6-10/regenerate_docs.py "$PWD"
git status --short -- docs/cli docs/web docs/xarch
git diff --stat -- docs/cli docs/web docs/xarch
```
Expected: `written`; no file listed; no diff. If a golden doc moved, do not hand-edit it: restore with
`git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 5: Run every gate**

```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
git diff --quiet 9db8c30 -- xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml \
  xarch/architectures/presets/testing tests/bootstrap/corpora && echo "profiles, presets and corpora unchanged"
grep -rn "beside" xarch/architectures/cli.yaml xarch/architectures/web.yaml architecture.yaml \
  xarch/architectures/presets/testing; echo "beside in a bundled profile or preset: $?"
timeout 900 uv run pytest -q > /tmp/xarch-6-10/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-6-10/suite.log
tail -5 /tmp/xarch-6-10/suite.log
```
Expected: `All checks passed!`; exit 0 for each `xarch` command; `profiles, presets and corpora unchanged`;
`beside in a bundled profile or preset: 1`; `N passed`, no failure or error, last line `exit 0`.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say testing.beside keeps every test of a part beside its code, with the R4 refusal and the test-tree report; the golden docs regenerate unchanged"
```

---

## Self-Review

**Spec coverage:**
- B1 (the key): Task 1 Steps 1, 3, 6, 7 — forms table (tests 1, 2, 3; `{beside: true}` alone keeps today's
  "missing" problems, covered by the unchanged `test_a_bad_testing_key_is_refused` rows plus the new beside branch
  returning no new text when tiers exist), skipped by 6.9's refusal (`_SETTINGS`, test 8), not walked by needs (Task
  1 needs test), the "use ..." lists (Step 2, test 9), the preset refusal (test 10).
- B2 (refusals 1-4): Task 1 tests 4, 5, 6, 7, and the both-reported test (B2.4); the file prefix in
  `tests/bootstrap/test_profile_file.py`.
- B3 (what `check` reads): Task 3 (facts: `in_tests`, `is_test`, tier, mirrors, `place` None, `known`/`known_tests`;
  filters: tests side, `mirrors-a-part`, `below`), Task 4 (tiers, scenario-coverage, stand-ins, never a fake), Task 6
  (`source_check` split; end-to-end: no app-side finding on it, named by its app path, syntax once, excluded not
  read). Without beside the file is app code: Task 6
  `test_without_beside_the_same_file_is_code_of_its_part_and_the_mirrored_tree_is_not_reported`.
- B4 (tier of a test beside the code): Task 3 `test_tested_beside` (rules 1, 2, 3), Task 4 tiers texts (untested,
  no part, mirrored keeps `NO_TIER`), Task 6 untested-part test.
- B5 (`test-tree`): Task 5 logic tests (reported, tier folder, fakes, non-test, `__pycache__`, sorted, one sentence),
  service tests (`unmirrored` not run, no tests root), Task 6 end-to-end. Without beside unchanged: the existing
  `test_structure_check.py` tests stay as they are.
- B6 (looseness): Task 2 (tests 12, 13, 14; `test_origin`; `published.py` docstring; `architecture.yaml` lists none).
- B7 (texts, docs, explain): key table and `keys.yaml` (Task 1 Step 6; the example is the whole map, see the note in
  that step), parser docstring (Step 7a), explain tests (Task 1 Step 3), README and CHANGELOG and golden docs (Task 7).
- Gates: Task 7 Step 5.

**Deviation from the spec, stated:** the `keys.yaml` example of `testing.beside` writes the whole map
(`<<testing>>` plus `beside: true`) instead of `testing: {preset: <preset>, beside: true}`, because `explain` fills
`<preset>` only for a key that offers the presets as choices, and `beside` must not (it is a bool).

**Placeholder scan:** no TBD/TODO; every code step shows its code. Two steps tell the executor to read one name before
writing (`Saying.when` in Task 4, the `dataclass` import in `structure.py`), each with the file to read.

**Type consistency:** `tested(profile, path, beside=False)` (Task 3) is called as `tested(profile, file.path,
file.beside)` in Tasks 3 and 4; `is_test_file(profile, path)` (Task 3) is used in Task 6; `Facts.beside` (Task 3) is
read in `facts._into_tests` and `sentences._target`; `Beside(files, kept)` (Task 5) matches `Skeleton.test_files` and
`Skeleton.kept`; `stray(tests, files, beside, naming)` matches its call in `structure_check`.

**Review Focus:** each of the five lines names its test and the task that owns it.

<!-- task-pipeline: validated -->
