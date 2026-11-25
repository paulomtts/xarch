# 4.4 `holds` becomes a map of kinds Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A part's `holds` becomes a map of kinds (`classes`, `functions`, `records`, `exceptions`), each `{}` or its
settings (`names`, `immutable`, `built_by`). The flat part keys and `holds` as one word are refused with hints from the
retired table. Every bundled profile finds the same findings except for the nested keys and the one wording change.

**Architecture:** spec parses `holds` in one new module (`holds_written.py`) into a `Held` value per kind, in the order
of `KINDS`. The key table opens a scope for `holds` and one for each kind. `function.top_level` is marked read-when-supplied
(`Key.when_supplied`/`without`), and `profile_needs.read_less` turns it into an `unread` approximate item. rules reads
the kinds through `spec_profile.py` into `Profile.holds/names/immutable/built_by`. `expansion.py` builds the presence,
`names`, `immutable` and `built-by` rules by the narrowest-kind rule. A construction carries `exception`/`record` so
that `built_by` can exempt the narrower kinds.

**Tech Stack:** Python 3, uv, pytest, ruff, PyYAML; xarch's own `xarch check` / `xarch profile check`.

**Spec:** `docs/superpowers/specs/4-4-spec-holds-becomes-468cc608.md`

## Status of this branch (read first)

The plan phase ran twice before and hung both times (no plan file came out). The card was then taken over by hand, and
the work this plan describes is **already committed on this branch**, one commit per task below:

| Task | Commit |
|---|---|
| 1 Fact groundwork (shortfall `unread`, construction `exception`/`record`) | `49f960d` |
| 2 Spec side: the map, the refusals, the key table, needs, values, catalogue, docs template, evals, profiles | `04d2673` |
| 3 Rules side: expansion by kind, adapter, elsewhere, explain line, recorded corpora | `6ef5c10` |
| 4 README and CHANGELOG | `405b032` |

When this plan was written, all gates passed at `405b032`: `uv run ruff check` gave "All checks passed!",
`uv run xarch profile check architecture.yaml` gave "OK: the profile is valid", `uv run xarch check` and
`--strict` exited 0, and `uv run pytest -q` gave `5537 passed in 175.02s`. **For each task the executor's job is verification,
not re-implementation.** Check that the commit is present (`git log --oneline | grep <sha>`), run the task's tests, and
read the diff against the spec section named. If a step's expectation fails, the plan's code excerpts and the commit
diff are the reference for fixing it. Fix it in a new commit with the task's message style. Never amend or rewrite the
existing commits.

## Global Constraints

- No comments in xarch's code (docstrings only); never `ruff --fix`.
- Tests written first, each seen failing for the right reason; examples simple, with absolute `app.` imports.
- Recorded corpora (`tests/bootstrap/corpora/`) edited by hand only, and only as spec 2.12 says; no blind replace of `.names)`.
- Python only in the reader adapter and the data files under `xarch/architectures/presets/`.
- A fact of `supplies` decides language questions, never a test of the language's name.
- `.claude/` stays out of commits; nothing is pushed.
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated, never hand-edited; each moves exactly the one `immutable` line.
- README and CHANGELOG lines go under `## [Unreleased]`.
- No old form accepted as an alias or with a warning; no compatibility window; the key keeps the name `holds`.
- Gates: `uv run pytest -q` (over two minutes: in the background), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check`, `uv run xarch profile check architecture.yaml`.

## Review Focus

1. **A class in a part listing `classes` and a narrower kind, built from another part.** `built_by` must not hold an
   exception or a record to `classes.built_by` (spec 2.2, risk 6). Pinned in Task 1, by the construction fields
   (`test_facts.py`), and in Task 3 (`test_built_by.py::...narrower...`).
2. **A language whose `supplies` leaves out `function.top_level`.** A part of classes must load, build no function
   rule, and say so once in explain and in the enforcement section. `holds.functions`/`holds.records` must be refused.
   Pinned in Task 2 (`test_profile_needs.py`, `test_explain.py`) and Task 3 (`test_holds.py`, `test_profile_report.py`).
3. **Several problems in one part's `holds`** (an unknown kind, a bad setting, a misplaced setting): all are collected,
   in written order, and none is raised alone. Pinned in Task 2 (`test_profile_parsing_substance.py`).
4. **A file breaking both a function rule and a class rule of one part.** `elsewhere.broken` names the part once.
   Pinned in Task 3 (`test_elsewhere.py`, `tests/modules/rules/application/test_holds.py`).
5. **Kinds written out of order** (`{exceptions: {}, functions: {}}`). They are parsed into the order of 2.1, and
   `{held}` reads in that order. Pinned in Task 2 (`test_profile_parsing_substance.py`) and Task 3 (`test_holds.py`
   sentences).

---

### Task 1: Fact groundwork — a shortfall that reads less, a construction that knows what it builds

Spec: 2.5 (the read-when-supplied fact said by its note alone), 6 risk 1 (`built_by` needs the built class's traits).

**Files:**
- Modify: `xarch/profile_values/capabilities.py` (`Shortfall` gains `unread: bool = False`)
- Modify: `xarch/modules/rules/application/logic/enforcement.py` (`detail`, `approximation`)
- Modify: `xarch/modules/rules/application/services/source_check.py:54`
- Modify: `xarch/modules/rules/domain/rule.py` (`Defined.records`)
- Modify: `xarch/modules/rules/application/logic/facts.py` (`_built`, `Defined(..., records)`)
- Modify: `xarch/modules/rules/domain/vocabulary.py` (kind `construction` fields `exception`, `record`)
- Test: `tests/modules/rules/application/logic/test_enforcement.py`, `tests/modules/rules/application/logic/test_facts.py`, `tests/modules/rules/application/test_check_app.py`

**Interfaces:**
- Produces: `Shortfall(address, fact, note, unread=False)`; `enforcement.approximation(address, fact, note, unread=False) -> str` returning `note` alone when `unread`; `Defined.records: frozenset[tuple[str, ...]]`; construction facts with traits `exception`/`record`.

- [ ] **Step 1: Confirm the commit and read its tests**

Run: `git log --oneline | grep 49f960d && git show 49f960d --stat`
Expected: the commit is listed and touches the files above.

The tests it adds, for example in `test_enforcement.py`:

```python
UNREAD = "holds reads no top-level functions: the language Toy does not supply function.top_level"


def test_a_key_whose_check_reads_less_for_want_of_a_fact_is_a_strict_finding_said_by_its_note_alone():
    unread = Shortfall("parts.domain.holds", "function.top_level", UNREAD, True)
    assert strict_findings(Enforcement(approximate=(unread,))) == (Finding("approximate", unread),)
    assert detail(unread) == UNREAD
```

- [ ] **Step 2: Run the task's tests**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_enforcement.py tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/test_check_app.py`
Expected: PASS

- [ ] **Step 3: Check the implementation against the spec**

The core of it (`facts.py`):

```python
def _built(func: tuple[str, ...], defined: Defined) -> frozenset[str]:
    """Of the traits a class has, those of the class a construction builds, by its dotted path: an exception, a
    record."""
    return frozenset(n for n, on in (("exception", (func[1:-1], func[-1]) in defined.exceptions),
                                     ("record", func in defined.records)) if on)
```

and `vocabulary.py`: `Kind("construction", ..., ("line", "path", "name", "place", "exception", "record"), needs=("call", "class", "import.resolved"), field_needs={"exception": _CLASS_EXCEPTION, "record": ("class.record",)}, verb="build")`.
Confirm that the fields need their facts only when read (`field_needs`), so `built_by`'s row stays `class, call, import.resolved`.

- [ ] **Step 4: Commit (only if a fix was needed)**

```bash
git add <the files fixed>
git commit -m "<what the fix makes true, in the style of 49f960d>"
```

---

### Task 2: Spec side — `holds` is a map of kinds

Spec: 2.1-2.3, 2.5 (needs, `profile_needs`), 2.6 (refusals, retired table), 2.7 (values, contract), 2.8 (evals), 2.9
(catalogue), 2.10 (docs template), 2.11 (profiles); section 3's extra gate (review's ruled-out parts); tests 1-5, 13-15,
18, 19, 21, 22, 24, 25.

**Files:**
- Create: `xarch/modules/spec/application/logic/holds_written.py`
- Modify: `xarch/modules/spec/domain/published.py` (`KINDS`, `Held`), `values.py` (`Part.holds: tuple[Held, ...]`; `names`/`immutable`/`built_by` go), `profile_keys.py` (scopes `PART_HOLDS*`, `Key.when_supplied`/`without`, `Retired.value`, the retired entries), `key_table.py` (keys and `NEEDS`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py`, `profile_needs.py` (`read_less`), `key_lookup.py` (`retired_value`; key entries only for `retired`/`retired_at`), `evals.py` (`_RULED`, text), `explain.py`, `docs_template.py`, `services/publishing.py`, `contract/__init__.py`
- Modify: `xarch/modules/rules/adapters/spec_profile.py` (temporary bridge to the old shape, removed in Task 3)
- Modify: `xarch/architectures/presets/format/keys.yaml`, `xarch/architectures/cli.yaml`, `web.yaml`, `architecture.yaml`, `tests/bootstrap/corpora/{7cc6111,df537ca,stress}.yaml`
- Regenerate: `docs/{cli,web,xarch}/testing.md`
- Test: `tests/modules/spec/application/logic/test_profile_parsing_substance.py`, `test_retired_keys.py`, `test_profile_needs.py`, `test_docs_template.py`, `test_evals.py`, `test_profile_parsing.py`, `test_profile_parsing_tests.py`, `test_never_use.py`, `test_key_catalogue.py`, `test_testing.py`; `tests/modules/spec/domain/test_profile_keys.py`; `tests/modules/spec/application/test_explain.py`, `test_language.py`; `tests/bootstrap/test_holds_ruled_out.py` (new), `test_profile_check.py`, `test_architecture_files.py`, `test_needs_agree.py`, `test_rule_ids.py`, `test_bundled_guards.py`, `test_checks_of_its_own.py`, `project.py`; `tests/modules/rules/adapters/test_spec_profile.py`

**Interfaces:**
- Consumes: `Shortfall.unread` (Task 1).
- Produces: `published.KINDS = ("classes", "functions", "records", "exceptions")`; `Held(kind: str, names: tuple[str, ...], immutable: bool, built_by: tuple[str, ...])`; `Part.holds: tuple[Held, ...]`; `PartView.holds` of the same; `holds_written.holds(value, where, declared, problems) -> tuple[Held, ...]`; `Key.when_supplied: tuple[str, ...]`, `Key.without: str`; `Retired.value: str`; `key_lookup.retired_value(scope, name, value) -> str`.

- [ ] **Step 1: Confirm the commit**

Run: `git log --oneline | grep 04d2673 && git show 04d2673 --stat | tail -3`
Expected: listed; 46 files changed.

- [ ] **Step 2: Run the parsing and refusal tests**

These tests pin spec 2.6 verbatim. For example, `test_retired_keys.py` holds the table's texts:

```python
IMMUTABLE_MOVED = "moved in 0.3.0: write it under the kind it applies to, such as holds: {records: {immutable: true}}"
NAMES_MOVED = 'moved in 0.3.0: write it under the kind it names, such as holds: {classes: {names: "*Service"}}'
BUILT_BY_MOVED = "moved in 0.3.0: write holds: {classes: {built_by: [<part>, ...]}}"
OF_CLASSES_AND_RECORDS = "a setting of classes and records"
OF_CLASSES = "a setting of classes"
HOLDS_FUNCTIONS = ("holds as one word was removed in 0.3.0: write holds: {functions: {}, records: {}, exceptions: {}}, "
                   "which allows what holds: functions allowed")
HOLDS_CLASSES = "holds as one word was removed in 0.3.0: write holds: {classes: {}}"
# parametrized rows, among others:
    pytest.param(PART, "immutable", IMMUTABLE_MOVED, id="the part key immutable"),
    pytest.param(PART_HOLDS_FUNCTIONS, "immutable", OF_CLASSES_AND_RECORDS, id="immutable under functions"),
    pytest.param(PART, "holds", "", id="the part key holds, whose one-word values are retired, not the key"),
```

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_parsing_substance.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_profile_parsing.py tests/modules/spec/application/logic/test_profile_parsing_tests.py tests/modules/spec/application/logic/test_never_use.py`
Expected: PASS. Check by reading the tests that every row of spec 2.6's table has a test with its exact text, including
several problems in one part collected together (Review Focus 3) and kinds written out of order read in the order of
2.1 (Review Focus 5).

- [ ] **Step 3: Check the parser against spec 2.3 and 2.6**

`holds_written.holds` (already in the tree) is:

```python
def holds(value: Any, where: str, declared: Collection[str], problems: list[str]) -> tuple[Held, ...]:
    at = f"{where}.holds"
    retired = retired_value(PART, "holds", value) if isinstance(value, str) else ""
    if retired:
        problems.append(f"{at}: {value!r}: {retired}")
        return ()
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a map of kinds, such as {{classes: {{}}}}")
        return ()
    if not value:
        problems.append(f"{at}: lists no kind: list the kinds the part may hold, or drop holds to allow every kind")
        return ()
    problems += [f"{at}: no kind {str(name)!r}: use {', '.join(sorted(KINDS))}" for name in value if name not in KINDS]
    return tuple(held for kind in KINDS if kind in value
                 for held in _kind(kind, value[kind], "classes" in value, f"{at}.{kind}", declared, problems))
```

Confirm `_kind` refuses a non-map kind with `EXAMPLES[kind]`, and that misplaced settings come from the `RETIRED`
entries on the kind scopes through `ck.unknown_keys`. Also confirm `records: {}`/`exceptions: {}` beside `classes` is
refused with "says nothing beside classes, which already allows ...".

- [ ] **Step 4: Run the key table, needs and explain tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/test_explain.py tests/modules/spec/application/test_language.py tests/bootstrap/test_needs_agree.py`
Expected: PASS. Check that `key_table.py` has
`Key(PART, "holds", rules=("holds",), opens=PART_HOLDS, when_supplied=("function.top_level",), without="holds reads no top-level functions")`,
that the `NEEDS` rows match spec 2.5, and that `records.names`/`records.immutable` also read `class.exception`, which
the agreement test decides per spec 2.5. Also check that `profile_needs.read_less` is the only change to `short`.

- [ ] **Step 5: Run the catalogue, docs, evals and adapter tests**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_key_catalogue.py tests/modules/spec/application/logic/test_docs_template.py tests/modules/spec/application/logic/test_evals.py tests/modules/spec/application/logic/test_testing.py tests/modules/rules/adapters/test_spec_profile.py tests/bootstrap/test_docs_templates.py`
Expected: PASS.

- [ ] **Step 6: Confirm the golden docs moved one line each**

Run: `git show 04d2673 -- docs/cli/testing.md docs/web/testing.md docs/xarch/testing.md | grep '^[-+]-'`
Expected: in each file, one `-` line `` - `immutable`: every class of ... or an exception; ...`` and one `+` line
`` - `immutable`: every record of ...; ...`` with the same parts. Nothing else moved.

- [ ] **Step 7: Run the wired gate tests (review's ruled-out parts, CLI refusals, bundled profiles)**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_holds_ruled_out.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_architecture_files.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_checks_of_its_own.py`
Expected: PASS. `test_holds_ruled_out.py` holds every app file of xarch to the parts recorded before the change (spec
section 3, test 21).

- [ ] **Step 8: Commit (only if a fix was needed)**

```bash
git add <the files fixed>
git commit -m "<what the fix makes true, in the style of 04d2673>"
```

---

### Task 3: Rules side — the rules read the kinds

Spec: 2.2, 2.4 (sentences, keys, exact equals), 2.5 (no function rule without `function.top_level`; explain line;
enforcement item), 2.7 (`Profile` shape, `KEYS`, `elsewhere`), 2.12 (recorded corpora); tests 6-12, 16, 17, 20, 23.

**Files:**
- Modify: `xarch/modules/rules/domain/profile.py` (`holds: dict[str, tuple[str, ...]]`, `names: dict[str, dict[str, tuple[str, ...]]]`, `immutable: dict[str, tuple[str, ...]]`)
- Modify: `xarch/modules/rules/adapters/spec_profile.py` (bridge removed; built from `PartView.holds`)
- Modify: `xarch/modules/rules/application/logic/expansion.py`, `elsewhere.py`, `expandable.py`, `sentences.py`; `xarch/modules/rules/domain/vocabulary.py`; `xarch/cli/reports/profile_report.py`, `refusal_report.py`
- Modify (data, anchored replace): `tests/bootstrap/corpora/7cc6111.json`, `df537ca.json`, `stress-7cc6111.json.xz`
- Test: `tests/modules/rules/application/logic/test_holds.py`, `test_names.py`, `test_built_by.py`, `test_elsewhere.py`, `test_expandable.py`, `test_expansion.py`, `test_sentences.py`; `tests/modules/rules/application/test_holds.py`, `test_rule.py`, `test_words.py`; `tests/modules/rules/adapters/test_spec_profile.py`; `tests/cli/reports/test_profile_report.py`; `tests/bootstrap/test_bundled_holds.py` (new), `test_recorded_corpora.py`, `test_profile_explain_words.py`, `test_checks_of_its_own.py`, `test_rule_ids.py`

**Interfaces:**
- Consumes: `PartView.holds: tuple[Held, ...]` (Task 2); construction traits `exception`/`record` (Task 1).
- Produces: rule keys `parts.<part>.holds.{classes,functions,records,exceptions}.names`, `parts.<part>.holds.{classes,records}.immutable`, `parts.<part>.holds.classes.built_by`; `expansion.KEYS` with those plain keys.

- [ ] **Step 1: Confirm the commit**

Run: `git log --oneline | grep 6ef5c10`
Expected: listed.

- [ ] **Step 2: Run the presence and names tests**

For example, `tests/modules/rules/application/logic/test_holds.py` (spec 2.4, tests 6-7):

```python
@pytest.mark.parametrize("kinds, held, found", [
    pytest.param(("classes",), "classes", ["functions"], id="classes"),
    pytest.param(("functions",), "functions", ["class", "record", "exception"], id="functions alone"),
    pytest.param(("functions", "records"), "functions and records", ["class", "exception"], id="functions and records"),
    pytest.param(FUNCTIONS, "functions, records and exceptions", ["class"], id="what logic holds"),
    pytest.param(("records",), "records", ["functions", "class", "exception"], id="records alone"),
    pytest.param(("classes", "exceptions"), "classes and exceptions", ["functions"], id="classes beside exceptions"),
])
def test_a_part_lists_what_its_holds_does_not_allow_each_as_the_narrowest_kind_it_fits(kinds, held, found):
    messages = listed(FILE, checked=profile(holds={"logic": kinds}))
    assert [message.split(": ", 1)[1] for message in messages] == [
        f"{said}, but logic/ of modules/docs holds {held} (parts.logic.holds)" for kind in found for said in SAID[kind]]
```

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_holds.py tests/modules/rules/application/logic/test_names.py tests/modules/rules/application/logic/test_built_by.py tests/modules/rules/application/logic/test_sentences.py`
Expected: PASS.

- [ ] **Step 3: Check the presence rule against spec 2.4**

`expansion._holds` (in the tree):

```python
for part, kinds in profile.holds.items():
    key, held, within = f"parts.{part}.holds", _listed(kinds), Scope(APP, part, where=_all("not package-file"))
    if "functions" not in kinds and _top_level(profile):
        found.append(Rule("holds", within, ("function",), MAY_NOT, EXISTING,
                          (Saying(f"{{name}} is a function at the top level, but {{where}} holds {held} ({{key}})",
                                  ...),), keep=_all("top-level", "public"), mode=LIST, key=key))
    if "classes" not in kinds:
        fix = "move {name} to {parts_holding_classes}, or make what it does functions"
        sayings = tuple(Saying(f"{{name}} is {called}, but {{where}} holds {held} ({{key}})", fix, _all(trait))
                        for kind, trait, called in _UNLISTED if kind not in kinds)
        found.append(Rule("holds", within, ("class",), MAY_NOT, EXISTING,
                          (*sayings, Saying(f"{{name}} is a class, but {{where}} holds {held} ({{key}})", fix)),
                          exempt=_all(*(trait for kind, trait in _NARROWER if kind in kinds)), mode=LIST, key=key))
```

Confirm that `_top_level` decides by `profile.language.supplies` and never by the language's name. Confirm that
`_names` exempts the narrower listed kinds from `classes.names` (2.2) and that `_built_by` builds one rule per part
listing a narrower kind (Review Focus 1).

- [ ] **Step 4: Run the exact-equals and corpora tests**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_bundled_holds.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_profile_explain_words.py tests/bootstrap/test_rule_ids.py tests/modules/rules/application/logic/test_elsewhere.py tests/modules/rules/application/logic/test_expandable.py tests/modules/rules/application/logic/test_expansion.py tests/modules/rules/application/test_holds.py tests/modules/rules/application/test_rule.py tests/modules/rules/application/test_words.py tests/modules/rules/adapters/test_spec_profile.py tests/cli/reports/test_profile_report.py`
Expected: PASS.

- [ ] **Step 5: Read the corpora diff line by line (spec 2.12)**

Run, for each of `7cc6111` and `df537ca`: `git show 6ef5c10 -- tests/bootstrap/corpora/$f.json | grep -E '^\+"' | grep -oE 'holds functions, records and exceptions \(|\(parts\.services\.holds\.classes\.names\)|\(parts\.services\.holds\.classes\.built_by\)' | sort | uniq -c`
(the corpus lines start with `+"`, not `+ `, so a `'^[-+] '` pattern matches nothing)
Expected: the 7cc6111 counts are 2 `holds functions, records and exceptions`, 7 `services.holds.classes.names` and 4
`services.holds.classes.built_by`; the df537ca count is 3 `holds functions, records and exceptions`.

Then the stress file: `xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz > /tmp/stress-after.json && git show 6ef5c10^:tests/bootstrap/corpora/stress-7cc6111.json.xz | xz -dc > /tmp/stress-before.json && diff /tmp/stress-before.json /tmp/stress-after.json | grep -c '^<'; diff /tmp/stress-before.json /tmp/stress-after.json | grep -c '^>'`
Expected: `117` and `109`. The 109 lines replaced are 6+7+4+4+87+1 of spec 2.12. The 8 extra removed lines are the one finding that goes, the record of
`FileSystem does not match *Reader, as every class of platform/ must (parts.platform.names)` at
`xarch/platform/filesystem.py:7` (its message, rule id `names`, file, line, fix and brackets). Check that `test_recorded_corpora.py`'s docstring says 1734
stress findings. The oracle edit (spec 2.12) was made in a scratch worktree of `1f6b01b` and is not committed: its
`names` check, for a part whose `holds` is `functions`, keeps only exceptions and records.

- [ ] **Step 6: Commit (only if a fix was needed)**

```bash
git add <the files fixed>
git commit -m "<what the fix makes true, in the style of 6ef5c10>"
```

---

### Task 4: README and CHANGELOG

Spec: 2.13.

**Files:**
- Modify: `README.md`, `CHANGELOG.md`

- [ ] **Step 1: Confirm and read**

Run: `git show 405b032 -- README.md CHANGELOG.md`
Expected: the README writes `holds: {classes: {names, immutable, built_by}, functions: {names}, records: {names,
immutable}, exceptions: {names}}` in the profile shape, with no flat `immutable`/`names`/`built_by` on the part. The
rule table keys `holds`, `immutable`, `names` and `built-by` by the nested keys. The `alike` sentence names "the same
kinds with the same `immutable` under `holds`". The "ruled out by `holds`" text gains the sentence that a file rules a
part out when it defines at the top level a kind the part does not list. The CHANGELOG's `## [Unreleased]` has
`### Changed` and `### Added` lines for every item of spec 2.13.

- [ ] **Step 2: Check the golden docs still match**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py`
Expected: PASS.

- [ ] **Step 3: Commit (only if a fix was needed)**

```bash
git add README.md CHANGELOG.md
git commit -m "<what the fix makes true, in the style of 405b032>"
```

---

### Task 5: Full gates

- [ ] **Step 1: Run every gate**

Run, the suite in the background:
`timeout 900 uv run pytest -q > /tmp/xarch-44-pytest.log 2>&1; echo EXIT $?`, then
`uv run ruff check`, `uv run xarch check`, `uv run xarch check --strict`, `uv run xarch profile check architecture.yaml`.
Expected: pytest `EXIT 0` with no failure; ruff "All checks passed!"; both checks exit 0; "OK: the profile is valid".

- [ ] **Step 2: The review smoke check (spec section 3)**

Run: `uv run xarch review --offline --all --max-files 500 --format json > /tmp/review-after.json` and the same on
`git worktree add /tmp/xarch-44-base ff55259` into `/tmp/review-before.json`, then `diff` the two and remove the
scratch worktree.
Expected: no diff. With no kept answers, review reads no file, so this is a smoke check only. The substance is
`tests/bootstrap/test_holds_ruled_out.py` and `test_bundled_holds.py`.
<!-- task-pipeline: validated -->
