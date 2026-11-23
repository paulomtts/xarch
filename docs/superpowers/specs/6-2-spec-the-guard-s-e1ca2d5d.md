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
