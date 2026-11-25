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

---

# 3.1 Reader: every import of the app resolved to the place it names: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The Python reader follows a relative `from` import to the place it names, marks one it cannot follow
`unresolved`, and the keys whose checks read Refs need the new fact `import.resolved`, which Python supplies `exact`.

**Architecture:** All resolution lives in the reader adapter `xarch/modules/rules/adapters/fs_source_tree.py`.
`FsSourceTree.read` gives each file a `_Where` (its package, the root, the file system). `_from` turns a `from`
import into the place it names, and every scope reader (`_bound`, so `_scope`, `_Calls`, `_classes`, `_functions`)
binds names through it. `Import` gains `unresolved` as its last field. The fact goes into `FACTS`, `python.yaml`,
`NEEDS` and the four Ref-reading kinds of the rules' vocabulary. The texts that said "absolute import" are reworded.

**Tech Stack:** Python 3.13, `ast`, pytest, ruff, uv; xarch's own `xarch check`.

**Spec:** `docs/superpowers/specs/3-1-reader-every-import-bea20072.md` (prepended above).

## Global Constraints

- No Python-specific code outside the reader adapter and `xarch/architectures/presets/language/python.yaml`;
  `tests/architecture/test_agnostic.py` and `test_language_seam.py` enforce it.
- No comments in xarch's code (docstrings only). Never `ruff --fix`. `.claude/` stays out of commits. Nothing is pushed.
- `Import.unresolved: bool = False` is the **last** field of `Import` (`tests/modules/rules/builders.py:124` builds
  `Import` positionally).
- `module`, `names`, `relative`, `up`, `standard`, `written`, `every`, `last` keep today's values for every import.
- The recorded corpora (`tests/bootstrap/corpora/`) and the golden docs `docs/{cli,web,xarch}/*.md` are never
  hand-edited. The golden docs are regenerated and their diff read; no diff is expected.
- No profile line changes, in any profile file.
- The fact text is exactly `"every import of the app is followed to the place it names, however written"`.
- Line length is 140 (ruff.toml). Wrap prose in docstrings and yaml at about 120, as the files around do.
- Run the full suite in the background with `timeout` and read it at the end. Never `pkill`/`killall`. Signal only a
  PID you recorded yourself.

## Decisions this plan takes where the spec is silent or wrong

1. **A name bound by a relative import is `Use.bound` 0.** The never-use rule exempts a use under
   `reported-at-import` when `bound >= len(hit)` (`filters.py:157`). It also keeps import facts only `not relative`
   (`expansion.py:56`). So if a relatively bound `now` kept `bound=4`, the use would be exempt *and* the import line
   would not be reported, and test 15 would stay silent. I checked this on a prototype: with `bound=4` there is no
   finding. A relative import's line names none of the path from the top, so the reader reports `bound=0` for such a
   name. The finding then lands at the use. `Use`'s docstring says so. `function-reference` (`facts.py:219`) starts
   scanning at `max(bound, 2)`, which is still correct for 0, and no Use is bound by a relative import today, so no
   output of a project without relative imports moves.
2. **Test 15's two cases give different findings, not the same one.** The spec says the relative case gives "the same
   [finding] the absolute `from app.kernel.clock import now` gives". On today's code the absolute one is reported at
   the **import**: `app/modules/docs/domain/document.py:1: domain/ of modules/docs may not import
   app.kernel.clock.now (parts.domain.uses.never)`. The relative one is reported at the **use**: `...:4: ... may not
   use app.kernel.clock.now (...)`. Both were run, on the parent commit and on a prototype. The parametrized test
   asserts each one's own finding. The copied web profile accepts an app name (`app.kernel.clock.now`) in `pure`, so
   no fallback list entry is needed.
3. **The marker for "bound relatively" is a private `tuple` subclass `_Relative`** that is held only as a value of a
   scope's dict. Every path the reader hands out is rebuilt as `(*base, *attrs)`, a plain tuple, so `_Relative` never
   leaves the adapter.
4. **Existence is looked up as `<steps>/` (a folder) or `<steps[:-1]>/<steps[-1]>.py`** through the adapter's
   `FileSystem.is_dir`/`is_file`. An `OSError` from either counts as missing.
5. **`import.resolved` is appended last** to each of the ten `NEEDS` entries and to each of the four kinds' `needs`.
   Refusals list it after the entry's other facts.
6. **Three existing tests change beyond those the spec names** (B4 and test 18 allow it: "updated only where the new
   fact appears"). The full suite on the prototype showed exactly these, and no other:
   - `tests/bootstrap/test_profile_explain_words.py:65`: `kinds.call` needs `["call", "import.resolved"]`.
   - `tests/modules/rules/application/logic/test_own_checks.py:18`: the hand-made Toy language must also supply
     `import.resolved`, or its own check that reads `call` is refused.
   - `tests/modules/rules/adapters/test_fs_source_tree.py` row "a relative import climbs one folder fewer than its
     dots" reads through `parsed(text)`, so its imports are now `unresolved=True` (B2).
   - Plus `test_profile_needs.py`'s two never-list refusal tests, which gain `import.resolved` last.
7. **`keys.yaml:395` is rewrapped**, since the new words push the line past 120 columns. It is folded (`>-`) yaml, so
   the text it gives is the same words.

## Review Focus

1. **A relative import in a test file** (`tests/modules/test_x.py` writing `from ..fakes.repo import FakeRepo`). It
   must bind `("tests", "fakes", "repo", "FakeRepo")`, never an app name. Pinned in Task 1 by
   `test_a_test_file_s_relative_import_binds_a_place_of_the_tests`.
2. **A relative import inside a function or a class body.** It must resolve through that scope as at module level.
   Pinned in Task 1 by `test_a_relative_import_in_a_function_or_a_class_body_is_followed_there`.
3. **A file at the root writing `from . import b`.** It binds `("app", "b")` and is resolved. Pinned by
   `test_a_file_at_the_root_imports_relatively_from_the_root_s_own_folder`.
4. **The file system refusing a lookup** (permission denied on a folder). The import must be unresolved, never raise.
   Pinned by `test_a_place_the_file_system_cannot_look_up_is_missing`.
5. **Existing wired fixtures that already hold relative imports** (`tests/bootstrap/test_imports.py`,
   `test_app.py:208`, `test_review.py:24`, `test_project_files.py:124`). With Refs resolved, a `uses.never`, `shared`
   or `built_by` finding could appear. On the prototype the full suite showed none. If one appears while you
   implement, read it. Change the test's expected value only if the finding is right, and report it.

---

## File Structure

- `xarch/kernel/source.py`: `Import` gains `unresolved`.
- `xarch/modules/rules/adapters/fs_source_tree.py`: `_Where`, `_Relative`, `_from`; `read` builds a `_Where` per
  file; `_parsed`, `_imports`, `_functions`, `_scope`, `_bound`, `_reached`, `_Calls`, `_classes` take it through;
  module and `_scope` docstrings.
- `xarch/modules/rules/domain/parsed.py`: the `Ref` and `Use` docstrings.
- `xarch/profile_values/capabilities.py`, `xarch/architectures/presets/language/python.yaml`,
  `xarch/modules/spec/domain/key_table.py`, `xarch/modules/rules/domain/vocabulary.py`: the fact.
- The B5 texts: `keys.yaml`, `facts.py`, `twins.py`, `stand_ins.py`, `vocabulary.py`, `profile_checks.py`,
  `tests/modules/rules/application/logic/test_types_only.py`.
- Tests: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/bootstrap/test_rule_ids.py`,
  `tests/bootstrap/test_never_use.py`, `tests/modules/spec/application/logic/test_profile_needs.py`,
  `tests/bootstrap/test_profile_explain_words.py`, `tests/modules/rules/application/logic/test_own_checks.py`.
- `CHANGELOG.md`.

---

### Task 1: The reader follows every relative import, and says when it cannot

**Files:**
- Modify: `xarch/kernel/source.py:9-25`
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py` (module docstring lines 4-7; imports; `read` line 145;
  new `_Where`/`_Relative` before `_parsed`; `_parsed` 161-177; `_imports` 232-244; `_functions` 268-269; `_scope`
  608-611; `_bound` 614 and 643-647; `_reached` 679-692; `_Calls.__init__` 698 and `_within` 756; `_classes` 840-841)
- Modify: `xarch/modules/rules/domain/parsed.py:36-39` (Ref) and `:80-84` (Use)
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py`, `tests/bootstrap/test_rule_ids.py`,
  `tests/bootstrap/test_never_use.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `Import(..., last: int = 0, unresolved: bool = False)`. A relatively imported name's Ref is the resolved
  place, root first (for example `("app", "domain", "order", "Order")`). Its `Use.bound` is 0. Task 2 relies on no
  name; Task 3 rewords the texts that describe this.

- [ ] **Step 1: Write the failing adapter tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, replace exactly this test (lines 79-80):

```python
def test_relative_imports_bind_nothing(tmp_path):
    assert parsed(tmp_path, "from .helpers import build\nbuild()\n").calls == ()
```

with this block (the imports it needs, `Import`, `Call`, `Use`, `SourceFile`, `FsSourceTree`, `FileSystem`, `Path`,
`pytest`, are already at the top of the file):

```python
ORDER = "app/domain/order.py"
SERVICES = "app/domain/services.py"


def read_at(tmp_path: Path, files: dict[str, str], path: str) -> SourceFile:
    """The file at path, its first step the root it is read below, once every file given is written below tmp_path."""
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body)
    root, *steps = path.split("/")
    return FsSourceTree(FileSystem()).read(tmp_path / root, [tuple(steps)])[0]


def test_a_relative_import_of_a_name_binds_the_place_it_names(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports == (Import(1, ("order",), ("Order",), relative=True, up=0, written=".order"),)


def test_a_module_imported_relatively_is_the_place_its_names_are_read_on(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from . import order\n\norder.Order()\n"}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports == (Import(1, (), ("order",), relative=True, up=0, written="."),)


def test_a_relative_import_with_more_dots_climbs_a_folder_for_each(tmp_path):
    text = "from ..kernel.errors import Failed\nfrom .. import kernel\n\nFailed\nkernel\n"
    found = read_at(tmp_path, {"app/kernel/errors.py": "class Failed(Exception): ...\n", SERVICES: text}, SERVICES)
    assert found.uses == (Use(4, ("app", "kernel", "errors", "Failed"), 0), Use(5, ("app", "kernel"), 0))
    assert [(i.up, i.unresolved) for i in found.imports] == [(1, False), (1, False)]


def test_a_package_file_imports_relatively_from_its_own_folder(tmp_path):
    init = "app/domain/__init__.py"
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", init: "from .order import Order\n\nOrder()\n"}, init)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)


def test_an_alias_of_a_relative_import_keeps_the_place_it_names(tmp_path):
    text = "from .order import Order as O\nfrom . import order as o\n\nO()\no.Order()\n"
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: text}, SERVICES)
    assert found.calls == (Call(4, ("app", "domain", "order", "Order")), Call(5, ("app", "domain", "order", "Order")))


def test_a_relative_import_of_a_folder_is_followed_to_it(tmp_path):
    files = {"app/domain/order/__init__.py": "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}
    found = read_at(tmp_path, files, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports[0].unresolved is False


def test_a_relative_import_of_nothing_below_the_root_binds_nothing_and_is_unresolved(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from .ordr import Order\n\nOrder()\n"}, SERVICES)
    assert (found.calls, found.uses) == ((), ())
    assert found.imports == (Import(1, ("ordr",), ("Order",), relative=True, up=0, written=".ordr", unresolved=True),)


@pytest.mark.parametrize("text", [
    pytest.param("from .. import x\n\nx()\n", id="one folder above a file at the root"),
    pytest.param("from ... import x\n\nx()\n", id="two folders above it"),
    pytest.param("from ..up import x\n\nx()\n", id="a module of a folder above it"),
])
def test_a_relative_import_that_climbs_above_the_root_binds_nothing_and_is_unresolved(tmp_path, text):
    found = read_at(tmp_path, {"app/a.py": text}, "app/a.py")
    assert (found.calls, [i.unresolved for i in found.imports]) == ((), [True])


def test_a_file_at_the_root_imports_relatively_from_the_root_s_own_folder(tmp_path):
    found = read_at(tmp_path, {"app/a.py": "from . import b\n\nb()\n"}, "app/a.py")
    assert (found.calls, [i.unresolved for i in found.imports]) == ((Call(3, ("app", "b")),), [False])


def test_a_name_imported_relatively_reaches_every_reading_at_its_place_bound_none_of_its_steps(tmp_path):
    text = ("from unittest.mock import Mock\nfrom .base import Base\nfrom .ports import Repo\n\n\nclass Store(Base): ...\n\n\n"
            "def build(repo: Repo):\n    return Mock(spec=Repo)\n")
    files = {"app/domain/base.py": "class Base: ...\n", "app/domain/ports.py": "class Repo: ...\n", SERVICES: text}
    found = read_at(tmp_path, files, SERVICES)
    assert found.classes[0].bases == (("app", "domain", "base", "Base"),)
    assert found.calls == (Call(10, ("unittest", "mock", "Mock"), (), (("spec", ("app", "domain", "ports", "Repo")),)),)
    assert Use(9, ("app", "domain", "ports", "Repo"), 0) in found.uses


def test_a_relative_import_in_a_function_or_a_class_body_is_followed_there(tmp_path):
    text = ("def make():\n    from .order import Order\n    return Order()\n\n\n"
            "class Shop:\n    from .order import Order\n    built = Order()\n")
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: text}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")), Call(8, ("app", "domain", "order", "Order")))


def test_an_absolute_import_is_resolved_and_read_as_before(tmp_path):
    found = read_at(tmp_path, {SERVICES: "from app.domain.order import Order\nimport os\n\nOrder()\nos.getcwd()\n"}, SERVICES)
    assert [i.unresolved for i in found.imports] == [False, False]
    assert found.calls == (Call(4, ("app", "domain", "order", "Order")), Call(5, ("os", "getcwd")))
    assert found.uses == (Use(4, ("app", "domain", "order", "Order"), 4), Use(5, ("os", "getcwd"), 1))


def test_a_relative_import_of_a_file_beside_binds_its_name(tmp_path):
    files = {"app/domain/helpers.py": "def build(): ...\n", "app/domain/x.py": "from .helpers import build\nbuild()\n"}
    assert read_at(tmp_path, files, "app/domain/x.py").calls == (Call(2, ("app", "domain", "helpers", "build")),)


def test_a_text_read_with_no_file_follows_no_relative_import():
    found = FsSourceTree(FileSystem()).parsed("from .order import Order\nimport os\n\nOrder()\nos.getcwd()\n")
    assert found.calls == (Call(5, ("os", "getcwd")),)
    assert [i.unresolved for i in found.imports] == [True, False]


def test_a_test_file_s_relative_import_binds_a_place_of_the_tests(tmp_path):
    files = {"tests/fakes/repo.py": "class FakeRepo: ...\n",
             "tests/modules/test_x.py": "from ..fakes.repo import FakeRepo\n\nFakeRepo()\n"}
    found = read_at(tmp_path, files, "tests/modules/test_x.py")
    assert found.calls == (Call(3, ("tests", "fakes", "repo", "FakeRepo")),)


def test_a_relative_star_import_is_resolved_as_any_other_relative_import(tmp_path):
    found = read_at(tmp_path, {ORDER: "", SERVICES: "from .order import *\nfrom .ordr import *\n"}, SERVICES)
    assert [i.unresolved for i in found.imports] == [False, True]


def denied(self: FileSystem, path: Path) -> bool:
    raise PermissionError(13, "Permission denied", str(path))


def test_a_place_the_file_system_cannot_look_up_is_missing(tmp_path, monkeypatch):
    files = {ORDER: "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body)
    monkeypatch.setattr(FileSystem, "is_dir", denied)
    monkeypatch.setattr(FileSystem, "is_file", denied)
    found = FsSourceTree(FileSystem()).read(tmp_path / "app", [("domain", "services.py")])[0]
    assert (found.calls, [i.unresolved for i in found.imports]) == ((), [True])
```

In the same file, in `test_the_imports_are_recorded_in_terms_no_language_owns`'s table (around line 754), replace:

```python
    pytest.param("from . import doc\nfrom ..store import Repo\n",
         (Import(1, (), ("doc",), True, 0, written="."), Import(2, ("store",), ("Repo",), True, 1, written="..store")),
         id="a relative import climbs one folder fewer than its dots"),
```

with:

```python
    pytest.param("from . import doc\nfrom ..store import Repo\n",
         (Import(1, (), ("doc",), True, 0, written=".", unresolved=True),
          Import(2, ("store",), ("Repo",), True, 1, written="..store", unresolved=True)),
         id="a relative import climbs one folder fewer than its dots, and with no file it is not followed"),
```

- [ ] **Step 2: Write the failing wired tests**

`tests/bootstrap/test_rule_ids.py`: change the import line

```python
from tests.bootstrap.project import APP, TESTS, source_check, write
```

to

```python
from tests.bootstrap.project import APP, TESTS, problems, source_check, write
```

and append at the end of the file:

```python


@pytest.mark.parametrize("controller", [
    pytest.param("from .services.doc import DocService\n\nDocService()\n", id="the class imported relatively"),
    pytest.param("from .services import doc\n\ndoc.DocService()\n", id="its file imported relatively"),
])
def test_a_class_built_through_a_relative_import_is_held_to_built_by(tmp_path, controller):
    assert problems(tmp_path, app={"modules/docs/application/services/doc.py": "class DocService: ...\n",
                                   "modules/docs/application/controller.py": controller}) == [
        "app/modules/docs/application/controller.py:3: controller/ of modules/docs builds DocService, a class of "
        "services/ of modules/docs, which only bootstrap/ may build (parts.services.built_by)"]


def test_a_part_used_only_as_a_type_is_held_to_it_through_a_relative_import(tmp_path):
    """The web profile is given types_only on services, as in the test above, and the service imports relatively."""
    shutil.copytree(BUNDLED, tmp_path / "arch")
    services = "    may_import: [logic, domain, ports, contract, kernel, kernel-logic]\n    holds: classes\n"
    text = (BUNDLED / "web.yaml").read_text()
    assert text.count(services) == 1
    (tmp_path / "arch/typed.yaml").write_text(text.replace(services, services + "    types_only: [contract]\n"))
    app = write(tmp_path / "app", {**APP, "modules/docs/application/services/doc.py":
                                   "from ...contract import Published\n\n\nclass DocService:\n"
                                   "    def run(self):\n        return Published()\n"})
    result = source_check(app, str(tmp_path / "arch/typed.yaml"), write(tmp_path / "tests", TESTS))
    assert [(v.rule, v.line, bool(v.fix)) for v in result.violations] == [("types-only", 6, True)]
```

`tests/bootstrap/test_never_use.py`: replace the head

```python
import pytest

from tests.bootstrap.project import problems

DOMAIN = "modules/docs/domain/document.py"
```

with

```python
import shutil
from pathlib import Path

import pytest

import xarch
from tests.bootstrap.project import problems

BUNDLED = Path(xarch.__file__).parent / "architectures"
DOMAIN = "modules/docs/domain/document.py"
```

and append at the end of the file:

```python


@pytest.mark.parametrize("imported, problem", [
    pytest.param("from app.kernel.clock import now",
                 f"app/{DOMAIN}:1: domain/ of modules/docs may not import app.kernel.clock.now (parts.domain.uses.never)",
                 id="imported from the top: found at the import, which names it in full"),
    pytest.param("from ....kernel.clock import now",
                 f"app/{DOMAIN}:4: domain/ of modules/docs may not use app.kernel.clock.now (parts.domain.uses.never)",
                 id="imported relatively: found at the use, since the import names it from the file's folder"),
])
def test_a_name_of_the_app_on_a_never_list_is_found_however_it_is_imported(tmp_path, imported, problem):
    """No bundled list names a name of the app, which is all a relative import reaches, so the web profile's pure list
    is given one."""
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    listed = "  pure: [datetime.datetime.now,"
    assert text.count(listed) == 1
    (tmp_path / "arch/clocked.yaml").write_text(text.replace(listed, "  pure: [app.kernel.clock.now, datetime.datetime.now,"))
    body = f"{imported}\n\ndef stamp():\n    return now()\n"
    assert problems(tmp_path, app={"kernel/clock.py": "def now(): ...\n", DOMAIN: body},
                    profile=str(tmp_path / "arch/clocked.yaml")) == [problem]
```

- [ ] **Step 3: Run the new tests and see them fail**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_never_use.py 2>&1 | tail -30
```
Expected: FAIL. The adapter tests that build `Import(..., unresolved=...)` fail with
`TypeError: Import.__init__() got an unexpected keyword argument 'unresolved'`, the ones that read `.unresolved`
fail with `AttributeError`, and the others fail because the relative names give no call or use. The wired tests fail
with `assert [] == [...]`, except `test_a_name_of_the_app_on_a_never_list_is_found_however_it_is_imported[imported
from the top: ...]`, which passes already (it is the absolute twin). Every test that existed before this step passes,
except the edited row of `test_the_imports_are_recorded_in_terms_no_language_owns`.

- [ ] **Step 4: Add `unresolved` to `Import`**

In `xarch/kernel/source.py`, replace the `Import` class with:

```python
@dataclass(frozen=True)
class Import:
    """One import as written. module is the name it imports from, as steps; names is None when it imports module as
    a whole, else the names it imports from it. relative: module is named from the importing file's own folder, which
    the import climbs up folders above before it takes module's steps; else module is named from the top. standard:
    an absolute import whose first step names the standard library. written: the module as the source writes it.
    every: it imports every name the module makes public rather than names it lists (names then holds how the source
    writes that). last: the last line the import spans, when it is not its first (0: it spans one line). unresolved:
    the import names a place of the code being read (relative, or by an alias the project maps) that the reader found
    no file or folder for."""
    line: int
    module: tuple[str, ...]
    names: tuple[str, ...] | None = None
    relative: bool = False
    up: int = 0
    standard: bool = False
    written: str = ""
    every: bool = False
    last: int = 0
    unresolved: bool = False
```

- [ ] **Step 5: Follow relative imports in the reader**

All edits are in `xarch/modules/rules/adapters/fs_source_tree.py`.

5a. Imports: after `from collections.abc import Iterable` add `from dataclasses import dataclass`, so the block reads:

```python
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
```

5b. In `FsSourceTree.read`, replace

```python
            found.append(_parsed(name, path, text, table, immutable))
```

with

```python
            found.append(_parsed(name, path, text, table, immutable, _Where((root.name, *path[:-1]), root, self._fs)))
```

(`parsed(self, text)` stays `return _parsed("", (), text, None)`: no `_Where`, so every relative import of a bare
text is unresolved.)

5c. Replace the head of `_parsed` and its body down to the `return` with this, `_Where` and `_Relative` going
directly above it:

```python
@dataclass(frozen=True)
class _Where:
    """Where a file read below a root lies, so that its relative imports can be followed: the steps of the package it
    is in, the root's name first (a package file stands for its own folder), the root, and the file system the places
    below the root are looked up on."""
    package: tuple[str, ...]
    root: Path
    fs: FileSystem

    def target(self, level: int, module: tuple[str, ...]) -> tuple[str, ...] | None:
        """The place a relative import of that many dots names, the root's name first: up one folder fewer than its
        dots, then down module's steps; None when it climbs above the root or names neither a file nor a folder."""
        kept = len(self.package) - (level - 1)
        if kept < 1:
            return None
        steps = (*self.package[:kept], *module)
        return steps if self._exists(steps[1:]) else None

    def _exists(self, steps: tuple[str, ...]) -> bool:
        """Whether steps below the root name a folder or a `.py` file; a place the file system cannot look up is not
        there."""
        place = self.root.joinpath(*steps)
        try:
            return self.fs.is_dir(place) or (bool(steps) and self.fs.is_file(place.with_name(f"{steps[-1]}.py")))
        except OSError:
            return False


class _Relative(tuple):
    """A path a relative import binds: read as any other, but bound none of its steps, since the import's line names
    none of them from the top (see the module's docstring)."""


def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None,
            marks: tuple[RecordMark, ...] = (), where: _Where | None = None) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=Unparsable(e.lineno or 0, e.msg))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=Unparsable(0, str(e)))
    calls = _Calls(_BUILTINS if not _star_import(tree) else frozenset(), where)
    calls.visit(tree)
    return SourceFile(name, path, tuple(_imports(tree, where)), comments, _functions(tree, form, where),
                      tuple(_unions(tree)), calls=tuple(calls.found), classes=tuple(_classes(tree, marks, where)),
                      uses=tuple(calls.uses), parameter_calls=tuple(calls.parameter_calls),
                      module_functions=_module_functions(tree), named=_named(tree), callbacks=tuple(calls.callbacks),
                      method_calls=tuple(calls.method_calls), constants=tuple(_constants(tree)),
                      unmentioned=_unmentioned(tree), pieces=_pieces(tree))
```

5d. Replace `_imports` with this, `_from` going directly above it:

```python
def _from(node: ast.ImportFrom, where: _Where | None) -> tuple[str, ...] | None:
    """The place a `from` import takes its names from: its module for an absolute one; for a relative one the place
    it climbs to, the root's name first, or None when it cannot be followed (no file to climb from, above the root,
    or nothing there)."""
    module = tuple(node.module.split(".")) if node.module else ()
    if not node.level:
        return module
    found = where.target(node.level, module) if where is not None else None
    return _Relative(found) if found is not None else None


def _imports(tree: ast.AST, where: _Where | None = None) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split(".")), standard=_standard(alias.name.split(".")[0]),
                             written=alias.name, last=_last(node)) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, tuple(a.name for a in node.names), node.level > 0,
                                max(node.level - 1, 0), not node.level and bool(module) and _standard(module[0]),
                                "." * node.level + (node.module or ""), any(a.name == "*" for a in node.names),
                                _last(node), _from(node, where) is None))
    return found
```

5e. `_functions`: replace its first two lines

```python
def _functions(tree: ast.Module, form: CaseTable | None) -> tuple[Function, ...]:
    scope = [_scope(tree)]
```

with

```python
def _functions(tree: ast.Module, form: CaseTable | None, where: _Where | None = None) -> tuple[Function, ...]:
    scope = [_scope(tree, where)]
```

5f. Replace `_scope` with:

```python
def _scope(node: ast.AST, where: _Where | None = None) -> Scope:
    """The names a module, class, function, lambda or comprehension binds: the path an import binds, however
    written, or None when the name is bound any other way or by a relative import the reader cannot follow."""
    return _bound(node, where)[0]
```

5g. In `_bound`, replace the signature line

```python
def _bound(node: ast.AST) -> tuple[Scope, frozenset[str], frozenset[str]]:
```

with

```python
def _bound(node: ast.AST, where: _Where | None = None) -> tuple[Scope, frozenset[str], frozenset[str]]:
```

and replace its `ImportFrom` branch

```python
        elif isinstance(child, ast.ImportFrom):
            for alias in child.names:
                if alias.name != "*":
                    path = (*child.module.split("."), alias.name) if child.module and not child.level else None
                    bind(alias.asname or alias.name, path)
```

with

```python
        elif isinstance(child, ast.ImportFrom):
            base = _from(child, where)
            for alias in child.names:
                if alias.name == "*":
                    continue
                path = None if base is None else (*base, alias.name)
                bind(alias.asname or alias.name, _Relative(path) if child.level and path is not None else path)
```

5h. Replace `_reached` with:

```python
def _reached(node: ast.AST, chain: list[Scope], names: frozenset[str]) -> tuple[Ref, int]:
    """The path a name or a chain of attributes on one reaches, and how many of its steps the import binding it names
    from the top (none for a relative import); a name no scope binds that is in names is a builtin."""
    attrs: list[str] = []
    while isinstance(node, ast.Attribute):
        attrs.insert(0, node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None, 0
    scope = next((scope for scope in chain if node.id in scope), None)
    if scope is None:
        return (("builtins", node.id, *attrs), 0) if node.id in names else (None, 0)
    base = scope[node.id]
    if base is None:
        return None, 0
    return (*base, *attrs), 0 if isinstance(base, _Relative) else len(base)
```

5i. `_Calls.__init__`: replace

```python
    def __init__(self, builtins: frozenset[str] = frozenset()) -> None:
        self.found: list[Call] = []
```

with

```python
    def __init__(self, builtins: frozenset[str] = frozenset(), where: _Where | None = None) -> None:
        self._where = where
        self.found: list[Call] = []
```

and in `_within` replace `        scope, parameters, _ = _bound(node)` with `        scope, parameters, _ = _bound(node, self._where)`.

5j. `_classes`: replace

```python
def _classes(tree: ast.Module, marks: tuple[RecordMark, ...] = ()) -> list[Class]:
    scope = [_scope(tree)]
```

with

```python
def _classes(tree: ast.Module, marks: tuple[RecordMark, ...] = (), where: _Where | None = None) -> list[Class]:
    scope = [_scope(tree, where)]
```

(`_module_functions` keeps `_bound(tree)[2]`: it reads only which names a `def` alone binds, which no import's place
changes.)

5k. Replace the module docstring's second paragraph (lines 4-7):

```
A name in a call or a class base is read as Python scopes it: through the innermost function, lambda or
comprehension that binds it (a class body only for its own statements), then the module. It is a Ref only when that
scope binds it with an absolute import and nothing else; a parameter, an assignment, a def, a relative import or a
second, different binding of the same name in that scope makes it None, and so does a name no scope binds.
```

with these two paragraphs:

```
A name in a call or a class base is read as Python scopes it: through the innermost function, lambda or
comprehension that binds it (a class body only for its own statements), then the module. It is a Ref only when that
scope binds it with an import, however written, that the reader follows, and nothing else; a parameter, an
assignment, a def or a second, different binding of the same name in that scope makes it None, and so does a name no
scope binds.

A relative import is followed from the package of the file it is in, the root's name then the folders below it (a
package file stands for its own folder): up one folder fewer than its dots, then down its module's steps, to a `.py`
file or a folder of that name, looked up on the file system and never opened or run. One that climbs above the root,
or names nothing below it, binds None and is marked unresolved; so is every relative import of a text read with no
file. A name a relative import binds is bound none of its steps, since that import names none of them from the top.
```

- [ ] **Step 6: Reword the `Ref` and `Use` docstrings**

In `xarch/modules/rules/domain/parsed.py`, replace the `Ref` docstring (lines 37-39) with LN 1.1's "After" text, word
for word:

```python
Ref = tuple[str, ...] | None
"""The place a name reaches, as steps: for a name of the app, the app's root, the steps of the file that defines it
below the root, then the name; for an outside name, its package as one step, then the steps below it. However the
import is written (absolute, relative, or by a name the project maps to a folder), the reader follows it. None for
a name no import binds (a literal, an expression, a parameter, an assignment), and for an import the reader could
not follow (see Import.unresolved)."""
```

and the `Use` docstring (lines 81-84) with:

```python
    """A name read where it is used, called or not, as the dotted path it reaches, and the line it is on: `dt.now`
    after `from datetime import datetime as dt` is ("datetime", "datetime", "now"). bound is how many steps of the
    path the import that binds its first name names from the top (2 here: `from datetime import datetime`; 0 for a
    relative import, which names none of them so, and whose line therefore carries no finding on the path); a builtin
    used by its bare name is (<its namespace>, <name>), bound 0."""
```

- [ ] **Step 7: Run the tests and see them pass**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_never_use.py tests/architecture 2>&1 | tail -5
uv run ruff check
```
Expected: all PASS (`test_fs_source_tree.py` 247 passed); ruff `All checks passed!`. If ruff reports `I001` on
`test_never_use.py`, read it and order the imports by hand as it says (never `--fix`).

- [ ] **Step 8: Run the wider suites the reader feeds**

Run:
```bash
timeout 900 uv run pytest -q tests/modules/rules tests/bootstrap/test_imports.py tests/bootstrap/test_app.py tests/bootstrap/test_review.py tests/bootstrap/test_project_files.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_source_checks.py 2>&1 | tail -8
```
Expected: all PASS. If a wired test with a relative import in its fixture now gives a new finding (Review Focus 5),
read the finding. Change that test's expected value only when the finding is right, and say so in the commit message.
On the prototype none appeared. `test_own_checks.py` passes here; it fails only once Task 2 adds the fact.

- [ ] **Step 9: Commit**

```bash
git add xarch/kernel/source.py xarch/modules/rules/adapters/fs_source_tree.py xarch/modules/rules/domain/parsed.py \
  tests/modules/rules/adapters/test_fs_source_tree.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_never_use.py
git commit -m "The Python reader follows every relative import to the place it names: from .order import Order in app/domain/services.py binds app.domain.order.Order, a name it binds is bound none of its steps so a never-use finding lands at the use, and an import that climbs above the root or names nothing below it binds nothing and is Import.unresolved; built_by, types_only and uses.never now find relatively imported names

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The fact `import.resolved`

**Files:**
- Modify: `xarch/profile_values/capabilities.py:23` (after `import.standard`)
- Modify: `xarch/architectures/presets/language/python.yaml:46` (after `import.standard: exact`)
- Modify: `xarch/modules/spec/domain/key_table.py:192-227`
- Modify: `xarch/modules/rules/domain/vocabulary.py:203-213`
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`, `tests/bootstrap/test_profile_explain_words.py:65`,
  `tests/modules/rules/application/logic/test_own_checks.py:18-19`; held by `tests/bootstrap/test_needs_agree.py`
  (unchanged)

**Interfaces:**
- Consumes: Task 1's reader, which makes the fact true of Python.
- Produces: `FACTS["import.resolved"]`; `NEEDS` entries and the kinds `use`, `call`, `construction`,
  `function-reference` list `"import.resolved"` last.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_profile_needs.py`, replace

```python
    assert problems(document, languages=LANGUAGES) == [refusal("parts.service.uses.never", "use"),
                                                       refusal("parts.service.uses.never", "method_call")]
```

with

```python
    assert problems(document, languages=LANGUAGES) == [refusal("parts.service.uses.never", "use"),
                                                       refusal("parts.service.uses.never", "method_call"),
                                                       refusal("parts.service.uses.never", "import.resolved")]
```

replace

```python
        refusal("tiers.unit.uses.apply_never", "use"), refusal("tiers.unit.uses.apply_never", "method_call")]
```

with

```python
        refusal("tiers.unit.uses.apply_never", "use"), refusal("tiers.unit.uses.apply_never", "method_call"),
        refusal("tiers.unit.uses.apply_never", "import.resolved")]
```

and append at the end of the file:

```python


def test_a_key_whose_check_reads_names_through_imports_needs_them_followed_however_written():
    assert problems(services(built_by=["api"]), languages=LANGUAGES) == [
        refusal("parts.service.built_by", "call"), refusal("parts.service.built_by", "import.resolved")]
```

In `tests/bootstrap/test_profile_explain_words.py:65`, replace

```python
    assert (word["name"], word["verb"], word["needs"]) == ("call", "call", ["call"])
```

with

```python
    assert (word["name"], word["verb"], word["needs"]) == ("call", "call", ["call", "import.resolved"])
```

In `tests/modules/rules/application/logic/test_own_checks.py:18-19`, replace

```python
SUPPLIES = CheckedLanguage("Toy", supplies=(Supply("call", EXACT), Supply("import", "partial", "no star imports"),
                                            Supply("file", EXACT)))
```

with

```python
SUPPLIES = CheckedLanguage("Toy", supplies=(Supply("call", EXACT), Supply("import.resolved", EXACT),
                                            Supply("import", "partial", "no star imports"), Supply("file", EXACT)))
```

(Toy's own checks read `call`, which now needs the new fact; Toy supplying it keeps those tests about what they test.)

- [ ] **Step 2: Run them and see them fail**

Run:
```bash
timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain_words.py 2>&1 | tail -8
```
Expected: FAIL. The three `test_profile_needs.py` tests fail with `KeyError: 'import.resolved'` (from `refusal`,
which reads `FACTS[fact]`), and `test_json_gives_each_of_them_as_one_document` fails on the `needs` list.
`test_own_checks.py` still passes at this point.

- [ ] **Step 3: Add the fact**

`xarch/profile_values/capabilities.py`: after the line
`    "import.standard": "whether an import names the standard library",` add

```python
    "import.resolved": "every import of the app is followed to the place it names, however written",
```

`xarch/architectures/presets/language/python.yaml`: after `  import.standard: exact` add `  import.resolved: exact`,
so the block reads:

```yaml
  import.relative: exact
  import.standard: exact
  import.resolved: exact
  import.mentioned: exact
```

`xarch/modules/spec/domain/key_table.py`, make these exact replacements (the ten entries: two through `_TYPES_ONLY`,
two through `_NEVER_USE`, six by hand):

```python
_NEVER_USE = (*_IMPORTS, "use", "method_call", "import.resolved")
_TYPES_ONLY = ("call", "use", "module_functions", "import.resolved")
```

```python
    "parts.<part>.built_by": ("class", "call", "import.resolved"),
    "parts.<part>.shared": (*_IMPORTS, "import.mentioned", "use", "class", "class.named", "function", "function.named",
                            "module_functions", "constant", "import.resolved"),
```

```python
    "testing.skips": ("use", "import.resolved"),
```

```python
    "testing.mocks": ("call", "parameter_call", "import.resolved"),
```

```python
    "guards.stand-ins": ("class", "class.methods", "class.attributes", "call", "parameter_call",
                         "import.resolved"),
```

```python
    "guards.no-twins.translated": ("class", "class.fields", "call", "function", "function.named", *_IMPORTS,
                                   "import.resolved"),
```

`xarch/modules/rules/domain/vocabulary.py`, replace these four kinds' `needs`:

```python
    Kind("use", "each name read, called or not, as the dotted path the import binding its first name reaches",
         ("line", "path", "bound"), needs=("use", "import.resolved"), verb="use"),
```

```python
    Kind("call", "each call whose callee an import binds, as that dotted path", ("line", "path"),
         {"place": "target-placed"}, needs=("call", "import.resolved"), verb="call"),
    Kind("construction", "each call of a class the app defines at the top level of a file, read through the import "
                         "that binds it", ("line", "path", "name", "place"), needs=("call", "class", "import.resolved"),
         verb="build"),
    Kind("function-reference", "each name read that is a function the app defines at the top level of a file, other "
                               "than as the callee of a call (passed on, stored)",
         ("line", "path", "reaches", "place"), needs=("use", "call", "module_functions", "import.resolved"),
         verb="reference"),
```

(`method-call`, `import`, `imported-name`, `import-into-app` and `import-into-tests` do not change.)

- [ ] **Step 4: Run the tests and see them pass**

Run:
```bash
timeout 900 uv run pytest -q tests/modules/spec tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain_words.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/rules/application/logic/test_explained.py tests/modules/rules/domain tests/architecture 2>&1 | tail -5
uv run ruff check
```
Expected: all PASS, including `test_needs_agree.py` unchanged (if it reports a key whose sides differ, the table is
right: adjust the kinds until it passes, and say which in the commit message) and
`test_python_supplies_every_fact_a_bundled_check_reads`; ruff clean.

- [ ] **Step 5: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml \
  xarch/modules/spec/domain/key_table.py xarch/modules/rules/domain/vocabulary.py \
  tests/modules/spec/application/logic/test_profile_needs.py tests/bootstrap/test_profile_explain_words.py \
  tests/modules/rules/application/logic/test_own_checks.py
git commit -m "The fact import.resolved, every import of the app followed to the place it names however written: Python supplies it exact, the ten keys whose checks read uses or calls need it and so do the kinds use, call, construction and function-reference, so a language without it is refused on them with the existing message; no profile line changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The texts that said "absolute import", the CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `xarch/architectures/presets/format/keys.yaml:140, 158, 343, 394-397`
- Modify: `xarch/modules/rules/application/logic/facts.py:48-49`, `twins.py:30`, `stand_ins.py:30-31`
- Modify: `xarch/modules/rules/domain/vocabulary.py:256`, `xarch/modules/spec/application/logic/profile_checks.py:400`
- Modify: `tests/modules/rules/application/logic/test_types_only.py:2`
- Modify: `CHANGELOG.md` (`## [Unreleased]` / `### Changed`)
- Regenerate (never hand-edit): `docs/cli/*.md`, `docs/web/*.md`, `docs/xarch/*.md`

**Interfaces:**
- Consumes: Tasks 1 and 2 (the texts describe them).
- Produces: nothing code reads.

- [ ] **Step 1: Pin the grep that must come out clean (RED)**

Run:
```bash
grep -rn "absolute import" xarch tests --include=*.py --include=*.yaml | grep -v "tests/bootstrap/corpora/"
```
Expected now (after Task 1): 12 lines: `keys.yaml:140, 158, 343, 395`, `kernel/source.py:14`, `facts.py:49`,
`twins.py:30`, `stand_ins.py:31`, `vocabulary.py:256`, `profile_checks.py:400`, `test_types_only.py:2` and
`test_tier_imports.py:243`. After Step 2 only `kernel/source.py:14` and `test_tier_imports.py:243` remain.

- [ ] **Step 2: Reword the texts**

`xarch/architectures/presets/format/keys.yaml`:
- line 140: `Dotted names are what an absolute import binds;` becomes `Dotted names are what an import binds;`
- line 158: `      name as an absolute import binds it (`datetime` becomes `      name as an import binds it (`datetime`
- line 343: `read through absolute imports only, as` becomes `read through every import, however written, as`
- lines 394-397 (`parts.<part>.built_by` `accepts`), replace

```yaml
      [<part>, ...]: only code of those parts calls the constructor of a class defined at the top level in a file of
      this part, `X(...)` or `m.X(...)`, read through absolute imports; code of this part counts as any other, and tests
      are not read. Silent on a class reached through a package file that re-exports it, built in its own file, or built
      through a variable or a parameter
```

with

```yaml
      [<part>, ...]: only code of those parts calls the constructor of a class defined at the top level in a file of
      this part, `X(...)` or `m.X(...)`, read through every import, however written; code of this part counts as any
      other, and tests are not read. Silent on a class reached through a package file that re-exports it, built in its
      own file, or built through a variable or a parameter
```

`xarch/modules/rules/application/logic/facts.py:48-49`: replace

```
                        a class of the app that is an exception, however far that goes (a base read through the
                        absolute import that binds it)
```

with

```
                        a class of the app that is an exception, however far that goes (a base read through the
                        import that binds it)
```

`xarch/modules/rules/application/logic/twins.py:30`: `(a call of it read through the absolute import that binds it)`
becomes `(a call of it read through the import that binds it)`.

`xarch/modules/rules/application/logic/stand_ins.py:30-31`: replace

```
The check stays silent on what it cannot read: a call that unpacks its arguments, a spec that is not a name an
absolute import binds (a variable, an expression, a string), a spec imported from a package that re-exports the port,
```

with

```
The check stays silent on what it cannot read: a call that unpacks its arguments, a spec that is not a name an
import binds (a variable, an expression, a string), a spec imported from a package that re-exports the port,
```

`xarch/modules/rules/domain/vocabulary.py:256`: replace

```python
    Filter("app-package", "the import names the app's own package by its root (an absolute import of the app)", FACT,
```

with

```python
    Filter("app-package", "the import names the app's own package by its root (an import written from the top)", FACT,
```

`xarch/modules/spec/application/logic/profile_checks.py:400`: `"""A dotted name such as pkg.sub.name, the path an
absolute import binds."""` becomes `"""A dotted name such as pkg.sub.name, the path an import binds."""`.

`tests/modules/rules/application/logic/test_types_only.py:2`: `it reaches of them through an absolute import, and may
call everything else."""` becomes `it reaches of them through an import, however written, and may call everything
else."""`. Keep the docstring's first line as it is; if line 2 grows past 120 columns, wrap it onto a third line.

Then run:
```bash
grep -rn "absolute import" xarch tests --include=*.py --include=*.yaml | grep -v "tests/bootstrap/corpora/"
awk 'FNR>=393 && FNR<=397 && length > 120 {print FILENAME": "FNR}' xarch/architectures/presets/format/keys.yaml
```
Expected: the grep prints only `xarch/kernel/source.py:14` and
`tests/modules/rules/application/logic/test_tier_imports.py:243`; the awk prints nothing.

- [ ] **Step 3: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Changed`, after the bullet that starts `- Internal names follow the
0.3.0 key names`, add a blank line and:

```markdown
- The Python reader follows relative imports to the place they name: `from .order import Order` in
  `app/domain/services.py` binds `app.domain.order.Order`, as `from app.domain.order import Order` does, so
  `uses.never`, `built_by`, `types_only`, `shared`, the mocks, `stand-ins` and the twins' translation read names
  imported relatively as they read absolute ones; a name of the app that a `uses.never` list names is found at its use,
  since a relative import's line does not name it in full. An import it cannot follow (one that climbs above the root,
  or names no file or folder below it) is marked unresolved and binds nothing. Python has no alias map, so the reader
  reads no config for aliases. The keys that read those names need the new fact `import.resolved`, which Python
  supplies `exact`; a language that does not supply it is refused on them with the existing message. A project with no
  relative import sees no change.
```

README: no section lists the facts or a language's `supplies` (`grep -n "import.standard" README.md` prints nothing),
so it does not change.

- [ ] **Step 4: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-3-1/regenerate_docs.py` (outside the worktree):

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
uv run python -I /tmp/xarch-3-1/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs/cli docs/web docs/xarch
```
Expected: `written`; `git status` shows only the untracked spec and plan under `docs/superpowers/` (the workflow
commits those); `git diff --stat` prints nothing. Any moved golden doc is a defect of this step: do not keep or
hand-edit it. Restore it with `git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 5: Run the gates**

```bash
uv run ruff check
uv run xarch check; echo "check exit $?"
uv run xarch check --strict; echo "strict exit $?"
uv run xarch profile check architecture.yaml; echo "profile exit $?"
mkdir -p /tmp/xarch-3-1
timeout 1800 uv run pytest -q > /tmp/xarch-3-1/pytest.txt 2>&1 &
echo $! > /tmp/xarch-3-1/pytest.pid
```
Expected: ruff `All checks passed!`; each `exit 0`; `profile check` ends `OK: the profile is valid`. When the suite
process has exited (`tail -3 /tmp/xarch-3-1/pytest.txt`, run in about three minutes), it reports all passed and no
failure. On the prototype of this plan it gave `4828 passed`. `test_recorded_corpora.py`, `test_docs.py`
and `test_docs_templates.py` pass, with no corpus or golden doc edited (`git status --short tests/bootstrap/corpora
docs/cli docs/web docs/xarch` prints nothing).

- [ ] **Step 6: Commit**

```bash
git add xarch/architectures/presets/format/keys.yaml xarch/modules/rules/application/logic/facts.py \
  xarch/modules/rules/application/logic/twins.py xarch/modules/rules/application/logic/stand_ins.py \
  xarch/modules/rules/domain/vocabulary.py xarch/modules/spec/application/logic/profile_checks.py \
  tests/modules/rules/application/logic/test_types_only.py CHANGELOG.md
git commit -m "The texts that said a name is read through an absolute import say an import however written, in keys.yaml, the facts, twins and stand-ins docstrings, the app-package filter and the dotted-name reader, and the CHANGELOG says the Python reader follows relative imports, marks what it cannot follow unresolved, and the keys that read those names need import.resolved; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review against the spec

- B1: every bullet has a Task 1 test: file target (1), module (2), `..` (3), package file (4), aliases (5), every
  reading: base, `spec=`, annotation (9), inner scopes (9b, Review Focus 2), the tests root (Review Focus 1), scope
  rules unchanged (the existing two-bindings tests keep passing).
- B2: field last with a default (Task 1 Step 4); absolute always resolved (10); climb above the root (8);
  missing target (7); folder target (6); star (star test); `parsed(text)` (12 and the edited table row); file system
  error (Review Focus 4); other fields unchanged (tests 1, 2, 7 assert whole `Import` values).
- B3: nothing is built; the reader reads no config; the CHANGELOG says so.
- B4: `FACTS`, `python.yaml`, the ten `NEEDS` entries and the four kinds (Task 2). `test_needs_agree.py` is
  unchanged and must pass. The refusal of a language without the fact is test 17. No profile line changes.
- B5: every listed text (Task 3 Step 2; `parsed.py` and `fs_source_tree.py` in Task 1 Steps 5k-6); the grep (Task 3
  Steps 1-2).
- B6: corpora untouched and `test_recorded_corpora.py` run (Task 1 Step 8, Task 3 Step 5); golden docs regenerated
  with no diff (Task 3 Step 4; checked on the prototype).
- Tests 13-15: Task 1 Step 2, seen failing on the parent in Step 3 (checked on an untouched copy). Test 15 departs
  from the spec's "same finding" (Decision 2).
- Placeholders: none. Types: `_Where.target(level: int, module: tuple[str, ...]) -> tuple[str, ...] | None`,
  `_from(node, where)`, and `where: _Where | None = None` on `_parsed`, `_imports`, `_functions`, `_scope`, `_bound`,
  `_classes`, `_Calls.__init__`, the same in every step.
<!-- task-pipeline: validated -->
