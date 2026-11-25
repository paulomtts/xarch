# 3.4 spec: a named list of `never` may include another

Card: 8bd5284c (subtask of 3c7754c4). Release step 7a of the merged order (`0.3.0-cohesion-review-3.md`, section 3,
line 265). Blocked by 305c9f45 (3.3, the one outside-name parser), which is on this branch.

Owning note: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/list-reuse-design.md` ("the note"). Review 3:
`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md` ("review 3").

## Inherited constraints

- The note, rulings (lines 10-16): a named list of `never` may include another in 0.3.0; the block is `never:` and a
  part names one list with `uses: {never: <list>}`; one wording for every refusal, no compatibility window; R6: the
  bundled profiles write `published: [pure, typing.Any]` in this step (also review 3, line 447).
- The note, 1 (lines 34-52): an entry is a name, as today, or the name of another list. A list reads as its entries
  with each included list put in its place, in order, however deep. A list may include several, and be included by
  several. Block order does not matter. A part still names one list; `uses: {never: [pure, ambient]}` is refused.
- The note, 2 (lines 54-78): an entry names a list exactly when it equals the name of a list of `never`; every other
  entry goes to the outside-name parser as today. Two collision refusals: a list named like a standard module
  (`standard_names`), and a list named like a package the profile names (a part's libraries, or `reserved`). The gap
  that is left is G1 (review 3, line 407), named, not fixed. No prefix spelling (`never.pure`) for entries.
- The note, 3 (lines 80-90): a list including itself however far is refused; a name reaching a list twice (written
  twice, or written once and included once) is refused; including one list twice is refused; a list of only includes
  is fine; `never` needs one list and each list one entry, as today.
- The note, 4 (lines 92-102): findings name the part's key and never a list; `where` and its JSON `never_uses` hold
  the expanded names in order; the docs print the expanded names in order; a problem of an entry names the list it is
  written in, and a problem of an included list is said once, under its own name; `profile explain never` says how an
  entry naming a list reads and gives the two refusals.
- The note, 5 (lines 104-115): the refusal texts (given exactly in Behavior below). Each keeps a plain description and
  no "in 0.3.0"; none is a retired key.
- The note, 6 (lines 117-136): `Architecture` unchanged (a part's field holds the expanded names); `looseness.py`
  unchanged; `keys.yaml` entry `never` gets the text and an example with an include; README one sentence and the
  example; CHANGELOG "Added: a list of never may include another". `pure` and `ambient` are left as written.
- The note, dodges (lines 138-146), each a thing this step must not do: guess a list from a bare word; accept a
  colliding name "since nothing collides today"; let a part name several lists; expand includes in rules, docs or
  `where`; print the list a name came through in findings; reorder `pure` or `ambient` so the golden docs move.
- Review 3, C11 (lines 183-189): the saving is 5 lines per bundled profile; nothing else is included.
- Review 3, O20 (line 244): this step reads `standard_names` as it is today (the interpreter's for Python); step 8a
  changes its source, not its value, so these tests pass before and after 8a.
- Review 3, section 5 clash 23 (lines 402-403) and G1 (lines 407-409): the collision is refused for standard modules
  and named packages; a package named nowhere is the gap.
- Review 3, O4, O5, O8 (lines 228-232): README and CHANGELOG lines under `[Unreleased]`; the golden docs
  `docs/{cli,web,xarch}/testing.md` regenerate with no diff ("List reuse (7a) expects none").
- Project rules (card): no comments in xarch's code; never `ruff --fix`; tests written first; examples simple, with
  absolute `app.` imports; recorded corpora (`tests/bootstrap/corpora/`) not edited; Python only in the reader adapter
  and the data files under `xarch/architectures/presets/`; `.claude/` out of commits; nothing pushed.

### Where the code differs from the note

- The note writes `imports.libraries`; that grouping lands at release step 13 (review 3, line 271). Today the key is
  `parts.<part>.libraries` (`key_table.py:81`). The package-collision refusal names the key as it exists on this
  branch: `(parts.<part>.libraries)`. Step 13 rewrites it with every other `libraries` text.
- The note's `_forbidden_lists` / `forbidden_names` are now `_never_lists` (`profile_parsing.py:448-461`) and
  `never_names` (`profile_checks.py:617-647`).
- `reserved` accepts only names in `standard_names` (`profile_checks.py:586`), so a list named like a reserved module
  is always named like a standard module too: it gets the standard-module refusal, and only that one. The
  "named package" refusal is therefore met through a part's `libraries` in practice.

## Behavior

### Telling an entry that names a list

1. Every list name of the block is known before any entry is read. A list name is a key of `never` that passes
   today's list-name check (`ck.PART_NAME`); a key refused by that check is no list, and an entry equal to it is read
   as a name, as today.
2. An entry is an include when it is a string exactly equal to a list name of the block (case-sensitive, no
   trimming). Every other entry goes to the outside-name parser unchanged, with today's texts (a method, a builtin,
   an outside name, a package, the bare-builtin hint, "listed twice"). A bare word that is not a list name is a
   package entry as today, never a dangling list.
3. A list name refused by a collision refusal (rule 5 or 6) is still a list name for rule 2, so entries equal to it
   raise no second problem.

### Expansion

4. A list's expansion is its entries in written order, each include replaced by the expansion of the included list,
   however deep. An included list may be written above or below. The expansion is computed once, at load; a part's
   `uses: {never: <list>}` takes that list's expansion as its `uses_never` field. Nothing downstream (rules, docs,
   `where`, its JSON `never_uses`, the comparison, `looseness.py`) learns that includes exist, and no finding, `where`
   line or doc line names a list a name came through.
5. With `published: [pure, typing.Any]`, `published`'s expansion is `pure`'s names in `pure`'s order followed by
   `typing.Any`: the same tuple, in the same order, as the 34 names written out today.

### Refusals (exact texts)

Each problem is at the address of the list it is about. One list may receive several of rules 6-11, in this order:
its name problem (at most one, rule 6 or 7), then its entry problems in entry order (today's texts, rule 2), then its
include problems (rules 8-11) in entry order.

6. A list name in the language's `standard_names`:
   `never.socket: a list may not take the name of a standard module, since an entry socket would name the list: rename it`
   (`socket` stands for the list's name, in both places).
7. A list name, not a standard module, that a part's `libraries` lists (a valid package entry of it; `everything`
   lists none) or that `reserved` lists:
   `never.sqlmodel: a list may not take the name of a package this profile names (parts.service.libraries): rename it`.
   The key in parentheses is the first place naming it: the parts in the order the file writes them, then
   `reserved`. One problem per list, however many places name it.
8. A list that names itself as an entry: `never.a: includes itself`.
9. A list that reaches itself through other lists: `never.a: includes itself, through never.b: drop one of the two`
   when the cycle is two lists. For a cycle of more lists, the lists after `a` along the cycle, in order, joined by
   `, `: `never.a: includes itself, through never.b, never.c: drop one of the includes`. A cycle is reported once,
   under the list of the cycle written first in the block; the other lists of the cycle, and lists that include a list
   of the cycle, get no problem for it (and no expansion, as a list already reported today is `None`).
10. A list that reaches one list twice, whether written twice (`both: [pure, pure]`) or once directly and once through
    another include (`both: [pure, mid]`, `mid: [pure]`): `never.both: includes never.pure twice`. Its names are not
    then also reported as repeats.
11. A name that reaches a list twice through what it includes, compared on the parsed steps as "listed twice" is
    today:
    - written in the list and also in a list it includes (directly or through others):
      `never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it here`, where
      the quoted text is the entry as written in the list (`published`) and `never.pure` is the list whose own entries
      hold it;
    - reached through two included lists, written in neither of them by the list itself (`both: [pure, ambient]`
      where each writes `os.environ`): `never.both: 'os.environ' is listed in never.pure and in never.ambient, which
      never.both includes: drop it from one` (the two lists whose own entries hold it, in the order the expansion
      reaches them). This text is not in the note, which words only the first case; it follows the note's form.
    - written twice in the same list: today's `never.pure: 'os.environ' is listed twice`, unchanged.
    The expansion keeps a name's first arrival and drops the later one, so a repeat is reported only at the lowest
    list where the two arrivals meet, and never again under each list that includes that one.
12. A part naming a list of lists keeps today's refusal, with a tail:
    `parts.domain.uses.never: names one list under never: write the name of a list, such as pure; a list may include
    others`. Every other `uses.never` text is unchanged.
13. A problem inside an included list (a bad entry, a name listed twice there, a non-list value, an empty list) is said
    once, under that list's own address. A list that includes a list whose value is no list or is empty gets no
    problem for it; its expansion skips that list's names (the profile is refused anyway).
14. Unchanged: `never` that is no mapping is its one problem; a list that is no list or is empty is refused as today;
    a list of only includes (`both: [pure, ambient]` with disjoint lists) is accepted.

### Order of the problems

15. Every problem of the block `never`, new ones included, is reported where `never`'s problems are reported today in
    the problem list (after `based_on`, before the parts), lists in block order. The problems of `reserved` and of
    each part's `libraries` are reported once, at their own place, as today; reading their names early for rules 6-7
    must not report them twice or move them.

### The format text, the bundled profiles, README, CHANGELOG, golden docs

16. `xarch/architectures/presets/format/keys.yaml`, entry `never`: `accepts` gains, in the file's style: an entry that
    is exactly the name of another list of `never` includes that list's names in its place, in order, however deep,
    and the list may be written below; a list may not include itself, nor reach a name or a list twice; a list may not
    take the name of a standard module, nor of a package the profile names in a part's `libraries` or in `reserved`,
    since an entry of that name would name the list. `meaning` unchanged. The example becomes:

    ```yaml
    never:
      pure: [time.time, socket]
      published: [pure, typing.Any]
      ambient: [pathlib.Path.cwd, .absolute()]
    <<part>>
        uses: {never: published}
    ```

    `xarch profile explain never` prints the new text and example (it reads this entry).
17. `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`: the written-out `published`
    (6 lines each) becomes the one line `  published: [pure, typing.Any]`. `pure`, `ambient`, `environment` and every
    other line are unchanged. `tests/bootstrap/corpora/stress.yaml` is not touched.
18. `profile_parsing.py`'s module docstring line for `never` says an entry may be the name of another list:
    `never: {<list>: [<name> | <list>, ...]}` and its note "named lists of what a part never uses; an entry naming
    another list includes it".
19. README: the shape line `never:    {<list>: [<dotted name> | .<method>(), ...]}` gains `| <list>` as an entry form
    (keep the block's column alignment), and one sentence near the block: an entry of a `never` list that is the name
    of another list includes it, such as `published: [pure, typing.Any]`, and a list may not take the name of a
    standard module or of a package the profile names.
20. CHANGELOG, under `## [Unreleased]`, a new `### Added` section above `### Changed`: one entry, "A list of `never`
    may include another" with the example `published: [pure, typing.Any]`, that the bundled profiles now write it with
    no part's names changed, and the new refusal texts of rules 6-12 (short forms, as the existing entries quote theirs).
21. The golden docs `docs/{cli,web,xarch}/testing.md` regenerate with no diff (O8). The recorded findings and corpora do
    not change.

## Shape (what the planner needs to know, not how to write it)

- `_never_lists` (`profile_parsing.py:448-461`) becomes two passes plus an expansion: (1) the list names; (2) per
  list, its entries split into includes (rule 2) and names, the names handed to `ck.never_names` exactly as today
  (so its texts and its "listed twice" stay); (3) the expansion with rules 8-11. Its return type stays
  `dict[str, tuple[tuple[str, ...], ...] | None] | None`, now holding expansions, so `_never_refs`
  (`profile_parsing.py:464-487`) and `Architecture.uses_never` are unchanged in type.
- `never_names` must not see an include: an include passed to it would parse as a package. The repeat check across
  includes (rule 11) runs in the expansion, on steps, after `never_names` has removed same-list repeats. For rule 11
  the expansion needs, per list, each name's steps with its written text and the list whose own entries hold it; keep
  that inside the parsing module, not in `Architecture`.
- The collision refusals read `language.standard_names`, the valid package names of every part's `libraries`, and the
  names `reserved` accepts. `parse_profile` (`profile_parsing.py:169-178`) parses `never` before `reserved` and
  `libraries`; rule 15 fixes where the problems appear, so either read those names silently first (a throwaway
  problems list) or parse `never` later and insert its problems at today's place. The planner checks
  `test_profile_parsing.py` and the other parsing tests for pinned problem orders before choosing.
- No Python in the parsing code (`tests/architecture/test_language_seam.py`, `test_agnostic.py`): "a standard
  module" is read from the language, never from `sys`.
- No new key, no key-table change, no retired entry.

## Out of scope

- Rewriting `ambient` to include `environment`, or `pure` to include anything (the note, 6, line 134-136; card).
- A fix for gap G1 (a list named like a package the profile names nowhere and the language does not ship).
- A refusal for a list named like a builtin (`print`): not in the note; an entry `print` equal to such a list name is
  an include, as rule 2 says. Same family as G1; not addressed here.
- The `imports` grouping of parts and its key `imports.libraries` (step 13); the source of `standard_names` (step 8a).
- Any change to rules, docs templates, `where`, looseness or the comparison: they read expanded names.
- Sibling cards of story 3c7754c4 and later release steps (8 onward).

## Tests (written first)

Profile tier, `tests/modules/spec/application/logic/test_never_use.py` (`parse_profile` on documents from
`tests/modules/spec/profiles.py`, `covered`/`with_list`/`service_uses`; this is the tier where a refusal carries its
address and the parsed `uses_never` is visible):

- T1 An include in order: `never: {pure: [time.time, socket], published: [pure, typing.Any]}`, service
  `uses: {never: published}`: service's `uses_never` is `(("time", "time"), ("socket",), ("typing", "Any"))`.
- T2 Include in the middle: `published: [typing.Any, pure, os.getenv]` expands to `typing.Any`, pure's names,
  `os.getenv`, in that order.
- T3 A chain of three: `a: [b, x.one]`, `b: [c, x.two]`, `c: [x.three]`: `a` expands to `x.three, x.two, x.one`.
- T4 A list written below the one that includes it: `published` above `pure` gives T1's tuple.
- T5 A list of only includes, disjoint: `both: [pure, ambient]` with LISTS gives `socket, os.getcwd`; no problem.
- T6 The same part's `uses_never` whether `published` is written `[pure, typing.Any]` or its names written out (a
  parse of both documents, field compared).
- T7 Standard-module collision under `PYTHON`: a list `socket` gives exactly rule 6's text; another list's entry
  `socket` raises no further problem.
- T8 Standard-module collision is read from the language: under `replace(BRACE, standard_names=frozenset({"fs"}))`
  a list `fs` gives rule 6's text with `fs`; the same document under `PYTHON` gives none (no Python in the check).
- T9 Named-package collision: service `libraries: [sqlmodel]`, list `sqlmodel`: rule 7's text with
  `(parts.service.libraries)`; with two parts listing it, one problem naming the first part in file order.
- T10 A list named like a reserved module (`reserved: {ast: ...}`, list `ast`): rule 6's text only, one problem.
- T11 `libraries: everything` on a part names no package: a list named `sqlmodel` is accepted when nothing else names
  it.
- T12 Includes itself directly: `a: [a, x.one]`: rule 8's text.
- T13 Includes itself through another: `a: [b]`, `b: [a]`: one problem, rule 9's two-list text under `never.a` (the
  list written first); none under `never.b`. A three-list cycle gives the longer text under its first list.
- T14 A list that includes a cycle's list (`top: [a]`, `a: [b]`, `b: [a]`): only the cycle's one problem.
- T15 A name written in a list and in a list it includes: `pure: [os.environ]`, `published: [pure, os.environ]`:
  rule 11's first text; also when the name is written before the include, and through a chain (`top: [mid,
  os.environ]`, `mid: [pure]`) naming `never.pure`.
- T16 A name reached through two includes: rule 11's second text.
- T17 Including a list twice, directly (`both: [pure, pure]`) and through another (`both: [pure, mid]`, `mid:
  [pure]`): rule 10's text, and no repeat-name problem beside it.
- T18 A repeat reported once: `mid: [pure, os.environ]` with `pure` holding `os.environ`, `top: [mid]`: one problem,
  under `never.mid`; none under `never.top`.
- T19 A bad entry in an included list (`pure: [datetime..now]`, `published: [pure]`) is reported once, under
  `never.pure`; an included list whose value is `[]` or no list gives only its own problem.
- T20 A part naming a list of lists: the `ONE_LIST` constant changes to rule 12's text (with "; a list may include
  others"); the existing case still passes with it.
- T21 A bare word that is no list name stays a package: `pure: [socket]` with no list `socket` gives
  `uses_never == (("socket",),)` (no guessing; dodge 1).
- T22 A key refused as a list name (`never: {"a b": [x.one], c: ["a b"]}`) is no list: `"a b"` in `c` is refused by
  the outside-name parser with today's text.
- T23 Problem order (rule 15): a document with a bad `never` entry, a bad `reserved` entry and a bad part `libraries`
  entry lists them in today's order, each once.

Bundled data tier, `tests/bootstrap/test_bundled_architectures.py` (the shipped profiles as loaded; this is where the
R6 rewrite is pinned):

- T24 For `cli`, `web` and xarch's own `architecture.yaml`, the part with `uses: {never: published}` has
  `uses_never` equal to `pure`'s expansion plus `("typing", "Any")`, 34 names, and each file writes `published:
  [pure, typing.Any]`.

Bootstrap tier, `tests/bootstrap/test_never_use.py` (the real check on a throwaway project, where findings are what a
user reads):

- T25 A contract file of the web profile using `typing.Any` and `datetime.datetime.now` gives the same findings under
  the bundled `web.yaml` as under a copy whose `published` line is replaced by the 34 names written out; each finding
  ends `(parts.contract.uses.never)` and names no list.

Explain tier, `tests/bootstrap/test_profile_explain.py` (the user-facing text of `keys.yaml`):

- T26 `xarch profile explain never` says an entry naming a list includes it, gives both collision refusals, and shows
  `published: [pure, typing.Any]`.

Format-data tier: T27 the key-catalogue tests (`test_key_catalogue.py`) still load `keys.yaml`; if a test parses each
example, the new example parses.

Docs tier: T28 `tests/bootstrap/test_docs.py` passes, the golden docs regenerate with no diff (the regenerate script of
`docs/superpowers/plans/1-1-corpora-the-two-40fa4c21.md`, Task 2 step 6), and `tests/architecture/test_readme.py`
passes with the README edit.

Seam tier: T29 `tests/architecture/test_language_seam.py` and `test_agnostic.py` pass unchanged.

## Review Focus (inputs the tests above do not all pin, for the planner)

- A list name with surrounding spaces or different case from an entry (`Pure` vs `pure`): an entry is an include only
  on exact equality; `Pure` is a package entry.
- A non-string list key (`1: [x.one]`) or a non-string entry: today's refusals, no include, no crash in the expansion.
- A part naming a list refused by a collision or a cycle: no extra `uses.never` problem beyond today's for a list
  already reported.
- `where` and its JSON for the contract part print the 34 names in order (already covered by the golden docs for the
  docs; a `where` check is worth adding where `where` is tested).
- A large or deep block (a chain of many lists): the expansion terminates and the cycle check does not recurse
  without bound.

## Gates

On this branch alone, the full suite green: `uv run pytest -q` (over two minutes: run it in the background with
`timeout`, read it at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never
`--fix`), `uv run xarch profile check architecture.yaml`. Regenerate the golden docs and confirm no diff.

---

# 3.4 spec: a named list of `never` may include another Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An entry of a `never` list that is exactly the name of another list of the block includes that list's names
in its place, in order, however deep. Includes that loop, repeat a list or repeat a name are refused, and so is a list
named like a package an entry would otherwise read as. The bundled profiles write `published: [pure, typing.Any]`, and
no part's names, finding, `where` line or doc line changes.

**Architecture:** A new pure module `xarch/modules/spec/application/logic/never_lists.py` reads the block. First it
takes the list names. Then it splits each list's entries into includes and names, and the names still go through
`ck.never_names`, which now gives one slot per item so a name keeps its written place. Last it expands the lists. It
finds loops without recursion (a reach set per list), expands the other lists bottom-up in order of reach size, and
says each repeat at the lowest list where its two arrivals meet. `parse_profile` calls it at today's place, handing it
the packages the profile names, which it reads silently first. Nothing downstream changes: a part's `uses_never` holds
the expanded names.

**Tech Stack:** Python 3.13, pytest, PyYAML, ruff (line length 140; the project keeps lines at 120), `uv run`.

**Spec:** `docs/superpowers/specs/3-4-spec-a-named-list-8bd5284c.md` (prepended above; read it whole before Task 1).

## Global Constraints

- No comments in xarch's code; docstrings only. Never `ruff --fix`. Keep every line at 120 characters or fewer.
- Tests are written first and run red before the code that makes them pass.
- Python is named only in the reader adapter and the data files under `xarch/architectures/presets/`. No string
  literal or docstring in `xarch/` may write `Python`, `builtins`, `typing`, `Protocol`, `importlib`, `__init__` or
  `.py` (`tests/architecture/test_language_seam.py`). "A standard module" is read from `language.standard_names`, never
  from `sys`.
- No string literal in `xarch/` may hold, as a whole word, a part or folder name of the bundled profiles (`module`,
  `modules`, `service`, `domain`, `contract`, `logic`, `kernel`, `adapters`, `platform`, `web`, `cli`, ...)
  (`tests/architecture/test_agnostic.py`; its `ALLOWED` stays empty).
- No new key, no key-table change, no retired entry. `Architecture`, `looseness.py`, rules, docs templates and `where`
  are unchanged.
- `tests/bootstrap/corpora/` is not edited. `pure`, `ambient` and `environment` are left exactly as written in the
  three profiles.
- The golden docs `docs/{cli,web,xarch}/testing.md` regenerate with no diff.
- README and CHANGELOG lines go under `[Unreleased]`.
- `.claude/` stays out of every commit; nothing is pushed.
- Run long suites with `timeout` and a recorded PID (`timeout 1200 uv run pytest -q`), never `pkill`/`killall`.

## Spec deviations (decided by the planner, with evidence)

1. **Rule 6's text says "a package of the <title> standard library", not "a standard module".** The spec's text is
   `never.socket: a list may not take the name of a standard module, since an entry socket would name the list:
   rename it`. `tests/architecture/test_agnostic.py` scans every string literal of `xarch/` for the bundled profiles'
   part and folder names, and its `concept_names()` holds `module` (the word of the repeating folder `<module>`). I
   ran it, and it lists `module` among the names. `ALLOWED` must stay empty. So the text becomes
   `never.socket: a list may not take the name of a package of the Python standard library, since an entry socket
   would name the list: rename it`, with `{language.checked.title}` for `Python`. That follows
   `reserved`'s own `is not in the {title} standard library` (`profile_checks.py:589`), and xarch calls a top-level
   import name a package everywhere (`_is_package`, `libraries`). The keys.yaml text, the README sentence and the
   CHANGELOG say "a package of the standard library" to match.
2. **`ck.never_names` returns one slot per item, `None` for a refused item.** The spec says the names are "handed to
   `ck.never_names` exactly as today". Its texts and its "listed twice" stay byte for byte, but the expansion needs
   each accepted name at its written place among the includes. Today's return, the accepted names only, loses that
   place. A second, tests-only function would be flagged by the `dead-code` guard (`tests_only: true` in
   `architecture.yaml`). So the one function changes its return. Its only callers are the parser and
   `tests/modules/spec/application/logic/test_profile_checks.py`, whose helper filters the slots back to today's shape.
3. **One loop problem per group of lists that reach each other.** Rule 9 says "a cycle is reported once, under the
   list of the cycle written first in the block". When several cycles share lists (`a: [b, c]`, `b: [a]`, `c: [a]`),
   they make one group. It is said once, at its first-written list, along the shortest way back to it, trying
   includes in written order (`never.a: includes itself, through never.b: drop one of the two`).
4. **A list that writes itself and also loops through others gets both texts, rule 8 first.** The spec does not order
   the two. A list with a loop has no expansion, so rules 10-11 never come with them.
5. **The repeat of a name reached through two includes quotes the first arrival's text.** Both included lists hold the
   same steps, so either text reads the same under Python.
6. **The `keys.yaml` example writes `published: [pure, json.dumps]`, not `[pure, typing.Any]`.**
   `tests/architecture/test_language_seam.py::test_no_data_file_of_the_format_names_the_language_of_the_data_file`
   refuses any word of the Python data file in `xarch/architectures/presets/format/*.yaml`, and `typing` is one of
   them, as a step of its `interface`. The planner ran it against the spec's example, and it failed with
   `[('keys.yaml', 'typing')]`. `json.dumps` is a name of no language's data file. The README, the CHANGELOG and the
   bundled profiles are not format data files, so they keep `typing.Any`.
7. **`tests/modules/spec/application/test_explain.py:211` changes.** It pins that the `never` example ends with
   `    uses: {never: pure}\n`. The new example ends with `    uses: {never: published}\n`, as rule 16 asks.

## Review Focus

1. A list name that differs from an entry only by case or by a surrounding space (`Pure`, `" pure"`). Only exact
   equality includes. `Pure` is a package entry, and `" pure"` is refused by the outside-name parser with today's text.
   Test: Task 2, Step 1 (`test_never_use.py`).
2. A non-string list key (`1: [x.one]`) or a non-string entry beside an include (`c: [pure, 3]`). Today's refusals
   apply, no include is read, and the expansion does not crash. Test: Task 2, Step 1.
3. A part naming a list that a loop or a collision refuses. Only the list's own problem is said, with no `uses.never`
   problem beside it. Test: Task 2, Step 1 (loop) and Task 3, Step 1 (collision).
4. A chain or a loop of 1,500 lists (more than the interpreter's recursion limit). The chain expands, and the loop is
   said once, with no `RecursionError`. Test: Task 2, Step 1.
5. `where` and its JSON for the contract part print pure's 33 names then `typing.Any`, in order, after the rewrite.
   Test: Task 4, Step 1 (`tests/bootstrap/test_where.py`).

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `xarch/modules/spec/application/logic/profile_checks.py` | `never_names` gives one slot per item | 1 |
| `tests/modules/spec/application/logic/test_profile_checks.py` | the slot test; `forbidding` filters slots | 1 |
| `xarch/modules/spec/application/logic/profile_parsing.py` | calls the new module; `ONE_LIST` tail; docstring; `_named_packages` | 1, 2, 3 |
| `xarch/modules/spec/application/logic/never_lists.py` (new) | the block read into expanded lists, with every include problem | 2, 3 |
| `tests/modules/spec/application/logic/test_never_use.py` | T1-T23 and Review Focus 1-4 | 2, 3 |
| `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml` | `published: [pure, typing.Any]` | 4 |
| `tests/bootstrap/project.py` | `PURE`, the 33 names of the bundled `pure` in order | 4 |
| `tests/bootstrap/test_bundled_architectures.py` | T24 | 4 |
| `tests/bootstrap/test_never_use.py` | T25 | 4 |
| `tests/bootstrap/test_where.py` | Review Focus 5 | 4 |
| `xarch/architectures/presets/format/keys.yaml` | entry `never`: accepts and example | 5 |
| `tests/bootstrap/test_profile_explain.py` | T26 | 5 |
| `README.md`, `CHANGELOG.md` | shape line, one sentence; `### Added` | 5 |

---

### Task 1: `never_names` gives one slot per item

**Files:**
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:617-647` (`never_names`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:458-460` (`_never_lists`, its one caller)
- Test: `tests/modules/spec/application/logic/test_profile_checks.py:16-19` (the `forbidding` helper) and a new test

**Interfaces:**
- Consumes: nothing new.
- Produces: `never_names(value: Any, where: str, problems: list[str], language: Language) ->
  tuple[tuple[str, ...] | None, ...] | None`. It gives one slot per item of `value`, in order: the item's steps when
  it is accepted, and `None` when it is refused (a bad name, a bare builtin, a special method, or listed twice). The
  whole result is `None` when `value` is no list or is empty, as today. Problems and their texts are unchanged.

- [ ] **Step 1: Write the failing test**

In `tests/modules/spec/application/logic/test_profile_checks.py`, replace the helper `forbidding` (lines 16-19) with:

```python
def forbidding(item: str) -> tuple[tuple[tuple[str, ...], ...] | None, list[str]]:
    """What a `never` list of the one item comes to: the names it bans, and every problem."""
    problems: list[str] = []
    read = never_names([item], "at", problems, PYTHON)
    return (None if read is None else tuple(steps for steps in read if steps is not None)), problems
```

and add, right after it:

```python
def test_each_item_of_a_never_list_keeps_its_place_and_a_refused_one_holds_none():
    problems: list[str] = []
    assert never_names(["socket", "pkg..x", "socket", ".absolute()"], "at", problems, PYTHON) == (
        ("socket",), None, None, ("", "absolute()"))
    assert problems == [f"at: 'pkg..x' {NOT_OUTSIDE}", "at: 'socket' is listed twice"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_checks.py`
Expected: FAIL in `test_each_item_of_a_never_list_keeps_its_place_and_a_refused_one_holds_none`. The left side is
`(('socket',), ('', 'absolute()'))`. Every other test passes.

- [ ] **Step 3: Write the minimal implementation**

In `xarch/modules/spec/application/logic/profile_checks.py`, replace the whole of `never_names` (lines 617-647) with:

```python
def never_names(value: Any, where: str, problems: list[str],
                language: Language) -> tuple[tuple[str, ...] | None, ...] | None:
    """The names a part may not use, one for each item in its place, None for an item refused: outside names,
    <package><member><name>, or packages alone, read by the language's patterns; a builtin is written in the language's
    namespace for them, <namespace><member><name>. A method called on anything is written `.<name>()` and kept as
    written, split at its dot: ("", "<name>()")."""
    member = language.checked.member
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of outside names, packages or methods, such as "
                        f"[{_such(language)}, <package>, .<name>()]")
        return None
    found: list[tuple[str, ...]] = []
    read: list[tuple[str, ...] | None] = []
    for item in value:
        count = len(problems)
        method = _method_name(item, language) if isinstance(item, str) else None
        steps = (("", f"{method}{CALLED}") if method is not None
                 else _outside(item, language, language.namespace) if isinstance(item, str) else None)
        if method is not None and language.checked.is_special(method):
            problems.append(f"{where}: {item!r} is a special method, which no code calls by name")
        elif method is None and isinstance(item, str) and item.startswith(".") and names.is_name(item[1:], language.names):
            problems.append(f"{where}: {item!r} is neither an outside name nor a method: write {item}() for a method "
                            "called on anything")
        elif steps is None:
            problems.append(f"{where}: {item!r} is not an outside name such as {_such(language)}, nor a package, nor a "
                            "method such as .<name>()")
        elif len(steps) == 1 and item in language.builtin_names:
            problems.append(f"{where}: {item!r} is a {language.checked.title} builtin, which a bare name does not ban: "
                            f"write {language.namespace}{member}{item}")
        elif steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(steps)
        read.append(steps if len(problems) == count else None)
    return tuple(read)
```

In `xarch/modules/spec/application/logic/profile_parsing.py`, inside `_never_lists`, replace the line

```python
            never_lists[name] = ck.never_names(names, f"never.{name}", problems, language)
```

with

```python
            read = ck.never_names(names, f"never.{name}", problems, language)
            never_lists[name] = None if read is None else tuple(steps for steps in read if steps is not None)
```

(Task 2 replaces `_never_lists` as a whole. This keeps the suite green in between.)

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_profile_checks.py tests/modules/spec/application/logic/test_never_use.py`
Expected: all pass.

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff check xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_profile_checks.py
git add xarch/modules/spec/application/logic/profile_checks.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_profile_checks.py
git commit -m "Reading a never list gives one slot per item in its place, None for an item refused, so a name keeps its written place among what else the list holds; every refusal text and the listed-twice check are as before

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: A list of `never` may include another, expanded at load, with the loop and repeat refusals

**Files:**
- Create: `xarch/modules/spec/application/logic/never_lists.py`
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py`: the docstring line 31, the imports (line 75),
  the call at line 169, delete `_never_lists` (lines 448-461), and the `ONE_LIST` text in `_never_refs` (line 479)
- Test: `tests/modules/spec/application/logic/test_never_use.py`

**Interfaces:**
- Consumes: `ck.never_names` as Task 1 left it (one slot per item); `ck.text(value) -> bool`; `ck.PART_NAME`
  (a compiled pattern); `Language` from `xarch.modules.spec.domain.values`.
- Produces: `never_lists(value: Any, problems: list[str], language: Language) ->
  dict[str, tuple[tuple[str, ...], ...] | None] | None` in module `never_lists`. It holds every valid list name in
  block order. The value is the list's expanded names, or `None` for a list whose value is no list or is empty, a list
  that includes itself however far, and a list that includes such a list. The whole result is `None` when `never` is
  no mapping. Task 3 adds a fourth parameter, `named: Mapping[str, str]`.

- [ ] **Step 1: Write the failing tests**

In `tests/modules/spec/application/logic/test_never_use.py`:

(a) Change the constant on line 15 to:

```python
ONE_LIST = "names one list under never: write the name of a list, such as pure; a list may include others"
```

(b) Add these constants and the helper below the existing `service_uses` helper (after line 30):

```python
EMPTY = ("must be a non-empty list of outside names, packages or methods, such as [<package>.<name>, <package>, "
         ".<name>()]")
TIME_SOCKET = (("time", "time"), ("socket",))


def naming(never, uses) -> dict:
    """The covered profile with the lists given under `never`, its service part naming the list uses."""
    document = covered(never=never)
    document["parts"]["service"]["uses"] = {"never": uses}
    return document
```

(c) Append these tests at the end of the file:

```python
@pytest.mark.parametrize("never, uses, found", [
    pytest.param({"pure": ["time.time", "socket"], "published": ["pure", "typing.Any"]}, "published",
                 (*TIME_SOCKET, ("typing", "Any")), id="an include, then a name"),
    pytest.param({"pure": ["time.time", "socket"], "published": ["typing.Any", "pure", "os.getenv"]}, "published",
                 (("typing", "Any"), *TIME_SOCKET, ("os", "getenv")), id="an include between two names"),
    pytest.param({"a": ["b", "x.one"], "b": ["c", "x.two"], "c": ["x.three"]}, "a",
                 (("x", "three"), ("x", "two"), ("x", "one")), id="a chain of three lists"),
    pytest.param({"published": ["pure", "typing.Any"], "pure": ["time.time", "socket"]}, "published",
                 (*TIME_SOCKET, ("typing", "Any")), id="the included list written below"),
    pytest.param(LISTS | {"both": ["pure", "ambient"]}, "both", (("socket",), ("os", "getcwd")),
                 id="a list of only includes"),
    pytest.param({"pure": ["published"]}, "pure", (("published",),),
                 id="a bare word that is no list name is a package"),
    pytest.param({"pure": ["socket"], "published": ["Pure"]}, "published", (("Pure",),),
                 id="an entry differing from a list name by case is a package"),
])
def test_an_entry_naming_a_list_puts_that_list_s_names_in_its_place(never, uses, found):
    assert parsed(naming(never, uses)).uses_never == {"service": found}


def test_a_list_including_another_reads_as_the_same_names_written_out():
    included = parsed(naming({"pure": ["time.time", "socket"], "published": ["pure", "typing.Any"]}, "published"))
    written = parsed(naming({"pure": ["time.time", "socket"], "published": ["time.time", "socket", "typing.Any"]},
                            "published"))
    assert included.uses_never == written.uses_never


@pytest.mark.parametrize("never, found", [
    pytest.param({"a": ["a", "x.one"]}, ["never.a: includes itself"], id="a list writing itself"),
    pytest.param({"a": ["b"], "b": ["a"]}, ["never.a: includes itself, through never.b: drop one of the two"],
                 id="two lists including each other, said at the one written first"),
    pytest.param({"b": ["a"], "a": ["b"]}, ["never.b: includes itself, through never.a: drop one of the two"],
                 id="said at whichever is written first"),
    pytest.param({"a": ["b"], "b": ["c"], "c": ["a"]},
                 ["never.a: includes itself, through never.b, never.c: drop one of the includes"],
                 id="three lists in a loop"),
    pytest.param({"top": ["a"], "a": ["b"], "b": ["a"]},
                 ["never.a: includes itself, through never.b: drop one of the two"],
                 id="a list including a list of a loop gets no problem for it"),
    pytest.param({"pure": ["os.environ"], "published": ["pure", "os.environ"]},
                 ["never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a name written after an include holding it"),
    pytest.param({"pure": ["os.environ"], "published": ["os.environ", "pure"]},
                 ["never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a name written before an include holding it"),
    pytest.param({"pure": ["os.environ"], "mid": ["pure"], "top": ["mid", "os.environ"]},
                 ["never.top: 'os.environ' is listed in never.pure, which never.top includes: drop it here"],
                 id="a name held by a list included through another, naming the list holding it"),
    pytest.param({"pure": ["os.environ"], "ambient": ["os.environ"], "both": ["pure", "ambient"]},
                 ["never.both: 'os.environ' is listed in never.pure and in never.ambient, which never.both includes: "
                  "drop it from one"], id="a name reached through two includes"),
    pytest.param({"pure": ["socket"], "both": ["pure", "pure"]}, ["never.both: includes never.pure twice"],
                 id="a list included twice"),
    pytest.param({"pure": ["socket"], "mid": ["pure"], "both": ["pure", "mid"]},
                 ["never.both: includes never.pure twice"],
                 id="a list included directly and through another, and its names not said again"),
    pytest.param({"pure": ["os.environ"], "mid": ["pure", "os.environ"], "top": ["mid"]},
                 ["never.mid: 'os.environ' is listed in never.pure, which never.mid includes: drop it here"],
                 id="a repeat said once, at the lowest list where it meets"),
    pytest.param({"pure": ["datetime..now"], "published": ["pure"]}, [f"never.pure: 'datetime..now' {METHOD}"],
                 id="a bad entry of an included list said once, under that list"),
    pytest.param({"pure": [], "published": ["pure", "x.one"]}, [f"never.pure: {EMPTY}"],
                 id="an included list that is empty"),
    pytest.param({"pure": "socket", "published": ["pure", "x.one"]}, [f"never.pure: {EMPTY}"],
                 id="an included list that is no list"),
    pytest.param({"a b": ["x.one"], "c": ["a b"]},
                 ["never: 'a b' is not a list name: use letters, digits, '_' and '-'", f"never.c: 'a b' {METHOD}"],
                 id="a key refused as a list name is no list"),
    pytest.param({1: ["x.one"], "c": ["pure", 3]},
                 ["never: 1 is not a list name: use letters, digits, '_' and '-'", f"never.c: 3 {METHOD}"],
                 id="a key that is no text, and an entry that is no text beside a name"),
    pytest.param({"pure": ["socket"], "published": [" pure"]}, [f"never.published: ' pure' {METHOD}"],
                 id="an entry with a space around a list name is no include"),
    pytest.param({"pure": ["os.environ"], "published": ["pure", "os.environ", "2fast"]},
                 [f"never.published: '2fast' {METHOD}",
                  "never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a list's entry problems before its include problems"),
])
def test_an_include_written_wrong_is_refused_at_the_list_it_is_about(never, found):
    assert problems(covered(never=never)) == [f"layered.yaml: {problem}" for problem in found]


def test_a_part_naming_a_list_of_a_loop_adds_no_problem_of_its_own():
    assert problems(naming({"a": ["b"], "b": ["a"]}, "b")) == [
        "layered.yaml: never.a: includes itself, through never.b: drop one of the two"]


def test_a_chain_and_a_loop_of_many_lists_are_read_whole():
    count = 1500
    chain = {f"l{i}": [f"l{i + 1}"] for i in range(count)} | {f"l{count}": ["x.one"]}
    assert parsed(naming(chain, "l0")).uses_never == {"service": (("x", "one"),)}
    loop = {f"l{i}": [f"l{(i + 1) % count}"] for i in range(count)}
    found = problems(naming(loop, "l0"))
    assert len(found) == 1
    assert found[0].startswith("layered.yaml: never.l0: includes itself, through never.l1, never.l2, never.l3, ")
    assert found[0].endswith(f", never.l{count - 1}: drop one of the includes")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_never_use.py`
Expected: FAIL. The include cases fail because an include reads as a package today (for example, `uses_never` holds
`('pure',)`). The loop cases fail with problems such as `never.a: 'a' ...` missing, or with no `InvalidArchitecture`
raised. The two `ONE_LIST` cases fail on the missing tail `; a list may include others`. The bad-entry, key and
space cases may already pass. The others fail.

- [ ] **Step 3: Write the module `never_lists`**

Create `xarch/modules/spec/application/logic/never_lists.py`:

```python
"""The lists of `never`, each read into the names it reaches: an entry that is exactly the name of another list of the
block includes that list's names in its place, in order, however deep, and every other entry is read as
`profile_checks.never_names` reads one. Each problem is said at the address of the list it is about, lists in block
order: its name, then its entries, then its includes."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.domain.values import Language

Steps = tuple[str, ...]


@dataclass(frozen=True)
class _Arrival:
    """A name a list reaches: its steps, the text the list whose own entries hold it writes, and that list."""
    steps: Steps
    text: str
    holder: str


@dataclass(frozen=True)
class _Expansion:
    """What a list reaches: its names in order, the first arrival of each kept, and every list it includes however
    deep, each once."""
    names: tuple[_Arrival, ...]
    lists: tuple[str, ...]


def never_lists(value: Any, problems: list[str], language: Language) -> dict[str, tuple[Steps, ...] | None] | None:
    """The lists of `never` by name, each the names it reaches in order; a list whose value is no list or is empty, one
    that includes itself however far, and one that includes such a list, is None. None: `never` is no mapping."""
    if not isinstance(value, Mapping):
        problems.append("never: must be a mapping of list names to lists of dotted names, such as "
                        "{pure: [datetime.datetime.now, socket]}")
        return None
    lists = [name for name in value if ck.text(name) and ck.PART_NAME.fullmatch(name)]
    said: dict[str, list[str]] = {name: [] for name in lists}
    entries = {name: _entries(name, value[name], lists, said[name], language) for name in lists}
    edges = {name: tuple(entry for entry in found if isinstance(entry, str)) if found else ()
             for name, found in entries.items()}
    reach = {name: _reach(name, edges) for name in lists}
    looping = {name for name in lists if name in edges[name] or name in reach[name]}
    _say_loops(lists, edges, reach, said)
    order = sorted((len(reach[name]), place, name) for place, name in enumerate(lists)
                   if entries[name] is not None and name not in looping and not reach[name] & looping)
    done: dict[str, _Expansion] = {}
    for _, _, name in order:
        done[name] = _expand(name, entries[name] or (), done, said[name])
    for name in value:
        if name in said:
            problems += said[name]
        else:
            problems.append(f"never: {name!r} is not a list name: use letters, digits, '_' and '-'")
    return {name: tuple(arrival.steps for arrival in done[name].names) if name in done else None for name in lists}


def _entries(name: str, value: Any, lists: list[str], problems: list[str],
             language: Language) -> tuple[_Arrival | str, ...] | None:
    """A list's entries in written order: an entry that is the name of a list of the block as that name, every other
    as the name it reads as, a refused one left out and said. None: the value is no list or is empty."""
    where = f"never.{name}"
    if not isinstance(value, list) or not value:
        ck.never_names(value, where, problems, language)
        return None
    rest = [item for item in value if not (isinstance(item, str) and item in lists)]
    read = iter(ck.never_names(rest, where, problems, language) or ()) if rest else iter(())
    found: list[_Arrival | str] = []
    for item in value:
        if isinstance(item, str) and item in lists:
            found.append(item)
            continue
        steps = next(read)
        if steps is not None:
            found.append(_Arrival(steps, item, name))
    return tuple(found)


def _reach(name: str, edges: Mapping[str, tuple[str, ...]]) -> set[str]:
    """Every list a list includes however far, not counting a list writing itself; the list itself when it comes back
    to itself through others. Walked without recursion, so a deep block is read whole."""
    reached: set[str] = set()
    waiting = [item for item in edges[name] if item != name]
    while waiting:
        item = waiting.pop()
        if item not in reached:
            reached.add(item)
            waiting += [after for after in edges[item] if after != item]
    return reached


def _say_loops(lists: list[str], edges: Mapping[str, tuple[str, ...]], reach: Mapping[str, set[str]],
               said: Mapping[str, list[str]]) -> None:
    """A list that writes itself, said at it; lists that include each other, said once, at the one written first."""
    covered: set[str] = set()
    for name in lists:
        if name in edges[name]:
            said[name].append(f"never.{name}: includes itself")
        if name in reach[name] and name not in covered:
            covered |= {item for item in reach[name] if name in reach[item]}
            way = _way_back(name, edges, reach)
            drop = "drop one of the two" if len(way) == 1 else "drop one of the includes"
            said[name].append(f"never.{name}: includes itself, through "
                              f"{', '.join(f'never.{item}' for item in way)}: {drop}")


def _way_back(name: str, edges: Mapping[str, tuple[str, ...]], reach: Mapping[str, set[str]]) -> tuple[str, ...]:
    """The lists after a list along the shortest way back to it, each list's includes tried in written order."""
    ways: list[tuple[str, tuple[str, ...]]] = [(name, ())]
    seen = {name}
    for here, way in ways:
        for item in edges[here]:
            if item == name and way:
                return way
            if item not in seen and name in reach[item]:
                seen.add(item)
                ways.append((item, (*way, item)))
    return ()


def _expand(name: str, found: tuple[_Arrival | str, ...], done: Mapping[str, _Expansion],
            problems: list[str]) -> _Expansion:
    """A list's names in order, each included list's names in its place; a list or a name reached twice is said here,
    where its two arrivals meet, and the first arrival kept. An included list with no names of its own adds none."""
    names: dict[Steps, _Arrival] = {}
    lists: list[str] = []
    for entry in found:
        if isinstance(entry, _Arrival):
            _arrive(name, entry, names, problems)
        elif entry in lists:
            problems.append(f"never.{name}: includes never.{entry} twice")
        elif entry in done:
            twice = [item for item in done[entry].lists if item in lists]
            problems += [f"never.{name}: includes never.{item} twice" for item in twice]
            lists += [item for item in (entry, *done[entry].lists) if item not in twice]
            for arrival in done[entry].names:
                if arrival.holder not in twice:
                    _arrive(name, arrival, names, problems)
    return _Expansion(tuple(names.values()), tuple(lists))


def _arrive(name: str, arrival: _Arrival, names: dict[Steps, _Arrival], problems: list[str]) -> None:
    """The name in the list's names when it is not there yet; else the repeat, said at the list."""
    first = names.get(arrival.steps)
    if first is None:
        names[arrival.steps] = arrival
    elif name in (first.holder, arrival.holder):
        own, other = (first, arrival) if first.holder == name else (arrival, first)
        problems.append(f"never.{name}: {own.text!r} is listed in never.{other.holder}, which never.{name} includes: "
                        "drop it here")
    else:
        problems.append(f"never.{name}: {first.text!r} is listed in never.{first.holder} and in "
                        f"never.{arrival.holder}, which never.{name} includes: drop it from one")
```

Why this shape, for the reviewer:
- `_entries` hands `ck.never_names` only the entries that are not includes, so an include never parses as a package.
  The slots come back aligned with `rest`, so `next(read)` puts each accepted name at its written place.
- A list's own repeats are refused by `ck.never_names` ("listed twice") before the expansion. Every repeat the
  expansion meets therefore crosses an include, and each included list's expansion is already free of repeats. So a
  repeat is said only at the lowest list where its two arrivals meet (rule 11).
- In a DAG, a list that includes another reaches strictly more lists than the one it includes. Sorting by
  `len(reach)` is therefore a valid bottom-up order with no recursion. The list's place breaks ties, so the order is
  deterministic.
- An included list whose value was refused (`entries[...] is None`) is never in `done`. `_expand` skips it and says
  nothing (rule 13).
- When a list is reached a second time, its names have all arrived already, so dropping them with no repeat problem is
  the same as keeping the first arrival (rule 10).

- [ ] **Step 4: Wire it into `parse_profile` and change the refusal and the docstring**

In `xarch/modules/spec/application/logic/profile_parsing.py` (line numbers are as they stand before this task;
find each place by the quoted text):

1. Docstring line 31, today

```
    never: {<list>: [<name>, ...]}             named lists of what a part never uses
```

becomes the two lines

```
    never: {<list>: [<name> | <list>, ...]}    named lists of what a part never uses; an entry naming another
                               list includes it
```

2. Imports: add, directly above line 75 (`from xarch.modules.spec.application.logic import profile_checks as ck`):

```python
from xarch.modules.spec.application.logic import never_lists as nl
```

3. Line 169, today

```python
    never_lists = _never_lists(document["never"], problems, language) if "never" in document else {}
```

becomes

```python
    never_lists = nl.never_lists(document["never"], problems, language) if "never" in document else {}
```

4. Delete the whole function `_never_lists` (lines 448-461, from `def _never_lists(` through its `return never_lists`
   and the two blank lines after it).

5. In `_never_refs`, line 479, today

```python
            problems.append(f"{where}: names one list under never: write the name of a list, such as pure")
```

becomes

```python
            problems.append(f"{where}: names one list under never: write the name of a list, such as pure; a list may "
                            "include others")
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_never_use.py tests/modules/spec/application/logic/test_profile_checks.py`
Expected: all pass. `test_a_chain_and_a_loop_of_many_lists_are_read_whole` takes about a second.

- [ ] **Step 6: Run the spec module's tests and the guards on the new file**

Run:
```bash
timeout 600 uv run pytest -q tests/modules/spec tests/architecture/test_agnostic.py tests/architecture/test_language_seam.py
uv run ruff check xarch/modules/spec/application/logic/never_lists.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_never_use.py
uv run xarch check
uv run xarch check --strict
```
Expected: all pass. `xarch check --strict` lists no new weak finding for `never_lists.py`. The two records are frozen
dataclasses named in the return annotations of `_entries` and `_expand`, as `holds: functions` with `immutable: true`
asks of the `logic` part. If one does appear, stop and report it.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/never_lists.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_never_use.py
git commit -m "A list of never may include another: an entry that is exactly the name of a list of the block puts that list's names in its place, in order, however deep, the list written above or below, expanded once at load so a part's uses_never holds the names; a list including itself, directly or through others (said once, at the list of the loop written first), one reaching a list twice and one reaching a name twice are refused at the lowest list where it meets; a part naming a list of lists is told a list may include others

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: A list may not take a name an entry would read as: a standard-library package, or a package the profile names

**Files:**
- Modify: `xarch/modules/spec/application/logic/never_lists.py` (`never_lists` gains `named`; new `_name_problems`)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py` (the call at line 169; new `_named_packages`
  placed directly above `_never_refs`)
- Test: `tests/modules/spec/application/logic/test_never_use.py`

**Interfaces:**
- Consumes: `never_lists(value, problems, language)` from Task 2; `ck.reserved_modules(value, problems, language) ->
  dict[str, str]`; `_libraries(spec, where, problems, language, reserved) -> tuple[str, ...]` (in
  `profile_parsing.py`); `EVERYTHING` (already imported in `profile_parsing.py` from `xarch.kernel.placement`).
- Produces: `never_lists(value: Any, problems: list[str], language: Language, named: Mapping[str, str]) ->
  dict[str, tuple[tuple[str, ...], ...] | None] | None`. `named` maps each package the profile names to the key of the
  first place naming it, such as `{"sqlmodel": "parts.store.libraries"}`. Also `_named_packages(document:
  Mapping[Any, Any], language: Language) -> dict[str, str]` in `profile_parsing.py`.

- [ ] **Step 1: Write the failing tests**

At the top of `tests/modules/spec/application/logic/test_never_use.py`, add `from dataclasses import replace` as the
first import line (above `import pytest`, with a blank line between the two groups, as ruff's import sorting wants),
so the head reads:

```python
from dataclasses import replace

import pytest
```

Add below the `EMPTY` and `TIME_SOCKET` constants from Task 2:

```python
def standard(name: str, title: str = "Python") -> str:
    """The refusal of a list named like a package of the language's standard library."""
    return (f"never.{name}: a list may not take the name of a package of the {title} standard library, since an entry "
            f"{name} would name the list: rename it")


def named(name: str, key: str) -> str:
    """The refusal of a list named like a package the profile names at key."""
    return f"never.{name}: a list may not take the name of a package this profile names ({key}): rename it"
```

Append at the end of the file:

```python
def test_a_list_named_like_a_standard_package_is_refused_and_an_entry_of_that_name_still_includes_it():
    assert problems(covered(never={"pure": ["socket"], "socket": ["time.time"]})) == [
        f"layered.yaml: {standard('socket')}"]


def test_the_standard_library_a_list_may_not_be_named_from_is_the_language_s():
    document = layered(never={"fs": ["lodash"], "pure": ["fs"]})
    document["parts"]["service"]["uses"] = {"never": "pure"}
    assert problems(document, languages={"brace": replace(BRACE, standard_names=frozenset({"fs"}))}) == [
        f"layered.yaml: {standard('fs', 'Brace')}"]
    assert parsed(document).uses_never == {"service": (("lodash",),)}


def test_a_list_named_like_a_package_a_part_lists_is_refused_naming_the_first_part_that_lists_it():
    assert problems(covered(never={"sqlmodel": ["x.one"]})) == [
        f"layered.yaml: {named('sqlmodel', 'parts.store.libraries')}"]
    document = covered(never={"sqlmodel": ["x.one"]})
    document["parts"]["service"]["libraries"] = ["sqlmodel"]
    assert problems(document) == [f"layered.yaml: {named('sqlmodel', 'parts.service.libraries')}"]


def test_a_list_named_like_a_reserved_module_is_refused_once_as_a_standard_package():
    document = covered(never={"ast": ["x.one"]}, reserved={"ast": "only the reader parses the language"})
    assert problems(document) == [f"layered.yaml: {standard('ast')}"]


def test_a_part_whose_libraries_are_everything_names_no_package():
    document = covered(never={"sqlmodel": ["x.one"]})
    document["parts"]["store"]["libraries"] = "everything"
    assert parsed(document).uses_never == {}


def test_a_part_naming_a_list_refused_for_its_name_adds_no_problem_of_its_own():
    assert problems(naming({"socket": ["time.time"]}, "socket")) == [f"layered.yaml: {standard('socket')}"]


def test_a_list_s_name_problem_comes_first_then_its_entries_then_its_includes():
    document = covered(never={"pure": ["os.environ"], "socket": ["pure", "os.environ", "2fast"]})
    assert problems(document) == [
        f"layered.yaml: {standard('socket')}",
        f"layered.yaml: never.socket: '2fast' {METHOD}",
        "layered.yaml: never.socket: 'os.environ' is listed in never.pure, which never.socket includes: drop it here"]


def test_never_reserved_and_libraries_are_said_once_each_in_their_own_place():
    document = covered(never={"pure": ["datetime..now"]}, reserved={"json": ""})
    document["parts"]["store"]["libraries"] = ["2fast"]
    assert problems(document) == [
        f"layered.yaml: never.pure: 'datetime..now' {METHOD}",
        "layered.yaml: reserved.json: must say in one line why it is reserved",
        "layered.yaml: parts.store.libraries: '2fast' is not a package name the language Python allows"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_never_use.py -k "standard or named_like or reserved or everything or refused_for_its_name or name_problem_comes_first or own_place"`
Expected: the collision tests FAIL, since no name problem is said yet (for example, `DID NOT RAISE` for the `socket`
list). `test_a_part_whose_libraries_are_everything_names_no_package` and
`test_never_reserved_and_libraries_are_said_once_each_in_their_own_place` already pass. They pin that this task does
not break them.

- [ ] **Step 3: Write the name problems in `never_lists`**

In `xarch/modules/spec/application/logic/never_lists.py`:

1. Replace the module docstring's first sentence so the whole docstring reads:

```python
"""The lists of `never`, each read into the names it reaches: an entry that is exactly the name of another list of the
block includes that list's names in its place, in order, however deep, and every other entry is read as
`profile_checks.never_names` reads one. A list may not take a name such an entry would read as: a package of the
language's standard library, or one the profile names. Each problem is said at the address of the list it is about,
lists in block order: its name, then its entries, then its includes."""
```

2. Replace the signature, docstring and the `said` line of `never_lists`:

```python
def never_lists(value: Any, problems: list[str], language: Language,
                named: Mapping[str, str]) -> dict[str, tuple[Steps, ...] | None] | None:
    """The lists of `never` by name, each the names it reaches in order; a list whose value is no list or is empty, one
    that includes itself however far, and one that includes such a list, is None. None: `never` is no mapping. named is
    each package the profile names, by the key of the first place naming it."""
```

and

```python
    said = {name: _name_problems(name, language, named) for name in lists}
```

(in place of `said: dict[str, list[str]] = {name: [] for name in lists}`). Every other line of the function is
unchanged.

3. Add directly below `never_lists`:

```python
def _name_problems(name: str, language: Language, named: Mapping[str, str]) -> list[str]:
    """The problem of a list's name that an entry would read as the list: the name of a package of the language's
    standard library, or of one the profile names."""
    if name in language.standard_names:
        return [f"never.{name}: a list may not take the name of a package of the {language.checked.title} standard "
                f"library, since an entry {name} would name the list: rename it"]
    if name in named:
        return [f"never.{name}: a list may not take the name of a package this profile names ({named[name]}): rename "
                "it"]
    return []
```

- [ ] **Step 4: Read the named packages silently in `parse_profile`**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

1. The line Task 2 left at 169:

```python
    never_lists = nl.never_lists(document["never"], problems, language) if "never" in document else {}
```

becomes

```python
    never_lists = (nl.never_lists(document["never"], problems, language, _named_packages(document, language))
                   if "never" in document else {})
```

2. Add directly above `def _never_refs(`:

```python
def _named_packages(document: Mapping[Any, Any], language: Language) -> dict[str, str]:
    """Each package the profile names, by the key of the first place naming it: the parts' `libraries` in the order the
    file writes them, then `reserved`. Read silently: each is said at its own place."""
    reserved = ck.reserved_modules(document["reserved"], [], language) if "reserved" in document else {}
    parts = document.get("parts")
    named: dict[str, str] = {}
    for part, spec in parts.items() if isinstance(parts, Mapping) else ():
        found = _libraries(spec, f"parts.{part}.libraries", [], language, reserved) if isinstance(spec, Mapping) else ()
        named |= {package: f"parts.{part}.libraries" for package in found
                  if package != EVERYTHING and package not in named}
    named |= {module: "reserved" for module in reserved if module not in named}
    return named
```

(`reserved` accepts only names in `standard_names`, so `_name_problems` always says the standard-library text for
such a list first. The `reserved` entry of `named` is there for a language whose `reserved` might one day differ, as
rule 7 asks. Nothing reaches it today, and no test claims it does.)

- [ ] **Step 5: Run the tests to verify they pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec/application/logic/test_never_use.py`
Expected: all pass.

- [ ] **Step 6: Run the spec module's tests, the guards, lint and the self-check**

```bash
timeout 600 uv run pytest -q tests/modules/spec tests/architecture/test_agnostic.py tests/architecture/test_language_seam.py
uv run ruff check xarch/modules/spec/application/logic/never_lists.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_never_use.py
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
```
Expected: all pass. `test_agnostic` passes because no literal holds `module`; that is spec deviation 1.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/never_lists.py xarch/modules/spec/application/logic/profile_parsing.py tests/modules/spec/application/logic/test_never_use.py
git commit -m "A list of never may not take the name of a package of the language's standard library, nor of a package the profile names in a part's libraries or in reserved, since an entry of that name would name the list: refused at the list, naming the first place naming it; an entry of that name still includes the list, and never, reserved and libraries are each said once, at their own place

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: The bundled profiles write `published: [pure, typing.Any]`

**Files:**
- Modify: `architecture.yaml:246-251`, `xarch/architectures/cli.yaml:201-206`, `xarch/architectures/web.yaml:203-208`
- Modify: `tests/bootstrap/project.py` (a new constant `PURE`, after `TESTS`)
- Test: `tests/bootstrap/test_bundled_architectures.py`, `tests/bootstrap/test_never_use.py`,
  `tests/bootstrap/test_where.py`

**Interfaces:**
- Consumes: the expansion from Tasks 2-3; `load_architecture(location)` from `xarch.bootstrap.wiring`;
  `problems(tmp_path, app=..., tests=..., profile="web")` from `tests/bootstrap/project.py`.
- Produces: `PURE: tuple[str, ...]` in `tests/bootstrap/project.py`, the 33 names of the bundled `pure` list in
  order.

- [ ] **Step 1: Write the failing tests**

(a) In `tests/bootstrap/project.py`, add after the `TESTS` mapping (before `def write`):

```python
PURE = ("datetime.datetime.now", "datetime.datetime.utcnow", "datetime.datetime.today", "datetime.date.today",
        "time.time", "time.time_ns", "time.monotonic", "time.perf_counter", "builtins.open", "builtins.print",
        "builtins.input", "sys.stdin", "sys.stdout", "sys.stderr", "os.environ", "os.getenv", "socket", "subprocess",
        "sqlite3", "urllib", "http", "shutil", "pathlib.Path.cwd", "pathlib.Path.absolute", "os.getcwd",
        "os.path.abspath", "os.path.realpath", "pathlib.Path.resolve", "pathlib.Path.home", "pathlib.Path.expanduser",
        "os.path.expanduser", "os.getcwdb", "os.chdir")
"""The names the bundled profiles' list `pure` holds, in the order it writes them."""
```

(b) In `tests/bootstrap/test_bundled_architectures.py`, change the imports to:

```python
from importlib import resources
from pathlib import Path

import pytest

from tests.bootstrap.project import PURE, bundled_profiles
from xarch.bootstrap.wiring import load_architecture
```

add below `PROFILE_NAMES = ["cli", "web"]`:

```python
OWN = Path(__file__).parent.parent.parent / "architecture.yaml"
FILES = [OWN, *(Path(str(resources.files("xarch").joinpath("architectures", f"{name}.yaml"))) for name in PROFILE_NAMES)]
```

and append at the end of the file:

```python
@pytest.mark.parametrize("location", [*PROFILE_NAMES, str(OWN)])
def test_published_is_pure_then_typing_any_and_pure_is_as_written(location):
    architecture = load_architecture(location)
    assert architecture.uses_never["domain"] == tuple(tuple(name.split(".")) for name in PURE)
    assert architecture.uses_never["contract"] == tuple(tuple(name.split(".")) for name in (*PURE, "typing.Any"))


@pytest.mark.parametrize("path", FILES, ids=lambda path: path.name)
def test_each_profile_writes_published_as_an_include_of_pure(path):
    assert path.read_text(encoding="utf-8").count("\n  published: [pure, typing.Any]\n") == 1
```

(c) In `tests/bootstrap/test_never_use.py`, change the import line `from tests.bootstrap.project import problems` to
`from tests.bootstrap.project import PURE, problems`, and append:

```python
def test_a_contract_file_is_found_the_same_whether_published_includes_pure_or_writes_its_names_out(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    included = "\n  published: [pure, typing.Any]\n"
    assert text.count(included) == 1
    written = tmp_path / "arch/written.yaml"
    written.write_text(text.replace(included, f"\n  published: [{', '.join((*PURE, 'typing.Any'))}]\n"))
    body = "from typing import Any\nimport datetime\n\nSTAMP = datetime.datetime.now()\n"
    contract = "modules/docs/contract/commands.py"
    found = problems(tmp_path / "included", app={contract: body})
    assert found == problems(tmp_path / "written", app={contract: body}, profile=str(written))
    assert found == [
        f"app/{contract}:1: contract/ of modules/docs may not import typing.Any (parts.contract.uses.never)",
        f"app/{contract}:4: contract/ of modules/docs may not use datetime.datetime.now (parts.contract.uses.never)"]
    assert not any("pure" in line or "published" in line for line in found)
```

(d) In `tests/bootstrap/test_where.py`, insert `from tests.bootstrap.project import PURE` between line 10
(`import xarch`) and line 11 (`from xarch.bootstrap.app import app`), the place ruff's import sorting wants, as
`tests/bootstrap/test_never_use.py` already has it. Then append:

```python
def test_the_contract_part_never_uses_pure_s_names_then_typing_any_in_order():
    found = document("app/modules/docs/contract/commands.py")
    assert found["never_uses"] == [*PURE, "typing.Any"]
    assert lines("app/modules/docs/contract/commands.py")["never uses"] == ", ".join((*PURE, "typing.Any"))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_never_use.py tests/bootstrap/test_where.py`
Expected: `test_each_profile_writes_published_as_an_include_of_pure` FAILS three times (`0 == 1`), and
`test_a_contract_file_is_found_the_same_...` FAILS at `assert text.count(included) == 1`. The `uses_never` test and
the `where` test already pass, because the names are written out today. They pin that the rewrite keeps them.

- [ ] **Step 3: Rewrite `published` in the three profiles**

In each of `architecture.yaml`, `xarch/architectures/cli.yaml` and `xarch/architectures/web.yaml`, the six lines
starting `  published: [datetime.datetime.now, datetime.datetime.utcnow, ...` and ending `              os.getcwdb,
os.chdir, typing.Any]` become the one line:

```yaml
  published: [pure, typing.Any]
```

So each file's `never:` block reads, with `pure`, `ambient` and `environment` exactly as before:

```yaml
never:
  pure: [datetime.datetime.now, datetime.datetime.utcnow, datetime.datetime.today, datetime.date.today, time.time,
         time.time_ns, time.monotonic, time.perf_counter, builtins.open, builtins.print, builtins.input, sys.stdin,
         sys.stdout, sys.stderr, os.environ, os.getenv, socket, subprocess, sqlite3, urllib, http, shutil,
         pathlib.Path.cwd, pathlib.Path.absolute, os.getcwd, os.path.abspath, os.path.realpath, pathlib.Path.resolve,
         pathlib.Path.home, pathlib.Path.expanduser, os.path.expanduser, os.getcwdb, os.chdir]
  published: [pure, typing.Any]
  ambient: [pathlib.Path.cwd, pathlib.Path.absolute, pathlib.Path.resolve, pathlib.Path.home, pathlib.Path.expanduser,
            os.getcwd, os.getcwdb, os.chdir, os.path.abspath, os.path.realpath, os.path.expanduser, .absolute(),
            .resolve(), .expanduser(), .chdir(), os.environ, os.getenv]
  environment: [os.environ, os.getenv]
```

Do not touch `tests/bootstrap/corpora/`. Then confirm that only those lines moved:
`git diff --stat -- architecture.yaml xarch/architectures` shows 3 files changed, 3 insertions and 18 deletions.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_never_use.py tests/bootstrap/test_where.py tests/bootstrap/test_recorded_corpora.py tests/bootstrap/test_profile_file.py`
Expected: all pass.

- [ ] **Step 5: Lint, self-check and commit**

```bash
uv run ruff check tests/bootstrap/project.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_never_use.py tests/bootstrap/test_where.py
uv run xarch check
uv run xarch profile check architecture.yaml
git add architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/project.py tests/bootstrap/test_bundled_architectures.py tests/bootstrap/test_never_use.py tests/bootstrap/test_where.py
git commit -m "The bundled profiles cli and web and xarch's own write published: [pure, typing.Any] in place of pure's 33 names written out again; the contract part never uses the same 34 names in the same order, and its findings and where's never uses are as before, naming no list

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The format text, README, CHANGELOG, golden docs and the gates

**Files:**
- Modify: `xarch/architectures/presets/format/keys.yaml:154-173` (entry `never`)
- Modify: `README.md:119` and a new paragraph after the shape block (after line 131, before line 133)
- Modify: `CHANGELOG.md:6-8`
- Test: `tests/bootstrap/test_profile_explain.py`; `tests/modules/spec/application/test_explain.py:211`
- Regenerate (expected unchanged): `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`
- Throwaway, never committed: `/tmp/xarch-3-4/regenerate_docs.py`

**Interfaces:**
- Consumes: the behaviour of Tasks 2-4.
- Produces: nothing later tasks use.

- [ ] **Step 1: Write the failing explain test**

Append to `tests/bootstrap/test_profile_explain.py`:

```python
def test_never_says_an_entry_naming_a_list_includes_it_and_a_list_may_not_take_a_name_an_entry_reads_as():
    found = json.loads(runner.invoke(app, ["profile", "explain", "never", "--format", "json"]).output)
    accepts = " ".join(found["accepts"].split())
    for said in ("a map {<list>: [<dotted name> | <list>, ...]}",
                 "An entry that is exactly the name of another list of `never` includes that list's names in its "
                 "place, in order, however deep, and the list may be written below",
                 "a list may not include itself, nor reach a name or a list twice",
                 "A list may not take the name of a package of the Python standard library, nor of a package the "
                 "profile names in a part's `libraries` or in `reserved`, since an entry of that name would name the "
                 "list"):
        assert said in accepts
    assert "  published: [pure, json.dumps]\n" in found["example"]
    assert "uses: {never: published}" in found["example"]
    shown = runner.invoke(app, ["profile", "explain", "never"])
    assert shown.exit_code == 0 and "published: [pure, json.dumps]" in shown.output
```

In `tests/modules/spec/application/test_explain.py`, line 211, today

```python
    assert "`uses: {never: <list>}`" in block.accepts and block.example.endswith("    uses: {never: pure}\n")
```

becomes

```python
    assert "`uses: {never: <list>}`" in block.accepts and block.example.endswith("    uses: {never: published}\n")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `timeout 300 uv run pytest -q tests/bootstrap/test_profile_explain.py -k includes_it tests/modules/spec/application/test_explain.py`
Expected: FAIL at the first `said` (`a map {<list>: [<dotted name> | <list>, ...]}` is not in the text), and
`test_the_lists_a_part_never_uses_are_the_top_level_never_and_the_key_never_of_its_uses` FAILS on the example's
ending.

- [ ] **Step 3: Write the `never` entry of `keys.yaml`**

In `xarch/architectures/presets/format/keys.yaml`, replace the entry `never` (lines 154-173, from `  never:` through
`          uses: {never: pure}`) with:

```yaml
  never:
    meaning: named lists of names a part never uses
    accepts: >-
      a map {<list>: [<dotted name> | <list>, ...]}; a part points to one list with `uses: {never: <list>}`. An entry
      is a dotted name as an import binds it (`datetime.datetime.now`; a builtin as `%namespace%.open`, a bare `open`
      is refused), a whole package (`socket`), or a method written with a leading dot and parentheses (`.absolute()`).
      An entry that is exactly the name of another list of `never` includes that list's names in its place, in order,
      however deep, and the list may be written below; a list may not include itself, nor reach a name or a list
      twice. A list may not take the name of a package of the %language% standard library, nor of a package the
      profile names in a part's `libraries` or in `reserved`, since an entry of that name would name the list. A file
      may not import a listed package or anything below it, nor use a listed name, called or not, as the file writes
      it (through the import that binds it, or a builtin by its bare name where nothing shadows it), nor call a listed
      method on anything no import names (a variable, a parameter, the result of a call), but on the method's own
      object and what it holds (`self.paths.resolve()`: a port's or its own). A method entry matches any object with a
      method of that name, so it belongs only in a list of parts that never call one legitimately. Silent on a name
      reached through a variable or `getattr`, a method of an object the list does not name, an annotation, and what a
      helper in another file does: a ban list, not a proof of purity. Not `review.never`, the files review never
      sends, which is another list
    example: |
      never:
        pure: [time.time, socket]
        published: [pure, json.dumps]
        ambient: [pathlib.Path.cwd, .absolute()]
      <<part>>
          uses: {never: published}
```

First check how `%language%` is filled: `grep -n "%language%" xarch/architectures/presets/format/keys.yaml | head -3`
shows that `reserved` already uses it ("a top-level import name of the %language% standard library"). Then run
`uv run xarch profile explain never` and confirm the text says `of the Python standard library`.

- [ ] **Step 4: Run the explain and catalogue tests**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_profile_explain.py tests/architecture/test_language_seam.py tests/modules/spec/application/logic/test_key_catalogue.py tests/modules/spec/application/test_explain.py tests/modules/spec/adapters/test_fs_architecture_files.py`
Expected: all pass.

- [ ] **Step 5: README**

In `README.md`, line 119, today

```
never:    {<list>: [<dotted name> | .<method>(), ...]}        layers: {<chain>: [<part>, ...]}
```

becomes

```
never:    {<list>: [<dotted name> | .<method>() | <list>, ...]}  layers: {<chain>: [<part>, ...]}
```

The values still start at column 11, as on every other line of the block. `layers` keeps the two-space gap to the left
that the block puts between two keys on one line.

Then, between the closing fence of the shape block (line 131, the line holding only three backticks) and the paragraph
starting `` `language` names the language of the app`` (line 133), insert this paragraph with one blank line on each
side:

```markdown
An entry of a `never` list that is the name of another list includes that list's names in its place, such as
`published: [pure, typing.Any]`; a list may not take the name of a package of the standard library or of a package the
profile names, since an entry of that name would name the list.
```

Run: `timeout 300 uv run pytest -q tests/architecture/test_readme.py`
Expected: all pass.

- [ ] **Step 6: CHANGELOG**

In `CHANGELOG.md`, lines 6-8 read `## [Unreleased]`, a blank line, then `### Changed`. Insert a new section between
the blank line and `### Changed`, so that part reads:

```markdown
## [Unreleased]

### Added

- A list of `never` may include another: an entry that is exactly the name of another list of the block puts that
  list's names in its place, in order, however deep, the list written above or below, as in
  `published: [pure, typing.Any]`. The bundled profiles and xarch's own now write `published` that way, with no
  part's names changed. Refused at the list: one that includes itself (`includes itself`, or `includes itself,
  through never.<list>: drop one of the two`), one that reaches a list twice (`includes never.<list> twice`), one
  that reaches a name twice (`'<name>' is listed in never.<list>, which never.<list> includes: drop it here`), and
  one named like a package of the standard library or one the profile names (`a list may not take the name of a
  package ...: rename it`). A part naming a list of lists is told `a list may include others`.

### Changed
```

- [ ] **Step 7: Regenerate the golden docs and check they did not move**

Create `/tmp/xarch-3-4/regenerate_docs.py` (never committed):

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
uv run python -I /tmp/xarch-3-4/regenerate_docs.py "$PWD"
git diff --stat -- docs/cli docs/web docs/xarch docs/templates docs/examples
```

Expected: three `written` lines, and an empty `git diff`. If the diff is not empty, stop and report it with the diff.
This step must not move them (`git checkout -- docs/cli docs/web docs/xarch` restores them).

- [ ] **Step 8: Run the gates**

```bash
mkdir -p /tmp/xarch-3-4
uv run ruff check
uv run xarch check
uv run xarch check --strict
uv run xarch profile check architecture.yaml
timeout 1200 uv run pytest -q > /tmp/xarch-3-4/final-pytest.txt 2>&1 &
echo $! > /tmp/xarch-3-4/final-pytest.pid
```

Expected: the first four pass. The suite takes over two minutes. Wait until the PID in
`/tmp/xarch-3-4/final-pytest.pid` has exited (`while kill -0 "$(cat /tmp/xarch-3-4/final-pytest.pid)" 2>/dev/null;
do sleep 10; done`), then read `tail -5 /tmp/xarch-3-4/final-pytest.txt`. Expected: `passed`, with no `failed` and no
`error`. If something fails, read the failure, fix it in the task that owns the code, and run the suite again. Never
signal any process but that recorded PID.

- [ ] **Step 9: Commit**

```bash
git add xarch/architectures/presets/format/keys.yaml README.md CHANGELOG.md tests/bootstrap/test_profile_explain.py tests/modules/spec/application/test_explain.py
git commit -m "The format text of never says an entry that is exactly the name of another list includes that list's names in its place, in order, however deep, that a list may not include itself nor reach a name or a list twice, nor take the name of a package of the standard library or one the profile names, and its example writes published: [pure, json.dumps]; the README's shape line and one sentence say the same, and the CHANGELOG adds it under Unreleased with the new refusal texts; the golden docs regenerate with no diff

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review against the spec

The planner applied Tasks 1-5 as written to a scratch copy of this branch, outside the worktree. Each task's
new tests failed before its code and passed after. `tests/modules/spec`, `test_agnostic.py`, `test_language_seam.py`,
`ruff check`, `xarch check --strict` and `xarch profile check architecture.yaml` passed, and the golden docs
regenerated with no diff. The first full-suite run found the two failures that deviations 6 and 7 fix. With both in,
the full suite passes.


- Rules 1-3 (telling an include): Task 2. Exact equality comes from `item in lists`. Keys refused by `PART_NAME` are
  not in `lists` (T22, the `1:` key). A list refused for its name stays in `lists` (Task 3, the `socket` test).
- Rules 4-5 (expansion, `published`): Task 2 (T1-T6) and Task 4 (T24, the `where` test, T25).
- Rule 6: Task 3, with the text of spec deviation 1 (T7, T8, T10). Rule 7: Task 3 (T9, T11).
- Rules 8-9: Task 2 (T12-T14, with the 1,500-list loop). Rule 10: Task 2 (T17). Rule 11: Task 2 (T15, T16, T18). The
  text for two includes is the spec's.
- Rule 12: Task 2 (`ONE_LIST`, T20). Rule 13: Task 2 (T19, three cases). Rule 14: the existing tests stay, plus T5.
- Rule 15 (order): Task 3's last two tests; the order inside one list is pinned in Tasks 2 and 3.
- Rules 16-21: Task 5 (keys.yaml, README, CHANGELOG, golden docs) and Task 2 Step 4 (docstring, rule 18). Rule 17 is
  Task 4.
- T26 is Task 5 Step 1, with the example of spec deviation 6. T27 is Task 5 Step 4: no test parses each example (`grep -rn "\.example" tests` shows none for
  the catalogue). T28 is Task 5 Steps 5, 7 and 8. T29 is Task 2 Step 6, Task 3 Step 6 and Task 5 Step 8.
- Names used across tasks: `never_lists` (module and function), `nl` (its alias in `profile_parsing.py`),
  `_named_packages`, `_name_problems`, `PURE`, `naming`, `EMPTY`, `TIME_SOCKET`, `standard`, `named`. Each is defined
  in the task that first uses it, with the same signature everywhere.
<!-- task-pipeline: validated -->
