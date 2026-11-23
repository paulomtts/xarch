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
