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

---

# 4.1 language: the fact `function.top_level` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make "a function is defined at the top level of its file" a fact `function.top_level` a language's reader supplies, needed by `parts.<part>.holds`, `guards.dead-code.tests_only` and every rule whose words read the field `top-level`, and hold an eval of the profile's own to the facts it reads, as a check of its own already is (R3 G6).

**Architecture:** The fact is one entry of `FACTS` (profile_values) and one line of `python.yaml`'s `supplies`. Rules derive a rule's needs from the vocabulary's `field_needs`; spec's key table `NEEDS` says the same for the two keys; `tests/bootstrap/test_needs_agree.py` holds both in step. The existing own-check refusal (`own_checks._supplied`) becomes a shared helper `unsupplied` that `asked.made` also calls, and the two services that make evals hand it `profile.language`.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/4-1-language-the-fact-7f5fb57d.md` (prepended above).

## Global Constraints

- `FACTS["function.top_level"] == "whether a function is defined at the top level of its file, in no class"`, placed directly after `class.record`.
- `python.yaml` `supplies` gains `function.top_level: exact`; no other language data file changes (`tests/fakes/languages/{brace,percent}.yaml` untouched).
- `sorted(key.address for key in KEYS if "function.top_level" in key.needs) == ["guards.dead-code.tests_only", "parts.<part>.holds"]`; `guards.dead-code.known` does not get it.
- Load-time refusal goes through spec's existing `refused`; no new wording there. Own-check text is unchanged.
- Eval refusal text: `evals.<name>: needs <fact> (<FACTS[fact]>), which the reader of <title> does not supply: read another kind of fact, or drop the eval`.
- No comments in xarch's code (docstrings only, in the register of the files around them).
- No `language.name ==` (or title test) in spec or rules; decisions come from `supplies` only.
- Python's reader does not change; no recorded corpus under `tests/bootstrap/corpora/` is edited.
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated, never hand-edited; diff read (none expected).
- `.claude/` stays out of commits; nothing is pushed.
- Commit messages: one long sentence saying what changed, as `git log` shows, then the `Co-Authored-By` trailer.
- Gates: `uv run pytest -q` (in the background, read at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Review Focus

- A rule that reads `top-level` negated (`not top-level`) or in `exempt` still reads the field, so it must need `function.top_level` (a reader who does not say it cannot say its negation either). Pinned in Task 2 Step 1 (`test_rule.py`).
- `holds: classes` is the rule that actually reads `top-level`, while `holds: functions` does not; both are under the one key `parts.<part>.holds` and both must be refused under a language without the fact. Pinned in Task 2 Step 1 (parametrized `test_profile_needs.py`).
- An eval whose fact is supplied only partly (a `Supply` with a note) must still be made, not refused; and an unchecked language (`supplies=None`) must refuse nothing. Pinned in Task 3 Step 1 (`test_asked.py`).
- The eval refusal is for every fact an eval needs, not only `function.top_level`: an eval of `function` keeping `public` under a language without `public` is refused likewise. Pinned in Task 3 Step 1 (`test_asked.py`).
- A refused eval must not have its examples read (they may be code the reader cannot even parse for that language). Pinned in Task 3 Step 1 (`test_profile_check.py`: the example text is a key `FakeSourceTree` does not hold, so reading it would raise).

---

## File Structure

- Modify `xarch/profile_values/capabilities.py`: one `FACTS` entry.
- Modify `xarch/architectures/presets/language/python.yaml`: one `supplies` line.
- Modify `xarch/modules/rules/domain/vocabulary.py`: `field_needs` of `Kind("function", ...)`.
- Modify `xarch/modules/spec/domain/key_table.py`: two `NEEDS` entries.
- Modify `xarch/modules/rules/application/logic/own_checks.py`: `_supplied` becomes the shared `unsupplied(address, rule, language, what)`.
- Modify `xarch/modules/rules/application/logic/asked.py`: `made` takes the language and refuses an eval that reads an unsupplied fact; module docstring.
- Modify `xarch/modules/rules/application/services/examples.py` and `.../services/asking.py`: hand `profile.language` to `made`.
- Modify `README.md`, `CHANGELOG.md`.
- Tests: `tests/modules/spec/application/logic/test_profile_needs.py`, `tests/modules/rules/domain/test_vocabulary.py`, `tests/modules/rules/domain/test_rule.py`, `tests/modules/rules/application/logic/test_own_checks.py`, `tests/modules/rules/application/logic/test_asked.py`, `tests/modules/rules/application/test_profile_check.py`, `tests/modules/rules/application/test_kept.py`.

---

### Task 1: The fact `function.top_level`, supplied by Python

**Files:**
- Modify: `xarch/profile_values/capabilities.py` (the `FACTS` dict, the line after `"class.record": ...`)
- Modify: `xarch/architectures/presets/language/python.yaml` (`supplies`, after `function: exact`)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `FACTS["function.top_level"]` (str), used by Tasks 2 and 3 in refusal texts; Python's `supplies` lists it `exact`, so every test building a language from `FACTS` (`UNSAID`, `UNRECORDED`, `FLAT`) supplies it.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/application/logic/test_profile_needs.py`, directly after `test_class_record_is_a_fact_after_public` (which ends with `assert FACTS["class.record"] == "whether a class is a record, as the language writes one"`), add:

```python
def test_function_top_level_is_a_fact_after_class_record():
    facts = list(FACTS)
    assert facts[facts.index("class.record") + 1] == "function.top_level"
    assert FACTS["function.top_level"] == "whether a function is defined at the top level of its file, in no class"
```

- [ ] **Step 2: Run it to make sure it fails**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_needs.py::test_function_top_level_is_a_fact_after_class_record -q`
Expected: FAIL (`AssertionError`: `'function' != 'function.top_level'` or similar: the fact after `class.record` is `function`).

- [ ] **Step 3: Add the fact**

In `xarch/profile_values/capabilities.py`, replace:

```python
    "class.record": "whether a class is a record, as the language writes one",
    "function": "the functions a file defines, at the top level and in its classes: name, owner, line",
```

with:

```python
    "class.record": "whether a class is a record, as the language writes one",
    "function.top_level": "whether a function is defined at the top level of its file, in no class",
    "function": "the functions a file defines, at the top level and in its classes: name, owner, line",
```

- [ ] **Step 4: Run the new test and Python's supplies test**

Run: `uv run pytest tests/modules/spec/application/logic/test_profile_needs.py -q`
Expected: `test_function_top_level_is_a_fact_after_class_record` PASSES; `test_python_supplies_every_fact_a_bundled_check_reads` now FAILS (Python's `supplies` lacks `function.top_level`). This is the RED of the data file (spec T10).

- [ ] **Step 5: Python supplies it**

In `xarch/architectures/presets/language/python.yaml`, replace:

```yaml
  function: exact
  function.statements: exact
```

with:

```yaml
  function: exact
  function.top_level: exact
  function.statements: exact
```

- [ ] **Step 6: Run the spec and rules suites**

Run: `timeout 600 uv run pytest tests/modules/spec tests/modules/rules -q`
Expected: all PASS (the existing `UNSAID`/`UNRECORDED`/`FLAT` tests build their supplies from `FACTS`, so they supply the new fact; nothing needs it yet).

- [ ] **Step 7: Commit**

```bash
git add xarch/profile_values/capabilities.py xarch/architectures/presets/language/python.yaml tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'MSG'
The fact function.top_level, whether a function is defined at the top level of its file, in no class, follows class.record in FACTS; Python supplies it exactly

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 2: Who needs `function.top_level`: the field `top-level`, `holds` and `dead-code.tests_only`

**Files:**
- Modify: `xarch/modules/rules/domain/vocabulary.py` (`Kind("function", ...)`, its `field_needs`)
- Modify: `xarch/modules/spec/domain/key_table.py:199` (`"parts.<part>.holds"`) and `:234` (`"guards.dead-code.tests_only"`)
- Test: `tests/modules/rules/domain/test_vocabulary.py`, `tests/modules/rules/domain/test_rule.py`, `tests/modules/rules/application/logic/test_own_checks.py`, `tests/modules/spec/application/logic/test_profile_needs.py`

**Interfaces:**
- Consumes: `FACTS["function.top_level"]` (Task 1).
- Produces: `KINDS` kind `function` has `field_needs["top-level"] == ("function.top_level",)`, so `Rule.needs` of any rule of kind `function` whose `keep`/`exempt`/`where` names `top-level` (negated or not) contains `"function.top_level"`. `NEEDS["parts.<part>.holds"]` and `NEEDS["guards.dead-code.tests_only"]` contain `"function.top_level"`. Task 3 relies on `Rule.needs` carrying it.

These two edits land together: `tests/bootstrap/test_needs_agree.py` compares `NEEDS` with the rules' derived needs, so changing one without the other turns it red.

- [ ] **Step 1: Write the failing tests**

(a) In `tests/modules/rules/domain/test_vocabulary.py`, directly after `test_whether_a_class_is_a_record_needs_the_reader_to_say_it`, add:

```python
def test_whether_a_function_is_at_the_top_level_needs_the_reader_to_say_it():
    kind = next(kind for kind in KINDS if kind.name == "function")
    top = next(word for word in FILTERS if word.name == "top-level")
    assert (kind.field_needs["top-level"], top.meaning) == (
        ("function.top_level",), "the function is defined at the top level of its file, in no class")
```

(b) In `tests/modules/rules/domain/test_rule.py`, directly after `test_a_check_of_comments_needs_comment_doc_only_when_it_reads_whether_one_is_a_doc_comment`, add:

```python
@pytest.mark.parametrize("words", [
    pytest.param({"keep": c("top-level")}, id="kept"),
    pytest.param({"keep": c("not top-level")}, id="negated: it still reads the field"),
    pytest.param({"exempt": c("top-level")}, id="exempted"),
])
def test_a_rule_of_functions_that_reads_whether_one_is_at_the_top_level_needs_function_top_level(words):
    assert made(facts=("function",), targets=EXISTING, sayings=say("{name}"), **words).needs == (
        "function", "function.top_level")


def test_a_rule_of_functions_that_does_not_read_the_top_level_does_not_need_function_top_level():
    assert made(facts=("function",), targets=EXISTING, sayings=say("{name}")).needs == ("function",)
```

(c) In `tests/modules/rules/application/logic/test_own_checks.py`, at the end of the file, add:

```python
TOPPING = WrittenCheck(("function",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("{name}", "f"),),
                       keep=(Condition("top-level"),))
TOPPING_RULE = Rule("topping", Scope(), ("function",), MAY_NOT, (Match("exist"),), (Saying("{name}", "f"),),
                    keep=(Condition("top-level"),), key="checks.topping")


def test_an_own_check_that_reads_whether_a_function_is_at_the_top_level_needs_the_reader_to_say_it():
    untopped = CheckedLanguage("Toy", supplies=(Supply("function", EXACT),), member=".")
    topped = replace(untopped, supplies=(Supply("function", EXACT), Supply("function.top_level", EXACT)))
    assert made({"topping": TOPPING}, profile(language=untopped)) == MadeChecks((), (
        "checks.topping: needs function.top_level (whether a function is defined at the top level of its file, in no "
        "class), which the reader of Toy does not supply: read another kind of fact, or drop the check",))
    assert made({"topping": TOPPING}, profile(language=topped)) == MadeChecks((OwnCheck(TOPPING_RULE),), ())
```

(d) In `tests/modules/spec/application/logic/test_profile_needs.py`, at the end of the file (after the `UNRECORDED` test), add:

```python
UNTOPPED = replace(PYTHON, name="untopped", checked=replace(
    PYTHON.checked, title="Untopped",
    supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "function.top_level")))
"""A language whose reader supplies every fact but function.top_level: it does not say which functions are defined at
the top level of their file."""


def untopped(address: str) -> str:
    return (f"layered.yaml: {address}: its check reads function.top_level (whether a function is defined at the top "
            f"level of its file, in no class), which the language untopped does not supply: drop {address}, or check "
            "the app with a language whose reader supplies function.top_level")


@pytest.mark.parametrize("holds", [
    pytest.param("functions", id="a part of functions"),
    pytest.param("classes", id="a part of classes, whose rule reads top-level"),
])
def test_a_part_that_holds_is_refused_under_a_language_whose_reader_does_not_say_which_functions_are_top_level(holds):
    document = layered(language="untopped")
    document["parts"]["service"] |= {"holds": holds}
    assert problems(document, languages={"untopped": UNTOPPED}) == [untopped("parts.service.holds")]
    said = replace(UNTOPPED, checked=replace(UNTOPPED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"untopped": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "function.top_level" in key.needs) == [
        "guards.dead-code.tests_only", "parts.<part>.holds"]


def test_dead_code_tests_only_is_refused_under_a_language_whose_reader_does_not_say_which_functions_are_top_level():
    document = covered(guards={"dead-code": {"tests_only": True}}, fakes=FAKES, language="untopped")
    assert problems(document, languages={"untopped": UNTOPPED}) == [untopped("guards.dead-code.tests_only")]
    said = replace(UNTOPPED, checked=replace(UNTOPPED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"untopped": said}).approximate == ()
```

(`replace`, `pytest`, `PYTHON`, `covered`, `layered`, `parsed`, `problems`, `KEYS`, `EXACT`, `FACTS`, `Supply`, `FAKES` are all already imported or defined in that file.)

- [ ] **Step 2: Run them to make sure they fail**

Run: `uv run pytest tests/modules/rules/domain/test_vocabulary.py tests/modules/rules/domain/test_rule.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/logic/test_profile_needs.py -q -k top_level`
Expected: FAIL: `KeyError: 'top-level'` in the vocabulary test; `needs == ("function",)` in the three `test_rule` params; `made` returns the check made with no problem under `untopped` in `test_own_checks`; spec's `problems` raises `Failed: DID NOT RAISE InvalidArchitecture` for the holds and tests_only tests. `test_a_rule_of_functions_that_does_not_read_the_top_level_...` PASSES already (it is the control).

- [ ] **Step 3: Add the field need**

In `xarch/modules/rules/domain/vocabulary.py`, in `Kind("function", ...)`, replace:

```python
         field_needs={"forwards": ("function.forwards",), "forwarded": ("function.forwards",),
                      "returned": ("function.forwards",), "public": ("public",)}),
```

with:

```python
         field_needs={"top-level": ("function.top_level",), "forwards": ("function.forwards",),
                      "forwarded": ("function.forwards",), "returned": ("function.forwards",), "public": ("public",)}),
```

Do not touch the `FIELDS["top-level"]` text or the `Filter("top-level", ...)` text.

- [ ] **Step 4: Add the key needs**

In `xarch/modules/spec/domain/key_table.py`, replace:

```python
    "parts.<part>.holds": ("class", "class.exception", "class.record", "function", "public"),
```

with:

```python
    "parts.<part>.holds": ("class", "class.exception", "class.record", "function", "function.top_level", "public"),
```

and replace:

```python
    "guards.dead-code.tests_only": ("class", "class.exception", "function", "named", "public"),
```

with:

```python
    "guards.dead-code.tests_only": ("class", "class.exception", "function", "function.top_level", "named", "public"),
```

Leave `"guards.dead-code.known"` as it is.

- [ ] **Step 5: Run the new tests, the existing neighbours and the agreement test**

Run: `timeout 900 uv run pytest tests/modules/rules tests/modules/spec tests/bootstrap/test_needs_agree.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_profile_explain_words.py -q`
Expected: all PASS, including the unchanged `UNSAID` and `UNRECORDED` tests (spec T4: they supply `function.top_level`, so each still expects only its own refusal) and `test_needs_agree.py` with no edit (spec T11). If `test_needs_agree.py` reports a disagreement for a key, the fix is in `NEEDS`, not in the test; any key other than the two above means a rule reads `top-level` that the spec did not name: stop and report it.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/rules/domain/vocabulary.py xarch/modules/spec/domain/key_table.py tests/modules/rules/domain/test_vocabulary.py tests/modules/rules/domain/test_rule.py tests/modules/rules/application/logic/test_own_checks.py tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'MSG'
The field top-level of a function needs the fact function.top_level, and so do parts.<part>.holds and guards.dead-code.tests_only, so that a language whose reader does not supply it is refused those keys at load, and a check of your own reading top-level, negated or not, with the needs text

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 3: An eval of the profile's own is held to the facts it reads (R3 G6)

**Files:**
- Modify: `xarch/modules/rules/application/logic/own_checks.py` (`_supplied` → `unsupplied`, and its one caller in `made`)
- Modify: `xarch/modules/rules/application/logic/asked.py` (module docstring, imports, `made`)
- Modify: `xarch/modules/rules/application/services/examples.py:49`
- Modify: `xarch/modules/rules/application/services/asking.py:23`
- Test: `tests/modules/rules/application/logic/test_asked.py`, `tests/modules/rules/application/test_profile_check.py`, `tests/modules/rules/application/test_kept.py`

**Interfaces:**
- Consumes: `Rule.needs` carrying `function.top_level` for a `top-level` filter (Task 2); `FACTS` (Task 1); `xarch.kernel.logic.capabilities.shortfalls(address, needs, supplies) -> list[Shortfall]` (exists).
- Produces:
  - `xarch.modules.rules.application.logic.own_checks.unsupplied(address: str, rule: Rule, language: CheckedLanguage, what: str) -> list[str]`: one problem `f"{address}: needs {fact} ({FACTS[fact]}), which the reader of {language.title} does not supply: read another kind of fact, or drop the {what}"` per fact of `rule.needs` the language does not supply at all; `[]` when `language.supplies is None`; a partly supplied fact is no problem.
  - `xarch.modules.rules.application.logic.asked.made(name: str, asked: Asked, language: CheckedLanguage) -> tuple[Rule | None, list[str]]` (the `language` parameter is new and required).

- [ ] **Step 1: Write the failing tests**

(a) Replace the top of `tests/modules/rules/application/logic/test_asked.py` (the module docstring and imports, through the `CODE = ...` line) with:

```python
"""An eval of the profile's own as rules reads it: made into a rule that lists each fact it reads (a filter that is no
word of the vocabulary, or a fact the language's reader does not supply, refused at the eval's address), the facts it
reads in a small project of files, how each is named, and an example file in which it reads nothing named at its
address."""
import pytest

from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.application.logic.asked import made, named, project, span, unread
from xarch.modules.rules.application.logic.engine import kept
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.modules.rules.domain.published import Piece
from xarch.modules.rules.domain.rule import Fact
from xarch.profile_values.capabilities import EXACT, Supply
from xarch.profile_values.checks import APP, Condition, Scope
from xarch.profile_values.language import CheckedLanguage

DOMAIN = "modules/docs/domain/x.py"
CODE = SourceFile("", (), (), functions=(Function(2, "publish", owner="Document"), Function(5, "_check", public=False)),
                  classes=(Class(1, "Document"),))
```

Then in the same file change each of the four existing calls of `made` to pass `PYTHON` (the builders' Python, whose `supplies` is `None`, an unchecked language) as the third argument:

- `made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)))` → `made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)), PYTHON)` (twice: in `test_an_eval_is_made_into_a_rule_of_its_kind_scope_and_filters` and in `test_the_facts_an_eval_reads_in_a_small_project_are_those_of_its_kind_that_pass_its_filters`)
- `made("rule", Asked("class", Scope(), (Condition("publc"),)))` → `made("rule", Asked("class", Scope(), (Condition("publc"),)), PYTHON)`
- `made("rule", Asked("class", Scope(APP, "domain")))` → `made("rule", Asked("class", Scope(APP, "domain")), PYTHON)`

Then, directly after `test_a_filter_that_is_no_word_of_the_vocabulary_is_a_problem_at_the_eval_address`, add:

```python
TOPPED = Asked("function", Scope(APP, "domain"), (Condition("top-level"),))
UNTOPPED = ("evals.rule: needs function.top_level (whether a function is defined at the top level of its file, in no "
            "class), which the reader of Toy does not supply: read another kind of fact, or drop the eval")
UNSAID = ("evals.rule: needs public (whether a name a file defines, or takes by an import, is for other files to use, "
          "as the language decides it), which the reader of Toy does not supply: read another kind of fact, or drop "
          "the eval")


def toy(*supplies: Supply) -> CheckedLanguage:
    return CheckedLanguage("Toy", supplies=(Supply("function", EXACT), *supplies), member=".")


@pytest.mark.parametrize("asked, language, problems", [
    pytest.param(TOPPED, toy(), [UNTOPPED], id="a fact the reader does not supply is refused at the eval's address"),
    pytest.param(Asked("function", Scope(APP, "domain"), (Condition("public"),)), toy(), [UNSAID],
                 id="any fact the eval reads, not only function.top_level"),
])
def test_an_eval_that_reads_a_fact_the_language_does_not_supply_is_not_made(asked, language, problems):
    assert made("rule", asked, language) == (None, problems)


@pytest.mark.parametrize("language", [
    pytest.param(toy(Supply("function.top_level", EXACT)), id="supplied exactly"),
    pytest.param(toy(Supply("function.top_level", "partial", "a function defined in a branch is not read")),
                 id="supplied partly: no problem"),
    pytest.param(CheckedLanguage("Toy", member="."), id="a language whose data file says nothing of its reader"),
])
def test_an_eval_whose_facts_the_language_supplies_or_does_not_grade_is_made(language):
    rule, problems = made("rule", TOPPED, language)
    assert problems == [] and rule is not None and "function.top_level" in rule.needs
```

(b) In `tests/modules/rules/application/test_profile_check.py`, add to the imports:

```python
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
```

and, also near the top, `from dataclasses import replace` and `from tests.modules.rules.builders import PYTHON, profile` (replacing the existing `from tests.modules.rules.builders import profile`). Then at the end of the file add:

```python
UNTOPPED = replace(PYTHON, title="Untopped",
                   supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "function.top_level"))
"""Python's language but for its reader, which supplies every fact but function.top_level."""
UNTOPPED_EVAL = ("evals.rule: needs function.top_level (whether a function is defined at the top level of its file, in "
                 "no class), which the reader of Untopped does not supply: read another kind of fact, or drop the eval")


def test_an_eval_that_reads_a_fact_the_language_does_not_supply_is_refused_at_its_address_and_its_examples_unread():
    evals = {"rule": Asked("function", Scope(APP, "domain"), (Condition("top-level"),), ((DOMAIN, "unreadable"),),
                           ((DOMAIN, "unreadable"),))}
    profiles = FakeProfiles({"mine": profile(asked=evals, language=UNTOPPED)}, reviewed={"mine": MINE})
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=PARSED)
    assert controller(tree, profiles).check_profile(CheckProfile(APP_FOLDER, "mine")) == ProfileHeld(
        MINE, ChecksHeld((), 0, (UNTOPPED_EVAL,), 1))
    assert tree.handed == []
```

(`"unreadable"` is no key of `PARSED`, so the fake would raise `KeyError` if an example were read; `tree.handed` records every `parsed` call.)

(c) In `tests/modules/rules/application/test_kept.py`, add to the imports `from dataclasses import replace`, `from xarch.profile_values.capabilities import EXACT, FACTS, Supply`, and change `from tests.modules.rules.builders import profile` to `from tests.modules.rules.builders import PYTHON, profile`. Then at the end of the file add:

```python
def test_an_eval_that_reads_a_fact_the_language_does_not_supply_is_refused_at_its_address():
    untopped = replace(PYTHON, title="Untopped",
                       supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "function.top_level"))
    asked = {"rule": Asked("function", Scope(APP, "domain"), (Condition("top-level"),))}
    profiles = FakeProfiles({"mine": profile(asked=asked, language=untopped)})
    found = controller(FakeSourceTree(Path("/src/app"), {}, parsed=PARSED), profiles).kept(
        KeepFacts("mine", "app", "rule", ((DOMAIN, "service"),)))
    assert found == ChecksCannotRun((
        "evals.rule: needs function.top_level (whether a function is defined at the top level of its file, in no "
        "class), which the reader of Untopped does not supply: read another kind of fact, or drop the eval",))
```

- [ ] **Step 2: Run them to make sure they fail**

Run: `uv run pytest tests/modules/rules/application/logic/test_asked.py tests/modules/rules/application/test_profile_check.py tests/modules/rules/application/test_kept.py -q`
Expected: every test of `test_asked.py` that calls `made` FAILS with `TypeError: made() takes 2 positional arguments but 3 were given`; the new `test_profile_check.py` test FAILS (no eval problem; the fake raises `KeyError: 'unreadable'` when it reads the example); the new `test_kept.py` test FAILS (facts kept come back instead of `ChecksCannotRun`).

- [ ] **Step 3: Share the refusal of an unsupplied fact**

In `xarch/modules/rules/application/logic/own_checks.py`, replace:

```python
        lacking = _supplied(name, rule, profile.language)
```

with:

```python
        lacking = unsupplied(f"checks.{name}", rule, profile.language, "check")
```

and replace the whole function:

```python
def _supplied(name: str, rule: Rule, language: CheckedLanguage) -> list[str]:
    """A problem for each fact the rule needs that the language's reader does not supply."""
    if language.supplies is None:
        return []
    supplies = {s.fact: s for s in language.supplies}
    return [f"checks.{name}: needs {short.fact} ({FACTS[short.fact]}), which the reader of {language.title} does "
            "not supply: read another kind of fact, or drop the check"
            for short in shortfalls(rule.key, rule.needs, supplies) if short.note is None]
```

with:

```python
def unsupplied(address: str, rule: Rule, language: CheckedLanguage, what: str) -> list[str]:
    """A problem at address for each fact the rule needs that the language's reader does not supply at all, its fix
    to drop what the rule is made of (the check, the eval); none when the language's data file does not say what its
    reader supplies. A fact supplied partly is no problem."""
    if language.supplies is None:
        return []
    supplies = {s.fact: s for s in language.supplies}
    return [f"{address}: needs {short.fact} ({FACTS[short.fact]}), which the reader of {language.title} does not "
            f"supply: read another kind of fact, or drop the {what}"
            for short in shortfalls(rule.key, rule.needs, supplies) if short.note is None]
```

- [ ] **Step 4: Hold an eval to it**

In `xarch/modules/rules/application/logic/asked.py`:

Replace the module docstring:

```python
"""The evals the profile writes itself, as rules reads them: what one question of an eval is asked of is each fact of
the kind it reads, in the files of its scope, that passes the filters it keeps, found as a check finds the facts it
reads. An eval is made into a rule that lists each such fact and is never run as a check: a filter that is not a word
of the vocabulary, or does not apply to the kind read, is a problem at the eval's address, as for a check. An example
file holding no fact the eval reads is a problem too: the question would never be asked of it."""
```

with:

```python
"""The evals the profile writes itself, as rules reads them: what one question of an eval is asked of is each fact of
the kind it reads, in the files of its scope, that passes the filters it keeps, found as a check finds the facts it
reads. An eval is made into a rule that lists each such fact and is never run as a check: a filter that is not a word
of the vocabulary, or does not apply to the kind read, is a problem at the eval's address, as for a check, and so is a
fact the rule reads that the language's reader does not supply. An example file holding no fact the eval reads is a
problem too: the question would never be asked of it."""
```

Replace:

```python
from xarch.modules.rules.application.logic.own_checks import placed
```

with:

```python
from xarch.modules.rules.application.logic.own_checks import placed, unsupplied
```

and add, after `from xarch.profile_values.checks import LIST, Saying`:

```python
from xarch.profile_values.language import CheckedLanguage
```

Replace:

```python
def made(name: str, asked: Asked) -> tuple[Rule | None, list[str]]:
    """The rule of the eval, or None and each problem at its address."""
    try:
        return asking(name, asked), []
    except RuleRefused as refused:
        return None, [f"evals.{name}.{problem}" for problem in refused.problems]
```

with:

```python
def made(name: str, asked: Asked, language: CheckedLanguage) -> tuple[Rule | None, list[str]]:
    """The rule of the eval, or None and each problem at its address: a word that does not exist or apply, or a fact
    the rule reads that the language's reader does not supply."""
    try:
        rule = asking(name, asked)
    except RuleRefused as refused:
        return None, [f"evals.{name}.{problem}" for problem in refused.problems]
    lacking = unsupplied(f"evals.{name}", rule, language, "eval")
    return (None, lacking) if lacking else (rule, [])
```

- [ ] **Step 5: Hand the profile's language to both callers**

In `xarch/modules/rules/application/services/examples.py`, replace:

```python
            rule, problems = evals.made(name, asked)
```

with:

```python
            rule, problems = evals.made(name, asked, profile.language)
```

In `xarch/modules/rules/application/services/asking.py`, replace:

```python
        rule, problems = made(cmd.asked, profile.asked[cmd.asked])
```

with:

```python
        rule, problems = made(cmd.asked, profile.asked[cmd.asked], profile.language)
```

- [ ] **Step 6: Run the tests**

Run: `timeout 900 uv run pytest tests/modules/rules -q`
Expected: all PASS, the own-checks tests unchanged (`checks.<name>: ... drop the check` text kept). Then run `grep -rn "evals.made\|asked import made\| made(" xarch/modules/rules/application` and check every call of `asked.made` passes three arguments.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/rules/application/logic/own_checks.py xarch/modules/rules/application/logic/asked.py xarch/modules/rules/application/services/examples.py xarch/modules/rules/application/services/asking.py tests/modules/rules/application/logic/test_asked.py tests/modules/rules/application/test_profile_check.py tests/modules/rules/application/test_kept.py
git commit -F - <<'MSG'
An eval of the profile's own is held to the facts it reads, as a check of its own is, through one helper both share: one that reads a fact the language's reader does not supply is not made, its examples are not read, and xarch profile check and keeping its facts say the problem at evals.<name>

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

### Task 4: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md` (the language paragraph, the line ending "``reader supplies, which `holds` and the filter `record` read.``", ~line 159)
- Modify: `CHANGELOG.md` (`## [Unreleased]`, `### Added` and `### Changed`)
- Regenerate (never hand-edit): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`

**Interfaces:**
- Consumes: everything of Tasks 1-3.
- Produces: nothing code depends on.

- [ ] **Step 1: README**

In `README.md`, replace the line:

```markdown
reader supplies, which `holds` and the filter `record` read.
```

with:

```markdown
reader supplies, which `holds` and the filter `record` read. Whether a function is defined at the top level of its
file, in no class, is the fact `function.top_level` a reader supplies, which `holds`, `guards.dead-code.tests_only`
and the filter `top-level` read.
```

(Check with `grep -n "the filter \`record\` read" README.md` first that exactly one line matches.)

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, insert as the first bullet of `### Added` (before `- The fact \`class.record\`, ...`):

```markdown
- The fact `function.top_level`, whether a function is defined at the top level of its file, in no class, which
  `parts.<part>.holds`, `guards.dead-code.tests_only` and a check of your own or an eval whose filter reads
  `top-level` (negated or not) need; a language that does not supply it is refused them with the needs text. Python
  supplies it exactly.
```

and as the first bullet of `### Changed` (before `- A language's data file writes what makes a class an immutable record as marks, ...`):

```markdown
- An eval of your own is now held to the facts it reads, as a check of your own is: one that reads a fact the
  language's reader does not supply is refused at its address, `evals.<name>: needs <fact> (<what it is>), which the
  reader of <language> does not supply: read another kind of fact, or drop the eval`, in `xarch profile check` and
  when its facts are kept, and its examples are not read.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-4-1/regenerate_docs.py` (never committed):

```python
"""Write docs/{cli,web,xarch}/testing.md from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        if "/".join(file.path) == "testing.md":
            (root / "docs" / folder / "testing.md").write_text(file.template, encoding="utf-8")
            print(f"docs/{folder}/testing.md written")
```

Run:

```bash
mkdir -p /tmp/xarch-4-1
uv run python -I /tmp/xarch-4-1/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines and an empty `git diff`. If the diff is not empty, read it: a line that moves is a defect of this step unless it names `function.top_level` in a needs list the docs already print. Otherwise stop and report it with the diff (`git checkout -- docs/cli docs/web docs/xarch` restores the files); the fix belongs in the code, never in the docs.

- [ ] **Step 4: Run the gates**

Run the suite in the background with a recorded PID, the rest in the foreground, then read the log:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-4-1/pytest.log 2>&1 & echo $! > /tmp/xarch-4-1/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-4-1/pytest.log`.
Expected: the suite passes (corpora, golden-doc, needs-agree, self-check and seam tests included), both checks report no violation, ruff reports nothing, the profile check loads with no check or eval problem. Then confirm:
- `git status --short` shows no change under `tests/bootstrap/corpora/`, nothing under `.claude/` staged, nothing under `tests/fakes/languages/`;
- `git diff 0efbc92 -- xarch/architectures/presets/language/python.yaml` shows only the added `function.top_level: exact` line;
- `git diff 0efbc92 -- xarch/modules/rules/adapters/` is empty (Python's reader did not change);
- `grep -rn "language.name ==\|\.title ==" xarch/modules/spec xarch/modules/rules` prints nothing new compared with `0efbc92`.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'MSG'
The README's language paragraph says whether a function is defined at the top level of its file is the fact function.top_level that holds, guards.dead-code.tests_only and the filter top-level read, and the CHANGELOG adds the fact and says an eval of your own is now held to the facts it reads; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
```

---

## Self-review against the spec

- 2.1 the fact: Task 1 (`FACTS` after `class.record`, verbatim text, T1; `python.yaml` `supplies`, T10 through the existing `test_python_supplies_every_fact_a_bundled_check_reads`); test-only languages untouched (Task 4 Step 4 check); reader untouched (Task 4 Step 4 check).
- 2.2 who needs it: Task 2 (`field_needs`, T5 in `test_vocabulary.py` and `test_rule.py` with `not top-level`; `NEEDS` on exactly two keys, the `KEYS` list asserted; `holds: classes` and `holds: functions` alike; `known` untouched; `test_needs_agree.py` run unchanged, T11).
- 2.3 refusal at load: Task 2 Step 1(d), T2 and T3, text built from the exact spec wording; said variants load with `approximate == ()`; T4 by running the `UNSAID`/`UNRECORDED` tests unchanged in Step 5.
- 2.4 refusal of an own check: Task 2 Step 1(c), T6, no code change beyond `field_needs`.
- 2.5 refusal of an eval: Task 3 (`made` takes `CheckedLanguage`; only `note is None` shortfalls; `supplies=None` none; partial none; not made → `None`; both callers pass `profile.language`, T8 and T9; one shared helper `unsupplied` with address and last word, own-check text unchanged; any fact, `public` param).
- 2.6 texts: vocabulary texts untouched (Task 2 Step 3 note); `keys.yaml` untouched; README and CHANGELOG (Task 4 Steps 1-2); golden docs regenerated and diffed (Task 4 Step 3).
- 3 tests: T1 Task 1; T2, T3, T4, T5, T6, T11 Task 2; T7, T8, T9 Task 3; T10 Task 1 Step 4/6.
- 4 out of scope: no task touches `holds` as a map, `profile_needs._configured`, `may_import` texts, `expansion.py`, the reader, `dead-code.known`, spec's `evals.py`, the corpora.
- 5 constraints: docstrings only; RED before GREEN in every task; no language-name test; commit messages one sentence.
- Types: `unsupplied(address: str, rule: Rule, language: CheckedLanguage, what: str) -> list[str]` defined and used in Task 3 only (own_checks and asked); `made(name, asked, language)` in Task 3's tests, both services and the logic; `UNTOPPED` is defined separately in each test file it is used in (spec's `LanguageFile`-shaped value in `test_profile_needs.py`, a `CheckedLanguage` in `test_profile_check.py`), never imported across.
<!-- task-pipeline: validated -->
