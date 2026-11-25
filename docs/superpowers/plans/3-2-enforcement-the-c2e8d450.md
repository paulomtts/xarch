# 3.2 enforcement: the `unresolved` section lists imports the reader could not follow

Card: c2e8d450 (subtask of 3c7754c4). Release step 6 of the merged order, second half; the first half (3.1, the
reader) is already on this branch (`Import.unresolved` at `xarch/kernel/source.py:28`, set by
`xarch/modules/rules/adapters/fs_source_tree.py:283-295`).

Owning note: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below, "the note").

## Inherited constraints

- The note, 1.5 second bullet (lines 196-198): "A new enforcement section, `unresolved`, lists each `Import.unresolved`
  by file and line, and fails `--strict`, as `dynamic` does today (`enforcement.py:80`). Text: `app/x.ts:3: import
  "../domain/ordr" names no file of the app`. JSON key `unresolved`, with the README section on enforcement."
- The note, 1.1 (lines 137-138): an import the reader could not follow binds no `Ref` "and is listed (1.5)". A gap is
  never silent (1.3, lines 181-182; rulings, default (2), lines 37-38: "imports the reader cannot follow listed under
  `unresolved`, failing `--strict`").
- The note, 1.6 (lines 210-214): no refusal at load; no profile line changes.
- The note, 1.7 hand-built facts bullet (lines 223-225): `tests/modules/rules/builders.py` builds a `SourceFile` whose
  `Import` is written `@app/domain/order` with `module` resolved to the root, and one with `unresolved=True`. "The
  first is checked as an absolute import; the second is listed under `unresolved` and fails `--strict`."
- The note, 1.7 third bullet (lines 226-227): the recorded corpora do not move.
- The note, 13 row 5a (line 1091): `enforcement.py`, `Enforcement`, report, JSON, README, "about 6 places"; row "all"
  (lines 1112-1114): README and CHANGELOG get this step's lines; no profile changes; recorded corpora and golden docs
  "none expected".
- Review 3 (`0.3.0-cohesion-review-3.md`), O4 and O5 (lines 228-229): this step's README and CHANGELOG lines go under
  `[Unreleased]`; O8 (line 232): golden docs regenerated, diff read, never hand edited.
- Card dodge: passing in silence on an import the reader cannot follow.

## Behavior

### What is listed

1. An import is listed under `unresolved` exactly when its `Import.unresolved` is true. Nothing else decides it: an
   absolute import, a resolved relative import and an import written by an alias whose `module` the reader resolved to
   the root (`written="@app/domain/order"`, `module=("app", "domain", "order")`, `relative=False`) are never listed.
2. The files read are the app's governed files and the test files, as for `dynamic`
   (`source_check.py`, `dynamic([*app, *tests], rules)`). Files that did not parse (`error` set) are already dropped
   before the enforcement is built and are not looked at.
3. Each listed import is one item: the file as shown (`SourceFile.name`, e.g. `app/domain/services.py`), the import's
   first line (`Import.line`), and the module as the source writes it (`Import.written`, e.g. `.ordr` for
   `from .ordr import X`). One `from ... import a, b` statement is one item.
4. Order: files in the order read (app files, then test files), and within a file by line. (The Python reader yields
   imports in `ast.walk` order, which is not line order when an import sits in a function; the section sorts by line
   within a file.)

### The item in words

5. One sentence, used both by the text line and by the strict finding's detail:
   `<file>:<line>: import "<written>" names no file of the app`, e.g.
   `app/domain/services.py:3: import ".ordr" names no file of the app`. The quotes are double quotes around `written`
   as is. The sentence is the same for a test file (the card's wording is kept verbatim).

### Text output (`xarch check`)

6. The enforcement section shows one line per listed import, labelled `unresolved`, right after the `dynamic` line
   and before the `weak` lines:
   `  unresolved:  app/domain/services.py:3: import ".ordr" names no file of the app`
   (label padded as every other label, `_line(..., 2)` in `xarch/cli/reports/report.py`). No cap of `SHOWN`: each
   import gets its line, as `weak` does. With nothing listed, no line appears.

### JSON output (`--format json`)

7. `enforcement` always holds the key `unresolved`: a list, empty when nothing is listed, of
   `{"file": <str>, "line": <int>, "written": <str>}` in the order of 4. It sits right after `"dynamic"` in the
   object.
8. A strict finding from it is `{"key": "unresolved", "detail": "<the sentence of 5>"}` in `strict_failures`, which is
   filled whether or not `--strict` was given, as for every other key.

### `--strict`

9. `unresolved` is a section key (the published constant `UNRESOLVED = "unresolved"`, in `SECTIONS` right after
   `DYNAMIC`). Each listed import is one strict finding, placed right after the dynamic findings and before the weak
   ones in `strict_findings`. `xarch check --strict` exits 1 when any is listed; the text lists each under `strict:` as
   `    unresolved: <sentence>`. Without `--strict` the section never changes the exit code.
10. A project with no unresolved import sees no change but the always-present empty JSON key `"unresolved": []`.

### Help and docs

11. `xarch check --help` (the text at `xarch/cli/commands/check.py:31`) names imports the reader could not follow
    among what `--strict` fails on, after "dynamic imports".
12. README, section "The enforcement section" and the JSON contract above it: the JSON example gains
    `"unresolved": [],` after `"dynamic"`; the item description says `unresolved` items `{"file", "line", "written"}`;
    the `strict_failures` key list gains `unresolved` after `dynamic`; the text example gains an `unresolved:` line
    after `dynamic:`; a bullet `unresolved` after the `dynamic` bullet says each import of the files read that names a
    place of the app (relative, or by an alias the project maps) the reader found no file or folder for, with the module
    as written, so the import rules cannot see what it names; the `--strict` paragraph gains "each unresolved import"
    after "each dynamic import".
13. CHANGELOG, under `## [Unreleased]` / `### Changed` (after the 3.1 entry on the reader): the new enforcement
    section `unresolved` lists each import the reader could not follow by file and line with the module as written,
    in text and under the JSON key `unresolved` (`{"file", "line", "written"}`), and `--strict` fails on each, as on a
    dynamic import; a project with no such import sees only the empty JSON key.

## Shape (what the planner needs to know, not how to write it)

- The `At` value (`published.py`) carries no written text, so the item needs a carrier. Use a new frozen published
  value `Unresolved(file: str, line: int, written: str)` in `xarch/modules/rules/domain/published.py`, re-exported by
  `xarch/modules/rules/contract/__init__.py` with `UNRESOLVED`. `At` is not changed.
- `enforcement.unresolved(files) -> list[Unresolved]` in `xarch/modules/rules/application/logic/enforcement.py`, beside
  `dynamic`; `detail()` gains the `Unresolved` case giving the sentence of 5; the module docstring's list and strict
  paragraph name the section.
- `Enforcement.unresolved: tuple[Unresolved, ...] = ()` (`outcomes.py`), next to `dynamic`; `Finding.item`'s union
  gains `Unresolved`; docstrings updated.
- `EnforcementView.unresolved: tuple[UnresolvedView, ...] = ()` where the contract's `UnresolvedView(file, line,
  written, sentence)` is built by `SourceCheckService.view()` with `sentence = enforcement.detail(item)`, so the report
  shows the one sentence the logic writes and never rebuilds it. Add the field at the end of `EnforcementView` (it is
  built positionally in `view()`); pass it by keyword.
- `report.py`: `LABELS[UNRESOLVED] = "unresolved"` (required: `tests/cli/reports/test_report.py:183` holds
  `set(LABELS) == set(SECTIONS)`), the text line of 6, the JSON key of 7.
- No comments in code; docstrings only.

## Out of scope

- Any reader change (3.1, sibling card bea20072): what the reader marks unresolved, how it resolves, aliases.
- `import.resolved`, `NEEDS`, the "absolute import" texts (done in 3.1).
- `xarch/architectures/testing.md` and the golden docs `docs/{cli,web,xarch}/testing.md`: the note expects no golden
  doc to move (13, line 1114), so the paragraph listing the enforcement's contents is not edited in this step. The
  implementer regenerates the golden docs and confirms an empty diff; a non-empty diff is a defect to report, not to
  commit.
- Recorded corpora (`tests/bootstrap/corpora/`): untouched; they hold no relative import, so their recorded findings
  and strict failures do not move.
- Any profile file (`architecture.yaml`, `cli.yaml`, `web.yaml`, the stress and archived ones).
- A per-language wording of the sentence, and counting/capping of the text lines.

## Tests (written first)

Hand-built facts tier, `tests/modules/rules/application/logic/test_enforcement.py` (pure logic on hand-built
`SourceFile`/`Import` values: the fastest place to pin the selection rule and the order, and the note's 1.7 asks for
hand-built facts):

- T1 `unresolved()` lists an `Import(..., unresolved=True)` as `Unresolved(file, line, written)` and skips an absolute,
  a resolved relative and an aliased-resolved import in the same file.
- T2 `unresolved()` keeps files in the order given (an app file, then a test file) and, within a file, sorts by line
  (an unresolved import at line 9 given before one at line 3 comes out 3, 9).
- T3 `unresolved([])` and files with no unresolved import give `[]`.
- T4 `strict_findings` of an `Enforcement` with `dynamic=(DYNAMIC,)`, `unresolved=(UNRESOLVED_ITEM,)`, `weak=(WEAK,)`
  gives `Finding("unresolved", UNRESOLVED_ITEM)` right after the dynamic finding and before the weak one (extend the
  existing ordered test at `:71-76`).
- T5 `detail(Unresolved("app/x.py", 3, ".ordr"))` is `app/x.py:3: import ".ordr" names no file of the app` (a new
  param of the existing `detail` table).

Hand-built facts tier, the may-import rule (`tests/modules/rules/application/logic/test_imports.py`, which already
checks `may-import` on `builders.source`/`imp`): the note's 1.7 first half.

- T6 Add to `tests/modules/rules/builders.py` a builder for an import written by an alias and resolved to the root
  (e.g. `aliased(line, written, module, *names)` giving `Import(line, dotted(module), names or None, written=written)`)
  and one for an unresolved import (`unresolved(line, written, *names)` giving
  `Import(line, (), names or None, True, 0, written=written, unresolved=True)`, the shape the Python reader gives a
  relative import it cannot follow).
- T7 A file `modules/docs/domain/values.py` with `aliased(3, "@app/platform/sql", "app.platform", "sql")` gets the same
  `may-import` violation (rule, file, line, and the `domain/ of modules/docs may not import platform/` text) as the
  absolute `imp(3, "app.platform", "sql")`; and with an allowed target (`@app/kernel/ids`) none. It is checked as an
  absolute import.
- T8 The same aliased file is not listed by `enforcement.unresolved`, and a file with `unresolved(4, "@app/domain/ordr",
  "Order")` is listed and, in an `Enforcement` built from it, yields a strict finding with key `unresolved`
  (`test_enforcement.py`).

Report tier, `tests/cli/reports/test_report.py` (rendering of a hand-built `EnforcementView`; no reading):

- T9 The text section shows `  unresolved:  <sentence>` once per item, after the `dynamic` line and before `weak`; no
  line with none.
- T10 The JSON `enforcement.unresolved` is `[{"file", "line", "written"}]` in order, and `[]` with none.
- T11 With `strict=True` and a finding `FindingView("unresolved", <sentence>)`, the strict list prints
  `    unresolved: <sentence>`. The existing `LABELS`/`SECTIONS` test covers the label.

End-to-end tier, `tests/bootstrap/` (the real Python reader on a temporary project: proves the wiring of
`source_check.py` and the CLI, which no hand-built test reaches):

- T12 `tests/bootstrap/test_enforcement.py`: a project whose `app/kernel/a.py` writes `from .ordr import X` at line 2
  (no `ordr.py`) gives `found.enforcement.unresolved == (Unresolved("app/kernel/a.py", 2, ".ordr"),)`; a project whose
  relative import names an existing file gives `()`. A test file with an unresolvable relative import is listed too.
- T13 `tests/bootstrap/test_check_enforcement.py`: the always-present JSON key set (`:46`) gains `unresolved`; on the
  project of T12 `xarch check` exits 0 and prints the `unresolved:` line; `xarch check --strict` exits 1 and lists
  `unresolved: app/kernel/a.py:2: import ".ordr" names no file of the app`; JSON `strict_failures` holds
  `{"key": "unresolved", ...}`.

Docs tier:

- T14 `tests/architecture/test_readme.py` and the rest of `tests/architecture/` pass with the README edits; the
  recorded corpora test passes unchanged.

## Gates

On this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background, read it at the
end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`. xarch's own code has no relative import, so its own `check --strict`
stays green. Regenerate the golden docs and confirm no diff.


---

# 3.2 enforcement: the `unresolved` section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A new enforcement section, `unresolved`, lists every import the reader marked `Import.unresolved` (file, first
line, module as written), in text and in JSON, and `xarch check --strict` fails on each, as it does on a dynamic import.

**Architecture:** A new published value `Unresolved(file, line, written)` (rules `domain/published.py`) is selected by
`enforcement.unresolved(files)` (pure logic beside `dynamic`), held on `Enforcement.unresolved`, turned into strict
findings by `strict_findings` and into words by `detail`. `SourceCheckService` fills it from the parsed app and test
files and hands it out as `EnforcementView.unresolved: tuple[UnresolvedView, ...]`, each view holding the value and the
sentence `detail` writes; `xarch/cli/reports/report.py` prints the sentence and the JSON items.

**Tech Stack:** Python 3.13, frozen dataclasses, pytest, typer (`CliRunner`), ruff, uv.

**Spec:** `docs/superpowers/specs/3-2-enforcement-the-c2e8d450.md` (prepended above; read it whole before starting).

## Spec deviation (decided by the planner, with evidence)

The spec's Shape asks for a contract `UnresolvedView(file, line, written, sentence)`. Built that way, xarch's own
`uv run xarch check` (a gate of this step) reports a **no-twins violation**: the planner put both classes into a scratch
copy of this branch and ran it:

```
xarch/modules/rules/contract/__init__.py:621: UnresolvedView declares the fields of Unresolved at xarch/modules/rules/domain/published.py:167 in the same order, and 1 more (sentence) (file, line, written, sentence): contract/ of modules/rules and domain/ of modules/rules hold one type written twice (no-twins)
```

(`architecture.yaml:331`, `no-twins: {min_subset: 3}`: three fields of one class, in order, inside the four of another.)
So the plan builds the view as **`UnresolvedView(item: Unresolved, sentence: str)`**: the published value as it is,
plus the one sentence the logic writes. The same scratch run with this shape reported no twin. Nothing a user sees
changes: the text line, the JSON item `{"file", "line", "written"}`, the strict finding and its detail are exactly as
the spec says. The only other effect is on T12: the bootstrap test reads `found.unresolved[i].item` (an `Unresolved`)
and `.sentence`, not a bare `Unresolved`.

## Global Constraints

- No comments in code; docstrings only (spec, Shape). xarch's own `no-comments` guard enforces this.
- `ruff.toml`: `line-length = 140`. Run `uv run ruff check`, **never** `--fix`.
- The sentence is exactly `<file>:<line>: import "<written>" names no file of the app` (double quotes around `written`
  as is), the same for app and test files.
- Text label `unresolved`, padded by `_line(..., 2)`; one line per import; **no `SHOWN` cap**.
- JSON: `enforcement.unresolved` always present, `[]` when empty, items `{"file", "line", "written"}`, the key right
  after `"dynamic"`.
- `UNRESOLVED = "unresolved"`, in `SECTIONS` right after `DYNAMIC`; strict findings right after the dynamic ones, before
  the weak ones.
- Without `--strict` the section never changes the exit code.
- No reader change, no profile file change (`architecture.yaml`, `cli.yaml`, `web.yaml`, stress, archived), no change
  under `tests/bootstrap/corpora/`, no edit of `xarch/architectures/testing.md` or `docs/{cli,web,xarch}/`.
- Golden docs are regenerated and their diff read; a non-empty diff is a defect to report, never to commit or hand-edit.
- README and CHANGELOG lines go under `## [Unreleased]` / `### Changed`.
- Kill nothing by name or pattern; stop a stuck test with `timeout`.

## Review Focus

1. An unresolved import inside a function body, above a top-level one: the Python reader yields it later (`ast.walk`
   is breadth-first), yet it must be listed first, by line. Test: Task 3, Step 1
   (`test_the_unresolved_imports_of_a_file_are_listed_by_line_whatever_the_reader_yields_first`).
2. A relative import that climbs above the root (`from ...above import V` in `app/kernel/c.py`) is listed with its
   dots as written (`"...above"`). Test: same Task 3 test.
3. A parenthesised `from .gone import (a, b)` spanning several lines is one item, at its first line. Test: same Task 3
   test, and the one-statement-two-names case in Task 1 (`test_an_import_the_reader_could_not_follow_is_listed_...`).
4. A test file's unresolved relative import (below `tests/`) is listed, after the app's. Test: Task 3
   (`test_an_import_the_reader_could_not_follow_is_listed_in_an_app_file_and_in_a_test_file`).
5. A relative import that the reader *did* follow (the file exists) is never listed, so a project that writes relative
   imports correctly sees no line and passes `--strict`. Test: Task 3
   (`test_a_relative_import_of_a_file_that_exists_is_not_listed`).

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `xarch/modules/rules/domain/published.py` | modify | `UNRESOLVED`, `SECTIONS`, new `Unresolved` value, docstrings |
| `xarch/modules/rules/domain/outcomes.py` | modify | `Enforcement.unresolved`, `Finding.item` union, docstrings |
| `xarch/modules/rules/application/logic/enforcement.py` | modify | `unresolved()`, `strict_findings`, `detail`, docstring |
| `xarch/modules/rules/contract/__init__.py` | modify | re-export `UNRESOLVED`, `Unresolved`; new `UnresolvedView`; `EnforcementView.unresolved` |
| `xarch/modules/rules/application/services/source_check.py` | modify | fill `Enforcement.unresolved`; build the views |
| `xarch/cli/reports/report.py` | modify | `LABELS`, text line, JSON key |
| `xarch/cli/commands/check.py` | modify | `--strict` help names the imports the reader could not follow |
| `tests/modules/rules/builders.py` | modify | `aliased()`, `unresolved()` import builders |
| `tests/modules/rules/application/logic/test_enforcement.py` | modify | T1–T5, T8 |
| `tests/modules/rules/application/logic/test_imports.py` | modify | T7 |
| `tests/cli/reports/test_report.py` | modify | T9–T11 |
| `tests/bootstrap/test_enforcement.py` | modify | T12 + Review Focus 1, 2, 3, 4, 5 |
| `tests/bootstrap/test_check_enforcement.py` | modify | T13, help text |
| `README.md`, `CHANGELOG.md` | modify | docs (T14) |

---

### Task 1: The `Unresolved` value, its selection, its strict finding and its sentence

**Files:**
- Modify: `xarch/modules/rules/domain/published.py:1-43`
- Modify: `xarch/modules/rules/domain/outcomes.py:8,42-82`
- Modify: `xarch/modules/rules/application/logic/enforcement.py:1-113`
- Modify: `xarch/modules/rules/contract/__init__.py:12-58` (re-export only)
- Modify: `xarch/cli/reports/report.py:22-47` (label only; needed because `tests/cli/reports/test_report.py:182-183`
  holds `set(LABELS) == set(SECTIONS)`)
- Modify: `tests/modules/rules/builders.py` (append two builders)
- Test: `tests/modules/rules/application/logic/test_enforcement.py`, `tests/modules/rules/application/logic/test_imports.py`

**Interfaces:**
- Consumes: `xarch.kernel.source.Import` (fields `line`, `written`, `unresolved`), `SourceFile.name`, `SourceFile.imports`.
- Produces:
  - `xarch.modules.rules.domain.published.UNRESOLVED: str == "unresolved"`, in `SECTIONS` right after `DYNAMIC`.
  - `xarch.modules.rules.domain.published.Unresolved(file: str, line: int, written: str)`, frozen dataclass.
  - `Enforcement.unresolved: tuple[Unresolved, ...] = ()` (field right after `dynamic`).
  - `Finding.item: str | Drift | At | Unresolved | Weak | Shortfall`.
  - `enforcement.unresolved(files: Iterable[SourceFile]) -> list[Unresolved]`.
  - `enforcement.detail(Unresolved(f, l, w)) -> f'{f}:{l}: import "{w}" names no file of the app'`.
  - `xarch.modules.rules.contract` re-exports `UNRESOLVED` and `Unresolved`.
  - `report.LABELS[UNRESOLVED] == "unresolved"`.
  - `tests.modules.rules.builders.aliased(line: int, written: str, module: str, *names: str) -> Import` and
    `tests.modules.rules.builders.unresolved(line: int, written: str, *names: str) -> Import`.

- [ ] **Step 1: Add the two test builders**

Append to the end of `tests/modules/rules/builders.py`:

```python


def aliased(line: int, written: str, module: str, *names: str) -> Import:
    """An import written by an alias the project maps, such as `@app/domain/order`, that the reader resolved to module
    from the top: absolute, as the reader hands it over, with the module as the source writes it."""
    return Import(line, dotted(module), names or None, written=written)


def unresolved(line: int, written: str, *names: str) -> Import:
    """An import naming a place of the app the reader found no file or folder for, as the Python reader hands over a
    relative one it cannot follow: no module, relative, climbing none, marked unresolved, as written."""
    return Import(line, (), names or None, True, 0, written=written, unresolved=True)
```

- [ ] **Step 2: Write the failing logic tests (T1–T5, T8)**

In `tests/modules/rules/application/logic/test_enforcement.py`:

Replace the imports block (lines 7–23) with:

```python
from tests.modules.rules import builders
from tests.modules.rules.builders import PYTHON
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.enforcement import (
    detail,
    drift,
    dynamic,
    excluded_folder,
    folders,
    reading,
    skipped,
    strict_findings,
    unresolved,
    weak_of,
)
from xarch.modules.rules.domain.outcomes import Enforcement, Finding, InitFile
from xarch.modules.rules.domain.parsed import SourceFile, Use
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import At, Drift, Unresolved, Weak
```

Replace the strict test and the constants after it (lines 70–82) with:

```python
def test_strict_fails_on_every_finding_but_the_guards_its_baseline_also_leaves_off_and_how_the_profile_differs():
    enforcement = Enforcement(
        ("no-comments", "closed-tree"), ("closed-tree",),
        ungoverned=("app/scripts/x.py",), init_files=(CHANGED,), skipped=(SKIP,), dynamic=(DYNAMIC,),
        unresolved=(UNRESOLVED_ITEM,), weak=(WEAK,))
    assert strict_findings(enforcement) == (
        Finding("guards_off", "no-comments"), Finding("ungoverned", "app/scripts/x.py"), Finding("init_files", CHANGED),
        Finding("skipped", SKIP), Finding("dynamic", DYNAMIC), Finding("unresolved", UNRESOLVED_ITEM),
        Finding("weak", WEAK))


CHANGED = Drift(("tests", "test_rules.py"), "changed")
SKIP = At("tests/test_a.py", 3)
DYNAMIC = At("app/kernel/dyn.py", 2)
UNRESOLVED_ITEM = Unresolved("app/x.py", 3, ".ordr")
WEAK = Weak("stand-ins", "tests/fakes/repo.py", 1, "FakeRepo does not define get, which Repo declares")
```

In the `test_the_detail_of_a_finding` parametrize list, add this param right after the `a place is its file and line`
param:

```python
    pytest.param(UNRESOLVED_ITEM, 'app/x.py:3: import ".ordr" names no file of the app',
                 id="an import the reader could not follow is its place, its module as written and why"),
```

Append to the end of the file:

```python


def test_an_import_the_reader_could_not_follow_is_listed_by_its_file_line_and_module_as_written():
    files = [builders.source("domain/services.py", builders.imp(1, "app.kernel", "ids"),
                             builders.imp(2, "", "order", up=0),
                             builders.aliased(3, "@app/domain/order", "app.domain.order", "Order"),
                             builders.unresolved(4, ".ordr", "Order", "Line"))]
    assert unresolved(files) == [Unresolved("app/domain/services.py", 4, ".ordr")]


def test_the_unresolved_imports_keep_the_order_of_the_files_and_within_a_file_go_by_line():
    files = [builders.source("kernel/a.py", builders.unresolved(9, ".late", "x"), builders.unresolved(3, ".early", "y")),
             builders.in_tests("kernel/test_a.py", builders.unresolved(2, "..gone", "z"))]
    assert unresolved(files) == [Unresolved("app/kernel/a.py", 3, ".early"), Unresolved("app/kernel/a.py", 9, ".late"),
                                 Unresolved("tests/kernel/test_a.py", 2, "..gone")]


def test_with_no_import_the_reader_could_not_follow_nothing_is_listed():
    assert unresolved([]) == []
    assert unresolved([builders.source("kernel/a.py", builders.imp(1, "app.kernel", "ids")),
                       builders.source("kernel/b.py")]) == []


def test_an_aliased_import_resolved_to_the_root_is_not_listed_and_one_the_reader_could_not_follow_fails_strict():
    aliased = builders.source("modules/docs/domain/values.py",
                              builders.aliased(3, "@app/platform/sql", "app.platform", "sql"))
    lost = builders.source("domain/services.py", builders.unresolved(4, "@app/domain/ordr", "Order"))
    assert unresolved([aliased]) == []
    found = tuple(unresolved([aliased, lost]))
    assert found == (Unresolved("app/domain/services.py", 4, "@app/domain/ordr"),)
    assert strict_findings(Enforcement(unresolved=found)) == (Finding("unresolved", found[0]),)
    assert detail(found[0]) == 'app/domain/services.py:4: import "@app/domain/ordr" names no file of the app'
```

- [ ] **Step 3: Write the may-import test for the aliased import (T7)**

In `tests/modules/rules/application/logic/test_imports.py`, change line 8 to:

```python
from tests.modules.rules.builders import PROFILE, PYTHON, aliased, imp, source, steps
```

and append to the end of the file:

```python


def test_an_import_written_by_an_alias_and_resolved_below_the_root_is_checked_as_an_absolute_import():
    written = source("modules/docs/domain/values.py", aliased(3, "@app/platform/sql", "app.platform", "sql"))
    absolute = source("modules/docs/domain/values.py", imp(3, "app.platform", "sql"))
    found = violations([written, *APP], PROFILE, "app")
    assert [str(v) for v in found] == ["app/modules/docs/domain/values.py:3: domain/ of modules/docs may not import "
                                       "platform/ (app.platform.sql)"]
    assert found == violations([absolute, *APP], PROFILE, "app")
    allowed = source("modules/docs/domain/values.py", aliased(3, "@app/kernel/ids", "app.kernel", "ids"))
    assert violations([allowed, *APP], PROFILE, "app") == []
```

- [ ] **Step 4: Run the tests to see them fail**

Run: `timeout 300 uv run pytest tests/modules/rules/application/logic/test_enforcement.py tests/modules/rules/application/logic/test_imports.py -q`
Expected: `test_enforcement.py` fails to collect with `ImportError: cannot import name 'unresolved' from
'xarch.modules.rules.application.logic.enforcement'` (or `cannot import name 'Unresolved'`). The new
`test_imports.py` test **passes** already (the planner checked: the aliased import gives the same violation as the
absolute one today); it pins that behaviour and needs no production change.

- [ ] **Step 5: Add `UNRESOLVED` and `Unresolved` to `published.py`**

In `xarch/modules/rules/domain/published.py`, replace the docstring line 5:

```
    At    a place in a file, as the enforcement section names a skip or a dynamic import; the command line shows it
```

with:

```
    At    a place in a file, as the enforcement section names a skip or a dynamic import; the command line shows it
    Unresolved an import the reader could not follow, as the enforcement section lists it; the command line shows it
```

Replace lines 29–34:

```python
GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, WEAK, APPROXIMATE, VACUOUS, UNPLACED = (
    "guards_off", "ungoverned", "init_files", "skipped", "dynamic", "weak", "approximate", "vacuous", "litmus")
"""The keys of the sections of the enforcement a finding `--strict` fails on is under: a guard left off, an
ungoverned file, an init file, a skip, a dynamic import, a weak finding, an approximate key, a check of the
profile's own that reads nothing, and a part redefined without its litmus."""
SECTIONS = (GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, WEAK, APPROXIMATE, VACUOUS, UNPLACED)
```

with:

```python
GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, UNRESOLVED, WEAK, APPROXIMATE, VACUOUS, UNPLACED = (
    "guards_off", "ungoverned", "init_files", "skipped", "dynamic", "unresolved", "weak", "approximate", "vacuous",
    "litmus")
"""The keys of the sections of the enforcement a finding `--strict` fails on is under: a guard left off, an
ungoverned file, an init file, a skip, a dynamic import, an import the reader could not follow, a weak finding, an
approximate key, a check of the profile's own that reads nothing, and a part redefined without its litmus."""
SECTIONS = (GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, UNRESOLVED, WEAK, APPROXIMATE, VACUOUS, UNPLACED)
```

Right after the `At` class (after line 42, `    line: int`), insert:

```python


@dataclass(frozen=True)
class Unresolved:
    """An import of a file read that names a place of the app (relative, or by an alias the project maps) the reader
    found no file or folder for: how the file is shown, the import's first line, and the module as the source writes
    it."""
    file: str
    line: int
    written: str
```

- [ ] **Step 6: Hold it on `Enforcement` and in `Finding`**

In `xarch/modules/rules/domain/outcomes.py`, line 8 becomes:

```python
from xarch.modules.rules.domain.published import At, Drift, KnownName, Loosened, Translation, Unresolved, Weak
```

Replace the `Finding` class (lines 41–48) with:

```python
@dataclass(frozen=True)
class Finding:
    """An enforcement finding that `--strict` fails on: the key of the enforcement section it is under, and the item
    there that fails: a guard left off or an ungoverned file (by name), an init file that drifted, a skip or a dynamic
    import (where it is), an import the reader could not follow, a weak check, a key whose check reads a fact the
    language supplies only partly, a check of the profile's own that read nothing (its id), or a part redefined
    without its litmus (as said)."""
    key: str
    item: str | Drift | At | Unresolved | Weak | Shortfall
```

In the `Enforcement` docstring replace

```
    tests skipped or expected to fail, and the dynamic imports, where they are; the checks satisfied to the letter
```

with

```
    tests skipped or expected to fail, and the dynamic imports, where they are; the imports of the files read that the
    reader could not follow, with the module as written; the checks satisfied to the letter
```

and right after the field `    dynamic: tuple[At, ...] = ()` insert:

```python
    unresolved: tuple[Unresolved, ...] = ()
```

(Only the first four fields of `Enforcement` are ever passed positionally — `source_check.py:133` and the tests — so
inserting after `dynamic` moves no caller.)

- [ ] **Step 7: Select, fail strict on, and say the unresolved imports in `enforcement.py`**

In `xarch/modules/rules/application/logic/enforcement.py`:

Replace the docstring lines 7–9:

```
    dynamic    a use, in a file read, of what the language of the app imports by a computed or string name with,
               the names its data file lists; the import rules cannot see what those import
    drift      an init file (`files` in the profile) that is missing, or pinned and not what `init` would write now
```

with:

```
    dynamic    a use, in a file read, of what the language of the app imports by a computed or string name with,
               the names its data file lists; the import rules cannot see what those import
    unresolved an import, in a file read, naming a place of the app (relative, or by an alias the project maps) the
               reader found no file or folder for, with the module as written; the import rules cannot see what it
               names
    drift      an init file (`files` in the profile) that is missing, or pinned and not what `init` would write now
```

Replace line 14:

```
changed, the skips, the dynamic imports, the weak checks, the keys whose check reads a fact the language supplies only
```

with:

```
changed, the skips, the dynamic imports, the imports the reader could not follow, the weak checks, the keys whose
check reads a fact the language supplies only
```

(Leave the rest of that paragraph as it is; re-wrap nothing else. Lines stay under 140 characters.)

In the import from `published` (lines 31–45) add `UNRESOLVED,` after `UNPLACED,` and `Unresolved,` after `Loosened,`:

```python
from xarch.modules.rules.domain.published import (
    APPROXIMATE,
    DYNAMIC,
    GUARDS_OFF,
    INIT_FILES,
    SKIPPED,
    UNGOVERNED,
    UNPLACED,
    UNRESOLVED,
    VACUOUS,
    WEAK,
    At,
    Drift,
    Loosened,
    Unresolved,
    Weak,
)
```

Right after the `dynamic` function (after line 59) insert:

```python


def unresolved(files: Iterable[SourceFile]) -> list[Unresolved]:
    """Each import of the files that the reader could not follow, the files in the order given and the imports of each
    by line: a reader need not hand them over in that order."""
    return [Unresolved(file.name, i.line, i.written) for file in files
            for i in sorted(file.imports, key=lambda i: i.line) if i.unresolved]
```

In `strict_findings`, right after the line `    found += [Finding(DYNAMIC, at) for at in enforcement.dynamic]` insert:

```python
    found += [Finding(UNRESOLVED, item) for item in enforcement.unresolved]
```

Replace `detail` (lines 99–113) with:

```python
def detail(item: str | Drift | At | Unresolved | Weak | Shortfall) -> str:
    """A finding's item in words: a guard or a file by its name, an init file with its state, a place as
    `<file>:<line>`, an import the reader could not follow as its place, its module as written and that it names no
    file of the app, a weak check as its place (the file alone for a whole file) and its message, a key whose check
    reads a fact partly as the key, the fact and what the reader misses."""
    match item:
        case Drift(path, state):
            return f"{'/'.join(path)} is {state}"
        case At(file, line):
            return f"{file}:{line}"
        case Unresolved(file, line, written):
            return f'{file}:{line}: import "{written}" names no file of the app'
        case Weak(file=file, line=line, message=message):
            return f"{file}{f':{line}' if line else ''}: {message}"
        case Shortfall(address, fact, note):
            return approximation(address, fact, note or "")
        case _:
            return item
```

- [ ] **Step 8: Re-export from the contract and label the section**

In `xarch/modules/rules/contract/__init__.py`, in the import from `published` (lines 12–42) add `UNRESOLVED,` after
`UNPLACED,` and `Unresolved,` after `Translation,`. In `__all__` (line 45) change
`"INIT_FILES", "SKIPPED", "DYNAMIC",` to `"INIT_FILES", "SKIPPED", "DYNAMIC", "UNRESOLVED", "Unresolved",`.

In `xarch/cli/reports/report.py`, add `UNRESOLVED,` after `UNPLACED,` in the contract import (lines 22–36), and
replace lines 45–46 with:

```python
LABELS = {GUARDS_OFF: "guards off", UNGOVERNED: "ungoverned", INIT_FILES: "init files", SKIPPED: "skipped",
          DYNAMIC: "dynamic", UNRESOLVED: "unresolved", WEAK: "weak", APPROXIMATE: "approximate",
          VACUOUS: "reads nothing", UNPLACED: "litmus"}
```

- [ ] **Step 9: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/modules/rules tests/cli -q`
Expected: all pass, including `test_every_section_of_the_enforcement_has_a_label`.

- [ ] **Step 10: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!` (fix any finding by hand; never `--fix`).

- [ ] **Step 11: Commit**

```bash
git add xarch/modules/rules/domain/published.py xarch/modules/rules/domain/outcomes.py \
  xarch/modules/rules/application/logic/enforcement.py xarch/modules/rules/contract/__init__.py \
  xarch/cli/reports/report.py tests/modules/rules/builders.py \
  tests/modules/rules/application/logic/test_enforcement.py tests/modules/rules/application/logic/test_imports.py
git commit -m "The enforcement section unresolved: each import the reader could not follow, by file, first line and module as written, files in the order read and each file's imports by line, is a strict finding right after the dynamic imports, said as <file>:<line>: import \"<written>\" names no file of the app; an import written by an alias and resolved below the root is checked as an absolute one and never listed

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The view and the report: the text line and the JSON key

**Files:**
- Modify: `xarch/modules/rules/contract/__init__.py:44-58,95-116`
- Modify: `xarch/cli/reports/report.py:96-97,154`
- Test: `tests/cli/reports/test_report.py`

**Interfaces:**
- Consumes: `Unresolved`, `UNRESOLVED`, `LABELS[UNRESOLVED]` (Task 1).
- Produces:
  - `xarch.modules.rules.contract.UnresolvedView(item: Unresolved, sentence: str)`, frozen dataclass, in `__all__`.
  - `EnforcementView.unresolved: tuple[UnresolvedView, ...] = ()` — the **last** field of `EnforcementView`
    (it is built positionally in `SourceCheckService.view()`; pass it by keyword).
  - Text: `  unresolved:  <sentence>` per item, after the `dynamic` line, before the `weak` lines.
  - JSON: `enforcement["unresolved"] == [{"file", "line", "written"}, ...]`, right after `"dynamic"`.

- [ ] **Step 1: Write the failing report tests (T9–T11)**

In `tests/cli/reports/test_report.py`, add `Unresolved,` and `UnresolvedView,` (after `Translation,`) to the contract
import (lines 10–22), so it reads:

```python
from xarch.modules.rules.contract import (
    SECTIONS,
    AppChecked,
    ApproximateView,
    At,
    EnforcementView,
    ExcludedView,
    FindingView,
    KnownName,
    OwnCheckView,
    Translation,
    Unresolved,
    UnresolvedView,
    Weak,
)
```

Append to the end of the file:

```python


LOST = UnresolvedView(Unresolved("app/domain/services.py", 3, ".ordr"),
                      'app/domain/services.py:3: import ".ordr" names no file of the app')
GONE = UnresolvedView(Unresolved("tests/test_a.py", 1, "..gone"),
                      'tests/test_a.py:1: import "..gone" names no file of the app')


def test_each_import_the_reader_could_not_follow_has_a_line_of_its_own_after_the_dynamic_imports_and_before_weak():
    state = EnforcementView(dynamic=(At("app/kernel/dyn.py", 3),), weak=(OLD,), unresolved=(LOST, GONE))
    assert lines(state=state) == [
        *OK, "  dynamic:     1 dynamic import (app/kernel/dyn.py:3)",
        '  unresolved:  app/domain/services.py:3: import ".ordr" names no file of the app',
        '  unresolved:  tests/test_a.py:1: import "..gone" names no file of the app',
        "  weak:        tests/fakes/r.py:1: FakeR does not define get, which R declares"]
    assert lines(state=EnforcementView()) == OK


def test_every_import_the_reader_could_not_follow_has_its_line_however_many_there_are():
    many = tuple(UnresolvedView(Unresolved("app/a.py", n, ".x"), f'app/a.py:{n}: import ".x" names no file of the app')
                 for n in range(1, 8))
    assert lines(state=EnforcementView(unresolved=many)) == [
        *OK, *(f'  unresolved:  app/a.py:{n}: import ".x" names no file of the app' for n in range(1, 8))]


def test_the_json_document_lists_each_import_the_reader_could_not_follow_and_none_as_an_empty_list():
    state = EnforcementView(unresolved=(LOST, GONE))
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["unresolved"] == [
        {"file": "app/domain/services.py", "line": 3, "written": ".ordr"},
        {"file": "tests/test_a.py", "line": 1, "written": "..gone"}]
    keys = list(document["enforcement"])
    assert keys.index("unresolved") == keys.index("dynamic") + 1
    empty = json.loads(json_document("web", Origin("web"), AppChecked((), EnforcementView(), {}, True), False))
    assert empty["enforcement"]["unresolved"] == []


def test_an_import_the_reader_could_not_follow_is_listed_under_strict_by_its_sentence():
    state = EnforcementView(strict=(FindingView("unresolved", LOST.sentence),), unresolved=(LOST,))
    assert lines(state=state, strict=True) == [
        *OK, f"  unresolved:  {LOST.sentence}", "strict:      1 finding fails the check",
        f"    unresolved: {LOST.sentence}"]
```

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 300 uv run pytest tests/cli/reports/test_report.py -q`
Expected: collection error `ImportError: cannot import name 'UnresolvedView' from 'xarch.modules.rules.contract'`.

- [ ] **Step 3: Add `UnresolvedView` and `EnforcementView.unresolved`**

In `xarch/modules/rules/contract/__init__.py`:

In `__all__`, change `"Drift", "FindingView", "ExcludedView", "EnforcementView",` to
`"Drift", "FindingView", "ExcludedView", "UnresolvedView", "EnforcementView",`.

Right after the `OwnCheckView` class (after line 92, `    said: str`), insert:

```python


@dataclass(frozen=True)
class UnresolvedView:
    """An import the reader could not follow, as the enforcement section shows it: the import (its file as shown, its
    first line and its module as the source writes it), and all of it in words."""
    item: Unresolved
    sentence: str
```

Replace the `EnforcementView` docstring and fields (lines 96–116) with:

```python
class EnforcementView:
    """The state of the check's own enforcement, beside its violations, as the enforcement section shows it: the
    files no part governs, and the top folders holding them (each once, in order); the init
    files missing or changed; the skipped tests and dynamic imports; the checks met to the letter only; the findings
    `--strict` fails on; the folders the profile excludes; how the language of the app is named; the keys whose
    check reads a fact the language supplies only partly, each in words; the checks the profile writes itself,
    each with how many facts it read in the project; the public names only the tests use that the profile
    accepts; the pairs of classes no-twins accepts as translations; and the imports of the files read that the
    reader could not follow, each in words."""
    ungoverned: tuple[str, ...] = ()
    ungoverned_folders: tuple[str, ...] = ()
    init_files: tuple[Drift, ...] = ()
    skipped: tuple[At, ...] = ()
    dynamic: tuple[At, ...] = ()
    weak: tuple[Weak, ...] = ()
    strict: tuple[FindingView, ...] = ()
    excluded: tuple[ExcludedView, ...] = ()
    language: str = ""
    approximate: tuple[ApproximateView, ...] = ()
    checks: tuple[OwnCheckView, ...] = ()
    known: tuple[KnownName, ...] = ()
    translated: tuple[Translation, ...] = ()
    unresolved: tuple[UnresolvedView, ...] = ()
```

(Keep the `@dataclass(frozen=True)` line above `class EnforcementView:` as it is.)

Why `item: Unresolved` and not four copied fields: see "Spec deviation" at the top of this plan — copying
`file, line, written` into the view is a no-twins violation of xarch's own architecture.

- [ ] **Step 4: Print the line and the JSON key**

In `xarch/cli/reports/report.py`, right after line 97 (the `dynamic` text line, inside `_enforcement_lines`) insert:

```python
    lines += [_line(LABELS[UNRESOLVED], item.sentence, 2) for item in state.unresolved]
```

so it sits between the `if state.dynamic:` block and `for weak in state.weak:`.

In `_enforcement_document`, right after the line `        "dynamic": {"count": len(state.dynamic), "at": _at(state.dynamic)},` insert:

```python
        "unresolved": [{"file": item.item.file, "line": item.item.line, "written": item.item.written}
                       for item in state.unresolved],
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `timeout 300 uv run pytest tests/cli tests/modules/rules -q`
Expected: all pass.

- [ ] **Step 6: Lint**

Run: `uv run ruff check`
Expected: `All checks passed!`

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules/contract/__init__.py xarch/cli/reports/report.py tests/cli/reports/test_report.py
git commit -m "xarch check shows each import the reader could not follow on a line of its own, unresolved:, after the dynamic imports and before the weak checks, and its JSON enforcement always holds unresolved, each {file, line, written}, right after dynamic; the view holds the published value and the sentence the logic writes, never a copy of its fields

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Wiring: the check fills the section from the files it read; `--strict` fails on it

**Files:**
- Modify: `xarch/modules/rules/application/services/source_check.py:24-56,133-138`
- Modify: `xarch/cli/commands/check.py:28-34`
- Test: `tests/bootstrap/test_enforcement.py`, `tests/bootstrap/test_check_enforcement.py`

**Interfaces:**
- Consumes: `enforcement.unresolved`, `enforcement.detail` (Task 1); `UnresolvedView`, `EnforcementView.unresolved`
  (Task 2).
- Produces: `SourceCheckService.check(...)` returns an `Enforcement` whose `unresolved` lists the app's governed and
  test files' unresolved imports (parse failures already dropped at `source_check.py:86-87`), and whose `strict` holds
  their findings; `view()` builds `UnresolvedView(item, enforcement.detail(item))` for each.

- [ ] **Step 1: Write the failing end-to-end tests (T12 and Review Focus 1–5)**

In `tests/bootstrap/test_enforcement.py`, change line 7 to:

```python
from xarch.modules.rules.contract import At, Drift, EnforcementView, Unresolved, Weak
```

and append to the end of the file:

```python


def test_an_import_the_reader_could_not_follow_is_listed_in_an_app_file_and_in_a_test_file(tmp_path):
    found = enforcement(tmp_path, {"kernel/a.py": "x = 1\nfrom .ordr import X\n"},
                        {"kernel/test_b.py": "from .gone import Y\n"})
    assert [view.item for view in found.unresolved] == [Unresolved("app/kernel/a.py", 2, ".ordr"),
                                                        Unresolved("tests/kernel/test_b.py", 1, ".gone")]
    assert [view.sentence for view in found.unresolved] == [
        'app/kernel/a.py:2: import ".ordr" names no file of the app',
        'tests/kernel/test_b.py:1: import ".gone" names no file of the app']


def test_a_relative_import_of_a_file_that_exists_is_not_listed(tmp_path):
    found = enforcement(tmp_path, {"kernel/a.py": "x = 1\nfrom .order import X\n", "kernel/order.py": "X = 1\n"})
    assert found.unresolved == ()
    assert [f for f in found.strict if f.key == "unresolved"] == []


def test_the_unresolved_imports_of_a_file_are_listed_by_line_whatever_the_reader_yields_first(tmp_path):
    text = ("def f():\n    from .inner import Z\n    return Z\n\n\nfrom .outer import W\nfrom ...above import V\n"
            "from .gone import (\n    a,\n    b,\n)\n")
    found = enforcement(tmp_path, {"kernel/c.py": text})
    assert [(view.item.line, view.item.written) for view in found.unresolved] == [
        (2, ".inner"), (6, ".outer"), (7, "...above"), (8, ".gone")]
    assert [f.detail for f in found.strict if f.key == "unresolved"] == [view.sentence for view in found.unresolved]
```

In `tests/bootstrap/test_check_enforcement.py`:

Add `import typer` after `import pytest` (line 7) — keep the imports sorted as ruff's isort wants: third-party block
`import pytest`, `import typer`, `from typer.testing import CliRunner`.

In `test_the_json_enforcement_always_holds_every_key`, right after the line `        "dynamic": {"count": 0, "at": []},`
insert:

```python
        "unresolved": [],
```

Append to the end of the file:

```python


LOST = 'app/kernel/a.py:2: import ".ordr" names no file of the app'


def test_an_import_the_reader_could_not_follow_is_listed_and_fails_only_strict(tmp_path):
    (tmp_path / "app/kernel/a.py").write_text("x = 1\nfrom .ordr import X\n")
    result = check()
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines() == ["OK: no violations", "enforcement", "  profile:     web (bundled)",
                                          f"  unresolved:  {LOST}"]
    strict = check("--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", f"    unresolved: {LOST}"]
    document = json.loads(check("--format", "json").stdout)
    assert document["ok"] is True
    assert document["enforcement"]["unresolved"] == [{"file": "app/kernel/a.py", "line": 2, "written": ".ordr"}]
    assert document["enforcement"]["strict_failures"] == [{"key": "unresolved", "detail": LOST}]
    assert json.loads(check("--strict", "--format", "json").stdout)["ok"] is False


def test_the_help_of_strict_names_the_imports_the_reader_could_not_follow():
    command = typer.main.get_command(app).commands["check"]
    strict = next(param for param in command.params if "--strict" in param.opts)
    assert "dynamic imports, imports the reader could not follow, checks met to the letter" in strict.help
```

(The project fixture of this file runs `init --profile web` and `new module docs` in `tmp_path`, so `tmp_path / "app/kernel"`
exists. The planner ran this exact project on the branch: with `app/kernel/a.py` as above, `xarch check` prints no
violation and no other enforcement line.)

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 600 uv run pytest tests/bootstrap/test_enforcement.py tests/bootstrap/test_check_enforcement.py -q`
Expected: the three new `test_enforcement.py` tests fail (`found.unresolved` is `()`: the first and third with
`assert [] == [...]`; `test_a_relative_import_of_a_file_that_exists_is_not_listed` **passes** already, pinning Review
Focus 5); `test_the_json_enforcement_always_holds_every_key` passes already (the key exists since Task 2, empty);
`test_an_import_the_reader_could_not_follow_is_listed_and_fails_only_strict` fails on the stdout lines; the help test
fails on the `in strict.help` assertion.

- [ ] **Step 3: Fill the section in the service**

In `xarch/modules/rules/application/services/source_check.py`, add `UnresolvedView,` after `OwnCheckView,` in the
contract import (lines 24–30):

```python
from xarch.modules.rules.contract import (
    ApproximateView,
    EnforcementView,
    ExcludedView,
    FindingView,
    OwnCheckView,
    UnresolvedView,
)
```

Replace the last line of `view()` (line 56):

```python
            state.known, state.translated)
```

with:

```python
            state.known, state.translated,
            unresolved=tuple(UnresolvedView(item, enforcement.detail(item)) for item in state.unresolved))
```

In `_enforcement`, replace line 136:

```python
                           dynamic=tuple(enforcement.dynamic([*app, *tests], rules)), weak=tuple(weak),
```

with:

```python
                           dynamic=tuple(enforcement.dynamic([*app, *tests], rules)),
                           unresolved=tuple(enforcement.unresolved([*app, *tests])), weak=tuple(weak),
```

(`check()` already passes `app` and `test_files` with the unparsed files dropped, lines 86–87, and then sets
`strict=enforcement.strict_findings(state)` at line 122, so the strict findings follow with no further change.)

- [ ] **Step 4: Name them in the `--strict` help**

In `xarch/cli/commands/check.py`, replace lines 31–32:

```python
         "ungoverned files, missing or changed init files, skipped tests, dynamic imports, checks met to the letter "
         "only (weak), approximate keys, checks of the profile's own that read nothing, and a part redefined without "
```

with:

```python
         "ungoverned files, missing or changed init files, skipped tests, dynamic imports, imports the reader could "
         "not follow, checks met to the letter only (weak), approximate keys, checks of the profile's own that read "
         "nothing, and a part redefined without "
```

(The next line, `"the litmus the compared profile gives it. Every other way ..."`, stays as it is; the joined string
reads `... nothing, and a part redefined without the litmus the compared profile gives it. ...`.)

- [ ] **Step 5: Run the tests to see them pass**

Run: `timeout 600 uv run pytest tests/bootstrap/test_enforcement.py tests/bootstrap/test_check_enforcement.py tests/modules/rules tests/cli -q`
Expected: all pass.

- [ ] **Step 6: Lint and xarch's own check**

Run: `uv run ruff check && uv run xarch check && uv run xarch check --strict`
Expected: `All checks passed!`, then `OK: no violations` twice with exit 0 (xarch's own code has no relative import, so
no `unresolved:` line; no `weak:` line naming `Unresolved` or `UnresolvedView` — both are now used by the app).

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules/application/services/source_check.py xarch/cli/commands/check.py \
  tests/bootstrap/test_enforcement.py tests/bootstrap/test_check_enforcement.py
git commit -m "xarch check lists the imports of the app's governed files and of the tests that the reader could not follow, and --strict exits 1 on each, listing it under strict: as unresolved: <file>:<line>: import \"<written>\" names no file of the app; a relative import of a file that exists is never listed, and the --strict help names them after the dynamic imports

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:342,371-377,398,433-435,446-449`
- Modify: `CHANGELOG.md:46` (append an entry after the 3.1 reader entry)
- Test: `tests/architecture/` (T14), `tests/bootstrap/test_docs_templates.py`, `tests/bootstrap/test_docs.py`,
  `tests/bootstrap/test_recorded_corpora.py`, then the whole suite

**Interfaces:**
- Consumes: the finished behaviour of Tasks 1–3.
- Produces: docs only.

- [ ] **Step 1: README — the JSON example**

In `README.md`, replace

```
    "dynamic": {"count": 0, "at": []},
    "weak": [],
```

with

```
    "dynamic": {"count": 0, "at": []},
    "unresolved": [],
    "weak": [],
```

- [ ] **Step 2: README — the JSON items and the `strict_failures` keys**

Replace

```
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `weak` items `{"rule", "file", "line",
  "message", "fix"}` (`fix` is `null` for a weak check that has none); `approximate` items `{"key", "fact", "note"}`;
  `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `ungoverned`, `init_files`,
  `skipped`, `dynamic`, `weak`, `approximate`, `vacuous` (a check of the profile's own that read nothing), `litmus` (a
```

with

```
  `changed`; `skipped.at` and `dynamic.at` items `{"file", "line"}`; `unresolved` items `{"file", "line", "written"}`,
  each import the reader could not follow, at its first line, with the module as the source writes it; `weak` items
  `{"rule", "file", "line", "message", "fix"}` (`fix` is `null` for a weak check that has none); `approximate` items
  `{"key", "fact", "note"}`; `strict_failures` items `{"key", "detail"}`, `key` one of `guards_off`, `ungoverned`,
  `init_files`, `skipped`, `dynamic`, `unresolved`, `weak`, `approximate`, `vacuous` (a check of the profile's own
  that read nothing), `litmus` (a
```

- [ ] **Step 3: README — the text example and the bullet**

Replace

```
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
```

with

```
  dynamic:     1 dynamic import (app/kernel/dyn.py:3)
  unresolved:  app/modules/docs/domain/services.py:3: import ".ordr" names no file of the app
  weak:        tests/fakes/repo.py:1: FakeRepo does not define save, which Repo declares (app/...)
```

Replace

```
  (for Python, `importlib.import_module`, `importlib.__import__` and the builtin `__import__`), so it needs no entry in
  the profile; the import rules cannot see what it imports.
```

with

```
  (for Python, `importlib.import_module`, `importlib.__import__` and the builtin `__import__`), so it needs no entry in
  the profile; the import rules cannot see what it imports.
- `unresolved`: each import, in the files read, that names a place of the app (relative, or by an alias the project
  maps) the reader found no file or folder for, at its first line, with the module as written, one line each; the
  import rules cannot see what it names.
```

- [ ] **Step 4: README — the `--strict` paragraph**

Replace

```
every guard left off); each ungoverned file; each missing or changed init file; each skip; each dynamic import; each weak finding;
```

with

```
every guard left off); each ungoverned file; each missing or changed init file; each skip; each dynamic import; each
unresolved import; each weak finding;
```

- [ ] **Step 5: CHANGELOG**

In `CHANGELOG.md`, right after the line ending `relative import sees no change.` (line 46, the end of the 3.1 reader
entry under `## [Unreleased]` / `### Changed`) and before the blank line that precedes `## [0.2.0] - 2026-11-18`,
insert a blank line and:

```
- A new enforcement section, `unresolved`, lists each import the reader could not follow by file and line with the
  module as written, in text (`unresolved:  app/domain/services.py:3: import ".ordr" names no file of the app`) and
  under the JSON key `unresolved` (`{"file", "line", "written"}`), and `--strict` fails on each, as on a dynamic
  import (`strict_failures` key `unresolved`). A project with no such import sees only the empty JSON key
  `"unresolved": []`.
```

Check: `sed -n 36,56p CHANGELOG.md` shows the 3.1 entry, a blank line, the new entry, a blank line, `## [0.2.0] ...`.

- [ ] **Step 6: Run the docs tests (T14)**

Run: `timeout 600 uv run pytest tests/architecture tests/bootstrap/test_docs.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_recorded_corpora.py -q`
Expected: all pass; no file under `tests/bootstrap/corpora/` is changed (`git status --short tests/bootstrap/corpora`
prints nothing).

- [ ] **Step 7: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-3-2/regenerate_docs.py` (outside the worktree):

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
mkdir -p /tmp/xarch-3-2
uv run python -I /tmp/xarch-3-2/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs/cli docs/web docs/xarch
```

Expected: `written`; `git status` shows nothing under `docs/` besides the spec and plan under `docs/superpowers/` (the
workflow commits those); `git diff --stat` prints nothing. A moved golden doc is a defect of this step: do not keep or
hand-edit it; restore it with `git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 8: Run the gates**

```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
git status --short -- architecture.yaml xarch/architectures tests/bootstrap/corpora
```

Expected: `All checks passed!`; `OK: no violations` with exit 0 for both checks; the profile check exits 0; the last
command prints nothing.

Then the full suite (it takes over two minutes; run it in the background and read it when it ends):

```bash
timeout 1200 uv run pytest -q > /tmp/xarch-3-2/pytest.log 2>&1; echo "exit=$?" >> /tmp/xarch-3-2/pytest.log
tail -5 /tmp/xarch-3-2/pytest.log
```

Expected: `N passed` (plus any pre-existing skips) and `exit=0`.

- [ ] **Step 9: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "The README's enforcement section and JSON contract name unresolved, each import the reader could not follow at its first line with the module as written, {file, line, written}, among the keys of strict_failures and what --strict fails on, and the CHANGELOG says so under Unreleased; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review (run by the planner against the spec)

- Behavior 1 (selection by `Import.unresolved` alone; absolute, resolved relative, aliased-resolved never listed):
  Task 1 T1, T8; Task 3 `test_a_relative_import_of_a_file_that_exists_is_not_listed`.
- Behavior 2 (app governed files + test files; unparsed dropped): Task 3 Step 3 passes `[*app, *tests]` after the
  existing `error is None` filter; Task 3 test with a test file.
- Behavior 3 (item = `SourceFile.name`, `Import.line`, `Import.written`; one statement one item): Task 1 T1 (two
  names, one item); Task 3 multi-line test.
- Behavior 4 (files in order read, by line within a file): Task 1 T2; Task 3 function-body test.
- Behavior 5 (the sentence): Task 1 T5, T8; Task 3 sentence assertions.
- Behavior 6 (text line, label, placement, no cap, none when empty): Task 2 T9 and the seven-line test.
- Behavior 7 (JSON key always present, items, after `dynamic`): Task 2 T10; Task 3 always-present-keys test.
- Behavior 8 (`strict_failures` filled without `--strict`): Task 3 CLI test (JSON without `--strict`).
- Behavior 9 (`UNRESOLVED` in `SECTIONS` after `DYNAMIC`; strict order; exit 1; `    unresolved: <sentence>`): Task 1
  T4; Task 2 T11; Task 3 CLI test.
- Behavior 10 (no change for a project without one but the empty key): Task 3 always-present-keys test; Task 4 gates
  (xarch's own check unchanged).
- Behavior 11 (help): Task 3 Step 4 and its test.
- Behavior 12, 13 (README, CHANGELOG): Task 4 Steps 1–5.
- Shape: all followed except `UnresolvedView`, changed to `(item, sentence)` for the reason under "Spec deviation".
- Out of scope respected: no reader, profile, corpora, `testing.md` or golden-doc edits; golden docs regenerated and
  diffed (Task 4 Step 7).
- Gates: Task 4 Step 8.
- Placeholder scan: no TBD/TODO; every code step shows its code.
- Names: `unresolved` (logic function), `Unresolved` (value), `UNRESOLVED` (key), `UnresolvedView(item, sentence)`,
  `EnforcementView.unresolved`, `Enforcement.unresolved`, builders `aliased` / `unresolved` — the same in every task.
<!-- task-pipeline: validated -->
