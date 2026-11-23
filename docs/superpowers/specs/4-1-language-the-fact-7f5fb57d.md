# 4.1 language: the fact `function.top_level` replaces the field `top-level`

Card `7f5fb57d`, subtask of `c34d7f47`. Release step 9 of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3).

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**):

- 2.1 (lines 237-247): the Needs column of the kind `functions` is `function`, `function.top_level` "(new, 2.9)",
  `public`.
- 2.9 (lines 397-425): the fact's text (line 403-404), Python supplies it `exact` (line 404), the field and filter
  `top-level` of kind `function` get `field_needs={"top-level": ("function.top_level",)}` and
  `guards.dead-code.tests_only` needs it (lines 405-406); the refusal goes through the existing `refused` with the
  needs text (lines 407-413).
- 5.1 item 10 (line 691): `rules/domain/vocabulary.py`: "`function.top_level` field needs; the texts at 35, 246, 295,
  322, 360-362, 392".
- 5.1 item 11 (line 692): `FACTS` and `python.yaml` `supplies`: `function.top_level`.
- 7 item 1 (line 803): "The fact `function.top_level` (release step 9). Tests first: a language without it refuses
  `holds.functions`."
- Dodges (line 966): "A test of the language's name in spec (`if language.name == ...`) where a fact of `supplies`
  should decide."

R3 rules inherited: gap **G6** (lines 420-421): "whether an eval's `keep` filters are held to their field needs was
not found. Step 9 should test it."; **O4**, **O5** (lines 228-229): README and CHANGELOG lines under `[Unreleased]`;
**O8** (line 232): golden docs `docs/{cli,web,xarch}/testing.md` regenerated and the diff read, never hand-edited.

## 1. Goal

Whether a function is defined at the top level of its file, in no class, becomes a fact a language's reader says it
supplies, `function.top_level`, like `public` (8d) and `class.record` (8e) before it. Every check that reads the field
`top-level` of a function needs that fact, so a language whose data file does not list it is refused the keys and
checks that read it, at load, with the one needs text, instead of loading and passing in silence. Python supplies it
`exact`; its reader already sets the trait `top-level` on every function fact, so no Python finding, recorded corpus
or golden doc moves.

The step also closes R3 G6: an eval of the profile's own is held to the facts its `keep` filters read, as a check of
the profile's own already is.

## 2. Behaviour

### 2.1 The fact

- `FACTS` (`xarch/profile_values/capabilities.py`) gains `"function.top_level": "whether a function is defined at the
  top level of its file, in no class"` (CS line 403-404, verbatim). It is placed directly after `class.record` (the
  order the language facts of this release were added in: `public`, `class.record`, `function.top_level`). A test pins
  the place and the text.
- `xarch/architectures/presets/language/python.yaml` `supplies` gains `function.top_level: exact`. No other language
  data file changes: the test-only languages `tests/fakes/languages/{brace,percent}.yaml` list no `supplies` (an
  unchecked language), so nothing is refused for them.
- Python's reader does not change.

### 2.2 Who needs it

- The kind `function` (`xarch/modules/rules/domain/vocabulary.py`, `Kind("function", ...)`) gains
  `"top-level": ("function.top_level",)` in its `field_needs`, beside `forwards`, `forwarded`, `returned`, `public`.
  `Rule.needs` (`xarch/modules/rules/domain/rule.py:126-137`) then derives the need for every rule of kind `function`
  whose `keep`, `exempt` or `where` reads the field `top-level`, written plain or negated (`not top-level` still reads
  the field). No filter's own `facts` change.
- `NEEDS` (`xarch/modules/spec/domain/key_table.py`) gains `function.top_level` on exactly two keys:
  `parts.<part>.holds` and `guards.dead-code.tests_only` (CS 2.9 line 405-406; CS 2.1 for holds). After the step,
  `sorted(key.address for key in KEYS if "function.top_level" in key.needs) == ["guards.dead-code.tests_only",
  "parts.<part>.holds"]`. `guards.dead-code.known` is not given it (the card names only `tests_only`).
- `holds` is one key today, so a language without the fact is refused `holds: functions` and `holds: classes` alike
  (both rules of `holds` are under the one key). Refusing per kind, and not refusing a part of classes (CS 2.9 line
  415-418), belongs to the map of kinds, card 4.4; see section 4.
- The rules' derived needs and `NEEDS` must keep agreeing: `tests/bootstrap/test_needs_agree.py` stays green with no
  edit to its profile, or with an edit only if it reports a disagreement this step introduces (then the fix is in
  `NEEDS`, not in the test).

### 2.3 The refusal at load (keys of the profile)

Through the existing `refused` of `xarch/modules/spec/application/logic/profile_needs.py`; no new wording. For the
profile `layered.yaml` of `tests/modules/spec/profiles.py`, a language `untopped` whose reader supplies every fact of
`FACTS` but `function.top_level`, and `parts.service.holds: functions`, loading fails with exactly one problem:

    layered.yaml: parts.service.holds: its check reads function.top_level (whether a function is defined at the top
    level of its file, in no class), which the language untopped does not supply: drop parts.service.holds, or check
    the app with a language whose reader supplies function.top_level

(one line, no break). `guards: {dead-code: {tests_only: ...}}` (with whatever value turns `tests_only` on, as the
existing dead-code tests write it) under the same language fails with the same text at `guards.dead-code.tests_only`.
With Python's `supplies` in place of the language's, both load and `approximate == ()`. The decision is made only
from `supplies`; spec never tests the language's name (CS line 966).

### 2.4 The refusal of a check of the profile's own

No code change: `own_checks._supplied` already refuses a check by `rule.needs`. Once `field_needs` carries the fact, a
check of kind `function` whose `keep` (or `exempt`, or `where`) names `top-level`, under a `CheckedLanguage` whose
`supplies` lack `function.top_level`, is the problem:

    checks.<name>: needs function.top_level (whether a function is defined at the top level of its file, in no
    class), which the reader of <title> does not supply: read another kind of fact, or drop the check

and is not made. With the fact supplied it is made, with no problem.

### 2.5 The refusal of an eval of the profile's own (R3 G6)

Today an eval (`Asked`) is made into a rule by `xarch/modules/rules/application/logic/asked.py` `made(name, asked)`
with no look at the language; it is held only to the vocabulary. After the step:

- `made` takes the profile's language (`CheckedLanguage`) and returns, beside the vocabulary problems, one problem per
  fact of the eval rule's `needs` that the language's `supplies` lack outright (a shortfall whose `note` is `None`, as
  `own_checks` does it, through `kernel/logic/capabilities.shortfalls`). A fact supplied only partly is not a
  problem. When `language.supplies is None` (an unchecked language) there is no such problem.
- The problem's text, at the eval's address, mirrors the check's:

      evals.<name>: needs <fact> (<FACTS[fact]>), which the reader of <title> does not supply: read another kind of
      fact, or drop the eval

- An eval with such a problem is not made: `made` returns `None` and its problems, so its examples are not read and
  `AskingService.kept` raises `ChecksRefused` with the problems, as for a vocabulary problem.
- The two callers pass `profile.language`: `ExamplesService._held`
  (`xarch/modules/rules/application/services/examples.py:49`) and `AskingService.kept`
  (`xarch/modules/rules/application/services/asking.py:23`). `xarch profile check` therefore shows the problem among
  the evals' problems.
- The needs-of-a-rule-against-a-language logic is shared between `own_checks` and `asked` (one helper in
  rules' application logic, taking the address and the last words of the text), not written twice. `own_checks`'s
  text does not change.
- This holds for every fact an eval needs, not only `function.top_level`: an eval that reads `function` and keeps
  `public` under a language without `public` is refused likewise. Python supplies every fact, so no bundled profile's
  eval and xarch's own `architecture.yaml` change outcome.

### 2.6 Texts

- `vocabulary.py`: the field text `"top-level"` (line 177) and the filter `top-level` (line 281) keep their words;
  CS 5.1 item 10's line numbers were taken at `6dda0e7` and those lines (35, 246, 295, 322, 360-362, 392 there) are
  the `may_import` texts, which belong to the `imports` steps (release steps 13-14, CS 7 items 5-6). This step changes
  only `field_needs` in that file.
- `xarch/architectures/presets/format/keys.yaml`: no edit; `profile explain` derives a key's needs from `NEEDS`.
- README (`README.md`, the language paragraph ending at line ~159, "Whether a class is a record ... which `holds` and
  the filter `record` read."): one sentence after it, in the same register: whether a function is defined at the top
  level of its file is the fact `function.top_level` a reader supplies, which `holds`, `guards.dead-code.tests_only`
  and the filter `top-level` read.
- CHANGELOG `## [Unreleased]`: under `### Added`, a first bullet in the shape of the `class.record` bullet: the fact
  `function.top_level`, its text, that `parts.<part>.holds`, `guards.dead-code.tests_only` and a check of your own or
  an eval whose filter reads `top-level` need it, that a language that does not supply it is refused them with the
  needs text, that Python supplies it exactly. Under `### Changed` (create the heading if absent, after `### Added`),
  one bullet: an eval of your own is now held to the facts it reads, as a check of your own is: one that reads a fact
  the language's reader does not supply is refused at its address.
- Golden docs: regenerated with the repository's regenerate command, the diff read. None is expected; any line that
  moves is a defect of the step unless it names `function.top_level` in a needs list the docs already print.

## 3. Tests (written first)

Each test fails before the change and passes after it. Tier names follow the repository: `tests/modules/**` unit and
use-case tests; `tests/bootstrap/**` whole-program tests.

| # | Test | File | Tier and why |
|---|---|---|---|
| T1 | `function.top_level` is the fact after `class.record`, with the text of CS line 403-404 | `tests/modules/spec/application/logic/test_profile_needs.py` (beside `test_class_record_is_a_fact_after_public`) | unit: `FACTS` is a pure table |
| T2 | Under `untopped` (every fact of `FACTS` but `function.top_level`, built like `UNRECORDED`), `parts.service.holds: functions` is refused with exactly the text of 2.3; with Python's supplies it loads and `approximate == ()`; `KEYS` needing the fact are exactly `["guards.dead-code.tests_only", "parts.<part>.holds"]` | same file | unit (spec logic): load-time refusal is spec's `refused`, decided from `supplies` alone |
| T3 | Under `untopped`, `guards.dead-code.tests_only` turned on is refused with the same text at `guards.dead-code.tests_only`; with Python's supplies it loads | same file | unit (spec logic): the second key of the card |
| T4 | The existing `UNRECORDED` and `UNSAID` tests still expect only their own refusal (they supply `function.top_level`); their "said" variants (Python's supplies) still load: run unchanged | same file | unit: guards against a refusal leaking onto the wrong fact |
| T5 | `KINDS` kind `function` `field_needs["top-level"] == ("function.top_level",)`, and a `Rule` of kind `function` with `keep` `top-level` has `function.top_level` in `needs`, also with `not top-level` | `tests/modules/rules/domain/test_vocabulary.py` (beside line 53's assertion) and `tests/modules/rules/domain/` rule needs test if one exists, else the same file | unit: pure vocabulary and `Rule.needs` |
| T6 | A check of the profile's own, kind `function`, `keep [top-level]`, under a `CheckedLanguage` whose supplies lack the fact, is the problem of 2.4 and not made; with the fact supplied, made | `tests/modules/rules/application/logic/test_own_checks.py` | unit: `own_checks.made` with a hand-built language |
| T7 | `made("rule", Asked("function", Scope(APP, "domain"), (Condition("top-level"),)), language)` with a language lacking `function.top_level` returns `None` and `["evals.rule: needs function.top_level (whether a function is defined at the top level of its file, in no class), which the reader of <title> does not supply: read another kind of fact, or drop the eval"]`; with the fact supplied, a rule and `[]`; with `supplies=None`, a rule and `[]`; with the fact supplied only partly (a `Supply` with a note), a rule and `[]` | `tests/modules/rules/application/logic/test_asked.py` | unit: the G6 rule-level behaviour; existing tests there gain the language argument |
| T8 | `xarch profile check` (use case, `ExamplesService` through `controller`, `FakeProfiles`): a profile whose language lacks `function.top_level` and whose eval keeps `top-level` reports the eval problem of T7 among the evals' problems and reads none of its examples | `tests/modules/rules/application/test_profile_check.py` | use case: proves `_held` passes `profile.language` |
| T9 | Keeping facts for an eval (`AskingService.kept` through `controller`) under the same profile raises `ChecksRefused` with that problem | `tests/modules/rules/application/test_kept.py` | use case: proves the second caller passes `profile.language` |
| T10 | `python.yaml`'s `supplies` lists `function.top_level` as `exact`: the existing agreement tests of Python's supplies against `FACTS` (run them; extend only if none pins every fact) | `tests/modules/spec/application/logic/test_language*.py` / `tests/bootstrap/` as found | unit/bootstrap: the data file is the source of the fact |
| T11 | `tests/bootstrap/test_needs_agree.py` stays green | as is | bootstrap: `NEEDS` and the rules' derived needs agree over a profile of every key |

All existing tests stay green; the gates are the card's: `uv run pytest -q` (in the background, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

## 4. Out of scope

- The kinds of `holds` (`holds` as a map, `parts.<part>.holds.functions` and the other nested addresses, refusing per
  kind, not refusing a part of `classes` in a language with no top-level functions, the explain line "holds reads no
  top-level functions ..."): card 4.4 (release step 12, CS 2.1-2.10, CS 7 item 4).
- The needs walker descending into `holds` and its kinds (`profile_needs._configured`): release step 11 (CS 7 item 3).
- The `may_import` texts of CS 5.1 item 10 (vocabulary lines 35, 246, 295, 322, 360-362, 392 at `6dda0e7`): the
  `imports` steps, release steps 13-14.
- Changing what `holds` or `dead-code` reads, or Python's reader.
- `guards.dead-code.known` needing the fact.
- Evals' load-time parsing in spec (`spec/application/logic/evals.py`): the field-needs table lives in rules, so the
  eval's needs are checked where it is made into a rule (2.5), not in spec.
- Recorded corpora under `tests/bootstrap/corpora/`: untouched.

## 5. Constraints for the plan

- No comments in xarch's code (docstrings only, in the register of the files around them).
- Tests first, each run red before the code that makes it green.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`.
- No `language.name ==` in spec or rules; decisions come from `supplies` only.
- Golden docs regenerated, never edited by hand; diff read.
- `.claude/` stays out of commits; nothing is pushed.
- Commit messages: one long sentence saying what changed, as `git log` shows.
