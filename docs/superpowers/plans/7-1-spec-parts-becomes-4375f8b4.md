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

---

# 7.1 `parts` becomes the folder tree, Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Under `parts`, a profile writes the app's folder tree. Folders end in `/`, files hold a dot, every other key is a key of the part, and the placement order is the tree's reading order. The parser reads the tree, the writer writes it, and every bundled, own, archived and fixture profile is rewritten as one.

**Architecture:** A new pure module, `xarch/modules/spec/application/logic/parts_tree.py`, walks the tree once. It returns the parts in reading order with their own keys, the folders that are not parts with their notes, the old flat parts of B4 and the tree's own problems. `parse_profile`, `profile_needs.short` and `_named_packages` all read parts through it, and everything after it still reads `specs[name]`. The adapter `YamlProfileFormat.written` rebuilds `parts` in canonical form with private helpers before `YamlWriter` dumps it.

**Tech Stack:** Python 3.13, pytest, PyYAML, uv, ruff; xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/7-1-spec-parts-becomes-4375f8b4.md` (above, prepended to this plan).

## Global Constraints

- No comments in xarch's code (`xarch/`). Docstrings are allowed and used, as today.
- Never run `ruff --fix`. Fix lint by hand.
- Tests are written first. Each RED step must be run and seen failing before its GREEN step.
- Examples stay simple, with absolute `app.` imports.
- Recorded corpora (`tests/bootstrap/corpora/`) are edited by hand, and only their three `.yaml` profiles' `parts` block. `*.json`, `*.tar.xz` and `stress-7cc6111.json.xz` are never touched or re-dumped. If `test_recorded_corpora.py` fails after the rewrite, stop and escalate.
- Python appears only in the reader adapter and the data files under `xarch/architectures/presets/`.
- `.claude/` stays out of commits. Nothing is pushed.
- Golden docs (`docs/{cli,web,xarch}/*.md`) are regenerated, never edited by hand, and their diff is read.
- README and CHANGELOG lines go under `[Unreleased]`.
- `<known>` for the part scope is exactly `holds, imports, litmus, name, package_only, role, shared, tests, untested, uses`.
- The fixed key order of a part is `name, role, litmus, imports, uses, holds, shared, package_only, tests | untested`, then the folders and files below.
- Every address stays by part name: `parts.<part>.<key>`.
- Dodges never taken: `path:` beside the tree; `path:` as an override; an unknown plain key read as a folder; an invented name; rules on a folder passing down; a writer emitting only joined keys; a part printed by tree path in other messages; a silent change of placement order; a folder written twice; a loosened "use ..." list.
- Gates (each must pass at the end): `uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`, `uv run pytest -q` (run in the background with `timeout 900`, read at the end).

**The full suite is red from Task 2 until Task 5 ends.** Removing `path` from the key table refuses every flat fixture at once. Tasks 2-4 are gated on the targeted tests each one names. Task 5 makes the whole suite green again, and Task 6 runs every gate.

## Review Focus

1. **A part's own former `folders` and the docs skeleton order.** The layout dict is built from the parts in reading order, then the folder records. That is the insertion order today's parser used (parts, then their `folders`), so `docs/xarch/architecture.md`'s tree keeps `cli/` → `reports/` before `commands/`, even though the file now writes `commands/` first. If the skeleton moves in the regenerated diff, that is a defect. Pinned by Task 3's test `test_a_part_s_own_folders_follow_the_parts_in_the_layout_as_today`.
2. **A key with a dot that is meant as a folder** (`v1.2`, `app.config`). It is read as a file and refused by row 6 with `write a folder as <key>/`, never silently turned into a folder. Pinned in Task 2 (`notes.txt` row 6), and through the CLI in Task 4 (`tests/bootstrap/test_profile_file.py`).
3. **An old flat profile mixed with tree keys.** Only the old parts' lines come back, with no cascade from parts never read. Pinned in Task 3 (`test_retired_keys.py`) and Task 4 (bootstrap).
4. **A non-canonical tree given to the writer** (a nested `modules/: {<module>/: …}`, own keys out of order, an empty `None` folder). It must come out joined, ordered and `{}`, and a part folder with one child must never be joined. Pinned in Task 1.
5. **A refused node cascading.** A part with a bad name, a second part with a taken name, or a repeating folder whose only part was refused must not also give "repeating folder with no part below it". Pinned in Task 2 (`test_a_refused_part_still_counts_as_a_part_below_its_repeating_folder`).

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `xarch/modules/spec/adapters/yaml_profile_format.py` | modify | `written` rebuilds `parts` in canonical tree form (private `_tree`, `_nested`, `_put`, `_joined`, `_PART_KEYS`) |
| `tests/modules/spec/adapters/test_yaml_profile_format.py` | modify | tests 14-18 of the writer |
| `tests/platform/test_yaml_writer.py` | modify | test 20: tree keys plain or quoted |
| `xarch/modules/spec/application/logic/parts_tree.py` | create | the one walk of the tree: `parts_tree`, `PartsTree`, `TreePart`, `TreeFolder` |
| `tests/modules/spec/application/logic/test_parts_tree.py` | create | B1, B3 rows 1-15 and 17, the B4 lines at the walk |
| `xarch/modules/spec/application/logic/profile_checks.py` | modify | `_endings` becomes public `endings` |
| `xarch/modules/spec/domain/key_table.py` | modify | `name` in, `path`/`folders` out |
| `xarch/modules/spec/domain/profile_keys.py` | modify | two `RETIRED` entries |
| `xarch/architectures/presets/format/keys.yaml` | modify | tree texts and examples |
| `xarch/modules/spec/application/logic/profile_parsing.py` | modify | reads the tree, B4 first, new `_layout`, docstring |
| `xarch/modules/spec/application/logic/profile_needs.py` | modify | walks parts by name through `parts_tree` |
| `xarch/modules/spec/application/logic/docs_template.py` | modify | `{{placement}}` refusal text |
| `xarch/architectures/web.yaml`, `cli.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/{7cc6111,df537ca,stress}.yaml` | modify | `parts` written as trees |
| every fixture under `tests/` that writes `path:` or `folders:` | modify | trees |
| `README.md`, `CHANGELOG.md` | modify | the tree form |
| `docs/{cli,web,xarch}/architecture.md` | regenerate | placement line and part-ordered rows |

---

### Task 1: The writer writes `parts` as a canonical tree (B7)

This task stands alone. It goes first because Task 4 uses the writer to draft the rewritten profiles.

**Files:**
- Modify: `xarch/modules/spec/adapters/yaml_profile_format.py:1-48`
- Test: `tests/modules/spec/adapters/test_yaml_profile_format.py`
- Test: `tests/platform/test_yaml_writer.py`

**Interfaces:**
- Consumes: `YamlWriter.dump(document) -> str` (unchanged).
- Produces: `YamlProfileFormat.written(document: dict[str, Any]) -> bytes`. When `document["parts"]` is a mapping, it is written as the canonical tree. Every other key is written as before.

- [ ] **Step 1: Write the failing writer tests**

Append to `tests/modules/spec/adapters/test_yaml_profile_format.py`. `import yaml` goes at the top with the other imports:

```python
def parts_written(parts: dict) -> str:
    """The text written for a document of only parts, without the `parts:` line."""
    return FORMAT.written({"parts": parts}).decode().split("parts:\n", 1)[1]


def test_a_chain_of_folders_that_are_no_part_is_written_as_one_joined_key():
    assert parts_written({"modules/": {"<module>/": {"domain/": {"role": "the rules"},
                                                     "adapters/": {"role": "the repos"}}}}) == (
        "  modules/<module>/:\n"
        "    domain/:\n      role: the rules\n"
        "    adapters/:\n      role: the repos\n")


def test_a_part_s_own_keys_come_first_in_the_fixed_order_then_its_folders_and_files():
    assert parts_written({"cli/": {"reports/": {"role": "r"}, "tests": "unit", "commands/": {}, "imports": {"may": ["x"]},
                                   "role": "c", "name": "cli"}}) == (
        "  cli/:\n    name: cli\n    role: c\n    imports:\n      may: [x]\n    tests: unit\n"
        "    reports/:\n      role: r\n    commands/: {}\n")


def test_a_part_folder_with_one_folder_inside_it_is_written_nested_never_joined():
    assert parts_written({"kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "l"}}}) == (
        "  kernel/:\n    role: k\n    logic/:\n      name: kernel-logic\n      role: l\n")


def test_a_joined_part_key_is_split_and_written_under_its_folder():
    assert parts_written({"kernel/": {"role": "k"}, "lib/logic/": {"role": "l"}}) == (
        "  kernel/:\n    role: k\n  lib/logic/:\n    role: l\n")
    assert parts_written({"a/": {"b/": {"role": "x"}, "c.py": {"role": "z"}}}) == (
        "  a/:\n    b/:\n      role: x\n    c.py:\n      role: z\n")


@pytest.mark.parametrize("value", [None, {}], ids=["null", "an empty map"])
def test_a_folder_with_neither_note_nor_children_is_written_as_an_empty_map(value):
    assert parts_written({"web/": {"role": "w", "ui/": value}}) == "  web/:\n    role: w\n    ui/: {}\n"


def test_a_note_is_written_as_the_folder_s_string():
    assert parts_written({"web/": {"role": "w", "routes/": "one file per route group"}}) == (
        "  web/:\n    role: w\n    routes/: one file per route group\n")


def test_a_lone_folder_holding_one_file_is_joined_with_it():
    assert parts_written({"bin/": {"run.py": {"role": "starts it"}}}) == "  bin/run.py:\n    role: starts it\n"


def test_the_rest_of_the_document_is_written_as_before():
    document = {"name": "x", "parts": {"core/": {"role": "r"}}, "layers": {"a": ["core"]}}
    assert yaml.safe_load(FORMAT.written(document)) == document
```

Then add to `tests/platform/test_yaml_writer.py`, after the existing tests:

```python
@pytest.mark.parametrize("key, text", [
    pytest.param("modules/<module>/", "modules/<module>/: 1\n", id="a joined folder with a repeating step"),
    pytest.param("domain/", "domain/: 1\n", id="a folder"),
    pytest.param("controller.py", "controller.py: 1\n", id="a file"),
    pytest.param("__main__.py", "__main__.py: 1\n", id="a file named with underscores"),
    pytest.param("[slug]/", '"[slug]/": 1\n', id="a folder YAML reads as a list is quoted"),
    pytest.param("@types/", '"@types/": 1\n', id="a folder starting with @ is quoted"),
    pytest.param("(group)/", '"(group)/": 1\n', id="a folder starting with a bracket is quoted"),
])
def test_a_key_of_the_folder_tree_is_plain_when_yaml_reads_it_back_as_written(key, text):
    written = YamlWriter().dump({key: 1})
    assert written == text
    assert yaml.safe_load(written) == {key: 1}
```

Add `import yaml` at the top of `tests/platform/test_yaml_writer.py`.

- [ ] **Step 2: Run them to verify the writer tests fail**

Run: `uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py tests/platform/test_yaml_writer.py -q`
Expected: the new tests in `test_yaml_profile_format.py` FAIL (e.g. `modules/:` written nested, `{}` vs `null`, order not fixed). `test_a_lone_folder…` fails. `test_the_rest_of_the_document_is_written_as_before` may pass. The `test_yaml_writer.py` parameters PASS already, which pins today's behavior.

- [ ] **Step 3: Implement the canonical tree in the adapter**

In `xarch/modules/spec/adapters/yaml_profile_format.py`, replace the module docstring's first sentence and `written`, and add the helpers at the end of the file:

Docstring (lines 1-4) becomes:

```python
"""A profile xarch writes, as a YAML file that reads as one written by hand, its `parts` as the folder tree in canonical
form (see _tree); and the checks of a profile written as the YAML of its `checks` (see written_checks for the format):
each check under its id, one slot to a line in the order a check is written, a slot left out when it says what the
format assumes, maps and lists of words on one line, and sentences quoted."""
```

Below `_INDENT` add:

```python
_PART_KEYS = ("name", "role", "litmus", "imports", "uses", "holds", "shared", "package_only", "tests", "untested")
"""The keys of a part in the order a profile writes them, before the folders and files below the part."""
```

`written` becomes:

```python
    def written(self, document: dict[str, Any]) -> bytes:
        parts = document.get("parts")
        shown = {**document, "parts": _tree(parts)} if isinstance(parts, Mapping) else document
        return self._writer.dump(shown).encode("utf-8")
```

At the end of the file:

```python
def _tree(parts: Mapping[str, Any]) -> dict[str, Any]:
    """The folder tree in canonical form: each key split into its steps and the tree built again, a part's own keys
    first in the order a profile writes them, then its folders and files in the order given; a folder that is no part,
    has no note and holds one entry joined with that entry; a folder holding nothing written {}."""
    return _joined(_nested(parts))


def _below(key: str) -> bool:
    """Whether a key of the tree is a folder (it ends in `/`) or a file (it holds a dot), not a key of a part."""
    return key.endswith("/") or "." in key


def _nested(node: Mapping[str, Any]) -> dict[str, Any]:
    """The node with its own keys in the order a profile writes them and each folder or file key one step to a
    level."""
    own = sorted((key for key in node if not _below(key)),
                 key=lambda key: _PART_KEYS.index(key) if key in _PART_KEYS else len(_PART_KEYS))
    nested: dict[str, Any] = {key: node[key] for key in own}
    for key, value in node.items():
        if _below(key):
            _put(nested, key, value)
    return nested


def _put(nested: dict[str, Any], key: str, value: Any) -> None:
    """The folder or file a key writes, put in nested one step to a level."""
    first, slash, rest = key.partition("/")
    if rest:
        held = nested.get(f"{first}/")
        if not isinstance(held, dict):
            held = nested[f"{first}/"] = {}
        _put(held, rest, value)
        return
    below = _nested(value) if isinstance(value, Mapping) else value
    step = f"{first}{slash}"
    held = nested.get(step)
    nested[step] = {**held, **below} if isinstance(held, dict) and isinstance(below, dict) else below


def _joined(nested: dict[str, Any]) -> dict[str, Any]:
    """The nested tree with each folder that is no part, has no note and holds one entry joined with that entry, and
    each folder holding nothing as {}."""
    joined: dict[str, Any] = {}
    for key, value in nested.items():
        if _below(key) and isinstance(value, Mapping):
            value = _joined(dict(value))
            if key.endswith("/") and len(value) == 1 and _below(next(iter(value))):
                ((step, value),) = value.items()
                key += step
        joined[key] = {} if value is None and key.endswith("/") else value
    return joined
```

`Mapping` is already imported from `collections.abc`.

- [ ] **Step 4: Run the writer tests to verify they pass**

Run: `uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py tests/platform/test_yaml_writer.py -q`
Expected: all PASS.

Run: `uv run ruff check xarch/modules/spec/adapters/yaml_profile_format.py tests/modules/spec/adapters/test_yaml_profile_format.py tests/platform/test_yaml_writer.py`
Expected: `All checks passed!`

Run: `timeout 900 uv run pytest -q -x tests/modules/spec tests/platform`
Expected: PASS (nothing else reads `written` with a flat `parts` and expects it flat). If a test that wrote a flat `parts` through `written` fails, its `parts` was not a tree: rewrite that fixture as a tree, as Task 5 does.

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/spec/adapters/yaml_profile_format.py tests/modules/spec/adapters/test_yaml_profile_format.py tests/platform/test_yaml_writer.py
git commit -m "The profile writer writes parts as the folder tree in canonical form: keys split into steps and rebuilt, a part's own keys first in the fixed order, single chains of plain folders joined, an empty folder as {}"
```

---

### Task 2: The key table, the format's texts and the walk of the tree

**Files:**
- Create: `xarch/modules/spec/application/logic/parts_tree.py`
- Create: `tests/modules/spec/application/logic/test_parts_tree.py`
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:83-87,751,758` (`_endings` → `endings`)
- Modify: `xarch/modules/spec/domain/key_table.py:80-91`
- Modify: `xarch/modules/spec/domain/profile_keys.py:189-228`
- Modify: `xarch/architectures/presets/format/keys.yaml`
- Modify: `tests/modules/spec/application/logic/test_profile_keys.py:33,168`
- Test: `tests/modules/spec/application/logic/test_key_catalogue.py` (runs as is)

**Interfaces:**
- Consumes: `ck.unknown_keys(spec, known, where, scope) -> list[str]`, `ck.text`, `ck.PART_NAME`, `names_of(PART)`, `required_of(PART)`, `EACH`, `Language`.
- Produces:
  - `profile_checks.endings(language: Language) -> str`, which is today's `_endings`, renamed.
  - `parts_tree(value: Any, language: Language) -> PartsTree`
  - `PartsTree(parts: tuple[TreePart, ...] = (), folders: tuple[TreeFolder, ...] = (), old: tuple[str, ...] = (), problems: tuple[str, ...] = ())`
  - `TreePart(name: str, steps: tuple[str, ...], words: tuple[str, ...], order: int, keys: Mapping[str, Any], shown: str, file: bool)`. `steps` has `EACH` for each repeating step, and `words` holds the words of those steps in order. `shown` is the path as written, with a trailing `/` for a folder.
  - `TreeFolder(steps: tuple[str, ...], note: str)`

- [ ] **Step 1: Write the failing key-table and catalogue tests**

In `tests/modules/spec/application/logic/test_profile_keys.py`, change line 33 to the tree:

```python
BASE = {"name": "example", "parts": {"documents/": {"role": "the documents"}}}
```

Add this test at the end of the file. `PART` is imported from `xarch.modules.spec.domain.profile_keys` and `required_of`/`names_of` from `xarch.modules.spec.application.logic.key_lookup`; add whichever import is missing:

```python
def test_a_part_is_named_by_its_place_or_by_name_and_holds_no_path_and_no_folders():
    assert names_of(PART) == {"holds", "imports", "litmus", "name", "package_only", "role", "shared", "tests",
                              "untested", "uses"}
    assert required_of(PART) == ("role",)
    assert [key.name for key in KEYS if key.scope == PART][0] == "name"
```

(`KEYS` from `xarch.modules.spec.domain.key_table`. If `required_of` returns a list, compare with `["role"]`.)

Line 168 (`load(yaml.safe_load(CATALOGUE.smallest)).parts["documents"].path`) stays. It passes again once `smallest` is a tree.

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_keys.py -q -k "named_by_its_place"`
Expected: FAIL, `path`/`folders` in the set and `name` missing.

- [ ] **Step 3: Change the key table, the retired names and the catalogue**

`xarch/modules/spec/domain/key_table.py`, the `PART` block (lines 80-91) becomes:

```python
    Key(PART, "name", rules=("structure",)),
    Key(PART, "role", True, False),
    Key(PART, "litmus", False, False),
    Key(PART, "imports", rules=("may-import", "must-import", "libraries"), opens=PART_IMPORTS),
    Key(PART, "holds", rules=("holds",), opens=PART_HOLDS, when_supplied=("function.top_level",),
        without="holds reads no top-level functions"),
    Key(PART, "shared", rules=("shared",)),
    Key(PART, "uses", opens=PART_USES),
    Key(PART, "tests", rules=("tiers",)),
    Key(PART, "untested"),
    Key(PART, "package_only", rules=("package-only",)),
```

`xarch/modules/spec/domain/profile_keys.py`, in `RETIRED`, after `Retired(PART, "forbidden", …)`:

```python
    Retired(PART, "path", "moved in 0.3.0: a part is the folder or file it is written as under parts: drop it"),
    Retired(PART, "folders", "moved in 0.3.0: write each folder below the part as a key ending in /, with its note as "
                             "its value"),
```

`xarch/architectures/presets/format/keys.yaml`:

1. `fragments.part` and `fragments.two`:

```yaml
  part: |
    parts:
      documents/:
        role: the documents
  two: |
    parts:
      core/:
        role: the rules of the documents
      documents/:
        role: the documents
        imports:
          may: [core]
```

2. The fragment at lines 55-63 (the `units/<unit>/` parts):

```yaml
    parts:
      units/<unit>/:
        documents/:
          role: the documents
          tests: integration
        results/:
          role: the result unions
          tests: integration
```

3. `smallest`:

```yaml
smallest: |
  name: documents-app
  parts:
    documents/:
      role: the documents
```

4. `symbols`. Replace the `"<word>"` line and the last line, and add one before `<word>`:

```yaml
  "<folder>/": "under parts, a key ending in /: a folder, holding the folders, files and keys of what lies in it"
  "<word>/": "under parts, a folder key written <word>/: a repeating folder, one per name, as in units/<unit>/; there may be several"
```
and
```yaml
  "<file>%extension%": "under parts, a key holding a dot: a file, always a part"
```
(This drops `a path ending in %extension%`. Keep the `store`, `store@any`, `store/schema`, `store:*Id` and `everything` lines.)

5. `keys.parts`:

```yaml
  parts:
    meaning: the folder tree of the app, and its parts
    accepts: >-
      the folder tree below the app: a key ending in `/` is a folder of one or more steps (`modules/<module>/`), a key
      holding a dot is a file, and any other key is a key of the part the folder or file is. A folder with a `role` is
      a part, one with another key of a part and no `role` is refused, and one with neither is only a folder, whose
      value may be one line of text, its note; a file is always a part. A part is named by its folder's last step or
      its file's name before the first dot, or by `name:`; two parts of one name are refused. A part may lie inside
      another, and a file belongs to the deepest part around it. The parts' reading order, top to bottom and a part
      before the parts inside it, is the order their litmus tests run
    example: |
      <<two>>
```

6. Delete `parts.<part>.path` (lines 307-316) and `parts.<part>.folders` (lines 545-551). Add before `parts.<part>.role`:

```yaml
  parts.<part>.name:
    meaning: the part's name, when its folder or file does not give it
    accepts: >-
      a name of letters, digits, `_` and `-`: the part is called this instead of its folder's last step or its file's
      name before the first dot; needed when two parts would take one name, and every other key names the part by it
    example: |
      parts:
        kernel/:
          role: the bases every module shares
          logic/:
            name: kernel-logic
            role: the pure rules every module shares
```

7. Rewrite every other example that writes `path:` (keys.yaml lines ~360-368, ~748-756, ~1249-1256). Each `<name>:\n  path: <name>` becomes `<name>/:`, with the remaining keys kept at the same indent. For example, lines 360-368 become:

```yaml
    example: |
      parts:
        core/:
          role: the rules of the documents
        documents/:
          role: the documents
          imports:
            may: [{core: types_only}]
```

Then run `grep -n "path:" xarch/architectures/presets/format/keys.yaml` and account for every remaining hit. Only keys that are not part paths may remain (none are expected).

- [ ] **Step 4: Write the failing walk tests**

Create `tests/modules/spec/application/logic/test_parts_tree.py`:

```python
"""The folder tree under `parts`, walked once: a key ending in `/` is a folder, a key holding a dot a file, any other
key a key of the part; the parts in reading order, each with its own keys, the folders that are no part with their
notes, and the problems of the tree, each addressed by part name; a profile of the parts of 0.2.0 refused alone."""
import pytest

from tests.modules.spec.languages import PYTHON
from xarch.kernel.placement import EACH
from xarch.modules.spec.application.logic.parts_tree import PartsTree, TreeFolder, TreePart, parts_tree
from xarch.modules.spec.domain.values import Language

KNOWN = "holds, imports, litmus, name, package_only, role, shared, tests, untested, uses"


def walked(value):
    return parts_tree(value, PYTHON)


def test_a_folder_with_a_role_is_a_part_named_by_its_last_step_and_a_joined_key_is_its_steps():
    tree = walked({"modules/<module>/": {"domain/": {"role": "the rules", "tests": "unit"}}})
    assert tree == PartsTree(
        (TreePart("domain", ("modules", EACH, "domain"), ("module",), 0, {"role": "the rules", "tests": "unit"},
                  "modules/<module>/domain/", False),),
        (TreeFolder(("modules", EACH), ""),))


def test_the_parts_come_in_reading_order_a_part_before_the_parts_inside_it():
    tree = walked({"kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "kl"}},
                   "platform/": {"role": "p"}})
    assert [(part.name, part.order, part.shown) for part in tree.parts] == [
        ("kernel", 0, "kernel/"), ("kernel-logic", 1, "kernel/logic/"), ("platform", 2, "platform/")]
    assert tree.parts[0].keys == {"role": "k"} and tree.parts[1].keys == {"name": "kernel-logic", "role": "kl"}


def test_a_file_is_named_before_its_first_dot_and_name_replaces_any_name():
    tree = walked({"__main__.py": {"role": "starts"}, "cli/": {"main.tool.py": {"name": "tool", "role": "t"}}})
    assert [(part.name, part.steps, part.file) for part in tree.parts] == [
        ("__main__", ("__main__.py",), True), ("tool", ("cli", "main.tool.py"), True)]
    assert tree.folders == (TreeFolder(("cli",), ""),)


def test_a_folder_that_is_no_part_is_a_folder_with_its_note_or_none():
    tree = walked({"web/": {"role": "w", "routes/": "one file per route group", "ui/": None, "i18n/": {}}})
    assert tree.folders == (TreeFolder(("web", "routes"), "one file per route group"), TreeFolder(("web", "ui"), ""),
                            TreeFolder(("web", "i18n"), ""))
    assert [part.name for part in tree.parts] == ["web"]


def test_two_repeating_steps_on_the_way_to_a_part_are_kept_for_the_parser_to_refuse():
    assert walked({"<a>/": {"<b>/": {"c/": {"role": "r"}}}}).parts[0].words == ("a", "b")


@pytest.mark.parametrize("value, expected", [
    pytest.param(3, "parts: must be the folder tree of the app: folders ending in /, files with their extension",
                 id="1 parts not a map"),
    pytest.param({"rol": "x"}, "parts: unknown key 'rol': a key under parts is a folder ending in / or a file ending "
                 "in .py", id="2 a typo directly under parts"),
    pytest.param({"core/": {"litmus": "q"}}, "parts.core: missing `role`", id="3 a folder with a part key, no role"),
    pytest.param({"main.py": "x"}, "parts.main: a file is a part: write it as a map with role", id="4 a file no map"),
    pytest.param({"main.py": {}}, "parts.main: missing `role`", id="5 a file with no role"),
    pytest.param({"notes.txt": {"role": "r"}}, "parts.notes: 'notes.txt' is a file, since its key holds a dot, but it "
                 "does not end in .py: write a folder as notes.txt/", id="6 a file of another extension"),
    pytest.param({"application/": {"logic/": {"role": "a"}}, "kernel/": {"logic/": {"role": "b"}}},
                 "parts.logic: 'application/logic/' and 'kernel/logic/' are both named logic: write name: <part name> "
                 "on one of them", id="7 two parts of one name, no name invented"),
    pytest.param({"kernel/": {"role": "k"}, "kernel/logic/": {"role": "l"}},
                 "parts: the folder 'kernel/' is written twice, in 'kernel/' and 'kernel/logic/': write it once and "
                 "nest what lies in it", id="8 a part folder beside a key below it"),
    pytest.param({"modules/<module>/domain/": {"role": "d"}, "modules/<module>/adapters/": {"role": "a"}},
                 "parts: the folder 'modules/<module>/' is written twice, in 'modules/<module>/domain/' and "
                 "'modules/<module>/adapters/': write it once and nest what lies in it", id="8 a joined folder twice"),
    pytest.param({"core/": {"role": "r", "rol": "x"}}, f"parts.core: unknown key 'rol': use {KNOWN}",
                 id="9 a typo inside a folder is never a folder"),
    pytest.param({"core/": {"role": "r", "path": "core"}}, "parts.core: unknown key 'path': moved in 0.3.0: a part "
                 f"is the folder or file it is written as under parts: drop it; use {KNOWN}", id="10 path in a node"),
    pytest.param({"core/": {"role": "r", "folders": {"a": "n"}}}, "parts.core: unknown key 'folders': moved in "
                 "0.3.0: write each folder below the part as a key ending in /, with its note as its value; use "
                 f"{KNOWN}", id="11 folders in a node"),
    pytest.param({"src/<module>/": {"role": "r"}}, "parts: 'src/<module>/' is named '<module>', which is not a part "
                 "name: write name: with letters, digits, '_' and '-'", id="12 a name from the folder"),
    pytest.param({"core/": {"name": "a b", "role": "r"}}, "parts: 'core/' is named 'a b', which is not a part name: "
                 "write name: with letters, digits, '_' and '-'", id="12 a name from name"),
    pytest.param({"docs/": "two\nlines"}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a note of two lines"),
    pytest.param({"docs/": ["a"]}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a list"),
    pytest.param({"docs/": 3}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a number"),
    pytest.param({"main.py": {"role": "r", "x/": {}}}, "parts.main: 'main.py' is a file and holds nothing below it",
                 id="14 a folder below a file"),
    pytest.param({"a//b/": {"role": "r"}}, "parts: 'a//b/' has an empty, `.` or `..` step", id="15 an empty step"),
    pytest.param({"a/../b/": {"role": "r"}}, "parts: 'a/../b/' has an empty, `.` or `..` step", id="15 climbing"),
    pytest.param({"a/*/b/": {"role": "r"}}, "parts: 'a/*/b/' has a `*` step: write the repeating folder as one word "
                 "between `<` and `>`", id="15 a star step"),
    pytest.param({"a/<mo dule>/b/": {"role": "r"}}, "parts: 'a/<mo dule>/b/' has a step with `<` or `>` that is not "
                 "one word between them: write the repeating folder as `<name>`", id="15 a bracket that is no word"),
    pytest.param({"modules/<module>/": {}}, "parts: 'modules/<module>/' is a repeating folder with no part below it: "
                 "write a part in it, or drop it", id="17 a repeating folder with no part"),
])
def test_each_refusal_of_the_tree_says_where_and_what_to_write(value, expected):
    assert walked(value).problems == (expected,)


def test_a_typo_alone_in_a_folder_leaves_it_a_folder_and_no_part():
    tree = walked({"core/": {"rol": "x"}})
    assert (tree.parts, tree.folders, tree.problems) == ((), (TreeFolder(("core",), ""),),
                                                         (f"parts.core: unknown key 'rol': use {KNOWN}",))


def test_a_file_of_another_extension_is_checked_only_when_the_language_lists_any():
    assert parts_tree({"notes.txt": {"role": "r"}}, Language()).problems == ()


def test_a_refused_part_still_counts_as_a_part_below_its_repeating_folder():
    assert walked({"src/<module>/": {"core/": {"name": "a b", "role": "r"}}}).problems == (
        "parts: 'src/<module>/core/' is named 'a b', which is not a part name: write name: with letters, digits, "
        "'_' and '-'",)


def test_several_problems_of_one_tree_are_all_listed():
    assert walked({"rol": 1, "core/": {"rol": 2}, "main.py": "x"}).problems == (
        "parts: unknown key 'rol': a key under parts is a folder ending in / or a file ending in .py",
        f"parts.core: unknown key 'rol': use {KNOWN}",
        "parts.main: a file is a part: write it as a map with role")


def test_an_old_flat_part_is_refused_alone_with_where_to_write_it():
    tree = walked({"domain": {"path": "modules/<module>/domain", "role": "r"}, "core/": {"rol": 1},
                   "kernel-logic": {"path": "kernel/logic", "role": "r"}, "main": {"path": "__main__.py", "role": "r"},
                   "x": {"path": 3, "role": "r"}})
    assert (tree.parts, tree.folders, tree.problems) == ((), (), ())
    assert tree.old == (
        "parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the folder it "
        f"lies in (modules/<module>/); use {KNOWN}",
        "parts.kernel-logic: unknown key 'path': moved in 0.3.0: write the part as the folder logic/: with name: "
        f"kernel-logic, under the folder it lies in (kernel/); use {KNOWN}",
        "parts.main: unknown key 'path': moved in 0.3.0: write the part as the file __main__.py: with name: main, at "
        f"the top of parts; use {KNOWN}",
        f"parts.x: unknown key 'path': moved in 0.3.0: write the part as a folder ending in /; use {KNOWN}")
```

- [ ] **Step 5: Run to verify the walk tests fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_parts_tree.py -q`
Expected: collection ERROR, `ModuleNotFoundError: No module named 'xarch.modules.spec.application.logic.parts_tree'`.

- [ ] **Step 6: Make `endings` public and write the walk**

In `xarch/modules/spec/application/logic/profile_checks.py`, rename `def _endings(` to `def endings(` (line 83) and its two calls at lines 751 and 758 from `_endings(language)` to `endings(language)`. Run `grep -rn "_endings" xarch tests` and expect no hit.

Create `xarch/modules/spec/application/logic/parts_tree.py`:

```python
"""The folder tree a profile writes under `parts`, walked once, depth first, in the order the file writes its keys: a
key ending in `/` is a folder of one or more steps, a key holding a dot is a file, and any other key is a key of the
part the folder or file is. A folder holding a key of a part is a part, and a file always is; a part is named by
`name:`, else by its folder's last step or its file's name before the first dot, and two parts of one name are refused,
never renamed. The walk yields the parts in reading order, a part before the parts inside it, each with its own keys;
the folders that are no part, each with its note; the problems of the tree, each addressed by part name where the
place is a part; and, for a profile whose parts write their `path` as before 0.3.0, only a refusal for each such part,
so that nothing is read from parts that were never written as a tree."""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from xarch.kernel.placement import EACH
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of
from xarch.modules.spec.domain.profile_keys import PART
from xarch.modules.spec.domain.values import Language

_REPEATING = re.compile(r"<([A-Za-z_][A-Za-z0-9_-]*)>")
_TREE = "parts: must be the folder tree of the app: folders ending in /, files with their extension"


@dataclass(frozen=True)
class TreePart:
    """A part of the tree: its name, its steps from the app (EACH for a repeating step) and the words of its repeating
    steps, its place in the reading order from 0, its own keys, its path as written (a folder's ending in /), and
    whether it is a file."""
    name: str
    steps: tuple[str, ...]
    words: tuple[str, ...]
    order: int
    keys: Mapping[str, Any]
    shown: str
    file: bool


@dataclass(frozen=True)
class TreeFolder:
    """A folder of the tree that is no part: its steps from the app (EACH for a repeating step) and its note, "" for
    none."""
    steps: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class PartsTree:
    """What the tree holds: its parts in reading order, its folders that are no part, the refusals of the parts
    written as before 0.3.0 (when there is one, nothing else is read), and its problems."""
    parts: tuple[TreePart, ...] = ()
    folders: tuple[TreeFolder, ...] = ()
    old: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Found:
    """What the walk has found so far: the parts, the folders that are no part, the problems, the path each name was
    first given at, the path of every node read as a part, refused or not, and the language."""
    parts: list[TreePart]
    folders: list[TreeFolder]
    problems: list[str]
    named: dict[str, str]
    met: list[str]
    language: Language


def parts_tree(value: Any, language: Language) -> PartsTree:
    """The tree a profile writes under `parts`; language gives the endings a file key must have, none checked when it
    lists none."""
    if not isinstance(value, Mapping):
        return PartsTree(problems=(_TREE,))
    old = tuple(_old(str(key), spec) for key, spec in value.items() if _own(key) and _holds_path(spec))
    if old:
        return PartsTree(old=old)
    found = _Found([], [], [], {}, [], language)
    _walk(value, (), found)
    return PartsTree(tuple(found.parts), tuple(found.folders), (), tuple(found.problems))


def _own(key: Any) -> bool:
    """Whether a key of the tree is a key of a part: it ends in no `/` and holds no dot."""
    return not isinstance(key, str) or (not key.endswith("/") and "." not in key)


def _holds_path(spec: Any) -> bool:
    return isinstance(spec, Mapping) and "path" in spec


def _known() -> str:
    return ", ".join(sorted(names_of(PART)))


def _old(key: str, spec: Mapping[Any, Any]) -> str:
    """The refusal of a part written as before 0.3.0, saying the folder or file to write it as and where."""
    path = spec["path"]
    steps = path.strip("/").split("/") if ck.text(path) else []
    if not steps or "" in steps:
        what = "a folder ending in /"
    else:
        *parent, last = steps
        given = last.split(".")[0] if "." in last else last
        shown = f"the file {last}" if "." in last else f"the folder {last}/"
        named = f"with name: {key}, " if key != given else ""
        where = f"under the folder it lies in ({'/'.join(parent)}/)" if parent else "at the top of parts"
        what = f"{shown}: {named}{where}"
    return f"parts.{key}: unknown key 'path': moved in 0.3.0: write the part as {what}; use {_known()}"


def _walk(node: Mapping[Any, Any], at: tuple[str, ...], found: _Found) -> None:
    """The folders and files a node holds, in the order written, below the folder whose steps as written are at."""
    firsts: dict[str, tuple[str, tuple[str, ...]]] = {}
    for key, value in node.items():
        if _own(key):
            if not at:
                found.problems.append(f"parts: unknown key {str(key)!r}: a key under parts is a folder ending in / or "
                                      f"a file ending in {ck.endings(found.language)}")
            continue
        steps = _steps(key, found.problems)
        if steps is None:
            continue
        if steps[0] in firsts:
            prior, written = firsts[steps[0]]
            common = _common(written, steps)
            found.problems.append(f"parts: the folder '{'/'.join(at + common)}/' is written twice, in '{prior}' and "
                                  f"'{key}': write it once and nest what lies in it")
            continue
        firsts[steps[0]] = (key, steps)
        met = len(found.met)
        if key.endswith("/"):
            _folder(at + steps, value, found)
        else:
            _file(at + steps, key, value, found)
        repeat = next((i for i, step in enumerate(steps) if _REPEATING.fullmatch(step)), None)
        if repeat is not None and len(found.met) == met:
            found.problems.append(f"parts: '{'/'.join(at + steps[:repeat + 1])}/' is a repeating folder with no part "
                                  "below it: write a part in it, or drop it")


def _steps(key: str, problems: list[str]) -> tuple[str, ...] | None:
    """The steps a folder or file key writes, `<word>` as written; None, said, when one of them is no step."""
    steps = tuple((key[:-1] if key.endswith("/") else key).split("/"))
    if any(step in ("", ".", "..") or "\\" in step for step in steps):
        problems.append(f"parts: '{key}' has an empty, `.` or `..` step")
    elif any(EACH in step for step in steps):
        problems.append(f"parts: '{key}' has a `*` step: write the repeating folder as one word between `<` and `>`")
    elif any(("<" in step or ">" in step) and not _REPEATING.fullmatch(step) for step in steps):
        problems.append(f"parts: '{key}' has a step with `<` or `>` that is not one word between them: write the "
                        "repeating folder as `<name>`")
    else:
        return steps
    return None


def _common(first: tuple[str, ...], second: tuple[str, ...]) -> tuple[str, ...]:
    """The steps two keys of one map both start with."""
    common: list[str] = []
    for one, other in zip(first, second, strict=False):
        if one != other:
            break
        common.append(one)
    return tuple(common)


def _folder(path: tuple[str, ...], value: Any, found: _Found) -> None:
    """A folder: a part when it holds a key of a part, else a folder with its note; then what lies in it."""
    if isinstance(value, Mapping):
        own = {key: item for key, item in value.items() if _own(key)}
        if not _part(path, f"{'/'.join(path)}/", False, own, found):
            found.folders.append(TreeFolder(_placed(path), ""))
        _walk(value, path, found)
    elif value is None or (isinstance(value, str) and "\n" not in value):
        found.folders.append(TreeFolder(_placed(path), value or ""))
    else:
        found.problems.append(f"parts: '{'/'.join(path)}/': a folder is a map, one line of text (its note), or "
                              "nothing")


def _file(path: tuple[str, ...], key: str, value: Any, found: _Found) -> None:
    """A file: always a part, a map with role, ending in one of the language's endings, holding nothing below it."""
    shown, stem = "/".join(path), path[-1].split(".")[0]
    if not isinstance(value, Mapping):
        found.met.append(shown)
        found.problems.append(f"parts.{stem}: a file is a part: write it as a map with role")
        return
    own = {name: item for name, item in value.items() if _own(name)}
    name = own.get("name", stem)
    if len(own) < len(value):
        found.problems.append(f"parts.{name}: '{shown}' is a file and holds nothing below it")
    extensions = tuple(found.language.checked.extensions)
    if extensions and not path[-1].endswith(extensions):
        found.met.append(shown)
        found.problems.append(f"parts.{name}: '{shown}' is a file, since its key holds a dot, but it does not end in "
                              f"{ck.endings(found.language)}: write a folder as {key}/")
        return
    _part(path, shown, True, own, found)


def _part(path: tuple[str, ...], shown: str, file: bool, own: Mapping[Any, Any], found: _Found) -> bool:
    """Whether the folder or file at path is a part (a file always is, a folder when it holds a key of a part), with
    the problems of its own keys and its name; a part of a good name not yet given is found."""
    known = names_of(PART)
    given = path[-1].split(".")[0] if file else path[-1]
    name = own.get("name", given)
    where = f"parts.{name}"
    if not file and not any(key in known for key in own):
        found.problems.extend(ck.unknown_keys(own, known, where, PART))
        return False
    found.met.append(shown)
    if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
        found.problems.append(f"parts: '{shown}' is named '{name}', which is not a part name: write name: with "
                              "letters, digits, '_' and '-'")
        return True
    found.problems.extend(ck.unknown_keys(own, known, where, PART))
    found.problems.extend(f"{where}: missing `{key}`" for key in required_of(PART) if key not in own)
    if name in found.named:
        found.problems.append(f"{where}: '{found.named[name]}' and '{shown}' are both named {name}: write name: "
                              "<part name> on one of them")
        return True
    found.named[name] = shown
    words = tuple(match.group(1) for match in map(_REPEATING.fullmatch, path) if match)
    found.parts.append(TreePart(name, _placed(path), words, len(found.parts), dict(own), shown, file))
    return True


def _placed(path: tuple[str, ...]) -> tuple[str, ...]:
    """The steps as the layout holds them: a repeating step as EACH."""
    return tuple(EACH if _REPEATING.fullmatch(step) else step for step in path)
```

Notes for the implementer:
- `language.checked.extensions` is the field `profile_checks.endings` already reads. If it is a list, the `tuple(...)` makes `str.endswith` accept it.
- When a test's expected text differs from what you get only in a quote or a word, the test is the source of truth, because the texts are the spec's (B3/B4). Change the code, not the test.

- [ ] **Step 7: Run the walk, catalogue and key tests**

Run: `uv run pytest tests/modules/spec/application/logic/test_parts_tree.py tests/modules/spec/application/logic/test_key_catalogue.py -q`
Expected: PASS.

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_keys.py -q`
Expected: `test_a_part_is_named_by_its_place_or_by_name_and_holds_no_path_and_no_folders` PASSES. Tests that load examples through `parse_profile` still FAIL, because the parser reads trees only after Task 3. Record which ones fail, so you can confirm they pass after Task 3.

Run: `uv run ruff check xarch/modules/spec tests/modules/spec/application/logic/test_parts_tree.py`
Expected: `All checks passed!`

- [ ] **Step 8: Commit**

```bash
git add xarch/modules/spec/application/logic/parts_tree.py xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/domain/key_table.py xarch/modules/spec/domain/profile_keys.py xarch/architectures/presets/format/keys.yaml tests/modules/spec/application/logic/test_parts_tree.py tests/modules/spec/application/logic/test_profile_keys.py
git commit -m "A part is named by its folder or file under parts, or by name; path and folders are retired with what to write; parts_tree walks the folder tree once, in reading order, and says each refusal of the tree by part name"
```

---

### Task 3: The parser, the needs walk and the packages read the tree

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (docstring 17-36; `parse_profile` 173-240; `_specs` 282-293 removed; `_layout` 296-335; `_path`, `_shown`, `_folders` removed; `_repeats_alike`, `_insert`, `_add_folder` reworded; `_named_packages` 480-494; imports)
- Modify: `xarch/modules/spec/application/logic/profile_needs.py:79-88`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:215`
- Modify: `tests/modules/spec/profiles.py` (`layered`, `two_folders`, `covered`, new `part_of`)
- Modify: `tests/modules/spec/application/logic/test_profile_parsing.py`
- Modify: `tests/modules/spec/application/logic/test_retired_keys.py`
- Modify: `tests/modules/spec/application/logic/test_profile_needs.py`
- Modify: `tests/modules/spec/application/logic/test_docs_template.py`

**Interfaces:**
- Consumes: `parts_tree(value, language) -> PartsTree` (Task 2).
- Produces: `parse_profile` (same signature). `Architecture.parts` is in reading order, and `placement == tuple(parts)`. `tests.modules.spec.profiles.part_of(document: dict, name: str) -> dict` returns the map of a named part in a tree document, for tests only.

- [ ] **Step 1: Rewrite the spec test builders as trees**

In `tests/modules/spec/profiles.py`, `layered`, `two_folders` and `covered` become:

```python
def layered(**changes) -> dict:
    """A profile with no tiers and no tests; the keys given are added or replaced."""
    return {
        "name": "layered",
        "parts": {
            "src/<module>/": {
                "api/": {"role": "HTTP handlers", "imports": {"may": ["service"]}},
                "service/": {"role": "business logic", "imports": {"may": ["store", "shared"]}},
                "store/": {"role": "database access", "imports": {"may": ["shared"], "libraries": ["sqlmodel"]}},
            },
            "shared/": {"role": "shared code"},
        },
    } | changes


def two_folders(**changes) -> dict:
    """layered(), with a second repeating folder, ext/<plugin>/, holding a hooks folder and a manifest.py file."""
    document = layered()
    document["parts"]["ext/<plugin>/"] = {"hooks/": {"role": "what a plugin runs"},
                                          "manifest.py": {"role": "what a plugin declares",
                                                          "imports": {"may": ["hooks"]}}}
    return document | changes


def covered(**changes) -> dict:
    """layered(), with the test framework, a unit and an integration tier, and every part in a tier or untested."""
    document = layered(testing=deepcopy(TESTING),
                       tiers={"unit": {"proves": "a rule", "litmus": "Does it decide?\nIf yes, it is a unit test.\n"},
                              "integration": {"proves": "a request", "litmus": "Does it need the database?"}})
    for name, tier in (("api", "integration"), ("service", "unit"), ("store", "integration")):
        part_of(document, name)["tests"] = tier
    part_of(document, "shared")["untested"] = "reached through the parts that use it"
    return document | changes


def part_of(document: dict, name: str) -> dict:
    """The map of the part named name in the document's folder tree: the folder or file whose `name` is name, else
    whose last step, or whose file name before the first dot, is."""
    found = _part_in(document["parts"], name)
    assert found is not None, f"no part {name!r} in the tree"
    return found


def _part_in(node: dict, name: str) -> dict | None:
    for key, value in node.items():
        if not isinstance(key, str) or not (key.endswith("/") or "." in key) or not isinstance(value, dict):
            continue
        last = key.rstrip("/").split("/")[-1]
        given = last if key.endswith("/") else last.split(".")[0]
        if value.get("name", given) == name and any(not (k.endswith("/") or "." in k) for k in value):
            return value
        deeper = _part_in(value, name)
        if deeper is not None:
            return deeper
    return None
```

- [ ] **Step 2: Write the failing parser tests**

In `tests/modules/spec/application/logic/test_profile_parsing.py`:

(a) Delete these tests, whose behavior is gone: `test_a_bad_folders_entry_is_refused` (with its parametrize), `test_a_part_that_is_a_file_has_no_folders`, `test_a_folder_that_is_a_part_is_refused_since_its_note_is_its_role`, `test_a_bad_part_path_is_refused` (with its parametrize), `test_a_bad_part_is_refused_with_every_problem` (with its parametrize), `test_a_file_cannot_hold_a_part_below_it` and `test_a_folder_that_holds_a_part_cannot_also_be_a_file`. The walk tests of Task 2 now cover them.

(b) Rewrite `test_the_smallest_profile_…` so its document is `{"name": "tiny", "parts": {"core/": {"role": "the rules"}, "cli/": {"role": "commands and output", "imports": {"may": ["core"], "libraries": ["typer"]}}}}`.

(c) In `test_every_unknown_key_message_reads_the_table_of_keys`, the third assert's document becomes `layered(parts={"x/": {"role": "r", "colour": 1}})`.

(d) Replace `test_the_order_of_the_parts_is_the_placement_order`, `test_a_last_step_with_a_dot_is_a_file_…`, `test_a_top_level_file_is_a_file`, `test_the_folders_of_a_part_are_in_the_layout_…`, `test_two_words_may_not_share_a_parent`, `test_one_word_repeats_in_one_folder_only` and `test_a_profile_may_hold_several_repeating_folders_…` with the following. Read each old test first: keep any assert in it that is not listed below, written for the tree.

```python
def test_a_nested_tree_and_the_same_tree_joined_parse_to_one_architecture():
    nested = layered(parts={"src/": {"<module>/": {"api/": {"role": "HTTP handlers", "imports": {"may": ["service"]}},
                                                   "service/": {"role": "business logic",
                                                                "imports": {"may": ["store", "shared"]}},
                                                   "store/": {"role": "database access",
                                                              "imports": {"may": ["shared"],
                                                                          "libraries": ["sqlmodel"]}}}},
                            "shared/": {"role": "shared code"}})
    one, other = parsed(layered()), parsed(nested)
    assert (one.parts, one.layout, one.notes, one.repeats, one.placement) == (
        other.parts, other.layout, other.notes, other.repeats, other.placement)


def test_the_reading_order_of_the_tree_is_the_placement_order_a_part_before_the_parts_inside_it():
    architecture = parsed(layered(parts={
        "src/<module>/": {"contract/": {"role": "c"}, "api/": {"role": "a"}},
        "platform/": {"role": "p"},
        "kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "kl"}}}))
    assert architecture.placement == ("contract", "api", "platform", "kernel", "kernel-logic")
    assert architecture.placement == tuple(architecture.parts)
    assert architecture.parts["kernel-logic"].path == ("kernel", "logic")


def test_a_file_part_is_a_file_of_the_layout_and_a_part_may_sit_inside_another():
    document = layered()
    document["parts"]["src/<module>/"]["entry.py"] = {"role": "the entry"}
    part_of(document, "store")["sql/"] = {"role": "queries"}
    document["parts"]["__main__.py"] = {"name": "main", "role": "starts the app"}
    architecture = parsed(document)
    assert architecture.layout["src"]["*"]["entry.py"] is None and architecture.layout["__main__.py"] is None
    assert architecture.parts["sql"].path == ("src", "*", "store", "sql")
    assert architecture.parts["main"].path == ("__main__.py",)
    assert is_file(architecture.layout, architecture.parts["entry"].path)


def test_a_folder_with_a_note_or_with_nothing_is_a_folder_of_the_layout_and_its_note_a_note():
    document = layered()
    part_of(document, "shared")["text/"] = "text helpers"
    part_of(document, "shared")["io/"] = None
    part_of(document, "shared")["disk/"] = {}
    architecture = parsed(document)
    assert architecture.layout["shared"] == {"text": {}, "io": {}, "disk": {}}
    assert architecture.notes == {("shared", "text"): "text helpers"}


def test_a_part_s_own_folders_follow_the_parts_in_the_layout_as_today():
    architecture = parsed(layered(parts={"cli/": {"role": "c", "commands/": {}, "reports/": {"role": "r"}}}))
    assert list(architecture.layout["cli"]) == ["reports", "commands"]


def test_two_repeating_steps_on_the_way_to_a_part_are_refused():
    assert problems(layered(parts={"<a>/": {"<b>/": {"c/": {"role": "r"}}}})) == [
        "layered.yaml: parts.c: '<a>/<b>/c/' has two repeating steps, <a> and <b>: a repeating folder cannot sit "
        "inside another, so give each its own folder"]


def test_two_words_may_not_share_a_parent():
    document = layered(parts={"src/": {"<module>/": {"api/": {"role": "a"}}, "<doc>/": {"x/": {"role": "r"}}}})
    assert problems(document) == [
        "layered.yaml: parts.x: 'src/<doc>/x/' calls the repeating folder <doc>, but part 'api' called it <module> in "
        "the same folder 'src': two words may not share a parent, use one word"]


def test_one_word_repeats_in_one_folder_only():
    document = layered()
    document["parts"]["other/<module>/"] = {"y/": {"role": "r"}}
    assert problems(document) == [
        "layered.yaml: parts.y: 'other/<module>/y/' repeats <module> below 'other', but part 'api' repeats it below "
        "'src': one word repeats in one folder, so give this one a word of its own"]


def test_a_profile_may_hold_several_repeating_folders_each_with_its_word_and_parent():
    architecture = parsed(two_folders())
    assert architecture.repeats == (Repeat("module", ("src",)), Repeat("plugin", ("ext",)))
    assert architecture.parts["manifest"].path == ("ext", "*", "manifest.py")
```

In the `<doc>` case, `<module>/` and `<doc>/` sit in one written `src/`, because two keys `src/<module>/` and `src/<doc>/` would share `src` and be refused by row 8 first. Check the old texts against today's `_repeats_alike` in `profile_parsing.py:377-384`: only the address changes, from `{where}.path: '{value}'` to `parts.<name>: '<shown>'`.

Import `part_of` from `tests.modules.spec.profiles` at the top of the file.

(e) Every other `document["parts"]["<name>"]` in this file that reads or changes an existing part becomes `part_of(document, "<name>")`. Every line that adds a part with `{"path": …}` becomes a key in the tree at that path, as in (d). Every `parts={...}` with `path` becomes a tree. Then run `grep -nE "\"path\"|folders" tests/modules/spec/application/logic/test_profile_parsing.py` and account for each hit: none may remain except `Part.path` attribute reads.

In `tests/modules/spec/application/logic/test_retired_keys.py`:

```python
PART_USE = "holds, imports, litmus, name, package_only, role, shared, tests, untested, uses"
```

Line 248's `unknown_keys({"path": "a", "banned": 1, "colour": 2}, …)` now gets `path`'s retired text as its own first problem. Rewrite its expected list to put `f"parts.api: unknown key 'path': moved in 0.3.0: a part is the folder or file it is written as under parts: drop it; use {PART_USE}"` first, then today's others. Line 351's `{"role": "x", "path": "a"}` becomes `{"role": "x", "name": "a"}`. Line 371-372 becomes:

```python
    document["parts"]["src/<module>/"]["api/"] = ["x"]
    assert problems(document) == ["layered.yaml: parts: 'src/<module>/api/': a folder is a map, one line of text (its "
                                  "note), or nothing"]
```

Every other `document["parts"]["x"]` in the file becomes `part_of(document, "x")`. Then add:

```python
KNOWN = PART_USE


def test_path_and_folders_inside_a_node_say_how_the_tree_writes_them_and_nothing_else_of_the_node():
    document = layered()
    part_of(document, "shared")["path"] = "shared"
    part_of(document, "api")["folders"] = {"a": "n"}
    assert problems(document) == [
        "layered.yaml: parts.api: unknown key 'folders': moved in 0.3.0: write each folder below the part as a key "
        f"ending in /, with its note as its value; use {KNOWN}",
        "layered.yaml: parts.shared: unknown key 'path': moved in 0.3.0: a part is the folder or file it is written "
        f"as under parts: drop it; use {KNOWN}"]


OLD = {"domain": {"path": "modules/<module>/domain", "role": "r", "imports": {"may": ["nothing"]}},
       "platform": {"path": "platform", "role": "r"},
       "controller": {"path": "modules/<module>/application/controller.py", "role": "r"},
       "kernel-logic": {"path": "kernel/logic", "role": "r"}}
OLD_LINES = [
    "layered.yaml: parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the "
    f"folder it lies in (modules/<module>/); use {KNOWN}",
    "layered.yaml: parts.platform: unknown key 'path': moved in 0.3.0: write the part as the folder platform/: at the "
    f"top of parts; use {KNOWN}",
    "layered.yaml: parts.controller: unknown key 'path': moved in 0.3.0: write the part as the file controller.py: "
    f"under the folder it lies in (modules/<module>/application/); use {KNOWN}",
    "layered.yaml: parts.kernel-logic: unknown key 'path': moved in 0.3.0: write the part as the folder logic/: with "
    f"name: kernel-logic, under the folder it lies in (kernel/); use {KNOWN}"]


def test_an_old_flat_profile_is_refused_with_one_line_per_part_and_no_other_problem():
    assert problems(layered(parts=OLD, colour=1, layers={"a": ["nothing"]})) == OLD_LINES


def test_a_profile_mixing_tree_keys_with_an_old_part_gets_only_the_old_part_s_line():
    assert problems(layered(parts={"core/": {"rol": "x"}, "platform": {"path": "platform", "role": "r"}})) == [
        OLD_LINES[1]]
```

In `tests/modules/spec/application/logic/test_profile_needs.py`, add the following, using the file's existing `TOY`/`LANGUAGES` and `problems`. Read one existing refusal test in the file first, and use the fact and key it uses: `holds` needs `class` per its `Key`, and `TOY` supplies `class` only partly. Adapt it like this:

```python
def test_a_part_inside_another_is_addressed_by_its_name_and_a_folder_key_is_no_part():
    document = layered(language="toy", parts={"kernel/": {"role": "k", "docs/": "the notes", "logic/": {
        "name": "kernel-logic", "role": "kl", "holds": {"classes": {}}}}})
    found = short(document, {}, TOY)
    assert [item.address for item in found] == ["parts.kernel-logic.holds", "parts.kernel-logic.holds.classes"][
        :len(found)]
    assert all(not item.address.startswith(("parts.kernel.logic", "parts.docs", "parts.kernel/")) for item in found)
    assert found
```

If `short` on this document yields different addresses (look at what `holds` and `holds.classes` need in `key_table.py`), assert the exact list it yields. The point of the test is that every address starts `parts.kernel-logic.` and that the list is not empty.

The same file reads `layered()`'s parts as a flat map in ten places, and `layered()` is a tree now, so they must move in this task or Step 5 fails with a `KeyError` (or, worse, with keys set on a folder). Add `part_of` to the file's import from `tests.modules.spec.profiles`, then:
- lines 55, 86, 88, 330, 421, 442, 468, 493: `document["parts"]["service"]` becomes `part_of(document, "service")`, so `document["parts"]["service"] |= keys` becomes `part_of(document, "service").update(keys)`, which keeps the same effect on the part's map;
- line 551: `document["parts"]["store"]["imports"]["must"]` becomes `part_of(document, "store")["imports"]["must"]`;
- line 62, in `tiered`: `for spec in document["parts"].values(): spec["tests"] = "unit"` becomes `for name in ("api", "service", "store", "shared"): part_of(document, name)["tests"] = "unit"`. Iterating `document["parts"].values()` would now visit the `src/<module>/` and `shared/` folder maps and set `tests` on the wrong node;
- then `grep -nE "\[\"parts\"\]" tests/modules/spec/application/logic/test_profile_needs.py` and account for every hit. None may index a part by its name.

In `tests/modules/spec/application/logic/test_docs_template.py`, rewrite `PARTS` (lines 12-20) and `parts` (lines 37-38) as the tree, keeping the reading order `store, service, api, shared`:

```python
PARTS = {
    "src/<module>/": {
        "store/": {"role": "database access", "litmus": "Does it touch the database?",
                   "imports": {"may": ["shared/text"]}, "sql/": "the queries"},
        "service/": {"role": "business logic", "litmus": "Does it decide?",
                     "imports": {"may": ["store", "api@any", "shared"]}},
        "api.py": {"role": "HTTP handlers", "litmus": "Does it parse a request?", "imports": {"may": "everything"}},
    },
    "shared/": {"role": "code every module uses", "litmus": "Is it shared?", "imports": {"may": []}},
}
```

```python
def parts(**changes) -> dict:
    document = {"parts": deepcopy(PARTS)}
    for name, change in changes.items():
        part_of(document, name).update(change)
    return document["parts"]
```

(`from copy import deepcopy` and `from tests.modules.spec.profiles import part_of`.) Rewrite the file's other `path` fixtures the same way, and these three flat uses by hand, since none of them has a `path` literal on its own line or they build a part from `PARTS` by name:
- line 176, `layered(docs={}, parts={**PARTS, "shared": shared})`, which would now add a plain key `shared` under `parts` and be refused by row 2: write `document = {"parts": deepcopy(PARTS)}`, then `del part_of(document, "shared")["litmus"]`, then `layered(docs={}, parts=document["parts"])`;
- line 209, `feature`, which rewrote each part's `path`: `feature = {key.replace("<module>", "<feature>"): value for key, value in PARTS.items()}`, the word being a step of the `src/<module>/` key now;
- `TWO` (lines 216-223), written as `{"src/<module>/": {"service/": {...}}, "ext/<plugin>/": {"hooks/": {...}, "manifest.py": {...}}, "shared/": {...}}`. The reading order stays `service, hooks, manifest, shared`, which the test that uses it reads.

Line 89's expected `` `store` → `service` → `api` → `shared` `` stays. Then add:

```python
def test_a_profile_with_no_part_has_no_placement_order_and_is_told_to_write_its_parts_under_parts():
    assert problems("{{placement}}", {"name": "layered", "parts": {}}) == [
        "layered.md: {{placement}}: the architecture has no placement order: write its parts under `parts`, whose "
        "reading order is the order the litmus tests run"]
```

- [ ] **Step 3: Run the parser tests to verify they fail**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_docs_template.py -q`
Expected: FAIL. `parse_profile` still reads `parts` flat: `"parts: 'src/<module>/' is not a part name"` and `missing path`-style problems appear, and the placement text differs.

- [ ] **Step 4: Switch the parser to the tree**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

Imports: add `from xarch.modules.spec.application.logic import parts_tree as pt`. Remove `from xarch.modules.spec.application.logic.layout_walk import is_file` and `_REPEATING` if nothing else uses them (`grep -n "is_file\|_REPEATING" xarch/modules/spec/application/logic/profile_parsing.py`). Keep `EACH`.

Docstring lines 17-21 become:

```
    parts: {<folder>/: {<key of the part>, <folder>/, <file>, ...}, <file>: {role, ...}}
                               the folder tree of the app: a key ending in / is a folder of one or more steps, one
                               written `<word>` the repeating folder, one instance per name, the word what the docs
                               call one instance; a key holding a dot is a file; any other key is a key of the part
                               the folder or file is. A folder with a part's keys is a part, a file always is; a folder
                               with none is only a folder, its value one line of text (its note) or nothing. A part is
                               named by its folder's last step or its file's name before the first dot, or by `name`;
                               the reading order, a part before the parts inside it, is the order their litmus tests run
        name: <name>           the part's name, when its folder or file does not give it
```

Lines 35-36 (the `folders:` entry) are deleted.

`parse_profile`, right after the mapping check:

```python
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys"])
    tree = pt.parts_tree(document.get("parts", {}), _language(document, languages or {}, []))
    if tree.old:
        raise InvalidArchitecture(source, list(tree.old))
```

Replace

```python
    specs = _specs(document.get("parts", {}), problems)
    declared = set(specs)
    built = _layout(specs, problems)
```

with

```python
    problems += tree.problems
    specs = {part.name: part.keys for part in tree.parts}
    declared = set(specs)
    built = _layout(tree, problems)
```

Delete `_specs`, `_path`, `_shown` and `_folders`. Replace `_layout`, `_repeats_alike`, `_insert` and `_add_folder` with:

```python
def _layout(tree: pt.PartsTree, problems: list[str]) -> _Layout:
    """The parts that place validly, in reading order, and the layout they make; then the folders that are no part,
    added after them as the folders of the parts were before 0.3.0, so the layout keeps that order, with their notes."""
    parts: dict[str, Part] = {}
    layout: Layout = {}
    notes: dict[tuple[str, ...], str] = {}
    repeats: list[Repeat] = []
    owners: dict[tuple[str, ...], str] = {}
    for entry in tree.parts:
        where, spec = f"parts.{entry.name}", entry.keys
        for key in ("role", "litmus"):
            if key in spec and not isinstance(spec[key], str):
                problems.append(f"{where}.{key}: must be a string")
        if "untested" in spec and not ck.line(spec["untested"]):
            problems.append(f"{where}.untested: must be one line of text: why no tier tests the part")
        if "package_only" in spec and not isinstance(spec["package_only"], bool):
            problems.append(f"{where}.package_only: must be true or false")
        if len(entry.words) > 1:
            problems.append(f"{where}: '{entry.shown}' has two repeating steps, <{entry.words[0]}> and "
                            f"<{entry.words[1]}>: a repeating folder cannot sit inside another, so give each its own "
                            "folder")
            continue
        word = entry.words[0] if entry.words else ""
        if not _repeats_alike(entry.name, entry.steps, word, repeats, owners, f"{where}: '{entry.shown}'", problems):
            continue
        _insert(layout, entry.steps, entry.file, entry.name, owners)
        parts[entry.name] = Part(entry.name, entry.steps, ck.string(spec.get("role")), ck.string(spec.get("litmus")),
                                 False, spec["untested"] if ck.line(spec.get("untested")) else "")
    for folder in tree.folders:
        _add_folder(layout, folder.steps)
        if folder.note:
            notes[folder.steps] = folder.note
    return _Layout(parts, layout, notes, tuple(repeats))


def _repeats_alike(name: str, steps: tuple[str, ...], word: str, repeats: list[Repeat],
                   owners: dict[tuple[str, ...], str], where: str, problems: list[str]) -> bool:
    """A word repeats in one folder, and a folder is repeated by one word."""
    root = root_of(steps)
    if root is None:
        return True
    here = next((repeat for repeat in repeats if repeat.root == root), None)
    named = next((repeat for repeat in repeats if repeat.word == word), None)
    if here is not None and here.word != word:
        problems.append(f"{where} calls the repeating folder <{word}>, but part '{owners[(*root, EACH)]}' called it "
                        f"<{here.word}> in the same folder '{'/'.join(root)}': two words may not share a parent, use "
                        "one word")
    elif named is not None and named.root != root:
        problems.append(f"{where} repeats <{word}> below '{'/'.join(root)}', but part '{owners[(*named.root, EACH)]}' "
                        f"repeats it below '{'/'.join(named.root)}': one word repeats in one folder, so give this one a "
                        "word of its own")
    else:
        if here is None:
            repeats.append(Repeat(word, root))
            owners[(*root, EACH)] = name
        return True
    return False


def _insert(tree: Layout, steps: tuple[str, ...], file: bool, name: str, owners: dict[tuple[str, ...], str]) -> None:
    """The part's steps in the layout: a folder for every step, the last a file when the part is one."""
    here = tree
    for step in steps[:-1]:
        here = here.setdefault(step, {})
    if file:
        here[steps[-1]] = None
    else:
        here.setdefault(steps[-1], {})
    for i in range(1, len(steps) + 1):
        owners.setdefault(steps[:i], name)


def _add_folder(tree: Layout, path: tuple[str, ...]) -> None:
    here = tree
    for step in path:
        here = here.setdefault(step, {})
```

Collisions `_insert` used to refuse can no longer reach it. Two keys of one map sharing a first step are refused by row 8, anything below a file by row 14, and two words in one folder by `_repeats_alike`. So it holds no refusals.

`_named_packages` becomes:

```python
def _named_packages(document: Mapping[Any, Any], language: Language) -> dict[str, str]:
    """Each package the profile names, by the key of the first place naming it: the parts' `imports.libraries` in
    reading order, then `reserved`. Read silently, and only from an `imports` that is a map: each is said at its own
    place."""
    reserved = ck.reserved_modules(document["reserved"], [], language) if "reserved" in document else {}
    named: dict[str, str] = {}
    for part in pt.parts_tree(document.get("parts"), language).parts:
        written = part.keys.get("imports")
        found = (_imports_libraries(written, f"parts.{part.name}.imports.libraries", [], language, reserved)
                 if isinstance(written, Mapping) else ())
        named |= {package: f"parts.{part.name}.imports.libraries" for package in found
                  if package != EVERYTHING and package not in named}
    named |= {module: "reserved" for module in reserved if module not in named}
    return named
```

In `xarch/modules/spec/application/logic/profile_needs.py`, add the imports `from xarch.modules.spec.application.logic.parts_tree import parts_tree` and `Language` (already imported). Extend the docstring's second sentence with ", the parts by their names in the folder tree under `parts` (see parts_tree)". Then:

```python
def short(document: Mapping[Any, Any], presets: Mapping[str, Any], language: Language, *,
          keys: tuple[Key, ...] = (*KEYS, *SLOTS)) -> list[Shortfall]:
    """... (unchanged) ..."""
    if language.checked.supplies is None:
        return []
    supplies = {supply.fact: supply for supply in language.checked.supplies}
    return [read_less(found, key, language) for address, key in _configured(_named(document), PROFILE, "", presets, keys)
            for found in shortfalls(address, key.needs, supplies)]


def _named(document: Mapping[Any, Any]) -> Mapping[Any, Any]:
    """The document with its folder tree under `parts` as the map of its parts by name, each to its own keys: a folder
    key is no part, and a part inside another is reached."""
    if not isinstance(document.get("parts"), Mapping):
        return document
    return {**document, "parts": {part.name: part.keys for part in parts_tree(document["parts"], Language()).parts}}
```

In `xarch/modules/spec/application/logic/docs_template.py:215`:

```python
        raise _Missing("the architecture has no placement order: write its parts under `parts`, whose reading order is "
                       "the order the litmus tests run")
```

Check for an import cycle: `uv run python -c "import xarch.modules.spec.application.logic.profile_parsing"` must print nothing.

- [ ] **Step 5: Run the parser tests to verify they pass**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_docs_template.py tests/modules/spec/application/logic/test_parts_tree.py tests/modules/spec/application/logic/test_profile_keys.py tests/modules/spec/application/logic/test_key_catalogue.py -q`
Expected: PASS. `test_profile_keys.py` loads every `keys.yaml` example through the parser, so a failure there points at an example of Task 2 that is not yet a tree. Fix the example, not the test.

Run: `uv run ruff check xarch tests/modules/spec`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_parsing.py xarch/modules/spec/application/logic/profile_needs.py xarch/modules/spec/application/logic/docs_template.py tests/modules/spec/profiles.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_docs_template.py
git commit -m "The parser reads parts as the folder tree: the parts in reading order, which is the placement order, a flat profile refused alone with where each part goes, needs and packages read by part name, and the folders of the layout added after the parts as before"
```

---

### Task 4: The bundled, own and archived profiles are written as trees (B6)

**Files:**
- Modify: `xarch/architectures/web.yaml` (the `parts:` block, lines 6-198)
- Modify: `xarch/architectures/cli.yaml` (the `parts:` block)
- Modify: `architecture.yaml` (lines 7-243)
- Modify: `tests/bootstrap/corpora/7cc6111.yaml`, `df537ca.yaml`, `stress.yaml` (the `parts:` blocks)
- Test: `tests/modules/spec/adapters/test_yaml_profile_format.py` (test 19)
- Test: `tests/bootstrap/test_presets.py` or `tests/bootstrap/test_bundled_architectures.py` (test 24)
- Test: `tests/bootstrap/test_profile_new.py` (test 25)
- Test: `tests/bootstrap/test_profile_file.py` (tests 21, 22)
- Test: `tests/bootstrap/test_profile_explain.py` (test 23)
- Test: `tests/bootstrap/test_recorded_corpora.py` (test 26, unchanged)

**Interfaces:**
- Consumes: `YamlProfileFormat.written` (Task 1) and the tree parser (Task 3).
- Produces: the six profile files, as trees.

- [ ] **Step 1: Write the failing profile tests**

Append to `tests/modules/spec/adapters/test_yaml_profile_format.py`:

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize("path", ["xarch/architectures/web.yaml", "xarch/architectures/cli.yaml", "architecture.yaml",
                                  "tests/bootstrap/corpora/7cc6111.yaml", "tests/bootstrap/corpora/df537ca.yaml",
                                  "tests/bootstrap/corpora/stress.yaml"])
def test_each_profile_shipped_or_archived_is_its_tree_as_the_writer_writes_it(path):
    document = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    written = yaml.safe_load(FORMAT.written(document))["parts"]
    assert written == document["parts"]
    assert json.dumps(written) == json.dumps(document["parts"])
    assert all(key.endswith("/") or "." in key for key in document["parts"])
```

(Put the imports at the top of the file. Check `parents[4]` resolves to the repo root: `tests/modules/spec/adapters/<file>` → parents[0]=adapters, [1]=spec, [2]=modules, [3]=tests, [4]=root.)

In `tests/bootstrap/test_bundled_architectures.py` (read it first, and put the test beside the ones that load bundled profiles):

```python
WEB_ORDER = ("domain", "logic", "ports", "services", "controller", "adapters", "contract", "platform", "web",
             "bootstrap", "kernel", "kernel-logic")


@pytest.mark.parametrize("name, order", [
    pytest.param("web", WEB_ORDER, id="web"),
    pytest.param("cli", tuple("cli" if part == "web" else part for part in WEB_ORDER), id="cli"),
    pytest.param("architecture.yaml", ("domain", "logic", "ports", "services", "controller", "adapters", "contract",
                                       "platform", "cli", "reports", "main", "bootstrap", "profile-values", "kernel",
                                       "kernel-logic"), id="xarch"),
])
def test_the_placement_of_each_profile_is_its_tree_s_reading_order(name, order):
    source = Path(__file__).resolve().parents[2] / name if name.endswith(".yaml") else name
    architecture = load_architecture(source)
    assert architecture.placement == order == tuple(architecture.parts)
```

(`load_architecture` from `xarch.bootstrap.wiring`, and `Path` from `pathlib`. Add whichever is missing.)

In `tests/bootstrap/test_profile_new.py`, add:

```python
def test_the_copy_of_web_writes_its_parts_as_the_folder_tree_and_loads(tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "web"]).exit_code == 0
    copy = tmp_path / "architecture" / "mine" / "mine.yaml"
    parts = yaml.safe_load(copy.read_text(encoding="utf-8"))["parts"]
    assert list(parts) == ["modules/<module>/", "platform/", "web/", "bootstrap/", "kernel/"]
    assert load_architecture(copy).placement[-2:] == ("kernel", "kernel-logic")
```

In `tests/bootstrap/test_profile_file.py`, rewrite `PROFILE` (lines 16-…) as a tree: `core:\n    path: core` becomes `core/:`, and the same for `cli`. Then add (`profile_in` is the file's helper):

```python
FLAT = """\
name: old
language: python
parts:
  domain:
    path: modules/<module>/domain
    role: the rules
  platform:
    path: platform
    role: the clients
"""

KNOWN = "holds, imports, litmus, name, package_only, role, shared, tests, untested, uses"


def test_a_profile_of_0_2_0_is_refused_with_where_each_part_goes(tmp_path):
    path = profile_in(tmp_path, FLAT)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the "
        f"folder it lies in (modules/<module>/); use {KNOWN}",
        f"{path}: parts.platform: unknown key 'path': moved in 0.3.0: write the part as the folder platform/: at the "
        f"top of parts; use {KNOWN}")
    result = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert result.exit_code == 2
    assert "parts.domain: unknown key 'path': moved in 0.3.0" in result.output


def test_a_file_part_of_another_extension_is_refused_under_python(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("parts:\n", "parts:\n  notes.txt:\n    role: the notes\n", 1))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert (f"{path}: parts.notes: 'notes.txt' is a file, since its key holds a dot, but it does not end in .py: write "
            "a folder as notes.txt/") in caught.value.problems
```

(If `profile_in` writes to a name other than `small.yaml`, the `path` it returns is what the messages carry, which is why the test uses it.)

In `tests/bootstrap/test_profile_explain.py`, add:

```python
def test_parts_states_the_reading_order_and_name_is_explained_and_path_is_retired():
    whole = runner.invoke(app, ["profile", "explain", "parts"])
    assert whole.exit_code == 0, whole.output
    assert "a part before the parts inside it, is the order their litmus tests run" in " ".join(whole.output.split())
    named = runner.invoke(app, ["profile", "explain", "parts.name"])
    assert named.exit_code == 0, named.output
    assert "the part's name, when its folder or file does not give it" in named.output
    old = runner.invoke(app, ["profile", "explain", "parts.path"])
    assert old.exit_code == 2
    assert "moved in 0.3.0: a part is the folder or file it is written as under parts: drop it" in old.output
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py -q -k "tree or placement or 0_2_0 or extension or reading_order"`
Expected: FAIL. The six files are still flat, so the bundled profiles are refused with the B4 lines.

- [ ] **Step 3: Draft the six `parts` blocks with a throwaway script**

Create `/tmp/xarch-7-1/to_tree.py`, outside the worktree:

```python
"""Draft the parts block of a flat profile as a tree, written by the profile writer: parts in the order given,
former folders as folder keys before child parts, name: only where the place does not give the name."""
import sys
from pathlib import Path

import yaml

from xarch.modules.spec.adapters.yaml_profile_format import YamlProfileFormat
from xarch.platform.yaml_writer import YamlWriter

ORDERS = {
    "web": "domain logic ports services controller adapters contract platform web bootstrap kernel kernel-logic",
    "cli": "domain logic ports services controller adapters contract platform cli bootstrap kernel kernel-logic",
    "xarch": "domain logic ports services controller adapters contract platform cli reports main bootstrap "
             "profile-values kernel kernel-logic",
    "7cc6111": "domain logic ports services controller adapters contract platform cli main bootstrap kernel",
    "df537ca": "domain logic ports services controller adapters contract platform cli reports main bootstrap kernel",
    "stress": "domain logic ports services controller adapters contract platform cli reports main bootstrap kernel",
}
ORDER = ("name", "role", "litmus", "imports", "uses", "holds", "shared", "package_only", "tests", "untested")


def tree(parts: dict, order: list[str]) -> dict:
    assert sorted(order) == sorted(parts), (sorted(order), sorted(parts))
    root: dict = {}
    for name in order:
        spec = dict(parts[name])
        steps = spec.pop("path").strip("/").split("/")
        folders = spec.pop("folders", None)
        here = root
        for step in steps[:-1]:
            here = here.setdefault(f"{step}/", {})
        last = steps[-1]
        key = last if "." in last else f"{last}/"
        given = last.split(".")[0] if "." in last else last
        node = {"name": name} if name != given else {}
        node |= {k: spec[k] for k in ORDER if k in spec}
        assert set(spec) <= set(ORDER), set(spec) - set(ORDER)
        if isinstance(folders, dict):
            node |= {f"{f}/": note for f, note in folders.items()}
        elif isinstance(folders, list):
            node |= {f"{f}/": {} for f in folders}
        assert key not in here, key
        here[key] = node
    return root


path, which = Path(sys.argv[1]), sys.argv[2]
text = path.read_text(encoding="utf-8")
document = yaml.safe_load(text)
block = YamlProfileFormat(YamlWriter()).written({"parts": tree(document["parts"], ORDERS[which].split())}).decode()
lines = text.split("\n")
start = lines.index("parts:")
end = next(i for i in range(start + 1, len(lines)) if lines[i] and not lines[i].startswith(" "))
while end > start and not lines[end - 1].strip():
    end -= 1
lines[start:end] = block.rstrip("\n").split("\n")
path.write_text("\n".join(lines), encoding="utf-8")
print(f"{path}: {len(document['parts'])} parts written as a tree")
```

`here.setdefault(f"{step}/", {})` puts a part's former folders, set when its node is created, before child parts, which are added later in the order. `kernel` comes before `kernel-logic` in every order, so `kernel/` exists when `logic/` is put under it. In 7cc6111/df537ca/stress, `kernel`'s `folders: [logic]` becomes `logic/: {}`.

Run:

```bash
mkdir -p /tmp/xarch-7-1
uv run python -I /tmp/xarch-7-1/to_tree.py xarch/architectures/web.yaml web
uv run python -I /tmp/xarch-7-1/to_tree.py xarch/architectures/cli.yaml cli
uv run python -I /tmp/xarch-7-1/to_tree.py architecture.yaml xarch
uv run python -I /tmp/xarch-7-1/to_tree.py tests/bootstrap/corpora/7cc6111.yaml 7cc6111
uv run python -I /tmp/xarch-7-1/to_tree.py tests/bootstrap/corpora/df537ca.yaml df537ca
uv run python -I /tmp/xarch-7-1/to_tree.py tests/bootstrap/corpora/stress.yaml stress
```

Expected: six `… parts written as a tree` lines.

- [ ] **Step 4: Read each file and finish the archived ones by hand**

For each of the six files, run `git diff -- <file>` and read the whole parts block:
- Every part's role, litmus and rules are unchanged in content. Each litmus is the same words, re-folded as `>-` within 120 columns. Check it: `uv run python -c "import yaml,sys; a=yaml.safe_load(open(sys.argv[1])); print(len(a))" <file>` loads, and no line of the parts block is longer than 120: `awk '/^parts:/{p=1;next} /^[a-z]/{p=0} p && length > 120' <file>` prints nothing (a long line outside `parts`, such as `docs.naming` in `architecture.yaml`, was there before and stays).
- `name:` appears only on `kernel/logic/` (`kernel-logic`), `profile_values/` (`profile-values`) and `__main__.py` (`main`).
- No part gains a key (no `shared: 2`).
- The top level reads `modules/<module>/`, `platform/`, `web/` or `cli/`, (`__main__.py`,) `bootstrap/`, (`profile_values/`,) `kernel/`, and within `modules/<module>/`: `domain/`, `application/` (`logic/`, `ports/`, `services/`, `controller.py`), `adapters/`, `contract/`.
- The text outside the block, including the blank line before the next top-level key, is unchanged (`git diff` shows no hunk outside `parts`).
For the three corpora `.yaml` files, the script only draft. Fix any blank-line or folding detail by hand so the file reads as written by hand, and change nothing outside `parts`.

- [ ] **Step 5: Run the profile tests and the recorded corpora**

Run: `uv run pytest tests/modules/spec/adapters/test_yaml_profile_format.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_presets.py -q`
Expected: the new tests PASS. Older tests in these files that write flat fixtures may still fail; they belong to Task 5. List them.

Run: `timeout 900 uv run pytest tests/bootstrap/test_recorded_corpora.py -q`
Expected: PASS, unchanged. **If it fails, stop.** Do not edit or re-dump any `*.json`, `*.tar.xz` or `*.json.xz`. Restore with `git checkout -- tests/bootstrap/corpora/*.json*` if anything moved, and escalate with the failing assertion.

Run: `uv run xarch profile check architecture.yaml; echo "exit $?"`
Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add xarch/architectures/web.yaml xarch/architectures/cli.yaml architecture.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml tests/bootstrap/corpora/stress.yaml tests/modules/spec/adapters/test_yaml_profile_format.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_profile_new.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py
git commit -m "The bundled profiles, xarch's own and the archived ones write parts as the folder tree, as the writer writes it; contract moves up and kernel comes before kernel-logic in placement; the recorded findings are unchanged"
```

---

### Task 5: Every remaining fixture is a tree (test 27)

**Files (modify; each is read before it is edited):**
Builders first: `tests/modules/spec/application/builders.py`, `tests/modules/spec/application/helpers.py`, `tests/modules/spec/application/origins.py`, `tests/bootstrap/project.py`, `tests/modules/rules/builders.py`, `tests/fakes/review.py`, `tests/fakes/filesystem.py`, `tests/fakes/folders.py`, `tests/platform/conftest.py`.
Then each test file that `grep -rlnE "\"path\": *[\"']|'path': *[\"']|^\s+path: |[{ ,]path: [a-zA-Z_<\"]|\"folders\"|folders:|\[\"parts\"\]\[" tests --include=*.py` lists. Today that is about 70 files, among them `test_architecture_files.py`, `test_looseness.py`, `test_profile_parsing_tests.py`, `test_never_use.py`, `test_imports_written.py`, `test_libraries_and_guards.py`, `test_tiers.py`, `test_profile_parsing_docs.py`, `test_evals.py`, `test_language_seam.py`, `test_where.py`, `test_repeating_folders.py`, `test_imports.py`, `test_docs_templates.py` and the `tests/cli/reports/*` files.

**Interfaces:**
- Consumes: `tests.modules.spec.profiles.part_of` (Task 3) for tests under `tests/modules/spec/`.

The rewrite rules, applied to every fixture:

| Flat (today) | Tree |
|---|---|
| `"core": {"path": "core", "role": r, ...}` | `"core/": {"role": r, ...}` |
| `"api": {"path": "src/<module>/api", ...}` with siblings in `src/<module>/` | one `"src/<module>/": {"api/": {...}, "service/": {...}}`; never two keys sharing `src/` |
| `"main": {"path": "__main__.py", ...}` | `"__main__.py": {"name": "main", ...}` |
| `"x": {"path": "a/b", ...}` where the key differs from `b` | `"a/b/": {"name": "x", ...}`, or nested under an existing `a/` |
| `"folders": {"routes": "note"}` | `"routes/": "note"` inside the part, after its own keys |
| `"folders": ["a"]` | `"a/": {}` |
| a file part with a made-up name (`"f": {"path": "notes"}`) | a real extension: `"notes.py"` |
| `document["parts"]["x"]["k"]` (an existing part) | `part_of(document, "x")["k"]` under `tests/modules/spec/`; the literal tree path (`document["parts"]["src/<module>/"]["api/"]["k"]`) elsewhere |
| `document["parts"]["new"] = {"path": ...}` (adds a part) | the key at its tree place, as in the rows above |
| YAML text: `  core:\n    path: core\n    role: r` | `  core/:\n    role: r` |
| YAML flow: `api: {path: "src/<module>/api", role: x}` | `"src/<module>/":\n    api/: {role: x}` |

Keep the reading order equal to the old file order wherever a test reads `placement`, part order, review's option order or a docs line. The exception is a test that reads the rewritten bundled or own profiles: update its expected order to B2's, and to no other order.

- [ ] **Step 1: List what to rewrite and confirm it fails**

Run:
```bash
grep -rlnE "\"path\": *[\"']|'path': *[\"']|^\s+path: |[{ ,]path: [a-zA-Z_<\"]|\"folders\"|folders:|\[\"parts\"\]\[" tests --include=*.py > /tmp/xarch-7-1/fixtures.txt
wc -l /tmp/xarch-7-1/fixtures.txt
timeout 900 uv run pytest -q -x --co -q >/dev/null && timeout 900 uv run pytest -q 2>&1 | tail -3
```
Expected: about 70 files, and a full suite with many failures, almost all `unknown key 'path': moved in 0.3.0` (the B4 refusal). These failing tests are this task's RED. No new test is written here: the existing tests are the spec, and each keeps its substance.

- [ ] **Step 2: Rewrite the builders**

`tests/modules/spec/application/builders.py:17-18`:

```python
        "parts": {"core/": {"role": "the rules"},
                  "api/": {"role": "the handlers", "imports": {"may": ["core"]}}},
```

For each other builder in the list above, read the file, apply the rules table, and run the tests that import it:
`uv run pytest -q $(grep -rl "<builder module path>" tests | tr '\n' ' ')`.
Many hits in `tests/fakes/filesystem.py`, `tests/modules/rules/builders.py` and `tests/bootstrap/project.py` are `Path`/`path` variables that do not write a profile: leave those alone.

- [ ] **Step 3: Rewrite each test file, one at a time**

For each file in `/tmp/xarch-7-1/fixtures.txt`:
1. Read the file.
2. Rewrite every profile fixture by the rules table.
3. Run `uv run pytest -q <file>` and expect PASS. A test that still fails keeps its assertion. Only the fixture changes, except where the assertion holds the old refusal texts or the order of the rewritten bundled profiles. Today's `.path` and `folders` texts are gone, so a test that asserted one either moves to the tree text of B3 that says the same thing, or is deleted when Task 2's `test_parts_tree.py` already covers it. Note each such deletion for the commit message.
4. After each group of about ten files, commit:

```bash
git add <the files>
git commit -m "The fixtures of <area> write parts as the folder tree"
```

- [ ] **Step 4: Account for every remaining hit**

Run:
```bash
grep -rnE "\"path\": *[\"']|'path': *[\"']|^\s+path: |[{ ,]path: [a-zA-Z_<\"]|\"folders\"|folders:" tests --include=*.py --include=*.yaml | grep -v "tests/bootstrap/corpora/.*json"
grep -rnE "^\s+path: |folders:" docs --include=*.md | grep -v "docs/superpowers\|docs/examples"
```
Expected: every remaining hit is not a part's path. Examples: a `path:` that is a field of another structure (a fixture file listing, a JSON report field), `docs/examples/*.py` (out of scope), and the golden `docs/*/architecture.md` (regenerated in Task 6). Write the list of remaining hits and why each stays into the last commit message of this task.

- [ ] **Step 5: Run the whole suite**

Run:
```bash
timeout 900 uv run pytest -q > /tmp/xarch-7-1/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-7-1/suite.log
tail -5 /tmp/xarch-7-1/suite.log
```
Expected: `exit 0`, all passed. The one allowed exception is golden-doc tests (`test_docs_templates.py::test_xarch_own_architecture_generates_exactly_the_docs_checked_in_under_docs_xarch`, `test_docs.py` comparisons), which Task 6 regenerates. List them if they fail. Any other failure is fixed here.

- [ ] **Step 6: Commit**

```bash
git add tests
git commit -m "Every fixture writes parts as the folder tree; the remaining path hits are not part paths: <list>"
```

---

### Task 6: README, CHANGELOG, golden docs and every gate

**Files:**
- Modify: `README.md:105-125` (the profile block), `README.md:205-226` (the smallest profile and the symbols)
- Modify: `CHANGELOG.md` (`## [Unreleased]`)
- Regenerate: `docs/cli/architecture.md`, `docs/web/architecture.md`, `docs/xarch/architecture.md`
- Test: `tests/architecture/test_readme.py`, `tests/bootstrap/test_docs.py`, `tests/bootstrap/test_docs_templates.py`

- [ ] **Step 1: Rewrite the README's profile sections**

`README.md` around line 110. The sentence "Its parts are listed in the order their litmus tests run, which is also the order of the generated docs' tree and rules table." becomes:

```
A profile is one YAML file that states each fact once, on the thing it is about. Its `parts` are the app's folder tree,
and the tree's reading order (top to bottom, a part before the parts inside it) is the order their litmus tests run,
which is also the order of the generated docs' rules table. The shape (`*` is required; everything else is optional,
and a key left out means off):
```

The `parts*:` lines of the shape block become:

```
parts*:   {<folder>/: {<folder>/ | <file> | name, role*, litmus, imports: {may, must, libraries}, uses: {never},
                       holds: {classes: {names, immutable, built_by}, functions: {names}, records: {names, immutable},
                               exceptions: {names}}, shared, package_only, tests | untested}, <file>: {...}}
```

The smallest profile (line ~215):

```yaml
name: documents-app
parts:
  documents/:
    role: the documents
```

The first symbols bullet becomes:

```
- Under `parts`, a key ending in `/` is a folder of one or more steps (`modules/<module>/`), a key holding a dot is a
  file (`controller.py`), and any other key is a key of the part the folder or file is. A folder with a `role` is a
  part; one with no key of a part is only a folder, whose value may be one line of text, its note; a file is always a
  part. A part is named by its folder's last step or its file's name before the first dot, or by `name:`, which two
  parts of one name need. `<unit>/` is a repeating folder, one instance per name (`xarch new` takes the word); a
  profile may have several, each with a word of its own and one parent, and one cannot sit inside another.
```

Run `uv run pytest tests/architecture/test_readme.py -q` and expect PASS. If it pins a sentence that changed, read that test. It checks the README against the format, so make the README say what the test reads rather than loosening the test.

- [ ] **Step 2: Add the CHANGELOG entry**

Under `## [Unreleased]`, add a `### Changed` section if there is none (after `### Added`), and add this entry to it:

```
- `parts` is the app's folder tree: a key ending in `/` is a folder, a key holding a dot a file, any other key a key
  of the part; a folder with a `role` is a part, a file always is, and a part is named by its folder's last step or
  its file's name before the first dot. `name` is new, for a part whose place does not give its name (`kernel/logic/`
  with `name: kernel-logic`). `path` and `folders` are retired: a profile written with them is refused with one line
  per part saying where it goes (`parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder
  domain/: under the folder it lies in (modules/<module>/); use ...`), and a folder of a part is written below it, its
  note as its value. The placement order is the tree's reading order, a part before the parts inside it: in the
  bundled profiles `contract` moves up to follow `adapters`, and `kernel` now comes before `kernel-logic`, so review's
  placement question offers its options in that order. `profile new` copies the tree, and the profile writer writes
  it, single chains of plain folders joined.
```

- [ ] **Step 3: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-7-1/regenerate_docs.py`:

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
uv run python -I /tmp/xarch-7-1/regenerate_docs.py "$PWD"
git status --short -- docs/cli docs/web docs/xarch
git diff -- docs/cli docs/web docs/xarch
```

Expected: `written`. Only `docs/{cli,web,xarch}/architecture.md` move, and `docs/{cli,web,xarch}/testing.md` do not move. Read every hunk:
- The placement line: `` `domain` → `logic` → `ports` → `services` → `controller` → `adapters` → `contract` → `platform` → `web` → `bootstrap` → `kernel` → `kernel-logic` `` (cli and xarch per B2).
- Lines or rows that iterate `architecture.parts` (the rules table, and lists of parts) are reordered and otherwise unchanged.
- The folder tree of section 1 (from `{{tree}}`) does **not** move. In xarch, `cli/` still shows `reports/` before `commands/`.

Any other change is a defect. Restore with `git checkout -- docs/cli docs/web docs/xarch`, find its cause in the code, fix it, and regenerate. Do not hand-edit a golden doc. Write the summary of the read diff (files, which lines moved, and that `testing.md` did not move although the card and O8 name it) into the commit message.

- [ ] **Step 4: Run every gate**

Run:
```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile check exit $?"
timeout 900 uv run pytest -q > /tmp/xarch-7-1/suite.log 2>&1; echo "exit $?" >> /tmp/xarch-7-1/suite.log
tail -5 /tmp/xarch-7-1/suite.log
git status --short -- .claude
```
Expected: `All checks passed!`, exit 0 for each of the three `xarch` commands, `exit 0` with all passed in the suite log, and nothing under `.claude` staged.

`xarch check` may report the new module. If `dead-code` lists a field of `TreePart` (such as `order`, read only by tests), read the finding. `order` is part of the spec's entry and `tests_only` flags code reached only by tests. Make the parser read it, by building `Part`s in `sorted(tree.parts, key=lambda entry: entry.order)` in `_layout`, rather than dropping the field the spec names. If `xarch check` holds `parts_tree.py` to a rule of `logic` (pure, no classes beyond records), the frozen records meet it. Fix any finding in the code; never loosen `architecture.yaml`.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md docs/cli docs/web docs/xarch
git commit -m "README and CHANGELOG say parts is the folder tree, with name, the retired path and folders and the old-profile refusal, and the reading order as the placement order; the golden architecture docs regenerate with only the placement line and the part-ordered rows moved (<diff summary>); testing.md does not move, though the card and O8 name it"
```

---

## Self-Review

**1. Spec coverage.**
- B1: reading the tree is Task 2 (`parts_tree`) and Task 3 (`_layout`, `specs`). Equality of joined and nested is Task 3 test (d). Notes are Task 3. Placement equals parts in Tasks 3 and 4.
- B2: the orders are Task 4 (`test_the_placement_of_each_profile_…`) and Task 6 (docs). The `_Missing` text is Task 3.
- B3: rows 1-15 and 17 are Task 2's parametrized test. Row 16 is Task 3 (`two repeating steps`, `two words`, `one word`). Several problems at once are Task 2.
- B4: Task 2 (walk), Task 3 (parse, mixed) and Task 4 (bootstrap).
- B5: needs is Task 3. `_named_packages` is Task 3. `declared` comes from `specs` in Task 3.
- B6: Task 4, with test 19 there and the corpora gate there.
- B7: Task 1, plus test 19 in Task 4.
- B8: the key table, RETIRED and `keys.yaml` are Task 2. The docstring is Task 3. README, CHANGELOG and golden docs are Task 6.
- Tests 1-28 are each placed. Test 27 is Task 5. Tests 26 and 28 run in Tasks 4 and 6.

**2. Placeholder scan.** Task 5 gives rules and worked rewrites instead of each of ~70 files' edits. The edits are mechanical by the rules table, and the existing tests are their RED and GREEN. Every other step carries its code.

**3. Type consistency.** `parts_tree(value, language) -> PartsTree`. `TreePart(name, steps, words, order, keys, shown, file)` and `TreeFolder(steps, note)` are used with the same fields in Tasks 2 and 3. `part_of(document, name)` is defined in Task 3 and used in Tasks 3 and 5. `endings` is public from Task 2.

**4. Review Focus.** Each of its five lines has its test in the owning task, as named there.
<!-- task-pipeline: validated -->
