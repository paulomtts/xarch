# 7.1 spec: `parts` becomes the folder tree, in the parser with the writer

Card: 4375f8b4-dfb5-48f7-ac88-9b174bb24188 (subtask of 49165a1c). This is release step 23 of the merged order
(`0.3.0-cohesion-review-3.md`, section 3, row 23 at line 286), without its measure of the placement record, which is
card 7.2.

Parent design spec: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-form-proposal.md` ("the note"). This
card implements 5.1 (lines 500-580), 5.2 (lines 582-606), 5.3 (lines 608-643), 5.4 (lines 645-670, all but the
measure) and 2.5 option A (lines 183-222). The reading-order target is `demo/web-0.3.0-tree.yaml` in the same folder.
From `0.3.0-cohesion-review-3.md` ("review 3"): Q2 (line 48), O4, O5, O8 (lines 228-232) and row 23 (line 286).

## Goal

Under `parts`, the profile writes the app's folder tree. A key that ends in `/` is a folder, a key that holds a dot is
a file, and any other key is a key of a part. A folder with a `role` is a part, and a file is always a part. The words
`path` and `folders` leave the part, and `name` joins it. The placement order is the tree's reading order. The bundled
profiles, xarch's own profile, the archived profiles and every fixture are written as trees. The writer writes the
same nested form.

## What is already done (not to be redone)

- `parse_profile` (`xarch/modules/spec/application/logic/profile_parsing.py:173-240`) reads `parts` as a flat map
  from name to spec. `_specs` (282-293) checks the names. `_layout` (296-335) reads `path` and `folders` and builds
  `_Layout(parts, tree, notes, repeats)`. `_path`, `_shown`, `_repeats_alike`, `_insert`, `_folders` and `_add_folder`
  (338-462) hold the rules of a path: no empty, `.` or `..` step, no `*` step, one `<word>` per path, one word per
  folder, one folder per word, nothing below a file, and a last step that holds a dot is a file.
- Everything after `_layout` reads `specs[name]` by part name. That includes `iw.group`, `_substance`, `_never_refs`,
  `_tiers`, `_tests_beside`, `_guards` and `_fakes`. Every problem is addressed `parts.<name>...`.
- The model keeps `Part.path` (steps, with `EACH` for the repeating step), `Architecture.tree`, `notes`, `repeats` and
  `placement` (`xarch/modules/spec/domain/values.py`, `placement` documented at 365, field at 402). The readers of
  `placement` are `docs_template._placement` (213-216, `ARROW = " → "`) and review's placement question
  (`review/application/logic/questions.py:18-22`, in `ProfileView.parts` order, which `publishing.py:64-69` builds from
  `architecture.parts`).
- Duplicate keys at one level are already refused by the loader (`platform/data_files.py`).
- Retired keys are refused through `RETIRED` (`xarch/modules/spec/domain/profile_keys.py:189-228`), with the text
  `unknown key '<k>': <text>; use <known>` (`ck.unknown_of` / `ck.unknown_keys`, `profile_checks.py:781-805`).
- `YamlWriter` (`xarch/platform/yaml_writer.py`) writes keys through `_scalar`. `_PLAIN` already writes
  `modules/<module>/`, `domain/`, `controller.py` and `__main__.py` plain. It quotes `[slug]/`, `@types/` and
  `(group)/`.
- `profile new` (`profile_creation.py`) copies the bundled file's text. A copy therefore has the tree form as soon as
  the bundled file has it.

## Inherited constraints

- The form (note 5.1, rules 1-6, lines 525-535):
  1. Under `parts`, a key that ends in `/` is a folder of one or more steps. A key that holds a dot and does not end
     in `/` is a file. Any other key must be a key of a part, and an unknown one is refused with the list.
  2. A folder with a `role` is a part. A folder with another key of a part and no `role` is refused with "missing
     `role`". A folder with neither is only a folder, and its value may be one line of text, its note.
  3. A file is always a part and needs a `role`.
  4. A part's name is its folder's last step, or the file's name before its first dot. `name:` replaces it. Two parts
     with one name are refused, and the message names both paths and shows `name:`. xarch never invents a name (note
     section 6, line 690).
  5. A part inside a part is allowed. A file belongs to the deepest part around it.
  6. At most one `<word>/` on the way down to a part, one word per folder, one folder per word. These are today's
     rules, read from the keys.
- Addresses stay by name: `parts.<part>.<key>` (rule 7, line 536; review 3 dodge "printing a part by tree path in some
  messages").
- The placement order is the tree's reading order: top to bottom, a part before the parts inside it (rule 8, line 537;
  2.5 option A; review 3 Q2, line 48). The rule is stated once in `profile explain parts` and in the README.
- A folder is written once (note 4 item 6, lines 482-485). A folder with children carries no note. A folder carries no
  rules for the parts below it (note 2.8, line 241; "Rulings already given", lines 27-30).
- The fixed order of keys is `name`, `role`, `litmus`, `imports`, `uses`, `holds`, `shared`, `package_only`, `tests`
  or `untested`, then the folders below. It is shown and written, not enforced (note 2.3, lines 166-168).
- The writer writes the nested form, joins chains of single folders, and puts parts in the tree's reading order (note
  5.4, line 659). It must never emit only joined keys (note 6, line 692).
- Part keys: `path` and `folders` go out and `name` comes in (note 5.2, lines 596-600). Each removed key has a retired
  entry with its hint, and an old flat profile gets one message (note 5.3, line 621; 5.4, lines 654-656).
- A file key holds one of the language's extensions (note 5.3, lines 639-641; card).
- Litmus texts stay on their part, word for word, re-wrapped for their new indent (note "Rulings", line 15; 4 item 7).
- Golden docs: they are regenerated and their diff is read, never edited by hand (review 3 O8, line 232). README and
  CHANGELOG lines go under `[Unreleased]` (O4, O5, lines 228-229).
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as the note says;
  Python only in the reader adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays out of
  commits; nothing is pushed.
- Dodges that this card must not take (card; note section 6): accepting `path:` beside the tree; keeping `path:` as an
  override; reading an unknown key with no `/` and no dot as a folder; inventing a name when two folders clash; rules
  on a folder passing down; a writer that emits only joined keys; printing a part by tree path in some messages;
  changing the placement order without saying so; writing a folder twice; loosening the "use ..." lists.

## Behavior

### B1. Reading the tree

The first pass walks `parts` depth first, keys in the order the file writes them. A joined key (`modules/<module>/`)
is read as its steps, one folder after another. For each part, the pass yields four things:

- its name (rule 4);
- its steps from the app root (`Part.path`, with `EACH` for a `<word>` step, as today);
- its place in the reading order (0 for the first part met);
- a flat map of its own keys, without the folder and file keys below it.

For each folder that is not a part, the pass yields its steps and its note ("" when it has none).

Everything after the pass reads the specs by name, exactly as it does today. The result must hold three things:

- `Architecture.parts` is in reading order, and `Architecture.placement == tuple(Architecture.parts)`.
- `tree`, `notes` and `repeats` equal what today's flat profile with the same paths and `folders` builds. A former
  `folders` entry becomes a folder node, with its note if it had one.
- Each `Part` equals today's except for its order.

A folder's value takes one of three forms:

| Value | Meaning |
|---|---|
| a map | its keys: part keys, folder keys, file keys |
| a string of one line | a folder that is no part, with that note |
| `null` or `{}` | a folder that is no part, with no note |

A file's value must be a map with `role`.

### B2. The placement order (option A)

The placement order is pre-order: a part comes before the parts inside it, and siblings run top to bottom. Once the
three profiles are rewritten (B6), their orders are:

- web: `domain → logic → ports → services → controller → adapters → contract → platform → web → bootstrap → kernel →
  kernel-logic`
- cli: the same, with `cli` in place of `web`
- xarch: `domain → logic → ports → services → controller → adapters → contract → platform → cli → reports → main →
  bootstrap → profile-values → kernel → kernel-logic`

Against today, that is the change of the note's table (2.5): `contract` moves up (web and cli 10th to 7th, xarch 12th
to 7th), and `kernel` and `kernel-logic` swap. Review's placement question offers its options in this new order. The
measure of whether its answers move is card 7.2.

The `{{placement}}` refusal with no part keeps its condition. Its text becomes `the architecture has no placement
order: write its parts under `parts`, whose reading order is the order the litmus tests run in`.

### B3. Refusals of the tree

Every problem is collected, as today, and is addressed by part name when the place is a part. The texts below are
exact. `<known>` is `ck.unknown_keys`' sorted list of `names_of(PART)`, which is now `holds, imports, litmus, name,
package_only, role, shared, tests, untested, uses`. `<endings>` is `_endings(language)` (for Python, `.py`).

| # | Written | Problem |
|---|---|---|
| 1 | `parts` not a map | `parts: must be the folder tree of the app: folders ending in /, files with their extension` |
| 2 | a key with no `/` and no dot directly under `parts`, whose value is no map holding `path` | `parts: unknown key 'rol': a key under parts is a folder ending in / or a file ending in <endings>` |
| 3 | a folder holding a part key and no `role` | `parts.<name>: missing `role`` |
| 4 | a file whose value is not a map | `parts.<name>: a file is a part: write it as a map with role` |
| 5 | a file map with no `role` | `parts.<name>: missing `role`` |
| 6 | a file key that ends in none of the language's extensions (checked only when the language lists any) | `parts.<name>: '<path>' is a file, since its key holds a dot, but it does not end in <endings>: write a folder as <key>/` |
| 7 | two parts with one name | `parts.<name>: '<path 1>' and '<path 2>' are both named <name>: write name: <part name> on one of them` (paths as shown, folders with a trailing `/`, in reading order) |
| 8 | a folder written twice: two keys of one map whose steps introduce the same folder (`kernel/` and `kernel/logic/`; `modules/<module>/domain/` and `modules/<module>/adapters/`) | `parts: the folder '<path>/' is written twice, in '<key 1>' and '<key 2>': write it once and nest what lies in it` |
| 9 | an unknown key with no `/` and no dot inside a folder | `parts.<name>: unknown key 'rol': use <known>` (dodge 3: never a folder) |
| 10 | `path` inside a node | `parts.<name>: unknown key 'path': moved in 0.3.0: a part is the folder or file it is written as under parts: drop it; use <known>` (retired entry) |
| 11 | `folders` inside a node | `parts.<name>: unknown key 'folders': moved in 0.3.0: write each folder below the part as a key ending in /, with its note as its value; use <known>` (retired entry) |
| 12 | a name that is no part name, from the folder or from `name:` | `parts: '<path>' is named '<n>', which is not a part name: write name: with letters, digits, '_' and '-'` |
| 13 | a folder whose value is a string of several lines, a list or a number | `parts: '<path>/': a folder is a map, one line of text (its note), or nothing` |
| 14 | a folder or file below a file | `parts.<name>: '<path>' is a file and holds nothing below it` |
| 15 | a step that is empty, `.`, `..`, holds `\`, `*`, or `<`/`>` that is not one word between them | today's `_path` texts, with `parts: '<key>'` in place of `<where>.path: '<value>'` |
| 16 | two repeating steps on the way to a part, two words in one folder, or one word in two folders | today's `_path` / `_repeats_alike` texts, with `parts.<name>: '<path>'` in place of `<where>.path: '<value>'` |
| 17 | a `<word>/` folder with no part below it | `parts: '<path>/' is a repeating folder with no part below it: write a part in it, or drop it` |

Today's `folders` texts, `.path` texts and `must be a mapping with path and role` are gone, along with the code that
raised them.

### B4. An old flat profile

A key directly under `parts` with no `/` and no dot, whose value is a map holding `path`, is an old part. If `parts`
holds one, the profile is refused before anything else is read. The refusal has one problem per old part, in file
order, and no other problem, so that nothing cascades from parts that were never read:

```
parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the folder it lies in (modules/<module>/); use <known>
parts.platform: unknown key 'path': moved in 0.3.0: write the part as the folder platform/: at the top of parts; use <known>
parts.controller: unknown key 'path': moved in 0.3.0: write the part as the file controller.py: under the folder it lies in (modules/<module>/application/); use <known>
parts.kernel-logic: unknown key 'path': moved in 0.3.0: write the part as the folder logic/: with name: kernel-logic, under the folder it lies in (kernel/); use <known>
```

The folder or file shown is the path's last step: a step with a dot is a file, and any other step is shown with
`/`. `with name: <key>, ` is added only when the key differs from the name that step gives (rule 4). A path that is no
valid string shows `a folder ending in /`, with no parent. A profile that mixes tree keys with old parts gets the
same refusal, so `path:` is never accepted beside the tree (dodge 1).

### B5. Needs, libraries, names

- `profile_needs` walks the parts of the tree. It addresses each one `parts.<name>.<key>` and walks only a part's own
  keys. It never treats a folder key as a part name, and it reaches nested parts (`kernel/logic/` named
  `kernel-logic`).
- `_named_packages` reads each part's `imports.libraries` in reading order, addressed by part name.
- `declared` and `ck.part_names` / `_listed_parts` see part names, not keys.

### B6. The rewritten profiles

All of the following are written as trees with today's content: `xarch/architectures/web.yaml`,
`xarch/architectures/cli.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `df537ca.yaml` and
`stress.yaml`.

- Each part keeps its name, role, litmus (word for word, re-wrapped as `>-` to 120 columns at its new indent) and
  every rule. Nothing is added, not even the demo's `shared: 2`. `name:` is written only where it is needed:
  `kernel-logic` (`kernel/logic/`), `profile-values` (`profile_values/`) and `main` (`__main__.py`).
- Former `folders` become folder keys under their part: `commands/: {}` and `migrations/: {}` in xarch, and `web/`'s
  `routes/`, `i18n/` and `ui/` keep their notes as string values. A part's own former folders come before its child
  parts. Part keys follow the fixed order.
- Top-level order. The bundled profiles follow the demo: `modules/<module>/` (domain, application/{logic, ports,
  services, controller.py}, adapters, contract), then `platform/`, `web/` or `cli/`, `bootstrap/`, `kernel/` (with
  `logic/`). xarch follows note 5.1: `modules/<module>/`, `platform/`, `cli/` (with `commands/`, then `reports/`),
  `__main__.py`, `bootstrap/`, `profile_values/`, `kernel/`. The archived profiles follow the same rule for the parts
  they have.
- Each of the six files must equal what the writer (B7) writes, as data: `parse(written(doc))["parts"] ==
  doc["parts"]` and the key order at every level is the same. Dict `==` ignores order, so the order is compared
  apart, on the nested lists of `(key, ...)` pairs, or on `json.dumps` of both without `sort_keys`.
- The findings corpora (`*.json`, `*.tar.xz`, `stress-7cc6111.json.xz`) do not change. `test_recorded_corpora.py`
  stays green unchanged. If a recorded findings file would move, stop and escalate. Never re-dump it.

### B7. The writer

`YamlProfileFormat.written(document)`, the spec port `ProfileFormat.written`, writes a document whose `parts` is a
tree. The YAML it writes holds that tree in canonical form:

- Every key is split into steps, and the tree is built again.
- A folder that is no part, has no note, and holds exactly one entry is joined with that entry (`modules/` and
  `<module>/` become `modules/<module>/`). No other folder is joined.
- Siblings keep the order they were given. A part's own keys come first, in the fixed order, then its folders and
  files.
- A folder with neither note nor children is written `{}`.

The nesting stays private to the adapter, since adapters do not import spec logic and a public helper used only by
tests would fail `dead-code tests_only`. `YamlWriter` writes each key plain when YAML reads it back as written, and
quoted otherwise: `"[slug]/"`, `"@types/"`. A writer that emits only joined keys, or that writes a folder twice,
fails B7's tests.

### B8. The key table, the format data, the docs

- `key_table.py`: `Key(PART, "path", ...)` and `Key(PART, "folders", ...)` are removed. `Key(PART, "name",
  rules=("structure",))` is added first in the `PART` block. `role` stays required. `RETIRED` gains `(PART, "path",
  ...)` and `(PART, "folders", ...)` with the texts of B3 rows 10-11.
- `xarch/architectures/presets/format/keys.yaml` changes in five places:
  - The `parts` entry states the tree form, rules 1-4 and the reading order (rule 8) once.
  - `parts.<part>.path` and `parts.<part>.folders` are dropped.
  - `parts.<part>.name` is added.
  - The symbols table gains "a key ending in `/` is a folder", and `<word>` is written as a key.
  - Every example with `path:` is written as a tree.
  - The key catalogue must still agree with the table.
- The module docstring of `profile_parsing.py` (lines 17-36) describes the tree in place of `{<part>: {path, ...}}`
  and `folders`.
- README: the profile block (lines 117-118) and the symbols (lines 215-226), with the example at 215, are written for
  the tree, and the reading-order rule is said once. CHANGELOG `[Unreleased]` gains one entry for the change: `parts`
  is the folder tree; `name` is new; `path` and `folders` are retired, with the old-profile message; the placement
  order is the tree's reading order, and `contract` and `kernel-logic` move.
- Golden docs. They are regenerated through the repo's docs path and the diff is read. The expected diff is in
  `docs/{cli,web,xarch}/architecture.md`: the placement line (B2) and only those lines or rows that iterate
  `architecture.parts`, each reordered and otherwise unchanged. `docs/{cli,web,xarch}/testing.md` are expected not
  to move: they print no `{{placement}}`, although the card and O8 name them. Report this mismatch. Any other change
  in the diff is a defect, not something to regenerate past.

## Tests that prove it (written first)

There are three tiers here. Unit tests of pure spec logic and of the adapter and platform writers sit under
`tests/modules/...` and `tests/platform/`, mirroring the code. Bootstrap tests under `tests/bootstrap/` run the wired
loader and CLI on real files. Architecture tests sit under `tests/architecture/`.

### Unit, spec logic: `tests/modules/spec/application/logic/test_profile_parsing.py` (and a mirror of a new tree module, if one is made)

These are unit tests because the first pass and `parse_profile` are pure over a document.

1. A nested tree and the same tree with single chains joined parse to equal `Architecture`s (parts, tree, notes,
   repeats, placement).
2. Reading order: `kernel/` with `logic/` named `kernel-logic` gives placement `(..., kernel, kernel-logic)`.
   `modules/<module>/contract/` written before `platform/` comes before it. Also check that `placement ==
   tuple(parts)`.
3. A folder with a note string and a folder with `{}` or `null` are folder nodes. The note lands in
   `Architecture.notes` at the folder's steps.
4. Names: from the last step, from a file before its first dot (`__main__.py` is `__main__`), and from `name:`.
5. Each refusal of B3, rows 1-17, as one `pytest.param` each, with the exact text. That includes:
   - a typo `rol:` directly under `parts` (row 2);
   - `rol:` inside a folder (row 9), which proves it is not read as a folder;
   - `application/logic/` and `kernel/logic/` with no `name:` (row 7), which proves no name is invented;
   - `kernel/` beside `kernel/logic/` (row 8);
   - `modules/<module>/domain/` beside `modules/<module>/adapters/` (row 8).
6. Several refusals in one file are all listed.
7. Today's repeating-folder tests move to keys and keep their substance: two `<word>`s, two words in one folder, one
   word in two folders.
8. B2's `_Missing` text for a profile with no part (in `test_docs_template.py`).

### Unit, spec logic: `tests/modules/spec/application/logic/test_retired_keys.py`

These are unit tests because the retired texts are tested here.

9. `path:` and `folders:` inside a tree node give rows 10-11. Neither gives any other problem for its node.
10. B4: an old flat profile with `domain`, `platform`, `controller` and `kernel-logic` gives exactly the four lines of
    B4 and no other problem. A mixed profile (one tree key, one old part) gives only the old part's line.
11. Every existing "use ..." list of the part scope is updated to the new `<known>`. None is loosened.

### Unit, spec logic: `tests/modules/spec/application/logic/test_profile_needs.py`

These are unit tests because needs are pure over the key table.

12. A tree with a nested part whose key needs a fact yields `parts.kernel-logic.<key>`, not `parts.kernel.logic/...`.
    A plain folder key yields nothing.

### Unit, spec domain: `tests/modules/spec/application/logic/test_profile_keys.py` / `test_key_catalogue.py`

These are unit tests because they check domain data.

13. The part scope holds `name`, not `path` or `folders`. `role` is required. The catalogue agrees with
    `keys.yaml`. Every example in `keys.yaml` loads.

### Unit, adapter: `tests/modules/spec/adapters/test_yaml_profile_format.py`

These are unit tests because B7 is the adapter's own formatting.

14. A tree given with `modules/: {<module>/: {...}}` is written as `modules/<module>/:`.
15. A part whose own keys are given in another order is written in the fixed order, before its children.
16. `kernel/` (a part) with `logic/` is written nested, never as `kernel/logic/`.
17. A folder with nothing is written `{}`.
18. A note is written as a string.
19. For each of `web.yaml`, `cli.yaml` and `architecture.yaml`, `yaml.safe_load(written(doc))["parts"] ==
    doc["parts"]`, and the key order at every level is the same, compared apart from `==`, which ignores it. This proves B6's "equals what the writer writes" and that the bundled profiles
    show a tree.

### Unit, platform: `tests/platform/test_yaml_writer.py`

These are unit tests because `YamlWriter` is platform code.

20. The keys `modules/<module>/`, `domain/`, `controller.py` and `__main__.py` are written plain. `[slug]/` and
    `@types/` are written quoted. All read back as written. This may pass already, and it pins the behavior.

### Bootstrap

These are bootstrap tests because they run the wired loader and CLI on real files, which no unit test reaches.

21. `tests/bootstrap/test_profile_file.py`: a flat 0.2.0-style profile file is refused (exit 2) with the B4 lines,
    each prefixed by the file.
22. `tests/bootstrap/test_profile_file.py`: a file part with a `.txt` key under `language: python` gives row 6.
23. `tests/bootstrap/test_profile_explain.py`: `profile explain parts` states the reading-order rule.
    `profile explain parts.name` prints its meaning. `profile explain parts.path` refuses as a retired key, the way
    other retired keys do.
24. `tests/bootstrap/test_presets.py` / `test_architecture_files.py`: the bundled profiles load, and their placement
    is B2's order.
25. `tests/bootstrap/test_profile_new.py`: `profile new` of `web` writes a copy whose `parts` is a tree, and which loads.
26. `tests/bootstrap/test_recorded_corpora.py` stays green unchanged against the rewritten archived profiles.

### Architecture and the rest

27. Every fixture with `path:` or `folders:` is rewritten: the builders (`tests/modules/spec/application/builders.py`,
    `helpers.py`, `tests/modules/spec/profiles.py`, `tests/bootstrap/project.py`, `tests/modules/rules/builders.py`,
    `tests/fakes/*`) first, then each test file. A file part gets a real extension. Tests that hold review's option
    order or a part order are updated to B2's order, and only where they read the rewritten profiles.
28. `test_docs.py` / `test_docs_templates.py` stay green against the regenerated golden docs.

### Gates

Each gate must pass on this branch alone:

- `uv run ruff check`
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run xarch profile check architecture.yaml`
- `uv run pytest -q` (over two minutes: run it in the background with `timeout`, and read it at the end)

There is no typecheck command.

## Out of scope

- The measure of the placement record (two review runs) is card 7.2.
- The `placement:` fallback list (option C) is out of scope unless 7.2 calls for it.
- Part references (`parts.<part>`, `<word>.<part>`, the refusal of the word `parts` as a step) belong to step 24. The
  bare names in `imports.may` stay as written today.
- Rule 7's "the first time a message names a part it adds the path" is not applied to today's rule and key messages.
  Only the tree's own refusals (B3, B4) quote paths, as today's `.path` texts do. Every address stays by name.
- The README sentence of Q28 (guards versus part keys) belongs to step 25.
- `excluded` stays top-level and is unchanged. `profile new` keeps copying text, and no migration command is added.
- `docs/superpowers/plans/*.md` (past plans) and `docs/examples/*.py` are not edited.

## Notes for the planner

- Put the walk in a new pure module, such as `xarch/modules/spec/application/logic/parts_tree.py`, with one public
  entry. `parse_profile`, `profile_needs` and `_named_packages` all call it. It returns, in reading order:
  - entries of `(name, steps, word, order, keys)`;
  - folders of `(steps, note)`;
  - the old parts of B4.

  `_layout` then builds `_Layout` from the entries, keeping `_repeats_alike` and `_insert` with reworded addresses,
  and builds `_folders` from the folder records. `_specs` becomes `{entry.name: entry.keys}`.
- Do B4's check in `parse_profile` right after the mapping check, and raise at once.
- Start the fixture rewrite at the builders. A throwaway script may draft it, but each file is read after the script
  runs, and the archived corpora yaml files are finished by hand. Grep `path:` and `"path":` across `tests/` and
  `docs/` and account for each hit.
- Regenerate the golden docs through the path `test_docs.py` uses, and paste the read diff summary into the commit
  message.
