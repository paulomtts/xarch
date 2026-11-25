# 4.5 A part's import keys move into one `imports` group Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A part writes `imports: {may, must, libraries}` in place of `may_import`, `must_import` and `libraries`. A
target it may use only as a type is marked on its entry of `may` as `{<target>: types_only}`, in place of the part's
`types_only` list. The four old part keys are refused with the form that replaces them. Findings, `profile explain`
and `profile check` name the new addresses. Every bundled profile, and xarch's own, finds the same findings, but for the
key.

**Architecture:** spec reads the group in a new module, `imports_written.py`. `group` checks the shape of `imports`,
`may` gives every entry as a plain target plus the marked targets, and `must` gives the `must` targets. `Part.types_only`
becomes the marked `Target`s. The key table opens two scopes, `parts.<part>.imports` and `parts.<part>.imports.may`. The
second holds one key, the mark `types_only`. The needs walker reads a list of entries as the modes its entries carry.
rules keys its findings by the new addresses. The types-only rule of a part then matches, with `Match("place")`, what
the marked targets reach (with their name patterns dropped), not part names. Looseness gains the line
`imports.may.types_only`.

**Tech Stack:** Python 3.13, uv, pytest, ruff, PyYAML, typer's CliRunner; xarch's own `xarch check` and
`xarch profile check`.

**Spec:** `docs/superpowers/specs/4-5-spec-a-part-s-912dfd81.md` (read it with this plan; section numbers below are its)

## Global Constraints

- No comments in xarch's code (docstrings only); never `ruff --fix`.
- Tests written first, each seen failing for the right reason; examples simple, with absolute `app.` imports.
- Recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as spec 2.11 says. Each replacement is
  anchored on `parts.<p>.`. Never a blind replace of `types_only)`. The stress file is decompressed to a scratch copy,
  edited, and recompressed, and the text diff is read.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`.
- `.claude/` stays out of commits; nothing is pushed.
- Golden docs `docs/{cli,web,xarch}/testing.md` are regenerated, never hand-edited. Each moves only the `may-import`
  line and the enforcement paragraph.
- README and CHANGELOG lines go under `## [Unreleased]`.
- No compatibility window: old keys are never accepted as aliases or with a warning.
- Rule ids, `where`'s JSON fields (`may_import`, `may_import_text`, `libraries`, `test.types_only`), the filter
  `may-import-everything` and the tier keys (`tiers.<t>.may_import`, `may_also_import`, `must_import`, `types_only`)
  do not change.
- Internal Python names (`must_import`, `types_only`, `libraries`, `rules`, `may_import` fields and functions) stay.
- Entries keep today's spelling (`kernel`, `contract@any`, `domain/values:*Id`). References are story 8.
- No bundled profile and not xarch's own gains a mark.
- Gates: `uv run pytest -q` (over two minutes: in the background), `uv run xarch check`, `uv run xarch check --strict`,
  `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## Review Focus

1. **`imports` with `must` but no `may`** (`imports: {must: [platform]}`). A person expects the "is not in imports.may"
   problem for each entry, not a crash and not silence. Pinned in Task 2 (`test_imports_written.py::test_must_without_may_is_refused_entry_by_entry`).
2. **A retired key written beside `imports` on one part** (`may_import: [x]` and `imports: {may: [y]}`). A person
   expects exactly the retired-key problem, with `imports` still read and checked. Pinned in Task 2
   (`test_imports_written.py::test_a_retired_key_beside_the_group_is_its_own_problem_and_the_group_is_still_read`).
3. **The needs walker on odd `may` values**: `may: everything`, and a refused mode `{ports: types}`. The walker must
   not crash, and it gives no `types_only` shortfall. Pinned in Task 2
   (`test_profile_needs.py::test_a_may_with_no_mark_needs_nothing_of_types_only`).
4. **The same target written plain and marked** (`may: [contract, {contract: types_only}]`). A person expects the
   profile to load, with the mark kept. Pinned in Task 2 (`test_imports_written.py::test_a_target_written_plain_and_marked_keeps_its_mark`).
5. **A custom part widened to `may: everything` over a bundled mark.** This loosens the mark, so a person expects the
   new looser line. Pinned in Task 4 (`test_looseness.py`, the id `everything over a mark`).

---

### Task 1: A wired test holds what the bundled profiles import to what they import today

Spec: test 16. The test is written first and passes on the code before the change. Task 2 changes only its keys.

**Files:**
- Create: `tests/bootstrap/test_bundled_imports.py`

**Interfaces:**
- Produces: `tests/bootstrap/test_bundled_imports.py` with the dict `KEYS = {"may": ..., "must": ..., "libraries": ...}`
  of explain addresses. Task 2 changes only that dict.

- [ ] **Step 1: Write the test, with the literals recorded from today's code**

The literals below were recorded from the code at `533afaf` with `xarch where --format json` and
`xarch profile explain <key> --rule --format json`. Each `checks` text is hashed. The one wording change of spec 2.7
inside a rule text, `(parts.{first_library_owner}.libraries)` becoming `.imports.libraries)`, is undone before
hashing, so the hash holds "the same rules but for the key".

```python
"""What a part of a bundled profile, or of xarch's own, may import, must import and may import from outside stays what
it was before the part's import keys moved into one `imports` group: `where` says the same of a file of every part of
xarch's own profile, and the rules the keys expand to are, as checks, the same text for each profile but for the key."""
import hashlib
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
KEYS = {"may": "parts.may_import", "must": "parts.must_import", "libraries": "parts.libraries"}
"""The address `profile explain` is asked for each key of the group."""
PATHS = {"domain": "xarch/modules/spec/domain/x.py", "logic": "xarch/modules/spec/application/logic/x.py",
         "ports": "xarch/modules/spec/application/ports/x.py",
         "services": "xarch/modules/spec/application/services/x.py",
         "controller": "xarch/modules/spec/application/controller.py", "adapters": "xarch/modules/spec/adapters/x.py",
         "platform": "xarch/platform/x.py", "cli": "xarch/cli/x.py", "reports": "xarch/cli/reports/x.py",
         "main": "xarch/__main__.py", "bootstrap": "xarch/bootstrap/x.py",
         "contract": "xarch/modules/spec/contract/x.py", "profile-values": "xarch/profile_values/x.py",
         "kernel-logic": "xarch/kernel/logic/x.py", "kernel": "xarch/kernel/x.py"}
"""One path of each part of xarch's own profile."""
WHERE = {
    "domain": ("its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "logic": ("its own module's `application/logic/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "ports": ("its own module's `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "services": ("its own module's `application/services/`, `application/logic/`, `domain/`, `application/ports/` and "
                 "`contract/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "controller": ("its own module's `application/controller.py`, `application/services/`, `contract/` and "
                   "`domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "adapters": ("its own module's `adapters/`, `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`, `platform/`, any module's `contract/`", ["ast", "tokenize"]),
    "platform": ("`platform/`, `kernel/`, `kernel/logic/`", ["yaml"]),
    "cli": ("`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, `kernel/`, "
            "`kernel/logic/`", ["typer"]),
    "reports": ("`cli/reports/`, any module's `contract/`, `kernel/`, `kernel/logic/`", []),
    "main": ("`__main__.py`, `bootstrap/`", []),
    "bootstrap": ("everything", []),
    "contract": ("its own module's `contract/`, `domain/values:*Id` and `domain/published`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`", []),
    "profile-values": ("`profile_values/`, `kernel/`", []),
    "kernel-logic": ("`kernel/logic/`, `kernel/`, `profile_values/`", []),
    "kernel": ("`kernel/`", []),
}
"""What `where` said of each part before the change: may_import_text and libraries."""
RULES = {
    ("cli", "may"): (12, "56c3045d340f9998"), ("cli", "must"): (1, "3a6fe3a7e4628850"),
    ("cli", "libraries"): (24, "530c3c0c9fe79616"),
    ("web", "may"): (12, "0f4747306974eadd"), ("web", "must"): (1, "3a6fe3a7e4628850"),
    ("web", "libraries"): (24, "482cc8c560189bf3"),
    ("architecture.yaml", "may"): (15, "55bbcc7bd4a5acdd"), ("architecture.yaml", "must"): (1, "3a6fe3a7e4628850"),
    ("architecture.yaml", "libraries"): (30, "5a45f6bcb3e80741"),
}
"""For each profile and key of the group: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change."""


def explained(key: str, profile: str) -> tuple[int, str]:
    found = json.loads(runner.invoke(app, ["profile", "explain", KEYS[key], "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    text = found["checks"].replace(".imports.libraries)", ".libraries)")
    return found["rules"], hashlib.sha256(text.encode()).hexdigest()[:16]


@pytest.mark.parametrize("part", list(PATHS))
def test_where_says_what_each_part_of_xarch_may_import_as_before(part):
    found = json.loads(runner.invoke(app, ["where", PATHS[part], "--format", "json"]).output)
    assert found["part"]["name"] == part
    assert (found["may_import_text"], found["libraries"]) == WHERE[part]


@pytest.mark.parametrize("profile, key", list(RULES))
def test_each_key_of_the_group_expands_to_the_rules_of_before(profile, key):
    assert explained(key, profile) == RULES[profile, key]
```

- [ ] **Step 2: Run it on today's code**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_bundled_imports.py`
Expected: PASS (24 tests). If a hash differs, the code has moved since `533afaf`. Re-record that hash with the
`explained` function on this commit, before anything else changes, and say so in the commit message.

- [ ] **Step 3: Commit**

```bash
git add tests/bootstrap/test_bundled_imports.py
git commit -m "A wired test holds what where says each part of xarch's own profile may import and the libraries it may use, and the rules may_import, must_import and libraries expand to in the bundled profiles and xarch's own, to what they are before the part's import keys move into one group"
```

---

### Task 2: The `imports` group replaces the four part keys

Spec: 2.1-2.5, 2.6 (values; adapter bridged), 2.7 (finding keys and texts), 2.9 (profiles), 2.11 (corpora), 2.4 (explain
examples); tests 1-9, 11, 13, 14, 15 (text half), 16 (keys switched), 17, 20-23; domain test. This is one task because
the suite is green only when the parser, the key table, every profile and the rule keys move together. `profile
explain parts.imports.may --rule` must find the rules keyed `parts.<p>.imports.may`.

**Files:**
- Create: `xarch/modules/spec/application/logic/imports_written.py`
- Create: `tests/modules/spec/application/logic/test_imports_written.py`
- Modify: `xarch/modules/spec/domain/profile_keys.py` (scopes `PART_IMPORTS`, `PART_IMPORTS_MAY`; `RETIRED`)
- Modify: `xarch/modules/spec/domain/key_table.py` (rows, `NEEDS`)
- Modify: `xarch/architectures/presets/format/keys.yaml` (in the same commit as `key_table.py`: the catalogue test reads both)
- Modify: `xarch/modules/spec/application/logic/profile_needs.py` (`_held` reads the modes of a list's entries)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (lines 19-22, 36, 178, 185-193, 444-470, 850-869, 933-951)
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:601`
- Modify: `xarch/modules/spec/application/logic/example_imports.py:6,68`
- Modify: `xarch/modules/spec/application/logic/key_lookup.py:13-14`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:566-568`
- Modify: `xarch/modules/spec/domain/values.py:84,95`, `xarch/modules/spec/contract/__init__.py:95-110`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:80` (bridge: marked targets to part names until Task 3)
- Modify: `xarch/modules/rules/application/logic/expansion.py` (keys of `_libraries`, `_rules`, `_types_only_parts`, `_must_import`; `KEYS`; docstrings)
- Modify: `xarch/modules/rules/application/logic/sentences.py:144-147`
- Modify: `xarch/modules/rules/domain/vocabulary.py:35,259,267,307,334,372-374,392,406`
- Modify: `xarch/cli/commands/profile.py:66`, `xarch/cli/reports/profile_report.py:44`
- Modify (profiles): `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`, `tests/bootstrap/corpora/stress.yaml`
- Modify (recorded findings, anchored replace): `tests/bootstrap/corpora/7cc6111.json`, `df537ca.json`, `stress-7cc6111.json.xz`
- Modify (tests): `tests/bootstrap/test_bundled_imports.py` (`KEYS` only), `tests/modules/spec/domain/test_profile_keys.py`, `tests/modules/spec/application/logic/test_retired_keys.py`, `test_profile_needs.py`, `test_profile_parsing.py`, `test_profile_parsing_substance.py`, `test_targets_written.py`, `tests/bootstrap/test_needs_agree.py`, `tests/bootstrap/test_profile_explain.py`, and every test file holding an inline profile or an expected text naming a part's import key (Step 14 lists how to find them)

**Interfaces:**
- Consumes: `targets_written.may_import(value, owner, parts, declared, where, problems, patterns=False, mirrored=False) -> tuple[Target, ...]`; `ck.unknown_keys(spec, known, where, scope)`; `key_lookup.names_of(scope)`.
- Produces:
  - `profile_keys.PART_IMPORTS = "part.imports"`, `PART_IMPORTS_MAY = "part.imports.may"`.
  - `imports_written.group(spec: Mapping, where: str, problems: list[str]) -> Mapping`
  - `imports_written.may(value, owner: Part, parts: dict[str, Part], declared: set[str], where: str, problems: list[str]) -> tuple[tuple[Target, ...], tuple[Target, ...]]` (every entry as a plain target, and the marked targets)
  - `imports_written.must(group: Mapping, owner: Part, parts, declared, allowed: tuple[Target, ...], problems) -> tuple[Target, ...]`
  - `Part.types_only: tuple[Target, ...]`, `PartView.types_only: tuple[Target, ...]`.
  - Rule keys `parts.<p>.imports.may`, `parts.<p>.imports.must`, `parts.<p>.imports.libraries`, `parts.<p>.imports.may.types_only`. `expansion.KEYS` holds `parts.imports.may`, `parts.imports.libraries`, `parts.imports.must`, `parts.imports.may.types_only`.
  - rules `Profile.types_only` stays `dict[str, tuple[str, ...]]` in this task (bridged); Task 3 changes it.

- [ ] **Step 1: Write the failing domain test for the scopes and the retired entries**

In `tests/modules/spec/domain/test_profile_keys.py`, import `PART_IMPORTS`, `PART_IMPORTS_MAY` and `PART`/`TIER` from
`profile_keys`, and `KEYS` from `key_table`, and add:

```python
def test_imports_opens_a_scope_of_may_must_and_libraries_and_may_opens_the_scope_of_its_mark():
    def names(scope):
        return [key.name for key in KEYS if key.scope == scope]

    imports = next(key for key in KEYS if key.scope == PART and key.name == "imports")
    may = next(key for key in KEYS if key.scope == PART_IMPORTS and key.name == "may")
    assert imports.opens == PART_IMPORTS and imports.rules == ("may-import", "must-import", "libraries")
    assert names(PART_IMPORTS) == ["may", "must", "libraries"]
    assert may.opens == PART_IMPORTS_MAY and names(PART_IMPORTS_MAY) == ["types_only"]
    assert SCOPES[PART_IMPORTS] == "parts.<part>.imports" and SCOPES[PART_IMPORTS_MAY] == "parts.<part>.imports.may"
    assert not {"may_import", "must_import", "libraries", "types_only"} & set(names(PART))
    assert {"may_import", "must_import", "types_only", "may_also_import"} <= set(names(TIER))


def test_the_part_import_keys_need_what_the_keys_they_replace_needed():
    imports = ("import", "import.relative")
    assert NEEDS["parts.<part>.imports.may"] == imports
    assert NEEDS["parts.<part>.imports.must"] == (*imports, "import.standard", "function.statements", "file",
                                                   "file.package")
    assert NEEDS["parts.<part>.imports.libraries"] == (*imports, "import.standard")
    assert NEEDS["parts.<part>.imports.may.types_only"] == ("call", "use", "module_functions", "import.resolved")
    assert "parts.<part>.imports" not in NEEDS
    assert not [address for address in NEEDS if address.startswith("parts.<part>.") and address.rsplit(".", 1)[1]
                in ("may_import", "must_import", "libraries", "types_only")]
```

(add `NEEDS` and `SCOPES` to the imports if they are missing). Then update
`test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules` (line
48). Read its body and add the six new entries of Step 3 to the set it expects.

- [ ] **Step 2: Run it to see it fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py`
Expected: FAIL with `ImportError: cannot import name 'PART_IMPORTS'`.

- [ ] **Step 3: Add the scopes and the retired entries**

In `xarch/modules/spec/domain/profile_keys.py`, after `PART_USES = "part.uses"`:

```python
PART_IMPORTS = "part.imports"
PART_IMPORTS_MAY = "part.imports.may"
```

and in `SCOPES`, after `PART_USES: "parts.<part>.uses",`:

```python
    PART_IMPORTS: "parts.<part>.imports",
    PART_IMPORTS_MAY: "parts.<part>.imports.may",
```

At the end of `RETIRED`, before the closing parenthesis, add the entries in this order (spec 2.3, word for word):

```python
    Retired(PART, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
    Retired(PART, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
    Retired(PART, "libraries", "moved in 0.3.0: write imports: {libraries: [...]}"),
    Retired(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                                "[{ports: types_only}]"),
    Retired(PART_IMPORTS, "never", "a key of uses, beside imports: write uses: {never: <list>}"),
    Retired(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                                        "[{ports: types_only}]"),
```

- [ ] **Step 4: Change the key table**

In `xarch/modules/spec/domain/key_table.py`, import `PART_IMPORTS` and `PART_IMPORTS_MAY`. In `_KEYS`, put
`Key(PART, "imports", ...)` in the place of `may_import`. Delete the rows `Key(PART, "must_import", ...)`,
`Key(PART, "types_only", ...)` and `Key(PART, "libraries", ...)`:

```python
    Key(PART, "litmus", False, False),
    Key(PART, "imports", rules=("may-import", "must-import", "libraries"), opens=PART_IMPORTS),
    Key(PART, "holds", rules=("holds",), opens=PART_HOLDS, when_supplied=("function.top_level",),
        without="holds reads no top-level functions"),
    Key(PART, "shared", rules=("shared",)),
    Key(PART, "uses", opens=PART_USES),
```

Insert the two scopes just before `Key(PART_USES, "never", rules=("never-use",)),`:

```python
    Key(PART_IMPORTS, "may", rules=("may-import",), opens=PART_IMPORTS_MAY),
    Key(PART_IMPORTS, "must", rules=("must-import",)),
    Key(PART_IMPORTS, "libraries", rules=("libraries",)),

    Key(PART_IMPORTS_MAY, "types_only", rules=("types-only",)),

```

In `NEEDS`, replace the rows `"parts.<part>.may_import"`, `"parts.<part>.must_import"`, `"parts.<part>.types_only"` with
the rows below, and the row `"parts.<part>.libraries"` with `"parts.<part>.imports.libraries"` (the same value):

```python
    "parts.<part>.imports.may": _IMPORTS,
    "parts.<part>.imports.must": (*_IMPORTS, "import.standard", "function.statements", "file", "file.package"),
    "parts.<part>.imports.may.types_only": _TYPES_ONLY,
```
```python
    "parts.<part>.imports.libraries": (*_IMPORTS, "import.standard"),
```

- [ ] **Step 5: Change the catalogue texts (`keys.yaml`), in the same commit**

In `xarch/architectures/presets/format/keys.yaml`:

1. Fragment `two` (line 24): replace `        may_import: [core]` with these two lines:

```yaml
        imports:
          may: [core]
```

2. `symbols` (lines 115, 118, 119): `"in may_import, a bare name: ..."` becomes `"in imports.may, a bare name: ..."`.
   `"in may_import, after ..."` becomes `"in imports.may, after ..."`. `everything: "in may_import or libraries: no limit"`
   becomes `everything: "in imports.may or imports.libraries: no limit"`.
3. `never` (line 163): "a part's `libraries`" becomes "a part's `imports.libraries`".
4. `reserved` (lines 182-183, 189): "the `libraries` check reads it ..., so a file of a part imports it only when the
   part's `libraries` lists it" becomes "... only when the part's `imports.libraries` lists it". The example's last line
   `          libraries: [json]` becomes the two lines `          imports:` and `            libraries: [json]`.
5. `layers` (line 193): "when a `may_import` breaks a chain" becomes "when an `imports.may` breaks a chain".
6. Replace the whole blocks `parts.<part>.may_import` (322-331), `parts.<part>.must_import` (332-342) and
   `parts.<part>.types_only` (343-352) with:

```yaml
  parts.<part>.imports:
    meaning: what the part may import, what each of its files must import one of, and its outside packages
    accepts: >-
      a map {may, must, libraries}, at least one of them, in any order: `may` the targets the part may import besides
      itself, `must` those each of its files imports one of, `libraries` the outside packages it may import. Without
      `imports`, or without `may`, the part imports only itself; without `libraries`, no outside package. `never`
      belongs to `uses`, beside `imports`
    example: |
      <<two>>
  parts.<part>.imports.may:
    meaning: what the part may import besides itself
    accepts: >-
      [<part>, <part>@any, <part>/<path>, <part>:<pattern>, {<target>: types_only}, ...] or everything: a bare name is
      that part in the importer's own instance (a part of another repeating folder has none: write `@any`), `@any` any
      instance, `/<path>` only what lies below it, `:<pattern>` only the names that match the pattern (`*` for any
      text, such as `core/ids:*Id`): `from <there> import <name>` for each name, never the file as a whole, and a file
      of the tests is not narrowed; an entry written `{<target>: types_only}` is a target the part may import only to
      use as a type (imports.may.types_only); a part may always import itself, so a target that only says so is refused
    example: |
      <<two>>
  parts.<part>.imports.may.types_only:
    meaning: a target of imports.may the part may use only as a type
    accepts: >-
      the mode of an entry of `imports.may`, written `{<target>: types_only}`, one target per entry, such as
      `[{core: types_only}]`: a file of the part may import what the entry reaches to annotate, and for `isinstance`
      and exception matching, but never call what it imports from there (`X(...)`, `m.X(...)`, `X.build(...)`) nor
      reference one of its top-level functions at all, read through every import, however written. The rule reads what
      the entry reaches, its part, instance and path; its name pattern narrows only what may be imported. A tier's
      `types_only` is the list form of the same idea, read on a test
    example: |
      parts:
        core:
          path: core
          role: the rules of the documents
        documents:
          path: documents
          role: the documents
          imports:
            may: [{core: types_only}]
  parts.<part>.imports.must:
    meaning: what each file of the part has to reach
    accepts: >-
      [<target>, ...] written as `imports.may` writes them, with no mode, each an entry of `imports.may`: each file
      imports one of them, or an outside package (top-level, neither standard library nor the app's own, whatever
      `imports.libraries` says), or imports a file of its own part that does, however far the chain; files that only
      import each other meet nothing. Exempt: `%package_file%` and a file with no function or method holding a real
      statement (types, constants, %interface% stubs). A failing file is reported once, as a whole
    example: |
      <<two>>
            must: [core]
  parts.<part>.imports.libraries:
    meaning: the outside packages the part may import
    accepts: >-
      [<package>, ...] by top-level name, or everything; none by default; the standard library is always allowed, but
      for a name `reserved` holds, which a part lists here to import it; tests are not checked
    example: |
      <<part>>
          imports:
            libraries: [yaml]
```

7. Delete the old `parts.<part>.libraries` block (lines 480-487).
8. `parts.<part>.uses.never` (line 528): "which `may_import` says" becomes "which `imports.may` says".
9. `tiers.<tier>.may_import` (line 612): "as a part's `may_import`" becomes "as a part's `imports.may`, with no mode".
   `tiers.<tier>.may_also_import` (line 624): "as a part's `may_import`" becomes "as a part's `imports.may`".
10. The `no-twins.translated` example (line 1074): `          may_import: [documents]` becomes `          imports: {may: [documents]}`.
11. `grep -nE "may_import|must_import|libraries|types_only" xarch/architectures/presets/format/keys.yaml`: every hit
    left must be a tier key, a `imports.*` address, or the word `libraries` under `imports`.

- [ ] **Step 6: Run the key table and catalogue tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_key_catalogue.py`
Expected: `test_profile_keys.py` PASS. If the catalogue test fails because the order of `catalogue.texts` differs
from `KEYS`, move the new blocks in `keys.yaml` until the order of addresses matches `[key.address for key in KEYS]`.

- [ ] **Step 7: Write the failing parser tests (`test_imports_written.py`)**

Create `tests/modules/spec/application/logic/test_imports_written.py`. It uses `layered()` from `tests/modules/spec/profiles.py`.
After Step 14, `layered()` writes `imports`. Write the tests now against the shape `layered()` will have; they fail
until the parser reads the group:

```python
"""A part's `imports` group, read by the parser: what it may import, each entry alone or marked types_only, what each
of its files must import one of, and its outside packages; every refusal of the group, of `may`'s marks and of
`must`, each at its address in fixed text."""
import pytest

from tests.modules.spec.profiles import layered, parsed, problems
from xarch.kernel.placement import EVERYTHING
from xarch.profile_values.placement import Target

USE = "use folders, holds, imports, litmus, package_only, path, role, shared, tests, untested, uses"
"""What every unknown-key problem of a part ends with."""


def with_imports(part: str, imports) -> dict:
    document = layered()
    document["parts"][part]["imports"] = imports
    return document


def test_the_group_gives_what_the_old_keys_gave_for_the_same_lists():
    architecture = parsed(with_imports("store", {"may": ["shared"], "must": ["shared"], "libraries": ["sqlmodel"]}))
    assert architecture.rules["store"] == (Target("shared"),)
    assert architecture.parts["store"].must_import == (Target("shared"),)
    assert architecture.libraries["store"] == ("sqlmodel",)


@pytest.mark.parametrize("imports, rules", [
    pytest.param({"may": "everything"}, (Target(EVERYTHING),), id="may everything"),
    pytest.param({"may": []}, (), id="may nothing"),
    pytest.param({"libraries": ["sqlmodel"]}, (), id="libraries alone"),
])
def test_what_may_allows(imports, rules):
    assert parsed(with_imports("store", imports)).rules["store"] == rules


def test_a_part_with_no_imports_imports_only_itself_and_no_outside_package():
    document = layered()
    del document["parts"]["store"]["imports"]
    architecture = parsed(document)
    assert architecture.rules["store"] == () and architecture.libraries["store"] == ()


@pytest.mark.parametrize("imports, problem", [
    pytest.param({}, "parts.store.imports: says nothing: write may, must or libraries, or drop it", id="empty"),
    pytest.param(["shared"], "parts.store.imports: must be a map of may, must and libraries, such as {may: [kernel]}",
                 id="a list"),
    pytest.param(True, "parts.store.imports: must be a map of may, must and libraries, such as {may: [kernel]}",
                 id="true"),
    pytest.param("shared", "parts.store.imports: must be a map of may, must and libraries, such as {may: [kernel]}",
                 id="a string"),
    pytest.param(None, "parts.store.imports: must be a map of may, must and libraries, such as {may: [kernel]}",
                 id="null"),
    pytest.param({"never": "pure"}, "parts.store.imports: unknown key 'never': a key of uses, beside imports: write "
                 "uses: {never: <list>}; use libraries, may, must", id="never"),
    pytest.param({"types_only": ["shared"]}, "parts.store.imports: unknown key 'types_only': write it as the mode of "
                 "its entry in imports.may, such as [{ports: types_only}]; use libraries, may, must", id="types_only"),
    pytest.param({"also": ["shared"]}, "parts.store.imports: unknown key 'also': use libraries, may, must", id="also"),
])
def test_the_group_is_refused_when_written_wrong(imports, problem):
    assert problems(with_imports("store", imports)) == [f"layered.yaml: {problem}"]


def test_a_marked_entry_is_a_target_of_may_and_a_marked_target():
    architecture = parsed(with_imports("service", {"may": ["store", {"shared": "types_only"}]}))
    assert architecture.rules["service"] == (Target("store", "own"), Target("shared"))
    assert architecture.parts["service"].types_only == (Target("shared"),)


@pytest.mark.parametrize("entry, marked", [
    pytest.param({"store": "types_only"}, Target("store", "own"), id="own instance"),
    pytest.param({"store@any": "types_only"}, Target("store", "any"), id="any instance"),
    pytest.param({"store/rules:*Id": "types_only"}, Target("store", "own", ("rules",), "*Id"), id="path and pattern"),
])
def test_a_mark_keeps_the_scope_path_and_pattern_of_its_target(entry, marked):
    assert parsed(with_imports("service", {"may": [entry]})).parts["service"].types_only == (marked,)


def test_two_marks_keep_the_order_of_may():
    architecture = parsed(with_imports("service", {"may": [{"store": "types_only"}, "api", {"shared": "types_only"}]}))
    assert architecture.parts["service"].types_only == (Target("store", "own"), Target("shared"))


def test_a_target_written_plain_and_marked_keeps_its_mark():
    architecture = parsed(with_imports("service", {"may": ["shared", {"shared": "types_only"}]}))
    assert architecture.parts["service"].types_only == (Target("shared"),)


@pytest.mark.parametrize("entry, problem", [
    pytest.param({"store": "types"}, "{store: types}: no mode 'types': write types_only, or the reference alone",
                 id="another word"),
    pytest.param({"store": True}, "{store: true}: no mode True: write types_only, or the reference alone",
                 id="true"),
    pytest.param({"store": "types_only", "shared": "types_only"},
                 "{store: types_only, shared: types_only}: one reference per entry: write each in its own {...}",
                 id="two targets"),
    pytest.param({}, "{}: one reference per entry: write each in its own {...}", id="an empty map"),
    pytest.param({"everything": "types_only"}, "everything takes no mode: list the entries to give one a mode",
                 id="everything"),
    pytest.param({"repo": "types_only"}, "'repo' names no part 'repo'", id="an undeclared part"),
    pytest.param({3: "types_only"}, "3 is not a target: use <part>, <part>@any, optionally followed by /<path>",
                 id="no target"),
])
def test_a_mark_written_wrong_is_refused_at_may(entry, problem):
    assert problems(with_imports("service", {"may": [entry]})) == [f"layered.yaml: parts.service.imports.may: {problem}"]


@pytest.mark.parametrize("must, problem", [
    pytest.param([], "must be a list of targets such as [<part>, <part>@any]", id="empty"),
    pytest.param("shared", "must be a list of targets such as [<part>, <part>@any]", id="no list"),
    pytest.param([{"shared": "types_only"}], "{shared: types_only}: must takes references only, with no mode",
                 id="a mode"),
    pytest.param(["api"], "'api' is not in imports.may, so no file could import it: add it there, or name a part the "
                 "part may import", id="not in may"),
])
def test_must_is_refused_when_written_wrong(must, problem):
    document = with_imports("store", {"may": ["shared"], "must": must})
    assert problems(document) == [f"layered.yaml: parts.store.imports.must: {problem}"]


def test_a_must_entry_equal_to_a_marked_entry_of_may_passes():
    architecture = parsed(with_imports("store", {"may": [{"shared": "types_only"}], "must": ["shared"]}))
    assert architecture.parts["store"].must_import == (Target("shared"),)


def test_must_without_may_is_refused_entry_by_entry():
    assert problems(with_imports("store", {"must": ["shared"]})) == [
        "layered.yaml: parts.store.imports.must: 'shared' is not in imports.may, so no file could import it: add it "
        "there, or name a part the part may import"]


@pytest.mark.parametrize("key, text", [
    pytest.param("may_import", "moved in 0.3.0: write imports: {may: [...]}", id="may_import"),
    pytest.param("must_import", "moved in 0.3.0: write imports: {must: [...]}", id="must_import"),
    pytest.param("libraries", "moved in 0.3.0: write imports: {libraries: [...]}", id="libraries"),
    pytest.param("types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                 "[{ports: types_only}]", id="types_only"),
])
def test_each_old_key_of_a_part_is_refused_with_the_form_that_replaces_it(key, text):
    document = layered()
    document["parts"]["shared"][key] = ["api"]
    assert problems(document) == [f"layered.yaml: parts.shared: unknown key {key!r}: {text}; {USE}"]


def test_old_keys_written_together_give_one_problem_each_in_sorted_order():
    document = layered()
    document["parts"]["shared"] |= {"may_import": ["api"], "types_only": ["api"], "libraries": ["yaml"]}
    assert [problem.split(": unknown key ")[1].split("'")[1] for problem in problems(document)] == [
        "libraries", "may_import", "types_only"]


def test_a_retired_key_beside_the_group_is_its_own_problem_and_the_group_is_still_read():
    document = with_imports("store", {"may": ["repo"]})
    document["parts"]["store"]["may_import"] = ["shared"]
    assert problems(document) == [
        f"layered.yaml: parts.store: unknown key 'may_import': moved in 0.3.0: write imports: {{may: [...]}}; {USE}",
        "layered.yaml: parts.store.imports.may: 'repo' names no part 'repo'"]


def test_a_standard_library_name_in_libraries_is_refused_at_imports_libraries():
    document = with_imports("store", {"may": ["shared"], "libraries": ["json"]})
    assert problems(document) == [
        "layered.yaml: parts.store.imports.libraries: 'json' is in the standard library, which every part may import "
        "unless `reserved` names it"]
```

Then check two things against today's code, with `grep -n "_named_packages\|named" xarch/modules/spec/application/logic/never_lists.py`.
First, how a `never` list named like a package says its first-naming place. Second, which test of
`test_profile_parsing.py` or `test_never_use.py` pins that text today (`grep -n "parts\.[a-z]*\.libraries" tests/modules/spec/application/logic/test_never_use.py`).
Change that expected text from `parts.<p>.libraries` to `parts.<p>.imports.libraries` (spec test 8). Also add this test
next to the others, for the risk of spec 6 (`_named_packages` reads a raw document):

```python
def test_a_never_list_beside_imports_written_as_no_map_names_no_package_and_says_nothing_of_it():
    document = with_imports("store", True)
    document["never"] = {"pure": ["time.time"]}
    document["parts"]["service"]["uses"] = {"never": "pure"}
    assert problems(document) == [
        "layered.yaml: parts.store.imports: must be a map of may, must and libraries, such as {may: [kernel]}"]
```

- [ ] **Step 8: Run them to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_imports_written.py`
Expected: FAIL. The parser does not know `imports` yet (`unknown key 'imports'`, or a `KeyError` on `rules`).

- [ ] **Step 9: Write the parser of the group**

Create `xarch/modules/spec/application/logic/imports_written.py`:

```python
"""What a part's `imports` says: what it may import, what each of its files must import one of, and the outside
packages it may import, in one group.

    imports: {may: [<target> | {<target>: types_only}, ...] | everything, must: [<target>, ...],
              libraries: [<package>, ...] | everything}

An entry of `may` is a target as the target grammar writes it (see kernel/logic/targets), or a map of one target to its
mode; the only mode is `types_only`, a target the part may import only to use as a type. A marked entry is an entry of
`may` like any other, its mark read apart. `must` takes targets alone, each one an entry of `may`. The old keys of a
part, and `never` and `types_only` written in the group, are refused from the table of retired names.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.application.logic.targets_written import WORD, may_import
from xarch.modules.spec.domain.profile_keys import PART_IMPORTS
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Target

MODE = "types_only"
"""The one mode an entry of `may` takes."""


def group(spec: Mapping[Any, Any], where: str, problems: list[str]) -> Mapping[Any, Any]:
    """The `imports` of the part at where: {} when the part writes none, or when it is no map or says nothing, each
    problem added; its unknown keys are refused under its own scope."""
    if "imports" not in spec:
        return {}
    value, at = spec["imports"], f"{where}.imports"
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a map of may, must and libraries, such as {{may: [kernel]}}")
        return {}
    if not value:
        problems.append(f"{at}: says nothing: write may, must or libraries, or drop it")
        return {}
    problems += ck.unknown_keys(value, names_of(PART_IMPORTS), at, PART_IMPORTS)
    return value


def may(value: Any, owner: Part, parts: dict[str, Part], declared: set[str], where: str,
        problems: list[str]) -> tuple[tuple[Target, ...], tuple[Target, ...]]:
    """What the part may import, every entry as its target, marked or not, in the order written; and the targets of
    its marked entries, in the same order. An entry refused adds its problem and is in neither."""
    if not isinstance(value, list):
        return may_import(value, owner, parts, declared, where, problems, patterns=True), ()
    allowed: list[Target] = []
    marked: list[Target] = []
    for entry in value:
        written = _marked(entry, where, problems) if isinstance(entry, Mapping) else entry
        if written is None:
            continue
        found = may_import([written], owner, parts, declared, where, problems, patterns=True)
        allowed += found
        if isinstance(entry, Mapping):
            marked += found
    return tuple(allowed), tuple(marked)


def must(written: Mapping[Any, Any], owner: Part, parts: dict[str, Part], declared: set[str],
         allowed: tuple[Target, ...], problems: list[str]) -> tuple[Target, ...]:
    """The targets each file of the part must import one of: each one an entry of `may` (allowed), marked or not."""
    where = f"parts.{owner.name}.imports.must"
    if "must" not in written:
        return ()
    value = written["must"]
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of targets such as [<part>, <part>@any]")
        return ()
    count = len(problems)
    problems += [f"{where}: {_shown(item)}: must takes references only, with no mode" for item in value
                 if isinstance(item, Mapping)]
    found = may_import(value, owner, parts, declared, where, problems) if len(problems) == count else ()
    if len(problems) != count:
        return ()
    for item, target in zip(value, found):
        if not any(t.part == EVERYTHING or t == target for t in allowed):
            problems.append(f"{where}: {item!r} is not in imports.may, so no file could import it: add it there, or "
                            "name a part the part may import")
    return found if len(problems) == count else ()


def _marked(entry: Mapping[Any, Any], where: str, problems: list[str]) -> Any:
    """The target a marked entry of `may` writes; None, with its problem, when the entry is no map of one target to
    the mode."""
    if len(entry) != 1:
        problems.append(f"{where}: {_shown(entry)}: one reference per entry: write each in its own {{...}}")
        return None
    ((target, mode),) = entry.items()
    if target == WORD:
        problems.append(f"{where}: {WORD} takes no mode: list the entries to give one a mode")
        return None
    if mode != MODE:
        problems.append(f"{where}: {_shown(entry)}: no mode {mode!r}: write {MODE}, or the reference alone")
        return None
    return target


def _shown(entry: Mapping[Any, Any]) -> str:
    """A map entry as a profile writes it, in flow style: {ports: types_only}."""
    return "{" + ", ".join(f"{_scalar(key)}: {_scalar(value)}" for key, value in entry.items()) + "}"


def _scalar(value: Any) -> str:
    """A value as a profile writes it: true, false and null in their own words."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return "null" if value is None else str(value)
```

Note on `may`: an entry written `everything` inside a list reaches `may_import([WORD])`, which keeps today's
"'everything' stands alone" refusal. A target that is not a string reaches the target grammar, which says
"... is not a target".

- [ ] **Step 10: Read the group in the parser**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

1. Import it: `from xarch.modules.spec.application.logic import imports_written as iw` (next to the other
   `from xarch.modules.spec.application.logic import ... as ...` lines).
2. In `parse_profile`, replace the lines from `rules = {part: may_import(...` through the `_substance` line
   (lines 185-193) with:

```python
    imports = {part: iw.group(specs[part], f"parts.{part}", problems) for part in parts}
    read = {part: iw.may(imports[part].get("may"), item, parts, declared, f"parts.{part}.imports.may", problems)
            for part, item in parts.items()}
    rules = {part: allowed for part, (allowed, _) in read.items()}
    reserved = ck.reserved_modules(document["reserved"], problems, language) if "reserved" in document else {}
    libraries = {part: _libraries(imports[part], f"parts.{part}.imports.libraries", problems, language, reserved)
                 for part in parts}
    parts = {part: replace(item, must_import=iw.must(imports[part], item, parts, declared, rules[part], problems),
                           types_only=read[part][1]) for part, item in parts.items()}
    parts = {part: _substance(specs[part], item, declared, problems) for part, item in parts.items()}
```

3. `_libraries` keeps its body; its first parameter now receives the group. Rename the parameter `spec` to `written`
   and update its docstring: "The outside packages the part's `imports` group lists, and the reserved modules it may
   import: ...".
4. `_named_packages` (lines 459-470) becomes:

```python
def _named_packages(document: Mapping[Any, Any], language: Language) -> dict[str, str]:
    """Each package the profile names, by the key of the first place naming it: the parts' `imports.libraries` in the
    order the file writes them, then `reserved`. Read silently, and only from an `imports` that is a map: each is said
    at its own place."""
    reserved = ck.reserved_modules(document["reserved"], [], language) if "reserved" in document else {}
    parts = document.get("parts")
    named: dict[str, str] = {}
    for part, spec in parts.items() if isinstance(parts, Mapping) else ():
        written = spec.get("imports") if isinstance(spec, Mapping) else None
        found = (_libraries(written, f"parts.{part}.imports.libraries", [], language, reserved)
                 if isinstance(written, Mapping) else ())
        named |= {package: f"parts.{part}.imports.libraries" for package in found
                  if package != EVERYTHING and package not in named}
    named |= {module: "reserved" for module in reserved if module not in named}
    return named
```

5. `_substance` drops `types_only` and its `may_import` parameter:

```python
def _substance(spec: Any, part: Part, declared: set[str], problems: list[str]) -> Part:
    """The keys of a part that say what its code holds and how it is used: holds, with the settings of each kind it
    lists (see holds_written), and shared."""
    where = f"parts.{part.name}"
    if not isinstance(spec, Mapping):
        return part
    holds = held_kinds(spec["holds"], where, declared, problems) if "holds" in spec else ()
    shared = spec.get("shared")
    if shared is not None and not _whole(shared, 2):
        problems.append(f"{where}.shared: must be a whole number of users, at least 2, such as 2; leave it out for a "
                        "part that is not there to be shared")
        shared = None
    return replace(part, holds=holds, shared=shared)
```

6. Delete `_must_import` (lines 933-951). Its body now lives in `imports_written.must`.
7. The module docstring (lines 19-22) becomes:

```
        imports: {may, must, libraries}
                               what the part may import besides itself, which it always may: each entry a target
                               (a bare name of a part in the repeating folder is the importer's own instance, `@any`
                               any instance, `/<path>` below it) or one marked {<target>: types_only}, or everything;
                               the targets each file must import one of; the outside packages by top-level import
                               name, none unless listed, everything leaving the part unchecked (see imports_written)
```

   and line 36's "only the parts whose `libraries` list them" becomes "only the parts whose `imports.libraries` list them".
8. Remove the now unused imports that ruff reports (`EVERYTHING`, `may_import`, `Target` if no longer used).

- [ ] **Step 11: Carry the marked targets**

In `xarch/modules/spec/domain/values.py`, `Part`: the field becomes `types_only: tuple[Target, ...] = ()`. The docstring
line becomes `types_only: the targets of its imports.may marked types_only, in the order of may: its files may import
what they reach and use it as types, but never call it`. In `xarch/modules/spec/contract/__init__.py`, `PartView`:
`types_only: tuple[Target, ...] = ()`, and the docstring's "the parts it may use as types only" becomes "the targets
it may use as types only". `xarch/modules/spec/application/services/publishing.py:61` needs no change.

In `xarch/modules/rules/adapters/spec_profile.py:80`, bridge to the old shape until Task 3:

```python
                       types_only={p.name: tuple(dict.fromkeys(t.part for t in p.types_only)) for p in parts
                                   if p.types_only},
```

In `tests/modules/rules/adapters/test_spec_profile.py:49`, the `VIEW`'s part `api` now carries targets,
`types_only=(Target("core"),)`. The expected `Profile` of `test_the_profile_view_becomes_the_profile_the_checks_see`
keeps `types_only={"api": ("core",)}` in this task: that is the bridge.

In `xarch/modules/spec/application/logic/docs_template.py:566-568` (`_part_lines`):

```python
        if part.types_only:
            lines.append(f"`types-only`: {shown([part.name])} uses "
                         f"{shown(list(dict.fromkeys(t.part for t in part.types_only)))} only as a type: it "
                         "imports it to annotate and never calls it.")
```

- [ ] **Step 12: Let the needs walker read the mark**

In `xarch/modules/spec/application/logic/profile_needs.py`, `_held`'s last branch:

```python
    else:
        entries = [(address, _modes(value) if isinstance(value, list) else value)]
```

and add below `_held`:

```python
def _modes(entries: list[Any]) -> dict[str, bool]:
    """A list whose entries are each a value or a one-key map of a value to its mode (imports.may), as the map of the
    modes its entries carry, each set: the keys of the scope it opens are its modes."""
    return {mode: True for entry in entries if isinstance(entry, Mapping) for mode in entry.values()
            if isinstance(mode, str)}
```

Also add to the module docstring, after "addressed by its index from 0 (<list>.0.<key>).": " A list of entries each a
target or a map of one to its mode (imports.may) holds the scope of its modes: a mode an entry carries is set."

In `tests/modules/spec/application/logic/test_profile_needs.py`, add these tests. They use the file's own `TOY`
language, which supplies `file`, `import`, `import.relative`, `import.standard`, `class` (partly) and `public`, but
not `call`, `use`, `module_functions` or `import.resolved`. They also use its `services(**keys)` builder, which
replaces keys of the part `service` of `layered(language="toy")`:

```python
def test_a_mark_needs_what_types_only_reads_at_its_address():
    document = services(imports={"may": ["store", {"shared": "types_only"}]})
    assert [(item.address, item.fact) for item in short(document, {}, TOY)] == [
        ("parts.service.imports.may.types_only", fact) for fact in ("call", "use", "module_functions",
                                                                    "import.resolved")]


@pytest.mark.parametrize("may", [
    pytest.param(["store", "shared"], id="no mark"),
    pytest.param("everything", id="everything"),
    pytest.param(["store", {"shared": "types"}], id="a mode refused"),
])
def test_a_may_with_no_mark_needs_nothing_of_types_only(may):
    assert short(services(imports={"may": may}), {}, TOY) == []


def test_must_and_libraries_fall_short_at_their_new_addresses():
    no_standard = replace(TOY, checked=replace(TOY.checked, supplies=tuple(
        supply for supply in TOY.checked.supplies if supply.fact != "import.standard")))
    document = layered(language="toy")
    document["parts"]["store"]["imports"]["must"] = ["shared"]
    found = {(item.address, item.fact) for item in short(document, {}, no_standard)}
    assert {("parts.store.imports.must", "import.standard"),
            ("parts.store.imports.libraries", "import.standard")} <= found
```

(`layered()`'s `store` writes `imports: {may: [shared], libraries: [sqlmodel]}` after Step 14.)

- [ ] **Step 13: Key the rules and their texts by the new addresses**

`xarch/modules/rules/application/logic/expansion.py`:
- `_libraries`: `key=f"parts.{part}.imports.libraries"`. In `owners`, `(parts.{first_library_owner}.libraries)`
  becomes `(parts.{first_library_owner}.imports.libraries)`. In the docstring, "its `libraries` list" becomes "its
  `imports.libraries` lists".
- `_rules`: `key=f"parts.{part}.imports.may"`. In the docstring, "its `may_import` row" becomes "its `imports.may`".
- `_types_only_parts`: `f"parts.{part}.imports.may.types_only"`. Its docstring: "A file of a part whose `imports.may`
  marks entries types_only is held to the same rule."
- `_must_import`: `key=f"parts.{part}.imports.must"`. In the docstring, "`must_import`" becomes "`imports.must`".
- `KEYS`: replace `"parts.may_import"` with `"parts.imports.may"`, `"parts.libraries"` with `"parts.imports.libraries"`,
  `"parts.types_only"` with `"parts.imports.may.types_only"`, and `"parts.must_import"` with `"parts.imports.must"`,
  each in its place.

`xarch/modules/rules/application/logic/sentences.py:146`: `parts = ", ".join(f"parts.{p}.imports.may" for p in found.read.mirrors)`.

`xarch/modules/rules/domain/vocabulary.py`. Change only the prose quoted here; names of variables and filters stay:
- line 35: "places written as `may_import` writes them" becomes "places written as an entry of `imports.may` writes a
  target".
- line 259: "(`may_import: everything`)" becomes "(`imports: {may: everything}`)".
- line 267: "is in the `libraries` of a part other" becomes "is in the `imports.libraries` of a part other".
- line 307: "pattern of its `may_import` allows" becomes "pattern of its `imports.may` allows".
- line 334: "`may_import` writes a target without a name pattern" becomes "an entry of `imports.may` writes a target,
  with no name pattern and no mode".
- lines 372-374 (`mirrored_may_import`): "parts.store.may_import; tiers.unit.may_also_import" becomes
  "parts.store.imports.may; tiers.unit.may_also_import". Change any other `may_import` in that description that
  names the part key.
- line 392: "whose `libraries` list" becomes "whose `imports.libraries` list".
- line 406: "its `may_import`" becomes "its `imports.may`".

Spec module texts:
- `example_imports.py:68`: `f"(parts.{source.part}.imports.may)"`. Line 6: "in the importer's `may_import`" becomes
  "in the importer's `imports.may`".
- `profile_checks.py:601`: "whose `libraries` list it already" becomes "whose `imports.libraries` list it already".
- `key_lookup.py:13-14`: "parts.<part>.may_import being parts.may_import" becomes "parts.<part>.imports.may being
  parts.imports.may".
- `xarch/cli/commands/profile.py:66`: "such as parts, parts.may_import, guards.no-duplicates" becomes "such as parts,
  parts.imports.may, guards.no-duplicates".
- `xarch/cli/reports/profile_report.py:44`: the first line of `DEEPER` becomes
  `"xarch profile explain parts.imports.may       one key in full: what it accepts, its rule, an example\n"` (seven
  spaces after the key, so the column stays where the other lines have it).

`tests/bootstrap/test_bundled_imports.py`: `KEYS = {"may": "parts.imports.may", "must": "parts.imports.must",
"libraries": "parts.imports.libraries"}`. Change nothing else in it.

`profile explain` answers a key typed with a part's or a tier's name in it (spec 2.4: `parts.adapters.imports.may`).
Today `key_at` (`xarch/modules/spec/application/logic/explain.py`) knows only the plain address. Add to
`tests/modules/spec/application/test_explain.py`, beside the tests that call its `explained(address)` helper:

```python
@pytest.mark.parametrize("address, key", [
    pytest.param("parts.adapters.imports.may", "parts.imports.may", id="may on a part"),
    pytest.param("parts.adapters.imports", "parts.imports", id="the group on a part"),
    pytest.param("parts.services.imports.may.types_only", "parts.imports.may.types_only", id="the mark on a part"),
    pytest.param("parts.imports.must", "parts.imports.must", id="must, plain"),
    pytest.param("parts.uses.never", "parts.uses.never", id="a key whose second step is a key of the part"),
])
def test_a_key_is_explained_typed_plain_or_with_the_part_it_sits_on(address, key):
    assert explained(address).key == key
```

and in `explain.py`:

```python
def key_at(address: str) -> Key | None:
    """The key at the address as typed: a key by its plain address, or with the name of a part or a tier in its second
    step (parts.adapters.imports.may), or a slot of an entry of a map of ids written with any id in the id's step
    (evals.title-rule.ask) or with the placeholder itself (evals.<id>.ask)."""
    typed = cleaned(address)
    written = address.strip().strip(".")
    found = next((key for key in KEYS if plain(key.address) == typed), None)
    found = found or next((key for key in KEYS if plain(key.address) == _unnamed(typed)), None)
    return found or next((slot for slot in SLOTS if written == slot.address or of_an_entry(typed, slot.scope, slot.name)), None)


def _unnamed(typed: str) -> str:
    """A typed address of a key of a part or a tier with the name of the one it sits on left out (parts.adapters.imports
    as parts.imports); the address itself when its second step is a key of a part or a tier, or it has no third."""
    steps = typed.split(".")
    scope = {"parts": PART, "tiers": TIER}.get(steps[0])
    if scope is None or len(steps) < 3 or steps[1] in names_of(scope):
        return typed
    return ".".join((steps[0], *steps[2:]))
```

(import `PART`, `TIER` from `profile_keys` and `names_of` from `key_lookup` if `explain.py` does not yet). Run
`timeout 300 uv run pytest -q tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py`.
If a test there pins the refusal of a part-qualified address as "no key", it contradicts spec 2.4. Change it to the
answer, and name it in the commit message.

- [ ] **Step 14: Rewrite every profile and inline test profile for the group**

The rule, for every part (never a tier) that writes any of the four keys:
- `may_import: X`, `must_import: Y`, `libraries: Z` become one key `imports: {may: X, must: Y, libraries: Z}`. Keep
  only the keys the part wrote, in the order `may`, `must`, `libraries`, at the place the first of them stood. Keep
  flow (`[a, b]`) or block (`- a`) style as written. In a block-style file such as `stress.yaml`, write
  `imports:` with `may:`, `must:`, `libraries:` nested two spaces deeper, and their list items two spaces deeper still.
- `may_import: everything` becomes `imports: {may: everything}`, and `libraries: everything` becomes
  `libraries: everything` under `imports`.
- A part's `types_only: [a, b]` goes away. Each of `a`, `b` is written in `may` as `{a: types_only}` in place of its
  plain entry `a`.
- Python dict profiles: `"may_import": [...]` becomes `"imports": {"may": [...]}`, merged as above. A mutation
  `document["parts"][p]["may_import"] = v` becomes `document["parts"][p].setdefault("imports", {})["may"] = v`, and the
  same for `"must"`/`"libraries"`. A `del ...["libraries"]` becomes `del ...["imports"]["libraries"]`, and the whole
  `imports` is dropped when nothing is left in it.
- Expected texts: `parts.<p>.may_import` becomes `parts.<p>.imports.may`, and the same for `must_import` (`.imports.must`),
  `libraries` (`.imports.libraries`) and `types_only` (`.imports.may.types_only`). "is not in `may_import`, so no file
  could import it" becomes "is not in imports.may, so no file could import it". The "use ..." list of a part becomes
  `use folders, holds, imports, litmus, package_only, path, role, shared, tests, untested, uses`.
- Tier keys and their texts (`tiers.<t>.may_import`, `.may_also_import`, `.must_import`, `.types_only`) are not
  touched. Python identifiers (`may_import=` keyword arguments of `Profile`, `PartView`, `CheckedTier`, the function
  `may_import`) are not touched.

The profiles, by hand, each checked with `uv run xarch profile check <file>` after the edit:
- `architecture.yaml` (parts at lines 21-205; the tier lines 266-291 stay). For example, adapters:

```yaml
    imports:
      may: [ports, domain, kernel, kernel-logic, profile-values, platform, contract@any]
      must: [platform, contract@any]
      libraries: [ast, tokenize]
```
  and bootstrap `imports: {may: everything}`.
- `xarch/architectures/cli.yaml` and `web.yaml` (part lines 19-259; line 244/246 `types_only: [controller]` is a
  tier's and stays). The bootstrap part becomes:

```yaml
    imports:
      may: everything
      libraries: [sqlmodel, typer]
```
- `tests/bootstrap/corpora/7cc6111.yaml` and `df537ca.yaml`. services (line 36, `types_only: [contract]`) becomes:

```yaml
    imports:
      may: [logic, domain, ports, {contract: types_only}, kernel]
```
- `tests/bootstrap/corpora/stress.yaml`, block style. services (lines 38-50):

```yaml
    imports:
      may:
      - logic
      - domain
      - ports
      - {contract: types_only}
      - kernel
      must:
      - ports
```
  Here `holds`, `uses` and `tests` stay where they were, and the old `types_only`/`must_import` lines go. adapters (lines
  67-83): `may` with `- {domain: types_only}` in place of `- domain`, `must` and `libraries` under the same `imports`,
  and the `types_only:` at line 81 gone. `reports` (line 117) `libraries: []` becomes `libraries: []` under its
  `imports`. The tier lines 211, 228, 244 stay.

The inline test profiles: list them with

```bash
git grep -nE '"(may_import|must_import|libraries|types_only)"|\b(may_import|must_import|libraries|types_only):' -- tests docs/examples
```

and rewrite each hit that sits on a part by the rule above. That covers, among others, `tests/modules/spec/profiles.py`
(`layered`, `two_folders`), `tests/modules/spec/application/builders.py`, `tests/modules/spec/application/origins.py`,
`tests/bootstrap/test_needs_agree.py` (`EVERY_KEY`, spec test 21: `core` becomes
`imports: {may: [{api: types_only}], must: [api], libraries: [yaml]}` and its `types_only:` line goes), the YAML strings
of `tests/bootstrap/test_*.py`, and `docs/examples/**` profiles. `tests/architecture/test_language_seam.py:491` is a
docstring fed to the seam check, not a profile: leave it unless its test fails. Then list the expected texts with

```bash
git grep -nE 'parts\.[a-z<>{}_-]+\.(may_import|must_import|libraries|types_only)\b' -- tests
```

and change each one, as the rule says. In `test_profile_parsing.py`, line 164-165's `use ...` list becomes the new
one. Delete the test that holds `parts.<p>.types_only: '<name>' is not in may_import ...` (spec 2.3: gone with no
replacement). Find it with `git grep -n "to use as a type: add it there" tests`.

In `tests/modules/spec/application/logic/test_targets_written.py`, add (spec test 6):

```python
def test_a_tier_folder_s_may_import_refuses_a_marked_entry_as_any_entry_that_is_no_target():
    problems: list[str] = []
    assert may_import([{"shared": "types_only"}], None, PARTS, {"shared"}, "tiers.guard.may_import", problems) == ()
    assert problems == ["tiers.guard.may_import: {'shared': 'types_only'} is not a target: use <part>, <part>@any, "
                        "optionally followed by /<path>"]
```

(use the `PARTS` the file already builds; check with `grep -n "^[A-Z_]* = \|^def " tests/modules/spec/application/logic/test_targets_written.py`).

In `tests/modules/spec/application/logic/test_retired_keys.py`, add to the parametrize of
`test_the_shipped_table_answers_each_name_in_its_scope` (and import `PART_IMPORTS`, `PART_IMPORTS_MAY`):

```python
    pytest.param(PART, "may_import", "moved in 0.3.0: write imports: {may: [...]}", id="the part key may_import"),
    pytest.param(PART, "must_import", "moved in 0.3.0: write imports: {must: [...]}", id="the part key must_import"),
    pytest.param(PART, "libraries", "moved in 0.3.0: write imports: {libraries: [...]}", id="the part key libraries"),
    pytest.param(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                 "[{ports: types_only}]", id="the part key types_only"),
    pytest.param(PART_IMPORTS, "never", "a key of uses, beside imports: write uses: {never: <list>}",
                 id="never in imports"),
    pytest.param(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                 "[{ports: types_only}]", id="types_only in imports"),
    pytest.param(TIER, "types_only", "", id="the tier key types_only, a key"),
    pytest.param(TIER, "may_import", "", id="the tier key may_import, a key"),
    pytest.param(PART_IMPORTS_MAY, "types_only", "", id="the mark, a key"),
```

and to `test_the_shipped_table_answers_each_address_profile_explain_is_typed_with`:

```python
    pytest.param("parts.may_import", "moved in 0.3.0: write imports: {may: [...]}", id="parts.may_import"),
    pytest.param("parts.<part>.types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such "
                 "as [{ports: types_only}]", id="parts.<part>.types_only"),
    pytest.param("parts.imports.may.types_only", "", id="parts.imports.may.types_only"),
    pytest.param("tiers.types_only", "", id="tiers.types_only"),
```

In `tests/bootstrap/test_profile_explain.py`, add (spec test 17; reuse the file's runner and JSON helper, which you can
see with `grep -n "^def \|^runner" tests/bootstrap/test_profile_explain.py`):

```python
def test_the_mark_is_a_key_with_its_text_and_its_rule():
    found = runner.invoke(app, ["profile", "explain", "parts.imports.may.types_only", "--format", "json"])
    shown = json.loads(found.output)
    assert found.exit_code == 0 and shown["key"] == "parts.imports.may.types_only"
    assert shown["meaning"] == "a target of imports.may the part may use only as a type"


def test_an_old_part_key_answers_with_the_form_that_replaces_it():
    found = runner.invoke(app, ["profile", "explain", "parts.may_import"])
    assert "moved in 0.3.0: write imports: {may: [...]}" in found.output
```

Before you fix the exit code of the second test, read how the file tests `parts.immutable` (a retired key) with
`grep -n "immutable" tests/bootstrap/test_profile_explain.py`. Assert the same exit code it asserts there (spec:
"exit codes as today"). If the JSON keys differ from `key`/`meaning`, use the ones the file's other tests read.

In `tests/modules/rules/application/logic/test_expandable.py` (or `test_explained.py`), add (spec test 14):

```python
def test_the_keys_of_the_group_are_expanded_and_the_old_part_keys_are_not():
    assert all(expands(key) for key in ("parts.imports.may", "parts.imports.must", "parts.imports.libraries",
                                        "parts.imports.may.types_only", "parts.services.imports.may.types_only"))
    assert not any(expands(key) for key in ("parts.may_import", "parts.must_import", "parts.libraries",
                                            "parts.types_only"))
    assert expands("tiers.types_only") and expands("tiers.must_import")
```

and, in `test_explained.py`, that `keyed(book_rules, "parts.imports.may")` lists only rules of id `may-import`. Use the
file's own way of building the book's rules for a profile with a marked part. Check it with
`grep -n "keyed(" tests/modules/rules/application/logic/test_explained.py`.

- [ ] **Step 15: Edit the recorded findings, anchored on `parts.<p>.`**

```bash
cd tests/bootstrap/corpora
xz -dc stress-7cc6111.json.xz > /tmp/stress-before.json
cp /tmp/stress-before.json /tmp/stress-after.json
cp 7cc6111.json /tmp/7cc6111-before.json; cp df537ca.json /tmp/df537ca-before.json
perl -pi -e 's/(?<![\w.])parts\.([A-Za-z0-9_-]+)\.may_import\b/parts.$1.imports.may/g;
             s/(?<![\w.])parts\.([A-Za-z0-9_-]+)\.must_import\b/parts.$1.imports.must/g;
             s/(?<![\w.])parts\.([A-Za-z0-9_-]+)\.libraries\b/parts.$1.imports.libraries/g;
             s/(?<![\w.])parts\.([A-Za-z0-9_-]+)\.types_only\b/parts.$1.imports.may.types_only/g' \
     7cc6111.json df537ca.json /tmp/stress-after.json
xz -9 -c /tmp/stress-after.json > stress-7cc6111.json.xz
for pair in "/tmp/7cc6111-before.json 7cc6111.json" "/tmp/df537ca-before.json df537ca.json" "/tmp/stress-before.json /tmp/stress-after.json"; do
  set -- $pair; echo "$2 $(diff $1 $2 | grep -c '^<') $(diff $1 $2 | grep -c '^>')"; done
cd -
```

Expected: `7cc6111.json 58 58`, `df537ca.json 2 2`, `/tmp/stress-after.json 117 117`. Then read each diff
(`diff /tmp/stress-before.json /tmp/stress-after.json | less`). Every changed line must differ only by the key
inside parentheses: 31 `(parts.<p>.imports.may)`, 27 `(parts.services.imports.may.types_only)` in 7cc6111; 2
`imports.libraries` in df537ca; 31 `imports.may`, 67 `imports.may.types_only` and 19 `imports.libraries` in stress.
Check that `tiers.<t>.types_only` (694 lines of stress), `tiers.<t>.must_import`, `tiers.<t>.may_also_import` and the
module `xarch.modules.rules.application.logic.must_import`/`.libraries` lines are untouched:
`diff /tmp/stress-before.json /tmp/stress-after.json | grep -E 'tiers\.|application\.logic\.(must_import|libraries)'`
must print only lines that also hold a changed `parts.` key. The recorded counts in `test_recorded_corpora.py`'s
docstring do not change.

- [ ] **Step 16: Run the spec, rules and wired tests of this task**

Run: `timeout 900 uv run pytest -q tests/modules/spec tests/modules/rules tests/bootstrap/test_bundled_imports.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_docs_templates.py`
Expected: PASS. `test_bundled_imports.py` passes with only `KEYS` changed: the bundled profiles import what they
imported. `test_docs_templates.py` passes with no doc regenerated (no template text changed yet). On a failure, read
it: an expected text still on an old key is Step 14's to change. A where or rules hash that differs is a defect of the
profile rewrite; fix the profile, never the literal.

- [ ] **Step 17: Run the whole suite and the gates**

Run: `timeout 900 uv run pytest -q > /tmp/xarch-45-t2.log 2>&1; echo EXIT $?; tail -5 /tmp/xarch-45-t2.log` (in the background), then
`uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: `EXIT 0`; "All checks passed!"; both checks exit 0; "OK: the profile is valid". Fix each failure by the rule
of Step 14.

- [ ] **Step 18: Commit**

```bash
git add xarch tests architecture.yaml docs/examples
git status --short   # nothing under .claude/, nothing else left unstaged
git commit -m "A part's may_import, must_import and libraries move into one imports group, {may, must, libraries}, and its types_only becomes the mark {<target>: types_only} on an entry of imports.may, read into the targets Part.types_only carries; the old part keys, and never or types_only written in the group, are refused with the form that replaces them from the table of retired names, and a mark, a must and the group written wrong each in fixed text; the key table opens parts.<part>.imports and parts.<part>.imports.may, whose one key is the mark, with the facts the old keys needed, the needs walker reading the modes of may's entries; rules and findings are keyed by the new addresses, rules reading the marks as part names through the adapter until they read what each reaches; every profile and test profile writes the group, and the recorded corpora change by anchored replace in the lines that named a part's import key"
```

---

### Task 3: The types-only rule reads what a marked entry reaches

Spec: 2.2 (the rule reads what the entry reaches; `_caller_fix`), 2.6 (`Profile.types_only` targets; `Match("place")`
with patterns dropped); risk 2; tests 12, 15 (fix half), adapter test.

**Files:**
- Modify: `xarch/modules/rules/domain/profile.py:65,108`
- Modify: `xarch/modules/rules/adapters/spec_profile.py:80` (bridge goes)
- Modify: `xarch/modules/rules/application/logic/expansion.py:135-155`
- Modify: `xarch/modules/rules/application/logic/sentences.py:162-170`
- Test: `tests/modules/rules/application/logic/test_types_only.py`, `tests/modules/rules/application/logic/test_sentences.py`, `tests/modules/rules/adapters/test_spec_profile.py`

**Interfaces:**
- Consumes: `PartView.types_only: tuple[Target, ...]` (Task 2); rule key `parts.<p>.imports.may.types_only` (Task 2).
- Produces: `Profile.types_only: dict[str, tuple[Target, ...]]`; `expansion._types_only(scope, who, key, match: Match, fix) -> Rule`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_types_only.py`, change `PARTS_ON` and add the tests (import `Target`
from `xarch.profile_values.placement`, and `RULES` from `tests.modules.rules.builders`):

```python
PARTS_ON = profile(types_only={"services": (Target("contract", "own"),)})
```

```python
OTHER_RESULT = ("app", "modules", "billing", "contract", "Published")
OTHER_CONTRACT = source("modules/billing/contract/results.py", module_functions=("published",))
ANY_TOO = profile(rules={**RULES, "services": (*RULES["services"], Target("contract", "any"))},
                  types_only={"services": (Target("contract", "own"),)})


def test_a_mark_on_the_own_instance_reads_the_own_instance_only():
    assert part_problems(SERVICE, Call(4, RESULT), Call(5, OTHER_RESULT), checked=ANY_TOO,
                         others=(CONTRACT_FILE, OTHER_CONTRACT)) == [
        f"app/{SERVICE}:4: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not call "
        "app.modules.docs.contract.Published (parts.services.imports.may.types_only)"]


def test_a_marked_entry_with_a_name_pattern_still_reads_every_name_it_reaches():
    patterned = profile(types_only={"services": (Target("contract", "own", (), "*Id"),)})
    assert part_problems(SERVICE, Call(4, RESULT), checked=patterned) == [
        f"app/{SERVICE}:4: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not call "
        "app.modules.docs.contract.Published (parts.services.imports.may.types_only)"]


def test_a_marked_entry_with_a_path_reads_below_its_path_only():
    below = profile(types_only={"services": (Target("contract", "own", ("results",)),)})
    use = Use(6, ("app", "modules", "docs", "contract", "results", "published"), 6)
    assert part_problems(SERVICE, Call(4, RESULT), uses=(use,), checked=below) == [
        f"app/{SERVICE}:6: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not "
        "reference app.modules.docs.contract.results.published, a function (parts.services.imports.may.types_only)"]
```

In `tests/modules/rules/application/logic/test_sentences.py`, add (spec test 15). Look at how the file builds a found
for `{type_only_fix}` with `grep -n "type_only_fix\|_caller_fix\|leave the call" tests/modules/rules/application/logic/test_sentences.py`.
If it has no such builder, put the test in `test_types_only.py` beside `test_the_fix_names_the_parts_that_may_call_it`:

```python
def test_the_fix_leaves_out_a_part_whose_entry_for_the_target_is_marked():
    marked = profile(types_only={"services": (Target("contract", "own"),), "controller": (Target("contract", "own"),)})
    found = part_violations([source(SERVICE, calls=(Call(4, RESULT),))], marked, "app")
    assert [v.fix for v in found] == [
        "use contract/ here only as a type, and leave the call to adapters/ or web/, which may make it"]
```

In `tests/modules/rules/adapters/test_spec_profile.py`, in the expected `Profile` of
`test_the_profile_view_becomes_the_profile_the_checks_see` (line 122), `types_only={"api": ("core",)}` becomes
`types_only={"api": (Target("core"),)}`: the profile carries each part's marked targets as the view gives them. The
view's `api` already writes `types_only=(Target("core"),)` (Task 2).

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_types_only.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/application/logic/test_sentences.py`
Expected: FAIL. `test_a_mark_on_the_own_instance_reads_the_own_instance_only` reports line 5 too (the rule matches the
part in any instance), and the adapter test gets part names, not targets.

- [ ] **Step 3: Read the marks as places**

`xarch/modules/rules/domain/profile.py:108`: `types_only: dict[str, tuple[Target, ...]] = field(default_factory=dict)`.
In the docstring (line 65), "types_only, by part, the parts it may use as types only" becomes "types_only, by part,
the targets of its imports.may marked types_only, whose reach it may use as types only". Import `Target` if the module
does not yet.

`xarch/modules/rules/adapters/spec_profile.py:80`: `types_only={p.name: p.types_only for p in parts if p.types_only},`

`xarch/modules/rules/application/logic/expansion.py` (add `from dataclasses import replace` at the top):

```python
def _types_only_tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test of a tier that names parts in `types_only` never calls what it imports from them, and never references
    one of their functions; a call is not said again as a reference."""
    return tuple(_types_only(Scope(TESTS, tier=tier.name), f"a {tier.name} test", f"tiers.{tier.name}.types_only",
                             Match("part", words=tier.types_only), "{tier_type_only_fix}")
                 for tier in profile.tiers if tier.types_only)


def _types_only_parts(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part whose `imports.may` marks entries types_only is held to the same rule on what those entries
    reach: their part, instance scope and path, a name pattern aside, which narrows only what may be imported."""
    return tuple(_types_only(Scope(APP, part), "{where}", f"parts.{part}.imports.may.types_only",
                             Match("place", places=tuple(replace(target, names="") for target in targets)),
                             "{type_only_fix}")
                 for part, targets in profile.types_only.items())


def _types_only(scope: Scope, who: str, key: str, match: Match, fix: str) -> Rule:
    said = f"{who} uses {{target_part}} only as a type: it may not "
    return Rule("types-only", scope, ("call", "function-reference"), MAY_NOT, (match,),
                (Saying(said + "call {path} ({key})", fix, _all("of-kind call")),
                 Saying(said + "reference {target}, a function ({key})", fix)),
                keep=_all("target-placed"), key=key)
```

`xarch/modules/rules/application/logic/sentences.py` `_caller_fix`:

```python
def _caller_fix(found: Found, profile: Profile) -> str:
    """Use the part as a type only and leave the call to a part that may make it: one whose `imports.may` reaches it by
    an entry with no mark, named from the profile."""
    src, dst = found.rule.scope.named_part, found.fact.at.part if found.fact.at is not None else None
    owners = [name for name, targets in profile.rules.items() if name not in (src, dst)
              and any(t.part == dst and t not in profile.types_only.get(name, ()) for t in targets)]
```

(the rest of the function is unchanged).

Other uses of `Profile.types_only`: run `git grep -n "\.types_only" xarch/modules/rules`. Each hit must read the
targets; only `sentences.py` and `expansion.py` should read a part's.

- [ ] **Step 4: Run the tests**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_types_only.py tests/modules/rules/adapters/test_spec_profile.py tests/modules/rules/application/logic/test_sentences.py tests/modules/rules/application/logic/test_expansion.py`
Expected: PASS.

- [ ] **Step 5: The corpora and the needs agreement (spec risk 1)**

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_bundled_imports.py`
Expected: PASS with no corpus edited. Every recorded types-only finding of a part is a call into the own instance:
7cc6111's 27 and stress's 67 all name `contract/` or `domain/` of the file's own module. The fix of each finding names
the same owners as before. If a finding vanishes, stop: per spec 2.11, record it only from an oracle extended by the
same change, and report it.

- [ ] **Step 6: Run the whole suite and the gates**

Run: `timeout 900 uv run pytest -q > /tmp/xarch-45-t3.log 2>&1; echo EXIT $?; tail -5 /tmp/xarch-45-t3.log` (in the background), then
`uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: `EXIT 0`, and every gate passes.

- [ ] **Step 7: Commit**

```bash
git add xarch tests
git commit -m "The types-only rule of a part reads what each entry of imports.may marked types_only reaches, its part, instance and path, a name pattern aside, and no longer the part by name in any instance; the profile carries the marked targets, the bridge in the adapter goes, and the fix of a types-only finding names the parts whose imports.may reaches the target by an entry with no mark; the recorded corpora, whose every such finding is a call into the file's own instance, are unchanged"
```

---

### Task 4: `profile check` names the new keys and lists a dropped mark

Spec: 2.8; test 10, 18; Review Focus 5.

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (docstring, `LOOSER`, `_looser`, `_sentence`)
- Modify: `xarch/modules/spec/domain/published.py:109-115`
- Test: `tests/modules/spec/application/logic/test_looseness.py`, `tests/modules/spec/application/test_origin.py`, `tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_json.py`

**Interfaces:**
- Consumes: `Part.types_only: tuple[Target, ...]`, `Architecture.rules` (Task 2).
- Produces: `Loosened.key` values `imports.may`, `imports.may.types_only`, `imports.libraries`, `imports.must`.

- [ ] **Step 1: Write the failing tests**

`test_looseness.py` compares through its own `loosened(custom, base) -> tuple[Loosened, ...]` (line 16), which runs
`origin_of` with `custom` based on `base`. It parses with `parsed` from `tests/modules/spec/profiles.py`. Add:

```python
MARK = "imports.may.types_only"


def marked(may) -> dict:
    """layered(), its part service allowed may."""
    document = layered()
    document["parts"]["service"]["imports"]["may"] = may
    return document


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(["store", {"shared": "types_only"}], ["store", "shared"],
                 [(MARK, "service", "shared", "service may now call shared, which it used only as a type "
                                             "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an entry that stays"),
    pytest.param(["store", {"shared": "types_only"}], ["store"], [], id="the entry dropped with its mark"),
    pytest.param(["store", {"shared": "types_only"}], ["store", {"shared": "types_only"}], [], id="the mark kept"),
    pytest.param(["store", {"shared/x": "types_only"}], ["store", {"shared": "types_only"}], [],
                 id="a wider mark covers it"),
    pytest.param(["store", {"shared": "types_only"}], "everything",
                 [(MARK, "service", "shared", "service may now call shared, which it used only as a type "
                                             "(parts.service.imports.may.types_only)")],
                 id="everything over a mark"),
])
def test_a_mark_dropped_while_its_target_stays_allowed_is_looser(base, custom, found):
    assert [(item.key, item.part, item.what, item.sentence)
            for item in loosened(parsed(marked(custom)), parsed(marked(base))) if item.key == MARK] == found
```

Change every existing expectation of `test_looseness.py`, `tests/modules/spec/application/test_origin.py` and
`tests/modules/spec/application/origins.py` that holds a part's looser key, to the new key and sentence of spec 2.8:
`"may_import"` becomes `"imports.may"`, `"libraries"` becomes `"imports.libraries"`, `"must_import"` becomes
`"imports.must"`, and their sentences become `... (parts.<p>.imports.may)`, `... (parts.<p>.imports.libraries)`,
`<p> may also meet imports.must with <what> (parts.<p>.imports.must)` and
`<p> no longer has to import anything (parts.<p>.imports.must)`. Find them with
`grep -nE '"(may_import|libraries|must_import)"|parts\.[a-z]+\.(may_import|libraries|must_import)' tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py tests/modules/spec/application/origins.py`.
The tier key `"types_only"` and its sentence stay. `test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own`
(line 162) reads `LOOSER`, so it covers the new key once `LOOSER` lists it.

In `tests/bootstrap/test_profile_check.py`, change the test that adds a target to a part's import list of a custom
profile (`grep -n "may also import" tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_json.py`) so that
its profile writes `imports: {may: [...]}` (done in Task 2). It now expects key `imports.may` and the sentence
`... (parts.<p>.imports.may)`, in text and in JSON (spec test 18).

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py`
Expected: FAIL. `ValueError: no sentence says how a profile is looser under 'imports.may'`, and the old keys are
returned.

- [ ] **Step 3: Change the keys, add the line**

In `xarch/modules/spec/application/logic/looseness.py`:

```python
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "types_only", "may_also_import", "uses.apply_never", "testing.skips", "files.pinned", "reserved",
          "known", "translated", "review.never", "review.mask", "evals.placement.lines")
```

In `_looser`, the first loop and the new one right after it:

```python
    for name in shared:
        before = base.rules.get(name, ())
        found += [("imports.may", name, _shown(t)) for t in custom.rules.get(name, ())
                  if not any(_covers(b, t) for b in before)]
    for name in shared:
        allows, marks = custom.rules.get(name, ()), custom.parts[name].types_only
        found += [("imports.may.types_only", name, _shown(t)) for t in base.parts[name].types_only
                  if any(_covers(c, t) for c in allows) and not any(_covers(c, t) for c in marks)]
```

then `("libraries", ...)` becomes `("imports.libraries", ...)` three times, and `("must_import", ...)` becomes
`("imports.must", ...)` twice. In `_sentence`:

```python
        case "imports.may":
            return f"{part} may also import {what} (parts.{part}.imports.may)"
        case "imports.may.types_only":
            return f"{part} may now call {what}, which it used only as a type (parts.{part}.imports.may.types_only)"
        case "imports.libraries" if not part:
            return "outside packages are not checked"
        case "imports.libraries" if what == EVERYTHING:
            return f"{part} may import any outside package (parts.{part}.imports.libraries)"
        case "imports.libraries":
            return f"{part} may also import {what} (parts.{part}.imports.libraries)"
```
```python
        case "imports.must" if not what:
            return f"{part} no longer has to import anything (parts.{part}.imports.must)"
        case "imports.must":
            return f"{part} may also meet imports.must with {what} (parts.{part}.imports.must)"
```

The module docstring: "a target added to a part's `may_import`" becomes "a target added to a part's `imports.may`".
After that clause add "; a `types_only` mark dropped from an entry of a part's `imports.may` whose target the part
still may import (some entry covers it) and no mark of its covers". "an outside package added to a part's
`libraries`" becomes "... to a part's `imports.libraries`". "a target added to a part's `must_import`" becomes "... to
a part's `imports.must`".

In `xarch/modules/spec/domain/published.py:109-115`, the `Loosened` docstring rows become:

```
        imports.may     part may also import what (a target as written)
        imports.may.types_only
                        part may now call what, a target it used only as a type
        imports.libraries
                        part may also import the outside package what; with no part, outside packages are unchecked
        imports.must    part may also meet imports.must with the target what; with no what, it has none now
```

Keep the alignment of the docstring's other rows.

- [ ] **Step 4: Run the tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_json.py`
Expected: PASS.

- [ ] **Step 5: Whole suite and gates**

Run: `timeout 900 uv run pytest -q > /tmp/xarch-45-t4.log 2>&1; echo EXIT $?; tail -5 /tmp/xarch-45-t4.log` (in the background), then
`uv run ruff check && uv run xarch check && uv run xarch check --strict && uv run xarch profile check architecture.yaml`
Expected: `EXIT 0`, and every gate passes.

- [ ] **Step 6: Commit**

```bash
git add xarch tests
git commit -m "profile check lists the ways a part's imports group is looser under imports.may, imports.libraries and imports.must, each sentence naming the new address, and a types_only mark dropped from an entry of imports.may whose target the part still may import and no mark of its covers as imports.may.types_only, the part now able to call it; tier keys keep their words"
```

---

### Task 5: The docs say the group

Spec: 2.10, 2.12; test 19.

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:403-405`
- Modify: `xarch/architectures/testing.md:225`, `xarch/architectures/agents.md:28,58`
- Regenerate: `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Modify: `README.md`, `CHANGELOG.md`
- Test: `tests/modules/spec/application/logic/test_docs_template.py`, `tests/bootstrap/test_docs_templates.py`

- [ ] **Step 1: Write the failing test of the line**

In `tests/modules/spec/application/logic/test_docs_template.py`, find the test that holds the `may-import` line
(`grep -n "may-import" tests/modules/spec/application/logic/test_docs_template.py`). Change its expected text to:

```python
"- `may-import`: every import between parts is one that the `imports.may` of the importing part allows (architecture.md, section 5)."
```

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_docs_template.py`
Expected: FAIL on that line.

- [ ] **Step 2: Change the template sources**

`docs_template.py:404`: `` "`may-import`: every import between parts is one that the `imports.may` of the importing part allows " ``.

`xarch/architectures/testing.md:225`, in the enforcement paragraph: "a `may_import` target or a `libraries` package added
to a part, a `must_import` target added to a part or the key dropped" becomes "an `imports.may` target or an
`imports.libraries` package added to a part, a `types_only` mark dropped from an entry of a part's `imports.may`, an
`imports.must` target added to a part or the key dropped". The tier words ("a tier that lost a `types_only` part",
"`may_also_import`") stay.

`xarch/architectures/agents.md:28`: "`parts.may_import`" becomes "`parts.imports.may`". Line 58: "its `may_import`,
`libraries` or `uses.never` entries" becomes "its `imports.may`, `imports.libraries` or `uses.never` entries".

Leave `docs/templates/architecture.md:183` and `docs/examples/modules/rules/application/logic/imports.py:33` as they
are. Changing them would move `docs/xarch/architecture.md`, which spec 2.10 forbids. Name them in the hand-off note as
the two prose hits the re-grep finds (Task 6).

- [ ] **Step 3: Regenerate the golden docs and read the diff**

```bash
uv run python - <<'EOF'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for profile, out in (("cli", "docs/cli"), ("web", "docs/web"), ("architecture.yaml", "docs/xarch")):
    for found in spec.docs(profile).files:
        Path(out, *found.path).write_text(found.template, encoding="utf-8")
EOF
git diff --stat docs/
git diff docs/ | grep '^[-+]' | grep -v '^[-+][-+]' | cut -c1-120
```

Expected: only `docs/cli/testing.md`, `docs/web/testing.md` and `docs/xarch/testing.md` change, each by 2 lines out and
2 in: the `may-import` line and the enforcement paragraph. Any other moved line or file is a defect to explain or fix,
never to accept. Restore an unexpected file with `git checkout -- <file>` and find its cause.

- [ ] **Step 4: README**

Make these edits, each to the line the spec names (2.12):
- Lines 117-118: the `parts*` shape line becomes

```
parts*:   {<part>: {path*, role*, litmus, imports: {may, must, libraries}, uses: {never}, tests | untested,
                    package_only, folders, shared,
```
  (the `holds:` lines below stay; lines 122-123 for tiers stay).
- Lines 199-202: "In `may_import`, a bare name ..." becomes "In `imports.may`, a bare name ...". Append, before "A
  part may always import itself.": "an entry written `{store: types_only}` is a target the part may import only to use
  as a type; " and change "`everything` no limit (also for `libraries`)" to "`everything` no limit (also for
  `imports.libraries`)".
- Line 210: `xarch profile explain parts.imports.may    # one key; ...` (keep the `#` column).
- Line 223: "(`parts.may_import` or `parts.<part>.may_import`)" becomes "(`parts.imports.may` or
  `parts.<part>.imports.may`)".
- Line 295: the key column `` `parts.may_import` `` becomes `` `parts.imports.may` ``, and "the importing part's
  `may_import`" becomes "the importing part's `imports.may`". Line 296: `` `parts.libraries` `` becomes
  `` `parts.imports.libraries` ``. Line 300: `` `parts.types_only` `` becomes `` `parts.imports.may.types_only` ``.
  Line 303: `` `parts.must_import` `` becomes `` `parts.imports.must` ``.
- Line 321: `` `parts.must_import` `` becomes `` `parts.imports.must` ``.
- Line 338: `(parts.kernel.may_import)` becomes `(parts.kernel.imports.may)`.
- Lines 392-394: the `key` list becomes "`imports.may`, `imports.may.types_only`, `imports.libraries`, `uses.never`,
  `untested`, `types_only`, `may_also_import`, `uses.apply_never`, `testing.skips`, `files.pinned`, `reserved`,
  `imports.must`, `litmus`, `known`, `translated`". The example address becomes `parts.kernel.imports.may`.
- Line 420: `    imports.may:  kernel may also import platform (parts.kernel.imports.may)`.
- Lines 437-440: "a target added to a part's `may_import`, an outside package added to its `libraries`" becomes "a
  target added to a part's `imports.may`, a `types_only` mark dropped from an entry of it, an outside package added to
  its `imports.libraries`". "a target added to a part's `must_import`" becomes "a target added to a part's
  `imports.must`".
- Line 506: "(its `may_import`, in the words of the docs' rules table)" becomes "(its `imports.may`, ...)" and
  "(`libraries`: `none`," becomes "(`imports.libraries`: `none`,". The JSON field names of `where` (535-565) stay.
- Line 1069: "`may_import`, `libraries` and `uses.never`" becomes "`imports.may`, `imports.libraries` and `uses.never`".

Then `grep -nE "may_import|must_import|libraries|types_only" README.md`: each hit left must be a tier key, a `where`
JSON field, an `imports.*` address, or the rule id `libraries`.

- [ ] **Step 5: CHANGELOG**

Under `## [Unreleased]`, add to `### Added`:

```markdown
- `profile check` lists a `types_only` mark dropped from an entry of a part's `imports.may`, whose target the part
  still may import and no mark of the part covers, under the key `imports.may.types_only`: `<part> may now call
  <target>, which it used only as a type (parts.<part>.imports.may.types_only)`.
```

and, under `### Changed` (create the heading after `### Added` if it is missing):

```markdown
- A part's `may_import`, `must_import` and `libraries` move into one group, `imports: {may, must, libraries}`, with
  the same meaning: `may` what the part may import besides itself (or `everything`), `must` the targets each of its
  files imports one of, each an entry of `may`, `libraries` its outside packages. A part's `types_only` becomes a mark
  on its entry of `imports.may`, `{<target>: types_only}`, such as `may: [ports, {contract: types_only}]`, read on what
  the entry reaches (its part, instance and path; a name pattern narrows only what may be imported), not on the part
  in any instance; a tier's `types_only` list stays. Findings name the new addresses (`parts.<part>.imports.may`,
  `.imports.must`, `.imports.libraries`, `.imports.may.types_only`), and so do `profile explain` and the `Loosened`
  keys of `profile check` (`imports.may`, `imports.libraries`, `imports.must`). The old keys are refused with the form
  that replaces them (`unknown key 'may_import': moved in 0.3.0: write imports: {may: [...]}`, and the same for
  `must_import`, `libraries` and `types_only`); `profile explain parts.may_import` says the same. Rule ids, `where`'s
  JSON fields and the tier keys do not change.
```

- [ ] **Step 6: Run the docs tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_docs_template.py tests/bootstrap/test_docs_templates.py tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add xarch docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md README.md CHANGELOG.md tests
git commit -m "The docs say a part's imports group: the may-import line of the generated testing docs names imports.may, and their enforcement paragraph names imports.may, imports.libraries and imports.must and lists a types_only mark dropped as looser; AGENTS.md names parts.imports.may; the README writes imports: {may, must, libraries} on a part, the mark {<target>: types_only}, and the new addresses in its explain examples, rule table, sample finding, looser keys and where text; the CHANGELOG says, under Unreleased, that the keys moved into the group, that types_only became the mark read on what its entry reaches, how the old keys are refused, and the new looser line; the golden docs regenerate moving the may-import line and the enforcement paragraph alone"
```

---

### Task 6: Gates and the re-grep

Spec: section 3.

- [ ] **Step 1: Run every gate**

Run, the suite in the background:
`timeout 900 uv run pytest -q > /tmp/xarch-45-pytest.log 2>&1; echo EXIT $?; tail -3 /tmp/xarch-45-pytest.log`, then
`uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`.
Expected: `EXIT 0` with no failure; "All checks passed!"; both checks exit 0; "OK: the profile is valid".

- [ ] **Step 2: The re-grep**

Run: `git grep -nE "may_import|must_import|libraries|types_only" -- xarch tests README.md CHANGELOG.md docs architecture.yaml ':!docs/superpowers'`
Expected: for a part, every hit is one of these: the retired table (`profile_keys.py`); the refusal tests; a key under
`imports` (`libraries:` under `imports`, `imports.libraries`, `imports.may.types_only`); `where`'s JSON fields
(`where_report.py`, README 535-565, their tests); a Python identifier (fields, functions, `_may_import_everything`,
keyword arguments); the source module `xarch.modules.rules.application.logic.must_import`; prose about tiers or tier
keys; the CHANGELOG's own lines about the move. The two known prose hits, `docs/templates/architecture.md:183` and
`docs/examples/modules/rules/application/logic/imports.py:33`, are left as they are, because changing them moves
`docs/xarch/architecture.md` (spec 2.10). Their copies in `docs/xarch/architecture.md` are left too. Fix any other hit
in the commit of the task that owns its file (a new commit in that task's message style).

- [ ] **Step 3: Commit (only if a fix was needed)**

```bash
git add <the files fixed>
git commit -m "<what the fix makes true, in the style of the task that owns the file>"
```
<!-- task-pipeline: validated -->
