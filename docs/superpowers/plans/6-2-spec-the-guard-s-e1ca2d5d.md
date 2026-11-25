# 6.2: the guard's `file` writes the case of `{name}` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The guard `scenario-coverage` fills `{name:snake}`, `{name:kebab}`, `{name:camel}` or `{name:pascal}` in its `file` with the use case's name in that case, a bare `{name}` is refused with a fixed hint, and nothing a user sees changes for today's profiles but the two reworded refusals.

**Architecture:** A new kernel module `xarch/kernel/logic/cases.py` owns the case list (`CASES`), the four placeholders (`CASED`), the word split moved from `scenarios._snake_name` (`written`) and the fill (`filled`). The rules module's guard (`scenarios._test_file`) and the spec module's profile check (`profile_checks.use_case_file`) and docs line (`docs_template._guard_line`) read only from it. `architecture.yaml` gives `kernel-logic` `shared: 2`: every public name there must be used by two modules, so `filled` is called by both rules (to fill the use case's name) and spec (to fill `x` before the file-name check). The switch of the profile check, the guard, the docs line, the six profiles and every fixture is one task, because a refused bare `{name}` and a guard that no longer fills `{name}` each break every fixture still writing it.

**Tech Stack:** Python ≥ 3.13, `re`, pytest, ruff (line length 140), `uv`, YAML data files.

**Spec:** `docs/superpowers/specs/6-2-spec-the-guard-s-e1ca2d5d.md`. It is copied in full below, before the tasks.

## Global Constraints

- No comments in xarch's code; docstrings only.
- Tests are written first; each must fail, for the reason named, before the code changes.
- Table tests use `pytest.param(..., id="<a sentence>")`; `unit` and `integration` set `plain_tables: true`, so a table test's body holds no `if`, `match`, `try`, `for`, `while` statement and no `x if c else y` (a generator expression is fine).
- The four cases are `snake`, `kebab`, `camel`, `pascal`, in that order, listed only in `xarch/kernel/logic/cases.py` (`CASES`).
- The bare-name refusal is exactly `<where>: <value!r>: {name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant`.
- The reworded refusals are exactly `<where>: must hold `{name:<case>}` once, <case> one of snake, kebab, camel, pascal, such as a_{name:snake}<ext>` and `<where>: must be a file name below the test folders, such as a_{name:snake}<ext>`.
- `written(name, "snake")` equals today's `_snake_name(name)` for every name: the recorded corpora (`tests/bootstrap/corpora/`) replay unchanged and the golden docs `docs/{cli,web,xarch}/testing.md` regenerate byte for byte. Neither is ever edited by hand; the `.tar.xz` archives and the `.json` corpora are never touched.
- Six profile lines change, each `file: test_{name}.py` to `file: test_{name:snake}.py`, and nothing else in those files.
- `{name}` placeholders of a rule's `message`/`fix` are another feature and stay.
- Python wording only in the reader adapter and `xarch/architectures/presets/`.
- Never run `ruff --fix`; fix by hand what `uv run ruff check` reports.
- Gates, each green on this branch alone at the end: `uv run pytest -q` (over two minutes: run it in the background with `timeout 900`, read the result at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.
- README does not change. CHANGELOG lines go under `## [Unreleased]`.
- `.claude/` stays out of commits; nothing is pushed.
- Process safety: never `pkill`/`killall`/`kill` by pattern; stop a stuck run with `timeout`.

## Review Focus

1. **A bare `{name}` written beside a cased one** (`test_{name}_{name:snake}.py`): one refusal, the bare-name one, never two. Pinned by a row of `test_a_bare_name_is_refused_with_its_hint` (Task 2).
2. **`{name:pascal}` against the framework's file patterns.** The check fills the name as `X` for pascal (`filled(value, "x")`), so `test_{name:pascal}.py` under pytest's `test_*.py` must still be accepted, as each other case is. Pinned by `test_a_file_in_any_case_is_checked_against_the_testing_patterns` (Task 2).
3. **The docs line under a case other than snake**: `{name:kebab}_spec.py` must show as `` `<name>_spec.py` ``, never as the raw placeholder. Pinned by `test_the_guard_line_shows_the_name_as_name_whatever_its_case` (Task 2).
4. **A placeholder typed almost right** (`{name: snake}` with a space, `{name:Snake}`, `{name:}`): the "must hold once" refusal, not a crash and not a silent literal file name. Pinned by rows of `test_a_file_without_one_case_is_refused` (Task 2).
5. **A use case name holding an underscore** (`Publish_Doc`): no character but a change of case splits a word, in every case, so kebab gives `publish_doc`, not `publish-doc`. Pinned by `test_no_character_but_a_change_of_case_ends_a_word` (Task 1).

---

## The spec

# 6.2 The guard's `file` writes the case of `{name}`: design spec

Card: e1ca2d5d (subtask of 15e55316). Release step 18 of the merged order
(`~/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, section 3). Blocked by 6.1 (908b19fa),
which is done on this branch (8cafeb4, 50d1f42, 789750f).

Parent design: `~/.claude/bedtime/xarch-2026-11-16-audits/test-tables-design.md` (below, "the note"). This card
implements its section 4 (lines 283-307), the `{name}` refusal of section 7 (line 372) and item 2 of section 8
(lines 398-399).

## 1. Goal

Today the guard `scenario-coverage` reads `{name}` in its `file` as "the use case's name in snake_case", a rule
typed into the checking code (`xarch/modules/rules/application/logic/scenarios.py:45-53, 124-126`). After this card
the profile writes the case itself: `{name:snake}`, `{name:kebab}`, `{name:camel}` or `{name:pascal}`. A bare
`{name}` is refused with a fixed hint. The words of a name are split by today's rule, which moves to a kernel helper,
and joined in the case asked for. For every profile that exists today nothing a user sees changes, apart from the
refusal texts of section 3.3, which are reworded on purpose.

## 2. Inherited constraints

Each line cites its source.

- Owner ruling: the guard's `file` writes the case explicitly, with the four cases `snake`, `kebab`, `camel`, `pascal`,
  and a bare `{name}` is refused (note, "Rulings already given", lines 17-18).
- The case lives in the profile. It does not go in the framework or language data file (note 4, lines 290-293).
  Named dodge: "Moving the snake_case rule to the framework file because pytest projects use it. Case is written in
  the profile" (note, "Dodges", line 445).
- The words are split by the rule `_snake_name` uses today. That rule moves to a kernel helper (note 4, lines
  292-293; section 6 table, `scenarios.py` row, line 347).
- The refusal wording is fixed text, in the one wording of every 0.3.0 refusal (note 7, lines 367-372, 374):
  `guards.scenario-coverage.file: 'test_{name}.py': {name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant`
- No compatibility window (note, "Rulings", lines 10-11; note 7, lines 377-378).
- Messages print the file name after it is filled, so findings do not change (note 4, line 301).
- The docs line replaces the whole placeholder with `<name>`, so the golden docs do not change (note 4, lines 301-302;
  section 6, "Golden docs" row, line 355).
- `use_case_file` checks that the placeholder appears once and accepts the four cases (note 4, lines 302-303).
- The six profile lines change one line each, `test_{name}.py` to `test_{name:snake}.py` (note 4, lines 295-298;
  section 6, "Profiles" row, line 354). The two archived profiles are plain yaml since release step 0 (note,
  "Rulings", lines 19-21; note 4, lines 305-307). The archived code is never edited.
- Today's pytest behaviour stays byte for byte. Any change in the recorded corpora or the golden docs is a defect
  (note 6, lines 364-366; "Dodges", line 448).
- Gates on this branch alone, with the full suite green: `uv run pytest -q`, `uv run xarch check`,
  `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`
  (note 8, lines 389-391; card).
- Project rules (card): no comments in xarch's code (docstrings only); tests written first; examples simple, with
  absolute `app.` imports; recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as the note
  says; Python only in the reader adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays
  out of commits; nothing is pushed.
- README and CHANGELOG lines go under `[Unreleased]` (review 3, O4 and O5, `0.3.0-cohesion-review-3.md:228-229`).
  The golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read, never edited by hand
  (review 3, O8, line 232). For this card the diff must be empty.

## 3. Observable behaviour

### 3.1 The kernel helper: words and cases

A new module `xarch/kernel/logic/cases.py`, with tests in `tests/kernel/logic/test_cases.py`, is the only code that
splits a name into words or joins words in a case.

- **Words.** A name splits into words at the same two boundaries `_snake_name` uses today
  (`scenarios.py:53`): before a capital that follows a lowercase letter or a digit, and before the last capital of a
  run of capitals that is followed by a lowercase letter. No other character splits a word. A digit stays with the
  word before it, and an underscore or any other character stays inside its word.
- **Cases.** Every word is lowercased first. Then:
  - `snake`: the words joined by `_`.
  - `kebab`: the words joined by `-`.
  - `camel`: the first word as it is, each later word with its first character uppercased, all joined with nothing
    between.
  - `pascal`: every word with its first character uppercased, joined with nothing between.
- For every name, `snake` gives exactly what `_snake_name` gives today. This is what keeps the corpora and the
  findings byte for byte.

The table the helper's test must hold. Each row is one name and the four forms it is written in:

| name | snake | kebab | camel | pascal |
|---|---|---|---|---|
| `Publish` (one word) | `publish` | `publish` | `publish` | `Publish` |
| `PublishDocument` (two words) | `publish_document` | `publish-document` | `publishDocument` | `PublishDocument` |
| `HTTPCheck` (a run of capitals is one word) | `http_check` | `http-check` | `httpCheck` | `HttpCheck` |
| `MarkRead2` (a digit stays with its word) | `mark_read2` | `mark-read2` | `markRead2` | `MarkRead2` |

The ids in parentheses are the ones used today in `tests/modules/rules/application/logic/test_scenarios.py:36-41`.
The expectations of that test move into this table.

The helper exposes the four case names in one place, `CASES = ("snake", "kebab", "camel", "pascal")`, in that
order. The profile check (3.3) and the guard (3.2) both read them from there, so no other file spells the list.

### 3.2 The guard fills the file name in its case

`scenarios._test_file` finds the one `{name:<case>}` in `guard.file` and replaces it with the use case's name (the
union's name without the suffix), written in that case by the kernel helper. `_snake_name` and `import re` leave
`scenarios.py`. `NAME = "{name}"` and its docstring (`scenarios.py:45-46`) go too, replaced by whatever the fill needs,
and the module docstring (`scenarios.py:4-5`) says the file is the guard's `file` with `{name:<case>}` replaced by
<Name> in that case (PublishDocument with `{name:snake}`: publish_document).

Observable result:
- With `file: test_{name:snake}.py`, every finding is word for word what `file: test_{name}.py` gave before. For
  example: `app/modules/docs/contract/results.py:4: HTTPCheckResult has no test file test_http_check.py among the
  integration tests of docs (scenario-coverage)`.
- With `file: {name:kebab}.test.ts` (or camel, or pascal), the guard looks for `http-check.test.ts`
  (`httpCheck.test.ts`, `HttpCheck.test.ts`) and names that file in its finding.

The guard never meets a bare `{name}`, because the profile check refuses it first (3.3).

### 3.3 The profile check of `guards.scenario-coverage.file`

`use_case_file` (`xarch/modules/spec/application/logic/profile_checks.py:403-415`) checks the value in this order.
It stops at the first problem and records exactly one:

1. A string holding a bare `{name}` (the exact text `{name}`, anywhere, whether or not a cased placeholder is also
   present): the fixed refusal
   `<where>: <value!r>: {name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant`.
   Under the bundled path `<where>` is `guards.scenario-coverage.file`, so a profile `p.yaml` writing
   `file: test_{name}.py` gets exactly:
   `p.yaml: guards.scenario-coverage.file: 'test_{name}.py': {name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant`
   (the `<profile>.yaml: ` prefix is added by the caller, as it is today).
2. Not a string, or the number of placeholders `{name:snake}`, `{name:kebab}`, `{name:camel}` and `{name:pascal}`
   together is not exactly one:
   `<where>: must hold `{name:<case>}` once, <case> one of snake, kebab, camel, pascal, such as a_{name:snake}<ext>`.
   This covers no placeholder, two placeholders (of the same case or of two cases), and a case that does not exist
   (`{name:upper}`, `{name:Snake}`, `{name:}`): a placeholder with an unknown case is not a placeholder, so the
   value holds none.
3. The value with its placeholder replaced by `x` is not a file name below the test folders (the existing
   `_file_name(language)` check):
   `<where>: must be a file name below the test folders, such as a_{name:snake}<ext>`.
4. A framework is given and the filled name matches none of its `files` patterns: the existing message, unchanged,
   `<where>: <value!r> is not a name `<files_key>` recognises as a test file`.

Otherwise the value is returned as written, with its case placeholder, so `ScenarioCoverage.file` holds
`test_{name:snake}.py`.

The messages of items 2 and 3 are reworded on purpose. Today they read "must hold `{name}` once, such as
a_{name}.ts", which offers as an example a value that this card refuses. The card's "messages unchanged" refers to
the findings, the docs and the corpora (note 4, line 301), which do not change. These two refusal texts are the one
deliberate wording change of this card, and their tests in
`tests/modules/spec/application/logic/test_testing.py:353-364` change with them.

`NAME` in `xarch/modules/spec/domain/values.py:242-243` and its docstring ("in snake_case") are replaced by what the
check needs: the bare form, to refuse, and the cased form built from the kernel's `CASES`. No file but the kernel
helper lists the cases.

### 3.4 The docs line

`docs_template._guard_line` (`docs_template.py:486`) replaces the whole `{name:<case>}` placeholder with `<name>`.
`docs/{cli,web,xarch}/testing.md` regenerate byte for byte; `docs/xarch/testing.md` keeps `test_<name>.py`.

### 3.5 The texts xarch says of the key

`xarch/architectures/presets/format/keys.yaml` describes the key as it is today. Update these lines:
- line 69, the fragment `coverage-guard`: `file: check_{name}%extension%` becomes `file: check_{name:snake}%extension%`.
  Without this change, every example that uses the fragment would be refused.
- line 919: "(`{name}` is <Name> in snake_case)" becomes "(`{name:<case>}` is <Name> in that case: snake, kebab, camel
  or pascal)".
- line 1065: `accepts: a name holding {name} once, for the use case` becomes
  `accepts: a name holding {name:<case>} once, <case> one of snake, kebab, camel, pascal, for the use case`.

`xarch/profile_values/testing.py:35-36` (the `ScenarioCoverage` docstring) says `{name:<case>}` standing for the use
case in the case it writes, in place of "`{name}` standing for the use case in snake_case".

Do these texts have to stay within the vocabulary the language-seam guard allows (`tests/architecture/test_language_seam.py`)? They do already. "snake", "kebab", "camel" and "pascal" are format words, not words of the Python data file.

### 3.6 The six profile lines

Each changes from `file: test_{name}.py` to `file: test_{name:snake}.py`, and nothing else in the file changes:

- `architecture.yaml:328`
- `xarch/architectures/cli.yaml:290`
- `xarch/architectures/web.yaml:292`
- `tests/bootstrap/corpora/stress.yaml:283`
- `tests/bootstrap/corpora/7cc6111.yaml:164`
- `tests/bootstrap/corpora/df537ca.yaml:184`

The `.tar.xz` archives and the `.json` corpora are not touched. `tests/bootstrap/test_recorded_corpora.py` replays
the edited yaml and its recorded findings must not change.

### 3.7 Tests and fakes that write a guard `file`

Every test or fake that writes `{name}` as a guard `file` value (explore list: `tests/modules/rules/builders.py:143`,
`tests/bootstrap/test_bundled_guards.py:28`, `tests/bootstrap/test_profile_file.py:46`,
`tests/modules/rules/adapters/test_spec_profile.py:56,121`, `tests/modules/rules/application/logic/test_must_import.py`,
`tests/modules/spec/application/logic/test_libraries_and_guards.py`, `test_profile_parsing_tests.py`,
`test_testing.py`; check `tests/bootstrap/test_other_framework.py`, `tests/fakes/*.py`,
`tests/bootstrap/test_bundled_architectures.py`, `tests/fakes/check_format.py` and
`tests/modules/rules/adapters/test_fs_source_tree_*.py`) writes `{name:snake}` instead. Their other expectations stay
as they are, except the two reworded refusals of 3.3, which are also pinned outside `test_testing.py`:
`tests/modules/spec/application/logic/test_profile_parsing_tests.py:590` expects
``scenarios.file: must hold `{name}` once, such as a_{name}.py`` and changes to the reworded message of 3.3.2
(``must hold `{name:<case>}` once, <case> one of snake, kebab, camel, pascal, such as a_{name:snake}.py``).
`tests/modules/rules/application/logic/test_scenarios.py:161` writes `file="{name}_test.py"` and changes to
`{name:snake}_test.py`. Find them with
`grep -rn '{name}' tests --include=*.py`. Many hits are `{name}` placeholders of a rule's `message`/`fix`
(README:876, 891). Those are a different feature and stay as they are.

### 3.8 The language-seam allowance moves

`tests/architecture/test_language_seam.py:147-151` exempts `("modules/rules/application/logic/scenarios.py", "_")`
as "the separator of snake_case". When `_snake_name` leaves `scenarios.py` that entry is stale, and a stale entry
fails the test (line 50, line 343). The entry is replaced by one for `("kernel/logic/cases.py", "_")` with the same
reason, reworded to the new key form: "the separator of snake_case, the case a profile asks for with `{name:snake}`
in the test file of a use case (guards.scenario-coverage.file); it is no private prefix". No other new allowance
should be needed. If one is (for `-`, say), it gets its own reason.

### 3.9 README and CHANGELOG

- README: nothing in it quotes the guard's `file` (`grep -n '{name}' README.md` hits only the message placeholders
  at 876 and 891). No README line changes.
- CHANGELOG, under `## [Unreleased]`, `### Changed`, one entry: the guard `scenario-coverage`'s `file` writes the case
  of the use case's name, `{name:snake}`, `{name:kebab}`, `{name:camel}` or `{name:pascal}`. The words are split as
  before (HTTPCheck is http, check). A bare `{name}` is refused with "write {name:snake} for what {name} meant". The
  bundled profiles write `test_{name:snake}.py`.

## 4. Tests that prove it

Tests are written first. Tables use `pytest.param(..., id="<a sentence>")`, as in `test_scenarios.py:34-42`. Both
`unit` and `integration` set `plain_tables: true` (`architecture.yaml:266, 278`), so a table test's body must not
branch.

| # | Test | Where | Tier, and why |
|---|---|---|---|
| T1 | `test_a_name_is_written_in_each_case`: the table of 3.1, one row per name, asserting the tuple of its four forms in `CASES` order | `tests/kernel/logic/test_cases.py` | unit: a pure rule of the kernel, called directly |
| T2 | `test_the_cases_are_four_in_order`: `CASES == ("snake", "kebab", "camel", "pascal")` | same | unit: the list both modules read |
| T3 | `test_snake_case_is_the_rule_of_before`: rows that pin the rule's edges: `Publish_Doc` gives `publish_doc`, `ABC` gives `abc`, `A` gives `a`, `X2Y` gives `x2_y` (each equal to today's regex) | same | unit: it holds the move byte for byte |
| T4 | `test_the_test_file_of_a_use_case_is_its_name_in_its_case`: the existing table in `test_scenarios.py:34-42`, with the profile's file `test_{name:snake}.py`, plus rows for `{name:kebab}.test.py`, `{name:camel}`, `{name:pascal}` naming `http-check.test.py`-style files in the finding | `tests/modules/rules/application/logic/test_scenarios.py` | unit: the guard's logic over facts built by hand |
| T5 | `test_a_bare_name_is_refused_with_its_hint`: `use_case_file("test_{name}.py", ...)` records exactly the fixed refusal of 3.3.1 and returns None; a row where `{name}` sits beside `{name:snake}` gets the same single refusal | `tests/modules/spec/application/logic/test_testing.py` | unit: a pure check of the spec module |
| T6 | `test_each_case_is_accepted`: the four values `a_{name:<case>}.py` return themselves, no problem | same | unit |
| T7 | `test_a_file_without_one_case_is_refused`: rows: no placeholder, two of one case, two of two cases, `{name:upper}`, `{name:Snake}`, `{name:}`, a non-string. Each gives the single "must hold `{name:<case>}` once ..." message | same | unit |
| T8 | the existing `test_under_several_endings_the_scenario_file_may_end_in_any_of_them` (353-364) rewritten to `{name:snake}.test.tsx` etc., expecting `such as a_{name:snake}.ts` | same | unit: pins the reworded message under a braced language |
| T9 | a profile file writing `file: test_{name}.py` is refused through `profile check` with the full prefixed line of 3.3.1 | `tests/bootstrap/test_profile_file.py` | wired: what `profile check` prints from a real file through bootstrap |
| T10 | the golden docs regenerate unchanged (existing `tests/bootstrap/test_docs_templates.py`) | existing | wired: byte-for-byte proof of 3.4 |
| T11 | the recorded corpora replay unchanged (existing `tests/bootstrap/test_recorded_corpora.py`) | existing | wired: byte-for-byte proof of 3.6 |
| T12 | the language-seam allowance (existing `test_language_seam.py`) passes with the moved entry, and would fail on the stale one | existing | guard: xarch's own source |
| T13 | `profile explain guards.scenario-coverage.file` (or the existing keys.yaml example test) prints the new `accepts` text, and every `<<coverage-guard>>` example parses | wherever keys.yaml texts and examples are pinned today (find with `grep -rn 'coverage-guard\|holding {name}' tests`) | wired: what the command prints |

The existing bundled-profile tests (`test_bundled_guards.py`, `test_bundled_architectures.py`) keep passing with
`{name:snake}` and prove that the shipped profiles still parse.

## 5. Out of scope

- Table forms: `TableForm`, `testing.tables`, `columns_from`, `testing.table` retired through the retired-keys table,
  `pytest.yaml` rewritten, the port and reader taking the list, `_rows` wording from the language (6.3, release
  step 19; note 8 item 3).
- Facts per form, the loop form, the no-form path, the second frameworks (note 8 items 4 to 7, later cards).
- The bare `{name}` refusal through the retired-keys table (`profile_keys.py:168-197`). That table is keyed by key
  name, not by a fragment of a value. This refusal is fixed text in `use_case_file` (explore finding).
- Any case beyond the four, and any key that sets a case outside the guard's `file` (framework or language data
  files; named dodge).
- `{name}` placeholders in a rule's `message`/`fix` (a different feature).
- The archived `.tar.xz` code and the `.json` corpora.
- The re-grep of note 8 item 7 (`_snake_name` gone everywhere): that is step 7's check. This card already removes
  `_snake_name` from `xarch/`.

## 6. Hand-off notes for the plan

- File map: create `xarch/kernel/logic/cases.py` and `tests/kernel/logic/test_cases.py`. Modify `scenarios.py`,
  `values.py`, `profile_checks.py`, `docs_template.py`, `profile_values/testing.py`, `keys.yaml`, the six profiles,
  `test_language_seam.py`, CHANGELOG.md, and the tests and fakes of 3.7.
- The kernel module must satisfy xarch's own `check --strict`: a module docstring, a docstring on every public
  function, no dead code (each name used outside its tests), stdlib imports only. `architecture.yaml` lets rules logic
  and spec logic import kernel logic (lines 22, 36, 51).
- Suggested interface (a plan may refine the names, but must keep one owner of the case list):
  `CASES: tuple[str, ...]`, `words(name: str) -> tuple[str, ...]`, `written(name: str, case: str) -> str`.
- Order: T1-T3 and the helper first. Then T5-T8 with `use_case_file`, `values.py`, keys.yaml and the six profiles
  and test fixtures in the same task, since a refused bare `{name}` breaks every fixture that still writes it. Then T4
  with `scenarios.py` and the seam allowance, then the docs line, then the CHANGELOG. Run the full gates last.
- `uv run pytest -q` takes over two minutes: run it in the background with `timeout`, and read the result at the end.

---

## File structure

| File | Responsibility | Task |
|---|---|---|
| `xarch/kernel/logic/cases.py` (create) | the four cases, their placeholders, the word split, the fill | 1 |
| `tests/kernel/logic/test_cases.py` (create) | T1, T2, T3 and the fill | 1 |
| `tests/architecture/test_language_seam.py` | the `_` allowance moves from `scenarios.py` to `cases.py` | 1 (add), 2 (remove stale) |
| `xarch/modules/spec/application/logic/profile_checks.py` | `use_case_file` refuses a bare `{name}` and checks one cased placeholder | 2 |
| `xarch/modules/spec/domain/values.py` | `NAME` becomes the bare form, refused | 2 |
| `xarch/modules/spec/application/logic/docs_template.py` | the docs line shows any `{name:<case>}` as `<name>` | 2 |
| `xarch/modules/rules/application/logic/scenarios.py` | `_test_file` fills through `filled`; `_snake_name`, `NAME`, `import re` go | 2 |
| `xarch/profile_values/testing.py` | the `ScenarioCoverage` docstring | 2 |
| `xarch/architectures/presets/format/keys.yaml` | the fragment, the guard's accepts, the file key's accepts | 2 |
| six profiles | `test_{name}.py` → `test_{name:snake}.py` | 2 |
| tests and fixtures writing a guard `file` | `{name}` → `{name:snake}`; reworded refusals | 2 |
| `CHANGELOG.md` | one `### Changed` entry | 3 |

---

### Task 1: The kernel helper `cases`

**Files:**
- Create: `xarch/kernel/logic/cases.py`
- Create: `tests/kernel/logic/test_cases.py`
- Modify: `tests/architecture/test_language_seam.py:147-151` (add one entry beside the `scenarios.py` one; that one stays until Task 2)

**Interfaces:**
- Consumes: nothing.
- Produces (Task 2 relies on these exact names):
  - `CASES: tuple[str, ...] = ("snake", "kebab", "camel", "pascal")`
  - `CASED: tuple[str, ...] = ("{name:snake}", "{name:kebab}", "{name:camel}", "{name:pascal}")`, built from `CASES`, same order
  - `written(name: str, case: str) -> str`: `name` in one of `CASES`
  - `filled(text: str, name: str) -> str`: `text` with each placeholder of `CASED` replaced by `written(name, <its case>)`; any other text, a bare `{name}` included, stays

- [ ] **Step 1: Write the failing tests**

Create `tests/kernel/logic/test_cases.py`:

```python
"""How a name is written in a case: split into words where the case of its letters changes, joined in the case a
profile asks for, and filled into a text in place of the placeholder that asks for it."""
import pytest

from xarch.kernel.logic.cases import CASED, CASES, filled, written


@pytest.mark.parametrize("name, forms", [
    pytest.param("Publish", ("publish", "publish", "publish", "Publish"), id="one word"),
    pytest.param("PublishDocument", ("publish_document", "publish-document", "publishDocument", "PublishDocument"),
                 id="two words"),
    pytest.param("HTTPCheck", ("http_check", "http-check", "httpCheck", "HttpCheck"), id="a run of capitals is one word"),
    pytest.param("MarkRead2", ("mark_read2", "mark-read2", "markRead2", "MarkRead2"), id="a digit stays with its word"),
])
def test_a_name_is_written_in_each_case(name, forms):
    assert tuple(written(name, case) for case in CASES) == forms


def test_the_cases_are_four_in_order_and_each_has_its_placeholder():
    assert (CASES, CASED) == (("snake", "kebab", "camel", "pascal"),
                              ("{name:snake}", "{name:kebab}", "{name:camel}", "{name:pascal}"))


@pytest.mark.parametrize("name, snake", [
    pytest.param("Publish_Doc", "publish_doc", id="an underscore stays inside its word"),
    pytest.param("ABC", "abc", id="a run of capitals alone is one word"),
    pytest.param("A", "a", id="one capital is one word"),
    pytest.param("X2Y", "x2_y", id="a capital after a digit starts a word"),
])
def test_snake_case_is_the_rule_of_before(name, snake):
    assert written(name, "snake") == snake


def test_no_character_but_a_change_of_case_ends_a_word():
    assert tuple(written("Publish_Doc", case) for case in CASES) == ("publish_doc", "publish_doc", "publish_doc",
                                                                     "Publish_doc")


@pytest.mark.parametrize("text, expected", [
    pytest.param("test_{name:snake}.py", "test_http_check.py", id="snake fills the words joined by an underscore"),
    pytest.param("{name:kebab}.test.ts", "http-check.test.ts", id="kebab fills them joined by a hyphen"),
    pytest.param("{name:camel}.test.ts", "httpCheck.test.ts", id="camel capitalises each word but the first"),
    pytest.param("{name:pascal}.test.ts", "HttpCheck.test.ts", id="pascal capitalises every word"),
    pytest.param("test_{name}.py", "test_{name}.py", id="a name with no case is no placeholder and stays"),
    pytest.param("test_{name:upper}.py", "test_{name:upper}.py", id="nor is a name in a case there is not"),
])
def test_a_text_is_filled_with_the_name_in_the_case_its_placeholder_asks_for(text, expected):
    assert filled(text, "HTTPCheck") == expected
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 120 uv run pytest tests/kernel/logic/test_cases.py -q`
Expected: collection ERROR, `ModuleNotFoundError: No module named 'xarch.kernel.logic.cases'`.

- [ ] **Step 3: Write the helper**

Create `xarch/kernel/logic/cases.py` (no comments; no backticks and no file extension such as `.py` in the docstrings, since the language-seam guard reads spans quoted as code and tokens of the language's data file in the kernel's source):

```python
"""How a name is written in a case: split into its words where the case of its letters changes, then joined in one of
the cases a profile may ask for, and filled into a text in place of the placeholder that asks for it ({name:snake},
...). Nothing else splits a name into words, joins words in a case or lists the cases."""
from __future__ import annotations

import re

CASES = ("snake", "kebab", "camel", "pascal")
"""The cases a profile may ask a name to be written in, in the order the format lists them."""
CASED = tuple(f"{{name:{case}}}" for case in CASES)
"""How a profile asks for a name in each of CASES, in the same order: {name:snake}, {name:kebab}, ..."""
_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def _words(name: str) -> tuple[str, ...]:
    """The words of a name, lowercased: a word ends before a capital that follows a lowercase letter or a digit, and
    before the last capital of a run of capitals followed by a lowercase letter (HTTPCheck is http, check); no other
    character ends one."""
    return tuple(word.lower() for word in _BOUNDARY.split(name))


def written(name: str, case: str) -> str:
    """The name written in one of CASES: snake joins its words with an underscore, kebab with a hyphen; camel
    capitalises each word but the first and pascal every word, both joining them with nothing between."""
    found = _words(name)
    if case == "snake":
        return "_".join(found)
    if case == "kebab":
        return "-".join(found)
    capitalised = [word[:1].upper() + word[1:] for word in found]
    return found[0] + "".join(capitalised[1:]) if case == "camel" else "".join(capitalised)


def filled(text: str, name: str) -> str:
    """The text with each placeholder of CASED in it replaced by the name written in that placeholder's case
    (PublishDocument in test_{name:snake}: test_publish_document); anything else in it stays as written."""
    for case, cased in zip(CASES, CASED):
        text = text.replace(cased, written(name, case))
    return text
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 120 uv run pytest tests/kernel/logic/test_cases.py -q`
Expected: all PASS (4 + 1 + 4 + 1 + 6 = 16 passed).

- [ ] **Step 5: Run the language-seam guard to see the new `_` reported**

Run: `timeout 300 uv run pytest tests/architecture/test_language_seam.py -q`
Expected: FAIL in `test_no_file_outside_the_reader_and_the_platform_writes_a_token_of_the_language_of_the_data_file[python]` with `Left contains one more item: ('kernel/logic/cases.py', '_')` and nothing else for `cases.py` (a `('kernel/logic/cases.py', '.py')` item means a docstring still names a `.py` file: reword it).

- [ ] **Step 6: Add the allowance for `cases.py`**

In `tests/architecture/test_language_seam.py`, directly after the closing line of the `("modules/rules/application/logic/scenarios.py", "_")` entry (the line ending `"{name} in that case",`, line 151) and before the `}` that closes `EXEMPT`, insert:

```python
    ("kernel/logic/cases.py", "_"): "the separator of snake_case, the case a profile asks for with `{name:snake}` in the "
                                    "test file of a use case (guards.scenario-coverage.file); it is no private prefix",
```

Leave the `scenarios.py` entry: `_snake_name` is still there until Task 2.

- [ ] **Step 7: Run the seam guard and ruff**

Run: `timeout 300 uv run pytest tests/architecture/test_language_seam.py tests/kernel -q && uv run ruff check`
Expected: all PASS; ruff `All checks passed!`.

Known and expected until Task 2: `uv run xarch check --strict` (and so `tests/architecture/test_self_check.py`) reports `CASES`, `CASED`, `written` and `filled` as "used by nothing outside kernel-logic/ ... (parts.kernel-logic.shared)". Task 2 gives them their two users (rules and spec). Do not change `architecture.yaml` to silence it.

- [ ] **Step 8: Commit**

```bash
git add xarch/kernel/logic/cases.py tests/kernel/logic/test_cases.py tests/architecture/test_language_seam.py
git commit -m "A name is written in a case by one kernel helper: its words split where the case of its letters changes, as scenario-coverage splits them today, joined in snake, kebab, camel or pascal, and filled in place of {name:<case>}"
```

---

### Task 2: The guard's `file` writes its case, and a bare `{name}` is refused

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:23` (import) and `:403-415` (`use_case_file`)
- Modify: `xarch/modules/spec/domain/values.py:242-243`
- Modify: `xarch/modules/spec/application/logic/docs_template.py:63-64` (import) and `:486`
- Modify: `xarch/modules/rules/application/logic/scenarios.py:4-8` (docstring), `:32` (`import re`), `:45-53`, `:124-126`
- Modify: `xarch/profile_values/testing.py:33-36`
- Modify: `xarch/architectures/presets/format/keys.yaml:69`, `:917-920`, `:1065`
- Modify: `architecture.yaml:328`, `xarch/architectures/cli.yaml:290`, `xarch/architectures/web.yaml:292`, `tests/bootstrap/corpora/stress.yaml:283`, `tests/bootstrap/corpora/7cc6111.yaml:164`, `tests/bootstrap/corpora/df537ca.yaml:184`
- Modify (tests): `tests/modules/spec/application/logic/test_testing.py`, `tests/modules/spec/application/logic/test_profile_parsing_tests.py:435,446,590-594`, `tests/modules/spec/application/logic/test_libraries_and_guards.py:13`, `tests/modules/rules/application/logic/test_scenarios.py:35-44,161`, `tests/modules/rules/builders.py:143`, `tests/modules/rules/adapters/test_spec_profile.py:56,121`, `tests/bootstrap/test_bundled_guards.py:28`, `tests/bootstrap/test_profile_file.py`, `tests/bootstrap/test_other_framework.py:33`, `tests/bootstrap/test_profile_explain.py`, `tests/architecture/test_language_seam.py:147-151`

**Interfaces:**
- Consumes (Task 1, `xarch.kernel.logic.cases`): `CASES`, `CASED`, `filled(text: str, name: str) -> str`.
- Produces: `use_case_file(value, framework, where, problems, language, files_key="testing.files") -> str | None`, same signature, new checks; `ScenarioCoverage.file` holds the value as written (`test_{name:snake}.py`); `values.NAME == "{name}"`, now the bare form that is refused.

#### 2a. The profile check (T5, T6, T7, T8 and Review Focus 2)

- [ ] **Step 1: Write the failing tests of `use_case_file`**

In `tests/modules/spec/application/logic/test_testing.py`:

1. Line 18, in `SCENARIOS`, change `"file": "test_{name}.py"}` to `"file": "test_{name:snake}.py"}`.
2. Line 227, change `{"file": "spec_{name}.py"}` to `{"file": "spec_{name:snake}.py"}`.
3. Replace the table of `test_a_bad_scenario_file_is_refused` (lines 232-239) with:

```python
@pytest.mark.parametrize("file, expected", [
    pytest.param("{name:snake}_{name:snake}.py", f"{ONCE}.py", id="a file holding the name twice is refused"),
    pytest.param("a/{name:snake}.py", "must be a file name below the test folders, such as a_{name:snake}.py",
                 id="a file with a folder is refused"),
    pytest.param("spec_{name:snake}.py", "'spec_{name:snake}.py' is not a name `testing.files` recognises as a test file",
                 id="a file the framework does not recognise as a test file is refused"),
])
```

   (the body of `test_a_bad_scenario_file_is_refused` stays as it is).
4. Line 277, change `{"file": "{name}_spec.py"}` to `{"file": "{name:snake}_spec.py"}`.
5. Replace the table of `test_under_several_endings_the_scenario_file_may_end_in_any_of_them` (lines 356-361) with:

```python
@pytest.mark.parametrize("file, kept, expected", [
    pytest.param("{name:snake}.test.tsx", "{name:snake}.test.tsx", [], id="a file of the second ending"),
    pytest.param("{name:snake}.test.mts", "{name:snake}.test.mts", [], id="a file of the third ending"),
    pytest.param("{name:snake}.test.js", None,
                 ["scenarios: must be a file name below the test folders, such as a_{name:snake}.ts"],
                 id="an ending the language does not have, the refusal printing the first"),
])
```

6. Directly below the `WRITE = ...` line near the top (line 39), add:

```python
BARE = "{name} with no case was removed in 0.3.0: write {name:snake} for what {name} meant"
ONCE = "must hold `{name:<case>}` once, <case> one of snake, kebab, camel, pascal, such as a_{name:snake}"
```

7. Append at the end of the file:

```python
@pytest.mark.parametrize("file", [
    pytest.param("test_{name}.py", id="a bare name"),
    pytest.param("test_{name}_{name:snake}.py", id="a bare name beside a cased one gets the one refusal"),
])
def test_a_bare_name_is_refused_with_its_hint(file):
    found: list[str] = []
    assert (use_case_file(file, None, "guards.scenario-coverage.file", found, PYTHON), found) == (
        None, [f"guards.scenario-coverage.file: {file!r}: {BARE}"])


@pytest.mark.parametrize("file", [
    pytest.param("a_{name:snake}.py", id="snake"),
    pytest.param("a_{name:kebab}.py", id="kebab"),
    pytest.param("a_{name:camel}.py", id="camel"),
    pytest.param("a_{name:pascal}.py", id="pascal"),
])
def test_each_case_is_accepted(file):
    found: list[str] = []
    assert (use_case_file(file, None, "scenarios", found, PYTHON), found) == (file, [])


@pytest.mark.parametrize("file", [
    pytest.param("a_x.py", id="no placeholder"),
    pytest.param("{name:snake}_{name:snake}.py", id="two of one case"),
    pytest.param("{name:snake}_{name:kebab}.py", id="two of two cases"),
    pytest.param("a_{name:upper}.py", id="a case that does not exist"),
    pytest.param("a_{name:Snake}.py", id="a case written with a capital"),
    pytest.param("a_{name:}.py", id="no case after the colon"),
    pytest.param("a_{name: snake}.py", id="a blank before the case"),
    pytest.param(3, id="not a string"),
])
def test_a_file_without_one_case_is_refused(file):
    found: list[str] = []
    assert (use_case_file(file, None, "scenarios", found, PYTHON), found) == (None, [f"scenarios: {ONCE}.py"])


@pytest.mark.parametrize("file", [
    pytest.param("test_{name:snake}.py", id="snake"),
    pytest.param("test_{name:kebab}.py", id="kebab"),
    pytest.param("test_{name:camel}.py", id="camel"),
    pytest.param("test_{name:pascal}.py", id="pascal, its name filled with a capital"),
])
def test_a_file_in_any_case_is_checked_against_the_testing_patterns(file):
    assert problems(covered(guards={"scenario-coverage": SCENARIOS | {"file": file}})) == []


@pytest.mark.parametrize("case", [
    pytest.param("snake", id="snake"),
    pytest.param("kebab", id="kebab"),
    pytest.param("camel", id="camel"),
    pytest.param("pascal", id="pascal"),
])
def test_the_guard_line_shows_the_name_as_name_whatever_its_case(case):
    testing = {"files": ["*_spec.py"], "functions": "it_*"}
    lines = guard_lines(testing=testing, guards={"scenario-coverage": SCENARIOS | {"file": f"{{name:{case}}}_spec.py"}})
    assert "in `<name>_spec.py`" in lines[0]
```

In `tests/modules/spec/application/logic/test_profile_parsing_tests.py`:

8. Line 435, `"file": "test_{name}.py"}` → `"file": "test_{name:snake}.py"}`; line 446, `"test_{name}.py"),` → `"test_{name:snake}.py"),`.
9. Replace lines 590-594 (the three `file` rows of `test_a_bad_scenario_coverage_is_refused`) with:

```python
    pytest.param({"file": "test.py"}, [
        f"{SCENARIOS}.file: must hold `{{name:<case>}}` once, <case> one of snake, kebab, camel, pascal, such as "
        "a_{name:snake}.py"]),
    pytest.param({"file": "{name:snake}.rb"}, [
        f"{SCENARIOS}.file: must be a file name below the test folders, such as a_{{name:snake}}.py"]),
    pytest.param({"file": "{name:snake}.py"}, [
        f"{SCENARIOS}.file: '{{name:snake}}.py' is not a name `testing.files` recognises as a test file"]),
    pytest.param({"file": "test_{name}.py"}, [
        f"{SCENARIOS}.file: 'test_{{name}}.py': {{name}} with no case was removed in 0.3.0: write {{name:snake}} for "
        "what {name} meant"]),
```

   (The second string of the first and last rows is not an f-string, so its braces are single.)

In `tests/modules/spec/application/logic/test_libraries_and_guards.py`:

10. Line 13, `FILE = "test_{name}.py"` → `FILE = "test_{name:snake}.py"`.

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_libraries_and_guards.py -q`
Expected: FAIL. Among them: `test_a_bare_name_is_refused_with_its_hint` (today's message is "must hold `{name}` once"), `test_each_case_is_accepted` (refused today: no `{name}`), `test_a_file_without_one_case_is_refused`, `test_a_file_in_any_case_is_checked_against_the_testing_patterns`, the rewritten rows of `test_a_bad_scenario_file_is_refused` and `test_a_bad_scenario_coverage_is_refused`, and every test that parses `SCENARIOS`/`GUARDS`/`FILE` (refused today).

- [ ] **Step 3: Rewrite `use_case_file` and `NAME`**

In `xarch/modules/spec/domain/values.py`, replace lines 242-243:

```python
NAME = "{name}"
"""Stands, in the file name a guard expects, for the name of the use case in snake_case."""
```

with:

```python
NAME = "{name}"
"""A name with no case, which the file a guard expects may no longer hold: refused since 0.3.0, the case written in
its place ({name:snake} for what it meant)."""
```

In `xarch/modules/spec/application/logic/profile_checks.py`, after line 12 (`from xarch.kernel.logic import names`) add:

```python
from xarch.kernel.logic.cases import CASED, CASES, filled
```

and replace `use_case_file` (lines 403-415) with:

```python
def use_case_file(value: Any, framework: Framework | None, where: str, problems: list[str], language: Language,
                  files_key: str = "testing.files") -> str | None:
    such = f"such as a_{CASED[0]}{language.checked.extension}"
    if isinstance(value, str) and NAME in value:
        problems.append(f"{where}: {value!r}: {NAME} with no case was removed in 0.3.0: write {CASED[0]} for what "
                        f"{NAME} meant")
        return None
    if not isinstance(value, str) or sum(value.count(cased) for cased in CASED) != 1:
        problems.append(f"{where}: must hold `{{name:<case>}}` once, <case> one of {', '.join(CASES)}, {such}")
        return None
    name = filled(value, "x")
    if not _file_name(language).fullmatch(name):
        problems.append(f"{where}: must be a file name below the test folders, {such}")
        return None
    if framework is not None and not any(fnmatchcase(name, pattern) for pattern in framework.files):
        problems.append(f"{where}: {value!r} is not a name `{files_key}` recognises as a test file")
        return None
    return value
```

(Line 23 keeps importing `NAME` from `values`.)

- [ ] **Step 4: Show any case as `<name>` in the docs line**

In `xarch/modules/spec/application/logic/docs_template.py`:
- Remove `    NAME,` (line 64) from the `from xarch.modules.spec.domain.values import (...)` list.
- Insert `from xarch.kernel.logic.cases import CASED` as a new line directly *before* line 57 (`from xarch.kernel.logic.imports import shown_target, targets_phrase`), so the kernel imports stay sorted (`cases` < `imports`; ruff's `I` rule checks it).
- (`_named` is already a function of this file, at line 625, with another signature: the new helper is `_uncased`.)
- At line 486 replace `` `{file.replace(NAME, '<name>')}` `` with `` `{_uncased(file)}` ``.
- Directly after the end of `_guard_line`, add:

```python
def _uncased(file: str) -> str:
    """The file a guard expects as the docs show it: its {name:<case>}, whatever the case, as <name>."""
    for cased in CASED:
        file = file.replace(cased, "<name>")
    return file
```

- [ ] **Step 5: Run the spec tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/spec -q`
Expected: PASS, except tests that load a bundled profile or `architecture.yaml` (they still write `test_{name}.py`, refused now) — those are fixed in 2c. Note which ones fail; only bundled-profile loaders may.

#### 2b. The guard fills its case (T4)

- [ ] **Step 6: Write the failing test of the guard**

In `tests/modules/rules/builders.py` line 143, change `"test_{name}.py"),` to `"test_{name:snake}.py"),`.

In `tests/modules/rules/application/logic/test_scenarios.py`, replace lines 35-44 (the table and `test_the_test_file_of_a_use_case_is_its_name_in_snake_case`) with:

```python
@pytest.mark.parametrize("use_case, written, file", [
    pytest.param("Publish", "test_{name:snake}.py", "test_publish.py", id="one word"),
    pytest.param("PublishDocument", "test_{name:snake}.py", "test_publish_document.py", id="two words"),
    pytest.param("HTTPCheck", "test_{name:snake}.py", "test_http_check.py", id="a run of capitals is one word"),
    pytest.param("MarkRead2", "test_{name:snake}.py", "test_mark_read2.py", id="a digit stays with its word"),
    pytest.param("HTTPCheck", "{name:kebab}.test.py", "http-check.test.py", id="kebab joins the words with a hyphen"),
    pytest.param("HTTPCheck", "{name:camel}.test.py", "httpCheck.test.py", id="camel capitalises each word but the first"),
    pytest.param("HTTPCheck", "{name:pascal}.test.py", "HttpCheck.test.py", id="pascal capitalises every word"),
])
def test_the_test_file_of_a_use_case_is_its_name_in_its_case(use_case, written, file):
    results = source("modules/docs/contract/results.py", unions=(Union(4, f"{use_case}Result", ("Done", "Failed")),))
    checked = profile(scenarios=replace(PROFILE.scenarios, file=written))
    assert problems(app=(results,), checked=checked) == [f"app/modules/docs/contract/results.py:4: {use_case}Result has "
                                                         f"no test file {file} among the integration tests of docs "
                                                         "(scenario-coverage)"]
```

At line 161 (`test_the_test_file_follows_the_guards_file_pattern`), change `file="{name}_test.py"` to `file="{name:snake}_test.py"`.

In `tests/modules/rules/adapters/test_spec_profile.py`, lines 56 and 121: `"test_{name}.py")` → `"test_{name:snake}.py")`.

- [ ] **Step 7: Run it to verify it fails**

Run: `timeout 300 uv run pytest tests/modules/rules/application/logic/test_scenarios.py -q`
Expected: FAIL: `test_the_test_file_of_a_use_case_is_its_name_in_its_case` (all 7 rows) report `no test file test_{name:snake}.py` / `{name:kebab}.test.py` (the placeholder is not filled), and every coverage test of `PROFILE` reports a missing test file.

- [ ] **Step 8: Fill through the kernel helper**

In `xarch/modules/rules/application/logic/scenarios.py`:
- Delete `import re` (line 32).
- Add `from xarch.kernel.logic.cases import filled` before `from xarch.kernel.violations import Violation`.
- Delete lines 45-46 (`NAME = "{name}"` and its docstring) and lines 50-53 (`_snake_name` and the two blank lines after it), leaving `RULE`, then `Problem` and its docstring, then two blank lines, then `def violations`.
- Replace `_test_file` (lines 124-126) with:

```python
def _test_file(union: Union, guard: ScenarioCoverage) -> str:
    """The name of the test file the guard expects for the use case a union holds the results of: the guard's file,
    the use case's name written in the case its placeholder asks for."""
    return filled(guard.file, union.name.removesuffix(guard.suffix))
```

- In the module docstring, replace these four lines (5-8):

```
`file` with `{name}` replaced by <Name> in snake_case (PublishDocument: publish_document), among the files of the
table tier in the same instance (see tier_of). That file must hold a table, read from its syntax tree; the
decorator, the row and the keyword of a row's id are the names the guard is given (see CaseTable), a test function
is one whose name matches the profile's pattern:
```

with:

```
`file` with `{name:<case>}` replaced by <Name> in that case (PublishDocument with `{name:snake}`: publish_document),
among the files of the table tier in the same instance (see tier_of). That file must hold a table, read from its
syntax tree; the decorator, the row and the keyword of a row's id are the names the guard is given (see CaseTable), a
test function is one whose name matches the profile's pattern:
```

- [ ] **Step 9: Run the rules tests to verify they pass**

Run: `timeout 300 uv run pytest tests/modules/rules -q`
Expected: PASS.

#### 2c. The profiles, the texts of the key, the wired tests (T9, T13) and the seam (T12)

- [ ] **Step 10: Write the failing wired tests**

In `tests/bootstrap/test_profile_file.py`:
- Line 46, `file: "test_{name}.py"}` → `file: "test_{name:snake}.py"}`.
- Add imports: `from typer.testing import CliRunner` (directly after `import pytest`, in the same block, as `test_profile_explain.py` does) and `from xarch.bootstrap.app import app` (before `from xarch.bootstrap.wiring import load_architecture`).
- Append:

```python
BARE = ("guards.scenario-coverage.file: 'test_{name}.py': {name} with no case was removed in 0.3.0: write "
        "{name:snake} for what {name} meant")


def test_a_bare_name_in_the_file_of_the_scenario_guard_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, PRESET_PROFILE.replace("test_{name:snake}.py", "test_{name}.py"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert (caught.value.problems, checked.exit_code) == ((f"{path}: {BARE}",), 1)
    assert f"    {path}: {BARE}" in checked.output.splitlines()
```

In `tests/bootstrap/test_profile_explain.py`:
- Add imports `from xarch.bootstrap.wiring import build_controllers, load_architecture` (replace the existing `from xarch.bootstrap.wiring import build_controllers`) and `from xarch.profile_values.testing import ScenarioCoverage` (after the `xarch.modules.spec.domain.profile_keys` import).
- Append:

```python
def test_the_file_of_the_scenario_guard_is_explained_with_its_cases_and_its_example_loads(tmp_path):
    key = json.loads(runner.invoke(app, ["profile", "explain", "guards.scenario-coverage.file", "--format", "json"]).output)
    guard = json.loads(runner.invoke(app, ["profile", "explain", "guards.scenario-coverage", "--format", "json"]).output)
    (tmp_path / "example.yaml").write_text("name: documents-app\n" + key["example"])
    loaded = load_architecture(tmp_path / "example.yaml")
    assert key["accepts"] == ("a name holding {name:<case>} once, <case> one of snake, kebab, camel, pascal, for the "
                              "use case")
    assert "(`{name:<case>}` is <Name> in that case: snake, kebab, camel or pascal)" in guard["accepts"]
    assert [g.file for g in loaded.guards if isinstance(g, ScenarioCoverage)] == ["check_{name:snake}.py"]
```

In `tests/bootstrap/test_bundled_guards.py` line 28: `"test_{name}.py"),` → `"test_{name:snake}.py"),`.

In `tests/bootstrap/test_other_framework.py` line 33: `file: "{name}_spec.py"` → `file: "{name:snake}_spec.py"`.

- [ ] **Step 11: Run them to verify they fail**

Run: `timeout 300 uv run pytest tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_other_framework.py -q`
Expected: FAIL: the bundled profiles and `architecture.yaml` still write `test_{name}.py` and are refused (`test_the_preset_holds_exactly_what_the_bundled_profiles_spell_out`, `test_the_bundled_profiles_use_every_guard_of_their_own`, ...); the explain test fails on `accepts` (still "a name holding {name} once") and on loading the example (`check_{name}.py` refused). `test_a_bare_name_in_the_file_of_the_scenario_guard_is_refused_with_its_hint` may already pass (the refusal is in since step 3); that is fine.

- [ ] **Step 12: Change the six profile lines**

```bash
for f in architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml \
         tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml; do
  sed -i 's/^\(    file: test_\){name}\.py$/\1{name:snake}.py/' "$f"
done
git diff --numstat architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/
```

Expected: six lines `1	1	<file>`, no `.json` or `.tar.xz` listed. Check with `git diff -U0` that each hunk is exactly `-    file: test_{name}.py` / `+    file: test_{name:snake}.py` at the line of the spec's 3.6 list.

- [ ] **Step 13: Change the texts xarch says of the key**

In `xarch/architectures/presets/format/keys.yaml`:
- Line 69: `        file: check_{name}%extension%` → `        file: check_{name:snake}%extension%`.
- Lines 917-920 (the `accepts` of `guards.scenario-coverage`), replace:

```
      {results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], file: <name>}: every
      variant of a union named <Name><suffix> in a results part is the result column of a row of the table in its use
      case's test file <file> (`{name}` is <Name> in snake_case) of that tier, or is named by a standalone test of it;
      every row is a `testing.table.row` call with a `testing.table.id`, and a table test has no branching; read from
      the syntax tree, never run
```

  with:

```
      {results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], file: <name>}: every
      variant of a union named <Name><suffix> in a results part is the result column of a row of the table in its use
      case's test file <file> (`{name:<case>}` is <Name> in that case: snake, kebab, camel or pascal) of that tier, or
      is named by a standalone test of it; every row is a `testing.table.row` call with a `testing.table.id`, and a
      table test has no branching; read from the syntax tree, never run
```

- Line 1065: `    accepts: a name holding {name} once, for the use case` →
  `    accepts: a name holding {name:<case>} once, <case> one of snake, kebab, camel, pascal, for the use case`.

In `xarch/profile_values/testing.py`, replace the last two lines of the `ScenarioCoverage` docstring (lines 35-36):

```
    how the table is written, and the name of a use case's test file, `{name}` standing for the use case in
    snake_case."""
```

with:

```
    how the table is written, and the name of a use case's test file, `{name:<case>}` standing for the use case in
    the case it writes."""
```

- [ ] **Step 14: Run the wired tests to verify they pass**

Run: `timeout 600 uv run pytest tests/bootstrap/test_profile_file.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_docs_templates.py tests/bootstrap/test_recorded_corpora.py -q`
Expected: PASS. `test_docs_templates.py` passing proves the golden docs regenerate unchanged (T10); `test_recorded_corpora.py` passing proves the corpora replay unchanged (T11).

- [ ] **Step 15: See the stale seam allowance fail**

Run: `timeout 300 uv run pytest tests/architecture/test_language_seam.py -q`
Expected: FAIL in `test_every_exemption_is_one_some_language_still_needs` with `('modules/rules/application/logic/scenarios.py', '_')` listed: `_snake_name` is gone.

- [ ] **Step 16: Remove the stale entry**

In `tests/architecture/test_language_seam.py`, delete the five lines of the entry:

```python
    ("modules/rules/application/logic/scenarios.py", "_"): "the separator of snake_case, which the profile format "
                                                            "defines `{name}` to be in the test file of a use case "
                                                            "(guards.scenario-coverage.file); it is no private prefix, "
                                                            "and a profile in another language would still say "
                                                            "{name} in that case",
```

The `("kernel/logic/cases.py", "_")` entry added in Task 1 stays.

- [ ] **Step 17: Confirm no guard `file` still writes a bare `{name}`**

Run: `grep -rnE "[a-z_./]\{name\}|\{name\}[._a-z]" tests xarch architecture.yaml --include=*.py --include=*.yaml | grep -vE 'f"|f'"'"'|tar.xz'`
Expected: only these hits remain, none a guard `file`: `tests/modules/rules/application/logic/test_must_import.py:17` and `:93` (message templates), `tests/modules/spec/application/logic/test_language_file.py:171` (an `importing` value), the bare-name rows added in this task (`test_testing.py`, `test_profile_parsing_tests.py`, `test_profile_file.py`, `test_cases.py`), and `test_language_seam.py`'s `cases.py` reason. If any other hit is a guard `file`, change it to `{name:snake}`.

- [ ] **Step 18: Run the gates that read xarch's own source**

Run: `timeout 600 uv run pytest tests/architecture tests/modules tests/kernel -q && uv run xarch check && uv run xarch check --strict && uv run ruff check && uv run xarch profile check architecture.yaml`
Expected: all PASS. The kernel-logic.shared findings of Task 1 are gone: `filled` is used by rules (`scenarios.py`) and spec (`profile_checks.py`), `CASED` by spec and through `filled`, `CASES` by spec and through `CASED`/`filled`, `written` through `filled`. If `xarch check --strict` still reports one of them, show the finding before changing anything.

- [ ] **Step 19: Commit**

```bash
git add xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/domain/values.py \
        xarch/modules/spec/application/logic/docs_template.py xarch/modules/rules/application/logic/scenarios.py \
        xarch/profile_values/testing.py xarch/architectures/presets/format/keys.yaml \
        architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml \
        tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml \
        tests/modules/spec/application/logic/test_testing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py \
        tests/modules/spec/application/logic/test_libraries_and_guards.py tests/modules/rules/application/logic/test_scenarios.py \
        tests/modules/rules/builders.py tests/modules/rules/adapters/test_spec_profile.py tests/bootstrap/test_bundled_guards.py \
        tests/bootstrap/test_profile_file.py tests/bootstrap/test_other_framework.py tests/bootstrap/test_profile_explain.py \
        tests/architecture/test_language_seam.py
git status --short
git commit -m "The guard scenario-coverage's file writes the case of the use case's name, {name:snake}, {name:kebab}, {name:camel} or {name:pascal}, and a bare {name} is refused: write {name:snake} for what {name} meant; the bundled profiles write test_{name:snake}.py and no finding, doc or corpus changes"
```

`git status --short` before the commit must show nothing else modified (the spec and plan under `docs/superpowers/` are committed by the workflow, not here).

---

### Task 3: CHANGELOG, and the gates on the whole branch

**Files:**
- Modify: `CHANGELOG.md:87-88` (first entry of `### Changed` under `## [Unreleased]`)

**Interfaces:**
- Consumes: the behaviour of Tasks 1 and 2.
- Produces: nothing code reads.

- [ ] **Step 1: Confirm README needs no change**

Run: `grep -n '{name' README.md`
Expected: only the rule-message placeholders (around lines 876 and 891), none a guard `file`. README is not edited.

- [ ] **Step 2: Add the CHANGELOG entry**

In `CHANGELOG.md`, under `## [Unreleased]`, the `### Changed` heading is at line 87 followed by a blank line. Insert directly after that blank line, before the entry starting `- The description of the fact \`function.tables\``:

```markdown
- The guard `scenario-coverage`'s `file` writes the case of the use case's name: `{name:snake}`, `{name:kebab}`,
  `{name:camel}` or `{name:pascal}`, so `{name:kebab}.test.ts` looks for `http-check.test.ts`. The words are split as
  before (HTTPCheck is http, check). A bare `{name}` is refused with "write {name:snake} for what {name} meant". The
  bundled profiles write `test_{name:snake}.py`.
```

- [ ] **Step 3: Run the full gates**

Run the suite in the background and the other gates meanwhile:

```bash
timeout 900 uv run pytest -q > /tmp/6-2-pytest.txt 2>&1; echo "exit $?" >> /tmp/6-2-pytest.txt
```

(as a background command), then:

```bash
uv run xarch check && uv run xarch check --strict && uv run ruff check && uv run xarch profile check architecture.yaml
git diff --stat HEAD -- docs/cli docs/web docs/xarch tests/bootstrap/corpora/*.json tests/bootstrap/corpora/*.tar.xz
```

Expected: each command exits 0; the `git diff --stat` prints nothing (golden docs and recorded corpora untouched). When the background run ends, `tail -5 /tmp/6-2-pytest.txt` shows `passed` with no `failed` or `error`, and `exit 0`.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "CHANGELOG says the guard scenario-coverage's file writes the case of {name}, the words split as before, a bare {name} refused with its hint and the bundled profiles writing test_{name:snake}.py"
```

---

## Self-review against the spec

- 3.1 the helper, its table, `CASES` in one place: Task 1 (T1, T2, T3; `CASED` also there, so no other file spells a placeholder per case).
- 3.2 the guard fills its case; `_snake_name`, `import re`, `NAME` leave `scenarios.py`; docstring reworded: Task 2, steps 6-9 (T4).
- 3.3 `use_case_file` in the order 1-4, one problem each, value returned as written; `values.NAME` the bare form; the cased form from the kernel: Task 2, steps 1-5 (T5-T8). Deviation, deliberate: item 3 fills the placeholder through `filled(value, "x")`, so a pascal file is checked as `X` rather than `x`. It is what makes spec a second user of `filled`, which `parts.kernel-logic.shared: 2` requires. Review Focus 2 pins that a pascal file is still accepted.
- 3.4 the docs line: Task 2, step 4; T10 at step 14; Review Focus 3.
- 3.5 keys.yaml lines 69, 919, 1065 and the `ScenarioCoverage` docstring: Task 2, step 13 (T13 at steps 10-14).
- 3.6 the six profile lines: Task 2, step 12; T11 at step 14.
- 3.7 tests and fakes: Task 2, steps 1, 6, 10, 17 (`tests/fakes/*.py`, `test_fs_source_tree_*.py`, `test_must_import.py` and `test_bundled_architectures.py` checked: none writes a guard `file`).
- 3.8 the seam allowance moves: Task 1 step 6 (add), Task 2 steps 15-16 (remove the stale one, T12).
- 3.9 README unchanged, CHANGELOG entry: Task 3.
- 4: T1-T13 each placed above. 5: nothing out of scope is touched. 6: the gates at Task 2 step 18 and Task 3 step 3.
<!-- task-pipeline: validated -->
