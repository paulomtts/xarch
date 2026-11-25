# 3.8 language: comments read in more than one form

Card `0954fb83`, subtask of `3c7754c4`, blocked by `1d9a0cdb` (3.7, done on the branch this one stacks on). Release
step 8c of the merged order (`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below
**R3**, section 3, line 269: "`comments` forms, `Comment.marker`, `.doc`, `comment.doc`. | language-neutral 8 | Step
7."; vocabulary table line 345: "`comment: "#"` | `comments: [{line} | {block} | {doc}]` | language data file | ruled
(item 8)").

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/language-neutral-design.md` (below **LN**),
section 8 (lines 847-906). Release-wide rules this step inherits: R3 O4, O5 (lines 228-229: README and CHANGELOG under
`[Unreleased]`), O7 (line 231: `comment.doc` is the fact of 8c, placed after `file.package` in `FACTS`, `python.yaml`
`supplies`, `NEEDS`, `test_needs_agree.py`), O8 (line 232: golden docs regenerated, diff read; none expected for 8c),
O18 (line 242: `python.yaml` is edited by 8c, its lines only). R3 line 394 (item 18): the form name `doc` and the fact
`comment.doc` live in the language data file, the profile's `docs` blocks elsewhere; no clash to resolve. Dodges that
apply (card, LN lines 1139-1167): a hidden default (`comments` meaning `#`, LN line 1151); "a step is not done
without its test-only file" (LN line 1143); an ObjectScript-shaped case with two line markers (LN line 1145); letting
the corpora or golden docs move "a little" (LN line 1166).

## 1. Goal

A comment is opened by a marker and runs to the end of its line or to a closing marker; some languages keep their
documentation in comments of their own (LN 8.1, lines 851-852). The data file says so with one list key, `comments`,
replacing the scalar `comment`. The reader says of each comment the marker it opens with and whether it is a doc
comment (LN 8.2). The checking code stops assuming one marker opens every comment, that `%comment%` has one value of
its own, and that every comment is one `no-comments` reads (LN 8.3). Python's findings, the recorded corpora (comment
texts included) and the golden docs do not move (LN 8.5, line 894).

## 2. Observable behavior

### 2.1 The data file (LN 8.1, 8.4)

- `comment` is no longer a key. Written, it is an unknown key, refused with today's unknown-key text
  (`unknown key 'comment': use ...`), listing the new key set (which holds `comments`); no retired-keys entry or hint
  (data-file keys get none; the same rule 3.7 applied to `extension`).
- `comments` is optional, like every other token key: left out, the language has no comment forms. No code supplies
  `#` (or any marker) in its place (dodge: hidden default). `%comment%` is then `""`.
- Given, `comments` is a list of forms, in the order written. Each form is a map of exactly one key:
  - `line: <marker>`: a non-empty string; the comment runs to the end of its line.
  - `block: [<open>, <close>]`: a list of exactly two strings, both non-empty.
  - `doc: [<open>, <close>]`: a list of exactly two strings, the opening non-empty; the closing may be `""`, meaning
    the end of the line (LN 8.1 line 861: `{doc: ["///", ""]}`).
- Refusals, exact texts (LN 8.4, line 884-885), each given once for the key:
  - a value that is no list, or a list holding any item that is no form as above (a string, a map of two keys, an
    unknown key such as `{hash: "#"}`, a `block` with one item or an empty closing, a `line` with an empty marker or a
    non-string):
    `comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}`
  - an empty list: `comments: needs one form at least`
- No profile line is refused by this step (LN 8.4, line 885).
- The module docstring of `language_file.py` and the header comment of `python.yaml` describe `comments` in place of
  `comment` (the forms, the empty closing of a doc form, and that a directive and an encoding declaration are matched
  after the marker of any form).

`python.yaml` (R3 O18): `comment: "#"` becomes `comments: [{line: "#"}]` (LN 8.1 line 856), `supplies` gains
`comment.doc: exact` right after `comment: exact` (LN 8.2, line 870: "Python supplies both `exact`"), plus its header
words. Nothing else in the file moves.

### 2.2 The language value (LN 8.3)

- `xarch/profile_values/language.py` gains a small frozen value for one form, e.g. `CommentForm(kind: str, open: str,
  close: str = "")` with `kind` one of `line`, `block`, `doc` (the planner names it; it lives beside `RecordMark` and
  `InterfaceMark`). `CheckedLanguage.comment: str` is replaced by `comments: tuple[CommentForm, ...] = ()`.
- A read-only property `comment` (kept under that name so its readers read on) is the first `line` marker, else the
  first `block` opening, else `""` (LN 8.3 line 877). A `doc` form is never `%comment%`. Docstring updated.

### 2.3 What the reader supplies (LN 8.2)

- `xarch/modules/rules/domain/parsed.py` `Comment` gains `marker: str` (the opening marker, as written) and `doc: bool`
  (whether it is a doc comment), both with defaults (`""`, `False`) placed after the existing fields, so positional
  constructions in tests still build. `text` stays the comment as written, marker included (and for a block, its
  closing), since messages and review's cuts print it. The docstring says "a comment", not "a line comment".
- `xarch/modules/rules/adapters/fs_source_tree.py` `_comments` sets `marker="#"` and `doc=False` on every comment.
  This adapter is the only place in xarch's code that may write the Python marker (the seam test exempts it).
- `FACTS` (`xarch/profile_values/capabilities.py`): `comment` reads "each comment, its text, its line and where on it
  it starts and ends, and the marker it opens with, which review cuts before it sends a text" (LN 8.2 line 868, with
  today's trailing clause kept); a new `comment.doc`: "whether a comment is a doc comment" (LN 8.2 line 869), placed
  right after `file.package` (R3 O7).
- The `comment` fact the engine builds (`facts.py` `case "comment"`) carries the marker and the doc flag (how, e.g.
  `name=c.marker` and a `doc` trait, is the planner's), so that a filter can read both. The kind table in `facts.py`'s
  docstring and `vocabulary.py`'s `Kind("comment", ...)` say "each comment, its text as written" (LN 8.3 line 880),
  and the kind may carry `doc` (sometimes, needing `comment.doc`).

### 2.4 What the checking code stops assuming (LN 8.3)

- **Directives** (`filters.py` `_directive`): the directive words and the encoding pattern are matched against what
  follows the comment's own `marker`, at its start (spaces allowed between, as today), not against an escaped
  `language.comment`. A comment whose text does not start with its marker is no directive by those two branches. The
  shebang branch is unchanged (line 1, text starts with `language.shebang`). For Python every finding is unchanged.
  The filter `directive`'s meaning says "after the marker of the comment", not "after the comment marker".
- **`no-comments`** (`expansion.py` `_no_comments`): reports every comment but a doc comment, and still exempts
  directives, a shebang on line 1 and an encoding line on line 1 or 2 (LN 8.3 line 878). Its docstring says "No
  comment, ... but doc comments and those the language's tools read". A rule that exempts doc comments reads the fact
  `comment.doc`, so the rule's needs (`Rule.needs`) hold `comment` and `comment.doc`; `NEEDS` in
  `xarch/modules/spec/domain/key_table.py` for `guards.no-comments` becomes `("comment", "comment.doc")` (LN 8.3 line
  879), and `tests/bootstrap/test_needs_agree.py` stays green. A suggested shape: a filter `doc` ("the comment is a
  doc comment") with `facts=("comment.doc",)`, written in the rule's `exempt`; its name and wording are the planner's,
  and `profile explain filters` shows it as it shows the others.
- **`%comment%`** (`written.py` `_tokens_filled`, `docs_template.py` `_block` and the `no-comments` docs line,
  `explain.py` `words`): read the property of 2.2. The docs line and the `%directives%` word print each directive
  after it, as today (LN 8.3 line 877). For Python they print `#`, byte for byte as today.
- `file_types.py` / `FileType.comment` (the marker of a non-language file's header) is a different thing and does not
  change.

### 2.5 Profile-format text (`keys.yaml`)

- `guards.no-comments` says the guard reads every comment but a doc one: e.g. meaning "no `%comment%` comments in the
  app or its tests", accepts "... whole-line or trailing; docstrings and doc comments stay, and so do %directives%, a
  shebang and an encoding line" (exact wording the planner's). These texts appear in `profile explain` and the key
  catalogue, not in the golden docs (checked: only `docs_template.py` writes the golden `no-comments` line).

### 2.6 Things that stay as they are

- Python's findings on every profile; the recorded corpora (`tests/bootstrap/corpora/`), not edited (LN 8.5: comment
  texts included); the golden docs `docs/{cli,web,xarch}/testing.md`, regenerated with the repo's command and their
  diff read, expected empty (R3 O8). Line 180 of `docs/xarch/testing.md` stays
  ``- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives (`# type: ignore`, `# noqa`,
  `# pragma:`) stay.``
- Review's masking (`review/.../masking.py`) cuts by `Comment.span` and needs no change: a block comment is spanned
  by `last` already.
- `uv run xarch check`, `--strict`, `xarch profile check architecture.yaml` on xarch itself (xarch's own profile sets
  `no-comments`; Python supplies `comment.doc`, so it loads).

## 3. The test-only language files (LN 8.5; dodges lines 1143, 1145)

- `tests/fakes/languages/brace.yaml` gains `comments: [{line: "//"}, {block: ["/*", "*/"]}, {doc: ["/**", "*/"]}]`
  (LN 8.1 line 857) and `directives: ["@ts-expect-error", eslint-disable]` (LN 8.5 line 891); header says it.
- `tests/fakes/languages/percent.yaml` gains two line markers and a doc form:
  `comments: [{line: "//"}, {line: ";"}, {block: ["/*", "*/"]}, {doc: ["///", ""]}]` (LN 8.1 line 858); header says
  it. Its `%comment%` is `//`, the first line marker.
- Both must keep loading in `test_language_seam.py`'s parametrized tests and `test_language_file.py`.
- `tests/modules/rules/builders.py` (`PYTHON`, and `BRACE`/`PERCENT` where they are built), `test_written.py:70,83`,
  `test_docs_template.py:294`, and every test building `CheckedLanguage(comment=...)` move to `comments=`. Tests that
  build `Comment(...)` by hand and lean on a directive being matched give the marker (`marker="#"`); those that only
  report a comment keep building it positionally.

## 4. Tests (written first)

Unit = pure logic or a service with fakes, no disk; adapter = real adapter against tmp files or source text;
architecture = the repository guards; bootstrap = the wired app end to end.

### 4.1 Loader — `tests/modules/spec/application/logic/test_language_file.py` (unit: `language_of` is pure)

1. Brace's three forms read into `checked.comments` in the order written, each form's kind, opening and closing as
   written; `checked.comment == "//"`.
2. Percent's forms: two `line` forms (`//`, `;`), a doc form with closing `""`; `checked.comment == "//"`.
3. A language whose only form is `{block: ["/*", "*/"]}` has `checked.comment == "/*"`; one whose only form is a doc
   form has `checked.comment == ""` (a doc opening is never `%comment%`).
4. `comments` left out: `checked.comments == ()`, `checked.comment == ""`, the file loads (no hidden default).
5. Each wrong `comments` gives exactly one form problem (parametrized, `id` a sentence: `"#"` as a string, `[{hash:
   "#"}]`, `[{line: "#", block: ["/*", "*/"]}]`, `[{line: ""}]`, `[{line: 3}]`, `[{block: ["/*"]}]`, `[{block: ["/*",
   ""]}]`, `[{doc: ["", "*/"]}]`, `["#"]`).
6. `comments: []` gives `comments: needs one form at least`.
7. `comment: "#"` is an unknown key, the listed key set holds `comments` and not `comment`, no hint (`KEYS_USED` at
   `:33` swaps the word).
8. `python.yaml` reads `comments == (line "#",)`, `comment == "#"`, and supplies `comment.doc` exactly.

### 4.2 Reader — `tests/modules/rules/adapters/test_fs_source_tree.py:1047-1053` (adapter: real Python tokens)

9. The existing comment cases also assert `marker == "#"` and `doc is False` on every comment, whole-line and
   trailing; a `#` inside a string is still none.

### 4.3 Directives and `no-comments` — `tests/modules/rules/application/logic/test_comments.py` (unit: hand-built
`Comment` values through the engine, LN 8.5)

10. Under brace: `no-comments` flags `// a note` (marker `//`) and `/* a note */` (marker `/*`), and keeps
    `/** a doc */` (marker `/**`, `doc=True`) (LN 8.5 line 889-890).
11. Under brace: `// @ts-expect-error` and `/* eslint-disable */` are directives, kept; `//@ts-expect-error` (no
    space) is kept too; `// see @ts-expect-error` is flagged (the word is not right after the marker) (LN 8.5 line
    890-891).
12. Under percent (two line markers): `; a note` (marker `;`) is flagged as a comment, `// a note` too, and
    `/// a doc` (marker `///`, `doc=True`) is kept as documentation (LN 8.5 line 892).
13. Python: the existing cases (`# type: ignore`, `# noqa`, `# pragma:`, shebang on line 1, encoding on line 1 or 2,
    trailing comment) give today's findings, with `marker="#"` given; a `# -*- coding: utf-8 -*-` on line 3 is flagged
    as today.
14. A comment whose marker is not the language's `%comment%` is still a directive when its words follow its own
    marker (brace `/* eslint-disable */`, where `%comment%` is `//`).

### 4.4 Rule needs (unit) — `tests/modules/rules/domain/test_rule.py` or `test_expansion.py`

15. The `no-comments` rule's `needs` are `("comment", "comment.doc")`; a check reading `comment` with no doc filter
    needs only `comment`.

### 4.5 Spec side (unit)

16. `tests/modules/spec/application/logic/test_profile_needs.py`: a language with `supplies` listing `comment` but not
    `comment.doc` refuses `guards.no-comments` with today's needs text naming `comment.doc` ("whether a comment is a doc
    comment"); listing both, it loads.
17. `test_key_catalogue.py` / NEEDS tests: `FACTS` holds `comment.doc` right after `file.package`; every key's needs
    stay within `FACTS`.
18. `tests/modules/rules/application/logic/test_written.py`: `%comment%` fills with `//` under a brace-shaped language
    and with `#` under Python (moved to `comments=`).
19. `tests/modules/spec/application/logic/test_explain.py` (or the file testing `words`): under brace `comment` is `//`
    and `directives` is ``"`// @ts-expect-error`, `// eslint-disable`"``; under percent `comment` is `//`; with no
    `comments`, `comment` is `""`.
20. `test_docs_template.py:294`: a brace block's header comment and the `no-comments` docs line print `//`, from
    `comments` (the test's `replace(... comment="//")` becomes `comments=`).

### 4.6 Guards (architecture) and end to end (bootstrap)

21. `tests/architecture/test_language_seam.py`: `TOKEN_KEYS` loses `comment`; `language_tokens` and `ticked_pattern`
    add every non-empty marker of `comments` (each `line` marker, each `block`/`doc` opening and closing) to the
    tokens a literal may not be and a ticked span may not hold (the card's "the seam test also looks for the tokens of
    `comments` outside the reader"). A probe (in the style of the file's existing probe tests) shows a literal `"#"`
    in a checking-code file outside the seam is found, and the same under brace for `"/*"`. Its docstring (`:31-37`)
    says "the comment markers". `test_every_exemption_is_one_some_language_still_needs` stays green.
22. `tests/bootstrap/test_needs_agree.py` green: spec's `NEEDS` and the expanded `no-comments` rule agree on
    `comment.doc`; `test_python_supplies_every_fact_a_bundled_check_reads` holds.
23. `tests/bootstrap/test_bundled_guards.py:120` (the docs line) unchanged; the corpora tests and the golden-doc tests
    pass with no change (`tests/bootstrap/`).
24. `tests/architecture/test_self_check.py` green (xarch's own `no-comments` still finds none in xarch).

## 5. Docs (R3 O4, O5, O8)

- `README.md:151` (language paragraph): "the comment marker and the comments its tools read" becomes the comment forms
  (`comments`: `line`, `block` and `doc` forms, a doc comment being one `no-comments` keeps) and the comments its tools
  read after the marker of any form. `README.md:292` (the `no-comments` row): a comment of the language (not "a `#`
  comment"), doc comments aside. `tests/architecture/test_readme.py` stays green.
- `CHANGELOG.md` `[Unreleased]`: under `### Changed`, `comment` became `comments`, a list of `{line}`, `{block}` and
  `{doc}` forms, with the two refusal texts of 2.1 quoted, that a directive is matched after the marker of any form,
  that `no-comments` keeps doc comments, and that no finding of a Python app moves; under `### Added`, `Comment.marker`
  and `.doc`, and the fact `comment.doc`, which `guards.no-comments` needs.
- Golden docs regenerated with the repo's command, diff read, expected empty; never edited by hand.
- `docs/examples/**` copies of changed files (`profile_values/language.py`, `parsed.py`, `fs_source_tree.py`, ...):
  updated only if a test or the docs generator holds them to the code; the planner checks which.

## 6. Out of scope

- Privacy decided by the reader (LN 9, release step 8d, card 3.9) and records and immutable marks (LN 10, 8e, 3.10).
- A reader for any language but Python; any reader that sets `doc=True` (Python has none; brace and percent are
  proved with hand-built `Comment` values only).
- `FileType.comment` and `file_types.yaml` (headers of non-language files).
- Any retired-keys entry or migration hint for `comment`.
- Refusing two forms written twice, or a `line` marker equal to a block's opening (not ruled; read as written).
- Editing the recorded corpora.

## 7. Gates

Each passes on this branch alone, full suite green: `uv run pytest -q` (over two minutes: run it in the background
with `timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`.

Project rules: no comments in xarch's code (docstrings as the code base writes them); tests first; examples simple,
with absolute `app.` imports; recorded corpora edited by hand only, and not at all in this step; Python only in the
reader adapter and the data files under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is
pushed.

## 8. Review focus (for the planner)

1. A hand-built `Comment` with no marker (`marker=""`, the default): never a directive by the words or encoding
   branches (no hidden `#`), still reported by `no-comments` unless `doc`.
2. A doc form whose opening starts with a line marker (percent `///` against `//`; brace `/**` against `/*`): the
   reader decides which form a comment is; the checks read `doc` and `marker` only, never re-derive them from `text`.
3. Python's docs line, `%directives%` and every `no-comments` finding byte-identical to today's.
4. `comments` left out: `%comment%` is `""` everywhere (`written.py`, docs, explain); nothing prints a stray marker
   or crashes on an empty one (e.g. `re.escape("")`).
5. The seam test with a doc form's empty closing: `""` is never added to the tokens (it would match every empty
   literal).


---

# 3.8 language: comments read in more than one form — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A language's data file says the forms its comments are written in (`comments`: `line`, `block`, `doc`), the
reader says of each comment the marker it opens with and whether it is a doc comment, and the checking code stops
assuming one marker, one `%comment%` value of its own, and that every comment is one `no-comments` reports — with no
finding, corpus or golden doc of a Python app moving.

**Architecture:** `profile_values/language.py` gains `CommentForm` and the kind constants `LINE`, `BLOCK`;
`CheckedLanguage.comment` becomes a read-only property over the new `comments` field, so every reader of `%comment%`
(`written.py`, `docs_template.py`, `explain.py`) reads on unchanged; spec's loader reads and refuses the list
(Task 1). The rules domain's `Comment` gains `marker` and `doc`; the Python reader sets `marker="#"`; the `comment`
fact carries the marker as its `name` and the vocabulary declares it as a field `marker`; the `directive` filter
matches after the comment's own marker (Task 2). A `doc` trait, field and filter let `no-comments` exempt doc
comments, which makes the rule (and spec's `NEEDS`) need the new fact `comment.doc` (Task 3). Docs and gates last
(Task 4).

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140), `uv run`.

**Spec:** `docs/superpowers/specs/3-8-language-comments-0954fb83.md` (prepended above).

## Global Constraints

- `comment` is no longer a data-file key; written, it is an unknown key with today's text
  (`unknown key 'comment': use ...`, the sorted key set holding `comments`), no retired-keys entry, no hint.
- `comments` is optional: left out, the language has no forms and `%comment%` is `""`. No code supplies `#` (or any
  marker) in its place.
- Refusal texts, verbatim, each once for the key:
  `comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}`;
  `comments: needs one form at least`.
- `FACTS["comment"]` is exactly `each comment, its text, its line and where on it it starts and ends, and the marker it
  opens with, which review cuts before it sends a text`; `FACTS["comment.doc"]` is exactly
  `whether a comment is a doc comment`, placed right after `file.package`.
- `python.yaml`: only `comments: [{line: "#"}]` (in `comment`'s place), `comment.doc: exact` right after
  `comment: exact` under `supplies`, and the header words for `comments`/`directives`/`encoding` change.
- `NEEDS["guards.no-comments"] == ("comment", "comment.doc")`.
- Python's findings, `tests/bootstrap/corpora/` (never edited) and the golden docs `docs/{cli,web,xarch}/testing.md`
  (regenerated, diff empty) do not move; line 180 of `docs/xarch/testing.md` stays byte for byte.
- `FileType.comment` / `file_types.yaml` / `file_types.py` do not change.
- No comments in xarch's code (docstrings as the code base writes them); tests first; Python only in the reader
  adapter (`modules/rules/adapters/fs_source_tree.py`, the only xarch file that writes the literal `"#"`) and the data
  files under `xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed.
- `profile_values/` imports only `kernel` (not `kernel/logic`); `CommentForm`, `LINE` and `BLOCK` are plain values; `DOC` lives in `language_file.py` because only the loader uses it.
- Gates (Task 4): `uv run pytest -q` (run in the background with `timeout`), `uv run xarch check`,
  `uv run xarch check --strict`, `uv run ruff check` (never `--fix`), `uv run xarch profile check architecture.yaml`.

## Design decisions the spec left to the planner

- The value is `CommentForm(kind: str, opening: str, closing: str = "")` (not `open`/`close`, which shadow builtins),
  with module constants `LINE = "line"` and `BLOCK = "block"` in `xarch/profile_values/language.py` (the `comment` property reads
  them), and `DOC = "doc"` in `xarch/modules/spec/application/logic/language_file.py`, its one user: a `DOC` constant
  in `profile_values/` is read by `modules/spec` alone, and `tests/architecture/test_self_check.py` (and `xarch check`)
  refuse it with `parts.profile-values.shared` ("profile-values/ holds only what at least 2 users share").
- The `comment` fact carries the marker as `Fact.name` (`c.marker or None`, so a hand-built comment with no marker
  keeps today's `name=None`), declared in the vocabulary as a new field `marker` (`FIELDS["marker"]`), which the
  `directive` filter reads beside `text`; and the doc flag as the trait `doc`, declared as a field `doc` of the comment
  kind with `field_needs={"doc": ("comment.doc",)}` — the same pattern as the class kind's `interface` field and
  `class.interface`. (The spec's "sometimes" is read as "needing `comment.doc`": `Kind.sometimes` means "carried only
  when a filter holds", which does not fit a flag.)
- The filter is named `doc` (`the comment is a doc comment: a comment the language keeps its documentation in`),
  answered by the trait, listed in `FILTERS` right after `directive`.
- `no-comments` is `exempt=_all("directive", "doc")`.

## Review Focus

1. A hand-built `Comment` with no marker (`marker=""`): never a directive by the words or the encoding branch (no
   hidden `#`, no `re.escape("")` matching at the start), still reported by `no-comments` unless `doc`. Pinned in Task
   2 (`test_allowed` rows "a comment whose reader gives no marker is no directive", "nor an encoding declaration, with
   no marker given") and Task 3 (row "a doc comment with no marker stays").
2. A doc form whose opening starts with a line marker (percent `///` against `//`; brace `/**` against `/*`): the checks
   read `doc` and `marker` only. Pinned in Task 2 (`/// a note` with marker `//` under percent is reported; `/** a note
   */` with marker `/*` under brace is reported) and Task 3 (the same texts with `doc=True` and their own markers stay).
3. Python's docs line, `%directives%` and every `no-comments` finding byte-identical. Pinned in Task 1
   (`test_the_words_of_a_language_say_its_first_comment_marker_and_each_directive_after_it`, Python row), Task 2 (every
   Python row of `test_allowed` keeps today's answer with `marker="#"`), Task 4 (golden docs diff empty,
   `tests/bootstrap/test_bundled_guards.py` unchanged).
4. `comments` left out: `%comment%` is `""` in `written.py` and `explain.py`, nothing crashes. Pinned in Task 1
   (`test_comments_left_out_read_no_form_and_no_marker_and_the_file_loads`; the `bare` row of the explain test; the
   `%comment%` row of `test_the_tokens_of_the_language_are_filled_in` under a language with no forms).
5. The seam guard with a doc form's empty closing: `""` is never a token (it would equal every empty literal). Pinned in
   Task 1 (`test_the_guard_finds_every_comment_marker_of_a_test_only_language_and_never_an_empty_closing`, which writes
   `G = ""` under percent).

---

### Task 1: The data file's `comments`, the language value, and `comment.doc` supplied

**Files:**
- Modify: `xarch/profile_values/language.py` (constants and `CommentForm` beside `InterfaceMark`; `CheckedLanguage`
  field `comment` → `comments`, property `comment`, docstring lines 40-42)
- Modify: `xarch/modules/spec/application/logic/language_file.py` (docstring lines 32-36; `KEYS` line 67-69; texts;
  `tokens` line 122-123; `_comments`/`_comment_form`; construction line 138-140)
- Modify: `xarch/profile_values/capabilities.py:26-27` (`comment`) and after line 45 (`comment.doc`)
- Modify: `xarch/modules/spec/application/logic/explain.py:27-31` (docstring only)
- Modify: `xarch/architectures/presets/language/python.yaml` (header lines 16-19, `comment:` line, `supplies`)
- Modify: `tests/fakes/languages/brace.yaml`, `tests/fakes/languages/percent.yaml`
- Modify: `tests/modules/rules/builders.py:24,39-60`
- Modify: `tests/architecture/test_language_seam.py` (docstring lines 31-33; `TOKEN_KEYS`; `language_tokens`;
  `ticked_pattern`; a new probe test)
- Test: `tests/modules/spec/application/logic/test_language_file.py`
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`
- Test: `tests/modules/spec/application/logic/test_explain.py`
- Test: `tests/modules/rules/application/logic/test_written.py:10,66-71,81-83`
- Test: `tests/modules/spec/application/logic/test_docs_template.py:2,290-297`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `xarch.profile_values.language.LINE: str = "line"`, `BLOCK: str = "block"`; `language_file.DOC: str = "doc"`.
  - `xarch.profile_values.language.CommentForm(kind: str, opening: str, closing: str = "")`, frozen.
  - `CheckedLanguage.comments: tuple[CommentForm, ...] = ()` (in the field slot `comment` held); property
    `CheckedLanguage.comment -> str` (first `LINE` form's opening, else first `BLOCK` form's opening, else `""`).
  - `language_file.COMMENTS: str`, `language_file.NO_COMMENTS: str` (the two refusal texts).
  - `FACTS["comment.doc"]`; Python supplies it `exact`.
  - `tests.modules.rules.builders.forms_of(file: dict) -> tuple[CommentForm, ...]`; `PYTHON`, `BRACE`, `PERCENT` carry
    their files' forms, and `BRACE` its `directives`.

- [ ] **Step 1: Write the failing loader tests**

In `tests/modules/spec/application/logic/test_language_file.py`:

Replace the import line

```python
from xarch.modules.spec.application.logic.language_file import PARTIAL, first_language, language_of
```

with

```python
from xarch.modules.spec.application.logic.language_file import DOC, PARTIAL, first_language, language_of
```

and the import line

```python
from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark
```

with

```python
from xarch.profile_values.language import BLOCK, LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark
```

(`DOC` is the loader's, not `profile_values`': a constant there that only spec reads fails `test_self_check.py`.)

Replace `KEYS_USED` (lines 33-35) with

```python
KEYS_USED = ("branching, branching_expressions, cache, call, comments, directives, dynamic, encoding, extensions, "
             "immutable, importing, interface, member, name, namespace, nothing, package, package_files, private, "
             "shebang, special, standard, supplies, title, unannotated")
"""The keys of a data file, as the unknown-key text lists them."""
COMMENTS = "comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}"
```

In `test_the_tokens_of_the_code_are_read_when_the_document_gives_them`, replace `"comment": "//",` with
`"comments": [{"line": "//"}],` (the assertion on `checked.comment == "//"` stays as written: it now reads the
property).

In the parametrize list of `test_a_token_that_is_not_what_its_key_takes_is_a_problem`, delete the row

```python
    pytest.param({"comment": ""}, "comment: must be a non-empty string", id="an empty comment marker"),
```

Append at the end of the file:

```python
def test_the_test_only_languages_read_their_comment_forms_in_the_order_written():
    read = {path.stem: language_of(path.stem, yaml.safe_load(path.read_text(encoding="utf-8"))).checked
            for path in TEST_LANGUAGES}
    assert read["brace"].comments == (CommentForm(LINE, "//"), CommentForm(BLOCK, "/*", "*/"),
                                      CommentForm(DOC, "/**", "*/"))
    assert read["percent"].comments == (CommentForm(LINE, "//"), CommentForm(LINE, ";"), CommentForm(BLOCK, "/*", "*/"),
                                        CommentForm(DOC, "///", ""))
    assert (read["brace"].comment, read["percent"].comment) == ("//", "//")


@pytest.mark.parametrize("comments, comment", [
    pytest.param([{"block": ["/*", "*/"]}], "/*", id="a block form alone gives its opening"),
    pytest.param([{"doc": ["///", ""]}], "", id="a doc form alone gives none, a doc opening never being the comment"),
    pytest.param([{"doc": ["/**", "*/"]}, {"block": ["/*", "*/"]}, {"line": "--"}], "--",
                 id="a line form wins over a block form written before it"),
])
def test_the_comment_is_the_first_line_marker_else_the_first_block_opening(comments, comment):
    assert language_of("pascal", DOCUMENT | {"comments": comments}).checked.comment == comment


def test_comments_left_out_read_no_form_and_no_marker_and_the_file_loads():
    checked = language_of("pascal", DOCUMENT).checked
    assert (checked.comments, checked.comment) == ((), "")


@pytest.mark.parametrize("value", [
    pytest.param("#", id="a string"),
    pytest.param([{"hash": "#"}], id="a form of an unknown kind"),
    pytest.param([{"line": "#", "block": ["/*", "*/"]}], id="a form of two keys"),
    pytest.param([{"line": ""}], id="a line form with an empty marker"),
    pytest.param([{"line": 3}], id="a line form whose marker is no text"),
    pytest.param([{"block": ["/*"]}], id="a block form of one item"),
    pytest.param([{"block": ["/*", ""]}], id="a block form with an empty closing"),
    pytest.param([{"doc": ["", "*/"]}], id="a doc form with an empty opening"),
    pytest.param(["#"], id="a list holding a string"),
    pytest.param([{"line": "//"}, {"line": ""}], id="one wrong form among right ones"),
])
def test_comments_that_are_not_a_list_of_forms_are_one_problem(value):
    assert refused(DOCUMENT | {"comments": value}) == [COMMENTS]


def test_comments_that_list_no_form_are_refused():
    assert refused(DOCUMENT | {"comments": []}) == ["comments: needs one form at least"]


def test_the_old_key_of_one_comment_marker_is_an_unknown_key():
    assert refused(DOCUMENT | {"comment": "#"}) == [f"unknown key 'comment': use {KEYS_USED}"]
    assert "comments" in KEYS_USED.split(", ") and "comment" not in KEYS_USED.split(", ")


def test_python_writes_one_line_form_and_supplies_comment_doc_exactly():
    document = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                              .read_text(encoding="utf-8"))
    checked = PYTHON_LANGUAGE.checked
    assert (checked.comments, checked.comment) == ((CommentForm(LINE, "#"),), "#")
    assert list(document["supplies"])[list(document["supplies"]).index("comment") + 1] == "comment.doc"
    assert Supply("comment.doc", EXACT) in checked.supplies
```

In `tests/modules/spec/application/logic/test_profile_needs.py`, append:

```python
def test_comment_doc_is_a_fact_after_file_package_and_comment_says_the_marker_it_opens_with():
    facts = list(FACTS)
    assert facts[facts.index("file.package") + 1] == "comment.doc"
    assert FACTS["comment.doc"] == "whether a comment is a doc comment"
    assert FACTS["comment"] == ("each comment, its text, its line and where on it it starts and ends, and the marker it "
                                "opens with, which review cuts before it sends a text")
```

- [ ] **Step 2: Write the failing tests of what reads `%comment%`**

In `tests/modules/spec/application/logic/test_explain.py`, replace the import block (lines 3-12) with

```python
from dataclasses import replace

from tests.modules.spec.languages import BRACE, PERCENT, PYTHON
from xarch.modules.spec.application.logic.explain import (
    cleaned,
    example_of,
    held_by,
    key_at,
    nearest,
    overview_keys,
    words,
)
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
```

and append:

```python
def test_the_words_of_a_language_say_its_first_comment_marker_and_each_directive_after_it():
    assert (words(PYTHON)["comment"], words(PYTHON)["directives"]) == ("#", "`# type: ignore`, `# noqa`, `# pragma:`")
    assert (words(BRACE)["comment"], words(BRACE)["directives"]) == (
        "//", "`// @ts-expect-error`, `// eslint-disable`")
    assert (words(PERCENT)["comment"], words(PERCENT)["directives"]) == ("//", "")
    bare = replace(PERCENT, checked=replace(PERCENT.checked, comments=()))
    assert words(bare)["comment"] == ""
```

In `tests/modules/rules/application/logic/test_written.py`:

Replace line 10 `from xarch.profile_values.language import CheckedLanguage` with

```python
from tests.modules.rules.builders import BRACE
from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm
```

(place the `tests.` import first in the first-party block, before the `xarch.` imports, as ruff's isort orders them:
move it above line 6 `from xarch.kernel.logic.targets import target`.)

In `test_a_check_of_one_s_own_is_written_under_its_id_with_its_examples_filled_in`, replace
`CheckedLanguage(extensions=(".py",), comment="#")` with
`CheckedLanguage(extensions=(".py",), comments=(CommentForm(LINE, "#"),))`.

In `test_the_tokens_of_the_language_are_filled_in`, replace
`language = CheckedLanguage(extensions=(".py",), comment="#", importing=importing)` with
`language = CheckedLanguage(extensions=(".py",), comments=(CommentForm(LINE, "#"),), importing=importing)`.

After that test, add:

```python
def test_the_comment_token_is_the_first_comment_marker_of_the_language_and_nothing_when_it_has_none():
    own = OwnCheck(Rule("no-todo", Scope(), ("comment",), MAY_NOT, EXISTING, SAID),
                   (("notes%extension%", "%comment% TODO\n"),), ())
    (shown,) = written_own((own,), BRACE).values()
    assert shown.flagged == (("notes.ts", "// TODO\n"),)
    (bare,) = written_own((own,), CheckedLanguage(extensions=(".py",))).values()
    assert bare.flagged == (("notes.py", " TODO\n"),)
```

In `tests/modules/spec/application/logic/test_docs_template.py`, delete line 2 `from dataclasses import replace` (the
blank line after the docstring stays), and replace the test at lines 290-296 with:

```python
def test_a_quoted_file_of_any_ending_of_the_language_of_the_app_is_fenced_with_the_language_s_name():
    view = "src/billing/api/view.tsx"
    architecture = parsed(layered(docs=DOCS | {"example_notes": {}}, language="brace"), folders={"ex": (view,)},
                          languages={"python": PYTHON, "brace": BRACE})
    assert fill("{{example:" + view + "}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES) == (
        "```brace\n// src/billing/api/view.tsx\nx\n```")


def test_the_no_comments_line_says_the_first_comment_marker_of_the_language_and_each_directive_after_it():
    view = "src/billing/api/view.tsx"
    architecture = parsed(layered(docs=DOCS | {"example_notes": {}}, language="brace", guards={"no-comments": {}}),
                          folders={"ex": (view,)}, languages={"python": PYTHON, "brace": BRACE})
    filled_in = fill("{{guards}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES)
    assert [line for line in filled_in.splitlines() if "`no-comments`" in line] == [
        "- `no-comments`: no `//` comments in the app or its tests; docstrings and tool directives "
        "(`// @ts-expect-error`, `// eslint-disable`) stay."]
```

(`BRACE` of `tests/modules/spec/languages.py` is loaded from `brace.yaml`, which carries the forms after Step 5, so the
old `replace(..., comment="//")` is no longer needed.)

- [ ] **Step 3: Write the failing seam-guard probe**

In `tests/architecture/test_language_seam.py`, after `test_the_guard_finds_a_token_of_the_language_where_it_is_written`,
add:

```python
def test_the_guard_finds_every_comment_marker_of_a_test_only_language_and_never_an_empty_closing(tmp_path):
    brace, percent = (next(path for path in TEST_LANGUAGES if path.stem == stem) for stem in ("brace", "percent"))
    (tmp_path / "tokens.py").write_text('A = "/*"\nB = "*/"\nC = "/**"\nD = "//"\nE = ";"\nF = "///"\nG = ""\nH = "/"\n')
    assert sorted(token for _, _, token in token_leaks(tmp_path, brace)) == ["*/", "/*", "/**", "//"]
    assert sorted(token for _, _, token in token_leaks(tmp_path, percent)) == ["*/", "/*", "//", "///", ";"]
```

- [ ] **Step 4: Run the new tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_explain.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/logic/test_docs_template.py tests/architecture/test_language_seam.py`

Expected: FAIL — `ImportError: cannot import name 'BLOCK' from 'xarch.profile_values.language'` (collection errors of
`test_language_file.py` and `test_written.py`); `test_explain.py` fails on `comments=()` being an unexpected field or
`"comment": ""` for BRACE; the docs-template brace test prints `no `` comments`; the seam probe raises `KeyError`
(brace has no `private`) or finds no marker.

- [ ] **Step 5: The language value, the loader, the facts, the data files**

In `xarch/profile_values/language.py`, after the `InterfaceMark` class, add:

```python
LINE = "line"
"""The kind of a comment form that runs from its marker to the end of its line."""
BLOCK = "block"
"""The kind of a comment form that runs from its opening to its closing."""


@dataclass(frozen=True)
class CommentForm:
    """One form a comment of the language is written in: its kind (LINE, BLOCK or "doc"), the marker that opens it, and
    the one that closes it ("" for a line form, and for a doc form that runs to the end of its line)."""
    kind: str
    opening: str
    closing: str = ""
```

In `CheckedLanguage`'s docstring, replace

```
    gives none (unannotated: nothing when it does; empty when the data file does not say), the marker of a line
    comment, the comments its tools read (after the marker, a space standing for any spaces), how line 1 names the
    program that runs the file, how line 1 or 2 declares the encoding (a regular expression, after the marker), and
```

with

```
    gives none (unannotated: nothing when it does; empty when the data file does not say), the forms a comment is
    written in (comments, in the order written: a line form runs from its marker to the end of its line, a block form
    from its opening to its closing, and a doc form, a comment the language keeps its documentation in, the same, an
    empty closing being the end of its line; none: the language has no comments), the comments its tools read (after
    the marker of a comment of any form, a space standing for any spaces), how line 1 names the program that runs the
    file, how line 1 or 2 declares the encoding (a regular expression, after the marker of a comment), and
```

Replace the field line `    comment: str = ""` with `    comments: tuple[CommentForm, ...] = ()` (same place, between
`nothing` and `directives`), and after the `package_file` property add:

```python
    @property
    def comment(self) -> str:
        """The marker the docs and `%comment%` print: the first line form's, else the first block form's opening; ""
        when the language has neither. A doc form's opening never is."""
        line = next((form.opening for form in self.comments if form.kind == LINE), "")
        return line or next((form.opening for form in self.comments if form.kind == BLOCK), "")
```

In `xarch/modules/spec/application/logic/language_file.py`:

Replace the four docstring lines

```
    comment        the marker of a line comment
    directives     the comments its tools read as instructions, each after the marker; a space stands for any spaces
    shebang        how line 1 names the program that runs the file
    encoding       a regular expression: how line 1 or 2 declares the file's encoding, after the marker
```

with

```
    comments       the forms a comment is written in, a non-empty list in the order written: {line: <marker>}, from
                   the marker to the end of its line; {block: [<open>, <close>]}, from the one to the other; and
                   {doc: [<open>, <close>]}, a comment the language keeps its documentation in, whose closing may be
                   "" for the end of its line. The docs print the first line form's marker, else the first block
                   form's opening
    directives     the comments its tools read as instructions, each after the marker of a comment of any form; a
                   space stands for any spaces
    shebang        how line 1 names the program that runs the file
    encoding       a regular expression: how line 1 or 2 declares the file's encoding, after the marker of a comment
                   of any form
```

Replace the import line

```python
from xarch.profile_values.language import NOTHING, CheckedLanguage, InterfaceMark, RecordMark
```

with

```python
from xarch.profile_values.language import BLOCK, LINE, NOTHING, CheckedLanguage, CommentForm, InterfaceMark, RecordMark
```

In `KEYS`, replace `"comment"` with `"comments"` (same place). After the `PACKAGE_FILES` constant and its docstring,
add:

```python
DOC = "doc"
"""The kind of a comment form the language keeps its documentation in, from its opening to its closing (empty: the end
of its line); `line` and `block` are LINE and BLOCK of `profile_values/language.py`, which the language reads itself."""
COMMENTS = "comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}"
"""What the loader says of a value of `comments` that is not a list of comment forms, once for the key."""
NO_COMMENTS = "comments: needs one form at least"
"""What the loader says of an empty list of comment forms."""
```

In `language_of`, replace

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "comment", "shebang")}
```

with

```python
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "shebang")}
    comments = _comments(document, problems)
```

and in the `CheckedLanguage(...)` construction replace `comment=tokens["comment"]` with `comments=comments`.

After `_package_files`, add:

```python
def _comments(document: Mapping[Any, Any], problems: list[str]) -> tuple[CommentForm, ...]:
    """The forms a comment is written in, in the order written; none when the key is left out. One problem for the
    key when it is an empty list, or no list, or any item is no form."""
    if "comments" not in document:
        return ()
    value = document["comments"]
    if value == []:
        problems.append(NO_COMMENTS)
        return ()
    items = value if isinstance(value, list) else None
    forms = tuple(form for form in (_comment_form(item) for item in items or ()) if form is not None)
    if items is None or len(forms) != len(items):
        problems.append(COMMENTS)
        return ()
    return forms


def _comment_form(item: Any) -> CommentForm | None:
    """One form: a map of one key, line with a non-empty marker, or block or doc with a list of two strings, the
    opening non-empty and, for a block, the closing too; None when the item is none of them."""
    if not (isinstance(item, Mapping) and len(item) == 1):
        return None
    ((kind, value),) = item.items()
    if kind == LINE:
        return CommentForm(LINE, value) if isinstance(value, str) and value.strip() else None
    if kind in (BLOCK, DOC) and isinstance(value, list) and len(value) == 2 and all(isinstance(part, str) for part in value):
        opening, closing = value
        return CommentForm(kind, opening, closing) if opening.strip() and (closing.strip() or kind == DOC) else None
    return None
```

In `xarch/profile_values/capabilities.py`, replace

```python
    "comment": "each line comment, its text, its line and where on it it starts and ends, which review cuts before it "
               "sends a text",
```

with

```python
    "comment": "each comment, its text, its line and where on it it starts and ends, and the marker it opens with, "
               "which review cuts before it sends a text",
```

and right after the line `    "file.package": "a file stands for the folder that holds it",` add

```python
    "comment.doc": "whether a comment is a doc comment",
```

In `xarch/modules/spec/application/logic/explain.py`, replace the docstring of `words`:

```python
    """What the language says for each `%word%` a text of the format may write: the title, the extension, the package
    file, the name of an interface and its path (the first mark's base as an outside name, or its keyword), the
    namespace of the names bound without an import, the comment marker (its first line form's, else its first block
    form's opening, "" when it has neither) and the comments its tools read, each quoted after that marker, the prefix
    of a private name, and the annotations of no value, each as written, joined by ` or `."""
```

(the code of `words` does not change: `checked.comment` is now the property.)

In `xarch/architectures/presets/language/python.yaml`, replace the header lines

```
# function with no return annotation gives none; comment, the marker of a line comment; directives, the comments its
# tools read as instructions, each after the marker (a space in one stands for any spaces); shebang, how line 1 names
# the program that runs the file; encoding, how line 1 or 2 declares the file's encoding (a regular expression, after
# the marker); branching, the keywords of the statements that branch; branching_expressions, the keywords of the
```

with

```
# function with no return annotation gives none; comments, the forms a comment is written in, each {line: <marker>},
# to the end of its line, {block: [<open>, <close>]}, or {doc: [<open>, <close>]}, a comment that holds documentation
# (its closing may be "" for the end of its line; Python writes line comments only, its documentation being in
# docstrings), the docs printing the first line form's marker; directives, the comments its tools read as
# instructions, each after the marker of a comment of any form (a space in one stands for any spaces); shebang, how
# line 1 names the program that runs the file; encoding, how line 1 or 2 declares the file's encoding (a regular
# expression, after the marker of a comment of any form); branching, the keywords of the statements that branch;
# branching_expressions, the keywords of the
```

replace the line `comment: "#"` with `comments: [{line: "#"}]`, and under `supplies` add `  comment.doc: exact` on
the line right after `  comment: exact`. Nothing else in the file moves.

Replace `tests/fakes/languages/brace.yaml`'s header and add two keys at the end, so the file reads:

```yaml
# A test-only language that imitates a TypeScript-like one: no profile names it and no reader is written for it. Its
# packages are named as a package manager names them (a scope, a dash, a dot) or as its runtime's own modules
# (node:fs), and a name in one is joined to it by #. It gives its standard library's top-level modules, its reserved
# words and its builtins as lists, so that spec reads them from here and asks no runtime. Its source files end in .ts,
# .tsx or .mts, and index.ts or index.tsx stands for the folder holding it; index.mts is a module like any other. Its
# comments come in three forms, a line one (//), a block one (/* */) and a doc one (/** */), and its tools read two
# directives after the marker of any of them. The tests load it to show that the profile and the checks read outside
# names and comments by a language's own patterns; later steps add their keys to it.
title: Brace
extensions: [.ts, .tsx, .mts]
package_files: [index.ts, index.tsx]
namespace: globalThis
standard: {modules: [fs, path, "node:fs", "node:path"], reserved: [class, const, function, interface],
           builtins: [globalThis, fetch]}
name: '[A-Za-z_$][A-Za-z0-9_$]*'
package: '(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*|node:[a-z_/]+'
member: "#"
interface: [{keyword: interface}]
nothing: [void, "Promise<void>"]
dynamic: ["node:module#createRequire"]
comments: [{line: "//"}, {block: ["/*", "*/"]}, {doc: ["/**", "*/"]}]
directives: ["@ts-expect-error", eslint-disable]
```

Replace `tests/fakes/languages/percent.yaml` so it reads:

```yaml
# A test-only language that imitates an ObjectScript-like one: no profile names it and no reader is written for it.
# Its names and packages may start with %, and a name in a package is joined to it by a dot. Its source files end in
# .cls or .mac, and it has no package file: no file stands for the folder holding it. Its comments come in four forms,
# two line ones (// and ;), a block one (/* */) and a doc one (///) that runs to the end of its line; the docs print
# the first line marker. The tests load it to show that the profile and the checks read outside names and comments by
# a language's own patterns; later steps add their keys to it.
title: Percent
extensions: [.cls, .mac]
namespace: "%SYSTEM"
standard: interpreter
name: '%?[A-Za-z][A-Za-z0-9]*'
package: '%?[A-Za-z][A-Za-z0-9]*'
member: "."
special: '%\w+'
unannotated: nothing
interface: [{keyword: Abstract}]
dynamic: ["%SYSTEM.OBJ.Load"]
immutable: ["%SerialObject"]
comments: [{line: "//"}, {line: ";"}, {block: ["/*", "*/"]}, {doc: ["///", ""]}]
```

- [ ] **Step 6: The builders and the seam guard**

In `tests/modules/rules/builders.py`, replace line 24

```python
from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark
```

with

```python
from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark
```

After `marks_of`, add:

```python
def forms_of(file: dict) -> tuple[CommentForm, ...]:
    """The comment forms a language's data file writes, as its loader reads them: a line form's marker alone, a block
    form's or a doc form's opening and closing."""
    return tuple(CommentForm(kind, value) if kind == LINE else CommentForm(kind, *value)
                 for form in file.get("comments", ()) for kind, value in form.items())
```

In `PYTHON = CheckedLanguage(...)`, replace `comment="#",` with `comments=forms_of(PYTHON_FILE),`.

Replace the `BRACE` and `PERCENT` definitions and their docstrings with:

```python
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extensions=tuple(BRACE_FILE["extensions"]),
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        comments=forms_of(BRACE_FILE), directives=tuple(BRACE_FILE["directives"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
"""The TypeScript-like test-only language as a check reads it, its endings, package files, patterns, member, interface
marks, annotations of no value, comment forms, directives and standard modules read from its data file."""
PERCENT_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "percent.yaml")
                              .read_text(encoding="utf-8"))
PERCENT = CheckedLanguage(title=PERCENT_FILE["title"], extensions=tuple(PERCENT_FILE["extensions"]),
                          interface=marks_of(PERCENT_FILE), comments=forms_of(PERCENT_FILE),
                          special=PERCENT_FILE["special"], unannotated=PERCENT_FILE["unannotated"],
                          names=PERCENT_FILE["name"], package=PERCENT_FILE["package"], member=PERCENT_FILE["member"])
"""The ObjectScript-like test-only language as a check reads it: its interface marks, its comment forms (two line
markers among them), the pattern of a special name and its word on a method with no annotation read from its data
file."""
```

(keep the `BRACE_FILE = ...` line above `BRACE` as it is; the `PERCENT_FILE` line is repeated here only because it sits
between the two definitions.)

In `tests/architecture/test_language_seam.py`:

In the module docstring, replace

```
    a literal that is a token     the prefix of a private name, the affix of a special one, the special method calling
                                  an instance runs, the annotation of no value, the comment marker, the shebang: a
                                  string literal equal to one is the language's rule written in xarch's code
```

with

```
    a literal that is a token     the prefix of a private name, the affix of a special one, the special method calling
                                  an instance runs, the annotation of no value, the comment markers (the marker of
                                  each line form, the opening and the closing of each block or doc form), the
                                  shebang: a string literal equal to one is the language's rule written in xarch's code
```

Replace `TOKEN_KEYS`, its docstring and `language_tokens` with:

```python
TOKEN_KEYS = ("private", "call", "shebang")
"""The keys of the data file whose value is a token of the language's code; `nothing` lists several, each a token, and
`comments` several markers, each a token too (comment_markers); `special` is the pattern of a special name, which a
literal may not match in full."""


def comment_markers(data: dict) -> set[str]:
    """Every marker of the data file's comment forms: each line form's marker, and the opening and the closing of each
    block or doc form; a doc form's empty closing (the end of its line) is none."""
    found: set[str] = set()
    for form in data.get("comments", ()):
        for kind, value in form.items():
            found |= {value} if kind == "line" else set(value)
    return found - {""}


def alternatives(words) -> str:
    """The words as the alternatives of a pattern, the longest first; a pattern that matches nothing when there are
    none."""
    return "|".join(sorted((re.escape(word) for word in words), key=len, reverse=True)) or "(?!)"


def language_tokens(language: Path = LANGUAGE) -> tuple[set[str], re.Pattern[str], re.Pattern[str]]:
    """The tokens a literal may not be, the pattern of a special name a literal may not match in full, and the pattern
    of the directive words and of the branching keywords quoted as code."""
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    tokens = {data[key] for key in TOKEN_KEYS if key in data} | set(data.get("nothing", ())) | comment_markers(data)
    special = re.compile(data.get("special") or "(?!)")
    directives, branching = alternatives(data.get("directives", ())), alternatives(data.get("branching", ()))
    return tokens, special, re.compile(rf"(?<![A-Za-z0-9_])(?:{directives})(?![A-Za-z0-9_])|`(?:{branching})`")
```

In `ticked_pattern`, replace

```python
    tokens = "|".join(re.escape(token) for token in (*(data[key] for key in TOKEN_KEYS), *data.get("nothing", ())))
```

with

```python
    markers = comment_markers(data)
    tokens = alternatives((*(data[key] for key in TOKEN_KEYS if key in data), *data.get("nothing", ()), *markers))
```

and in its returned pattern replace `rf"|^{re.escape(data['comment'])}|^{importing}(?= )"` with
`rf"|^(?:{alternatives(markers)})|^{importing}(?= )"`.

- [ ] **Step 7: Run the tests of the task to verify they pass**

Run: `timeout 600 uv run pytest -q tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_explain.py tests/modules/rules/application/logic/test_written.py tests/modules/spec/application/logic/test_docs_template.py tests/architecture/test_language_seam.py tests/bootstrap/test_needs_agree.py`

Expected: PASS (`test_python_supplies_every_fact_a_bundled_check_reads` holds: Python supplies `comment.doc`;
`test_needs_agree.py` holds: nothing reads `comment.doc` yet on either side).

Then the modules that build languages and comments:

Run: `timeout 900 uv run pytest -q tests/modules tests/profile_values tests/kernel tests/architecture`
Expected: PASS. If a test still builds `CheckedLanguage(comment=...)`, it fails with
`TypeError: ... unexpected keyword argument 'comment'`: move it to `comments=(CommentForm(LINE, "<marker>"),)`
(`grep -rn "comment=" tests --include=*.py | grep -v FileType` finds none beyond those of Steps 1-2).

- [ ] **Step 8: Commit**

```bash
git add xarch/profile_values/language.py xarch/profile_values/capabilities.py \
  xarch/modules/spec/application/logic/language_file.py xarch/modules/spec/application/logic/explain.py \
  xarch/architectures/presets/language/python.yaml tests/fakes/languages/brace.yaml tests/fakes/languages/percent.yaml \
  tests/modules/rules/builders.py tests/architecture/test_language_seam.py \
  tests/modules/spec/application/logic/test_language_file.py tests/modules/spec/application/logic/test_profile_needs.py \
  tests/modules/spec/application/logic/test_explain.py tests/modules/rules/application/logic/test_written.py \
  tests/modules/spec/application/logic/test_docs_template.py
git commit -F - <<'EOF'
A language's data file says the forms its comments are written in, comments, a list of line, block and doc forms, refused once otherwise; %comment% is the first line marker, else the first block opening, and empty with no forms; the fact comment.doc follows file.package and Python supplies it; brace and percent write three and four forms

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: The reader's marker, and a directive matched after the comment's own marker

**Files:**
- Modify: `xarch/modules/rules/domain/parsed.py:10-19` (`Comment`)
- Modify: `xarch/modules/rules/adapters/fs_source_tree.py:310-315` (`_comments`)
- Modify: `xarch/modules/rules/application/logic/facts.py:28,169-170`
- Modify: `xarch/modules/rules/domain/vocabulary.py:165` (FIELDS), `:226` (Kind comment), `:291-292` (Filter directive)
- Modify: `xarch/modules/rules/application/logic/filters.py:145-154` (`_directive`)
- Test: `tests/modules/rules/adapters/test_fs_source_tree.py:1043-1054`
- Test: `tests/modules/rules/application/logic/test_comments.py` (rewritten)
- Test: `tests/modules/rules/application/logic/test_facts.py` (one test appended)
- Test: `tests/modules/rules/application/logic/world.py:59` (markers on DOMAIN's comments)
- Test: `tests/modules/rules/application/logic/test_reads.py:21-23` (`STORED`)

**Interfaces:**
- Consumes: `BRACE`, `PERCENT`, `PYTHON` of `tests/modules/rules/builders.py` with their comment forms and (brace)
  directives (Task 1); `CheckedLanguage.directives`, `.shebang`, `.encoding`.
- Produces:
  - `Comment(line, text, column=0, end=0, last=0, marker: str = "", doc: bool = False)` (`doc` used by Task 3).
  - The `comment` fact: `Fact("comment", line, name=marker or None, text=text)`.
  - `FIELDS["marker"]`; the comment kind's fields `("line", "text", "marker")`; the `directive` filter reads
    `("text", "marker")`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/adapters/test_fs_source_tree.py`, replace the test at lines 1043-1055 with:

```python
@pytest.mark.parametrize("text, comments", [
    pytest.param("x = 1  # one\n    # two\n",
                 (Comment(1, "# one", 7, 12, marker="#"), Comment(2, "# two", 4, 9, marker="#")),
                 id="a comment after code and one on a line of its own, each where it lies on its line"),
    pytest.param("x = '# not one'  # one\n", (Comment(1, "# one", 17, 22, marker="#"),),
                 id="a # inside a string is no comment"),
    pytest.param('"""# no comment"""\ndef f():\n    """Nor # this."""\n', (),
                 id="a docstring is no comment, whatever it holds"),
    pytest.param("x = 1  # one\ry = 2  # two\r\nz = 3  # three\n",
                 (Comment(1, "# one", 7, 12, marker="#"), Comment(2, "# two", 7, 12, marker="#"),
                  Comment(3, "# three", 7, 14, marker="#")),
                 id="a line ended by a carriage return alone is a line of its own, as the parser counts it"),
])
def test_each_comment_is_read_with_where_it_lies(tmp_path, text, comments):
    assert parsed(tmp_path, text).comments == comments
    assert FsSourceTree(FileSystem()).parsed(text, STANDARD).comments == comments
    assert all(comment.marker == "#" and comment.doc is False for comment in parsed(tmp_path, text).comments)
```

Replace `tests/modules/rules/application/logic/test_comments.py` with:

```python
"""The no-comments guard on hand-made comments, each with the marker its reader says it opens with: a comment is
reported unless it is a directive a tool reads right after its own marker, a shebang on line 1 or an encoding
declaration on line 1 or 2; under the test-only languages too, whose comments come in several forms."""
import pytest

from tests.modules.rules.application.logic.checks import comment_allowed as allowed
from tests.modules.rules.application.logic.checks import no_comments as violations
from tests.modules.rules.builders import BRACE, PERCENT, PYTHON, source
from xarch.modules.rules.domain.parsed import Comment


def python_comment(line: int, text: str) -> Comment:
    """A comment as Python's reader hands it over: opened by its one marker."""
    return Comment(line, text, marker="#")


@pytest.mark.parametrize("comment, kept", [
    pytest.param(python_comment(5, "# a note"), False, id="a whole-line comment is reported"),
    pytest.param(python_comment(5, "#a note"), False, id="a comment with no space is reported"),
    pytest.param(python_comment(5, "# type: ignore"), True, id="a type: ignore stays"),
    pytest.param(python_comment(5, "#type:ignore[attr-defined]"), True,
                 id="a type: ignore with a code and no spaces stays"),
    pytest.param(python_comment(5, "# noqa: E501"), True, id="a noqa stays"),
    pytest.param(python_comment(5, "# pragma: no cover"), True, id="a pragma with its colon stays"),
    pytest.param(python_comment(5, "# pragmatic note"), False, id="a word starting with pragma is a comment"),
    pytest.param(python_comment(5, "# pragma no cover"), False, id="a pragma without its colon is a comment"),
    pytest.param(python_comment(5, "# see the noqa rule"), False, id="a directive not at the start is a comment"),
    pytest.param(python_comment(1, "#!/usr/bin/env python"), True, id="a shebang on line 1 stays"),
    pytest.param(python_comment(2, "#!/usr/bin/env python"), False, id="a shebang on line 2 is a comment"),
    pytest.param(python_comment(1, "# -*- coding: utf-8 -*-"), True, id="an encoding declaration on line 1 stays"),
    pytest.param(python_comment(2, "# vim: set fileencoding=utf-8 :"), True,
                 id="an encoding declaration on line 2 stays"),
    pytest.param(python_comment(3, "# -*- coding: utf-8 -*-"), False, id="an encoding declaration on line 3 is a comment"),
    pytest.param(python_comment(1, "# coding is fun"), False, id="the word coding without its value is a comment"),
    pytest.param(Comment(5, "# noqa"), False, id="a comment whose reader gives no marker is no directive"),
    pytest.param(Comment(1, "# -*- coding: utf-8 -*-"), False, id="nor an encoding declaration, with no marker given"),
    pytest.param(Comment(5, "noqa", marker="#"), False,
                 id="a comment whose text does not start with its marker is no directive"),
])
def test_allowed(comment, kept):
    assert allowed(comment, PYTHON) is kept


@pytest.mark.parametrize("comment, kept", [
    pytest.param(Comment(5, "// a note", marker="//"), False, id="a line comment is reported"),
    pytest.param(Comment(5, "/* a note */", marker="/*"), False, id="a block comment is reported"),
    pytest.param(Comment(5, "// @ts-expect-error", marker="//"), True, id="a directive after a line marker stays"),
    pytest.param(Comment(5, "//@ts-expect-error", marker="//"), True, id="a directive right after the marker stays"),
    pytest.param(Comment(5, "/* eslint-disable */", marker="/*"), True,
                 id="a directive after a block opening stays, though the docs print the line marker"),
    pytest.param(Comment(5, "// see @ts-expect-error", marker="//"), False,
                 id="a directive not right after the marker is a comment"),
    pytest.param(Comment(5, "/** a note */", marker="/*"), False,
                 id="a block the reader says is no doc comment is reported, whatever its text starts with"),
])
def test_allowed_under_a_language_of_line_and_block_comments(comment, kept):
    assert allowed(comment, BRACE) is kept


@pytest.mark.parametrize("comment, kept", [
    pytest.param(Comment(5, "; a note", marker=";"), False, id="a comment of the second line marker is reported"),
    pytest.param(Comment(5, "// a note", marker="//"), False, id="a comment of the first line marker is reported"),
    pytest.param(Comment(5, "/// a note", marker="//"), False,
                 id="a line comment whose text starts as a doc one is reported, the reader saying which it is"),
])
def test_allowed_under_a_language_of_two_line_markers(comment, kept):
    assert allowed(comment, PERCENT) is kept


def test_every_comment_not_allowed_is_reported_where_it_is_with_its_fix():
    found = violations([source("kernel/x.py", comments=(python_comment(1, "#!/bin/python"), python_comment(3, "# why"),
                                                         python_comment(4, "# noqa")))], PYTHON)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/kernel/x.py:3: a comment (no-comments)", "no-comments",
         "say it in a docstring or a name, and delete the comment")]
```

In `tests/modules/rules/application/logic/test_facts.py`, after
`test_a_callback_a_comment_the_names_of_a_file_and_the_file_as_a_whole_are_facts`, add:

```python
def test_a_comment_carries_the_marker_it_opens_with_as_its_name():
    read = facts_of([source("modules/docs/domain/a.py", comments=(Comment(2, "// a note", marker="//"),))], [],
                    PROFILE, "app").files[0]
    assert read.facts["comment"] == (Fact("comment", 2, name="//", text="// a note"),)
```

In `tests/modules/rules/application/logic/world.py`, replace

```python
           comments=(Comment(13, "# noqa: E501"), Comment(14, "# a note TODO")),
```

with

```python
           comments=(Comment(13, "# noqa: E501", marker="#"), Comment(14, "# a note TODO", marker="#")),
```

In `tests/modules/rules/application/logic/test_reads.py`, replace `STORED` (lines 21-23) with:

```python
STORED = {"line": "line", "path": "path", "method": "name", "name": "name", "written": "text", "text": "text",
          "marker": "name", "forwarded": "text", "mentions": "names", "reaches": "target", "returned": "target",
          "place": "at", "bound": "bound", "function": "path", **{trait: trait for trait in TRAITS}}
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_filters.py tests/modules/rules/application/logic/test_reads.py`

Expected: FAIL — `TypeError: Comment.__init__() got an unexpected keyword argument 'marker'` at collection.

- [ ] **Step 3: The value, the reader, the fact, the vocabulary, the filter**

In `xarch/modules/rules/domain/parsed.py`, replace the `Comment` class's docstring and fields (keep the `span`
property as it is) with:

```python
@dataclass(frozen=True)
class Comment:
    """A comment as written, its marker included (and a block's closing), and the line it is on; where it lies there:
    from column column to column end of line last (0: its own line), columns counted in characters from 0, end past its
    last character; the marker it opens with, as written ("" when the reader does not say); and whether it is a doc
    comment, one the language keeps its documentation in."""
    line: int
    text: str
    column: int = 0
    end: int = 0
    last: int = 0
    marker: str = ""
    doc: bool = False
```

In `xarch/modules/rules/adapters/fs_source_tree.py`, replace `_comments` with:

```python
def _comments(text: str) -> tuple[Comment, ...]:
    """Each comment the tokens of the text hold, a `#` inside a string being none, its lines cut where the parser
    cuts them (a carriage return alone ending one too), so that they are the lines an import or a piece is on. Each
    opens with `#`, Python's one marker, and none is a doc comment: Python keeps its documentation in docstrings."""
    tokens = tokenize.generate_tokens(io.StringIO(text, newline=None).readline)
    return tuple(Comment(t.start[0], t.string, t.start[1], t.end[1], t.end[0] if t.end[0] != t.start[0] else 0,
                         marker="#", doc=False)
                 for t in tokens if t.type == tokenize.COMMENT)
```

In `xarch/modules/rules/application/logic/facts.py`, replace the docstring line

```
    comment             each line comment, text as written
```

with

```
    comment             each comment, text as written, name the marker it opens with
```

and replace

```python
        case "comment":
            return tuple(Fact("comment", c.line, text=c.text) for c in file.comments)
```

with

```python
        case "comment":
            return tuple(Fact("comment", c.line, name=c.marker or None, text=c.text) for c in file.comments)
```

In `xarch/modules/rules/domain/vocabulary.py`:

After the `FIELDS` line `    "text": "what it says: a comment's text, a syntax error's message",` add

```python
    "marker": "the marker a comment opens with, as its reader writes it",
```

Replace

```python
    Kind("comment", "each line comment, its text as written", ("line", "text"), needs=("comment",)),
```

with

```python
    Kind("comment", "each comment, its text as written", ("line", "text", "marker"), needs=("comment",)),
```

Replace

```python
    Filter("directive", "the comment is one the language's tools read: a directive after the comment marker, a "
                        "shebang on line 1, an encoding declaration on line 1 or 2", FACT, ("text",)),
```

with

```python
    Filter("directive", "the comment is one the language's tools read: a directive after the marker of the comment, "
                        "a shebang on line 1, an encoding declaration on line 1 or 2", FACT, ("text", "marker")),
```

In `xarch/modules/rules/application/logic/filters.py`, replace `_directive` with:

```python
def _directive(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    language, comment = profile.language, found.fact
    marker = comment.name or ""
    after = comment.text[len(marker):] if marker and comment.text.startswith(marker) else None
    words = "|".join(r"\s*".join(re.escape(part) for part in word.split(" ")) for word in language.directives)
    if after is not None and words and re.match(rf"\s*({words})", after):
        return True
    if comment.line == 1 and language.shebang and comment.text.startswith(language.shebang):
        return True
    return after is not None and comment.line <= 2 and bool(language.encoding) and bool(
        re.match(rf".*?{language.encoding}", after))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/adapters/test_fs_source_tree.py tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_filters.py tests/modules/rules/application/logic/test_reads.py tests/modules/rules/domain tests/architecture/test_language_seam.py`

Expected: PASS.

Run: `timeout 900 uv run pytest -q tests/modules/rules tests/modules/review tests/bootstrap/test_source_checks.py tests/bootstrap/test_bundled_guards.py`
Expected: PASS (the reader sets `marker="#"`, so every Python finding is today's).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules/domain/parsed.py xarch/modules/rules/adapters/fs_source_tree.py \
  xarch/modules/rules/application/logic/facts.py xarch/modules/rules/domain/vocabulary.py \
  xarch/modules/rules/application/logic/filters.py tests/modules/rules/adapters/test_fs_source_tree.py \
  tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py \
  tests/modules/rules/application/logic/world.py tests/modules/rules/application/logic/test_reads.py
git commit -F - <<'EOF'
The reader says of each comment the marker it opens with, which the comment fact carries; a directive and an encoding declaration are matched right after the comment's own marker, so a comment of no marker is none, and brace's two directives are read after a line or a block marker alike

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: `no-comments` keeps doc comments, and needs `comment.doc`

**Files:**
- Modify: `xarch/modules/rules/domain/vocabulary.py` (FIELDS `doc` after `unreadable`; Kind comment; Filter `doc`
  after `directive`)
- Modify: `xarch/modules/rules/application/logic/filters.py:200-209` (`_FACT`)
- Modify: `xarch/modules/rules/application/logic/facts.py:28,85,169-170`
- Modify: `xarch/modules/rules/application/logic/expansion.py:206-213` (`_no_comments`)
- Modify: `xarch/modules/spec/domain/key_table.py:222` (`NEEDS`)
- Modify: `xarch/architectures/presets/format/keys.yaml:820-824` (`guards.no-comments`)
- Test: `tests/modules/rules/application/logic/test_comments.py` (rows added)
- Test: `tests/modules/rules/application/logic/test_facts.py` (one test appended)
- Test: `tests/modules/rules/application/logic/world.py` (a file `NOTES`), `test_filters.py` (a row `doc`)
- Test: `tests/modules/rules/application/logic/test_reads.py:18-19` (`TRAITS`)
- Test: `tests/modules/rules/domain/test_rule.py:191-196` (the filter list), a needs test
- Test: `tests/modules/spec/application/logic/test_profile_needs.py` (one test appended)

**Interfaces:**
- Consumes: `Comment.doc` and `Comment.marker` (Task 2); `FACTS["comment.doc"]` (Task 1).
- Produces: the trait `doc` on a `comment` fact; `FIELDS["doc"]`; the comment kind's fields
  `("line", "text", "marker", "doc")` with `field_needs={"doc": ("comment.doc",)}`; the filter `doc`;
  `NEEDS["guards.no-comments"] == ("comment", "comment.doc")`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/rules/application/logic/test_comments.py`:

Add as the last row of `test_allowed`'s list:

```python
    pytest.param(Comment(5, "a doc", doc=True), True, id="a doc comment with no marker stays"),
```

Add as the last row of `test_allowed_under_a_language_of_line_and_block_comments`'s list:

```python
    pytest.param(Comment(5, "/** a doc */", marker="/**", doc=True), True, id="a doc comment stays"),
```

Add as the last row of `test_allowed_under_a_language_of_two_line_markers`'s list:

```python
    pytest.param(Comment(5, "/// a doc", marker="///", doc=True), True,
                 id="a doc comment that runs to the end of its line stays"),
```

In `tests/modules/rules/application/logic/test_facts.py`, after
`test_a_comment_carries_the_marker_it_opens_with_as_its_name`, add:

```python
def test_a_doc_comment_carries_the_doc_trait():
    read = facts_of([source("modules/docs/domain/a.py", comments=(Comment(2, "/** a doc */", marker="/**", doc=True),))],
                    [], PROFILE, "app").files[0]
    assert read.facts["comment"] == (Fact("comment", 2, name="/**", traits=frozenset({"doc"}), text="/** a doc */"),)
```

In `tests/modules/rules/application/logic/world.py`:

In the module docstring's table, after the line
`    app/modules/docs/domain/errors.py         a file of exceptions only` add

```
    app/modules/docs/domain/notes.py          comments of several forms, the first a doc comment
```

After `ERRORS = "app/modules/docs/domain/errors.py"` add `NOTES = "app/modules/docs/domain/notes.py"`, and as the last
item of `APP` (after the `errors.py` source) add:

```python
    source("modules/docs/domain/notes.py",
           comments=(Comment(1, "/** a doc */", marker="/**", doc=True), Comment(2, "// a note", marker="//"))),
```

(so the list ends `..., source("modules/docs/domain/errors.py", classes=(Class(1, "DocMissing", exception=True),)),`
then the new item, then `]`.)

In `tests/modules/rules/application/logic/test_filters.py`, add `NOTES,` to the `world` import list right after
`NARROWED,`, and right after the row `pytest.param("directive", DOMAIN, "comment", [13], PROFILE, None, id="directive"),`
add:

```python
    pytest.param("doc", NOTES, "comment", [1], PROFILE, None, id="doc"),
```

In `tests/modules/rules/application/logic/test_reads.py`, replace `TRAITS` with:

```python
TRAITS = ("relative", "standard", "on-own-object", "top-level", "forwards", "exception", "record", "interface",
          "immutable", "receiver", "annotated-callable", "no-statements", "exceptions-only", "unreadable", "doc")
```

In `tests/modules/rules/domain/test_rule.py`, in the expected text of the row
`id="..."` that starts `["keep: no filter is named 'sunny': write one of ...`, replace

```python
                  "directive, no-statements, exceptions-only, reported-at-import, names-restricted, of-kind, target-placed, "
```

with

```python
                  "directive, doc, no-statements, exceptions-only, reported-at-import, names-restricted, of-kind, "
                  "target-placed, "
```

and after `test_a_filter_about_the_package_file_needs_the_language_to_have_one_unless_it_is_negated` add:

```python
def test_a_check_of_comments_needs_comment_doc_only_when_it_reads_whether_one_is_a_doc_comment():
    assert made(facts=("comment",), targets=EXISTING, exempt=c("directive", "doc"), sayings=say()).needs == (
        "comment", "comment.doc")
    assert made(facts=("comment",), targets=EXISTING, exempt=c("directive"), sayings=say()).needs == ("comment",)
```

In `tests/modules/spec/application/logic/test_profile_needs.py`, append:

```python
def test_no_comments_is_refused_under_a_language_that_does_not_say_which_comments_are_doc_comments():
    commenting = replace(TOY, checked=replace(TOY.checked, supplies=(*TOY.checked.supplies, Supply("comment", EXACT))))
    document = layered(language="toy", guards={"no-comments": {}})
    assert problems(document, languages={"toy": commenting}) == [refusal("guards.no-comments", "comment.doc")]
    both = replace(TOY, checked=replace(TOY.checked, supplies=(*commenting.checked.supplies,
                                                                Supply("comment.doc", EXACT))))
    assert parsed(document, languages={"toy": both}).approximate == ()
    assert sorted(key.address for key in KEYS if "comment.doc" in key.needs) == ["guards.no-comments"]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_filters.py tests/modules/rules/application/logic/test_reads.py tests/modules/rules/domain/test_rule.py tests/modules/spec/application/logic/test_profile_needs.py`

Expected: FAIL — the three doc rows report the comment; the doc trait test sees `traits=frozenset()`;
`test_filters.py` fails with `ValueError: no filter is named 'doc'`; `test_rule.py` fails on the listed filters and
`read`/`except: no filter is named 'doc'`; `test_profile_needs.py` finds no refusal.

- [ ] **Step 3: The trait, the field, the filter, the rule, the needs, the key's text**

In `xarch/modules/rules/application/logic/facts.py`, after `_FORWARDS = frozenset({"forwards"})` add
`_DOC = frozenset({"doc"})`; replace the docstring line

```
    comment             each comment, text as written, name the marker it opens with
```

with

```
    comment             each comment, text as written, name the marker it opens with; doc when it is a doc comment
```

and replace

```python
            return tuple(Fact("comment", c.line, name=c.marker or None, text=c.text) for c in file.comments)
```

with

```python
            return tuple(Fact("comment", c.line, name=c.marker or None, traits=_DOC if c.doc else frozenset(),
                              text=c.text) for c in file.comments)
```

In `xarch/modules/rules/domain/vocabulary.py`:

After `    "unreadable": "whether a file could not be read as text at all",` add

```python
    "doc": "whether a comment is a doc comment",
```

Replace

```python
    Kind("comment", "each comment, its text as written", ("line", "text", "marker"), needs=("comment",)),
```

with

```python
    Kind("comment", "each comment, its text as written", ("line", "text", "marker", "doc"), needs=("comment",),
         field_needs={"doc": ("comment.doc",)}),
```

Right after the `Filter("directive", ...)` entry add:

```python
    Filter("doc", "the comment is a doc comment: one the language keeps its documentation in", FACT, ("doc",)),
```

In `xarch/modules/rules/application/logic/filters.py`, in `_FACT`, replace

```python
    **{name: _trait(name) for name in ("top-level", "forwards", "exception", "record", "interface", "immutable",
                                       "receiver", "annotated-callable", "no-statements", "exceptions-only",
                                       "unreadable")},
```

with

```python
    **{name: _trait(name) for name in ("top-level", "forwards", "exception", "record", "interface", "immutable",
                                       "receiver", "annotated-callable", "no-statements", "exceptions-only",
                                       "unreadable", "doc")},
```

In `xarch/modules/rules/application/logic/expansion.py`, replace `_no_comments` with:

```python
def _no_comments(profile: Profile) -> tuple[Rule, ...]:
    """No comment, in the app or its tests, but doc comments and those the language's tools read: its directives, a
    shebang on line 1, an encoding declaration on line 1 or 2."""
    if not profile.no_comments:
        return ()
    return (Rule("no-comments", Scope(ALL), ("comment",), MAY_NOT, EXISTING,
                 (Saying("a comment (no-comments)", "say it in a docstring or a name, and delete the comment"),),
                 exempt=_all("directive", "doc"), key="guards.no-comments"),)
```

In `xarch/modules/spec/domain/key_table.py`, replace `    "guards.no-comments": ("comment",),` with
`    "guards.no-comments": ("comment", "comment.doc"),`.

In `xarch/architectures/presets/format/keys.yaml`, replace

```yaml
  guards.no-comments:
    meaning: no `%comment%` comments in the app or its tests
    accepts: >-
      {}: no `%comment%` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do
      %directives%, a shebang and an encoding line
```

with

```yaml
  guards.no-comments:
    meaning: no `%comment%` comments in the app or its tests
    accepts: >-
      {}: no comment of the language in the app or its tests, `%comment%` or any other form, whole-line or trailing;
      docstrings and doc comments stay, and so do %directives%, a shebang and an encoding line
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py tests/modules/rules/application/logic/test_filters.py tests/modules/rules/application/logic/test_reads.py tests/modules/rules/domain tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/logic/test_key_catalogue.py tests/modules/spec/application/logic/test_profile_keys.py`

Expected: PASS.

Run: `timeout 900 uv run pytest -q tests/bootstrap/test_needs_agree.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_source_checks.py tests/architecture/test_self_check.py tests/architecture/test_language_seam.py tests/modules/rules/application`
Expected: PASS (spec's `NEEDS` and the expanded rule agree on `comment.doc`; xarch's own `no-comments` finds none).

- [ ] **Step 5: Commit**

```bash
git add xarch/modules/rules/domain/vocabulary.py xarch/modules/rules/application/logic/filters.py \
  xarch/modules/rules/application/logic/facts.py xarch/modules/rules/application/logic/expansion.py \
  xarch/modules/spec/domain/key_table.py xarch/architectures/presets/format/keys.yaml \
  tests/modules/rules/application/logic/test_comments.py tests/modules/rules/application/logic/test_facts.py \
  tests/modules/rules/application/logic/world.py tests/modules/rules/application/logic/test_filters.py \
  tests/modules/rules/application/logic/test_reads.py tests/modules/rules/domain/test_rule.py \
  tests/modules/spec/application/logic/test_profile_needs.py
git commit -F - <<'EOF'
no-comments keeps doc comments, read by a new filter doc on the comment's doc trait, and so needs comment.doc beside comment, in spec's table of keys as in the rule; a language whose reader does not say which comments are doc comments refuses it with the needs text

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `README.md:151-152` (language paragraph), `README.md:292` (the `no-comments` row)
- Modify: `CHANGELOG.md` (`## [Unreleased]`: first entry of `### Added`, first entry of `### Changed`)
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-3-8/regenerate_docs.py`
- Not touched: `docs/examples/**` — checked: `docs/examples/profile_values/language.py` is a simplified illustration
  with no comment field, `docs/examples/modules/rules/adapters/fs_source_tree.py` holds no `_comments`, and no test or
  generator holds them to the code.

**Interfaces:**
- Consumes: the behaviour of Tasks 1-3.
- Produces: nothing.

- [ ] **Step 1: README**

In `README.md`, replace the two lines

```
annotation gives none (`unannotated: nothing`), the comment marker and the comments its tools read, the shebang, the
encoding declaration, the keywords of the statements that branch and of the expressions that choose between values
```

with

```
annotation gives none (`unannotated: nothing`), the forms a comment is written in (`comments`, a list of `line`,
`block` and `doc` forms, `[{line: "#"}]` for Python, a doc comment being one `no-comments` keeps) and the comments
its tools read after the marker of any form, the shebang, the encoding declaration, the keywords of the statements
that branch and of the expressions that choose between values
```

and replace the row

```
| `no-comments` | a `#` comment in the app or its tests | `guards.no-comments` |
```

with

```
| `no-comments` | a comment of the language in the app or its tests (`#` for Python), but a doc comment and those its tools read | `guards.no-comments` |
```

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: PASS.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]`, `### Added`, insert as the first entry (one blank line after the heading,
one after the entry):

```markdown
- The fact `comment.doc`, whether a comment is a doc comment, which `guards.no-comments` needs beside `comment`. The
  reader says of each comment the marker it opens with and whether it is a doc comment (`Comment.marker` and
  `Comment.doc`), and a check of your own reads the doc ones with the filter `doc`. Python supplies it: no Python
  comment is a doc comment.
```

Under `### Changed`, insert as the first entry:

```markdown
- A language's data file says how its comments are written as a list of forms: `comment` became `comments`, each
  form `{line: <marker>}`, `{block: [<open>, <close>]}` or `{doc: [<open>, <close>]}` (a doc form's closing may be
  `""`, the end of its line; `[{line: "#"}]` for Python); left out, the language has none. `%comment%` is the first
  line form's marker, else the first block form's opening. A directive and an encoding declaration are matched after
  the marker of the comment, whatever its form, and `no-comments` keeps doc comments. The old key is an unknown key.
  Refused: `comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}` and
  `comments: needs one form at least`. No finding of a Python app changes.
```

- [ ] **Step 3: Regenerate the golden docs and confirm no diff**

Create `/tmp/xarch-3-8/regenerate_docs.py` (never committed):

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
mkdir -p /tmp/xarch-3-8
uv run python -I /tmp/xarch-3-8/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
sed -n 180p docs/xarch/testing.md
```

Expected: three `written` lines, an empty `git diff`, and line 180 reading
``- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives (`# type: ignore`, `# noqa`, `# pragma:`) stay.``
If the diff is not empty, stop and report it with the diff (`git checkout -- docs/cli docs/web docs/xarch` restores the
files). The docs must not move.

- [ ] **Step 4: Run the gates**

Run the suite in the background with a recorded PID, the rest in the foreground, then read the log:

```bash
timeout 1800 uv run pytest -q > /tmp/xarch-3-8/pytest.log 2>&1 & echo $! > /tmp/xarch-3-8/pytest.pid
uv run xarch check
uv run xarch check --strict
uv run ruff check
uv run xarch profile check architecture.yaml
```

When the background run ends: `tail -5 /tmp/xarch-3-8/pytest.log`.

Expected: the suite passes (corpora and golden-doc tests of `tests/bootstrap/` included), both checks report no
violation, ruff reports nothing, the profile check loads. `git status --short` shows no change under
`tests/bootstrap/corpora/` and nothing under `.claude/` staged; `git diff main -- xarch/architectures/presets/language/python.yaml`
shows only the header lines, `comments: [{line: "#"}]` and `comment.doc: exact`.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'EOF'
The README's language paragraph and no-comments row and the CHANGELOG say comments, a list of line, block and doc forms, with the two refusal texts, that a directive is matched after the marker of any form, and the fact comment.doc that no-comments needs to keep doc comments; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

## Self-review against the spec

**Spec coverage.**
- 2.1 `comment` an unknown key, `comments` optional, the three forms, the two refusals once for the key, no profile
  refusal, docstring and header, `python.yaml` lines: Task 1 (Steps 1, 5).
- 2.2 `CommentForm`, `comments` field, `comment` property (first line, else first block, never doc): Task 1.
- 2.3 `Comment.marker`/`.doc` with defaults after the existing fields, `text` as written, docstring: Task 2; reader
  `marker="#"`, `doc=False` (the seam exempts the adapter): Task 2; `FACTS` `comment` text and `comment.doc` after
  `file.package`: Task 1; the fact carries marker (Task 2) and doc (Task 3); kind meaning "each comment, its text as
  written": Task 2; the kind carries `doc` needing `comment.doc`: Task 3.
- 2.4 directives after the comment's own marker, a comment not starting with its marker no directive, shebang
  unchanged, filter meaning: Task 2; `no-comments` exempting doc comments, its docstring, `Rule.needs`, `NEEDS`, filter
  `doc`: Task 3; `%comment%` readers (`written.py`, `docs_template.py`, `explain.py`) read the property, no code
  change: Task 1 (tests 18-20 of the spec); `FileType.comment` untouched.
- 2.5 `keys.yaml` text: Task 3.
- 2.6 unchanged things: Task 4 (golden diff, gates); masking needs no change.
- 3 test-only files and their headers: Task 1 Step 5; builders and every `CheckedLanguage(comment=...)`: Task 1 Steps
  2, 6; hand-built `Comment`s that need a directive matched: `world.py` (Task 2), `test_comments.py` (Task 2).
- 4 tests: 1-8 Task 1 Step 1; 9 Task 2; 10-14 Tasks 2-3 (`test_comments.py`); 15 Task 3 (`test_rule.py`); 16 Task 3,
  17 Task 1 (`test_profile_needs.py`; `test_key_catalogue.py` needs no new test: the catalogue reads the key texts and
  `test_a_key_needs_only_facts_of_the_vocabulary_of_facts` holds `comment.doc` within `FACTS`); 18 Task 1
  (`test_written.py`); 19 Task 1 (`test_explain.py`); 20 Task 1 (`test_docs_template.py`); 21 Task 1 (seam); 22-24 run
  in Tasks 3, 4.
- 5 docs: Task 4. `docs/examples/**`: checked, no change.

**Placeholder scan.** Every code step shows its code; no TBD, no "similar to". The probes of the brace docs line, of
`words` for the three languages and of the toy refusal for `guards.no-comments` were dry-run against today's code
and give the shapes the tests expect before the change.

**Type consistency.** `CommentForm(kind, opening, closing)`, `LINE`/`BLOCK` (profile_values) and `DOC` (language_file), `CheckedLanguage.comments` and the
property `comment`, `language_file.COMMENTS`/`NO_COMMENTS`, `forms_of`, `Comment(..., marker, doc)`,
`Fact.name` as the marker, `FIELDS["marker"]`/`FIELDS["doc"]`, filter `doc`, `_DOC`, `NEEDS["guards.no-comments"]`.
Names match across tasks.

**Review Focus.** Each of the five lines has its test in the task that owns the code (named in the section).
<!-- task-pipeline: validated -->
