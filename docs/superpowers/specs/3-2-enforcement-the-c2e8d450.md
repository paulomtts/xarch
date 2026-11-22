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
