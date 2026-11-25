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
