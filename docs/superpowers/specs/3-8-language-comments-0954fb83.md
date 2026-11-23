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
