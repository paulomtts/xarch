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
