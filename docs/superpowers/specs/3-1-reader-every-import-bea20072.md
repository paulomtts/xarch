# 3.1 Reader: every import of the app resolved to the place it names

Card `bea20072`, subtask of `3c7754c4`. Release step 6 of the 0.3.0 merged order, the reader half of note step 5a;
the enforcement half (the `unresolved` section) is card 3.2. Stacked on step 5 (card `c61068a6`, branch tip `5d0cd83`).

Today the Python reader binds a name to a `Ref` only through an absolute import. `from .order import Order` binds
`Order` to None, so every check that reads uses, calls, constructions, class bases or mock specs is silent on code that
imports its own package relatively. After this step the reader follows the import however it is written, records
whether it could follow it, and the language says so as a fact the keys that read Refs need.

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`. `LN` is `language-neutral-design.md`, `R3` is
`0.3.0-cohesion-review-3.md`.

- LN lines 17-18 (ruling): Python belongs only in the reader adapter and the data files under
  `xarch/architectures/presets/`.
- LN lines 37-39 (default 1): aliases are read by the reader from the project's config; imports the reader cannot
  follow are listed under `unresolved` (the listing is 3.2's).
- LN lines 68-81 (facts read): `parsed.py:36-39`, `fs_source_tree.py:646`; import rules already follow relative
  imports (`kernel/logic/source.py`), only Refs do not; the app's names are told apart by their first step
  (`facts.py:193`, `filters.py:110`, `stand_ins.py:194`); zero relative imports in the repository and in each archive.
- LN 1.1, lines 130-153: the neutral form of a `Ref` and its new docstring, word for word.
- LN 1.2, lines 155-166: what the reader supplies; `relative` and `up` kept; `Import.unresolved`; the Python example
  `("app", "domain", "order", "Order")`; the fact `import.resolved` and its text; Python lists it `exact`.
- LN 1.3, lines 168-184: aliases are the reader's, no profile key and no data-file key; an alias it cannot read gives
  unresolved imports.
- LN 1.4, lines 186-189: `python.yaml` gains only `import.resolved: exact`; `importing:` stays.
- LN 1.5, lines 191-208, first and third bullets: the "absolute import" texts reworded; the code paths need no change;
  `NEEDS` gains `import.resolved` on about 10 entries, held by `test_needs_agree.py`; the `keys.yaml` before/after
  wording (lines 205-208). The second bullet (the `unresolved` section, lines 196-198) is 3.2's.
- LN 1.6, lines 210-214: no refusal at load; a language without the fact gets the existing refusal.
- LN 1.7, lines 216-227, first and third bullets: the three real-reader tests; the corpora do not move. The second
  bullet (hand-built `@app/...` facts listed under `unresolved`) is 3.2's.
- LN 11, line 1043; LN 13, lines 1087-1089 and 1091 (row 1090, enforcement, is 3.2's): the places that change.
- LN dodges, lines 1147-1150 and 1165: relative imports left unresolved because the repository has none; aliases
  resolved in the checking code or by a profile key; silence on an import the reader cannot follow; corpora or golden
  docs moving "a little".
- LN not verified, line 1185: that every recorded finding stays; this step's gates decide it.
- R3 line 263: step 6 is note 5a, after step 3 (the `keys.yaml` texts).
- R3 lines 228, 229, 232 (O4, O5, O8): each step its README and CHANGELOG lines under `[Unreleased]`; the golden docs
  `docs/{cli,web,xarch}/testing.md` regenerated and their diff read, never edited by hand.

Today's key names are used below (`parts.<part>.types_only`, `parts.<part>.built_by`); the note's later names
(`holds.classes.built_by`, the mode `types_only` of an `imports.may` entry) arrive in release step 12 and later.

## Observable behaviour

### B1. A relative `from` import binds the resolved place

In a file read by `SourceTree.read(root, paths, ...)` at `path` (steps below `root`), the package the file lies in is
`(root.name, *path[:-1])`; this holds for `__init__.py` too (it stands for its folder, whose steps are `path[:-1]`). A
`from` import with level `n` (`n` dots) names the package `n - 1` folders above that one (`Import.up`), then its
`module` steps.

- `from .order import Order` in `app/domain/services.py` binds `Order` to `("app", "domain", "order", "Order")`,
  exactly as `from app.domain.order import Order` does.
- `from . import order` there binds `order` to `("app", "domain", "order")`; `order.Order()` is then a call of
  `("app", "domain", "order", "Order")`.
- `from ..kernel.errors import Failed` in `app/domain/services.py` binds `("app", "kernel", "errors", "Failed")`;
  `from .. import kernel` binds `("app", "kernel")`.
- In `app/domain/__init__.py`, `from .order import Order` binds `("app", "domain", "order", "Order")`.
- An alias keeps the resolved place: `from .order import Order as O` binds `O` to `("app", "domain", "order",
  "Order")`; `from . import order as o` binds `o` to `("app", "domain", "order")`.
- Every reading that goes through a scope sees the resolved place, in every scope that binds the name (module, class,
  function, lambda): uses (annotations included), calls (callee and keyword values such as a mock's `spec=`), class
  bases, constructions, function references, method calls, parameter calls and the module's functions. The scope
  rules do not change: a name bound twice to different places, or also bound another way, is still None.
- A test file read below the tests root resolves the same way, its first step being the tests root's name
  (`("tests", "fakes", "repo", "FakeRepo")`); the checks that compare a first step with the app's root then treat it
  as not of the app, as they treat an absolute `from tests.fakes.repo import ...` today.

### B2. `Import` records whether the reader could follow it

`xarch.kernel.source.Import` gains `unresolved: bool = False`, its last field. Its docstring says: the import names a
place of the code being read (relative, or by an alias the project maps) that the reader found no file or folder for.
For the Python reader, read through `read(root, ...)`:

- An absolute import (`import x`, `from x import y`): always `unresolved=False`. Absolute imports are not checked for
  existence (an outside package is not below the root).
- A relative import whose climb stays at or below the root, and whose target exists below the root:
  `unresolved=False`. The target for `from .<module> import ...` is the module's file `<folder>/<module steps>.py` or
  the folder `<folder>/<module steps>/`; for `from . import x` / `from .. import x` (no module) it is the folder the
  climb reaches. Existence is read through the adapter's `FileSystem`, never by opening or importing anything.
- A relative import that climbs above the root (`from ... import x` in `app/a.py`, whose package is `("app",)`):
  `unresolved=True`, and every name it binds is None.
- A relative import whose target does not exist (`from .ordr import Order` with no `ordr.py` and no `ordr/` beside the
  file): `unresolved=True`, and every name it binds is None (LN 1.1: a Ref is None for an import the reader could not
  follow).
- `module`, `names`, `relative`, `up`, `standard`, `written`, `every`, `last` keep today's values for every import, so
  the import rules (`kernel/logic/source.py`) and every import finding are unchanged.
- A star import (`from .order import *`) gets `unresolved` like any other relative import; it still binds no name.

`SourceTree.parsed(text)` (no file, no root; used for examples, asking, holding) has no location to climb from: a
relative import there binds None and is `unresolved=True`, since the reader could not follow it. Absolute imports are
read as above. The port does not widen.

### B3. Aliases from the project's config

Python has no alias map in its tools' config; `import a.b as c` and `from x import y as z` are bindings the reader
already follows. The Python reader therefore reads no config file for aliases. No profile key, no data-file key and
no code outside the reader adapter learns about aliases (LN 1.3; dodge line 1149).

### B4. The fact `import.resolved`

- `FACTS` (`xarch/profile_values/capabilities.py`) gains, after `import.standard`, `"import.resolved": "every import of
  the app is followed to the place it names, however written"`.
- `xarch/architectures/presets/language/python.yaml` `supplies:` gains `import.resolved: exact`, after
  `import.standard`.
- `NEEDS` (`xarch/modules/spec/domain/key_table.py`): every entry whose facts include `use` or `call` gains
  `import.resolved`. That is exactly these ten: `parts.<part>.types_only` and `tiers.<tier>.types_only` (through
  `_TYPES_ONLY`), `parts.<part>.built_by`, `parts.<part>.shared`, `parts.<part>.uses.never` and
  `tiers.<tier>.uses.apply_never` (through `_NEVER_USE`), `testing.skips`, `testing.mocks`, `guards.stand-ins`,
  `guards.no-twins.translated`. No other entry changes.
- The rules' vocabulary (`xarch/modules/rules/domain/vocabulary.py`): the kinds whose facts are Refs need it too: `use`,
  `call`, `construction`, `function-reference`. `method-call` (what no import names) and the import kinds do not.
  `profile explain <key>` and `profile explain <key> --rule` then show the same facts for every key of
  `test_needs_agree.py`'s `EVERY_KEY`; if a kind's needs disagree with the table, the table is right and the kinds are
  adjusted until that test passes.
- A language whose data file does not list `import.resolved` is refused on those keys with the existing message ("its
  check reads import.resolved (...), which the language ... does not supply"); one that lists it `{partial: ...}` has
  them listed as approximate. Nothing new is built for this (LN 1.6). Every profile the repository holds loads
  unchanged: no profile line changes.

### B5. Texts that said "absolute import"

Reworded so that none presumes a name is read only through an absolute import. Meaning otherwise unchanged:

- `parsed.py` `Ref` docstring: LN 1.1's "After" text, word for word (LN lines 149-153).
- `fs_source_tree.py` module docstring (lines 4-7) and `_scope` docstring (line 609): a name is a Ref when its scope
  binds it with an import, however written, that the reader follows, and nothing else; a relative import that climbs
  above the root or names nothing below it binds None and is marked unresolved.
- `keys.yaml:343` and `:395`: "read through absolute imports only" / "read through absolute imports" become "read
  through every import, however written" (LN lines 205-208).
- `keys.yaml:140` and `:158`: "Dotted names are what an absolute import binds" / "a dotted name as an absolute import
  binds it" become "what an import binds" / "as an import binds it" (an outside name is absolute in any case).
- `facts.py:49`, `twins.py:30`, `stand_ins.py:31`: "the absolute import that binds it" becomes "the import that binds
  it"; `stand_ins.py:31`'s "a name an absolute import binds" becomes "a name an import binds".
- `vocabulary.py:256` (the filter `app-package`): the text must stay true of import facts, whose path is the module as
  written; it becomes "the import names the app's own package by its root (an import written from the top)". The
  filter's behaviour does not change; relative imports stay matched by `own-code`.
- `profile_checks.py:400`: "the path an absolute import binds" becomes "the path an import binds".
- Left as they are: `kernel/source.py:14` (says what `standard` means for an absolute import, which stays true),
  `README.md:1033` (the ruff setting of projects), the test id at `test_tier_imports.py:243`.
- `tests/modules/rules/application/logic/test_types_only.py:2` docstring: "through an absolute import" becomes
  "through an import, however written".

A grep of `absolute import` over `xarch tests` afterwards finds only `kernel/source.py:14`, the test id at
`test_tier_imports.py:243`, and the docstrings that now contrast absolute with relative on purpose.

### B6. What does not move

- The recorded corpora (`tests/bootstrap/corpora/`) and their findings: no file edited; `test_recorded_corpora.py`
  passes untouched. Any change is a defect of this step (LN lines 226-227, 1165).
- The golden docs `docs/{cli,web,xarch}/testing.md`: regenerated with the repository's own generator, the diff read;
  none is expected, since none of them prints the reworded texts. A diff is a defect to explain, not to accept.
- The output of `xarch check`, `--strict` and `--json` on every project with no relative import; no new section, no new
  JSON key (3.2's).
- Every profile file the repository holds.

## Error paths

- Climb above the root: Ref None, `unresolved=True`; no exception, no message from the reader.
- Target missing: Ref None, `unresolved=True`.
- A file that is unreadable or does not parse: unchanged (`Unparsable`, no imports).
- A relative import read by `parsed(text)`: Ref None, `unresolved=True`.
- A file system error while checking existence: treated as missing (unresolved), never raised.

## Tests that prove it

Tests are written first. Examples elsewhere keep absolute `app.` imports; these tests need relative ones by nature.

### Adapter tier (`tests/modules/rules/adapters/test_fs_source_tree.py`), the real Python reader on files in `tmp_path`

Why this tier: resolution is Python knowledge that lives in the reader adapter alone; only a real `FsSourceTree` over
real files proves the climb and the existence check. A helper writes nested files (`tmp_path/"app"/"domain"/...`) and
reads them with `FsSourceTree(FileSystem()).read(tmp_path / "app", paths)`.

1. `from .order import Order` then `Order()` in `app/domain/services.py`, with `app/domain/order.py` present: the call
   is at `("app", "domain", "order", "Order")`; the import has `unresolved=False`, `relative=True`, `up=0`,
   `module=("order",)`.
2. `from . import order` then `order.Order()`: the call is at `("app", "domain", "order", "Order")`.
3. `from ..kernel.errors import Failed` and `from .. import kernel` with `app/kernel/errors.py` present: uses at
   `("app", "kernel", "errors", "Failed")` and `("app", "kernel")`.
4. In `app/domain/__init__.py`, `from .order import Order`: `("app", "domain", "order", "Order")`.
5. Aliases: `from .order import Order as O` then `O()`, and `from . import order as o` then `o.Order()`: both calls at
   `("app", "domain", "order", "Order")`.
6. The target is a folder: `from .order import Order` with `app/domain/order/` (holding an `__init__.py`) and no
   `order.py`: resolved, `unresolved=False`.
7. Missing target: `from .ordr import Order` then `Order()`: `calls == ()`, the import `unresolved=True`.
8. Climbing above the root: `from ... import x` then `x()` in `app/a.py`: no call, `unresolved=True`.
9. A resolved name reaches every reading: a class base (`class Repo(Base)` after `from .base import Base`), a mock's
   `spec=` keyword, a use in an annotation; each at its resolved place.
10. Absolute imports are unchanged: `from app.domain.order import Order` and `import os` both `unresolved=False`,
    Refs as today.
11. The existing `test_relative_imports_bind_nothing` is replaced: the same text in `app/domain/x.py` with
    `app/domain/helpers.py` present now gives a call at `("app", "domain", "helpers", "build")`.
12. `parsed(text)` with a relative import: the name binds nothing and the import is `unresolved=True`; absolute ones
    as today.

### Wired tier (`tests/bootstrap/`), the app's own check on a throwaway web project

Why this tier: LN 1.7 asks for proof through the real reader inside the real check, and these three are the failures
that pass in silence today. Each uses `tests/bootstrap/project.py` (`problems`, `source_check`, `write`); each asserts
the same finding its absolute twin gives (the same rule, line and text but for the import as written). Each test is
seen to fail on the parent commit before the reader changes.

13. `built_by` (`test_rule_ids.py` beside the `built-by` case, or `test_source_checks.py`): with
    `modules/docs/application/services/doc.py` holding `class DocService: ...`, the controller
    `modules/docs/application/controller.py` writes `from .services.doc import DocService\n\nDocService()\n`: a
    `built-by` finding at line 3, `(parts.services.built_by)`. A second case writes `from .services import doc` then
    `doc.DocService()`.
14. `types_only` (`test_rule_ids.py`, as `test_a_part_used_only_as_a_type_names_its_rule_and_its_fix` does): the copied
    web profile with `types_only: [contract]` on services; `services/doc.py` writes `from ...contract import
    Published` and calls `Published()`: one `types-only` finding at the line of the call.
15. `uses.never` (`test_never_use.py`): a relative import reaches only names of the app, and the bundled `never`
    lists name only outside names, so the test copies the web profile (as test 14 does) and adds an app name,
    `app.kernel.clock.now`, to the list `pure`. With `kernel/clock.py` holding `def now(): ...`,
    `modules/docs/domain/document.py` writes `from ....kernel.clock import now\n\ndef stamp():\n    return now()\n`:
    a `never-use` finding at line 4, `(parts.domain.uses.never)`, the same the absolute
    `from app.kernel.clock import now` gives (the test asserts both, parametrized). If the copied profile refuses an
    app name in a `never` list, the planner picks the nearest list entry the loader accepts that names an app module
    and records why.

### Spec and vocabulary tier

16. `tests/bootstrap/test_needs_agree.py` (wired): unchanged; it must pass with the new fact on both sides. Why: it
    holds `NEEDS` and the vocabulary to the same facts for every expanded key.
17. `tests/modules/spec/application/logic/test_profile_needs.py` (unit): a language that supplies everything but
    `import.resolved` refuses `parts.<part>.built_by` with the existing message naming `import.resolved`. Why: proves
    B4's refusal reaches the new fact, on hand-built `Supply` values.
18. Any test that enumerates `FACTS`, Python's `supplies`, or a kind's `needs` (`test_explained.py:118` and the like) is
    updated only where the new fact appears in its expected value.

### Gates

`uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check
architecture.yaml`, then `uv run pytest -q` in the background (over two minutes) read at the end. All pass on this
branch alone. `test_recorded_corpora.py`, `test_docs.py` and `test_docs_templates.py` pass with no corpus or golden
doc edited.

## README and CHANGELOG

- `CHANGELOG.md`, `## [Unreleased]` / `### Changed`, one paragraph bullet: the Python reader follows relative imports
  (and aliases it can read) to the place they name, so `uses.never`, `built_by`, `types_only`, `shared`, the mocks,
  `stand-ins` and the twins' translation read names imported relatively as they read absolute ones; an import it
  cannot follow is marked unresolved; the keys that read those names need the new fact `import.resolved`, which
  Python supplies `exact`.
- README: only if a section lists the facts or a language's `supplies` (none found by grep of `import.standard`); the
  `unresolved` section's lines are 3.2's.

## Out of scope

- The `unresolved` enforcement section, its text, `--strict` failure, JSON key and README section; `enforcement.py`,
  `Enforcement`, the report (card 3.2, LN 1.5 second bullet, LN line 1090).
- Hand-built `@app/...` and `unresolved=True` facts in `tests/modules/rules/builders.py` checked by the enforcement
  (LN 1.7 second bullet; 3.2).
- Any profile line, in any profile file.
- An alias source for Python (none exists); a config reader for TypeScript-style aliases (a future reader's).
- Steps 5b, 5c and later: `package`/`member`, interface marks, the `holds` kinds, type arguments of mock specs.
- Changing `Import.module` for relative imports or the import rules in `kernel/logic/source.py`.

## For the planner

- Files: `xarch/modules/rules/adapters/fs_source_tree.py` (thread the file's package and an existence check from
  `read` into `_parsed`, `_bound`/`_scope`, `_Calls`, `_classes`, `_functions`, `_module_functions`; `_imports` sets
  `unresolved`); `xarch/kernel/source.py`; `xarch/modules/rules/domain/parsed.py`; `xarch/profile_values/
  capabilities.py`; `xarch/architectures/presets/language/python.yaml`; `xarch/modules/spec/domain/key_table.py`;
  `xarch/modules/rules/domain/vocabulary.py`; the B5 texts; the tests above; `CHANGELOG.md`.
- No Python-specific code outside the reader adapter and `python.yaml`; `tests/architecture/test_agnostic.py` and
  `test_language_seam.py` enforce it.
- No comments in xarch's code (docstrings only); never `ruff --fix`; `.claude/` out of commits; nothing pushed.
- `tests/modules/rules/builders.py:124` builds `Import` positionally: the new field goes last with a default so no
  caller changes.

## Review focus

1. Existing wired tests whose app strings already hold relative imports (`tests/bootstrap/test_imports.py`'s
   conforming tree, `test_tier_imports.py`): with Refs resolved, a `uses.never`, `shared` or `built_by` finding may
   appear where none did. Each new finding is read; a test's expected value changes only if the finding is right.
2. `from . import x` where `x` is a module of the folder versus a name of its `__init__.py`: both bind
   `(*package, "x")`, and the folder exists, so both resolve.
3. A relative import inside a function or class body: it resolves through that scope as at module level.
4. A file at the root (`app/a.py`) writing `from . import b`: the package is `("app",)`, `b` binds `("app", "b")`.
5. A test file's relative import of another test file resolves to `("tests", ...)` and does not become an app name.
