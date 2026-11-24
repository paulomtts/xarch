# 9.2 docs: README describes the 0.3.0 format as built — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The README's shape block, symbols and rule table say what the code as built does: the `structure` row's Key
cell names keys that exist, the sentence of Q28 sits after the shape block, and a test holds the rule table's Key
column to the key table.

**Architecture:** One new test in `tests/architecture/test_readme.py` reads the README's rule table and asks
`xarch profile explain <key>` (through the app, with typer's `CliRunner`) which rules each named key feeds; it fails
red on `parts.path`, `parts.folders` today. Then `README.md` gets two edits: the `structure` row's Key cell, and one
new paragraph (the sentence of Q28). Nothing else moves; the gates and the golden docs are run as checks.

**Tech Stack:** Python 3, pytest, typer (`typer.testing.CliRunner`), uv, ruff, xarch itself.

**Spec:** `docs/superpowers/specs/9-2-docs-readme-12d4e58b.md` (prepended below, verbatim).

## Global Constraints

- Files changed: `README.md` and `tests/architecture/test_readme.py` only. No CHANGELOG line (9.3 owns it; R3 O5, 229).
- No comments in xarch's code, the new test included; docstrings on helper functions, as the file's others have.
- Tests written first, run red before the README edit.
- The sentence of Q28 goes in verbatim: `A key on a part is about its own code and reach; a guard is a pre-built check
  with a scope, which names the parts it reads.` Plain prose, wrapped at 120, its own paragraph right after the shape
  block's closing fence, before "An entry of a `never` list".
- `structure` row Key cell: `` `parts.path`, `parts.folders` `` becomes `` `parts`, `parts.name` ``; the row's other
  cells do not change.
- No rewording for style, no reflow of a paragraph that is not edited. `git diff README.md` shows only this card's edits.
- Golden docs `docs/{cli,web,xarch}/testing.md` are only regenerated (as `tests/bootstrap/test_docs_templates.py`
  builds them), never edited by hand; their diff must be empty.
- `xarch/cli/reports/profile_report.py:83` ("such as parts.path in each part") is NOT changed: reported in the result.
- `.claude/` stays out of commits; nothing is pushed; no file outside the repository is edited; recorded corpora,
  `docs/superpowers/`, `docs/examples/`, bundled profiles and `keys.yaml` untouched.
- Never `ruff check --fix`. Long commands under `timeout`; never `pkill`/`killall`/pattern `kill`.

## Deviation from the spec, and why

Spec section 4 says each key is found with `xarch.modules.spec.application.logic.explain.key_at`. A test in
`tests/architecture/` is of the `guard` tier, and `architecture.yaml` (tier `guard`, `imports.types_only`) lists
`parts.logic`: the guard tier may import logic only as a type. Calling `key_at` there makes `uv run xarch check` fail
(checked while writing this plan: `tests/architecture/test_readme.py:60: a guard test uses logic/ of modules/spec only
as a type: it may not call xarch.modules.spec.application.logic.explain.key_at (tiers.guard.imports.types_only)`).
So the test asks the same function through the command that wraps it: `CliRunner().invoke(app, ["profile",
"explain", key])` (the file already imports `app` from `xarch.bootstrap.app`, and `test_self_check.py` already uses
`CliRunner` this way). A key that is not one exits 2; a key's rules are the backticked ids on its `  enforced:` line
(`enforced: yes, by the rules `tiers`, `test-tree``). The kinds of `parts.holds` are still read from the key table
(`KEYS`, `PART_HOLDS` from the domain: reading a value is allowed, only a call is not). Everything else of spec 4 and 5
holds as written; the red output is the one the spec names.

## Review Focus

1. A key that exists but feeds another rule than its row's (not only a missing key): the test must name it. Pinned by
   Task 1 Step 5, a throwaway mutation of one row, run red, then reverted.
2. A key feeding several rules (`tiers` feeds `tiers` and `test-tree`, and the `test-tree` row names it): every
   backticked id on the `enforced:` line is read, not only the first. Pinned by the test itself going green in Task 1
   Step 4 (the `test-tree` row only passes if the second id is read).
3. The sentence of Q28 split across two lines by the 120 wrap: a `grep -c` of the whole sentence on the raw file would
   say 0. Task 2 Step 3 counts it on the text with newlines turned into spaces (expect 1), and once in the raw file the
   first half (expect 1).
4. A Markdown paragraph break lost around the new paragraph (it would merge with the fence or with "An entry of a
   `never` list"): Task 2 Step 3 prints the lines around it, expect a blank line before and after.
5. The golden docs moving: nothing here changes a profile's meaning or the generated text; Task 3 Step 1 regenerates
   them as the test builds them and expects `git status --short docs/` to list only this card's spec and plan.

---

# The spec (verbatim)

# 9.2 docs: README describes the 0.3.0 format as built

Card `12d4e58b`, subtask of `d96ff4b1`. Release step 25 of the merged order, the part of it this card owns: the
README's profile block and symbols read whole against the code as built, and the sentence of Q28 added.

Sources, cited by short name and line (all under `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`, read only,
never edited):

- R3: `0.3.0-cohesion-review-3.md`. Row 25 of section 3 (288): "README block read whole, with the sentence of Q28";
  overlap O4 (228): "README profile block (113-122) and symbols (170-175) ... step 25 reads the block whole, and adds
  the sentence of Q28"; O5 (229) and O8 (232); section 4 (301-354), the vocabulary after the release, read as the
  list of names the README must use.
- PF: `profile-form-proposal.md` 5.4, 668-670: the sentence of Q28 (the old Q11), placed in the wrap-up, and
  "`package_only` stays on the part".
- CS: `code-shape-design.md` 5.3, 739-744: the README list (the key shape, the symbols naming `imports.may` and the
  mode, the rule table key column, `no-callbacks` among the guards).

The line numbers the notes give for the README (113-122, 170-175, 269-290) are of the README of their day. Today the
shape block is `README.md:115-134`, the symbols `README.md:221-241`, the rule table `README.md:347-374`.

The truth this card reads the README against is the code, not the notes (card: "Read the implementation, not the
notes"; dodge: "describing an interface from the notes that got built differently"):

- `xarch/modules/spec/domain/key_table.py` (`_KEYS`, `_guard`, `_GUARD_SCOPES`): every key, its scope and its rules;
- `xarch/architectures/presets/format/keys.yaml`: what each key means and accepts, and the symbols;
- the bundled profiles `xarch/architectures/cli.yaml` and `web.yaml`;
- `uv run xarch profile explain [<key>]`, which reads the same table.

## 1. Scope

In scope, `README.md` only:

1. The shape block (115-134) and the symbols (221-241) read whole against the code. Found by exploration and
   re-checked for this spec: every part key (`name`, `role`, `litmus`, `imports: {may, must, libraries}`,
   `uses: {never}`, `tests | untested`, `package_only`, `shared`, `holds: {classes: {names, immutable, built_by},
   functions: {names}, records: {names, immutable}, exceptions: {names}}`), every tier key (`proves`, `litmus`,
   `uses: {apply_never}`, `plain_tables`, `folder`, `imports: {may, also, must, types_only}`, `docs`) and the ten
   guards equal `key_table.py`; the symbols paragraph equals `keys.yaml`'s symbols (`parts.<part>`, `<word>.<part>`,
   `/<path>`, `:<pattern>`, `everything`, the `types_only` mark). These lines do not change, unless the full read of
   section 2 finds a token that disagrees with the code, which is then fixed in the same way.
2. The sentence of Q28, added verbatim (section 3).
3. The rule table's Key column (347-374), which CS 5.3 (743) lists with the block: the `structure` row cites
   `parts.path` and `parts.folders`, two keys that no longer exist (R3 section 4, row "`parts.<p>.path`,
   `parts.<p>.folders` -> the folder tree of `parts`; `parts.<p>.name` where needed"). It is the one stale spot found.
4. One test that pins the rule table's Key column to the key table (section 4), written first.

Out of scope:

- CHANGELOG, its 0.3.0 lead and the table of R3 section 4: card 9.3 (R3 O5, 229). This card adds no CHANGELOG line:
  it moves no behaviour.
- The final golden-docs regeneration expected with no diff: card 9.4 (R3 O8, 232). This card regenerates them once as
  a check and edits none by hand; it changes no generated text, so the diff must be empty.
- The version, the combined re-grep, the coupling-audit rows: card 9.1 (done, `83356b4`).
- `xarch/cli/reports/profile_report.py:83`, which prints "such as parts.path in each part" in `xarch profile explain`.
  It is code and moves the golden output of `profile explain`; the card is README only. Report it in the result note
  for the owner; do not change it.
- Any README section beyond what section 2 finds disagreeing with the code. No rewording for style, no reflow of a
  paragraph that is not edited.
- Files under `docs/superpowers/`, `docs/examples/`, the recorded corpora, the bundled profiles, `keys.yaml`.

## 2. The read

The README is read whole, 1-1171, against the code, with these mechanical checks run first (each a throwaway command,
not committed):

- Every backticked dotted key the README names (`parts.`, `tiers.`, `guards.`, `testing.`, `evals.`, `review.`,
  `fakes.`, `docs.`, `files.`, `checks.`) is run through `uv run xarch profile explain <key>`. Done for this spec: the
  only keys that fail and are meant as keys are `parts.path` and `parts.folders` (line 350). The others that fail are
  not keys and stay: `checks.<id>.keep` (326) and `evals.<id>.answer.choice` (931) are problem addresses as a refusal
  prints them; `docs.example`, `docs.helpers` (1064) are a tier's `docs` keys, written after "A tier's"
  (`tiers.docs.example` resolves); `parts.store` is the reference symbol; `parts.holds.<kind>.names` is a key per kind;
  `testing.md` is a file name.
- The guards in the shape line (126-127) equal `_guard(...)` in `key_table.py:62-71`, in that order: scenario-coverage,
  no-comments, stand-ins, closed-tree, no-duplicates, no-twins, dead-code, pass-through, no-callbacks,
  private-imports. They do.
- Each rule row's keys carry that rule in `key_table.py` (the test of section 4 automates this).

Then the prose of the block and the symbols is read for interface claims the checks above cannot see (what a key
accepts, a refusal's message, a default), each compared with `xarch profile explain <key>` and `keys.yaml`. A claim that
disagrees with the code is fixed to the code; one that agrees is left word for word.

## 3. Observable result in the README

### 3.1 The sentence of Q28

The README holds, exactly once, this sentence, verbatim from the card and PF 668-669:

> A key on a part is about its own code and reach; a guard is a pre-built check with a scope, which names the parts it
> reads.

Placement: its own paragraph directly after the shape block's closing fence (after line 134), before the paragraph
that begins "An entry of a `never` list". It is the first thing a reader meets after the shape, which is where the
parts' keys and the `guards` line sit side by side. It is plain prose (no backticks, no quote marker), wrapped at the
README's width (120). It agrees with the code as built: `package_only`, `imports`, `uses`, `holds`, `shared` sit on the
part (`key_table.py` PART), and `pass-through` and `no-callbacks` take `{parts: [<part>, ...]}`
(`key_table.py:204-206`, bundled `cli.yaml:307-308`, `web.yaml:309-310`). PF 670, "`package_only` stays on the part",
is already true of the shape line (119) and needs no edit.

### 3.2 The `structure` row of the rule table

Line 350, Key column: `` `parts.path`, `parts.folders` `` becomes `` `parts`, `parts.name` ``, the two keys whose rules
hold `structure` in `key_table.py` (`Key(PROFILE, "parts", ..., rules=("structure", "may-import"))` at 65,
`Key(PART, "name", rules=("structure",))` at 80). The row's other cells do not change. No other row changes: each of
their keys resolves through `key_at` and carries the row's rule (checked for this spec).

### 3.3 Everything else

No other line of the README changes unless the read of section 2 finds it disagreeing with the code; each such edit is
listed in the commit message with the line of the code it follows. `git diff README.md` shows only these edits.

## 4. Tests

One new test, in `tests/architecture/test_readme.py`, written before the README edit and run red first.

Tier: architecture. Why: `tests/architecture/` is where the README is held to the code (the two tests already there
hold the JSON rule list and the commands block to `RULES` and the app); this test reads the README file and xarch's
key table, no app under test, no fixture project, so it fits neither unit nor scenario tiers.

`test_each_key_the_rule_table_names_feeds_that_rule`:

- Reads the rule table: the lines from the header `| Rule id | What it catches | Key |` to the first blank line, the
  header and its `|---|` line aside.
- For each row: the rule id is the first cell without backticks; the keys are the backticked tokens of the last cell.
  A last cell of `-`, or starting with `-` (`- (needs a repeating folder)`), names no key and is skipped.
- A key holding `<kind>` stands for that key with each kind of `parts.holds` in its place (`classes`, `functions`,
  `records`, `exceptions`, taken from the key table's keys under `parts.holds`, not typed in the test), and each must
  pass.
- Each key is found with `xarch.modules.spec.application.logic.explain.key_at`, the function `profile explain` uses.
  The assertion compares a dict, rule id to the sorted list of keys that do not resolve or whose `rules` lack that rule,
  against a dict of the same rule ids each mapped to `[]`, so a failure names every stale key at once.
- Red today with `{"structure": ["parts.folders", "parts.path"], ...}`; green after 3.2.

No test is written for the sentence of 3.1: it is prose whose words the card fixes, and a test asserting a sentence is
present would restate the edit. Its check is the diff read and a `grep -c` in the plan's last task (expect 1).

The existing two tests of `test_readme.py` stay green unchanged (the README's `rule` list and commands block are not
edited).

## 5. Error paths and edge cases the test must handle

- A table row whose Key cell holds a key with a placeholder other than `<kind>` (none today): `key_at` is given the
  address as written; `key_at` accepts the placeholder-free form and the form with a part or tier name in its second
  step, so a new `<part>` cell resolves or fails loudly. The test does not silently skip it.
- A row added to the table later with a key of another rule: the test fails naming it, which is its purpose.
- The table's end: the first blank line after the header. The paragraph after the table ("A key left out means its
  check is off") is not read as a row.
- Backticks inside the "What it catches" cell (`` `branching` ``, `` `min_renamed` ``) are not read as keys: only the
  last cell is read.

## 6. Gates

Each passes on this branch alone, with the full suite green:

- `uv run pytest -q` (over two minutes: run it in the background with `timeout`, read it at the end)
- `uv run xarch check`
- `uv run xarch check --strict`
- `uv run ruff check` (never `ruff --fix`)
- `uv run xarch profile check architecture.yaml`
- Golden docs `docs/{cli,web,xarch}/testing.md` regenerated as `tests/bootstrap/test_docs_templates.py` builds them,
  `git diff docs/` read: empty (R3 O8, 232). Never edited by hand.

## 7. Project rules that bind this card

- No comments in xarch's code, the new test included; a docstring is allowed where the file's others have one.
- Tests written first.
- `.claude/` stays out of commits; nothing is pushed; no file outside the repository is edited.
- No CHANGELOG line (9.3 owns it; R3 O5, 229).
- Recorded corpora untouched.

## 8. Dodges

- Describing an interface from the notes that got built differently: every README token edited or kept is checked
  against `key_table.py`, `keys.yaml` or `xarch profile explain`, never against a note. The notes' README line numbers
  are of their day and are not used to place edits.
- Rewording the sentence of Q28: it goes in verbatim.
- Fixing `profile_report.py:83` here: out of scope, reported instead.

---

# Implementation

## File Structure

- Modify: `tests/architecture/test_readme.py` — module docstring extended by one clause; three imports added
  (`CliRunner`, `KEYS`, `PART_HOLDS`); two helpers (`keys_named`, `rules_of`) and one test
  (`test_each_key_the_rule_table_names_feeds_that_rule`) appended. Its responsibility stays "the README says what the
  app does".
- Modify: `README.md:350` — the `structure` row's Key cell.
- Modify: `README.md:134-136` — one new paragraph (two lines plus a blank line) between the shape block's closing
  fence (line 134) and "An entry of a `never` list" (line 136 today).

Scratch files (never committed) go in `/tmp/xarch-9-2/`.

---

### Task 1: The rule table's Key column is held to the key table

**Files:**
- Modify: `tests/architecture/test_readme.py` (whole file shown below)
- Modify: `README.md:350`

**Interfaces:**
- Consumes: `between(start, end)` already in `tests/architecture/test_readme.py`; `app` from `xarch.bootstrap.app`;
  `KEYS: tuple[Key, ...]` from `xarch.modules.spec.domain.key_table`; `PART_HOLDS = "part.holds"` from
  `xarch.modules.spec.domain.profile_keys`; `Key.scope: str`, `Key.name: str`.
- Produces: `keys_named(cell: str, kinds: list[str]) -> list[str]`; `rules_of(key: str) -> list[str]`;
  `test_each_key_the_rule_table_names_feeds_that_rule()`. Nothing later depends on them.

- [ ] **Step 1: Write the failing test**

Replace the top of `tests/architecture/test_readme.py` (docstring and imports, lines 1-11) so it reads:

```python
"""The README says what the app does: its list of rule ids is the catalogue the violations name, its block of
commands gives every option each command takes, and its table of rules names for each rule keys that feed it."""
import re
from pathlib import Path

import typer
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS
from xarch.modules.spec.domain.profile_keys import PART_HOLDS

README = (Path(__file__).resolve().parents[2] / "README.md").read_text(encoding="utf-8")
```

Leave `between`, `options` and the two existing tests exactly as they are. Append at the end of the file (two blank
lines before each `def`):

```python


def keys_named(cell: str, kinds: list[str]) -> list[str]:
    """The keys a Key cell of the rule table names, one holding <kind> once with each kind in its place; none for -."""
    if cell.startswith("-"):
        return []
    return [key.replace("<kind>", kind) for key in re.findall(r"`([^`]+)`", cell)
            for kind in (kinds if "<kind>" in key else [""])]


def rules_of(key: str) -> list[str]:
    """The rules `xarch profile explain` says the key feeds; none for an address that is no key."""
    shown = CliRunner().invoke(app, ["profile", "explain", key])
    enforced = next((line for line in shown.output.splitlines() if line.startswith("  enforced:")), "")
    return re.findall(r"`([a-z-]+)`", enforced) if shown.exit_code == 0 else []


def test_each_key_the_rule_table_names_feeds_that_rule():
    rows = [line for line in between("| Rule id | What it catches | Key |", "\n\n").splitlines()
            if line.startswith("|") and not line.startswith("|---")]
    cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    kinds = [key.name for key in KEYS if key.scope == PART_HOLDS]
    named = {row[0].strip("`"): keys_named(row[-1], kinds) for row in cells}
    assert {rule: sorted(key for key in keys if rule not in rules_of(key)) for rule, keys in named.items()} == {
        rule: [] for rule in named}
```

Notes for the engineer:
- `between(header, "\n\n")` returns the text after the header up to the first blank line: the `|---|` line and the 26
  rows. The paragraph after the table ("A key left out means its check is off") is past the blank line, so not read.
- Only the first cell (rule id) and the last cell (Key) are read, so backticks in "What it catches" (`` `branching` ``,
  `` `min_renamed` ``) are never taken as keys.
- `- ` and `- (needs a repeating folder)` start with `-`: no key.
- `parts.holds.<kind>.names` becomes `parts.holds.classes.names`, `...functions.names`, `...records.names`,
  `...exceptions.names` (the kinds come from `KEYS`, in that order).
- A key with any other placeholder is passed to `profile explain` as written; it either resolves or exits 2 and is
  named. Nothing is skipped silently.
- `kinds if "<kind>" in key else [""]` makes a key without `<kind>` appear once (`replace` of an absent token is a
  no-op).

- [ ] **Step 2: Run the test to verify it fails**

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | grep -E "Differing|!=|passed|failed"`
Expected:
```
E         Differing items:
E         {'structure': ['parts.folders', 'parts.path']} != {'structure': []}
1 failed, 2 passed in ...
```
If any other rule is listed, stop: the README or the key table moved since this plan; read the row against
`uv run xarch profile explain <key>` and report before editing.

Also run `uv run xarch check; echo "exit=$?"` — expected `exit=0` (the test calls only `app`, which the guard tier may
call; it reads `KEYS` and `PART_HOLDS` as values). If it reports `tiers.guard.imports.types_only`, a call into logic
crept in: remove it, do not change `architecture.yaml`.

- [ ] **Step 3: Write the minimal README edit**

`README.md` line 350 today:
```
| `structure` | a folder or file of the layout missing, at any depth, in the app and in every instance of each repeating folder | `parts.path`, `parts.folders` |
```
Change only its Key cell, so the line reads:
```
| `structure` | a folder or file of the layout missing, at any depth, in the app and in every instance of each repeating folder | `parts`, `parts.name` |
```
Command (or use an editor):
`sed -i '350s/| `parts.path`, `parts.folders` |$/| `parts`, `parts.name` |/' README.md && git diff --stat README.md`
Expected: `README.md | 2 +-`. Why these two: `key_table.py` has `Key(PROFILE, "parts", True, rules=("structure",
"may-import"), opens=PART)` and `Key(PART, "name", rules=("structure",))`, the only keys whose rules hold `structure`
(`uv run xarch profile explain parts.name` prints `enforced: yes, by the rule `structure``).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | tail -1`
Expected: `3 passed in ...`

- [ ] **Step 5: Prove the test names a key of the wrong rule (throwaway)**

Run:
```bash
mkdir -p /tmp/xarch-9-2 && cp README.md /tmp/xarch-9-2/README.green.md
sed -i 's/| `guards.no-comments` |$/| `guards.no-duplicates` |/' README.md
timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | grep -E "!=|passed|failed"
cp /tmp/xarch-9-2/README.green.md README.md && git diff --stat README.md
```
Expected: `{'no-comments': ['guards.no-duplicates']} != {'no-comments': []}`, `1 failed, 2 passed`, then after the
restore `README.md | 2 +-` (only the Step 3 edit).

- [ ] **Step 6: Lint and the self-check**

Run: `uv run ruff check tests/architecture/test_readme.py && uv run xarch check --strict; echo "exit=$?"`
Expected: `All checks passed!` and `exit=0`.

- [ ] **Step 7: Commit**

```bash
git add tests/architecture/test_readme.py README.md
git commit -m "The README's rule table names, for structure, the keys parts and parts.name in place of parts.path and parts.folders, which 0.3.0 removed (key_table.py: Key(PROFILE, \"parts\", ..., rules=(\"structure\", \"may-import\")), Key(PART, \"name\", rules=(\"structure\",))); a test holds every key the table's Key column names to the rules xarch profile explain says it feeds, parts.holds.<kind>.names once per kind, so a stale key fails naming its rule

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The sentence of Q28, and the README read whole against the code

**Files:**
- Modify: `README.md:134-136` (insert after the shape block's closing fence)
- Modify: any other `README.md` line only if Step 1 or Step 2 finds it disagreeing with the code (expected: none)

**Interfaces:**
- Consumes: Task 1's committed README and test (the test must stay green).
- Produces: nothing code depends on.

- [ ] **Step 1: The mechanical read: every backticked dotted key**

Write `/tmp/xarch-9-2/keys.py` (scratch, never committed; it imports the key lookup directly, which is fine outside the
repo's tests):

```python
import re
import sys
from pathlib import Path

from xarch.modules.spec.application.logic.explain import key_at

text = Path(sys.argv[1]).read_text(encoding="utf-8")
roots = "parts|tiers|guards|testing|evals|review|fakes|docs|files|checks"
for number, line in enumerate(text.splitlines(), 1):
    for token in re.findall(rf"`((?:{roots})\.[^`\s]+)`", line):
        if key_at(token) is None:
            print(f"{number}\t{token}")
```

Run: `uv run python -I /tmp/xarch-9-2/keys.py README.md`
Expected, exactly these lines (after Task 1, `parts.path` and `parts.folders` are gone):
```
182	testing.tables.0.call
182	testing.declared.0.call
183	testing.mocks.specs.0.type_argument
227	parts.store
231	parts.store/schema
232	parts.store:*Id
326	checks.<id>.keep
371	parts.holds.<kind>.names
1064	docs.example
1064	docs.helpers
1146	testing.md
```
None is meant as a key and all stay: 182-183 and 326 are problem addresses as a refusal prints them (an entry index,
an id); 227-232 are the reference symbol; 371 is a key per kind (Task 1's test resolves each kind); 1064 are a tier's
`docs` keys written after "A tier's" (`uv run xarch profile explain tiers.docs.example` resolves); 1146 is a file name.
Any other line printed is a stale key: check it with `uv run xarch profile explain <key>` (its error names what to
write), fix the token to the code, and list it in Step 6's commit message with the code line it follows.

- [ ] **Step 2: The read of the block and the symbols for interface claims**

Check the guards line equals the key table, in order:

Run: `sed -n '126,127p' README.md; sed -n '/^_KEYS/,/^)/p' xarch/modules/spec/domain/key_table.py | grep -o '_guard("[a-z-]*")'`
Expected: the README lists `scenario-coverage, no-comments, stand-ins, closed-tree, no-duplicates, no-twins,
dead-code, pass-through, no-callbacks, private-imports`, and the grep prints the same ten names in the same order.

Then read `README.md:115-134` (the shape) and `README.md:221-241` (the symbols) whole, and compare each claim of what a
key accepts, a refusal's message or a default against the code:
- each part key and tier key of the shape: `uv run xarch profile explain parts` and `uv run xarch profile explain
  tiers` (their `keys:` lists), and `sed -n '/^_KEYS/,/^)/p' xarch/modules/spec/domain/key_table.py`;
- the symbols: `sed -n '/^symbols:/,/^keys:/p' xarch/architectures/presets/format/keys.yaml`;
- the refusal of the old forms, `'store@any': @any was removed in 0.3.0: write parts.store`: the message is built at
  `xarch/kernel/logic/targets.py:95` (`f"{value!r}: {form} was removed in 0.3.0: write {instead}"`);
- "a repeating folder cannot be written `<parts>`": `xarch/modules/spec/application/logic/parts_tree.py:23`
  (`_RESERVED = "<parts>"`).
Expected (checked while writing this plan and for the spec): every claim agrees, and no line of 115-134 or 221-241
changes. A claim that disagrees is fixed to the code (smallest word change, the paragraph not reflowed beyond the
edited line) and listed in Step 6's commit message with the code line it follows. Never fix a line from a note.

Also confirm the claim the new sentence rests on:
Run: `uv run xarch profile explain guards.pass-through | grep -A3 keys:; uv run xarch profile explain guards.no-callbacks | grep -A3 keys:; grep -n -A2 "pass-through:\|no-callbacks:" xarch/architectures/cli.yaml xarch/architectures/web.yaml`
Expected: each guard holds a `parts` key, and both bundled profiles write `{parts: [...]}` under those two guards.

- [ ] **Step 3: Insert the sentence of Q28**

`README.md` lines 133-136 today:
````
          fix*, examples*}}                             what `xarch review` asks; `check` never acts on it
```

An entry of a `never` list that is the name of another list includes that list's names in its place, such as
````
Insert, right after the closing fence line (134), a blank line and these two lines, so lines 134-138 read:

````
```

A key on a part is about its own code and reach; a guard is a pre-built check with a scope, which names the parts it
reads.

An entry of a `never` list that is the name of another list includes that list's names in its place, such as
````

Command:
```bash
python3 - <<'EOF'
from pathlib import Path
path = Path("README.md")
text = path.read_text(encoding="utf-8")
anchor = "```\n\nAn entry of a `never` list"
assert text.count(anchor) == 1
sentence = ("A key on a part is about its own code and reach; a guard is a pre-built check with a scope, which names "
            "the parts it\nreads.")
path.write_text(text.replace(anchor, "```\n\n" + sentence + "\n\nAn entry of a `never` list"), encoding="utf-8")
EOF
```

Check it (Review Focus 3 and 4):
```bash
sed -n '133,139p' README.md
python3 -c "import pathlib; t = pathlib.Path('README.md').read_text(encoding='utf-8').replace('\n', ' '); print(t.count('A key on a part is about its own code and reach; a guard is a pre-built check with a scope, which names the parts it reads.'))"
grep -c 'A key on a part is about its own code and reach' README.md
awk 'length > 120' README.md | grep -c 'A key on a part' ; true
```
Expected: line 134 the fence, 135 blank, 136-137 the sentence, 138 blank, 139 "An entry of a `never` list ..."; the
two counts print `1` and `1`; the awk line prints `0` (no line of the sentence over 120).

- [ ] **Step 4: Only this card's edits in the README**

Run: `git diff README.md`
Expected: three added lines (blank, sentence, `reads.`) after the fence, plus any fix Step 1 or 2 required (expected
none). The Task 1 edit is already committed, so it does not show.

- [ ] **Step 5: The README tests still pass**

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py 2>&1 | tail -1`
Expected: `3 passed in ...`

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "The README says after its shape block that a key on a part is about its own code and reach and a guard is a pre-built check with a scope, which names the parts it reads (Q28, profile-form-proposal.md 5.4); read whole against key_table.py, keys.yaml and xarch profile explain, the shape block and the symbols agree with the code and do not change

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
If Step 1 or 2 fixed a line, append to the message, per fix: `; line <n>: <old token> -> <new token>, as <file>:<line>
says`.

---

### Task 3: The gates, and the golden docs that must not move

**Files:**
- Modify: none (each step is a check; nothing here is committed)

**Interfaces:**
- Consumes: the branch after Tasks 1 and 2.
- Produces: the result note's facts (gate results, the `profile_report.py:83` report).

- [ ] **Step 1: The golden docs, regenerated as the test builds them**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_docs_templates.py 2>&1 | tail -1; git status --short docs/`
Expected: `N passed` with no failure, and `git status` lists nothing under `docs/` apart from this card's spec and plan
under `docs/superpowers/` if they are still untracked. A failure is read and reported, never fixed by editing a
golden doc by hand.

- [ ] **Step 2: The diff of the branch**

Run: `git diff --stat 83356b4..HEAD -- . ':!docs/superpowers'`
Expected: `README.md` (4 lines: 1 changed in Task 1, 3 added in Task 2, plus any Task 2 fix) and
`tests/architecture/test_readme.py`; nothing else. `git diff 83356b4..HEAD -- CHANGELOG.md` prints nothing.

- [ ] **Step 3: The gates**

Run, one at a time, each expected to exit 0:
```bash
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```
Expected: `All checks passed!` from ruff; `xarch check` and `--strict` report no violation; `profile check` says the
profile is valid. Never `ruff check --fix`.

Then the suite in the background (over two minutes), with the Bash tool's `run_in_background: true`:
`mkdir -p /tmp/xarch-9-2; timeout 900 uv run pytest -q > /tmp/xarch-9-2/pytest.log 2>&1; echo "exit=$?" >> /tmp/xarch-9-2/pytest.log`
When it finishes: `tail -3 /tmp/xarch-9-2/pytest.log`
Expected: `N passed` with no `failed` or `error`, and `exit=0`. A failure is read and reported, not retried until it
passes.

- [ ] **Step 4: Report what is out of scope**

Run: `sed -n '83p' xarch/cli/reports/profile_report.py`
Expected: the line still holds "such as parts.path in each part". Do not change it (code, and it moves the golden
output of `profile explain`). Put in the result note: "`xarch/cli/reports/profile_report.py:83` prints `such as
parts.path in each part` in `xarch profile explain`; `parts.path` was removed in 0.3.0; left for its owner (it moves
`profile explain`'s golden output)."

---

## Self-review (done while writing)

- Spec coverage: 1.1 and section 2 -> Task 2 Steps 1-2; 1.2 and 3.1 -> Task 2 Step 3; 1.3 and 3.2 -> Task 1 Step 3;
  1.4 and section 4 -> Task 1 Steps 1-2, 4-5; section 5 edge cases -> Task 1 Step 1 notes and Step 5; 3.3 -> Task 2
  Step 4 and Task 3 Step 2; section 6 gates -> Task 3; out-of-scope `profile_report.py:83` -> Task 3 Step 4.
- One deviation, stated above: the test reaches `key_at` through `xarch profile explain` because the guard tier may
  not call logic. Its red output is the spec's.
- Task 2 Step 1's expected list adds three lines the spec's list did not name (182-183, problem addresses with an
  entry index, of the same kind as the spec's `checks.<id>.keep`); they stay.
- Names: `keys_named`, `rules_of`, `test_each_key_the_rule_table_names_feeds_that_rule`, `KEYS`, `PART_HOLDS`, `app`,
  `between` are the same everywhere they appear.
- The test code, the README edit, the red and green outputs and the `xarch check` result were each run on this branch
  while writing the plan, then the worktree was restored.
<!-- task-pipeline: validated -->
